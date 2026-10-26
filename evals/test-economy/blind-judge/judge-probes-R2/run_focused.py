import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent
OUT = Path(__file__).resolve().parent
CASES = {"C01": "01_shipping_bands", "C02": "02_display_name", "C04": "04_discount_cap", "C06": "06_upload_workflow"}
VARIANTS = {
    "C01": ["machine_integer_upper_limit"],
    "C02": ["normalize_internal_nbsp"],
    "C04": ["zero_cap_skips_old_validation"],
    "C06": ["numeric_boolean_returns", "two_id_cycle_after_success", "integer_subclass_ids"],
}
before = {}
for candidate in ("A", "B"):
    for case in CASES.values():
        for path in (ROOT / "R2" / candidate / "cases" / case).glob("*.py"):
            before[str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()

records = []
for candidate in ("A", "B"):
    for case, variants in VARIANTS.items():
        for variant in ["baseline"] + variants:
            source = ROOT / "R2" / candidate / "cases" / CASES[case]
            work = OUT / candidate / case / variant
            work.mkdir(parents=True, exist_ok=False)
            for path in source.glob("*.py"):
                shutil.copy2(path, work / path.name)
            change = None
            classification = "baseline"
            if variant == "machine_integer_upper_limit":
                path = work / "shipping.py"
                header, body = path.read_text().split("\n", 1)
                path.write_text(header + '\n    if subtotal_cents > 2**63 - 1:\n        raise ValueError("machine integer upper bound")\n' + body)
                change = "Reject amounts above signed 64-bit maximum; violates explicit absence of upper bound."
            elif variant == "normalize_internal_nbsp":
                path = work / "names.py"
                original = path.read_text()
                assert original.count("name = raw.strip()") == 1
                path.write_text(original.replace("name = raw.strip()", 'name = raw.strip().replace("\\u00a0", " ")'))
                change = "Convert remaining interior NBSP to ASCII space after correct edge stripping; violates exact preservation of interior characters."
            elif variant == "zero_cap_skips_old_validation":
                path = work / "discounts.py"
                header, body = path.read_text().split("\n", 1)
                path.write_text(header + "\n    if max_discount_cents == 0:\n        return subtotal_cents\n" + body)
                change = "Zero-cap early return bypasses original amount and percent validation."
            elif variant == "numeric_boolean_returns":
                path = work / "upload.py"
                original = path.read_text()
                assert "return True" in original and "return False" in original
                path.write_text(original.replace("return True", "return 1").replace("return False", "return 0"))
                change = "Return integer 1/0 in place of literal True/False while preserving state/result behavior; tests of truthiness may miss explicit return-value type contract."
            elif variant == "two_id_cycle_after_success":
                path = work / "upload.py"
                original = path.read_text()
                marker = "        self._last_attempt += 1"
                assert original.count(marker) == 1
                path.write_text(original.replace(marker, '        if self.state == "done":\n            self._last_attempt %= 2\n' + marker))
                change = "Cycle the counter modulo two only on restart from done, so a third consecutive success reuses id while a done/cancelled mixed third begin does not. Violates strictly increasing ids."
            elif variant == "integer_subclass_ids":
                path = work / "upload.py"
                original = path.read_text()
                marker = "        return self._active_attempt"
                assert original.count(marker) == 1
                path.write_text("class _AttemptId(int):\n    pass\n\n\n" + original.replace(marker, "        return _AttemptId(self._active_attempt)"))
                change = "Return an int subclass with unchanged positive value, comparison, identity matching, and monotonicity. Contract-compatible under the ordinary isinstance(int) reading; exact built-in type is not specified. Interpretation caveat must be recorded."
                classification = "contract_preserving_under_integer_subclass_reading"
            if change and classification == "baseline":
                classification = "contract_violation"
            unchanged = all((work / p.name).read_bytes() == p.read_bytes() for p in source.glob("test_*.py"))
            assert unchanged
            env = os.environ.copy()
            env["PYTHONDONTWRITEBYTECODE"] = "1"
            command = [sys.executable, "-m", "unittest", "discover", "-v"]
            run = subprocess.run(command, cwd=work, env=env, capture_output=True, text=True, timeout=10)
            log = run.stdout + run.stderr
            (work / "unittest.log").write_text(log)
            summary = [line for line in log.splitlines() if line.startswith(("Ran ", "FAILED", "OK", "FAIL:", "ERROR:", "AssertionError:", "ValueError:"))]
            record = dict(candidate=candidate, case=case, variant=variant, classification=classification,
                          change=change, cwd=str(work.relative_to(ROOT)), command=command,
                          env_override={"PYTHONDONTWRITEBYTECODE": "1"}, exit_code=run.returncode,
                          tests_unchanged=unchanged, log_path=str((work / "unittest.log").relative_to(ROOT)),
                          run_summary=summary)
            records.append(record)
            print(candidate, case, variant, run.returncode, summary)

after = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in before}
assert before == after
(OUT / "results.json").write_text(json.dumps(dict(
    origin="Executed by the blind judge in disposable copies only; distinct from supplied mechanical and participant evidence.",
    purpose="Resolve six concrete ambiguities already identified in code review, including reciprocal protection differences and an explicitly qualified type-interpretation question.",
    candidate_source_hashes_unchanged=True, candidate_source_hashes=before, records=records,
), ensure_ascii=False, indent=2) + "\n")
