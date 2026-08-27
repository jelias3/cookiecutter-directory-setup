# `analysis/` — index of exploratory analyses

Each subdirectory is one dated, self-contained investigation, holding the notebook(s), a
narrative `SUMMARY.md`, and a `figures/` directory of compact WebP figures.

**Read the `SUMMARY.md` first.** It is a lab-notebook record of what the analysis set out
to settle, the steps taken, and what each step concluded, with the actual numbers inline —
so the reasoning survives without re-running anything.

## Conventions

- **Directory naming — declared here, referenced everywhere else:**
  `analysis/<YY>_<MM>_<DD>_<topic>/`, **two-digit zero-padded** month and day, `<topic>`
  in lowercase `snake_case`. e.g. `26_08_27_polya_length_vs_splicing`.

  Zero-padding is not cosmetic: it makes `ls` chronological, which is what lets this index
  and the generated site agree without anyone hand-ordering entries. Never `26_8_27`.
  Never `26_08_27_PolyALength`. Never `2026-08-27` or `20260827_121333`.
- **Results live under `output/`, not here.** Anything a Snakemake rule produces is
  canonical in `output/`; notebooks here read from there. A small derived table that only
  one notebook uses may stay local — say so in that directory's `SUMMARY.md`.
- **Figures** are written by an injected `savefig('<name>')` helper to
  `figures/<descriptive_name>.webp`, never as `cell_N_plot.png`. WebP because a hundred
  figures at PNG resolution is a repo you regret; at `dpi=110` it renders fine on GitHub.
- **Notebooks are re-run manually by the user; nothing here is executed headlessly.** Read
  the stored outputs. See `docs/conventions.md` §Notebooks for why.
- **Notebooks** open with a Purpose / Question / Inputs / Env markdown cell and close with
  Conclusions.
- **One-off helper scripts** a notebook needs but the pipeline does not go in
  `analysis/scripts/`, named after the notebook they pair with. See `docs/conventions.md`.
- **Heavy intermediates do not belong here.** Compute them under `output/` via the
  pipeline, or into a gitignored `work/` subdirectory.
- **`.gitignore` here is a deny-all allowlist by extension.** A new file type is silently
  not committed until you add an allow line. Read `analysis/.gitignore` before wondering
  why your file never showed up in `git status`.
- Template for new summaries: [`_TEMPLATE_SUMMARY.md`](_TEMPLATE_SUMMARY.md). The process
  is encoded as the `analysis-summary` skill; `/new-analysis <topic>` creates a correctly
  named directory.
{% if cookiecutter.use_quarto_site == 'y' %}
## Analyses

**The chronological index is generated, not hand-maintained.** `_quarto.yml` builds it
from the YAML front matter (`title`, `date`, `description`) of every
`analysis/*/SUMMARY.md`. Your job when finishing an analysis is to **write good front
matter**, not to edit this file:

- `title` — the question, not the method.
- `date` — `YYYY-MM-DD`, the date of the *conclusion*, matching the directory's date prefix.
- `description` — **the headline: the actual numeric conclusion**, negative results
  included. "We do not reproduce the paper's 7.2 min median; ours is 0.80 min" is a good
  description. "Analysis of splicing rates" is not. This string is the only thing most
  readers will ever see.

Render from this directory with `quarto render`; output lands in `../docs/site/`.

If you find yourself wanting prose *between* entries, that prose belongs in a `docs/*.md`
file, not here.
{% else %}
## Analyses (chronological)

Hand-maintained. **Append a new entry at the bottom when an analysis reaches a
conclusion**, newest last. One entry per directory, in this exact shape:

### YYYY-MM-DD — [`<YY>_<MM>_<DD>_<topic>`](<YY>_<MM>_<DD>_<topic>/SUMMARY.md)

Two or three lines on what this analysis did and on what data. Method-level, not results.

**Headline:** the actual numeric conclusion, in one or two sentences, with real numbers.
State negative results as headlines too — "we do **not** reproduce X", "the advertised
comparison **never happened**", "the signal is **absent**" are the most valuable entries
in this file. *If the headline has no number in it, the analysis is not finished.*

<!-- TODO: delete the example shape above once the first real entry is written. -->

A directory still in progress gets an entry marked *(in progress)* pointing at its
`README.md` or `HYPOTHESES.md` instead of a `SUMMARY.md`, with a "**Headline so far:**".

---

TODO: keep this line accurate — state which directories, if any, lack a `SUMMARY.md`, and why.
{% endif %}
