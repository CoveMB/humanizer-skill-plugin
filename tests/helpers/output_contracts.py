import re


CHATBOT_WRAPPER_STARTS = (
    "here is",
    "here's",
    "certainly",
    "of course",
    "sure",
    "great question",
)

SUPPORTED_CONSTRAINT_KEYS = {
    "must_include",
    "must_include_exact",
    "must_match",
    "must_not_include",
    "must_not_match",
    "ordered_fragments",
    "exact_occurrences",
    "must_differ_from_source",
    "must_equal_source",
    "no_new_named_entities",
    "no_new_numbers",
    "no_em_dash",
    "no_chatbot_wrapper",
    "no_contrast_frame",
    "no_rule_of_three",
    "no_markdown_fence",
    "rewrite_must_not_include",
    "rewrite_only",
    "max_question_marks",
    "minimum_score_out_of_80",
    "minimum_sentence_count",
    "maximum_sentence_count",
    "maximum_word_count",
}

REWRITE_SECTION_BOUNDARY_PATTERN = re.compile(
    r"(?im)^\s*(?:#{1,6}\s*)?(?:\*\*)?"
    r"(?:brief\s+notes|notes|score|form\s+changes|preservation\s+notes|explanation)"
    r"(?:\*\*)?(?:\s*:\s*|\s*$)"
)

NUMBER_PATTERN = re.compile(
    r"(?<![\w.])(?:[$])?\d[\d,]*(?:\.\d+)?%?(?!\w)"
)
AUDIT_SCORE_PATTERN = re.compile(
    r"(?i)\b(?:score\s*:?\s*\d{1,2}/80|"
    r"factual\s+integrity\s*:\s*(?:\d|10)/10)\b"
)

CAMEL_CASE_PATTERN = re.compile(r"\b[A-Z][a-z]+(?:[A-Z][A-Za-z0-9]*)+\b")
ACRONYM_PATTERN = re.compile(r"\b[A-Z]{2,}\b")
TITLE_CASE_PHRASE_PATTERN = re.compile(
    r"\b[A-Z][A-Za-z0-9]*(?:\s+[A-Z][A-Za-z0-9]*)+\b"
)
ATTRIBUTION_SOURCE_PATTERN = re.compile(
    r"\b(?i:according\s+to)\s+(?:(?i:a|an|the)\s+)?([A-Z][A-Za-z0-9]*)\b"
)
REPORTING_SOURCE_PATTERN = re.compile(
    r"\b([A-Z][A-Za-z0-9]*)\s+"
    r"(?i:says|said|reports|reported|claims|claimed|notes|noted|"
    r"found|finds|argues|argued|writes|wrote)\b"
)
QUESTION_REPORTING_SOURCE_TERMS = {
    "what",
    "which",
    "who",
    "whose",
}

CONTRAST_FRAME_PATTERNS = (
    r"(?i)\bnot\s+only\b[^.?!]{0,120}\bbut\b",
    r"(?i)\bnot\s+just\b[^.?!]{0,120}\bbut\b",
    r"(?i)\bnot\s+merely\b[^.?!]{0,120}\bbut\b",
    r"(?i)\bnot\s+(?:a|an|the)\b[^.?!]{0,120}\bbut\b",
    r"(?i)\bmore\s+than\s+just\b",
)

GENERIC_RULE_OF_THREE_TERMS = (
    "align",
    "aligned",
    "aligning",
    "alignment",
    "creativity",
    "groundbreaking",
    "innovation",
    "innovative",
    "intuitive",
    "powerful",
    "productivity",
    "robust",
    "scalable",
    "seamless",
    "synergy",
)

GENERIC_RULE_OF_THREE_TERM_PATTERN = re.compile(
    r"(?i)\b(?:"
    + "|".join(re.escape(term) for term in GENERIC_RULE_OF_THREE_TERMS)
    + r")\b"
)

THREE_ITEM_LIST_PATTERN = re.compile(
    r"(?i)\b([^,.;!?]{1,80}),\s+([^,.;!?]{1,80}),\s+(?:and|or)\s+([^,.;!?]{1,80})(?=$|[.?!;:])"
)

