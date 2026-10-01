#!/usr/bin/env python3
"""Aggregate saved review predictions into category counts and examples."""

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

from baseline import LABELS


def main():
    here = Path(__file__).parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, default=here / "real_pilot_dataset.csv")
    parser.add_argument("--predictions", type=Path, default=here / "zero_shot_predictions.csv")
    parser.add_argument("--examples", type=int, default=2, help="Examples per category")
    parser.add_argument("--output", type=Path, help="Optional JSON output path")
    args = parser.parse_args()
    if args.examples < 0:
        parser.error("--examples must be nonnegative")

    with args.dataset.open(newline="", encoding="utf-8") as f:
        dataset = {row["review_id"]: row for row in csv.DictReader(f)}
    with args.predictions.open(newline="", encoding="utf-8") as f:
        predictions = list(csv.DictReader(f))
    if not predictions:
        raise SystemExit("The prediction file contains no rows.")
    if len({row["review_id"] for row in predictions}) != len(predictions):
        raise SystemExit("The prediction file contains duplicate review IDs.")
    if any(row["review_id"] not in dataset for row in predictions):
        raise SystemExit("A prediction review ID is missing from the dataset.")
    if any(row["predicted"] not in LABELS for row in predictions):
        raise SystemExit("All predictions must contain one of the four valid labels.")

    counts = Counter(row["predicted"] for row in predictions)
    total = len(predictions)
    result = {
        "total_reviews": total,
        "category_counts": {label: counts[label] for label in LABELS},
        "category_percentages": {
            label: round(100 * counts[label] / total, 1) for label in LABELS
        },
        "examples": {},
    }
    for label in LABELS:
        rows = sorted(
            (row for row in predictions if row["predicted"] == label),
            key=lambda row: row["review_id"],
        )[:args.examples]
        result["examples"][label] = [
            {"review_id": row["review_id"], "review": dataset[row["review_id"]]["review"]}
            for row in rows
        ]

    rendered = json.dumps(result, indent=2, ensure_ascii=False)
    print(rendered)
    if args.output:
        args.output.write_text(rendered + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
