import pathlib
import sys
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import install  # type: ignore  # noqa: E402
import uninstall  # type: ignore  # noqa: E402


class InstallHelpersTests(unittest.TestCase):
    def test_repo_contains_skill_directories(self):
        names = install.skill_names()

        self.assertEqual(
            names,
            [
                "background-supervisor-skill",
                "effort-calibration",
                "obsidian-memory-router",
                "obsidian-research-memory",
                "obsidian-writeback-ledger",
                "plan-review-collaboration",
            ],
        )

    def test_install_and_uninstall_round_trip(self):
        with tempfile.TemporaryDirectory() as tmp:
            claude_home = pathlib.Path(tmp)

            installed = install.install_skills(claude_home)
            removed = uninstall.uninstall_skills(claude_home)

            self.assertEqual([path.name for path in installed], install.skill_names())
            self.assertEqual([path.name for path in removed], install.skill_names())
            for name in install.skill_names():
                self.assertFalse((claude_home / "skills" / name).exists())


if __name__ == "__main__":
    unittest.main()