RULE_OF_THREE_PATTERNS = (
    r"(?i)\b\w+ing\b[^.?!,]{0,80},\s+\w+ing\b[^.?!,]{0,80},\s+and\s+\w+ing\b",
)

REWRITE_ONLY_META_FRAGMENTS = (
    "notes:",
    "score:",
    "changes made:",
    "rewrite:",
    "rewritten text:",
)

SENTENCE_END_PATTERN = re.compile(r"[.!?]+(?:[\"'”’)]*)?(?=\s|$)")


def normalize_text(text):
    return " ".join(text.strip().split())


def unique_normalized_terms(terms):
    return list(dict.fromkeys(term.lower() for term in terms))


def raise_if_violations(violations):
    violation_list = list(violations)
    if violation_list:
        raise AssertionError("\n".join(violation_list))


def reject_unsupported_constraint_keys(case_id, constraints):
    unsupported_keys = sorted(set(constraints) - SUPPORTED_CONSTRAINT_KEYS)
    raise_if_violations(
        f"{case_id}: unsupported constraint key {constraint_key!r}"
        for constraint_key in unsupported_keys
    )


def require_fragments(case_id, output, fragments):
    lowered_output = output.lower()
    missing_fragments = [
        fragment for fragment in fragments if fragment.lower() not in lowered_output
    ]
    raise_if_violations(
        f"{case_id}: missing required fragment {fragment!r}"
        for fragment in missing_fragments
    )


def require_exact_fragments(case_id, output, fragments):
    missing_fragments = [fragment for fragment in fragments if fragment not in output]
    raise_if_violations(
        f"{case_id}: missing required exact fragment {fragment!r}"
        for fragment in missing_fragments
    )


def require_fragments_in_order(case_id, output, fragments):
    normalized_output = normalize_text(output).casefold()
    search_start = 0
    violations = []
    for fragment in fragments:
        normalized_fragment = normalize_text(fragment).casefold()
        fragment_index = normalized_output.find(normalized_fragment, search_start)
        if fragment_index == -1:
            violations.append(
                f"{case_id}: ordered fragment missing or out of order {fragment!r}"
            )
            break
        search_start = fragment_index + len(normalized_fragment)
    raise_if_violations(violations)


def reject_fragments(case_id, output, fragments):
    lowered_output = output.lower()
    present_fragments = [
        fragment for fragment in fragments if fragment.lower() in lowered_output
    ]
    raise_if_violations(
        f"{case_id}: forbidden fragment present {fragment!r}"
        for fragment in present_fragments
    )


def reject_rewrite_fragments(case_id, output, fragments):
    rewrite_text = extract_rewrite_section(output)
    lowered_rewrite_text = rewrite_text.lower()
    present_fragments = [
        fragment for fragment in fragments if fragment.lower() in lowered_rewrite_text
    ]
    raise_if_violations(
        f"{case_id}: rewrite contains forbidden fragment {fragment!r}"
        for fragment in present_fragments
    )


def reject_patterns(case_id, output, patterns):
    matched_patterns = [pattern for pattern in patterns if re.search(pattern, output)]
    raise_if_violations(
        f"{case_id}: forbidden pattern matched {pattern!r}"
        for pattern in matched_patterns
    )


def require_patterns(case_id, output, patterns):
    missing_patterns = [
        pattern for pattern in patterns if re.search(pattern, output) is None
    ]
    raise_if_violations(
        f"{case_id}: required pattern missing {pattern!r}"
        for pattern in missing_patterns
    )


