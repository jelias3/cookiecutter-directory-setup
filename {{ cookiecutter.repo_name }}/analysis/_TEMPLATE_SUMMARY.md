---
title: "<The question this analysis answers, phrased as a question>"
date: "<YYYY-MM-DD of the conclusion; must match the directory's date prefix>"
description: "<THE HEADLINE. The actual numeric conclusion in one or two sentences. Negative results count and are often the most valuable. If there is no number here, the analysis is not finished.>"
categories: [<optional tags, e.g. splicing, qc, method-comparison>]
---

<!--
  Copy this file to <analysis_dir>/SUMMARY.md and fill it in.
  Directory naming rule: see analysis/README.md (zero-padded YY_MM_DD_topic).

  GOAL: a story-like, lab-notebook record of what the notebook(s) in this directory set out
  to answer, the steps taken, and what each step concluded -- so the reasoning survives
  without re-reading or re-running the notebook.

  STRUCTURE -- this is the part that gets done wrong:
    - Each MAJOR QUESTION is its own `##` section, phrased as a question.
    - Beneath it, the STEPS taken to answer it are `###` subsections, in the order they
      actually happened, including the ones that failed.
    - Beneath each step, give that step's CONCLUSION right there, bolded -- not collected
      at the end.
    - Write it as a NARRATIVE: what we tried, what it showed, what that prompted next. A
      bulleted list of findings is not a summary; it is an abstract, and it loses the
      reasoning -- which is the only thing that does not survive somewhere else.
    - Include tables of ACTUAL numbers: medians, correlations, n, fractions. A claim
      without a number in it is not a result. Use LaTeX ($...$) so math renders on GitHub.
    - Depth over brevity: 150-400 lines is normal and correct for a real analysis.

  FIGURES: embed compact WebP under the relevant step with ![desc](figures/<name>.webp).
  Those files are produced by savefig() calls injected into the notebook (the
  `analysis-summary` skill, `notebook_figures.py inject`) and are written when the USER
  re-runs the notebook manually. Keep the re-run note below so the broken-image state is
  explained until that re-run happens.

  CLEANUP: while writing this, ACTIVELY FIX the problems you find rather than only noting
  them -- a broken path, a stale filename, a reference to a file that moved. Fix it at the
  source with a surgical, output-preserving edit (a literal string replace inside the
  .ipynb, never a JSON reformat, never a re-execute), verify the notebook still parses, and
  record what you did under "Cleanup actions". "Noted but not fixed" just transfers the
  cost to the next reader unchanged, and a stale ref inside a notebook stays invisible
  until someone re-runs it and gets a confusing error far from the cause.

  FRONT MATTER: the YAML block below is consumed by the Quarto listing to build the
  chronological index (see analysis/README.md). `description` IS the headline -- the actual
  numeric conclusion, negative results included. It is the only line most readers see.
  Keep the H1 below it as well: the H1 is what makes this file read correctly on GitHub
  when the Quarto site is off.

  Delete this whole comment block once the summary is written.
-->

# <Short title of the analysis>

- **Date(s):** <YYYY-MM-DD, or range>
- **Notebook(s):** `<notebook.ipynb>`
- **Scripts:** `<any .py/.R/.sbatch in this directory>`
- **Conda env:** `<env name>`

<One short paragraph framing the motivation: why this analysis exists and what it was
trying to settle. Define the metrics being computed, precisely. Name the two or three
observations that forced the question.>

> Figures referenced below are written to `figures/` by the notebook's injected `savefig()`
> calls. Re-run `<notebook.ipynb>` (env `<env name>`) to (re)generate them.

## <Major question 1, phrased as a question>

<One line on why this question mattered.>

### <Step: what was done>

<Narrative of the step, with the actual numbers inline.>

**Conclusion:** <what this step showed, and what it meant.>

![<description>](figures/<name>.webp)

### <Step: the next thing done>

<Narrative.>

**Conclusion:** <interpretation.>

## <Major question 2, phrased as a question>

### <Step ...>

**Conclusion:** ...

## Where this leads

<How these outputs feed later work. Cross-link related analysis directories by name. Open
questions, and the natural follow-on. Say explicitly if this supersedes an earlier analysis.>

## Outputs

<Files this notebook wrote, one line each, with the path. Flag which are canonical
(under `output/`) and which are local scratch.>

## Cleanup actions

<What was fixed or removed in this directory during the cleanup pass -- broken paths
fixed, stale artifacts deleted, notebook refs corrected. Be specific.>
