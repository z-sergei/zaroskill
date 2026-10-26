import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent
OUT = Path(__file__).resolve().parent
CASE_MAP = {"C02": "02_display_name", "C04": "04_discount_cap"}
before = {}
for candidate in ("A", "B"):
    for case in CASE_MAP.values():
        for path in (ROOT / "R1" / candidate / "cases" / case).glob("*.py"):
            before[str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()

records = []
for candidate in ("A", "B"):
    for case, variant in (
        ("C02", "baseline"),
        ("C02", "normalize_after_validation"),
        ("C04", "baseline"),
        ("C04", "zero_cap_skips_old_validation"),
        ("C04", "zero_subtotal_skips_cap_validation"),
    ):
        source = ROOT / "R1" / candidate / "cases" / CASE_MAP[case]
        work = OUT / candidate / case / variant
        work.mkdir(parents=True, exist_ok=False)
        for path in source.glob("*.py"):
            shutil.copy2(path, work / path.name)
        change = None
        if variant == "normalize_after_validation":
            path = work / "names.py"
            original = path.read_text()
            assert original.count("    return name") == 1
            path.write_text("import unicodedata\n\n" + original.replace(
                "    return name", '    return unicodedata.normalize("NFC", name)'))
            change = "Return NFC normalization only after the original strip and len validation; violates exact preservation of valid decomposed text."
        elif variant == "zero_cap_skips_old_validation":
            path = work / "discounts.py"
            original = path.read_text()
            header, body = original.split("\n", 1)
            path.write_text(header + "\n    if max_discount_cents == 0:\n        return subtotal_cents\n" + body)
            change = "Early zero-cap return before old amount/percent validation; violates original invalid-input rules."
        elif variant == "zero_subtotal_skips_cap_validation":
            path = work / "discounts.py"
            original = path.read_text()
            marker = "    if max_discount_cents is not None and max_discount_cents < 0:"
            assert original.count(marker) == 1
            path.write_text(original.replace(marker, "    if subtotal_cents == 0:\n        return 0\n" + marker))
            change = "Early zero-subtotal return after original amount/percent validation but before cap validation; violates negative-cap rejection at zero calculated discount."
        unchanged = all((work / p.name).read_bytes() == p.read_bytes() for p in source.glob("test_*.py"))
        assert unchanged
        env = os.environ.copy()
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        command = [sys.executable, "-m", "unittest", "discover", "-v"]
        run = subprocess.run(command, cwd=work, env=env, capture_output=True, text=True, timeout=10)
        log = run.stdout + run.stderr
        (work / "unittest.log").write_text(log)
        records.append({
            "candidate": candidate, "case": case, "variant": variant,
            "change": change, "cwd": str(work.relative_to(ROOT)),
            "command": command, "env_override": {"PYTHONDONTWRITEBYTECODE": "1"},
            "exit_code": run.returncode, "tests_unchanged": unchanged,
            "log_path": str((work / "unittest.log").relative_to(ROOT)),
            "run_summary": [line for line in log.splitlines() if line.startswith(("Ran ", "FAILED", "OK", "FAIL:", "ERROR:", "AssertionError:"))],
        })
        print(candidate, case, variant, run.returncode, records[-1]["run_summary"])

after = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in before}
assert before == after
report = {
    "origin": "Executed by the blind judge in disposable copies. These are neither supplied mechanical results nor participant execution records.",
    "purpose": "Resolve concrete cross-suite distinctions not contained in the fixed fault set, without claiming completeness or treating kill-set equality as redundancy.",
    "candidate_source_hashes_unchanged": before == after,
    "candidate_source_hashes": before,
    "records": records,
}
(OUT / "results.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
