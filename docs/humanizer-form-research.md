# Research notes: form-only humanization

Date reviewed: 2026-07-17

## Research question

How can a humanizer make AI-drafted prose read more naturally without changing
what the author says, adding a personality, correcting the argument, or deleting
content that an editor considers vague or weak?

The review focused on public `SKILL.md` implementations rather than commercial
paraphrasers. It examined their operating rules, examples, output contracts,
false-positive protections, and preservation checks.

## Sources reviewed

| Project | Useful ideas | Substance-drift risks |
|---|---|---|
| [CoveMB/humanizer-skill-plugin](https://github.com/CoveMB/humanizer-skill-plugin) | Fact mapping, explicit no-invention rule, exact noun preservation, output-only mode | Default personality injection, opinion and first-person guidance, global punctuation and structure bans, deletion of vague claims |
| [blader/humanizer](https://github.com/blader/humanizer) | Rewrite rather than merely delete; context-sensitive false-positive guidance; preserve already-human detail | Defaults to an opinionated voice when no sample is supplied; examples add scenes, reactions, and details |
| [jpeggdev/humanize-writing](https://github.com/jpeggdev/humanize-writing) | Pass-based editing and useful context checks for individual patterns | Explicitly adds opinions, first person, lived detail, humor, and emotional reactions; example rewrites invent sources and anecdotes |
| [Aboudjem/humanizer-skill](https://github.com/Aboudjem/humanizer-skill) | Cluster-based detection, protection for quotes and code, minimal edit mode | Voice injection, aggressive mode, personality presets, detector-oriented burstiness and perplexity targets |
| [hardikpandya/stop-slop](https://github.com/hardikpandya/stop-slop) | Compact checklist and directness checks | Absolute rules against adverbs, passive voice, em dashes, and three-item groupings can override genre and author intent |
| [apurvrdx1/tagore](https://github.com/apurvrdx1/tagore) | Separates mechanical quality from factual integrity; staged verification | Treats point of view, stakes, opinions, first person, and deliberate messiness as required human qualities |
| [stephenturner/skill-deslop](https://github.com/stephenturner/skill-deslop) | Lean structure; register-aware scientific-writing guidance | Requires active human subjects, specificity, shorter groupings, and other stylistic preferences that can alter emphasis or agency |
| [theclaymethod/unslop](https://github.com/theclaymethod/unslop) | Strongest preservation framework: exact anchors, modality, negation, scope, conditions, attribution, register guards, and post-rewrite validation | Broader presets and anti-slop scanners still make more editorial choices than a form-only skill should make |
| [conorbronsdon/avoid-ai-writing](https://github.com/conorbronsdon/avoid-ai-writing) | Minimal targeted edits, leave clean passages alone, protect quoted material and code, treat patterns as signals rather than proof | Rewrite mode still has zero-tolerance and density targets for some punctuation, vocabulary, and structures |
| [brandonwise/humanizer](https://github.com/brandonwise/humanizer) | Transparent pattern grouping and automated checks | Statistical scoring, vocabulary bans, personality injection, and examples that replace source content with external specifics |
| [softaworks/agent-toolkit: writing clearly and concisely](https://github.com/softaworks/agent-toolkit/tree/main/skills/writing-clearly-and-concisely) | Progressive disclosure and a compact clarity-oriented skill design | General clarity rules such as active voice and concreteness are useful editorial defaults, not semantic invariants |
| [humanizerai/agent-skills](https://github.com/humanizerai/agent-skills) and detector-oriented variants | Shows a distinct market category and trigger vocabulary | Optimizing to bypass detectors is a different objective from improving prose and encourages unnecessary transformation |

## Main findings

### 1. Most humanizers combine two different tasks

The reviewed skills commonly mix:

1. removing repetitive or awkward AI-associated forms; and
2. creating a more distinctive writer by adding opinions, emotion, anecdotes,
   specificity, humor, first person, or a voice preset.

The second task is substantive authorship. It may be useful for ghostwriting, but
it is incompatible with a form-only editor.

### 2. "Preserve meaning" is too weak as a safeguard

A general instruction to preserve the core message does not protect local meaning.
A rewrite can keep the topic while changing:

- `may` into `will`;
- `some` into an unqualified universal claim;
- correlation into causation;
- the author's opinion into a neutral report;
- a source-attributed claim into the editor's own assertion;
- an exception, negation, condition, or sequence;
- the number and identity of examples or list items.

A conservative skill therefore needs explicit invariants and a bidirectional
semantic diff, not only a factual-integrity reminder.

### 3. Pattern catalogs are better diagnostic cues than hard rules

The same surface feature can be artificial in one passage and appropriate in
another. Em dashes, passive voice, formal transitions, adverbs, technical jargon,
curly quotes, title case, and three-item lists all have ordinary human uses.

A form-only humanizer should ask whether a feature is locally awkward or repetitive.
It should not remove it merely because it appears in a catalog.

### 4. Unsupported content must remain content

Several humanizers delete vague claims, request sources, or replace them with named
facts. That is defensible fact-safe editing, but it changes the supplied text.

For a form-only rewrite:

- `Experts argue ...` must remain attributed to unnamed experts;
- promotional language must retain its evaluative force;
- an unsupported conclusion must remain present;
- no source may be invented;
- fact-checking must be a separate request.

The result may remain less polished than a substantive editor would prefer. That
is an intentional constraint.

### 5. Minimality is a preservation mechanism

Whole-paragraph regeneration creates more opportunities for drift than local edits.
The conservative default should therefore be:

- protect exact spans first;
- identify only form-level friction;
- edit the smallest possible span;
- leave already-natural passages untouched;
- restore original wording whenever equivalence is uncertain.

### 6. Register guards are necessary

Legal, medical, scientific, security, policy, and technical prose often uses
qualifiers, passive constructions, repetition, and defined terms for reasons that
outweigh stylistic smoothness. The skill must preserve these rather than applying
general anti-AI preferences.

### 7. Detector optimization should be excluded

Perplexity, burstiness, vocabulary scores, and detector outcomes are not reliable
proxies for faithful editing. Optimizing them can reward random variation and
unnecessary rewrites. The new skill explicitly targets reader-facing naturalness,
not classifier evasion.

## Design adopted for `humanizer-form`

The new skill uses five controls:

1. **Source authority**: the supplied text defines the content; the editor does not
   adjudicate it.
2. **Explicit semantic invariants**: claims, stance, modality, negation, scope,
   logic, attribution, chronology, emphasis, and list membership are protected.
3. **Exact anchors**: names, numbers, dates, units, quotes, citations, URLs, code,
   identifiers, and domain terms remain unchanged.
4. **Minimal local edits**: only wording, syntax, grammar, punctuation, transitions,
   repetition, and rhythm may change.
5. **Bidirectional semantic diff**: every source proposition must map to the output,
   and every output proposition must map back to the source.

## Rejected design choices

`humanizer-form` does not include:

- a banned-word list;
- an em-dash or passive-voice ban;
- a required sentence-length distribution;
- a rule against three-item lists;
- personality, opinion, anecdote, or first-person injection;
- deletion of vague, promotional, unsupported, or disputed claims;
- fact checking or source requests;
- an AI-likeness score;
- detector-evasion targets;
- a private quality score that can pressure the model to keep rewriting.

## Licensing note

The `humanizer-form` instructions were written from scratch for this repository.
They use general editing concepts and link to the projects reviewed above, but do
not copy their pattern catalogs or examples. The new skill is MIT-licensed. The
repository as a whole retains its existing mixed-license notice because the
original `humanizer` skill includes separately attributed material.
