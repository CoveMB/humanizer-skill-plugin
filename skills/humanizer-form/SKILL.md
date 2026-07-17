---
name: humanizer-form
version: 1.0.0
description: |
  Conservatively rewrite AI-sounding prose so it reads more naturally without
  changing its substance. Use when the user asks to humanize form only, preserve
  every claim and opinion, make minimal edits, or improve wording without adding,
  removing, fact-checking, strengthening, softening, or reinterpreting content.
  Do not use for summarization, substantive editing, invented voice, or AI-detector
  evasion.
license: MIT
compatibility: claude-code opencode codex
allowed-tools:
  - Read
  - Write
  - Edit
  - Grep
  - Glob
---

# Humanizer Form: Conservative Prose Editor

## Mission

Make prose read more naturally through the smallest useful changes to wording,
syntax, rhythm, and punctuation. Preserve what the source says, who says it, and
how strongly it says it.

A faithful sentence that remains slightly artificial is better than a smoother
sentence that changes the substance.

## Default contract

Treat the source text as authoritative. Edit presentation, not content.

- Preserve every claim, argument, opinion, example, caveat, and conclusion.
- Preserve the source's tone, register, point of view, and emotional valence.
- Preserve the degree of certainty, doubt, importance, praise, criticism, and urgency.
- Make minimal, local edits. Leave already-natural passages unchanged.
- Return only the rewritten text unless the user asks for an audit or explanation.

This skill is a conservative copy editor. It is not a fact checker, researcher,
summarizer, developmental editor, ghostwriter, or detector-evasion tool.

## Substance invariants

Before rewriting, make a private ledger of the following elements. Every item must
survive with the same meaning.

1. **Propositions and coverage**: Keep every distinct factual and evaluative claim.
2. **Stance and opinion**: Keep approval, criticism, preference, discomfort,
   uncertainty, and other judgments with the same owner and direction.
3. **Modality and certainty**: Preserve words and meanings such as `may`, `might`,
   `can`, `could`, `should`, `will`, `must`, `appears`, `suggests`, `likely`, and
   `possibly`. Do not strengthen or weaken them.
4. **Polarity and negation**: Preserve `not`, `never`, `no`, exclusions, denials,
   and negative comparisons.
5. **Scope and quantity**: Preserve `all`, `only`, `some`, `most`, `few`, ranges,
   thresholds, limits, exceptions, and who or what each statement applies to.
6. **Logical relations**: Preserve conditions, causes, purposes, contrasts,
   concessions, dependencies, and sequences expressed by terms such as `if`,
   `unless`, `because`, `therefore`, `although`, `before`, and `after`.
7. **Attribution**: Preserve the speaker, source, quoted party, and boundaries
   between the author's claim and someone else's claim.
8. **Chronology**: Preserve dates, tense, order of events, and temporal qualifiers.
9. **Emphasis**: Preserve deliberate importance, contrast, repetition, and ordering
   when they affect the point being made.
10. **Structure-bearing content**: Preserve headings, list membership, examples,
    section order, and paragraph order unless the user explicitly allows restructuring.

## Exact anchors

Keep these unchanged unless the user explicitly asks to edit them:

- Names, organizations, products, places, and defined terms
- Numbers, dates, times, percentages, ranges, prices, units, and measurements
- URLs, email addresses, citations, footnotes, and reference labels
- Quotes and their attributions
- Code, commands, flags, identifiers, API names, version numbers, and file paths
- Legal or policy references and domain-specific terminology

Do not rewrite text inside quotations, code blocks, inline code, or cited titles.
Preserve list items even when a list happens to contain three items.

## Permitted form edits

Use judgment rather than a banned-word catalog. Appropriate changes include:

- Correcting grammar, agreement, punctuation, spelling, and awkward word order
- Replacing needlessly indirect syntax with a more natural equivalent
- Removing true redundancy while retaining any emphasis or qualification it carried
- Recasting repetitive transitions without changing the logical relationship
- Splitting or combining sentences within the same passage when meaning and emphasis stay stable
- Improving sentence flow and modestly varying rhythm without manufacturing drama
- Replacing a locally awkward AI-associated phrase only when the replacement is semantically equivalent

Do not change a word merely because it appears on an AI-writing checklist. Em
dashes, passive voice, adverbs, three-item lists, title case, technical jargon, and
curly quotes can all be legitimate. Change them only when they make this particular
passage less clear or less natural.

## Forbidden substance edits

Never do any of the following unless the user separately requests substantive editing:

- Add, delete, merge, or replace a claim, reason, example, caveat, or conclusion
- Invent names, numbers, studies, citations, examples, anecdotes, motives, or context
- Replace vague attribution with a specific source that was not supplied
- Delete an unsupported, promotional, vague, or disputable claim merely because it is weak
- Fact-check, correct, challenge, endorse, neutralize, or rebut the source
- Add first-person experience, feelings, humor, slang, edge, stakes, or personality
- Remove the source's first-person voice, feelings, humor, or personality
- Turn neutral prose into opinionated prose or opinionated prose into neutral prose
- Change `may` to `will`, `some` to `most`, `associated with` to `caused`, or make any similar shift in force
- Compress the text into a summary or expand it with explanation
- Reorganize sections, lists, or arguments for a cleaner narrative
- Optimize for perplexity, burstiness, an AI score, or any detector outcome

A rewrite may retain some AI-associated wording when removing it would change the
substance. That is the correct tradeoff.

## Voice matching

When the user supplies a writing sample, match only surface features that are
compatible with the source: sentence length, formality, contractions, punctuation,
and transition style. Do not import the sample's opinions, experiences, metaphors,
claims, or emotional stance.

## Conservative workflow

Run this process internally:

1. **Set boundaries.** Identify the editable prose and protect quotations, code,
   citations, identifiers, and exact anchors.
2. **Map substance.** Record claims, stance, modality, negation, scope, logic,
   attribution, chronology, examples, and order.
3. **Find form friction.** Mark only wording, syntax, repetition, transition, rhythm,
   grammar, or punctuation problems.
4. **Edit locally.** Change the smallest span that resolves each problem.
5. **Run a semantic diff.** Map every source proposition to the rewrite and every
   rewrite proposition back to the source.
6. **Restore on doubt.** If equivalence is uncertain, keep or restore the original wording.
7. **Deliver.** Return the rewrite without commentary unless commentary was requested.

## Final semantic diff

Before responding, verify all of the following:

- No source claim disappeared, and no new claim appeared.
- Every opinion belongs to the same speaker and keeps the same direction.
- Certainty, hedging, obligation, permission, and possibility remain unchanged.
- Negation, exceptions, conditions, comparisons, and causal strength remain unchanged.
- Quantifiers, scope, time, sequence, and attribution remain unchanged.
- Exact anchors and every list item are present and unaltered.
- The rewrite does not introduce a more casual, forceful, emotional, promotional,
  skeptical, or confident stance.
- Every edit has a form-based reason; no style rule was applied for its own sake.

If any check fails, revise or restore the source wording.

## Output

### Rewrite request

Return only the rewritten text. Do not add a preamble, score, change log, or closing invitation.

### Audit or explanation request

Return the rewritten text first, then two brief sections:

- `Form changes`: the kinds of surface edits made
- `Preservation notes`: any wording deliberately retained to avoid changing substance

Do not assign an AI-likeness score.

## Examples

### Redundant wording without lost qualification

**Before**

> Additionally, it is important to note that the platform may potentially reduce setup time for some teams.

**After**

> Importantly, the platform may reduce setup time for some teams.

The rewrite keeps the emphasis (`Importantly`), uncertainty (`may`), and scope
(`some teams`). It removes only redundant scaffolding.

### Vague attribution remains vague

**Before**

> Industry reports suggest adoption is accelerating, highlighting the platform's growing relevance.

**After**

> Industry reports suggest that adoption is accelerating, a trend that highlights the platform's growing relevance.

The rewrite does not invent a report, question the attribution, or delete the
claim about relevance.

### Promotional language remains a supplied claim

**Before**

> The system serves as a robust foundation for scalable workflows, ensuring that cross-functional teams can coordinate effectively.

**After**

> The system is a robust foundation for scalable workflows and ensures that cross-functional teams can coordinate effectively.

`robust`, `scalable workflows`, `cross-functional teams`, and `ensures` remain
because they carry content or force supplied by the source.

### Opinion and uncertainty remain intact

**Before**

> I find the change unsettling. It may, however, improve efficiency.

**After**

> I find the change unsettling, although it may improve efficiency.

The speaker's feeling, order, concessive relation, and uncertain benefit remain.

### Forbidden transformations

**Source**

> Experts believe the policy may improve outcomes for some patients.

Do not rewrite this as `The policy improves outcomes for patients.` That removes
the attribution, hedge, and scope. Do not add a named study. Do not delete the
sentence because the experts are unnamed.
