# Buoy 1.003 local candidate gates

The v1.003 candidate is built locally from Inter commit
`353b61b9f4430d5f420d56605a6e7993e0941470`. It is not published.

## Results

| gate | result | evidence |
| --- | --- | --- |
| two complete builds | PASS | every file in `release/v1.003` had the same SHA-256 on both builds |
| unit and negative gate tests | PASS | collapsed-line rules, exit statuses, required features and combining mappings |
| cubic point parity | PASS | zero failures in `parity.json` |
| self-intersection comparison | PASS | zero introduced offenders in `compare.json`; glyph draw errors fail the command |
| final collapsed lines | PASS | finish removed 4 from Regular and 10 from Medium; zero remain |
| point-index safety | PASS | zero point-attached components and zero glyph instructions before cleanup |
| full TTF shaping | PASS | `shaping-ttf.md` |
| WOFF2 and Latin TTF shaping | PASS | `shaping-subsets.md` |
| OpenType FontBakery | PASS | all four release TTFs and both WOFF2 files expanded to TTF, six files total |
| Universal FontBakery | BASELINE | six failures, the same count and ids as v1.002: `base_has_width`, `case_mapping`, `transformed_components`, once per full font |
| mixed contour/component source glyphs | PASS | `mixed-contours.json`; all 101 per weight compiled as simple glyphs after overlap removal |
| v1.002 raster parity | PASS | 8,556 encoded glyph renders per weight at 12, 16 and 48 px had zero bitmap, position or advance differences; see `independent-raster-parity.json` |
| candidate proof page | PASS | HTTP load plus root CUA inspection on macOS |

`release.py --skip-subset` also passed. That mode now validates existing WOFF2
and Latin TTF artifacts before it copies them.

## Combining marks

The default web repertoire now includes U+0300-036F and U+03A9. U+03A9 closes
the canonical decomposition of the retained ohm sign. The shaping proof checks
NFC and NFD café, double acute text, a live `ccmp` dot-removal substitution,
base-to-mark positioning and mark-to-mark stacking.

Inter does not map U+030B directly. HarfBuzz composes the retained double-acute
letters before mapping, and the NFC/NFD regression passes. This candidate does
not add or redraw an upstream glyph.

## Browser attestation

Root opened `candidate.html` through the local HTTP server on macOS. Both font
files reported loaded. Desktop and 390px layouts passed visual inspection.
Native browser platform-font checks showed `Buoy-Regular` and `Buoy-Medium` on
the q-plus-acute samples, with two glyphs and no fallback. Stacked marks,
NFC/NFD samples, the Omega pair, tabular numerals and identity glyphs looked
correct. The CUA captures are task output and are not saved in this repository.

The fixed specimen generator is a separate sheet. Its clipped 390px screenshot
was removed and is not counted as responsive proof. The CUA inspection of
`candidate.html` is the current responsive proof.

This proves the inspected macOS browser path. It does not prove Windows
DirectWrite, iOS, Android or Linux browser rendering.

## Fallback limit

The generated fallback keeps Buoy's line metrics. The recorded Arial sample
still differs by 0.72% in line width. Text near a wrap boundary can reflow.

## Simplify review

Root completed the required simplify pass before final proof. The applied
changes derive each Latin TTF from its WOFF2, make authoritative measurement
commands return failure statuses, correct parity accounting, and add negative
validation tests. Root found no reason to change glyph style.

## Platform follow-up, 2026-09-06

[Saved iOS simulator captures and Windows blocker](platform-checks-2026-09-06/REPORT.md) extend the earlier browser evidence.
Safari on iOS 26.5 simulator passed. Physical iOS, Windows, Android, and Linux browser claims remain unverified.

## Hosted native raster follow-up

[`native-raster-validation.md`](native-raster-validation.md) documents the
bounded DirectWrite and FreeType raster workflow. Hosted results remain
separate from this local gate report until the workflow runs. The fixed runs
do not constitute native shaping proof.

## Latin universal profile

The two Latin TTFs passed 146 checks, with no errors or fatal results. Four
failures remain: `case_mapping` and `transformed_components` in each weight.
The missing case counterpart is U+214E for U+2132. The transformed components
are retained upstream constructions. These fonts are unhinted; the check
warns about compatibility with downstream autohinting. Neither finding is
claimed as a passing check. See `latin-universal-summary.json`.

## Final native result

Windows DirectWrite and Linux FreeType passed on the frozen candidate fonts.
Root inspected all unique saved sheets. See `native-raster-validation.md` and
`native-raster/receipt.json`. The native test tooling received a root simplify
review. That review enabled tabular numeral checks, preserved overlapping ink,
and limited CI to changes in its test inputs.

The required independent Fable review did not run. Its OAuth session expired
and could not refresh. No Fable approval or final release sign-off is claimed.
