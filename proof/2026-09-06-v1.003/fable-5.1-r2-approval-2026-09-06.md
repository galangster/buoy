**Verdict: APPROVE** the revised archive `dist/Buoy-1.003-candidate-r2.zip` at SHA-256 `5f8b405d31eb31accde68c097fc6ea6f6e77a139129cc08d1a61fbf0e7a2c199` (3,028,944 bytes, 58 entries) as the Buoy 1.003 candidate package. The six font artifacts stay approved at the hashes from the earlier audit. Finding 2 is still open and blocks merge, not this package.

## What I verified

- **Archive integrity.** CRC test passes on both zips. The original archive still hashes to `948d11da…773a` and its sidecar and the receipt's baseline block agree. The r2 sidecar and `packaging/v1.003/archive-receipt.json` match the actual r2 bytes, hash, and entry count.
- **Entry hashes.** All 57 entries in `PACKAGE-SHA256.json` match by SHA-256. The only uncovered entry is that file itself, as documented.
- **Font hashes.** All six fonts inside r2 match the approved set byte for byte, and match the worktree copies. Zero diff against tested commit `6263fb36` for release files, tools, workflows, and docs.
- **Original preserved.** 51 of 57 original entries carry byte-identical. The six changed entries are documentation only: package README, READINESS, CHANGES, evidence gates.json, gates.md, and the manifest hash file. One entry was added, a copy of the Fable audit. No production receipt or preflight file is in the zip.
- **Zip matches worktree.** Every changed doc entry in the zip equals its worktree source, including the audit copy.

## Findings 1, 3, 4, 5, 6: resolved

- **1.** Evidence gates.json now records the native raster run as pass with run URL and tested commit, and splits `iosSimulatorSafari: true` from `physicalIos: false`. Numbers agree with the shipped receipt and both renderer reports (96 source runs, 192 raster runs each). I confirmed the full versus Latin sheet byte identity for all eight pairs.
- **3.** Handoff now runs `tools/test_round_filter.py` directly. The vacuous unittest discovery command is gone.
- **4.** Handoff states the gitignored build artifacts that `test_subset_validation` needs.
- **5.** gates.md carries an INDIRECT row naming both skipped weights and the 17,112-render parity as coverage. The two SKIP rows in shaping-ttf.md match.
- **6.** READINESS now says the macOS capture is not stored and the iOS simulator captures are.
- Stale "OAuth expired" wording is replaced everywhere in the diff. No document overclaims package approval.

## Prior permission limit closed

I opened all six fonts with fontTools from the zip bytes. Family names carry no "Inter" string, copyright and OFL name records are present, fsType is 0, weight classes are 400 and 500, revision is 1.003. U+030B and U+214E are absent and U+2132 and U+0151 are present, exactly as documented. Tables contain no hinting instructions beyond prep and gasp, consistent with the stated autohinting caveat.

## Remaining blockers and scope limits

- **Finding 2, pre-merge.** `docs/index.html` still shows "Version 1.003 candidate" and links to `../release/v1.003/`. Unchanged by this pass, correctly. Fix on the branch before merge.
- **Owner boundaries.** Merge, tag, release, and site publication remain unauthorized by this review.
- **Self-description.** The zip's own gates.json and READINESS say the successor audit is pending. That cannot change without changing the hash. Record this approval outside the zip, in the receipt and handoff.
- **Not reverified.** The Actions run page (no network), passing font gates (inputs hash-identical), and any browser or physical-device rendering beyond the stated macOS browser and iOS simulator evidence. Universal FontBakery failures remain labelled failures, as before.

**Next action.** Record this verdict against the r2 hash in the receipt and handoff, then correct finding 2 on the branch before any merge. Continue in this session or a fresh one, either is fine; the state is fully captured on disk.
