"""Turn a rounded Inter instance into a shipping Buoy TTF.

fontmake writes the source family's identity into every binary, so a build
straight out of ``build.py release`` still calls itself Inter, keeps Inter's
unique font identifier and Inter's vendor ID. An OS font cache would then serve
these files as Inter. This module rewrites the identity, sets the tables the
gates read, and refuses to write a font whose vertical metrics have moved away
from the flat instance it was interpolated from.

    python tools/finish.py
    python tools/finish.py --weights Regular
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

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

# Vertical metrics that must not move. fontkit reads hhea, not sTypo, so
# next/font's size-adjust maths depends on the hhea trio surviving.
VERTICAL = (
    ("hhea", "ascent"), ("hhea", "descent"), ("hhea", "lineGap"),
    ("OS/2", "sTypoAscender"), ("OS/2", "sTypoDescender"),
    ("OS/2", "sTypoLineGap"), ("OS/2", "usWinAscent"), ("OS/2", "usWinDescent"),
)


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


def finish(weight: str, raw_path: Path, flat_path: Path, out_path: Path):
    style = params.STYLES[weight]
    font = TTFont(raw_path, recalcTimestamp=False)
    flat = TTFont(flat_path, recalcTimestamp=False)

    # -- vertical metrics, asserted before anything is written ------------
    got, want = read_vertical(font), read_vertical(flat)
    drift = {k: (want[k], got[k]) for k in want if want[k] != got[k]}
    if drift:
        raise SystemExit(
            f"{weight}: vertical metrics moved from the flat instance: {drift}"
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
    os2.fsSelection = selection
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
        "vertical": got,
        "fsSelection": os2.fsSelection,
        "underlineThickness": font["post"].underlineThickness,
        "usWeightClass": os2.usWeightClass,
        "names": records,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--weights", default=",".join(params.RELEASE_WEIGHTS))
    args = parser.parse_args(argv)

    rows = []
    for weight in args.weights.split(","):
        weight = weight.strip()
        raw = params.RAW_DIR / params.flat_name(weight)
        flat = params.FLAT_DIR / params.flat_name(weight)
        for path in (raw, flat):
            if not path.exists():
                raise SystemExit(f"missing {path}; run build.py release first")
        rows.append(finish(weight, raw, flat, params.RELEASE_DIR / params.ttf_name(weight)))

    for row in rows:
        print(f"{row['weight']:8s} -> {row['path'].name}")
        print(f"  usWeightClass={row['usWeightClass']} "
              f"fsSelection={row['fsSelection']:#010b}")
        print("  vertical metrics equal the flat instance: " +
              " ".join(f"{k.split('.')[-1]}={v}" for k, v in row["vertical"].items()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
