"""Subset a finished Buoy TTF to a Latin woff2 without losing a feature.

The blocks, features and name IDs live in `params`. This module flattens them
for pyftsubset, and then *proves* the result: it reopens the woff2 and fails if
a required layout feature, a required name ID or a required table did not
survive. `release.py` calls it for the sealed woff2 files.

    python tools/subset.py build/release/Buoy-Regular.ttf
    python tools/subset.py build/release/*.ttf --out-dir build/lane/subset
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import unicodedata
from pathlib import Path

from fontTools.ttLib import TTFont

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import params  # noqa: E402

DEFAULT_OUT = params.PKG / "build" / "lane" / "subset"

# `gasp` carries grayscale and symmetric smoothing across the whole ppem
# range; `prep` carries smart dropout control. pyftsubset hands them back only
# while hinting stays on.
REQUIRED_TABLES = ("gasp", "prep", "GSUB", "GPOS", "GDEF", "cmap")


def blocks() -> tuple[tuple[str, str], ...]:
    """The kept ranges, in codepoint order."""
    return tuple(sorted(params.SUBSET_BLOCKS, key=lambda block: block[1]))


def unicodes() -> str:
    return ",".join(rng for _, rng in blocks())


def requested_codepoints() -> set[int]:
    """Expand the authored Unicode ranges for mapping validation."""
    codepoints = set()
    for chunk in unicodes().split(","):
        value = chunk.removeprefix("U+")
        if "-" in value:
            start, end = value.split("-", 1)
            codepoints.update(range(int(start, 16), int(end, 16) + 1))
        else:
            codepoints.add(int(value, 16))
    return codepoints


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


def subset(ttf: Path, output: Path, flavor: str | None = "woff2") -> None:
    cmd = [
        str(params.PYFTSUBSET), str(ttf),
        f"--output-file={output}",
        f"--unicodes={unicodes()}",
        f"--layout-features={','.join(params.SUBSET_FEATURES)}",
        f"--name-IDs={','.join(str(i) for i in params.SUBSET_NAME_IDS)}",
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
    if flavor:
        cmd.append(f"--flavor={flavor}")
    done = subprocess.run(cmd, capture_output=True, text=True)
    if done.returncode != 0:
        raise SystemExit(f"pyftsubset failed on {ttf.name}:\n{done.stderr[-1500:]}")


def verify(before: TTFont, font: TTFont, expected_flavor="woff2") -> tuple[list[str], list[str]]:
    """Reopen the written file and hold it to the three hard requirements.

    Returns (failures, notes). Required mappings and live features fail closed.
    Feature requests that the source font does not provide remain visible as
    notes because subsetting cannot preserve data that is not in the source.
    """
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

    if font.flavor != expected_flavor:
        failures.append(
            f"flavor is {font.flavor!r}, expected {expected_flavor!r}"
        )

    got, source_tags = feature_tags(font), feature_tags(before)
    missing_required = [
        tag for tag in params.SUBSET_REQUIRED_FEATURES
        if tag not in source_tags or tag not in got
    ]
    if missing_required:
        failures.append(
            f"required live features dropped: {', '.join(missing_required)}"
        )
    absent = [tag for tag in params.SUBSET_FEATURES if tag not in source_tags]
    pruned = [tag for tag in params.SUBSET_FEATURES
              if tag in source_tags and tag not in got
              and tag not in params.SUBSET_REQUIRED_FEATURES]
    if absent:
        notes.append(f"not in the source font: {', '.join(absent)}")
    if pruned:
        notes.append(f"non-required features pruned: {', '.join(pruned)}")

    # Every canonical decomposition that the source can map must remain mapped.
    # U+030B is the one retained decomposition Inter does not map directly. Its
    # precomposed letters still shape equivalently and the shaping gate records it.
    source_cmap = before.getBestCmap()
    result_cmap = font.getBestCmap()
    dropped_mappings = sorted(
        (set(source_cmap) & requested_codepoints()) - set(result_cmap)
    )
    if dropped_mappings:
        failures.append(
            "requested mappings dropped: "
            + ", ".join(f"U+{codepoint:04X}" for codepoint in dropped_mappings)
        )
    closure = {
        ord(character)
        for codepoint in result_cmap
        for character in unicodedata.normalize("NFD", chr(codepoint))
        if ord(character) in source_cmap
    }
    missing_closure = sorted(closure - set(result_cmap))
    if missing_closure:
        failures.append(
            "canonical decomposition mappings dropped: "
            + ", ".join(f"U+{codepoint:04X}" for codepoint in missing_closure)
        )
    return failures, notes


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("fonts", nargs="*", type=Path, help="finished TTFs")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    parser.add_argument(
        "--list-ranges", action="store_true",
        help="print the kept blocks and exit",
    )
    args = parser.parse_args(argv)

    if args.list_ranges:
        for name, rng in blocks():
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
        subset(ttf, woff2)
        after = woff2.stat().st_size
        source, result = TTFont(ttf), TTFont(woff2)
        glyphs_before = source["maxp"].numGlyphs
        glyphs_after = result["maxp"].numGlyphs

        problems, notes = verify(source, result)
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
