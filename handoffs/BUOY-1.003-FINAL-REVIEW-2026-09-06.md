# Buoy 1.003 final review handoff

## Objective

Finish independent review of the validated Buoy 1.003 candidate.
Resolve actionable findings before any release. Do not redesign the glyphs without evidence.

## Current state

Repository: `/Users/galangster/clawd/work/buoy`.
Worktree: `/Users/galangster/clawd/work/buoy/.worktrees/buoy-v1-003-hardening`.
Branch: `codex/buoy-v1-003-hardening-2026-09-06`.
Baseline: `fabafa0968ccf6348f793aeddc085912aed6472a`.
Implementation and CI commit: `6263fb363e88b5be7e89c33ee5cc084571ad20e9`.
Evidence and package commit: `931189e`.
Both commits were sent to `https://github.com/galangster/buoy`.
This handoff is a later local commit. It does not change the tested inputs.
The delegate has stopped writing. The root worktree remains on its original branch.

The original archive remains `dist/Buoy-1.003-candidate.zip`, 3,024,599 bytes.
SHA-256: `948d11daae359fe6213e9ac7aadc1fbc6c81e46ae6047ae3e2ab72f19d37773a`.
Fable placed that archive on hold for a repackage. The successor archive is
`dist/Buoy-1.003-candidate-r2.zip`, 3,028,944 bytes. Its SHA-256 is
`5f8b405d31eb31accde68c097fc6ea6f6e77a139129cc08d1a61fbf0e7a2c199`.
Both archives contain the same six frozen font files.
No merge, release tag or production website publication occurred.

## Authority and constraints

Read current account and repository AGENTS.md instructions before work.
The loaded package was agentic-v2.99.0.
Content hash: `695a0ded24893bea85bffcdfffa87f0734d5bcce2c920bd725c4916272841656`.
Skills hash: `b6957568be3f9a9f0613742cfb55782a1183db3439eae3827f02ba2f552d38b7`.
The package assigns Fable independent review and sign-off.
Codex Sol high executes changes. Use one writer. Delegates do not seal their own changes.
Preserve v1.002 and all unrelated work. Do not rewrite shared history.
Do not publish internal `proof/2026-09-06-production/` receipts.
User authorized autonomous hardening. Final public release and merge remain separate boundaries.
Do not switch the global GitHub login. Dedicated branch pushes used a command-scoped owner credential.

Internal receipts: `proof/2026-09-06-production/preflight.json`, `skills.json`,
and `validation-publication-preflight.json`. The last preflight passed design and publication scope.

## Completed proof

Read `proof/2026-09-06-v1.003/gates.md` and `packaging/v1.003/READINESS.md`.
Two complete builds were byte-identical. Unit and negative gate checks passed.
All six font artifacts passed OpenType checks. Feature shaping and mark regressions passed.
17,112 encoded renders matched v1.002. No new intersections or collapsed lines remain.
MacOS browser and iOS 26.5 simulator Safari visual checks passed.

Native CI: https://github.com/galangster/buoy/actions/runs/34080077832
Windows DirectWrite and Linux FreeType each passed 192 raster runs.
The Windows compiler passed /W4 /WX. Eight unique sheets passed root visual inspection.
Full and Latin sheets match byte for byte at both weights and scales.
Saved captures, reports and hashes are under `proof/2026-09-06-v1.003/native-raster/`.
These are native raster proofs from HarfBuzz runs. They are not native browser shaping proofs.
The root simplify review is complete for both hardening and raster tooling.

## Live surfaces

The worktree HTTP server was running at http://127.0.0.1:8793/.
Candidate: http://127.0.0.1:8793/proof/2026-09-06-v1.003/candidate.html
The in-app browser shows that candidate. Check server liveness before relying on it.
Restart command from the worktree: `python3 -m http.server 8793 --bind 127.0.0.1`.
The iPhone 17 Pro simulator was returned to Shutdown.
Windows App's saved remote PC failed with 0x204. Do not retry that path for raster proof.
No Android or physical iOS capture exists. No Linux or Windows browser capture exists.

