"""Remove fully collapsed line segments from compiled TrueType outlines.

The cubic-to-quadratic conversion can round two consecutive on-curve points to
the same integer coordinate. That creates a zero-length line. Removing the
second point preserves the drawn path, but point indices can also be used by
glyph instructions and point-attached composite components. This module fails
instead of changing an index that another table can observe.
"""

from __future__ import annotations

from array import array

from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._g_l_y_f import GlyphCoordinates

ON_CURVE = 0x01


def _instructions(glyph) -> bytes:
    program = getattr(glyph, "program", None)
    return program.getBytecode() if program is not None else b""


def point_attached_components(font: TTFont) -> list[tuple[str, str, int, int]]:
    """Return every component that aligns points instead of XY coordinates."""
    attached = []
    glyf = font["glyf"]
    for glyph_name in font.getGlyphOrder():
        glyph = glyf[glyph_name]
        if not glyph.isComposite():
            continue
        for component in glyph.components:
            if hasattr(component, "firstPt"):
                attached.append((
                    glyph_name,
                    component.glyphName,
                    component.firstPt,
                    component.secondPt,
                ))
    return attached


def prune_contour(points, flags):
    """Remove consecutive equal on-curve points from one closed contour."""
    points = list(points)
    flags = list(flags)
    removed = 0
    while len(points) > 2:
        duplicate = next((
            index
            for index in range(len(points))
            if flags[index] & ON_CURVE
            and flags[index - 1] & ON_CURVE
            and points[index] == points[index - 1]
        ), None)
        if duplicate is None:
            break
        del points[duplicate]
        del flags[duplicate]
        removed += 1
    if removed and len(points) < 3:
        raise ValueError("collapsed contour would have fewer than three points")
    return points, flags, removed


def degenerate_lines(font: TTFont) -> dict[str, int]:
    """Count fully collapsed on-curve line segments by glyph."""
    glyf = font["glyf"]
    found = {}
    for glyph_name in font.getGlyphOrder():
        glyph = glyf[glyph_name]
        if glyph.isComposite() or glyph.numberOfContours <= 0:
            continue
        coordinates, end_points, flags = glyph.getCoordinates(glyf)
        start = 0
        count = 0
        for end in end_points:
            points = coordinates[start:end + 1]
            contour_flags = flags[start:end + 1]
            count += sum(
                1
                for index in range(len(points))
                if contour_flags[index] & ON_CURVE
                and contour_flags[index - 1] & ON_CURVE
                and points[index] == points[index - 1]
            )
            start = end + 1
        if count:
            found[glyph_name] = count
    return found


def prune_degenerate_lines(font: TTFont) -> dict[str, int]:
    """Prune collapsed lines after rejecting point-index consumers."""
    attached = point_attached_components(font)
    if attached:
        raise ValueError(
            f"cannot reindex glyf points: {len(attached)} point-attached "
            f"components exist, first is {attached[0]}"
        )

    glyf = font["glyf"]
    instructed = [
        glyph_name
        for glyph_name in font.getGlyphOrder()
        if _instructions(glyf[glyph_name])
    ]
    if instructed:
        raise ValueError(
            f"cannot reindex instructed glyphs, first is {instructed[0]}"
        )

    changed = {}
    for glyph_name in font.getGlyphOrder():
        glyph = glyf[glyph_name]
        if glyph.isComposite() or glyph.numberOfContours <= 0:
            continue
        coordinates, end_points, flags = glyph.getCoordinates(glyf)
        new_coordinates = []
        new_flags = []
        new_end_points = []
        start = 0
        removed = 0
        for end in end_points:
            points, contour_flags, count = prune_contour(
                coordinates[start:end + 1], flags[start:end + 1]
            )
            new_coordinates.extend(points)
            new_flags.extend(contour_flags)
            new_end_points.append(len(new_coordinates) - 1)
            removed += count
            start = end + 1
        if not removed:
            continue
        glyph.coordinates = GlyphCoordinates(new_coordinates)
        glyph.flags = array("B", new_flags)
        glyph.endPtsOfContours = new_end_points
        glyph.recalcBounds(glyf)
        changed[glyph_name] = removed

    remaining = degenerate_lines(font)
    if remaining:
        raise ValueError(f"collapsed line cleanup incomplete: {remaining}")
    return changed
