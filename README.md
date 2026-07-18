# Humanizer Plugin

Humanizer Plugin contains two prose-editing skills with deliberately different
levels of editorial authority:

| Skill | Invocation | Core promise |
|---|---|---|
| **Editorial Humanizer** | `$editorial-humanizer` | Improve the writing with broad editorial judgment while preserving factual integrity |
| **Faithful Humanizer** | `$faithful-humanizer` | Improve only the presentation while preserving every substantive element |

The names describe what each editor is allowed to do:

- **Editorial** means the skill may decide that material is weak, generic,
  repetitive, unsupported, badly structured, or inconsistent with the intended
  voice. It can remove or reshape that material.
- **Faithful** means the supplied text remains authoritative. The skill can improve
  grammar, syntax, punctuation, transitions, repetition, and rhythm, but it cannot
  add, remove, strengthen, weaken, fact-check, neutralize, or reinterpret content.

“Faithful” is more precise than “non-opinionated.” The skill still makes local
copy-editing judgments, but it cannot impose a new position or editorial agenda.

## Choose the correct skill

Use this decision rule:

> Would you accept the editor deleting a weak sentence, changing the structure, or
> sharpening the voice?

- **Yes:** use Editorial Humanizer.
- **No, every supplied idea and qualifier must survive:** use Faithful Humanizer.

### Detailed comparison

| Dimension | Editorial Humanizer | Faithful Humanizer |
|---|---|---|
| Primary goal | Produce stronger, less AI-shaped prose | Produce more natural wording without semantic drift |
| Claims | May remove weak, generic, unsupported, or redundant claims | Must preserve every claim, including weak or unsupported ones |
| Opinions | May sharpen a supplied point of view, but cannot invent an attitude or experience | Must preserve the same opinion, owner, direction, and emotional valence |
| Certainty | Must not invent certainty, but may remove a weak claim entirely | Must preserve `may`, `might`, `will`, `must`, and all other modality exactly in force |
| Attribution | May remove vague attribution or ask for a source | Must preserve vague attribution as vague attribution |
| Structure | May merge, split, reorder, or replace paragraphs, headings, and lists | Preserves section order, paragraph order, examples, and list membership by default |
| Voice | May add stronger human texture or match a supplied voice sample broadly | Matches only compatible surface features; never imports opinions or experiences |
| Promotional language | May neutralize or delete it | Preserves its evaluative force if the author supplied it |
| Fact checking | Does not research by default, but may flag or question unsupported claims | Does not fact-check, correct, challenge, endorse, or rebut |
| Missing evidence | May ask for evidence, generalize, or remove the claim | Keeps the claim and attribution without inventing evidence |
| Detector optimization | Not a goal | Not a goal |
| Audit and score | Supports an 80-point editorial audit | Supports form-change notes only; no AI-likeness score |

## Same source, different result

Source:

```text
Atlas Draft can generate documentation and tests. Industry observers say it helps developers move faster.
```

Editorial Humanizer may return:

```text
Atlas Draft can generate documentation and tests.
```

That is a valid editorial rewrite because it keeps the supported product behavior
and removes an attributed benefit that the source does not establish. It does not
replace the discarded benefit with softer praise or audit commentary.

Faithful Humanizer may return:

```text
Atlas Draft can generate documentation and tests. Industry observers say it helps developers move faster.
```

That version keeps the unnamed observers and attributed benefit because Faithful
Humanizer preserves supplied claims rather than evaluating their support.

A second example:

Source:

```text
The system serves as a robust foundation for scalable workflows, ensuring that cross-functional teams can coordinate effectively.
```

Editorial Humanizer may simplify the claim:

```text
The system supports scalable workflows for cross-functional teams.
```

Faithful Humanizer keeps the supplied evaluative and causal force:

```text
The system is a robust foundation for scalable workflows and ensures that cross-functional teams can coordinate effectively.
```

Neither result is universally better. They answer different editing contracts.

## Editorial Humanizer

Editorial Humanizer is the broader anti-slop editor.

Use it when you want:

