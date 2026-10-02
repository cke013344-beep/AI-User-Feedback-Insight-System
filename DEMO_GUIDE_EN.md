# PE6201 demonstration guide

Suggested duration: 4–6 minutes. This is a preparation suggestion, not a confirmed instructor requirement. Follow the actual submission page for duration, format and naming.

## Preparation

Open `Launch_Feedback_Studio_EN.command`. Configure the key before recording. Download the two-row sample under **CSV batch import → Download sample CSV**. Keep the final evaluation results document and repository page available. On macOS, Shift+Command+5 opens recording controls; select your microphone under Options.

## Screen actions and narration

### Problem and design

Show the English home page.

“My project helps a small app product team organise English reviews. It returns an issue category, severity, user need and source evidence, with a fixed topic for grouping. I started with an explainable keyword baseline and used GPT-4o-mini for indirect wording. The review contains the information needed, so I did not add RAG or an agent.”

### Single review

Open a saved successful AI record from **Analysis history**, select its row, and show **Review details**. Say that this is a saved result. Alternatively, enter a review and choose **Start AI analysis**, which makes a new paid call.

“Here I can compare the keyword category with the AI fields and check the evidence against the source text. Valid fields and an exact quote still require human interpretation.”

### CSV batch and exports

Choose **CSV batch import**, select `synthetic_format_examples.csv`, and show the two-row preview. Say these are synthetic demonstration comments. Choose **Confirm and start AI batch**, confirm the two calls, and wait for completion. Keyword mode is available for a practice run without model calls, but it does not produce the full AI fields.

Show charts, change a category filter, clear the filter, select a row, and choose **Export CSV** or **Export JSON**.

“Importing previews the data before any model calls. Each result is saved. The filters affect the list, while charts and exports describe the whole batch.”

### Weekly reporting

Enter **App name** as DEMO and assign the actual demonstration week; choose **Save report assignment**. Select that app, week and analysis method under **Weekly trends and report**, then choose **Generate / refresh report** and **Download report Markdown**.

“This report reuses saved results without extra AI calls. With no previous-week data, it shows a current-week summary and explicitly avoids a growth claim. Real comparisons require reviews from both actual weeks. The report includes sample counts, shares and source comments so a product manager can review them.”

Do not relabel the same batch as two real weeks to manufacture a trend. A one-week summary is an honest first demonstration.

### Recorded evaluation and a failure

Open `FINAL_EVALUATION_RESULTS.md`. Explain the two separate experiments:

“The original category-only experiment compared methods on the same 120 reviews: keyword accuracy was 59.2 percent and zero-shot LLM accuracy was 90 percent. The expanded V5 workflow used 20 fresh reviews: category accuracy was 95 percent, topic 85 percent, severity 80 percent and complete-output validity 95 percent. These are different experiments, so 90 versus 95 is not a direct improvement comparison.”

Show H018 changing quote case and H014 overstating severity. Explain that small, curated samples and owner-reviewed labels limit generalisation. Weekly reports and the English interface were later usability additions, with no new end-to-end validation claim.

### Conclusion

“I would use this as a local triage assistant with human review. The weekly report helps move from individual comments to a discussion of recurring topics, while keeping the source text available. My next priority would be broader independent annotation and measured review-time savings.”

Show the repository URL: https://github.com/cke013344-beep/AI-User-Feedback-Insight-System

Stop and replay the recording. Confirm audible narration, readable text and accurate descriptions of saved versus live results. The video has not been submitted merely because the repository exists.
