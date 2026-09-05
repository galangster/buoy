"""Measurements for the Backable rounding sweep.

Three jobs.

``stems``
    Vertical stem width per flat instance UFO, taken as the bounding box width
    of ``I`` and of ``l``. ``I`` is the value the filter consumes.

``compare``
    Ink area delta, point count delta and a self-intersection gate for one
    rounded TTF against the flat baseline TTF of the same weight.

Run ``python tools/measure.py stems`` or ``python tools/measure.py compare``.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from fontTools.pens.areaPen import AreaPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.ttLib import TTFont

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import params  # noqa: E402

PKG = params.PKG

WEIGHTS = params.SWEEP_WEIGHTS
STEMS = params.STEMS
VARIANTS = params.VARIANTS

# The glyph set the ink-area delta is reported over.
AREA_GLYPHS = (
    "H a n d g l o v e s "
    "zero one two three four five six seven eight nine"
).split()


# ---------------------------------------------------------------------------
# stems


def bbox_width(font, glyph_name: str):
    """Bounding box width of one glyph in an already opened UFO."""
    if glyph_name not in font:
        return None
    glyph = font[glyph_name]
    pen = BoundsPen(font)
    glyph.draw(pen)
    if pen.bounds is None:
        return None
    x0, _, x1, _ = pen.bounds
    return x1 - x0


def measure_stems(ufo_dir: Path):
    import ufoLib2

    rows = {}
    for weight in WEIGHTS:
        path = ufo_dir / f"Inter-{weight}.ufo"
        if not path.exists():
            continue
        # One open per instance. Both stems are read off the same object.
        font = ufoLib2.Font.open(path)
        rows[weight] = {
            "I": bbox_width(font, "I"),
            "l": bbox_width(font, "l"),
        }
    return rows


# ---------------------------------------------------------------------------
# TTF measurements


def glyph_metrics(font: TTFont, names=None, area: bool = True):
    """Ink area and point count per glyph.

    ``area=False`` skips the ``AreaPen``, which is the whole cost of this
    function. The whole-font pass consumes point counts only, so it runs an
    area pen over several thousand glyphs for nothing otherwise.
    """
    glyph_set = font.getGlyphSet()
    glyf = font["glyf"]
    out = {}
    for name in names if names is not None else font.getGlyphOrder():
        if name not in glyph_set:
            continue
        ink = 0.0
        if area:
            pen = AreaPen(glyph_set)
            try:
                glyph_set[name].draw(pen)
            except Exception:  # a malformed glyph must not stop the sweep
                continue
            ink = abs(pen.value)
        n_points = 0
        g = glyf[name]
        if g.numberOfContours > 0:
            n_points = len(g.getCoordinates(glyf)[0])
        out[name] = {"area": ink, "points": n_points}
    return out


def simplify_area_change(font: TTFont, names):
    """Push each glyph through pathops.simplify and report the area change.

    A rounded contour that intersects itself loses area when simplified, so a
    change above the gate means the clamp failed.
    """
    import pathops

    glyph_set = font.getGlyphSet()
    out = {}
    for name in names:
        if name not in glyph_set:
            continue
        path = pathops.Path()
        try:
            glyph_set[name].draw(path.getPen(glyphSet=glyph_set))
        except Exception:
            continue
        try:
            before = abs(path.area)
        except Exception:
            continue
        simplified = pathops.Path()
        try:
            pathops.simplify(path, simplified.getPen(), fix_winding=True)
            after = abs(simplified.area)
        except Exception:
            continue
        if before <= 0:
            continue
        out[name] = 100.0 * (after - before) / before
    return out


def parity(ufo_dir: Path, weight: str, stem: float, outer: float, inner: float,
           alternates: bool = False):
    """Cubic-space integrity gate, measured before cu2qu touches anything.

    Rounding one corner replaces one on-curve point with two on-curve points
    and two handles, so the point delta of a glyph is exactly three times the
    number of corners it rounded. Any delta that is not a multiple of three is
    a half-inserted corner. The same test on the compiled TTF is meaningless:
    the cubic to quadratic conversion rewrites every point count.
    """
    import ufoLib2
    from ufo2ft.filters.removeOverlaps import RemoveOverlapsFilter

    from round_filter import RoundCornerFilter, SwapAlternatesFilter

    font = ufoLib2.Font.open(ufo_dir / f"Inter-{weight}.ufo")
    glyph_set = {g.name: g for g in font if len(g)}
    # The release build swaps before it rounds, so the gate must measure the
    # outlines that ship, not the ones the swap displaced.
    if alternates:
        SwapAlternatesFilter(presets=params.ALTERNATES)(font, glyph_set)
    # Overlap removal rewrites point counts on its own, so the baseline is
    # taken after it. Otherwise its deltas would be read as broken corners.
    RemoveOverlapsFilter(backend="pathops")(font, glyph_set)
    before = {n: sum(len(c.points) for c in g) for n, g in glyph_set.items()}

    # Everything the gate does not vary comes from the ruling, never from a
    # filter default.
    filt = RoundCornerFilter(
        **{**params.ROUNDING, "stem": stem, "outer_ratio": outer,
           "inner_ratio": inner}
    )
    modified = filt(font, glyph_set)
    after = {n: sum(len(c.points) for c in g) for n, g in glyph_set.items()}

    deltas = {n: after[n] - before[n] for n in before}
    touched = [n for n in deltas if deltas[n]]
    bad = sorted(n for n in touched if deltas[n] % 3 != 0)
    odd = [n for n in touched if deltas[n] % 2 == 1]
    return {
        "weight": weight,
        "orientation": filt.context.orientation,
        "outline_glyphs": len(before),
        "modified": len(modified),
        "touched": len(touched),
        "corners_rounded": sum(deltas.values()) // 3,
        "point_delta": sum(deltas.values()),
        "not_multiple_of_three": len(bad),
        "not_multiple_of_three_names": bad[:20],
        "odd_delta_glyphs": len(odd),
        "skipped_contours": filt.stats["skipped_contours"],
    }


def compare(flat_dir: Path, variant_dir: Path, weight: str, gate: float = 0.5,
            prefix: str = "Inter"):
    flat_path = flat_dir / f"Inter-{weight}.ttf"
    var_path = variant_dir / f"{prefix}-{weight}.ttf"
    if not flat_path.exists() or not var_path.exists():
        return None
    flat = TTFont(flat_path)
    var = TTFont(var_path)

    flat_area = glyph_metrics(flat, AREA_GLYPHS)
    var_area = glyph_metrics(var, AREA_GLYPHS)
    shared_area = [n for n in AREA_GLYPHS if n in flat_area and n in var_area]
    total_flat = sum(flat_area[n]["area"] for n in shared_area)
    total_var = sum(var_area[n]["area"] for n in shared_area)
    ink_delta = (
        100.0 * (total_var - total_flat) / total_flat if total_flat else 0.0
    )

    # Only point counts are read below, and the twenty ink areas are already
    # measured above, so the whole-font pass never runs an area pen.
    flat_all = glyph_metrics(flat, area=False)
    var_all = glyph_metrics(var, area=False)
    shared_all = [n for n in flat_all if n in var_all]
    pts_flat = sum(flat_all[n]["points"] for n in shared_all)
    pts_var = sum(var_all[n]["points"] for n in shared_all)
    odd = sum(
        1
        for n in shared_all
        if (var_all[n]["points"] - flat_all[n]["points"]) % 2 == 1
    )
    touched = sum(
        1
        for n in shared_all
        if var_all[n]["points"] != flat_all[n]["points"]
    )

    self_int = simplify_area_change(var, shared_all)
    offenders = sorted(
        ((n, v) for n, v in self_int.items() if abs(v) > gate),
        key=lambda kv: -abs(kv[1]),
    )

    return {
        "weight": weight,
        "ink_delta_pct": ink_delta,
        "ink_glyphs": len(shared_area),
        "points_flat": pts_flat,
        "points_rounded": pts_var,
        "points_delta": pts_var - pts_flat,
        "points_delta_pct": (
            100.0 * (pts_var - pts_flat) / pts_flat if pts_flat else 0.0
        ),
        "glyphs_compared": len(shared_all),
        "glyphs_touched": touched,
        "odd_delta_glyphs": odd,
        "self_intersect_gate_pct": gate,
        "self_intersect_offenders": offenders[:25],
        "self_intersect_offender_count": len(offenders),
        "per_glyph_ink": {
            n: 100.0 * (var_area[n]["area"] - flat_area[n]["area"])
            / (flat_area[n]["area"] or 1.0)
            for n in shared_area
        },
    }


# ---------------------------------------------------------------------------


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("stems", "compare", "parity"))
    parser.add_argument("--build", default=str(PKG / "build"))
    parser.add_argument("--ufo-dir", default=None)
    parser.add_argument("--variants", default="A,B,C,D")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    build = Path(args.build)

    if args.mode == "stems":
        ufo_dir = Path(args.ufo_dir) if args.ufo_dir else build / "ufo-flat"
        rows = measure_stems(ufo_dir)
        if args.json:
            print(json.dumps(rows, indent=2))
        else:
            print(f"{'weight':10s} {'I':>8s} {'l':>8s}")
            for weight, row in rows.items():
                print(f"{weight:10s} {row['I']:8.0f} {row['l']:8.0f}")
        return 0

    if args.mode == "parity":
        ufo_dir = Path(args.ufo_dir) if args.ufo_dir else build / "ufo-flat"
        rows = []
        for variant in args.variants.split(","):
            variant = variant.strip()
            if variant not in VARIANTS:
                continue
            spec = VARIANTS[variant]
            for weight in spec["weights"]:
                row = parity(
                    ufo_dir, weight, STEMS[weight],
                    spec["outer_ratio"], spec["inner_ratio"],
                    alternates=spec["alternates"],
                )
                row["variant"] = variant
                rows.append(row)
                print(
                    f"{variant}-{weight:9s} corners={row['corners_rounded']:6d} "
                    f"bad={row['not_multiple_of_three']}",
                    file=sys.stderr, flush=True,
                )
        print(json.dumps(rows, indent=2))
        return 0

    flat = build / "flat"
    results = []
    for variant in args.variants.split(","):
        variant = variant.strip()
        vdir = build / variant
        if not vdir.exists():
            continue
        # The release build carries the shipping family name, the sweep does
        # not, so the baseline is always Inter and the candidate is not.
        prefix = params.FAMILY if variant == "release" else "Inter"
        weights = (
            params.RELEASE_WEIGHTS if variant == "release" else WEIGHTS
        )
        for weight in weights:
            row = compare(flat, vdir, weight, prefix=prefix)
            if row is None:
                continue
            row["variant"] = variant
            results.append(row)
    print(json.dumps(results, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
