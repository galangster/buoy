"""ufo2ft filters for the Backable rounded derivative of Inter.

Two filters live here.

``RoundCornerFilter``
    Replaces every hard corner with a tangent circular arc. Radii are ratios of
    the instance stem width, so one parameter set applies to every weight.

``SwapAlternatesFilter``
    Swaps outlines, advance width and anchors between named glyph pairs, so a
    stylistic alternate becomes the default glyph.

Both run as *pre* filters. ufo2ft's default filter chain converts cubics to
quadratics, so a post filter would receive quadratic outlines and the cubic arc
construction below would be wrong. Run ``RemoveOverlapsFilter(pre=True)``
immediately before ``RoundCornerFilter`` so inner (white) corners exist.
"""

from __future__ import annotations

import logging
import math

from fontTools.misc.arrayTools import calcBounds
from fontTools.misc.bezierTools import approximateCubicArcLength, splitCubicAtT
from fontTools.pens.recordingPen import RecordingPointPen
from ufo2ft.filters import BaseFilter

logger = logging.getLogger(__name__)

# Glyphs whose corners are deliberately hard.
EXCLUDE_PREFIXES = ("box", "block", "arrow", "uni25", "uni2B")

# Glyphs that carry a tittle or a dot-like counterless contour.
DOT_GLYPHS = frozenset(
    "i j period colon semicolon exclam question dieresis".split()
)

# Inter feature files supply these pairs. See the report for provenance:
#   cv02 "Open four"          src/features/cv02-four.fea
#   cv06 "Simplified u"       src/features/cv06-u.fea
#   ss03 "Round quotes & commas"   fontinfo.plist feature ss03
ALTERNATE_PRESETS = {
    "cv02": (
        ("four", "four.ss01"),
        ("four.tf", "four.tf.ss01"),
        ("four.squared", "four.ss01.squared"),
        ("four.circled", "four.ss01.circled"),
        ("four.dnom", "four.dnom.ss01"),
        ("four.numr", "four.numr.ss01"),
        ("four.sups", "four.sups.ss01"),
        ("four.subs", "four.subs.ss01"),
    ),
    "cv06": (
        ("u", "u.1"),
        ("uacute", "uacute.1"),
        ("ubar", "ubar.1"),
        ("ubreve", "ubreve.1"),
        ("ucaron", "ucaron.1"),
        ("ucircumflex", "ucircumflex.1"),
        ("ucircumflexbelow", "ucircumflexbelow.1"),
        ("udblgrave", "udblgrave.1"),
        ("udieresis", "udieresis.1"),
        ("udieresis.ss07", "udieresis.1.ss07"),
        ("udieresisacute", "udieresisacute.1"),
        ("udieresisacute.ss07", "udieresisacute.1.ss07"),
        ("udieresisbelow", "udieresisbelow.1"),
        ("udieresisbelow.ss07", "udieresisbelow.1.ss07"),
        ("udieresiscaron", "udieresiscaron.1"),
        ("udieresiscaron.ss07", "udieresiscaron.1.ss07"),
        ("udieresisgrave", "udieresisgrave.1"),
        ("udieresisgrave.ss07", "udieresisgrave.1.ss07"),
        ("udieresismacron", "udieresismacron.1"),
        ("udieresismacron.ss07", "udieresismacron.1.ss07"),
        ("udotbelow", "udotbelow.1"),
        ("udotbelow.ss07", "udotbelow.1.ss07"),
        ("ugrave", "ugrave.1"),
        ("uhookabove", "uhookabove.1"),
        ("uhorn", "uhorn.1"),
        ("uhornacute", "uhornacute.1"),
        ("uhorndotbelow", "uhorndotbelow.1"),
        ("uhorndotbelow.ss07", "uhorndotbelow.1.ss07"),
        ("uhorngrave", "uhorngrave.1"),
        ("uhornhookabove", "uhornhookabove.1"),
        ("uhorntilde", "uhorntilde.1"),
        ("uhungarumlaut", "uhungarumlaut.1"),
        ("uinvertedbreve", "uinvertedbreve.1"),
        ("umacron", "umacron.1"),
        ("umacrondieresis", "umacrondieresis.1"),
        ("umacrondieresis.ss07", "umacrondieresis.1.ss07"),
        ("uogonek", "uogonek.1"),
        ("uring", "uring.1"),
        ("utilde", "utilde.1"),
        ("utildeacute", "utildeacute.1"),
        ("utildebelow", "utildebelow.1"),
    ),
    "ss03": (
        ("comma.dnom", "comma.dnom.ss03"),
        ("comma.numr", "comma.numr.ss03"),
        ("Gcommaaccent", "Gcommaaccent.ss03"),
        ("Gcommaaccent.1", "Gcommaaccent.1.ss03"),
        ("Kcommaaccent", "Kcommaaccent.ss03"),
        ("Lcommaaccent", "Lcommaaccent.ss03"),
        ("Ncommaaccent", "Ncommaaccent.ss03"),
        ("Rcommaaccent", "Rcommaaccent.ss03"),
        ("Scommaaccent", "Scommaaccent.ss03"),
        ("kcommaaccent", "kcommaaccent.ss03"),
        ("lcommaaccent", "lcommaaccent.ss03"),
        ("lcommaaccent.ss02", "lcommaaccent.ss02.ss03"),
        ("ncommaaccent", "ncommaaccent.ss03"),
        ("rcommaaccent", "rcommaaccent.ss03"),
        ("scommaaccent", "scommaaccent.ss03"),
        ("tcommaaccent", "tcommaaccent.ss03"),
        ("tcommaaccent.1", "tcommaaccent.1.ss03"),
        ("commaaccent", "commaaccent.ss03"),
        ("comma", "comma.ss03"),
        ("semicolon", "semicolon.ss03"),
        ("reversedsemicolon", "reversedsemicolon.ss03"),
        ("quotedblleft", "quotedblleft.ss03"),
        ("quotedblright", "quotedblright.ss03"),
        ("quoteleft", "quoteleft.ss03"),
        ("quoteright", "quoteright.ss03"),
        ("quotereversed", "quotereversed.ss03"),
        ("quotedblreversed", "quotedblreversed.ss03"),
        ("quotesinglbase", "quotesinglbase.ss03"),
        ("quotedblbase", "quotedblbase.ss03"),
    ),
}

