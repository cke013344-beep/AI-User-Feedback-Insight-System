# Stage 2: four-part feedback insight

The single-review AI workflow now returns all four planned capabilities in one response:

1. **Issue classification:** a broad `category` plus a more specific `issue_topic`.
2. **Severity classification:** `low`, `medium`, or `high` based on stated impact.
3. **User need extraction:** a short, grounded statement of what the user wants fixed or made possible.
4. **Evidence extraction:** an exact contiguous quote from the original review.

Run from this folder with `OPENROUTER_API_KEY` or `OPENAI_API_KEY` set:

```bash
python3 insight.py --provider openrouter "I was charged after cancelling my subscription."
```

Illustrative output, not a recorded model result:

```json
{
  "category": "PAYMENT",
  "issue_topic": "CHARGES_REFUNDS",
  "severity": "high",
  "user_need": "The user needs the unwanted charge reversed and the cancellation respected.",
  "evidence": "charged after cancelling my subscription"
}
```

The four broad categories remain `BUG`, `ACCOUNT`, `PAYMENT`, and `FEATURE_UX` so the frozen 120-review pilot is comparable with the original baseline. `issue_topic` now selects one of ten fixed topics (introduced in V3). This makes counts consistent across reviews without grouping free-text synonyms. Topic and broad category are separate dimensions; for example, BUG and FEATURE_UX may both use NOTIFICATIONS.

| Fixed topic | Meaning |
|---|---|
| ACCOUNT_ACCESS | Login, registration, password, verification |
| CHARGES_REFUNDS | Wrong or duplicate charges, refunds |
| PRICING_SUBSCRIPTION | Price, paywall, subscription plans or cancellation without a disputed charge |
| CRASH_PERFORMANCE | Crashes, freezing, slowness, overheating |
| FUNCTION_FAILURE | Other existing functionality failing |
| NOTIFICATIONS | Reminders, notifications, notification settings |
| INSTALL_REMOVAL | Installation, preinstallation, removal |
| USABILITY_DESIGN | Interface, navigation, inconvenient workflows |
| FEATURE_REQUEST | New capabilities without a more specific topic |
| OTHER | None of the listed topics fits |

Prefer a specific topic over FUNCTION_FAILURE or FEATURE_REQUEST. An optional notification setting uses NOTIFICATIONS; a disputed subscription charge uses CHARGES_REFUNDS. OTHER prevents forcing an unsupported specific topic. The existing pilot covers mental-health apps and cannot measure general accuracy for booking or search. Fixed topic names need no additional model call; the actual latency and token cost still need measurement.

## Severity guide

| Level | Use when the review says… |
|---|---|
| `high` | A core task is impossible, the phone is unusable, data is lost, or a wrong/unauthorised charge is reported. |
| `medium` | A concrete function fails or causes repeated disruption, without evidence that core use or the whole phone is impossible. Missing reminders, recurring errors, overheating alone, and explicitly failed removal belong here. |
| `low` | A feature request, price preference, minor distraction, or dislike without an established obstacle. A removal question alone or a lingering status notification alone belongs here. |

Use only the impact stated in the review. Angry wording alone does not make an issue `high`; when impact is unclear, use the lower supported level.

The `user_need` sentence should describe the outcome the user wants, such as being able to log in or getting a wrong charge reversed. It should not prescribe an implementation that the review never mentioned.

## Grounding and current evidence

`insight.py` checks that all five fields are present, that category, fixed topic, and severity are valid, and that the evidence appears **verbatim** in the input review. The user need and specific topic still require human judgment; the program cannot prove that an inference is correct merely by checking JSON.

The frozen Stage 1 evaluation measured only broad issue classification: accuracy 0.900 and macro-F1 0.900 on 120 human-checked reviews. Those numbers do **not** measure the new severity, need, topic, or evidence quality. `extended_evaluation_sheet.csv` is a separate 20-review sample, five per category, drawn with seed `6204`. Its severity, user need, and evidence references were drafted by the assistant and approved by the project owner on **2026-10-02**, before the extended model run: **20 KEEP, 0 CHANGE, 0 UNSURE**. This is owner review of assistant drafts, not independent multi-rater annotation. All original reference values were retained. For user need, compare meaning and grounding rather than identical wording. Freeze these references during the experiment; do not change them to match model outputs.

Approved reference CSV SHA-256: `4d3b42aa22e3ba69772fd311280717fa5f318299df02513774c5d4a40522595c`.

The first run is complete: category 17/20, valid complete outputs 19/20, severity 11/20. Following owner approval of a clearer severity guide, V2 is prepared with a separate reference file and separate prediction output. R011 severity is revised from medium to low; all other reference values are unchanged. See `STAGE2_REVISION_LOG.md` for preserved prompts, hashes, and interpretation. These 20 rows now serve as development data; a fresh sample is needed for final evaluation.

V2 completed with category and severity accuracy both 18/20, and 19/20 valid complete outputs. V3 adds the owner-approved fixed topic list. V3 completed with category accuracy 17/20, severity accuracy 16/20, and 18/20 valid complete outputs. R011 and R063 placed a topic code in the category field. V4 explicitly separates the allowed values and adds generic boundary examples for removal, unexpected charges, unwanted apps, and persistent status notifications. These changes are prompt guidance plus the existing strict validation; they do not guarantee the model obeys the schema, repair output automatically, or make extra model calls.

The default command still uses `extended_evaluation_sheet_v2.csv` and now writes `extended_insight_predictions_v4.csv`. Run V4:

```bash
python3 batch_insight.py --provider openrouter
```

The script saves each V4 response to `extended_insight_predictions_v4.csv` and resumes an interrupted run. It reports broad-category accuracy and valid five-field output rate. It reports severity accuracy only if every `reference_severity` has been filled. Human review is still needed to judge whether `user_need` and `issue_topic` are faithful to each comment; evidence can additionally be checked mechanically for exact quotation. Do not use the Stage 1 category score as the score for this new prompt.

For the final write-up, review each new output against its original review and record three simple yes/no judgments: (1) does the specific topic name the real issue, (2) is the stated user need supported without adding facts, and (3) does the quote actually support the chosen issue? Report the number of yes decisions out of 20 for each check. These human judgments complement the script's format and severity checks.

## Batch overview

`aggregate_insights.py` still summarises the saved Stage 1 category predictions locally:

```bash
python3 aggregate_insights.py
```

It reports 32 `BUG`, 31 `ACCOUNT`, 28 `PAYMENT`, and 29 `FEATURE_UX` predictions in the deliberately balanced pilot. These are sample counts, not production issue frequencies.

Fixed topics are validated mechanically for membership, not semantic correctness. No fixed-topic reference labels have yet been collected, so no topic accuracy score is claimed.

V4 completed: broad-category accuracy 20/20, valid complete outputs 20/20, severity accuracy 17/20. These are development-set results, not independent final evaluation. V4 user need and evidence relevance still require content review; see `STAGE2_REVISION_LOG.md` for the remaining issues and usage.

## Current final-evaluation preparation (V5)

V5 is the shared prompt used by CLI and web. Its snapshot is `insight_prompt_v5_final.txt`. The owner approved the V4 grounding corrections. The default batch command now uses `final_evaluation_sheet.csv` and saves `final_insight_predictions_v5.csv`; the project owner approved all 20 references KEEP before the final run. The reference and prompt hashes are recorded in `final_evaluation_freeze.json`. See `FINAL_EVALUATION_REVIEW_CN.md` and `README_FINAL_EVALUATION.md`. Earlier run descriptions above are historical, not current defaults.
