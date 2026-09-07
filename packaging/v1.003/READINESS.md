# Buoy 1.003 readiness

The engineering and native raster checks are complete for this candidate.
Final release sign-off remains pending independent Fable review. That review
could not authenticate because its OAuth session expired.

## Passed

- Two full builds produced identical release hashes.
- Unit and negative tests cover outline cleanup and failure propagation.
- OpenType FontBakery passed all four TTFs and both expanded WOFF2 files.
- HarfBuzz proofs cover features, NFC/NFD, mark attachment and stacking.
- 17,112 encoded glyph renders match v1.002 without bitmap or advance changes.
- macOS browser and iOS 26.5 simulator Safari visual checks passed.
- Windows DirectWrite and Linux FreeType each passed 192 raster runs.
- Root inspected all unique native sheets. Full and Latin sheets match byte for byte.

The hosted run is https://github.com/galangster/buoy/actions/runs/34080077832
on commit 6263fb363e88b5be7e89c33ee5cc084571ad20e9.

## Known limits

Universal FontBakery retains six failures across the full fonts and four
across Latin fonts. Check ids are base_has_width (full only), case_mapping,
and transformed_components. The Latin case gap is U+214E. The transformed
components are upstream constructions. These fonts are unhinted. Do not
assume downstream autohinting preserves their rendering.

The source has no direct U+030B mapping. Supported Hungarian NFC/NFD words
recompose correctly, but arbitrary base-plus-double-acute combinations are
not guaranteed. The web subset does not cover every language.

Native sheets use pre-shaped HarfBuzz runs. They do not prove Windows or
Linux native shaping or browser integration. Physical iOS and Android were
not tested. No italic, bold, variable or display styles are included.

Evidence files accompany the package. No release tag, merge or website
publication was performed for this candidate.