def enforce_exact_occurrences(case_id, output, expected_occurrences):
    if not isinstance(expected_occurrences, dict):
        raise AssertionError(f"{case_id}: exact_occurrences must be an object")
    violations = []
    lowered_output = output.lower()
    for fragment, expected_count in expected_occurrences.items():
        if not isinstance(fragment, str) or not fragment:
            violations.append(
                f"{case_id}: exact_occurrences keys must be non-empty strings"
            )
            continue
        if type(expected_count) is not int or expected_count < 0:
            violations.append(
                f"{case_id}: exact occurrence count for {fragment!r} must be a "
                "non-negative integer"
            )
            continue
        actual_count = lowered_output.count(fragment.lower())
        if actual_count != expected_count:
            violations.append(
                f"{case_id}: {fragment!r} occurs {actual_count} time(s); "
                f"expected {expected_count}"
            )
    raise_if_violations(violations)


def require_source_change(case_id, source, output):
    if normalize_text(source).casefold() == normalize_text(output).casefold():
        raise AssertionError(f"{case_id}: output did not rewrite the source")


def require_source_equality(case_id, source, output):
    if source.strip() != output.strip():
        raise AssertionError(f"{case_id}: output changed already-natural source text")


def reject_em_dash(case_id, output):
    if "\u2014" in output:
        raise AssertionError(f"{case_id}: output contains an em dash")


def reject_markdown_fence(case_id, output):
    if "```" in output:
        raise AssertionError(f"{case_id}: output contains a markdown fence")


def reject_contrast_frames(case_id, output):
    matched_patterns = [
        pattern for pattern in CONTRAST_FRAME_PATTERNS if re.search(pattern, output)
    ]
    raise_if_violations(
        f"{case_id}: contrast frame matched {pattern!r}"
        for pattern in matched_patterns
    )


def has_generic_rule_of_three_term(item):
    return GENERIC_RULE_OF_THREE_TERM_PATTERN.search(item) is not None


def iter_generic_rule_of_three_lists(output):
    for match in THREE_ITEM_LIST_PATTERN.finditer(output):
        items = match.groups()
        if any(has_generic_rule_of_three_term(item) for item in items):
            yield match.group(0).strip()


def reject_rule_of_three(case_id, output):
    matched_patterns = [
        pattern for pattern in RULE_OF_THREE_PATTERNS if re.search(pattern, output)
    ]
    matched_generic_lists = list(iter_generic_rule_of_three_lists(output))
    raise_if_violations(
        [
            *(
                f"{case_id}: rule-of-three pattern matched {pattern!r}"
                for pattern in matched_patterns
            ),
            *(
                f"{case_id}: generic rule-of-three list matched {matched_list!r}"
                for matched_list in matched_generic_lists
            ),
        ]
    )


def extract_number_tokens(text):
    return unique_normalized_terms(
        match.group(0).replace(",", "") for match in NUMBER_PATTERN.finditer(text)
    )


def extract_named_entity_terms(text):
    text = REWRITE_SECTION_BOUNDARY_PATTERN.sub("", text)
    matches = [
        *(match.group(0) for match in TITLE_CASE_PHRASE_PATTERN.finditer(text)),
        *(match.group(0) for match in CAMEL_CASE_PATTERN.finditer(text)),
        *(match.group(0) for match in ACRONYM_PATTERN.finditer(text)),
        *(match.group(1) for match in ATTRIBUTION_SOURCE_PATTERN.finditer(text)),
        *(
            match.group(1)
            for match in REPORTING_SOURCE_PATTERN.finditer(text)
            if match.group(1).lower() not in QUESTION_REPORTING_SOURCE_TERMS
        ),
    ]
    return unique_normalized_terms(matches)


def source_contains_term(source, term):
    return re.search(
        rf"(?i)(?<!\w){re.escape(term)}(?!\w)",
        source,
    ) is not None


def reject_introduced_terms(
    case_id,
    source,
    output,
    extract_terms,
    term_label,
    allow_source_text_match=False,
):
    source_terms = set(extract_terms(source))
    introduced_terms = [
        term
        for term in extract_terms(output)
        if term not in source_terms
        and not (allow_source_text_match and source_contains_term(source, term))
    ]
    raise_if_violations(
        f"{case_id}: introduced {term_label} not present in source {term!r}"
        for term in introduced_terms
    )


