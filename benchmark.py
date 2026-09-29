"""Reproducible, paired-input benchmark. No third-party dependencies."""
import argparse
import csv
import gc
import json
import os
import platform
import random
import statistics
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from sorting import ALGORITHMS

PATTERNS = ("random", "sorted", "reversed", "nearly_sorted", "duplicates")


def make_input(n, pattern, seed):
    rng = random.Random(seed)
    if pattern == "random":
        values = list(range(n))
        rng.shuffle(values)
        return values
    if pattern == "sorted":
        return list(range(n))
    if pattern == "reversed":
        return list(range(n - 1, -1, -1))
    if pattern == "nearly_sorted":
        values = list(range(n))
        for _ in range(max(1, n // 100)):
            i, j = rng.randrange(n), rng.randrange(n)
            values[i], values[j] = values[j], values[i]
        return values
    if pattern == "duplicates":
        return [rng.randrange(10) for _ in range(n)]
    raise ValueError(pattern)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sizes", nargs="+", type=int, default=[100, 500, 1000, 3000, 6000])
    parser.add_argument("--repeats", type=int, default=7)
    parser.add_argument("--seed", type=int, default=20260929)
    args = parser.parse_args()
    if args.repeats < 2 or any(n < 1 for n in args.sizes):
        parser.error("repeats >= 2 and sizes >= 1 required")
    out = Path("results")
    out.mkdir(exist_ok=True)
    for sort in ALGORITHMS.values():
        for _ in range(3):
            sort(make_input(100, "random", args.seed))
    rows = []
    order_rng = random.Random(args.seed)
    for pattern_index, pattern in enumerate(PATTERNS):
        for n in args.sizes:
            for repeat in range(args.repeats):
                seed = args.seed + pattern_index * 1000000 + n * 100 + repeat
                source = make_input(n, pattern, seed)
                expected = sorted(source)
                names = list(ALGORITHMS)
                order_rng.shuffle(names)
                for name in names:
                    values = source.copy()  # excluded from measured interval
                    enabled = gc.isenabled()
                    gc.disable()
                    try:
                        start = time.perf_counter_ns()
                        ALGORITHMS[name](values)
                        elapsed = time.perf_counter_ns() - start
                    finally:
                        if enabled:
                            gc.enable()
                    if values != expected:
                        raise AssertionError((name, pattern, n, repeat))
                    rows.append(dict(pattern=pattern, n=n, repeat=repeat, seed=seed,
                                     algorithm=name, elapsed_ns=elapsed))
            print(f"Completed {pattern}, n={n}", flush=True)
    with (out / "raw.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    summaries = []
    for pattern in PATTERNS:
        for n in args.sizes:
            for name in ALGORITHMS:
                times = [r["elapsed_ns"] / 1e6 for r in rows
                         if r["pattern"] == pattern and r["n"] == n and r["algorithm"] == name]
                q1, _, q3 = statistics.quantiles(times, n=4, method="inclusive")
                summaries.append(dict(pattern=pattern, n=n, algorithm=name,
                                      median_ms=statistics.median(times), q1_ms=q1, q3_ms=q3,
                                      min_ms=min(times), max_ms=max(times)))
    with (out / "summary.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(summaries[0]))
        writer.writeheader()
        writer.writerows(summaries)
    metadata = dict(timestamp=datetime.now(timezone.utc).isoformat(), python=sys.version,
                    platform=platform.platform(), processor=platform.processor(),
                    logical_cpus=os.cpu_count(), parameters=vars(args),
                    timer="perf_counter_ns", gc="disabled during timing", validated_runs=len(rows))
    (out / "environment.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
