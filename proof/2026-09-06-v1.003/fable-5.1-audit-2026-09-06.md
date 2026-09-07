# Buoy 1.003 independent audit, Fable 5.1, 2026-09-06

**Verdict.** The six frozen font artifacts are **approved** at the hashes below, tested at commit `6263fb363e88b5be7e89c33ee5cc084571ad20e9`. The candidate archive `Buoy-1.003-candidate.zip`, SHA-256 `948d11daae359fe6213e9ac7aadc1fbc6c81e46ae6047ae3e2ab72f19d37773a`, is on **hold for one repackage** because its evidence bundle carries a stale machine receipt that contradicts the human-readable reports. No finding touches the fonts. Merge and tag remain separate owner boundaries and carry one additional pre-merge fix.

| artifact | SHA-256 |
| --- | --- |
| Buoy-Regular.ttf | 820d453532dfbb4f93361a0c9b72e2651ab32cf6e51715443615ab5ec2066732 |
| Buoy-Medium.ttf | 793e936389e1b25140cb93238772a647236ce7977ac98cf9593e9c4a6e61420e |
| Buoy-Regular.woff2 | 4631ec5613a96c8bae1a329a47f88f2c6d66335908fd1fddf485686f7f99066c |
| Buoy-Medium.woff2 | 7073bfe7316103bb630615292245794ca56e3ac0c8c670868d3a4adb1461b8c0 |
| Buoy-Regular-Latin.ttf | fa4a855d623c22351803e8341bd31240ff843daaf6aaae07d693e400530c27f5 |
| Buoy-Medium-Latin.ttf | 46e222c7d270ef6978ecccf0144b920bff43411491a0ed275489c532da83deb1 |

## What I verified

- **Inputs unchanged.** Worktree `release/v1.003`, `tools`, and `.github/workflows` have zero diff against the implementation commit. The worktree hashes match `manifest.json`, the DirectWrite and FreeType reports, the fixture rows, and `PACKAGE-SHA256.json` inside the zip. The archive zip entries match the worktree byte for byte. The fixture hash matches the receipt. The only local change is the untracked `proof/2026-09-06-production/` directory, which is correctly absent from the zip.
- **Baseline comparison.** The diff from `fabafa09` to `6263fb36` touches 56 files. Source changes are confined to subsetting, glyf cleanup, gate exit statuses, shaping cases, release packaging, and the native raster tooling. No outline source or rounding parameter changed. Version and proof-directory constants moved to 1.003.
- **Source review.** `tools/subset.py` now fails closed on dropped required features, dropped requested mappings, and broken canonical closure. `tools/glyf_cleanup.py` refuses to reindex when instructions or point-attached components exist and only removes consecutive equal on-curve points, which draw nothing. `tools/release.py` derives each Latin TTF from its validated WOFF2 and re-validates on the skip path. `tools/measure.py` returns failure statuses and no longer swallows draw errors. The workflow pins actions by hash, uses read-only permissions, and asserts run counts and report flags.
- **Licensing and metadata.** OFL.txt is byte-identical to the v1.002 baseline. NOTICE.md now lists all six files, the cleanup, and the combining-mark change. FONTLOG has the 1.003 entry. Subset name IDs keep copyright and license records. Universal checks on the Latin TTFs pass every naming check.
- **Evidence I inspected directly.** One DirectWrite sheet at 125 percent shows all four rows at six sizes with stacked marks, dotless i, the Omega pair, and tabular digits intact. The iOS simulator capture of stacked marks matches its description, including the Safari telephone-link underline noted in the report.

## Findings

1. **Medium, archive evidence conflict.** `proof/2026-09-06-v1.003/gates.json` still records `nativeRasterValidation.status` as awaiting the hosted run and `platformClaims.ios` as false. The same file ships in the zip as `evidence/gates.json`, beside a receipt and reports that say the run passed. Update the JSON, repackage, and re-verify `PACKAGE-SHA256.json`. The zip hash will change.
2. **Medium, merge boundary only.** `docs/index.html` now labels the site "Version 1.003 candidate" and links to `../release/v1.003/`, and `docs/fonts` already carries the 1.003 WOFF2 files. If GitHub Pages serves `docs/` from main, a merge publishes candidate wording and a dead relative link. Fix before merge, not before repackage.
3. **Low, vacuous gate command.** The handoff lists `python -m unittest discover -s tools -p 'test_*.py'`. `tools/test_round_filter.py` defines no TestCase, so discovery runs zero tests and exits green. The real gate is running the script directly, which exits 1 on failure. Correct the documented command.
4. **Low, non-hermetic test.** `test_subset_validation` reads fonts from the gitignored `build/release` directory and fails on a clean checkout. Acceptable for a local gate, but it should be stated.
5. **Low, unsurfaced skip.** `shaping-ttf.md` marks the "promoted alternates moved the drawing" proof as SKIP for both weights because `build/C` is missing. `gates.md` does not mention this. The claim is covered indirectly by the 17,112-render parity with v1.002, and should be described that way.
6. **Low, wording.** `READINESS.md` in the zip states the macOS browser check passed without noting that the capture is not stored. `gates.md` and the README carry that caveat. Add it to READINESS.

## Documented limits, assessed

- **Universal profile failures.** `case_mapping` flags U+2132 without U+214E. Inter upstream has no turned small f. This has no effect on Latin text. `transformed_components` lists mirrored upstream constructions such as d from b and q from p. Mirrored components render correctly under nonzero winding, and the DirectWrite sheet shows q with attached marks at every size. The practical cost is autohinting incompatibility, which READINESS states. `base_has_width` is full-font only and inherited. All three are labeled failures or baseline, never passes. That is correct.
- **U+030B.** The double acute is not mapped. HarfBuzz composes O plus U+030B to the precomposed letter before lookup, so supported Hungarian text works, and the shaping rows prove it. Any base without a precomposed double-acute form will fall back to another font for the mark. READINESS states this. Acceptable for this release scope.
- **Platform scope.** The native evidence is raster-only from pre-shaped runs. No Windows or Linux browser, physical iOS, or Android evidence exists. Every document I read states this correctly. I make no browser or device claim from that evidence.

## Limitations of this audit

- Bash was denied for Python, `ttx`, and `unzip -t` execution. I could not open the font tables directly. Coverage of cmap, name, and OS/2 rests on the FontBakery summaries, the HarfBuzz shaping rows, the fixture glyph ids, and the hash chain.
- No network or `gh` access. I did not fetch the Actions run. The saved reports carry consistent OS and renderer details, but the run page itself is unverified by me.
- Bash was denied for reading outside the worktree. The account AGENTS.md loaded through the Read tool. No repository AGENTS.md exists. I did not re-run the MetaDAO preflight because the task is read-only and the production receipts record a passing preflight.
- Passing gates were not rerun. Their inputs are hash-identical to the tested commit.

**Next action.** Have the executor correct findings 1, 3, 5, and 6 in documentation only, repackage, and record the new archive hash. Then fix finding 2 on the branch before any merge. The font hashes above stay the approved set.
