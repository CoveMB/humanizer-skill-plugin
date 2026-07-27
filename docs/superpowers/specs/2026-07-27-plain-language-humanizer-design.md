# Plain Language Humanizer Design

**Status:** Approved design

**Date:** 2026-07-27

## Summary

Add `plain-language-humanizer` as a third Humanizer skill. It adapts supplied
technical content for an informed non-specialist while preserving technical
meaning, operational safety, and source boundaries. It supports two deterministic
modes: Rewrite by default and Explain when explicitly requested.

The skill is distinct from the existing editors:

- Editorial Humanizer may remove, compress, reprioritize, or substantively
  restructure supplied material.
- Faithful Humanizer preserves the source's substance and register without adding
  explanatory content.
- Plain Language Humanizer preserves substantive technical content while adapting
  terminology and explanation for a less technical audience.

## Context

The plugin currently provides Editorial Humanizer and Faithful Humanizer. Faithful
has Structural and Conservative modes, giving the plugin three user-facing
behaviors. Adding Plain Language Rewrite and Explain will bring the total to three
skills and five user-facing behaviors. The repository has deterministic artifact
tests, output-contract fixtures, a live evaluation runner, rubric calibration,
installation documentation, and client-specific activation examples.

At design time:

- `main` matched `origin/main` with no local changes;
- all 185 deterministic tests passed; and
- all 38 existing evaluation cases passed dry-run validation.

The new skill must integrate with those mechanisms without changing the existing
skills' contracts.

## Goals

1. Make technical prose easier for a non-specialist to understand.
2. Preserve every substantive claim, condition, warning, prerequisite, step,
   qualifier, and conclusion.
3. Replace unnecessary jargon while retaining and briefly defining terminology
   required for precision.
4. Protect operational literals and meaningful technical order.
5. Support concise source-bound explanations without turning the skill into a
   research, troubleshooting, or advisory system.
6. Prevent accessibility work from creating unnecessary length.
7. Cover technical content across software, engineering, scientific, medical,
   legal, financial, security, policy, and other technical domains.
8. Preserve backward compatibility for Editorial Humanizer and Faithful Humanizer.

## Non-goals

The skill does not:

- claim WCAG, dyslexia-specific, or reading-grade compliance;
- perform research, fact-checking, troubleshooting, translation, summarization, or
  AI-detector evasion;
- provide professional medical, legal, financial, security, or scientific advice;
- add tutorials, history, background, decorative examples, or repeated explanations;
  or add an example or analogy unless the user explicitly requests it or it is
  materially needed for comprehension;
- delete substantive source content merely to make the output shorter; or
- simplify protected technical literals into approximate substitutes.

## Audience

Use an informed non-specialist as the default audience: a reader comfortable with
ordinary workplace language but without domain expertise. A user-specified audience
always overrides the default. Do not infer that a reader is unintelligent or use a
patronizing tone.

## Skill and package identity

- Skill name and directory: `plain-language-humanizer`
- Display name: Plain Language Humanizer
- Initial skill version: `1.0.0`
- Plugin version after addition: `3.1.0`
- License: MIT
- Compatibility: match the existing skills' supported clients

Keep existing Editorial and Faithful skill versions and behavior unchanged. Update
the existing artifact test that assumes the Editorial skill version must equal the
plugin package version; package and individual skill versions are separate concerns
once the plugin contains three independently versioned skills.

## Public contract

Preserve technical meaning while adapting the explanation for a less technical
audience. Remove unnecessary jargon, retain and briefly explain necessary
terminology, protect technical literals, and add only the explanation required for
comprehension.

The source remains authoritative for source-specific behavior. A definition may
use a term's unambiguous conventional meaning, but it must remain generic and must
not invent source-specific behavior, consequences, or guarantees. Preserve an
ambiguous or overloaded term and ask a precise question rather than guessing.

## Mode routing

An explicitly named mode always wins.

### Rewrite mode

Rewrite is the default when the user:

- names Rewrite mode;
- asks to rewrite, simplify, reduce jargon, use plain language, make content
  accessible, or adapt it for a nontechnical reader; or
- invokes `$plain-language-humanizer` without choosing a mode.

Return replacement text in plain language. Define necessary terminology inline at
its first meaningful use. Return only the rewrite unless the user requests another
output shape.

