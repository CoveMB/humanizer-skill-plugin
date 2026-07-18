import contextlib
import importlib.util
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from tests.helpers.skill_artifacts import REPO_ROOT


RUNNER_PATH = REPO_ROOT / "scripts" / "run_humanizer_evals.py"
EVAL_CASES_PATH = REPO_ROOT / "evals" / "humanizer_eval_cases.json"
SKILL_TRACE_PATH = "skills/editorial-humanizer/SKILL.md"
FAITHFUL_SKILL_TRACE_PATH = "skills/faithful-humanizer/SKILL.md"
DEFAULT_OUTPUT_CONTRACT_CASES = object()


def load_runner_module():
    spec = importlib.util.spec_from_file_location("run_humanizer_evals", RUNNER_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_cases_file(temporary_directory, data):
    cases_path = Path(temporary_directory) / "cases.json"
    cases_path.write_text(json.dumps(data), encoding="utf-8")
    return cases_path


def minimal_eval_case(**overrides):
    return {
        "id": "case",
        "category": "explicit",
        "should_trigger": True,
        "prompt": "Use $editorial-humanizer.",
        "source": "Here is a draft.",
        **overrides,
    }


def two_dimension_rubric(
    minimum_total_score=16,
    minimum_dimension_score=8,
    minimum_dimension_scores=None,
):
    rubric = {
        "minimum_total_score": minimum_total_score,
        "minimum_dimension_score": minimum_dimension_score,
        "dimensions": [
            {"name": "factual_fidelity", "question": "Facts?"},
            {"name": "rewrite_only", "question": "Rewrite only?"},
        ],
    }
    if minimum_dimension_scores is not None:
        rubric["minimum_dimension_scores"] = minimum_dimension_scores
    return rubric


def skill_read_trace(usage=None):
    trace_lines = [
        {
            "type": "item.completed",
            "item": {
                "type": "command_execution",
                "command": f"sed -n '1,20p' {SKILL_TRACE_PATH}",
                "aggregated_output": SKILL_TRACE_PATH,
            },
        }
    ]
    if usage is not None:
        trace_lines.append({"type": "turn.completed", "usage": usage})
    return "\n".join(json.dumps(line) for line in trace_lines) + "\n"


def completed_codex_process(stdout):
    return subprocess.CompletedProcess(
        args=["codex"],
        returncode=0,
        stdout=stdout,
        stderr="",
    )


class HumanizerEvalRunnerTests(unittest.TestCase):
    def setUp(self):
        self.runner = load_runner_module()

    def _load_cases_from_data(
        self,
        data,
        output_contract_cases=DEFAULT_OUTPUT_CONTRACT_CASES,
    ):
        with tempfile.TemporaryDirectory() as temporary_directory:
            cases_path = write_cases_file(temporary_directory, data)
            if output_contract_cases is DEFAULT_OUTPUT_CONTRACT_CASES:
                return self.runner.load_eval_cases(cases_path)
            return self.runner.load_eval_cases(
                cases_path,
                output_contract_cases=output_contract_cases,
            )

    def test_eval_cases_cover_trigger_modes_and_output_contracts(self):
        cases = self.runner.load_eval_cases(EVAL_CASES_PATH)
        categories = {case["category"] for case in cases}
        contract_ids = {
            case["output_contract_case_id"]
            for case in cases
            if case.get("output_contract_case_id")
        }
        rubric_ids = {case["rubric_id"] for case in cases if case.get("rubric_id")}
        forced_read_case_ids = {
            case["id"] for case in cases if case.get("force_skill_file_read")
        }
        trigger_prompts = " ".join(
            case["prompt"].lower() for case in cases if case["should_trigger"]
        )
        positive_case_ids = {case["id"] for case in cases if case["should_trigger"]}
        positive_cases_without_forced_skill_read = [
            case["id"]
            for case in cases
            if case["should_trigger"] and not case.get("force_skill_file_read", False)
        ]
        negative_cases_without_contract = [
            case["id"]
            for case in cases
            if not case["should_trigger"] and not case.get("output_contract_case_id")
        ]
        dense_reference_cases = [
            case
            for case in cases
            if case.get("output_contract_case_id")
            in {"dense_ai_rewrite", "dense_pattern_catalog_scrub"}
            and case.get("force_reference_file_read", False)
        ]

        self.assertGreaterEqual(len(cases), 38)
        self.assertTrue({"explicit", "implicit", "contextual", "negative"}.issubset(categories))
        self.assertTrue(
            {
                "dense_ai_rewrite",
                "editorial_broader_boundary",
                "missing_source_handling",
                "voice_calibration",
                "audit_mode",
                "dense_pattern_catalog_scrub",
                "contextual_release_notes",
                "contextual_docs_cleanup",
                "unsupported_benefit_substitution",
                "epistemic_status_preservation",
                "already_natural_restraint",
                "editorial_contextual_false_positives",
                "editorial_scientific_profile",
                "faithful_structural_product_reconstruction",
                "faithful_structural_academic_reconstruction",
                "faithful_structural_opinion_reconstruction",
                "faithful_structural_already_natural_restraint",
                "faithful_attribution_modality_scope",
                "faithful_promotional_opinion_chronology",
                "faithful_exact_anchors_and_list_membership",
                "faithful_meaningful_local_rewrite",
                "faithful_scientific_register",
                "faithful_already_natural_restraint",
                "faithful_mixed_local_edit",
                "faithful_audit_mode",
                "faithful_voice_matching",
                "faithful_structure_and_protected_spans",
                "faithful_conditions_exceptions_comparison",
                "negative_fact_check_only",
                "negative_translate_only",
                "negative_summary_only",
                "negative_spellcheck_only",
            }.issubset(contract_ids)
        )
        self.assertTrue(
            {
                "humanizer_rewrite",
                "faithful_humanizer_rewrite",
                "missing_source_handling",
                "humanizer_audit",
                "negative_fact_check",
            }.issubset(rubric_ids)
        )
        self.assertTrue(positive_case_ids)
        self.assertTrue(forced_read_case_ids)
        self.assertTrue(forced_read_case_ids.issubset(positive_case_ids))
        self.assertEqual(
            set(positive_cases_without_forced_skill_read),
            {
                "faithful_implicit_form_only_activation",
                "faithful_rework_structure_activation",
                "faithful_contextual_preservation_activation",
                "faithful_explicit_catalog_activation",
            },
        )
        self.assertTrue(
            all(
                case.get("activation_probe", False)
                for case in cases
                if case["id"] in positive_cases_without_forced_skill_read
            )
        )
        editorial_boundary_case = next(
            case
            for case in cases
            if case["id"] == "editorial_routes_broader_rewrite_away_from_faithful"
        )
        self.assertTrue(editorial_boundary_case["force_skill_file_read"])
        self.assertFalse(editorial_boundary_case.get("activation_probe", False))
        self.assertIn(SKILL_TRACE_PATH, editorial_boundary_case["expected_trace_terms"])
        self.assertIn(
            FAITHFUL_SKILL_TRACE_PATH,
            editorial_boundary_case["forbidden_trace_terms"],
        )
        self.assertEqual(negative_cases_without_contract, ["negative_detector_evasion_only"])
        self.assertTrue(
            next(
                case for case in cases if case["id"] == "negative_detector_evasion_only"
            )["activation_probe"]
        )
        self.assertIn("sounds padded", trigger_prompts)
        self.assertIn("reads like a person wrote it", trigger_prompts)
        self.assertTrue(dense_reference_cases)
        for case in dense_reference_cases:
            with self.subTest(dense_reference_case=case["id"]):
                self.assertIn(
                    "skills/editorial-humanizer/references/pattern-catalog.md",
                    case["expected_trace_terms"],
                )
                self.assertTrue(case.get("force_reference_file_read", False))
        rewrite_rubric = next(
            case["rubric"] for case in cases if case.get("rubric_id") == "humanizer_rewrite"
        )
        factual_fidelity_question = next(
            dimension["question"]
            for dimension in rewrite_rubric["dimensions"]
            if dimension["name"] == "factual_fidelity"
        )
        self.assertIn("Do not penalize removal of generic filler", factual_fidelity_question)
        self.assertIn(
            "removal of vague attribution when the user requests broader Editorial cleanup",
            factual_fidelity_question,
        )
        self.assertEqual(
            rewrite_rubric["minimum_dimension_scores"],
            {"factual_fidelity": 9},
        )
        for case in cases:
            if case.get("rubric_id"):
                self.assertIn("rubric", case)

    def test_eval_cases_cover_faithful_preservation_invariants(self):
        cases = self.runner.load_eval_cases(EVAL_CASES_PATH)
        faithful_cases = {
            case["id"]: case
            for case in cases
            if case.get("target_skill") == "faithful-humanizer"
        }
        quality_cases = {
            case_id: case
            for case_id, case in faithful_cases.items()
            if case["should_trigger"] and not case.get("activation_probe", False)
        }
        activation_cases = {
            case_id: case
            for case_id, case in faithful_cases.items()
            if case["should_trigger"] and case.get("activation_probe", False)
        }

        self.assertEqual(
            set(quality_cases),
            {
                "faithful_structural_rebuilds_product_description",
                "faithful_structural_rebuilds_academic_limitation",
                "faithful_structural_rebuilds_opinion",
                "faithful_structural_leaves_natural_methods_unchanged",
                "faithful_preserves_attribution_modality_scope",
                "faithful_preserves_promotional_opinion_chronology",
                "faithful_preserves_exact_anchors_and_list_membership",
                "faithful_performs_meaningful_local_rewrite",
                "faithful_preserves_scientific_register",
                "faithful_leaves_already_natural_text_unchanged",
                "faithful_edits_only_formulaic_sentence",
                "faithful_returns_audit_sections_without_score",
                "faithful_matches_voice_without_importing_content",
                "faithful_preserves_structure_and_protected_spans",
                "faithful_preserves_conditions_exceptions_and_comparisons",
            },
        )
        self.assertEqual(
            set(activation_cases),
            {
                "faithful_implicit_form_only_activation",
                "faithful_rework_structure_activation",
                "faithful_contextual_preservation_activation",
                "faithful_explicit_catalog_activation",
            },
        )
        self.assertIn("negative_detector_evasion_only", faithful_cases)
        self.assertFalse(faithful_cases["negative_detector_evasion_only"]["should_trigger"])
        for case in quality_cases.values():
            with self.subTest(case=case["id"]):
                self.assertTrue(case["should_trigger"])
                self.assertTrue(case["force_skill_file_read"])
                self.assertFalse(case.get("force_reference_file_read", False))
                self.assertIn(FAITHFUL_SKILL_TRACE_PATH, case["expected_trace_terms"])
                self.assertEqual(case["rubric_id"], "faithful_humanizer_rewrite")
                self.assertEqual(
                    case["rubric"]["minimum_dimension_scores"],
                    {"semantic_fidelity": 9},
                )
                mode_dimension_name = {
                    "structural": "structural_initiative",
                    "conservative": "conservative_restraint",
                }[case["faithful_mode"]]
                self.assertIn(
                    mode_dimension_name,
                    {
                        dimension["name"]
                        for dimension in case["rubric"]["dimensions"]
                    },
                )
        explicit_activation_case = activation_cases[
            "faithful_explicit_catalog_activation"
        ]
        self.assertFalse(explicit_activation_case.get("force_skill_file_read", False))
        for case_id in {
            "faithful_implicit_form_only_activation",
            "faithful_rework_structure_activation",
            "faithful_contextual_preservation_activation",
            "faithful_explicit_catalog_activation",
        }:
            case = activation_cases[case_id]
            with self.subTest(activation_case=case["id"]):
                self.assertFalse(case.get("force_skill_file_read", False))
                self.assertIn(FAITHFUL_SKILL_TRACE_PATH, case["expected_trace_terms"])
                self.assertIn(SKILL_TRACE_PATH, case["forbidden_trace_terms"])
                self.assertIn(
                    "less formulaic rewrite appropriate to the requested Faithful mode",
                    next(
                        dimension["question"]
                        for dimension in case["rubric"]["dimensions"]
                        if dimension["name"] == "meaningful_surface_rewrite"
                    ),
                )
        for case in activation_cases.values():
            with self.subTest(activation_case=case["id"]):
                self.assertIn(SKILL_TRACE_PATH, case["forbidden_trace_terms"])
        scientific_case = faithful_cases["faithful_preserves_scientific_register"]
        self.assertEqual(
            scientific_case["force_reference_file_reads"],
            ["skills/references/registers/scientific-writing.md"],
        )

        self.assertEqual(
            {
                case_id: case["faithful_mode"]
                for case_id, case in activation_cases.items()
            },
            {
                "faithful_implicit_form_only_activation": "structural",
                "faithful_rework_structure_activation": "structural",
                "faithful_contextual_preservation_activation": "conservative",
                "faithful_explicit_catalog_activation": "structural",
            },
        )

    def test_rubric_calibrations_cover_both_modes_and_key_failures(self):
        calibrations = self.runner.load_rubric_calibrations(EVAL_CASES_PATH)

        self.assertEqual(
            {calibration["id"] for calibration in calibrations},
            {
                "faithful_structural_calibration_good_reconstruction",
                "faithful_structural_calibration_rejects_unchanged_source",
                "faithful_structural_calibration_rejects_local_only_repair",
                "faithful_structural_calibration_rejects_semantic_drift",
                "faithful_conservative_calibration_good_local_rewrite",
                "faithful_conservative_calibration_rejects_broad_reconstruction",
                "faithful_conservative_calibration_rejects_semantic_drift",
            },
        )
        self.assertEqual(
            [calibration["expected_pass"] for calibration in calibrations],
            [True, False, False, False, True, False, False],
        )
        self.assertTrue(
            all(
                calibration["rubric"]["minimum_dimension_scores"]
                == {"semantic_fidelity": 9}
                for calibration in calibrations
            )
        )
        self.assertEqual(
            {calibration["faithful_mode"] for calibration in calibrations},
            {"structural", "conservative"},
        )

    def test_eval_cases_cover_deterministic_mode_routing_language(self):
        cases = {
            case["id"]: case for case in self.runner.load_eval_cases(EVAL_CASES_PATH)
        }

        expected_modes = {
            "faithful_structural_rebuilds_product_description": "structural",
            "faithful_preserves_attribution_modality_scope": "conservative",
            "faithful_implicit_form_only_activation": "structural",
            "faithful_rework_structure_activation": "structural",
            "faithful_contextual_preservation_activation": "conservative",
            "faithful_explicit_catalog_activation": "structural",
            "negative_detector_evasion_only": "structural",
        }
        for case_id, expected_mode in expected_modes.items():
            with self.subTest(case=case_id):
                self.assertEqual(cases[case_id]["faithful_mode"], expected_mode)

        self.assertIn(
            "Structural mode",
            cases["faithful_structural_rebuilds_product_description"]["prompt"],
        )
        self.assertIn(
            "Conservative mode",
            cases["faithful_preserves_attribution_modality_scope"]["prompt"],
        )
        self.assertNotIn(
            "Structural",
            cases["faithful_implicit_form_only_activation"]["prompt"],
        )
        self.assertIn(
            "Rework the sentence structure",
            cases["faithful_rework_structure_activation"]["prompt"],
        )
        self.assertIn(
            "minimal, light-touch",
            cases["faithful_contextual_preservation_activation"]["prompt"],
        )
        self.assertIn(
            "$faithful-humanizer",
            cases["faithful_explicit_catalog_activation"]["prompt"],
        )
        self.assertFalse(
            cases["negative_detector_evasion_only"]["should_trigger"]
        )
        self.assertNotIn(
            "faithful_mode",
            cases["editorial_routes_broader_rewrite_away_from_faithful"],
        )

    def test_all_cases_reject_humanizer_plugin_loader_warnings(self):
        cases = self.runner.load_eval_cases(EVAL_CASES_PATH)

        for case in cases:
            with self.subTest(case=case["id"]):
                forbidden_stderr_terms = case.get("forbidden_stderr_terms", [])
                self.assertIn(
                    'plugin="humanizer-plugin" error=invalid marketplace',
                    forbidden_stderr_terms,
                )
                self.assertIn(
                    'plugin="humanizer@humanizer-local"',
                    forbidden_stderr_terms,
                )

    def test_load_eval_cases_rejects_duplicate_ids(self):
        with self.assertRaisesRegex(ValueError, "duplicate"):
            self._load_cases_from_data(
                {
                    "cases": [
                        minimal_eval_case(
                            id="duplicate",
                            prompt="Use Editorial Humanizer.",
                            expected_trace_terms=[SKILL_TRACE_PATH],
                        ),
                        minimal_eval_case(
                            id="duplicate",
                            category="implicit",
                            prompt="Make this sound natural.",
                            source="Here is another draft.",
                            expected_trace_terms=[SKILL_TRACE_PATH],
                        ),
                    ]
                }
            )

    def test_load_eval_cases_rejects_unknown_target_skill(self):
        with self.assertRaisesRegex(ValueError, "unsupported target_skill"):
            self._load_cases_from_data(
                {
                    "cases": [
                        minimal_eval_case(target_skill="unknown-humanizer")
                    ]
                },
                output_contract_cases={},
            )

    def test_load_eval_cases_requires_explicit_metadata_for_faithful_mode(self):
        with self.assertRaisesRegex(ValueError, "faithful_mode must be one of"):
            self._load_cases_from_data(
                {
                    "cases": [
                        minimal_eval_case(target_skill="faithful-humanizer")
                    ]
                },
                output_contract_cases={},
            )

    def test_load_eval_cases_rejects_unknown_faithful_mode(self):
        with self.assertRaisesRegex(ValueError, "faithful_mode must be one of"):
            self._load_cases_from_data(
                {
                    "cases": [
                        minimal_eval_case(
                            target_skill="faithful-humanizer",
                            faithful_mode="aggressive",
                        )
                    ]
                },
                output_contract_cases={},
            )

    def test_load_eval_cases_rejects_faithful_mode_on_editorial_case(self):
        with self.assertRaisesRegex(ValueError, "only valid for faithful-humanizer"):
            self._load_cases_from_data(
                {
                    "cases": [minimal_eval_case(faithful_mode="structural")]
                },
                output_contract_cases={},
            )

    def test_load_eval_cases_rejects_faithful_reference_catalog_reads(self):
        with self.assertRaisesRegex(ValueError, "not supported for faithful-humanizer"):
            self._load_cases_from_data(
                {
                    "cases": [
                        minimal_eval_case(
                            target_skill="faithful-humanizer",
                            faithful_mode="structural",
                            force_reference_file_read=True,
                        )
                    ]
                },
                output_contract_cases={},
            )

    def test_load_eval_cases_accepts_shared_scientific_reference_for_faithful(self):
        cases = self._load_cases_from_data(
            {
                "cases": [
                    minimal_eval_case(
                        target_skill="faithful-humanizer",
                        faithful_mode="structural",
                        force_reference_file_reads=[
                            "skills/references/registers/scientific-writing.md"
                        ],
                    )
                ]
            },
            output_contract_cases={},
        )

        self.assertEqual(
            self.runner.reference_paths_for_case(cases[0]),
            ["skills/references/registers/scientific-writing.md"],
        )

    def test_load_eval_cases_rejects_unknown_reference_path(self):
        with self.assertRaisesRegex(ValueError, "unsupported reference path"):
            self._load_cases_from_data(
                {
                    "cases": [
                        minimal_eval_case(
                            force_reference_file_reads=["../../outside.md"]
                        )
                    ]
                },
                output_contract_cases={},
            )

    def test_load_eval_cases_rejects_unknown_output_contract_case_id(self):
        with self.assertRaisesRegex(ValueError, "unknown output contract"):
            self._load_cases_from_data(
                {
                    "cases": [
                        minimal_eval_case(
                            id="unknown_contract",
                            prompt="Use Editorial Humanizer.",
                            output_contract_case_id="missing_contract",
                        )
                    ]
                }
            )

    def test_load_eval_cases_rejects_unknown_rubric_id(self):
        with self.assertRaisesRegex(ValueError, "unknown rubric"):
            self._load_cases_from_data(
                {
                    "rubrics": {},
                    "cases": [
                        minimal_eval_case(
                            id="unknown_rubric",
                            prompt="Use Editorial Humanizer.",
                            rubric_id="missing_rubric",
                        )
                    ],
                },
                output_contract_cases={},
            )

    def test_load_eval_cases_rejects_invalid_rubric_schema(self):
        with self.assertRaisesRegex(ValueError, "rubric"):
            self._load_cases_from_data(
                {
                    "rubrics": {
                        "bad": {
                            "minimum_total_score": 1,
                            "minimum_dimension_score": 1,
                            "dimensions": [],
                        }
                    },
                    "cases": [
                        minimal_eval_case(
                            id="bad_rubric",
                            prompt="Use Editorial Humanizer.",
                            rubric_id="bad",
                        )
                    ],
                },
                output_contract_cases={},
            )

    def test_load_eval_cases_rejects_boolean_rubric_score_threshold(self):
        with self.assertRaisesRegex(ValueError, "minimum_total_score"):
            self._load_cases_from_data(
                {
                    "rubrics": {
                        "bad": {
                            "minimum_total_score": True,
                            "minimum_dimension_score": 1,
                            "dimensions": [
                                {"name": "rewrite_only", "question": "Rewrite only?"}
                            ],
                        }
                    },
                    "cases": [
                        minimal_eval_case(
                            id="bad_rubric",
                            prompt="Use Editorial Humanizer.",
                            rubric_id="bad",
                        )
                    ],
                },
                output_contract_cases={},
            )

    def test_load_eval_cases_accepts_dimension_specific_thresholds(self):
        cases = self._load_cases_from_data(
            {
                "rubrics": {
                    "fact_safe": two_dimension_rubric(
                        minimum_dimension_scores={"factual_fidelity": 9}
                    )
                },
                "cases": [minimal_eval_case(rubric_id="fact_safe")],
            },
            output_contract_cases={},
        )

        self.assertEqual(
            cases[0]["rubric"]["minimum_dimension_scores"],
            {"factual_fidelity": 9},
        )

    def test_load_eval_cases_rejects_unknown_dimension_threshold(self):
        with self.assertRaisesRegex(ValueError, "unknown dimension"):
            self._load_cases_from_data(
                {
                    "rubrics": {
                        "bad": two_dimension_rubric(
                            minimum_dimension_scores={"missing": 9}
                        )
                    },
                    "cases": [minimal_eval_case(rubric_id="bad")],
                },
                output_contract_cases={},
            )

    def test_load_eval_cases_rejects_mismatched_output_contract_source(self):
        with self.assertRaisesRegex(ValueError, "source mismatch"):
            self._load_cases_from_data(
                {
                    "cases": [
                        minimal_eval_case(
                            id="source_mismatch",
                            prompt="Use Editorial Humanizer.",
                            source="Different source text.",
                            output_contract_case_id="contract_case",
                        )
                    ]
                },
                output_contract_cases={
                    "contract_case": {
                        "id": "contract_case",
                        "source": "Expected source text.",
                        "constraints": {},
                    }
                },
            )

    def test_load_eval_cases_rejects_mismatched_output_contract_mode(self):
        with self.assertRaisesRegex(ValueError, "faithful_mode mismatch"):
            self._load_cases_from_data(
                {
                    "cases": [
                        minimal_eval_case(
                            id="mode_mismatch",
                            target_skill="faithful-humanizer",
                            faithful_mode="structural",
                            source="Expected source text.",
                            output_contract_case_id="contract_case",
                        )
                    ]
                },
                output_contract_cases={
                    "contract_case": {
                        "id": "contract_case",
                        "faithful_mode": "conservative",
                        "source": "Expected source text.",
                        "constraints": {},
                    }
                },
            )

    def test_build_codex_prompt_includes_source_and_output_rules(self):
        case = {
            "id": "sample",
            "category": "explicit",
            "should_trigger": True,
            "force_skill_file_read": True,
            "prompt": "Use $editorial-humanizer to rewrite this.",
            "source": "Great question! This is a pivotal moment.",
            "output_contract_case_id": "dense_ai_rewrite",
        }

        prompt = self.runner.build_codex_prompt(case)

        self.assertIn("Use $editorial-humanizer to rewrite this.", prompt)
        self.assertIn("Read `skills/editorial-humanizer/SKILL.md` before answering.", prompt)
        self.assertIn("Read the complete skill file from its first line through EOF", prompt)
        self.assertIn("Reading every section of the skill file is essential", prompt)
        self.assertIn("Great question! This is a pivotal moment.", prompt)
        self.assertIn("Return only the final Editorial Humanizer output", prompt)
        self.assertIn("Do not edit repository files", prompt)

    def test_build_codex_prompt_supports_unforced_activation_probes(self):
        case = {
            "id": "activation",
            "category": "contextual",
            "should_trigger": True,
            "force_skill_file_read": False,
            "activation_probe": True,
            "prompt": "This sounds padded. Tighten it.",
            "source": "This release represents a pivotal step.",
        }

        prompt = self.runner.build_codex_prompt(case)

        self.assertNotIn("Read `skills/editorial-humanizer/SKILL.md` before answering.", prompt)
        self.assertIn("Return only the final answer", prompt)
        self.assertNotIn("Editorial Humanizer output", prompt)

    def test_build_codex_prompt_targets_faithful_skill(self):
        case = {
            "id": "faithful",
            "target_skill": "faithful-humanizer",
            "faithful_mode": "structural",
            "category": "explicit",
            "should_trigger": True,
            "force_skill_file_read": True,
            "prompt": "Use $faithful-humanizer to edit only the form.",
            "source": "Experts believe this may help some patients.",
        }

        prompt = self.runner.build_codex_prompt(case)

        self.assertIn("Read `skills/faithful-humanizer/SKILL.md` before answering.", prompt)
        self.assertIn("Return only the final Faithful Humanizer output", prompt)
        self.assertNotIn("skills/editorial-humanizer/SKILL.md", prompt)

    def test_build_codex_prompt_can_force_reference_file_read(self):
        case = {
            "id": "dense",
            "category": "implicit",
            "should_trigger": True,
            "force_skill_file_read": True,
            "force_reference_file_read": True,
            "prompt": "Clean this dense AI draft.",
            "source": "Certainly! This robust, scalable, and innovative dashboard helps.",
        }

        prompt = self.runner.build_codex_prompt(case)

        self.assertIn("Read `skills/editorial-humanizer/SKILL.md` before answering.", prompt)
        self.assertIn(
            "Read `skills/editorial-humanizer/references/pattern-catalog.md` before answering.",
            prompt,
        )
        self.assertIn("Read the complete reference from its first line through EOF", prompt)

    def test_build_codex_prompt_can_read_shared_scientific_reference(self):
        case = {
            "id": "scientific",
            "target_skill": "faithful-humanizer",
            "faithful_mode": "conservative",
            "category": "explicit",
            "should_trigger": True,
            "force_skill_file_read": True,
            "force_reference_file_reads": [
                "skills/references/registers/scientific-writing.md"
            ],
            "prompt": "Preserve this scientific register.",
            "source": "The samples may be associated with the outcome.",
        }

        prompt = self.runner.build_codex_prompt(case)

        self.assertIn("Read `skills/faithful-humanizer/SKILL.md`", prompt)
        self.assertIn(
            "Read `skills/references/registers/scientific-writing.md` before answering.",
            prompt,
        )

    def test_build_codex_prompt_reads_installed_plugin_files(self):
        case = {
            "id": "installed",
            "category": "explicit",
            "should_trigger": True,
            "force_skill_file_read": True,
            "force_reference_file_read": True,
            "prompt": "Use $editorial-humanizer to rewrite this.",
            "source": "This is a pivotal moment.",
        }
        plugin_root = Path("/tmp/isolated-codex-home/plugins/humanizer")

        prompt = self.runner.build_codex_prompt(case, plugin_root=plugin_root)

        self.assertIn(
            f"`{plugin_root}/skills/editorial-humanizer/SKILL.md`",
            prompt,
        )
        self.assertIn(
            f"`{plugin_root}/skills/editorial-humanizer/references/pattern-catalog.md`",
            prompt,
        )

    def test_build_codex_prompt_does_not_force_skill_for_no_trigger_cases(self):
        case = {
            "id": "negative",
            "category": "negative",
            "should_trigger": False,
            "prompt": "Translate this.",
            "source": "The release includes offline comments.",
        }

        prompt = self.runner.build_codex_prompt(case)

        self.assertNotIn("skills/editorial-humanizer/SKILL.md", prompt)

    def test_build_rubric_prompt_includes_source_output_and_schema(self):
        case = {
            "id": "rubric",
            "source": "Atlas Note adoption rose 43% last quarter.",
            "rubric": {
                "minimum_total_score": 8,
                "minimum_dimension_score": 4,
                "minimum_dimension_scores": {"factual_fidelity": 9},
                "dimensions": [
                    {
                        "name": "factual_fidelity",
                        "question": "Does the output preserve supplied facts?",
                    },
                    {
                        "name": "rewrite_only",
                        "question": "Does the output avoid commentary?",
                    },
                ],
            },
        }

        prompt = self.runner.build_rubric_prompt(
            case,
            "Atlas Note adoption rose 43% last quarter.",
        )

        self.assertIn("Atlas Note adoption rose 43% last quarter.", prompt)
        self.assertIn("Does the output avoid commentary?", prompt)
        self.assertIn("Do not treat user-requested labels or audit explanations", prompt)
        self.assertIn("<user_request>", prompt)
        self.assertNotIn("Faithful intervention mode", prompt)
        self.assertIn("factual_fidelity", prompt)
        self.assertIn('"factual_fidelity": 9', prompt)
        self.assertIn('"scores"', prompt)
        self.assertIn("Return only JSON", prompt)

    def test_build_rubric_prompt_names_faithful_mode(self):
        case = {
            "id": "faithful_rubric",
            "target_skill": "faithful-humanizer",
            "faithful_mode": "structural",
            "source": "Source text.",
            "rubric": {
                "minimum_total_score": 8,
                "minimum_dimension_score": 8,
                "minimum_dimension_scores": {},
                "dimensions": [
                    {"name": "semantic_fidelity", "question": "Faithful?"}
                ],
            },
        }

        prompt = self.runner.build_rubric_prompt(case, "Output text.")

        self.assertIn("Faithful intervention mode: structural.", prompt)

    def test_validate_rubric_grade_rejects_low_dimension_score(self):
        case = {
            "id": "rubric",
            "rubric": {
                "minimum_total_score": 16,
                "minimum_dimension_score": 8,
                "dimensions": [
                    {"name": "factual_fidelity", "question": "Facts?"},
                    {"name": "rewrite_only", "question": "Rewrite only?"},
                ],
            },
        }
        grade = {
            "case_id": "rubric",
            "scores": {
                "factual_fidelity": {"score": 10, "rationale": "preserved facts"},
                "rewrite_only": {"score": 7, "rationale": "added commentary"},
            },
            "total_score": 17,
            "passed": True,
            "issues": ["commentary"],
        }

        with self.assertRaisesRegex(AssertionError, "rewrite_only"):
                self.runner.validate_rubric_grade(case, grade)

    def test_validate_rubric_grade_can_return_expected_failure_for_calibration(self):
        case = {
            "id": "calibration",
            "rubric": two_dimension_rubric(),
        }
        grade = {
            "case_id": "calibration",
            "scores": {
                "factual_fidelity": {"score": 7, "rationale": "claim drift"},
                "rewrite_only": {"score": 9, "rationale": "correct format"},
            },
            "total_score": 16,
            "passed": False,
            "issues": ["claim drift"],
        }

        result = self.runner.validate_rubric_grade(
            case,
            grade,
            require_pass=False,
        )

        self.assertFalse(result["rubric_passed"])
        self.assertIn("factual_fidelity score 7", result["rubric_score_violations"][0])

    def test_validate_rubric_grade_uses_dimension_specific_threshold(self):
        case = {
            "id": "rubric",
            "rubric": two_dimension_rubric(
                minimum_total_score=16,
                minimum_dimension_scores={"factual_fidelity": 9},
            ),
        }
        grade = {
            "case_id": "rubric",
            "scores": {
                "factual_fidelity": {"score": 8, "rationale": "added a benefit"},
                "rewrite_only": {"score": 10, "rationale": "rewrite only"},
            },
            "total_score": 18,
            "passed": True,
            "issues": ["unsupported benefit"],
        }

        with self.assertRaisesRegex(AssertionError, "factual_fidelity"):
            self.runner.validate_rubric_grade(case, grade)

    def test_validate_rubric_grade_rejects_boolean_dimension_score(self):
        case = {
            "id": "rubric",
            "rubric": {
                "minimum_total_score": 1,
                "minimum_dimension_score": 1,
                "dimensions": [{"name": "rewrite_only", "question": "Rewrite only?"}],
            },
        }
        grade = {
            "case_id": "rubric",
            "scores": {
                "rewrite_only": {"score": True, "rationale": "not an integer score"}
            },
            "total_score": 1,
            "passed": True,
            "issues": [],
        }

        with self.assertRaisesRegex(AssertionError, "rewrite_only"):
            self.runner.validate_rubric_grade(case, grade)

    def test_parse_jsonl_events_reports_invalid_lines(self):
        jsonl_text = '{"type":"session.started"}\nnot json\n'

        with self.assertRaisesRegex(ValueError, "line 2"):
            self.runner.parse_jsonl_events(jsonl_text)

    def test_parse_jsonl_events_rejects_empty_trace(self):
        with self.assertRaisesRegex(ValueError, "no JSONL events"):
            self.runner.parse_jsonl_events("\n\n")

    def test_check_trace_expectations_uses_recursive_event_search(self):
        events = [
            {"type": "item.started", "item": {"path": "skills/editorial-humanizer/SKILL.md"}},
            {"type": "turn.completed", "usage": {"input_tokens": 1234}},
        ]
        case = {
            "id": "trace",
            "expected_trace_terms": ["skills/editorial-humanizer/SKILL.md"],
            "forbidden_trace_terms": ["dangerously-bypass-approvals"],
        }

        self.runner.check_trace_expectations(case, events)

    def test_check_trace_expectations_ignores_agent_messages_for_activation_terms(self):
        events = [
            {
                "type": "agent_message",
                "text": "I used skills/editorial-humanizer/SKILL.md for this rewrite.",
            }
        ]
        case = {
            "id": "trace",
            "expected_trace_terms": ["skills/editorial-humanizer/SKILL.md"],
        }

        with self.assertRaisesRegex(AssertionError, "missing trace term"):
            self.runner.check_trace_expectations(case, events)

    def test_check_trace_expectations_ignores_paths_only_listed_in_command_output(self):
        events = [
            {
                "type": "item.completed",
                "item": {
                    "type": "command_execution",
                    "command": "rg --files -g SKILL.md",
                    "aggregated_output": (
                        "skills/editorial-humanizer/SKILL.md\n"
                        "skills/faithful-humanizer/SKILL.md\n"
                    ),
                },
            },
            {
                "type": "item.completed",
                "item": {
                    "type": "command_execution",
                    "command": "sed -n '1,240p' skills/faithful-humanizer/SKILL.md",
                    "aggregated_output": "name: faithful-humanizer",
                },
            },
        ]
        case = {
            "id": "trace",
            "expected_trace_terms": ["skills/faithful-humanizer/SKILL.md"],
            "forbidden_trace_terms": ["skills/editorial-humanizer/SKILL.md"],
        }

        self.runner.check_trace_expectations(case, events)

    def test_check_trace_expectations_fails_for_missing_required_term(self):
        with self.assertRaisesRegex(AssertionError, "missing trace term"):
            self.runner.check_trace_expectations(
                {"id": "trace", "expected_trace_terms": ["skills/editorial-humanizer/SKILL.md"]},
                [{"type": "turn.completed"}],
            )

    def test_collect_trace_metrics_counts_tokens_and_commands(self):
        events = [
            {
                "type": "item.completed",
                "item": {"type": "command_execution", "command": "sed -n '1,20p' file"},
            },
            {
                "type": "turn.completed",
                "usage": {
                    "input_tokens": 123,
                    "cached_input_tokens": 45,
                    "output_tokens": 67,
                    "reasoning_output_tokens": 8,
                },
            },
        ]

        self.assertEqual(
            self.runner.collect_trace_metrics(events),
            {
                "command_count": 1,
                "input_tokens": 123,
                "cached_input_tokens": 45,
                "output_tokens": 67,
                "reasoning_output_tokens": 8,
            },
        )

    def test_check_stderr_expectations_fails_for_forbidden_loader_warning(self):
        case = {
            "id": "stderr",
            "forbidden_stderr_terms": [
                "path={repo_root}/.agents/plugins/marketplace.json plugin=\"humanizer-plugin\" error=invalid marketplace"
            ],
        }

        with self.assertRaisesRegex(AssertionError, "forbidden stderr term"):
            self.runner.check_stderr_expectations(
                case,
                f'WARN path={REPO_ROOT}/.agents/plugins/marketplace.json '
                'plugin="humanizer-plugin" error=invalid marketplace',
            )

    def test_check_stderr_expectations_fails_for_user_marketplace_warning(self):
        case = {
            "id": "stderr",
            "forbidden_stderr_terms": [
                'plugin="humanizer-plugin" error=invalid marketplace'
            ],
        }

        with self.assertRaisesRegex(AssertionError, "forbidden stderr term"):
            self.runner.check_stderr_expectations(
                case,
                'WARN path=/Users/example/.agents/plugins/marketplace.json '
                'plugin="humanizer-plugin" error=invalid marketplace file',
            )

    def test_build_codex_command_uses_read_only_json_trace_and_output_file(self):
        command = self.runner.build_codex_command(
            codex_bin="codex",
            working_directory=REPO_ROOT,
            output_path=Path("/tmp/final.txt"),
            prompt="Humanize this.",
            model="gpt-5.4",
        )

        self.assertEqual(command[:2], ["codex", "exec"])
        self.assertIn("--json", command)
        self.assertIn("--sandbox", command)
        self.assertIn("read-only", command)
        self.assertIn("--ephemeral", command)
        self.assertIn("--skip-git-repo-check", command)
        self.assertIn("--output-last-message", command)
        self.assertIn("/tmp/final.txt", command)
        self.assertIn("--model", command)
        self.assertNotIn("--dangerously-bypass-approvals-and-sandbox", command)

    def test_build_codex_command_isolates_current_repo_plugin(self):
        plugin_id = "humanizer-plugin@humanizer-eval-test"
        command = self.runner.build_codex_command(
            codex_bin="codex",
            working_directory=REPO_ROOT,
            output_path=Path("/tmp/final.txt"),
            prompt="Humanize this.",
            model=None,
            plugin_id=plugin_id,
        )

        self.assertIn("--ignore-user-config", command)
        self.assertIn("--ignore-rules", command)
        self.assertIn(
            f'plugins."{plugin_id}".enabled=true',
            command,
        )
        self.assertFalse(any("marketplaces." in argument for argument in command))

    def test_stage_eval_marketplace_copies_checkout_plugin_package(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            marketplace_root = Path(temporary_directory)
            plugin_root = self.runner.stage_eval_marketplace(
                REPO_ROOT,
                marketplace_root,
                "humanizer-eval-test",
            )

            marketplace = json.loads(
                marketplace_root.joinpath(
                    ".agents",
                    "plugins",
                    "marketplace.json",
                ).read_text(encoding="utf-8")
            )

            self.assertEqual(marketplace["name"], "humanizer-eval-test")
            self.assertEqual(
                marketplace["plugins"][0]["source"],
                {
                    "source": "local",
                    "path": "./plugins/humanizer-plugin",
                },
            )
            self.assertEqual(
                marketplace["plugins"][0]["policy"]["installation"],
                "AVAILABLE",
            )
            self.assertEqual(
                plugin_root.joinpath(".codex-plugin", "plugin.json").read_bytes(),
                REPO_ROOT.joinpath(".codex-plugin", "plugin.json").read_bytes(),
            )
            self.assertEqual(
                plugin_root.joinpath("skills", "editorial-humanizer", "SKILL.md").read_bytes(),
                REPO_ROOT.joinpath("skills", "editorial-humanizer", "SKILL.md").read_bytes(),
            )
            self.assertEqual(
                plugin_root.joinpath("skills", "faithful-humanizer", "SKILL.md").read_bytes(),
                REPO_ROOT.joinpath("skills", "faithful-humanizer", "SKILL.md").read_bytes(),
            )
            self.assertEqual(
                plugin_root.joinpath(
                    "skills",
                    "references",
                    "registers",
                    "scientific-writing.md",
                ).read_bytes(),
                REPO_ROOT.joinpath(
                    "skills",
                    "references",
                    "registers",
                    "scientific-writing.md",
                ).read_bytes(),
            )
            self.assertFalse(plugin_root.joinpath(".git").exists())
            self.assertFalse(plugin_root.joinpath("tests").exists())

    def test_verify_eval_plugin_is_model_visible_targets_both_skills(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            installed_path = Path(temporary_directory) / "plugin"
            expected_paths = [
                (installed_path / "skills" / skill_name / "SKILL.md").resolve()
                for skill_name in ("editorial-humanizer", "faithful-humanizer")
            ]
            with mock.patch.object(
                self.runner,
                "run_cli_json",
                return_value={
                    "prompt_input": [str(path) for path in expected_paths]
                },
            ):
                actual_paths = self.runner.verify_eval_plugin_is_model_visible(
                    "codex",
                    "humanizer-plugin@humanizer-eval-test",
                    installed_path,
                    {},
                )
            self.assertEqual(actual_paths, [str(path) for path in expected_paths])

    def test_require_isolated_codex_home_rejects_missing_and_default_home(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            user_home = Path(temporary_directory) / "user"
            default_codex_home = user_home / ".codex"
            default_codex_home.mkdir(parents=True)

            with mock.patch.dict(os.environ, {"HOME": str(user_home)}, clear=True):
                with self.assertRaisesRegex(ValueError, "CODEX_HOME is required"):
                    self.runner.require_isolated_codex_home()

            with mock.patch.dict(
                os.environ,
                {
                    "HOME": str(user_home),
                    "CODEX_HOME": str(default_codex_home),
                },
                clear=True,
            ):
                with self.assertRaisesRegex(ValueError, "must not use the default"):
                    self.runner.require_isolated_codex_home()

    def test_require_isolated_codex_home_accepts_explicit_non_default_home(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            user_home = Path(temporary_directory) / "user"
            codex_home = Path(temporary_directory) / "eval-codex-home"
            user_home.mkdir()
            codex_home.mkdir()

            with mock.patch.dict(
                os.environ,
                {
                    "HOME": str(user_home),
                    "CODEX_HOME": str(codex_home),
                },
                clear=True,
            ):
                self.assertEqual(
                    self.runner.require_isolated_codex_home(),
                    codex_home.resolve(),
                )

    def test_build_eval_environment_isolates_agents_home(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary_root = Path(temporary_directory)
            codex_home = temporary_root / "codex-home"
            isolated_home = temporary_root / "home"
            codex_home.mkdir()
            isolated_home.mkdir()

            with mock.patch.dict(
                os.environ,
                {
                    "HOME": "/Users/example",
                    "CODEX_HOME": str(codex_home),
                    "PATH": "/usr/bin",
                },
                clear=True,
            ):
                environment = self.runner.build_eval_environment(
                    codex_home,
                    isolated_home,
                )

            self.assertEqual(environment["HOME"], str(isolated_home.resolve()))
            self.assertEqual(environment["CODEX_HOME"], str(codex_home.resolve()))
            self.assertEqual(environment["PATH"], "/usr/bin")

    def test_validate_eval_plugin_install_rejects_stale_remote_version(self):
        expected_version = json.loads(
            REPO_ROOT.joinpath(".codex-plugin", "plugin.json").read_text(
                encoding="utf-8"
            )
        )["version"]
        with tempfile.TemporaryDirectory() as temporary_directory:
            codex_home = Path(temporary_directory) / "codex-home"
            installed_path = codex_home / "plugins" / "cache" / "humanizer"
            installed_path.mkdir(parents=True)

            with self.assertRaisesRegex(
                RuntimeError,
                f"expected {expected_version!r}",
            ):
                self.runner.validate_eval_plugin_install(
                    REPO_ROOT,
                    codex_home,
                    "humanizer-plugin@humanizer-eval-test",
                    {
                        "pluginId": "humanizer-plugin@humanizer-eval-test",
                        "version": "0.0.0-stale",
                        "installedPath": str(installed_path),
                    },
                )

    def test_validate_eval_plugin_install_rejects_content_mismatch(self):
        expected_version = json.loads(
            REPO_ROOT.joinpath(".codex-plugin", "plugin.json").read_text(
                encoding="utf-8"
            )
        )["version"]
        plugin_id = "humanizer-plugin@humanizer-eval-test"
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary_root = Path(temporary_directory)
            codex_home = temporary_root / "codex-home"
            installed_path = self.runner.stage_eval_marketplace(
                REPO_ROOT,
                codex_home / "staged",
                "humanizer-eval-test",
            )
            installed_path.joinpath("skills", "editorial-humanizer", "SKILL.md").write_text(
                "stale installed content\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(RuntimeError, "do not match the checkout"):
                self.runner.validate_eval_plugin_install(
                    REPO_ROOT,
                    codex_home,
                    plugin_id,
                    {
                        "pluginId": plugin_id,
                        "version": expected_version,
                        "installedPath": str(installed_path),
                    },
                )

    def test_installed_eval_plugin_cleans_up_rejected_marketplace(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary_root = Path(temporary_directory)
            codex_home = temporary_root / "codex-home"
            artifacts_dir = temporary_root / "artifacts"
            codex_home.mkdir()
            responses = iter(
                [
                    {"marketplaceName": "unexpected-marketplace"},
                    {},
                ]
            )

            with mock.patch.object(
                self.runner,
                "run_cli_json",
                side_effect=lambda *args: next(responses),
            ) as run_cli_json:
                with self.assertRaisesRegex(RuntimeError, "wrong name"):
                    with self.runner.installed_eval_plugin(
                        "codex",
                        REPO_ROOT,
                        artifacts_dir,
                        codex_home,
                    ):
                        self.fail("a rejected marketplace must not reach the eval")

            cleanup_command = run_cli_json.call_args_list[-1].args[0]
            self.assertEqual(
                cleanup_command[:4],
                ["codex", "plugin", "marketplace", "remove"],
            )
            self.assertTrue(cleanup_command[4].startswith("humanizer-eval-"))

    def test_run_eval_suite_uses_verified_installed_plugin(self):
        case = minimal_eval_case(id="installed_plugin")
        installation = self.runner.EvalPluginInstallation(
            plugin_id="humanizer-plugin@humanizer-eval-test",
            marketplace_name="humanizer-eval-test",
            version="test-version",
            installed_path=Path("/tmp/installed-humanizer"),
            package_sha256="digest",
            environment={"HOME": "/tmp/home", "CODEX_HOME": "/tmp/codex-home"},
        )

        with tempfile.TemporaryDirectory() as temporary_directory, mock.patch.object(
            self.runner,
            "require_isolated_codex_home",
            return_value=Path("/tmp/codex-home"),
        ), mock.patch.object(
            self.runner,
            "installed_eval_plugin",
            return_value=contextlib.nullcontext(installation),
        ), mock.patch.object(
            self.runner,
            "run_eval_case",
            return_value={"id": case["id"], "passed": True},
        ) as run_eval_case:
            provenance_path = (
                Path(temporary_directory) / self.runner.PLUGIN_PROVENANCE_FILENAME
            )
            provenance_path.write_text("stale provenance\n", encoding="utf-8")
            summaries, summary_path = self.runner.run_eval_suite(
                [case],
                Path(temporary_directory),
                codex_bin="codex",
                model="gpt-5.5",
            )
            self.assertTrue(summary_path.exists())
            self.assertFalse(provenance_path.exists())

        self.assertEqual(summaries, [{"id": case["id"], "passed": True}])
        self.assertEqual(
            run_eval_case.call_args.kwargs["plugin_id"],
            installation.plugin_id,
        )
        self.assertEqual(
            run_eval_case.call_args.kwargs["plugin_root"],
            installation.installed_path,
        )
        self.assertEqual(
            run_eval_case.call_args.kwargs["environment"],
            installation.environment,
        )

    def test_run_eval_suite_repeats_trials_with_distinct_artifacts_and_rubric_model(self):
        case = minimal_eval_case(
            id="repeated",
            target_skill="faithful-humanizer",
            faithful_mode="structural",
        )
        installation = self.runner.EvalPluginInstallation(
            plugin_id="humanizer-plugin@humanizer-eval-test",
            marketplace_name="humanizer-eval-test",
            version="test-version",
            installed_path=Path("/tmp/installed-humanizer"),
            package_sha256="digest",
            environment={"HOME": "/tmp/home", "CODEX_HOME": "/tmp/codex-home"},
        )

        with tempfile.TemporaryDirectory() as temporary_directory, mock.patch.object(
            self.runner,
            "require_isolated_codex_home",
            return_value=Path("/tmp/codex-home"),
        ), mock.patch.object(
            self.runner,
            "installed_eval_plugin",
            return_value=contextlib.nullcontext(installation),
        ), mock.patch.object(
            self.runner,
            "run_eval_case",
            side_effect=lambda current_case, *args, **kwargs: {
                "id": current_case["id"],
                "target_skill": current_case["target_skill"],
                "trial": kwargs["trial"],
                "passed": True,
                "failure_stage": None,
            },
        ) as run_eval_case:
            summaries, summary_path = self.runner.run_eval_suite(
                [case],
                Path(temporary_directory),
                codex_bin="codex",
                model="writer-model",
                rubric_model="grader-model",
                trials=3,
            )

            written_summary = json.loads(summary_path.read_text(encoding="utf-8"))

        self.assertEqual([summary["trial"] for summary in summaries], [1, 2, 3])
        self.assertEqual(
            [call.kwargs["artifact_stem"] for call in run_eval_case.call_args_list],
            [
                "repeated.trial-01",
                "repeated.trial-02",
                "repeated.trial-03",
            ],
        )
        self.assertTrue(
            all(
                call.kwargs["rubric_model"] == "grader-model"
                for call in run_eval_case.call_args_list
            )
        )
        self.assertEqual(written_summary["metadata"]["trials"], 3)
        self.assertEqual(written_summary["metadata"]["rubric_model"], "grader-model")

    def test_run_rubric_calibration_suite_accepts_expected_pass_and_failure(self):
        calibrations = [
            {
                "id": "good",
                "source": "Source.",
                "output": "Good output.",
                "expected_pass": True,
            },
            {
                "id": "bad",
                "source": "Source.",
                "output": "Bad output.",
                "expected_pass": False,
            },
        ]

        def grade_calibration(calibration, *args, **kwargs):
            rubric_passed = calibration["id"] == "good"
            return {
                "rubric_passed": rubric_passed,
                "rubric_total_score": 40 if rubric_passed else 20,
                "rubric_dimension_scores": {"semantic_fidelity": 10 if rubric_passed else 4},
                "rubric_score_violations": [] if rubric_passed else ["semantic drift"],
            }

        with tempfile.TemporaryDirectory() as temporary_directory, mock.patch.object(
            self.runner,
            "require_isolated_codex_home",
            return_value=Path("/tmp/codex-home"),
        ), mock.patch.object(
            self.runner,
            "run_rubric_grade",
            side_effect=grade_calibration,
        ) as run_rubric_grade:
            summaries, summary_path = self.runner.run_rubric_calibration_suite(
                calibrations,
                Path(temporary_directory),
                codex_bin="codex",
                model="grader-model",
            )
            written_summary = json.loads(summary_path.read_text(encoding="utf-8"))

        self.assertTrue(all(summary["passed"] for summary in summaries))
        self.assertEqual(written_summary["aggregate"]["passed"], 2)
        self.assertEqual(run_rubric_grade.call_count, 2)
        self.assertTrue(
            all(
                call.kwargs["require_pass"] is False
                for call in run_rubric_grade.call_args_list
            )
        )

    def test_run_rubric_calibration_suite_reports_expectation_mismatch(self):
        calibration = {
            "id": "unexpected_pass",
            "source": "Source.",
            "output": "Drifted output.",
            "expected_pass": False,
        }

        with tempfile.TemporaryDirectory() as temporary_directory, mock.patch.object(
            self.runner,
            "require_isolated_codex_home",
            return_value=Path("/tmp/codex-home"),
        ), mock.patch.object(
            self.runner,
            "run_rubric_grade",
            return_value={
                "rubric_passed": True,
                "rubric_total_score": 40,
                "rubric_dimension_scores": {"semantic_fidelity": 10},
                "rubric_score_violations": [],
            },
        ):
            summaries, _ = self.runner.run_rubric_calibration_suite(
                [calibration],
                Path(temporary_directory),
                codex_bin="codex",
                model="grader-model",
            )

        self.assertFalse(summaries[0]["passed"])
        self.assertEqual(summaries[0]["failure_stage"], "rubric_calibration")
        self.assertIn("expected False", summaries[0]["error"])

    def test_dry_run_lists_cases_without_invoking_codex(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            result = subprocess.run(
                [
                    sys.executable,
                    str(RUNNER_PATH),
                    "--cases",
                    str(EVAL_CASES_PATH),
                    "--artifacts-dir",
                    temporary_directory,
                    "--dry-run",
                ],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertIn("would run", result.stdout)
        self.assertIn("explicit_dense_rewrite", result.stdout)

    def test_dry_run_lists_rubric_calibrations_without_invoking_codex(self):
        result = subprocess.run(
            [
                sys.executable,
                str(RUNNER_PATH),
                "--cases",
                str(EVAL_CASES_PATH),
                "--calibrate-rubric",
                "--dry-run",
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertIn("would run 7 rubric calibration(s)", result.stdout)
        self.assertIn(
            "faithful_conservative_calibration_rejects_broad_reconstruction",
            result.stdout,
        )

    def test_main_runs_rubric_calibration_with_selected_grader_model(self):
        calibrations = [
            {
                "id": "calibration",
                "source": "Source.",
                "output": "Output.",
                "expected_pass": True,
            }
        ]
        summaries = [{"id": "calibration", "passed": True}]

        with tempfile.TemporaryDirectory() as temporary_directory, mock.patch.object(
            self.runner,
            "load_rubric_calibrations",
            return_value=calibrations,
        ), mock.patch.object(
            self.runner,
            "run_rubric_calibration_suite",
            return_value=(summaries, Path(temporary_directory) / "summary.json"),
        ) as run_calibrations, mock.patch.object(
            self.runner,
            "print_summary",
        ):
            returncode = self.runner.main(
                [
                    str(RUNNER_PATH),
                    "--calibrate-rubric",
                    "--rubric-model",
                    "grader-model",
                    "--artifacts-dir",
                    temporary_directory,
                ]
            )

        self.assertEqual(returncode, 0)
        self.assertEqual(run_calibrations.call_args.kwargs["model"], "grader-model")
        self.assertEqual(
            run_calibrations.call_args.kwargs["artifacts_dir"],
            Path(temporary_directory),
        )

    def test_parser_pins_default_eval_model(self):
        args = self.runner.build_parser().parse_args([])

        self.assertEqual(args.model, "gpt-5.5")
        self.assertIsNone(args.rubric_model)
        self.assertEqual(args.trials, 1)
        self.assertEqual(args.target_skill, [])
        self.assertEqual(args.faithful_mode, [])

    def test_parser_accepts_skill_filter_trials_and_separate_rubric_model(self):
        args = self.runner.build_parser().parse_args(
            [
                "--target-skill",
                "faithful-humanizer",
                "--faithful-mode",
                "structural",
                "--trials",
                "3",
                "--rubric-model",
                "grader-model",
            ]
        )

        self.assertEqual(args.target_skill, ["faithful-humanizer"])
        self.assertEqual(args.faithful_mode, ["structural"])
        self.assertEqual(args.trials, 3)
        self.assertEqual(args.rubric_model, "grader-model")

    def test_select_cases_filters_by_target_skill_after_case_ids(self):
        cases = [
            minimal_eval_case(id="editorial"),
            minimal_eval_case(
                id="faithful",
                target_skill="faithful-humanizer",
                faithful_mode="structural",
            ),
        ]

        selected = self.runner.select_cases(
            cases,
            ["faithful"],
            target_skills=["faithful-humanizer"],
        )

        self.assertEqual([case["id"] for case in selected], ["faithful"])
        with self.assertRaisesRegex(ValueError, "no eval cases match"):
            self.runner.select_cases(
                cases,
                ["editorial"],
                target_skills=["faithful-humanizer"],
            )

    def test_select_cases_filters_by_faithful_mode(self):
        cases = [
            minimal_eval_case(
                id="structural",
                target_skill="faithful-humanizer",
                faithful_mode="structural",
            ),
            minimal_eval_case(
                id="conservative",
                target_skill="faithful-humanizer",
                faithful_mode="conservative",
            ),
        ]

        selected = self.runner.select_cases(
            cases,
            [],
            faithful_modes=["conservative"],
        )

        self.assertEqual([case["id"] for case in selected], ["conservative"])

    def test_aggregate_summaries_reports_skill_rates_dimensions_and_stages(self):
        aggregate = self.runner.aggregate_summaries(
            [
                {
                    "target_skill": "faithful-humanizer",
                    "faithful_mode": "structural",
                    "passed": True,
                    "failure_stage": None,
                    "rubric_dimension_scores": {"semantic_fidelity": 10},
                },
                {
                    "target_skill": "faithful-humanizer",
                    "faithful_mode": "conservative",
                    "passed": False,
                    "failure_stage": "output_contract",
                    "rubric_dimension_scores": {"semantic_fidelity": 9},
                },
            ]
        )

        self.assertEqual(aggregate["runs"], 2)
        self.assertEqual(aggregate["passed"], 1)
        self.assertEqual(aggregate["pass_rate"], 0.5)
        self.assertEqual(aggregate["failure_stages"], {"output_contract": 1})
        faithful_summary = aggregate["by_target_skill"]["faithful-humanizer"]
        self.assertEqual(faithful_summary["minimum_rubric_dimension_scores"], {"semantic_fidelity": 9})
        self.assertEqual(
            aggregate["by_faithful_mode"],
            {
                "conservative": {"runs": 1, "passed": 0, "pass_rate": 0.0},
                "structural": {"runs": 1, "passed": 1, "pass_rate": 1.0},
            },
        )

    def test_parser_sets_default_case_timeout(self):
        args = self.runner.build_parser().parse_args([])

        self.assertEqual(args.timeout_seconds, 300)

    def test_parser_rejects_non_positive_timeout(self):
        with mock.patch("sys.stderr", new=io.StringIO()), self.assertRaises(SystemExit):
            self.runner.build_parser().parse_args(["--timeout-seconds", "0"])

    def test_run_eval_case_reports_timeout(self):
        case = minimal_eval_case(id="timeout_case")

        with tempfile.TemporaryDirectory() as temporary_directory:
            artifact_dirs = self.runner.ensure_artifact_dirs(Path(temporary_directory))
            timeout_error = subprocess.TimeoutExpired(
                cmd=["codex"],
                timeout=1,
                output="partial trace",
                stderr="partial stderr",
            )

            with mock.patch.object(
                self.runner.subprocess,
                "run",
                side_effect=timeout_error,
            ):
                summary = self.runner.run_eval_case(
                    case,
                    artifact_dirs,
                    codex_bin="codex",
                    output_contract_cases={},
                    model="gpt-5.5",
                    timeout_seconds=1,
                )

            self.assertFalse(summary["passed"])
            self.assertIn("timed out after 1 seconds", summary["error"])
            self.assertEqual(Path(summary["trace_path"]).read_text(), "partial trace")
            self.assertEqual(Path(summary["stderr_path"]).read_text(), "partial stderr")

    def test_run_eval_case_reports_startup_failure(self):
        case = minimal_eval_case(id="startup_failure")

        with tempfile.TemporaryDirectory() as temporary_directory:
            artifact_dirs = self.runner.ensure_artifact_dirs(Path(temporary_directory))

            with mock.patch.object(
                self.runner.subprocess,
                "run",
                side_effect=FileNotFoundError("missing codex"),
            ):
                summary = self.runner.run_eval_case(
                    case,
                    artifact_dirs,
                    codex_bin="missing-codex",
                    output_contract_cases={},
                    model="gpt-5.5",
                )

            self.assertFalse(summary["passed"])
            self.assertIn("failed to start codex", summary["error"])
            self.assertIn("missing codex", summary["error"])

    def test_run_eval_case_does_not_reuse_stale_output_file(self):
        case = minimal_eval_case(
            id="stale_output",
            output_contract_case_id="dense_ai_rewrite",
        )

        with tempfile.TemporaryDirectory() as temporary_directory:
            artifact_dirs = self.runner.ensure_artifact_dirs(Path(temporary_directory))
            output_path = artifact_dirs["outputs"] / "stale_output.txt"
            output_path.write_text(
                "AI coding assistants can help with docs and tests.",
                encoding="utf-8",
            )
            result = completed_codex_process('{"type":"turn.completed"}\n')

            with mock.patch.object(self.runner.subprocess, "run", return_value=result):
                summary = self.runner.run_eval_case(
                    case,
                    artifact_dirs,
                    codex_bin="codex",
                    output_contract_cases=self.runner.load_output_contract_cases(),
                    model="gpt-5.5",
                )

            self.assertFalse(summary["passed"])
            self.assertIn("missing final output file", summary["error"])

    def test_run_eval_case_reports_success_metrics(self):
        case = minimal_eval_case(
            id="success",
            expected_trace_terms=[SKILL_TRACE_PATH],
            output_contract_case_id="dense_ai_rewrite",
        )

        with tempfile.TemporaryDirectory() as temporary_directory:
            artifact_dirs = self.runner.ensure_artifact_dirs(Path(temporary_directory))
            observed_commands = []
            result = completed_codex_process(
                skill_read_trace(
                    {
                        "input_tokens": 123,
                        "cached_input_tokens": 45,
                        "output_tokens": 67,
                        "reasoning_output_tokens": 8,
                    }
                )
            )

            def run_and_write_output(*args, **kwargs):
                observed_commands.append(args[0])
                artifact_dirs["outputs"].joinpath("success.txt").write_text(
                    "AI coding assistants can help with doc work and tests.",
                    encoding="utf-8",
                )
                return result

            with mock.patch.object(
                self.runner.subprocess,
                "run",
                side_effect=run_and_write_output,
            ):
                summary = self.runner.run_eval_case(
                    case,
                    artifact_dirs,
                    codex_bin="codex",
                    output_contract_cases={
                        "dense_ai_rewrite": {
                            "id": "dense_ai_rewrite",
                            "constraints": {"must_include": ["AI coding assistants", "doc", "test"]},
                        }
                    },
                    model="gpt-5.5",
                )

            self.assertTrue(summary["passed"], summary["error"])
            self.assertEqual(summary["command_count"], 1)
            self.assertEqual(summary["input_tokens"], 123)
            self.assertIsNotNone(summary["editorial_source_diagnostics"])
            self.assertIsNotNone(summary["editorial_output_diagnostics"])
            self.assertNotIn("verdict", summary["editorial_output_diagnostics"])
            command = observed_commands[0]
            self.assertEqual(
                Path(command[command.index("--cd") + 1]),
                Path(temporary_directory).resolve(),
            )

    def test_editorial_diagnostics_are_not_applied_to_faithful_cases(self):
        case = minimal_eval_case(
            target_skill="faithful-humanizer",
            faithful_mode="conservative",
            source="It is important to note that the samples were measured.",
        )

        self.assertIsNone(
            self.runner.editorial_diagnostics_for_case(case, case["source"])
        )

    def test_run_eval_case_runs_rubric_grade_when_enabled(self):
        case = minimal_eval_case(
            id="graded",
            expected_trace_terms=[SKILL_TRACE_PATH],
            rubric=two_dimension_rubric(),
        )

        with tempfile.TemporaryDirectory() as temporary_directory:
            artifact_dirs = self.runner.ensure_artifact_dirs(Path(temporary_directory))
            primary_result = completed_codex_process(
                skill_read_trace({"input_tokens": 100})
            )
            rubric_result = completed_codex_process(
                '{"type":"turn.completed","usage":{"input_tokens":50}}\n'
            )

            def run_and_write_outputs(*args, **kwargs):
                if not artifact_dirs["outputs"].joinpath("graded.txt").exists():
                    artifact_dirs["outputs"].joinpath("graded.txt").write_text(
                        "Here is a draft.",
                        encoding="utf-8",
                    )
                    return primary_result

                artifact_dirs["rubric_outputs"].joinpath("graded.json").write_text(
                    json.dumps(
                        {
                            "case_id": "graded",
                            "scores": {
                                "factual_fidelity": {
                                    "score": 8,
                                    "rationale": "preserved facts",
                                },
                                "rewrite_only": {
                                    "score": 8,
                                    "rationale": "no commentary",
                                },
                            },
                            "total_score": 16,
                            "passed": True,
                            "issues": [],
                        }
                    ),
                    encoding="utf-8",
                )
                return rubric_result

            with mock.patch.object(
                self.runner.subprocess,
                "run",
                side_effect=run_and_write_outputs,
            ):
                summary = self.runner.run_eval_case(
                    case,
                    artifact_dirs,
                    codex_bin="codex",
                    output_contract_cases={},
                    model="gpt-5.5",
                    grade_rubric=True,
                )

            self.assertTrue(summary["passed"], summary["error"])
            self.assertTrue(summary["rubric_passed"], summary["rubric_error"])
            self.assertEqual(summary["rubric_total_score"], 16)

    def test_run_rubric_grade_does_not_enable_skill_under_test(self):
        case = {
            "id": "rubric_isolation",
            "source": "Atlas Note adoption rose 43% last quarter.",
            "rubric": {
                "minimum_total_score": 8,
                "minimum_dimension_score": 8,
                "dimensions": [{"name": "factual_fidelity", "question": "Facts?"}],
            },
        }

        with tempfile.TemporaryDirectory() as temporary_directory:
            artifact_dirs = self.runner.ensure_artifact_dirs(Path(temporary_directory))
            commands = []

            def run_and_write_grade(command, *args, **kwargs):
                commands.append(command)
                artifact_dirs["rubric_outputs"].joinpath("rubric_isolation.json").write_text(
                    json.dumps(
                        {
                            "case_id": "rubric_isolation",
                            "scores": {
                                "factual_fidelity": {
                                    "score": 8,
                                    "rationale": "preserved facts",
                                }
                            },
                            "total_score": 8,
                            "passed": True,
                            "issues": [],
                        }
                    ),
                    encoding="utf-8",
                )
                return completed_codex_process('{"type":"turn.completed"}\n')

            with mock.patch.object(
                self.runner.subprocess,
                "run",
                side_effect=run_and_write_grade,
            ):
                self.runner.run_rubric_grade(
                    case,
                    "Atlas Note adoption rose 43% last quarter.",
                    artifact_dirs,
                    codex_bin="codex",
                    model="gpt-5.5",
                )

            self.assertEqual(len(commands), 1)
            command_text = "\n".join(commands[0])
            self.assertNotIn("humanizer-plugin-local", command_text)
            self.assertNotIn("humanizer-plugin@humanizer-plugin-local", command_text)

    def test_run_eval_case_preserves_rubric_timeout_artifacts(self):
        case = minimal_eval_case(
            id="graded_timeout",
            expected_trace_terms=[SKILL_TRACE_PATH],
            rubric={
                "minimum_total_score": 8,
                "minimum_dimension_score": 8,
                "dimensions": [{"name": "rewrite_only", "question": "Rewrite only?"}],
            },
        )

        with tempfile.TemporaryDirectory() as temporary_directory:
            artifact_dirs = self.runner.ensure_artifact_dirs(Path(temporary_directory))
            primary_result = completed_codex_process(skill_read_trace())

            def run_primary_then_timeout(*args, **kwargs):
                if not artifact_dirs["outputs"].joinpath("graded_timeout.txt").exists():
                    artifact_dirs["outputs"].joinpath("graded_timeout.txt").write_text(
                        "Here is a draft.",
                        encoding="utf-8",
                    )
                    return primary_result

                raise subprocess.TimeoutExpired(
                    cmd=args[0],
                    timeout=300,
                    output='{"type":"turn.started"}\n',
                    stderr="rubric still running",
                )

            with mock.patch.object(
                self.runner.subprocess,
                "run",
                side_effect=run_primary_then_timeout,
            ):
                summary = self.runner.run_eval_case(
                    case,
                    artifact_dirs,
                    codex_bin="codex",
                    output_contract_cases={},
                    model="gpt-5.5",
                    grade_rubric=True,
                )

            self.assertFalse(summary["passed"])
            self.assertIn("rubric grader timed out", summary["rubric_error"])
            self.assertEqual(
                artifact_dirs["rubric_traces"].joinpath("graded_timeout.jsonl").read_text(
                    encoding="utf-8"
                ),
                '{"type":"turn.started"}\n',
            )
            self.assertEqual(
                artifact_dirs["rubric_stderr"].joinpath("graded_timeout.stderr").read_text(
                    encoding="utf-8"
                ),
                "rubric still running",
            )


if __name__ == "__main__":
    unittest.main()
