# Conventions — layout, naming, and agent tooling

Status: CURRENT. This is the reference `AGENTS.md` routes to for "where does a new file
go". `AGENTS.md` states the one-line rule; the reasoning and the edge cases are here.

Much of this file is inherited from the project template's upstream
(`bfairkun/cookiecutter-quarto-smk`), **with its layout contract corrected** — see
§Layout. Where this file and any inherited boilerplate disagree, this file wins.

## Layout

```
<repo>/
├── AGENTS.md        # routing index (line-budgeted); CLAUDE.md is a one-line import of it
├── README.md        # thin signpost for GitHub visitors
├── analysis/        # dated, self-contained investigations + notebook helpers
│   ├── <YY>_<MM>_<DD>_<topic>/   # notebook(s) + SUMMARY.md + figures/*.webp
│   └── scripts/                  # one-off notebook helpers (NOT called by Snakemake)
├── code/            # the Snakemake workflow -- the ONLY committed code
│   ├── Snakefile
│   ├── rules/       # *.smk modules
│   ├── scripts/     # production scripts called BY Snakemake rules
│   ├── jobs/        # hand-written .sbatch scripts (see _TEMPLATE.sbatch)
│   ├── envs/        # one conda env per tool; <repo>.yaml is the driver env
│   ├── config/      # config.yaml + samples.tsv
│   ├── schemas/     # JSON schemas validating config/*.tsv
│   ├── module_workflows/  # git submodules for shared Snakemake modules
│   └── scratch/     # regenerable intermediates, never committed
├── data/            # raw inputs. GITIGNORED except README.md
├── output/          # canonical pipeline results. GITIGNORED except README.md
├── logs/            # every log this project writes. GITIGNORED except README.md
└── docs/            # hand-written prose (this directory)
```

### Where things go

| File type | Location | Notes |
|---|---|---|
| Snakemake-invoked script | `code/scripts/` | Anything a `rules/*.smk` file calls. Production code. |
| Notebook helper (one-off, not in Snakemake) | `analysis/scripts/` | Named after the notebook it pairs with. See §Ad-hoc helpers. |
| Snakemake rule | `code/rules/<topic>.smk` | Grouped by topic, never by date. |
| Hand-written batch job | `code/jobs/<name>.sbatch` | Copy `code/jobs/_TEMPLATE.sbatch`. An `.sbatch` inside the `analysis/` dir that owns it is also correct — then the job travels with its `SUMMARY.md`. |
| Conda env YAML | `code/envs/<tool>.yaml` | One small env per tool or tightly-coupled group, never a monolith. Filename == `name:`. `.yaml`, not `.yml`. |
| Raw data | `data/<dataset>/` | Never edited. Not committed. |
| Pipeline output | `output/<stage>/<key>/` | Every path a declared rule output. Not committed. |
| Analysis notebook | `analysis/<YY>_<MM>_<DD>_<topic>/` | One directory per investigation. See `analysis/README.md`. |
| Figures | `analysis/<dir>/figures/*.webp` | Committed. Written by the injected `savefig()` helper. |
| Any log | `logs/<name>/` | One policy. See `running_and_slurm.md` §Logs. |

**Corrected from upstream, deliberately.** The inherited version of this table described
`data/` as "small, never-edited raw data (git-tracked)" and `output/` as "pipeline outputs
intended to be committed and shared", and called `docs/` the rendered HTML site. None of
those hold here:

- `data/`, `output/` and `logs/` are **gitignored wholesale** (except their READMEs). In
  practice these directories reach hundreds of gigabytes; a template that tells an agent
  to commit them is a template that will one day commit a BAM.
- `output/` is **canonical but regenerable** — reproduced by running the pipeline, not by
  cloning. A fresh clone gets code, config, docs and analysis prose.
- `docs/` is **hand-written prose**. The Quarto site, when enabled, renders to
  `docs/site/`.
- `code/scratch/` still exists for regenerable intermediates, but prefer `output/` for
  anything a rule declares, so it is reproducible rather than merely present.

### What NOT to do

- Don't write production helpers into `code/scratch/` — that directory is regenerable junk.
- Don't invent a new top-level directory. If something doesn't fit above, that's a
  conversation, not a `mkdir`.
- Don't hardcode absolute paths to reference data, scratch space, or prebuilt conda envs.
  Use the `genome_prefix` / `scratch_dir` keys in `code/config/config.yaml` and per-rule
  `conda: "envs/<tool>.yaml"`. A path into another user's directory works exactly until it
  doesn't, and then silently.
- Don't add a bare gitlink. Submodules go in via `git submodule add` so `.gitmodules`
  records them; a gitlink without it produces a clone that cannot be populated.

## Samples

The sample ID is the primary Snakemake wildcard: it appears in every output path derived
from that sample, so **renaming one later is a migration, not an edit.**

- **Grammar:** `<YY>_<MM>_<DD>_<subject>[_rep<N>]` — zero-padded date fields, lowercase
  snake_case subject. e.g. `26_08_27_hela_rep1`.
