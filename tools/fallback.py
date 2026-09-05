"""Derive the metric-matched `@font-face` fallback overrides for Buoy.

A fallback that is not metric-matched moves the text on the first paint after
the woff2 arrives. `size-adjust` scales the fallback until its average
character is as wide as Buoy's, and the three override descriptors then restate
Buoy's own vertical metrics on top of the scaled fallback, so the line box
never changes height. This is the calculation `next/font/local` performs:

    sizeAdjust  = (buoy.xWidthAvg / buoy.upem) / (fallback.xWidthAvg / fallback.upem)
    ascent      =  buoy.ascent   / (buoy.upem * sizeAdjust)
    descent     = |buoy.descent| / (buoy.upem * sizeAdjust)
    lineGap     =  buoy.lineGap  / (buoy.upem * sizeAdjust)

Only the width metric is contested, and it decides everything, so both readings
are computed and both are written out. See `WIDTH` below.

    python tools/fallback.py                       # writes build/lane/fallback.css
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from fontTools.ttLib import TTFont

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import params  # noqa: E402

DEFAULT_OUT = params.PKG / "build" / "lane" / "fallback.css"

# ---------------------------------------------------------------------------
# WIDTH
#
# `OS/2.xAvgCharWidth` has two incompatible definitions and the two reference
# fonts below carry the older one.
#
# Version 0 of OS/2 defines it as the lowercase alphabet plus the space,
# weighted by their frequency in English. Version 3 redefined it as the plain
# mean of every non-zero advance in the font. Arial reports 904 at 2048 upem
# (0.441) under the old definition. Buoy reports 1309 (0.639) under the new one,
# because it counts 2,987 glyphs including arrows, currency and box-width
# symbols that no running text contains.
#
# Dividing one by the other compares two different measurements and returns
# `size-adjust: 145%`, which would set the fallback nearly half again too wide.
# So the shipped numbers recompute Buoy's width under the version 0 weighting,
# which is the measurement Arial and Helvetica Neue actually report. The raw
# ratio is still printed, as the rejected reading.

# OS/2 version 0, the documented weighting. The values sum to exactly 1000.
V0_WEIGHTS = {
    " ": 166, "a": 64, "b": 14, "c": 27, "d": 35, "e": 100, "f": 20, "g": 14,
    "h": 42, "i": 63, "j": 3, "k": 6, "l": 35, "m": 20, "n": 56, "o": 56,
    "p": 17, "q": 4, "r": 49, "s": 56, "t": 71, "u": 31, "v": 10, "w": 18,
    "x": 3, "y": 18, "z": 2,
}

# Both are system fonts and neither ships with the product, so their metrics
# are constants here. Arial's are the documented ones; Helvetica Neue's are
# read from /System/Library/Fonts/HelveticaNeue.ttc, face 0.
FALLBACKS = (
    {"name": "Arial", "stack": "Arial", "upem": 2048, "x_width_avg": 904},
    {"name": "Helvetica Neue", "stack": "'Helvetica Neue'", "upem": 1000,
     "x_width_avg": 447},
)


def v0_x_width_avg(font: TTFont) -> float:
    """The version 0 average advance, in font units."""
    cmap, hmtx = font.getBestCmap(), font["hmtx"]
    total = 0.0
    for char, weight in V0_WEIGHTS.items():
        name = cmap.get(ord(char))
        if name is None:
            raise SystemExit(f"the font has no glyph for {char!r}")
        total += hmtx[name][0] * weight
    return total / sum(V0_WEIGHTS.values())


def metrics(ttf: Path) -> dict:
    font = TTFont(ttf)
    head, hhea, os2 = font["head"], font["hhea"], font["OS/2"]
    # fsSelection bit 7 asks a renderer to prefer the sTypo metrics. Buoy sets
    # it and its two sets are equal, so hhea is read and the equality asserted
    # rather than the branch being written and never taken.
    use_typo = bool(os2.fsSelection & (1 << 7))
    if use_typo and (hhea.ascender, hhea.descender, hhea.lineGap) != (
        os2.sTypoAscender, os2.sTypoDescender, os2.sTypoLineGap
    ):
        raise SystemExit(
            f"{ttf.name} sets USE_TYPO_METRICS and its hhea and sTypo metrics "
            "disagree; pick one before deriving a fallback from them"
        )
    return {
        "upem": head.unitsPerEm,
        "ascent": hhea.ascender,
        "descent": abs(hhea.descender),
        "line_gap": hhea.lineGap,
        "os2_x_width_avg": os2.xAvgCharWidth,
        "glyphs": font["maxp"].numGlyphs,
        "v0_x_width_avg": v0_x_width_avg(font),
    }


def overrides(buoy: dict, fallback: dict, x_width_avg: float) -> dict:
    size_adjust = (x_width_avg / buoy["upem"]) / (
        fallback["x_width_avg"] / fallback["upem"]
    )
    scaled = buoy["upem"] * size_adjust
    return {
        "size_adjust": size_adjust,
        "ascent": buoy["ascent"] / scaled,
        "descent": buoy["descent"] / scaled,
        "line_gap": buoy["line_gap"] / scaled,
    }


def pct(value: float) -> str:
    return f"{value * 100:.2f}%"


def css(buoy: dict, rows: list[tuple[dict, dict, dict]]) -> str:
    blocks = []
    for fallback, shipped, raw in rows:
        blocks.append(f"""/* Buoy over {fallback['name']}. Rejected reading, the OS/2 v3 mean advance:
   size-adjust {pct(raw['size_adjust'])}, ascent {pct(raw['ascent'])}, descent {pct(raw['descent'])}. */
