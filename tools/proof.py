"""The v1 proof set, rendered from the finished Buoy TTFs and woff2 files.

Shaped rows go through ``hb-view`` so kerning and the promoted alternates are
real. Glyph sheets go through ``fontTools.pens.freetypePen``. The specimen page
is a static HTML file that loads the two shipping woff2 files and nothing else,
rendered by a real browser because FreeType cannot predict a browser's layout.

Every sheet is composed by ``specimen.py``. This module owns the roster of
sheets, the release fonts they compare, and the specimen page; it does not
re-implement a sheet.

    python tools/proof.py            # every sheet
    python tools/proof.py numerals
"""

from __future__ import annotations

import argparse
import socket
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import params  # noqa: E402
import specimen  # noqa: E402

SCALE = specimen.SCALE

CHROME = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
PORT = 8787

NUMERALS = "$1,000,000  4,213  +12.5%  0.0042 SOL  2026-09-04 14:32"
STATEMENT = "A backable company publishes its decisions before it makes them."


def buoy(weight: str) -> Path:
    return params.RELEASE_DIR / params.ttf_name(weight)


def inter(weight: str) -> Path:
    return params.FLAT_DIR / params.flat_name(weight)


def measure(px: int) -> int:
    """Characters per line that keep every size block about one width wide."""
    return max(24, min(80, int(2600 / px)))


# ---------------------------------------------------------------------------
# sheets


def sheet_text_sizes(out_dir: Path):
    """Six sizes, Inter above Buoy at each.

    Every block is an independent run of ``hb-view``, so the blocks are shaped
    concurrently. ``ThreadPoolExecutor.map`` keeps the row order.
    """
    jobs = [
        (f"{px}px {label}", path, px, measure(px))
        for px in (12, 14, 16, 24, 48, 72)
        for label, path in (
            ("Inter", inter("Regular")), (params.FAMILY, buoy("Regular")),
        )
    ]
    with ThreadPoolExecutor() as pool:
        blocks = list(pool.map(
            lambda job: specimen.shape_block(
                job[1], specimen.PARAGRAPH, job[2], job[3]
            ),
            jobs,
        ))
    rows = [(job[0], block) for job, block in zip(jobs, blocks)]
    return specimen.save(
        specimen.stack_rows(rows, 130 * SCALE, gap=16 * SCALE),
        "text-sizes.png", out_dir,
    )


