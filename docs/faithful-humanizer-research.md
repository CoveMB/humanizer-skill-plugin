# Research notes: Faithful Humanizer

Date reviewed: 2026-07-17

## Research question

How can an AI-writing editor make prose read more naturally without changing what
the author says, adding a personality, correcting the argument, or deleting content
that the editor considers vague or weak?

The review focused on public `SKILL.md` implementations rather than commercial
paraphrasers. It examined operating rules, examples, preservation guarantees,
false-positive protections, output contracts, and detector-oriented behavior.

## Naming conclusion

The plugin now uses two names that describe editorial authority rather than an
implementation detail:

- **Editorial Humanizer** applies broader editorial judgment.
- **Faithful Humanizer** preserves the supplied substance and edits only its form.

“Opinionated” and “non-opinionated” are useful informal descriptions, but they are
not precise product names. Faithful Humanizer still makes copy-editing judgments;
it simply cannot impose a new position or remove supplied content. “Form Humanizer”
was also too technical and did not clearly communicate the user-facing guarantee.

## Sources reviewed

| Project | Useful ideas | Substance-drift risks |
|---|---|---|
| [CoveMB/humanizer-skill-plugin](https://github.com/CoveMB/humanizer-skill-plugin) | Fact mapping, explicit no-invention rule, exact noun preservation, output-only mode | Personality injection, global style rules, restructuring, and deletion of weak claims |
| [blader/humanizer](https://github.com/blader/humanizer) | Context-sensitive false-positive guidance and preservation of already-human detail | Defaults to an opinionated voice and examples add scenes, reactions, and details |
| [jpeggdev/humanize-writing](https://github.com/jpeggdev/humanize-writing) | Pass-based editing and useful context checks | Explicitly adds opinions, first person, humor, lived detail, sources, and anecdotes |
| [Aboudjem/humanizer-skill](https://github.com/Aboudjem/humanizer-skill) | Cluster-based detection, protection for quotes and code, minimal edit mode | Voice profiles, aggressive mode, and detector-oriented metrics |
| [hardikpandya/stop-slop](https://github.com/hardikpandya/stop-slop) | Compact checklist and directness checks | Absolute style rules can override genre and author intent |
| [apurvrdx1/tagore](https://github.com/apurvrdx1/tagore) | Separates mechanical quality from factual integrity | Treats point of view, stakes, opinion, and deliberate messiness as required |
| [stephenturner/skill-deslop](https://github.com/stephenturner/skill-deslop) | Lean structure and register-aware scientific guidance | Active-subject and specificity defaults can alter agency or emphasis |
| [theclaymethod/unslop](https://github.com/theclaymethod/unslop) | Strong preservation framework: anchors, modality, negation, scope, conditions, attribution, and validation | Presets and scanners still make broader editorial choices |
| [conorbronsdon/avoid-ai-writing](https://github.com/conorbronsdon/avoid-ai-writing) | Minimal targeted edits, protection for quotes and code, patterns as signals rather than proof | Rewrite mode retains hard density and punctuation targets |
| [brandonwise/humanizer](https://github.com/brandonwise/humanizer) | Transparent pattern grouping and automated checks | Statistical scoring, vocabulary bans, personality injection, and invented specifics in examples |
| [softaworks/agent-toolkit](https://github.com/softaworks/agent-toolkit) | Progressive disclosure and compact clarity guidance | Active voice and concreteness are editorial defaults, not semantic invariants |
| [humanizerai/agent-skills](https://github.com/humanizerai/agent-skills) and detector-oriented variants | Distinct trigger vocabulary and market category | Detector bypass is a different objective and rewards unnecessary transformation |

## Main findings

### 1. Most humanizers combine two tasks

The reviewed skills commonly mix:

1. removing repetitive or awkward AI-associated forms; and
2. creating a more distinctive writer by adding opinions, emotion, anecdotes,
   specificity, humor, first person, or a voice preset.

The second task is substantive authorship. It may be useful in Editorial Humanizer,
but it is incompatible with Faithful Humanizer.

### 2. “Preserve meaning” is too weak

A rewrite can preserve the general topic while changing local meaning:

- `may` becomes `will`;
- `some` becomes an unrestricted claim;
- correlation becomes causation;
- the author's opinion becomes a neutral report;
- a source-attributed claim becomes the editor's claim;
- an exception, negation, condition, or sequence disappears;
- a list item or example is removed.

Faithful Humanizer therefore uses explicit invariants and a bidirectional semantic
diff rather than relying on “core meaning.”

### 3. Pattern catalogs are diagnostic cues, not universal rules

Em dashes, passive voice, formal transitions, adverbs, technical jargon, title case,
curly quotes, and three-item lists all have legitimate human uses. A faithful editor
should change them only when they are locally awkward and the replacement is
semantically equivalent.

### 4. Unsupported content must remain content

Editorial Humanizer may delete vague claims, request sources, or replace inflation
with supplied facts. Faithful Humanizer cannot.

For a faithful rewrite:

- `Experts argue ...` remains attributed to unnamed experts;
- promotional language retains its evaluative force;
- an unsupported conclusion remains present;
- no source is invented;
- fact checking remains a separate task.

### 5. Minimality is a preservation mechanism

Whole-paragraph regeneration creates more opportunities for drift than local edits.
Faithful Humanizer therefore protects exact spans first, changes the smallest useful
span, leaves natural passages untouched, and restores original wording whenever
equivalence is uncertain.

### 6. Register guards are necessary

Legal, medical, scientific, financial, security, policy, and technical prose often
uses qualifiers, passive constructions, repetition, defined terms, and rigid order
for reasons that outweigh stylistic smoothness.

### 7. Detector optimization should be excluded

Perplexity, burstiness, vocabulary scores, and detector outcomes are not reliable
proxies for faithful editing. Optimizing them can reward random variation and
unnecessary rewriting.

## Adopted design

Faithful Humanizer uses six controls:

1. **Source authority:** the supplied text defines the content.
2. **Explicit semantic invariants:** claims, stance, modality, negation, scope,
   logic, attribution, chronology, emphasis, examples, and list membership survive.
3. **Exact anchors:** names, numbers, dates, units, quotes, citations, URLs, code,
   identifiers, and domain terms remain unchanged.
4. **Minimal local edits:** only wording, syntax, grammar, punctuation, transitions,
   repetition, and rhythm may change.
5. **Bidirectional semantic diff:** every source proposition maps to the output and
   every output proposition maps back to the source.
6. **Restore on doubt:** uncertain paraphrases revert to source wording.

## Rejected design choices

Faithful Humanizer does not include:

- a banned-word list;
- an em-dash or passive-voice ban;
- a required sentence-length distribution;
- a rule against three-item lists;
- personality, opinion, anecdote, or first-person injection;
- deletion of vague, promotional, unsupported, or disputed claims;
- fact checking or source requests;
- an AI-likeness score;
- detector-evasion targets;
- a private style score that pressures the model to keep rewriting.

## Licensing note

Faithful Humanizer was written from scratch for this repository. It uses general
editing concepts and links to the reviewed projects, but does not copy their pattern
catalogs or examples. It is MIT-licensed. Editorial Humanizer retains the existing
mixed-license attribution described in `NOTICE`.
