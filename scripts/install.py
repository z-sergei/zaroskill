"""Preview or install self-contained skill copies. Python standard library only."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import tempfile
import uuid

ROOT = Path(__file__).resolve().parents[1]
CORE = ("khorikov-unit-testing", "requirements-tdd", "test-quality-review", "state-machine-verification")
MATT = ("domain-modeling", "codebase-design")


def package(name):
    base = ROOT / "skills" if name in CORE else ROOT / "vendor/mattpocock"
    source = base / name
    files = {}
    for path in sorted(source.rglob("*")):
        if path.is_symlink():
            raise ValueError(f"Package contains a symlink: {path}")
        if path.is_file():
            files[str(path.relative_to(source))] = path.read_bytes()
    if "SKILL.md" not in files:
        raise ValueError(f"Missing skill entrypoint: {name}")
    if name in MATT:
        upstream = json.loads((ROOT / "provenance.json").read_text())["mattpocock_upstream"]
        files["LICENSE"] = (ROOT / "vendor/mattpocock/LICENSE").read_bytes()
        files["UPSTREAM.md"] = (
            f"Matt Pocock skills {upstream['version']}\n\n"
            f"Source: {upstream['repository']}\n"
            f"Revision: {upstream['revision']}\n"
            "Upstream instructions are unchanged; MIT license is included.\n"
        ).encode()
    return files


def same_contents(target, files):
    if not target.is_dir() or target.is_symlink():
        return False
    actual = {}
    for path in target.rglob("*"):
        if path.is_symlink():
            return False
        if path.is_file():
            actual[str(path.relative_to(target))] = hashlib.sha256(path.read_bytes()).digest()
    return actual == {name: hashlib.sha256(data).digest() for name, data in files.items()}


def install(destination, names, *, apply=False, replace=False):
    destination = destination.expanduser().resolve()
    if destination == ROOT or ROOT in destination.parents:
        raise ValueError("Choose an installation directory outside the source repository")
    plan = []
    for name in dict.fromkeys(names):
        target = destination / name
        if target.is_symlink() or (target.exists() and not target.is_dir()):
            raise ValueError(f"Existing target is not a regular directory: {target}")
        files = package(name)
        action = "unchanged" if same_contents(target, files) else "replace" if target.exists() else "install"
        plan.append((name, target, files, action))
    for name, target, files, action in plan:
        print(f"{action}: {target}")
    if not apply:
        print("Preview only. Add --apply to write; replacements also require --replace.")
        return
    conflicts = [name for name, _, _, action in plan if action == "replace"]
    if conflicts and not replace:
        raise ValueError("Existing skills differ; review the preview and use --replace: " + ", ".join(conflicts))
    if all(action == "unchanged" for _, _, _, action in plan):
        return
    destination.mkdir(parents=True, exist_ok=True)
    backup_root = destination.parent / "skill-backups" / (
        "zaroskill-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8]
    )
    for name, target, files, action in plan:
        if action == "unchanged":
            continue
        with tempfile.TemporaryDirectory(prefix=".zaroskill-", dir=destination) as temporary:
            staged = Path(temporary) / name
            staged.mkdir()
            for relative, data in files.items():
                path = staged / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(data)
            previous = None
            if action == "replace":
                backup_root.mkdir(parents=True, exist_ok=True)
                previous = backup_root / name
                target.rename(previous)
            elif target.exists() or target.is_symlink():
                raise ValueError(f"Target appeared during installation: {target}")
            try:
                staged.rename(target)
            except BaseException:
                if previous is not None and not target.exists():
                    previous.rename(target)
                raise
            if previous is not None:
                print(f"backup: {previous}")
    print("Installed copies are ready. New conversations may be needed to refresh skill discovery.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dest", type=Path, default=Path(os.environ.get("CODEX_HOME") or Path.home() / ".codex") / "skills")
    parser.add_argument("--skill", action="append", choices=CORE + MATT, help="Select a skill; repeat to select several")
    parser.add_argument("--with-matt", action="store_true", help="Include both vendored Matt skills with the default core set")
    parser.add_argument("--apply", action="store_true", help="Write the previewed installation")
    parser.add_argument("--replace", action="store_true", help="Back up and replace different existing skill directories")
    args = parser.parse_args()
    names = args.skill or list(CORE) + (list(MATT) if args.with_matt else [])
    try:
        install(args.dest, names, apply=args.apply, replace=args.replace)
    except (ValueError, OSError) as error:
        parser.exit(2, f"Installation stopped: {error}\n")


if __name__ == "__main__":
    main()
