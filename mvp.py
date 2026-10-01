#!/usr/bin/env python3
"""Classify one English mobile-app review into a product issue category."""

import argparse
import json
import os
import sys
import urllib.error

from baseline import predict


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("review", nargs="?", help="Review text; reads standard input when omitted")
    parser.add_argument("--method", choices=("rule", "llm"), default="rule")
    parser.add_argument("--provider", choices=("auto", "openai", "openrouter"), default="auto")
    parser.add_argument("--model", help="Optional model override used with --method llm")
    args = parser.parse_args()

    review = args.review if args.review is not None else (
        input("Review: ") if sys.stdin.isatty() else sys.stdin.read()
    )
    review = review.strip()
    if not review:
        parser.error("Provide a review argument or pipe review text to standard input.")

    if args.method == "rule":
        category = predict(review)
    else:
        from zero_shot import call_model, parse_category

        provider = args.provider
        if provider == "auto":
            provider = "openrouter" if os.environ.get("OPENROUTER_API_KEY") else "openai"
        key_name = "OPENROUTER_API_KEY" if provider == "openrouter" else "OPENAI_API_KEY"
        model = args.model or ("openai/gpt-4o-mini" if provider == "openrouter" else "gpt-6-luna")
        key = os.environ.get(key_name)
        if not key:
            parser.error(f"--method llm requires {key_name} in the environment.")
        try:
            output, _, _ = call_model(review, key, model, provider)
        except (urllib.error.URLError, TimeoutError) as error:
            raise SystemExit(f"Model request failed: {error}") from error
        category, valid = parse_category(output)
        if not valid:
            raise SystemExit("The model response was not a valid category JSON object.")

    print(json.dumps({"category": category}))


if __name__ == "__main__":
    main()
