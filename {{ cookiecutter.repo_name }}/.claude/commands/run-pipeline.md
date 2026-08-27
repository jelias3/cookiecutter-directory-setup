---
description: Dry-run the Snakemake pipeline, show the plan, then submit only on approval
argument-hint: [targets or flags]
allowed-tools: Bash, Read
---

Targets/flags requested: **$ARGUMENTS**

Read `docs/running_and_slurm.md` before doing anything in this command.

**Phase 1 — dry run.** From `code/`:

```bash
cd code && snakemake --profile snakemake_profiles/slurm -n -p -- $ARGUMENTS
```

- The `--` before targets is required; without it snakemake consumes the first target as a
  flag value.
- `-n` does not run jobs, but it is **not read-only**: `rules/common.smk` executes at parse
  time (creating submodule script symlinks) and snakemake writes into `.snakemake/`. Expect
  a permission prompt, and do not treat a dry run as free.

**Phase 2 — report, then stop.** Summarize for the user: total jobs, the count per rule,
and anything surprising — a rule you did not expect to fire, an unexpectedly large job
count, or a rule that will rebuild something that already exists (usually an mtime problem;
`--rerun-triggers mtime` is the usual fix, but *say so* rather than adding it silently). If
the dry run errors, diagnose it and stop. **Do not submit.**

**Phase 3 — submit, only after the user explicitly approves.**

```bash
cd code
mkdir -p ../logs/snakemake
nohup conda run -n {{ cookiecutter.repo_name }} \
  snakemake --profile snakemake_profiles/slurm \
  -- $ARGUMENTS &> ../logs/snakemake/<label>_$(date +%Y%m%d_%H%M%S).log &
```

- Pick a short descriptive `<label>`; if this is a retry of an earlier run, version it (`v2`).
- All logs go under repo-root `logs/`. One policy, no exceptions —
  `docs/running_and_slurm.md` §Logs.
- Background it: these runs last hours. Report the driver log path and the `squeue` command
  to watch it. Do not poll in a loop.
