#!/usr/bin/env python3
"""Extract one app review's issue, severity, user need, and evidence."""

import argparse
import json
import os
import sys
import urllib.error

from baseline import LABELS
from zero_shot import call_model


TOPICS = (
    "ACCOUNT_ACCESS", "CHARGES_REFUNDS", "PRICING_SUBSCRIPTION",
    "CRASH_PERFORMANCE", "FUNCTION_FAILURE", "NOTIFICATIONS",
    "INSTALL_REMOVAL", "USABILITY_DESIGN", "FEATURE_REQUEST", "OTHER",
)

INSTRUCTIONS = """Classify one English mobile-app review by its primary product issue.
Return a practical first-pass insight for a product team.

The two classification fields have separate allowed values.
category MUST be exactly BUG, ACCOUNT, PAYMENT, or FEATURE_UX.
Never put a topic code (such as INSTALL_REMOVAL) in category.
Choose category using these definitions:
BUG: an existing app function fails, crashes, freezes, loses data, or misbehaves.
ACCOUNT: sign-in, registration, password, verification, identity, or account access.
PAYMENT: charges, prices, subscriptions, cancellation, refunds, purchases, or paid access.
FEATURE_UX: a missing capability or a usability/design improvement.
Use the primary issue, not a passing word. A crash during login is BUG; an
account that cannot be accessed is ACCOUNT; a completed purchase that does not
unlock content is PAYMENT. Mandatory registration as a design objection is
FEATURE_UX. A request for free content or a refund is PAYMENT.

issue_topic MUST be exactly one of the following ten codes, never a category code:
ACCOUNT_ACCESS: login, registration, password recovery, or account verification.
CHARGES_REFUNDS: wrong/duplicate charges or refunds.
PRICING_SUBSCRIPTION: price, paid access, subscription plans, or cancellation
without a disputed charge. A disputed charge takes CHARGES_REFUNDS instead.
CRASH_PERFORMANCE: crashes, freezing, slow performance, or overheating.
FUNCTION_FAILURE: another existing function fails; use a more specific topic
above or below when it applies.
NOTIFICATIONS: missing reminders, notification behaviour, or notification settings.
INSTALL_REMOVAL: installation, preinstallation, or removing an app.
USABILITY_DESIGN: confusing screens, navigation, or inconvenient existing workflows.
FEATURE_REQUEST: a new capability, unless a more specific topic above applies.
OTHER: the issue does not fit any of these topics. Do not create new topic names.
Choose category and topic separately based on the primary issue: a missing
reminder is BUG + NOTIFICATIONS; a request for reminder settings is
FEATURE_UX + NOTIFICATIONS. A price objection proposing a free alternative is
PAYMENT + PRICING_SUBSCRIPTION. Apply these boundary examples:
- "How do I remove this app?" -> FEATURE_UX / INSTALL_REMOVAL / low.
- "The preinstalled app cannot be removed." -> FEATURE_UX / INSTALL_REMOVAL /
  medium. This is a removal/design restriction, not proof of a crash or blocked
  core app task. Use BUG only if the review describes an actual malfunction.
- "I thought it was free, then it charged me." -> PAYMENT / CHARGES_REFUNDS /
  high. The unexpected charge takes priority over a general subscription complaint.
- "The updating notification stays on screen." -> BUG / NOTIFICATIONS / low
  unless the review explicitly describes additional disruption or blocked use.
- "I do not want this monitoring app." -> FEATURE_UX / USABILITY_DESIGN / low;
  rejecting an existing app is not a request for a new capability.
Do not infer events absent from the review.

Rate severity only by the impact explicitly stated in this review, not anger,
capitalisation, star ratings, or how alarming the wording sounds.
high = a core task is impossible (for example the user cannot sign in or start
using the app), the phone becomes unusable, data is lost, or a wrong/unauthorised
charge is reported. Do not infer any of these consequences without evidence.
medium = a concrete function fails or repeated disruption creates an obstacle,
but the review does not establish that a core task or the whole phone is unusable.
Examples: reminders do not arrive; errors recur after several sessions; the
phone overheats without reported shutdown or inability to use it; the user
explicitly says they cannot remove the app despite trying.
low = an optional feature request, price preference without wrongful charging,
minor distraction, or dislike without a stated practical obstacle.
Examples: a subscription is too expensive; the user asks how to remove an app
without describing a failed removal attempt; an updating notification stays on
screen without blocking use; the user simply does not want a monitoring app.
A question about removal alone is low; an explicit inability to remove is medium.
Overheating alone is medium; overheating that makes the phone unusable is high.
A missing reminder is medium; a lingering status notification alone is low.
When information is insufficient, choose the lower level supported by the text.

Write user_need as one short sentence describing what the user wants to be
able to do or have fixed. It may be a modest inference, but must be supported
by the review. Do not invent facts, intent, or a proposed technical solution.
Do not add a location or container the user never stated (for example "inside
the app"). If the user disputes an error message, do not treat that message
as established fact; describe the need to resolve the obstacle instead.
Evidence must be one short, nonempty, exact contiguous substring copied
verbatim from the review that supports the main issue. Do not use ellipses or
paraphrase. Preserve the original capitalisation, spelling, and punctuation;
do not correct even the first letter of the quote. Include the decisive context
when available: for a charge after cancellation, quote both cancellation and
charging together in one contiguous passage, not just the fact of a charge.

Return only a JSON object with exactly these five keys: category,
issue_topic, severity, user_need, evidence. No explanation or markdown.
Before returning, check each field against its OWN allowed values; never swap
category and issue_topic. The evidence key must be spelled exactly evidence.
Example shape (replace the content with this review's actual insight):
{"category":"FEATURE_UX","issue_topic":"INSTALL_REMOVAL","severity":"low",
"user_need":"Remove the app from the phone.","evidence":"exact quote from input"}"""


