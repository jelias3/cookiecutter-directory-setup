#!/usr/bin/env python3
"""
notebook_figures.py — figure helpers for the `analysis-summary` skill.

The user RE-RUNS notebooks manually (no headless execution here). This tool only
edits notebook source / reads stored outputs; it never executes a kernel.

Subcommands
-----------
  list    <nb>
      Print every code cell: index, whether it produces a figure, and a guessed
      title (from set_title/suptitle). Use this to choose figure names.

  inject  <nb> [--map IDX=name ...] [--dpi N] [--dry-run]
      Insert a `savefig()` helper cell (once) and a `savefig('<name>')` call before
      each `plt.show()`, so that when the user re-runs the notebook it writes
      figures/<name>.webp next to the notebook. Idempotent and output-preserving.
      Cells not named in --map get `fig_cell{IDX}`.

  extract <nb> [--out figures] [--map IDX=name ...] [--max-px N]
      FALLBACK for notebooks that won't be re-run: decode the PNG already stored in
      each cell's outputs and recompress to figures/<name>.webp (no re-run).

Names should be descriptive snake_case (e.g. `gs_distributions`), not `cell_8`.
WebP keeps figures small; the helper falls back to PNG if WebP isn't available.
"""
import argparse
import base64
import io
import json
import re
import sys
from pathlib import Path

HELPER_MARKER = "[analysis-summary] figure saver"

HELPER_SOURCE = f"""# {HELPER_MARKER} — writes figures/<name>.webp for SUMMARY.md (re-run to populate)
from pathlib import Path as _Path
_FIGDIR = _Path('figures'); _FIGDIR.mkdir(parents=True, exist_ok=True)
def savefig(name, dpi=110):
    \"\"\"Save the current matplotlib figure to figures/<name> for the SUMMARY.\"\"\"
    import matplotlib.pyplot as _plt
    for _ext in ('webp', 'png'):
        try:
            _p = _FIGDIR / f'{{name}}.{{_ext}}'
            _plt.savefig(_p, dpi=dpi, bbox_inches='tight')
            print(f'[saved] {{_p}}')
            return str(_p)
        except Exception:
            try:
                _p.unlink(missing_ok=True)   # don't leave a 0-byte file SUMMARY.md links to
            except Exception:
                pass
            continue
    raise RuntimeError(f'could not save figure {{name!r}} as webp or png')
"""

TITLE_RE = re.compile(r"""(?:set_title|suptitle)\(\s*[frbu]?["']([^"']{3,80})["']""")
SHOW_RE = re.compile(r"^(\s*)(?:plt|fig|f)\.show\(\s*\)\s*;?\s*$")


def load(nb_path):
    return json.loads(Path(nb_path).read_text(encoding="utf-8"))


def save(nb_path, nb):
    Path(nb_path).write_text(json.dumps(nb, indent=1, ensure_ascii=False) + "\n",
                             encoding="utf-8")


def src(cell):
    s = cell.get("source", [])
    return "".join(s) if isinstance(s, list) else s


def makes_figure(cell):
    if cell.get("cell_type") != "code":
        return False
    if "plt.show(" in src(cell) or "savefig(" in src(cell):
        return True
    for o in cell.get("outputs", []):
        if "image/png" in (o.get("data") or {}):
            return True
    return False


def guess_title(cell):
    m = TITLE_RE.search(src(cell))
    return m.group(1) if m else ""


def parse_map(pairs):
    out = {}
    for p in pairs or []:
        if "=" not in p:
            sys.exit(f"--map entry must be IDX=name, got {p!r}")
        i, name = p.split("=", 1)
        out[int(i)] = name.strip()
    return out


def cmd_list(args):
    nb = load(args.notebook)
    for i, cell in enumerate(nb["cells"]):
        if cell.get("cell_type") != "code":
            continue
        fig = makes_figure(cell)
        flag = "FIG" if fig else "   "
        title = guess_title(cell) if fig else ""
        first = (src(cell).strip().splitlines() or [""])[0][:60]
        print(f"[{i:3}] {flag}  {title or first}")


