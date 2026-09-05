"""Specimen sheets for the Backable rounding sweep.

Shaped text goes through ``hb-view`` so kerning and OpenType features are real.
Glyph sheets and the diff overlay go through ``fontTools.pens.freetypePen``,
which rasterises the outline directly and needs no shaping.

``proof.py`` renders the release sheets from these same functions, so every
helper takes its roster, its output directory and its geometry as arguments
rather than reading a module global.

    python tools/specimen.py all
    python tools/specimen.py sweep-medium
"""

from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

import numpy as np
from fontTools.pens.freetypePen import FreeTypePen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import params  # noqa: E402

HB_VIEW = params.HB_BIN / "hb-view"

# The sweep sheets are spike evidence, not release evidence, so they keep their
# own directory. It is the default output directory of this module's sheets and
# nothing else: every function below is told where to write.
SPIKE_PROOF = params.PKG / "proof" / "2026-09-04-spike"

SCALE = 2  # 2x pixel density
LABEL_PX = 13 * SCALE
MARGIN = 24 * SCALE

SPECIMEN_LINE = "Backable Handgloves 0123456789 $1,000 +12.5%"
ALTERNATES_LINE = 'Quiet "founders" ship, 4 of 9 u-turns.'
PARAGRAPH = (
    "A backable company publishes its decisions before it makes them. "
    "Every market prices one question. The winning side pays for being "
    "right, and the record stays open for anyone to read afterwards. "
    "Nothing here is a promise, only a price."
)  # 40 words


def variant_label(variant: str) -> str:
    """The row label for one sweep variant, read off its ruled radius."""
    if variant == "flat":
        return "flat (Inter)"
    spec = params.VARIANTS[variant]
    if spec["alternates"]:
        return f"{variant}  = C + alternates"
    return f"{variant}  outer {spec['outer_ratio']:.2f} stem"


VARIANT_LABELS = {
    "flat": variant_label("flat"),
    **{name: variant_label(name) for name in params.VARIANTS},
}


def font_path(variant: str, weight: str) -> Path:
    return params.BUILD / variant / params.flat_name(weight)


def label_font():
    for candidate in (
        "/System/Library/Fonts/SFNSMono.ttf",
        "/System/Library/Fonts/Supplemental/Andale Mono.ttf",
        "/System/Library/Fonts/Menlo.ttc",
    ):
        if Path(candidate).exists():
            try:
                return ImageFont.truetype(candidate, LABEL_PX)
            except OSError:
                continue
    return ImageFont.load_default()


LABEL_FONT = label_font()


# ---------------------------------------------------------------------------
# hb-view


def shape_png(font: Path, text: str, px: int, features: str | None = None):
    """Render shaped text to a greyscale image via hb-view."""
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as handle:
        out = Path(handle.name)
    args = [
        "--output-format=png",
        f"--output-file={out}",
        f"--font-size={px * SCALE}",
        "--margin=0",
        "--background=#FFFFFF",
        "--foreground=#000000",
    ]
    if features:
        args.append(f"--features={features}")
    args += [str(font), text]
    params.run_hb("hb-view", args, label=font.name)
    image = Image.open(out).convert("L")
    image.load()
    out.unlink(missing_ok=True)
    return image


# ---------------------------------------------------------------------------
# freetypePen


def glyph_array(font_path_: Path, glyph_name: str, em_px: int, cache={}):
    """Rasterise one glyph at ``em_px`` per em. Returns a numpy alpha array."""
    key = str(font_path_)
    if key not in cache:
        cache[key] = TTFont(font_path_)
    ttf = cache[key]
    upm = ttf["head"].unitsPerEm
    glyph_set = ttf.getGlyphSet()
    if glyph_name not in glyph_set:
        return None
    scale = em_px / upm
    width = int(round(glyph_set[glyph_name].width * scale)) or em_px // 2
    pen = FreeTypePen(glyph_set)
    glyph_set[glyph_name].draw(
        TransformPen(pen, (scale, 0, 0, scale, 0, 0))
    )
    ascent = int(round(ttf["hhea"].ascent * scale))
    descent = int(round(-ttf["hhea"].descent * scale))
    return pen.array(width=width, height=ascent + descent, transform=(1, 0, 0, 1, 0, descent))


def array_to_ink(array):
    """Alpha (1.0 = ink) to an 8 bit greyscale ink image."""
    return Image.fromarray(
        np.uint8(255 * (1.0 - np.clip(array, 0.0, 1.0)))
    )


# ---------------------------------------------------------------------------
# sheet assembly


