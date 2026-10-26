#!/usr/bin/env python3
"""Freeze or verify authored follow-up material and preflight evidence."""
import argparse
import datetime
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SNAPSHOT = ROOT / 'grading/freeze_manifest.json'


def files():
    for path in sorted(ROOT.rglob('*')):
        relative = path.relative_to(ROOT)
        if not path.is_file() or path == SNAPSHOT:
            continue
        if any(part in ('.scratch', '__pycache__') for part in relative.parts) or path.suffix == '.pyc':
            continue
        yield relative.as_posix(), hashlib.sha256(path.read_bytes()).hexdigest()


def write_snapshot():
    data = {
        'created_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'evaluation_kind': 'directed_followup_on_previously_exposed_tasks',
        'authored_before_followup_agent_runs': True,
        'fresh_holdout': False,
        'part_of_original_preregistered_comparison': False,
        'exclusions': ['This self-referential manifest', 'Transient .scratch execution copies', '__pycache__ and .pyc'],
        'sha256': dict(files()),
    }
    SNAPSHOT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    if args.check:
        recorded = json.loads(SNAPSHOT.read_text(encoding='utf-8'))['sha256']
        actual = dict(files())
        changed = sorted(path for path in recorded if actual.get(path) != recorded[path])
        added = sorted(set(actual) - set(recorded))
        print(json.dumps({'passed': not changed and not added, 'recorded_files':len(recorded), 'changed_or_missing':changed, 'added':added}, indent=2))
        return int(bool(changed or added))
    data = write_snapshot()
    print(json.dumps({'frozen_files':len(data['sha256']), 'manifest':str(SNAPSHOT)}, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
