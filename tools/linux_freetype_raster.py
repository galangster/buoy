"""Rasterize the fixed native proof runs with FreeType on Linux.

This is a small reference job beside the authoritative Windows DirectWrite
job. Both consume the same pre-shaped HarfBuzz fixture, so neither is a native
shaping proof.
"""

from __future__ import annotations

import csv
import hashlib
import json
import platform
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

import freetype
from PIL import Image, ImageChops


@dataclass(frozen=True)
class Run:
    font_id: str
    font_path: Path
    sha256: str
    weight: str
    upem: int
    size_px: int
    case_id: str
    glyph_ids: tuple[int, ...]
    x_advances: tuple[int, ...]
    y_advances: tuple[int, ...]
    x_offsets: tuple[int, ...]
    y_offsets: tuple[int, ...]


def ints(value: str) -> tuple[int, ...]:
    return tuple(int(part) for part in value.split(","))


def read_runs(path: Path, root: Path) -> list[Run]:
    lines = [line for line in path.read_text(encoding="utf-8").splitlines()
             if line and not line.startswith("#")]
    rows = csv.DictReader(lines, delimiter="\t")
    runs = []
    for row in rows:
        run = Run(
            font_id=row["font_id"],
            font_path=(root / row["font_path"]).resolve(),
            sha256=row["sha256"],
            weight=row["weight"],
            upem=int(row["upem"]),
            size_px=int(row["size_px"]),
            case_id=row["case_id"],
            glyph_ids=ints(row["glyph_ids"]),
            x_advances=ints(row["x_advances"]),
            y_advances=ints(row["y_advances"]),
            x_offsets=ints(row["x_offsets"]),
            y_offsets=ints(row["y_offsets"]),
        )
        count = len(run.glyph_ids)
        if not count or 0 in run.glyph_ids or any(
            len(values) != count for values in (
                run.x_advances, run.y_advances,
                run.x_offsets, run.y_offsets,
            )
        ):
            raise ValueError("fixture glyph and position counts differ")
        runs.append(run)
    if len(runs) != 96:
        raise ValueError(f"expected 96 fixture runs, found {len(runs)}")
    return runs


def glyph_mask(bitmap: freetype.Bitmap) -> Image.Image:
    width, height, pitch = bitmap.width, bitmap.rows, bitmap.pitch
    source = bytes(bitmap.buffer)
    packed = bytearray(width * height)
    for y in range(height):
        source_y = y if pitch >= 0 else height - 1 - y
        start = source_y * abs(pitch)
        packed[y * width:(y + 1) * width] = source[start:start + width]
    return Image.frombytes("L", (width, height), bytes(packed))


def rasterize(face: freetype.Face, run: Run, scale: float) -> tuple[Image.Image, int]:
    dpi = round(96 * scale)
    face.set_char_size(0, run.size_px * 48, dpi, dpi)
    factor = run.size_px * scale / run.upem
    pen_x = 0.0
    glyphs: list[tuple[int, int, Image.Image]] = []
    for index, glyph_id in enumerate(run.glyph_ids):
        if run.y_advances[index]:
            raise ValueError("vertical advances are not supported")
        face.load_glyph(
            glyph_id,
            freetype.FT_LOAD_DEFAULT | freetype.FT_LOAD_TARGET_NORMAL,
        )
        face.glyph.render(freetype.FT_RENDER_MODE_NORMAL)
        bitmap = face.glyph.bitmap
        if bitmap.width and bitmap.rows:
            x = round(pen_x + run.x_offsets[index] * factor) + face.glyph.bitmap_left
            y = -round(run.y_offsets[index] * factor) - face.glyph.bitmap_top
            glyphs.append((x, y, glyph_mask(bitmap)))
        pen_x += run.x_advances[index] * factor
    if not glyphs:
        raise ValueError("FreeType produced an empty run")
    left = min(x for x, _, _ in glyphs)
    top = min(y for _, y, _ in glyphs)
    right = max(x + image.width for x, _, image in glyphs)
    bottom = max(y + image.height for _, y, image in glyphs)
    raster = Image.new("L", (right - left, bottom - top), 255)
    ink_sum = 0
    for x, y, mask in glyphs:
        ink_sum += sum(mask.get_flattened_data())
        layer = Image.new("L", raster.size, 255)
        layer.paste(0, (x - left, y - top), mask)
        raster = ImageChops.darker(raster, layer)
    if not ink_sum:
        raise ValueError("FreeType glyph bitmaps contain no ink")
    return raster, ink_sum


