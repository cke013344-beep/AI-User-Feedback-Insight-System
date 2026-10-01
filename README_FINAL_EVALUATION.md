# Fresh 20-review evaluation: preparation

Status: owner approved all 20 references KEEP on 2026-10-02, before the final V5 model run. References and prompt are frozen in `final_evaluation_freeze.json`. This is owner verification of assistant drafts, not independent multi-rater annotation.

Source: [MHARD author repository](https://github.com/Sensify-Lab/MHARD), same source commit as the original pilot: `6a492efa0eaf9a27e2593a4a370349f91e1e044d`.
[Exact source CSV](https://raw.githubusercontent.com/Sensify-Lab/MHARD/6a492efa0eaf9a27e2593a4a370349f91e1e044d/MHARD_dataset.csv).
Source SHA-256: `03f962fd905300238864ff1b6a41f6ebde109acb8f850154a279bdb6ff237da8`.

Real source reviews are preserved verbatim. Classification, topic, severity, need, and evidence references are assistant annotations, not original MHARD labels. The source's rating predictions and developer replies are not used as ground truth or model input.

## Selection

Excluded every UID and whitespace-normalized/case-folded exact review text in the old 260-candidate annotation pool (including all original 120 pilot reviews and 20 development reviews). Restricted to the same five apps, review lengths 45–300 characters, with no obvious URLs, email-address marker, or selected self-harm terms. Shuffled remaining reviews with seed 6205. Four keyword screens generated up to 15 candidates per screen; then the assistant selected 5 clear examples per broad category, including different task impacts, before any V5 model run. The selection is purposive, not random class-balanced sampling. The screens overlap and their matches are not reference labels. Candidate pool: `work/final_candidate_pool.json`; selection/annotation procedure: `work/prepare_final.py`.

Rows H001–H020 retain source UID and app. There are no exact-text/UID overlaps with the old 260 candidates, but fuzzy near-duplicates were not exhaustively assessed. A fresh sample from the same domain is not a cross-domain test, and cannot rule out model pretraining exposure. Twenty curated reviews give an imprecise estimate and do not represent natural issue frequencies. No synthetic samples are used.

## Reference review and freezing

Review `FINAL_EVALUATION_REVIEW_CN.md` or edit `final_evaluation_sheet.csv`. Every row needs KEEP or CHANGE; resolve UNSURE and validate references before running. Record the approved reference hash after review. No model predictions are visible during this reference review. The prompt snapshot is `insight_prompt_v5_final.txt`; it was prepared using development-set findings before selecting these new reviews. Do not tune it on final-run results and retain failures in the reported scores.

## Run only after approval

From this folder with the terminal API key set:

```bash
python3 batch_insight.py --provider openrouter
```

The default will use the new reference sheet and save `final_insight_predictions_v5.csv`. It refuses to call the model with pending review decisions. Reports cover category, topic, severity, complete schema/exact-quote validity, and token usage. Need groundedness and evidence relevance require a separate post-run human content review. Prompt length and cost must be measured from the saved actual usage.

Approved reference SHA-256: `d76688de33d6caa81c7ee6c584c61b91c754a87c3f29bc4297b602402a2eedcd`.

Frozen prompt SHA-256: `1f033838af1a0b9a97bf8a9dc556c0c1b0da4a151c1de584e94fdc567d1a8dcd`.

## Recorded V5 run

Completed: category 19/20, topic 17/20, severity 16/20, complete validity 19/20. The frozen reference and prompt hashes match the prediction records. Detailed results: `FINAL_EVALUATION_RESULTS.md`; content review: `FINAL_OUTPUT_REVIEW_CN.md`. V5 remains unchanged after this run.
