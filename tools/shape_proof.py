"""Shaping proofs for the finished Buoy fonts.

A feature can survive subsetting as a table entry and still reach no lookup, so
every claim here is made by shaping text with HarfBuzz, never by reading a
table. Two further proofs are outline identity checks: they show that promoting
an alternate to the default actually moved the drawing, and that the retired
default is still reachable through its reverse toggle.

    python tools/shape_proof.py                       # the release TTFs
    python tools/shape_proof.py --fonts a.woff2 b.woff2 --out shaping-woff2.md
"""

from __future__ import annotations

import argparse
import functools
import re
import sys
import tempfile
from pathlib import Path

from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.ttLib import TTFont

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import params  # noqa: E402

HB_SHAPE = params.HB_BIN / "hb-shape"


def shapeable(font: Path):
    """A path HarfBuzz can open.

    The Homebrew harfbuzz build refuses a woff2 face, so a woff2 is expanded
    back to sfnt first. woff2 is a lossless transform of the same tables, so
    the expanded file shapes with the tables the woff2 carries.
    """
    if font.suffix != ".woff2":
        return font, ""
    expanded = Path(tempfile.mkdtemp()) / f"{font.stem}-from-woff2.ttf"
    ttf = TTFont(font)
    ttf.flavor = None
    ttf.save(expanded)
    return expanded, (
        " (expanded from woff2: this harfbuzz build cannot open a woff2 face)"
    )

KERN_TEXT = "AVATAR To Wa."
GLYPH_RE = re.compile(r"([^\[\]|=+@<]+)=(\d+)(?:@[-\d,]+)?\+(-?\d+)")
GID_RE = re.compile(r"^gid\d+$")


@functools.lru_cache(maxsize=None)
def shape(font: Path, text: str, features: str | None = None, extents=False):
    """One `hb-shape` run, memoised on its arguments.

    Shaping the same string with the same feature twice cannot give two
    answers, and the no-glyph-names fallback below re-asks for six runs the
    feature loop has already made.
    """
    args = []
    if features:
        args.append(f"--features={features}")
    if extents:
        args.append("--show-extents")
    args += [str(font), text]
    return params.run_hb("hb-shape", args, label=font.name).strip()


def names(output: str):
    return [m.group(1) for m in GLYPH_RE.finditer(output)]


def advances(output: str):
    return [int(m.group(3)) for m in GLYPH_RE.finditer(output)]


def named(output: str) -> bool:
    """False when the file carries no glyph names, so hb-shape prints gids.

    ``pyftsubset`` writes `post` format 3.0, which is the point of subsetting,
    so a woff2 proof can assert advances and difference but not glyph names.
    """
    return bool(names(output)) and not any(GID_RE.match(n) for n in names(output))


# ---------------------------------------------------------------------------
# outline identity


def outline(glyph_set, name: str):
    """Decomposed outline, in font units.

    A plain recording pen records `addComponent` by name, so two composites
    that draw the same shape through differently named bases would read as
    different. Every pair here has a composite on one side, so the pen has to
    decompose. The glyph set is built once per font and passed in: building it
    per glyph rebuilt it twenty-four times a weight.
    """
    if name not in glyph_set:
        return None
    pen = DecomposingRecordingPen(glyph_set)
    glyph_set[name].draw(pen)
    return pen.value


def swap_identity(release: Path, unswapped: Path, pairs):
    """The swap moved drawings, and the reverse toggle still finds the old one.

    ``build/C`` is the same rounding run without ``SwapAlternatesFilter``, so
    the two builds may differ only by the swap. Buoy's default must equal C's
    alternate, and Buoy's alternate must equal C's default.
    """
    release_font, unswapped_font = TTFont(release), TTFont(unswapped)
    a, b = release_font.getGlyphSet(), unswapped_font.getGlyphSet()
    rows = []
    for default, alternate in pairs:
        got_default, got_alt = outline(a, default), outline(a, alternate)
        want_default, want_alt = outline(b, alternate), outline(b, default)
        if None in (got_default, got_alt, want_default, want_alt):
            rows.append((default, alternate, "SKIP", "glyph missing"))
            continue
        forward = got_default == want_default
        reverse = got_alt == want_alt
        rows.append((
            default, alternate,
            "PASS" if forward and reverse else "FAIL",
            f"default==C[{alternate}]: {forward}, {alternate}==C[{default}]: {reverse}",
        ))
    return rows


# ---------------------------------------------------------------------------
# the shaping cases


