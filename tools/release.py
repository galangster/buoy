"""Subset the finished TTFs to woff2 and seal the release directory.

pyftsubset drops `tnum`, `case`, every `ss*` and `cv*` and name IDs 13 and 14
unless each one is named, so the feature list and the name-ID list here are not
decoration. Sizes are measured after the files are written, never estimated.

    python tools/release.py
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import textwrap
from datetime import date
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

from fontTools.ttLib import TTFont

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import params  # noqa: E402

PYFTSUBSET = params.PKG / ".venv" / "bin" / "pyftsubset"

# Recorded in the manifest, so the order is the order they are written in.
TOOL_PACKAGES = (
    "brotli", "fontbakery", "fontmake", "fonttools", "glyphsLib",
    "skia-pathops", "ufo2ft", "ufoLib2", "uharfbuzz",
)

STACKED_NOTICE = [
    "Copyright (c) 2016 The Inter Project Authors (https://github.com/rsms/inter)",
    "Copyright (c) 2026 MetaDAO (https://metadao.fi)",
    "",
    f"{params.FAMILY} is a modified version of Inter. Inter is a trademark of",
    "Rasmus Andersson and no word of it appears in this family's name.",
    "",
    "This Font Software is licensed under the SIL Open Font License, Version 1.1.",
    "This license is copied below, and is also available with a FAQ at:",
    "https://openfontlicense.org",
]

# The FONTLOG changelog, newest first. OFL-FAQ 4.3 asks a derivative to keep a
# running record of what changed and when. That record is prose a person writes,
# not a value a build derives, so it lives here beside STACKED_NOTICE rather
# than in `params`. One entry per sealed release, dated the day it was sealed.
# Never rewrite an entry; a correction is a new one.
CHANGELOG = (
    (
        "4 September 2026", "1.000", "MetaDAO",
        (
            "First release. Two static weights, Regular 400 and Medium 500, "
            "interpolated from the Inter Roman masters at the text optical "
            "size and then rounded.",
            "Every hard corner is replaced by a tangent circular arc, at radii "
            "that are ratios of the measured stem of that weight, so terminals "
            "stay semicircular at both weights.",
            "Three groups of stylistic alternates are promoted to the default "
            "drawing: the open four, the spurless u, and the round quotes and "
            "commas. Their feature tags survive as reverse toggles back to "
            "Inter's drawings.",
            "The name table, vendor ID, unique font identifier, version and "
            "embedding permission are rewritten. Inter's trademark record is "
            "removed. Inter's vertical metrics are preserved.",
            "No outline is redrawn by hand.",
        ),
    ),
)

# Alphabetical, as the FONTLOG template asks. No email address is published for
# either party, so the E field is omitted rather than invented.
CONTRIBUTORS = (
    (
        "MetaDAO", "https://metadao.fi",
        "Derived Buoy from Inter: the corner rounding, the promotion of the "
        "alternates, the identity and table work, and the release toolchain.",
    ),
    (
        "Rasmus Andersson and the Inter Project Authors",
        "https://github.com/rsms/inter",
        "Designed and maintain Inter, the source of every outline in this "
        "family.",
    ),
)

FONTLOG_WIDTH = 78


def _bullets(notes, marker: str = "- ") -> list[str]:
    indent = " " * len(marker)
    return [
        textwrap.fill(note, FONTLOG_WIDTH,
                      initial_indent=marker, subsequent_indent=indent)
        for note in notes
    ]


def write_fontlog(dist: Path):
    """The OFL FONTLOG, in the layout the OFL-FAQ template uses.

    OFL condition 2 already travels in `OFL.txt`, and `NOTICE.md` records what
    this build did to Inter. Neither one is the running log the FAQ asks a
    derivative to keep, and a downstream author who forks Buoy needs a place to
    add their own entry.
    """
    heading = f"FONTLOG for the {params.FAMILY} font family"
    body = [
        heading,
        "-" * len(heading),
        "",
        textwrap.fill(
            f"This file provides detailed information on the {params.FAMILY} "
            f"font software. This information should be distributed along with "
            f"the {params.FAMILY} fonts and any derivative works.",
            FONTLOG_WIDTH),
        "",
        "",
        "Basic Font Information",
        "----------------------",
        "",
        textwrap.fill(
            f"{params.FAMILY} is a rounded sans in two static weights, Regular "
            f"400 and Medium 500, at 2048 units per em. It is a modified "
            f"version of Inter.", FONTLOG_WIDTH),
        "",
        textwrap.fill(
            "Inter's copyright notice carries no Reserved Font Name, so this "
            "derivative is free to publish under a name of its own. Inter is a "
            "trademark of Rasmus Andersson and no word of it appears in this "
            "family's name.", FONTLOG_WIDTH),
        "",
        "Copyright (c) 2016 The Inter Project Authors (https://github.com/rsms/inter)",
        "Copyright (c) 2026 MetaDAO (https://metadao.fi)",
        "",
        textwrap.fill(
            "This Font Software is licensed under the SIL Open Font License, "
            "Version 1.1. See OFL.txt, which travels with these fonts and "
            "carries both notices above the license text.", FONTLOG_WIDTH),
        "",
        textwrap.fill(
            "What was modified, with which parameters and from which upstream "
            "commit, is recorded in NOTICE.md. Byte counts and SHA-256 digests "
            "for every file are in manifest.json.", FONTLOG_WIDTH),
        "",
        "",
        "ChangeLog",
        "---------",
        "",
    ]
    for when, released, author, notes in CHANGELOG:
        body.append(f"{when} ({author}) {params.FAMILY} Version {released}")
        body.extend(_bullets(notes))
        body.append("")
    body += [
        "",
        "Acknowledgements",
        "----------------",
        "",
        textwrap.fill(
            "If you make modifications be sure to add your name (N), email (E), "
            "web-address (W) and description (D). This list is in alphabetical "
            "order.", FONTLOG_WIDTH),
        "",
    ]
    for name, web, description in CONTRIBUTORS:
        body.append(f"N: {name}")
        body.append(f"W: {web}")
        body.extend(_bullets([description], marker="D: "))
        body.append("")
    text = "\n".join(body).rstrip() + "\n"
    (dist / "FONTLOG.txt").write_text(text)
    return text


def subset(ttf: Path, woff2: Path):
    cmd = [
        str(PYFTSUBSET), str(ttf),
        f"--output-file={woff2}",
        "--flavor=woff2",
        f"--unicodes={params.SUBSET_UNICODES}",
        f"--layout-features={params.SUBSET_FEATURES}",
        f"--name-IDs={params.SUBSET_NAME_IDS}",
        "--notdef-outline",
        "--recalc-bounds",
        "--canonical-order",
    ]
    done = subprocess.run(cmd, capture_output=True, text=True)
    if done.returncode != 0:
        raise SystemExit(f"pyftsubset failed on {ttf.name}:\n{done.stderr[-1500:]}")
    return woff2


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def inter_commit() -> str:
    done = subprocess.run(
        ["git", "-C", str(params.INTER_REPO), "rev-parse", "HEAD"],
        capture_output=True, text=True,
    )
    return done.stdout.strip() if done.returncode == 0 else "unknown"


def tool_versions() -> dict[str, str]:
    """The versions this build actually imported.

    Read from the installed distribution metadata rather than by parsing a
    `pip freeze` subprocess, which reports the whole environment and has to be
    filtered back down to these nine.
    """
    out = {}
    for name in TOOL_PACKAGES:
        try:
            out[name] = version(name)
        except PackageNotFoundError:
            continue
    out["python"] = sys.version.split()[0]
    hb = subprocess.run(["hb-shape", "--version"], capture_output=True, text=True)
    out["harfbuzz"] = hb.stdout.strip().splitlines()[0] if hb.stdout else "unknown"
    return out


def write_ofl(dist: Path):
    source = (params.INTER_REPO / "LICENSE.txt").read_text().splitlines()
    # Everything from the first rule onwards is the OFL 1.1 text itself and is
    # copied byte for byte. Only the notice above it is restacked.
    cut = next(i for i, line in enumerate(source) if line.startswith("-----"))
    text = "\n".join(STACKED_NOTICE + [""] + source[cut:]) + "\n"
    (dist / "OFL.txt").write_text(text)
    return text


def write_notice(dist: Path, versions: dict[str, str], commit: str):
    text = f"""# NOTICE

