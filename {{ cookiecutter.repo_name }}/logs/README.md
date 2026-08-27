# `logs/` — the one and only log destination

**This directory is gitignored except for this file** (`/logs/*` plus `!/logs/README.md` in
`/.gitignore`).

## The policy

**Every log this project writes lands under repo-root `logs/<name>/`, and nothing outside
`logs/` writes logs at all.** One policy, no exceptions. Stated in full in
`docs/running_and_slurm.md` §Logs.

```
logs/snakemake/<label>_<YYYYMMDD>_<HHMMSS>.log   the snakemake driver's own stdout+stderr
logs/slurm/<rule>/...                            per-job SLURM output (written by the
                                                 executor plugin; stdout+stderr merged)
logs/<jobname>/<jobname>_%A_%a.log               hand-written sbatch (code/jobs/_TEMPLATE.sbatch)
```

Note the path prefix depends on your CWD: `../logs/...` from `code/` (where snakemake
runs), `logs/...` from the repo root (where hand-written sbatch runs). See `/AGENTS.md`
§Two working directories.

## Why this is written down at all

Because the alternative is what happens by default, and it is expensive. Predecessor
projects in this lab ended up with logs split three ways — repo-root `logs/`, `code/logs/`,
and SLURM stderr in a fourth place — so answering "did this rule produce anything?" meant
checking three directories, and the split ended up *documented as an apology* rather than
fixed. In another, ad-hoc job logs were written beside the scripts in `code/scripts/`,
mixing generated output into tracked source.

**Consequences of the policy, so nobody has to rediscover them:**

- `logs/` is always a directory of directories. A bare `.log` or `.err` at the top level of
  `logs/` is a bug in whatever wrote it. One predecessor's flat `logs/` grew large enough
  that simply listing it was slow.
- A job that writes its log somewhere else is misconfigured, not "using a different
  convention". Fix the `--output=` line.
- **`mkdir -p` the log directory before the job needs it.** SLURM does not create the parent
  of `--output=`; it silently fails to write the log, and you end up debugging a job with no
  output at all. `code/jobs/_TEMPLATE.sbatch` does this in-script for exactly this reason.
- Nothing here is committed, so anything worth keeping — a resource number, a failure cause
  — belongs in `docs/` or a `SUMMARY.md`, not in a log you will eventually delete.