- Declared machine-readably in `code/schemas/samples.schema.yaml` (`pattern` on the
  `Sample` property). Tighten or relax that pattern as the project needs — but change the
  schema and this section together, never one alone.
- **Every output file is prefixed with its sample ID**, so a file that gets copied out of
  the tree still says what it came from.
- `code/config/samples.tsv` is the single source of truth for sample metadata. It is a
  TSV: preserve tabs, do not whitespace-align it.
- Use `enum` in the schema for closed vocabularies (library type, condition). A typo in an
  un-enumerated column silently creates a new group of one, which is the kind of bug that
  survives to a figure.

## Ad-hoc notebook helper scripts

Sometimes a notebook needs a one-off data-prep step that doesn't belong in the pipeline —
e.g. a per-barcode pileup only one notebook depends on. Those go in `analysis/scripts/`.

1. **Name** the script after the notebook it pairs with: `<notebook_stem>_<purpose>.py`.
2. The script's **docstring** states which notebook it pairs with and the exact CLI used
   to generate its outputs.
3. The notebook **references the script by path** and shows the command that produced the
   files it loads.
4. **Outputs** go to `output/` (canonical) or a gitignored `work/` subdir (scratch) —
   never loose in `analysis/`.
5. If a helper turns out to be reused across notebooks, **promote** it: move to
   `code/scripts/`, wire a rule in `code/rules/<topic>.smk`, and update the notebook to
   read the rule's output path instead of running the script.

## Notebooks

- **Never executed headlessly by an agent.** The user re-runs notebooks manually; agents
  read the stored outputs. Re-running can change results, and the stored outputs *are* the
  record being documented. This is enforced by convention, not by tooling — see
  §Agent tooling for why no hook enforces it.
- Papermill-parameterized notebooks run *as pipeline rules* are the exception, and are
  fine: the executed notebook is a declared rule output under `output/`, which buys
  provenance for free. That is `code/scripts/*.ipynb`, not `analysis/`.
- Open with a markdown Purpose / Question / Inputs / Env cell; close with Conclusions.
- Figures via the injected `savefig()` helper → `figures/<descriptive>.webp`.

## Commits

`type(scope): imperative summary`, e.g. `docs(analysis): summarize 26_08_27_polya_length`.

Bodies carry real numbers and state what was *not* changed. Prose that explains the
biology and the decision is worth more than a restatement of the diff — these messages are
a lab notebook, and they are the only record of *why* that survives a refactor.

## Agent tooling

`.claude/` ships three things and deliberately omits two.

**Shipped:** the `analysis-summary` skill (documenting an analysis dir is the one workflow
that recurs and has a real tool behind it), three slash commands (`/new-analysis`,
`/add-sample`, `/run-pipeline` — each encodes a rule that would otherwise decay in
someone's memory), and a committed read-only `settings.json` allowlist.

**Omitted:** subagent definitions, and hooks. A hook runs on every matching tool call and
fails across the whole project when its assumptions don't hold. The tempting one here is a
`PreToolUse` hook blocking `papermill` / `nbconvert --execute` under `analysis/` to enforce
the never-run-headlessly rule — but this project may also run notebooks through papermill
*as legitimate Snakemake rules*, and a hook that blocks a valid pipeline rule is a worse
failure than a forgotten convention. Enable it per-project once that question is settled
for this project.

### The read-only allowlist, and its one caveat

`.claude/settings.json` pre-approves commands that only read state, so they stop costing a
prompt. **An allowlist entry matches a command prefix, and shell redirection is not part of
the command name** — `wc -l x > y` still matches `Bash(wc:*)` and still writes `y`. The
allowlist bounds *intent*, not *capability*. Treat it as "things I got tired of approving",
never as a sandbox.

Deliberately **excluded**, each for a reason worth knowing:

- **`Bash(python3:*)`, `Rscript`, `bash`, `sh`, `xargs`, `perl`, `conda run`** — arbitrary
  code execution. A committed allowlist containing any of these permits everything.
  Approve them per-session in `.claude/settings.local.json` instead.
- **`Bash(snakemake -n:*)`** — *looks* read-only, isn't. A dry run evaluates the Snakefile
  as Python, and `rules/common.smk` creates symlinks at parse time; it also writes
  `.snakemake/` metadata and can take the workflow lock. `/run-pipeline` makes the prompt
  cheap instead.
- **`Bash(samtools view -H:*)`** — *looks* read-only, isn't, twice: `-o` comes after the
  matched prefix so `view -H in.bam -o /anywhere.sam` writes an arbitrary path, and on a
  CRAM samtools may populate a reference cache under `$HOME`. Use `flagstat` / `idxstats`
  for the common questions.
- **`Bash(find:*)`** — `find . -delete` and `find . -exec rm {} \;` are both `find`. The
  Glob and Grep tools cannot delete.
- **`Bash(scontrol:*)` unscoped** — `scontrol update` / `requeue` / `hold` all mutate. Only
  `scontrol show` is allowlisted.
- **`cat` / `head` / `tail` / `grep`** — read-only as commands, but the redirection caveat
  makes them a broad write channel, and the Read/Grep tools cover the use case with better
  output. Left out to keep the list short enough to actually audit.
