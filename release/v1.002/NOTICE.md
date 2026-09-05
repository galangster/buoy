# NOTICE

Buoy 1.002 is a modified version of Inter, published by
The Creative Company under the SIL Open Font License, Version 1.1. See
`OFL.txt` for the license and for both copyright notices.

## What was modified

Every hard corner is replaced by a tangent circular arc. Radii are ratios of
the measured stem width of that weight, so terminals stay semicircular at both
weights.

| parameter | value |
| --- | ---: |
| outer radius | 0.5 x stem |
| inner radius | 0.3 x stem |
| stem, Regular / Medium | 190 / 229 units at 2048 upem |
| minimum corner angle | 14.0 degrees |
| visual correction | 0.25 |
| cut-back clamp, normal / stem end | 0.4 / 0.5 |
| weight compensation | none |

Three groups of stylistic alternates become the default drawings: the open
four, the spurless u, and the round quotes and commas. Their feature tags
(cv02, cv06, ss03) still work, now as reverse toggles
back to Inter's drawings.

The name table, vendor ID, unique font identifier, version and embedding
permission are rewritten. Inter's trademark record is removed. Inter's vertical
metrics are preserved exactly, because `next/font/local` derives its fallback
overrides from them.

`gasp` is set to grayscale and symmetric smoothing across the whole range, and
`prep` carries smart dropout control. The fonts are otherwise unhinted.

Nothing else is changed. No outline is redrawn by hand.

## Source

- Inter, https://github.com/rsms/inter, commit `353b61b9f4430d5f420d56605a6e7993e0941470`.
- Roman masters only, text optical size, instances `Inter Regular` and
  `Inter Medium`.

## Weights

| file | weight | usWeightClass |
| --- | --- | --- |
| `Buoy-Regular.woff2` | Regular | 400 |
| `Buoy-Medium.woff2` | Medium | 500 |

## Build

Built on 2026-09-05 from the toolchain in this repository,
https://github.com/galangster/buoy. Tool versions:

- brotli 1.2.0
- fontbakery 1.1.0
- fontmake 3.12.1
- fonttools 4.64.0
- glyphsLib 6.14.0
- harfbuzz hb-shape (HarfBuzz) 14.2.1
- python 3.14.7
- skia-pathops 0.9.2
- ufo2ft 3.9.0
- ufoLib2 0.18.1
- uharfbuzz 0.56.1

Gates and proof: `proof/2026-09-05-v1.002/`.
