#!/usr/bin/env python3
"""Keyword-rule baseline for four-class mobile-app feedback."""

import argparse
import csv
import re
from collections import Counter
from pathlib import Path

LABELS = ["BUG", "ACCOUNT", "PAYMENT", "FEATURE_UX"]

# Ordered rules resolve some overlaps: billing/account access terms precede
# broad product-usage terms, while suggestions and usability language map last.
RULES = [
    ("PAYMENT", (
        "charge", "charged", "billing", "billed", "payment", "paid", "pay",
        "refund", "subscription", "renew", "renewal", "invoice", "price",
        "cost", "card", "voucher", "checkout", "premium",
    )),
    ("ACCOUNT", (
        "sign in", "signin", "log in", "login", "logged out", "signed out",
        "password", "account", "profile", "verification", "verify", "email address",
        "face id", "registered", "reset link",
    )),
    ("BUG", (
        "crash", "closes", "force quit", "spinning", "stops moving", "won't load",
        "disappears", "cuts out", "blank page", "stuck", "hang", "hangs",
        "sent me back", "takes forever", "doesn't work", "does not work",
        "stopped", "jumps back", "won't open", "won’t load",
    )),
    ("FEATURE_UX", (
        "would help", "could you", "i wish", "it would", "could add", "add a way",
        "would be", "easier", "too many taps", "tiny", "hard to", "crowded",
        "choose which", "save a", "offline use", "side by side", "higher-contrast",
        "sort saved", "one-handed",
    )),
]


def predict(review):
    text = review.casefold().replace("-", " ")
    for label, terms in RULES:
        if any(re.search(rf"\b{re.escape(term)}\b", text) for term in terms):
            return label
    # The four-label taxonomy requires a label even when no rule matches.
    return "FEATURE_UX"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "csv_path", nargs="?", type=Path,
        default=Path(__file__).with_name("evaluation_dataset.csv"),
        help="CSV with review and label columns (defaults to the bundled dataset)",
    )
    args = parser.parse_args()

    with args.csv_path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise SystemExit("The CSV contains no data rows.")
    missing = {"review", "label"} - set(rows[0])
    if missing:
        raise SystemExit("CSV is missing required column(s): " + ", ".join(sorted(missing)))

    actual = [row["label"].strip() for row in rows]
    predicted = [predict(row["review"]) for row in rows]
    if any(label not in LABELS for label in actual):
        raise SystemExit("Labels must be one of: " + ", ".join(LABELS))

    correct = sum(y == p for y, p in zip(actual, predicted))
    accuracy = correct / len(rows)
    f1_values = []
    for label in LABELS:
        tp = sum(y == label and p == label for y, p in zip(actual, predicted))
        fp = sum(y != label and p == label for y, p in zip(actual, predicted))
        fn = sum(y == label and p != label for y, p in zip(actual, predicted))
        denom = 2 * tp + fp + fn
        f1_values.append((2 * tp / denom) if denom else 0.0)
    macro_f1 = sum(f1_values) / len(LABELS)

    matrix = Counter(zip(actual, predicted))
    print("Predictions:")
    for row, label, pred in zip(rows, actual, predicted):
        print(f'{row.get("review_id", "")}: expected={label:<10} predicted={pred:<10} | {row["review"]}')
    print(f"\nAccuracy: {accuracy:.3f} ({correct}/{len(rows)})")
    print(f"Macro-F1: {macro_f1:.3f}")
    print("\nConfusion matrix (rows=actual, columns=predicted):")
    print("actual\\pred  " + "  ".join(f"{label:>10}" for label in LABELS))
    for actual_label in LABELS:
        values = [matrix[(actual_label, predicted_label)] for predicted_label in LABELS]
        print(f"{actual_label:<12}" + "  ".join(f"{value:>10}" for value in values))


if __name__ == "__main__":
    main()
