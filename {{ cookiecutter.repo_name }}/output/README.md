# `output/` — canonical pipeline results

**This directory is gitignored except for this file** (`/output/*` plus
`!/output/README.md` in `/.gitignore`). It is regenerable by definition: everything here is
produced by a rule in `code/rules/*.smk` from `data/` plus committed code and config.

> **Note:** some inherited template boilerplate describes `output/` as small and
> git-tracked. In this project it is neither. If you are reading a stale copy of that
> sentence, this file and `/.gitignore` win — see the precedence rule in `/AGENTS.md`.

## Contract

- **Every path here is a declared rule output.** If a file in `output/` was made by hand or
  by a notebook, either wire it into a rule or move it into the analysis directory that
  made it. An undeclared file *looks* canonical and is not, which is how two people end up
  citing different numbers for the same quantity.
- **Layout:** `output/<stage>/<key>/<file>`, where `<key>` is a wildcard value from
  `code/config/samples.tsv` or a registry in `code/config/config.yaml`. Keep the key
  literal — do not prettify a sample name on its way into a path.
- **Notebooks read from here; they do not write here.** Notebook outputs go in the analysis
  directory (`figures/`, small TSVs) or, if they are genuinely a pipeline product, get
  promoted to a rule.
- **Nothing here is the source of truth for a *claim*.** The claim lives in the
  `analysis/*/SUMMARY.md` that interpreted the file. This directory holds the numbers, not
  what they mean.
- **Superseded outputs are a liability.** When a lineage is replaced, either delete it or
  name the canonical one explicitly in `docs/`, in exactly one place. "The newest directory
  is probably the right one" is not a convention; it is a future mistake.

## Canonical outputs

TODO: as soon as there is a result other people load by default, list it here — the exact
path, one line on what it is, and one line on what makes it canonical rather than its
siblings. Keep the list short; if it grows past a handful, it belongs in a `docs/*.md`.
