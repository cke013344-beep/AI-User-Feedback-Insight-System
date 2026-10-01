# Stage 2 prompt revision: 2026-10-02

## Recorded first run

V1 results are preserved in `extended_insight_predictions.csv`, with the original references in `extended_evaluation_sheet.csv` and prompt in `insight_prompt_v1.txt`.

- Broad-category accuracy: 17/20 (85%).
- Valid complete outputs, including exact evidence quotation: 19/20 (95%).
- Severity accuracy against the original references: 11/20 (55%).
- R037: the model changed `it had charged` to `It had charged`. Its complete output was rejected under case-sensitive exact quotation. Invalid complete outputs count as failures in the category and severity metrics.
- User need, topic correctness, and evidence relevance have not yet received human quality scores.

## Approved V2 changes

The project owner approved the clearer severity guide after inspecting V1 results. Severity uses stated impact, with explicit examples for removal questions, failed removal, overheating, missing reminders, price preferences, and lingering status notifications. The prompt additionally reminds the model to preserve quote capitalisation, spelling, and punctuation. Broad category definitions and exact-substring validation stay as before.

Only R011's reference severity changes: `medium` → `low`. It asks how to remove the app without describing a failed attempt. R063 remains `medium`: it explicitly describes not being allowed to remove the preinstalled app. All other reference fields are retained. These are post-run rule revisions, not a claim that the original labels were independently established ground truth.

V2 uses `extended_evaluation_sheet_v2.csv` and saves predictions to `extended_insight_predictions_v2.csv`. The default batch command now selects these V2 files. Both prompt snapshots are saved for reproducibility.

## Interpretation

These 20 reviews are now a development sample used to refine the prompt. A V2 improvement on them is not independent final evaluation. Report each run against its own versioned references. Comparing prompt effects directly requires scoring both runs against the same references, with the changed R011 label disclosed. Use a fresh, human-reviewed sample before claiming general improvement.

## SHA-256 records

- V1 reference CSV: `4d3b42aa22e3ba69772fd311280717fa5f318299df02513774c5d4a40522595c`
- V1 predictions: `b0d3a5b8688a022990812c7df68085649c8c54ff5ac40a3d7bbd0974bffb8e0e`
- V1 prompt: `ebe86b5858125078a5d8f19b2b3a9762222d56aa9a0c621a8c35f8fddf10c4e1`
- V2 reference CSV: `93000f22fee9d20ea88cb8b041aabeb554713ca30ca339878657b3bfd93e999d`
- V2 prompt: `3ac98cef3fe08fa4afb4d6febdbd5b5bbf8dca611c29767ed04475f5e3fc2d73`

## Run V2

With the API key set in the terminal, run from this folder:

```bash
python3 batch_insight.py --provider openrouter
```

No V2 API requests have been made as part of preparing this revision.

## Recorded V2 run

V2 completed on 2026-10-02, using the same model and 20 development reviews:

| Metric | V1 scored against V2 references | V2 scored against V2 references |
|---|---:|---:|
| Broad-category accuracy | 17/20 (85%) | 18/20 (90%) |
| Severity accuracy | 12/20 (60%) | 18/20 (90%) |
| Valid complete outputs | 19/20 (95%) | 19/20 (95%) |

The original V1 severity score was 11/20 against the original references. Using the same V2 references for both runs accounts for the revised R011 label. This is a single run per prompt on development data, not independent evidence of general improvement.

Remaining failures:

- R007: PAYMENT reference, FEATURE_UX prediction. The review objects to subscription pricing and proposes an advertisement-supported alternative.
- R014: the response uses the misspelled key `eveidence` instead of `evidence`. Category BUG and severity medium are correct in the raw response, but the complete output is rejected and counts as a failure in both metrics. The stored raw response is preserved.
- R084: low severity reference, medium prediction. The review describes a persistent updating notification without stating that it blocks use.

User need, topic correctness, and evidence relevance still await human quality scoring. No automatic repair or additional API calls were made.

V2 prediction CSV SHA-256: `2daca8a38f9fe9fd2a9d2c63c99bebe557fc05965b04f74599fe9238dae6273b`.

## V3: fixed issue topics, approved 2026-10-02

The owner approved the ten-topic taxonomy in the conversation. The shared prompt now requires one fixed topic, the parser rejects unknown topics, and the web page displays Chinese topic labels with the stored English codes. CLI, batch, and web use the same parser and prompt. Category and severity reference values are unchanged from V2. A price-objection example clarifies PAYMENT + PRICING_SUBSCRIPTION. The evidence and user-need rules are unchanged.

The owner accepted the V2 content review after reading the Chinese guide. This is a qualitative owner approval, not independently recorded per-field binary scores. R014 remains an invalid complete output because of its misspelled evidence key; approval does not retroactively repair that record.

V1 and V2 outputs and prompt snapshots are preserved. V3 saves to `extended_insight_predictions_v3.csv`; its dataset remains the V2 reference CSV. These 20 reviews remain development data. No fixed-topic ground truth or topic accuracy is claimed. No V3 API calls or runtime tests were performed while preparing this change.

V3 prompt SHA-256: `0e25e5ae7c64315317cef6e1bf004a2343ec8f4d4bb0bc3a3e64a448c4f3c64e`.

## Recorded V3 run

