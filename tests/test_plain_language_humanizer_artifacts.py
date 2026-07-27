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

TASK_1_EXAMPLE_SOURCES = [
    "The API enforces a per-client rate limit of 120 requests per minute and returns HTTP 429 for requests above the threshold.",
    "When an invoice is paid, Ledger emits an `invoice.paid` webhook to the configured HTTPS endpoint. Delivery is retried with exponential backoff for up to 24 hours.",
    "Run `atlas migrate --dry-run` before `atlas migrate --apply`. Do not use `--apply` if validation reports an incompatible schema. If the second command fails, restore `/srv/atlas/schema.json`.",
    "Smith et al. (2024) reported a hazard ratio of 0.78 (95% CI 0.61–0.99). This association does not establish causality.",
    "Run `make test` before deployment. Stop if any test fails.",
]


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

    def test_required_headings_are_ordered_and_skill_stays_under_line_limit(self):
        actual_headings = [
            line
            for line in self.skill_markdown.splitlines()
            if line.startswith(("# ", "## "))
        ]
        self.assertEqual(actual_headings, REQUIRED_HEADINGS)
        self.assertLess(len(self.skill_markdown.splitlines()), 500)

    def test_task_1_example_sources_are_retained_exactly(self):
        for source in TASK_1_EXAMPLE_SOURCES:
            self.assertIn(source, self.skill_markdown)

    def test_output_contract_rejects_generic_shape_escape_clauses(self):
        normalized_lower = self.normalized_skill.lower()
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


if __name__ == "__main__":
    unittest.main()
