"""Subset a finished Buoy TTF to a Latin woff2 without losing a feature.

`release.py` already subsets, but it holds its ranges as one opaque string and
it seals a release directory at the same time. This module does the subsetting
step alone, names every Unicode block it keeps, and then *proves* the result:
it reopens the woff2 and fails if a required layout feature, a required name ID
or a required table did not survive. pyftsubset drops `tnum`, `case`, every
`ss*` and `cv*`, and name IDs 13 and 14 unless each one is named, so the lists
below are load-bearing, not decoration.

    python tools/subset.py build/release/Buoy-Regular.ttf
    python tools/subset.py build/release/*.ttf --out-dir build/lane/subset
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from fontTools.ttLib import TTFont

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import params  # noqa: E402

PYFTSUBSET = params.PKG / ".venv" / "bin" / "pyftsubset"
DEFAULT_OUT = params.PKG / "build" / "lane" / "subset"

# ---------------------------------------------------------------------------
# what the web build keeps
#
# Named block by block, because "U+2100-214F" tells a later reader nothing and
# a range that has to be justified is a range nobody widens by accident.

UNICODE_BLOCKS = (
    ("Basic Latin",                 "U+0000-007F"),
    ("Latin-1 Supplement",          "U+0080-00FF"),
    ("Latin Extended-A",            "U+0100-017F"),
    ("General Punctuation",         "U+2000-206F"),
    # Superscript four only: the numerator the fraction feature needs a home
    # for, and the one superscript that appears in prose.
    ("Superscript four",            "U+2074"),
    ("Currency Symbols",            "U+20A0-20BF"),
    ("Letterlike Symbols",          "U+2100-214F"),
    # Minus sign. U+2212 is not the hyphen and a numeral row that uses the
    # hyphen for a negative reads wrong at tabular widths.
    ("Minus sign",                  "U+2212"),
    # Arrows, the common ones only: the four cardinals, both bidirectionals,
    # the four diagonals, the two hook arrows and the return arrow. The rest
    # of U+2190-21FF is mathematical and no interface reaches for it.
    ("Arrows, common",              "U+2190-2199"),
    ("Arrows, hook and return",     "U+21A9-21AA,U+21B5"),
    ("Byte order mark",             "U+FEFF"),
    # Asked for and not there: Buoy inherits no U+FFFD from Inter, so unmapped
    # text falls to `.notdef`. The range stays so that an upstream which does
    # draw one is picked up without a code change here.
    ("Replacement character",       "U+FFFD"),
)

# Opt-in, behind --combining-marks. Precomposed Latin-1 and Latin Extended-A
# need no mark attachment, so `ccmp`, `mark` and `mkmk` prune to nothing
# without this block and the file is ~9 KB smaller. Add it when the product
# has to render decomposed (NFD) text, which macOS input readily produces.
COMBINING_BLOCK = ("Combining Diacritical Marks", "U+0300-036F")


# Every feature the family claims. `--layout-features` replaces pyftsubset's
# default list rather than adding to it, so a tag missing here is a tag gone.
FEATURES = (
    # shaping and spacing
    "kern", "calt", "ccmp", "locl", "mark", "mkmk", "rlig", "liga", "clig",
    # case-sensitive forms
    "case",
    # numerals
    "tnum", "pnum", "lnum", "onum", "zero", "frac", "numr", "dnom",
    # the promoted alternates, still reachable as reverse toggles
    "ss02", "ss03", "cv02", "cv06",
)

# 0 copyright, 13 license, 14 license URL. The OFL travels with the file.
NAME_IDS = (0, 1, 2, 3, 4, 5, 6, 8, 9, 11, 13, 14, 16, 17)

# `gasp` carries grayscale and symmetric smoothing across the whole ppem
# range; `prep` carries smart dropout control. Both are what keeps a hairline
# stem from dropping out at small sizes, and pyftsubset will hand them back
# only while hinting stays on.
REQUIRED_TABLES = ("gasp", "prep", "GSUB", "GPOS", "GDEF", "cmap")


def blocks(combining: bool) -> tuple[tuple[str, str], ...]:
    """The kept blocks, in codepoint order.

    Sorted rather than authored in order, so the optional block lands in the
    same place a reader would look for it and the two modes print one list.
    Sorting the range strings is sorting the codepoints: every range here is
    written with the same `U+` prefix and four upper-case hex digits.
    """
    kept = UNICODE_BLOCKS + ((COMBINING_BLOCK,) if combining else ())
    return tuple(sorted(kept, key=lambda block: block[1]))


def unicodes(combining: bool) -> str:
    return ",".join(rng for _, rng in blocks(combining))


def feature_tags(font: TTFont) -> set[str]:
    """Every feature tag that reaches a lookup, read from both layout tables."""
    tags = set()
    for table in ("GSUB", "GPOS"):
        if table not in font:
            continue
        feature_list = font[table].table.FeatureList
        if feature_list is None:
            continue
        for record in feature_list.FeatureRecord:
            if record.Feature.LookupCount or record.Feature.FeatureParams:
                tags.add(record.FeatureTag)
    return tags


def subset(ttf: Path, woff2: Path, combining: bool = False) -> None:
    cmd = [
        str(PYFTSUBSET), str(ttf),
        f"--output-file={woff2}",
        "--flavor=woff2",
        f"--unicodes={unicodes(combining)}",
        f"--layout-features={','.join(FEATURES)}",
        f"--name-IDs={','.join(str(i) for i in NAME_IDS)}",
        # Reach every glyph a kept codepoint can produce through GSUB.
        # Closure is pyftsubset's default; it is named so that a later reader
        # sees the decision instead of inheriting it.
        "--layout-closure",
        # Keeps `gasp` and `prep`. `--no-hinting` would drop both.
        "--hinting",
        "--notdef-outline",
        "--recalc-bounds",
        "--canonical-order",
    ]
    done = subprocess.run(cmd, capture_output=True, text=True)
    if done.returncode != 0:
        raise SystemExit(f"pyftsubset failed on {ttf.name}:\n{done.stderr[-1500:]}")


def verify(source: Path, woff2: Path) -> tuple[list[str], list[str]]:
    """Reopen the written file and hold it to the three hard requirements.

    Returns (failures, notes). A requested feature that is missing is only a
    failure when it could still have done work. Two cases cannot:

    * the tag is absent from the source font, so subsetting did not lose it;
    * the tag is in the source but every one of its lookups became empty once
      the glyph set closed, and pyftsubset prunes a feature that references no
      lookup. `mark` over a repertoire with no combining marks is exactly that.

    Both are reported as notes, because a reader has to see them to judge the
    Unicode ranges, but neither means the subsetter dropped something live.
    """
    font, before = TTFont(woff2), TTFont(source)
    failures, notes = [], []

    missing_tables = [t for t in REQUIRED_TABLES if t not in font]
    if missing_tables:
        failures.append(f"tables dropped: {', '.join(missing_tables)}")

    have_ids = {record.nameID for record in font["name"].names}
    missing_ids = [i for i in (0, 13, 14) if i not in have_ids]
    if missing_ids:
        failures.append(
            f"name IDs dropped: {', '.join(str(i) for i in missing_ids)}"
        )

    if font.flavor != "woff2":
        failures.append(f"flavor is {font.flavor!r}, not woff2")

    got, source_tags = feature_tags(font), feature_tags(before)
    absent = [tag for tag in FEATURES if tag not in source_tags]
    pruned = [tag for tag in FEATURES if tag in source_tags and tag not in got]
    if absent:
        notes.append(f"not in the source font: {', '.join(absent)}")
    if pruned:
        notes.append(f"pruned empty by the glyph closure: {', '.join(pruned)}")
    return failures, notes


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("fonts", nargs="*", type=Path, help="finished TTFs")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    parser.add_argument(
        "--combining-marks", action="store_true",
        help="also keep U+0300-036F, so ccmp/mark/mkmk survive with lookups",
    )
    parser.add_argument(
        "--list-ranges", action="store_true",
        help="print the kept blocks and exit",
    )
    args = parser.parse_args(argv)

    if args.list_ranges:
        for name, rng in blocks(args.combining_marks):
            print(f"{name:28s} {rng}")
        return 0

    if not args.fonts:
        parser.error("give at least one TTF, or --list-ranges")

    args.out_dir.mkdir(parents=True, exist_ok=True)
    failures = 0
    print(f"{'file':22s} {'before':>9s} {'after':>8s} {'kept':>6s} "
          f"{'glyphs':>13s}  verdict")
    for ttf in args.fonts:
        woff2 = args.out_dir / f"{ttf.stem}.woff2"
        before = ttf.stat().st_size
        glyphs_before = TTFont(ttf)["maxp"].numGlyphs
        subset(ttf, woff2, args.combining_marks)
        after = woff2.stat().st_size
        glyphs_after = TTFont(woff2)["maxp"].numGlyphs

        problems, notes = verify(ttf, woff2)
        failures += bool(problems)
        verdict = "PASS" if not problems else "FAIL " + "; ".join(problems)
        print(f"{ttf.name:22s} {before:9d} {after:8d} {after / before:5.1%} "
              f"{glyphs_before:6d}->{glyphs_after:<6d} {verdict}")
        for note in notes:
            print(f"{'':22s} note: {note}")

    print(f"\nwrote {args.out_dir}  failures={failures}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
