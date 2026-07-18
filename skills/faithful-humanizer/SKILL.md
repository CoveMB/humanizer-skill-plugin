---
name: faithful-humanizer
version: 1.0.0
description: |
  Rewrite AI-sounding prose so it reads more naturally without changing its
  substance. Use whenever the user explicitly invokes `$faithful-humanizer`, or
  asks to preserve every claim and opinion, keep approved claims or all substance,
  preserve propositions, hedges, scope qualifiers, or relations, humanize form
  only, make prose less formulaic, or improve wording without adding, removing,
  fact-checking, strengthening, softening, or reinterpreting content. Structural
  mode is the default and may reconstruct sentence and paragraph form.
  Conservative mode is opt-in for minimal, local edits that stay close to the
  existing structure. Do not use for broader editorial cleanup, summarization,
  invented voice, or AI-detector evasion; use editorial-humanizer when substantive
  editorial judgment is wanted.
license: MIT
compatibility: claude-code opencode codex
allowed-tools:
  - Read
  - Write
  - Edit
  - Grep
  - Glob
sources:
  - Avoid AI Writing by Conor Bronsdon for targeted-edit and false-positive principles
  - Skill Deslop by Stephen Turner for scientific-register considerations
---

# Faithful Humanizer: Form-Only Prose Editor

## Purpose

Make prose read more naturally by improving its wording and form. Preserve what
the source says, who says it, how strongly it says it, and how its ideas relate.

Faithful Humanizer has two intervention strategies under one preservation
contract:

- **Structural mode (default)** reconstructs sentence and paragraph form when a
  local edit would leave the passage formulaic or poorly connected.
- **Conservative mode (opt-in)** makes the smallest useful localized intervention
  and stays close to the source's subjects, boundaries, architecture, and order.

A faithful sentence that remains slightly artificial is better than a smoother
sentence that changes the substance.

Faithful does not mean literal or timid. When a passage has genuine surface-level
AI patterns, make a clearly more natural rewrite when a semantically equivalent
repair exists. Structural mode may rebuild the form; Conservative mode remains
local-first. Neither mode may leave fixable formulaic prose untouched merely to
avoid changing words.

**Direct distinction:** Editorial Humanizer may change content selection, argument
architecture, emphasis, and rhetorical presentation. Faithful Humanizer may change
only form. In Structural mode, form includes grammatical subjects, clause and
sentence boundaries, local clause order, cohesion, and non-meaningful paragraph
boundaries; it does not include changing claims, force, meaningful order, or
emphasis.

Use **Editorial Humanizer** instead when the user wants broader anti-slop editing,
removal of weak or generic material, argument restructuring, stronger voice, or
an editorial-quality audit and score.

## Shared preservation contract

Treat the source text as authoritative. Edit presentation, not content.

- Preserve every claim, argument, opinion, example, caveat, and conclusion.
- Preserve the source's tone, register, point of view, and emotional valence.
- Preserve the degree of certainty, doubt, importance, praise, criticism, and urgency.
- Resolve every genuine form problem with the intervention strategy selected for
  the request. Leave already-natural passages unchanged in both modes.
- Return only the rewritten text unless the user asks for an audit or explanation.

This skill is a form-only editor. It is not a fact checker, researcher, summarizer,
developmental editor, ghostwriter, or detector-evasion tool.

## Deterministic mode selection

Choose the mode before rewriting. An explicitly named mode always wins.

Select **Structural** when the user names Structural mode or asks to rework or
rebuild sentence structure, make the prose less formulaic or less templated, or
uses equivalent language. A Faithful request that does not choose an intensity
also selects Structural.

Select **Conservative** when the user names Conservative mode or asks for minimal
editing, a light touch, copyediting only, wording that stays close to the source,
or preservation of the existing sentence or paragraph structure.

A request to preserve every claim does not by itself select Conservative. A
scientific, legal, medical, financial, security, policy, or other high-stakes
register strengthens the semantic and register checks but does not silently switch
the selected mode.

If a requested transformation conflicts with the shared preservation contract,
explain the boundary. Route to Editorial Humanizer only when the user authorizes
substantive selection, compression, reprioritization, or argument restructuring.

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
9. **Comparison**: Preserve comparison sets, direction, baselines, degree, and what
   is being compared.
10. **Emphasis**: Preserve deliberate importance, contrast, repetition, and ordering
    when they affect the point being made.
11. **Meaningful information and argument order**: Preserve sequence when it carries
    chronology, causality, scope, emphasis, grouping, or argumentative progression.
12. **Structure-bearing content**: Preserve headings, list membership, examples,
    section order, and paragraph groupings that encode meaning.
13. **Register constraints**: Preserve genre-specific formality, terminology,
    conventions, and precision.

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
- Splitting or combining sentences when meaning and emphasis stay stable
- Improving sentence flow and modestly varying rhythm without manufacturing drama
- Replacing a locally awkward AI-associated phrase only when the replacement is semantically equivalent
- Changing grammatical subjects without changing agency, scope, attribution, or emphasis
- Moving qualifications closer to the claims they govern
- Changing clause order when chronology, causality, scope, emphasis, and meaningful
  argument order remain intact
