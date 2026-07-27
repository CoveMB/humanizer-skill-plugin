import json
import re
import unittest

from tests.helpers.skill_artifacts import (
    MANIFEST_PATH,
    MARKETPLACE_PATH,
    PLAIN_LANGUAGE_SKILL_PATH,
    REFERENCE_PATH,
    REPO_ROOT,
    SCIENTIFIC_REFERENCE_PATH,
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
SKILL_EXAMPLES_PATH = REPO_ROOT / "docs" / "skill-examples.md"
COMPARISON_EXAMPLES_PATH = (
    REPO_ROOT / "docs" / "humanizer-comparison-examples.md"
)
EXPECTED_DEFAULT_PROMPTS = [
    (
        "Use $editorial-humanizer to improve this draft with broader editorial "
        "judgment:"
    ),
    (
        "Use $faithful-humanizer to improve the wording without changing the "
        "substance:"
    ),
    (
        "Use $plain-language-humanizer to rewrite this technical content for an "
        "informed non-specialist:"
    ),
]
EXPECTED_LIVE_EVAL_TARGET_OPTIONS = [
    "all",
    "editorial-humanizer",
    "faithful-humanizer",
    "plain-language-humanizer",
]


class EditorialHumanizerArtifactTests(unittest.TestCase):
    def setUp(self):
        self.skill_markdown = read_text(SKILL_PATH)
        self.frontmatter = extract_frontmatter(self.skill_markdown)
        self.manifest = json.loads(read_text(MANIFEST_PATH))
        self.marketplace = json.loads(read_text(MARKETPLACE_PATH))
        self.reference_markdown = read_text(REFERENCE_PATH)
        self.readme_markdown = read_text(REPO_ROOT / "README.md")
        self.comparison_examples_markdown = read_text(COMPARISON_EXAMPLES_PATH)

    def assert_manifest_prompt_contract(self, manifest):
        self.assertEqual(
            manifest["interface"]["defaultPrompt"],
            EXPECTED_DEFAULT_PROMPTS,
        )

    def extract_indented_block(self, text, header):
        lines = text.splitlines()
        self.assertIn(header, lines)
        header_index = lines.index(header)
        header_indent = len(header) - len(header.lstrip())
        block_lines = []

        for line in lines[header_index + 1 :]:
            if line.strip() and len(line) - len(line.lstrip()) <= header_indent:
                break
            block_lines.append(line)

        return "\n".join(block_lines)

    def assert_live_eval_workflow_contract(self, workflow):
        trigger_block = self.extract_indented_block(workflow, "on:")
        trigger_names = [
            match.group(1)
            for line in trigger_block.splitlines()
            if (match := re.match(r"^  ([A-Za-z_][\w-]*):", line))
        ]
        self.assertEqual(trigger_names, ["workflow_dispatch"])

        workflow_dispatch_block = self.extract_indented_block(
            trigger_block,
            "  workflow_dispatch:",
        )
        inputs_block = self.extract_indented_block(
            workflow_dispatch_block,
            "    inputs:",
        )
        target_skill_block = self.extract_indented_block(
            inputs_block,
            "      target_skill:",
        )
        options_block = self.extract_indented_block(
            target_skill_block,
            "        options:",
        )
        target_options = [
            match.group(1)
            for line in options_block.splitlines()
            if (match := re.match(r"^          - (.+)$", line))
        ]
        self.assertEqual(target_options, EXPECTED_LIVE_EVAL_TARGET_OPTIONS)

    def test_required_files_exist(self):
        for path in [
            MANIFEST_PATH,
            MARKETPLACE_PATH,
            SKILL_PATH,
            REFERENCE_PATH,
            SCIENTIFIC_REFERENCE_PATH,
            FAITHFUL_SKILL_PATH,
            PLAIN_LANGUAGE_SKILL_PATH,
            RESEARCH_PATH,
            SKILL_EXAMPLES_PATH,
            COMPARISON_EXAMPLES_PATH,
        ]:
            with self.subTest(path=path):
                self.assertTrue(path.exists(), path)

    def test_manifest_points_at_skill_directory(self):
        self.assertEqual(self.manifest["skills"], "./skills/")
        self.assertEqual(self.manifest["name"], "humanizer-plugin")
        self.assertEqual(self.manifest["interface"]["displayName"], "Humanizer Plugin")

    def test_manifest_and_skill_versions_are_explicit(self):
        self.assertEqual(self.manifest["version"], "3.1.0")
        self.assertEqual(frontmatter_scalar(self.frontmatter, "version"), "3.0.0")
        faithful_frontmatter = extract_frontmatter(read_text(FAITHFUL_SKILL_PATH))
        plain_language_frontmatter = extract_frontmatter(
            read_text(PLAIN_LANGUAGE_SKILL_PATH)
        )
        self.assertEqual(
            frontmatter_scalar(faithful_frontmatter, "version"), "1.0.0"
        )
        self.assertEqual(
            frontmatter_scalar(plain_language_frontmatter, "version"), "1.0.0"
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

    def test_editorial_skill_directly_distinguishes_substantive_and_surface_edits(self):
        normalized = " ".join(self.skill_markdown.split())
        for term in [
            "substantive, voice-oriented Humanizer",
            "Editorial Humanizer may change content selection, argument architecture, emphasis, and rhetorical presentation",
            "Faithful Humanizer may change only form",
            "Faithful's default Structural mode",
            "opt-in Conservative mode",
        ]:
            with self.subTest(term=term):
                self.assertIn(term, normalized)

    def test_editorial_skill_protects_factual_integrity(self):
        normalized = " ".join(self.skill_markdown.split())
        required_terms = [
            "Do not invent details",
            "Do not invent benefits or causal explanations",
            "Preserve epistemic status",
            "Use the smallest sufficient intervention",
            "Rewrite mode is not audit mode",
            "Preserve fitting punctuation",
            "Do not force rule-of-three lists",
            "Do not use contrast framing as a crutch",
            "Treat `not just` as a contextual signal",
            "Avoid manufactured staccato",
            "Evaluate rhetorical transition hooks",
            "No fake naming",
            "Remove empty self-narration",
            "No chatbot wrapper",
            "No vague attribution presented as evidence",
            "Preserve supplied concrete nouns",
            "Do not silently strengthen claims",
            "Make voice stronger through form, not invention",
            "a ranking such as `most useful` or `best`",
            "an enabling condition such as `when the team provides enough context`",
            "a skeptical or approving frame such as `beyond the hype`",
            "Do not add a more specific fact than the source supports",
        ]
        for term in required_terms:
            with self.subTest(term=term):
                self.assertIn(term, normalized)

    def test_editorial_patterns_are_contextual_signals_not_blanket_bans(self):
        normalized = " ".join(self.skill_markdown.split())
        for term in [
            "diagnostic signals, not proof of authorship",
            "Is the pattern isolated, or does it cluster or repeat?",
            "genre, register, locale, or supplied style guide",
            "A single em dash is not an AI tell by itself",
            "Do not fail this check because of one em dash",
            "Passive voice is not a problem by itself",
        ]:
            with self.subTest(term=term):
                self.assertIn(term, normalized)
        self.assertNotIn("No em dashes by default", normalized)

    def test_fact_safe_boundaries_cover_observed_live_failures(self):
        normalized = " ".join(self.skill_markdown.split())
        expected_patterns = [
            r"saves? time",
            r"moves? faster",
            r"reduces? friction",
            r"makes? work easier",
            r"improves? quality",
            r"causal explanation",
            r"attributed, uncertain, or unsupported claims",
            r"preferences, feelings, experiences, timing, or evaluations",
            r"`finally`, `I care about`, or `sounds usable`",
            r"`value proposition` into `practical value`",
            r"`Some say` is still vague attribution",
            r"`documentation` to `docs`",
            r"`offline mode` to `works offline`",
            r"`adoption` to `traction`",
            r"`flights` to `a flight`",
            r"`helping teams stay on the same page`",
            r"`reliable starting point`",
            r"One plain sentence is enough",
            r"A statement appearing in the source does not make it established fact",
            r"Attribution and uncertainty are not interchangeable",
        ]
        for expected_pattern in expected_patterns:
            with self.subTest(pattern=expected_pattern):
                self.assertRegex(normalized, expected_pattern)

    def test_user_requested_editorial_score_thresholds_are_present(self):
        for threshold in [
            "Total must be at least 56/80",
            "Mechanics must be at least 35/50",
            "Substance must be at least 21/30",
            "Factual integrity must be at least 9/10",
        ]:
            self.assertIn(threshold, self.skill_markdown)

    def test_reference_catalog_is_available(self):
        self.assertIn("references/pattern-catalog.md", self.skill_markdown)
        for section in [
            "## Transition words to evaluate in context",
            "## Adjective clusters AI writing often overuses",
            "## Possible plain-word alternatives",
            "## Repeated contrast framing",
            "## Repeated or padded rule-of-three patterns",
            "## Unsupported or ornamental naming",
        ]:
            with self.subTest(section=section):
                self.assertIn(section, self.reference_markdown)

    def test_shared_scientific_reference_has_editorial_preservation_boundaries(self):
        scientific_reference = read_text(SCIENTIFIC_REFERENCE_PATH)
        normalized_skill = " ".join(self.skill_markdown.split())
        normalized_reference = " ".join(scientific_reference.split())
        for term in [
            "../references/registers/scientific-writing.md",
            "Scientific and academic profile",
            "preserve epistemic caution, evidence boundaries, citation attribution",
            "Never replace `was measured` with `we measured`",
        ]:
            with self.subTest(term=term):
                self.assertIn(term, normalized_skill)
        for term in [
            "Faithful Humanizer treats this file as preservation constraints",
            "Editorial Humanizer uses it as genre-specific guidance",
            "Precision outranks lexical variety",
            "Passive voice is conventional and useful",
        ]:
            with self.subTest(term=term):
                self.assertIn(term, normalized_reference)

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

    def test_manifest_prompts_match_public_contract(self):
        self.assert_manifest_prompt_contract(self.manifest)

    def test_manifest_prompt_contract_rejects_copy_drift_with_skill_names_intact(self):
        mutated_manifest = json.loads(json.dumps(self.manifest))
        mutated_manifest["interface"]["defaultPrompt"][0] = (
            "Use $editorial-humanizer to revise this draft:"
        )

        with self.assertRaises(AssertionError):
            self.assert_manifest_prompt_contract(mutated_manifest)

    def test_readme_clearly_distinguishes_the_skills(self):
        normalized_readme = " ".join(self.readme_markdown.split())
        required_terms = [
            "Editorial Humanizer",
            "Faithful Humanizer",
            "Plain Language Humanizer",
            "three prose-editing skills",
            "five user-facing behaviors",
            "Faithful Humanizer — Structural",
            "Faithful Humanizer — Conservative",
            "Plain Language Humanizer — Rewrite",
            "Plain Language Humanizer — Explain",
            "Structural is the default",
            "Rewrite is the default",
            "informed non-specialist",
            "Conservative mode. Give this a minimal, light-touch edit",
            "$editorial-humanizer",
            "$faithful-humanizer",
            "$plain-language-humanizer",
            "Detailed comparison",
            "Same source, four results",
            "Would you accept the editor deleting a weak sentence",
            "every supplied idea and qualifier must survive",
        ]
        for term in required_terms:
            with self.subTest(term=term):
                self.assertIn(term, normalized_readme)

    def test_comparison_examples_cover_all_three_behaviors_across_contexts(self):
        examples = self.comparison_examples_markdown
        normalized_documentation = " ".join(
            (examples + self.readme_markdown).split()
        )
        for heading in [
            "## 1. Opinion and mixed stance",
            "## 2. Academic limitation and causal boundary",
            "## 3. Product and technical scope",
            "## 4. Multi-sentence community program",
            "## 5. Policy deadline and documented exception",
            "## 6. Medical instruction with time and escalation conditions",
            "## 7. Financial forecast with assumptions and exclusions",
            "## 8. Cybersecurity incident chronology and unresolved status",
            "## 9. Technical upgrade procedure with exact anchors",
            "## 10. Customer support with pending-payment uncertainty",
            "## 11. Fundraising appeal with a promotional belief claim",
            "## 12. Workplace update with criticism and early evidence",
        ]:
            with self.subTest(heading=heading):
                self.assertIn(heading, examples)

        self.assertEqual(examples.count("#### Source"), 12)
        self.assertEqual(examples.count("#### Editorial Humanizer"), 12)
        self.assertEqual(examples.count("#### Faithful Structural"), 12)
        self.assertEqual(examples.count("#### Faithful Conservative"), 12)
        self.assertEqual(examples.count("**Why they differ:**"), 12)

        for term in [
            "style anchors, not golden outputs",
            "Editorial is not automatically better",
            "generally available feature to one use case",
            "High-stakes or scientific register strengthens the preservation review",
            "Structural is the default",
            "30 calendar days",
            "some patients",
            "$18 million",
            "14:20 UTC",
            "`/var/backups/controller.json`",
            "3–5 business days",
            "every $75",
            "12% faster than in May",
            "docs/humanizer-comparison-examples.md",
        ]:
            with self.subTest(term=term):
                self.assertIn(term, normalized_documentation)

    def test_readme_documents_install_and_update_lifecycle(self):
        for term in [
            "codex plugin marketplace add CoveMB/humanizer-skill-plugin --ref main",
            "codex plugin add humanizer-plugin@humanizer-plugin-local",
            "codex plugin marketplace upgrade humanizer-plugin-local",
            "codex plugin remove humanizer-plugin@humanizer-plugin-local",
            "codex plugin list",
            "Start a new Codex session",
            "~/.agents/skills/editorial-humanizer",
            "~/.agents/skills/faithful-humanizer",
            "~/.agents/skills/plain-language-humanizer",
            "~/.claude/skills/plain-language-humanizer",
            "~/.config/opencode/skills/plain-language-humanizer",
            "--target-skill plain-language-humanizer --plain-language-mode rewrite",
            "--target-skill plain-language-humanizer --plain-language-mode explain",
            "Do not enable the plain skills and plugin copies at the same time",
        ]:
            with self.subTest(term=term):
                self.assertIn(term, self.readme_markdown)

    def test_manual_installations_share_an_explicit_checkout_prerequisite(self):
        clone_command = (
            "git clone https://github.com/CoveMB/humanizer-skill-plugin.git"
        )
        checkout_position = self.readme_markdown.index("### Manual skill checkout")
        clone_position = self.readme_markdown.index(clone_command)
        plain_position = self.readme_markdown.index("### Plain Codex skills")
        claude_position = self.readme_markdown.index("### Claude Code")
        opencode_position = self.readme_markdown.index("### OpenCode")

        self.assertLess(checkout_position, clone_position)
        self.assertLess(clone_position, plain_position)
        self.assertLess(plain_position, claude_position)
        self.assertLess(claude_position, opencode_position)
        for skill_name in (
            "editorial-humanizer",
            "faithful-humanizer",
            "plain-language-humanizer",
        ):
            source_path = f"humanizer-skill-plugin/skills/{skill_name}"
            self.assertGreaterEqual(self.readme_markdown.count(source_path), 3)
        shared_reference_path = "humanizer-skill-plugin/skills/references"
        self.assertGreaterEqual(self.readme_markdown.count(shared_reference_path), 3)

    def test_client_specific_activation_uses_supported_forms(self):
        examples = read_text(SKILL_EXAMPLES_PATH)
        normalized_examples = " ".join(examples.split())

        self.assertIn("## Client-specific activation", examples)
        self.assertIn("Codex accepts the `$skill-name` form", normalized_examples)
        self.assertIn("Use $editorial-humanizer", examples)
        self.assertIn("Use $faithful-humanizer", examples)
        self.assertIn("Use $plain-language-humanizer", examples)
        self.assertIn(
            "Claude Code exposes installed skills as slash commands",
            normalized_examples,
        )
        self.assertIn("/editorial-humanizer", examples)
        self.assertIn("/faithful-humanizer", examples)
        self.assertIn("/plain-language-humanizer", examples)
        self.assertIn("native `skill` tool", normalized_examples)
        self.assertIn(
            "does not define a direct OpenCode invocation command",
            normalized_examples,
        )
        for skill_name in (
            "editorial-humanizer",
            "faithful-humanizer",
            "plain-language-humanizer",
        ):
            self.assertIn(f"Load `{skill_name}` with the skill tool", examples)
        self.assertIn(
            "docs/skill-examples.md#client-specific-activation",
            self.readme_markdown,
        )

    def test_license_metadata_discloses_mixed_scope(self):
        notice = read_text(REPO_ROOT / "NOTICE")
        normalized_readme = " ".join(self.readme_markdown.split())
        normalized_notice = " ".join(notice.split())
        self.assertEqual(self.manifest["license"], "MIT AND CC-BY-SA-4.0")
        self.assertEqual(
            frontmatter_scalar(self.frontmatter, "license"),
            "MIT AND CC-BY-SA-4.0",
        )
        for term in [
            "Faithful Humanizer",
            "Plain Language Humanizer",
            "Editorial Humanizer",
            "CC BY-SA 4.0",
            "https://creativecommons.org/licenses/by-sa/4.0/",
        ]:
            with self.subTest(term=term):
                self.assertIn(term, notice + self.readme_markdown)
        self.assertIn(
            "tests, repository-authored documentation, Faithful Humanizer, and "
            "Plain Language Humanizer are released under the MIT License",
            normalized_readme,
        )
        self.assertIn(
            "Editorial Humanizer skill instructions, reference material, examples, "
            "and related plugin documentation remains available under CC BY-SA 4.0",
            normalized_readme,
        )
        self.assertIn(
            "Adapted, reorganized, and expanded into Editorial Humanizer's skill "
            "instructions, reference catalog, examples, and plugin documentation",
            normalized_notice,
        )

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
            "python -m pip install -r requirements-dev.txt",
            "make coverage",
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
            "Check Faithful eval stability flags",
            "--target-skill faithful-humanizer",
            "--trials 3",
            "--rubric-model gpt-5.5",
            "Check rubric calibration matrix",
            "--calibrate-rubric",
            "Check Plain Language eval mode flags",
            "--target-skill plain-language-humanizer",
            "--plain-language-mode rewrite",
            "--plain-language-mode explain",
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
        self.assert_live_eval_workflow_contract(workflow)

    def test_live_eval_contract_rejects_target_option_moved_to_another_input(self):
        workflow = read_text(LIVE_EVAL_WORKFLOW_PATH)
        mutated_workflow = workflow.replace(
            "          - plain-language-humanizer\n",
            "",
            1,
        )
        mutated_workflow = mutated_workflow.replace(
            "      trials:\n",
            "      unrelated_choice:\n"
            "        description: \"Controlled mutation\"\n"
            "        type: choice\n"
            "        options:\n"
            "          - plain-language-humanizer\n"
            "      trials:\n",
            1,
        )

        with self.assertRaises(AssertionError):
            self.assert_live_eval_workflow_contract(mutated_workflow)

    def test_live_eval_contract_rejects_automatic_trigger(self):
        workflow = read_text(LIVE_EVAL_WORKFLOW_PATH)
        mutated_workflow = workflow.replace(
            "on:\n  workflow_dispatch:",
            "on:\n  schedule:\n    - cron: '0 3 * * *'\n  workflow_dispatch:",
            1,
        )

        with self.assertRaises(AssertionError):
            self.assert_live_eval_workflow_contract(mutated_workflow)


if __name__ == "__main__":
    unittest.main()
