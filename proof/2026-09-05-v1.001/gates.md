# Buoy v1.001 gate record, 2026-09-05

Orchestrator audit, run independently of the lane scripts unless named.

| gate | v1.000 | v1.001 |
| --- | --- | --- |
| usWinAscent / usWinDescent | 1984 / 494 | 2272 / 668 |
| family ink yMax / yMin (Regular, Medium) | 2269/-660, 2272/-668 | unchanged |
| hhea and sTypo trio | 1984 / -494 / 0 | unchanged |
| USE_TYPO_METRICS (fsSelection bit 7) | set | set |
| head.fontRevision vs name ID 5 | 1.0 vs 1.000 | 1.001 vs 1.001 (was 1.0 vs 1.001 before the FONT_REVISION fix) |
| zero-length segments, Regular / Medium (own census) | 978 over 455 glyphs / 1135 over 550 | 4 over 4 / 10 over 9 |
| self-intersecting contour glyphs (pathops area, 0.1%) | 0 | 0 |
| fontbakery check-opentype FAIL | 0 | 0 |
| fontbakery check-universal FAIL | 8 (4 ids x 2) | 6 (base_has_width, case_mapping, transformed_components; all inherited from Inter, all outside the Latin subset) |
| shaping proofs TTF / woff2 (shape_proof.py) | 0 fail | 0 fail |
| woff2 layout features present | | calt case cv02 cv06 kern ss02 ss03 tnum zero |
| woff2 glyphs / ink / tables | | 708 / 2042,-627 inside the win box / gasp, prep, name 0 13 14 kept |
| reproducible bytes, two full builds | yes | yes |
| fallback size-adjust over Arial, own weighted a-z measurement vs tool | | 107.48% vs 107.50% |

macOS rendering: the specimen served over HTTP in Chrome on macOS loaded both
v1.001 woff2 files (status `loaded`, 34,220 and 35,984 bytes transferred) and
the 12 px labels, 16 px body and the `tnum zero ss02` hash line rendered
clean at 1x. Inspected live in the browser pane; not saved as a PNG.

Not run: DirectWrite (Windows) screenshots, which need a Windows session. The
headless Chrome captures (specimen-1440.png, specimen-390.png) are absent on
this run: the sandboxed shell cannot bind port 8787 for `proof.py`, and a
headless Chrome launched from the shell against a pane-hosted server hung.
The v1.000 captures in `proof/2026-09-04-v1/` remain the reference; the line
box and outlines above the baseline are unchanged in v1.001.