@font-face {{
  font-family: 'Buoy Fallback';
  src: local({fallback['stack']});
  font-weight: 400 500;
  size-adjust: {pct(shipped['size_adjust'])};
  ascent-override: {pct(shipped['ascent'])};
  descent-override: {pct(shipped['descent'])};
  line-gap-override: {pct(shipped['line_gap'])};
}}""")

    header = f"""/* Metric-matched fallback for Buoy.

   Generated by `tools/fallback.py` from Buoy-Regular.ttf. Do not hand-edit.

   Buoy-Regular is {buoy['upem']} upem, ascent {buoy['ascent']}, descent {buoy['descent']}, line gap {buoy['line_gap']}.
   Its average character width is {buoy['v0_x_width_avg']:.2f}, measured under the OS/2
   version 0 weighting, which is the measurement Arial and Helvetica Neue
   report. The font's own OS/2 field says {buoy['os2_x_width_avg']}, but that is the version 3
   mean over all {buoy['glyphs']:,} glyphs, most of which no running text contains.
   Comparing that number to Arial's oversizes the fallback by about 35%, so it
   is recorded above each block as the rejected reading and used nowhere.

   How to use it
   -------------
   Name 'Buoy Fallback' directly after Buoy, and put the generic last:

       font-family: 'Buoy', 'Buoy Fallback', sans-serif;

   Both blocks declare the same family, so they are one family with two faces.
   The later declaration wins where its `local()` face resolves, and a face
   whose source cannot be found is skipped: macOS takes Helvetica Neue,
   everything else falls back to the Arial block. Adding a third block means
   appending it, not inserting it.

   Pair this with `font-display: swap` on the real Buoy faces. Under `block`
   the fallback is invisible and under `optional` it is permanent, and in
   both cases these overrides do no work.

   Both weights share one set of overrides. Regular and Medium have identical
   vertical metrics and their average widths differ by 1%, which is under the
   threshold where the swap is visible as a reflow. `font-weight: 400 500`
   claims that range so the browser matches Medium to this face instead of
   synthesising a bolder one.
*/"""
    return header + "\n\n" + "\n\n".join(blocks) + "\n"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--font", type=Path,
        default=params.RELEASE_DIR / params.ttf_name("Regular"),
    )
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args(argv)

    buoy = metrics(args.font)
    rows = []
    print(f"{args.font.name}: {buoy['upem']} upem, ascent {buoy['ascent']}, "
          f"descent {buoy['descent']}, line gap {buoy['line_gap']}")
    print(f"  average advance: {buoy['v0_x_width_avg']:.2f} (OS/2 v0 weighting), "
          f"{buoy['os2_x_width_avg']} (the font's own OS/2 field, v3 mean)\n")
    print(f"{'fallback':16s} {'reading':10s} {'size-adjust':>12s} "
          f"{'ascent':>9s} {'descent':>9s} {'line-gap':>9s}")
    for fallback in FALLBACKS:
        shipped = overrides(buoy, fallback, buoy["v0_x_width_avg"])
        raw = overrides(buoy, fallback, buoy["os2_x_width_avg"])
        rows.append((fallback, shipped, raw))
        for label, row in (("shipped", shipped), ("rejected", raw)):
            print(f"{fallback['name']:16s} {label:10s} "
                  f"{pct(row['size_adjust']):>12s} {pct(row['ascent']):>9s} "
                  f"{pct(row['descent']):>9s} {pct(row['line_gap']):>9s}")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(css(buoy, rows))
    print(f"\nwrote {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
