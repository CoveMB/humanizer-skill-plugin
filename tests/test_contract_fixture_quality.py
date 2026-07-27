import unittest

from tests.helpers.output_contracts import SUPPORTED_CONSTRAINT_KEYS
from tests.helpers.skill_artifacts import load_fixture_cases


REQUIRED_TAGS = {
    "rewrite_only_output",
    "audit_output",
    "factual_integrity",
    "missing_source_handling",
    "no_chatbot_wrapper",
    "no_contrast_frame",
    "no_rule_of_three",
    "no_fake_naming",
    "no_self_narration",
    "dense_pattern_catalog",
    "voice_calibration",
    "preserve_supplied_facts",
    "no_unsupported_benefits",
    "preserve_epistemic_status",
    "minimal_edit",
    "contextual_false_positive",
    "scientific_register",
    "faithful_meaningful_rewrite",
    "faithful_scientific_register",
    "faithful_already_natural_restraint",
    "faithful_mixed_locality",
    "faithful_audit_mode",
    "faithful_voice_matching",
    "faithful_structure_preservation",
    "faithful_structural_reconstruction",
    "plain_language_rewrite",
    "plain_language_explain",
    "plain_language_combined",
    "plain_language_jargon",
    "plain_language_protected_literals",
    "plain_language_high_stakes",
    "plain_language_already_clear",
    "plain_language_anti_bloat",
}

SOURCE_AWARE_CONSTRAINT_KEYS = {
    "no_new_named_entities",
    "no_new_numbers",
}

OUTPUT_SHAPE_CONSTRAINT_KEYS = {
    "rewrite_only",
    "explain_only",
    "combined_output",
}

CANONICAL_API_OUTPUT = (
    "The API (application programming interface) sets a rate limit, or threshold, "
    "of 120 requests per minute for each client. Requests above the threshold receive "
    "HTTP 429, an error code meaning too many requests."
)

CANONICAL_LEGAL_OUTPUT = (
    "The controller—the party required to give notice—must notify the processor, "
    "the party receiving the notice, within 24 hours unless disclosure is prohibited "
    "by applicable law. This exception does not remove the duty to retain the incident "
    "record."
)


