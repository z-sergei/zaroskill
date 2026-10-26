"""Recheck portable fixtures without overwriting archived preflight evidence."""

from pathlib import Path
import argparse
import json
import shutil
import subprocess
import sys
import tempfile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--followup", action="store_true", help="Recheck the separate directed two-case fixture set")
    args = parser.parse_args()
    source = Path(__file__).resolve().parent
    if args.followup:
        source = source / "followup/evaluation"
    with tempfile.TemporaryDirectory(prefix="zaroskill-economy-check-") as temporary:
        work = Path(temporary)
        ignore = shutil.ignore_patterns("__pycache__", "*.pyc", ".scratch", ".preflight")
        for name in ("cases", "grading"):
            shutil.copytree(source / name, work / name, ignore=ignore)
        process = subprocess.run(
            [sys.executable, "-B", str(work / "grading/preflight.py")],
            cwd=work, text=True, capture_output=True, timeout=180,
        )
        if process.returncode:
            print(process.stdout)
            print(process.stderr, file=sys.stderr)
            return process.returncode
        result = json.loads((work / "grading/preflight.json").read_text())
        references = result["reference_suites_and_independent_contracts"]
        print(json.dumps({
            "passed": result["passed"],
            "cases": len(result["initial_suites"]),
            "fixed_faults": sum(len(case["faults"]) for case in references.values()),
            "equivalent_refactors": sum(len(case["refactors"]) for case in references.values()),
            "classifier_checks": len(result["runner_self_checks"]),
            "separate_non_gating_diagnostic": args.followup,
            "archived_evidence_unchanged": True,
            "note": "Fixture validation, not a new agent comparison or external mutation-tool run.",
        }, ensure_ascii=False, indent=2))
        return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
