#!/usr/bin/env python3
"""Run one zero-shot Responses API classification call per review."""

import argparse
import csv
import hashlib
import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path

from baseline import LABELS

INSTRUCTIONS = """Classify one English mobile-app review by its primary product issue.
Categories:
BUG: an existing app function fails, crashes, freezes, loses data, or misbehaves.
ACCOUNT: sign-in, registration, password, verification, identity, or account access.
PAYMENT: charges, prices, subscriptions, cancellation, refunds, purchases, or paid access.
FEATURE_UX: a missing capability or a usability/design improvement.
Use BUG for an app crash even if it happens while logging in. Use ACCOUNT when
the user cannot access an account even if they also mention having paid. Use
PAYMENT when a completed purchase does not unlock paid content. Return only a
JSON object with exactly one key, category, whose value is one of the four labels.
Do not add an explanation or markdown."""

FIELDS = ["review_id", "expected", "predicted", "valid_json", "latency_ms",
          "input_tokens", "output_tokens", "raw_output", "provider", "model",
          "dataset_sha256", "prompt_sha256"]


def call_model(review, key, model, provider="openai", instructions=INSTRUCTIONS):
    if provider == "openrouter":
        url = "https://openrouter.ai/api/v1/chat/completions"
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": instructions},
                {"role": "user", "content": review},
            ],
        }
    else:
        url = "https://api.openai.com/v1/responses"
        payload = {
            "model": model,
            "reasoning": {"effort": "low"},
            "instructions": instructions,
            "input": review,
        }
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
    )
    started = time.perf_counter()
    with urllib.request.urlopen(request, timeout=60) as response:
        result = json.load(response)
    latency_ms = round((time.perf_counter() - started) * 1000)
    if provider == "openrouter":
        output = result["choices"][0]["message"]["content"]
    else:
        output = "".join(
            content.get("text", "")
            for item in result.get("output", []) if item.get("type") == "message"
            for content in item.get("content", []) if content.get("type") == "output_text"
        )
    usage = result.get("usage") or {}
    if provider == "openrouter":
        usage = {
            "input_tokens": usage.get("prompt_tokens", ""),
            "output_tokens": usage.get("completion_tokens", ""),
        }
    return output, latency_ms, usage


def parse_category(output):
    try:
        value = json.loads(output)
    except json.JSONDecodeError:
        return "", False
    valid = isinstance(value, dict) and set(value) == {"category"} and value["category"] in LABELS
    return (value["category"] if valid else ""), valid


def report(dataset, results):
    complete = [results[row["review_id"]] for row in dataset]
    actual = [row["label"] for row in dataset]
    predicted = [row["predicted"] for row in complete]
    correct = sum(y == p for y, p in zip(actual, predicted))
    f1 = []
    for label in LABELS:
        tp = sum(y == label and p == label for y, p in zip(actual, predicted))
        fp = sum(y != label and p == label for y, p in zip(actual, predicted))
        fn = sum(y == label and p != label for y, p in zip(actual, predicted))
        f1.append(2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else 0.0)
    print(f"Accuracy: {correct / len(dataset):.3f} ({correct}/{len(dataset)})")
    print(f"Macro-F1: {sum(f1) / len(f1):.3f}")
    print(f"JSON validity: {sum(row['valid_json'] == '1' for row in complete)}/{len(dataset)}")
    print("Confusion matrix (rows=actual, columns=predicted; invalid outputs omitted from columns):")
    print("actual\\pred  " + "  ".join(f"{label:>10}" for label in LABELS))
    for y in LABELS:
        print(f"{y:<12}" + "  ".join(f"{sum(a == y and p == label for a, p in zip(actual, predicted)):>10}" for label in LABELS))
    print(f"Input tokens: {sum(int(row['input_tokens'] or 0) for row in complete)}")
    print(f"Output tokens: {sum(int(row['output_tokens'] or 0) for row in complete)}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, default=Path(__file__).with_name("real_pilot_dataset.csv"))
    parser.add_argument("--output", type=Path, default=Path(__file__).with_name("zero_shot_predictions.csv"))
    parser.add_argument("--provider", choices=("auto", "openai", "openrouter"), default="auto")
    parser.add_argument("--model", help="Defaults to gpt-6-luna or openai/gpt-4o-mini")
    parser.add_argument("--limit", type=int, default=0, help="Call only this many pending reviews; 0 means all")
    args = parser.parse_args()
    if args.limit < 0:
        parser.error("--limit must be nonnegative")

    provider = args.provider
    if provider == "auto":
        provider = "openrouter" if os.environ.get("OPENROUTER_API_KEY") else "openai"
    model = args.model or ("openai/gpt-4o-mini" if provider == "openrouter" else "gpt-6-luna")
    key_name = "OPENROUTER_API_KEY" if provider == "openrouter" else "OPENAI_API_KEY"
    digest = hashlib.sha256(args.dataset.read_bytes()).hexdigest()
    prompt_digest = hashlib.sha256(INSTRUCTIONS.encode("utf-8")).hexdigest()
    with args.dataset.open(newline="", encoding="utf-8") as f:
        dataset = list(csv.DictReader(f))
    if not dataset or any(not row.get("review_id") or not row.get("review") or row.get("label") not in LABELS for row in dataset):
        raise SystemExit("Dataset needs nonempty review_id, review, and valid label columns.")
    if len({row["review_id"] for row in dataset}) != len(dataset):
        raise SystemExit("Dataset has duplicate review_id values.")

    results = {}
    if args.output.exists():
        with args.output.open(newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if row["provider"] != provider or row["model"] != model or row["dataset_sha256"] != digest or row["prompt_sha256"] != prompt_digest:
                    raise SystemExit("Existing output belongs to another provider, model, dataset, or prompt; choose another --output path.")
                results[row["review_id"]] = row
    pending = [row for row in dataset if row["review_id"] not in results]
    if not pending:
        report(dataset, results)
        return
    key = os.environ.get(key_name)
    if not key:
        raise SystemExit(f"Set {key_name} before running API calls. No requests were sent.")

    count = 0
    with args.output.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        if f.tell() == 0:
            writer.writeheader()
        for row in pending[:args.limit or None]:
            try:
                output, latency_ms, usage = call_model(row["review"], key, model, provider)
            except (urllib.error.URLError, TimeoutError) as error:
                raise SystemExit(f"API call stopped at {row['review_id']}: {error}. Completed rows are saved.") from error
            predicted, valid = parse_category(output)
            record = {
                "review_id": row["review_id"], "expected": row["label"],
                "predicted": predicted, "valid_json": int(valid),
                "latency_ms": latency_ms, "input_tokens": usage.get("input_tokens", ""),
                "output_tokens": usage.get("output_tokens", ""), "raw_output": output,
                "provider": provider, "model": model, "dataset_sha256": digest,
                "prompt_sha256": prompt_digest,
            }
            writer.writerow(record)
            f.flush()
            results[row["review_id"]] = {key: str(value) for key, value in record.items()}
            count += 1
            print(f"{row['review_id']}: {predicted or 'INVALID'}")
    print(f"Saved {count} new predictions; {len(results)}/{len(dataset)} complete.")
    if len(results) == len(dataset):
        report(dataset, results)


if __name__ == "__main__":
    main()
