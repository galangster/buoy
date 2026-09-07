# Buoy 1.003 platform check, 2026-09-06

## Result

Safari passes the inspected iOS simulator cases. Windows DirectWrite remains blocked by an unreachable remote PC.

## iOS simulator proof

FlowDeck booted the previously shut-down iPhone 17 Pro simulator with iOS 26.5.
Safari opened the unchanged candidate page through the existing local HTTP server.
The page reported that both candidate font files loaded.

Visual inspection covered both weights at 11, 12, 13, 14, 16, and 18 px.
NFC/NFD accents, stacked marks, dotless i, the Omega pair, amounts, and identity glyphs rendered correctly.
The 18 px sample wraps on this viewport. It does not clip.
Safari auto-detects the digit sequence as a telephone link. Its blue underline is browser behavior, not a font defect.

This is iOS simulator Safari evidence. It does not prove rendering on a physical iPhone or iPad.

- [Small sizes](ios-small-sizes.png)
- [Accents](ios-accents.png)
- [Stacked marks](ios-stacked-marks.png)
- [Numerals and identity](ios-numerals-identity.png)
- [Font and capture hashes](results.json)

## Windows blocker

Windows App has an existing saved remote PC. The connection returned error `0x204`.
The client reported that it could not connect to the remote PC.
No connection settings, security controls, or remote files were changed.
No DirectWrite rendering check ran.

## Exact remaining check

Use a reachable Windows machine with Chrome or Edge.
Copy the candidate proof directory and `release/v1.003` without changing their relative locations.
Start an HTTP server at the copied repository root:

```sh
python -m http.server 8793 --bind 127.0.0.1
```

Open `http://127.0.0.1:8793/proof/2026-09-06-v1.003/candidate.html`.
Confirm both fonts load. Inspect both weights and every section at 100% browser zoom.
Check small-size stem clarity, comma visibility, accent positioning, clipping, and tabular alignment.
Capture the screen and record the Windows version, browser version, display scale, and font hashes.
Do not substitute macOS emulation, Wine, or an image of another platform for DirectWrite proof.

## Other platforms

No local Android emulator was found. No Android capture ran.
Docker is available, but no Linux browser capture ran.
The font files and their manifest hashes remain unchanged.