_EPS = 1e-9


# ---------------------------------------------------------------------------
# vector helpers


def unit(dx, dy):
    n = math.hypot(dx, dy)
    if n < _EPS:
        return (0.0, 0.0)
    return (dx / n, dy / n)


def signed_area(points):
    """Twice the signed area of a polygon, positive when counter-clockwise."""
    total = 0.0
    n = len(points)
    for i in range(n):
        x0, y0 = points[i][0], points[i][1]
        x1, y1 = points[(i + 1) % n][0], points[(i + 1) % n][1]
        total += x0 * y1 - x1 * y0
    return total


# ---------------------------------------------------------------------------
# contour <-> segment list


def contour_to_segments(contour):
    """Return (anchors, segments) or None when the contour cannot be handled.

    ``anchors[k]`` is ``(x, y, smooth)``. ``segments[k]`` runs from
    ``anchors[k]`` to ``anchors[k + 1]`` and is either ``("line",)`` or
    ``("curve", c1, c2)``.
    """
    pts = list(getattr(contour, "points", contour))
    if len(pts) < 2:
        return None
    types = [p.type for p in pts]
    if "move" in types:
        return None  # open contour
    if "qcurve" in types:
        return None  # already quadratic
    on_idx = [i for i, t in enumerate(types) if t is not None]
    if len(on_idx) < 2:
        return None

    anchors = [(pts[i].x, pts[i].y, bool(pts[i].smooth)) for i in on_idx]

    # segments_in[k] ends at anchors[k]
    segments_in = []
    for k in range(len(on_idx)):
        i_prev = on_idx[k - 1]
        i_cur = on_idx[k]
        offs = []
        j = (i_prev + 1) % len(pts)
        while j != i_cur:
            offs.append((pts[j].x, pts[j].y))
            j = (j + 1) % len(pts)
        kind = types[i_cur]
        if kind == "line":
            if offs:
                return None
            segments_in.append(("line",))
        elif kind == "curve":
            if len(offs) == 2:
                segments_in.append(("curve", offs[0], offs[1]))
            elif len(offs) == 0:
                segments_in.append(("line",))
            else:
                return None
        else:
            return None

    # re-index so segments[k] leaves anchors[k]
    segments = segments_in[1:] + segments_in[:1]
    return anchors, segments


