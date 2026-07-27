# Plain Language Humanizer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a two-mode Plain Language Humanizer that makes supplied technical content understandable to an informed non-specialist without changing technical meaning, protected literals, warnings, or operational order.

**Architecture:** Add one self-contained `plain-language-humanizer` skill beside the existing Editorial and Faithful skills. Extend the existing deterministic contract and evaluation infrastructure with a case-specific word-count ceiling and `plain_language_mode`, then expose the third skill through existing plugin metadata, documentation, CI, and live-eval entry points. Preserve all existing Editorial and Faithful contracts and avoid broad evaluator refactoring.

**Tech Stack:** Markdown Agent Skill, JSON plugin/eval fixtures, Python 3.12 standard library, `unittest`, `coverage`, Make, GitHub Actions, Codex plugin CLI.

## Global Constraints

- The approved design is `docs/superpowers/specs/2026-07-27-plain-language-humanizer-design.md`; read it completely before Task 1.
- Skill name and folder: `plain-language-humanizer`.
- Skill version: `1.0.0`.
- Plugin version: `3.1.0`.
- Modes: `rewrite` and `explain`; Rewrite is the deterministic default.
- Default audience: an informed non-specialist; a supplied audience overrides it.
- Scope includes software, engineering, scientific, medical, legal, financial, security, policy, and other technical domains.
- Preserve every substantive claim, condition, warning, prerequisite, step, qualifier, conclusion, and meaningful order.
- Preserve code, commands, flags, identifiers, configuration keys, API names, schema fields, error messages, URLs, paths, versions, citations, formulas, units, and other technically meaningful literals exactly.
- Necessary technical terms remain and receive one brief definition; unnecessary jargon receives a precise everyday replacement.
- Rewrite mode returns only replacement text. Explain mode returns only a source-grounded explanation. A combined request returns the rewrite followed by `Explanation:`.
- Every added sentence must define a necessary term, clarify a relationship, or explain a required action or source-supported consequence.
- Do not claim WCAG, dyslexia-specific, or reading-grade compliance.
- Do not turn this skill into research, fact-checking, troubleshooting, translation, summarization, professional advice, or detector evasion.
- Existing Editorial and Faithful behavior and skill versions remain unchanged.
- Do not create a branch, commit prefix, file, command, or Git label prefixed with `codex`.
- Do not create a pull request or respond to review comments unless the user explicitly asks.
- Use a meaningful stash name if execution requires stashing unrelated user changes.
- Live model evaluation requires a separate user confirmation because it can consume external model resources.

## Execution preflight

Before Task 1, fetch the remote, verify the intended branch, confirm the worktree is clean except for the approved design and plan commits, and run the deterministic baseline:

```bash
git fetch --all --prune
git status --short --branch
git branch --show-current
git rev-list --left-right --count HEAD...origin/main
make test
make eval-humanizer-dry-run
```

Expected baseline on the approved design commit: 185 deterministic tests pass and 38 eval cases validate. If remote history changed, inspect the incoming diff before implementing. Do not overwrite unrelated work.

## File map

**Create**

- `skills/plain-language-humanizer/SKILL.md` — public trigger contract, mode routing, transformation workflow, safety rules, and output shapes.
- `tests/test_plain_language_humanizer_artifacts.py` — deterministic checks for skill metadata and required behavioral contracts.

**Modify**

- `tests/helpers/skill_artifacts.py` — shared path constant for the third skill.
- `tests/helpers/output_contracts.py` — `maximum_word_count` validation and enforcement; recognize `Explanation:` as a rewrite-section boundary.
- `tests/test_output_contracts.py` — direct word-count and combined-output boundary tests.
- `tests/test_contract_fixture_quality.py` — fixture schema and required Plain Language tag/mode coverage.
- `tests/fixtures/humanizer_contract_cases.json` — deterministic cross-domain Plain Language cases.
- `scripts/run_humanizer_evals.py` — third target, mode validation/filtering, prompt metadata, visibility, summaries, and calibration support.
- `tests/test_humanizer_eval_runner.py` — unit coverage for every new evaluator branch and compatibility behavior.
- `evals/humanizer_eval_cases.json` — Plain Language cases, rubric, and calibrations.
- `.codex-plugin/plugin.json` — package version, third-skill description, keywords, and default prompts.
- `README.md` — three-skill/five-behavior selection, examples, installation, layout, eval commands, limits, and license scope.
- `docs/skill-examples.md` — Rewrite, Explain, combined, high-stakes, and client activation examples; fix the 17-versus-12 context drift.
- `skills/references/registers/scientific-writing.md` — Plain Language preservation profile.
- `NOTICE` — identify Plain Language Humanizer as original MIT work.
- `.github/workflows/test.yml` — deterministic Plain Language mode-filter dry-runs.
- `.github/workflows/live-eval.yml` — expose the third skill as a manual target option.
- `tests/test_skill_artifacts.py` — package metadata, documentation, install, CI, and version assertions for three skills.

---

### Task 1: Capture no-skill baseline failures

**Files:**

- Read: `docs/superpowers/specs/2026-07-27-plain-language-humanizer-design.md`
- Read: `skills/editorial-humanizer/SKILL.md`
- Read: `skills/faithful-humanizer/SKILL.md`
- Runtime artifacts only: `evals/artifacts/plain-language-baseline/` (ignored by Git)

**Interfaces:**

- Consumes: the approved Plain Language contract and six prompts below.
- Produces: an evidence table containing each prompt, raw output, material failure, and exact failure wording. Task 3 uses this evidence to choose positive recipes and conditional rules.

- [ ] **Step 1: Run six fresh-context controls without the new skill**

Dispatch read-only agents with `fork_turns="none"`; prohibit recursive fan-out and do not expose the approved design or desired answer. Run independent controls for these exact requests:

