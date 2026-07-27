# Humanizer Plugin

Humanizer Plugin contains three prose-editing skills and exposes five user-facing
behaviors:

| Behavior | Invocation | Core promise |
|---|---|---|
| **Editorial Humanizer** | `$editorial-humanizer` | Produce a substantive, voice-oriented editorial rewrite while preserving factual integrity |
| **Faithful Humanizer — Structural** (default) | `$faithful-humanizer` or an explicit Structural request | Reconstruct sentence and paragraph form while preserving every substantive element |
| **Faithful Humanizer — Conservative** (opt-in) | `$faithful-humanizer` with `Conservative`, `minimal`, `light touch`, `stay close`, or equivalent language | Make the smallest useful localized form edits under the same preservation contract |
| **Plain Language Humanizer — Rewrite** (default) | `$plain-language-humanizer` or an explicit Rewrite request | Produce replacement technical text for an informed non-specialist while preserving substantive content and protected literals |
| **Plain Language Humanizer — Explain** (opt-in) | `$plain-language-humanizer` with an explicit Explain request | Explain supplied technical content concisely for an informed non-specialist |

The names describe what each editor is allowed to do:

- **Editorial** means the skill may decide that material is weak, generic,
  repetitive, unsupported, badly structured, or inconsistent with the intended
  voice. It can remove or reshape that material.
- **Faithful** means the supplied text remains authoritative. Both modes can improve
  grammar, syntax, punctuation, transitions, repetition, and rhythm, but neither can
  add, remove, strengthen, weaken, fact-check, neutralize, or reinterpret content.
- **Plain Language** means the technical content remains authoritative while its
  presentation is adapted for a less technical audience. It preserves every
  substantive element and exact technical literal, while allowing only the brief
  definitions and explanations needed for comprehension.

“Faithful” is more precise than “non-opinionated.” The skill still makes form
judgments, but it cannot impose a new position or editorial agenda. Structural is
the default and can rebuild form; Conservative preserves the current local-first
behavior. Neither is a no-op or proofreading-only mode.

Editorial Humanizer may change content selection, argument architecture, emphasis,
and rhetorical presentation. Faithful Humanizer may change only form. Plain
Language Humanizer adapts the audience and may add tightly bounded explanation, but
it does not authorize substantive selection. Structural may change grammatical
subjects, sentence boundaries, local clause order, cohesion, and non-meaningful
paragraph boundaries without changing semantic invariants.

## Choose the correct skill

Choose the skill first by the real goal: editorial authority, strict form-only
preservation, or audience adaptation. Then choose the mode. Faithful Structural
can make substantial formal changes, Faithful Conservative stays local, Editorial
may leave a sound passage nearly unchanged, and Plain Language Rewrite is the
default when its mode is not named.

Use these decision rules:

> Does supplied technical content need to be rewritten or explained for a less
> technical reader?

- **Yes:** use Plain Language Humanizer. Use Rewrite for replacement copy and
  Explain when the user wants an explanation rather than replacement copy.
- **No:** decide between Editorial and Faithful by authority:

> Would you accept the editor deleting a weak sentence, changing the structure, or
> sharpening the voice?

- **Yes:** use Editorial Humanizer.
- **No, every supplied idea and qualifier must survive:** use Faithful Humanizer.
  Use Structural unless you explicitly want Conservative intervention.

If the answer is “only in some places,” the request needs explicit permissions.
Name what may change and treat everything else as Faithful. For example: “Preserve
every claim and qualifier, but you may merge the last two paragraphs and remove the
closing call to action.”

### Quick selector

| Your non-negotiable | Use |
|---|---|
| Improve the draft as an editor, including deciding what is weak or unnecessary | Editorial Humanizer |
| Preserve every supplied proposition and rebuild formulaic sentence or paragraph form | Faithful Structural |
| Preserve every supplied proposition with minimal, stay-close edits | Faithful Conservative |
| Remove unsupported benefits, vague authority, hype, or repeated conclusions | Editorial Humanizer |
| Keep approved marketing, legal, policy, or stakeholder language intact in force | Either Faithful mode |
| Rewrite supplied technical content for an informed non-specialist | Plain Language Rewrite |
| Explain what supplied technical content means without replacing it | Plain Language Explain |
| Reorganize an argument, headings, paragraphs, or lists | Editorial Humanizer |
| Protect meaningful order, list membership, examples, conditions, scope, and attribution | Either Faithful mode |
| Produce an editorial-quality audit and optional 80-point score | Editorial Humanizer |
| Receive only a form-change explanation and preservation notes | Either Faithful mode |