- AI-writing patterns removed rather than mechanically preserved;
- weak or generic material cut;
- lists and paragraphs restructured;
- promotional or inflated language reduced;
- a more distinctive point of view;
- voice matching from a writing sample;
- an audit and score of AI-writing patterns.

It protects factual integrity: it must not invent names, figures, dates, studies,
quotes, citations, examples, prices, experiences, benefits, attitudes, or causal
explanations. It must preserve epistemic status and may remove a claim that cannot
be supported or rewrite the surrounding argument more broadly. A rewrite must not
replace discarded claims with audit commentary unless the user requested an audit.

Basic use:

```text
Use $editorial-humanizer to improve this draft. Return only the rewrite:

[paste draft]
```

Audit use:

```text
Use $editorial-humanizer to audit and score this draft for AI-writing patterns.
Put the rewrite first, then concise notes:

[paste draft]
```

## Faithful Humanizer

Faithful Humanizer is the strict form-only editor.

Use it when:

- every claim and opinion must remain;
- legal, scientific, medical, policy, financial, security, or technical qualifiers
  must not drift;
- vague attribution must remain attributed rather than being challenged;
- promotional language belongs to the author's intended message;
- list items, examples, chronology, and argument order must remain;
- you want minimal local edits instead of paragraph regeneration.

It protects:

- every factual and evaluative proposition;
- stance, opinion, and emotional valence;
- modality and certainty;
- negation, exceptions, permissions, prohibitions, and conditions;
- quantifiers and scope;
- causality, comparison, concession, purpose, and sequence;
- attribution and ownership of claims;
- chronology, tense, examples, list membership, and ordering;
- exact names, numbers, dates, units, citations, quotations, URLs, code, identifiers,
  versions, file paths, and domain terminology.

Basic use:

```text
Use $faithful-humanizer. Make this read naturally, but preserve every claim,
opinion, qualifier, example, attribution, and logical relation. Return only the
rewrite:

[paste draft]
```

Stricter use:

```text
Use $faithful-humanizer. Humanize the form only. Do not add, remove, fact-check,
strengthen, soften, summarize, reorganize, or reinterpret any content. Preserve
all names, numbers, dates, quotations, citations, code, modality, negation, scope,
causality, attribution, examples, and list items.

[paste draft]
```

Audit use:

```text
Use $faithful-humanizer to rewrite this and briefly explain only the form changes.
Note any wording deliberately retained to avoid changing the substance:

[paste draft]
```

The audit contains:

1. the rewritten text;
2. `Form changes`;
3. `Preservation notes`.

It does not assign an AI-likeness score.

## Trigger behavior

The two skills intentionally have different trigger contracts.

Editorial Humanizer can be selected for requests such as:

```text
This draft sounds padded and generic. Tighten it and remove the AI-writing patterns.
```

```text
Make this read like a person wrote it and improve the structure.
```

Faithful Humanizer should be selected only when preservation is explicit, for
example:

```text
Humanize the form only. Do not change the substance.
```

```text
Preserve every claim, hedge, attribution, and example.
```