## Remaining work and blocker

Fable 5.1 approved the six font artifacts at the recorded hashes. Its audit is
`proof/2026-09-06-v1.003/fable-5.1-audit-2026-09-06.md`. The original archive
remains on hold. Fable 5.1 approved the exact successor archive. Its verdict is
`proof/2026-09-06-v1.003/fable-5.1-r2-approval-2026-09-06.md`.
The approved ZIP remains unchanged. Its internal pending-audit wording records
the state at packaging. This external verdict supersedes that wording.
Finding 2 is closed in the local working tree. The website retains the published
v1.002 label, release link, subset description, and matching specimen fonts.
Fable verified the correction in
`proof/2026-09-06-v1.003/fable-5.1-site-closure-2026-09-07.md`.
Root inspected the rendered page at `http://127.0.0.1:8793/docs/`.
The approved v1.003 ZIP remains unchanged. Nick authorized committing and pushing
the reviewed corrections on 2026-09-07. This handoff accompanies that commit.
Merge, tag, release, and website publication remain unauthorized.
The ignored ZIP archives remain local. Internal production receipts remain untracked.

Universal FontBakery remains non-green: six failures on full TTFs, four on Latin TTFs.
Check ids are base_has_width (full only), case_mapping and transformed_components.
The Latin case gap is U+214E. No direct U+030B exists upstream, although supported Hungarian text recomposes.
Fable assessed these documented limits as acceptable for this release scope.
Do not relabel the remaining failures as passes.

## Revised archive audit instruction, completed

Review the Buoy 1.003 successor candidate archive in the named hardening worktree.
Use read-only tools. Do not modify files, create delegates, commit, push or publish.
Compare it with `dist/Buoy-1.003-candidate.zip` at its recorded SHA-256.
Confirm that all six approved font hashes remain unchanged.
Confirm that findings 1, 3, 4, 5 and 6 are corrected.
Verify PACKAGE-SHA256.json against every archive entry.
Confirm that no internal production receipt is present.
State whether the exact successor archive can be approved.
Keep finding 2 as a separate pre-merge boundary.

## Verification commands

Run from the worktree. Do not repeat passing gates unless their inputs changed.

```sh
git status --short
git diff 6263fb363e88b5be7e89c33ee5cc084571ad20e9 -- release/v1.003 tools .github/workflows
shasum -a 256 dist/Buoy-1.003-candidate.zip
shasum -a 256 dist/Buoy-1.003-candidate-r2.zip
.venv/bin/python tools/test_round_filter.py
.venv/bin/fontbakery check-opentype -l FAIL release/v1.003/*.ttf
.venv/bin/python tools/shape_proof.py --fonts release/v1.003/*.woff2 release/v1.003/*-Latin.ttf --no-outline-proof
```

The direct test command includes `test_subset_validation`. It requires
`build/release/Buoy-Regular.ttf` and `build/release/Buoy-Regular.woff2`.
The build directory is gitignored, so a clean checkout must generate those
artifacts before it runs the test.

Workflow reruns can use workflow_dispatch from the dedicated branch after source changes.
Its push filter excludes evidence-only commits. The successful proof remains valid while inputs match.
The ZIP has a PACKAGE-SHA256.json entry. Verify it after any repackaging.
The archive-receipt.json outside the ZIP records the archive's own hash.

## Acceptance

Independent Fable review approves the unchanged font hashes.
The revised archive audit approves the exact successor archive.
The archive and its evidence agree.
Unverified platform scope remains explicit. Public release happens only at its authorized boundary.

Next action: obtain owner direction for merge or release after the branch push is verified.
Keep merge, tag, release, and website publication as separate owner boundaries.
Continue in this session. Both the package audit and website correction are complete.
