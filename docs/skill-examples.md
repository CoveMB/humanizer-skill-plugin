# Skill examples

This repository ships two related skills:

- `humanizer` is the existing fact-safe anti-slop editor. It can remove generic or unsupported material, restructure prose, and add voice when the source and context allow it.
- `humanizer-form` is a conservative form-only editor. It changes wording and flow while preserving every supplied claim, opinion, qualifier, attribution, example, and logical relation.

Use the explicit skill name when the distinction matters.

## Choosing a skill

| Need | Skill |
|---|---|
| Remove AI-writing patterns and improve the draft editorially | `humanizer` |
| Keep the substance exactly as supplied and change only presentation | `humanizer-form` |
| Audit AI-writing patterns and receive a score | `humanizer` |
| Preserve vague, promotional, disputed, or unsupported claims without fact-checking them | `humanizer-form` |
| Match a sample's voice and allow broader editorial shaping | `humanizer` |
| Match only surface features from a sample without importing its opinions or content | `humanizer-form` |

## Humanizer

Humanizer edits prose that sounds generated, padded, promotional, or too generic. It preserves the facts, claims, tone, and certainty the user supplied, but it is still an editorial anti-slop workflow rather than a strict form-only transformation.

It does not fact check by default. It also should not invent details, names, numbers, dates, sources, quotes, prices, examples, citations, or claims. If a rewrite needs missing facts, Humanizer should ask for them, keep the sentence general, or remove the unsupported claim.

### Good fits

- A draft sounds generated and needs a natural rewrite.
- A paragraph has filler such as "at its core," "this highlights," "unlocking potential," or a forced three-part list.
- Technical documentation needs to keep its meaning but read less mechanically.
- The user provides a writing sample and wants the rewrite to match that voice.
- The user asks for an audit, score, or short explanation of AI-writing patterns.

### Poor fits

- The task is only translation, summarization, or spellcheck.
- The user asks for fact checking, research, sourcing, or citation lookup without asking for prose cleanup.
- The draft needs new facts the user has not supplied.
- Exact legal, medical, financial, or compliance wording matters more than style.
- The user explicitly requires every claim and qualifier to remain in place; use `humanizer-form` instead.

### Basic rewrite

Use this when the user wants cleaner prose with no notes.

```text
Use Humanizer to rewrite this. Return only the rewritten text:

AI-assisted coding serves as a pivotal moment in the evolution of software development, unlocking productivity, creativity, and alignment across cross-functional teams.
```

Humanizer should:

- Remove inflated phrasing such as "pivotal moment" and "unlocking."
- Preserve anchor terms such as "AI-assisted coding" and "cross-functional teams" when they define the subject and scope.
- Avoid adding unsupported claims about speed, quality, adoption, or business value.
- Return only the rewritten text.

### Documentation cleanup

Use this when the documentation is accurate but padded.

```text
Use Humanizer on this documentation paragraph. Keep the technical meaning intact:

This configuration serves as a robust foundation for scalable workflows, ensuring developers can seamlessly optimize productivity and foster alignment across teams.
```

Humanizer should:

- Keep concrete terms such as "configuration" and "scalable workflows."
- Cut filler such as "serves as," "robust foundation," "seamlessly," and "foster alignment."
- Keep the rewrite technical and restrained.
- Avoid adding implementation details.

### Voice calibration

Use this when the rewrite needs to sound like a specific person or team.

```text
Use Humanizer to rewrite the draft. Match the style of this writing sample.

Writing sample:
I prefer short release notes. Name the change, explain the risk, and stop. If there is uncertainty, say exactly what is still unknown.

Draft:
This release introduces a comprehensive enhancement to the validation pipeline, highlighting our commitment to robust developer experiences and setting the stage for future improvements.
```

Humanizer should:

- Read the sample before rewriting.
- Match the sample's sentence length, directness, punctuation habits, and tolerance for uncertainty.
- Keep only supplied facts.
- Avoid turning the release note into a marketing paragraph.

### Audit and score

Use this when the user wants feedback along with the rewrite.

```text
Use Humanizer to audit and score this draft for AI-writing patterns:

Our platform is more than just a tool; it is a testament to innovation, empowering teams to collaborate, create, and scale like never before.
```