Automatic selection varies by client. Use the client-specific activation form
whenever the distinction matters. See
[`Client-specific activation`](docs/skill-examples.md#client-specific-activation)
for Codex, Claude Code, and OpenCode instructions.

## Installation

### Codex plugin marketplace

Add the repository as a marketplace:

```bash
codex plugin marketplace add CoveMB/humanizer-skill-plugin --ref main
```

Install the plugin:

```bash
codex plugin add humanizer-plugin@humanizer-plugin-local
```

Confirm the installed version:

```bash
codex plugin list
```

Start a new Codex session after installation or upgrade so the skill catalog is
reloaded.

### Upgrade

```bash
codex plugin marketplace upgrade humanizer-plugin-local
codex plugin remove humanizer-plugin@humanizer-plugin-local
codex plugin add humanizer-plugin@humanizer-plugin-local
codex plugin list
```

### Manual skill checkout

The Plain Codex, Claude Code, and OpenCode instructions below copy from a local
repository checkout. Create it first, then run the client-specific commands from
the directory that contains `humanizer-skill-plugin`:

```bash
git clone https://github.com/CoveMB/humanizer-skill-plugin.git
```

### Plain Codex skills

```bash
mkdir -p ~/.agents/skills/editorial-humanizer ~/.agents/skills/faithful-humanizer
cp -R humanizer-skill-plugin/skills/editorial-humanizer/. ~/.agents/skills/editorial-humanizer/
cp -R humanizer-skill-plugin/skills/faithful-humanizer/. ~/.agents/skills/faithful-humanizer/
```

Do not enable the plain skills and plugin copies at the same time. Duplicate copies
can make selection and provenance ambiguous.

### Claude Code

```bash
mkdir -p ~/.claude/skills
cp -R humanizer-skill-plugin/skills/editorial-humanizer ~/.claude/skills/editorial-humanizer
cp -R humanizer-skill-plugin/skills/faithful-humanizer ~/.claude/skills/faithful-humanizer
```

### OpenCode

```bash
mkdir -p ~/.config/opencode/skills
cp -R humanizer-skill-plugin/skills/editorial-humanizer ~/.config/opencode/skills/editorial-humanizer
cp -R humanizer-skill-plugin/skills/faithful-humanizer ~/.config/opencode/skills/faithful-humanizer
```

## Repository layout

```text
.
├── .agents/plugins/marketplace.json
├── .codex-plugin/plugin.json
├── docs/
│   ├── faithful-humanizer-research.md
│   └── skill-examples.md
├── evals/
│   └── humanizer_eval_cases.json
├── scripts/
│   ├── run_humanizer_evals.py
│   └── validate_humanizer_outputs.py
├── skills/
│   ├── editorial-humanizer/
│   │   ├── SKILL.md
│   │   └── references/banned-list.md
│   └── faithful-humanizer/
│       └── SKILL.md
└── tests/
```

The eval runner exercises both Editorial Humanizer and Faithful Humanizer.
Executable Faithful cases check attribution, modality, scope, supplied promotional
claims, opinion, chronology, logical relations, exact anchors, list membership,
and forbidden additions.

## Testing

Run deterministic tests:

```bash
make test
```

Validate the Humanizer eval matrix without invoking a model:

```bash
make eval-humanizer-dry-run
```

Run saved-output validation:

```bash
make validate-humanizer-output OUTPUT_DIR=output-dir
```

Live evals require isolated `HOME` and `CODEX_HOME` directories:

```bash
export HOME="$(mktemp -d)"
export CODEX_HOME="$(mktemp -d)"
python3 scripts/run_humanizer_evals.py --rubric-grade
```

## Research and design rationale

The design review compared public humanizer, de-slop, clarity, and detector-oriented
skills. The main finding was that most implementations mix surface cleanup with
substantive authorship: they add opinions, first person, anecdotes, emotional
reactions, specificity, or personality presets.

Faithful Humanizer separates those tasks. Its design is based on:

1. source authority;
2. explicit semantic invariants;
3. exact-anchor preservation;
4. minimal local edits;
5. a bidirectional semantic diff;
6. restore-on-doubt behavior.

The detailed comparison and rejected design choices are documented in
[`docs/faithful-humanizer-research.md`](docs/faithful-humanizer-research.md).

## Design limits

Neither skill can mathematically guarantee semantic equivalence. Language is
ambiguous, and a model can still make a bad paraphrase.

Faithful Humanizer reduces that risk through minimal edits, explicit invariants,
exact-anchor preservation, and restore-on-doubt rules. High-stakes legal, medical,
scientific, financial, security, or policy text still requires human review.

Neither skill guarantees that an AI detector will classify the output as
human-written. Detector evasion is not the objective.

## License

Original repository code, plugin metadata, tests, repository-authored
documentation, and Faithful Humanizer are released under the MIT License.

Wikipedia-derived material adapted into Editorial Humanizer skill instructions,
reference material, examples, and related plugin documentation remains available
under CC BY-SA 4.0. Attribution and license scope are documented in `NOTICE`.

The plugin therefore reports `MIT AND CC-BY-SA-4.0` at the package level.
