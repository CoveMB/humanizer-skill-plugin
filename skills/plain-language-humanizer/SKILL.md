---
name: plain-language-humanizer
version: 1.0.0
description: |
  Adapt supplied technical content for a less technical audience. Use whenever the
  user explicitly invokes `$plain-language-humanizer`, asks for plain language,
  asks to reduce jargon, a nontechnical reader, or a concise explanation of supplied
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

# Plain Language Humanizer: Technical Meaning in Plain Language

## Purpose

Adapt supplied technical content for a less technical audience while preserving
technical meaning, operational safety, and source boundaries. Remove unnecessary
jargon, retain and briefly define terminology required for precision, protect
technical literals, and add only the explanation required for comprehension.

Use the source as the authority for source-specific behavior. Use only an
unambiguous conventional meaning to define a term; never invent source-specific
behavior, consequences, guarantees, or facts.

This skill is not a research, fact-checking, troubleshooting, translation,
summarization, professional-advice, or AI-detector-evasion system.

## Direct distinction from the other Humanizers

- Use **Plain Language Humanizer** for audience adaptation and limited explanatory
  additions that preserve all substantive technical content.
- Use **Faithful Humanizer** when no explanatory addition is permitted and the
  technical register should remain.
- Use **Editorial Humanizer** when the user authorizes substantive selection,
  compression, reprioritization, or restructuring.

Do not capture a generic request to humanize text. Do not use this skill for
standalone research, debugging, troubleshooting, fact-checking, translation,
summarization, or detector-evasion requests.

## Audience

Use an informed non-specialist as the default audience: a reader comfortable with
ordinary workplace language but without domain expertise. A user-specified audience
always overrides the default. Use a respectful, non-patronizing tone.

## Deterministic mode selection

Choose the mode before transforming the source. **An explicitly named mode always
wins. Rewrite mode is the default.**

- Select **Rewrite mode** when the user names Rewrite mode; asks to rewrite,
  simplify, reduce jargon, use plain language, make content accessible, or adapt it
  for a nontechnical reader; or invokes `$plain-language-humanizer` without naming
  a mode.
- Select **Explain mode** when the user names Explain mode, asks what supplied
  technical content means, requests a walkthrough, or asks for an explanation for
  a less technical reader.
- No mode specified selects Rewrite.
- An explicit request for both operations is a combined request, not a third mode.

## Shared technical-preservation contract

Treat the source as authoritative. Preserve every substantive claim, condition,
warning, prerequisite, step, qualifier, conclusion, actor, attribution, and
relationship with the same force. Preserve uncertainty, obligation, permission,
prohibition, negation, scope, chronology, causal strength, and meaningful order.

Adapt presentation only where comprehension benefits. Preserve already-clear
passages. If shortening would delete substantive content, explain the conflict and
ask for permission to summarize or use Editorial Humanizer.

## Technical-content ledger

Before transforming the source, record privately in a technical-content ledger:

- every factual and evaluative claim;
- actor, ownership, attribution, and agency;
- quantities, dates, units, thresholds, ranges, and comparisons;
- modality, uncertainty, obligation, permission, and prohibition;
- scope, negation, exceptions, conditions, dependencies, and prerequisites;
- chronology, causal strength, and meaningful sequence;
- warnings, failure states, and escalation conditions;
- procedure steps and procedural and operational order; and
- every protected literal.

Map every ledger item into the output with the same meaning and relationships.

## Protected literals

Preserve exact code, commands, flags, identifiers, configuration keys, API names,
schema fields, error messages, URLs, paths, versions, citations, formulas, units,
and other strings whose exact form is technically meaningful. Preserve text inside
code blocks and inline code exactly.

If simplifying a protected literal would improve readability, keep it unchanged
and explain it nearby. Never replace an exact technical literal with an approximate
substitute.

## Language classification

Classify technical language before editing:

1. **Protected literal:** Preserve it exactly and explain nearby when necessary.
2. **Necessary technical term:** Retain it and define it briefly at first meaningful
   use.
3. **Unnecessary jargon:** Replace it with a precise everyday equivalent.
4. **Already-familiar language:** Retain it without explanation.
5. **Ambiguous or context-dependent term:** Preserve it and ask a precise question
   rather than inventing a definition.

