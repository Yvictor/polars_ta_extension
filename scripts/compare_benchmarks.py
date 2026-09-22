"""Compare same-machine benchmark JSONs and gate substantial hot-path regressions."""

import argparse
import json
import math
from pathlib import Path


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("baseline", type=Path)
    p.add_argument("candidate", type=Path)
    p.add_argument("--max-regression", type=float, default=0.25)
    p.add_argument("--output", type=Path)
    p.add_argument(
        "--report-only",
        action="store_true",
        help="Report timing regressions without failing; malformed/incomparable reports still fail",
    )
    args = p.parse_args()
    before = json.loads(args.baseline.read_text())
    after = json.loads(args.candidate.read_text())
    for key in (
        "python",
        "platform",
        "cpu_model",
        "numpy",
        "polars",
        "threads",
        "affinity",
        "repeats",
    ):
        if key not in before or key not in after:
            p.error(f"missing benchmark metadata: {key}")
        if before.get(key) != after.get(key):
            p.error(f"incomparable {key}: {before.get(key)} != {after.get(key)}")
    rows = [
        "| Query / rows | 0.1.6 median ms | 0.2.0 median ms | Speedup |",
        "| --- | ---: | ---: | ---: |",
    ]
    regressions = []
    for name, b in before["results"].items():
        a = after["results"][name]
        if any(not math.isfinite(v["median_ms"]) or v["median_ms"] <= 0 for v in (a, b)):
            p.error(f"invalid timing for {name}")
        ratio = b["median_ms"] / a["median_ms"]
        rows.append(f"| {name} | {b['median_ms']:.4f} | {a['median_ms']:.4f} | {ratio:.2f}x |")
        indicator, size = name.split("/")
        # Tiny/grouped queries are dominated by shared-runner scheduling noise.
        if (
            indicator in ("ema", "rsi", "macd", "atr", "null_rsi", "chunked_ema")
            and int(size) >= 100_000
        ):
            if a["median_ms"] > b["median_ms"] * (1 + args.max_regression):
                regressions.append(name)
    text = "\n".join(rows) + "\n"
    print(text)
    if args.output:
        args.output.write_text(text)
    if regressions:
        message = f"Regressions over {args.max_regression:.0%}: {regressions}"
        if args.report_only:
            print(f"::warning::{message}")
        else:
            raise SystemExit(message)


if __name__ == "__main__":
    main()
