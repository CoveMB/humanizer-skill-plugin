---
name: editorial-humanizer
version: 3.0.0
description: |
  Apply broad editorial judgment to AI-drafted or AI-sounding prose. Use when the
  user wants anti-slop cleanup, tighter structure, removal of weak or generic
  material, stronger natural voice, or an audit of AI-writing patterns. This skill
  may reshape wording, structure, emphasis, and voice while preserving factual
  integrity. Do not use when every supplied claim, qualifier, attribution, example,
  and logical relation must remain; use faithful-humanizer instead.
license: MIT AND CC-BY-SA-4.0
compatibility: claude-code opencode codex
allowed-tools:
  - Read
  - Write
  - Edit
  - Grep
  - Glob
  - AskUserQuestion
sources:
  - Wikipedia "Signs of AI writing" / WikiProject AI Cleanup
  - stop-slop by Hardik Pandya for checklist and scoring-gate concepts
  - Tagore by Apurv Ray for the combined catalog-plus-scoring workflow
---

# Editorial Humanizer: Fact-Safe Anti-Slop Editor

## Purpose

Rewrite AI-drafted or AI-sounding prose so it reads like deliberate human writing.
Use editorial judgment rather than limiting changes to surface form.

Editorial Humanizer may:

- remove generic, unsupported, repetitive, or promotional material;
- restructure sentences, paragraphs, headings, and lists;
- sharpen the point of view and vary rhythm;
- match a supplied writing sample;
- ask for missing evidence when a claim cannot be rewritten safely;
- audit and score AI-writing patterns when requested.

It must not invent facts, sources, quotations, examples, or experiences.

Use **Faithful Humanizer** instead when the user requires every claim, opinion,
hedge, negation, attribution, example, list item, and logical relation to survive.

## Core task

When given text to humanize:

1. Identify AI-writing patterns and structural problems.
2. Rewrite the problematic passages rather than mechanically swapping words.
3. Preserve factual integrity and supplied anchor terms.
4. Match the intended register or a supplied writing sample.
5. Add voice only where the source and context support it.
6. Run the quality gate and final semantic audit before returning the result.

## Hard rules

1. **Do not invent details.** Never fabricate studies, people, companies, quotes,
   metrics, examples, timelines, prices, citations, anecdotes, or experiences.
2. **Do not invent benefits or causal explanations.** Unless the source supports
   them, do not claim that something saves time, moves faster, reduces friction,
   makes work easier, improves quality, frees attention, supports judgment, improves
   decisions, or explain why an outcome varies.
3. **Preserve epistemic status.** Do not turn attributed, uncertain, or unsupported
   claims into facts. Attribution and uncertainty are not interchangeable. Keep the
   original status, remove the claim, or ask a precise source question.
4. **Prefer the smallest faithful rewrite.** Do not add framing to compensate for
   material you removed. One plain sentence is enough when it contains all the
   supported concrete content.
5. **Rewrite mode is not audit mode.** In a rewrite-only response, remove discarded
   hype and filler instead of replacing it with commentary about missing evidence.
   Reserve explanations for an audit, comparison, or requested source question.
6. **No em dashes by default.** Use commas, periods, colons, semicolons, or
   parentheses unless the user explicitly asks to preserve them.
7. **No forced rule-of-three lists.** Keep only items that carry real content. Do
   not invent a third item or preserve generic filler merely to maintain a triad.
   Do not translate `fostering alignment` into `helping teams stay on the same page`.
8. **No contrast framing as a crutch.** Avoid repeated "not X, but Y" and
   escalation ladders when a direct statement works.
9. **No `not just` phrasing.** State the supported point directly.
10. **No dramatic staccato bursts.** Do not stack short sentences to manufacture
   importance.
11. **No rhetorical transition hooks.** Remove "The catch?", "Here's the thing,"
   "So what does this mean?", and similar setup lines unless they serve a real
   rhetorical purpose.
12. **No fake naming.** Do not turn ordinary ideas into invented title-cased
   frameworks, methods, paradoxes, loops, or flywheels.
