import unittest

from tests.helpers.skill_artifacts import (
    PLAIN_LANGUAGE_SKILL_PATH,
    REPO_ROOT,
    SCIENTIFIC_REFERENCE_PATH,
    extract_frontmatter,
    frontmatter_list,
    frontmatter_scalar,
    load_fixture_cases,
    read_text,
)


def normalize_markdown(text):
    return " ".join(text.split())


REQUIRED_HEADINGS = [
    "# Plain Language Humanizer: Technical Meaning in Plain Language",
    "## Purpose",
    "## Direct distinction from the other Humanizers",
    "## Audience",
    "## Deterministic mode selection",
    "## Shared technical-preservation contract",
    "## Technical-content ledger",
    "## Protected literals",
    "## Language classification",
    "## Rewrite mode",
    "## Explain mode",
    "## Combined requests",
    "## Anti-bloat contract",
    "## High-stakes technical content",
    "## Scientific and academic profile",
    "## Missing or conflicting context",
    "## Rewrite workflow",
    "## Explain workflow",
    "## Final bidirectional content check",
    "## Output",
    "## Examples",
]


class PlainLanguageHumanizerArtifactTests(unittest.TestCase):
    def setUp(self):
        self.skill_markdown = read_text(PLAIN_LANGUAGE_SKILL_PATH)
        self.normalized_skill = normalize_markdown(self.skill_markdown)
        self.frontmatter = extract_frontmatter(self.skill_markdown)
        self.normalized_frontmatter = normalize_markdown(self.frontmatter.lower())
        self.fixture_cases = {case["id"]: case for case in load_fixture_cases()}
        self.public_artifacts = {
            "skill": self.skill_markdown,
            "readme": read_text(REPO_ROOT / "README.md"),
            "examples": read_text(REPO_ROOT / "docs" / "skill-examples.md"),
        }

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

    def test_canonical_definition_examples_align_across_public_artifacts(self):
        for case_id in (
            "plain_language_api_rewrite",
            "plain_language_legal_obligation",
            "plain_language_webhook_explain",
            "plain_language_protected_procedure",
            "plain_language_scientific_boundary",
        ):
            with self.subTest(case=case_id):
                output = self.fixture_cases[case_id]["passing_output"]
                self.assertIn(output, self.skill_markdown)
                self.assertIn(output, self.public_artifacts["examples"])

    def test_required_headings_are_ordered_and_skill_stays_under_line_limit(self):
        actual_headings = [
            line
            for line in self.skill_markdown.splitlines()
            if line.startswith(("# ", "## "))
        ]
        self.assertEqual(actual_headings, REQUIRED_HEADINGS)
        self.assertLess(len(self.skill_markdown.splitlines()), 500)

    def test_task_1_example_sources_are_retained_exactly(self):
        for case_id in (
            "plain_language_api_rewrite",
            "plain_language_webhook_explain",
            "plain_language_protected_procedure",
            "plain_language_scientific_boundary",
            "plain_language_already_clear",
        ):
            with self.subTest(case=case_id):
                self.assertIn(self.fixture_cases[case_id]["source"], self.skill_markdown)

    def test_output_contract_rejects_generic_shape_escape_clauses(self):
        for artifact_name, artifact in self.public_artifacts.items():
            with self.subTest(artifact=artifact_name):
                normalized_lower = normalize_markdown(artifact).lower()
                for escape_clause in (
                    "unless the user requests another output shape",
                    "unless the user requested another shape",
                ):
                    self.assertNotIn(escape_clause, normalized_lower)

    def test_explanatory_devices_have_the_complete_safety_boundary(self):
        normalized_lower = self.normalized_skill.lower()
        for term in (
            "example or analogy",
            "explicitly requests",
            "materially needed",
            "label it as explanatory",
            "rather than a source fact",
            "retain the technical term",
            "protected literals",
            "exact equivalence",
            "source-specific behavior, guarantees, numbers, consequences, or advice",
            "extra caution",
        ):
            self.assertIn(term, normalized_lower)

    def test_explanatory_device_authority_aligns_across_public_artifacts(self):
        for artifact_name, artifact in self.public_artifacts.items():
            with self.subTest(artifact=artifact_name):
                normalized_lower = normalize_markdown(artifact).lower()
                self.assertRegex(
                    normalized_lower,
                    r"\b(?:asks?|requests?|requested)\b",
                )
                self.assertIn("materially needed", normalized_lower)


if __name__ == "__main__":
    unittest.main()
