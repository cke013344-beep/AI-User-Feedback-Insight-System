# Feedback Studio user guide

## Open the app

On macOS, double-click `Launch_Feedback_Studio_EN.command`. Enter your own OpenRouter key if prompted; input is hidden. Press Enter without a key to use keyword mode. Keep the terminal open. Python 3.9+ is required; no external Python packages are needed. The server uses `fcntl`, so macOS/Linux are supported; Windows requires adaptation.

From a terminal:

```bash
python3 web_app.py --provider openrouter --language en --port 0 --open
```

The Chinese launcher remains available in the personal bilingual workspace. Use the language links in the sidebar to switch without repeating analysis. Both pages on the same local server use the same saved history. Language changes do not translate original user content or alter the model prompt.

Stop the old server with Ctrl+C and restart after updating Python files. Refreshing the page alone cannot update a running backend. Opening HTML directly is an offline preview: only single-review keyword classification is available, without saved history, batches or weekly reports.

## Single review and batches

- **Single review:** enter an English app review, then choose **Start AI analysis** or **Run keyword classification only**.
- **CSV batch import:** choose **Download sample CSV** for two synthetic demonstration comments. Select a UTF-8 file containing `review`; `review_id` is optional. Maximum 500 rows, 2000 characters per review and 2 MB per file.
- Import only previews the file. **Confirm and start AI batch** makes one paid model call per review. **Run keyword batch only** provides broad categories without model calls or the other AI fields.
- Select a result row to compare source text, baseline category and the five AI fields: category, topic, severity, need and evidence. Exact-quote validation does not establish correct interpretation.
- Pause waits for the current request. Resume continues pending reviews. Retry explicitly resends failed, invalid or interrupted reviews and may add charges. Network failures pause the batch.
- Filters affect the table; batch charts and CSV/JSON exports cover the entire batch. Export includes statuses and failures. Accepted-result counts are not accuracy scores.

## Weekly trends and reports

1. Open a saved batch. Enter **App name** and **Review week**, then choose **Save report assignment**.
2. Each batch must represent one app and one actual review week. Split mixed files. Any selected date is stored as that Monday. Old records are not automatically dated from their analysis time. Keep synthetic examples under a separate app name such as DEMO.
3. Under **Weekly trends and report**, select **Report week**, **App** and **Analysis method**, then choose **Generate / refresh report**.
4. Inspect current and previous counts, accepted denominators, topic shares, percentage-point changes and source comments. AI and keyword methods are separated. Keyword mode reports categories only. Missing previous-week data produces a current-week summary without fabricated growth.
5. Choose **View source review and full result** to trace an example, or **Download report Markdown** to save an editable report with source batch IDs.

Within one app/week/method, review text is deduplicated ignoring case and extra whitespace. Accepted results take precedence over failures; the latest successful batch wins. Identical text from distinct users can therefore be merged. Invalid, failed, interrupted and pending reviews are excluded from share denominators but counted separately. Different model/prompt versions are flagged.

The top three topics are ranked by current-week count; up to three examples per topic favour model-labelled high severity. This is descriptive grouping, not evidence of one shared fault or an automatic product priority. Counts describe selected imported reviews, not all users or statistically established incidence changes. Weekly reporting reuses saved results and makes no extra model calls.

## Privacy and reproducibility

Keys and workspace records live in `local_data/`, excluded from the code package and ignored by Git. The key file is private but plaintext. AI sends review text to the model provider, so screen sensitive inputs. Share source code and saved public evaluation materials, not private configuration or personal history. JSON exports preserve original reviews and evidence; English diagnostics are translated for display/export.

The recorded V5 evaluation is frozen and unchanged. Weekly reporting and the English interface were added afterward; no new model evaluation or end-to-end validation run is claimed. The code implements these features, but their presence does not prove every interaction works under all conditions.
