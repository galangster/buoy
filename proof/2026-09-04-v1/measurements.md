# Buoy v1 gate results, 2026-09-04

Every number here was measured on the files in `release/v1.000/`. Nothing is
estimated. Reproduce with `build.py release`, `finish.py`, `measure.py`,
`shape_proof.py`, `release.py`, `proof.py`.

## Files

| file | bytes |
| --- | ---: |
| `Buoy-Regular.ttf` | 386,404 |
| `Buoy-Medium.ttf` | 393,008 |
| `Buoy-Regular.woff2` | 32,040 |
| `Buoy-Medium.woff2` | 33,676 |

SHA-256 for each is in `release/v1.000/manifest.json`.

## Vertical metrics, asserted equal to the flat Inter instance

`finish.py` refuses to write a font whose metrics have moved. Both weights:

| field | value |
| --- | ---: |
| `hhea.ascent` / `descent` / `lineGap` | 1984 / -494 / 0 |
| `OS/2.sTypoAscender` / `Descender` / `LineGap` | 1984 / -494 / 0 |
| `OS/2.usWinAscent` / `usWinDescent` | 1984 / 494 |

`next/font/local` reads `hhea`, not `sTypo`, so the `hhea` trio is the one that
sets `size-adjust` and the fallback overrides.

## Cubic-space point parity, `measure.py parity --variants release`

One rounded corner adds exactly three points, so a delta that is not a multiple
of three is a half-inserted corner. Measured on the instance UFOs, after the
alternate swap and after overlap removal, before cu2qu.

| weight | outline glyphs | touched | corners rounded | point delta | delta not a multiple of 3 | skipped contours |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Regular | 897 | 858 | 7,292 | +21,876 | **0** | 3 |
| Medium | 897 | 860 | 7,306 | +21,918 | **0** | 0 |

Contour orientation calibrated on `o`: +1 (Inter's outer contours are
counter-clockwise). `SwapAlternatesFilter` reports 71 pairs missing in this
run: the parity gate builds its glyph set from contour glyphs only, so the
composite pairs (`comma`, `semicolon`, `four.tf`, the accented `u` family) are
not present to swap. They carry no points of their own, so the gate is
unaffected. The full build swaps all of them.

## Ink and self-intersection, `measure.py compare --variants release`

Self-intersection gate: each glyph is simplified with skia-pathops and the area
change is measured. Anything over 0.5% is a fault.

| weight | ink delta | glyphs compared | glyphs touched | points flat | points rounded | self-intersection faults |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Regular | -1.75% | 2,987 | 893 | 24,009 | 46,513 | **0** |
| Medium | -1.99% | 2,987 | 891 | 23,750 | 46,432 | **0** |

Both stay under the 2% ink line the ruling set, but Medium at -1.99% has no
margin left. Variant C alone measured -0.93% and -1.15%; the promoted
alternates (open four, spurless u) account for the rest. Any later change that
removes ink needs this re-measured before it ships.

## Shaping

`shaping.md` (the TTFs) and `shaping-woff2.md` (the shipping woff2 files).
All cases PASS on all four files. The woff2 files are expanded back to sfnt
first, because this harfbuzz build cannot open a woff2 face.

`shaping.md` also carries the outline-identity proof that promoting an
alternate moved the drawing: `build/C` is the same rounding run without
`SwapAlternatesFilter`, so Buoy's default must carry C's alternate outline and
Buoy's alternate must carry C's default outline. Twelve pairs, all PASS.

## fontbakery 1.1.0

| profile | FAIL | WARN | SKIP | PASS |
| --- | ---: | ---: | ---: | ---: |
| `check-universal` | 11 | 8 | 74 | 143 |
| `check-opentype` | 1 | 2 | 33 | 62 |

Reports: `fb-universal.html`, `fb-opentype.md`. The same universal profile was
run against the flat Inter build of the same two instances, as a baseline:
`fb-universal-flat-inter-baseline.md` (11 FAIL, 7 WARN).

| check id | Buoy | flat Inter | verdict |
| --- | ---: | ---: | --- |
| `base-has-width` | 2 | 2 | inherited from Inter |
| `case-mapping` | 2 | 2 | inherited from Inter |
| `family-win-ascent-and-descent` | 2 | 2 | inherited from Inter |
| `transformed-components` | 2 | 2 | inherited from Inter |
| `no-mac-entries` | 2 | 0 | introduced by this build |
| `opentype-fsselection` | 1 | 0 | introduced by this build |
| `opentype-family-underline-thickness` | 0 | 1 | fixed here |
| `smart-dropout` | 0 | 2 | fixed here |

### Every FAIL left in place, and why

- `opentype-fsselection` (Medium only). fontbakery wants the REGULAR bit set on
  a Medium whose subfamily is `Regular`. The build brief freezes REGULAR off
  for Medium, so the value stands and the check fails. One line in
  `finish.py` reverses it if the owner rules the other way.
- `no-mac-entries` (both). fontbakery treats platform 1 name records as
  obsolete and asks for their removal. The build brief freezes "write every
  record for platform 3/1/0x409 and 1/0/0". The records stay and the check
  fails.
- `family-win-ascent-and-descent` (both). fontbakery wants `usWinAscent` at
  least 2272 and `usWinDescent` at least 668, the real ink extremes. Inter
  ships 1984 and 494 deliberately, and the vertical-metrics assertion requires
  us to keep them. Changing them would change the Windows line box against
  every capture taken so far.
- `base-has-width` (both). `uni0488` (U+0488) has zero advance and is not in
  the GDEF mark class. Inherited from Inter, and the glyph is outside the
  subset ranges, so it is not in either shipping woff2.
- `case-mapping` (both). Glyphs without a case-swapping counterpart.
  Inherited from Inter.
- `transformed-components` (both). Components carrying scale, rotation or an
  inverted direction. Inherited from Inter.

### WARN

`opentype-gdef-mark-chars`, `contour-count`, `unreachable-glyphs` are all
inherited from Inter at the same count. `overlapping-path-segments` fires on
both Buoy files and on one flat Inter file, but on different glyphs: ours are
`sterling`, `lira`, `one.sups.ss01`, `one.subs.ss01`, `one.dnom.ss01` and
`one.numr.ss01`, each carrying a zero-length segment left by an arc that
collapsed. Rasterisers ignore them. They belong to the hand pass.

## Proof set

| file | what it shows |
| --- | --- |
| `text-sizes.png` | the paragraph at 12, 14, 16, 24, 48 and 72 px, Inter Regular above Buoy Regular at each size |
| `identity-glyphs.png` | `a g t j y R 4 0 u i ; , " & @` at 400 px em, Inter Medium above Buoy Medium |
| `diff-overlay.png` | red Inter, green Buoy, dark where they agree, Medium at 300 px em |
| `numerals.png` | the numeric line at 48 px, proportional above `+tnum` |
| `specimen.html` | a static page loading only the two shipping woff2 files |
| `specimen-1440.png` | that page at 1440x1200, device scale 2 |
| `specimen-390.png` | that page at 390x1400, device scale 2 |

Every PNG was checked non-blank by histogram at write time. Playwright is not
installed in this workspace, at the repository root or anywhere else, so the
two page captures were rendered by the locally installed Google Chrome in
headless mode instead, over a local HTTP server. The 72 px line in
`specimen-1440.png` shows semicircular terminals and a round period, so the
page is rendering Buoy and not a fallback face.
