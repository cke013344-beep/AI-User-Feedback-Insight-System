#!/usr/bin/env python3
"""Run the full five-field insight prompt on a frozen review sheet."""

import argparse
import csv
import hashlib
import os
import urllib.error
from pathlib import Path

from baseline import LABELS
from insight import INSTRUCTIONS, TOPICS, parse_insight
from zero_shot import call_model

HERE = Path(__file__).parent
FIELDS = ["review_id", "reference_category", "category", "issue_topic", "severity",
          "user_need", "evidence", "valid_schema", "latency_ms", "input_tokens",
          "output_tokens", "raw_output", "provider", "model", "dataset_sha256", "prompt_sha256"]


def report(rows, done):
    print(f"Saved {len(done)}/{len(rows)} reviews.")
    if len(done) != len(rows):
        return
    for field, reference, label in (
        ("category", "reference_category", "Broad-category"),
        ("issue_topic", "reference_topic", "Fixed-topic"),
        ("severity", "reference_severity", "Severity"),
    ):
        if all(row.get(reference) for row in rows):
            matches = sum(done[row["review_id"]][field] == row[reference] for row in rows)
            print(f"{label} accuracy: {matches / len(rows):.3f} ({matches}/{len(rows)})")
    print(f"Valid five-field outputs: {sum(r['valid_schema'] == '1' for r in done.values())}/{len(rows)}")
    print(f"Input tokens: {sum(int(r['input_tokens'] or 0) for r in done.values())}")
    print(f"Output tokens: {sum(int(r['output_tokens'] or 0) for r in done.values())}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, default=HERE / "final_evaluation_sheet.csv")
    parser.add_argument("--output", type=Path, default=HERE / "final_insight_predictions_v5.csv")
    parser.add_argument("--provider", choices=("auto", "openai", "openrouter"), default="auto")
    parser.add_argument("--model")
    parser.add_argument("--limit", type=int, default=0, help="Maximum new calls; 0 means all pending rows")
    args = parser.parse_args()
    if args.limit < 0:
        parser.error("--limit must be nonnegative")
    with args.dataset.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if not rows or any(not row.get("review_id") or not row.get("review") or
                       row.get("reference_category") not in LABELS for row in rows):
        raise SystemExit("Dataset needs review_id, review, and a valid reference_category on every row.")
    if len({row["review_id"] for row in rows}) != len(rows):
        raise SystemExit("Dataset has duplicate review IDs.")
    if any(row.get("review_decision") not in {"KEEP", "CHANGE"} or
           row.get("reference_severity") not in {"low", "medium", "high"} or
           not row.get("reference_user_need") or not row.get("reference_evidence") or
           row["reference_evidence"] not in row["review"] for row in rows):
        raise SystemExit("Review all severity, need, and exact evidence references; mark every row KEEP or CHANGE before this batch run.")

    if any("reference_topic" in row and row["reference_topic"] not in TOPICS for row in rows):
        raise SystemExit("Every reference_topic must use one of the ten fixed topic codes.")

    provider = args.provider
    if provider == "auto":
        provider = "openrouter" if os.environ.get("OPENROUTER_API_KEY") else "openai"
    model = args.model or ("openai/gpt-4o-mini" if provider == "openrouter" else "gpt-6-luna")
    key_name = "OPENROUTER_API_KEY" if provider == "openrouter" else "OPENAI_API_KEY"
    dataset_hash = hashlib.sha256(args.dataset.read_bytes()).hexdigest()
    prompt_hash = hashlib.sha256(INSTRUCTIONS.encode()).hexdigest()
    done = {}
    if args.output.exists():
        with args.output.open(newline="", encoding="utf-8") as f:
            for record in csv.DictReader(f):
                if (record["provider"], record["model"], record["dataset_sha256"], record["prompt_sha256"]) != \
                        (provider, model, dataset_hash, prompt_hash):
                    raise SystemExit("Existing output uses a different dataset, prompt, provider, or model. Choose another --output.")
                if record["review_id"] in done or record["review_id"] not in {row["review_id"] for row in rows}:
                    raise SystemExit("Existing output has a duplicate or unknown review ID.")
                done[record["review_id"]] = record
    pending = [row for row in rows if row["review_id"] not in done]
    if not pending:
        report(rows, done)
        return
    key = os.environ.get(key_name)
    if not key:
        raise SystemExit(f"Set {key_name} before running. No requests were sent.")

    with args.output.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        if f.tell() == 0:
            writer.writeheader()
        for row in pending[:args.limit or None]:
            try:
                raw, latency_ms, usage = call_model(row["review"], key, model, provider, INSTRUCTIONS)
            except (urllib.error.URLError, TimeoutError) as error:
                raise SystemExit(f"Stopped at {row['review_id']}: {error}. Completed rows are saved.") from error
            insight = parse_insight(raw, row["review"])
            record = {
                "review_id": row["review_id"], "reference_category": row["reference_category"],
                "category": insight["category"] if insight else "",
                "issue_topic": insight["issue_topic"] if insight else "",
                "severity": insight["severity"] if insight else "",
                "user_need": insight["user_need"] if insight else "",
                "evidence": insight["evidence"] if insight else "",
                "valid_schema": int(insight is not None), "latency_ms": latency_ms,
                "input_tokens": usage.get("input_tokens", ""), "output_tokens": usage.get("output_tokens", ""),
                "raw_output": raw, "provider": provider, "model": model,
                "dataset_sha256": dataset_hash, "prompt_sha256": prompt_hash,
            }
            writer.writerow(record)
            f.flush()
            done[row["review_id"]] = {key: str(value) for key, value in record.items()}
            print(f"{row['review_id']}: {record['category'] or 'INVALID'}")
    report(rows, done)


if __name__ == "__main__":
    main()
