"""Frozen build parameters for the Buoy typeface.

Every value here is ruled, not chosen at build time. The ruling is
``projects/metadao/decisions/backable-single-typeface.md`` (Nick, 2026-09-04)
and the delegated specimen decisions recorded in the same file.

``build.py``, ``finish.py``, ``measure.py``, ``release.py``, ``proof.py``,
``specimen.py`` and ``shape_proof.py`` read from this module. Nothing else holds
a copy of a parameter. The proof glyph rosters and the one HarfBuzz binary
location live here for the same reason: two modules render them, so neither one
owns them.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
PKG = HERE.parent

# ---------------------------------------------------------------------------
# identity

FAMILY = "Buoy"
VERSION = "1.001"
FONT_REVISION = float(VERSION)  # head.fontRevision follows the version string
VENDOR_ID = "MDAO"
MANUFACTURER = "MetaDAO"
DESIGNER = "MetaDAO"
VENDOR_URL = "https://metadao.fi"

# OFL 1.1 condition 2 keeps the upstream notice. FAQ 3.1 permits adding to it.
COPYRIGHT = (
    "Copyright (c) 2016 The Inter Project Authors "
    "(https://github.com/rsms/inter). Copyright (c) 2026 MetaDAO. "
    "Buoy is a modified version of Inter, licensed under the "
    "SIL Open Font License, Version 1.1."
)
LICENSE = (
    "This Font Software is licensed under the SIL Open Font License, "
    "Version 1.1. This license is available with a FAQ at: "
    "https://openfontlicense.org"
)
LICENSE_URL = "https://openfontlicense.org"

# Inter draws a thicker underline as the weight rises, which makes the two
# files disagree. A family must publish one underline, so both take the value
# Inter gives the Regular instance.
UNDERLINE_THICKNESS = 140

# ---------------------------------------------------------------------------
# source

SOURCE = PKG / "vendor" / "inter" / "src" / "Inter-Roman.glyphspackage"
INTER_REPO = PKG / "vendor" / "inter"

# Copied verbatim from vendor/inter/Makefile targets `static`/`static_ttf`.
INTER_FLAGS = [
    "--verbose", "WARNING",
    "--overlaps-backend", "pathops",
    "--flatten-components",
    "--no-autohint",
    "--production-names",
]

# ---------------------------------------------------------------------------
# the two shipping styles

# stem = bounding box width of `I` in the flat instance UFO, 2048 UPM,
# measured by `measure.py stems`.
STYLES = {
    "Regular": {
        "instance": "Inter Regular",
        "weight_class": 400,
        "stem": 190.0,
        "regular_bit": True,
    },
    "Medium": {
        "instance": "Inter Medium",
        "weight_class": 500,
        "stem": 229.0,
        "regular_bit": True,  # nameID 2 is "Regular" (four-style rule), so the OS/2 REGULAR bit follows it. Ruled 2026-09-04 on fontbakery `opentype/fsselection`.
    },
}
RELEASE_WEIGHTS = tuple(STYLES)

# ---------------------------------------------------------------------------
# rounding, variant C of the spike sweep

OUTER_RATIO = 0.50
INNER_RATIO = 0.30
MIN_ANGLE = 14.0
VISUAL = 0.25
CLAMP = 0.40
CLAMP_STEM_END = 0.50

# Alternates promoted to default. The same tags stay as reverse toggles.
ALTERNATES = "cv02,cv06,ss03"

ROUNDING = {
    "outer_ratio": OUTER_RATIO,
    "inner_ratio": INNER_RATIO,
    "min_angle": MIN_ANGLE,
    "visual": VISUAL,
    "clamp": CLAMP,
    "clamp_stem_end": CLAMP_STEM_END,
}

# ---------------------------------------------------------------------------
# the sweep, kept so the spike sheets still build

SWEEP_WEIGHTS = ("Regular", "Medium", "SemiBold", "Bold")

# Measured the same way as the shipping stems, for the two weights the sweep
# draws but v1 does not publish.
SWEEP_ONLY_STEMS = {"SemiBold": 267.0, "Bold": 306.0}

# One table. A shipping weight's stem is the one in STYLES, never a second copy.
STEMS = {
    **{weight: STYLES[weight]["stem"] for weight in STYLES},
    **SWEEP_ONLY_STEMS,
}

VARIANTS = {
    "A": {"outer_ratio": 0.35, "inner_ratio": 0.21, "weights": SWEEP_WEIGHTS,
          "alternates": False},
    "B": {"outer_ratio": 0.45, "inner_ratio": 0.27, "weights": SWEEP_WEIGHTS,
          "alternates": False},
    "C": {"outer_ratio": OUTER_RATIO, "inner_ratio": INNER_RATIO,
          "weights": SWEEP_WEIGHTS, "alternates": False},
    "D": {"outer_ratio": OUTER_RATIO, "inner_ratio": INNER_RATIO,
          "weights": ("Medium",), "alternates": True},
    # What v1 ships.
    "release": {"outer_ratio": OUTER_RATIO, "inner_ratio": INNER_RATIO,
                "weights": RELEASE_WEIGHTS, "alternates": True},
}

# ---------------------------------------------------------------------------
# directories

BUILD = PKG / "build"
FLAT_DIR = BUILD / "flat"
# fontmake writes the source family name, so the rounded binaries land here
# and `finish.py` writes the renamed fonts one level up, in RELEASE_DIR.
RAW_DIR = BUILD / "release" / "raw"
RELEASE_DIR = BUILD / "release"
DIST_DIR = PKG / "release" / f"v{VERSION}"
PROOF_DIR = PKG / "proof" / "2026-09-05-v1.001"

# ---------------------------------------------------------------------------
# subsetting

PYFTSUBSET = PKG / ".venv" / "bin" / "pyftsubset"

# The web build keeps these blocks, named one by one because a range that has
# to be justified is a range nobody widens by accident. `subset.py` flattens
# them for pyftsubset and proves the result.
SUBSET_BLOCKS = (
    ("Basic Latin",                 "U+0000-007F"),
    ("Latin-1 Supplement",          "U+0080-00FF"),
    ("Latin Extended-A",            "U+0100-017F"),
    ("General Punctuation",         "U+2000-206F"),
    # Superscript four only: the numerator the fraction feature needs a home
    # for, and the one superscript that appears in prose.
    ("Superscript four",            "U+2074"),
    ("Currency Symbols",            "U+20A0-20BF"),
    ("Letterlike Symbols",          "U+2100-214F"),
    # U+2212 is not the hyphen, and a negative set with the hyphen reads wrong
    # at tabular widths.
    ("Minus sign",                  "U+2212"),
    # The four cardinals, both bidirectionals, the four diagonals, the two hook
    # arrows and the return arrow. The rest of U+2190-21FF is mathematical.
    ("Arrows, common",              "U+2190-2199"),
    ("Arrows, hook and return",     "U+21A9-21AA,U+21B5"),
    ("Byte order mark",             "U+FEFF"),
    # Buoy inherits no U+FFFD from Inter, so unmapped text falls to `.notdef`.
    # The range stays so an upstream that draws one is picked up unchanged.
    ("Replacement character",       "U+FFFD"),
)
# Opt-in. Precomposed Latin needs no mark attachment, so `ccmp`, `mark` and
# `mkmk` prune to nothing without this block and the file is ~9 KB smaller.
# Keep it when the product must render decomposed (NFD) text.
SUBSET_COMBINING_BLOCK = ("Combining Diacritical Marks", "U+0300-036F")

# `--layout-features` replaces pyftsubset's default list rather than adding to
# it, so a tag missing here is a tag gone. `tnum`, `case`, `ss*` and `cv*` are
# not in the default list.
SUBSET_FEATURES = (
    "kern", "calt", "ccmp", "locl", "mark", "mkmk", "rlig", "liga", "clig",
    "case",
    "tnum", "pnum", "lnum", "onum", "zero", "frac", "numr", "dnom",
    "ss02", "ss03", "cv02", "cv06",
)
# 0 copyright, 13 license, 14 license URL: the OFL travels with the file.
SUBSET_NAME_IDS = (0, 1, 2, 3, 4, 5, 6, 8, 9, 11, 13, 14, 16, 17)


# ---------------------------------------------------------------------------
# proof glyph rosters
#
# ``specimen.py`` renders the sweep sheets and ``proof.py`` renders the release
# sheets from the same two rosters, so a glyph added to one sheet is on both.

# a g t j y R 4 0 u i ; , " & @
IDENTITY_GLYPHS = ["a", "g", "t", "j", "y", "R", "four", "zero", "u", "i",
                   "semicolon", "comma", "quotedbl", "ampersand", "at"]
# a e g s v w y k B R 4 6 9 0 u
DIFF_GLYPHS = ["a", "e", "g", "s", "v", "w", "y", "k", "B", "R",
               "four", "six", "nine", "zero", "u"]

# ---------------------------------------------------------------------------
# harfbuzz
#
# One location for `hb-view` and `hb-shape`. PATH first, Homebrew's prefix
# second, because a launchd or subprocess environment often carries neither.

_HB_FOUND = shutil.which("hb-view") or shutil.which("hb-shape")
HB_BIN = Path(_HB_FOUND).parent if _HB_FOUND else Path("/opt/homebrew/bin")


def run_hb(tool: str, args, label: str = "") -> str:
    """Run one harfbuzz binary and return its stdout.

    Both proof modules shell out to harfbuzz rather than binding uharfbuzz,
    because the command line is the artefact a reader can re-run by hand.
    """
    cmd = [str(HB_BIN / tool), *(str(a) for a in args)]
    done = subprocess.run(cmd, capture_output=True, text=True)
    if done.returncode != 0:
        where = f" on {label}" if label else ""
        raise RuntimeError(f"{tool} failed{where}: {done.stderr[:400]}")
    return done.stdout


def ttf_name(weight: str) -> str:
    return f"{FAMILY}-{weight}.ttf"


def woff2_name(weight: str) -> str:
    return f"{FAMILY}-{weight}.woff2"


def flat_name(weight: str) -> str:
    return f"Inter-{weight}.ttf"