def reject_new_numbers(case_id, source, output):
    reject_introduced_terms(case_id, source, output, extract_number_tokens, "number")


def reject_new_named_entities(case_id, source, output):
    reject_introduced_terms(
        case_id,
        source,
        output,
        extract_named_entity_terms,
        "named entity",
        allow_source_text_match=True,
    )


def reject_rewrite_only_meta_commentary(case_id, output):
    lowered_output = output.lower()
    present_fragments = [
        fragment for fragment in REWRITE_ONLY_META_FRAGMENTS if fragment in lowered_output
    ]
    raise_if_violations(
        f"{case_id}: rewrite-only output contains meta fragment {fragment!r}"
        for fragment in present_fragments
    )


def reject_chatbot_wrapper(case_id, output):
    stripped_output = output.strip().lower()
    start_violations = (
        f"{case_id}: output starts with chatbot wrapper {wrapper_start!r}"
        for wrapper_start in CHATBOT_WRAPPER_STARTS
        if stripped_output.startswith(wrapper_start)
    )

    lowered_output = output.lower()
    wrapper_closers = ("i hope this helps", "let me know", "would you like me to")
    closer_violations = (
        f"{case_id}: output contains chatbot closer {wrapper_closer!r}"
        for wrapper_closer in wrapper_closers
        if wrapper_closer in lowered_output
    )
    raise_if_violations([*start_violations, *closer_violations])


def extract_rewrite_section(output):
    section_boundary = REWRITE_SECTION_BOUNDARY_PATTERN.search(output)
    if section_boundary is None:
        return output
    return output[: section_boundary.start()].strip()


def enforce_question_limit(case_id, output, maximum_question_marks):
    question_mark_count = output.count("?")
    if question_mark_count > maximum_question_marks:
        raise AssertionError(
            f"{case_id}: expected at most {maximum_question_marks} question marks, "
            f"found {question_mark_count}"
        )


def enforce_minimum_score_out_of_80(case_id, output, minimum_score):
    if (
        not isinstance(minimum_score, int)
        or isinstance(minimum_score, bool)
        or not 0 <= minimum_score <= 80
    ):
        raise AssertionError(
            f"{case_id}: minimum_score_out_of_80 must be an integer from 0 to 80"
        )

    score_match = re.search(r"(?i)\bscore\s*:\s*(\d{1,2})/80\b", output)
    if score_match is None:
        raise AssertionError(f"{case_id}: missing Score: NN/80")

    score = int(score_match.group(1))
    if score > 80:
        raise AssertionError(f"{case_id}: score {score}/80 exceeds 80/80")
    if score < minimum_score:
        raise AssertionError(
            f"{case_id}: score {score}/80 below minimum {minimum_score}/80"
        )


def count_sentences(text):
    return len(SENTENCE_END_PATTERN.findall(text.strip()))


def count_words(text):
    normalized_text = normalize_text(text)
    return len(normalized_text.split()) if normalized_text else 0


def enforce_maximum_word_count(case_id, output, maximum_word_count):
    if type(maximum_word_count) is not int or maximum_word_count < 1:
        raise AssertionError(
            f"{case_id}: maximum_word_count must be a positive integer"
        )

    actual_count = count_words(output)
    if actual_count > maximum_word_count:
        raise AssertionError(
            f"{case_id}: found {actual_count} words; expected at most "
            f"{maximum_word_count} words"
        )


def require_sentence_count_bound(case_id, output, expected_count, relation):
    if type(expected_count) is not int or expected_count < 1:
        raise AssertionError(
            f"{case_id}: {relation}_sentence_count must be a positive integer"
        )

    actual_count = count_sentences(extract_rewrite_section(output))
    if relation == "minimum" and actual_count < expected_count:
        raise AssertionError(
            f"{case_id}: found {actual_count} sentence(s); expected at least "
            f"{expected_count}"
        )
    if relation == "maximum" and actual_count > expected_count:
        raise AssertionError(
            f"{case_id}: found {actual_count} sentence(s); expected at most "
            f"{expected_count}"
        )


