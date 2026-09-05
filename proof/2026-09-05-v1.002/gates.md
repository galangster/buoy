# Buoy v1.002 gate record, 2026-09-05

v1.002 changes identity only. The copyright holder, manufacturer, designer,
vendor ID and vendor URL become The Creative Company. `glyf`, `loca`, `hmtx`,
`cmap`, `GSUB`, `GPOS`, `gasp` and `prep` are byte-identical to v1.001 in both
weights, so every outline gate below carries over unchanged and was re-run
anyway.

| gate | result |
| --- | --- |
| fontbakery `check-opentype` | 0 FAIL, 63 PASS, 2 WARN |
| fontbakery `check-universal` | 6 FAIL = 3 checks x 2 fonts, 150 PASS |
| the 3 remaining FAILs | `base_has_width`, `case_mapping`, `transformed_components`; each fails identically on flat Inter, and every glyph involved is outside the Latin web subset |
| `head.fontRevision` vs name ID 5 | 1.002 vs `Version 1.002` |
| vendor ID / `fsType` | `TCCO` / 0, installable embedding |
| line box, hhea and sTypo | 1984 / -494 / 0, equal to the flat instance |
| clipping box `usWinAscent` / `usWinDescent` | 2272 / 668, contains the family ink (Regular reaches 2269/660, Medium 2272/668) |
| `USE_TYPO_METRICS` | set |
| point parity vs the flat instance | Regular 858 modified of 858 touched, Medium 860 of 860; orientation constant |
| self-intersections introduced by rounding | 0 |
| ink delta from rounding | Regular -1.75%, Medium -1.99% |
| shaping proofs, TTFs | 0 failures, 0 skips |
| shaping proofs, release woff2 | 0 failures |
| subset verify, both weights | PASS; `gasp`, `prep`, GSUB, GPOS, GDEF, cmap and name IDs 0, 13, 14 all survive |
| reproducible bytes | two full builds of v1.001 gave identical SHA-256 per file; v1.002 uses the same pinned `head.modified` |

## What the shaping proofs now cover

v1.001 claimed every feature was proved by shaping while three of the ten
features the family advertises were never shaped, and the outline-identity
proof reported SKIP because `build/C` was absent. Both are closed:

- `+frac` on `21/64` produces `two.numr one.numr fraction six.dnom four.dnom`.
- `-calt` on `==>` breaks the `uni27F9` ligature back into three glyphs, which
  proves `calt` is live and on by default.
- `+case` on `(A)` is proved **against `-calt`**, not against the default.
  `calt` already swaps in the `.case` parens next to a capital, so comparing
  `+case` with the default shows no difference and would read as a dead
  feature. Held against `-calt`, it produces `parenleft.case`.
- The alternate-swap outline proof runs: `build/C` is the same rounding run
  without `SwapAlternatesFilter`, and Buoy's default carries C's alternate
  outline in both weights.

## Rendering

macOS, Chrome: the specimen page served over HTTP loads both v1.002 woff2
files and renders the 12 px labels, 16 px body and the `tnum zero ss02` hash
line cleanly. Captured at 1440 and 390 CSS px in `specimen-1440.png` and
`specimen-390.png`.

Not run: DirectWrite (Windows). The fonts are unhinted with `gasp` 0x000A,
which is the correct unhinted setting; a screenshot pass on Windows 11 is the
one remaining rendering check.