class ContractFixtureQualityTests(unittest.TestCase):
    def setUp(self):
        self.cases = load_fixture_cases()

    def test_case_ids_are_unique(self):
        case_ids = [case["id"] for case in self.cases]
        self.assertEqual(len(case_ids), len(set(case_ids)))

    def test_required_tags_are_covered(self):
        covered_tags = {tag for case in self.cases for tag in case["tags"]}
        self.assertTrue(REQUIRED_TAGS.issubset(covered_tags), REQUIRED_TAGS - covered_tags)

    def test_each_case_has_prompt_source_and_constraints(self):
        for case in self.cases:
            with self.subTest(case=case["id"]):
                self.assertGreater(len(case["prompt"].strip()), 20)
                self.assertGreater(len(case["source"].strip()), 20)
                self.assertIn(
                    case["mode"],
                    {"rewrite", "audit", "answer", "translate", "summary", "spellcheck"},
                )
                self.assertIsInstance(case["constraints"], dict)

    def test_constraints_use_supported_keys(self):
        for case in self.cases:
            with self.subTest(case=case["id"]):
                self.assertTrue(
                    set(case["constraints"]).issubset(SUPPORTED_CONSTRAINT_KEYS)
                )

    def test_fact_preservation_cases_use_source_aware_constraints(self):
        for case in self.cases:
            tags = set(case["tags"])
            if "factual_integrity" not in tags and "preserve_supplied_facts" not in tags:
                continue

            with self.subTest(case=case["id"]):
                self.assertTrue(
                    set(case["constraints"]) & SOURCE_AWARE_CONSTRAINT_KEYS,
                    case["id"],
                )

    def test_80_point_score_thresholds_are_valid(self):
        for case in self.cases:
            constraints = case["constraints"]
            if "minimum_score_out_of_80" not in constraints:
                continue
            with self.subTest(case=case["id"]):
                threshold = constraints["minimum_score_out_of_80"]
                self.assertIsInstance(threshold, int)
                self.assertNotIsInstance(threshold, bool)
                self.assertGreaterEqual(threshold, 0)
                self.assertLessEqual(threshold, 80)

    def test_maximum_word_count_constraints_are_positive_integers(self):
        for case in self.cases:
            maximum_word_count = case["constraints"].get("maximum_word_count")
            if maximum_word_count is None:
                continue
            with self.subTest(case=case["id"]):
                self.assertIs(type(maximum_word_count), int)
                self.assertGreater(maximum_word_count, 0)

    def test_exact_occurrence_constraints_are_valid(self):
        for case in self.cases:
            expected_occurrences = case["constraints"].get("exact_occurrences")
            if expected_occurrences is None:
                continue
            with self.subTest(case=case["id"]):
                self.assertIsInstance(expected_occurrences, dict)
                self.assertTrue(expected_occurrences)
                for fragment, expected_count in expected_occurrences.items():
                    self.assertIsInstance(fragment, str)
                    self.assertTrue(fragment)
                    self.assertIs(type(expected_count), int)
                    self.assertGreaterEqual(expected_count, 0)

    def test_must_differ_constraints_are_boolean(self):
        for case in self.cases:
            constraints = case["constraints"]
            if "must_differ_from_source" not in constraints:
                continue
            with self.subTest(case=case["id"]):
                self.assertIs(type(constraints["must_differ_from_source"]), bool)

    def test_must_equal_constraints_are_boolean_and_not_conflicting(self):
        for case in self.cases:
            constraints = case["constraints"]
            if "must_equal_source" not in constraints:
                continue
            with self.subTest(case=case["id"]):
                self.assertIs(type(constraints["must_equal_source"]), bool)
                self.assertFalse(constraints.get("must_differ_from_source", False))

    def test_ordered_and_exact_fragment_constraints_are_non_empty_strings(self):
        for case in self.cases:
            constraints = case["constraints"]
            for constraint_name in ("must_include_exact", "ordered_fragments"):
                fragments = constraints.get(constraint_name)
                if fragments is None:
                    continue
                with self.subTest(case=case["id"], constraint=constraint_name):
                    self.assertIsInstance(fragments, list)
                    self.assertTrue(fragments)
                    self.assertTrue(
                        all(isinstance(fragment, str) and fragment for fragment in fragments)
                    )

    def test_docs_cleanup_contract_preserves_supplied_team_scope(self):
        docs_cleanup_case = next(
            case for case in self.cases if case["id"] == "contextual_docs_cleanup"
        )
        constraints = docs_cleanup_case["constraints"]

        self.assertIn("cross-functional teams", constraints["must_include"])
        self.assertNotIn("cross-functional", constraints["must_not_include"])

    def test_rule_of_three_tag_uses_matching_constraint(self):
        for case in self.cases:
            if "no_rule_of_three" not in set(case["tags"]):
                continue

            with self.subTest(case=case["id"]):
                self.assertTrue(case["constraints"].get("no_rule_of_three", False))

    def test_faithful_contracts_cover_core_preservation_invariants(self):
        faithful_cases = {
            case["id"]: case
            for case in self.cases
            if case["id"].startswith("faithful_")
        }

        self.assertEqual(
            set(faithful_cases),
            {
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
                "faithful_structural_product_reconstruction",
                "faithful_structural_academic_reconstruction",
                "faithful_structural_opinion_reconstruction",
                "faithful_structural_already_natural_restraint",
            },
        )
        covered_tags = {
            tag for case in faithful_cases.values() for tag in case["tags"]
        }
        self.assertTrue(
            {
                "faithful_attribution",
                "faithful_modality",
                "faithful_scope",
                "faithful_opinion",
                "faithful_chronology",
                "faithful_logical_relation",
                "faithful_exact_anchors",
                "faithful_list_membership",
                "faithful_negation",
                "faithful_causality",
                "faithful_meaningful_rewrite",
                "faithful_scientific_register",
                "faithful_already_natural_restraint",
                "faithful_mixed_locality",
                "faithful_audit_mode",
                "faithful_voice_matching",
                "faithful_structure_preservation",
                "faithful_structural_reconstruction",
            }.issubset(covered_tags)
        )
        for case in faithful_cases.values():
            with self.subTest(case=case["id"]):
                self.assertIn(
                    case["faithful_mode"],
                    {"structural", "conservative"},
                )
                constraints = case["constraints"]
                if case["mode"] == "rewrite":
                    self.assertTrue(constraints["rewrite_only"])
                else:
                    self.assertEqual(case["mode"], "audit")
                    self.assertNotIn("rewrite_only", constraints)
                self.assertTrue(constraints["no_new_numbers"])
                self.assertTrue(constraints["no_new_named_entities"])
                self.assertIsInstance(case.get("passing_output"), str)
                self.assertTrue(case["passing_output"])
                self.assertIsInstance(case.get("failing_outputs"), list)
                self.assertTrue(case["failing_outputs"])
                for failure in case["failing_outputs"]:
                    self.assertEqual(
                        set(failure),
                        {"label", "output", "expected_error"},
                    )

        structural_cases = {
            case_id
            for case_id, case in faithful_cases.items()
            if case["faithful_mode"] == "structural"
        }
        conservative_cases = {
            case_id
            for case_id, case in faithful_cases.items()
            if case["faithful_mode"] == "conservative"
        }
        self.assertEqual(
            structural_cases,
            {
                "faithful_structural_product_reconstruction",
                "faithful_structural_academic_reconstruction",
                "faithful_structural_opinion_reconstruction",
                "faithful_structural_already_natural_restraint",
            },
        )
        self.assertTrue(conservative_cases)

    def test_plain_language_contracts_cover_modes_domains_and_boundaries(self):
        plain_language_cases = {
            case["id"]: case
            for case in self.cases
            if case["id"].startswith("plain_language_")
        }
        self.assertEqual(
            set(plain_language_cases),
            {
                "plain_language_api_rewrite",
                "plain_language_webhook_explain",
                "plain_language_combined_output",
                "plain_language_protected_procedure",
                "plain_language_security_uncertainty",
                "plain_language_scientific_boundary",
                "plain_language_medical_condition",
                "plain_language_legal_obligation",
                "plain_language_financial_assumptions",
                "plain_language_already_clear",
            },
        )
        self.assertEqual(
            {case["plain_language_mode"] for case in plain_language_cases.values()},
            {"rewrite", "explain"},
        )
        self.assertTrue(
            all(
                "maximum_word_count" in case["constraints"]
                for case in plain_language_cases.values()
            )
        )

        for case_id, case in plain_language_cases.items():
            constraints = case["constraints"]
            shape_constraints = set(constraints) & OUTPUT_SHAPE_CONSTRAINT_KEYS
            if "plain_language_combined" in case["tags"]:
                expected_shape = {"combined_output"}
            elif case["plain_language_mode"] == "explain":
                expected_shape = {"explain_only"}
            else:
                expected_shape = {"rewrite_only"}
            with self.subTest(case=case_id, contract="output shape"):
                self.assertEqual(shape_constraints, expected_shape)
                shape_constraint = next(iter(shape_constraints))
                self.assertIs(type(constraints[shape_constraint]), bool)
                self.assertTrue(constraints[shape_constraint])

    def test_plain_language_shape_mutations_cannot_drift(self):
        cases = {case["id"]: case for case in self.cases}
        required_mutations = {
            "plain_language_api_rewrite": "adds an unrequested Explanation section",
            "plain_language_webhook_explain": "wraps explain-only output",
            "plain_language_combined_output": "duplicates the Explanation heading",
        }

        for case_id, required_label in required_mutations.items():
            labels = {
                failure["label"] for failure in cases[case_id]["failing_outputs"]
            }
            with self.subTest(case=case_id):
                self.assertIn(required_label, labels)

    def test_plain_language_definition_outputs_and_mutations_are_canonical(self):
        cases = {case["id"]: case for case in self.cases}

        self.assertEqual(
            cases["plain_language_api_rewrite"]["passing_output"],
            CANONICAL_API_OUTPUT,
        )
        self.assertEqual(
            cases["plain_language_legal_obligation"]["passing_output"],
            CANONICAL_LEGAL_OUTPUT,
        )
        required_mutations = {
            "plain_language_api_rewrite": "omits the threshold definition",
            "plain_language_legal_obligation": "omits the controller role definition",
        }
        for case_id, required_label in required_mutations.items():
            labels = {
                failure["label"] for failure in cases[case_id]["failing_outputs"]
            }
            with self.subTest(case=case_id):
                self.assertIn(required_label, labels)


if __name__ == "__main__":
    unittest.main()
