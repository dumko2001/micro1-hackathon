#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path


def load_trials(path: Path) -> list[dict]:
    result_path = path / "result.json" if path.is_dir() else path
    if result_path.is_file():
        value = json.loads(result_path.read_text())
        if "task_name" in value:
            return [value]

    trials = []
    for candidate in sorted(path.glob("*/result.json")):
        value = json.loads(candidate.read_text())
        if "task_name" in value:
            trials.append(value)
    return trials


def rewards(paths: list[Path]) -> list[float]:
    values = []
    for path in paths:
        trials = load_trials(path)
        if not trials:
            raise SystemExit(f"no trial results found in {path}")
        for trial in trials:
            if trial.get("exception_info") is not None:
                raise SystemExit(f"infrastructure exception in {trial.get('trial_name')}")
            reward = trial.get("verifier_result", {}).get("rewards", {}).get("reward")
            if reward not in (0, 0.0, 1, 1.0):
                raise SystemExit(f"missing binary reward in {trial.get('trial_name')}")
            values.append(float(reward))
    return values


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--positive", type=Path, action="append", required=True)
    parser.add_argument("--negative", type=Path, action="append", required=True)
    parser.add_argument("--expected-positive", type=int, default=10)
    parser.add_argument("--expected-negative", type=int, default=15)
    args = parser.parse_args()

    positive = rewards(args.positive)
    negative = rewards(args.negative)
    if len(positive) != args.expected_positive or len(negative) != args.expected_negative:
        raise SystemExit(
            f"expected {args.expected_positive} positive and {args.expected_negative} negative "
            f"trials, found {len(positive)} and {len(negative)}"
        )

    true_positive = sum(value == 1.0 for value in positive)
    false_negative = len(positive) - true_positive
    true_negative = sum(value == 0.0 for value in negative)
    false_positive = len(negative) - true_negative
    true_positive_rate = true_positive / len(positive)
    true_negative_rate = true_negative / len(negative)

    print(
        json.dumps(
            {
                "complete": True,
                "positive_cases": len(positive),
                "negative_cases": len(negative),
                "balanced_accuracy": (true_positive_rate + true_negative_rate) / 2,
                "false_accept_rate": false_positive / len(negative),
                "false_reject_rate": false_negative / len(positive),
                "true_positive": true_positive,
                "true_negative": true_negative,
                "false_positive": false_positive,
                "false_negative": false_negative,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
