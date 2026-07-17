# Humanizer Plugin

Humanizer Plugin packages two prose-editing skills for Codex and other skill-aware agents:

| Skill | Purpose | Editing latitude |
|---|---|---|
| `humanizer` | Remove common AI-writing patterns with the existing fact-safe anti-slop workflow | May cut weak or generic material, restructure prose, and add voice when the source allows it |
| `humanizer-form` | Make wording read more naturally while preserving the supplied substance | Changes form only; every claim, opinion, qualifier, attribution, example, and logical relation must survive |

The second skill exists for cases where the original Humanizer is too opinionated. It uses minimal local edits and a semantic-diff gate rather than a long catalog of banned words and structures.

The repository works as a plain skill source for Claude Code, OpenCode, and Codex. The repository root is also a Codex plugin package.

## Which skill should you use?

Use `humanizer` when you want editorial cleanup: less padding, fewer AI-writing patterns, tighter structure, and a more natural voice.

Use `humanizer-form` when the instruction is closer to:

- Humanize the form, not the substance.
- Preserve every claim and opinion.
- Do not fact-check, add evidence, remove vague claims, or reinterpret the argument.
- Keep every hedge, negation, exception, quantifier, attribution, example, and technical term.
- Make the smallest changes needed for natural wording.

A faithful result that remains slightly artificial is preferable to a smoother result that changes the content.

## Humanizer Form contract

`humanizer-form` protects more than the text's general topic or "core meaning." Its semantic ledger covers:

- every factual and evaluative proposition;
- the speaker and owner of each opinion;
- certainty and modality such as `may`, `might`, `will`, and `must`;
- negation, exclusions, exceptions, and conditions;
- quantifiers and scope such as `some`, `most`, `only`, and `all`;
- causal, comparative, concessive, and temporal relationships;
- attribution, chronology, emphasis, examples, and list membership;
- exact names, numbers, dates, units, URLs, citations, quotes, code, identifiers, and domain terms.

It may correct grammar, punctuation, awkward syntax, repetition, transitions, and sentence flow. It does not add personality, anecdotes, opinions, humor, sources, facts, examples, or detector-oriented randomness. It also does not remove supplied material because it is vague, promotional, unsupported, or disputable.

The full design rationale and comparison of existing skills is in [`docs/humanizer-form-research.md`](docs/humanizer-form-research.md).

## Installation

### Codex plugin marketplace

Add this repository as a marketplace:

```bash
codex plugin marketplace add CoveMB/humanizer-skill-plugin --ref main
```

Install the plugin:

```bash
codex plugin add humanizer-plugin@humanizer-plugin-local
```

Then start a new Codex session so the installed skills are loaded into the prompt.

Confirm the installation:

```bash
codex plugin list
```

The plugin exposes both `humanizer` and `humanizer-form` through the `./skills/` directory declared in `.codex-plugin/plugin.json`.

### Upgrade

Update the marketplace checkout and installed plugin:

```bash
codex plugin marketplace upgrade humanizer-plugin-local
```

Start a new Codex session after upgrading.

### Remove

```bash
codex plugin remove humanizer-plugin@humanizer-plugin-local
```

### Plain Codex skills

Clone the repository and copy either skill into the agent skill directory:

```bash
git clone https://github.com/CoveMB/humanizer-skill-plugin.git
mkdir -p ~/.agents/skills/humanizer ~/.agents/skills/humanizer-form
cp -R humanizer-skill-plugin/skills/humanizer/. ~/.agents/skills/humanizer/
cp -R humanizer-skill-plugin/skills/humanizer-form/. ~/.agents/skills/humanizer-form/
```

Do not enable the plain skill and plugin at the same time. Loading duplicate copies can make skill selection and provenance harder to reason about.

### Claude Code

```bash
mkdir -p ~/.claude/skills
cp -R humanizer-skill-plugin/skills/humanizer ~/.claude/skills/humanizer
cp -R humanizer-skill-plugin/skills/humanizer-form ~/.claude/skills/humanizer-form
```

