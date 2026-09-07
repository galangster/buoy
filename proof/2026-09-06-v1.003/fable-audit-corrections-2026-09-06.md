# Buoy 1.003 Fable audit corrections

## Scope

This correction covers Fable findings 1, 3, 4, 5 and 6. Finding 2 remains a
separate pre-merge boundary. This work did not modify `docs/index.html` or any
file under `docs/fonts/`.

Fable 5.1 approved the six frozen font artifacts. It placed the original
candidate archive on hold for a repackage. The successor candidate still
requires a revised archive audit. No final package approval is claimed.

## Corrections

- Finding 1: `gates.json` now records the hosted native raster pass. It also
  separates iOS simulator evidence from physical iOS coverage.
- Finding 3: the handoff now runs `tools/test_round_filter.py` directly.
- Finding 4: the handoff states that `test_subset_validation` requires the
  gitignored `build/release` artifacts.
- Finding 5: `gates.md` now records both skipped direct rows. It identifies the
  17,112-render v1.002 parity as indirect coverage.
- Finding 6: `READINESS.md` now states that the macOS browser capture is not
  stored. It distinguishes the stored iOS simulator captures.
- Stale authentication statements now reference the completed Fable font
  approval and the pending successor archive audit.

## Archives

Original baseline archive:

- File: `dist/Buoy-1.003-candidate.zip`
- Bytes: 3,024,599
- SHA-256: `948d11daae359fe6213e9ac7aadc1fbc6c81e46ae6047ae3e2ab72f19d37773a`

Successor candidate archive:

- File: `dist/Buoy-1.003-candidate-r2.zip`
- Bytes: 3,028,944
- SHA-256: `5f8b405d31eb31accde68c097fc6ea6f6e77a139129cc08d1a61fbf0e7a2c199`
- Entries: 58 total, including 57 entries in `PACKAGE-SHA256.json`

## Frozen font hashes

| artifact | SHA-256 |
| --- | --- |
| `Buoy-Regular.ttf` | `820d453532dfbb4f93361a0c9b72e2651ab32cf6e51715443615ab5ec2066732` |
| `Buoy-Medium.ttf` | `793e936389e1b25140cb93238772a647236ce7977ac98cf9593e9c4a6e61420e` |
| `Buoy-Regular.woff2` | `4631ec5613a96c8bae1a329a47f88f2c6d66335908fd1fddf485686f7f99066c` |
| `Buoy-Medium.woff2` | `7073bfe7316103bb630615292245794ca56e3ac0c8c670868d3a4adb1461b8c0` |
| `Buoy-Regular-Latin.ttf` | `fa4a855d623c22351803e8341bd31240ff843daaf6aaae07d693e400530c27f5` |
| `Buoy-Medium-Latin.ttf` | `46e222c7d270ef6978ecccf0144b920bff43411491a0ed275489c532da83deb1` |

## Verification

- The original archive kept its recorded SHA-256.
- The successor ZIP CRC check passed.
- Every entry matched its `PACKAGE-SHA256.json` value.
- All six archive font hashes matched the approved hashes.
- No internal production receipt appeared in the successor archive.
- JSON parsing and `git diff --check` passed before packaging.
- Source font gates were not repeated because no font input changed.

## Remaining boundary

Fable must audit the exact successor archive before package approval. Finding 2
must be corrected before merge. Merge, tag, release and website publication
remain separate owner boundaries.
