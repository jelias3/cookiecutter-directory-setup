# cookiecutter-directory-setup

Cookiecutter template for Snakemake 8 workflows on UChicago RCC **midway3**, with an
optional [Quarto](https://quarto.org/) site that indexes analysis write-ups.

Forked from [bfairkun/cookiecutter-quarto-smk](https://github.com/bfairkun/cookiecutter-quarto-smk),
which is itself inspired by the
[cookiecutter snakemake project template](https://github.com/snakemake-workflows/cookiecutter-snakemake-workflow)
and the [workflowr](https://jdblischak.github.io/workflowr/articles/wflow-01-getting-started.html)
project layout.

---

### USAGE

```
pip install cookiecutter            # or: mamba install -c conda-forge cookiecutter
cookiecutter gh:jelias3/cookiecutter-directory-setup
```

`gh:jelias3/...` is shorthand for the HTTPS clone URL. To generate from a branch:
`cookiecutter -c <branch> gh:jelias3/cookiecutter-directory-setup`.

To generate into a directory that **already exists** (even an empty one), add `-f`:

```
cookiecutter -f -o /project/yangili1/jelias3 gh:jelias3/cookiecutter-directory-setup
```

Without `-f` cookiecutter raises `OutputDirExistsException`. Note `-f` overwrites files in
place and does **not** remove pre-existing ones, so a partially-populated target yields a
hybrid tree -- check with `find <dir> -mindepth 1 | head` before using it for real.

### Prompts

| Prompt | Default | Notes |
|---|---|---|
| `full_name` / `email` / `username` | Jimmy Elias / jelias3@uchicago.edu / jelias3 | attribution |
| `project_name` | `My project` | human-readable; spaces OK |
| `repo_name` | derived | lowercased, spaces to `_` |
| `min_snakemake_version` | `8.25.5` | must be 8.x -- the SLURM executor plugin requires >=8 |
| `slurm_account` | `pi-yangili1` | midway3 `-A` |
| `slurm_partition` | `caslake` | e.g. `caslake`, `bigmem`, `gpu` |
| `genome_prefix` | `/project2/yangili1/bjf79/ReferenceGenomes/` | written into `code/config/config.yaml` |
| `scratch_dir` | `/scratch/midway3/<username>/` | written into `code/config/config.yaml` |
| `use_quarto_site` | `n` | `y` adds `analysis/_quarto.yml`, `index.qmd`, `styles.css`, rendering to `docs/site/` |
| `make_conda_env` | `n` | `y` runs the (slow) driver-env solve immediately |
| `license` | `MIT` | writes a real `LICENSE`; `None` writes none |
| `submodules` | `{}` | JSON dict of `{name: {url, branch}}` |

After filling the prompts, this will create a project template with the following directory structure:

```
{{ cookiecutter.repo_name }}/
├── AGENTS.md              # routing index for humans and agents (line-budgeted, <=150)
├── CLAUDE.md              # one-line @AGENTS.md import
├── README.md              # thin signpost for GitHub visitors
├── LICENSE                # real, from the `license` prompt (absent if license=None)
├── .claude/
│   ├── settings.json      # committed read-only Bash allowlist
│   ├── commands/          # /new-analysis, /add-sample, /run-pipeline
│   └── skills/analysis-summary/   # SKILL.md + scripts/notebook_figures.py
├── analysis/              # dated investigations: <YY>_<MM>_<DD>_<topic>/
│   ├── README.md          # declares the naming rule; index when Quarto is off
│   ├── _TEMPLATE_SUMMARY.md
│   ├── .gitignore         # deny-all-then-allowlist
│   ├── scripts/           # one-off notebook helpers (not called by Snakemake)
│   ├── _quarto.yml        # only when use_quarto_site=y
│   ├── index.qmd          #   "     "    (listing over */SUMMARY.md)
│   └── styles.css         #   "     "
├── code/
│   ├── Snakefile
│   ├── README.md          # inherited boilerplate, bannered as such
│   ├── config/{config.yaml, samples.tsv}
│   ├── schemas/samples.schema.yaml
│   ├── rules/{common.smk, other.smk}
│   ├── scripts/common/__init__.py
│   ├── jobs/_TEMPLATE.sbatch      # house style for hand-written batch jobs
│   ├── envs/
│   │   ├── {{ cookiecutter.repo_name }}.yaml   # driver env: snakemake + slurm plugin
│   │   ├── r_essentials.yaml
│   │   └── samtools.yaml                       # example per-tool env
│   ├── module_workflows/  # git submodules for shared Snakemake modules
│   ├── logs/
│   ├── scratch/
│   └── snakemake_profiles/slurm/config.yaml    # Snakemake 8 executor-plugin profile
├── data/README.md         # dir is gitignored; the README states the contract
├── output/README.md       #   "
├── logs/README.md         #   "
└── docs/
    ├── README.md          # index with CURRENT/SUPERSEDED/HISTORICAL status tags
    ├── abstract.md
    ├── conventions.md     # layout, samples, agent tooling
    ├── running_and_slurm.md
    └── assets/
```
---

### Guidelines for project organization

The generated project documents its own conventions -- start at its `AGENTS.md`, then
`docs/README.md`. The short version:

- **`code/` is the only committed code.** Run Snakemake from `code/` as the working
  directory. `code/.gitignore` is a deny-all-then-allowlist, so large intermediates there
  are untracked by default and a new file type needs an explicit allow line.
- **`data/`, `output/` and `logs/` are gitignored wholesale**, each keeping exactly one
  committed file: a `README.md` stating that directory's contract. A fresh clone contains
  code, config, docs and analysis prose, and reproduces the rest by running the pipeline.
  (This is a deliberate departure from the upstream template, which described `data/` and
  `output/` as git-tracked. At the data scales these projects reach, that guidance ends in
  a committed BAM.)
- **`analysis/` holds one dated, self-contained directory per investigation** --
  `<YY>_<MM>_<DD>_<topic>/`, zero-padded so `ls` sorts chronologically -- each with a
  narrative `SUMMARY.md` and `figures/*.webp`. Notebooks read from `output/`; they do not
  write there.
- **All logs land under repo-root `logs/<name>/`.** One policy, no exceptions.
- **Reference data and scratch come from config keys** (`genome_prefix`, `scratch_dir`),
  never a hardcoded absolute path.

### SLURM

The profile at `code/snakemake_profiles/slurm/config.yaml` targets **Snakemake >= 8** via
`snakemake-executor-plugin-slurm`. The Snakemake 7 `--cluster`/`--cluster-status`
mechanism, and the four vendored `slurm-*.py` scripts plus `cluster-config.yaml` that
implemented it, are gone.

Porting a rule from an old `cluster-config.yaml`, the things that bite:

- `time: "18:00:00"` becomes `runtime: 1080` -- **minutes**, not `HH:MM:SS`.
- `restart-times` is now `retries`.
- `gres`, `gpu`, `gpu_model` and `cpus_per_gpu` are first-class resources; do not route
  them through `slurm_extra`, which rejects the flags the plugin manages anyway.
- Per-job logs land at `logs/slurm/<rule>/<wildcards>/<jobid>.log`, stdout and stderr
  merged, and a successful job's log is **deleted** (only failures are kept). Anything that
  greps `logs/*.err` needs updating.
- All jobs in one run share one SLURM job name -- the run UUID, prefixed with the repo name.
  Per-rule names are not available, but `scancel --name <prefix>_<uuid>` now kills exactly
  one run.

### Conventions for AI coding agents

Every generated project ships an `AGENTS.md` at its root -- a deliberately line-budgeted
routing index, not a reference manual -- plus a `CLAUDE.md` containing only `@AGENTS.md`,
so Claude Code, Codex and Aider all read the same file. Reference material lives in
`docs/`, which is where new durable facts belong.

It also ships a committed `.claude/` payload: three slash commands, the `analysis-summary`
skill (with a bundled notebook tool that never starts a kernel), and a read-only Bash
allowlist. `.claude/settings.local.json` is gitignored -- share skills, not machine-local
state. See the generated `docs/conventions.md` §Agent tooling for what is deliberately
*omitted* and why.

### Quarto usage (only when `use_quarto_site=y`)

- `analysis/_quarto.yml` configures the site; `analysis/index.qmd` is a **listing** that
  builds a chronological index from the YAML front matter (`title`, `date`, `description`)
  of every `analysis/*/SUMMARY.md`. Adding an analysis requires no edit to any index.
- Render with `quarto render` from `analysis/`. Output lands in **`docs/site/`**, kept
  separate from the hand-written `docs/*.md` so a render never touches prose sources.
- `execute: enabled: false` -- rendering formats notebooks' **stored** outputs and never
  starts a kernel. Notebooks are executed out of band, by Snakemake or by you.

---

Start scripting and documenting your project!
