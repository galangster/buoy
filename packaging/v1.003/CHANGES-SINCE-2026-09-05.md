# Changes since 2026-09-05

## Summary

Baseline: `Buoy-1.002.zip` from the v1.002 GitHub release.
SHA-256: `a8a1c56427469c98610c5559550a9378a7a9109e8c8b257765a2581d2471a1f0`.
Changes implement the owner's 2026-09-06 production-hardening instruction.

## Behavior changes

Combining marks and canonical Omega closure now survive web subsetting.
Inspect q-plus-acute and stacked marks in the accent proof captures.
This fixes missing glyphs in those combinations. NFC/NFD café already worked.
Proof: `evidence/platform-checks-2026-09-06/ios-stacked-marks.png` and shaping-subsets.md.

## Visual changes

No glyph style change was intended. Cleanup removes 14 duplicate line points.
Inspect identity-glyphs.png and native raster sheets for both weights.
The cleanup removes degenerate segments while preserving visible outlines.
Proof: `evidence/independent-raster-parity.json` records 17,112 identical renders.

## Test and infrastructure changes

Gates now fail for missing inputs, draw errors and missing live subset features.
Inspect gates.md, shaping reports and native-raster-validation.md.
These checks prevent incomplete artifacts from appearing to pass validation.
Proof: native-raster/receipt.json binds hosted Windows and Linux captures.

## Packaging changes

Two Latin TTFs are added for server images, totaling 234,788 bytes.
Inspect the filenames and byte counts in manifest.json.
These avoid loading the full TTFs for Latin-only server text.
Proof: manifest.json and native raster full/Latin byte identity.

## Unchanged

OFL.txt is byte-identical to the baseline archive. Its SHA-256 is
`3bf90cd9a08f2051ae5f5a46bc0a05dc5ed086144d56d2f6ed58982e16d10225`.
The archive comparison is recorded in evidence/baseline-identity.json.
No other same-named release file is claimed unchanged.

## Known open items

Read READINESS.md. Independent Fable sign-off is pending authentication.
The universal-profile findings and untested platform paths remain explicit.