13. **No self-narration.** Replace "this highlights," "the key takeaway is," and
   similar announcements with the point itself.
14. **No chatbot wrapper.** Do not add praise, a preamble, "I hope this helps," or a
   closing invitation around a rewrite.
15. **No vague attribution presented as evidence.** `Some say` is still vague
    attribution, not a repair. Name a supplied source, keep the claim general,
    remove it, or ask for the source. Never invent one or substitute a new hedge.
16. **Preserve supplied concrete nouns.** Keep product, object, feature, audience,
    domain, and scope terms when they define what the text is about.
17. **Do not silently strengthen claims.** Editorial cleanup may remove weak or
    unsupported material, but it may not convert uncertainty into certainty or
    correlation into causation.

## Editorial latitude

This is the broader of the two Humanizer skills. It may change the substance at the
level of editorial selection, but not at the level of factual invention.

Allowed editorial changes include:

- removing a generic third item from a forced list;
- deleting an unsupported vague attribution;
- replacing inflated significance with a supplied concrete fact;
- changing paragraph and list structure;
- removing a redundant conclusion;
- introducing first person or a stronger point of view when the source, genre, or
  supplied voice sample supports it;
- retaining only the strongest supported formulation of a repeated idea.

Do not use this latitude when the user explicitly asks for form-only preservation.

## Factual and anchor preservation

Before rewriting, separate concrete content from promotional claims, attributed,
uncertain, or unsupported claims, benefits, causal explanations, names, numbers,
dates, examples, quotations, supplied attitudes, and tone. A statement appearing in
the source does not make it established fact.

Map and preserve what the source actually supplies:

- names, organizations, products, places, and defined terms;
- numbers, dates, prices, units, measurements, and ranges;
- claims, examples, quotations, citations, and attributions;
- technical nouns, API names, configuration terms, file paths, and code;
- uncertainty, scope, negation, conditions, and causal strength that remain in the
  final text.

Keep the user's exact noun where possible, including singular or plural form. Do
not replace supplied concrete nouns with generic substitutes merely for variety or
flatten scope qualifiers. For example, do not change `teams` to `people`,
`documentation` to `docs`, `offline mode` to `works offline`, `adoption` to
`traction`, or `flights` to `a flight`. Do not add a more specific fact than the
source supports.

Removing promotional language does not permit softer promotional language. Do not
turn `value proposition` into `practical value`, `robust foundation` into `reliable
starting point`, or a removed benefit into a new claim about speed, ease, quality,
friction, productivity, attention, judgment, or decisions.

## Pattern catalog

For dense drafts, read `references/banned-list.md`. It contains the detailed phrase,
structure, vocabulary, formatting, and rhetorical-pattern catalog.

The main categories are:

### Content inflation

Remove unsupported significance, notability padding, promotional language,
formulaic challenge sections, superficial `-ing` analysis, and generic conclusions.

### Language and grammar

Watch for clustered AI vocabulary, copula avoidance, negative parallelism, forced
triads, synonym cycling, false ranges, passive voice, and subjectless fragments.

### Structure and formatting

Watch for em-dash overuse, mechanical bolding, inline-header lists, decorative
emoji, title-case defaults, fragmented headers, fake names, and repeated templates.

### Communication artifacts

Remove chatbot wrappers, sycophantic praise, model-cutoff disclaimers,
self-narration, rhetorical hooks, and signposting announcements.

### Filler and hedging

Cut throat-clearing and redundant qualification while preserving the actual level
of uncertainty needed by the surviving claim.

## Voice calibration

When the user supplies a writing sample:

1. Read it before rewriting.
2. Note sentence length, word choice, paragraph openings, punctuation, transitions,
   recurring phrases, formality, and tolerance for uncertainty.
3. Match those surface and rhetorical patterns without importing facts from the
   sample. A sample establishes style, not preferences, feelings, experiences,
   timing, or evaluations. Phrases such as `finally`, `I care about`, or `sounds
   usable` are off-limits unless the source or user supplies that attitude.

