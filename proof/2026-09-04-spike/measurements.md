# Backable rounding sweep - measurements

Spike, 2026-09-04. Every number here is machine measured. No visual
judgment is recorded: that belongs to the orchestrator.

## Provenance

| item | value |
| --- | --- |
| Python | 3.14.7 at `/opt/homebrew/bin/python3`, venv at `.venv` |
| install path | direct `pip install` on 3.14; the uv 3.12 fallback was not needed |
| Inter commit | `353b61b9f4430d5f420d56605a6e7993e0941470` (2024-11-18) |
| source | `vendor/inter/src/Inter-Roman.glyphspackage` |
| UPM | 2048 |
| glyphs in font | 2987 compiled, 897 with contours |
| harfbuzz | hb-view 14.2.1 at `/opt/homebrew/bin` |

Package versions are pinned in `requirements.txt`: fontmake 3.12.1,
ufo2ft 3.9.0, fontTools 4.64.0, ufoLib2 0.18.1, glyphsLib 6.14.0,
skia-pathops 0.9.2, freetype-py 2.3.0, pillow 12.3.0, numpy 2.5.2,
fontbakery 1.1.0.

### Instance names

`fontmake -i` matches a regex against the designspace instance name with
`re.fullmatch`. The names below come from `fontinfo.plist` and are confirmed
by `vendor/inter/misc/tools/gen-instance-ufo.sh`.

| optical size | Regular | Medium | SemiBold | Bold |
| --- | --- | --- | --- | --- |
| text, `opsz` 14 | `Inter Regular` | `Inter Medium` | `Inter SemiBold` | `Inter Bold` |
| display, `opsz` 32 | `Inter Display Regular` | `Inter Display Medium` | `Inter Display SemiBold` | `Inter Display Bold` |

Weight axis values: Regular 400, Medium 490, SemiBold 580, Bold 670. The
whole sweep uses the text optical size.

### fontmake flags copied from `vendor/inter/Makefile`

`FM_ARGS` plus `FM_ARGS_2`, targets `static` and `static_ttf`:

```
--verbose WARNING --overlaps-backend pathops --flatten-components
--no-autohint --production-names
```

`--keep-overlaps` and `--no-production-names` are **not** copied. Inter sets
`--no-production-names` only under `DEBUG`. Inter also builds its statics
from instance UFOs with `-u`; this sweep uses `-i` instead, because the
filters have to run after interpolation.

## Stem widths, flat instance UFOs

Bounding box width, font units at 2048 UPM. `I` is the value the filter
consumes as `stem`.

| weight | `I` | `l` |
| --- | ---: | ---: |
| Regular | 190 | 180 |
| Medium | 229 | 220 |
| SemiBold | 267 | 260 |
| Bold | 306 | 300 |

## Variants

`inner` is 0.6 x `outer` throughout, and both are expressed against the stem
width of that weight.

| variant | outer / stem | inner / stem | weights | alternates |
| --- | ---: | ---: | --- | --- |
| A | 0.35 | 0.21 | all four | no |
| B | 0.45 | 0.27 | all four | no |
| C | 0.50 | 0.30 | all four | no |
| D | 0.50 | 0.30 | Medium | cv02, cv06, ss03 |

## Build wall time

One `fontmake` call per weight, because the stem width differs per weight.

| build | seconds |
| --- | ---: |
| A-Regular | 6.5 |
| A-Medium | 6.7 |
| A-SemiBold | 7.1 |
| A-Bold | 7.4 |
| B-Regular | 6.6 |
| B-Medium | 6.3 |
| B-SemiBold | 6.4 |
| B-Bold | 6.4 |
| C-Regular | 6.2 |
| C-Medium | 6.4 |
| C-SemiBold | 6.5 |
| C-Bold | 7.1 |
| D-Medium | 6.6 |

## Cubic integrity gate

Measured on the flat instance UFOs, after `RemoveOverlapsFilter` and before
`cu2qu`. Rounding one corner replaces one on-curve point with two on-curve
points and two handles, so a glyph's point delta is exactly three times the
corners it rounded. A delta that is not a multiple of three is a
half-inserted corner. The same test on a compiled TTF is meaningless,
because cu2qu rewrites every point count.

| variant | weight | outline glyphs | glyphs touched | corners rounded | delta not a multiple of 3 |
| --- | --- | ---: | ---: | ---: | ---: |
| A | Regular | 897 | 858 | 7292 | 0 |
| A | Medium | 897 | 860 | 7306 | 0 |
| A | SemiBold | 897 | 860 | 7308 | 0 |
| A | Bold | 897 | 860 | 7303 | 0 |
| B | Regular | 897 | 858 | 7292 | 0 |
| B | Medium | 897 | 860 | 7306 | 0 |
| B | SemiBold | 897 | 860 | 7308 | 0 |
| B | Bold | 897 | 860 | 7303 | 0 |
| C | Regular | 897 | 858 | 7292 | 0 |
| C | Medium | 897 | 860 | 7306 | 0 |
| C | SemiBold | 897 | 860 | 7308 | 0 |
| C | Bold | 897 | 860 | 7303 | 0 |
| D | Medium | 897 | 860 | 7306 | 0 |

Orientation calibrated on `o` returned `+1` in every run: outer contours run
counter-clockwise. `skipped_contours` was 0, so no contour was passed through
unparsed. The parity run for D omits `SwapAlternatesFilter`, so it is C's run
by construction; a swap moves outlines between glyph names and changes no
corner count.

