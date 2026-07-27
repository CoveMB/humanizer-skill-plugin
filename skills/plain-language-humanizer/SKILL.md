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
2. **Necessary technical term:** Preserve every actor, threshold value, condition,
   and consequence through the ledger. For a non-specialist, an unfamiliar or
   domain-specific actor-role label whose source states its duty or relationship
   is precision-bearing: retain it and add a brief description of its function in
   this passage beside first meaningful use. The source-stated duty or relationship
   is sufficient context for that bounded description. Retain an explicit technical
   threshold term when replacement would reduce precision and define it from the
   source cutoff and consequence. Skip definitions for familiar or already-clear
   language. If context cannot support a bounded definition, preserve the term and
   ask a precise question; do not import external facts.
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
If the source presents an unnumbered procedure, restructure it with prose or
bullets rather than inventing numeric step labels.

## Explain mode

Produce a concise explanation rather than replacement copy. Ground every factual
claim in the source or an unambiguous conventional definition. Group the source
into concepts such as what something is, what it does in the supplied context, and
what action the source requires. Include why something matters only when the source
establishes that consequence.

Use headings or bullets only when they materially reduce reading effort. Add an
example or analogy when the user explicitly requests one or when it is materially
needed to explain a technical concept. Label it as explanatory rather than a source
fact. Retain the technical term and every protected literal. State its limits so it
does not imply exact equivalence. Add no source-specific behavior, guarantees,
numbers, consequences, or advice. Apply extra caution to scientific, medical,
legal, financial, and security content. Make every device satisfy the anti-bloat
contract.

## Combined requests

When the user explicitly requests both operations, produce:

1. the plain-language rewrite; then
2. a short section labeled exactly `Explanation:`.

Treat this as a compound request, not a third mode.

## Anti-bloat contract

Build the output from the source plus only the explanation required for
comprehension. Every added sentence must do at least one of the following:

- define a necessary term;
- clarify a technical concept or a relationship between source elements; or
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
- retain exact source wording for terms or short phrases whose substitution could
  change safety, directive, or epistemic force, including medication action,
  frequency, and escalation wording and explicit evidence-boundary phrases such
  as `does not establish`; explain around them when clarification is needed;
- preserve broader clauses with the same meaning and force, allowing equivalent
  grammar and acronym expansion; protected literals remain exact;
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
7. **Deliver.** Return only the rewrite.

## Explain workflow

Run this process internally:

1. **Set the audience and mode.** Use the user's audience or the informed
   non-specialist default, and select Explain deterministically.
2. **Build the ledger.** Record all substantive content, relationships, order, and
   protected literals.
3. **Classify the language.** Identify what needs definition and what is already
   clear.
4. **Explain from the source.** Group ideas for comprehension while retaining every
   material detail and adding only conventional definitions, source-supported
   relationships, or a permitted bounded explanatory device.
5. **Apply the anti-bloat contract.** Use the shortest complete explanation.
6. **Run the final check.** Compare source and explanation in both directions and
   restore any unsupported or imprecise statement.
7. **Deliver.** Return only the explanation.

## Final bidirectional content check

Before responding, run a bidirectional content check:

- Map every substantive source element to an output element with the same force and
  relationships.
- Map every factual output claim back to the source or an unambiguous conventional
  definition. Treat every permitted example or analogy as a labeled explanatory
  device rather than a source fact, and confirm its limits satisfy Explain mode.
- Confirm that every protected literal remains exact.
- Confirm that procedural order, warnings, conditions, and exceptions remain
  intact.
- Confirm that every actor, threshold value, condition, and consequence survives
  through the ledger. For a non-specialist, confirm that each unfamiliar or
  domain-specific actor-role label with a source-stated duty or relationship
  appears with one brief description of its function in this passage; the stated
  duty or relationship is sufficient context. Retain each explicit technical
  threshold term whose replacement would reduce precision and define its cutoff
  and consequence from source context. Skip definitions for familiar or
  already-clear language. If context cannot support a bounded definition, preserve
  the term and ask a precise question; do not import external facts.
- Confirm that necessary terminology is defined once and unnecessary jargon is
  removed.
- Confirm that already-clear text changed only when comprehension benefited.
- Confirm that the output follows the selected mode without an unrequested wrapper.
- Confirm that every added sentence satisfies the anti-bloat contract.

Restore the source wording or ask a precise question if any check cannot pass.

## Output

- **Rewrite mode:** Return only the rewrite. Add no preamble, change log, or closing
  invitation.
- **Explain mode:** Return only the explanation. Add no rewrite or unrequested
  wrapper.
- **Combined request:** Return the rewrite first, followed by a short section
  labeled exactly `Explanation:`.
- **Missing or conflicting context:** Ask only the precise question needed to
  continue safely.

## Examples

### Rewrite: define necessary API terms

**Source**

> The API enforces a per-client rate limit of 120 requests per minute and returns HTTP 429 for requests above the threshold.

**Rewrite**

> The API (application programming interface) sets a rate limit, or threshold, of 120 requests per minute for each client. Requests above the threshold receive HTTP 429, an error code meaning too many requests.

### Rewrite: describe unfamiliar roles from the passage

**Source**

> The controller must notify the processor within 24 hours unless disclosure is prohibited by applicable law. The exception does not remove the duty to retain the incident record.

**Rewrite**

> The controller—the party required to give notice—must notify the processor, the party receiving the notice, within 24 hours unless disclosure is prohibited by applicable law. This exception does not remove the duty to retain the incident record.

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
