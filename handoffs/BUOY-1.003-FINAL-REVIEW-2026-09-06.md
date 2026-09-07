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

The local archive is `dist/Buoy-1.003-candidate.zip`, 3,024,599 bytes.
SHA-256: `948d11daae359fe6213e9ac7aadc1fbc6c81e46ae6047ae3e2ab72f19d37773a`.
It contains six font files, notices, CSS, instructions, delta notes and evidence.
Every archive entry and frozen release hash passed verification.
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

The independent Fable audit could not authenticate. Its OAuth session expired and could not refresh.
The failed result is `/tmp/buoy-fable-audit.json`. No audit result or approval exists.
Restore Fable authentication through its normal user login flow. Do not bypass authentication.
Then run the read-only audit below. Fix findings with the executor, review the diff, and rerun only affected gates.
If Fable approves, record its exact verdict against the font hashes and tested commit.
Prepare the release action for owner review. Do not infer merge or tag authorization from this handoff.

Universal FontBakery remains non-green: six failures on full TTFs, four on Latin TTFs.
Check ids are base_has_width (full only), case_mapping and transformed_components.
The Latin case gap is U+214E. No direct U+030B exists upstream, although supported Hungarian text recomposes.
Fable must assess these documented limits. Do not silently relabel them as passes.

## Audit instruction, not yet completed

Review Buoy 1.003 for release readiness in the named hardening worktree.
Use read-only tools. Do not modify files, create delegates, commit, push or publish.
Compare implementation commit 6263fb363e88b5be7e89c33ee5cc084571ad20e9 with baseline fabafa0968ccf6348f793aeddc085912aed6472a.
Read the public gate report, native raster receipt, Latin universal summary and package readiness report.
Inspect the six frozen artifacts and source changes for rendering, shaping, metadata, licensing and subset regressions.
Assess the inherited universal-profile failures and missing U+030B and U+214E mappings.
Verify that evidence supports each release claim and that the archive documents its limits.
Report concrete findings with severity and file references. State whether the exact candidate can be approved.
Do not claim browser or physical-device coverage from offscreen or simulator evidence.

## Verification commands

Run from the worktree. Do not repeat passing gates unless their inputs changed.

```sh
git status --short
git diff 6263fb363e88b5be7e89c33ee5cc084571ad20e9 -- release/v1.003 tools .github/workflows
shasum -a 256 dist/Buoy-1.003-candidate.zip
.venv/bin/python -m unittest discover -s tools -p 'test_*.py'
.venv/bin/fontbakery check-opentype -l FAIL release/v1.003/*.ttf
.venv/bin/python tools/shape_proof.py --fonts release/v1.003/*.woff2 release/v1.003/*-Latin.ttf --no-outline-proof
```

Workflow reruns can use workflow_dispatch from the dedicated branch after source changes.
Its push filter excludes evidence-only commits. The successful proof remains valid while inputs match.
The ZIP has a PACKAGE-SHA256.json entry. Verify it after any repackaging.
The archive-receipt.json outside the ZIP records the archive's own hash.

## Acceptance

Independent Fable review has an explicit verdict against unchanged font hashes.
Any blocking findings have a verified correction. The archive and evidence agree.
Unverified platform scope remains explicit. Public release happens only at its authorized boundary.

First action: check Fable authentication, then run the saved read-only audit instruction.