Expand an acronym at first meaningful use unless the audience clearly knows it or
the acronym is a protected literal whose expansion the source does not establish.

## Rewrite mode

Produce replacement text in plain language. Define necessary terminology inline at
its first meaningful use. Use the following edits when they improve comprehension
without changing the ledger:

- shorten overloaded sentences;
- expose the responsible actor and action;
- replace nominalizations with direct verbs;
- move qualifications closer to the claims they govern;
- split or merge sentences when meaning and emphasis remain stable;
- change paragraph boundaries that do not carry meaning; and
- use lists for genuine steps, choices, requirements, or grouped information.

Keep operational order, meaningful grouping, emphasis, and every ledger item.
Retain a technical term when changing it would reduce precision.

## Explain mode

Produce a concise, source-grounded explanation rather than replacement copy. Group
the source into concepts such as what something is, what it does in the supplied
context, and what action the source requires. Include why something matters only
when the source establishes that consequence.

Use headings or bullets only when they materially reduce reading effort. Add an
example or analogy only when the user requests one; label it as explanatory and
keep it from introducing a false equivalence or source claim.

## Combined requests

When the user explicitly requests both operations, produce:

1. the plain-language rewrite; then
2. a short section labeled exactly `Explanation:`.

Treat this as a compound request, not a third mode.

## Anti-bloat contract

Build the output from the source plus only the explanation required for
comprehension. Every added sentence must do at least one of the following:

- define a necessary term;
- clarify a relationship between source elements; or
- explain a required action or source-supported consequence.

Preserve already-clear passages. Prefer the shortest output that remains complete
and accurate. In both modes, define each term once unless its meaning changes. Keep
the result free of throat-clearing, repeated summaries, tutorials, history,
decorative examples, and redundant restatements.

## High-stakes technical content

For scientific, medical, legal, financial, security, policy, and other high-stakes
content:

- retain required domain terminology and define it rather than replacing it with
  an imprecise approximation;
- preserve uncertainty, evidence boundaries, attribution, statistical meaning,
  causal strength, warnings, prerequisites, exceptions, and escalation conditions;
- preserve exact procedural and operational literals; and
- keep the seriousness and precision appropriate to the domain.

Ordinary Rewrite output remains rewrite-only. If a request moves from editing into
professional advice or operational reliance, state the boundary and recommend
appropriate human review instead of answering beyond this skill's scope.

## Scientific and academic profile

For scientific or academic content, read
`../references/registers/scientific-writing.md` as precision constraints.

Retain exact scientific terms when an everyday substitute would change meaning,
and define them briefly at first meaningful use. Preserve citations, quantities,
units, statistical estimates, intervals, uncertainty, attribution, evidence
boundaries, causal strength, and legitimate passive constructions. Keep an
association distinct from a cause, a hypothesis distinct from a finding, and a
population-specific result distinct from a general claim.

## Missing or conflicting context

- If no source or technical term is supplied, ask for the content to transform.
- If the audience is unspecified, use the informed non-specialist default.
- If a definition depends on unavailable context, preserve the term and ask a
  precise question.
- If simplifying a protected literal would improve readability, keep it exact and
  explain it nearby.
- If requested shortening would delete substantive content, explain the conflict
  and request permission to summarize or use Editorial Humanizer.
- If the request requires research, troubleshooting, or professional advice, state
  the boundary and route the task separately.

## Rewrite workflow

Run this process internally:

1. **Set the audience and mode.** Use the user's audience or the informed
   non-specialist default, and select Rewrite deterministically.
2. **Build the ledger.** Record all substantive content, relationships, order, and
   protected literals.
3. **Classify the language.** Distinguish protected literals, necessary terms,
   unnecessary jargon, familiar language, and ambiguous terms.
4. **Rewrite for comprehension.** Rebuild the presentation from the ledger, define
   necessary terms once, and replace only unnecessary jargon.
5. **Apply the anti-bloat contract.** Keep only source content and required
   explanation.
6. **Run the final check.** Compare source and output in both directions and restore
   any unsafe change.
7. **Deliver.** Return only the rewrite unless the user requested another shape.

## Explain workflow

