#!/usr/bin/env python3
"""Validate and freeze fixtures before any skill-version comparisons."""
from __future__ import annotations

import datetime
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile

from grade import MANIFEST, ROOT, SCRATCH, execute, grade_case, mutation_verdict, summarize
from freeze import write_snapshot


def brief(result):
    return {
        'status': result['status'],
        'tests_run': result.get('tests_run'),
        'event_kinds': sorted({e['kind'] for e in result.get('events', [])}),
        'test_files_unchanged': result.get('test_files_unchanged'),
    }


def classification_self_checks():
    SCRATCH.mkdir(exist_ok=True)
    cases = [
        ('pass', 'def value():\n    return 3\n', 'def test_value(self):\n        self.assertEqual(value(), 3)', 'passed', 'SURVIVED', None),
        ('assertion', 'def value():\n    return 4\n', 'def test_value(self):\n        self.assertEqual(value(), 3)', 'failed', 'KILLED', 'assertion_failure'),
        ('domain_exception', 'def value():\n    raise ValueError("domain error")\n', 'def test_value(self):\n        value()', 'failed', 'KILLED', 'domain_error'),
        ('api_signature', 'def value():\n    return 3\n', 'def test_value(self):\n        value(extra=1)', 'failed', 'KILLED', 'api_call_error'),
        ('setup_assertion', 'def value():\n    return 3\n', 'def setUp(self):\n        self.fail("setup failed")\n    def test_value(self):\n        value()', 'invalid', 'INVALID', 'fixture_error'),
        ('setup_domain_exception', 'def value():\n    raise ValueError("domain error")\n', 'def setUp(self):\n        value()\n    def test_value(self):\n        pass', 'invalid', 'INVALID', 'fixture_error'),
        ('teardown_failure', 'def value():\n    return 3\n', 'def tearDown(self):\n        self.fail("teardown failed")\n    def test_value(self):\n        value()', 'invalid', 'INVALID', 'fixture_error'),
        ('body_import', 'def value():\n    return 3\n', 'def test_value(self):\n        import missing_fixture_dependency_92398', 'invalid', 'INVALID', 'import_error'),
        ('body_name_error', 'def value():\n    return 3\n', 'def test_value(self):\n        undefined_fixture_name_92398()', 'invalid', 'INVALID', 'test_body_error'),
        ('empty_suite', 'def value():\n    return 3\n', 'pass', 'no_tests', 'INVALID', None),
        ('all_skipped', 'def value():\n    return 3\n', '@unittest.skip("fixture")\n    def test_value(self):\n        value()', 'no_tests', 'INVALID', None),
        ('expected_failure_only', 'def value():\n    return 3\n', '@unittest.expectedFailure\n    def test_value(self):\n        self.fail("expected")', 'no_tests', 'INVALID', None),
        ('class_setup_error', 'def value():\n    return 3\n', '@classmethod\n    def setUpClass(cls):\n        raise RuntimeError("class setup failed")\n    def test_value(self):\n        value()', 'no_tests', 'INVALID', 'fixture_error'),
        ('discovery_import', 'import missing_fixture_dependency_92398\n', 'def test_value(self):\n        value()', 'invalid', 'INVALID', 'discovery_error'),
        ('timeout', 'def value():\n    return 3\n', 'def test_value(self):\n        import time\n        time.sleep(2)', 'timeout', 'INVALID', 'process_timeout'),
    ]
    summary = {}
    details = {}
    for name, source, test_body, expected_status, expected_verdict, expected_kind in cases:
        with tempfile.TemporaryDirectory(prefix='selfcheck-', dir=SCRATCH) as temp:
            folder = Path(temp)
            (folder / 'sample.py').write_text(source)
            (folder / 'test_sample.py').write_text('import unittest\nfrom sample import value\n\nclass Check(unittest.TestCase):\n    ' + test_body + '\n')
            result = execute(folder, 'sample.py', 'test_sample.py', timeout=0.2 if name == 'timeout' else 10)
        verdict = mutation_verdict(result)
        kinds = {e['kind'] for e in result.get('events', [])}
        okay = result['status'] == expected_status and verdict == expected_verdict and (expected_kind is None or expected_kind in kinds)
        summary[name] = {**brief(result), 'verdict': verdict, 'expected_status': expected_status, 'passed': okay}
        details[name] = result
    return summary, details