### OpenCode

```bash
mkdir -p ~/.config/opencode/skills
cp -R humanizer-skill-plugin/skills/humanizer ~/.config/opencode/skills/humanizer
cp -R humanizer-skill-plugin/skills/humanizer-form ~/.config/opencode/skills/humanizer-form
```

## Usage

### Standard Humanizer

```text
Use $humanizer to rewrite this. Return only the rewritten text:

[paste draft]
```

Use it for broader anti-slop editing, voice calibration, or an audit with the existing 80-point scoring gate.

### Form-only Humanizer

```text
Use $humanizer-form. Make this read naturally, but preserve every claim, opinion, qualifier, example, attribution, and logical relation. Return only the rewrite:

[paste draft]
```

A stricter version:

```text
Use $humanizer-form. Humanize the form only. Do not add, remove, fact-check, strengthen, soften, summarize, reorganize, or reinterpret any content. Preserve all names, numbers, dates, quotations, citations, code, modality, negation, scope, causality, attribution, and list items.

[paste draft]
```

### Form-only audit

```text
Use $humanizer-form to rewrite this and briefly explain only the form changes. Note any wording you deliberately retained to avoid changing the substance:

[paste draft]
```

The output should contain the rewrite, `Form changes`, and `Preservation notes`. Humanizer Form does not assign an AI-likeness score.

### Trigger behavior

A skill-aware client can auto-select Humanizer when the request says that writing sounds generated, padded, generic, should read more naturally, or should produce text that reads like a person wrote it. Examples include:

```text
This release note sounds padded. Rewrite it without adding facts.
```

```text
Make this read like a person wrote it.
```

For a deterministic workflow, explicitly say `Use Humanizer` or invoke `$humanizer`.

Humanizer Form has intentionally narrower triggers. Explicitly invoke `$humanizer-form` when preserving substance is the central constraint. Phrases such as "form only," "do not change the substance," and "preserve every claim and opinion" are included in its frontmatter trigger contract.

Do not treat auto-selection as guaranteed. Client behavior varies. In particular, `codex exec` traces do not expose a separate skill-invocation event, so the repository's live Humanizer evals force a read of the expected skill file and verify that path in the trace.

## Examples

### Preserve an uncertain claim

Input:

```text
Additionally, it is important to note that the platform may potentially reduce setup time for some teams.
```

`humanizer-form` output:

```text
Importantly, the platform may reduce setup time for some teams.
```

The rewrite preserves the importance claim, `may`, and `some teams`.

### Preserve vague attribution

Input:

```text
Industry reports suggest adoption is accelerating, highlighting the platform's growing relevance.
```

`humanizer-form` output:

```text
Industry reports suggest that adoption is accelerating, a trend that highlights the platform's growing relevance.
```

The skill does not invent a report, delete the attribution, or neutralize the relevance claim.

### Preserve opinion and emotional valence

Input:

```text
I find the change unsettling. It may, however, improve efficiency.
```

`humanizer-form` output:

```text
I find the change unsettling, although it may improve efficiency.
```

The feeling, order, concessive relation, and uncertain benefit all remain.

### Preserve promotional force when it is supplied content

Input:

```text
The system serves as a robust foundation for scalable workflows, ensuring that cross-functional teams can coordinate effectively.
```

`humanizer-form` output:

```text
The system is a robust foundation for scalable workflows and ensures that cross-functional teams can coordinate effectively.
```

A broader editor might delete `robust` or weaken `ensures`. Humanizer Form keeps them because they are part of the source's evaluative and causal force.

More examples are in [`docs/skill-examples.md`](docs/skill-examples.md).

## Repository layout