- Replacing repetitive transition-led sequencing with cohesive known-to-new flow
- Changing paragraph boundaries that do not encode a meaningful grouping

Do not change a word merely because it appears on an AI-writing checklist. Em
dashes, passive voice, adverbs, three-item lists, title case, technical jargon, and
curly quotes can all be legitimate. Change them only when they make this particular
passage less clear or less natural.

## Shared rewriting standard

Do not return the source unchanged merely because preservation is strict. After
protecting the substance, actively repair surface patterns such as:

- verbose scaffolding and throat-clearing that carry no independent meaning;
- redundant modal pairs such as `may potentially` or `could possibly` when
  removing the adverb preserves the same uncertainty; keep `may` or `could`;
- formulaic transitions and repeated sentence openings;
- indirect or nominalized syntax that has a clear equivalent;
- locally repetitive wording, synonym cycling, or metronomic sentence shapes;
- empty metadiscourse that can be expressed as natural emphasis; and
- awkward punctuation or sentence boundaries.

The result should be materially less formulaic, not merely proofread. Structural
mode should solve structural patterns through safe reconstruction. Conservative
mode should change the smallest span that fully resolves each local problem.

If two natural rewrites are equally faithful and equally appropriate for the
selected mode, choose the one that removes more of the AI-shaped form. If no
natural equivalent preserves the substance, retain the source wording. If
equivalence is uncertain, keep or restore the original wording.

## Structural mode

Use Structural mode by default. Reconstruct sentence and paragraph form from the
semantic ledger rather than editing the source linearly when its structure is
formulaic.

Structural mode may:

- change grammatical subjects;
- split or merge sentences;
- move qualifications closer to the claims they govern;
- change clause order when chronology, causality, scope, emphasis, and meaningful
  argument order remain intact;
- replace repetitive transition-led sequencing with cohesive known-to-new flow; and
- change paragraph boundaries when they do not encode a meaningful grouping.

Structural mode is not permission to paraphrase for its own sake. Leave
already-natural form alone. Do not create arbitrary fragments, random sentence
lengths, fake informality, grammatical errors, or punctuation bans. Sentence
variation must follow meaning, emphasis, cohesion, or the relationships among
ideas. Never optimize for an AI-detector score.

## Conservative mode

Use Conservative mode only when the user selects it through explicit naming or
clear minimal-intervention language. Preserve the current local-first behavior:

- prefer the smallest useful localized intervention;
- remove formulaic wording and repair local awkwardness;
- rewrite a phrase, clause, or sentence when necessary;
- preserve subjects, sentence boundaries, paragraph architecture, and ordering
  unless a local defect cannot otherwise be resolved;
- retain already-natural wording; and
- avoid broad reconstruction when a smaller safe change works.

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

Author-specific punctuation is part of voice. Preserve it unless a local change
clearly improves naturalness or the user supplies a different style guide.

## Scientific and academic register preservation

For scientific or academic prose, read
`../references/registers/scientific-writing.md` as preservation constraints.

In particular:

- preserve technical and disciplinary terminology, including deliberate repetition;
- preserve conventional hedging, qualification, uncertainty, and citation language;
- preserve methods-section conventions and legitimate passive constructions;
- preserve statistical meaning, evidence boundaries, and causal strength; and
- keep the formality appropriate to abstracts, manuscripts, grants, and peer review.

Do not change `was measured` to `we measured` unless authorship and agency are
explicit. Do not remove `may`, `suggests`, or `is associated with` to make a claim
more forceful. Do not vary an exact technical term merely for rhythm. Do not make
scientific prose conversational merely to make it sound human.

## Shared semantic ledger

Before rewriting in either mode, create a private ledger that accounts for:

- each factual and evaluative proposition;
- the speaker or source of each proposition;
- stance and opinion ownership;
- modality and epistemic strength;
- scope, quantities, dates, names, negation, and comparisons;
- chronology;
- causal, conditional, contrastive, and concessive relationships;
- exact anchors;
- meaningful information or argument order; and
- register constraints.

The numbered invariants and exact-anchor rules above define what each ledger item
must preserve. Do not duplicate or weaken that contract when applying a mode.

## Structural workflow

Run this process internally in Structural mode:

1. **Set boundaries.** Identify editable prose and protect quotations, code,
   citations, identifiers, and exact anchors.
2. **Diagnose structure.** Find formulaic sequencing, repetitive transition-led
   sentences, weak information flow, overloaded sentences, and boundaries that
   obscure relationships among ideas.
3. **Build the ledger.** Record every shared semantic and register constraint.
4. **Reconstruct from the ledger.** Rebuild the passage instead of editing it
   linearly. Use sentence and paragraph form that expresses the same relationships,
   emphasis, and meaningful order more naturally.
