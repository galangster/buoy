"""Checks for round_filter. Run: .venv/bin/python tools/test_round_filter.py

No pytest dependency: plain asserts, one process, non-zero exit on failure.
The orientation calibration test is the important one. Reading the winding per
contour instead of once per font classifies every counter corner as convex.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import ufoLib2

sys.path.insert(0, str(Path(__file__).resolve().parent))

import params  # noqa: E402
from round_filter import (  # noqa: E402
    RoundCornerFilter,
    SwapAlternatesFilter,
    contour_to_segments,
    signed_area,
    tangent_arriving,
    tangent_leaving,
    unit,
)

PKG = Path(__file__).resolve().parent.parent
FLAT_UFO = PKG / "build" / "ufo-flat" / "Inter-Regular.ufo"

FAILURES = []


def rounder(**overrides):
    """A filter carrying the ruled values, with this test's overrides on top.

    ``RoundCornerFilter`` has no defaults for a ruled value, so every caller
    states them. A test that only varies the radii still builds the ruled
    clamp, angle and visual correction.
    """
    return RoundCornerFilter(**{**params.ROUNDING, **overrides})


def check(condition, message):
    if condition:
        print(f"  ok   {message}")
    else:
        print(f"  FAIL {message}")
        FAILURES.append(message)


def square_glyph(font, name, points, width=1000):
    glyph = font.newGlyph(name)
    glyph.width = width
    pen = glyph.getPointPen()
    pen.beginPath()
    for x, y in points:
        pen.addPoint((x, y), "line", False)
    pen.endPath()
    return glyph


CCW_SQUARE = [(0, 0), (1000, 0), (1000, 1000), (0, 1000)]
CW_SQUARE = [(0, 0), (0, 1000), (1000, 1000), (1000, 0)]


def convexity(points, orientation):
    """Convexity of every vertex, using the filter's own rule."""
    anchors = [(x, y, False) for x, y in points]
    n = len(anchors)
    out = []
    for k in range(n):
        p = anchors[k][:2]
        u1 = unit(
            anchors[k - 1][0] - p[0],
            anchors[k - 1][1] - p[1],
        )
        u2 = unit(
            anchors[(k + 1) % n][0] - p[0],
            anchors[(k + 1) % n][1] - p[1],
        )
        cross = u1[0] * u2[1] - u1[1] * u2[0]
        out.append((cross * orientation) < 0)
    return out


def test_orientation_sign():
    print("orientation calibration")
    check(signed_area(CCW_SQUARE) > 0, "signed_area is positive for CCW")
    check(signed_area(CW_SQUARE) < 0, "signed_area is negative for CW")

    if not FLAT_UFO.exists():
        check(False, f"missing {FLAT_UFO}; run tools/build.py flat first")
        return
    font = ufoLib2.Font.open(FLAT_UFO)
    glyph_set = {n: font[n] for n in ("o", "H", "n")}
    orientation = RoundCornerFilter._calibrate_orientation(glyph_set)
    check(orientation == 1, "o's outer contour is CCW, so orientation is +1")

    # The calibrated value is a font-wide constant. Applied per contour it
    # would call every counter corner convex.
    rows = []
    for contour in font["o"]:
        anchors = contour_to_segments(contour)[0]
        xs = [a[0] for a in anchors]
        ys = [a[1] for a in anchors]
        box = (max(xs) - min(xs)) * (max(ys) - min(ys))
        rows.append((box, signed_area(anchors)))
    rows.sort(reverse=True)
    check(len(rows) == 2, f"o has 2 contours (got {len(rows)})")
    check(rows[0][1] > 0, "o's outer contour area is positive")
    check(rows[-1][1] < 0, "o's counter contour area is negative")

    check(
        all(convexity(CCW_SQUARE, orientation)),
        "every corner of a CCW outer square is convex",
    )
    check(
        not any(convexity(CW_SQUARE, orientation)),
        "every corner of a CW counter square is concave",
    )


