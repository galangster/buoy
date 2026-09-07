**Finding 2 is closed** at the working-tree level, pending merge, which I do not authorize.

What I verified on this checkout against baseline fabafa09 and implementation commit 6263fb3:

- **Label, link, and subset text are restored.** The only diff between docs/index.html and baseline is the fallback disclosure paragraph. The "Version 1.002" label, the absolute GitHub "Browse the release" URL, and the "about 34 KB each, Latin subset" description are byte-for-byte the baseline strings. The relative candidate link that the audit flagged as dead is gone.
- **The release path resolves.** The tree on main contains release/v1.002, so the restored absolute link has a target. GitHub reports v1.002 as the latest release.
- **Fonts match baseline.** Both docs/fonts WOFF2 blobs hash to the baseline objects, not the implementation commit's 1.003 objects.

| File | Baseline blob | Working tree blob | Match |
|---|---|---|---|
| Buoy-Regular.woff2 | 9f0b8dac | 9f0b8dac | yes |
| Buoy-Medium.woff2 | d600d3fb | d600d3fb | yes |

- **The approved archive is unchanged.** dist/Buoy-1.003-candidate-r2.zip hashes to 5f8b405d31eb31accde68c097fc6ea6f6e77a139129cc08d1a61fbf0e7a2c199, matching the r2 approval and archive-receipt.json.
- **Fallback disclosure is consistent.** The retained wording in index.html matches the 0.72% figure recorded in gates.md. The companion change in docs/fallback.css is comment-only, so no served metric values differ from baseline. That file is committed at HEAD and shows no working-tree change.

One residual note, not a blocker. The 0.72% figure was measured during the 1.003 work, while the served web fonts are again v1.002. The audit's 17,112-render parity between the two versions supports applying the figure to v1.002, so the disclosure is not misleading.

The site changes are uncommitted in the working tree alongside the other modified files. Merge and publication remain the owner's call.
