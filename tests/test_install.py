import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
INSTALLER = ROOT / "scripts/install.py"
CORE = {"khorikov-unit-testing", "requirements-tdd", "test-quality-review", "state-machine-verification"}


class InstallationTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.dest = self.root / "skills"

    def run_install(self, *args, success=True):
        result = subprocess.run([sys.executable, str(INSTALLER), "--dest", str(self.dest), *args],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode == 0, success, result.stdout + result.stderr)
        return result

    def test_preview_makes_no_installation_directory(self):
        self.run_install()
        self.assertFalse(self.dest.exists())

    def test_default_install_contains_four_complete_core_skills(self):
        self.run_install("--apply")
        self.assertEqual({p.name for p in self.dest.iterdir()}, CORE)
        self.assertTrue((self.dest / "state-machine-verification/references/design-checks.md").is_file())
        self.assertFalse((self.dest / "state-machine-verification/references/vance-android.md").exists())

    def test_conflict_is_reported_before_any_skill_is_installed(self):
        existing = self.dest / "state-machine-verification"
        existing.mkdir(parents=True)
        (existing / "user-note.txt").write_text("preserve my edits")
        self.run_install("--apply", success=False)
        self.assertEqual({p.name for p in self.dest.iterdir()}, {existing.name})
        self.assertEqual((existing / "user-note.txt").read_text(), "preserve my edits")

    def test_replace_keeps_a_recoverable_copy_and_repeat_is_unchanged(self):
        existing = self.dest / "state-machine-verification"
        existing.mkdir(parents=True)
        (existing / "user-note.txt").write_text("preserve my edits")
        self.run_install("--skill", existing.name, "--apply", "--replace")
        backups = list((self.root / "skill-backups").glob("*/state-machine-verification/user-note.txt"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_text(), "preserve my edits")
        self.assertTrue((existing / "SKILL.md").is_file())
        result = self.run_install("--skill", existing.name, "--apply")
        self.assertIn("unchanged:", result.stdout)
        self.assertEqual(list((self.root / "skill-backups").glob("*/state-machine-verification/user-note.txt")), backups)

    def test_matt_install_carries_license_and_attribution(self):
        self.run_install("--apply", "--with-matt")
        self.assertEqual(len(list(self.dest.iterdir())), 6)
        for name in ("domain-modeling", "codebase-design"):
            self.assertIn("Matt Pocock", (self.dest / name / "LICENSE").read_text())
            self.assertIn("5beb35b", (self.dest / name / "UPSTREAM.md").read_text())

    @unittest.skipIf(os.name == "nt", "Symlinks require platform-specific privileges")
    def test_symlink_target_is_preserved_and_outside_files_untouched(self):
        outside = self.root / "outside"
        outside.mkdir()
        (outside / "keep.txt").write_text("untouched")
        self.dest.mkdir()
        target = self.dest / "state-machine-verification"
        target.symlink_to(outside, target_is_directory=True)
        self.run_install("--skill", target.name, "--apply", "--replace", success=False)
        self.assertTrue(target.is_symlink())
        self.assertEqual(list(outside.iterdir()), [outside / "keep.txt"])

    def test_unknown_skill_does_not_create_destination(self):
        self.run_install("--skill", "not-a-skill", "--apply", success=False)
        self.assertFalse(self.dest.exists())


if __name__ == "__main__":
    unittest.main()