def test_square_rounds_to_expected_area():
    print("square rounding")
    font = ufoLib2.Font()
    glyph = square_glyph(font, "test.square", CCW_SQUARE)
    stem = 1000.0
    ratio = 0.20
    filt = rounder(
        stem=stem, outer_ratio=ratio, inner_ratio=ratio * 0.6, visual=0.0
    )
    filt.set_context(font, {"test.square": glyph})
    changed = filt.filter(glyph)
    check(changed, "the filter reports a change")
    check(len(glyph[0].points) == 16, "4 corners become 16 points")

    from fontTools.pens.areaPen import AreaPen
    from fontTools.pens.boundsPen import BoundsPen

    area_pen = AreaPen()
    glyph.draw(area_pen)
    radius = stem * ratio
    expected = 1000.0 * 1000.0 - (4.0 - math.pi) * radius * radius
    check(
        abs(abs(area_pen.value) - expected) / expected < 0.002,
        f"area {abs(area_pen.value):.0f} matches a {radius:.0f} unit fillet "
        f"({expected:.0f})",
    )
    bounds_pen = BoundsPen(None)
    glyph.draw(bounds_pen)
    check(
        bounds_pen.bounds == (0, 0, 1000, 1000),
        "the bounding box is unchanged",
    )


def test_stem_end_clamp_reaches_half():
    print("stem end clamp")
    font = ufoLib2.Font()
    # A 200 x 2000 stem. Every corner is convex and square, so the clamp is
    # 0.5 and the two arcs may meet as a semicircle.
    glyph = square_glyph(
        font, "test.stem", [(0, 0), (200, 0), (200, 2000), (0, 2000)]
    )
    filt = rounder(stem=200.0, outer_ratio=1.0, inner_ratio=0.6, visual=0.0)
    filt.set_context(font, {"test.stem": glyph})
    filt.filter(glyph)
    anchors = contour_to_segments(glyph[0])[0]
    ys = sorted({round(a[1], 3) for a in anchors})
    check(
        ys[:2] == [0.0, 100.0] or abs(ys[1] - 100.0) < 0.2,
        f"the cut-back reaches half the 200 unit width (got {ys[:2]})",
    )

    # A 1000 x 100 slab. Its four corners are convex and square too, so the
    # stem-end clamp of 0.5 governs here as well and the cut-back reaches half
    # of the 100 unit side, not the 0.4 the long side would allow.
    font2 = ufoLib2.Font()
    glyph2 = square_glyph(
        font2, "test.wide", [(0, 0), (1000, 0), (1000, 100), (0, 100)]
    )
    filt2 = rounder(stem=100.0, outer_ratio=1.0, inner_ratio=0.6, visual=0.0)
    filt2.set_context(font2, {"test.wide": glyph2})
    filt2.filter(glyph2)
    anchors2 = contour_to_segments(glyph2[0])[0]
    ys2 = sorted({round(a[1], 3) for a in anchors2})
    check(
        abs(ys2[1] - 50.0) < 0.2,
        f"the short side still reaches half (got {ys2[:2]})",
    )


def test_smooth_and_shallow_points_survive():
    print("skip rules")
    font = ufoLib2.Font()
    glyph = font.newGlyph("test.shallow")
    pen = glyph.getPointPen()
    pen.beginPath()
    # A near-straight vertex: 4 degrees of turn, below min_angle.
    for x, y in ((0, 0), (1000, 0), (1900, 63), (1900, 900), (0, 900)):
        pen.addPoint((x, y), "line", False)
    pen.endPath()
    filt = rounder(stem=100.0, outer_ratio=0.2, inner_ratio=0.12)
    filt.set_context(font, {"test.shallow": glyph})
    filt.filter(glyph)
    anchors = contour_to_segments(glyph[0])[0]
    check(
        any(abs(a[0] - 1000.0) < 0.01 and abs(a[1]) < 0.01 for a in anchors),
        "a vertex turning 4 degrees is left alone",
    )