def sheet_identity_glyphs(out_dir: Path):
    rows = [
        ("Inter Medium",
         specimen.glyph_row(inter("Medium"), params.IDENTITY_GLYPHS, 400)),
        (f"{params.FAMILY} Medium",
         specimen.glyph_row(buoy("Medium"), params.IDENTITY_GLYPHS, 400)),
    ]
    sheet = specimen.stack_rows(rows, 190 * SCALE)
    specimen.draw_label(
        sheet, (specimen.MARGIN // 2, 4),
        " ".join(params.IDENTITY_GLYPHS) + "   400 px em",
    )
    return specimen.save(sheet, "identity-glyphs.png", out_dir)


def sheet_diff_overlay(out_dir: Path):
    sheet = specimen.diff_overlay(
        inter("Medium"), buoy("Medium"), params.DIFF_GLYPHS, 8,
        f"red = Inter   green = {params.FAMILY}   dark = both   "
        f"Medium 300 px em",
    )
    return specimen.save(sheet, "diff-overlay.png", out_dir, threshold=200)


def sheet_numerals(out_dir: Path):
    path = buoy("Regular")
    with ThreadPoolExecutor() as pool:
        images = list(pool.map(
            lambda features: specimen.shape_png(path, NUMERALS, 48, features),
            (None, "+tnum"),
        ))
    rows = list(zip(("proportional", "+tnum"), images))
    return specimen.save(
        specimen.stack_rows(rows, 150 * SCALE), "numerals.png", out_dir
    )


# ---------------------------------------------------------------------------
# the specimen page


SPECIMEN_HTML = """<!doctype html>
<meta charset="utf-8">
<title>{family} {version}</title>
<style>
@font-face {{
  font-family: "{family}";
  src: url("../../release/v{version}/{family}-Regular.woff2") format("woff2");
  font-weight: 400; font-style: normal; font-display: block;
}}
@font-face {{
  font-family: "{family}";
  src: url("../../release/v{version}/{family}-Medium.woff2") format("woff2");
  font-weight: 500; font-style: normal; font-display: block;
}}
html {{ background: #fff; color: #000; }}
body {{ font-family: "{family}"; font-weight: 400; margin: 48px; }}
.statement {{ font-size: 72px; font-weight: 500; letter-spacing: -0.01em;
  line-height: 1.05; margin: 0 0 56px; max-width: 14ch; }}
h2 {{ font-size: 18px; font-weight: 500; margin: 40px 0 12px; }}
p {{ font-size: 16px; font-weight: 400; line-height: 1.55; max-width: 64ch;
  margin: 0 0 16px; }}
.labels {{ font-size: 12px; font-weight: 500; letter-spacing: 0.02em;
  margin: 32px 0 0; }}
.labels span {{ margin-right: 28px; }}
.numeric {{ font-size: 20px; font-variant-numeric: tabular-nums;
  margin: 16px 0 0; }}
.hash {{ font-size: 20px; font-feature-settings: "tnum", "zero", "ss02";
  margin: 12px 0 0; word-break: break-all; }}
</style>
<p class="statement">{statement}</p>
<h2>Heading, 18 px Medium</h2>
<p>{paragraph}</p>
<p>{paragraph}</p>
<p class="labels"><span>RAISE</span><span>DECISION</span><span>BACKERS</span>
<span>CLOSES IN</span><span>OWNERSHIP</span></p>
<p class="numeric">{numerals}</p>
<p class="hash">7Il1O0 9xQmZ4uK1sJ8vB2nR6tW3yE5dA0gH7cF4pL9sN2mV6bX</p>
"""


def write_specimen_html(out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "specimen.html"
    path.write_text(SPECIMEN_HTML.format(
        family=params.FAMILY, version=params.VERSION, statement=STATEMENT,
        paragraph=specimen.PARAGRAPH, numerals=NUMERALS,
    ))
    print(f"{'specimen.html':26s} {path.stat().st_size} bytes")
    return path


def wait_for_port(port: int, timeout: float = 5.0) -> bool:
    """Poll until the local server accepts a connection, or give up.

    A fixed sleep is either too short on a loaded machine or wasted time on an
    idle one, and neither one proves the port is open.
    """
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.25):
                return True
        except OSError:
            time.sleep(0.05)
    return False


def render_specimen(out_dir: Path):
    """Screenshot the specimen page at two viewports with a real browser.

    Playwright is not installed anywhere in this workspace, so the locally
    installed Chrome runs headless instead. The page is served over HTTP
    rather than file:// because Chrome gives every file:// document an opaque
    origin and then refuses the woff2.
    """
    if not CHROME.exists():
        print("no browser found; skipping the page captures")
        return []
    write_specimen_html(out_dir)
    server = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(PORT), "--bind", "127.0.0.1"],
        cwd=params.PKG, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    url = f"http://127.0.0.1:{PORT}/proof/{out_dir.name}/specimen.html"
    out = []
    try:
        if not wait_for_port(PORT):
            raise RuntimeError(f"the proof server never opened port {PORT}")
        for name, width, height in (
            ("specimen-1440.png", 1440, 1200), ("specimen-390.png", 390, 1400),
        ):
            target = out_dir / name
            done = subprocess.run([
                str(CHROME), "--headless=new", "--disable-gpu",
                "--hide-scrollbars", "--force-device-scale-factor=2",
                f"--window-size={width},{height}",
                f"--screenshot={target}", "--virtual-time-budget=4000", url,
            ], capture_output=True, text=True)
            if not target.exists():
                print(f"{name}: chrome wrote nothing\n{done.stderr[-500:]}")
                continue
            image = Image.open(target).convert("L")
            array = np.asarray(image)
            ink = int((array < 128).sum())
            print(f"{name:26s} {image.width}x{image.height} ink_px={ink} "
                  f"unique={len(np.unique(array))}")
            if ink == 0:
                raise RuntimeError(f"{name} is blank")
            out.append(target)
    finally:
        server.terminate()
        server.wait(timeout=10)
    return out


SHEETS = {
    "text-sizes": sheet_text_sizes,
    "identity-glyphs": sheet_identity_glyphs,
    "diff-overlay": sheet_diff_overlay,
    "numerals": sheet_numerals,
    "specimen": render_specimen,
}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("which", nargs="?", default="all")
    args = parser.parse_args(argv)
    if not specimen.HB_VIEW.exists():
        raise SystemExit("hb-view is required")
    for name in (list(SHEETS) if args.which == "all" else [args.which]):
        SHEETS[name](params.PROOF_DIR)
    return 0


if __name__ == "__main__":
    sys.exit(main())