### Explain mode

Explain is selected when the user names Explain mode or asks what supplied
technical content means, requests a walkthrough, or asks for an explanation for a
less technical reader.

Return a concise, source-grounded explanation rather than replacement copy. The
explanation may regroup ideas for comprehension but may not omit material details,
invent facts, or imply source-specific behavior that the source does not establish.

### Combined request

When the user explicitly requests both operations, return:

1. the plain-language rewrite; then
2. a short section labeled exactly `Explanation:`.

This is a compound request, not a third mode.

## Trigger boundaries

Activate for explicit `$plain-language-humanizer` invocations and for clear
plain-language audience-adaptation requests. Do not capture generic requests to
"humanize" text.

Use:

- Plain Language Humanizer for audience adaptation and limited explanatory
  additions;
- Faithful Humanizer when no explanatory addition is permitted and the technical
  register should remain; and
- Editorial Humanizer when the user authorizes substantive selection, compression,
  reprioritization, or restructuring.

Do not activate Plain Language Humanizer for standalone research, debugging,
troubleshooting, fact-checking, translation, summarization, or detector-evasion
requests.

## Technical-content ledger

Before transforming the source, record privately:

- every factual and evaluative claim;
- actor, ownership, attribution, and agency;
- quantities, dates, units, thresholds, ranges, and comparisons;
- modality, uncertainty, obligation, permission, and prohibition;
- scope, negation, exceptions, conditions, dependencies, and prerequisites;
- chronology, causal strength, and meaningful sequence;
- warnings, failure states, escalation conditions, and safety boundaries;
- procedure steps and operational order; and
- protected literals.

Protected literals include code, commands, flags, identifiers, configuration keys,
API names, schema fields, error messages, URLs, paths, versions, citations, formulas,
units, and other strings whose exact form is technically meaningful.

## Language classification

Classify technical language before editing:

1. **Protected literal:** preserve exactly and explain nearby when necessary.
2. **Necessary technical term:** retain and define briefly at first meaningful use.
3. **Unnecessary jargon:** replace with a precise everyday equivalent.
4. **Already-familiar language:** retain without explanation.
5. **Ambiguous or context-dependent term:** preserve and ask rather than invent a
   definition.

Expand an acronym at first meaningful use unless the audience clearly knows it or
the acronym is a protected literal whose expanded form is not established.

## Rewrite behavior

Rewrite mode may:

- shorten overloaded sentences;
- expose the responsible actor and action;
- replace nominalizations with direct verbs;
- move qualifications closer to the claims they govern;
- split or merge sentences when meaning and emphasis remain stable;
- change non-meaningful paragraph boundaries; and
- use lists for genuine steps, choices, requirements, or grouped information.

It must preserve operational order, meaningful grouping, emphasis, and every ledger
item. It must not change a term merely because it sounds technical.

## Explain behavior

Explain mode may group the source into concepts such as what something is, what it
does in the supplied context, and what action the source requires. Include why
something matters only when the source establishes that consequence.

Use headings or bullets only when they materially reduce reading effort. Examples
and analogies may appear when the user explicitly requests one or when one is
materially needed to explain a technical concept. If ordinary wording or a
conventional definition is sufficient, do not add one. Label every device as
explanatory rather than a source fact, retain the technical term and protected
literals, state the device's limits, and do not imply exact equivalence or add
source-specific behavior, guarantees, numbers, consequences, or advice. Apply extra
caution to high-stakes content.

## Anti-bloat contract

Every added sentence must do at least one of the following:

- define a necessary term;
- clarify a relationship between source elements; or
- explain a required action or source-supported consequence.

Define each term once unless its meaning changes. Do not add throat-clearing,
repeated summaries, tutorials, history, decorative examples, or redundant
"in other words" restatements. Preserve already-clear passages. Prefer the shortest
output that remains complete and accurate.

There is no universal percentage-based expansion limit. Deterministic evaluation
fixtures will set case-specific maximum word counts where a stable ceiling is
appropriate.

## High-stakes content

For scientific, medical, legal, financial, security, policy, and other high-stakes
material:

- retain required domain terminology and define it rather than replacing it with
  an imprecise approximation;
