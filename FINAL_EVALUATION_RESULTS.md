# V5 fresh-sample evaluation results

One recorded run on 20 curated MHARD reviews, five per category, with no UID/exact-text overlap with the prior 260 candidates. Assistant-drafted references were approved by the owner before execution. Dataset/prompt hashes match the pre-run freeze record. No labels, prompt, or predictions were changed after viewing this result.

| Metric | Result |
|---|---:|
| Broad-category accuracy | 19/20 (95%) |
| Broad-category macro-F1 | 0.972 |
| Fixed-topic accuracy | 17/20 (85%) |
| Severity accuracy | 16/20 (80%) |
| Complete output validity, including exact quotation | 19/20 (95%) |
| Input tokens | 25,239 |
| Output tokens | 875 |
| Mean recorded latency | 1,843 ms/review |

Provider: openrouter; model: openai/gpt-4o-mini.

Invalid complete outputs count as failures in category, topic, and severity accuracy and as missed true labels for macro-F1. These measure accepted complete predictions, not just the correctness of individual raw fields. JSON parsing alone is not the same as complete validity. This run has 20 parseable JSON objects and 19 accepted complete outputs.

## Observed errors

- H018: quote starts with `if`, while the review has `If`. Case-sensitive exact quotation rejects the complete output. Raw category, topic, and severity match the references, but that does not repair the failed output or change the reported scores.
- H005: FUNCTION_FAILURE versus reference NOTIFICATIONS; high versus reference medium. The reminder problem should use the more specific topic, and no whole-app blockage is described.
- H013: CHARGES_REFUNDS versus reference PRICING_SUBSCRIPTION. The complaint is paid access not unlocking; no wrongful charge or refund request is stated.
- H014: high versus reference low. A displayed price discrepancy is treated as serious loss despite no actual debit being stated.
- H015: medium versus reference low. The user cannot afford normal post-trial pricing; no wrongful charge is reported.

## Content review

The owner gave qualitative acceptance of the content review on 2026-10-02. No independent per-field binary quality scores or agreement statistics were collected. H011 adds “after uninstallation” to the payment need, which changes the complaint's meaning. H007/H009/H010 quote generic error text while omitting some account-action context. H020 quotes not wanting updates while omitting the inability to disable the app. These are assistant flags for review, not approved binary quality scores. H018's evidence failed exact quotation and must remain a failure even if its meaning is reasonable.

See `FINAL_OUTPUT_REVIEW_CN.md` for all 20 actual outputs and blank owner judgments.

## Reporting limits

The fresh reviews were selected after freezing V5, but they are a small purposive, keyword-screened sample in the same app domain. They are not random population data, a cross-domain test, or independently multi-rater annotated data. Topic coverage is incomplete. Use these scores as a small held-out final check, not a claim of general 95% accuracy. The prior 120-review category-only pilot and this full-insight 20-review run evaluate different workflows and datasets and should be reported separately.

Frozen reference SHA-256: `d76688de33d6caa81c7ee6c584c61b91c754a87c3f29bc4297b602402a2eedcd`.
Prompt SHA-256: `1f033838af1a0b9a97bf8a9dc556c0c1b0da4a151c1de584e94fdc567d1a8dcd`.
Prediction SHA-256: `442db797a91e63c5bb196ef3dfef06ff847841fb51c93b6e298420474e0ca571`.