def parse_insight(output, review):
    try:
        value = json.loads(output)
    except json.JSONDecodeError:
        return None
    fields = {"category", "issue_topic", "severity", "user_need", "evidence"}
    if not isinstance(value, dict) or set(value) != fields:
        return None
    if not isinstance(value["category"], str) or value["category"] not in LABELS:
        return None
    if not isinstance(value["severity"], str) or value["severity"] not in {"low", "medium", "high"}:
        return None
    for field, maximum in (("issue_topic", 80), ("user_need", 300), ("evidence", len(review))):
        text = value[field]
        if not isinstance(text, str) or not text.strip() or len(text) > maximum:
            return None
        value[field] = text.strip()
    if value["issue_topic"] not in TOPICS:
        return None
    if value["evidence"] not in review:
        return None
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("review", nargs="?", help="Review text; reads standard input when omitted")
    parser.add_argument("--provider", choices=("auto", "openai", "openrouter"), default="auto")
    parser.add_argument("--model", help="Optional model override")
    args = parser.parse_args()

    review = args.review if args.review is not None else (
        input("Review: ") if sys.stdin.isatty() else sys.stdin.read()
    )
    review = review.strip()
    if not review:
        parser.error("Provide a review argument or pipe review text to standard input.")

    provider = args.provider
    if provider == "auto":
        provider = "openrouter" if os.environ.get("OPENROUTER_API_KEY") else "openai"
    key_name = "OPENROUTER_API_KEY" if provider == "openrouter" else "OPENAI_API_KEY"
    model = args.model or ("openai/gpt-4o-mini" if provider == "openrouter" else "gpt-6-luna")
    key = os.environ.get(key_name)
    if not key:
        parser.error(f"Set {key_name} before running the insight call.")

    try:
        output, _, _ = call_model(review, key, model, provider, INSTRUCTIONS)
    except (urllib.error.URLError, TimeoutError) as error:
        raise SystemExit(f"Model request failed: {error}") from error
    result = parse_insight(output, review)
    if result is None:
        raise SystemExit("The model response was not valid five-field insight JSON.")
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
