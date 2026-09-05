# backable-type

The toolchain that derives **Buoy** from Inter 4.1, and the v1 release it
produced. Buoy is a rounded sans in two weights, published by MetaDAO under the
SIL Open Font License 1.1. Ruling:
`projects/metadao/decisions/backable-single-typeface.md`.

## The release

`release/v1.001/` is the current sealed release; `release/v1.000/` stays as shipped. Each release directory holds:

Builds are reproducible: `finish.py` pins `head.modified` to `head.created`, so two
builds of the same inputs give byte-identical TTFs and woff2 files. Prove it with two
runs of the release sequence and `shasum -a 256 release/v1.000/Buoy-*`.
`Buoy-Regular.ttf` (384,672 bytes), `Buoy-Medium.ttf` (391,092),
`Buoy-Regular.woff2` (33,920), `Buoy-Medium.woff2` (35,684), plus `OFL.txt`
(both copyright notices stacked, Inter's first), `FONTLOG.txt` (the OFL change log, from `tools/FONTLOG.txt`), `NOTICE.md` (what was
modified, from which Inter commit, with which parameters) and `manifest.json`
(bytes and SHA-256 per file, source commit, parameters, tool versions).

## Parameters

Every ruled value lives in `tools/params.py` and nowhere else. Outer radius
0.50 of the measured stem, inner 0.30, `min_angle` 14, `visual` 0.25. Stems are
the bounding box width of `I` in the flat instance: 190 Regular, 229 Medium.
Three alternate groups are promoted to default and their feature tags stay as
reverse toggles: `cv02` open four, `cv06` spurless u, `ss03` round quotes and
commas.

## The tools

- `round_filter.py` — two ufo2ft pre filters. `RoundCornerFilter` replaces a
  hard corner with a tangent circular arc. `SwapAlternatesFilter` makes an
  alternate the default and remaps swapped component bases.
- `build.py` — drives fontmake. Interpolation first, rounding second.
- `finish.py` — name table, vendor ID, `fsType`, `usWeightClass`, `gasp`,
  `prep` smart dropout, family underline. Refuses to write a font whose
  vertical metrics have moved away from the flat instance.
- `measure.py` — stems, the cubic-space parity gate, the ink and
  self-intersection gate.
- `shape_proof.py` — every feature claim proved by shaping, plus an
  outline-identity proof that the alternate swap moved the drawing.
- `release.py` — woff2 subsetting, the release directory, the manifest.
- `proof.py` — the proof sheets and the specimen page.

## Building v1

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
git clone --depth 1 https://github.com/rsms/inter vendor/inter

.venv/bin/python tools/build.py release        # flat + rounded, two weights
.venv/bin/python tools/finish.py               # identity and tables
.venv/bin/python tools/release.py              # woff2, release/, manifest
.venv/bin/python tools/proof.py                # the proof set
```

`vendor/`, `build/`, `dist/` and the virtualenvs are gitignored. `proof/` and
`release/` are committed. Shaping needs harfbuzz from Homebrew.

## Gates

Run before a release is sealed. Results: `proof/2026-09-04-v1/measurements.md`.

```bash
.venv/bin/fontbakery check-universal -l WARN --html proof/<date>/fb-universal.html build/release/*.ttf
.venv/bin/fontbakery check-opentype  -l WARN --ghmarkdown proof/<date>/fb-opentype.md build/release/*.ttf
.venv/bin/python tools/measure.py parity  --variants release   # 0 bad deltas
.venv/bin/python tools/measure.py compare --variants release   # 0 self-intersections
.venv/bin/python tools/shape_proof.py                          # exit 0
.venv/bin/python tools/shape_proof.py --fonts release/v1.000/*.woff2 \
  --out shaping-woff2.md --no-outline-proof
```

## What is unfinished

- No hand pass. The eight identity glyphs, bone-effect blunting at stem ends
  and terminal overshoot are all still mechanical.
- No italic, no display cut, no variable font.
- A glyph carrying both contours and components is rounded on its contour part
  only, and the overlap between the two parts is not removed first.
- A handful of segments still round to zero length. The corner filter now
  prunes its own collapsed arcs, but the cubic to quadratic conversion runs
  after it and makes a few more: 4 in Regular, 10 in Medium. Closing those
  needs a post filter on quadratics.
- Rendering is proved on FreeType and Chrome, not Core Text or DirectWrite.