```text
Control A — Rewrite / API jargon
Rewrite this for a nontechnical project manager. Keep every technical fact:
The API enforces a per-client rate limit of 120 requests per minute and returns
HTTP 429 for requests above the threshold.

Control B — Explain / webhook
Explain this to an informed non-specialist without adding outside facts:
When an invoice is paid, Ledger emits an `invoice.paid` webhook to the configured
HTTPS endpoint. Delivery is retried with exponential backoff for up to 24 hours.

Control C — Protected procedure
Make this procedure easier to understand without changing commands, warnings, or order:
Run `atlas migrate --dry-run` before `atlas migrate --apply`. Do not use `--apply`
if validation reports an incompatible schema. If the second command fails, restore
`/srv/atlas/schema.json`.

Control D — Scientific boundary
Rewrite for a general policy audience without changing the statistics or causal boundary:
Smith et al. (2024) reported a hazard ratio of 0.78 (95% CI 0.61–0.99). This
association does not establish causality.

Control E — Medical condition
Rewrite for a patient without changing the dose, threshold, prohibition, or escalation:
Take 5 mg once daily. If systolic blood pressure falls below 90 mmHg, do not take
the next dose and contact the prescribing clinician.

Control F — Already clear
Use plain language but leave text unchanged when it is already clear:
Run `make test` before deployment. Stop if any test fails.
```

- [ ] **Step 2: Record the observed failure classes**

For each raw output, record whether it exhibits any of these material defects:

```text
retained_unnecessary_jargon
imprecise_everyday_substitution
dropped_qualifier_or_causal_boundary
invented_definition_or_consequence
excess_background_or_repetition
altered_literal_warning_or_order
unnecessary_change_to_clear_text
wrong_mode_shape
```

Record exact output wording for every defect. If a control consistently succeeds, keep its behavior as a regression case but do not add extra skill prose solely for that control.

- [ ] **Step 3: Confirm the baseline is an evidence gate**

Expected: at least one control exhibits a material defect or inconsistent output shape. If all controls succeed, add two fresh variants for the riskiest classes—protected procedure and causal boundary—before proceeding. Do not write `SKILL.md` until the no-skill behavior has been observed.

No commit is created for this read-only task.

---

### Task 2: Add the deterministic anti-bloat constraint

**Files:**

- Modify: `tests/helpers/output_contracts.py:13-45,397-612`
- Modify: `tests/test_output_contracts.py:1-110`
- Modify: `tests/test_contract_fixture_quality.py:1-140`

**Interfaces:**

- Consumes: full output text and `constraints["maximum_word_count"]`.
- Produces: `count_words(text: str) -> int` and `enforce_maximum_word_count(case_id: str, output: str, maximum_word_count: int) -> None`.
- Invariant: count the full normalized output, including an `Explanation:` section.

- [ ] **Step 1: Write failing output-contract tests**

Add these methods to `OutputContractTests`:

```python
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
```

Add this fixture-quality test:

```python
def test_maximum_word_count_constraints_are_positive_integers(self):
    for case in self.cases:
        maximum_word_count = case["constraints"].get("maximum_word_count")
        if maximum_word_count is None:
            continue
        with self.subTest(case=case["id"]):
            self.assertIs(type(maximum_word_count), int)
            self.assertGreater(maximum_word_count, 0)
```

- [ ] **Step 2: Run the focused tests and verify RED**

Run:

```bash
python3 -m unittest \
  tests.test_output_contracts.OutputContractTests.test_enforces_maximum_word_count_on_full_output \
  tests.test_output_contracts.OutputContractTests.test_maximum_word_count_includes_combined_explanation \
  tests.test_output_contracts.OutputContractTests.test_maximum_word_count_requires_a_positive_integer -v
```

Expected: failures report `unsupported constraint key 'maximum_word_count'`.

- [ ] **Step 3: Implement the word-count contract**

Add `"maximum_word_count"` to `SUPPORTED_CONSTRAINT_KEYS`. Add these functions beside the sentence-count helpers:

```python
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
```

Invoke it near the other numeric constraints:

```python
if "maximum_word_count" in constraints:
    collect_violation(
        violations,
        enforce_maximum_word_count,
        case_id,
        output,
        constraints["maximum_word_count"],
    )
```

Add `explanation` to `REWRITE_SECTION_BOUNDARY_PATTERN` so rewrite-scoped constraints stop at a combined response's `Explanation:` label:

```python
r"(?:brief\s+notes|notes|score|form\s+changes|preservation\s+notes|explanation)"
```

- [ ] **Step 4: Run focused and full contract tests**

Run:

```bash
python3 -m unittest tests.test_output_contracts tests.test_contract_fixture_quality -v
```

Expected: all output-contract and fixture-quality tests pass.

- [ ] **Step 5: Commit the anti-bloat primitive**

```bash
git add tests/helpers/output_contracts.py tests/test_output_contracts.py tests/test_contract_fixture_quality.py
git commit -m "test: add maximum word count contract"
```

---

### Task 3: Add the Plain Language skill artifact test-first

**Files:**

- Modify: `tests/helpers/skill_artifacts.py:1-25`
- Create: `tests/test_plain_language_humanizer_artifacts.py`
- Create: `skills/plain-language-humanizer/SKILL.md`
- Modify: `skills/references/registers/scientific-writing.md`

**Interfaces:**

- Consumes: the approved design, Task 1 baseline failures, and the shared scientific reference.
- Produces: a discoverable `plain-language-humanizer` skill at version `1.0.0` with Rewrite and Explain mode contracts.
- Produces: `PLAIN_LANGUAGE_SKILL_PATH` for all later artifact and provenance tests.

- [ ] **Step 1: Add the shared skill path and failing artifact test**

Add to `tests/helpers/skill_artifacts.py`:

```python
PLAIN_LANGUAGE_SKILL_PATH = (
    REPO_ROOT / "skills" / "plain-language-humanizer" / "SKILL.md"
)
```

Create `tests/test_plain_language_humanizer_artifacts.py` with this structure:

```python
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


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the artifact test and verify RED**

Run:

```bash
python3 -m unittest tests.test_plain_language_humanizer_artifacts -v
```

Expected: `FileNotFoundError` for `skills/plain-language-humanizer/SKILL.md`.

- [ ] **Step 3: Write the minimal skill that satisfies the approved contract and observed failures**

Create `skills/plain-language-humanizer/SKILL.md` with this exact frontmatter shape:

```markdown
---
name: plain-language-humanizer
version: 1.0.0
description: |
  Adapt supplied technical content for a less technical audience. Use whenever the
  user explicitly invokes `$plain-language-humanizer`, asks for plain language,
  reduced jargon, a nontechnical reader, or a concise explanation of supplied
  technical content. Rewrite mode is the default; Explain mode is opt-in. Do not
  use for broad editorial selection, strict form-only preservation, research,
  troubleshooting, fact-checking, translation, summarization, professional advice,
  or AI-detector evasion; use editorial-humanizer or faithful-humanizer when their
  authority boundary fits instead.
