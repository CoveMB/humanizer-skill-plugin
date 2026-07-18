# Skill examples

This repository ships two related but intentionally different skills:

- **Editorial Humanizer** (`editorial-humanizer`) applies broad, voice-oriented
  editorial judgment.
- **Faithful Humanizer** (`faithful-humanizer`) makes decisive surface rewrites
  while preserving substance.

Editorial Humanizer may change selection, structure, emphasis, and rhetorical
presentation. Faithful Humanizer may change only surface form.

Use the explicit invocation whenever the distinction matters.

For side-by-side outputs from the same source across 17 genres and editing cases,
see [`Paired Humanizer comparison examples`](humanizer-comparison-examples.md).

## Choosing a skill

| Need | Skill |
|---|---|
| Remove AI-writing patterns and improve the draft editorially | Editorial Humanizer |
| Keep every claim and qualifier while improving presentation | Faithful Humanizer |
| Delete weak, generic, repetitive, or unsupported material | Editorial Humanizer |
| Preserve vague, promotional, disputed, or unsupported claims | Faithful Humanizer |
| Restructure paragraphs, headings, or lists | Editorial Humanizer |
| Preserve section order, examples, and list membership | Faithful Humanizer |
| Match a writing sample broadly and allow stronger voice | Editorial Humanizer |
| Match only compatible surface features from a sample | Faithful Humanizer |
| Audit editorial quality and receive an 80-point score | Editorial Humanizer |
| Receive only form-change and preservation notes | Faithful Humanizer |
| Tighten scientific prose within evidence boundaries | Editorial Humanizer |
| Preserve scientific terminology, hedging, passive voice, and citations | Faithful Humanizer |

## Editorial Humanizer

Editorial Humanizer is the broader anti-slop editor. It protects factual integrity,
but it may change editorial substance by removing weak material, challenging vague
attribution, restructuring the draft, or sharpening the voice.
It prefers targeted edits when the passage is sound and broadens the rewrite only
when local repair cannot fix a structural problem.

### Basic rewrite

```text
Use $editorial-humanizer to improve this draft. Return only the rewritten text:

AI-assisted coding serves as a pivotal moment in the evolution of software
development, unlocking productivity, creativity, and alignment across
cross-functional teams.
```

The skill should:

- remove inflated phrasing such as `pivotal moment` and `unlocking`;
- preserve supplied anchor terms when they still define the subject and scope;
- avoid inventing claims about speed, quality, adoption, or business value;
- remove generic filler when it adds no supported content.

### Documentation cleanup

```text
Use $editorial-humanizer on this documentation paragraph. Keep factual integrity,
but improve it editorially:

This configuration serves as a robust foundation for scalable workflows, ensuring
developers can seamlessly optimize productivity and foster alignment across teams.
```

Editorial Humanizer may return:

```text
This configuration supports scalable workflows for development teams.
```

It may remove `robust`, `seamlessly`, `productivity`, and `alignment` because the
editorial contract permits cutting generic or inflated material.

### Voice calibration

```text
Use $editorial-humanizer to rewrite the draft. Match the style of this sample.

Writing sample:
I prefer short release notes. Name the change, explain the risk, and stop. If
something is uncertain, say exactly what remains unknown.

Draft:
This release introduces a comprehensive enhancement to the validation pipeline,
highlighting our commitment to robust developer experiences and setting the stage
for future improvements.
```

The skill should match the sample's directness, sentence length, punctuation, and
tolerance for uncertainty without importing facts from the sample.

### Audit and score

```text
Use $editorial-humanizer to audit and score this draft's editorial quality:

Our platform is more than just a tool; it is a testament to innovation, empowering
teams to collaborate, create, and scale like never before.
```

The response should:

1. put the rewrite first;
2. add concise notes tied to actual changes;
3. use `Score: NN/80`;
4. avoid a ten-point or percentage output score.

Counts and distributions may support the audit, but they are advisory. They must
not become an AI-authorship verdict or mechanically determine the score.

### Contextual false positives

```text
Use $editorial-humanizer only where needed. Preserve legitimate scientific
punctuation and register:

The primary endpoint was time to recovery—specified before enrollment. This detail
was important because the protocol required blood pressure, heart rate, and oxygen
saturation.
```

The single em dash, passive construction, `important`, and concrete three-item list
are not automatic problems. The skill should preserve them unless the surrounding
context or a supplied style guide gives a real reason to change them.

### Missing evidence

```text
Use $editorial-humanizer. If a sentence needs unavailable evidence to become
specific, ask instead of inventing:

Industry reports show that Atlas Note adoption increased significantly last
quarter, proving the product is transforming team knowledge management.
```

Editorial Humanizer may ask for the reports, keep the statement general, or remove
the unsupported claim. It must not invent a source, percentage, or citation.

## Faithful Humanizer

Faithful Humanizer treats the source as authoritative. It may improve grammar,
syntax, repetition, punctuation, transitions, and rhythm, but it cannot decide that
a supplied idea is weak or unnecessary. This does not make it timid: it should
rewrite every genuine surface problem when a semantically equivalent repair exists.

