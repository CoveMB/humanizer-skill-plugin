import unittest

import scripts.editorial_diagnostics as editorial_diagnostics
from scripts.editorial_diagnostics import analyze_text


class EditorialDiagnosticsTests(unittest.TestCase):
    def test_module_contract_is_advisory_only(self):
        self.assertIn("raw", editorial_diagnostics.__doc__.lower())
        self.assertIn("without scoring authorship or quality", editorial_diagnostics.__doc__)

    def test_reports_raw_advisory_evidence(self):
        text = (
            "Moreover, Atlas is a robust platform—an important platform. "
            "The platform works.\n\n"
            "- **Result:** Teams leverage the platform.\n\n"
            "Moreover, teams reviewed the result. The platform works."
        )

        diagnostics = analyze_text(text)

        self.assertEqual(diagnostics["em_dash_count"], 1)
        self.assertGreater(diagnostics["em_dashes_per_1000_words"], 0)
        self.assertEqual(diagnostics["bold_label_count"], 1)
        self.assertEqual(diagnostics["transition_counts"]["moreover"], 2)
        self.assertEqual(
            diagnostics["vocabulary_clusters"]["business_jargon"]["terms"],
            {"leverage": 1, "robust": 1},
        )
        self.assertEqual(
            diagnostics["vocabulary_clusters"]["significance_language"]["terms"],
            {"important": 1},
        )
        self.assertIn(
            {"ending": "the platform works", "count": 2},
            diagnostics["repeated_paragraph_endings"],
        )

    def test_does_not_emit_authorship_or_quality_verdicts(self):
        diagnostics = analyze_text("One ordinary sentence—with a deliberate dash.")
        serialized_keys = " ".join(diagnostics).lower()

        for forbidden_term in (
            "ai_score",
            "ai_probability",
            "authorship",
            "human_score",
            "passed",
            "quality_score",
            "verdict",
        ):
            with self.subTest(term=forbidden_term):
                self.assertNotIn(forbidden_term, serialized_keys)

    def test_empty_text_has_stable_zero_distributions(self):
        diagnostics = analyze_text("")

        self.assertEqual(diagnostics["word_count"], 0)
        self.assertEqual(diagnostics["sentence_word_counts"]["counts"], [])
        self.assertEqual(diagnostics["paragraph_word_counts"]["counts"], [])
        self.assertEqual(diagnostics["em_dashes_per_1000_words"], 0.0)


if __name__ == "__main__":
    unittest.main()
