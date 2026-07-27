import unittest

from tests.helpers.skill_artifacts import (
    PLAIN_LANGUAGE_SKILL_PATH,
    REPO_ROOT,
    SCIENTIFIC_REFERENCE_PATH,
    extract_frontmatter,
    frontmatter_list,
    frontmatter_scalar,
    read_text,
)


def normalize_markdown(text):
    return " ".join(text.split())


class PlainLanguageHumanizerArtifactTests(unittest.TestCase):
    def setUp(self):
        self.skill_markdown = read_text(PLAIN_LANGUAGE_SKILL_PATH)
        self.normalized_skill = normalize_markdown(self.skill_markdown)
        self.frontmatter = extract_frontmatter(self.skill_markdown)
        self.normalized_frontmatter = normalize_markdown(self.frontmatter.lower())

    def test_frontmatter_identifies_the_skill_and_trigger_boundary(self):
        self.assertEqual(frontmatter_scalar(self.frontmatter, "name"), "plain-language-humanizer")
        self.assertEqual(frontmatter_scalar(self.frontmatter, "version"), "1.0.0")
        self.assertEqual(frontmatter_scalar(self.frontmatter, "license"), "MIT")
        self.assertEqual(
            frontmatter_list(self.frontmatter, "allowed-tools"),
            ["Read", "Write", "Edit", "Grep", "Glob", "AskUserQuestion"],
        )
        for term in (
            "`$plain-language-humanizer`",
            "plain language",
            "nontechnical reader",
            "reduce jargon",
            "explain",
            "editorial-humanizer",
            "faithful-humanizer",
            "troubleshooting",
            "fact-checking",
            "ai-detector",
        ):
            self.assertIn(term, self.normalized_frontmatter)

    def test_mode_routing_is_deterministic(self):
        for term in (
            "Rewrite mode is the default",
            "An explicitly named mode always wins",
            "Explain mode",
            "No mode specified selects Rewrite",
            "Explanation:",
        ):
            self.assertIn(term, self.normalized_skill)

    def test_technical_ledger_and_protected_literals_are_required(self):
        for term in (
            "technical-content ledger",
            "conditions, dependencies, and prerequisites",
            "warnings, failure states, and escalation conditions",
            "code, commands, flags, identifiers, configuration keys",
            "API names, schema fields, error messages",
            "procedural and operational order",
        ):
            self.assertIn(term, self.normalized_skill)

    def test_plain_language_rules_preserve_precision(self):
        for term in (
            "Necessary technical term",
            "Unnecessary jargon",
            "Ambiguous or context-dependent term",
            "define each term once",
            "shortest output that remains complete and accurate",
            "Every added sentence",
        ):
            self.assertIn(term, self.normalized_skill)

    def test_high_stakes_domains_and_scientific_reference_are_present(self):
        self.assertIn("../references/registers/scientific-writing.md", self.skill_markdown)
        for term in ("scientific", "medical", "legal", "financial", "security"):
            self.assertIn(term, self.normalized_skill.lower())
        scientific_reference = normalize_markdown(read_text(SCIENTIFIC_REFERENCE_PATH))
        self.assertIn("Plain Language Humanizer", scientific_reference)

    def test_output_contracts_are_exact(self):
        for term in (
            "Return only the rewrite",
            "Return only the explanation",
            "labeled exactly `Explanation:`",
            "bidirectional content check",
        ):
            self.assertIn(term, self.normalized_skill)


if __name__ == "__main__":
    unittest.main()
