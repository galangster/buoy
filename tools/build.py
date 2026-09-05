"""Drive fontmake for the Backable rounding sweep and for the v1 release.

Interpolation runs first and rounding second. Masters that differ by one corner
stop being compatible, so the filter must never see a master.

Every fontmake call carries the flags Inter's own Makefile passes to its static
targets (``FM_ARGS`` plus ``FM_ARGS_2``):

    --verbose WARNING --overlaps-backend pathops --flatten-components
    --no-autohint --production-names

Radii are ratios of the stem width of that weight, so one invocation runs per
weight rather than one per variant. Every parameter comes from ``params.py``.

    python tools/build.py flat
    python tools/build.py sweep --variants A,B,C,D
    python tools/build.py release
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import params  # noqa: E402

PKG = params.PKG
SOURCE = params.SOURCE
BUILD = params.BUILD
FONTMAKE = PKG / ".venv" / "bin" / "fontmake"

INTER_FLAGS = params.INTER_FLAGS
WEIGHTS = params.SWEEP_WEIGHTS
STEMS = params.STEMS
VARIANTS = params.VARIANTS


def _env():
    env = dict(os.environ)
    existing = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = f"{HERE}{os.pathsep}{existing}" if existing else str(HERE)
    return env


def _run(cmd, log_path: Path):
    log_path.parent.mkdir(parents=True, exist_ok=True)
    start = time.monotonic()
    with log_path.open("w") as log:
        proc = subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT,
                              env=_env(), cwd=PKG)
    return proc.returncode, time.monotonic() - start


def _instances(weights):
    return "Inter (%s)" % "|".join(weights)


def build_flat_ufos(weights=WEIGHTS):
    out = BUILD / "ufo-flat"
    cmd = [
        str(FONTMAKE), "-g", str(SOURCE),
        "-i", _instances(weights),
        "-o", "ufo", "--instance-dir", str(out), "--verbose", "WARNING",
    ]
    return _run(cmd, BUILD / "logs" / "flat-ufo.log")


def build_flat_ttfs(weights=WEIGHTS):
    out = params.FLAT_DIR
    cmd = [
        str(FONTMAKE), "-g", str(SOURCE),
        "-i", _instances(weights),
        "-o", "ttf", "--output-dir", str(out),
        *INTER_FLAGS,
    ]
    return _run(cmd, BUILD / "logs" / "flat-ttf.log")


def build_variant_weight(variant: str, weight: str, out_dir: Path | None = None):
    spec = VARIANTS[variant]
    stem = STEMS[weight]
    out = out_dir if out_dir is not None else BUILD / variant
    filters = ["--filter", "..."]
    if spec["alternates"]:
        filters += [
            "--filter",
            "round_filter::SwapAlternatesFilter("
            f"pre=True, presets='{params.ALTERNATES}')",
        ]
    filters += [
        "--filter",
        "ufo2ft.filters.removeOverlaps::RemoveOverlapsFilter("
        "pre=True, backend='pathops')",
        "--filter",
        "round_filter::RoundCornerFilter("
        f"pre=True, stem={stem}, outer_ratio={spec['outer_ratio']}, "
        f"inner_ratio={spec['inner_ratio']}, "
        f"min_angle={params.MIN_ANGLE}, visual={params.VISUAL}, "
        f"clamp={params.CLAMP}, clamp_stem_end={params.CLAMP_STEM_END})",
    ]
    cmd = [
        str(FONTMAKE), "-g", str(SOURCE),
        "-i", f"Inter {weight}",
        "-o", "ttf", "--output-dir", str(out),
        *INTER_FLAGS, *filters,
    ]
    return _run(cmd, BUILD / "logs" / f"{variant}-{weight}.log")


def _stage(name, fn, times, label, log: Path | None = None):
    """Run one build stage: time it, record it, print it, dump its log if it failed.

    ``fn`` returns ``(returncode, seconds)``. It is a plain call for a
    sequential stage and a finished future's ``result`` for a parallel one, so
    the reporting is the same either way.
    """
    rc, secs = fn()
    times[name] = {"seconds": round(secs, 1), "returncode": rc}
    print(f"{label} rc={rc} {secs:6.1f}s", flush=True)
    if rc and log is not None:
        print(log.read_text()[-3000:], file=sys.stderr)
    return rc


def _record(times, path=None):
    path = path or BUILD / "times.json"
    existing = {}
    if path.exists():
        existing = json.loads(path.read_text())
    existing.update(times)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(existing, indent=2))
    print(f"wrote {path}")


def run_release():
    """Build the two shipping weights, rounded, plus their flat baselines.

    Sequential on purpose. This is the build whose bytes are published, so it
    stays the simplest thing that can produce them.
    """
    times = {}
    stages = [
        ("release-ufo-flat",
         partial(build_flat_ufos, params.RELEASE_WEIGHTS),
         "release ufo-flat", None),
        ("release-flat",
         partial(build_flat_ttfs, params.RELEASE_WEIGHTS),
         "release flat", None),
    ]
    stages += [
        (f"release-{weight}",
         partial(build_variant_weight, "release", weight, params.RAW_DIR),
         f"release {weight}",
         BUILD / "logs" / f"release-{weight}.log")
        for weight in params.RELEASE_WEIGHTS
    ]
    for name, fn, label, log in stages:
        if _stage(name, fn, times, f"{label:20s}", log):
            return times[name]["returncode"]
    _record(times)
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("flat", "sweep", "all", "release"))
    parser.add_argument("--variants", default="A,B,C,D")
    parser.add_argument("--weights", default=None)
    args = parser.parse_args(argv)

    if args.mode == "release":
        return run_release()

    times = {}
    if args.mode in ("flat", "all"):
        for name, fn in (("ufo-flat", build_flat_ufos), ("flat", build_flat_ttfs)):
            if _stage(name, fn, times, f"{name:16s}"):
                return times[name]["returncode"]

    if args.mode in ("sweep", "all"):
        jobs = []
        for variant in args.variants.split(","):
            variant = variant.strip()
            if variant not in VARIANTS:
                print(f"unknown variant {variant}", file=sys.stderr)
                return 2
            weights = (
                args.weights.split(",") if args.weights
                else VARIANTS[variant]["weights"]
            )
            jobs += [(variant, weight) for weight in weights]

        # Each sweep run is an independent fontmake process writing one file
        # into its own variant's --output-dir, so they run together. Results
        # are reported in submission order, whichever finished first.
        with ThreadPoolExecutor(max_workers=os.cpu_count()) as pool:
            futures = [pool.submit(build_variant_weight, *job) for job in jobs]
        for (variant, weight), future in zip(jobs, futures):
            name = f"{variant}-{weight}"
            if _stage(name, future.result, times, f"{variant}-{weight:9s}",
                      BUILD / "logs" / f"{name}.log"):
                return times[name]["returncode"]

    _record(times)
    return 0


if __name__ == "__main__":
    sys.exit(main())