### Basic faithful rewrite

```text
Use $faithful-humanizer. Make the wording read naturally, but preserve every claim,
opinion, qualifier, example, attribution, and logical relation. Return only the
rewrite.

Additionally, it is important to note that the platform may potentially reduce
setup time for some teams.
```

Expected rewrite:

```text
Importantly, the platform may reduce setup time for some teams.
```

The rewrite preserves:

- the importance claim;
- uncertainty through `may`;
- scope through `some teams`.

### Meaningful local rewrite

```text
Use $faithful-humanizer. Make this substantially less formulaic without changing
any proposition, hedge, qualifier, or relation:

At this point in time, the committee is in the process of conducting an evaluation
of the proposal, and it may potentially recommend revisions for some sections.
```

Expected rewrite:

```text
The committee is currently evaluating the proposal and may recommend revisions for
some sections.
```

Faithful minimality is localized, not cosmetic. The sentence receives a real
rewrite while the actor, action, proposal, uncertainty, possible recommendation,
and scope remain intact.

### Scientific register preservation

```text
Use $faithful-humanizer. Preserve the terminology, passive construction, citation,
uncertainty, negation, and causal meaning:

It is important to note that, in Smith et al. (2024), the weighted interval score
was measured for each model. The weighted interval score may be associated with
forecast calibration, but the study did not establish causality.
```

The skill may remove `It is important to note that`, but it must retain both uses of
`weighted interval score`, the passive measurement, `may be associated with`, the
citation, and `did not establish causality`.

### Preserve vague attribution

```text
Use $faithful-humanizer. Do not fact-check, challenge, or delete any claim:

Industry reports suggest adoption is accelerating, highlighting the platform's
growing relevance.
```

Expected rewrite:

```text
Industry reports suggest that adoption is accelerating, a trend that highlights
the platform's growing relevance.
```

Faithful Humanizer must not invent a report, remove the attribution, or neutralize
the relevance claim.

### Preserve promotional force

```text
Use $faithful-humanizer on this documentation sentence:

The system serves as a robust foundation for scalable workflows, ensuring that
cross-functional teams can coordinate effectively.
```

Expected rewrite:

```text
The system is a robust foundation for scalable workflows and ensures that
cross-functional teams can coordinate effectively.
```

The words `robust`, `scalable workflows`, `cross-functional teams`, and the force of
`ensures` remain because they belong to the supplied content.

### Preserve opinion, order, and uncertainty

```text
Use $faithful-humanizer. Humanize the form only:

I find the change unsettling. It may, however, improve efficiency.
```

Expected rewrite:

```text
I find the change unsettling, although it may improve efficiency.
```

The output preserves the speaker's feeling, the order of the claims, the concessive
relationship, and the uncertain benefit.

### Preserve attribution, hedge, and scope

Source:

```text
Experts believe the policy may improve outcomes for some patients.
```

Faithful Humanizer must not return:

```text
The policy improves outcomes for patients.
```

That transformation removes the attribution, strengthens `may`, and widens `some
patients` to all patients.

### Faithful audit

```text
Use $faithful-humanizer to rewrite this and explain only the form changes. Note any
wording deliberately retained to protect the substance:

[paste draft]
```

The response should contain:

1. the rewritten text;
2. `Form changes`;
3. `Preservation notes`.

It should not assign an AI-likeness score.

## Same source, different contracts

Source:

```text
The company launched Atlas 2.0 on May 6. The launch marks a pivotal moment for the
company and may help some teams work more efficiently, according to industry
observers.
```

Editorial Humanizer may return:

```text
The company launched Atlas 2.0 on May 6.
```

Faithful Humanizer may return:

```text
The company launched Atlas 2.0 on May 6. According to industry observers, the
launch marks a pivotal moment for the company and may help some teams work more
efficiently.
```

The Editorial version keeps the supplied release fact and removes significance
inflation and the weakly sourced benefit without adding audit commentary to the
rewrite. The Faithful version preserves the release fact, significance claim,
attribution, hedge, and scope.

## Client-specific activation

Activation syntax depends on the client. Use the exact skill name for support
instructions, reproducible evals, review handoffs, and high-stakes preservation
requirements.

### Codex

Codex accepts the `$skill-name` form:

```text
Use $editorial-humanizer to rewrite this:
[paste draft]
```

```text
Use $faithful-humanizer to humanize the form only:
[paste draft]
```

### Claude Code

Claude Code exposes installed skills as slash commands:

```text
/editorial-humanizer Rewrite this:
[paste draft]
```

```text
/faithful-humanizer Humanize the form only:
[paste draft]
```

### OpenCode

OpenCode agents discover installed skills and load the selected instructions with
the native `skill` tool. Ask the agent to load the exact skill name before giving
the editing request:

```text
Load `faithful-humanizer` with the skill tool, then humanize the form only:
[paste draft]
```

This repository does not define a direct OpenCode invocation command. For a
reproducible check, inspect the session trace and confirm that the `skill` tool
loaded the selected skill's `SKILL.md`.

Do not rely on automatic skill selection when choosing the wrong editing contract
could change the content.