def border_clear(image: Image.Image) -> bool:
    width, height = image.size
    pixels = image.load()
    return (
        all(pixels[x, 0] == 255 and pixels[x, height - 1] == 255
            for x in range(width))
        and all(pixels[0, y] == 255 and pixels[width - 1, y] == 255
                for y in range(height))
    )


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: linux_freetype_raster.py <fixture.tsv> <output-dir>", file=sys.stderr)
        return 2
    root = Path.cwd()
    fixture = Path(sys.argv[1]).resolve()
    output_dir = Path(sys.argv[2]).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    runs = read_runs(fixture, root)
    groups: dict[str, list[Run]] = defaultdict(list)
    for run in runs:
        groups[run.font_id].append(run)

    sheets = []
    for font_id, font_runs in sorted(groups.items()):
        first = font_runs[0]
        digest = hashlib.sha256(first.font_path.read_bytes()).hexdigest()
        if digest != first.sha256 or any(
            (run.font_path, run.sha256, run.weight, run.upem)
            != (first.font_path, first.sha256, first.weight, first.upem)
            for run in font_runs
        ):
            raise ValueError(f"font hash or fixture metadata mismatch: {font_id}")
        face = freetype.Face(str(first.font_path))
        if face.units_per_EM != first.upem:
            raise ValueError(f"fixture and FreeType UPEM differ: {font_id}")
        for scale in (1.0, 1.25):
            rasters = [rasterize(face, run, scale) for run in font_runs]
            padding, gap = 12, 8
            width = max(image.width for image, _ in rasters) + padding * 2
            height = sum(image.height for image, _ in rasters) + gap * (len(rasters) - 1) + padding * 2
            sheet = Image.new("L", (width, height), 255)
            y = padding
            for image, _ in rasters:
                sheet.paste(image, (padding, y))
                y += image.height + gap
            if not border_clear(sheet):
                raise ValueError("sheet touches its target border")
            scale_name = "100" if scale == 1.0 else "125"
            output = output_dir / f"{font_id}-scale-{scale_name}.png"
            sheet.save(output, format="PNG")
            if not output.stat().st_size:
                raise ValueError("Pillow wrote an empty PNG")
            sheets.append({
                "fontId": font_id,
                "weight": first.weight,
                "sha256": digest,
                "scale": scale,
                "width": width,
                "height": height,
                "runCount": len(rasters),
                "inkSum": sum(ink for _, ink in rasters),
                "nonempty": True,
                "targetBorderClear": True,
                "png": output.name,
            })
    report = {
        "schemaVersion": 1,
        "result": "pass",
        "proofType": "FreeType raster reference from pre-shaped HarfBuzz glyph runs",
        "linuxShapingProof": False,
        "osVersion": platform.platform(),
        "renderer": f"FreeType {'.'.join(map(str, freetype.version()))}",
        "rasterMode": "FT_RENDER_MODE_NORMAL with FT_LOAD_TARGET_NORMAL",
        "fontLoading": "FreeType file faces; no system font installation",
        "fixture": str(fixture.relative_to(root)),
        "sizesPx": [11, 12, 13, 14, 16, 18],
        "scales": [1.0, 1.25],
        "caseIds": ["stems", "round-punctuation", "digits", "accents"],
        "sourceRunCount": len(runs),
        "rasterizedRunCount": len(runs) * 2,
        "checks": {
            "fontHashesMatch": True,
            "allTexturesNonempty": True,
            "allPngsNonempty": True,
            "allTargetBordersClear": True,
        },
        "sheets": sheets,
    }
    (output_dir / "freetype-report.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("PASS: 192 FreeType raster runs, eight PNG sheets")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
