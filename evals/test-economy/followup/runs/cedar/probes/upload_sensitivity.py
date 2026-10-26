from pathlib import Path
import hashlib
import json
import subprocess
import sys


root = Path(__file__).resolve().parent.parent
case = root / "work" / "cases" / "06_upload_workflow"
source = (case / "upload.py").read_text()
tests = (case / "test_upload.py").read_text()
before = hashlib.sha256((case / "upload.py").read_bytes()).hexdigest()
guard = '        if self.state != "waiting" or attempt_id != self._active_attempt:\n            return False'
variants = [
    (
        "rejected_begin_loses_active",
        '        if self.state == "waiting":\n            raise RuntimeError',
        '        if self.state == "waiting":\n            self._active_attempt = None\n            raise RuntimeError',
        "test_rejected_begin_preserves_the_active_attempt",
        1,
    ),
    (
        "cancelled_accepts_late_completion",
        guard,
        '        if self.state == "cancelled" and attempt_id == self._last_attempt:\n            self.state = "done"\n            self.result = value\n            return True\n' + guard,
        "test_cancelled_attempt_ignores_late_completion_and_repeated_cancel",
        1,
    ),
    (
        "restart_reuses_completed_id",
        '        self._last_attempt += 1',
        '        if self.state != "done":\n            self._last_attempt += 1',
        "test_restarts_keep_old_results_out_of_new_attempts",
        1,
    ),
    (
        "rejected_duplicate_overwrites_result",
        guard,
        '        if self.state != "waiting" or attempt_id != self._active_attempt:\n            if self.state == "done" and attempt_id == self._last_attempt:\n                self.result = value\n            return False',
        "test_completed_result_survives_repeated_completion_and_cancel",
        1,
    ),
    (
        "restart_retains_previous_result",
        '        self.state = "waiting"\n        self.result = None\n        return self._active_attempt',
        '        self.state = "waiting"\n        return self._active_attempt',
        "test_restarts_keep_old_results_out_of_new_attempts",
        1,
    ),
    (
        "valid_ids_increase_by_seven",
        '        self._last_attempt += 1',
        '        self._last_attempt += 7',
        None,
        0,
    ),
]
results = []
for name, old, new, test, expected_exit in variants:
    assert source.count(old) == 1, (name, "replacement must match once")
    target = root / "probes" / name
    target.mkdir(parents=True, exist_ok=True)
    (target / "upload.py").write_text(source.replace(old, new, 1))
    (target / "test_upload.py").write_text(tests)
    command = [sys.executable, "-m", "unittest"]
    command += ["-v", "test_upload.UploadTests." + test] if test else ["discover", "-v"]
    run = subprocess.run(command, cwd=target, text=True, capture_output=True)
    output = run.stdout + run.stderr
    (target / "output.txt").write_text(output)
    checks_out = run.returncode == expected_exit
    if expected_exit:
        checks_out = checks_out and "AssertionError:" in output and "FAILED (failures=" in output
    else:
        checks_out = checks_out and "Ran 8 tests" in output and "\nOK\n" in output
    result = {
        "variant": name,
        "command": command,
        "exit_code": run.returncode,
        "expected_exit": expected_exit,
        "verified_result": checks_out,
        "output": str(target / "output.txt"),
    }
    results.append(result)
    print(name + ": exit " + str(run.returncode) + ", verified=" + str(checks_out))
    for line in output.splitlines():
        if line.startswith(("AssertionError:", "Ran ", "FAILED", "OK")):
            print("  " + line)

after = hashlib.sha256((case / "upload.py").read_bytes()).hexdigest()
report = {"production_sha256_before": before, "production_sha256_after": after, "results": results}
(root / "probes" / "results.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
assert before == after, "production changed"
assert all(result["verified_result"] for result in results), "unexpected probe result"
print("Production SHA-256 unchanged: " + after)