### Detailed comparison

| Dimension | Editorial Humanizer | Faithful Structural | Faithful Conservative | Plain Language Rewrite | Plain Language Explain |
|---|---|---|---|---|---|
| Source authority | Editor may decide what belongs, within factual-integrity limits | Source is authoritative in full | Same as Structural | Source is authoritative in full; conventional definitions may be added | Same as Rewrite |
| Content selection | May cut, consolidate, or reshape material | Every proposition, reason, example, caveat, and conclusion survives | Same as Structural | Every substantive technical element survives | Explains every material element concisely |
| Semantic invariants | Preserves facts and epistemic status that remain | Preserves propositions, stance, attribution, modality, scope, chronology, logic, comparisons, exact anchors, register, and meaningful order | Same as Structural | Preserves substantive content, relationships, operational order, and protected literals | Same as Rewrite |
| Form strategy | May alter content selection, argument architecture, emphasis, and voice | Reconstructs sentence and non-meaningful paragraph form from a semantic ledger | Makes the smallest useful localized edit | Produces audience-adapted replacement copy | Produces a concise explanation, not replacement copy |
| Already-natural prose | Preserves it unless an authorized broader edit requires change | Leaves it unchanged | Leaves it unchanged | Leaves it unchanged when comprehension does not benefit | Explains only what needs explanation |
| Scientific register | May tighten and restructure within evidence boundaries | Preservation checks become stricter; the mode does not change silently | Same as Structural | Defines necessary terms without weakening evidence boundaries | Same as Rewrite, with extra caution for explanations |
| Default | Separate skill | Default Faithful mode | Opt-in only | Default Plain Language mode | Opt-in only |
| Audit and score | Optional 80-point editorial-quality audit | `Form changes:` and `Preservation notes:` only; no AI-likeness score | Same as Structural | Rewrite only unless combined output is requested | Explanation only |
| Detector optimization | Not a goal | Forbidden | Forbidden | Forbidden | Forbidden |

### Shared guarantees

All three Humanizers:

- preserve supplied names, numbers, dates, quotations, citations, code,
  identifiers, paths, and technical terms when they remain relevant to the output;
- do not present invented facts, sources, source examples, metrics, experiences,
  attitudes, benefits, or causal explanations as source content; Plain Language
  Explain may add only a bounded, labeled explanatory device under its rules;
- preserve the epistemic status of claims that remain in the output;
- respect genre, register, locale, and a supplied style guide rather than treating
  isolated punctuation or vocabulary as proof of AI authorship;
- leave already-natural prose alone and use the requested intervention strategy; and
- exclude detector evasion as an objective.

Their common factual-integrity boundary does not make them interchangeable.
Editorial may remove a supplied claim; Faithful and Plain Language may not.
Faithful permits no explanatory addition, while Plain Language may add only the
definitions and explanation required for comprehension. Neither preservation
contract verifies that the source content is true.

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

Choose **Structural** when sentence or paragraph form is the problem: repetitive
transition-led sequencing, overloaded sentences, templated subjects, or weak
information flow. It is the default when a Faithful request does not specify an
intensity.

Choose **Conservative** when the user asks for minimal edits, a light touch,
copyediting only, wording that stays close, or preservation of existing sentence
or paragraph structure. Preserving all claims does not automatically select
Conservative. High-stakes or scientific register strengthens the preservation
check but does not silently change the requested mode.

### When Plain Language Humanizer is ideal

Use Plain Language Humanizer when supplied technical content is accurate for its
purpose but the intended reader lacks domain expertise. Typical cases include API
behavior, webhooks, procedures, scientific findings, security notices, and other
technical instructions that need plain language without losing conditions,
warnings, operational order, or exact literals.

Choose **Rewrite** for replacement copy. Rewrite is the default. Choose **Explain**
when the reader needs a concise explanation of the supplied content rather than a
replacement passage. A request for both produces the rewrite first and then a short
`Explanation:` section.

Explain mode may use a brief example or analogy when the user asks for one or when
it is materially needed. It labels the device, states its limits, and must not add
source-specific behavior, guarantees, numbers, consequences, or advice. High-stakes
content requires extra caution, and every addition must be necessary for
comprehension.

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

## Same source, four results

Source:

```text
Atlas Notes provides offline access to saved documents, which enables travelers to review project files without an internet connection, while also allowing administrators to revoke access after a device has been lost, thereby helping organizations balance convenience with security.
```

Editorial Humanizer may return:

```text
Atlas Notes keeps saved documents available offline. Administrators can revoke access after a device is lost.
```

