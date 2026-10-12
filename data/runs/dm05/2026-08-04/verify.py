#!/usr/bin/env python3
"""Recompute the submitted DM0.5 results from the retained episode records."""

import argparse
import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path
from statistics import mean


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-root", type=Path,
                        help="Optionally verify original JSON file hashes")
    args = parser.parse_args()
    directory = Path(__file__).resolve().parent
    manifest = json.loads((directory / "run_manifest.json").read_text())
    result = json.loads((directory.parents[2] / "results/dm05.json").read_text())
    mapping = manifest["suiteMapping"]
    seeds = manifest["seeds"]
    expected_runs = {
        (suite, level, seed)
        for suite in mapping.values()
        for level in range(3)
        for seed in seeds
    }
    runs = {}
    for run in manifest["runs"]:
        key = (run["suite"], run["level"], run["seed"])
        assert key not in runs, f"Duplicate run: {key}"
        runs[key] = run
        if args.raw_root:
            source = args.raw_root / run["sourceFile"]
            digest = hashlib.sha256(source.read_bytes()).hexdigest()
            assert digest == run["sourceSha256"], source
    assert set(runs) == expected_runs

    episodes = defaultdict(list)
    with (directory / "episodes.csv").open(newline="") as handle:
        for row in csv.DictReader(handle):
            key = (row["suite"], int(row["level"]), int(row["seed"]))
            assert row["success"] in ("0", "1")
            episode = {
                "task": int(row["task_id"]),
                "episode": int(row["episode_idx"]),
                "success": int(row["success"]),
                "cost": float(row["cost"]),
                "attempts": int(row["attempts"]),
            }
            assert math.isfinite(episode["cost"])
            assert episode["attempts"] >= 1
            episodes[key].append(episode)
    assert set(episodes) == expected_runs

    statistics = {}
    for key, run in runs.items():
        rows = episodes[key]
        expected_ids = {
            (task, episode)
            for task in range(run["numTasks"])
            for episode in range(run["trialsPerTask"])
        }
        actual_ids = {(row["task"], row["episode"]) for row in rows}
        assert actual_ids == expected_ids, f"Incomplete episode IDs: {key}"
        assert len(rows) == len(actual_ids), f"Duplicate episodes: {key}"
        assert len(rows) == run["numEpisodes"]
        successes = sum(row["success"] for row in rows)
        cost = sum(row["cost"] for row in rows)
        assert successes == run["numSuccesses"]
        assert math.isclose(cost, run["totalCumulativeCost"], abs_tol=1e-9)
        statistics[key] = {
            "episodes": len(rows), "successes": successes,
            "sr": successes / len(rows), "cc": cost / len(rows),
        }

    assert len(result["tasks"]) == len(mapping) == 11
    assert {task["name"] for task in result["tasks"]} == set(mapping)
    for task in result["tasks"]:
        suite = mapping[task["name"]]
        records = [statistics[(suite, level, seed)]
                   for level in range(3) for seed in seeds]
        assert task["numEpisodes"] == sum(row["episodes"] for row in records)
        assert task["numSuccesses"] == sum(row["successes"] for row in records)
        for metric in ("sr", "cc") if task["hasCC"] else ("sr",):
            expected = [mean(statistics[(suite, level, seed)][metric]
                             for seed in seeds) for level in range(3)]
            actual = task["data"][metric]
            assert len(actual) == 3
            assert all(math.isclose(a, b, rel_tol=1e-12, abs_tol=1e-12)
                       for a, b in zip(actual, expected)), (suite, metric)

    total = sum(row["episodes"] for row in statistics.values())
    successes = sum(row["successes"] for row in statistics.values())
    assert len(runs) == 99 and total == 5100 and successes == 3202
    print(f"Verified {len(runs)} runs, {total} episodes, {successes} successes.")
    for level in range(3):
        sr = 100 * mean(task["data"]["sr"][level] for task in result["tasks"])
        cc = mean(task["data"]["cc"][level]
                  for task in result["tasks"] if task["hasCC"])
        print(f"L{level}: SR={sr:.6f}%, Safety CC={cc:.6f}")
    if args.raw_root:
        print("Verified SHA-256 hashes of all 99 original result files.")


if __name__ == "__main__":
    main()
