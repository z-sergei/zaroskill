"""Check package structure, local references, portability and pinned vendor hashes."""

import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def main():
    errors = []
    provenance = json.loads((ROOT / "provenance.json").read_text())
    packages = sorted((ROOT / "skills").iterdir()) + sorted(
        p for p in (ROOT / "vendor/mattpocock").iterdir() if p.is_dir()
    )
    for package in packages:
        skill = package / "SKILL.md"
        if not skill.is_file():
            errors.append(f"Missing entrypoint: {package.relative_to(ROOT)}")
            continue
        text = skill.read_text()
        parts = text.split("---", 2)
        if len(parts) != 3 or parts[0].strip():
            errors.append(f"Missing frontmatter: {package.name}")
            continue
        fields = dict(re.findall(r"^([a-z_-]+):\s*(.+)$", parts[1], re.M))
        if fields.get("name", "").strip("\"'") != package.name or not fields.get("description"):
            errors.append(f"Name or description mismatch: {package.name}")
        for path in package.rglob("*"):
            if path.is_symlink():
                errors.append(f"Symlink in package: {path.relative_to(ROOT)}")
            if not path.is_file() or path.suffix not in (".md", ".yaml"):
                continue
            content = path.read_text()
            if re.search(r"/Users/|/home/|/private/tmp/|[A-Z]:\\\\Users\\\\", content):
                errors.append(f"Machine-specific path: {path.relative_to(ROOT)}")
            # Code fences may contain illustrative project links, not package dependencies.
            prose = re.sub(r"```.*?```", "", content, flags=re.S)
            for link in re.findall(r"\]\(([^)]+)\)", prose):
                link = link.split("#")[0]
                if not link or re.match(r"[a-z]+://", link):
                    continue
                target = (path.parent / link).resolve()
                if package.resolve() not in target.parents or not target.exists():
                    errors.append(f"Unbundled reference: {path.relative_to(ROOT)} -> {link}")
    for item in provenance["skills"]:
        if item["kind"] != "mattpocock":
            continue
        folder = ROOT / "vendor/mattpocock" / item["name"]
        actual = {str(p.relative_to(folder)): hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in folder.rglob("*") if p.is_file()}
        if actual != item["snapshot_files"]:
            errors.append(f"Vendor snapshot changed: {item['name']}; record an intentional upstream update")
    if errors:
        raise SystemExit("\n".join(errors))
    print(f"OK: {len(packages)} self-contained skills; local references and vendor snapshots verified.")
    print("These structural checks do not evaluate the quality of agent decisions.")


if __name__ == "__main__":
    main()