def main():
    output = ROOT / '.preflight'
    output.mkdir(exist_ok=True)
    ref_root = output / 'reference_run'
    if ref_root.exists():
        shutil.rmtree(ref_root)
    shutil.copytree(ROOT.parent / 'cases', ref_root / 'cases', ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '.DS_Store'))
    initial = {}
    references = {}
    diagnostics = {}
    raw_details = {'initial': {}, 'references': {}}
    for cid, spec in MANIFEST['cases'].items():
        initial_dir = ROOT.parent / 'cases' / cid
        result = execute(initial_dir, spec['module'], spec['test_file'])
        initial[cid] = brief(result)
        raw_details['initial'][cid] = result
        ref_dir = ref_root / 'cases' / cid
        (ref_dir / spec['module']).write_bytes((ROOT / 'reference_solutions' / cid / spec['module']).read_bytes())
        (ref_dir / spec['required_response']).write_bytes((ROOT / 'reference_solutions' / cid / spec['required_response']).read_bytes())
        if spec['tests_editable']:
            (ref_dir / spec['test_file']).write_bytes((ROOT / 'reference_tests' / cid / spec['test_file']).read_bytes())
        # An oracle copy always uses the separate full reference suite, including
        # C05, whose evaluated submissions are forbidden to edit their tests.
        with tempfile.TemporaryDirectory(prefix='oracle-', dir=SCRATCH) as temp:
            oracle = Path(temp) / 'case'
            shutil.copytree(ref_dir, oracle)
            (oracle / spec['test_file']).write_bytes((ROOT / 'reference_tests' / cid / spec['test_file']).read_bytes())
            baseline = execute(oracle, spec['module'], spec['test_file'])
            contract_file = ROOT / 'contracts' / f'{cid}.py'
            contract = execute(oracle, spec['module'], spec['test_file'], contract=contract_file)
            faults, refactors = [], []
            for fault in spec['faults']:
                replacement = ROOT / 'variants' / cid / 'faults' / f'{fault["id"]}.py'
                candidate = execute(oracle, spec['module'], spec['test_file'], replacement=replacement)
                independent = execute(oracle, spec['module'], spec['test_file'], replacement=replacement, contract=contract_file)
                faults.append({'id': fault['id'], 'reference_verdict': mutation_verdict(candidate, baseline['status'] == 'passed'),
                               'contract_verdict': mutation_verdict(independent, contract['status'] == 'passed'),
                               'reference_run': brief(candidate), 'contract_run': brief(independent)})
                raw_details['references'][f'{cid}/fault/{fault["id"]}'] = {'reference': candidate, 'contract': independent}
            for refactor in spec['refactors']:
                replacement = ROOT / 'variants' / cid / 'refactors' / f'{refactor["id"]}.py'
                candidate = execute(oracle, spec['module'], spec['test_file'], replacement=replacement)
                independent = execute(oracle, spec['module'], spec['test_file'], replacement=replacement, contract=contract_file)
                refactors.append({'id': refactor['id'], 'reference_run': brief(candidate), 'contract_run': brief(independent)})
                raw_details['references'][f'{cid}/refactor/{refactor["id"]}'] = {'reference': candidate, 'contract': independent}
            diagnostics[cid] = []
            for diagnostic in spec.get('diagnostics', []):
                replacement = ROOT / 'variants' / cid / 'diagnostics' / f'{diagnostic["id"]}.py'
                candidate = execute(oracle, spec['module'], spec['test_file'], replacement=replacement)
                independent = execute(oracle, spec['module'], spec['test_file'], replacement=replacement, contract=contract_file)
                diagnostics[cid].append({**diagnostic, 'included_in_gates': False,
                    'reference_run': brief(candidate), 'independent_contract_run': brief(independent)})
                raw_details['references'][f'{cid}/diagnostic/{diagnostic["id"]}'] = {'reference': candidate, 'contract': independent}
            references[cid] = {'baseline': brief(baseline), 'contract': brief(contract), 'faults': faults, 'refactors': refactors,
                               'passed': baseline['status'] == contract['status'] == 'passed'
                                  and all(f['reference_verdict'] == f['contract_verdict'] == 'KILLED' for f in faults)
                                  and all(r['reference_run']['status'] == r['contract_run']['status'] == 'passed' for r in refactors)}

    cid = '04_discount_cap'
    spec = MANIFEST['cases'][cid]
    red = execute(ref_root / 'cases' / cid, spec['module'], spec['test_file'], replacement=ROOT / 'frozen' / cid / spec['module'])
    green = execute(ref_root / 'cases' / cid, spec['module'], spec['test_file'])
    tdd = {'red_original_production_with_reference_tests': brief(red),
           'green_updated_production_with_same_tests': brief(green),
           'passed': red['status'] == 'failed' and green['status'] == 'passed',
           'note': 'Observed preflight red/green for the reference. Does not prove any evaluated agent followed TDD.'}
    raw_details['reference_tdd'] = {'red': red, 'green': green}
    self_checks, self_details = classification_self_checks()
    raw_details['runner_self_checks'] = self_details
    reference_grading = [grade_case(ref_root, cid) for cid in MANIFEST['cases']]
    raw_details['reference_submission_grade'] = reference_grading
    # A strict-type assertion is deliberately added only in a disposable
    # synthetic self-check. It must affect the diagnostic, never the fixed gates.
    with tempfile.TemporaryDirectory(prefix='non-gating-', dir=SCRATCH) as temp:
        synthetic = Path(temp) / 'run'
        shutil.copytree(ref_root, synthetic)
        test_path = synthetic / 'cases/06_upload_workflow/test_upload.py'
        with test_path.open('a', encoding='utf-8') as stream:
            stream.write("\n\nclass DiagnosticIsolationCheck(unittest.TestCase):\n    def test_exact_type_only_for_harness_selfcheck(self):\n        self.assertIs(type(UploadSession().begin()), int)\n")
        synthetic_grade = grade_case(synthetic, '06_upload_workflow')
    diagnostic_isolation = {
        'fixed_gates_passed': synthetic_grade['automatic_gates_passed'],
        'diagnostic_submitted_status': synthetic_grade['diagnostics_non_gating'][0]['submitted_run']['status'],
        'passed': synthetic_grade['automatic_gates_passed'] and synthetic_grade['diagnostics_non_gating'][0]['submitted_run']['status'] == 'failed',
        'note': 'Synthetic exact-type assertion rejects int subclass; this must not change fixed gates.',
    }
    raw_details['diagnostic_gate_independence_check'] = synthetic_grade
    provenance = json.loads((ROOT / 'provenance.json').read_text(encoding='utf-8'))
    expected_bytes = {**provenance['unchanged_case_files'], **provenance['unchanged_correct_implementations']}
    initial_integrity = {
        relative: hashlib.sha256((ROOT.parent / relative).read_bytes()).hexdigest() == expected
        for relative, expected in expected_bytes.items()
    }
    for cid in MANIFEST['cases']:
        response_path = ref_root / 'cases' / cid / MANIFEST['cases'][cid]['required_response']
        # Responses are evidence aids only. The fixed references remain outside cases.
        assert response_path.is_file()
    passed = all(x['status'] == 'passed' for x in initial.values()) and all(x['passed'] for x in references.values()) and tdd['passed'] and all(x['passed'] for x in self_checks.values()) and all(x['automatic_gates_passed'] for x in reference_grading) and diagnostic_isolation['passed'] and all(initial_integrity.values())
    preflight = {
        'created_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'passed': passed,
        'authored_before_followup_agent_runs': True,
        'evaluation_kind': 'directed_followup_on_previously_exposed_tasks',
        'fresh_holdout': False,
        'part_of_original_preregistered_comparison': False,
        'diagnostics_non_gating': diagnostics,
        'diagnostic_gate_independence_check': diagnostic_isolation,
        'unchanged_initial_files_and_correct_sources': initial_integrity,
        'automatic_summary_for_reference_submission': summarize(reference_grading),
        'external_mutation_tool_executed': False,
        'initial_suites': initial,
        'reference_suites_and_independent_contracts': references,
        'reference_tdd': tdd,
        'runner_self_checks': self_checks,
        'reference_submission_automatic_gates': {r['case']: r['automatic_gates_passed'] for r in reference_grading},
        'limitations': ['Fixed samples are not exhaustive.', 'Economy and diagnostic value require rubric.md.', 'No score derives from method count or equal kill sets.', 'Final snapshots do not establish candidate TDD chronology.', 'Trusted-code runner; not an adversarial sandbox.', 'Directed checks on already exposed tasks are not a new holdout or part of the original comparison.', 'The integer-subclass variant is diagnostic only and never changes fixed gates.'],
    }
    (output / 'details.json').write_text(json.dumps(raw_details, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (ROOT / 'preflight.json').write_text(json.dumps(preflight, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    write_snapshot()
    print(json.dumps({'passed': passed, 'preflight': str(ROOT / 'preflight.json'), 'fixed_faults': sum(len(v['faults']) for v in MANIFEST['cases'].values()),
                      'reference_results': {cid: r['passed'] for cid, r in references.items()},
                      'self_checks': {name: r['passed'] for name, r in self_checks.items()},
                      'reference_submission_gates': preflight['reference_submission_automatic_gates'],
                      'summary': preflight['automatic_summary_for_reference_submission']}, ensure_ascii=False, indent=2))
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())
