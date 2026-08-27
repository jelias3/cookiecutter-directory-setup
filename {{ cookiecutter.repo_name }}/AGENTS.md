# {{ cookiecutter.project_name }}

TODO: four lines, maximum. What this project measures, on what data, with what methods,
toward what claim. Name the assay and the organism. No background here -- background goes
in `docs/abstract.md`, which this paragraph should end by pointing at. Delete this
instruction block once written.

Scientific motivation: `docs/abstract.md`. Runs on UChicago RCC midway3 (SLURM, account
`{{ cookiecutter.slurm_account }}`, partition `{{ cookiecutter.slurm_partition }}`).

## Coding discipline

- Avoid antipatterns, monolithic coding, spaghetti code, and God objects.
- Prioritize modularity and single responsibility.

## Read this first

**This file is an index, not a reference** -- it holds only what you need *before* you know
what you are doing. If your task touches a row below, open that doc **before** writing code
or commands. Don't infer behavior from source alone, and don't act on a recollection of
this repo that isn't on this page. For anything else in `docs/`, start at `docs/README.md`.

| about to touch | read first |
|---|---|
| where a new file goes; `analysis/scripts/`; layout questions | `docs/conventions.md` |
| launching a run, a failed job, hunting a log, writing sbatch | `docs/running_and_slurm.md` |
| `config/config.yaml`, `config/samples.tsv`, sample IDs | `docs/conventions.md` §Samples |
| "what do we already know about X" | `analysis/README.md` |
| TODO: first subsystem -- `code/rules/<X>.smk`, `output/<X>/**` | TODO: `docs/<x>.md` |
| TODO: any join/merge on genomic coordinates or IDs, once there is one | TODO: `docs/coordinate_conventions.md` |

**When sources disagree, precedence depends on the kind of claim:** *what the code does* →
the code wins, and a doc contradicting it is a bug worth reporting; *a number or empirical
result* → the most recent `analysis/*/SUMMARY.md` that measured it; *a convention or
decision* → `docs/`; *where to look* → this file. Never silently pick a side -- say which
rule you applied.

## Two working directories

| | Snakemake | hand-written sbatch / manual shell |
|---|---|---|
| CWD | **`code/`** | **repo root** |
| repo-root paths | `../output/`, `../logs/`, `../data/` | `output/`, `logs/`, `data/` |
| scripts | `scripts/foo.py` | `code/scripts/foo.py` |

The same script gets invoked both ways, so **decide which launcher owns a path before
writing it, and never copy one between the two without re-prefixing.** A bare relative
path in a rule lands inside `code/`.

## Running the pipeline

```bash
cd code
mkdir -p ../logs/snakemake
nohup conda run -n {{ cookiecutter.repo_name }} \
  snakemake --profile snakemake_profiles/slurm \
  -- <targets> &> ../logs/snakemake/<label>_$(date +%Y%m%d_%H%M%S).log &
```

- **The `--` before targets is required** -- snakemake otherwise consumes the first target
  as a flag value.
- The profile owns executor, account, partition, retries, `latency-wait` and the log
  destination. **Do not re-pass them.** Read `docs/running_and_slurm.md` before adding a flag.
- **`snakemake -n` is not free.** `rules/common.smk` executes at parse time and creates
  submodule script symlinks on disk, and snakemake writes into `.snakemake/`. A dry run is
  read-mostly, not read-only.

## Environments

- `{{ cookiecutter.repo_name }}` -- the driver env: snakemake plus the SLURM executor
  plugin. Created from `code/envs/{{ cookiecutter.repo_name }}.yaml`.
- Per-rule envs are `code/envs/<tool>.yaml`, named in the rule's `conda:` directive and
  created by snakemake. Never `conda activate` inside a rule, and never point `conda:` at
  an absolute path to a prebuilt env -- that path will not exist for anyone else.
- TODO: name the analysis-notebook env here once it exists, and say which env holds which
  hard-to-install dependency. One line each.

## What is actually wired up right now -- verify, don't trust

Every claim in this section must end with the command that recomputes it. A claim without
a command does not belong here.

- TODO: which rule modules are actually `include`d, and what `rule all` really builds.
  → `grep -n '^ *include\|^rule all' code/Snakefile`
- TODO: which submodules are initialized -- an uninitialized one that rules invoke is the
  classic silent failure.
  → `git submodule status`
- TODO: which config keys are set vs blank. A blank key usually means whole rule families
  are inert rather than broken.
  → `grep -n ':' code/config/config.yaml | grep -v '^\s*#'`

## Traps that fail silently

**Admission criteria -- a trap earns one line here only if all three hold:** you would hit
it spontaneously without being warned, **and** it fails *silently* (wrong numbers or fewer
rows, not an exception), **and** it fits on one line. Everything else goes in the relevant
`docs/` file. **Cap: 5 entries.** A sixth entry means demoting one.

- **`analysis/.gitignore` and `code/.gitignore` are deny-all allowlists by extension.** A
  new file type is silently *not committed* until you add an allow line; `git status` will
  not warn you. `git check-ignore -v <path>` names the rule that caught it.
- TODO: your first real trap goes here, with the assertion or print that would have caught it.

## Conventions

- **Analyses:** one dated dir per investigation, `analysis/<YY>_<MM>_<DD>_<topic>/`,
  zero-padded, lowercase snake_case topic. The rule and everything else about that
  directory is declared once in `analysis/README.md` -- read it there, don't restate it.
  Each dir carries a `SUMMARY.md` (template `analysis/_TEMPLATE_SUMMARY.md`, process = the
  `analysis-summary` skill).
- **Notebooks are re-run manually by the user, never headlessly** -- read the stored
  `.ipynb` outputs. Figures go through an injected `savefig()` helper to
  `figures/<name>.webp`, never `cell_N_plot.png`.
- **Results live under `output/`**, not in `analysis/`. `data/`, `output/` and `logs/` are
  gitignored except for their `README.md`.
- **All logs land under repo-root `logs/<name>/`. One policy, no exceptions.** Stated in
  full in `docs/running_and_slurm.md` §Logs.
- **Reference data and scratch come from config keys** (`genome_prefix`, `scratch_dir` in
  `code/config/config.yaml`), never a hardcoded absolute path.
- **ALL-CAPS filenames are documents of record** (`SUMMARY.md`, `HYPOTHESES.md`,
  `TEST_PLAN.md`); a leading `_` marks a template so it sorts first.
- **Commits:** `type(scope): imperative summary`. Bodies carry real numbers and say what
  was *not* changed.
- **Submodules are added with `git submodule add`, never as a bare gitlink** -- a gitlink
  with no `.gitmodules` entry produces a clone nobody can reproduce.

## Maintaining this file

- **Hard budget: 150 lines** (`wc -l AGENTS.md`). An edit that exceeds it must delete or
  demote something in the same edit. A budget with slack is not a budget.
- **New durable facts go in the relevant `docs/` file, not here.** Edit this file only when
  a routing target moves, a top-5 trap changes, or the launch command changes.
- **No rot-prone facts here:** file or sample counts, byte sizes, source line numbers,
  dates, per-dataset status, "currently running" state. State the shape, or the command
  that computes it.
- `CLAUDE.md` is a one-line `@AGENTS.md` import and must stay that way. Substance here.
