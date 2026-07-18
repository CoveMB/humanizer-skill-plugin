# Humanizer Plugin

Humanizer Plugin contains two prose-editing skills with deliberately different
levels of editorial authority:

| Skill | Invocation | Core promise |
|---|---|---|
| **Editorial Humanizer** | `$editorial-humanizer` | Produce a substantive, voice-oriented editorial rewrite while preserving factual integrity |
| **Faithful Humanizer** | `$faithful-humanizer` | Make the prose materially less formulaic while preserving every substantive element |

The names describe what each editor is allowed to do:

- **Editorial** means the skill may decide that material is weak, generic,
  repetitive, unsupported, badly structured, or inconsistent with the intended
  voice. It can remove or reshape that material.
- **Faithful** means the supplied text remains authoritative. The skill can improve
  grammar, syntax, punctuation, transitions, repetition, and rhythm, but it cannot
  add, remove, strengthen, weaken, fact-check, neutralize, or reinterpret content.

“Faithful” is more precise than “non-opinionated.” The skill still makes local
copy-editing judgments, but it cannot impose a new position or editorial agenda.
It is not a no-op or proofreading-only mode: it rewrites every genuine surface
problem when a semantically equivalent repair exists.

Editorial Humanizer may change selection, structure, emphasis, and rhetorical
presentation. Faithful Humanizer may change only surface form.

## Choose the correct skill

Choose by editorial authority, not by how much rewriting you want. Faithful
Humanizer can make substantial local improvements, and Editorial Humanizer can
leave a sound passage nearly unchanged.

Use this decision rule:

> Would you accept the editor deleting a weak sentence, changing the structure, or
> sharpening the voice?

- **Yes:** use Editorial Humanizer.
- **No, every supplied idea and qualifier must survive:** use Faithful Humanizer.

If the answer is “only in some places,” the request needs explicit permissions.
Name what may change and treat everything else as Faithful. For example: “Preserve
every claim and qualifier, but you may merge the last two paragraphs and remove the
closing call to action.”

### Quick selector

| Your non-negotiable | Use |
|---|---|
| Improve the draft as an editor, including deciding what is weak or unnecessary | Editorial Humanizer |
| Preserve every supplied proposition while making the prose more natural | Faithful Humanizer |
| Remove unsupported benefits, vague authority, hype, or repeated conclusions | Editorial Humanizer |
| Keep approved marketing, legal, policy, or stakeholder language intact in force | Faithful Humanizer |
| Reorganize an argument, headings, paragraphs, or lists | Editorial Humanizer |
| Protect order, list membership, examples, conditions, scope, and attribution | Faithful Humanizer |
| Produce an editorial-quality audit and optional 80-point score | Editorial Humanizer |
| Receive only a form-change explanation and preservation notes | Faithful Humanizer |

### Detailed comparison