```text
.
├── .agents/plugins/marketplace.json
├── .codex-plugin/plugin.json
├── .github/workflows/
│   ├── live-eval.yml
│   └── test.yml
├── docs/
│   ├── humanizer-form-research.md
│   └── skill-examples.md
├── evals/
│   └── humanizer_eval_cases.json
├── scripts/
│   ├── run_humanizer_evals.py
│   └── validate_humanizer_outputs.py
├── skills/
│   ├── humanizer/
│   │   ├── SKILL.md
│   │   └── references/banned-list.md
│   └── humanizer-form/
│       └── SKILL.md
└── tests/
    ├── test_humanizer_form_artifacts.py
    └── test_skill_artifacts.py
```

## Testing

Run all deterministic tests:

```bash
make test
```

Validate the existing Humanizer eval matrix without invoking a model:

```bash
make eval-humanizer-dry-run
```

The new form-only skill has static contract tests covering its trigger contract, semantic invariants, exact anchors, forbidden edits, contextual style rules, bidirectional semantic diff, output format, examples, and research record.

### Live Humanizer evals

The existing live runner installs the checked-out plugin into an isolated Codex home and exercises the standard `humanizer` cases:

```bash
export HOME="$(mktemp -d)"
export CODEX_HOME="$(mktemp -d)"
python3 scripts/run_humanizer_evals.py \
  --cases evals/humanizer_eval_cases.json \
  --artifacts-dir evals/artifacts/local \
  --codex-bin codex \
  --filter explicit_dense_rewrite \
  --timeout-seconds 600 \
  --rubric-grade
```

For live evals, isolate both `HOME` and `CODEX_HOME`. The runner requires a non-default Codex home, and CI configures a temporary `HOME` for every Codex subprocess so plugin and credential state cannot leak from the host environment.

Useful flags:

| Flag | Purpose |
|---|---|
| `--cases` | Select an eval-case JSON file |
| `--artifacts-dir` | Choose where results and traces are written |
| `--codex-bin` | Select the Codex executable |
| `--filter` | Run matching case IDs only |
| `--timeout-seconds` | Set the per-case timeout |
| `--rubric-grade` | Enable model-based rubric grading |

The form-only skill is not yet included in the live model matrix. Its first release relies on deterministic artifact tests and the explicit semantic contract. A separate live matrix should compare source and output for proposition coverage, modality, scope, negation, attribution, exact anchors, and forbidden additions rather than reward detector scores.

## Design limits

Neither skill can mathematically guarantee semantic equivalence. Language is ambiguous, and a model can still make a bad paraphrase. Humanizer Form reduces that risk through minimal edits, explicit invariants, exact-anchor preservation, and restore-on-doubt rules. High-stakes legal, medical, scientific, security, financial, or policy text still requires human review.

Neither skill guarantees that an AI detector will classify the output as human-written. Detector evasion is not the objective.

## Versioning

- Plugin `2.9.0`: adds `humanizer-form` 1.0.0, dual-skill documentation, a research record, and deterministic contract tests.
- `humanizer` remains the existing opinionated anti-slop editor, with its version advanced to match the plugin package.
- `humanizer-form` follows its own skill version because its contract is independent from the legacy catalog.

## Sources and research

The original Humanizer is based on Wikipedia's *Signs of AI writing* and incorporates attributed checklist and scoring concepts from stop-slop and Tagore. Its complete attribution is recorded in `NOTICE` and in the skill frontmatter.

Humanizer Form was written from scratch after reviewing multiple public humanizer and de-slop skills. The comparison and rejected design choices are documented in [`docs/humanizer-form-research.md`](docs/humanizer-form-research.md).

## License

Original repository code, plugin metadata, tests, documentation, and `humanizer-form` are released under the MIT License.

Wikipedia-derived material in the original `humanizer` skill is available under CC BY-SA 4.0. The attribution and scope of the Wikipedia-derived material are described in `NOTICE`.

CC BY-SA 4.0 license text and terms:

https://creativecommons.org/licenses/by-sa/4.0/

The package therefore reports `MIT AND CC-BY-SA-4.0` at the plugin level. See `LICENSE` and `NOTICE` for details.
