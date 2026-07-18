import json
import unittest

from tests.helpers.skill_artifacts import (
    MANIFEST_PATH,
    REPO_ROOT,
    SCIENTIFIC_REFERENCE_PATH,
    SKILL_PATH,
    extract_frontmatter,
    frontmatter_list,
    frontmatter_scalar,
    read_text,
)


FAITHFUL_SKILL_PATH = REPO_ROOT / "skills" / "faithful-humanizer" / "SKILL.md"
RESEARCH_PATH = REPO_ROOT / "docs" / "faithful-humanizer-research.md"


def normalize_markdown(text):
    return " ".join(text.split())


class FaithfulHumanizerArtifactTests(unittest.TestCase):
    def setUp(self):
        self.skill_markdown = read_text(FAITHFUL_SKILL_PATH)
        self.normalized_skill = normalize_markdown(self.skill_markdown)
        self.frontmatter = extract_frontmatter(self.skill_markdown)
        self.normalized_frontmatter = normalize_markdown(self.frontmatter.lower())
        self.research_markdown = read_text(RESEARCH_PATH)
        self.normalized_research = normalize_markdown(self.research_markdown)
        self.manifest = json.loads(read_text(MANIFEST_PATH))

    def test_required_files_exist_and_fit_plugin_skill_root(self):
        self.assertTrue(FAITHFUL_SKILL_PATH.exists(), FAITHFUL_SKILL_PATH)
        self.assertTrue(RESEARCH_PATH.exists(), RESEARCH_PATH)
        self.assertTrue(SCIENTIFIC_REFERENCE_PATH.exists(), SCIENTIFIC_REFERENCE_PATH)
        self.assertEqual(self.manifest["skills"], "./skills/")
        self.assertEqual(FAITHFUL_SKILL_PATH.parent.parent, REPO_ROOT / "skills")

    def test_frontmatter_identifies_a_separate_mit_skill(self):
        self.assertEqual(
            frontmatter_scalar(self.frontmatter, "name"),
            "faithful-humanizer",
        )
        self.assertEqual(frontmatter_scalar(self.frontmatter, "version"), "1.0.0")
        self.assertEqual(frontmatter_scalar(self.frontmatter, "license"), "MIT")
        self.assertEqual(
            frontmatter_list(self.frontmatter, "allowed-tools"),
            ["Read", "Write", "Edit", "Grep", "Glob"],
        )

    def test_description_triggers_faithful_requests_and_excludes_other_tasks(self):
        required_terms = [
            "preserve every claim and opinion",
            "humanize form only",
            "make minimal edits",
            "without adding",
            "fact-checking",
            "broader editorial cleanup",
            "editorial-humanizer",
            "ai-detector",
        ]
        for required_term in required_terms:
            with self.subTest(term=required_term):
                self.assertIn(required_term, self.normalized_frontmatter)

    def test_skill_is_leaner_than_editorial_humanizer(self):
        faithful_lines = len(self.skill_markdown.splitlines())
        editorial_lines = len(read_text(SKILL_PATH).splitlines())
        self.assertLess(faithful_lines, editorial_lines)
        self.assertIn("../references/registers/scientific-writing.md", self.skill_markdown)
        self.assertNotIn("pattern-catalog.md", self.skill_markdown)

    def test_faithful_is_local_but_not_timid(self):
        for term in [
            "Faithful does not mean literal or timid",
            "rewrite every problematic span for a clearly more natural result",
            "Minimal means localized",
            "Do not return the source unchanged merely because preservation is strict",
            "The result should be materially less formulaic, not merely proofread",
            "choose the one that removes more of the local AI-shaped form",
        ]:
            with self.subTest(term=term):
                self.assertIn(term, self.normalized_skill)

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
        for invariant in required_invariants:
            with self.subTest(invariant=invariant):
                self.assertIn(invariant, self.normalized_skill)

    def test_contract_preserves_exact_anchors(self):
        required_anchors = [
            "Names, organizations, products, places, and defined terms",
            "Numbers, dates, times, percentages, ranges, prices, units, and measurements",
            "URLs, email addresses, citations, footnotes, and reference labels",
            "Quotes and their attributions",
            "Code, commands, flags, identifiers, API names, version numbers, and file paths",
            "Preserve list items even when a list happens to contain three items",
        ]
        for anchor in required_anchors:
            with self.subTest(anchor=anchor):
                self.assertIn(anchor, self.normalized_skill)

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
        for rule in required_rules:
            with self.subTest(rule=rule):
                self.assertIn(rule, self.normalized_skill)

    def test_skill_uses_contextual_judgment_instead_of_blanket_style_bans(self):
        self.assertIn(
            "Em dashes, passive voice, adverbs, three-item lists, title case, technical jargon, and",
            self.normalized_skill,
        )
        self.assertIn(
            "Change them only when they make this particular passage less clear or less natural",
            self.normalized_skill,
        )
        for forbidden_rule in [
            "No em dashes.",
            "No forced rule-of-three lists.",
            "Have opinions.",
            "Add soul",
            "all adverbs",
            "Two items beat three",
        ]:
            with self.subTest(rule=forbidden_rule):
                self.assertNotIn(forbidden_rule, self.normalized_skill)

    def test_scientific_register_preserves_precision_and_epistemic_status(self):
        scientific_reference = normalize_markdown(read_text(SCIENTIFIC_REFERENCE_PATH))
        for term in [
            "Scientific and academic register preservation",
            "preserve technical and disciplinary terminology",
            "preserve conventional hedging, qualification, uncertainty, and citation language",
            "Do not change `was measured` to `we measured`",
            "Do not vary an exact technical term merely for rhythm",
        ]:
            with self.subTest(term=term):
                self.assertIn(term, self.normalized_skill)
        for term in [
            "Do not turn an observed association into a cause",
            "Precision outranks lexical variety",
            "Keep citation markers and their associated claims together",
        ]:
            with self.subTest(term=term):
                self.assertIn(term, scientific_reference)

    def test_workflow_requires_bidirectional_semantic_diff_and_restore_on_doubt(self):
        for step in [
            "Map every source proposition to the rewrite and every rewrite proposition back to the source",
            "If equivalence is uncertain, keep or restore the original wording",
            "No source claim disappeared, and no new claim appeared",
            "no style rule was applied for its own sake",
            "Every genuine form problem with a safe equivalent was repaired",
        ]:
            with self.subTest(step=step):
                self.assertIn(step, self.normalized_skill)

    def test_output_is_rewrite_only_by_default_and_has_no_score(self):
        self.assertIn(
            "Return only the rewritten text. Do not add a preamble, score, change log, or closing invitation",
            self.normalized_skill,
        )
        self.assertIn("Do not assign an AI-likeness score", self.normalized_skill)
        self.assertIn("`Form changes`", self.skill_markdown)
        self.assertIn("`Preservation notes`", self.skill_markdown)

    def test_skill_explicitly_contrasts_editorial_humanizer(self):
        for term in [
            "Use **Editorial Humanizer** instead",
            "broader anti-slop editing",
            "removal of weak or generic material",
            "structural reshaping",
            "editorial-quality audit and score",
        ]:
            with self.subTest(term=term):
                self.assertIn(term, self.normalized_skill)

    def test_examples_preserve_hedges_scope_attribution_and_opinion(self):
        expected_examples = [
            "Importantly, the platform may reduce setup time for some teams.",
            "Industry reports suggest that adoption is accelerating",
            "The system is a robust foundation for scalable workflows",
            "I find the change unsettling, although it may improve efficiency.",
            "The policy improves outcomes for patients.",
            "That removes the attribution, hedge, and scope",
            "Do not add a named study",
            "The committee is currently evaluating the proposal.",
        ]
        for example in expected_examples:
            with self.subTest(example=example):
                self.assertIn(example, self.normalized_skill)

    def test_research_documents_names_and_rejected_choices(self):
        for project in [
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
        ]:
            with self.subTest(project=project):
                self.assertIn(project, self.normalized_research)

        for finding in [
            "Naming conclusion",
            "Editorial Humanizer",
            "Faithful Humanizer",
            "“Preserve meaning” is too weak",
            "Pattern catalogs are diagnostic cues, not universal rules",
            "Unsupported content must remain content",
            "Minimality is a preservation mechanism",
            "Detector optimization should be excluded",
            "Bidirectional semantic diff",
        ]:
            with self.subTest(finding=finding):
                self.assertIn(finding, self.normalized_research)


if __name__ == "__main__":
    unittest.main()