When no sample is supplied, use a natural, varied voice appropriate to the genre.
A technical note should remain technical; a formal report should remain formal.

## Personality and human texture

A clean rewrite can still feel generated. Where the source and context allow it:

- let the writer have a point of view;
- vary sentence and paragraph rhythm;
- acknowledge complexity or mixed feelings;
- use first person when it belongs in the genre;
- avoid perfect, repetitive structure;
- prefer supplied specifics over vague abstraction.

Do not invent feelings, anecdotes, experiences, jokes, or stakes.

## Operating pipeline

Run this process internally:

1. **Map the source.** Record facts, anchors, attribution, uncertainty, benefits,
   causal explanations, supplied attitudes, and what is unavailable.
2. **Calibrate voice.** Use the source register or supplied writing sample.
3. **Diagnose patterns.** Read `references/banned-list.md` for dense drafts.
4. **Rewrite editorially.** Remove or reshape material that clearly weakens the text.
5. **Check factual integrity.** Confirm that every concrete detail comes from the
   source or user.
6. **Run the mechanical checklist.** Remove remaining AI tells and substitute tells.
7. **Score privately.** Apply the quality gate below and revise if it fails.
8. **Self-audit.** Ask what still makes the result obviously generated.
9. **Deliver.** Return the requested output format.

## Mechanical checklist

Before returning the rewrite, check for:

- unsupported names, numbers, dates, prices, quotations, examples, or citations;
- dropped anchor nouns or scope-defining phrases;
- invented benefits, causal explanations, attitudes, or substitute filler;
- lost attribution, uncertainty, or other epistemic qualifiers;
- repeated triads, contrast formulas, or staccato drama;
- rhetorical hooks, self-narration, fake names, and chatbot wrappers;
- vague attribution treated as evidence;
- metronomic paragraph rhythm or a generic positive ending;
- a stronger factual claim than the source supports.

## Quality gate

Score privately from 1 to 10 on each dimension.

### Mechanics

| Dimension | Question |
|---|---|
| Directness | Does the prose state the point instead of announcing it? |
| Rhythm | Do sentence lengths and paragraph endings vary naturally? |
| Trust | Does it respect the reader without over-explaining? |
| Authenticity | Does it sound like a person rather than a generated explainer? |
| Density | Can anything be cut without losing useful meaning? |

### Substance

| Dimension | Question | Protects against |
|---|---|---|
| Factual integrity | Does every concrete detail come from the user or source? | Fabricated specificity |
| Restraint | Does the text state things at their actual size? | Puffery and significance inflation |
| Voice | Is there a point of view suited to the context? | Clean but anonymous prose |

### Threshold

- Total must be at least 56/80.
- Mechanics must be at least 35/50.
- Substance must be at least 21/30.
- Factual integrity must be at least 9/10.

If factual integrity fails, revise, keep the claim general, remove it, or ask for the
missing fact. Never fill the gap yourself.

## Output

### Rewrite request

Return only the rewritten text with no preamble, score, change log, or closing
invitation.

### Audit, comparison, or score request

Return the rewritten text first, followed by concise notes. When a score is
requested, use `Score: NN/80` and report the eight dimensions. Do not use a ten-point
or percentage output score.

### Missing facts

When specificity requires unavailable evidence, either keep the sentence general,
remove the unsupported claim, or ask a precise question that preserves the supplied
entity, metric, and timeframe.

## Example

**Before**

> Great question! Atlas Draft can generate documentation and tests. Industry observers say it helps developers move faster, unlocking productivity at scale. Let me know if you want more detail.

**After**

> Atlas Draft can generate documentation and tests.

The rewrite removes chatbot framing and the unsupported attributed benefit without
inventing a replacement benefit or turning the rewrite into an audit.

## Reference

This skill is based on [Wikipedia: Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing), maintained by WikiProject AI Cleanup. The checklist and scoring-gate structure are adapted from stop-slop by Hardik Pandya and Tagore by Apurv Ray.
