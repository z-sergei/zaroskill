"""Judge-only narrow diagnostics selected after reading A/B; not frozen gates."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent
WORK = ROOT / 'judge-work' / 'narrow-copies'
ENV = {**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'}
report = {
    'author': 'blind judge',
    'kind': 'post_reading_narrow_diagnostics_not_fixed_gates',
    'invocation': 'PYTHONDONTWRITEBYTECODE=1 python3 judge-work/narrow_checks.py',
    'cwd': str(ROOT),
    'interpreter': sys.executable,
    'runs': [],
}
protected = [p for part in ('original-cases', 'R3') for p in (ROOT / part).rglob('*') if p.is_file()]
before = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in protected}


def run(label, case, variant, source, test_bytes, filename, witness=None):
    target = WORK / label / case / variant
    target.mkdir(parents=True, exist_ok=True)
    (target / filename).write_text(source)
    test_name = 'test_' + filename
    (target / test_name).write_bytes(test_bytes)
    assert (target / test_name).read_bytes() == test_bytes
    command = [sys.executable, '-m', 'unittest', 'discover', '-v']
    completed = subprocess.run(command, cwd=target, env=ENV, text=True, capture_output=True, timeout=30)
    output = completed.stdout + completed.stderr
    (target / 'submitted-suite.txt').write_text(output)
    item = {
        'label': label, 'case': case, 'variant': variant,
        'cwd': str(target), 'command': command,
        'environment_override': {'PYTHONDONTWRITEBYTECODE': '1'},
        'exit_code': completed.returncode,
        'test_file_sha256': hashlib.sha256(test_bytes).hexdigest(),
        'test_bytes_unchanged': True,
        'log': str((target / 'submitted-suite.txt').relative_to(ROOT)),
        'result_lines': [line for line in output.splitlines() if line.startswith(('Ran ', 'OK', 'FAILED', 'AssertionError:', 'ERROR:'))],
    }
    if witness:
        witness_command = [sys.executable, '-c', witness]
        observed = subprocess.run(witness_command, cwd=target, env=ENV, text=True, capture_output=True, timeout=30)
        (target / 'contract-witness.txt').write_text(observed.stdout + observed.stderr)
        item['judge_contract_witness'] = {'command': witness_command, 'exit_code': observed.returncode,
            'output': observed.stdout + observed.stderr,
            'log': str((target / 'contract-witness.txt').relative_to(ROOT))}
    report['runs'].append(item)
    print(label, case, variant, 'exit', completed.returncode, '; '.join(item['result_lines']))

for label in ['A', 'B']:
    for case, filename in [('04_discount_cap', 'discounts.py'), ('06_upload_workflow', 'upload.py')]:
        case_path = ROOT / 'R3' / label / 'cases' / case
        source = (case_path / filename).read_text()
        tests = (case_path / ('test_' + filename)).read_bytes()
        run(label, case, 'baseline', source, tests, filename)
        if case == '04_discount_cap':
            marker = '    if max_discount_cents is not None and max_discount_cents < 0:\n'
            assert source.count(marker) == 1
            changed = source.replace(marker,
                '    # Deliberately faulty early return for a positive amount rounded to zero.\n'
                '    if subtotal_cents > 0 and percent > 0 and subtotal_cents * percent < 100:\n'
                '        return subtotal_cents\n' + marker, 1)
            witness = 'from discounts import discounted_total; discounted_total(1, 1, max_discount_cents=-1); raise AssertionError("negative cap must raise ValueError even when a positive discount rounds to zero")'
            run(label, case, 'rounded_positive_discount_skips_negative_cap', changed, tests, filename, witness)
        else:
            marker = '    def complete(self, attempt_id, value):\n'
            assert source.count(marker) == 1
            changed = source.replace(marker, marker +
                '        # Deliberately faulty numeric false only for a future foreign id in waiting.\n'
                '        if self.state == "waiting" and attempt_id > self._active_attempt:\n'
                '            return 0\n', 1)
            witness = 'from upload import UploadSession; s = UploadSession(); current = s.begin(); result = s.complete(current + 1, "foreign"); assert result is False, f"expected False, got {result!r} ({type(result).__name__})"'
            run(label, case, 'future_foreign_completion_returns_numeric_zero', changed, tests, filename, witness)

after = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in protected}
assert before == after, 'Protected supplied material changed'
report['supplied_material_unchanged'] = True
report['protected_sha256'] = before
(ROOT / 'judge-work' / 'narrow-results.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
