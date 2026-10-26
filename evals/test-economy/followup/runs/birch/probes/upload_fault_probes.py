"""Disposable sensitivity checks; never edits the working implementation."""

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys


ROOT = Path("/private/tmp/zaroskill-economy-n9eezds3/followup/runs/birch")
CASE = ROOT / "work/cases/06_upload_workflow"
original = (CASE / "upload.py").read_bytes()
source = original.decode()
test_source = (CASE / "test_upload.py").read_bytes()
baseline_tests = [
    "test_upload.UploadTests.test_successful_upload",
    "test_upload.UploadTests.test_cancel_active_upload",
    "test_upload.UploadTests.test_unknown_completion_preserves_current_attempt",
]
faults = [
    (
        "rejected_begin_changes_active_attempt",
        '            raise RuntimeError("already waiting")',
        '            self._active_attempt += 1\n            raise RuntimeError("already waiting")',
        "test_upload.UploadTests.test_rejected_begin_preserves_the_attempt_that_can_complete",
    ),
    (
        "predecessor_result_is_accepted",
        '        if self.state != "waiting" or attempt_id != self._active_attempt:',
        '        if self.state != "waiting" or (attempt_id != self._active_attempt and attempt_id != self._active_attempt - 1):',
        "test_upload.UploadTests.test_restarts_clear_results_and_reject_previous_attempts",
    ),
    (
        "late_cancel_erases_result",
        '    def cancel(self):\n        if self.state != "waiting":\n            return False',
        '    def cancel(self):\n        if self.state != "waiting":\n            self.result = None\n            return False',
        "test_upload.UploadTests.test_completion_before_cancel_keeps_first_result",
    ),
]
results = []
for name, before, after, distinguishing_test in faults:
    if source.count(before) != 1:
        raise RuntimeError(f"Fault {name} does not identify one source location")
    probe = ROOT / "probes" / name
    probe.mkdir(exist_ok=True)
    (probe / "upload.py").write_text(source.replace(before, after))
    (probe / "test_upload.py").write_bytes(test_source)
    outcomes = {}
    for phase, names in [("existing", baseline_tests), ("distinguishing", [distinguishing_test])]:
        command = [sys.executable, "-m", "unittest", "-v", *names]
        run = subprocess.run(
            command,
            cwd=probe,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
            capture_output=True,
            text=True,
        )
        output = run.stdout + run.stderr
        (probe / f"{phase}.txt").write_text(output)
        outcomes[phase] = {"command": command, "exit_code": run.returncode}
        if phase == "existing" and run.returncode != 0:
            raise RuntimeError(f"Existing tests unexpectedly catch {name}: {output}")
        if phase == "distinguishing" and not (
            run.returncode == 1 and "AssertionError" in output and "FAILED (failures=" in output
        ):
            raise RuntimeError(f"New test did not meaningfully catch {name}: {output}")
    results.append({"fault": name, "directory": str(probe), **outcomes})
    print(f"{name}: existing tests PASS; new scenario FAILS with AssertionError")

if (CASE / "upload.py").read_bytes() != original:
    raise RuntimeError("Working implementation changed")
result = {
    "working_upload_sha256": hashlib.sha256(original).hexdigest(),
    "working_upload_unchanged": True,
    "results": results,
}
(ROOT / "probes/upload_probe_results.json").write_text(json.dumps(result, indent=2) + "\n")
print("Working upload.py unchanged:", result["working_upload_sha256"])