license: MIT
compatibility: claude-code opencode codex
allowed-tools:
  - Read
  - Write
  - Edit
  - Grep
  - Glob
  - AskUserQuestion
---
```

Use these headings in this order and fill them with the normative requirements from the identically named sections of the approved design:

```markdown
# Plain Language Humanizer: Technical Meaning in Plain Language

## Purpose
## Direct distinction from the other Humanizers
## Audience
## Deterministic mode selection
## Shared technical-preservation contract
## Technical-content ledger
## Protected literals
## Language classification
## Rewrite mode
## Explain mode
## Combined requests
## Anti-bloat contract
## High-stakes technical content
## Scientific and academic profile
## Missing or conflicting context
## Rewrite workflow
## Explain workflow
## Final bidirectional content check
## Output
## Examples
```

The examples must include the exact API, webhook, protected migration procedure, scientific causal-boundary, and already-clear sources from Task 1. Show one correct Rewrite output, one correct Explain output, one combined output with `Explanation:`, and one restore-or-ask outcome for an ambiguous term. Keep the file below 500 lines.

Use positive output recipes for mode shape and anti-bloat behavior. Use prohibitions only for hard preservation and scope boundaries. Every extra instruction beyond the approved design must trace to a defect recorded in Task 1.

- [ ] **Step 4: Extend the scientific-register reference**

Add a `## Plain Language Humanizer` section to `skills/references/registers/scientific-writing.md` containing these requirements:

```markdown
## Plain Language Humanizer

Plain Language Humanizer uses this file as precision constraints while adapting
scientific content for an informed non-specialist.

- Retain exact technical terms when an everyday substitute would change meaning;
  define the term briefly at first meaningful use.
- Preserve citations, quantities, units, statistical estimates, intervals,
  uncertainty, attribution, evidence boundaries, and causal strength.
- Preserve legitimate passive constructions when the actor is unknown or the
  measured object is the scientific focus.
- Do not turn an association into a cause, a hypothesis into a finding, or a
  population-specific result into a general claim.
- Explain a conventional term only at the level supported by the source and its
  unambiguous disciplinary meaning. Ask when a term is overloaded or context is
  missing.
- Prefer the shortest explanation that keeps the scientific distinction intact.
```

- [ ] **Step 5: Run validation and artifact tests**

Run:

```bash
python3 -m unittest tests.test_plain_language_humanizer_artifacts -v
python3 /Users/CoveMB/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/plain-language-humanizer
wc -l skills/plain-language-humanizer/SKILL.md
```

Expected: all artifact tests pass, the validator succeeds, and the skill is under 500 lines. If the generic validator rejects repository-standard optional frontmatter fields, record the exact incompatibility and rely on the repository artifact parser rather than deleting established metadata.

- [ ] **Step 6: Commit the skill artifact**

```bash
git add \
  skills/plain-language-humanizer/SKILL.md \
  skills/references/registers/scientific-writing.md \
  tests/helpers/skill_artifacts.py \
  tests/test_plain_language_humanizer_artifacts.py
git commit -m "feat: add plain language humanizer skill"
```

---

### Task 4: Extend evaluator target and mode plumbing

**Files:**

- Modify: `scripts/run_humanizer_evals.py:30-55,217-245,415-475,492-545,761-845,889-945,1387-1430,1508-1590,1666-1730`
- Modify: `tests/test_humanizer_eval_runner.py`

**Interfaces:**

- Consumes: eval cases with `target_skill="plain-language-humanizer"` and `plain_language_mode` equal to `rewrite` or `explain`.
- Produces: `plain_language_mode_for_case(case) -> str | None`, `--plain-language-mode`, prompt mode metadata, `summary["plain_language_mode"]`, and `aggregate["by_plain_language_mode"]`.
- Preserves: `faithful_mode`, `--faithful-mode`, and `by_faithful_mode` behavior.

- [ ] **Step 1: Add failing mode-validation and parser tests**

Add tests with these exact assertions:

```python
def test_load_eval_cases_requires_plain_language_mode(self):
    with self.assertRaisesRegex(ValueError, "plain_language_mode must be one of"):
        self._load_cases_from_data(
            {
                "cases": [
                    minimal_eval_case(target_skill="plain-language-humanizer")
                ]
            },
            output_contract_cases={},
        )

def test_load_eval_cases_rejects_unknown_plain_language_mode(self):
    with self.assertRaisesRegex(ValueError, "plain_language_mode must be one of"):
        self._load_cases_from_data(
            {
                "cases": [
                    minimal_eval_case(
                        target_skill="plain-language-humanizer",
                        plain_language_mode="tutorial",
                    )
                ]
            },
            output_contract_cases={},
        )

def test_load_eval_cases_rejects_plain_language_mode_on_other_skill(self):
    with self.assertRaisesRegex(
        ValueError,
        "plain_language_mode is only valid for plain-language-humanizer",
    ):
        self._load_cases_from_data(
            {"cases": [minimal_eval_case(plain_language_mode="rewrite")]},
            output_contract_cases={},
        )

def test_parser_accepts_plain_language_mode_filter(self):
    args = self.runner.build_parser().parse_args(
        [
            "--target-skill",
            "plain-language-humanizer",
            "--plain-language-mode",
            "explain",
        ]
    )
    self.assertEqual(args.target_skill, ["plain-language-humanizer"])
    self.assertEqual(args.plain_language_mode, ["explain"])
```

Use the existing temporary-JSON helper used by neighboring validation tests; do not add another file-writing abstraction.

- [ ] **Step 2: Add failing prompt, selection, visibility, and summary tests**

Add tests that assert:

```python
case = minimal_eval_case(
    target_skill="plain-language-humanizer",
    plain_language_mode="explain",
    force_skill_file_read=True,
)
prompt = self.runner.build_codex_prompt(case)
self.assertIn("skills/plain-language-humanizer/SKILL.md", prompt)
self.assertIn("Plain Language mode: explain.", prompt)

selected = self.runner.select_cases(
    [
        minimal_eval_case(id="rewrite", target_skill="plain-language-humanizer", plain_language_mode="rewrite"),
        minimal_eval_case(id="explain", target_skill="plain-language-humanizer", plain_language_mode="explain"),
    ],
    filters=[],
    plain_language_modes=["explain"],
)
self.assertEqual([case["id"] for case in selected], ["explain"])
```

Update the existing visibility test to expect all three installed `SKILL.md` paths. Extend the aggregate-summary test with one Rewrite and one Explain summary and assert:

```python
self.assertEqual(
    aggregate["by_plain_language_mode"],
    {
        "explain": {"runs": 1, "passed": 1, "pass_rate": 1.0},
        "rewrite": {"runs": 1, "passed": 0, "pass_rate": 0.0},
    },
)
```

- [ ] **Step 3: Run the focused evaluator tests and verify RED**

Run:

```bash
python3 -m unittest tests.test_humanizer_eval_runner -v
```

Expected failures include unsupported target skill, unknown parser option, missing prompt mode line, and absent `by_plain_language_mode`.

- [ ] **Step 4: Implement constants and mode validation**

Add or update the constants:

```python
TARGET_SKILL_DISPLAY_NAMES = {
    "editorial-humanizer": "Editorial Humanizer",
    "faithful-humanizer": "Faithful Humanizer",
    "plain-language-humanizer": "Plain Language Humanizer",
}
FAITHFUL_TARGET_SKILL = "faithful-humanizer"
VALID_FAITHFUL_MODES = ("structural", "conservative")
PLAIN_LANGUAGE_TARGET_SKILL = "plain-language-humanizer"
VALID_PLAIN_LANGUAGE_MODES = ("rewrite", "explain")
```

In `validate_eval_case`, validate `plain_language_mode` independently from `faithful_mode`:

```python
plain_language_mode = case.get("plain_language_mode")
if target_skill == PLAIN_LANGUAGE_TARGET_SKILL:
    if plain_language_mode not in VALID_PLAIN_LANGUAGE_MODES:
        raise ValueError(
            f"{case['id']}: plain_language_mode must be one of "
            f"{', '.join(VALID_PLAIN_LANGUAGE_MODES)}"
        )
elif plain_language_mode is not None:
    raise ValueError(
        f"{case['id']}: plain_language_mode is only valid for "
        f"{PLAIN_LANGUAGE_TARGET_SKILL}"
    )
```

Add:

```python
def plain_language_mode_for_case(case):
    if target_skill_for_case(case) != PLAIN_LANGUAGE_TARGET_SKILL:
        return None
    return case.get("plain_language_mode")
```

Extend contract-mode validation by checking both field names while keeping the existing Faithful error wording:

```python
for mode_field in ("faithful_mode", "plain_language_mode"):
    contract_mode = contract_case.get(mode_field)
    if case.get(mode_field) != contract_mode:
        mismatches_by_field[mode_field].append(
            f"{case['id']} -> {output_contract_case_id}"
        )
```

Raise `output contract faithful_mode mismatch: ...` or `output contract plain_language_mode mismatch: ...` for the relevant non-empty list.

- [ ] **Step 5: Implement prompts, selection, summaries, and visibility**

Apply these exact behaviors:

```python
plain_language_mode = plain_language_mode_for_case(case)
if plain_language_mode:
    prompt_lines.append(f"Plain Language mode: {plain_language_mode}.")
```

Add `plain_language_mode` to each run summary beside `faithful_mode`. Extend `select_cases` with `plain_language_modes=None` and filter through `plain_language_mode_for_case`. Add parser configuration:

```python
parser.add_argument(
    "--plain-language-mode",
    action="append",
    choices=VALID_PLAIN_LANGUAGE_MODES,
    default=[],
)
```

Pass `args.plain_language_mode` into `select_cases`. Add `plain_language_mode_summaries` to `aggregate_summaries` and return `by_plain_language_mode` using `summarize_pass_rate`, parallel to the Faithful aggregate. Include the mode in dry-run labels and rubric prompts.

Update `verify_eval_plugin_is_model_visible` so its probe names all three skills and its path loop continues to derive expected paths from `TARGET_SKILL_DISPLAY_NAMES`.

In `load_rubric_calibrations`, when `target_skill` is Plain Language, require a valid `plain_language_mode` even though the Plain Language rubric has no dynamic mode dimension. Reject `plain_language_mode` on other calibration targets.

- [ ] **Step 6: Run evaluator tests and dry-run compatibility checks**

Run:

```bash
python3 -m unittest tests.test_humanizer_eval_runner -v
make eval-humanizer-dry-run
```

Expected: evaluator tests pass; the existing 38 cases still dry-run with unchanged Editorial and Faithful labels.

- [ ] **Step 7: Commit evaluator plumbing**

```bash
git add scripts/run_humanizer_evals.py tests/test_humanizer_eval_runner.py
git commit -m "feat: support plain language eval modes"
```

---

### Task 5: Add cross-domain contracts, eval cases, rubric, and calibration

**Files:**

- Modify: `tests/fixtures/humanizer_contract_cases.json`
- Modify: `tests/test_contract_fixture_quality.py`
- Modify: `evals/humanizer_eval_cases.json`
- Modify: `tests/test_humanizer_eval_runner.py`

**Interfaces:**

- Consumes: `plain_language_mode`, existing deterministic constraints, and `maximum_word_count` from Task 2.
- Produces: contract IDs referenced one-to-one by eval cases and a `plain_language_humanizer` rubric.
- Invariant: eval source text must normalize exactly to its referenced contract source.

- [ ] **Step 1: Add failing fixture coverage assertions**

Extend `REQUIRED_TAGS` with:

```python
"plain_language_rewrite",
"plain_language_explain",
"plain_language_combined",
"plain_language_jargon",
"plain_language_protected_literals",
"plain_language_high_stakes",
"plain_language_already_clear",
"plain_language_anti_bloat",
```

Add this test:

```python
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
```

