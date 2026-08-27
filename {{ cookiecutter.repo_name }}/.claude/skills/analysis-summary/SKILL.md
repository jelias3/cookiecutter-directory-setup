---
name: analysis-summary
description: >
  Document and clean up an analysis/ directory in this repo. Use when asked to write a
  SUMMARY.md / conclusion doc for a dated analysis folder (analysis/<YY>_<MM>_<DD>_<topic>),
  summarize what its notebook(s) concluded, embed their figures, fix broken references, and
  tidy clutter. Produces a story-like, lab-notebook SUMMARY.md with YAML front matter, plus
  compact WebP figures, and updates the analysis index.
---

# analysis-summary

Turns one `analysis/<YY>_<MM>_<DD>_<topic>/` directory into a clean, documented,
reproducible unit: a narrative `SUMMARY.md`, embedded figures, fixed references, removed
clutter.

**The user runs notebooks manually. Never execute a notebook headlessly here** — not with
`jupyter nbconvert --execute`, not with `papermill`, not with `runipy`. Re-running can
change results, and the stored outputs are the record you are documenting.

Bundled helper: `scripts/notebook_figures.py` (`list` / `inject` / `extract`). It only
edits notebook source and reads stored outputs; it never starts a kernel.
Template: `analysis/_TEMPLATE_SUMMARY.md`. Conventions: `analysis/README.md`.

## Workflow (one directory at a time)

### 1. Inventory

List the directory. Identify the notebook(s), the conda env they need (named in the
notebook's Env cell, or in `analysis/README.md`), any existing `.md`, and the clutter:
`.ipynb_checkpoints/`, `__pycache__/`, stale standalone plot PNGs, `Untitled*.ipynb`,
scratch dirs, regenerable intermediates.

Check the directory name against the rule in `analysis/README.md`: zero-padded
`<YY>_<MM>_<DD>_<topic>`, lowercase snake_case topic. If it is wrong, say so and offer to
`git mv` it — an unpadded or CamelCase name breaks chronological sorting and the generated
index. **Do not rename without asking.**

### 2. Read, don't re-run

Read each notebook's markdown cells **and its stored outputs** — streams, tables, the
`image/png` payloads — to reconstruct the trajectory. Pull the ACTUAL numbers (medians,
correlations, n, fractions); those go verbatim into the SUMMARY. Do not re-run to read.

### 3. Actively fix problems, don't just note them

If a notebook references a path or file that no longer exists, or has another stale
reference, **fix it at the source**: a surgical, output-preserving edit — a literal string
replace inside the `.ipynb`, never a JSON reformat, never a re-execute. Verify it still
parses:

```bash
python3 -c "import json,sys; json.load(open(sys.argv[1]))" <notebook.ipynb>
```

Record every fix under the SUMMARY's "Cleanup actions".

Rationale, so this does not get skipped: "noted but not fixed" transfers the cost to the
next reader unchanged, and a stale ref inside a notebook stays invisible until someone
re-runs it and gets a confusing error far from the cause.

### 4. Figures (savefig → user re-runs → embed)

1. `python3 .claude/skills/analysis-summary/scripts/notebook_figures.py list <nb>` — see
   which cells make figures, plus a guessed title for each.
2. Choose **descriptive snake_case** names (`gs_distributions`, not `cell_8`).
3. `... inject <nb> --map IDX=name ...` — inserts a `savefig()` helper cell once and a
   `savefig('name')` call before each `plt.show()`. Idempotent (marker-guarded) and
   output-preserving. Use `--dry-run` first on a large notebook.
4. Ask the user to **re-run the notebook manually** in their env. That writes
   `figures/<name>.webp` (falls back to `.png` if WebP is unavailable — matplotlib plus the
   already-present Pillow handle WebP, no extra package needed).
   - Fallback if a notebook will not be re-run: `... extract <nb> --map ...` decodes the
     PNGs already stored in the notebook's outputs and recompresses them to
     `figures/*.webp`, with no re-run at all. Prefer `inject` — `extract` freezes whatever
     was last executed.
5. Limitation: this tool is matplotlib/Python only. For an R or Quarto notebook, save
   figures by hand to `figures/<name>.webp` and skip this step.

### 5. Write SUMMARY.md

Copy `analysis/_TEMPLATE_SUMMARY.md` and follow the instruction block inside it. The two
things most likely to be done wrong:

- **Structure.** Each major question is a `##` section phrased as a question; the steps
  taken are `###` beneath it in the order they happened; each step's conclusion sits
  directly under that step, bolded. It is a narrative, not a findings list — a findings
  list loses the reasoning, which is the only thing that does not survive elsewhere.
- **Front matter.** `title` / `date` / `description` at the very top of the file, before
  anything else (front matter is only recognized at position zero). `description` is the
  headline: the actual numeric conclusion, negative results included. It is what the index
  shows and often the only line anyone reads. No number in it means the analysis is
  unfinished.

Tables of real numbers. Figures embedded under the relevant step. Keep the re-run note.
End with "Where this leads", "Outputs", "Cleanup actions".

### 6. Clean up

Delete `.ipynb_checkpoints/`, `__pycache__/`, orphan `Untitled*` notebooks, stale
standalone plot exports superseded by `figures/*.webp`, stray SLURM logs (they belong under
repo-root `logs/` — see `docs/running_and_slurm.md`), and regenerable intermediates.

**Keep every real result.** When unsure whether something is regenerable scratch or a real
input, inspect it and **ask before deleting**. Record removals under "Cleanup actions".

### 7. Index

Append or update this directory's entry in the chronological index.

- If `analysis/README.md` has a hand-maintained "Analyses (chronological)" section: append
  an entry at the bottom in the exact shape that file specifies — date, directory link, two
  or three lines on what was done, then **Headline:** with the real numbers.
- If that section says the index is generated by Quarto: **do not edit
  `analysis/README.md`.** The front matter you wrote in step 5 *is* the index entry. Verify
  it renders: `cd analysis && quarto render`.

## Conventions for new notebooks (so this is near-mechanical next time)

- Open with a markdown Purpose / Question / Inputs / Env cell; close with Conclusions.
- Save figures via the `savefig()` helper to `figures/<descriptive>.webp` — never
  `cell_N_plot.png`.
- Keep heavy intermediates out of `analysis/`: compute them under `output/` via the
  pipeline, or into a gitignored `work/` subdirectory.
- One-off data-prep scripts a notebook needs go in `analysis/scripts/`, named after the
  notebook. See `docs/conventions.md`.