{params.FAMILY} {params.VERSION} is a modified version of Inter, published by
MetaDAO under the SIL Open Font License, Version 1.1. See `OFL.txt` for the
license and for both copyright notices.

## What was modified

Every hard corner is replaced by a tangent circular arc. Radii are ratios of
the measured stem width of that weight, so terminals stay semicircular at both
weights.

| parameter | value |
| --- | ---: |
| outer radius | {params.OUTER_RATIO} x stem |
| inner radius | {params.INNER_RATIO} x stem |
| stem, Regular / Medium | {params.STYLES["Regular"]["stem"]:.0f} / {params.STYLES["Medium"]["stem"]:.0f} units at 2048 upem |
| minimum corner angle | {params.MIN_ANGLE} degrees |
| visual correction | {params.VISUAL} |
| cut-back clamp, normal / stem end | {params.CLAMP} / {params.CLAMP_STEM_END} |
| weight compensation | none |

Three groups of stylistic alternates become the default drawings: the open
four, the spurless u, and the round quotes and commas. Their feature tags
({params.ALTERNATES.replace(",", ", ")}) still work, now as reverse toggles
back to Inter's drawings.

The name table, vendor ID, unique font identifier, version and embedding
permission are rewritten. Inter's trademark record is removed. Inter's vertical
metrics are preserved exactly, because `next/font/local` derives its fallback
overrides from them.

