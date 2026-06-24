import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "obsidian-research-memory" / "SKILL.md"


class EZSpecificityObsidianRoutingTests(unittest.TestCase):
    def test_skill_names_substrate_predictability_moc_first(self):
        text = SKILL.read_text(encoding="utf-8")

        self.assertIn(
            r"F:\Obsidian_Work_Memory\02_Experiments\Substrate_Predictability_MOC_20260602.md",
            text,
        )
        self.assertIn("Substrate predictability routing", text)
        self.assertIn("canonical dataset counts", text)
        self.assertIn("Phase 1 pair-level", text)
        self.assertIn("Phase 2 site-selectivity", text)
        self.assertIn("Phase-B / MORSE / SPECTRA", text)

    def test_skill_keeps_esp_protocol_guard(self):
        text = SKILL.read_text(encoding="utf-8")

        self.assertIn("ESP / EZSpecificity Protocol Guard", text)
        self.assertIn("released ESP direct inference", text)
        self.assertIn("same-data controls", text)
        self.assertIn("317,577 rows", text)


if __name__ == "__main__":
    unittest.main()
