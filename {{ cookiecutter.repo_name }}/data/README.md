# `data/` — raw inputs

**This directory is gitignored except for this file** (`/data/*` plus `!/data/README.md` in
`/.gitignore`). Nothing else in here is committed, ever. It is not backed up by git: if a
file here is not reproducible from a download command or a path outside the repo, it is not
safe.

## Contract

- **Raw and never edited.** A file in `data/` is exactly what arrived from the sequencer,
  from SRA/ENA, or from a collaborator. If you transformed it, the result belongs in
  `output/`, produced by a rule.
- **One subdirectory per dataset or per sample**, named with the same ID that appears in
  `code/config/samples.tsv`. That ID is the wildcard value which propagates into every
  output path, so the grammar in `docs/conventions.md` §Samples applies here too.
- **Reference genomes and annotations do not live here.** They live under
  `{{ cookiecutter.genome_prefix }}`, referenced from `code/config/config.yaml` as the
  `genome_prefix` key — never hardcoded in a rule, a script, or a notebook. A hardcoded
  absolute path into someone else's directory is the single most common reason an old rule
  stops working, and it fails at the worst time.
- **Large things that are not in the repo must still be findable.** If a dataset lives on
  scratch (`{{ cookiecutter.scratch_dir }}`) or in another project space, record the path
  and the command that fetched it in `docs/` — not only in your shell history.

## How things get here

TODO: name the mechanism. One of: a Snakemake download rule (preferred — it is
self-documenting and re-runnable), an sbatch script under `code/jobs/`, or a manual
transfer. If manual, write down the exact command: "I rsynced it" is not a provenance
record, and a year later it is not even a hint.