5. **Compare proposition by proposition.** Map every source proposition to the
   rewrite and every rewrite proposition back to the source.
6. **Run a naturalness and cohesion pass.** Confirm that the result is materially
   less formulaic and that known-to-new flow or another meaning-driven structure
   improves the passage.
7. **Restore on doubt.** Restore or revise any transformation whose semantic safety
   is uncertain.
8. **Deliver.** Return the rewrite without commentary unless commentary was requested.

## Conservative workflow

Run this process internally in Conservative mode:

1. **Set boundaries.** Identify editable prose and protect quotations, code,
   citations, identifiers, and exact anchors.
2. **Diagnose local surface problems.** Mark wording, syntax, repetition,
   transitions, grammar, rhythm, or punctuation that is locally formulaic or
   unnatural.
3. **Build the ledger.** Record every shared semantic and register constraint.
4. **Edit the smallest sufficient span.** Rewrite a whole sentence only when a
   smaller repair cannot resolve the local defect.
5. **Compare proposition by proposition.** Map every source proposition to the
   rewrite and every rewrite proposition back to the source.
6. **Restore on doubt.** Restore any edit whose equivalence is uncertain.
7. **Deliver.** Return the rewrite without commentary unless commentary was requested.

## Final semantic diff

Before responding, verify all of the following:

- No source claim disappeared, and no new claim appeared.
- Every opinion belongs to the same speaker and keeps the same direction.
- Certainty, hedging, obligation, permission, and possibility remain unchanged.
- Negation, exceptions, conditions, comparisons, and causal strength remain unchanged.
- Quantifiers, scope, time, sequence, and attribution remain unchanged.
- Exact anchors and every list item are present and unaltered.
- Meaningful information order, argument order, grouping, and emphasis remain intact.
- The rewrite does not introduce a more casual, forceful, emotional, promotional,
  skeptical, or confident stance.
- Every edit has a form-based reason; no style rule was applied for its own sake.
- Every genuine form problem with a safe equivalent was repaired; minimality did
  not become a reason for a cosmetic or unchanged result.
- The intervention matches the selected mode: Structural reconstruction is
  meaning-driven, or Conservative editing remains as local as the defect permits.

If any check fails, revise or restore the source wording.

## Output

### Rewrite request

Return only the rewritten text. Do not add a preamble, score, change log, or closing invitation.

### Audit or explanation request

Return the rewritten text first, then two brief sections:

- `Form changes`: the kinds of surface edits made
- `Preservation notes`: any wording deliberately retained to avoid changing substance

Always include both labels exactly as `Form changes:` and `Preservation notes:`.
Do not merge the two sections, replace them with an unlabeled explanation, or
omit either label. The required order is rewrite, `Form changes:`, then
`Preservation notes:`.

Do not assign an AI-likeness score.

## Examples

### Redundant wording without lost qualification

**Before**

> Additionally, it is important to note that the platform may potentially reduce setup time for some teams.

**After**

> Importantly, the platform may reduce setup time for some teams.

The rewrite keeps the emphasis (`Importantly`), uncertainty (`may`), and scope
(`some teams`). It removes only redundant scaffolding.

### Formulaic syntax receives a real rewrite

**Before**

> At this point in time, the committee is in the process of conducting an evaluation of the proposal.

**After**

> The committee is currently evaluating the proposal.

The proposition, actor, tense, and object remain, while the sentence loses its
formulaic scaffolding. Faithful editing does not require preserving awkward syntax.

### One contract, two intervention strategies

**Before**

> The findings suggest that remote work may improve retention for some employees. However, because the survey included only staff who had remained with the company for at least six months, the results should not be interpreted as evidence that remote work causes lower turnover. Taken together, these observations highlight the importance of conducting further research across a wider range of roles and tenure levels.

**Structural**

> The findings suggest that remote work may improve retention for some employees. The survey, however, included only staff who had remained with the company for at least six months. Its results should therefore not be interpreted as evidence that remote work causes lower turnover. Taken together, these observations show why further research across a wider range of roles and tenure levels is important.

**Conservative**

> The findings suggest that remote work may improve retention among some employees. However, because the survey included only staff who had remained with the company for at least six months, the results should not be taken as evidence that remote work causes lower turnover. Together, these observations highlight the importance of further research across a wider range of roles and tenure levels.

Both rewrites preserve the same propositions, uncertainty, sample limitation,
causal boundary, and research recommendation. Structural changes sentence form and
information flow; Conservative repairs the wording locally.

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

## Reference note

Targeted-edit and contextual false-positive principles were informed by Avoid AI
Writing by Conor Bronsdon. Scientific-register considerations were informed by
Skill Deslop by Stephen Turner, with blanket active-voice and punctuation rules
intentionally excluded. This skill's instructions and examples are independently
written for its stricter form-only contract.