def cases(font: Path):
    out = []

    off = shape(font, KERN_TEXT, "-kern")
    on = shape(font, KERN_TEXT, "+kern")
    out.append((
        f'kern on/off "{KERN_TEXT}"',
        "PASS" if off != on else "FAIL",
        f"+kern {on}",
        f"-kern {off}",
    ))

    tnum = shape(font, "0123456789", "+tnum", extents=True)
    widths = set(advances(tnum))
    # The reference advance is shaped, not read from hmtx, because a subset
    # font has no glyph names to look up.
    four_out = shape(font, "4", "+tnum")
    tabular_four = advances(four_out)[0]
    four_name = names(four_out)[0]
    ok = len(widths) == 1 and widths.pop() == tabular_four
    if named(four_out):
        ok = ok and four_name == "four.tf"
    out.append((
        '+tnum --show-extents "0123456789"',
        "PASS" if ok else "FAIL",
        f"one advance for all ten digits, equal to the tabular four "
        f"`{four_name}` ({tabular_four})",
        tnum,
    ))

    for feature, text, expect in (
        # Inter names the slashed zero `zero.slash`.
        ("+zero", "0", "zero.slash"),
        ("+ss02", "Il1O0", None),
        ("+cv02", "4", "four.ss01"),
        ("+cv06", "u", "u.1"),
        ("+ss03", ",;'", None),
    ):
        shaped = shape(font, text, feature)
        plain = shape(font, text)
        if expect and named(shaped):
            ok = expect in names(shaped)
            note = f"expected {expect}"
        else:
            ok = shaped != plain
            note = f"differs from the default `{plain}`"
        out.append((f'{feature} "{text}"', "PASS" if ok else "FAIL", note, shaped))

    swapped = shape(font, "4 u ,")
    if named(swapped):
        ok = names(swapped) == ["four", "space", "u", "space", "comma"]
        note = "the promoted alternates are the default glyphs"
    else:
        # No glyph names here, so the claim is made by difference: every
        # promoted default still has a reachable reverse toggle.
        ok = all(
            shape(font, text, feature) != shape(font, text)
            for text, feature in (("4", "+cv02"), ("u", "+cv06"), (",", "+ss03"))
        )
        note = "each promoted default still has a reachable reverse toggle"
    out.append(('default "4 u ,"', "PASS" if ok else "FAIL", note, swapped))
    return out


SWAP_PAIRS = (
    ("four", "four.ss01"),
    ("four.tf", "four.tf.ss01"),
    ("u", "u.1"),
    ("comma", "comma.ss03"),
    ("quoteright", "quoteright.ss03"),
    ("semicolon", "semicolon.ss03"),
)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fonts", nargs="*", default=None)
    parser.add_argument("--out", default="shaping.md")
    parser.add_argument("--no-outline-proof", action="store_true")
    args = parser.parse_args(argv)

    fonts = (
        [Path(f) for f in args.fonts] if args.fonts
        else [params.RELEASE_DIR / params.ttf_name(w) for w in params.RELEASE_WEIGHTS]
    )

    lines = ["# Shaping proofs, Buoy v1", "",
             "Every row is `hb-shape` output, not a table read.", ""]
    failures = 0
    for font in fonts:
        font, note = shapeable(font)
        lines += [f"## {font.name}{note}", "",
                  "| case | result | expectation | hb-shape |",
                  "| --- | --- | --- | --- |"]
        for case, verdict, note, output in cases(font):
            failures += verdict == "FAIL"
            lines.append(
                f"| `{case}` | **{verdict}** | {note} | `{output[:220]}` |"
            )
        lines.append("")

    if not args.no_outline_proof:
        lines += [
            "## Promoted alternates moved the drawing", "",
            "`build/C` is the same rounding run without `SwapAlternatesFilter`.",
            "The two builds may differ only by the swap, so Buoy's default must",
            "carry C's alternate outline and Buoy's alternate must carry C's",
            "default outline. Compared in TTF outline space.", "",
            "| weight | default | alternate | result | detail |",
            "| --- | --- | --- | --- | --- |",
        ]
        for weight in params.RELEASE_WEIGHTS:
            release = params.RELEASE_DIR / params.ttf_name(weight)
            unswapped = params.BUILD / "C" / params.flat_name(weight)
            if not unswapped.exists():
                lines.append(f"| {weight} | - | - | SKIP | {unswapped} missing |")
                continue
            for default, alternate, verdict, detail in swap_identity(
                release, unswapped, SWAP_PAIRS
            ):
                failures += verdict == "FAIL"
                lines.append(
                    f"| {weight} | `{default}` | `{alternate}` | "
                    f"**{verdict}** | {detail} |"
                )
        lines.append("")

    out_path = params.PROOF_DIR / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines) + "\n")
    print(f"wrote {out_path}  failures={failures}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
