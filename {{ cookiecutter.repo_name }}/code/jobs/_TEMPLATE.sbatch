#!/bin/bash
# =============================================================================
# _TEMPLATE.sbatch -- house style for hand-written batch jobs in this repo.
#
# THIS IS THE ONE TO COPY. Copy it to code/jobs/<jobname>.sbatch, or into the
# analysis/<YY>_<MM>_<DD>_<topic>/ directory that owns the job -- which is also
# correct, and often better, since the job then travels with its SUMMARY.md.
#
# Do NOT copy an existing job script that predates this template, and do not copy
# one from another project. The parts that matter here are exactly the ones that
# are easy to leave out, and leaving them out fails SILENTLY.
#
# Five things this template exists to enforce:
#   1. set -euo pipefail   -- a failing step fails the job, it is not skipped
#   2. absolute cd "$REPO" -- never depend on the submit directory
#   3. mkdir -p the logdir -- SLURM will NOT create the parent of --output=
#   4. output-presence skip -- a partly-failed array is resubmittable as-is
#   5. echoed provenance   -- the log says what ran, where, on what commit
#
# VALIDATE WITH ONE TASK FIRST:
#   sbatch --array=1     code/jobs/<jobname>.sbatch   # read the log, check the output
#   sbatch --array=2-N   code/jobs/<jobname>.sbatch   # only then commit the rest
# One bad task costs one log. N bad tasks cost an allocation and your afternoon.
#
# See docs/running_and_slurm.md for the log policy and the resume patterns.
# =============================================================================
#SBATCH --job-name=TODO_jobname
#SBATCH --output=logs/TODO_jobname/TODO_jobname_%A_%a.log
#SBATCH --error=logs/TODO_jobname/TODO_jobname_%A_%a.log
#SBATCH --account={{ cookiecutter.slurm_account }}
#SBATCH --partition={{ cookiecutter.slurm_partition }}
#SBATCH --time=TODO_HH:MM:SS
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=TODO_N
#SBATCH --mem=TODO_NG
#SBATCH --array=1-TODO_N
#
# --output and --error point at the SAME file on purpose: one file per task, stdout and
# stderr interleaved in causal order. Two files means reading two files to reconstruct one
# failure. The path is relative to the SUBMIT directory -- which is why you submit from the
# repo root -- and lives under repo-root logs/<jobname>/ per the single log policy.
#
# TODO: replace this block with what this job does and why, in prose. Name its inputs, its
# outputs, and anything about it that would surprise you in six months.

set -euo pipefail

# --- Absolute repo root ------------------------------------------------------------
# Absolute, not $SLURM_SUBMIT_DIR: a job that only works when submitted from the right
# directory is a job that will one day be submitted from the wrong one. This value is
# stamped in at project-generation time.
REPO=TODO_ABSOLUTE_PATH_TO_REPO
cd "$REPO"

JOBNAME=TODO_jobname
mkdir -p "logs/${JOBNAME}"

# --- Array index -> parameters -----------------------------------------------------
# Write the arithmetic out, in a comment, with the resulting grid size. An array whose
# index decode exists only in code is an array nobody can re-derive later.
#
#   TODO example: 4 samples x 3 conditions = 12 tasks
#     T         = SLURM_ARRAY_TASK_ID - 1     -> 0..11
#     sample    = SAMPLES[    T / 3 ]         -> 4 values
#     condition = CONDITIONS[ T % 3 ]         -> 3 values
#   Task 1 is therefore (SAMPLES[0], CONDITIONS[0]) -- that is the one to validate.
#
# Keep --array=1-N above equal to the product, and N_CONDITIONS equal to the array. A mismatch either silently skips work or
# indexes past the end of the array, which under `set -u` is a hard error -- that is the
# GOOD case, and it is why `set -u` is not optional here.
SAMPLES=(TODO_a TODO_b TODO_c TODO_d)
CONDITIONS=(TODO_x TODO_y TODO_z)
N_CONDITIONS=3      # keep equal to the number of CONDITIONS entries above

# Guard against N_CONDITIONS drifting out of sync with the array above -- a silent drift
# here mis-decodes every task's parameters, which is the worst kind of array bug.
#
# NOTE: bash's array-length operator (dollar, brace, hash, NAME) would be the idiomatic
# way to count, and it is deliberately NOT used. This file is a cookiecutter template, and
# Jinja2 reads that operator's brace-hash pair as the start of a comment tag, which breaks
# project generation with "Missing end of comment tag". Do not "simplify" this back.
_n_actual=$(printf '%s\n' "${CONDITIONS[@]}" | wc -l)
if [ "$N_CONDITIONS" -ne "$_n_actual" ]; then
    echo "N_CONDITIONS ($N_CONDITIONS) != number of CONDITIONS entries ($_n_actual)" >&2
    exit 1
fi

T=$((SLURM_ARRAY_TASK_ID - 1))
SAMPLE=${SAMPLES[$(( T / N_CONDITIONS ))]}
CONDITION=${CONDITIONS[$(( T % N_CONDITIONS ))]}

# --- Paths -------------------------------------------------------------------------
# Repo-root-relative, because CWD is the repo root. Reference data comes from the config
# prefix, never a hardcoded path into someone else's directory.
GENOME_PREFIX={{ cookiecutter.genome_prefix }}
IN="data/${SAMPLE}/TODO_input"
OUT_DIR="output/${JOBNAME}/${SAMPLE}"
OUT="${OUT_DIR}/${SAMPLE}_${CONDITION}_TODO.tsv"

mkdir -p "$OUT_DIR"

# --- Provenance: the log must be self-explanatory a year from now -------------------
echo "=== ${JOBNAME} task ${SLURM_ARRAY_TASK_ID}/${SLURM_ARRAY_TASK_COUNT:-?} ==="
echo "date:   $(date -Is)"
echo "host:   $(hostname)   cpus: ${SLURM_CPUS_PER_TASK:-1}   mem: ${SLURM_MEM_PER_NODE:-?}"
echo "repo:   ${REPO}   commit: $(git rev-parse --short HEAD 2>/dev/null || echo 'not a git checkout')"
echo "params: sample=${SAMPLE} condition=${CONDITION}"
echo "in:     ${IN}"
echo "out:    ${OUT}"

# --- Idempotent output-presence skip -----------------------------------------------
# A completed task is skipped on resubmit, so a partially failed array can be re-run with
# the SAME --array range and only the missing tasks do work.
#
# `-s` (exists AND non-empty), not `-e`: a job killed mid-write leaves a zero-byte file,
# and `-e` would treat that as success -- the exact silent failure this guard prevents.
# If your job can leave a NON-empty partial file, write to "${OUT}.tmp" and `mv` it into
# place at the end instead; rename is atomic, a half-written file is not.
if [ -s "$OUT" ]; then
    echo "output already present and non-empty -- skipping"
    exit 0
fi

# --- Environment -------------------------------------------------------------------
# Name the env; do not rely on whatever happened to be active at submit time.
# `conda run` is preferred over `conda activate` in a non-interactive shell, and
# --no-capture-output keeps the tool's stdout streaming into the log rather than being
# buffered until the end.
ENV_NAME=TODO_env

# --- Work --------------------------------------------------------------------------
conda run --no-capture-output -n "$ENV_NAME" \
    TODO_command \
        --input "$IN" \
        --genome-prefix "$GENOME_PREFIX" \
        --threads "${SLURM_CPUS_PER_TASK:-1}" \
        --output "$OUT"

echo "=== done: $(date -Is) ==="
