# Running the pipeline, and SLURM

Status: CURRENT. Read this before launching a run, debugging a failed job, or writing an
sbatch script.

Cluster: UChicago RCC **midway3**. Account `{{ cookiecutter.slurm_account }}`, default
partition `{{ cookiecutter.slurm_partition }}`.

## 1. Two working directories

| | Snakemake | hand-written sbatch / manual shell |
|---|---|---|
| CWD | **`code/`** | **repo root** |
| repo-root paths | `../output/`, `../logs/`, `../data/` | `output/`, `logs/`, `data/` |
| scripts | `scripts/foo.py` | `code/scripts/foo.py` |

A bare relative path in a Snakemake rule lands inside `code/`. Decide which launcher owns a
path before writing it, and never copy one between the two without re-prefixing.

## 2. The launch line

```bash
cd code
mkdir -p ../logs/snakemake
nohup conda run -n {{ cookiecutter.repo_name }} \
  snakemake --profile snakemake_profiles/slurm \
  -- <targets> &> ../logs/snakemake/<label>_$(date +%Y%m%d_%H%M%S).log &
```

- **The `--` before targets is required.** Without it snakemake consumes the first target as
  the value of the preceding flag, and you get a confusing "no rule to produce" error about
  something you did not ask for.
- `nohup ... &` because real runs last hours and you will lose the SSH session.
- **The profile owns** `executor`, `slurm_account`, `slurm_partition`, `retries`,
  `latency-wait`, `rerun-incomplete`, `keep-going`, the conda frontend and the log
  destination. Do not re-pass any of them; a command-line flag silently overrides the
  profile and then the next person cannot reproduce your run from the profile alone.
- **`snakemake -n` is not read-only.** `rules/common.smk` runs at parse time and creates
  submodule script symlinks on disk, and snakemake writes `.snakemake/` metadata and can
  take the workflow lock. Treat a dry run as read-mostly.

## 3. Logs — the single policy

**Every log this project writes lands under repo-root `logs/<name>/`, and nothing outside
`logs/` writes logs at all.** No exceptions. This is the one convention here that exists
purely because the alternative was tried and cost real time: predecessor projects split
logs three ways (repo-root `logs/`, `code/logs/`, and SLURM stderr elsewhere) and ended up
*documenting the split as an apology* instead of fixing it.

```
logs/snakemake/<label>_<YYYYMMDD>_<HHMMSS>.log    the driver's own stdout+stderr (set by
                                                  the launch line, not the profile)
logs/slurm/<rule>/<wildcards>/<jobid>.log         per-job SLURM output (the plugin)
logs/slurm/<rule>/<arrayjob>_<task>.log           per-job, for array jobs
logs/<jobname>/<jobname>_%A_%a.log                hand-written sbatch
```

Three things about the SLURM logs that differ from the old Snakemake 7 profile:

1. **stdout and stderr are merged** into one file per job. There is no way to split them or
   to discard stdout. The old profile set `output: "/dev/null"`, throwing away half of
   every job's diagnostics; do not try to reproduce that.
2. **A successful job's log is deleted; failures are kept.** That is the plugin's default
   and it is what `output: /dev/null` was really reaching for — no accumulation of 100k
   useless files, while the ones you need survive. `--slurm-keep-successful-logs` opts out.
   The profile also sets `slurm-delete-logfiles-older-than: 30` to prune old failures.
3. **The rule and wildcards are in the path, not the filename.** The old profile encoded
   them as `logs/{rule}.{wildcards}.err`; the plugin gives
   `logs/slurm/<rule>/<wildcards>/<jobid>.log`, which is the same information plus the job
   ID. Anything that greps `logs/*.err` needs updating.

The plugin creates its log directories itself. Hand-written sbatch does **not** get that:
see §6.

## 4. Job names in `squeue`

Every job in one snakemake run shares a single SLURM job name — the run's UUID, prefixed
with `{{ cookiecutter.repo_name }}` by the profile. Per-rule job names are not available
with this executor.

The upside is real: `scancel --name <prefix>_<uuid>` kills **exactly one run** and nothing
else, which the old per-rule naming could not do. To find which rule a queued job belongs
to, use the log path (§3) or `sacct -j <jobid> --format=JobID,JobName,State,Elapsed,MaxRSS`.

## 5. Resources and retries

Defaults live in the profile's `default-resources`; per-rule overrides in `set-resources`.

- **`runtime` is in MINUTES**, not `HH:MM:SS`. `runtime: 1080` is 18 hours. This is the
  most likely mistake when porting a rule from the old `cluster-config.yaml`.
- `mem_mb` in megabytes, `cpus_per_task` as an integer. `gres`, `gpu`, `gpu_model` and
  `cpus_per_gpu` are **first-class resources** — set them directly, do not smuggle them
  through `slurm_extra`.
- `slurm_extra` is only for flags the plugin does not manage. It **rejects** `--job-name`,
  `--output`, `--error`, `--account`, `--partition`, `--mem`, `--cpus-per-task`, `--time`,
  `--nodes`, `--qos` and `--constraint`, because it sets those itself.
- **`retries: 3` plus a fixed `runtime` means a timeout burns three more identical
  allocations.** Make retries ask for more, using snakemake's `attempt`:

  ```python
  rule heavy:
      resources:
          mem_mb = lambda wildcards, attempt: min(16000 * attempt, 48000),
          runtime = lambda wildcards, attempt: 240 * attempt,
  ```

  TODO: once you have measured a rule the hard way, record its real memory and runtime here
  in a table. Measured numbers are the most valuable thing in this file and the only ones
  nobody can re-derive without burning the allocations again.

## 6. Hand-written sbatch

**Copy `code/jobs/_TEMPLATE.sbatch`.** Do not copy an older job script, and do not copy one
from another project: the parts that matter are exactly the ones that are easy to leave
out, and leaving them out fails silently. The template enforces five things:

1. `set -euo pipefail` — a failing step fails the job instead of being skipped.
2. An absolute `cd "$REPO"` — never depend on the submit directory.
3. `mkdir -p` the log directory — **SLURM does not create the parent of `--output=`.** It
   silently writes no log, and you debug a job with no output. This is the single most
   common self-inflicted wound here.
4. An output-presence skip — makes a partly-failed array resubmittable with the same
   `--array` range.
5. Echoed provenance — the log says what ran, where, on what commit.

**Validate with one task first:**

```bash
sbatch --array=1 code/jobs/<jobname>.sbatch      # inspect the log, check the output
sbatch --array=2-N code/jobs/<jobname>.sbatch    # only then commit the rest
```

One bad task costs one log. N bad tasks cost an allocation and your afternoon.

## 7. Resume and idempotency

Long jobs get killed by walltime. Design so that a kill loses at most one unit of work:

- **Guard on output presence**, and use `[ -s "$OUT" ]` (exists AND non-empty), not
  `[ -e ]`. A job killed mid-write leaves a zero-byte file, and `-e` treats that as
  success — which is the exact silent failure the guard exists to prevent.
- **Write to a temp file and rename** at the end (`mv "$OUT.tmp" "$OUT"`) if the job can
  leave a non-empty partial file. Rename is atomic on a POSIX filesystem; a half-written
  output that looks complete is worse than no output.
- For a per-item cache, write each item separately and check progress with
  `ls <cache_dir> | wc -l`.

TODO: record this project's own resume mechanisms here as they appear, including how to
check progress on a run that is still going.