def collect_violation(violations, check_function, *args):
    try:
        check_function(*args)
    except AssertionError as error:
        violations.append(str(error))


def validate_case_output(case, output):
    case_id = case["id"]
    constraints = case.get("constraints", {})
    source = case.get("source", "")
    normalized_output = normalize_text(output)
    violations = []

    collect_violation(violations, reject_unsupported_constraint_keys, case_id, constraints)

    collect_violation(
        violations,
        require_fragments,
        case_id,
        normalized_output,
        constraints.get("must_include", []),
    )
    collect_violation(
        violations,
        require_exact_fragments,
        case_id,
        output,
        constraints.get("must_include_exact", []),
    )
    collect_violation(
        violations,
        require_patterns,
        case_id,
        output,
        constraints.get("must_match", []),
    )
    collect_violation(
        violations,
        reject_fragments,
        case_id,
        normalized_output,
        constraints.get("must_not_include", []),
    )
    collect_violation(
        violations,
        reject_rewrite_fragments,
        case_id,
        output,
        constraints.get("rewrite_must_not_include", []),
    )
    collect_violation(
        violations,
        reject_patterns,
        case_id,
        output,
        constraints.get("must_not_match", []),
    )

    collect_violation(
        violations,
        require_fragments_in_order,
        case_id,
        output,
        constraints.get("ordered_fragments", []),
    )

    if "exact_occurrences" in constraints:
        collect_violation(
            violations,
            enforce_exact_occurrences,
            case_id,
            normalized_output,
            constraints["exact_occurrences"],
        )

    if constraints.get("must_differ_from_source", False):
        collect_violation(
            violations,
            require_source_change,
            case_id,
            source,
            normalized_output,
        )

    if constraints.get("must_equal_source", False):
        collect_violation(
            violations,
            require_source_equality,
            case_id,
            source,
            output,
        )

    if constraints.get("no_em_dash", False):
        collect_violation(violations, reject_em_dash, case_id, normalized_output)

    if constraints.get("no_markdown_fence", False):
        collect_violation(violations, reject_markdown_fence, case_id, output)

    if constraints.get("no_chatbot_wrapper", False):
        collect_violation(violations, reject_chatbot_wrapper, case_id, normalized_output)

    if constraints.get("no_contrast_frame", False):
        collect_violation(violations, reject_contrast_frames, case_id, normalized_output)

    if constraints.get("no_rule_of_three", False):
        collect_violation(violations, reject_rule_of_three, case_id, normalized_output)

    if constraints.get("no_new_numbers", False):
        source_aware_output = output
        if "minimum_score_out_of_80" in constraints:
            source_aware_output = AUDIT_SCORE_PATTERN.sub("", output)
        collect_violation(
            violations,
            reject_new_numbers,
            case_id,
            source,
            source_aware_output,
        )

    if constraints.get("no_new_named_entities", False):
        collect_violation(violations, reject_new_named_entities, case_id, source, output)

    if constraints.get("rewrite_only", False):
        collect_violation(
            violations,
            reject_rewrite_only_meta_commentary,
            case_id,
            normalized_output,
        )

    if "max_question_marks" in constraints:
        collect_violation(
            violations,
            enforce_question_limit,
            case_id,
            normalized_output,
            constraints["max_question_marks"],
        )

    if "minimum_score_out_of_80" in constraints:
        collect_violation(
            violations,
            enforce_minimum_score_out_of_80,
            case_id,
            normalized_output,
            constraints["minimum_score_out_of_80"],
        )

    if "maximum_word_count" in constraints:
        collect_violation(
            violations,
            enforce_maximum_word_count,
            case_id,
            output,
            constraints["maximum_word_count"],
        )

    for relation in ("minimum", "maximum"):
        constraint_key = f"{relation}_sentence_count"
        if constraint_key in constraints:
            collect_violation(
                violations,
                require_sentence_count_bound,
                case_id,
                output,
                constraints[constraint_key],
                relation,
            )

    if violations:
        raise AssertionError("\n".join(violations))
