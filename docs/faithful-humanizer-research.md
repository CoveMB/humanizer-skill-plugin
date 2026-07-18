# Research notes: Faithful Humanizer

Date reviewed: 2026-07-18

## Research question

How can an AI-writing editor make prose read more naturally without changing what
the author says, adding a personality, correcting the argument, or deleting content
that the editor considers vague or weak?

The review focused on public `SKILL.md` implementations rather than commercial
paraphrasers. It examined operating rules, examples, preservation guarantees,
false-positive protections, output contracts, and detector-oriented behavior.

## Naming conclusion

The plugin uses two skill names that describe editorial authority rather than an
implementation detail, while Faithful exposes two intervention strategies:

- **Editorial Humanizer** applies broader editorial judgment.
- **Faithful Humanizer — Structural** preserves the supplied substance and
  reconstructs its form. It is the default Faithful behavior.
- **Faithful Humanizer — Conservative** preserves the same substance through the
  smallest useful localized intervention. It is opt-in.

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
| [Gude et al., ACL 2026](https://aclanthology.org/2026.acl-long.1803/) | Evidence that newer instruction-tuned models in the study's English news sample showed reduced syntactic and lexical diversity | Corpus-level, news-specific evidence cannot diagnose an individual passage or justify fixed surface targets |
| [Purdue OWL: Sentence Structure, Variety, and Clarity](https://owl.purdue.edu/owl/graduate_writing/introduction_to_writing/documents/revising-and-editing/sentence-structure-activity.pdf) | Sentence structure can express emphasis, balance, and relationships among ideas; variation should be purposeful | Does not support random sentence-length variation, fragments, or universal style rules |
| [George Mason Writing Center: Known/New Contract](https://writingcenter.gmu.edu/writing-resources/grammar-style/improving-cohesion-the-known-new-contract) | Known-to-new information flow can improve cohesion and place emphasis deliberately | A cohesion technique is not permission to reorder chronology, causality, scope, or argument progression |
| [Huang and Chang, EACL 2021](https://aclanthology.org/2021.eacl-main.88/) | Demonstrates that semantic and syntactic representations can be separated for controlled paraphrase generation | Model-level paraphrase results do not guarantee that any particular rewrite is semantically equivalent |

## Follow-up implementation review

The 2026-07-17 implementation pass rechecked the current upstream instructions for
Avoid AI Writing 3.16.0 and Skill Deslop 1.0.0.

Avoid AI Writing contributed four compatible principles:

- patterns are writing-quality signals rather than proof of authorship;
- already-natural passages should remain untouched;
- edits should target flagged spans before regenerating whole passages; and
- ordinary words and structures become more informative when they cluster or repeat.

Its fixed punctuation targets, stylometric ranges, authorship-oriented detector
features, and full-rewrite thresholds were not adopted as Humanizer rules.

Skill Deslop contributed attention to scientific formality, disciplinary
terminology, citations, and formulaic scientific conclusions. Its blanket
active-voice, first-person, no-em-dash, and anti-tricolon rules were rejected because
they can change agency, register, emphasis, or valid scientific form.

The resulting implementation uses a shared scientific-register reference with
skill-specific authority. Faithful treats it as preservation constraints; Editorial
uses it as genre-specific guidance within factual and epistemic boundaries.

The review also adopted the diagnose-then-reconstruct sequence from
[theclaymethod/unslop](https://raw.githubusercontent.com/theclaymethod/unslop/main/references/commands/rewrite.md)
for Structural mode, but not that project's broader content latitude, presets, or
scoring gates. Detector-oriented structure signals in Avoid AI Writing remain
diagnostic context only; its fixed targets and detector framing are outside the
Faithful contract.

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

### 5. Minimality is one preservation mechanism

Localized editing reduces opportunities for drift and remains the defining strategy
of Conservative mode. It protects exact spans first, changes the smallest useful
span, leaves natural passages untouched, and restores original wording whenever
equivalence is uncertain.

Minimality can also leave a passage's formulaic architecture intact. Structural
mode addresses that limitation by rebuilding form from a semantic ledger and then
checking the result proposition by proposition. Its wider intervention surface
requires stricter comparison, not broader semantic authority.

Neither mode permits an unchanged or cosmetic result when a safe, mode-appropriate
repair exists. Both leave already-natural passages alone.

### 6. Register guards are necessary

Legal, medical, scientific, financial, security, policy, and technical prose often
uses qualifiers, passive constructions, repetition, defined terms, and rigid order
for reasons that outweigh stylistic smoothness.

### 7. Detector optimization should be excluded

Perplexity, burstiness, vocabulary scores, and detector outcomes are not reliable
proxies for faithful editing. Optimizing them can reward random variation and
unnecessary rewriting.

Deterministic observations can still support Editorial audits. Counts of repeated
phrases, transitions, punctuation, sentence or paragraph lengths, bold-label
structures, and vocabulary clusters are raw diagnostic evidence. They do not
determine authorship, set an editorial score mechanically, or apply to Faithful as
humanness targets.

### 8. Sentence form carries meaning-adjacent signals

Purdue's guidance treats sentence structure as a way to express emphasis, balance,
and relationships among ideas. A dependent clause and an independent clause do not
necessarily carry equal weight. Structural rewriting therefore cannot vary syntax
arbitrarily: it must preserve the source's weighting and logical relationships.

George Mason's known-new guidance provides one useful cohesion strategy. It can
support moving familiar context toward sentence openings and newer information
toward sentence endings, but only when that movement preserves chronology,
causality, scope, emphasis, and meaningful argument order.

### 9. Syntax and semantics can be treated separately, but not assumed equivalent

Huang and Chang's syntactically controlled paraphrase work supports the design
premise that syntax can change while semantic content is held apart. Faithful
Structural operationalizes that premise conservatively: it uses a semantic ledger,
bidirectional proposition mapping, and restore-on-doubt behavior rather than
assuming that a smoother paraphrase is faithful.

### 10. Corpus patterns are guidance, not individual-text targets

Gude et al. found reduced syntactic and especially lexical diversity in newer
instruction-tuned models within their English news comparison. The result motivates
attention to structural regularity, but it is not an individual-text detector and
does not justify fixed sentence lengths, required "burstiness," random fragments,
manufactured errors, or detector-score optimization.

## Adopted design

Faithful Humanizer uses seven shared controls and two intervention strategies:

1. **Source authority:** the supplied text defines the content.
2. **Explicit semantic invariants:** claims, stance, modality, negation, scope,
   logic, attribution, chronology, emphasis, examples, and list membership survive.
3. **Exact anchors:** names, numbers, dates, units, quotes, citations, URLs, code,
   identifiers, and domain terms remain unchanged.
4. **Semantic ledger:** each proposition, owner, stance, modality, scope, anchor,
   comparison, chronology, logical relation, meaningful order, and register
   constraint is recorded before rewriting.
5. **Mode-specific intervention:** Structural reconstructs from the ledger;
   Conservative repairs the smallest sufficient span.
6. **Bidirectional semantic diff:** every source proposition maps to the output and
   every output proposition maps back to the source.
7. **Restore on doubt:** uncertain paraphrases revert to source wording.

Structural may change subjects, split or merge sentences, move qualifications,
change safe clause order, improve known-to-new flow, and change non-meaningful
paragraph boundaries. Conservative preserves subjects, sentence boundaries,
paragraph architecture, and ordering unless a local defect cannot otherwise be
resolved. Both preserve the same semantic invariants.

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