Extend the allowed top-level `mode` values only if a new value is necessary. Use existing `mode="rewrite"` for Rewrite and combined cases and `mode="answer"` for Explain cases. Every Plain Language fixture also carries `plain_language_mode`.

- [ ] **Step 2: Add ten deterministic contract fixtures**

Append cases with the exact IDs and sources below. Each case must contain `no_chatbot_wrapper`, `no_markdown_fence`, `no_new_numbers`, and `no_new_named_entities` unless the combined explanation intentionally requires rewrite-scoped handling. Use the listed required constraints and set a fixed ceiling no more than the listed word count.

```text
plain_language_api_rewrite — rewrite — maximum 38 words
Source: The API enforces a per-client rate limit of 120 requests per minute and
returns HTTP 429 for requests above the threshold.
Require: API; each client; 120 requests per minute; HTTP 429; requests above the threshold.
Reject: "rate limit" unless immediately defined; any claim that requests are slowed.

plain_language_webhook_explain — explain — maximum 65 words
Source: When an invoice is paid, Ledger emits an `invoice.paid` webhook to the
configured HTTPS endpoint. Delivery is retried with exponential backoff for up to
24 hours.
Require exact: `invoice.paid`; HTTPS; 24 hours.
Require: invoice is paid; sends/notification; retries; waits longer between attempts.
Reject: guaranteed delivery; a claimed retry count.

plain_language_combined_output — rewrite — maximum 75 words
Source: The cache uses a time to live of 15 minutes. After that period, the entry
is stale and the next read must retrieve a fresh value from the origin service.
Require: 15 minutes; stale; next read; fresh value; origin service; `Explanation:`.
Require ordered: rewrite content before `Explanation:`.

plain_language_protected_procedure — rewrite — maximum 70 words
Source: Run `atlas migrate --dry-run` before `atlas migrate --apply`. Do not use
`--apply` if validation reports an incompatible schema. If the second command
fails, restore `/srv/atlas/schema.json`.
Require exact and ordered: both commands, `--apply`, incompatible schema,
`/srv/atlas/schema.json`.

plain_language_security_uncertainty — rewrite — maximum 55 words
Source: At 14:20 UTC, telemetry indicated possible credential replay against two
accounts. The evidence may be consistent with token theft, but it does not establish
how the credentials were obtained.
Require: 14:20 UTC; possible; two accounts; may; token theft; does not establish.

plain_language_scientific_boundary — rewrite — maximum 65 words
Source: Smith et al. (2024) reported a hazard ratio of 0.78 (95% CI 0.61–0.99).
This association does not establish causality.
Require exact: Smith et al. (2024); 0.78; 95% CI 0.61–0.99.
Require: hazard ratio; association; does not establish causality.

plain_language_medical_condition — rewrite — maximum 55 words
Source: Take 5 mg once daily. If systolic blood pressure falls below 90 mmHg, do
not take the next dose and contact the prescribing clinician.
Require exact and ordered: 5 mg; once daily; systolic blood pressure; below 90 mmHg;
do not take the next dose; contact the prescribing clinician.

plain_language_legal_obligation — rewrite — maximum 60 words
Source: The controller must notify the processor within 24 hours unless disclosure
is prohibited by applicable law. The exception does not remove the duty to retain
the incident record.
Require: controller; must notify; processor; within 24 hours; unless; prohibited by
applicable law; does not remove; retain the incident record.

plain_language_financial_assumptions — rewrite — maximum 60 words
Source: The forecast assumes 4% annual revenue growth and excludes foreign-exchange
effects. Actual results may differ if either assumption changes.
Require: forecast; assumes; 4% annual revenue growth; excludes foreign-exchange
effects; may differ; either assumption changes.

plain_language_already_clear — rewrite — maximum 12 words
Source: Run `make test` before deployment. Stop if any test fails.
Require exact source equality.
```

For every case, add `passing_output` and at least two `failing_outputs`: one semantic or literal failure and one bloat or wrong-shape failure. Set `expected_error` to the deterministic error fragment produced by the violated constraint.

- [ ] **Step 3: Run fixture tests and verify GREEN for the contract layer**

Run:

```bash
python3 -m unittest tests.test_contract_fixture_quality tests.test_output_contracts -v
```

Expected: all fixture schema, mutation, and contract checks pass.

- [ ] **Step 4: Add failing eval-matrix assertions**

Extend `test_eval_cases_cover_trigger_modes_and_output_contracts` to require these eval IDs:

```python
{
    "plain_language_explicit_api_rewrite",
    "plain_language_explicit_webhook_explain",
    "plain_language_explicit_combined",
    "plain_language_protected_procedure",
    "plain_language_security_rewrite",
    "plain_language_scientific_rewrite",
    "plain_language_medical_rewrite",
    "plain_language_legal_rewrite",
    "plain_language_financial_rewrite",
    "plain_language_already_clear_rewrite",
    "plain_language_implicit_rewrite_activation",
    "plain_language_implicit_explain_activation",
    "plain_language_negative_troubleshooting",
    "plain_language_negative_generic_humanize",
}
```

Add `test_eval_cases_cover_plain_language_modes_and_boundaries` asserting that all positive cases target `plain-language-humanizer`, carry `plain_language_mode`, reference the expected contract ID, and use rubric `plain_language_humanizer`. Negative cases must set `should_trigger` to false and omit output contracts.

- [ ] **Step 5: Add the Plain Language rubric**

Add this rubric to `evals/humanizer_eval_cases.json`:

```json
"plain_language_humanizer": {
  "minimum_total_score": 42,
  "minimum_dimension_score": 8,
  "minimum_dimension_scores": {
    "technical_fidelity": 9,
    "protected_literals_and_operational_safety": 9
  },
  "dimensions": [
    {
      "name": "technical_fidelity",
      "question": "Does the output preserve every claim, actor, attribution, qualifier, condition, exception, warning, dependency, quantity, chronology, causal boundary, and conclusion without adding source-specific behavior?"
    },
    {
      "name": "protected_literals_and_operational_safety",
      "question": "Does the output preserve exact commands, flags, identifiers, configuration keys, API names, schema fields, error messages, URLs, paths, versions, citations, formulas, units, warnings, prerequisites, and operational order?"
    },
    {
      "name": "plain_language_clarity_and_audience_fit",
      "question": "Would an informed non-specialist understand the content without a patronizing tone or loss of domain seriousness?"
    },
    {
      "name": "jargon_and_definition_quality",
      "question": "Does the output replace unnecessary jargon precisely, retain necessary technical terms, and define each necessary term once at the level supported by the source or its unambiguous conventional meaning?"
    },
    {
      "name": "concision_and_mode_compliance",
      "question": "Does every added sentence define a term, clarify a relationship, or explain a required action or supported consequence, and does the output match Rewrite, Explain, or the explicitly combined shape?"
    }
  ]
}
```

