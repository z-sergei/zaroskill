"""One isolated unittest execution. Not a mutation-tool adapter."""
from __future__ import annotations

import argparse
import importlib.util
import io
import json
from pathlib import Path
import sys
import traceback
import unittest


def tracked(original, phase):
    def call(self, *args, **kwargs):
        self._evaluation_phase = phase
        return original(self, *args, **kwargs)
    return call


for method, phase in (
    ('_callSetUp', 'setup'),
    ('_callTestMethod', 'body'),
    ('_callTearDown', 'teardown'),
    ('_callCleanup', 'cleanup'),
):
    setattr(unittest.TestCase, method, tracked(getattr(unittest.TestCase, method), phase))


class Result(unittest.TextTestResult):
    production_path = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.events = []
        self.successful_tests = 0

    def startTest(self, test):
        test._evaluation_phase = 'setup'
        super().startTest(test)

    def addSuccess(self, test):
        self.successful_tests += 1
        super().addSuccess(test)

    def classify(self, test, err, is_failure=False):
        exc_type, exc, tb = err
        test_id = test.id()
        phase = getattr(test, '_evaluation_phase', 'unknown')
        frames = traceback.extract_tb(tb)
        if '_FailedTest.' in test_id:
            kind, phase = 'discovery_error', 'discovery'
        elif test_id.startswith(('setUpClass ', 'setUpModule ', 'tearDownClass ', 'tearDownModule ')):
            kind, phase = 'fixture_error', 'class_or_module_fixture'
        elif phase in ('setup', 'teardown', 'cleanup', 'unknown'):
            kind = 'fixture_error'
        elif issubclass(exc_type, (ImportError, SyntaxError)):
            kind = 'import_error'
        elif is_failure or issubclass(exc_type, AssertionError):
            kind = 'assertion_failure'
        elif any(Path(frame.filename).resolve() == self.production_path for frame in frames):
            kind = 'domain_error'
        elif issubclass(exc_type, TypeError):
            # Python raises public signature mismatches at the call site, outside
            # the callee. Baseline success is still required before kill credit.
            kind = 'api_call_error'
        else:
            kind = 'test_body_error'
        self.events.append({
            'test': test_id,
            'phase': phase,
            'kind': kind,
            'exception': exc_type.__name__,
            'message': str(exc)[:800],
        })

    def addFailure(self, test, err):
        self.classify(test, err, is_failure=True)
        super().addFailure(test, err)

    def addError(self, test, err):
        self.classify(test, err)
        super().addError(test, err)

    def addSubTest(self, test, subtest, err):
        if err is not None:
            self.classify(test, err, is_failure=issubclass(err[0], test.failureException))
            self.events[-1]['test'] = subtest.id()
        super().addSubTest(test, subtest, err)


def flatten(suite):
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from flatten(item)
        else:
            yield item.id()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', required=True, type=Path)
    parser.add_argument('--module', required=True)
    parser.add_argument('--test-file', required=True)
    parser.add_argument('--contract', action='store_true')
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    sys.path.insert(0, str(args.root.resolve()))
    Result.production_path = (args.root / args.module).resolve()
    log = io.StringIO()
    try:
        loader = unittest.TestLoader()
        if args.contract:
            suite = loader.loadTestsFromName('__contract__')
        else:
            suite = loader.discover(str(args.root), pattern=args.test_file, top_level_dir=str(args.root))
        test_ids = list(flatten(suite))
        result = unittest.TextTestRunner(stream=log, verbosity=2, resultclass=Result).run(suite)
        effective_tests = result.testsRun - len(result.skipped) - len(result.expectedFailures)
        invalid = [e for e in result.events if e['kind'] not in ('assertion_failure', 'domain_error', 'api_call_error')]
        if effective_tests <= 0:
            status = 'no_tests'
        elif invalid:
            status = 'invalid'
        elif result.failures or result.errors or result.unexpectedSuccesses:
            status = 'failed'
        elif result.successful_tests <= 0:
            status = 'no_tests'
        else:
            status = 'passed'
        data = {
            'status': status,
            'tests_run': result.testsRun,
            'effective_tests': effective_tests,
            'successful_tests': result.successful_tests,
            'skipped': len(result.skipped),
            'expected_failures': len(result.expectedFailures),
            'unexpected_successes': len(result.unexpectedSuccesses),
            'test_ids': test_ids,
            'events': result.events,
            'log': log.getvalue()[-8000:],
        }
    except BaseException as exc:
        data = {
            'status': 'invalid', 'tests_run': 0, 'effective_tests': 0,
            'events': [{'kind': 'runner_error', 'phase': 'runner', 'exception': type(exc).__name__, 'message': str(exc)}],
            'log': traceback.format_exc()[-8000:],
        }
    args.output.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