That is a valid Editorial rewrite only when the editor has permission to prioritize
the two concrete controls and omit the traveler use case and balancing claim.

Faithful Structural may return:

```text
Saved documents remain available offline in Atlas Notes, so travelers can review project files without an internet connection. If a device is lost, administrators can revoke its access. Together, these features help organizations balance convenience with security.
```

Faithful Conservative may return:

```text
Atlas Notes provides offline access to saved documents, so travelers can review project files without an internet connection. At the same time, it allows administrators to revoke access after a device has been lost, helping organizations balance convenience with security.
```

Plain Language Rewrite may return:

```text
Atlas Notes lets people open saved documents without an internet connection. This allows travelers to review project files while offline. If a device is lost, administrators can remove its access. These features help organizations balance convenience with security.
```

The Faithful and Plain Language outputs retain the same propositions and scope.
Structural rebuilds the sentence architecture; Conservative repairs it locally;
Plain Language adapts the technical presentation for its default informed
non-specialist audience. None of them narrows offline access to travelers:
travelers are one use case for a generally available feature.

Explain is not replacement copy, so it is not a fifth result in this comparison.
See the linked [Plain Language Explain examples](docs/skill-examples.md#explain-a-webhook)
for that output contract.

The existing comparison library applies the three Editorial and Faithful behaviors
to 12 same-source passages
spanning opinion, academic/scientific, product, community, policy, medical,
financial, cybersecurity, technical procedure, customer support, fundraising, and
workplace contexts:
[`Three-behavior Humanizer comparison examples`](docs/humanizer-comparison-examples.md).

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
is materially less formulaic, not merely proofread. It has a default Structural
mode and an opt-in Conservative mode.

Use it when:

- every claim and opinion must remain;
- legal, scientific, medical, policy, financial, security, or technical qualifiers
  must not drift;
- vague attribution must remain attributed rather than being challenged;
- promotional language belongs to the author's intended message;
- list items, examples, chronology, and meaningful argument order must remain; or
- you want form reconstruction or local copyediting without substantive selection.

It protects:

- every factual and evaluative proposition;
- stance, opinion, and emotional valence;
- modality and certainty;
- negation, exceptions, permissions, prohibitions, and conditions;
- quantifiers and scope;
- causality, comparison, concession, purpose, and sequence;
- attribution and ownership of claims;
- chronology, tense, comparisons, examples, list membership, meaningful ordering,
  and register constraints;
- exact names, numbers, dates, units, citations, quotations, URLs, code, identifiers,
  versions, file paths, and domain terminology.

Default Structural use:

```text
Use $faithful-humanizer. Make this read naturally, but preserve every claim,
opinion, qualifier, example, attribution, and logical relation. Return only the
rewrite:

[paste draft]
```

Explicit Structural use:

```text
Use $faithful-humanizer in Structural mode. Rebuild the sentence structure and make
the passage less templated. Preserve every proposition, opinion owner, hedge,
scope boundary, chronology, causal or logical relation, comparison, exact anchor,
and meaningful part of the argument order.

[paste draft]
```

Explicit Conservative use:

```text
Use $faithful-humanizer in Conservative mode. Give this a minimal, light-touch
edit. Stay close to the existing subjects, sentence boundaries, paragraph
architecture, and order. Preserve every claim, qualifier, attribution, example,
and logical relation.

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
2. `Form changes:`;
3. `Preservation notes:`.

It does not assign an AI-likeness score.

## Plain Language Humanizer

Plain Language Humanizer adapts supplied technical content for a less technical
audience while preserving technical meaning and operational safety. Its default
audience is an informed non-specialist. It replaces unnecessary jargon with precise
everyday language, briefly defines necessary technical terms, and keeps protected
literals such as code, commands, flags, identifiers, API names, error messages,
URLs, paths, versions, citations, formulas, and units exact.

Rewrite use:

```text
Use $plain-language-humanizer in Rewrite mode. Adapt this technical content for an informed non-specialist. Return only the rewrite:
[paste source]
```

Explain use:

```text
Use $plain-language-humanizer in Explain mode. Explain this supplied technical content concisely for an informed non-specialist:
[paste source]
```

Combined use:

```text
Use $plain-language-humanizer to rewrite this and then explain it briefly. Put the rewrite first, followed by Explanation:
[paste source]
```

An explicit mode always wins. Rewrite is the default when no mode is named.
Explain returns an explanation rather than replacement copy. A combined request is
not a third mode: it returns the rewrite followed by a short section labeled
exactly `Explanation:`.

### Scientific and academic writing

All three skills use a shared scientific-register reference, but with different
authority. Faithful treats terminology, passive voice, hedging, citations,
statistical meaning, and repeated exact terms as preservation constraints.
Editorial may remove formulaic padding or improve argument flow, but it must keep
epistemic caution, evidence boundaries, attribution, definitions, and causal
strength intact. Plain Language retains precise scientific terms when substitution
would change meaning, defines them briefly, and preserves statistics, uncertainty,
evidence boundaries, and causal strength.

## Trigger behavior

The three skills intentionally have different trigger contracts.

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

Plain Language Humanizer should be selected for audience adaptation of supplied
technical content, for example:

```text
Rewrite this API documentation in plain language for a nontechnical reader.
```

```text
Explain what this supplied webhook behavior means for an informed non-specialist.
```

Within Faithful, routing is deterministic:

- an explicitly named mode always wins;
- `Structural`, `rework/rebuild the sentence structure`, `less formulaic`, `less
  templated`, and equivalent language select Structural;
- `Conservative`, `minimal`, `light touch`, `stay close`, `copyedit only`, and
  preserving existing sentence or paragraph structure select Conservative;
- a Faithful request without an intensity selects Structural;
- preserving all claims does not automatically select Conservative; and
- high-stakes or scientific register strengthens preservation checks without
  silently changing the mode.

Within Plain Language, an explicit mode wins; rewrite, simplify, reduce-jargon, and
nontechnical-reader requests select Rewrite; explanation or walkthrough requests
select Explain; and no named mode selects Rewrite. An explicit request for both
operations produces combined output.

If the requested rewrite conflicts with a preservation contract, state the
boundary or use Editorial only when the user authorizes substantive selection,
compression, reprioritization, or argument restructuring. Detector-evasion requests
are rejected or reframed as ordinary writing-quality work; none of the skills
optimizes for detector outcomes.

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
mkdir -p \
  ~/.agents/skills/editorial-humanizer \
  ~/.agents/skills/faithful-humanizer \
  ~/.agents/skills/plain-language-humanizer \
  ~/.agents/skills/references
cp -R humanizer-skill-plugin/skills/editorial-humanizer/. ~/.agents/skills/editorial-humanizer/
cp -R humanizer-skill-plugin/skills/faithful-humanizer/. ~/.agents/skills/faithful-humanizer/
cp -R humanizer-skill-plugin/skills/plain-language-humanizer/. ~/.agents/skills/plain-language-humanizer/
cp -R humanizer-skill-plugin/skills/references/. ~/.agents/skills/references/
```

Do not enable the plain skills and plugin copies at the same time. Duplicate copies
can make selection and provenance ambiguous.

### Claude Code

```bash
mkdir -p \
  ~/.claude/skills/editorial-humanizer \
  ~/.claude/skills/faithful-humanizer \
  ~/.claude/skills/plain-language-humanizer \
  ~/.claude/skills/references
cp -R humanizer-skill-plugin/skills/editorial-humanizer/. ~/.claude/skills/editorial-humanizer/
cp -R humanizer-skill-plugin/skills/faithful-humanizer/. ~/.claude/skills/faithful-humanizer/
cp -R humanizer-skill-plugin/skills/plain-language-humanizer/. ~/.claude/skills/plain-language-humanizer/
cp -R humanizer-skill-plugin/skills/references/. ~/.claude/skills/references/
```

### OpenCode

```bash
mkdir -p \
  ~/.config/opencode/skills/editorial-humanizer \
  ~/.config/opencode/skills/faithful-humanizer \
  ~/.config/opencode/skills/plain-language-humanizer \
  ~/.config/opencode/skills/references
cp -R humanizer-skill-plugin/skills/editorial-humanizer/. ~/.config/opencode/skills/editorial-humanizer/
cp -R humanizer-skill-plugin/skills/faithful-humanizer/. ~/.config/opencode/skills/faithful-humanizer/
cp -R humanizer-skill-plugin/skills/plain-language-humanizer/. ~/.config/opencode/skills/plain-language-humanizer/
cp -R humanizer-skill-plugin/skills/references/. ~/.config/opencode/skills/references/
```

After a manual install or update, start a new client session so its skill catalog
reloads the copied files.

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
│   ├── plain-language-humanizer/
│   │   └── SKILL.md
│   └── references/registers/scientific-writing.md
└── tests/
```

The eval runner exercises Editorial Humanizer, both Faithful modes, and both Plain
Language modes. Executable
Faithful cases share checks for attribution, modality, scope, supplied promotional
claims, opinion, chronology, logical relations, comparisons, exact anchors, list
membership, scientific register, audit output, and forbidden additions. Structural
cases require meaning-driven reconstruction where local substitutions are
insufficient and reject unnecessary changes to already-natural prose. Conservative
cases preserve localized intervention and reject unnecessarily broad rewriting. An
explicit unforced catalog probe verifies named-skill
behavior, while plugin provenance verifies that the installed Faithful skill is
present in the model-visible catalog. Neutral implicit and contextual probes verify
faithful output behavior without assuming that every client exposes automatic or
client-managed skill-loading traces. Additional probes cover the boundary with
Editorial Humanizer and detector-evasion requests.
Its dedicated live rubric keeps semantic fidelity at a minimum 9/10 and adds either
`structural_initiative` or `conservative_restraint`; the two strategies are not
averaged into one intervention score.
Editorial eval summaries also record deterministic pattern diagnostics as advisory
evidence; those observations do not determine pass/fail or authorship.
Plain Language cases cover API and webhook behavior, protected procedures,
scientific and high-stakes boundaries, already-clear text, mode routing, and
anti-bloat constraints.

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

Preview only Faithful Structural cases across three trials:

```bash
make eval-humanizer-dry-run EVAL_ARGS='--target-skill faithful-humanizer --faithful-mode structural --trials 3 --rubric-grade --rubric-model gpt-5.5'
```

Preview only Faithful Conservative cases across three trials:

```bash
make eval-humanizer-dry-run EVAL_ARGS='--target-skill faithful-humanizer --faithful-mode conservative --trials 3 --rubric-grade --rubric-model gpt-5.5'
```

Preview only Plain Language Rewrite cases:

```bash
make eval-humanizer-dry-run EVAL_ARGS='--target-skill plain-language-humanizer --plain-language-mode rewrite'
```

Preview only Plain Language Explain cases:

```bash
make eval-humanizer-dry-run EVAL_ARGS='--target-skill plain-language-humanizer --plain-language-mode explain'
```

Validate the seeded rubric-calibration matrix without invoking a model:

```bash
make eval-humanizer-dry-run EVAL_ARGS='--calibrate-rubric'
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
remain supported. Live model and rubric subprocesses run from the isolated artifact
directory so activation probes cannot accidentally discover the repository checkout's
skill files instead of the installed plugin catalog.

For a model-backed rubric calibration, replace the dry-run Make target with
`python3 scripts/run_humanizer_evals.py --calibrate-rubric`. The calibration must
accept mode-appropriate faithful rewrites, reject unchanged or local-only formulaic
prose in Structural mode, reject broader-than-needed reconstruction in Conservative
mode, and reject smooth rewrites that change modality or scope in either mode.

## Research and design rationale

The design review compared public humanizer, de-slop, clarity, and detector-oriented
skills. The main finding was that most implementations mix surface cleanup with
substantive authorship: they add opinions, first person, anecdotes, emotional
reactions, specificity, or personality presets.

Faithful Humanizer separates those tasks. Its design is based on:

1. source authority;
2. explicit semantic invariants;
3. exact-anchor preservation;
4. a shared semantic ledger;
5. mode-specific reconstruction or localized intervention;
6. a bidirectional semantic diff;
7. restore-on-doubt behavior.

The detailed comparison and rejected design choices are documented in
[`docs/faithful-humanizer-research.md`](docs/faithful-humanizer-research.md).

## Design limits

None of the skills can mathematically guarantee semantic equivalence. Language is
ambiguous, and a model can still make a bad paraphrase or explanation.

Faithful Humanizer reduces that risk through a shared semantic ledger, explicit
invariants, exact-anchor preservation, mode-specific intervention, and
restore-on-doubt rules. High-stakes legal, medical, scientific, financial,
security, or policy text still requires human review.

Plain Language Humanizer reduces that risk through a technical-content ledger,
protected literals, a bidirectional content check, and an anti-bloat contract. It
does not research missing facts, troubleshoot systems, fact-check, summarize, or
provide professional advice. Examples and analogies remain bounded explanatory
devices, not source facts.

No skill guarantees that an AI detector will classify the output as human-written.
Detector evasion is not the objective.

## License

Original repository code, plugin metadata, tests, repository-authored
documentation, Faithful Humanizer, and Plain Language Humanizer are released under
the MIT License.

Wikipedia-derived material adapted into Editorial Humanizer skill instructions,
reference material, examples, and related plugin documentation remains available
under CC BY-SA 4.0. Attribution and license scope are documented in `NOTICE`.

The plugin therefore reports `MIT AND CC-BY-SA-4.0` at the package level.
