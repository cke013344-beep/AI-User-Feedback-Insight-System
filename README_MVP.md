# PE6201 AI User Feedback Insight System — MVP

This first slice classifies one English mobile-app review into one of four product feedback categories. The bundled 40 reviews are **synthetic smoke-test data written for this MVP**. They are not collected from a public dataset, and they are not the final evaluation set.

## Taxonomy and labeling rules

- `BUG`: an existing feature fails, crashes, freezes, or behaves incorrectly.
- `ACCOUNT`: sign-in, identity, registration, password, verification, or profile access.
- `PAYMENT`: charges, subscriptions, purchases, refunds, payment methods, or billing.
- `FEATURE_UX`: a requested capability or an improvement to usability, accessibility, or interaction.

Use the primary issue described in the review. A feature that fails belongs to `BUG`; a suggestion to add or change something belongs to `FEATURE_UX`. Account access belongs to `ACCOUNT`, and money or subscription issues belong to `PAYMENT`. Each sample has exactly one label.

The CSV contains 10 samples per label. Wording includes paraphrases and indirect requests so the baseline can be smoke-tested beyond exact label words. The labels and examples are synthetic, so scores only check that the script runs; they do not establish real-world model quality.

## Run

Requires Python 3 and no third-party packages. From this directory:

```bash
python3 mvp.py "The app closes whenever I open my saved trip."
python3 baseline.py
```

`mvp.py` returns one JSON object such as `{"category": "BUG"}`. It accepts a review argument, text piped to standard input, or interactive input when run by itself. The default `rule` method works locally. With `OPENAI_API_KEY` or `OPENROUTER_API_KEY` configured, `python3 mvp.py --method llm "review text"` calls the zero-shot model instead. Input should describe a product issue; general praise has no category in this four-label taxonomy.

To use another CSV with `review` and `label` columns:

```bash
python3 baseline.py path/to/reviews.csv
```

The script prints each prediction, accuracy, macro-F1, and a confusion matrix with actual labels as rows and predictions as columns.

## Smoke-test result and review

The keyword baseline correctly classified 39 of the 40 synthetic rows: accuracy **0.975** and macro-F1 **0.975**. Its one error is row `023` (`renewed me for a year`), classified as `FEATURE_UX` instead of `PAYMENT`. This is a useful example of a simple rule missing a word form. Earlier substring matching also mistook `change` for `hang`; the script now matches complete words and phrases.

| Actual \ Predicted | BUG | ACCOUNT | PAYMENT | FEATURE_UX |
|---|---:|---:|---:|---:|
| BUG | 10 | 0 | 0 | 0 |
| ACCOUNT | 0 | 10 | 0 | 0 |
| PAYMENT | 0 | 0 | 9 | 1 |
| FEATURE_UX | 0 | 0 | 0 | 10 |

Row `033` is potentially ambiguous: it mentions both tiny text (`FEATURE_UX`) and a text-size setting that does not work (`BUG`). Its existing smoke-test label is retained, but it should not be copied into a final single-label test set without adjudication. Rows `022`, `029`, and `030` also deserve a second labeling pass because they mention payment alongside failed functionality or navigation. A high score on examples written for this MVP is **not evidence of performance on real reviews**.

The real-review pilot and its 120-row human label check are now complete. See [README_PILOT.md](README_PILOT.md) for provenance, the keyword-versus-LLM comparison, label verification, error analysis, and reproducibility identifiers.

Stage 2 adds severity, user need, specific issue topics, exact evidence quotes, and a local batch summary while keeping the Stage 1 experiment frozen. See [README_STAGE2.md](README_STAGE2.md).

For a browser demo that can also be shared on the same Wi-Fi, see [README_WEB.md](README_WEB.md).