def test_ruled_values_are_required():
    print("ruled values")
    try:
        RoundCornerFilter(outer_ratio=0.5, inner_ratio=0.3)
    except ValueError as error:
        check("stem" in str(error), f"a missing stem raises ValueError ({error})")
    else:
        check(False, "a missing stem was accepted")


def test_tangents():
    print("tangent helpers")
    p0, p1 = (0.0, 0.0), (100.0, 0.0)
    check(
        tangent_leaving(p0, ("line",), p1) == (1.0, 0.0),
        "tangent_leaving follows a line forward",
    )
    check(
        tangent_arriving(p0, ("line",), p1) == (-1.0, 0.0),
        "tangent_arriving points back along a line",
    )
    seg = ("curve", (0.0, 50.0), (100.0, 50.0))
    check(
        tangent_leaving(p0, seg, p1) == (0.0, 1.0),
        "tangent_leaving follows the first handle",
    )
    check(
        tangent_arriving(p0, seg, p1) == (0.0, 1.0),
        "tangent_arriving follows the second handle",
    )


def test_exclusions():
    print("exclusions")
    filt = rounder(stem=190.0)
    font = ufoLib2.Font()
    for name in ("box.a", "block1", "arrowleft", "uni2500", "uni2B05"):
        glyph = square_glyph(font, name, CCW_SQUARE)
        check(filt._excluded(glyph), f"{name} is excluded")
    keep = square_glyph(font, "boxer", CCW_SQUARE)
    check(filt._excluded(keep), "the prefix rule is a prefix, so boxer goes too")

    empty = font.newGlyph("test.empty")
    filt.set_context(font, {"test.empty": empty})
    check(not filt.filter(empty), "a glyph with no contours is skipped")


def test_alternate_swap():
    print("alternate swap")
    if not FLAT_UFO.exists():
        check(False, f"missing {FLAT_UFO}")
        return
    font = ufoLib2.Font.open(FLAT_UFO)
    names = [
        "u", "u.1", "uacute", "uacute.1",
        "four", "four.ss01", "four.tf", "four.tf.ss01",
        "quoteright", "quoteright.ss03", "comma", "comma.ss03",
    ]
    glyph_set = {n: font[n] for n in names}
    before_u = [(p.x, p.y) for p in glyph_set["u"][0].points]
    before_u1 = [(p.x, p.y) for p in glyph_set["u.1"][0].points]
    before_w = glyph_set["quoteright.ss03"].width

    filt = SwapAlternatesFilter(presets="cv02,cv06,ss03")
    filt.set_context(font, glyph_set)
    filt.filter(glyph_set["u"])

    after_u = [(p.x, p.y) for p in glyph_set["u"][0].points]
    check(after_u == before_u1, "u now carries the spurless outline")
    check(
        [(p.x, p.y) for p in glyph_set["u.1"][0].points] == before_u,
        "u.1 keeps the displaced default",
    )
    check(
        glyph_set["quoteright"].width == before_w,
        "the advance width travels with the outline",
    )
    bases = [c.baseGlyph for c in glyph_set["uacute"].components]
    check(
        "u" in bases and "u.1" not in bases,
        f"uacute's component is remapped back to u (got {bases})",
    )
    tf_bases = [c.baseGlyph for c in glyph_set["four.tf"].components]
    check(
        tf_bases == ["four"],
        f"four.tf still points at four (got {tf_bases})",
    )
    comma_bases = [c.baseGlyph for c in glyph_set["comma"].components]
    check(
        comma_bases == ["quoteright"],
        f"comma still points at quoteright (got {comma_bases})",
    )


def main():
    for fn in (
        test_orientation_sign,
        test_square_rounds_to_expected_area,
        test_stem_end_clamp_reaches_half,
        test_smooth_and_shallow_points_survive,
        test_ruled_values_are_required,
        test_tangents,
        test_exclusions,
        test_alternate_swap,
    ):
        fn()
    print()
    if FAILURES:
        print(f"{len(FAILURES)} FAILURES")
        for message in FAILURES:
            print("  -", message)
        return 1
    print("all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
