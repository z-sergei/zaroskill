"""Evaluator-owned unittest host; generated submissions never receive this file."""
import json
from pathlib import Path
import sys
import unittest

workspace = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(workspace))
result_path = Path(sys.argv[2]).resolve()
sys.argv = ["unittest"]
try:
    suite = unittest.defaultTestLoader.discover(str(workspace / "tests"), pattern="test_*.py")
    found = suite.countTestCases()
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    data = {
        "found": found,
        "run": result.testsRun,
        "failures": [{"test": test.id(), "trace": trace} for test, trace in result.failures],
        "errors": [{"test": test.id(), "trace": trace} for test, trace in result.errors],
        "skipped": [(test.id(), reason) for test, reason in result.skipped],
        "expected_failures": len(result.expectedFailures),
        "unexpected_successes": len(result.unexpectedSuccesses),
    }
except BaseException as error:
    data = {"host_error": f"{type(error).__name__}: {error}"}
result_path.write_text(json.dumps(data, indent=2) + "\n")
raise SystemExit(0 if data.get("run", 0) > 0 and not any(data.get(key) for key in
    ("failures", "errors", "skipped", "expected_failures", "unexpected_successes", "host_error")) else 1)
