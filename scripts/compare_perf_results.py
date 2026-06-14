"""
Compare performance results from two test runs.

Three modes:
  1. No args (default):  Compares HEAD vs working tree via git stash.
  2. --baseline <ref>:   Compares <ref> vs current branch.
  3. before.json after.json: Compares two saved JSON files directly.

Usage:
    python scripts/compare_perf_results.py
    python scripts/compare_perf_results.py --baseline main
    python scripts/compare_perf_results.py baseline.json after.json
    python scripts/compare_perf_results.py --runs 1
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile


GREEN = "[improved]"
RED = "[regressed]"
SAME = "[same]"
BIG = "[big-win]"


def git(*args, capture=True):
    result = subprocess.run(
        ["git"] + list(args),
        capture_output=capture,
        text=True,
        timeout=60,
        check=False,
    )
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def stash_save():
    code, out, _ = git(
        "stash", "push", "--include-untracked", "-m", "perf-compare-auto-stash"
    )
    return out if code == 0 else None


def stash_pop():
    git("stash", "pop")


def current_branch():
    _, out, _ = git("rev-parse", "--abbrev-ref", "HEAD")
    return out or "HEAD"


def current_commit():
    _, out, _ = git("rev-parse", "--short", "HEAD")
    return out or "unknown"


def run_test(output_path: str, label: str):
    script = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "perf_test_all_transitions.py"
    )
    if not os.path.exists(script):
        print(f"Error: {script} not found.")
        sys.exit(1)
    print(f"  Running {label}...")
    result = subprocess.run(
        [sys.executable, script, "--runs", "2", "--output", output_path],
        capture_output=True,
        text=True,
        timeout=600,
        check=False,
    )
    if result.returncode != 0:
        print(f"  Error ({label}): {result.stderr[:500]}")
        return False
    for line in result.stdout.strip().split("\n")[-15:]:
        print(f"    {line}")
    return True


def load_results(path: str) -> list:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if "runs" in data and isinstance(data["runs"], list) and data["runs"]:
        return data["runs"][0].get("transitions", [])
    return []


def get_metric_map(transitions):
    return {t.get("name"): t for t in transitions if t.get("name")}


def compare_transitions(before_map, after_map):
    all_names = sorted(set(list(before_map.keys()) + list(after_map.keys())))
    results = []
    for name in all_names:
        b = before_map.get(name, {})
        a = after_map.get(name, {})
        b_max = b.get("max_frame_ms", 0)
        a_max = a.get("max_frame_ms", 0)
        b_avg = b.get("avg_frame_ms", 0)
        a_avg = a.get("avg_frame_ms", 0)

        delta_max = a_max - b_max
        pct_max = (delta_max / b_max * 100) if b_max > 0 else 0

        if b_max == 0 and a_max == 0:
            status = SAME
        elif a_max > 0 and (b_max == 0 or (delta_max > 10 and pct_max > 20)):
            status = RED
        elif a_max > 0 and (delta_max < -10 and pct_max < -20):
            status = GREEN if delta_max > -50 else BIG
        else:
            status = SAME

        if status == RED:
            status_text = "Regressed"
        elif status == BIG:
            status_text = "Big win"
        elif status == GREEN:
            status_text = "Improved"
        else:
            status_text = "Same"

        results.append(
            {
                "name": name,
                "before_max": b_max,
                "after_max": a_max,
                "delta_max": delta_max,
                "before_avg": b_avg,
                "after_avg": a_avg,
                "delta_avg": a_avg - b_avg,
                "status": status,
                "status_text": status_text,
            }
        )
    return results


def print_comparison(results, before_label, after_label):
    if not results:
        print("No transitions to compare.")
        return

    print(f"\n{'='*90}")
    print("  PERFORMANCE COMPARISON")
    print(f"  {before_label}  vs  {after_label}")
    print(f"{'='*90}")
    print(
        f"  {'Transition':<40} {'Before':>10} {'After':>10} {'Δ Max':>10} {'Status':<12}"
    )
    print(f"  {'-'*40} {'-'*10} {'-'*10} {'-'*10} {'-'*12}")

    for r in results:
        name = r["name"]
        b_max = f"{r['before_max']:.1f}" if r["before_max"] else "-"
        a_max = f"{r['after_max']:.1f}" if r["after_max"] else "-"
        d_max = f"{r['delta_max']:+.1f}" if r["delta_max"] != 0 else " 0.0"
        status_text = r["status_text"]
        print(f"  {name:<40} {b_max:>10} {a_max:>10} {d_max:>10}  {status_text}")

    improved = sum(1 for r in results if r["status"] in (GREEN, BIG))
    regressed = sum(1 for r in results if r["status"] == RED)
    same = sum(1 for r in results if r["status"] == SAME)
    print(f"  Summary: {improved} improved, {regressed} regressed, {same} unchanged")

    regressed_items = [r for r in results if r["status"] == RED]
    if regressed_items:
        print("\n  Regressions:")
        for r in regressed_items:
            print(
                f"    {r['name']}: {r['before_max']:.1f}ms → {r['after_max']:.1f}ms (Δ{r['delta_max']:+.1f}ms)"
            )


def mode_default(runs=2):
    print("Mode: HEAD vs working tree (stash-based)")
    print(f"Branch: {current_branch()} ({current_commit()})")

    stash_save()
    tmpdir = tempfile.mkdtemp()
    before_path = os.path.join(tmpdir, "before.json")
    if not run_test(before_path, "HEAD (before)"):
        stash_pop()
        shutil.rmtree(tmpdir, ignore_errors=True)
        sys.exit(1)

    stash_pop()
    after_path = os.path.join(tmpdir, "after.json")
    if not run_test(after_path, "Working tree (after)"):
        shutil.rmtree(tmpdir, ignore_errors=True)
        sys.exit(1)

    before_tx = load_results(before_path)
    after_tx = load_results(after_path)
    results = compare_transitions(get_metric_map(before_tx), get_metric_map(after_tx))
    print_comparison(
        results, f"HEAD ({current_commit()})", "Working tree (uncommitted changes)"
    )
    shutil.rmtree(tmpdir, ignore_errors=True)


def mode_baseline(ref, runs=2):
    original_branch = current_branch()
    original_commit = current_commit()
    print(f"Mode: {ref} vs {original_branch}")

    code, out, _ = git("status", "--porcelain")
    if code == 0 and out.strip():
        print("Error: Working tree has uncommitted changes. Commit or stash first.")
        sys.exit(1)

    tmpdir = tempfile.mkdtemp()
    try:
        git("checkout", ref)
        before_path = os.path.join(tmpdir, "before.json")
        if not run_test(before_path, ref):
            git("checkout", original_branch)
            sys.exit(1)

        git("checkout", original_branch)
        after_path = os.path.join(tmpdir, "after.json")
        if not run_test(after_path, original_branch):
            sys.exit(1)

        before_tx = load_results(before_path)
        after_tx = load_results(after_path)
        results = compare_transitions(
            get_metric_map(before_tx), get_metric_map(after_tx)
        )
        print_comparison(
            results,
            f"{ref} ({current_commit()})",
            f"{original_branch} ({original_commit})",
        )
    finally:
        if current_branch() != original_branch:
            git("checkout", original_branch)
        shutil.rmtree(tmpdir, ignore_errors=True)


def mode_file_compare(path_before, path_after):
    before_tx = load_results(path_before)
    after_tx = load_results(path_after)
    results = compare_transitions(get_metric_map(before_tx), get_metric_map(after_tx))
    print_comparison(
        results, os.path.basename(path_before), os.path.basename(path_after)
    )


def main():
    parser = argparse.ArgumentParser(
        description="Compare transition performance results"
    )
    parser.add_argument("before", nargs="?", default=None, help="Path to before JSON")
    parser.add_argument("after", nargs="?", default=None, help="Path to after JSON")
    parser.add_argument(
        "--baseline", type=str, default=None, help="Git ref to use as baseline"
    )
    parser.add_argument("--runs", type=int, default=2, help="Test runs per side")
    args = parser.parse_args()

    if args.baseline:
        mode_baseline(args.baseline, args.runs)
    elif args.before and args.after:
        mode_file_compare(args.before, args.after)
    else:
        mode_default(args.runs)


if __name__ == "__main__":
    main()
