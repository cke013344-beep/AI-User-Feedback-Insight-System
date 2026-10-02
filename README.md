# AI User Feedback Insight System

PE6201 individual project by CHENKE. A personal local workspace for English app-review triage: four broad categories, ten fixed topics, impact severity, a grounded user need and an exact evidence quote. Python 3.9+; no external Python packages required for the app. The macOS launcher uses zsh and the local history lock uses fcntl, so this personal launcher/server targets macOS/Linux rather than Windows.

## Run locally

For the English interface on macOS, double-click `Launch_Feedback_Studio_EN.command`. The Chinese page is available through the language link; keep the separate Chinese launcher in your personal workspace. Enter your own valid OpenRouter key when prompted, or press Enter for keyword-only mode. The browser opens automatically. Keep the terminal window running; Ctrl+C stops the service. Keys and history are written to local_data/, which is excluded from this code material and ignored by Git. If an archive download loses executable permissions, run `zsh Launch_Feedback_Studio_EN.command` from this folder.

Alternatively:

```bash
python3 web_app.py --provider openrouter --language en --open
```

AI needs OPENROUTER_API_KEY in the server environment or the private local config described in README_WEB_EN.md. Do not place a key in HTML, source files or GitHub. The project does not provide API credentials or deploy a public service.

## Weekly reports

Assign saved batches an app name and review week, compare with the preceding week, inspect representative reviews and export Markdown. Reporting uses saved results without model calls, separates AI and keyword methods, and deduplicates normalized text within each week. See README_WEB_EN.md for instructions and limitations. This addition has not received end-to-end validation.

## What to inspect without new API calls

- README_PILOT.md: same 120-row keyword versus zero-shot classification experiment.
- FINAL_EVALUATION_RESULTS.md: fresh 20-row full-insight evaluation.
- final_evaluation_freeze.json: reference and prompt freeze hashes.
- STAGE2_REVISION_LOG.md: development changes and observed errors.
- README_WEB_EN.md: batches, persistence, weekly reports, exports and usage limits.
- DEMO_GUIDE_EN.md: English recording steps and narration.

The saved outputs can be reviewed without spending API credits. `python3 baseline.py real_pilot_dataset.csv` reproduces the non-AI scoring if desired; do not rerun model calls simply to read the existing results.

## Data and attribution

`evaluation_dataset.csv` contains 40 **synthetic smoke-test comments**, not real public reviews or final evaluation data. The other selected review texts come from [MHARD](https://github.com/Sensify-Lab/MHARD), source commit 6a492efa0eaf9a27e2593a4a370349f91e1e044d. Source SHA256 and selection limitations are in README_PILOT.md and README_FINAL_EVALUATION.md. The upstream MIT notice is retained in MHARD_LICENSE.txt. Issue/severity/topic references are project annotations, not MHARD ground truth for those tasks. Labels were drafted with AI assistance and checked by one project owner; no independent multi-rater agreement is claimed.

Please cite the MHARD authors' paper when using the data: Wang et al. (2025), Leveraging Large Language Models for Review Classification and Rating Estimation of Mental Health Applications, ICWSM 19(1), 2017–2029, https://doi.org/10.1609/icwsm.v19i1.35916.

## Status

The model pipeline has recorded experiments. Local history also records one successful single-review AI use, but all newly added UI controls have not been separately validated end to end. An earlier version is published at https://github.com/cke013344-beep/AI-User-Feedback-Insight-System. This package contains the subsequent bilingual interface and weekly reports; uploading this revision and recording/submitting the demo remain separate steps.

The separate course report and problem statement accompany the project submission. The completed trade-off analysis is below the 1,200-word cap. Final upload format follows the actual NTULearn submission page.
