#!/usr/bin/env python

"""Post-generation hook.

Step order is load-bearing:

  1. prune optional files      -- before anything is staged
  2. finalize LICENSE          -- cheap, no side effects
  3. stamp the repo path       -- into code/jobs/_TEMPLATE.sbatch
  4. git init + submodules     -- submodule configs must exist for step 5
  5. splice submodule blocks   -- into code/Snakefile and code/config/config.yaml
  6. driver conda env          -- LAST, and never fatal

Step 6 is last and non-fatal on purpose. Cookiecutter deletes the entire generated tree
when a post-gen hook exits nonzero (unless --keep-project-on-failure), so a transient
solver failure on a 60-package env used to throw the whole scaffold away. It also used to
`sys.exit(os.system(...))` here, which (a) returned before steps 5 ran, leaving literal
SUBMODULE_*_PLACEHOLDER text in the generated Snakefile, and (b) exited with a wait-status
(exit<<8), so a conda failure of 1 became sys.exit(256), which POSIX truncates to 0 --
reporting failure as success.
"""

import ast
import json
import os
import shutil
import subprocess
import sys

REPO_NAME = "{{ cookiecutter.repo_name }}"
USE_QUARTO = "{{ cookiecutter.use_quarto_site }}" == "y"
MAKE_CONDA_ENV = "{{ cookiecutter.make_conda_env }}" == "y"

QUARTO_ONLY_PATHS = [
    os.path.join("analysis", "_quarto.yml"),
    os.path.join("analysis", "index.qmd"),
    os.path.join("analysis", "styles.css"),
    # Guarded by exists(); listed so the prune stays correct if these ever come back.
    os.path.join("analysis", "about.qmd"),
    os.path.join("analysis", "license.qmd"),
    os.path.join("analysis", f"{REPO_NAME}.Rproj"),
]


def fail(msg):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def warn(msg):
    print(f"WARNING: {msg}", file=sys.stderr)


def indent_lines(text, indent="    "):
    return "".join(
        f"{indent}{line}" if line.strip() else line
        for line in text.splitlines(keepends=True)
    )


def parse_submodules(raw):
    """Return a dict from cookiecutter's `submodules` answer. See pre_gen_project.py."""
    value = raw
    for _ in range(3):
        if isinstance(value, dict):
            return value
        if not isinstance(value, str):
            fail(f"submodules must be a dict, got {type(value).__name__}")
        text = value.strip()
        if text in ("", "None", "{}"):
            return {}
        try:
            value = ast.literal_eval(text)
        except (ValueError, SyntaxError):
            try:
                value = json.loads(text)
            except json.JSONDecodeError:
                fail(f"could not parse `submodules`: {text[:200]}")
    fail("`submodules` was nested too deeply; supply a plain dict")


def run(cmd, what):
    """Run a command, failing with a readable message instead of a traceback."""
    try:
        subprocess.run(cmd, check=True)
    except FileNotFoundError:
        fail(f"{cmd[0]!r} not found on PATH; needed to {what}")
    except subprocess.CalledProcessError as exc:
        fail(f"failed to {what} (exit {exc.returncode}): {' '.join(cmd)}")


def find_conda_executable():
    for exe in ("mamba", "micromamba", "conda"):
        if shutil.which(exe):
            return exe
    return None


def remove(path):
    if os.path.isdir(path) and not os.path.islink(path):
        shutil.rmtree(path)
    elif os.path.lexists(path):
        os.remove(path)
    else:
        return False
    return True


submodules = parse_submodules(r"""{{ cookiecutter.submodules }}""")

# ---------------------------------------------------------------- 1. prune
if not USE_QUARTO:
    removed = [p for p in QUARTO_ONLY_PATHS if remove(p)]
    if removed:
        print(
            "use_quarto_site=n: removed Quarto scaffolding "
            f"({', '.join(sorted(removed))})"
        )

# ------------------------------------------------------------- 2. LICENSE
# The LICENSE template is a Jinja conditional over cookiecutter.license. The 'None'
# branch renders a sentinel instead of license text; drop the file in that case.
if os.path.exists("LICENSE"):
    with open("LICENSE") as fh:
        license_text = fh.read()
    if "NO_LICENSE_CHOSEN" in license_text:
        os.remove("LICENSE")
        print("license=None: no LICENSE file written.")
    else:
        with open("LICENSE", "w") as fh:
            fh.write(license_text.strip() + "\n")

# ------------------------------------------------------- 3. stamp repo path
# Hand-written sbatch scripts cd to an absolute repo root rather than trusting
# $SLURM_SUBMIT_DIR. The hook runs inside the generated project, so os.getcwd() is it.
sbatch_template = os.path.join("code", "jobs", "_TEMPLATE.sbatch")
if os.path.exists(sbatch_template):
    with open(sbatch_template) as fh:
        text = fh.read()
    with open(sbatch_template, "w") as fh:
        fh.write(text.replace("TODO_ABSOLUTE_PATH_TO_REPO", os.getcwd()))