- [ ] **Step 6: Add eval cases and calibrations**

Create one forced-skill-read eval for each of the ten contract fixtures, mapping source and mode exactly. Add two unforced activation probes:

```text
plain_language_implicit_rewrite_activation
Prompt: Make this technical passage understandable to a nontechnical project manager.
Mode: rewrite
Contract: plain_language_api_rewrite

plain_language_implicit_explain_activation
Prompt: What does this technical passage mean for an informed non-specialist?
Mode: explain
Contract: plain_language_webhook_explain
```

Add negative activation probes:

```text
plain_language_negative_troubleshooting
Prompt: Debug why this webhook endpoint returns HTTP 500 and give me the code fix.
Source: The endpoint returns HTTP 500 after `invoice.paid` events.
Target: plain-language-humanizer
Mode metadata: explain
Expected activation: false; forbid the Plain Language skill trace; omit output contract and rubric.

plain_language_negative_generic_humanize
Prompt: Humanize this prose and make the voice more distinctive.
Source: This release introduces a comprehensive enhancement to the validation pipeline.
Target: plain-language-humanizer
Mode metadata: rewrite
Expected activation: false; forbid the Plain Language skill trace; omit output contract and rubric.
```

Add calibrations with these outcomes:

```text
PASS: concise API rewrite preserving 120 and HTTP 429.
PASS: concise webhook explanation preserving retry duration and exponential backoff meaning.
FAIL: unchanged jargon-heavy source.
FAIL: API rewrite claiming excess requests are slowed.
FAIL: procedure with `--apply` before `--dry-run`.
FAIL: scientific rewrite changing association to causation.
FAIL: correct facts buried in an unrequested tutorial exceeding the case ceiling.
FAIL: Explain request returned as replacement copy with no explanation.
```

Each calibration must include `target_skill: "plain-language-humanizer"`, the correct `plain_language_mode`, `rubric_id: "plain_language_humanizer"`, and `expected_pass`.

- [ ] **Step 7: Run eval tests, calibration dry-run, and target filters**

Run:

```bash
python3 -m unittest tests.test_humanizer_eval_runner -v
make eval-humanizer-dry-run
make eval-humanizer-dry-run EVAL_ARGS='--target-skill plain-language-humanizer --plain-language-mode rewrite'
make eval-humanizer-dry-run EVAL_ARGS='--target-skill plain-language-humanizer --plain-language-mode explain'
make eval-humanizer-dry-run EVAL_ARGS='--calibrate-rubric'
```

Expected: the complete matrix validates; both mode filters select non-empty case sets; all rubric calibrations validate without invoking a model.

- [ ] **Step 8: Commit fixtures and rubric**

```bash
git add \
  tests/fixtures/humanizer_contract_cases.json \
  tests/test_contract_fixture_quality.py \
  tests/test_humanizer_eval_runner.py \
  evals/humanizer_eval_cases.json
git commit -m "test: add plain language eval matrix"
```

---

### Task 6: Publish package metadata, documentation, installation, and CI

**Files:**

- Modify: `.codex-plugin/plugin.json`
- Modify: `README.md`
- Modify: `docs/skill-examples.md`
- Modify: `NOTICE`
- Modify: `.github/workflows/test.yml`
- Modify: `.github/workflows/live-eval.yml`
- Modify: `tests/test_skill_artifacts.py`

**Interfaces:**

- Consumes: final skill name, modes, package version, eval flags, and installation paths.
- Produces: three-skill/five-behavior public documentation and reproducible client activation.
- Preserves: existing marketplace ID and all Editorial/Faithful invocations.

- [ ] **Step 1: Write failing metadata and documentation assertions**

Update `tests/test_skill_artifacts.py` so package-version assertions become:

```python
def test_manifest_and_skill_versions_are_explicit(self):
    self.assertEqual(self.manifest["version"], "3.1.0")
    self.assertEqual(frontmatter_scalar(self.frontmatter, "version"), "3.0.0")
    faithful_frontmatter = extract_frontmatter(read_text(FAITHFUL_SKILL_PATH))
    plain_language_frontmatter = extract_frontmatter(
        read_text(PLAIN_LANGUAGE_SKILL_PATH)
    )
    self.assertEqual(frontmatter_scalar(faithful_frontmatter, "version"), "1.0.0")
    self.assertEqual(frontmatter_scalar(plain_language_frontmatter, "version"), "1.0.0")
```

Import `PLAIN_LANGUAGE_SKILL_PATH`. Update required-file assertions. Update prompt tests to require all three skill invocations while preserving the three-prompt limit:

```python
self.assertEqual(len(prompts), 3)
self.assertTrue(any("$editorial-humanizer" in prompt for prompt in prompts))
self.assertTrue(any("$faithful-humanizer" in prompt for prompt in prompts))
self.assertTrue(any("$plain-language-humanizer" in prompt for prompt in prompts))
```

Add README assertions for `three prose-editing skills`, `five user-facing behaviors`, both Plain Language modes, the informed non-specialist default, the four-result comparison, the third manual-install path, and both mode-filter commands. Extend client activation assertions for Codex, Claude Code, and OpenCode.

Extend CI assertions for `--target-skill plain-language-humanizer`, `--plain-language-mode rewrite`, and `--plain-language-mode explain`. Extend live workflow assertions for the third target option.

- [ ] **Step 2: Run artifact tests and verify RED**

Run:

```bash
python3 -m unittest tests.test_skill_artifacts -v
```

Expected: failures report manifest version `3.0.0`, absent Plain Language prompt/path, old skill and behavior counts, and missing CI flags.

