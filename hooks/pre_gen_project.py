#!/usr/bin/env python

"""Pre-generation validation of cookiecutter answers.

Every failure here exits 1 with a single actionable line rather than a traceback, so a
typo in an answer does not read like a bug in the template.
"""

import ast
import json
import re
import sys

REPO_REGEX = r"^[_a-zA-Z\-0-9]+$"
SUBMODULE_REGEX = r"^\w+$"


def fail(msg):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def parse_submodules(raw):
    """Return a dict from cookiecutter's `submodules` answer.

    The answer arrives as either a dict (Jinja renders it with str(), i.e. SINGLE quotes,
    which is not valid JSON) or a bare string -- because CLI extra-context values are
    always strings and cookiecutter's apply_overwrites_to_context replaces the dict
    outright instead of merging. Handle both, and handle double-encoding.
    """
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
                fail(
                    "could not parse `submodules`; expected a dict literal such as "
                    '{"rna_seq": {"url": "git@github.com:me/repo.git", "branch": "main"}}\n'
                    f"       got: {text[:200]}"
                )
    fail("`submodules` was nested too deeply; supply a plain dict")


repo_name = "{{ cookiecutter.repo_name }}"
if not re.match(REPO_REGEX, repo_name):
    fail(f"{repo_name!r} is not a valid repo_name (allowed: letters, digits, '_', '-')")

for name, choice in (
    ("use_quarto_site", "{{ cookiecutter.use_quarto_site }}"),
    ("make_conda_env", "{{ cookiecutter.make_conda_env }}"),
):
    if choice not in ("y", "n"):
        fail(f"{name} must be 'y' or 'n', got {choice!r}")

if not "{{ cookiecutter.slurm_account }}".strip():
    fail("slurm_account must not be empty (midway3 requires -A, e.g. pi-yangili1)")

if not "{{ cookiecutter.min_snakemake_version }}".startswith("8"):
    fail(
        "min_snakemake_version must be 8.x: the slurm profile in this template uses "
        "snakemake-executor-plugin-slurm, which requires Snakemake >=8. Got "
        "{{ cookiecutter.min_snakemake_version }}"
    )

submodules = parse_submodules(r"""{{ cookiecutter.submodules }}""")

for name, info in submodules.items():
    if not re.match(SUBMODULE_REGEX, name):
        fail(f"{name!r} is not a valid submodule name (allowed: letters, digits, '_')")
    url = info.get("url") if isinstance(info, dict) else info
    if not url:
        fail(f"submodule {name!r} has no 'url'")
