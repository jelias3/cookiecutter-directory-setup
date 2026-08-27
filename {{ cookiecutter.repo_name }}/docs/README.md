# `docs/` — index

Deep dives that `AGENTS.md` routes to. `AGENTS.md` is the index of *where to look*; these
files hold the actual mechanisms, conventions and hard-won gotchas. Anything durable that
does not fit `AGENTS.md`'s line budget belongs here.

Every file in this directory is hand-written source. Nothing here is generated.
{% if cookiecutter.use_quarto_site == 'y' -%}
(The Quarto site renders into `docs/site/`, a separate subdirectory, precisely so that
generated HTML never mixes with these sources. Do not hand-edit anything under
`docs/site/` — regenerate it with `quarto render` from `analysis/`.)
{%- endif %}

**Status tags — every row below carries one:**

- `CURRENT` — trustworthy; act on it.
- `SUPERSEDED-IN-PART` — read the correction banner at the top of the file before
  believing anything in it. Some of it still stands; the banner says which part does not.
- `HISTORICAL` — kept for provenance. Do not act on it.

A doc with no status tag is a bug. Tag it or delete it.

## Subsystem guides — read before touching the corresponding code

| doc | status | read before |
|---|---|---|
| [`conventions.md`](conventions.md) | CURRENT | deciding where a new file goes; writing a notebook helper script; adding a sample; adding a conda env. Layout contract, sample-ID grammar, agent tooling. |
| [`running_and_slurm.md`](running_and_slurm.md) | CURRENT | launching a run, debugging a failed job, writing an sbatch script. The two path conventions, the real launch line, **the single log policy**, resource escalation. |
| TODO: `<subsystem>.md` | TODO: CURRENT | TODO: *(example row — replace or delete)* editing `code/scripts/<x>/*` or `code/rules/<X>.smk`; interpreting anything in `output/<X>/`. Install, the metric definition, the traps, output provenance. |

**One doc per subsystem, and exactly one home per kind of fact.** If two docs both
describe per-sample caveats, one of them is wrong and you will not find out which until it
costs you a day. Pick the home, name it in the other doc's row, move the content.

## Methods and background

| doc | status | what it is |
|---|---|---|
| [`abstract.md`](abstract.md) | CURRENT | The project abstract — scientific motivation in prose. The one place background lives. |
| TODO: `<method>_walkthrough.md` | TODO: CURRENT | TODO: *(example row — replace or delete)* End-to-end worked example with real numbers, from raw input to the reported quantity. The place to check a modeling claim. |

A doc in this table that gets corrected later should **keep its filename** and gain a
**correction banner** at the top — dated, saying what changed and what still stands — and
flip to `SUPERSEDED-IN-PART`. Do not silently edit a claim that an `analysis/*/SUMMARY.md`
cites; that summary's numbers were computed against the old claim.

## Where other kinds of knowledge live

- **Empirical results and numbers** → `analysis/README.md` (the index) and each
  `analysis/<date>_<topic>/SUMMARY.md`. Results are **not** copied into `docs/`; docs link
  to them. A number stored in two places will eventually disagree with itself.
- **Per-sample / per-dataset status and caveats** → one section per key in whichever doc
  you named as its home above, nowhere else.
- **Routing, and the top handful of traps** → `/AGENTS.md`.
- **Machine-local anything** (paths on your laptop, personal tool settings) → nowhere in
  this repo. See the Claude Code block at the bottom of `/.gitignore`.

## Retired

When a doc is deleted it gets an entry here instead of vanishing. **Rationale:** git
history preserves the text but not the *reason*, and the reason is the expensive part. A
deleted doc almost always contains one insight worth keeping and one wrong framing worth
never re-deriving. An entry states what the doc proposed, what shipped instead, and where
its one durable insight now lives. Recover the full text from git history if ever needed.

TODO: nothing retired yet. Format, when the first one goes:

- `<filename>.md` — *(one line on what it claimed or proposed)*. What actually shipped is
  *(the thing that replaced it)*. Its one durable insight — *(the insight)* — now lives in
  `<doc>.md` §N.