- preserve uncertainty, evidence boundaries, attribution, statistical meaning,
  causal strength, warnings, prerequisites, exceptions, and escalation conditions;
- preserve exact procedural and operational literals; and
- do not make the prose conversational when that would weaken seriousness or
  precision.

Ordinary rewrite output remains rewrite-only. If a request moves from editing into
professional advice or operational reliance, state the boundary and recommend
appropriate human review instead of answering beyond the skill's scope.

For scientific or academic content, the skill may read the existing shared
`skills/references/registers/scientific-writing.md` reference after that reference
is updated with Plain Language-specific preservation guidance.

## Missing or conflicting information

- If no source or technical term is supplied, ask for the content to transform.
- If the audience is unspecified, use the informed non-specialist default.
- If a definition depends on unavailable context, preserve the term and ask a
  precise question.
- If simplifying a protected literal would improve readability, keep the literal
  unchanged and explain it nearby.
- If the requested shortening would delete substantive content, explain the
  conflict and request permission to summarize or use Editorial Humanizer.
- If the request requires research, troubleshooting, or professional advice, state
  the boundary and route the task separately.

## Final validation

Before returning output, compare source and output in both directions:

- Every substantive source element appears with the same force and relationships.
- Every output claim is supported by the source, is a conventional definition, or
  is an explanatory device that the user explicitly requested or that is materially
  needed for comprehension. Every device remains labeled, limited, and unable to
  assert source-specific facts or exact equivalence.
- All protected literals remain exact.
- Procedural order, warnings, conditions, and exceptions remain intact.
- Necessary terminology is defined once and unnecessary jargon is removed.
- Already-clear text is not rewritten without a comprehension benefit.
- The output follows the selected mode and contains no unrequested wrapper.
- Every added sentence satisfies the anti-bloat contract.

## Repository integration

### Skill artifact

Create `skills/plain-language-humanizer/SKILL.md` as a self-contained skill that
follows the existing plugin's frontmatter and structural conventions. Keep it below
500 lines. Do not create scripts, assets, or domain-specific references unless
baseline or forward evaluation demonstrates a concrete need.

### Plugin metadata

Update `.codex-plugin/plugin.json` to:

- set the package version to `3.1.0`;
- describe all three skills;
- add plain-language and technical-accessibility keywords; and
- use Editorial rewrite, Faithful rewrite, and Plain Language rewrite as the three
  default prompts.

The Editorial audit remains supported and documented but is removed from the
three-entry default prompt list.

### Documentation

Update:

- `README.md` selection rules, behavior count, comparison, skill section, routing,
  installation commands, repository layout, testing guidance, design limits, and
  license language;
- `docs/skill-examples.md` with Rewrite, Explain, combined, high-stakes, and
  client-specific activation examples;
- `skills/references/registers/scientific-writing.md` with Plain Language
  preservation rules; and
- `NOTICE` to identify Plain Language Humanizer as MIT-licensed original work.

Correct the existing statement in `docs/skill-examples.md` that says the comparison
library spans 17 genres. The comparison document and deterministic tests establish
that it contains 12 contexts.

Keep `docs/humanizer-comparison-examples.md` focused on Editorial and the two
Faithful intervention strategies. Add one concise four-result comparison to the
README and targeted Plain Language examples to `docs/skill-examples.md` rather than
adding a fourth output to all 12 existing cases.

### Evaluation runner

Extend `scripts/run_humanizer_evals.py` with:

- `plain-language-humanizer` as a supported target;
- a `plain_language_mode` field with `rewrite` and `explain` values;
- target and mode filtering;
- model-visible plugin checks for the third skill;
- mode information in prompts and summaries; and
- per-Plain-Language-mode aggregate results.

Preserve existing `faithful_mode` input, filtering, prompt, and summary behavior.
Avoid a broad runner refactor unless the new mode support creates concrete
duplication that a small shared helper removes safely.

### Deterministic output contracts

Add `maximum_word_count` to the supported output-contract constraints. Validate
that it is a positive integer, apply it to the full normalized output, and set each
case's ceiling for its requested output shape. Add mutation tests proving the guard
rejects bloated output without rejecting valid concise output.

Use existing constraints for exact literals, ordered fragments, required content,
forbidden jargon, source-aware numbers and entities, rewrite-only output, and
source equality or difference.

