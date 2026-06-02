"""
LAAVHA batch experiment runner.

Runs laavha_inference.py multiple times via subprocess, parses summary
metrics from stdout, and writes results to CSV.
"""

import argparse
import csv
import re
import subprocess
import sys
import time


def parse_summary(stdout):
    result = {"decisions": "", "handover_count": "", "final_net": ""}
    m = re.search(r"decisions:\s*(\d+)", stdout)
    if m:
        result["decisions"] = m.group(1)
    m = re.search(r"handover_count:\s*(\d+)", stdout)
    if m:
        result["handover_count"] = m.group(1)
    m = re.search(r"final_net:\s*(\d+)", stdout)
    if m:
        result["final_net"] = m.group(1)
    return result


def run_single(run_index, duration, period, flowmon_mode, seed_base,
               algorithm="laavha", fixed_net=1, extra_ns3_args=None,
               time_series_dir=None):
    cmd = [
        sys.executable, "laavha_inference.py",
        "--algorithm", algorithm,
        "--ns3-arg", f"duration={duration}",
        "--ns3-arg", f"period={period}",
        "--ns3-arg", f"flowmonMode={flowmon_mode}",
        "--run-index", str(run_index),
    ]
    if algorithm == "fixed":
        cmd.extend(["--fixed-net", str(fixed_net)])
    seed = seed_base + run_index if seed_base is not None else None
    if seed is not None:
        cmd.extend(["--ns3-arg", f"RngRun={seed}"])
        cmd.extend(["--seed", str(seed)])
    if extra_ns3_args:
        for kv in extra_ns3_args:
            cmd.extend(["--ns3-arg", kv])

    ts_path = ""
    if time_series_dir:
        import os
        os.makedirs(time_series_dir, exist_ok=True)
        ts_path = os.path.abspath(os.path.join(
            time_series_dir,
            f"ts_run{run_index}_{algorithm}_seed{seed or 0}.csv"))
        cmd.extend(["--time-series-output", ts_path])

    row = {
        "run_index": run_index, "algorithm": algorithm,
        "duration": duration, "period": period,
        "flowmonMode": flowmon_mode,
        "seed": seed if seed is not None else "",
        "return_code": "", "elapsed_seconds": "",
        "decisions": "", "handover_count": "", "final_net": "", "error": "",
    }

    print(f"[batch] run {run_index} ({algorithm}): {' '.join(cmd)}")
    t0 = time.time()
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        elapsed = time.time() - t0
        row["return_code"] = proc.returncode
        row["elapsed_seconds"] = f"{elapsed:.1f}"
        combined = proc.stdout + proc.stderr
        if proc.returncode == 0:
            summary = parse_summary(combined)
            row.update(summary)
            if not summary["decisions"]:
                row["error"] = "parse_failed: no decisions in output"
        else:
            row["error"] = f"exit_code={proc.returncode}"
            row.update(parse_summary(combined))
    except subprocess.TimeoutExpired:
        row["return_code"] = -1
        row["elapsed_seconds"] = f"{time.time() - t0:.1f}"
        row["error"] = "timeout"
    except Exception as e:
        row["return_code"] = -1
        row["elapsed_seconds"] = f"{time.time() - t0:.1f}"
        row["error"] = str(e)

    status = "OK" if not row["error"] else row["error"]
    print(f"[batch] run {run_index}: {status}, "
          f"decisions={row['decisions']}, "
          f"handovers={row['handover_count']}, "
          f"elapsed={row['elapsed_seconds']}s")
    return row


def main():
    parser = argparse.ArgumentParser(description="LAAVHA batch experiment runner")
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument("--duration", type=float, default=5.0)
    parser.add_argument("--period", type=float, default=0.1)
    parser.add_argument("--flowmonMode", default="feed")
    parser.add_argument("--output", default="batch_results.csv")
    parser.add_argument("--seed-base", type=int, default=None)
    parser.add_argument("--stop-on-failure", action="store_true")
    parser.add_argument("--algorithm", default="laavha")
    parser.add_argument("--fixed-net", type=int, default=1)
    parser.add_argument("--sweep-algorithm", default=None,
                        help="Comma-separated algorithms")
    parser.add_argument("--sweep-duration", default=None)
    parser.add_argument("--sweep-period", default=None)
    parser.add_argument("--sweep-flowmonMode", default=None)
    parser.add_argument("--randomizeScenario", action="store_true")
    parser.add_argument("--positionJitter", type=float, default=0.0)
    parser.add_argument("--altitudeJitter", type=float, default=0.0)
    parser.add_argument("--ns3-arg", action="append", default=[])
    parser.add_argument("--time-series-dir", default=None,
                        help="Directory for per-run time-series CSVs")
    args = parser.parse_args()

    durations = ([float(x) for x in args.sweep_duration.split(",")]
                 if args.sweep_duration else [args.duration])
    periods = ([float(x) for x in args.sweep_period.split(",")]
               if args.sweep_period else [args.period])
    modes = (args.sweep_flowmonMode.split(",")
             if args.sweep_flowmonMode else [args.flowmonMode])
    algorithms = (args.sweep_algorithm.split(",")
                  if args.sweep_algorithm else [args.algorithm])

    combos = [(d, p, m, a) for d in durations for p in periods
              for m in modes for a in algorithms]
    total = len(combos) * args.runs

    print("=" * 60)
    print("LAAVHA Batch Experiment Runner")
    print(f"  runs_per_combo={args.runs}, output={args.output}")
    print(f"  durations={durations}, periods={periods}, modes={modes}")
    print(f"  algorithms={algorithms}")
    print(f"  combos={len(combos)}, total_runs={total}")
    if args.seed_base is not None:
        print(f"  seed_base={args.seed_base}")
    print("=" * 60)

    fields = [
        "run_index", "algorithm", "duration", "period", "flowmonMode", "seed",
        "return_code", "elapsed_seconds", "decisions",
        "handover_count", "final_net", "error",
    ]

    extra_ns3_args = list(args.ns3_arg)
    if args.randomizeScenario:
        extra_ns3_args.append("randomizeScenario=true")
    if args.positionJitter > 0:
        extra_ns3_args.append(f"positionJitter={args.positionJitter}")
    if args.altitudeJitter > 0:
        extra_ns3_args.append(f"altitudeJitter={args.altitudeJitter}")

    rows = []
    run_idx = 0
    stop = False
    for dur, per, mode, algo in combos:
        if stop:
            break
        for r in range(args.runs):
            row = run_single(run_idx, dur, per, mode, args.seed_base,
                             algorithm=algo, fixed_net=args.fixed_net,
                             extra_ns3_args=extra_ns3_args or None,
                             time_series_dir=args.time_series_dir)
            rows.append(row)
            run_idx += 1
            if args.stop_on_failure and row["error"]:
                print(f"[batch] stopping due to failure at run {run_idx-1}")
                stop = True
                break

    with open(args.output, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\n[batch] Done. {len(rows)} runs written to {args.output}")
    ok = sum(1 for r in rows if not r["error"])
    print(f"[batch] {ok}/{len(rows)} succeeded.")


if __name__ == "__main__":
    main()