- [ ] **Step 3: Update plugin metadata**

Set `.codex-plugin/plugin.json` values to:

```json
{
  "name": "humanizer-plugin",
  "version": "3.1.0",
  "description": "Codex plugin with Editorial, Faithful, and Plain Language Humanizers.",
  "keywords": [
    "writing",
    "editing",
    "style",
    "humanizer",
    "codex",
    "editorial-editing",
    "semantic-preservation",
    "plain-language",
    "technical-accessibility"
  ]
}
```

Preserve the existing author, URLs, license, `skills`, category, capabilities, screenshots, and brand color. Set interface copy to:

```text
shortDescription: Editorial, faithful, and plain-language technical editing.
longDescription: Three clearly separated Codex writing editors: Editorial Humanizer applies broader anti-slop judgment, Faithful Humanizer changes presentation while preserving every substantive element, and Plain Language Humanizer adapts supplied technical content for an informed non-specialist through Rewrite and Explain modes.
```

Use these exact default prompts:

```json
[
  "Use $editorial-humanizer to improve this draft with broader editorial judgment:",
  "Use $faithful-humanizer to improve the wording without changing the substance:",
  "Use $plain-language-humanizer to rewrite this technical content for an informed non-specialist:"
]
```

- [ ] **Step 4: Update README and examples without expanding the 12-case comparison library**

Update the README opening table to list five behaviors: Editorial, Faithful Structural, Faithful Conservative, Plain Language Rewrite, and Plain Language Explain. Add decision rules that distinguish editorial authority from audience adaptation. Add one same-source comparison containing Editorial, Faithful Structural, Faithful Conservative, and Plain Language Rewrite; link Explain examples rather than treating Explain as replacement copy.

Add these invocation blocks:

```text
Use $plain-language-humanizer in Rewrite mode. Adapt this technical content for an informed non-specialist. Return only the rewrite:
[paste source]
```

```text
Use $plain-language-humanizer in Explain mode. Explain this supplied technical content concisely for an informed non-specialist:
[paste source]
```

```text
Use $plain-language-humanizer to rewrite this and then explain it briefly. Put the rewrite first, followed by Explanation:
[paste source]
```

Update plain-install commands to create and copy `~/.agents/skills/plain-language-humanizer`, `~/.claude/skills/plain-language-humanizer`, and `~/.config/opencode/skills/plain-language-humanizer` beside the existing skills. Update repository layout, testing commands, design limits, and MIT license scope.

In `docs/skill-examples.md`, change `17 genres and editing cases` to `12 contexts`. Add Plain Language sections using the approved API, webhook, procedure, scientific, and already-clear examples. Add `$plain-language-humanizer`, `/plain-language-humanizer`, and OpenCode skill-tool activation examples.

Do not add Plain Language outputs to all 12 entries in `docs/humanizer-comparison-examples.md`.

- [ ] **Step 5: Update NOTICE and CI workflows**

Change the MIT-original-work entry in `NOTICE` to name both Faithful Humanizer and Plain Language Humanizer.

Add this deterministic test step to `.github/workflows/test.yml`:

```yaml
- name: Check Plain Language eval mode flags
  run: >-
    make eval-humanizer-dry-run
    EVAL_ARGS='--target-skill plain-language-humanizer
    --plain-language-mode rewrite --plain-language-mode explain'
```

Add `plain-language-humanizer` to the manual `target_skill` choices in `.github/workflows/live-eval.yml`. Do not add an automatic live-model job.

- [ ] **Step 6: Run documentation and metadata tests**

Run:

```bash
python3 -m unittest tests.test_skill_artifacts tests.test_plain_language_humanizer_artifacts -v
make eval-humanizer-dry-run EVAL_ARGS='--target-skill plain-language-humanizer --plain-language-mode rewrite --plain-language-mode explain'
git diff --check
```

Expected: all artifact tests pass, the combined mode-filter dry-run selects both modes, and no whitespace errors are reported.

- [ ] **Step 7: Commit package documentation and CI**

```bash
git add \
  .codex-plugin/plugin.json \
  README.md \
  docs/skill-examples.md \
  NOTICE \
  .github/workflows/test.yml \
  .github/workflows/live-eval.yml \
  tests/test_skill_artifacts.py
git commit -m "docs: publish plain language humanizer"
```

---

### Task 7: Forward-test and refine the skill against observed failures

**Files:**

- Modify only when evidence requires: `skills/plain-language-humanizer/SKILL.md`
- Modify only when an uncovered stable behavior requires: `tests/fixtures/humanizer_contract_cases.json`
- Modify only when an uncovered stable behavior requires: `evals/humanizer_eval_cases.json`
- Runtime artifacts only: `evals/artifacts/plain-language-forward/`

**Interfaces:**

- Consumes: Task 1 controls, the implemented skill, contract fixtures, and rubric.
- Produces: fresh-context evidence that Rewrite and Explain generalize without jargon retention, semantic drift, literal changes, or bloat.

- [ ] **Step 1: Re-run the six Task 1 controls with the skill**

Dispatch fresh read-only agents with `fork_turns="none"` and explicit skill invocation. Do not provide expected outputs or Task 1 diagnoses. Prohibit recursive fan-out. Capture raw outputs and validate each one with the closest deterministic contract.

Expected:

```text
Control A: precise Rewrite, 120 and HTTP 429 preserved, no invented throttling behavior.
Control B: concise Explain output, webhook and exponential-backoff meaning retained, no delivery guarantee.
Control C: both commands, warning, failure condition, restore path, and order exact.
Control D: statistics and non-causal boundary exact, necessary terms defined once.
Control E: dose, threshold, prohibition, and escalation exact.
Control F: source unchanged.
```

- [ ] **Step 2: Run five variation scenarios**

Use fresh contexts for:

```text
1. Legal obligation with nested exception and record-retention duty.
2. Financial forecast with assumption, exclusion, and uncertainty.
3. Security incident with unresolved attribution and timestamps.
4. Combined Rewrite and Explain output requiring exactly one Explanation: label.
5. Ambiguous overloaded term where the correct response preserves the term and asks one precise question.
```

