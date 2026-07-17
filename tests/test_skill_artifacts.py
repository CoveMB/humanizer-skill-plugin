import json
import unittest

from tests.helpers.skill_artifacts import (
    MANIFEST_PATH,
    MARKETPLACE_PATH,
    REFERENCE_PATH,
    REPO_ROOT,
    SKILL_PATH,
    extract_frontmatter,
    frontmatter_list,
    frontmatter_scalar,
    read_text,
)


WORKFLOW_PATH = REPO_ROOT / ".github" / "workflows" / "test.yml"
LIVE_EVAL_WORKFLOW_PATH = REPO_ROOT / ".github" / "workflows" / "live-eval.yml"
FAITHFUL_SKILL_PATH = REPO_ROOT / "skills" / "faithful-humanizer" / "SKILL.md"
RESEARCH_PATH = REPO_ROOT / "docs" / "faithful-humanizer-research.md"


class EditorialHumanizerArtifactTests(unittest.TestCase):
    def setUp(self):
        self.skill_markdown = read_text(SKILL_PATH)
        self.frontmatter = extract_frontmatter(self.skill_markdown)
        self.manifest = json.loads(read_text(MANIFEST_PATH))
        self.marketplace = json.loads(read_text(MARKETPLACE_PATH))
        self.reference_markdown = read_text(REFERENCE_PATH)
        self.readme_markdown = read_text(REPO_ROOT / "README.md")

    def test_required_files_exist(self):
        for path in [
            MANIFEST_PATH,
            MARKETPLACE_PATH,
            SKILL_PATH,
            REFERENCE_PATH,
            FAITHFUL_SKILL_PATH,
            RESEARCH_PATH,
        ]:
            with self.subTest(path=path):
                self.assertTrue(path.exists(), path)

    def test_manifest_points_at_skill_directory(self):
        self.assertEqual(self.manifest["skills"], "./skills/")
        self.assertEqual(self.manifest["name"], "humanizer-plugin")
        self.assertEqual(self.manifest["interface"]["displayName"], "Humanizer Plugin")

    def test_manifest_and_editorial_skill_versions_match(self):
        self.assertEqual(self.manifest["version"], "3.0.0")
        self.assertEqual(
            self.manifest["version"],
            frontmatter_scalar(self.frontmatter, "version"),
        )

    def test_editorial_frontmatter_name_and_trigger_contract(self):
        self.assertEqual(
            frontmatter_scalar(self.frontmatter, "name"),
            "editorial-humanizer",
        )
        description = " ".join(self.frontmatter.lower().split())
        required_terms = [
            "broad editorial judgment",
            "anti-slop cleanup",
            "weak or generic material",
            "faithful-humanizer",
            "every supplied claim",
        ]
        for term in required_terms:
            with self.subTest(term=term):
                self.assertIn(term, description)

    def test_allowed_tools_are_intentional(self):
        self.assertEqual(
            frontmatter_list(self.frontmatter, "allowed-tools"),
            ["Read", "Write", "Edit", "Grep", "Glob", "AskUserQuestion"],
        )

    def test_editorial_skill_explains_its_latitude(self):
        required_terms = [
            "Editorial latitude",
            "remove generic, unsupported, repetitive, or promotional material",
            "changing paragraph and list structure",
            "removing a generic third item",
            "Do not use this latitude when the user explicitly asks for form-only preservation",
        ]
        normalized = " ".join(self.skill_markdown.split())
        for term in required_terms:
            with self.subTest(term=term):
                self.assertIn(term, normalized)

    def test_editorial_skill_protects_factual_integrity(self):
        required_terms = [
            "Do not invent details",
            "No vague attribution presented as evidence",
            "Preserve supplied concrete nouns",
            "Do not silently strengthen claims",
            "Do not add a more specific fact than the source supports",
        ]
        for term in required_terms:
            with self.subTest(term=term):
                self.assertIn(term, self.skill_markdown)

    def test_scoring_gate_thresholds_are_present(self):
        for threshold in [
            "Total must be at least 56/80",
            "Mechanics must be at least 35/50",
            "Substance must be at least 21/30",
            "Factual integrity must be at least 9/10",
        ]:
            self.assertIn(threshold, self.skill_markdown)

    def test_reference_catalog_is_available(self):
        self.assertIn("references/banned-list.md", self.skill_markdown)
        for section in [
            "## Transition words to avoid",
            "## Adjectives AI overuses",
            "## Plain-word swaps",
            "## Contrast framing (all variants)",
            "## Rule-of-three (all variants)",
            "## Fake naming",
        ]:
            with self.subTest(section=section):
                self.assertIn(section, self.reference_markdown)

    def test_editorial_output_contract_is_explicit(self):
        normalized = " ".join(self.skill_markdown.split())
        for term in [
            "Return only the rewritten text with no preamble, score, change log, or closing invitation",
            "Score: NN/80",
            "Do not use a ten-point or percentage output score",
            "entity, metric, and timeframe",
        ]:
            with self.subTest(term=term):
                self.assertIn(term, normalized)

    def test_manifest_prompts_use_new_skill_names(self):
        prompts = self.manifest["interface"]["defaultPrompt"]
        self.assertLessEqual(len(prompts), 3)
        self.assertTrue(any("$editorial-humanizer" in prompt for prompt in prompts))
        self.assertTrue(any("$faithful-humanizer" in prompt for prompt in prompts))
        self.assertFalse(any("$humanizer-form" in prompt for prompt in prompts))
        for prompt in prompts:
            self.assertLessEqual(len(prompt), 128)

    def test_readme_clearly_distinguishes_the_skills(self):
        required_terms = [
            "Editorial Humanizer",
            "Faithful Humanizer",
            "$editorial-humanizer",
            "$faithful-humanizer",
            "Detailed comparison",
            "Same source, different result",
            "Migration from 2.x",
            "Would you accept the editor deleting a weak sentence",
            "every supplied idea and qualifier must survive",
        ]
        for term in required_terms:
            with self.subTest(term=term):
                self.assertIn(term, self.readme_markdown)

    def test_readme_documents_rename_migration(self):
        self.assertIn("| `$humanizer` | `$editorial-humanizer` |", self.readme_markdown)
        self.assertIn("| `$humanizer-form` | `$faithful-humanizer` |", self.readme_markdown)
        self.assertIn("Version 3.0.0 renames the skills", self.readme_markdown)

    def test_readme_documents_install_and_update_lifecycle(self):
        for term in [
            "codex plugin marketplace add CoveMB/humanizer-skill-plugin --ref main",
            "codex plugin add humanizer-plugin@humanizer-plugin-local",
            "codex plugin marketplace upgrade humanizer-plugin-local",
            "codex plugin remove humanizer-plugin@humanizer-plugin-local",
            "codex plugin list",
            "start a new Codex session",
            "~/.agents/skills/editorial-humanizer",
            "~/.agents/skills/faithful-humanizer",
            "Do not enable the plain skills and plugin copies at the same time",
        ]:
            with self.subTest(term=term):
                self.assertIn(term, self.readme_markdown)

    def test_license_metadata_discloses_mixed_scope(self):
        notice = read_text(REPO_ROOT / "NOTICE")
        self.assertEqual(self.manifest["license"], "MIT AND CC-BY-SA-4.0")
        self.assertEqual(
            frontmatter_scalar(self.frontmatter, "license"),
            "MIT AND CC-BY-SA-4.0",
        )
        for term in [
            "Faithful Humanizer",
            "Editorial Humanizer",
            "CC BY-SA 4.0",
            "https://creativecommons.org/licenses/by-sa/4.0/",
        ]:
            with self.subTest(term=term):
                self.assertIn(term, notice + self.readme_markdown)

    def test_repo_marketplace_points_at_git_plugin_root(self):
        self.assertEqual(self.marketplace["name"], "humanizer-plugin-local")
        plugins = self.marketplace["plugins"]
        self.assertEqual(len(plugins), 1)
        self.assertEqual(plugins[0]["name"], "humanizer-plugin")
        self.assertEqual(
            plugins[0]["source"],
            {
                "source": "url",
                "url": "https://github.com/CoveMB/humanizer-skill-plugin.git",
                "ref": "main",
            },
        )

    def test_ci_runs_deterministic_quality_gates(self):
        workflow = read_text(WORKFLOW_PATH)
        for command in [
            "fetch-depth: 0",
            "git diff --check",
            "make test",
            "make eval-humanizer-dry-run",
            "Check eval flag variations",
            "--filter explicit_dense_rewrite",
            "--filter contextual_docs_cleanup",
            "--rubric-grade",
            "--model gpt-5.5",
            "--timeout-seconds 600",
            "--cases evals/humanizer_eval_cases.json",
            "--artifacts-dir /tmp/humanizer-eval-artifacts",
            "--codex-bin codex",
        ]:
            with self.subTest(command=command):
                self.assertIn(command, workflow)

    def test_live_eval_workflow_is_manual_and_authenticates_codex(self):
        workflow = read_text(LIVE_EVAL_WORKFLOW_PATH)
        for term in [
            "workflow_dispatch:",
            "OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}",
            "codex login --with-api-key",
            "make test",
            "make eval-humanizer-dry-run",
            "scripts/run_humanizer_evals.py",
            "actions/upload-artifact@v4",
        ]:
            with self.subTest(term=term):
                self.assertIn(term, workflow)
        self.assertNotIn("push:", workflow)
        self.assertNotIn("pull_request:", workflow)


if __name__ == "__main__":
    unittest.main()