## Test strategy

### Skill-authoring baseline

Before writing the skill, run fresh-context application scenarios without it.
Capture failures such as:

- retained unnecessary jargon;
- inaccurate everyday substitutions;
- dropped qualifiers or causal boundaries;
- invented explanations or consequences;
- excessive background and repeated summaries;
- altered commands, identifiers, warnings, or procedure order;
- failure to leave already-clear prose alone; and
- incorrect Rewrite or Explain output shape.

Only add guidance that addresses an observed failure or a requirement approved in
this specification. If a no-guidance control already succeeds consistently, retain
the behavior as a regression case rather than adding speculative instruction.

### Deterministic test-first sequence

1. Add artifact tests that fail because the new skill and metadata are absent.
2. Add output-contract tests that fail because `maximum_word_count` is unsupported.
3. Add eval-runner tests that fail because the third target and its modes are
   unsupported.
4. Implement the smallest changes that make each test group pass.
5. Run the full existing suite after each independently reviewable group.

### Representative fixtures

Include cases for:

- software, API, and architecture prose with unnecessary jargon;
- an operations procedure with exact commands, prerequisites, warnings, and order;
- a security explanation with uncertainty and unresolved status;
- scientific material with terminology, attribution, and causal boundaries;
- medical content with timing and escalation conditions;
- legal content with obligations, exceptions, and scope;
- financial content with assumptions, exclusions, and uncertainty;
- already-clear technical prose that must remain unchanged;
- Explain mode;
- a combined Rewrite and Explain request;
- missing context; and
- positive and negative activation boundaries.

### Live rubric

Add a Plain Language rubric with five dimensions:

1. technical fidelity;
2. protected-literal and operational safety;
3. plain-language clarity and audience fit;
4. jargon handling and necessary definition quality; and
5. concision and mode compliance.

Require at least 9/10 for technical fidelity and protected-literal safety, at least
8/10 for every other dimension, and at least 42/50 overall.

Calibrate the rubric with accepted outputs and deliberate failures: an unchanged
jargon-heavy source, an imprecise simplification, an invented explanation, a
bloated tutorial, an altered command or warning, reordered steps, and the wrong
mode shape.

### Activation coverage

Add explicit and contextual Rewrite and Explain cases. Add negative cases for
generic Humanizer requests, research, troubleshooting, fact-checking, translation,
summarization, and detector evasion. Preserve all existing Editorial and Faithful
activation cases.

## Verification and release gates

The implementation is complete only when:

1. the skill folder passes the skill validator;
2. `make test` passes with no regressions;
3. `make coverage` passes the repository's branch-coverage gate;
4. `make eval-humanizer-dry-run` validates the complete matrix;
5. target and mode dry-runs work for both Plain Language modes;
6. plugin provenance confirms that all three skills are model-visible;
7. documentation, manifest, installation commands, examples, and tests agree on
   names, versions, skill counts, and behavior counts;
8. `git diff --check` reports no whitespace errors; and
9. a focused requirements, DRY, security, privacy, and documentation-drift review
   finds no material omissions.

An isolated multi-trial live evaluation requires separate user approval because it
invokes external models. A pull request is outside scope unless explicitly
requested.

## Acceptance criteria

- The plugin exposes Editorial Humanizer, Faithful Humanizer, and Plain Language
  Humanizer as three skills and five user-facing behaviors without changing
  existing user-facing contracts.
- Plain Language Rewrite is the deterministic default.
- Plain Language Explain is selected only by explicit Explain intent.
- The default audience is an informed non-specialist unless the user supplies one.
- All substantive technical content and protected literals survive with the same
  meaning and operational order.
- Necessary terminology is retained and briefly defined; unnecessary jargon is
  replaced precisely.
- Added explanation is source-grounded or limited to conventional definitions and
  does not invent source-specific behavior.
- Outputs satisfy the anti-bloat contract and case-specific word-count ceilings.
- High-stakes content preserves terminology, evidence boundaries, warnings,
  conditions, exceptions, uncertainty, and causal strength.
- Existing Editorial and Faithful deterministic tests and eval cases continue to
  pass unchanged except where metadata assertions must acknowledge the third skill.