def segment_length(p0, seg, p1):
    if seg[0] == "line":
        return math.hypot(p1[0] - p0[0], p1[1] - p0[1])
    return approximateCubicArcLength(p0, seg[1], seg[2], p1)


def tangent_leaving(p0, seg, p1):
    """Unit vector at ``p0`` pointing along ``seg`` away from ``p0``."""
    if seg[0] == "line":
        return unit(p1[0] - p0[0], p1[1] - p0[1])
    for cand in (seg[1], seg[2], p1):
        v = unit(cand[0] - p0[0], cand[1] - p0[1])
        if v != (0.0, 0.0):
            return v
    return (0.0, 0.0)


def tangent_arriving(p0, seg, p1):
    """Unit vector at ``p1`` pointing back along ``seg`` toward ``p0``."""
    if seg[0] == "line":
        return unit(p0[0] - p1[0], p0[1] - p1[1])
    for cand in (seg[2], seg[1], p0):
        v = unit(cand[0] - p1[0], cand[1] - p1[1])
        if v != (0.0, 0.0):
            return v
    return (0.0, 0.0)


def t_at_arclength(p0, c1, c2, p3, target, iterations=26, total=None):
    """Parameter t whose arc length measured from ``p0`` equals ``target``.

    ``total`` is the arc length of the whole segment. The caller measured it
    once already, so passing it back stops this function measuring the same
    curve a second time. Omit it and it is measured here.
    """
    if total is None:
        total = approximateCubicArcLength(p0, c1, c2, p3)
    if total <= _EPS:
        return 0.0
    if target <= 0.0:
        return 0.0
    if target >= total:
        return 1.0
    lo, hi = 0.0, 1.0
    for _ in range(iterations):
        mid = 0.5 * (lo + hi)
        head = splitCubicAtT(p0, c1, c2, p3, mid)[0]
        if approximateCubicArcLength(*head) < target:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def trim_segment(p0, seg, p1, cut_start, cut_end, total=None):
    """Trim ``cut_start`` units off the head and ``cut_end`` off the tail.

    A curve leg is split at arc length with ``splitCubicAtT``. The endpoint is
    never dragged: dragging is what makes rounded curves bulge.
    Returns ``(start_point, geometry, end_point)``.

    ``total`` is this segment's length, already measured by ``segment_length``.
    Passing it turns four arc-length measurements of the same cubic into one.
    """
    if cut_start <= _EPS and cut_end <= _EPS:
        return p0, seg, p1

    if seg[0] == "line":
        length = (
            total if total is not None
            else math.hypot(p1[0] - p0[0], p1[1] - p0[1])
        )
        if length <= _EPS:
            return p0, seg, p1
        u = unit(p1[0] - p0[0], p1[1] - p0[1])
        a = (p0[0] + cut_start * u[0], p0[1] + cut_start * u[1])
        b = (p1[0] - cut_end * u[0], p1[1] - cut_end * u[1])
        return a, ("line",), b

    c1, c2 = seg[1], seg[2]
    if total is None:
        total = approximateCubicArcLength(p0, c1, c2, p1)
    if total <= _EPS:
        return p0, seg, p1
    t0 = (
        t_at_arclength(p0, c1, c2, p1, cut_start, total=total)
        if cut_start > _EPS
        else 0.0
    )
    t1 = (
        t_at_arclength(p0, c1, c2, p1, total - cut_end, total=total)
        if cut_end > _EPS
        else 1.0
    )
    if t1 <= t0 + 1e-6:
        return p0, seg, p1
    if t0 <= 0.0 and t1 >= 1.0:
        return p0, seg, p1
    ts = [t for t in (t0, t1) if 0.0 < t < 1.0]
    parts = splitCubicAtT(p0, c1, c2, p1, *ts)
    part = parts[1] if t0 > 0.0 else parts[0]
    return part[0], ("curve", part[1], part[2]), part[3]