Expected: outputs follow the mode contract and no agent turns the request into research, troubleshooting, advice, or a tutorial.

- [ ] **Step 3: Refine only against material evidence**

For each failure, classify it before editing:

```text
wrong output shape -> strengthen the positive mode recipe
omitted required element -> add it to the ledger or final-check structure
condition-dependent failure -> add a rule keyed to the observable condition
hard preservation violation -> add an explicit prohibition and regression fixture
```

Do not add a banned-word catalog, universal word-count ratio, extra mode, reference file, or broad domain taxonomy. Add the smallest instruction that addresses the exact failure and rerun the failing scenario in a fresh context.

- [ ] **Step 4: Run deterministic regression tests after each refinement**

Run:

```bash
python3 -m unittest \
  tests.test_plain_language_humanizer_artifacts \
  tests.test_output_contracts \
  tests.test_contract_fixture_quality \
  tests.test_humanizer_eval_runner -v
```

Expected: all targeted tests pass after every skill edit.

- [ ] **Step 5: Commit evidence-driven refinements if files changed**

If no tracked file changed, record that no refinement was needed and create no empty commit. Otherwise:

```bash
git add \
  skills/plain-language-humanizer/SKILL.md \
  tests/fixtures/humanizer_contract_cases.json \
  evals/humanizer_eval_cases.json
git commit -m "fix: harden plain language preservation"
```

---

### Task 8: Run full release verification and focused review

**Files:**

- Verify: all files changed by Tasks 2-7
- Optional runtime artifacts: `evals/artifacts/plain-language-release/`

**Interfaces:**

- Consumes: complete implementation and all deterministic/live evaluation entry points.
- Produces: merge-readiness evidence with no required code or documentation changes left unresolved.

- [ ] **Step 1: Run the complete deterministic suite**

```bash
make test
make coverage
make eval-humanizer-dry-run
make eval-humanizer-dry-run EVAL_ARGS='--target-skill plain-language-humanizer --plain-language-mode rewrite'
make eval-humanizer-dry-run EVAL_ARGS='--target-skill plain-language-humanizer --plain-language-mode explain'
make eval-humanizer-dry-run EVAL_ARGS='--calibrate-rubric'
python3 /Users/CoveMB/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/plain-language-humanizer
```

Expected: all tests pass; branch coverage remains at or above the repository's 84% gate; all eval and calibration matrices validate; the skill validator succeeds or only reports a documented incompatibility with repository-standard optional frontmatter.

- [ ] **Step 2: Run repository hygiene checks**

```bash
git diff --check
git status --short
rg -n 'exactly two|two prose-editing skills|three user-facing behaviors|17 genres' \
  README.md docs .codex-plugin tests skills NOTICE
rg -n 'editorial-humanizer|faithful-humanizer|plain-language-humanizer' \
  README.md docs/skill-examples.md .codex-plugin/plugin.json tests/test_skill_artifacts.py
```

Expected: no stale count claims remain outside historical design context; all three skills appear in metadata, installation, activation, tests, and examples.

- [ ] **Step 3: Perform the focused requirements and DRY review**

Confirm each acceptance criterion in the approved design maps to a skill section, deterministic test, eval case, or documentation assertion. Inspect mode handling for duplicated validation that can be removed by one small helper without changing Faithful behavior. Do not generalize the runner into a new framework unless concrete duplication remains after this pass.

Review likely failure points explicitly:

```text
mode collision with generic Humanizer requests
conventional definition presented as source-specific behavior
source-aware entity checks bypassed by Explanation: sections
word-count ceiling applied to only part of combined output
protected commands or warning order changed
high-stakes qualifiers or causal boundaries weakened
manifest, skill, and package versions conflated
live workflow missing the third target
```

- [ ] **Step 4: Request approval before optional live evaluation**

Do not run this step without explicit user confirmation. After confirmation, use isolated home and Codex directories:

```bash
eval_home_dir="$(mktemp -d)"
eval_codex_dir="$(mktemp -d)"
env HOME="$eval_home_dir" CODEX_HOME="$eval_codex_dir" \
  python3 scripts/run_humanizer_evals.py \
  --target-skill plain-language-humanizer \
  --trials 3 \
  --rubric-grade \
  --artifacts-dir evals/artifacts/plain-language-release
```

Expected rubric floors: technical fidelity and protected-literal safety at least 9/10, every other dimension at least 8/10, total at least 42/50. Inspect every failure manually before changing guidance. Eval artifacts remain ignored and are not committed.

- [ ] **Step 5: Run final verification after any live-eval repair**

```bash
make test
make coverage
make eval-humanizer-dry-run
git diff --check
git status --short --branch
```

Expected: all gates pass and the worktree contains only intended implementation changes or is clean after the final commit.

- [ ] **Step 6: Commit final verified repairs if needed**

If Task 8 required tracked repairs, stage only those files and commit:

```bash
git status --short
git add \
  skills/plain-language-humanizer/SKILL.md \
  skills/references/registers/scientific-writing.md \
  tests/helpers/skill_artifacts.py \
  tests/helpers/output_contracts.py \
  tests/test_output_contracts.py \
  tests/test_contract_fixture_quality.py \
  tests/test_plain_language_humanizer_artifacts.py \
  scripts/run_humanizer_evals.py \
  tests/test_humanizer_eval_runner.py \
  tests/fixtures/humanizer_contract_cases.json \
  evals/humanizer_eval_cases.json \
  .codex-plugin/plugin.json \
  README.md \
  docs/skill-examples.md \
  NOTICE \
  .github/workflows/test.yml \
  .github/workflows/live-eval.yml \
  tests/test_skill_artifacts.py
git diff --cached --name-only
git commit -m "fix: complete plain language verification"
```

Confirm every staged path is in the implementation allowlist above; stop if an unrelated path appears. Never use `git add -A` in a dirty worktree. If no repairs were required, create no empty commit.

## Completion handoff

Report:

- commits created by each task;
- deterministic test, coverage, and eval dry-run results;
- whether forward tests required skill refinements;
- whether optional live evaluation was approved and run;
- remaining human-review risks for high-stakes content; and
- confirmation that no pull request was created.

Do not claim completion if any required deterministic gate is failing or if the implementation diverges from the approved specification.