`gasp` is set to grayscale and symmetric smoothing across the whole range, and
`prep` carries smart dropout control. The fonts are otherwise unhinted.

Nothing else is changed. No outline is redrawn by hand.

## Source

- Inter, https://github.com/rsms/inter, commit `{commit}`.
- Roman masters only, text optical size, instances `Inter Regular` and
  `Inter Medium`.

## Weights

| file | weight | usWeightClass |
| --- | --- | --- |
""" + "".join(
        f"| `{params.woff2_name(w)}` | {w} | {params.STYLES[w]['weight_class']} |\n"
        for w in params.RELEASE_WEIGHTS
    ) + f"""
## Build

Built on {date.today().isoformat()} by `packages/backable-type` in the MetaDAO
workspace. Tool versions:

""" + "".join(f"- {k} {v}\n" for k, v in sorted(versions.items())) + """
Gates and proof: `packages/backable-type/proof/2026-09-04-v1/`.
"""
    (dist / "NOTICE.md").write_text(text)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skip-subset", action="store_true")
    args = parser.parse_args(argv)

    dist = params.DIST_DIR
    dist.mkdir(parents=True, exist_ok=True)

    files = []
    for weight in params.RELEASE_WEIGHTS:
        ttf = params.RELEASE_DIR / params.ttf_name(weight)
        woff2 = params.RELEASE_DIR / params.woff2_name(weight)
        if not args.skip_subset:
            subset(ttf, woff2)
        for path in (ttf, woff2):
            shutil.copy2(path, dist / path.name)
            files.append(dist / path.name)

    versions = tool_versions()
    commit = inter_commit()
    write_ofl(dist)
    write_notice(dist, versions, commit)
    write_fontlog(dist)

    manifest = {
        "family": params.FAMILY,
        "version": params.VERSION,
        "vendor_id": params.VENDOR_ID,
        "built": date.today().isoformat(),
        "source": {
            "upstream": "https://github.com/rsms/inter",
            "commit": commit,
            "instances": {
                w: params.STYLES[w]["instance"] for w in params.RELEASE_WEIGHTS
            },
        },
        "parameters": {
            **params.ROUNDING,
            "stems": {w: params.STYLES[w]["stem"] for w in params.RELEASE_WEIGHTS},
            "alternates_promoted": params.ALTERNATES,
            "weight_compensation": None,
            "hinting": "unhinted, gasp 0x000A over the full range, "
                       "prep smart dropout control",
        },
        "subset": {
            "unicodes": params.SUBSET_UNICODES,
            "layout_features": params.SUBSET_FEATURES,
            "name_ids": params.SUBSET_NAME_IDS,
        },
        "tools": versions,
        "files": [],
    }
    for path in files:
        font = TTFont(path)
        manifest["files"].append({
            "name": path.name,
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
            "glyphs": font["maxp"].numGlyphs,
            "unitsPerEm": font["head"].unitsPerEm,
        })
    for extra in ("OFL.txt", "NOTICE.md", "FONTLOG.txt"):
        path = dist / extra
        manifest["files"].append({
            "name": extra, "bytes": path.stat().st_size, "sha256": sha256(path),
        })
    (dist / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")

    print(f"{'file':28s} {'bytes':>9s}  sha256")
    for row in manifest["files"]:
        print(f"{row['name']:28s} {row['bytes']:9d}  {row['sha256'][:16]}")
    print(f"\nwrote {dist}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