V3 completed on 2026-10-02: category 17/20 (85%), valid complete outputs 18/20 (90%), severity 16/20 (80%). Scores use the unchanged V2 references. No fixed-topic accuracy is reported because topic reference labels were not frozen.

R011 and R063 used INSTALL_REMOVAL as category (outside the four broad categories), with OTHER as topic. Their complete outputs were rejected. R031 used BUG/high rather than FEATURE_UX/medium. R084 remains medium rather than low. Topic membership alone does not prove semantic correctness: R037 uses PRICING_SUBSCRIPTION despite its unexpected charge, and R080 uses FEATURE_REQUEST for an unwanted monitoring app.

Recorded usage for the same 20 reviews: V2 input 13,493 tokens, output 1,185, mean latency 2,129 ms; V3 input 17,493 tokens, output 1,212, mean latency 1,974 ms. Input usage increased by 4,000 tokens (29.6%). Single-run latency differences do not establish a speed improvement. No retries, schema repairs, or further API calls were made during analysis.

## V4: separate field vocabularies and boundary examples

Approved by the project owner on 2026-10-02 after discussion of V3 failures. The shared prompt now explicitly states that category accepts only the four broad labels, while issue_topic accepts only the ten topic codes. It includes generic examples for removal questions, preinstalled-app removal restrictions, unexpected subscription charges, persistent status notifications, and unwanted monitoring apps, plus a five-field JSON shape and evidence-key spelling reminder.

The parser already checks both enums separately; its validation rules are unchanged. This revision strengthens prompt guidance, not provider-enforced structured output. There are no automatic repairs or retries. Raw outputs, schema failures, and single-call token usage will remain visible. No new features or references are added. The new examples were motivated by development-set errors, so any improvement remains a development result, not independent final evaluation.

V4 uses the unchanged V2 reference CSV and writes `extended_insight_predictions_v4.csv`. V1–V3 prompt snapshots and predictions are preserved. CLI and web use the updated shared prompt. No API requests or runtime tests were made while preparing this revision.

V4 prompt SHA-256: `c5afa612898dc168e1fd9857ef2807bbedccd69126983ee6e00658b028aa1a6c`.

## Recorded V4 run

Completed on 2026-10-02: category accuracy 20/20 (100%), valid complete outputs 20/20 (100%), severity accuracy 17/20 (85%), against unchanged V2 references. All topic values belong to the fixed vocabulary; this is not a measured topic accuracy score.

Severity disagreements: R031 high versus medium; R069 medium versus low; R084 medium versus low. The field-mixing failures seen in V3 did not occur in this V4 run. This does not guarantee that future outputs will conform.

Content review still matters: R080 says to remove the monitoring program "from the app", although the review does not locate it inside another app. R100 asks to access an "existing account", while the reviewer disputes the already-registered message. R111's short quote omits the cancellation context needed to support the unauthorized-charge interpretation. No binary human quality scores are claimed for V4.

Input tokens: 23,653; output tokens: 869; mean recorded latency: 1,891 ms/review. V4 input usage is 35.2% greater than V3 (17,493) due to additional instructions/examples. Each is a single recorded run, so latency differences are not evidence of a speed improvement.

These are 20 development reviews used for multiple prompt revisions. A fresh sample with references fixed before model execution is needed for final evaluation. No predictions or references were edited during analysis, and no additional model calls were made.

V4 prediction SHA-256: `1d81e0a25c7bad1e6b3017d2b3da7bfab12cd26ead71191fc5c413d97d59dafc`.

## V5: final prompt and fresh evaluation preparation

The owner approved the three proposed V4 content corrections on 2026-10-02. V5 adds generic grounding rules: do not invent a container/location, do not treat a disputed account error as fact, and quote decisive charge/cancellation context together where available. V4 raw outputs and references are not rewritten. V5 was saved before new review selection; SHA-256 `1f033838af1a0b9a97bf8a9dc556c0c1b0da4a151c1de584e94fdc567d1a8dcd`.

Fresh H001–H020 references are prepared in `final_evaluation_sheet.csv`, with decisions left blank pending owner review. The final runner now defaults to that file and `final_insight_predictions_v5.csv`. It validates fixed-topic references, reports topic accuracy and actual token totals, and prints the same summary on a completed-file rerun. Existing prediction records are rejected if duplicate or unknown IDs are found. No model calls or runtime tests were performed while preparing this change.

See `README_FINAL_EVALUATION.md` for exact source, sampling exclusions, limitations, and the pre-run approval procedure. Do not report draft annotation as approved ground truth. The owner may correct references before the final call; freeze both references and prompt before execution.

## Final reference approval

On 2026-10-02, the project owner explicitly approved all 20 fresh references KEEP, before the final V5 call. The approved reference CSV and prompt hashes are recorded in `final_evaluation_freeze.json`. No reference values were changed.

## Final V5 recorded run

The fresh 20-review run completed: category 19/20, topic 17/20, severity 16/20, complete validity 19/20. H018 changed the quote's initial If to if. The frozen dataset/prompt hashes match all prediction records. No post-result prompt/reference edits or additional calls were made. Full metrics and caveats are in `FINAL_EVALUATION_RESULTS.md`, with actual output content awaiting owner review in `FINAL_OUTPUT_REVIEW_CN.md`.
