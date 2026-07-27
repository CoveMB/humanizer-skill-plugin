import unittest

from tests.helpers.output_contracts import validate_case_output
from tests.helpers.skill_artifacts import load_fixture_cases


BASE_CASE = {
    "id": "example",
    "constraints": {
        "must_include": ["Atlas Note", "43%"],
        "must_not_include": ["Gartner", "Let me know"],
        "must_match": ["Atlas Note"],
        "must_not_match": ["(?i)game[- ]changer"],
        "no_em_dash": True,
        "no_chatbot_wrapper": True,
        "no_contrast_frame": True,
        "no_markdown_fence": True,
        "rewrite_only": True,
        "max_question_marks": 0,
    },
}


class OutputContractTests(unittest.TestCase):
    def test_requires_exact_fragments_with_original_case_and_punctuation(self):
        case = {
            "id": "exact_anchor",
            "constraints": {"must_include_exact": ["`API v2.1`"]},
        }

        validate_case_output(case, "Verify `API v2.1` before release.")
        with self.assertRaisesRegex(AssertionError, "missing required exact fragment"):
            validate_case_output(case, "Verify `api v2.1` before release.")

    def test_requires_fragments_in_source_order(self):
        case = {
            "id": "ordered_items",
            "constraints": {"ordered_fragments": ["first", "second", "third"]},
        }

        validate_case_output(case, "First, do this. Second, do that. Third, stop.")
        with self.assertRaisesRegex(AssertionError, "ordered fragment"):
            validate_case_output(case, "Second, do that. First, do this. Third, stop.")

    def test_requires_already_natural_source_to_remain_unchanged(self):
        case = {
            "id": "already_natural",
            "source": "This sentence already reads naturally.",
            "constraints": {"must_equal_source": True},
        }

        validate_case_output(case, case["source"] + "\n")
        with self.assertRaisesRegex(AssertionError, "changed already-natural source"):
            validate_case_output(case, "This sentence already sounds natural.")

    def test_enforces_structural_sentence_count_bounds_on_rewrite_only(self):
        case = {
            "id": "structural_reconstruction",
            "constraints": {
                "minimum_sentence_count": 3,
                "maximum_sentence_count": 4,
            },
        }

        validate_case_output(case, "One sentence. A second sentence. The third sentence.")
        with self.assertRaisesRegex(AssertionError, "expected at least 3"):
            validate_case_output(case, "One sentence. A second sentence.")
        with self.assertRaisesRegex(AssertionError, "expected at most 4"):
            validate_case_output(
                case,
                "One. Two. Three. Four. Five.",
            )

    def test_sentence_count_bounds_ignore_requested_audit_sections(self):
        case = {
            "id": "structural_audit",
            "constraints": {"minimum_sentence_count": 2},
        }

        validate_case_output(
            case,
            "First sentence. Second sentence.\n\nForm changes:\nSplit one sentence.",
        )

    def test_enforces_maximum_word_count_on_full_output(self):
        case = {
            "id": "plain_language_brevity",
            "constraints": {"maximum_word_count": 8},
        }

        validate_case_output(case, "This concise explanation uses exactly seven words.")
        with self.assertRaisesRegex(AssertionError, "expected at most 8 words"):
            validate_case_output(
                case,
                "This explanation contains more than eight words in the complete output.",
            )

    def test_maximum_word_count_includes_combined_explanation(self):
        case = {
            "id": "plain_language_combined_brevity",
            "constraints": {"maximum_word_count": 9},
        }

        with self.assertRaisesRegex(AssertionError, "found 10 words"):
            validate_case_output(
                case,
                "Short rewrite here.\n\nExplanation:\nThis explanation adds five more words.",
            )

    def test_combined_output_accepts_source_grounded_explanation(self):
        cases = {case["id"]: case for case in load_fixture_cases()}
        case = cases["plain_language_combined_output"]

        validate_case_output(case, case["passing_output"])

    def test_combined_explanation_rejects_new_named_entity(self):
        cases = {case["id"]: case for case in load_fixture_cases()}
        case = cases["plain_language_combined_output"]
        output = case["passing_output"] + " According to Gartner, this is reliable."

        with self.assertRaisesRegex(AssertionError, "introduced named entity"):
            validate_case_output(case, output)

    def test_combined_explanation_rejects_new_number(self):
        cases = {case["id"]: case for case in load_fixture_cases()}
        case = cases["plain_language_combined_output"]
        output = case["passing_output"] + " This behavior remains supported in 2027."

        with self.assertRaisesRegex(AssertionError, "introduced number"):
            validate_case_output(case, output)

    def test_maximum_word_count_requires_a_positive_integer(self):
        for invalid_value in (0, -1, True, 2.5, "8"):
            with self.subTest(value=invalid_value):
                case = {
                    "id": "invalid_plain_language_limit",
                    "constraints": {"maximum_word_count": invalid_value},
                }
                with self.assertRaisesRegex(
                    AssertionError,
                    "maximum_word_count must be a positive integer",
                ):
                    validate_case_output(case, "Short output.")

    def test_fixture_mutations_prove_each_declared_guard(self):
        mutation_cases = [
            case
            for case in load_fixture_cases()
            if "passing_output" in case or "failing_outputs" in case
        ]

        self.assertTrue(mutation_cases)
        for case in mutation_cases:
            with self.subTest(case=case["id"], output="passing"):
                validate_case_output(case, case["passing_output"])
            for failure in case["failing_outputs"]:
                with self.subTest(case=case["id"], mutation=failure["label"]):
                    with self.assertRaisesRegex(
                        AssertionError,
                        failure["expected_error"],
                    ):
                        validate_case_output(case, failure["output"])

    def test_plain_language_claim_guards_allow_explicit_negation(self):
        cases = {case["id"]: case for case in load_fixture_cases()}
        allowed_outputs = {
            "api_never_delayed": (
                "plain_language_api_rewrite",
                "The API allows each client 120 requests per minute. Requests above "
                "the threshold are never delayed; they return HTTP 429.",
            ),
            "api_does_not_delay": (
                "plain_language_api_rewrite",
                "The API does not delay requests. It allows each client 120 requests "
                "per minute and returns HTTP 429 for requests above the threshold.",
            ),
            "webhook_does_not_guarantee": (
                "plain_language_webhook_explain",
                "Ledger does not guarantee delivery. It sends an `invoice.paid` "
                "notification to the configured HTTPS endpoint when an invoice is "
                "paid. If delivery fails, it retries for up to 24 hours and waits "
                "longer between attempts.",
            ),
            "webhook_never_guarantees": (
                "plain_language_webhook_explain",
                "Ledger never guarantees delivery. It sends an `invoice.paid` "
                "notification to the configured HTTPS endpoint when an invoice is "
                "paid. If delivery fails, it retries for up to 24 hours and waits "
                "longer between attempts.",
            ),
        }

        for label, (case_id, output) in allowed_outputs.items():
            with self.subTest(output=label):
                validate_case_output(cases[case_id], output)

    def test_requires_source_change_when_requested(self):
        case = {
            "id": "meaningful_rewrite",
            "source": "The committee is in the process of reviewing the proposal.",
            "constraints": {"must_differ_from_source": True},
        }

        with self.assertRaisesRegex(AssertionError, "did not rewrite the source"):
            validate_case_output(case, case["source"])

        validate_case_output(case, "The committee is reviewing the proposal.")

    def test_exact_occurrences_preserve_repeated_technical_terms(self):
        case = {
            "id": "technical_repetition",
            "constraints": {"exact_occurrences": {"weighted interval score": 2}},
        }

        validate_case_output(
            case,
            "The weighted interval score was recorded. The weighted interval score remained stable.",
        )
        with self.assertRaisesRegex(AssertionError, "occurs 1 time"):
            validate_case_output(case, "The weighted interval score remained stable.")

    def test_dense_ai_rewrite_rejects_live_rubric_failure(self):
        cases = {case["id"]: case for case in load_fixture_cases()}

        with self.assertRaisesRegex(AssertionError, "forbidden fragment"):
            validate_case_output(
                cases["dense_ai_rewrite"],
                (
                    "AI coding assistants are useful because they take some of the grind "
                    "out of software work. They can help draft documentation, improve "
                    "tests, and fill in routine code faster than a developer would want "
                    "to do by hand. Autocomplete is part of it, but the bigger value is "
                    "having a tool that can work through rough edges while the developer "
                    "stays focused on the actual problem."
                ),
            )

    def test_dense_ai_rewrite_rejects_invented_third_work_category(self):
        cases = {case["id"]: case for case in load_fixture_cases()}

        with self.assertRaisesRegex(AssertionError, "forbidden pattern"):
            validate_case_output(
                cases["dense_ai_rewrite"],
                "AI coding assistants can help with documentation, tests, and refactors.",
            )

    def test_dense_ai_rewrite_rejects_unsupported_benefit_substitutions(self):
        cases = {case["id"]: case for case in load_fixture_cases()}
        unsupported_outputs = (
            (
                "AI coding assistants can help with documentation and tests. "
                "They make development work easier."
            ),
            (
                "AI coding assistants can help with documentation and tests "
                "without lowering quality."
            ),
            (
                "AI coding assistants can help with documentation and tests. "
                "The pace depends on the team and the kind of code being written."
            ),
            (
                "AI coding assistants are one of the clearest ways large language "
                "models are showing up in software development. Autocomplete is "
                "part of it, but the practical value is in documentation and tests."
            ),
            (
                "AI coding assistants are useful for more than autocomplete. They "
                "can help with documentation and tests, and they may also make it "
                "easier for teams to stay on the same page."
            ),
            (
                "AI coding assistants are one of the more visible ways large "
                "language models are showing up in software development. Their "
                "clearest uses are practical ones: helping with documentation and "
                "tests. Autocomplete is part of the story, but the broader question "
                "is how these tools fit into day-to-day coding work."
            ),
        )

        for output in unsupported_outputs:
            with self.subTest(output=output), self.assertRaisesRegex(
                AssertionError,
                "forbidden",
            ):
                validate_case_output(cases["dense_ai_rewrite"], output)

    def test_dense_ai_rewrite_rejects_unqualified_adoption_claim(self):
        cases = {case["id"]: case for case in load_fixture_cases()}

        with self.assertRaisesRegex(AssertionError, "forbidden pattern"):
            validate_case_output(
                cases["dense_ai_rewrite"],
                (
                    "AI coding assistants can help with documentation and tests. "
                    "Adoption is rising."
                ),
            )

    def test_voice_calibration_rejects_invented_attitude(self):
        cases = {case["id"]: case for case in load_fixture_cases()}

        with self.assertRaisesRegex(AssertionError, "forbidden"):
            validate_case_output(
                cases["voice_calibration"],
                (
                    "ChronoPad finally has an offline mode that sounds usable. "
                    "You can edit notes on flights and sync them when you reconnect."
                ),
            )

    def test_docs_cleanup_rejects_invented_ease_claim(self):
        cases = {case["id"]: case for case in load_fixture_cases()}

        with self.assertRaisesRegex(AssertionError, "forbidden pattern"):
            validate_case_output(
                cases["contextual_docs_cleanup"],
                (
                    "This configuration supports scalable workflows and makes the "
                    "platform easier to use across cross-functional teams."
                ),
            )

    def test_docs_cleanup_rejects_softened_promotional_padding(self):
        cases = {case["id"]: case for case in load_fixture_cases()}
        padded_outputs = (
            (
                "This configuration gives developers a solid base for scalable "
                "workflows and helps cross-functional teams use the platform "
                "more productively."
            ),
            (
                "This configuration supports scalable workflows so developers "
                "can use the platform effectively across cross-functional teams."
            ),
            (
                "This configuration gives developers a reliable starting point for "
                "building scalable workflows on the platform across cross-functional "
                "teams."
            ),
            (
                "With this configuration, developers can use the platform for "
                "scalable workflows and productivity across cross-functional teams."
            ),
        )

        for output in padded_outputs:
            with self.subTest(output=output), self.assertRaisesRegex(
                AssertionError,
                "forbidden",
            ):
                validate_case_output(cases["contextual_docs_cleanup"], output)

    def test_targeted_fact_safe_contracts_accept_literal_outputs(self):
        cases = {case["id"]: case for case in load_fixture_cases()}

        validate_case_output(
            cases["unsupported_benefit_substitution"],
            "Atlas Draft can generate documentation and tests.",
        )
        validate_case_output(
            cases["epistemic_status_preservation"],
            "Which industry observers support the claim that Atlas Draft adoption is rising?",
        )
        validate_case_output(
            cases["already_natural_restraint"],
            cases["already_natural_restraint"]["source"],
        )

    def test_targeted_fact_safe_contracts_reject_known_regressions(self):
        cases = {case["id"]: case for case in load_fixture_cases()}
        rejected_outputs = {
            "unsupported_benefit_substitution": (
                "Atlas Draft generates documentation and tests so developers can "
                "move faster."
            ),
            "epistemic_status_preservation": "Atlas Draft adoption is rising.",
            "already_natural_restraint": "We shipped offline comments on Tuesday.",
        }

        for case_id, output in rejected_outputs.items():
            with self.subTest(case=case_id), self.assertRaises(AssertionError):
                validate_case_output(cases[case_id], output)

        with self.assertRaisesRegex(AssertionError, "forbidden"):
            validate_case_output(
                cases["epistemic_status_preservation"],
                "Some say Atlas Draft adoption is rising.",
            )

        with self.assertRaisesRegex(AssertionError, "required pattern"):
            validate_case_output(
                cases["epistemic_status_preservation"],
                "Atlas Draft adoption may be rising.",
            )

    def test_accepts_output_that_satisfies_constraints(self):
        output = "Atlas Note adoption rose 43%. The source is unnamed, so the claim should stay general."
        validate_case_output(BASE_CASE, output)

    def test_rejects_missing_required_fact(self):
        with self.assertRaises(AssertionError):
            validate_case_output(BASE_CASE, "Adoption rose last quarter.")

    def test_required_fragments_are_case_insensitive(self):
        validate_case_output(
            {"id": "required", "constraints": {"must_include": ["Atlas Note"]}},
            "atlas note adoption rose 43%. The source is unnamed, so the claim should stay general.",
        )

    def test_rejects_unsupported_constraint_keys(self):
        case = {"id": "unsupported", "constraints": {"must_includ": ["Atlas Note"]}}

        with self.assertRaisesRegex(AssertionError, "unsupported constraint"):
            validate_case_output(case, "Atlas Note adoption rose 43%.")

    def test_rejects_forbidden_fragment(self):
        with self.assertRaises(AssertionError):
            validate_case_output(BASE_CASE, "Atlas Note rose 43%, according to Gartner.")

    def test_rejects_forbidden_pattern(self):
        with self.assertRaises(AssertionError):
            validate_case_output(BASE_CASE, "Atlas Note rose 43%. This is a game-changer.")

    def test_rejects_missing_required_pattern(self):
        case = {"id": "score", "constraints": {"must_match": [r"Score:\s+\d+/80"]}}
        with self.assertRaises(AssertionError):
            validate_case_output(case, "Score unavailable.")

    def test_minimum_80_point_score_accepts_threshold(self):
        case = {
            "id": "score_threshold",
            "constraints": {"minimum_score_out_of_80": 56},
        }

        validate_case_output(case, "Score: 56/80")

    def test_minimum_80_point_score_rejects_low_score(self):
        case = {
            "id": "score_threshold",
            "constraints": {"minimum_score_out_of_80": 56},
        }

        with self.assertRaisesRegex(AssertionError, "below minimum"):
            validate_case_output(case, "Score: 55/80")

    def test_minimum_80_point_score_rejects_invalid_threshold(self):
        case = {
            "id": "score_threshold",
            "constraints": {"minimum_score_out_of_80": True},
        }

        with self.assertRaisesRegex(AssertionError, "integer from 0 to 80"):
            validate_case_output(case, "Score: 80/80")

    def test_minimum_80_point_score_rejects_score_above_80(self):
        case = {
            "id": "score_threshold",
            "constraints": {"minimum_score_out_of_80": 56},
        }

        with self.assertRaisesRegex(AssertionError, "exceeds 80/80"):
            validate_case_output(case, "Score: 81/80")

    def test_rejects_em_dash(self):
        with self.assertRaises(AssertionError):
            validate_case_output(BASE_CASE, "Atlas Note rose 43% \u2014 source unnamed.")

    def test_rejects_chatbot_wrapper_start(self):
        with self.assertRaises(AssertionError):
            validate_case_output(BASE_CASE, "Here is the rewritten version: Atlas Note rose 43%.")

    def test_rejects_too_many_question_marks(self):
        case = {"id": "questions", "constraints": {"max_question_marks": 1}}
        with self.assertRaises(AssertionError):
            validate_case_output(case, "What changed? Who reported it?")

    def test_rejects_markdown_fence_when_disallowed(self):
        case = {"id": "fence", "constraints": {"no_markdown_fence": True}}
        with self.assertRaises(AssertionError):
            validate_case_output(case, "```text\nAtlas Note rose 43%.\n```")

    def test_rejects_contrast_frame_when_disallowed(self):
        case = {"id": "contrast", "constraints": {"no_contrast_frame": True}}
        with self.assertRaises(AssertionError):
            validate_case_output(
                case,
                "AI coding assistants are not a replacement for engineers, but they help.",
            )

    def test_rejects_forced_rule_of_three_when_disallowed(self):
        case = {"id": "rule_of_three", "constraints": {"no_rule_of_three": True}}
        with self.assertRaisesRegex(AssertionError, "rule-of-three"):
            validate_case_output(
                case,
                "NovaBuild gives teams a robust, scalable, and innovative dashboard.",
            )

    def test_allows_concrete_source_backed_three_item_list(self):
        case = {
            "id": "concrete_list",
            "source": "The release includes documentation, tests, and refactors.",
            "constraints": {"no_rule_of_three": True},
        }

        validate_case_output(
            case,
            "The release includes documentation, tests, and refactors.",
        )

    def test_rejects_alignment_filler_in_three_item_list(self):
        case = {"id": "alignment_list", "constraints": {"no_rule_of_three": True}}
        with self.assertRaisesRegex(AssertionError, "rule-of-three"):
            validate_case_output(
                case,
                "AI coding assistants help with documentation, tests, and keeping teams aligned.",
            )

    def test_rejects_rewrite_only_meta_commentary(self):
        case = {"id": "rewrite", "constraints": {"rewrite_only": True}}
        with self.assertRaises(AssertionError):
            validate_case_output(case, "Atlas Note rose 43%.\n\nNotes: Removed AI phrasing.")

    def test_rejects_numbers_not_present_in_source_when_source_aware(self):
        case = {
            "id": "numbers",
            "source": "Atlas Note adoption rose 43% last quarter.",
            "constraints": {"no_new_numbers": True},
        }

        with self.assertRaisesRegex(AssertionError, "introduced number"):
            validate_case_output(case, "Atlas Note adoption rose 43% in 2026.")

    def test_rejects_named_entities_not_present_in_source_when_source_aware(self):
        case = {
            "id": "entities",
            "source": "Atlas Note adoption rose 43% last quarter.",
            "constraints": {"no_new_named_entities": True},
        }

        with self.assertRaisesRegex(AssertionError, "introduced named entity"):
            validate_case_output(
                case,
                "Atlas Note adoption rose 43%, according to Acme Research.",
            )

    def test_rejects_single_word_attribution_source_not_present_in_source(self):
        case = {
            "id": "single_word_entity",
            "source": "Atlas Note adoption rose 43% last quarter.",
            "constraints": {"no_new_named_entities": True},
        }

        with self.assertRaisesRegex(AssertionError, "introduced named entity"):
            validate_case_output(
                case,
                "Atlas Note adoption rose 43%, according to Gartner.",
            )

    def test_rejects_single_word_reporting_source_not_present_in_source(self):
        case = {
            "id": "single_word_reporting_source",
            "source": "The release includes offline comments and faster issue search.",
            "constraints": {"no_new_named_entities": True},
        }

        with self.assertRaisesRegex(AssertionError, "introduced named entity"):
            validate_case_output(
                case,
                "Gartner says the release includes offline comments and faster issue search.",
            )

    def test_allows_source_backed_single_word_reporting_source(self):
        case = {
            "id": "source_backed_reporting_source",
            "source": "Gartner says Atlas Note adoption rose 43% last quarter.",
            "constraints": {"no_new_named_entities": True},
        }

        validate_case_output(
            case,
            "Gartner says Atlas Note adoption rose 43% last quarter.",
        )

    def test_allows_question_word_before_reports_when_asking_for_missing_source(self):
        case = {
            "id": "missing_source_question",
            "source": "Industry reports show that Atlas Note adoption increased by 43% last quarter.",
            "constraints": {"no_new_named_entities": True},
        }

        validate_case_output(
            case,
            "Which reports support Atlas Note's 43% adoption increase last quarter?",
        )

    def test_allows_source_backed_sentence_initial_reporting_verb(self):
        case = {
            "id": "sentence_initial_reporting_verb",
            "source": "Users can edit notes on flights and sync them when they reconnect.",
            "constraints": {"no_new_named_entities": True},
        }

        validate_case_output(
            case,
            "Edit notes on flights and sync them when you reconnect.",
        )

    def test_rewrite_scoped_forbidden_fragments_allow_audit_notes(self):
        case = {
            "id": "audit",
            "constraints": {"rewrite_must_not_include": ["unlock collaboration"]},
        }

        validate_case_output(
            case,
            "Teams collaborate better when they are aligned.\n\n"
            "Notes: Removed vague “unlock collaboration” phrasing.",
        )

    def test_rewrite_scoped_forbidden_fragments_reject_rewrite_body(self):
        case = {
            "id": "audit",
            "constraints": {"rewrite_must_not_include": ["unlock collaboration"]},
        }

        with self.assertRaisesRegex(AssertionError, "rewrite contains forbidden fragment"):
            validate_case_output(
                case,
                "Teams can unlock collaboration when they align.\n\nNotes: Revised.",
            )

    def test_reports_all_contract_violations(self):
        case = {
            "id": "aggregate",
            "constraints": {
                "must_include": ["Atlas Note", "43%"],
                "must_not_include": ["Gartner"],
                "must_match": [r"Score:\s+\d+/80"],
                "no_em_dash": True,
            },
        }

        with self.assertRaises(AssertionError) as assertion:
            validate_case_output(case, "Gartner says adoption rose - Score: 8/10.")

        message = str(assertion.exception)
        self.assertIn("missing required fragment 'Atlas Note'", message)
        self.assertIn("missing required fragment '43%'", message)
        self.assertIn("required pattern missing", message)
        self.assertIn("forbidden fragment present 'Gartner'", message)


if __name__ == "__main__":
    unittest.main()