def cmd_inject(args):
    nb = load(args.notebook)
    name_map = parse_map(args.map)
    changed = []

    # Pass 1: insert savefig() before plt.show() in figure cells (original indices).
    for i, cell in enumerate(nb["cells"]):
        if cell.get("cell_type") != "code" or not makes_figure(cell):
            continue
        if "savefig(" in src(cell):
            continue  # already injected
        name = name_map.get(i) or (re.sub(r"[^a-z0-9]+", "_", guess_title(cell).lower()).strip("_")
                                   if guess_title(cell) else "") or f"fig_cell{i}"
        lines = cell["source"] if isinstance(cell["source"], list) else [cell["source"]]
        new_lines, injected = [], False
        for ln in lines:
            m = SHOW_RE.match(ln)
            if m and not injected:
                new_lines.append(f"{m.group(1)}savefig('{name}')\n")
                injected = True
            new_lines.append(ln)
        if not injected:  # figure cell with no plt.show() -> append at end
            tail = "" if (new_lines and new_lines[-1].endswith("\n")) else "\n"
            new_lines.append(f"{tail}savefig('{name}')")
        cell["source"] = new_lines
        changed.append((i, name))

    # Pass 2: prepend the helper cell once (after the first import cell if present).
    has_helper = any(HELPER_MARKER in src(c) for c in nb["cells"])
    if not has_helper:
        helper = {"cell_type": "code", "metadata": {}, "execution_count": None,
                  "outputs": [], "source": HELPER_SOURCE.splitlines(keepends=True)}
        insert_at = 0
        for i, c in enumerate(nb["cells"][:6]):
            if c.get("cell_type") == "code" and "import matplotlib" in src(c):
                insert_at = i + 1
                break
        nb["cells"].insert(insert_at, helper)

    print(f"helper cell: {'added' if not has_helper else 'already present'}")
    for i, name in changed:
        print(f"  cell {i:3} -> savefig('{name}')")
    if not changed:
        print("  (no new savefig calls; already injected?)")
    if args.dry_run:
        print("dry-run: notebook NOT written")
        return
    save(args.notebook, nb)
    print(f"wrote {args.notebook} — re-run it manually to populate figures/")


def cmd_extract(args):
    nb = load(args.notebook)
    name_map = parse_map(args.map)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    try:
        from PIL import Image
    except ImportError:
        sys.exit("extract needs Pillow (PIL) in the active env")
    n = 0
    for i, cell in enumerate(nb["cells"]):
        if cell.get("cell_type") != "code":
            continue
        png = None
        for o in cell.get("outputs", []):
            d = o.get("data") or {}
            if "image/png" in d:
                png = d["image/png"]  # keep last
        if png is None:
            continue
        name = name_map.get(i) or f"fig_cell{i}"
        raw = base64.b64decode("".join(png) if isinstance(png, list) else png)
        img = Image.open(io.BytesIO(raw)).convert("RGB")
        if args.max_px and max(img.size) > args.max_px:
            scale = args.max_px / max(img.size)
            img = img.resize((round(img.size[0] * scale), round(img.size[1] * scale)))
        dest = out / f"{name}.webp"
        img.save(dest, "WEBP", quality=80, method=6)
        print(f"  cell {i:3} -> {dest}")
        n += 1
    print(f"extracted {n} figure(s) to {out}/")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("list"); p.add_argument("notebook"); p.set_defaults(fn=cmd_list)

    p = sub.add_parser("inject")
    p.add_argument("notebook")
    p.add_argument("--map", nargs="*", help="IDX=name pairs")
    p.add_argument("--dpi", type=int, default=110)
    p.add_argument("--dry-run", action="store_true")
    p.set_defaults(fn=cmd_inject)

    p = sub.add_parser("extract")
    p.add_argument("notebook")
    p.add_argument("--out", default="figures")
    p.add_argument("--map", nargs="*", help="IDX=name pairs")
    p.add_argument("--max-px", type=int, default=1600, help="downscale longest side to N px")
    p.set_defaults(fn=cmd_extract)

    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