# ------------------------------------------------- 4. git init + submodules
run(["git", "init"], "initialize the git repository")

for name, info in submodules.items():
    url = info.get("url") if isinstance(info, dict) else info
    branch = info.get("branch") if isinstance(info, dict) else None
    dest = os.path.join("code", "module_workflows", name)
    cmd = ["git", "submodule", "add"]
    if branch:
        cmd += ["-b", branch]
    cmd += [url, dest]
    run(cmd, f"add submodule {name!r} from {url}")

if submodules:
    run(
        ["git", "submodule", "update", "--init", "--recursive"],
        "check out submodules",
    )
    print(f"Git repository initialized with {len(submodules)} submodule(s).")
else:
    print("Git repository initialized.")

# ------------------------------------- 5. splice submodule blocks (in Python)
# Done in Python rather than Jinja: under `--no-input` a dict passed on the CLI arrives
# as a *string*, and a Jinja for-loop over a string iterates its CHARACTERS -- which
# silently emitted one garbage module block per character. (Note this file is itself
# rendered through Jinja by cookiecutter, so a literal Jinja tag in a comment here is a
# syntax error, not a comment.)
snakefile_path = os.path.join("code", "Snakefile")
with open(snakefile_path) as fh:
    snakefile = fh.read()

module_blocks, all_inputs = [], []
for name in submodules:
    module_blocks.append(
        f'''module {name}:
    snakefile: "module_workflows/{name}/Snakefile"
    prefix: "{name}"
    config: config["{name}"]
use rule * from {name} as {name}_*
# Rules in the module may shell out to scripts using paths relative to the module's own
# workdir; symlink them into ours so those paths resolve.
CreateSymlinksOfDir1ContentsIntoDir2("module_workflows/{name}/scripts/", "scripts/")
'''
    )
    all_inputs.append(f"        rules.{name}_all.input,")

snakefile = snakefile.replace(
    "# SUBMODULE_BLOCKS_PLACEHOLDER", "\n".join(module_blocks)
)
snakefile = snakefile.replace(
    "        # ALL_INPUTS_PLACEHOLDER", "\n".join(all_inputs)
)
with open(snakefile_path, "w") as fh:
    fh.write(snakefile)

config_path = os.path.join("code", "config", "config.yaml")
with open(config_path) as fh:
    config_text = fh.read()

config_blocks = []
for name in submodules:
    sub_cfg = os.path.join("code", "module_workflows", name, "config", "config.yaml")
    body = ""
    if os.path.exists(sub_cfg):
        with open(sub_cfg) as fh:
            body = indent_lines(fh.read(), indent="    ")
    else:
        warn(f"{sub_cfg} not found; leaving the {name!r} config block empty")
    config_blocks.append(
        f"""{name}:
    ## {name}-specific config values; these override the workflow-wide values above.
    ## If {name} needs config keys not defined above, copy them in here.
{body}"""
    )

config_text = config_text.replace(
    "# SUBMODULE_CONFIG_PLACEHOLDER", "\n".join(config_blocks)
)
with open(config_path, "w") as fh:
    fh.write(config_text)

# A reindent of a placeholder line would make the exact-string replace above silently
# stop matching, shipping the placeholder text into a real project. Catch that here.
for path, token in (
    (snakefile_path, "SUBMODULE_BLOCKS_PLACEHOLDER"),
    (snakefile_path, "ALL_INPUTS_PLACEHOLDER"),
    (config_path, "SUBMODULE_CONFIG_PLACEHOLDER"),
):
    with open(path) as fh:
        if token in fh.read():
            fail(f"{token} survived substitution in {path}; the template is inconsistent")

# ----------------------------------------------- 6. conda env (never fatal)
if MAKE_CONDA_ENV:
    conda = find_conda_executable()
    env_file = os.path.join("code", "envs", f"{REPO_NAME}.yaml")
    if not conda:
        warn("make_conda_env=y but no mamba/micromamba/conda on PATH; skipping.")
        warn(f"  Create it later with: conda env create -f {env_file}")
    else:
        print(f"Creating conda environment from {env_file} using {conda} ...")
        result = subprocess.run([conda, "env", "create", "-y", "-f", env_file])
        if result.returncode != 0:
            warn(f"{conda} env create failed (exit {result.returncode}).")
            warn("  The project was still generated. Retry the solve manually with:")
            warn(f"    cd {REPO_NAME} && {conda} env create -f {env_file}")
            warn("  On memory-limited login nodes, micromamba solves with less RAM.")

print(f"\nDone. Next: cd {REPO_NAME}/code && snakemake -n")
