# Real-review classification pilot

This pilot uses real mobile-app reviews. Its labels were drafted by the assistant after reading the reviews, **before running the keyword baseline**, and were subsequently checked by the project owner. All 120 labels were retained.

## Data and selection

Source: [MHARD](https://github.com/Sensify-Lab/MHARD), a research dataset of Google Play reviews for mental-health apps. The authors' repository states an MIT license and provides original review text and source IDs. Source commit: `6a492efa0eaf9a27e2593a4a370349f91e1e044d`. Source CSV SHA-256: `03f962fd905300238864ff1b6a41f6ebde109acb8f850154a279bdb6ff237da8`.

`formal_annotation_candidates.csv` records all **260** reviewed candidates, draft labels, include/exclude decisions, and notes. The first 200 came from five apps (`digitalwellbeing`, `daylio`, `fabulous`, `headspace`, `calm`), 40 each, using seed `6201`. Each app contributed 30 reviews rated 1–3 and 10 rated 4–5. An additional 60 low-rated reviews mentioning account-access terms were drawn with seed `6202` to find enough `ACCOUNT` examples. Reviews were limited to 40–350 characters and screened for obvious links, email addresses, and selected sensitive terms. The draft review retained 30 `BUG`, 30 `ACCOUNT`, 86 `PAYMENT`, and 34 `FEATURE_UX` candidates; 80 were excluded.

`real_pilot_dataset.csv` contains **120** included rows, 30 per label, selected with seed `6203`. Every row preserves the source UID and app name. Its SHA-256 is `08a7c52ff744a17f3ad51afc6870df79deda9c26272d08be5127fa3909972b5b`. The labels were fixed in this file before scoring. This is a deliberately balanced, curated sample from a narrow app domain; it does not represent the natural frequency of issues across all mobile apps. The account supplement also favors reviews with explicit access vocabulary.

## Human label verification

On 30 September 2026, the project owner reviewed all 120 rows against the written taxonomy. The outcome was **120 `KEEP`, 0 `CHANGE`, and 0 `UNSURE`**. The 12 rows where the LLM disagreed with the reference label received an additional written check; every reference label was retained. The review took place after the pilot run, so it was not blind to the model disagreements, but no post-run label changes were made. `human_label_review.csv` records the decision for every row and the reasons for the 12 disagreement cases.

## Keyword baseline

Run `python3 baseline.py real_pilot_dataset.csv`. The saved per-row results are in `real_pilot_baseline_predictions.csv`.

| Metric | Result |
|---|---:|
| Accuracy | 0.592 (71/120) |
| Macro-F1 | 0.526 |

| Actual \ Predicted | BUG | ACCOUNT | PAYMENT | FEATURE_UX |
|---|---:|---:|---:|---:|
| BUG | 1 | 2 | 4 | 23 |
| ACCOUNT | 0 | 20 | 9 | 1 |
| PAYMENT | 0 | 0 | 24 | 6 |
| FEATURE_UX | 0 | 2 | 2 | 26 |

The main failure is `BUG`: the rules recognize only 1 of 30 examples. Many real reviews describe a symptom such as a stopped timer, failed reminder, or prolonged buffering without using one of the current rule phrases. Payment terms in a review can also override its primary account-access issue. These are observations about this frozen pilot set; no labels or rules were changed after scoring.

## Zero-shot LLM run

`zero_shot.py` makes one request per review with a four-class, example-free prompt. It asks for plain JSON so JSON validity can be measured separately. With `OPENROUTER_API_KEY`, the default is [`openai/gpt-4o-mini`](https://openrouter.ai/openai/gpt-4o-mini/overview); with `OPENAI_API_KEY`, the default is [`gpt-6-luna`](https://developers.openai.com/api/docs/models/gpt-6-luna). It uses only Python's standard library.

```bash
python3 zero_shot.py --limit 1
python3 zero_shot.py
```

The first command saves one prediction; the second resumes the remaining reviews. When all 120 are complete, the script prints accuracy, macro-F1, JSON validity, token usage, and a confusion matrix. It writes `zero_shot_predictions.csv` after each response, so an interrupted run can resume. The completed result below is frozen; use a new output filename if the prompt or model changes.

### Frozen pilot result

The full run completed on 30 September 2026 through OpenRouter with `openai/gpt-4o-mini`. The saved predictions use one dataset hash and one prompt hash across all 120 rows. No labels, rules, or prompt text were changed after scoring.

| Metric | Keyword baseline | Zero-shot LLM | Difference |
|---|---:|---:|---:|
| Accuracy | 0.592 (71/120) | **0.900 (108/120)** | +0.308 |
| Macro-F1 | 0.526 | **0.900** | +0.374 |
| Valid JSON | N/A | **120/120** | — |

Zero-shot confusion matrix:

| Actual \ Predicted | BUG | ACCOUNT | PAYMENT | FEATURE_UX |
|---|---:|---:|---:|---:|
| BUG | 28 | 0 | 0 | 2 |
| ACCOUNT | 1 | 29 | 0 | 0 |
| PAYMENT | 0 | 0 | 27 | 3 |
| FEATURE_UX | 3 | 2 | 1 | 24 |

| Label | Precision | Recall | F1 |
|---|---:|---:|---:|
| BUG | 0.875 | 0.933 | 0.903 |
| ACCOUNT | 0.935 | 0.967 | 0.951 |
| PAYMENT | 0.964 | 0.900 | 0.931 |
| FEATURE_UX | 0.828 | 0.800 | 0.814 |

The run used 25,072 input tokens and 693 output tokens. Mean latency was 1,455 ms per review, median latency was 1,398 ms, and the 95th percentile was 2,064 ms. At the model page's listed rates of $0.15 per million input tokens and $0.60 per million output tokens, the estimated model cost is about **US$0.0042**. This is an estimate rather than the provider invoice.

There were 12 errors. Six involved reviews labeled `FEATURE_UX`; uninstallability complaints were read as `BUG`, and mandatory registration was read as `ACCOUNT`. Three `PAYMENT` reviews framed price or free-content concerns as requests and were read as `FEATURE_UX`. Two indirect malfunction reports were also read as experience complaints. Human verification retained all 12 reference labels: the errors consistently came from following salient words such as account or pay instead of the review's primary issue under the stated rules.

Reproducibility identifiers:

- Dataset SHA-256: `08a7c52ff744a17f3ad51afc6870df79deda9c26272d08be5127fa3909972b5b`
- Human-review record SHA-256: `72f6c517f309813db7d61045bc3fa91678d59413bd09f64b8f64cfaa9174ee47`
- Prompt SHA-256: `5f90419fb0d4dbe2cb5034f393c1a7d78c3b10cbfc4357461ebdc909df13b300`
- Prediction file SHA-256: `c7859fc922f27c83b72e96f7f249fc186ef728c227907a80ba343d64afccba56`

These results can now be reported as the human-verified pilot evaluation. The report should still state that the set is small, balanced, curated, limited to mental-health apps, and partly sampled with account-related vocabulary. Those constraints limit how far the result can be generalized to mobile-app reviews overall.
