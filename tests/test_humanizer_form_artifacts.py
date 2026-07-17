import json
import unittest

from tests.helpers.skill_artifacts import (
    MANIFEST_PATH,
    REPO_ROOT,
    SKILL_PATH,
    extract_frontmatter,
    frontmatter_list,
    frontmatter_scalar,
    read_text,
)


FORM_SKILL_PATH = REPO_ROOT / "skills" / "humanizer-form" / "SKILL.md"
RESEARCH_PATH = REPO_ROOT / "docs" / "humanizer-form-research.md"


def normalize_markdown(text):
    return " ".join(text.split())


class HumanizerFormArtifactTests(unittest.TestCase):
    def setUp(self):
        self.skill_markdown = read_text(FORM_SKILL_PATH)
        self.normalized_skill = normalize_markdown(self.skill_markdown)
        self.frontmatter = extract_frontmatter(self.skill_markdown)
        self.normalized_frontmatter = normalize_markdown(self.frontmatter.lower())
        self.research_markdown = read_text(RESEARCH_PATH)
        self.normalized_research = normalize_markdown(self.research_markdown)
        self.manifest = json.loads(read_text(MANIFEST_PATH))

    def test_required_files_exist_and_fit_plugin_skill_root(self):
        self.assertTrue(FORM_SKILL_PATH.exists(), FORM_SKILL_PATH)
        self.assertTrue(RESEARCH_PATH.exists(), RESEARCH_PATH)
        self.assertEqual(self.manifest["skills"], "./skills/")
        self.assertEqual(FORM_SKILL_PATH.parent.parent, REPO_ROOT / "skills")

    def test_frontmatter_identifies_a_separate_mit_skill(self):
        self.assertEqual(frontmatter_scalar(self.frontmatter, "name"), "humanizer-form")
        self.assertEqual(frontmatter_scalar(self.frontmatter, "version"), "1.0.0")
        self.assertEqual(frontmatter_scalar(self.frontmatter, "license"), "MIT")
        self.assertEqual(
            frontmatter_list(self.frontmatter, "allowed-tools"),
            ["Read", "Write", "Edit", "Grep", "Glob"],
        )

    def test_description_triggers_form_only_requests_and_excludes_other_tasks(self):
        required_terms = [
            "humanize form only",
            "preserve every claim and opinion",
            "make minimal edits",
            "without adding",
            "fact-checking",
            "substantive editing",
            "ai-detector",
        ]
        for required_term in required_terms:
            with self.subTest(term=required_term):
                self.assertIn(required_term, self.normalized_frontmatter)

    def test_skill_is_leaner_than_the_existing_catalog_skill(self):
        form_lines = len(self.skill_markdown.splitlines())
        existing_lines = len(read_text(SKILL_PATH).splitlines())
        self.assertLess(form_lines, existing_lines / 2)
        self.assertNotIn("references/", self.skill_markdown)

    def test_contract_preserves_local_semantics_not_only_core_meaning(self):
        required_invariants = [
            "Propositions and coverage",
            "Stance and opinion",
            "Modality and certainty",
            "Polarity and negation",
            "Scope and quantity",
            "Logical relations",
            "Attribution",
            "Chronology",
            "Emphasis",
            "Structure-bearing content",
        ]
        for required_invariant in required_invariants:
            with self.subTest(invariant=required_invariant):
                self.assertIn(required_invariant, self.normalized_skill)

    def test_contract_preserves_exact_anchors(self):
        required_anchors = [
            "Names, organizations, products, places, and defined terms",
            "Numbers, dates, times, percentages, ranges, prices, units, and measurements",
            "URLs, email addresses, citations, footnotes, and reference labels",
            "Quotes and their attributions",
            "Code, commands, flags, identifiers, API names, version numbers, and file paths",
            "Preserve list items even when a list happens to contain three items",
        ]
        for required_anchor in required_anchors:
            with self.subTest(anchor=required_anchor):
                self.assertIn(required_anchor, self.normalized_skill)

    def test_forbidden_edits_cover_common_substance_drift(self):
        required_rules = [
            "Add, delete, merge, or replace a claim",
            "Invent names, numbers, studies, citations, examples, anecdotes",
            "Replace vague attribution with a specific source",
            "Delete an unsupported, promotional, vague, or disputable claim",
            "Fact-check, correct, challenge, endorse, neutralize, or rebut",
            "Add first-person experience, feelings, humor, slang, edge, stakes, or personality",
            "Turn neutral prose into opinionated prose or opinionated prose into neutral prose",
            "Change `may` to `will`, `some` to `most`, `associated with` to `caused`",
            "Compress the text into a summary or expand it with explanation",
            "Optimize for perplexity, burstiness, an AI score, or any detector outcome",
        ]
        for required_rule in required_rules:
            with self.subTest(rule=required_rule):
                self.assertIn(required_rule, self.normalized_skill)

    def test_skill_uses_contextual_judgment_instead_of_blanket_style_bans(self):
        self.assertIn(
            "Em dashes, passive voice, adverbs, three-item lists, title case, technical jargon, and",
            self.normalized_skill,
        )
        self.assertIn(
            "Change them only when they make this particular passage less clear or less natural",
            self.normalized_skill,
        )
        forbidden_blanket_rules = [
            "No em dashes.",
            "No forced rule-of-three lists.",
            "Have opinions.",
            "Add soul",
            "all adverbs",
            "Two items beat three",
        ]
        for forbidden_rule in forbidden_blanket_rules:
            with self.subTest(rule=forbidden_rule):
                self.assertNotIn(forbidden_rule, self.normalized_skill)

    def test_workflow_requires_a_bidirectional_semantic_diff_and_restore_on_doubt(self):
        required_steps = [
            "Map every source proposition to the rewrite and every rewrite proposition back to the source",
            "If equivalence is uncertain, keep or restore the original wording",
            "No source claim disappeared, and no new claim appeared",
            "no style rule was applied for its own sake",
        ]
        for required_step in required_steps:
            with self.subTest(step=required_step):
                self.assertIn(required_step, self.normalized_skill)

    def test_output_is_rewrite_only_by_default_and_has_no_score(self):
        self.assertIn(
            "Return only the rewritten text. Do not add a preamble, score, change log, or closing invitation",
            self.normalized_skill,
        )
        self.assertIn("Do not assign an AI-likeness score", self.normalized_skill)
        self.assertIn("`Form changes`", self.skill_markdown)
        self.assertIn("`Preservation notes`", self.skill_markdown)

    def test_examples_preserve_hedges_scope_attribution_and_opinion(self):
        expected_examples = [
            "Importantly, the platform may reduce setup time for some teams.",
            "Industry reports suggest that adoption is accelerating",
            "The system is a robust foundation for scalable workflows",
            "I find the change unsettling, although it may improve efficiency.",
            "The policy improves outcomes for patients.",
            "That removes the attribution, hedge, and scope",
            "Do not add a named study",
        ]
        for expected_example in expected_examples:
            with self.subTest(example=expected_example):
                self.assertIn(expected_example, self.normalized_skill)

    def test_research_documents_a_broad_comparison_and_rejected_choices(self):
        reviewed_projects = [
            "CoveMB/humanizer-skill-plugin",
            "blader/humanizer",
            "jpeggdev/humanize-writing",
            "Aboudjem/humanizer-skill",
            "hardikpandya/stop-slop",
            "apurvrdx1/tagore",
            "stephenturner/skill-deslop",
            "theclaymethod/unslop",
            "conorbronsdon/avoid-ai-writing",
            "brandonwise/humanizer",
            "softaworks/agent-toolkit",
            "humanizerai/agent-skills",
        ]
        for reviewed_project in reviewed_projects:
            with self.subTest(project=reviewed_project):
                self.assertIn(reviewed_project, self.normalized_research)

        required_findings = [
            '"Preserve meaning" is too weak as a safeguard',
            "Pattern catalogs are better diagnostic cues than hard rules",
            "Unsupported content must remain content",
            "Minimality is a preservation mechanism",
            "Detector optimization should be excluded",
            "Bidirectional semantic diff",
        ]
        for required_finding in required_findings:
            with self.subTest(finding=required_finding):
                self.assertIn(required_finding, self.normalized_research)


if __name__ == "__main__":
    unittest.main()
