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
}

SOURCE_AWARE_CONSTRAINT_KEYS = {
    "no_new_named_entities",
    "no_new_numbers",
}


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


if __name__ == "__main__":
    unittest.main()
