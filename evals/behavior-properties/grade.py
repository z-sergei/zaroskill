"""Execute public contracts and unchanged submitted search tests in disposable copies."""
from pathlib import Path
import hashlib, json, re, shutil, subprocess, sys, tempfile

ROOT = Path(__file__).resolve().parent

BOOKING_CONTRACT = '''
import unittest
from booking import TicketDesk

class ContractTests(unittest.TestCase):
    def test_first_customer_receives_the_seat_and_other_customer_does_not(self):
        desk = TicketDesk()
        self.assertIsNone(desk.owner)
        alice = desk.reserve('Alice', 'a1')
        self.assertEqual(('Alice', True), (alice.customer, alice.accepted))
        self.assertEqual('Alice', desk.owner)
        bob = desk.reserve('Bob', 'b1')
        self.assertEqual(('Bob', False), (bob.customer, bob.accepted))
        self.assertEqual('Alice', desk.owner)

    def test_success_and_rejection_receipts_survive_retries(self):
        desk = TicketDesk()
        alice = desk.reserve('Alice', 'a1')
        bob = desk.reserve('Bob', 'b1')
        self.assertEqual(alice, desk.reserve('Alice', 'a1'))
        self.assertEqual(bob, desk.reserve('Bob', 'b1'))
        self.assertEqual('Alice', desk.owner)

    def test_conflicting_identity_does_not_reassign_original_request(self):
        desk = TicketDesk()
        original = desk.reserve('Alice', 'one')
        with self.assertRaises(ValueError):
            desk.reserve('Bob', 'one')
        self.assertEqual(original, desk.reserve('Alice', 'one'))
        self.assertEqual('Alice', desk.owner)
'''

SEARCH_REFERENCE = '''
import unittest
from search import SearchApp

class Gateway:
    def __init__(self): self.requests = []
    def start(self, token, query): self.requests.append((token, query))

class SearchContract(unittest.TestCase):
    def test_active_results_survive_old_completions_and_new_search_start(self):
        gateway = Gateway()
        app = SearchApp(gateway)
        first = app.search('old')
        second = app.search('new')
        self.assertEqual([(first, 'old'), (second, 'new')], gateway.requests)
        self.assertNotEqual(first, second)
        app.receive(second, ['new-result'])
        self.assertEqual(('new-result',), app.visible)
        app.receive(first, ['old-result'])
        self.assertEqual(('new-result',), app.visible)
        third = app.search('next')
        self.assertEqual(('new-result',), app.visible)
        app.receive(third, ['next-result'])
        self.assertEqual(('next-result',), app.visible)
'''

VARIANTS = {
 'original': [],
 'fault_accept_obsolete': [('if token == self._active:', 'if True:')],
 'fault_skip_request': [('self.gateway.start(token, query)', 'pass')],
 'fault_never_publish': [('if token == self._active:', 'if False:')],
 'fault_clear_while_loading': [('self._active += 1', 'self._active += 1\n        self.visible = ()')],
 'refactor_token_values': [('self._active = 0', 'self._active = 100'), ('self._active += 1', 'self._active += 7')],
 'refactor_private_name': [('self._active', 'self._latest')],
}

def run(folder, args):
    proc = subprocess.run([sys.executable, '-B', *args], cwd=folder, capture_output=True, text=True, timeout=30)
    output = proc.stdout + proc.stderr
    counts = re.findall(r'Ran (\d+) tests?', output)
    return {'args':args, 'returncode':proc.returncode, 'tests':int(counts[-1]) if counts else 0,
            'assertion_failure':'FAIL:' in output, 'output':output}

def search_variants(source_dir, use_reference=False):
    results = {}
    source = (ROOT/'cases/C02/search.py').read_text()
    for name, replacements in VARIANTS.items():
        with tempfile.TemporaryDirectory(prefix='property-grade-') as tmp:
            dest = Path(tmp)
            if not use_reference:
                shutil.copytree(source_dir, dest, dirs_exist_ok=True, ignore=shutil.ignore_patterns('__pycache__'))
            else:
                (dest/'test_reference.py').write_text(SEARCH_REFERENCE)
            changed = source
            for before, after in replacements:
                assert before in changed, (name, before)
                changed = changed.replace(before, after)
            compile(changed, 'search.py', 'exec')
            (dest/'search.py').write_text(changed)
            results[name] = run(dest, ['-m','unittest','discover','-v'])
    return results

def preflight():
    results = {'search_reference': search_variants(None, True), 'review_baselines':{}}
    for case in ('C03','C05','C08'):
        results['review_baselines'][case] = run(ROOT/'cases'/case, ['-m','unittest','discover','-v'])
    results['review_baselines']['C04'] = run(ROOT/'cases/C04', ['-O','check_rules.py'])
    results['review_baselines']['C05_optimized'] = run(ROOT/'cases/C05', ['-O','-m','unittest','discover','-v'])
    for name, record in results['search_reference'].items():
        expected_red = name.startswith('fault_')
        assert (record['returncode'] != 0 and record['assertion_failure']) if expected_red else record['returncode'] == 0, name
    assert all(r['returncode']==0 for r in results['review_baselines'].values())
    return results

def grade(run_dir):
    work = run_dir/'work'
    results = {'booking_submitted':run(work/'C01',['-m','unittest','discover','-v']),
               'search_variants':search_variants(work/'C02'), 'preserved_inputs':{}}
    with tempfile.TemporaryDirectory(prefix='booking-grade-') as tmp:
        dest = Path(tmp)
        shutil.copytree(work/'C01', dest, dirs_exist_ok=True, ignore=shutil.ignore_patterns('__pycache__'))
        (dest/'test_public_contract.py').write_text(BOOKING_CONTRACT)
        results['booking_contract'] = run(dest,['-m','unittest','test_public_contract','-v'])
    for original in (ROOT/'cases').rglob('*'):
        if not original.is_file(): continue
        relative = original.relative_to(ROOT/'cases')
        if relative.parts[0]=='C01' and relative.name=='booking.py': continue
        submitted = work/relative
        results['preserved_inputs'][relative.as_posix()] = submitted.is_file() and submitted.read_bytes()==original.read_bytes()
    return results

if __name__=='__main__':
    if sys.argv[1]=='preflight':
        result = preflight()
        out=ROOT/'fixture-preflight.json'
    else:
        run_dir=Path(sys.argv[1])
        result=grade(run_dir)
        out=run_dir/'mechanical-results.json'
    out.write_text(json.dumps(result,indent=2)+'\n')
    print(out)