| Dimension | Editorial Humanizer | Faithful Humanizer |
|---|---|---|
| Source authority | The source supplies the facts and boundaries, but the editor may decide what belongs in the final draft | The source is authoritative in full; every substantive element must survive |
| Primary goal | Produce stronger, less AI-shaped prose | Produce more natural wording without semantic drift |
| Content selection | May retain, cut, consolidate, or reshape material using editorial judgment | May not add, delete, merge, or replace a claim, reason, example, caveat, or conclusion |
| Claims | May remove weak, generic, unsupported, or redundant claims | Must preserve every claim, including weak or unsupported ones |
| Opinions | May sharpen a supplied point of view, but cannot invent an attitude or experience | Must preserve the same opinion, owner, direction, and emotional valence |
| Certainty | Must not invent certainty, but may remove a weak claim entirely | Must preserve `may`, `might`, `will`, `must`, and all other modality exactly in force |
| Attribution | May remove vague attribution or ask for a source | Must preserve vague attribution as vague attribution |
| Structure | May merge, split, reorder, or replace paragraphs, headings, and lists | Preserves section order, paragraph order, examples, and list membership by default |
| Voice | May add stronger human texture or match a supplied voice sample broadly | Matches only compatible surface features; never imports opinions or experiences |
| Rewrite strength | Uses targeted edits first, but may rebuild structurally weak passages | Makes decisive local rewrites and may recast a whole sentence when its form is the problem |
| Already-natural prose | Preserves it unless a broader structural edit requires a change | Leaves it unchanged |
| Pattern handling | Treats density, repetition, genre, intent, and meaning as evidence | Changes a pattern only when it is locally awkward and an equivalent repair exists |
| Scientific register | May tighten and restructure within scientific evidence boundaries | Preserves terminology, hedging, passive constructions, citation language, and statistical meaning |
| Punctuation | Preserves punctuation suited to the author, genre, locale, and style guide | Treats author-specific punctuation as part of voice |
| Promotional language | May neutralize or delete it | Preserves its evaluative force if the author supplied it |
| Fact checking | Does not research by default, but may flag or question unsupported claims | Does not fact-check, correct, challenge, endorse, or rebut |
| Missing evidence | May ask for evidence, generalize, or remove the claim | Keeps the claim and attribution without inventing evidence |
| High-stakes text | Use only with clear permission for editorial selection and qualified human review | Safer default for form-only editing, still requiring qualified human review |
| Default rewrite output | Rewritten text only | Rewritten text only |
| Detector optimization | Not a goal | Not a goal |
| Audit and score | Supports an 80-point editorial-quality audit; raw diagnostics are advisory | Supports form-change notes only; no AI-likeness score |

### Shared guarantees

Both Humanizers:

- preserve supplied names, numbers, dates, quotations, citations, code,
  identifiers, paths, and technical terms when they remain relevant to the output;
- do not invent facts, sources, examples, metrics, experiences, attitudes,
  benefits, or causal explanations;
- preserve the epistemic status of claims that remain in the output;
- respect genre, register, locale, and a supplied style guide rather than treating
  isolated punctuation or vocabulary as proof of AI authorship;
- prefer targeted edits and leave already-natural prose alone; and
- exclude detector evasion as an objective.

Their common factual-integrity boundary does not make them interchangeable.
Editorial may remove a supplied claim; Faithful may not. Faithful preserves source
content, but it does not verify that the content is true.

### When Editorial Humanizer is ideal

Use Editorial Humanizer for drafts where improving the document matters more than
retaining every sentence. Typical cases include marketing cleanup, executive
summaries, release notes, web copy, repetitive explainers, generic AI drafts,
structurally weak articles, and voice matching where the writer permits broad
editing.

Editorial is also the right choice when you want unsupported benefits, vague
authority, repeated conclusions, ornamental headings, padded lists, or chatbot
framing removed. It may ask for missing evidence during an audit, but a rewrite-only
response removes or generalizes the weak material without inserting audit
commentary into the prose.

### When Faithful Humanizer is ideal

Use Faithful Humanizer when approval, traceability, or semantic precision matters
more than editorial selection. Typical cases include approved marketing or brand
language, legal and policy drafts, scientific and medical prose, financial or
security communication, technical procedures, stakeholder statements, quotations,
regulated content, translations awaiting review, and any text whose claims cannot
be silently dropped.

Faithful is also appropriate when a draft contains a position the editor should not
judge: a disputed claim, first-person reaction, vague attribution, promotional
promise, intentional repetition, or carefully ordered list. It can still repair
formulaic wording decisively, but it must keep the content and force intact.

### Mixed and ambiguous requests

“Preserve the meaning, but improve it editorially” is ambiguous because editorial
improvement may require removing or reorganizing material. Resolve the authority
boundary before rewriting:

1. list the elements that must survive;
2. name the permitted substantive operations, such as deleting one section or
   reordering a list;
3. protect all unmentioned content under the Faithful contract; and
4. request separate fact checking or subject-matter review when needed.

Do not choose Editorial merely because the user asks for a “strong” rewrite. Do not
choose Faithful merely because the user asks to “keep the general meaning.” The
relevant question is whether every substantive element must survive.

