> **This file is inherited upstream boilerplate and is NOT the documentation for this
> project.** It is kept because it documents the generic snakemake-workflows layout, but
> its instructions are generic and some of them are wrong here.
>
> Start at [`/AGENTS.md`](../AGENTS.md). For launching runs, envs, SLURM and the log
> policy, see [`/docs/running_and_slurm.md`](../docs/running_and_slurm.md).
>
> TODO: as you deviate from the instructions below -- a different env, a different launch
> line, a different profile -- note it here in one line each. Banner inherited docs; do
> not delete them, or you lose upstream's genuine content and its provenance.

---

# Snakemake workflow: {{cookiecutter.project_name}}

[![Snakemake](https://img.shields.io/badge/snakemake-≥{{cookiecutter.min_snakemake_version}}-brightgreen.svg)](https://snakemake.readthedocs.io)


## Authors

* {{cookiecutter.full_name}} (@{{cookiecutter.username}})

## Usage

### Step 1: Install workflow and dependencies

If you simply want to use this workflow, clone the [latest release](https://github.com/{{cookiecutter.username}}/{{cookiecutter.repo_name}}).

    git clone git@github.com:{{cookiecutter.username}}/{{cookiecutter.repo_name}}.git

If you intend to modify and further develop this workflow, fork this repository. Please consider providing any generally applicable modifications via a pull request.

Install snakemake and the workflow's other dependencies via conda/mamba. If conda/mamba isn't already installed, I recommend [installing miniconda](https://docs.conda.io/en/latest/miniconda.html) and then [install mamba](https://github.com/mamba-org/mamba) in your base environment. Then...

    # move to the snakemake's working directory
    cd {{cookiecutter.repo_name}}/code
    # Create environment for the snakemake
    mamba env create -f envs/{{ cookiecutter.repo_name }}.yaml
    # And activate the enviroment
    conda activate {{ cookiecutter.repo_name }}

### Step 2: Configure workflow

Configure the workflow according to your needs via editing the file `config/config.yaml`. Use/modify the config yaml files in the `snakemake_profiles/slurm/` profile to run on UChicago RCC Midway with slurm scheduler.

### Step 3: Execute workflow

Test your configuration by performing a dry-run via

    snakemake -n

Note that a dry run is not free: `rules/common.smk` executes at parse time and creates
submodule script symlinks on disk.

Execute the workflow locally via

    snakemake --cores $N

using `$N` cores, or submit to SLURM via the included profile, which sets the executor,
account, partition, retries and log destination -- do not re-pass those flags.

    snakemake --profile snakemake_profiles/slurm -n     # dry run, as SLURM would see it
    snakemake --profile snakemake_profiles/slurm        # submit

The profile requires Snakemake >= 8 and `snakemake-executor-plugin-slurm`; both are in the
driver env `envs/{{ cookiecutter.repo_name }}.yaml`. Per-rule resource overrides go in the
`set-resources:` block of `snakemake_profiles/slurm/config.yaml`.

See the [Snakemake documentation](https://snakemake.readthedocs.io) for further details.