Humanizer should:

- Put the rewrite first.
- Add concise notes after the rewrite.
- Use the `Score: NN/80` format when scoring is requested.
- Avoid `8/10`, percentages, or scores out of 100.

### Missing facts

Use this when a vague claim may need evidence before it can be rewritten safely.

```text
Use Humanizer on this. If a sentence needs missing facts to become specific, ask instead of inventing:

Industry reports show that Atlas Note adoption increased significantly last quarter, proving the product is transforming team knowledge management.
```

Humanizer should:

- Avoid inventing a report name, percentage, source, or citation.
- Ask for the missing source or keep the claim general.
- Preserve supplied details in any question, such as "Atlas Note," "adoption," and "last quarter."
- Remove unsupported certainty such as "proving" and "transforming."

## Humanizer Form

Humanizer Form is for strict form-only rewriting. It treats the source as authoritative and does not decide whether a claim is well supported, useful, specific, tasteful, or persuasive.

It may improve grammar, syntax, transitions, repetition, sentence flow, and punctuation. It must not add, remove, strengthen, weaken, fact-check, reinterpret, or reorganize the substance.

### Good fits

- The user says "humanize the form, not the substance."
- A legal, scientific, policy, medical, or technical draft needs cautious copy editing.
- The draft contains opinions or promotional claims that must remain the author's opinions or claims.
- Every hedge, negation, exception, quantifier, attribution, and example must survive.
- The user wants minimal edits rather than a full regeneration.

### Poor fits

- The user wants stronger arguments, better evidence, a new structure, or a shorter summary.
- The user wants facts checked, citations added, or unsupported claims removed.
- The user wants a distinctive personality, anecdotes, humor, or a new point of view.
- The purpose is to bypass an AI detector.

### Basic form-only rewrite

```text
Use $humanizer-form. Make the wording read naturally, but preserve every claim, opinion, qualifier, example, and attribution. Return only the rewrite.

Additionally, it is important to note that the platform may potentially reduce setup time for some teams.
```

Expected rewrite:

```text
Importantly, the platform may reduce setup time for some teams.
```

The rewrite preserves importance, uncertainty (`may`), and scope (`some teams`).

### Preserve vague attribution and evaluative force

```text
Use $humanizer-form. Do not fact-check or delete any claim:

Industry reports suggest adoption is accelerating, highlighting the platform's growing relevance.
```

Expected rewrite:

```text
Industry reports suggest that adoption is accelerating, a trend that highlights the platform's growing relevance.
```

Humanizer Form must not invent a report, remove the vague attribution, or neutralize the claim about relevance.

### Preserve opinion and uncertainty

```text
Use $humanizer-form. Humanize the form only:

Although I find the change unsettling, it may improve efficiency.
```

Expected rewrite:

```text
I find the change unsettling, although it may improve efficiency.
```

The output keeps both the first-person reaction and the uncertain benefit.

### Preserve technical anchors and claim strength

```text
Use $humanizer-form on this documentation sentence:

The system serves as a robust foundation for scalable workflows, ensuring that cross-functional teams can coordinate effectively.
```

Expected rewrite:

```text
The system is a robust foundation for scalable workflows and ensures that cross-functional teams can coordinate effectively.
```

The words `robust`, `scalable workflows`, `cross-functional teams`, and the force of `ensures` remain because they are part of the supplied content.

### Audit mode

```text
Use $humanizer-form to rewrite this and explain only the form changes. Note any wording you deliberately retained to protect the substance:

[paste draft]
```

Humanizer Form should return:

1. The rewritten text
2. A brief `Form changes` section
3. A brief `Preservation notes` section

It should not assign an AI-likeness score.

## Deterministic activation

Use explicit activation when the workflow needs predictable skill selection, such as support instructions, reproducible evals, or review handoffs.

```text
Use $humanizer to rewrite this:
[paste draft]
```

```text
Use $humanizer-form to humanize the form only:
[paste draft]
```

Avoid relying on automatic skill selection when activation matters. Client auto-selection can vary. This repository's existing live evals force a read of `skills/humanizer/SKILL.md` for positive Humanizer cases because `codex exec` traces do not expose a separate skill-invocation event.