## Same source, different result

Source:

```text
Atlas Draft can generate documentation and tests. Industry observers say it helps developers move faster.
```

Editorial Humanizer may return:

```text
Atlas Draft can generate documentation and tests.
```

That is a valid editorial rewrite because it keeps the concrete product behavior
supplied in the source and removes a vaguely attributed benefit. It does not replace
the discarded benefit with softer praise or audit commentary.

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

The full library contains 17 paired cases spanning product copy, vague attribution,
destination copy, executive updates, lists, project updates, release notes,
technical documentation, scientific prose, policy, finance, health communication,
internal voice, customer email, social posts, and fundraising:
[`Paired Humanizer comparison examples`](docs/humanizer-comparison-examples.md).

## Editorial Humanizer

Editorial Humanizer is the broader, voice-oriented editorial rewrite.

Use it when you want:

- AI-writing patterns removed rather than mechanically preserved;
- weak or generic material cut;
- lists and paragraphs restructured;
- promotional or inflated language reduced;
- a more distinctive point of view;
- voice matching from a writing sample;
- an editorial-quality audit with contextual pattern evidence.

It protects factual integrity: it must not invent names, figures, dates, studies,
quotes, citations, examples, prices, experiences, benefits, attitudes, or causal
explanations. It must preserve epistemic status and may remove a claim that cannot
be supported or rewrite the surrounding argument more broadly. A rewrite must not
replace discarded claims with audit commentary unless the user requested an audit.
It starts with targeted edits and broadens the rewrite only when structure, argument
flow, or repeated patterns cannot be repaired locally.

Pattern matches are signals, not proof of authorship or automatic edit commands.
One em dash, semicolon, three-item list, passive sentence, use of `important`,
title-case heading, or curly quotation mark does not require revision. The skill
considers density, repetition, genre, register, intent, and whether the change
actually improves the passage.

Basic use:

```text
Use $editorial-humanizer to improve this draft. Return only the rewrite:

[paste draft]
```

Audit use:

```text
Use $editorial-humanizer to audit and score this draft's editorial quality.
Put the rewrite first, then concise notes:

[paste draft]
```

## Faithful Humanizer

Faithful Humanizer is the strict form-only editor. Strict preservation does not mean
timid editing: it removes fixable AI-shaped surface form and should return prose that
is materially less formulaic, not merely proofread.

Use it when:

- every claim and opinion must remain;
- legal, scientific, medical, policy, financial, security, or technical qualifiers
  must not drift;
- vague attribution must remain attributed rather than being challenged;
- promotional language belongs to the author's intended message;
- list items, examples, chronology, and argument order must remain;
- you want decisive local edits instead of unnecessary paragraph regeneration.

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

### Scientific and academic writing