def new_sheet(width, height):
    return Image.new("L", (max(width, 1), max(height, 1)), 255)


def draw_label(image, xy, text):
    ImageDraw.Draw(image).text(xy, text, font=LABEL_FONT, fill=90)


def stack_rows(rows, label_width, gap=14 * SCALE):
    """rows = [(label, PIL image)] -> one sheet."""
    content_width = max((r[1].width for r in rows), default=1)
    heights = [r[1].height for r in rows]
    total = sum(heights) + gap * (len(rows) + 1)
    sheet = new_sheet(label_width + content_width + 2 * MARGIN, total + MARGIN)
    y = gap
    for text, image in rows:
        draw_label(sheet, (MARGIN // 2, y + image.height // 2 - LABEL_PX), text)
        sheet.paste(image, (label_width, y))
        y += image.height + gap
    return sheet


def save(image, name, out_dir: Path, threshold: int = 128):
    """Write one sheet into ``out_dir`` and refuse to write a blank one.

    ``threshold`` is the ink cutoff. A greyscale sheet of black text reads at
    128; a diff overlay, whose lightest ink is a tint, reads at 200. The image
    may be L or RGB, so a caller can save either kind through one gate.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / name
    image.save(path)
    array = np.asarray(image if image.mode == "L" else image.convert("L"))
    ink = int((array < threshold).sum())
    print(
        f"{name:26s} {image.width}x{image.height} "
        f"ink_px={ink} unique={len(np.unique(array))}"
    )
    if ink == 0:
        raise RuntimeError(f"{name} is blank")
    return path


def wrap(text, chars=58):
    lines, current = [], ""
    for word in text.split():
        if current and len(current) + 1 + len(word) > chars:
            lines.append(current)
            current = word
        else:
            current = f"{current} {word}".strip()
    if current:
        lines.append(current)
    return lines


def shape_block(font: Path, text: str, px: int, chars: int = 58):
    """hb-view shapes one line at a time, so wrap first and stack after."""
    images = [shape_png(font, line, px) for line in wrap(text, chars)]
    leading = int(round(px * SCALE * 1.45))
    width = max(i.width for i in images)
    block = new_sheet(width, leading * len(images))
    for index, image in enumerate(images):
        block.paste(image, (0, index * leading))
    return block


def glyph_row(path, names, em_px):
    images = []
    for name in names:
        array = glyph_array(path, name, em_px)
        if array is None:
            continue
        images.append((name, array_to_ink(array)))
    if not images:
        raise RuntimeError(f"no glyphs rendered from {path}")
    gap = 18 * SCALE
    width = sum(i.width for _, i in images) + gap * (len(images) + 1)
    height = max(i.height for _, i in images)
    row = new_sheet(width, height)
    x = gap
    for _, image in images:
        row.paste(image, (x, height - image.height))
        x += image.width + gap
    return row


def diff_overlay(font_a: Path, font_b: Path, names, per_row: int, legend: str):
    """Two fonts drawn over one another, one tile per glyph.

    Ink only in ``font_a`` prints red, ink only in ``font_b`` prints green, ink
    in both prints dark. Every disagreement should sit at a corner. Returns the
    RGB sheet; the caller names it and decides where it lands.
    """
    tiles = []
    for name in names:
        a = glyph_array(font_a, name, 300)
        b = glyph_array(font_b, name, 300)
        if a is None or b is None:
            continue
        height = max(a.shape[0], b.shape[0])
        width = max(a.shape[1], b.shape[1])

        def pad(array):
            out = np.zeros((height, width), dtype=float)
            out[: array.shape[0], : array.shape[1]] = array
            return np.clip(out, 0.0, 1.0)

        red, green = pad(a), pad(b)
        rgb = np.zeros((height, width, 3), dtype=np.uint8)
        rgb[..., 0] = np.uint8(255 * (1.0 - green))
        rgb[..., 1] = np.uint8(255 * (1.0 - red))
        rgb[..., 2] = np.uint8(255 * (1.0 - np.maximum(red, green)))
        tiles.append((name, Image.fromarray(rgb, "RGB")))

    gap = 20 * SCALE
    cell_w = max(t.width for _, t in tiles) + gap
    cell_h = max(t.height for _, t in tiles) + gap + LABEL_PX
    rows = (len(tiles) + per_row - 1) // per_row
    sheet = Image.new(
        "RGB", (cell_w * per_row + gap, cell_h * rows + gap + LABEL_PX * 2),
        (255, 255, 255),
    )
    draw = ImageDraw.Draw(sheet)
    draw.text((gap, gap // 2), legend, font=LABEL_FONT, fill=(90, 90, 90))
    for index, (name, tile) in enumerate(tiles):
        col, row = index % per_row, index // per_row
        x = gap + col * cell_w
        y = gap + LABEL_PX * 2 + row * cell_h
        sheet.paste(tile, (x, y))
        draw.text((x, y + tile.height + 2), name, font=LABEL_FONT,
                  fill=(90, 90, 90))
    return sheet


# ---------------------------------------------------------------------------
# the six sheets


def sheet_sweep_medium():
    rows = []
    for variant in ("flat", "A", "B", "C", "D"):
        path = font_path(variant, "Medium")
        if not path.exists():
            continue
        rows.append((VARIANT_LABELS[variant], shape_png(path, SPECIMEN_LINE, 96)))
    return save(stack_rows(rows, 200 * SCALE), "sweep-medium.png", SPIKE_PROOF)


def sheet_sweep_weights_c():
    rows = []
    for weight in params.SWEEP_WEIGHTS:
        for variant in ("flat", "C"):
            path = font_path(variant, weight)
            if not path.exists():
                continue
            rows.append((f"{weight} {variant}", shape_png(path, SPECIMEN_LINE, 72)))
    return save(stack_rows(rows, 170 * SCALE), "sweep-weights-C.png", SPIKE_PROOF)


def sheet_identity_glyphs():
    rows = []
    for variant in ("flat", "C"):
        path = font_path(variant, "Medium")
        if not path.exists():
            continue
        rows.append(
            (f"{variant} Medium", glyph_row(path, params.IDENTITY_GLYPHS, 400))
        )
    sheet = stack_rows(rows, 190 * SCALE)
    draw_label(
        sheet,
        (MARGIN // 2, 4),
        " ".join(params.IDENTITY_GLYPHS) + "   400 px em",
    )
    return save(sheet, "identity-glyphs.png", SPIKE_PROOF)


def sheet_text_sizes():
    rows = []
    for px in (12, 14, 16, 24, 48):
        for variant in ("flat", "C"):
            path = font_path(variant, "Regular")
            if not path.exists():
                continue
            rows.append((f"{px}px {variant}", shape_block(path, PARAGRAPH, px)))
    return save(
        stack_rows(rows, 130 * SCALE, gap=16 * SCALE), "text-sizes.png",
        SPIKE_PROOF,
    )


def sheet_diff_overlay():
    sheet = diff_overlay(
        font_path("flat", "Medium"), font_path("C", "Medium"),
        params.DIFF_GLYPHS, 7,
        "red = flat   green = rounded C   dark = both   Medium 300 px em",
    )
    return save(sheet, "diff-overlay-medium.png", SPIKE_PROOF, threshold=200)


def sheet_alternates():
    rows = []
    for variant in ("C", "D"):
        path = font_path(variant, "Medium")
        if not path.exists():
            continue
        rows.append(
            (VARIANT_LABELS[variant], shape_png(path, ALTERNATES_LINE, 96))
        )
    return save(stack_rows(rows, 200 * SCALE), "alternates-D.png", SPIKE_PROOF)


def contact_sheet(paths, out_dir: Path = SPIKE_PROOF):
    """One downscaled sheet, only so the labels can be checked once."""
    images = []
    for path in paths:
        image = Image.open(path).convert("RGB")
        ratio = min(1.0, 900 / image.width)
        images.append(
            image.resize(
                (int(image.width * ratio), int(image.height * ratio))
            )
        )
    width = max(i.width for i in images)
    height = sum(i.height for i in images) + 8 * len(images)
    sheet = Image.new("RGB", (width, height), (255, 255, 255))
    y = 0
    for image in images:
        sheet.paste(image, (0, y))
        y += image.height + 8
    path = out_dir / "_contact-sheet.png"
    sheet.save(path)
    print(f"contact sheet {sheet.width}x{sheet.height} -> {path}")
    return path


SHEETS = {
    "sweep-medium": sheet_sweep_medium,
    "sweep-weights-C": sheet_sweep_weights_c,
    "identity-glyphs": sheet_identity_glyphs,
    "text-sizes": sheet_text_sizes,
    "diff-overlay-medium": sheet_diff_overlay,
    "alternates-D": sheet_alternates,
}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("which", nargs="?", default="all")
    parser.add_argument("--contact", action="store_true")
    args = parser.parse_args(argv)

    names = list(SHEETS) if args.which == "all" else [args.which]
    paths = []
    for name in names:
        paths.append(SHEETS[name]())
    if args.contact:
        contact_sheet(paths)
    return 0


if __name__ == "__main__":
    sys.exit(main())
