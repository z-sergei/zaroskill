#!/usr/bin/env python3
"""Grade an existing run containing cases/<id>; Python standard library only.

Fixed behavioral variants replace only production in disposable copies. Candidate
unit tests stay byte-identical. This is an operational check, not an automatic
measure of redundancy or proof of general mutation adequacy.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parent
SCRATCH = ROOT / '.scratch'
MANIFEST = json.loads((ROOT / 'manifest.json').read_text(encoding='utf-8'))
ELIGIBLE_FAILURES = {'assertion_failure', 'domain_error', 'api_call_error'}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def semantic_review_fields():
    return {
        'additional_distinctions': None,
        'unjustified_scenarios': None,
        'maintenance_and_diagnostic_cost': None,
        'constraint_and_explanation_quality': None,
        'note': 'Human rubric required. Neither method count nor equal mutant kill sets determine these fields.',
    }


def test_hashes(case_dir):
    return {str(p.relative_to(case_dir)): digest(p) for p in sorted(case_dir.rglob('test_*.py')) if not p.is_symlink()}


def copy_case(source, target):
    shutil.copytree(source, target, ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '.DS_Store'), symlinks=True)
    for path in target.rglob('*'):
        if path.is_symlink():
            raise ValueError(f'Symlinks are not supported in submissions: {path.relative_to(target)}')


def execute(case_dir, module, test_file, *, replacement=None, contract=None, timeout=10):
    SCRATCH.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='check-', dir=SCRATCH) as temp:
        temp = Path(temp)
        copied = temp / 'case'
        try:
            copy_case(case_dir, copied)
        except (OSError, ValueError) as exc:
            return {'status': 'invalid', 'tests_run': 0, 'events': [{'kind': 'copy_error', 'message': str(exc)}]}
        if replacement is not None:
            (copied / module).write_bytes(replacement.read_bytes())
        before = test_hashes(copied)
        if contract is not None:
            (copied / '__contract__.py').write_bytes(contract.read_bytes())
        result_file = temp / 'result.json'
        command = [sys.executable, '-I', '-B', str(ROOT / 'runner.py'), '--root', str(copied),
                   '--module', module, '--test-file', test_file, '--output', str(result_file)]
        if contract is not None:
            command.append('--contract')
        started = time.monotonic()
        try:
            process = subprocess.run(command, cwd=copied, text=True, capture_output=True, timeout=timeout)
        except subprocess.TimeoutExpired as exc:
            return {
                'status': 'timeout', 'tests_run': None,
                'events': [{'kind': 'process_timeout', 'phase': 'process', 'message': f'Exceeded {timeout} seconds; no behavioral verdict.'}],
                'elapsed_seconds': round(time.monotonic() - started, 4),
            }
        if process.returncode != 0 or not result_file.is_file():
            return {
                'status': 'invalid', 'tests_run': None,
                'events': [{'kind': 'process_error', 'phase': 'process', 'message': f'Exit code {process.returncode}; missing or untrusted runner result.'}],
                'stdout': process.stdout[-4000:], 'stderr': process.stderr[-4000:],
                'elapsed_seconds': round(time.monotonic() - started, 4),
            }
        try:
            data = json.loads(result_file.read_text(encoding='utf-8'))
        except (ValueError, OSError) as exc:
            return {'status': 'invalid', 'events': [{'kind': 'result_error', 'message': str(exc)}]}
        data['elapsed_seconds'] = round(time.monotonic() - started, 4)
        data['test_files_unchanged'] = before == test_hashes(copied)
        if not data['test_files_unchanged']:
            data['status'] = 'invalid'
            data['events'].append({'kind': 'test_file_mutated', 'phase': 'process', 'message': 'Submitted test files changed during execution.'})
        if process.stdout:
            data['stdout'] = process.stdout[-4000:]
        if process.stderr:
            data['stderr'] = process.stderr[-4000:]
        return data


def mutation_verdict(result, baseline_ok=True):
    if not baseline_ok:
        return 'UNSCORABLE_BASELINE'
    if result['status'] == 'passed':
        return 'SURVIVED'
    events = result.get('events', [])
    if result['status'] == 'failed' and events and all(e['kind'] in ELIGIBLE_FAILURES for e in events):
        return 'KILLED'
    return 'INVALID'


def scope_check(case_dir, spec):
    issues = []
    original_names = {p.name for p in (ROOT / 'frozen' / case_dir.name).iterdir() if p.is_file()}
    permitted_names = original_names | set(spec['allowed_changes'])
    for name, expected in spec['frozen_sha256'].items():
        path = case_dir / name
        if not path.is_file() or path.is_symlink() or digest(path) != expected:
            issues.append(f'Forbidden file changed, missing, or symlinked: {name}')
    for path in case_dir.rglob('*'):
        relative = path.relative_to(case_dir)
        if '__pycache__' in relative.parts or path.suffix == '.pyc' or path.name == '.DS_Store':
            continue
        if path.is_symlink():
            issues.append(f'Symlink: {relative}')
        elif path.is_file() and str(relative) not in permitted_names:
            issues.append(f'File outside allowed changes: {relative}')
    if not (case_dir / spec['test_file']).is_file():
        issues.append(f'Missing test file: {spec["test_file"]}')
    response = case_dir / spec['required_response']
    response_present = response.is_file() and bool(response.read_text(encoding='utf-8').strip())
    if not response_present:
        issues.append(f'Missing nonempty explanation: {spec["required_response"]}')
    return {'passed': not issues, 'issues': issues, 'response_present': response_present}


def test_inventory(case_dir, test_file):
    """Operational diagnostics only: not a compression or redundancy score."""
    path = case_dir / test_file
    try:
        tree = ast.parse(path.read_text(encoding='utf-8'))
        names = [n.name for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name.startswith('test')]
        return {'test_method_names': names, 'test_file_sha256': digest(path), 'scoring_use': 'None; scenario meaning and cost require the rubric.'}
    except (OSError, SyntaxError) as exc:
        return {'error': str(exc), 'scoring_use': 'None'}


def grade_case(run_root, cid, timeout=10):
    spec = MANIFEST['cases'][cid]
    case_dir = run_root / 'cases' / cid
    if not case_dir.is_dir():
        return {'case': cid, 'automatic_gates_passed': False, 'error': f'Missing {case_dir}'}
    scope = scope_check(case_dir, spec)
    base = execute(case_dir, spec['module'], spec['test_file'], timeout=timeout)
    contract = execute(case_dir, spec['module'], spec['test_file'], contract=ROOT / 'contracts' / f'{cid}.py', timeout=timeout)
    faults = []
    for item in spec['faults']:
        result = execute(case_dir, spec['module'], spec['test_file'], replacement=ROOT / 'variants' / cid / 'faults' / f'{item["id"]}.py', timeout=timeout)
        faults.append({**item, 'verdict': mutation_verdict(result, base['status'] == 'passed'), 'run': result})
    refactors = []
    for item in spec['refactors']:
        result = execute(case_dir, spec['module'], spec['test_file'], replacement=ROOT / 'variants' / cid / 'refactors' / f'{item["id"]}.py', timeout=timeout)
        refactors.append({**item, 'passed': result['status'] == 'passed', 'run': result})
    kills_required = spec['tests_editable']
    gates = {
        'allowed_files_and_response': scope['passed'],
        'submitted_suite_runs_nonempty_and_passes': base['status'] == 'passed',
        'independent_contract_passes': contract['status'] == 'passed',
        'fixed_faults_detected': all(f['verdict'] == 'KILLED' for f in faults) if kills_required else None,
        'equivalent_refactors_pass': all(r['passed'] for r in refactors),
    }
    return {
        'case': cid,
        'skill': spec['skill'],
        'automatic_gates_passed': all(value is not False for value in gates.values()),
        'gates': gates,
        'scope': scope,
        'baseline': base,
        'contract': contract,
        'faults': faults,
        'refactors': refactors,
        'fault_scoring_note': 'Required protection checks; not a redundancy metric.' if kills_required else 'Review-only case: test changes forbidden. Fault outcomes are descriptive, not a submission gate.',
        'inventory': test_inventory(case_dir, spec['test_file']),
        'manual_review': semantic_review_fields(),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', required=True, type=Path, help='Directory containing cases/<id>')
    parser.add_argument('--output', type=Path, help='Optional JSON result path')
    parser.add_argument('--case', choices=sorted(MANIFEST['cases']), action='append', help='Limit to one or more case IDs')
    parser.add_argument('--timeout', type=float, default=10, help='Seconds per isolated unittest process')
    args = parser.parse_args()
    if args.timeout <= 0:
        parser.error('--timeout must be positive')
    selected = args.case or list(MANIFEST['cases'])
    results = [grade_case(args.run.resolve(), cid, args.timeout) for cid in selected]
    report = {
        'format_version': 1,
        'run': str(args.run.resolve()),
        'automatic_gates_passed': all(r['automatic_gates_passed'] for r in results),
        'manual_grading_required': True,
        'warning': 'Automatic gates do not score redundancy, useful distinctions, review correctness, or TDD chronology. Apply rubric.md separately.',
        'cases': results,
    }
    text = json.dumps(report, ensure_ascii=False, indent=2) + '\n'
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding='utf-8')
        print(json.dumps({'output': str(args.output.resolve()), 'automatic_gates_passed': report['automatic_gates_passed'],
                          'manual_grading_required': True, 'case_gates': {r['case']: r['automatic_gates_passed'] for r in results}}, ensure_ascii=False, indent=2))
    else:
        print(text, end='')
    return 0 if report['automatic_gates_passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