# ---------------------------------------------------------------------------
# the rounding filter


class RoundCornerFilter(BaseFilter):
    """Replace hard corners with tangent circular arcs."""

    # Ruled values have no default here. `tools/params.py` holds them, and a
    # default would silently shadow it: the old defaults were variant B at the
    # Regular stem, so a caller that forgot one built the wrong font quietly.
    REQUIRED = (
        "stem", "outer_ratio", "inner_ratio", "min_angle", "visual",
        "clamp", "clamp_stem_end",
    )

    _kwargs = {
        # Radii are ratios of the instance stem width, never raw units.
        "stem": None,
        "outer_ratio": None,
        "inner_ratio": None,
        # Degrees of turn below which a point is left alone.
        "min_angle": None,
        # An acute spike is chamfered, not speared. Not a ruled value: no
        # variant moves it, so it keeps a default.
        "max_angle": 150.0,
        # Glyphs-style visual correction: acute smaller, obtuse larger.
        "visual": None,
        # Cut-back ceilings as a fraction of the adjacent segment length.
        "clamp": None,
        "clamp_stem_end": None,
        # A stem end is a segment whose two corners are convex and both turn
        # within this many degrees of a right angle.
        "stem_end_tolerance": 20.0,
        # A contour smaller than this multiple of the outer radius on both axes
        # is a dot, and may round to a full circle.
        "dot_factor": 2.2,
        "dot_factor_named": 2.6,
        # Both legs curved and both tangents within this angle of one axis is a
        # smooth extremum, never a corner.
        "extrema_tolerance": 6.0,
    }

    def start(self):
        o = self.options
        missing = [name for name in self.REQUIRED if getattr(o, name) is None]
        if missing:
            raise ValueError(
                "RoundCornerFilter was given no value for "
                + ", ".join(missing)
                + ". These are ruled values; read them from tools/params.py "
                "and pass them explicitly."
            )
        # Ratios become units here, once, from the stem width of this instance.
        self.outer = float(o.outer_ratio) * float(o.stem)
        self.inner = float(o.inner_ratio) * float(o.stem)
        self.min_angle_rad = math.radians(float(o.min_angle))
        self.max_angle_rad = math.radians(float(o.max_angle))
        # One cosine for the whole run, not one per candidate corner.
        self.extrema_cos = math.cos(math.radians(float(o.extrema_tolerance)))
        self.stats = {"glyphs": 0, "corners": 0, "skipped_contours": 0}

    def set_context(self, font, glyphSet):
        context = super().set_context(font, glyphSet)
        context.orientation = self._calibrate_orientation(glyphSet)
        return context

    # -- orientation ------------------------------------------------------

    @staticmethod
    def _calibrate_orientation(glyphSet):
        """+1 when outer contours run counter-clockwise (PostScript order).

        Calibrated on the outer contour of ``o``: it is unambiguously an outer
        contour, so its winding names the convention for the whole font. The
        value is a font-wide constant, not a per-contour flag. Reading it per
        contour would classify every counter corner as convex.
        """
        glyph = None
        for name in ("o", "O", "n", "H"):
            if name in glyphSet:
                candidate = glyphSet[name]
                if len(candidate):
                    glyph = candidate
                    break
        if glyph is None:
            logger.warning("no calibration glyph found; assuming CCW outers")
            return 1
        best_area = None
        best_signed = 0.0
        for contour in glyph:
            parsed = contour_to_segments(contour)
            if parsed is None:
                continue
            anchors = parsed[0]
            x0, y0, x1, y1 = calcBounds([a[:2] for a in anchors])
            area = (x1 - x0) * (y1 - y0)
            if best_area is None or area > best_area:
                best_area = area
                best_signed = signed_area(anchors)
        if best_signed == 0.0:
            return 1
        return 1 if best_signed > 0 else -1

    # -- glyph selection --------------------------------------------------

    def _excluded(self, glyph):
        name = glyph.name or ""
        return any(name.startswith(p) for p in EXCLUDE_PREFIXES)

    # -- main -------------------------------------------------------------

    def filter(self, glyph):
        # Zero contours covers component-only composites, which therefore
        # inherit the rounded base glyphs and stay composites.
        if not len(glyph):
            return False
        if self._excluded(glyph):
            return False

        orientation = self.context.orientation
        parsed = []
        for contour in glyph:
            result = contour_to_segments(contour)
            if result is None:
                self.stats["skipped_contours"] += 1
            parsed.append((contour, result))

        if not any(r is not None for _, r in parsed):
            return False

        recording = RecordingPointPen()
        changed = False
        for contour, result in parsed:
            if result is None:
                contour.drawPoints(recording)
                continue
            anchors, segments = result
            new_points = self._round_contour(
                glyph.name, anchors, segments, orientation
            )
            if new_points is None:
                contour.drawPoints(recording)
                continue
            changed = True
            self._emit(recording, new_points)

        if not changed:
            return False

        glyph.clearContours()
        recording.replay(glyph.getPointPen())
        self.stats["glyphs"] += 1
        return True

    # -- per contour ------------------------------------------------------

    def _round_contour(self, glyph_name, anchors, segments, orientation):
        o = self.options
        n = len(anchors)
        if n < 3:
            return None

        # Dot rule. A contour small on both axes may round to a full circle,
        # so a tittle, a period or a colon does not stay a rounded square.
        x0, y0, x1, y1 = calcBounds([a[:2] for a in anchors])
        width, height = x1 - x0, y1 - y0
        factor = (
            float(o.dot_factor_named)
            if glyph_name in DOT_GLYPHS
            else float(o.dot_factor)
        )
        is_dot = width < factor * self.outer and height < factor * self.outer
        dot_radius = 0.5 * min(width, height) if is_dot else 0.0

        lengths = [
            segment_length(anchors[k][:2], segments[k], anchors[(k + 1) % n][:2])
            for k in range(n)
        ]

        # pass 1: angle, convexity, raw cut-back
        alphas = [0.0] * n
        convex = [False] * n
        raw = [0.0] * n
        active = [False] * n
        for k in range(n):
            prev_k = (k - 1) % n
            p = anchors[k][:2]
            seg_in = segments[prev_k]
            seg_out = segments[k]
            u1 = tangent_arriving(anchors[prev_k][:2], seg_in, p)
            u2 = tangent_leaving(p, seg_out, anchors[(k + 1) % n][:2])
            if u1 == (0.0, 0.0) or u2 == (0.0, 0.0):
                continue
            dot = max(-1.0, min(1.0, u1[0] * u2[0] + u1[1] * u2[1]))
            alpha = math.pi - math.acos(dot)
            cross = u1[0] * u2[1] - u1[1] * u2[0]
            convex[k] = (cross * orientation) < 0
            alphas[k] = alpha

            if anchors[k][2]:  # smooth point
                continue
            if alpha < self.min_angle_rad:
                continue
            if self._is_axis_extremum(seg_in, seg_out, u1, u2):
                continue

            alpha_c = min(alpha, self.max_angle_rad)
            alphas[k] = alpha_c
            if is_dot and convex[k]:
                radius = dot_radius
            else:
                radius = self.outer if convex[k] else self.inner
                if o.visual:
                    radius *= (alpha_c / (math.pi / 2.0)) ** float(o.visual)
            half = math.tan(alpha_c / 2.0)
            if half <= _EPS:
                continue
            raw[k] = radius * half
            active[k] = True

        if not any(active):
            return None

        # pass 2: per-segment clamp factor
        tol = float(o.stem_end_tolerance)
        clamp_default = float(o.clamp)
        clamp_stem = float(o.clamp_stem_end)
        seg_clamp = []
        for k in range(n):
            a, b = k, (k + 1) % n
            if is_dot:
                seg_clamp.append(clamp_stem)
                continue
            stem_end = (
                convex[a]
                and convex[b]
                and abs(math.degrees(alphas[a]) - 90.0) <= tol
                and abs(math.degrees(alphas[b]) - 90.0) <= tol
            )
            seg_clamp.append(clamp_stem if stem_end else clamp_default)

        # pass 3: clamp the cut-back against both adjacent segments
        cut = [0.0] * n
        for k in range(n):
            if not active[k]:
                continue
            prev_k = (k - 1) % n
            cut[k] = min(
                raw[k],
                seg_clamp[prev_k] * lengths[prev_k],
                seg_clamp[k] * lengths[k],
            )

        # No segment may be consumed twice over.
        for k in range(n):
            nxt = (k + 1) % n
            budget = lengths[k] * 0.999
            total = cut[k] + cut[nxt]
            if total > budget and total > _EPS:
                scale = budget / total
                cut[k] *= scale
                cut[nxt] *= scale

        handles = [0.0] * n
        for k in range(n):
            if cut[k] <= _EPS:
                active[k] = False
                continue
            half = math.tan(alphas[k] / 2.0)
            if half <= _EPS:
                active[k] = False
                continue
            r_eff = cut[k] / half
            handles[k] = (4.0 / 3.0) * math.tan(alphas[k] / 4.0) * r_eff

        if not any(active):
            return None

        # pass 4: trim every segment, then rebuild
        trimmed = []
        for k in range(n):
            nxt = (k + 1) % n
            trimmed.append(
                trim_segment(
                    anchors[k][:2],
                    segments[k],
                    anchors[nxt][:2],
                    cut[k] if active[k] else 0.0,
                    cut[nxt] if active[nxt] else 0.0,
                    total=lengths[k],
                )
            )

        nodes = []
        for k in range(n):
            prev_seg = trimmed[(k - 1) % n]
            cur_seg = trimmed[k]
            if not active[k]:
                nodes.append((prev_seg[2], prev_seg[1], anchors[k][2]))
                continue
            a_pt = prev_seg[2]
            b_pt = cur_seg[0]
            # Direction of travel leaving A, which points at the old corner.
            fwd_a = tangent_arriving(prev_seg[0], prev_seg[1], a_pt)
            fwd_a = (-fwd_a[0], -fwd_a[1])
            # Direction of travel leaving B, which points away from it.
            fwd_b = tangent_leaving(b_pt, cur_seg[1], cur_seg[2])
            k_h = handles[k]
            h1 = (a_pt[0] + k_h * fwd_a[0], a_pt[1] + k_h * fwd_a[1])
            h2 = (b_pt[0] - k_h * fwd_b[0], b_pt[1] - k_h * fwd_b[1])
            nodes.append((a_pt, prev_seg[1], True))
            nodes.append((b_pt, ("curve", h1, h2), True))
            self.stats["corners"] += 1

        return nodes

    def _is_axis_extremum(self, seg_in, seg_out, u1, u2):
        """A smooth extremum: both legs curved, both tangents on one axis."""
        if seg_in[0] != "curve" or seg_out[0] != "curve":
            return False
        for axis in ((1.0, 0.0), (0.0, 1.0)):
            a1 = abs(u1[0] * axis[0] + u1[1] * axis[1])
            a2 = abs(u2[0] * axis[0] + u2[1] * axis[1])
            if a1 >= self.extrema_cos and a2 >= self.extrema_cos:
                # opposite senses along that axis == a true extremum
                s1 = u1[0] * axis[0] + u1[1] * axis[1]
                s2 = u2[0] * axis[0] + u2[1] * axis[1]
                if s1 * s2 < 0:
                    return True
        return False

    @staticmethod
    def _emit(pen, nodes):
        """Write a closed contour, starting on an on-curve point."""
        pen.beginPath()
        first_pt, first_seg, first_smooth = nodes[0]
        pen.addPoint(
            first_pt,
            "curve" if first_seg[0] == "curve" else "line",
            first_smooth,
        )
        for pt, seg, smooth in nodes[1:]:
            if seg[0] == "curve":
                pen.addPoint(seg[1], None)
                pen.addPoint(seg[2], None)
                pen.addPoint(pt, "curve", smooth)
            else:
                pen.addPoint(pt, "line", smooth)
        if first_seg[0] == "curve":
            pen.addPoint(first_seg[1], None)
            pen.addPoint(first_seg[2], None)
        pen.endPath()


