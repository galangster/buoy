"""Turn a rounded Inter instance into a shipping Buoy TTF.

fontmake writes the source family's identity into every binary, so a build
straight out of ``build.py release`` still calls itself Inter, keeps Inter's
unique font identifier and Inter's vendor ID. An OS font cache would then serve
these files as Inter. This module rewrites the identity, sets the tables the
gates read, and refuses to write a font whose *line box* has moved away from the
flat instance it was interpolated from. The *clipping* box, `usWinAscent` and
`usWinDescent`, is a separate thing and is raised here to hold the family's real
ink, which Inter's own numbers do not.

    python tools/finish.py
    python tools/finish.py --weights Regular
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

from fontTools.pens.boundsPen import BoundsPen
from fontTools.ttLib import TTFont, newTable
from fontTools.ttLib.tables import ttProgram

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import params  # noqa: E402

# Windows/Unicode BMP/US English only. Ruled 2026-09-04 on fontbakery's
# `no-mac-entries`: Macintosh (platform 1) records are legacy, every current
# renderer reads platform 3, and a stray platform-1 record would still say Inter.
PLATFORMS = ((3, 1, 0x409),)

# PUSHW 511, SCANCTRL, PUSHB 4, SCANTYPE. Smart dropout control, the one piece
# of bytecode an unhinted font still needs so thin stems do not drop out at
# small ppem. This is what `gftools fix-nonhinting` writes.
SMART_DROPOUT = b"\xb8\x01\xff\x85\xb0\x04\x8d"

# fsSelection bits, OS/2 spec.
BIT_BOLD = 5
BIT_REGULAR = 6
BIT_USE_TYPO_METRICS = 7

# The line box. It must not move: fontkit reads hhea, not sTypo, so next/font's
# size-adjust maths depends on the hhea trio surviving, and every capture taken
# so far measures this leading.
VERTICAL_PINNED = (
    ("hhea", "ascent"), ("hhea", "descent"), ("hhea", "lineGap"),
    ("OS/2", "sTypoAscender"), ("OS/2", "sTypoDescender"),
    ("OS/2", "sTypoLineGap"),
)

# The clipping box, which is a different thing. Windows GDI cuts ink outside
# usWinAscent/usWinDescent, and Inter ships 1984/494 while its own ink reaches
# 2272/668, so the tall accented capitals and the comma-below capitals are
# already clipped there. Rounding makes it worse: a cedilla's corner arc pushes
# `Gcommaaccent` and eighteen siblings from -493 down past -625, and those are
# inside the shipping subset. Raising the win box only widens the region the
# rasteriser is allowed to paint. It moves no line box, because bit 7 below
# tells every renderer that reads it to lay out from sTypo instead.
VERTICAL_WIN = (("OS/2", "usWinAscent"), ("OS/2", "usWinDescent"))

VERTICAL = VERTICAL_PINNED + VERTICAL_WIN


def name_records(weight: str) -> dict[int, str]:
    """The name table for one style.

    The four-style rule: a family with a style outside Regular/Italic/Bold/
    Bold Italic puts the style into the legacy family (1) and keeps the
    typographic family (16) constant, so old applications still see a valid
    RIBBI pair while new ones see one family with two styles.
    """
    family = params.FAMILY
    postscript = f"{family}-{weight}"
    legacy_family = family if weight == "Regular" else f"{family} {weight}"
    legacy_style = "Regular"
    return {
        0: params.COPYRIGHT,
        1: legacy_family,
        2: legacy_style,
        3: f"{params.VERSION};{params.VENDOR_ID};{postscript}",
        4: legacy_family,
        5: f"Version {params.VERSION}",
        6: postscript,
        8: params.MANUFACTURER,
        9: params.DESIGNER,
        11: params.VENDOR_URL,
        12: params.VENDOR_URL,
        13: params.LICENSE,
        14: params.LICENSE_URL,
        16: family,
        17: weight,
    }


def read_vertical(font: TTFont) -> dict[str, int]:
    return {f"{tag}.{attr}": getattr(font[tag], attr) for tag, attr in VERTICAL}


def ink_box(path: Path) -> tuple[int, int]:
    """``(yMax, abs(yMin))`` over every glyph in one font, rounded outward.

    ``head`` alone is not enough. A composite whose component carries a scale
    draws outside the integer box fontTools recorded for it, and this family has
    283 of them, so the bounds are taken from the glyph set and every fraction
    is rounded away from the baseline.
    """
    font = TTFont(path, recalcTimestamp=False)
    glyphs = font.getGlyphSet()
    top, bottom = float(font["head"].yMax), float(font["head"].yMin)
    for name in font.getGlyphOrder():
        pen = BoundsPen(glyphs)
        glyphs[name].draw(pen)
        if pen.bounds:
            top = max(top, pen.bounds[3])
            bottom = min(bottom, pen.bounds[1])
    font.close()
    return math.ceil(top), math.ceil(-bottom)


def family_win_box(paths, floor: tuple[int, int]) -> tuple[int, int]:
    """One clipping box for the whole family, never below ``floor``.

    fontbakery's `family/vertical_metrics` requires every file in a family to
    publish the same numbers, so the box is the maximum across the weights, not
    each weight's own ink. ``floor`` is the flat instance's box, which keeps a
    future weight with shallower ink from *lowering* what Inter already shipped.
    """
    ascent, descent = floor
    for path in paths:
        top, bottom = ink_box(path)
        ascent, descent = max(ascent, top), max(descent, bottom)
    return ascent, descent


def finish(weight: str, raw_path: Path, flat_path: Path, out_path: Path,
           win_box: tuple[int, int] | None = None):
    style = params.STYLES[weight]
    font = TTFont(raw_path, recalcTimestamp=False)
    flat = TTFont(flat_path, recalcTimestamp=False)

    # -- vertical metrics, asserted before anything is written ------------
    got, want = read_vertical(font), read_vertical(flat)
    drift = {
        f"{tag}.{attr}": (want[f"{tag}.{attr}"], got[f"{tag}.{attr}"])
        for tag, attr in VERTICAL_PINNED
        if want[f"{tag}.{attr}"] != got[f"{tag}.{attr}"]
    }
    if drift:
        raise SystemExit(
            f"{weight}: vertical metrics moved from the flat instance: {drift}"
        )

    floor = (want["OS/2.usWinAscent"], want["OS/2.usWinDescent"])
    if win_box is None:
        win_box = family_win_box([raw_path], floor)
    if win_box[0] < floor[0] or win_box[1] < floor[1]:
        raise SystemExit(
            f"{weight}: win box {win_box} is below the flat instance's {floor}; "
            "the clipping box may be raised, never lowered"
        )
    ink = ink_box(raw_path)
    if ink[0] > win_box[0] or ink[1] > win_box[1]:
        raise SystemExit(
            f"{weight}: ink reaches {ink} but the win box is {win_box}; "
            "Windows GDI would clip it"
        )

    # -- name table --------------------------------------------------------
    records = name_records(weight)
    table = font["name"]
    # Inter's trademark cannot travel with a renamed derivative. Nor can its
    # WWS names: 16 and 17 are already WWS compatible here, so 21 and 22 are
    # both wrong and redundant.
    for name_id in (7, 21, 22):
        table.removeNames(nameID=name_id)
    # Every Macintosh record goes with them, for the reason at PLATFORMS.
    table.removeNames(platformID=1)
    # Any other-language copy of an ID we set would still say Inter.
    table.names = [
        r for r in table.names
        if r.nameID not in records
        or (r.platformID, r.platEncID, r.langID) in PLATFORMS
    ]
    for name_id, value in records.items():
        for platform, encoding, language in PLATFORMS:
            table.setName(value, name_id, platform, encoding, language)

    # -- OS/2, head --------------------------------------------------------
    os2 = font["OS/2"]
    os2.achVendID = params.VENDOR_ID
    os2.fsType = 0
    os2.usWeightClass = style["weight_class"]
    selection = os2.fsSelection
    selection &= ~(1 << BIT_BOLD)
    if style["regular_bit"]:
        selection |= 1 << BIT_REGULAR
    else:
        selection &= ~(1 << BIT_REGULAR)
    # Load-bearing once the win box is wider than sTypo: bit 7 is what tells a
    # renderer to take its line box from sTypo and read usWin* as a clipping
    # box only. Inter already sets it; it is set here rather than inherited,
    # because raising usWin* without it would change leading on Windows.
    selection |= 1 << BIT_USE_TYPO_METRICS
    os2.fsSelection = selection
    os2.usWinAscent, os2.usWinDescent = win_box
    font["head"].fontRevision = params.FONT_REVISION
    # One underline for the whole family, not one per weight.
    font["post"].underlineThickness = params.UNDERLINE_THICKNESS

    # -- gasp --------------------------------------------------------------
    # Unhinted plus grayscale and symmetric smoothing across the whole range,
    # the Google Fonts escape for a display face that hints badly.
    gasp = newTable("gasp")
    gasp.version = 1
    gasp.gaspRange = {0xFFFF: 0x000A}
    font["gasp"] = gasp

    # -- prep --------------------------------------------------------------
    prep = newTable("prep")
    prep.program = ttProgram.Program()
    prep.program.fromBytecode(SMART_DROPOUT)
    font["prep"] = prep
    # The two pushes have to fit on the interpreter stack.
    font["maxp"].maxStackElements = max(font["maxp"].maxStackElements, 2)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    # Reproducible release: fontTools would stamp head.modified with the wall clock on
    # every save, so two builds of the same inputs never matched. Pin it to created.
    font["head"].modified = font["head"].created
    font.save(out_path)
    return {
        "weight": weight,
        "path": out_path,
        "vertical": read_vertical(font),
        "ink": ink,
        "win_box": win_box,
        "fsSelection": os2.fsSelection,
        "underlineThickness": font["post"].underlineThickness,
        "usWeightClass": os2.usWeightClass,
        "names": records,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--weights", default=",".join(params.RELEASE_WEIGHTS))
    args = parser.parse_args(argv)

    weights = [w.strip() for w in args.weights.split(",")]

    def sources(weight: str) -> tuple[Path, Path]:
        raw = params.RAW_DIR / params.flat_name(weight)
        flat = params.FLAT_DIR / params.flat_name(weight)
        for path in (raw, flat):
            if not path.exists():
                raise SystemExit(f"missing {path}; run build.py release first")
        return raw, flat

    # Always the whole family, never `--weights`. The clipping box is a family
    # property, so finishing one weight on its own must not give it a narrower
    # box than the sibling it will ship beside.
    family_raw, family_flat = zip(*(sources(w) for w in params.RELEASE_WEIGHTS))
    floor = (
        max(TTFont(p, recalcTimestamp=False, lazy=True)["OS/2"].usWinAscent
            for p in family_flat),
        max(TTFont(p, recalcTimestamp=False, lazy=True)["OS/2"].usWinDescent
            for p in family_flat),
    )
    win_box = family_win_box(family_raw, floor)

    rows = []
    for weight in weights:
        raw, flat = sources(weight)
        rows.append(finish(weight, raw, flat,
                           params.RELEASE_DIR / params.ttf_name(weight), win_box))

    for row in rows:
        print(f"{row['weight']:8s} -> {row['path'].name}")
        print(f"  usWeightClass={row['usWeightClass']} "
              f"fsSelection={row['fsSelection']:#010b} "
              f"USE_TYPO_METRICS={bool(row['fsSelection'] & (1 << BIT_USE_TYPO_METRICS))}")
        print("  line box equals the flat instance: " +
              " ".join(f"{tag.split('/')[0]}.{attr}={row['vertical'][f'{tag}.{attr}']}"
                       for tag, attr in VERTICAL_PINNED))
        print(f"  win box {row['win_box']} contains the family ink; "
              f"this weight reaches {row['ink']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