## Ink area delta

Sum of |area| over `H a n d g l o v e s zero one two three four five six seven eight nine`, rounded against the flat TTF of the
same weight.

| variant | Regular | Medium | SemiBold | Bold |
| --- | ---: | ---: | ---: | ---: |
| A | -0.54% | -0.69% | -0.81% | -0.94% |
| B | -0.84% | -1.03% | -1.20% | -1.38% |
| C | -0.93% | -1.15% | -1.34% | -1.52% |
| D | - | -1.99% | - | - |

Every variant loses ink. A convex corner gives up more area than the
matching concave corner takes back, and there are more convex corners.
D loses most because the open four and the round comma are lighter shapes.

## Point count delta, compiled TTF

All 2987 glyphs, quadratic. The odd-delta column is reported because it was
asked for; it is not diagnostic after cu2qu. The cubic gate above is.

| variant | weight | flat | rounded | delta | delta % | glyphs touched | odd delta |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| A | Regular | 24009 | 46270 | +22261 | 92.7% | 891 | 303 |
| A | Medium | 23750 | 46124 | +22374 | 94.2% | 889 | 304 |
| A | SemiBold | 23499 | 46082 | +22583 | 96.1% | 889 | 259 |
| A | Bold | 23401 | 46040 | +22639 | 96.7% | 889 | 269 |
| B | Regular | 24009 | 46424 | +22415 | 93.4% | 891 | 291 |
| B | Medium | 23750 | 46314 | +22564 | 95.0% | 889 | 296 |
| B | SemiBold | 23499 | 46260 | +22761 | 96.9% | 889 | 259 |
| B | Bold | 23401 | 46169 | +22768 | 97.3% | 889 | 290 |
| C | Regular | 24009 | 46513 | +22504 | 93.7% | 891 | 306 |
| C | Medium | 23750 | 46432 | +22682 | 95.5% | 889 | 284 |
| C | SemiBold | 23499 | 46369 | +22870 | 97.3% | 889 | 268 |
| C | Bold | 23401 | 46256 | +22855 | 97.7% | 889 | 281 |
| D | Medium | 23750 | 46432 | +22682 | 95.5% | 891 | 284 |

## Self-intersection gate

Every glyph is pushed through `pathops.simplify(fix_winding=True)` and the
area is compared. A rounded contour that crosses itself loses area when
simplified. Gate: any glyph above 0.5 percent.

| variant | weight | glyphs above 0.5% |
| --- | --- | ---: |
| A | Regular | 0 |
| A | Medium | 0 |
| A | SemiBold | 0 |
| A | Bold | 0 |
| B | Regular | 0 |
| B | Medium | 0 |
| B | SemiBold | 0 |
| B | Bold | 0 |
| C | Regular | 0 |
| C | Medium | 0 |
| C | SemiBold | 0 |
| C | Bold | 0 |
| D | Medium | 0 |

Zero offenders in all thirteen builds. The clamp held.

## Per-glyph ink delta, variant C

| glyph | Regular | Medium | SemiBold | Bold |
| --- | ---: | ---: | ---: | ---: |
| `H` | -1.83% | -2.19% | -2.59% | -3.00% |
| `a` | -0.98% | -1.37% | -1.47% | -1.52% |
| `n` | -1.91% | -2.29% | -2.74% | -3.22% |
| `d` | -0.95% | -1.17% | -1.37% | -1.61% |
| `g` | -0.78% | -0.91% | -1.03% | -1.17% |
| `l` | -2.58% | -3.10% | -3.69% | -4.28% |
| `o` | +0.00% | +0.00% | +0.00% | +0.00% |
| `v` | -0.57% | -1.25% | -1.63% | -1.99% |
| `e` | -0.24% | -0.19% | -0.12% | -0.03% |
| `s` | -1.35% | -1.61% | -1.97% | -1.97% |
| `zero` | +0.00% | +0.00% | +0.00% | +0.00% |
| `one` | -2.11% | -2.41% | -2.76% | -3.07% |
| `two` | -1.28% | -1.60% | -1.86% | -2.13% |
| `three` | -1.37% | -1.67% | -1.93% | -2.13% |
| `four` | -1.07% | -1.10% | -1.08% | -1.02% |
| `five` | -1.34% | -1.69% | -2.07% | -2.36% |
| `six` | -0.40% | -0.50% | -0.59% | -0.74% |
| `seven` | -1.36% | -1.79% | -1.78% | -2.13% |
| `eight` | +0.02% | -0.03% | +0.04% | +0.01% |
| `nine` | -0.38% | -0.49% | -0.65% | -0.73% |

## Proof sheets

| file | what it shows |
| --- | --- |
| `sweep-medium.png` | one row per variant, Medium, 96 px |
| `sweep-weights-C.png` | flat and C for each of the four weights, 72 px |
| `identity-glyphs.png` | flat above rounded C, Medium, 400 px em |
| `text-sizes.png` | a 40 word paragraph at 12, 14, 16, 24 and 48 px |
| `diff-overlay-medium.png` | red flat, green rounded C, 300 px em |
| `alternates-D.png` | variant C above variant D, Medium, 96 px |
| `_contact-sheet.png` | all six, downscaled, for a label check |

Every sheet was confirmed non-blank by its pixel histogram. Only the contact
sheet was viewed.