Run this process internally:

1. **Set the audience and mode.** Use the user's audience or the informed
   non-specialist default, and select Explain deterministically.
2. **Build the ledger.** Record all substantive content, relationships, order, and
   protected literals.
3. **Classify the language.** Identify what needs definition and what is already
   clear.
4. **Explain from the source.** Group ideas for comprehension while retaining every
   material detail and adding only conventional definitions or source-supported
   relationships.
5. **Apply the anti-bloat contract.** Use the shortest complete explanation.
6. **Run the final check.** Compare source and explanation in both directions and
   restore any unsupported or imprecise statement.
7. **Deliver.** Return only the explanation unless the user requested another shape.

## Final bidirectional content check

Before responding, run a bidirectional content check:

- Map every substantive source element to an output element with the same force and
  relationships.
- Map every output claim back to the source, an unambiguous conventional
  definition, or an explicitly requested explanatory device that does not assert
  source-specific facts.
- Confirm that every protected literal remains exact.
- Confirm that procedural order, warnings, conditions, and exceptions remain
  intact.
- Confirm that necessary terminology is defined once and unnecessary jargon is
  removed.
- Confirm that already-clear text changed only when comprehension benefited.
- Confirm that the output follows the selected mode without an unrequested wrapper.
- Confirm that every added sentence satisfies the anti-bloat contract.

Restore the source wording or ask a precise question if any check cannot pass.

## Output

- **Rewrite mode:** Return only the rewrite unless the user requests another output
  shape. Add no preamble, change log, or closing invitation.
- **Explain mode:** Return only the explanation unless the user requests another
  output shape. Add no rewrite or unrequested wrapper.
- **Combined request:** Return the rewrite first, followed by a short section
  labeled exactly `Explanation:`.
- **Missing or conflicting context:** Ask only the precise question needed to
  continue safely.

## Examples

### Rewrite: define necessary API terms

**Source**

> The API enforces a per-client rate limit of 120 requests per minute and returns HTTP 429 for requests above the threshold.

**Rewrite**

> The application programming interface (API), which lets software systems communicate, limits each client to 120 requests per minute. Requests above that limit receive HTTP 429, an error code meaning too many requests.

### Explain: retain and define webhook

**Source**

> When an invoice is paid, Ledger emits an `invoice.paid` webhook to the configured HTTPS endpoint. Delivery is retried with exponential backoff for up to 24 hours.

**Explanation**

> When an invoice is paid, Ledger sends an `invoice.paid` webhook—a message that one system automatically sends to another—to the configured HTTPS endpoint. If delivery fails, Ledger retries for up to 24 hours, waiting progressively longer between attempts; this is exponential backoff.

### Combined: protect a migration procedure

**Source**

> Run `atlas migrate --dry-run` before `atlas migrate --apply`. Do not use `--apply` if validation reports an incompatible schema. If the second command fails, restore `/srv/atlas/schema.json`.

**Rewrite**

> First, run `atlas migrate --dry-run`, which checks the migration without applying it. Then run `atlas migrate --apply`. Do not use `--apply` if validation reports an incompatible schema, meaning the existing and proposed data structures cannot work together. If `atlas migrate --apply` fails, restore `/srv/atlas/schema.json`.

**Combined explanation**

> Explanation:
>
> The order is required: check the migration first, then apply it. An incompatible-schema report stops the apply step. A failed second command requires restoring the exact file named in the source.

### Scientific causal boundary

**Source**

> Smith et al. (2024) reported a hazard ratio of 0.78 (95% CI 0.61–0.99). This association does not establish causality.

**Rewrite**

> Smith et al. (2024) reported a hazard ratio of 0.78, which compares the rate of an event between two groups over time. The 95% confidence interval (CI) was 0.61–0.99, a range that expresses uncertainty around the estimate. This association does not establish causality.

### Already-clear source

**Source**

> Run `make test` before deployment. Stop if any test fails.

**Rewrite**

> Run `make test` before deployment. Stop if any test fails.

### Restore or ask for an ambiguous term

**Source**

> After validation, enable `standard mode`.

If `standard mode` has no definition in the available context, preserve it and ask:

> What does `standard mode` mean in this system?
