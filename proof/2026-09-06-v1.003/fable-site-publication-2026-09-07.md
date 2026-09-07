**APPROVE.**

Everything the diff claims checks out against the published release:

- **Font bytes match.** Both docs woff2 files are SHA-256 identical to release/v1.003, and the Regular hash matches the release manifest.
- **Size copy matches.** Regular is 43 KB and Medium is 45 KB on disk, matching the new "43 and 45 KB" prose.
- **Subset copy matches.** The manifest subset covers U+0300-036F and ships mark and mkmk features, so "Latin plus combining marks" and "mark attachment" are accurate. Dropping the old Inter stylistic-set caveat is consistent with the promoted alternates in the manifest.
- **Version copy matches.** The meta line reads 1.003 and the manifest reports 1.003.
- **Both links resolve with HTTP 200.** The release tag v1.003 is published, not draft or prerelease, and both the tag and the release target point at the published commit. The tree link pins to the tag rather than main, which is an improvement over the prior link.

The diff is limited to the three expected files with no stray changes.

Root browser inspection passed at http://127.0.0.1:8794/docs/.