Both skills use a shared scientific-register reference, but with different
authority. Faithful treats terminology, passive voice, hedging, citations,
statistical meaning, and repeated exact terms as preservation constraints.
Editorial may remove formulaic padding or improve argument flow, but it must keep
epistemic caution, evidence boundaries, attribution, definitions, and causal
strength intact.

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
mkdir -p ~/.agents/skills/editorial-humanizer ~/.agents/skills/faithful-humanizer ~/.agents/skills/references
cp -R humanizer-skill-plugin/skills/editorial-humanizer/. ~/.agents/skills/editorial-humanizer/
cp -R humanizer-skill-plugin/skills/faithful-humanizer/. ~/.agents/skills/faithful-humanizer/
cp -R humanizer-skill-plugin/skills/references/. ~/.agents/skills/references/
```

Do not enable the plain skills and plugin copies at the same time. Duplicate copies
can make selection and provenance ambiguous.

### Claude Code

```bash
mkdir -p ~/.claude/skills/references
cp -R humanizer-skill-plugin/skills/editorial-humanizer ~/.claude/skills/editorial-humanizer
cp -R humanizer-skill-plugin/skills/faithful-humanizer ~/.claude/skills/faithful-humanizer
cp -R humanizer-skill-plugin/skills/references/. ~/.claude/skills/references/
```

### OpenCode

```bash
mkdir -p ~/.config/opencode/skills/references
cp -R humanizer-skill-plugin/skills/editorial-humanizer ~/.config/opencode/skills/editorial-humanizer
cp -R humanizer-skill-plugin/skills/faithful-humanizer ~/.config/opencode/skills/faithful-humanizer
cp -R humanizer-skill-plugin/skills/references/. ~/.config/opencode/skills/references/
```

## Repository layout

```text
.
├── .agents/plugins/marketplace.json
├── .codex-plugin/plugin.json
├── docs/
│   ├── faithful-humanizer-research.md
│   ├── humanizer-comparison-examples.md
│   └── skill-examples.md
├── evals/
│   └── humanizer_eval_cases.json
├── scripts/
│   ├── run_humanizer_evals.py
│   ├── editorial_diagnostics.py
│   └── validate_humanizer_outputs.py
├── skills/
│   ├── editorial-humanizer/
│   │   ├── SKILL.md
│   │   └── references/pattern-catalog.md
│   ├── faithful-humanizer/
│   │   └── SKILL.md
│   └── references/registers/scientific-writing.md
└── tests/
```

The eval runner exercises both Editorial Humanizer and Faithful Humanizer.
Executable Faithful cases check attribution, modality, scope, supplied promotional
claims, opinion, chronology, logical relations, exact anchors, list membership,
scientific register, meaningful surface rewriting, already-natural restraint,
localized mixed-text edits, audit output, voice matching, protected structure, and
forbidden additions. Separate unforced probes verify automatic selection and the
boundary with Editorial Humanizer and detector-evasion requests.
Its dedicated live rubric requires both semantic fidelity and a clearly more
natural surface rewrite, so cosmetic changes do not satisfy the Faithful contract.
Editorial eval summaries also record deterministic pattern diagnostics as advisory
evidence; those observations do not determine pass/fail or authorship.

## Testing

Run deterministic tests:

```bash
make test
```

Install the development-only coverage dependency and run the branch-coverage gate:

```bash
python3 -m pip install -r requirements-dev.txt
make coverage
```

Validate the Humanizer eval matrix without invoking a model:

```bash
make eval-humanizer-dry-run
```

Preview only Faithful cases across three trials:

```bash
make eval-humanizer-dry-run EVAL_ARGS='--target-skill faithful-humanizer --trials 3 --rubric-grade --rubric-model gpt-5.5'
```

Run saved-output validation:

```bash
make validate-humanizer-output OUTPUT_DIR=output-dir
```

Live evals require isolated home and Codex directories:

```bash
eval_home_dir="$(mktemp -d)"
eval_codex_dir="$(mktemp -d)"
env HOME="$eval_home_dir" CODEX_HOME="$eval_codex_dir" \
  python3 scripts/run_humanizer_evals.py \
  --target-skill faithful-humanizer --trials 3 --rubric-grade
```

Summaries include per-skill pass rates, minimum rubric dimension scores, trial
numbers, models, and failure stages. Existing one-trial commands and case filters
remain supported.

## Research and design rationale

The design review compared public humanizer, de-slop, clarity, and detector-oriented
skills. The main finding was that most implementations mix surface cleanup with
substantive authorship: they add opinions, first person, anecdotes, emotional
reactions, specificity, or personality presets.

Faithful Humanizer separates those tasks. Its design is based on:

1. source authority;
2. explicit semantic invariants;
3. exact-anchor preservation;
4. decisive local edits;
5. a bidirectional semantic diff;
6. restore-on-doubt behavior.

The detailed comparison and rejected design choices are documented in
[`docs/faithful-humanizer-research.md`](docs/faithful-humanizer-research.md).

## Design limits

Neither skill can mathematically guarantee semantic equivalence. Language is
ambiguous, and a model can still make a bad paraphrase.

Faithful Humanizer reduces that risk through localized edits, explicit invariants,
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
