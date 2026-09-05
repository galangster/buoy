# Small-size rendering risk, v1.002

Windows is the one platform Buoy has never been rendered on. This is the
closest check that can be run without a Windows machine, and it is deliberately
narrow: it asks whether the corner rounding costs ink where it matters, at the
sizes where losing ink turns into a visible defect.

**It does not prove the font on Windows.** FreeType grayscale is not
DirectWrite: no ClearType subpixel filtering, no Windows gamma, no gridfit. A
screenshot pass on Windows 11 at 11 to 16 px is still owed.

## Method

Both weights of `release/v1.002` rasterised against the flat Inter instances
they were interpolated from, in `build/flat`. FreeType, `FT_LOAD_NO_HINTING`
plus `FT_RENDER_MODE_NORMAL`, which is the unhinted grayscale path Buoy's
`gasp` asks for. Sizes 11, 12, 13, 14, 16 and 18 pixels per em. Ink is the sum
of coverage over the bitmap; peak coverage is the darkest pixel in a stem.

The control matters. The flat Inter instances are the exact input to the
rounding filter, so a difference between them and Buoy is caused by the
rounding and nothing else. They are **not** shipping Inter: they carry no
`gasp` and no hinting, and they have no Windows track record of their own. So
this measures the rounding, not the platform.

## The mechanism people worry about does not occur

The rounding removes ink from stem *ends*. Stem *darkness* at small sizes is
set by stem *width*, which the filter never touches.

Measured across 120 cells, 10 vertical-stem glyphs (`l i t I r n H E 1 8`) by
6 sizes by 2 weights:

| | |
| --- | --- |
| worst peak-coverage deficit against Inter | **-0.0078** |
| stems dropping below 0.5 peak coverage where Inter's do not | **none** |

A deficit of eight thousandths of one level of coverage is not a rendering
risk. Whatever the rounding costs, it is not stem darkness.

## The large ink losses are the ruled alternates, not the rounding

A first pass flagged the four, the comma and the right quote as losing 9 to 18
percent of Inter's ink. That comparison used the wrong control. Buoy promotes
three of Inter's own alternates to the default drawing: the open four
(`four.ss01`), and the round comma and quotes (`.ss03`). Comparing Buoy's
default against Inter's default therefore measures a **ruled design decision**,
not the filter.

Against the drawing Buoy actually promotes, the loss collapses to the same 2 to
4 percent tax every other glyph pays. Medium:

| glyph | size | vs Inter's default | vs the alternate Buoy promotes |
| --- | ---: | ---: | ---: |
| `four` | 11 px | -17.68% | **-3.02%** |
| `four` | 16 px | -17.37% | **-2.94%** |
| `comma` | 11 px | -9.19% | **-3.75%** |
| `comma` | 16 px | -4.75% | **-0.52%** |
| `quoteright` | 11 px | -9.27% | **-3.74%** |
| `quoteright` | 16 px | -4.48% | **-0.40%** |

Aggregate ink loss over the whole tested set is 1.9 to 2.5 percent, and it is
flat from 11 px to 18 px. A rasterisation problem grows as size falls. This
does not.

## What the pictures show

`render-risk-12.png` and `render-risk-16.png` put Buoy above Inter at 12 and 16
pixels per em, magnified 8 times with nearest-neighbour so the pixel grid is
legible. At 12 px the two are near-indistinguishable in stem weight and
rhythm. The differences a reader can actually see are the promoted alternates:
Buoy's four is open where Inter's is closed, and Buoy's comma and quotes are
round where Inter's are cut. Nothing blurs, fills in, or drops out.

## What is left

- **Windows, unproved.** One screenshot pass on Windows 11 in Chrome or Edge at
  11, 12, 14 and 16 px closes it.
- **The round comma at 11 to 13 px** is the one glyph worth a human look on
  hardware. Its waist is the thinnest thing the rounding touches; it stays
  above 0.34 peak coverage under an adverse vertical pixel phase, so it softens
  rather than disappears, but it is the first thing that would show if
  DirectWrite were harsher than FreeType.
- **`prep` never ran here**, because the load was unhinted. On the grayscale
  non-gridfit path `gasp` asks for, it will not run on Windows either. The
  smart-dropout control is insurance for a monochrome fallback, not what
  protects the font at 11 px.

Numbers in this file were re-derived independently of the script that first
produced them; two of the original report's conclusions did not survive that
check and are corrected above.