# ---------------------------------------------------------------------------
# the alternate swap filter


class SwapAlternatesFilter(BaseFilter):
    """Make a stylistic alternate the default glyph.

    Outlines, advance width and anchors move in both directions, so the
    displaced default survives under the alternate's name.

    Composite pairs also swap, and every swapped component base name is then
    remapped through the pair table. Without that remap a swapped composite
    would point at a base that has itself just been swapped, and the two
    swaps would cancel: ``uacute`` would take ``uacute.1``'s reference to
    ``u.1``, which by then holds the old spurred ``u``.
    """

    _kwargs = {
        # Comma separated preset names from ALTERNATE_PRESETS.
        "presets": "cv02,cv06,ss03",
        # Extra pairs as "default>alternate", semicolon separated.
        "pairs": "",
    }

    def start(self):
        pairs = []
        for key in str(self.options.presets).split(","):
            key = key.strip()
            if not key:
                continue
            if key not in ALTERNATE_PRESETS:
                raise ValueError(f"unknown alternate preset: {key}")
            pairs.extend(ALTERNATE_PRESETS[key])
        for item in str(self.options.pairs).split(";"):
            item = item.strip()
            if not item:
                continue
            left, _, right = item.partition(">")
            if not right:
                raise ValueError(f"bad pair spec: {item}")
            pairs.append((left.strip(), right.strip()))
        self.pairs = tuple(pairs)
        self.swapped = []
        self.missing = []

    @staticmethod
    def _extract(glyph):
        recording = RecordingPointPen()
        glyph.drawPoints(recording)
        anchors = [
            {"name": a.name, "x": a.x, "y": a.y} for a in glyph.anchors
        ]
        return list(recording.value), glyph.width, anchors

    @staticmethod
    def _remap(value, mapping):
        out = []
        for operator, args, kwargs in value:
            if operator == "addComponent" and args and args[0] in mapping:
                args = (mapping[args[0]],) + tuple(args[1:])
            out.append((operator, args, kwargs))
        return out

    def _install(self, glyph, payload, mapping):
        value, width, anchors = payload
        glyph.clearContours()
        glyph.clearComponents()
        glyph.clearAnchors()
        recording = RecordingPointPen()
        recording.value = self._remap(value, mapping)
        recording.replay(glyph.getPointPen())
        glyph.width = width
        for anchor in anchors:
            glyph.appendAnchor(anchor)

    def filter(self, glyph):
        context = self.context
        if getattr(context, "swap_done", False):
            return False
        # One pass over the whole glyph set: a swap is not a per-glyph edit.
        context.swap_done = True
        glyph_set = context.glyphSet

        live = []
        mapping = {}
        for left, right in self.pairs:
            if left in glyph_set and right in glyph_set:
                live.append((left, right))
                mapping[left] = right
                mapping[right] = left
            else:
                self.missing.append((left, right))

        payloads = {}
        for left, right in live:
            payloads[left] = self._extract(glyph_set[left])
            payloads[right] = self._extract(glyph_set[right])

        for left, right in live:
            self._install(glyph_set[left], payloads[right], mapping)
            self._install(glyph_set[right], payloads[left], mapping)
            context.modified.add(left)
            context.modified.add(right)
            self.swapped.append((left, right))

        if self.missing:
            logger.warning("%d alternate pairs missing", len(self.missing))
        return glyph.name in context.modified
