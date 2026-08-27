# {{ cookiecutter.project_name }}

TODO: two or three sentences for someone who landed here from GitHub. What question this
project answers, on what data. No layout, no install instructions, no conventions --
those live in the files linked below and will drift if duplicated here.

- **Working index, for humans and agents:** [`AGENTS.md`](AGENTS.md) — start there.
- **Scientific motivation:** [`docs/abstract.md`](docs/abstract.md)
- **Conventions and deep dives:** [`docs/README.md`](docs/README.md)
- **What we already know:** [`analysis/README.md`](analysis/README.md)
- **Running the pipeline:** [`docs/running_and_slurm.md`](docs/running_and_slurm.md)

`data/`, `output/` and `logs/` are gitignored: a fresh clone contains code, config, docs
and analysis notebooks, and reproduces everything else by running the pipeline.

Runs on UChicago RCC midway3 (SLURM, account `{{ cookiecutter.slurm_account }}`,
partition `{{ cookiecutter.slurm_partition }}`).

Author: {{ cookiecutter.full_name }} (<{{ cookiecutter.email }}>)
{%- if cookiecutter.license != 'None' %}
License: {{ cookiecutter.license }} — see [`LICENSE`](LICENSE).
{%- endif %}

Generated from [cookiecutter-directory-setup](https://github.com/{{ cookiecutter.username }}/cookiecutter-directory-setup).

<!-- MAINTAINING THIS FILE: it is a signpost, not documentation. Every fact here that also
     lives in AGENTS.md or docs/ is a fact that will drift out of sync. If you are tempted
     to add a section, add it to docs/ and add a link here -- or don't. Cap: 25 lines. -->
