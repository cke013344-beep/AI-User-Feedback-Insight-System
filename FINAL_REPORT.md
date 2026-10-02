# AI User Feedback Insight System

## Business and technical trade off analysis

PE6201 Individual Project | CHENKE | Section C | 2 October 2026

## 1 Problem and scope

I built a feedback triage prototype for an app product manager preparing a weekly issue review. This user needs to identify recurring problems and inspect the supporting comments before deciding what to fix. As a planning example, reading 200 reviews at 30 seconds each takes about 100 minutes; this is an assumption, not measured time saved by my system.

Appbot already offers automated review topics and sentiment analysis [1]. My project addresses a smaller learning goal: making my own taxonomy, evidence rules and baseline comparison inspectable. I chose English mobile app reviews, with mental health apps as the pilot domain. Clinical advice, automatic refunds, replies and production decisions are outside scope.

## 2 Why this design

I began with a keyword classifier because it is inexpensive, transparent and easy to run locally. I then used openai/gpt-4o-mini through OpenRouter to interpret indirect wording. I did not train a model because my labelled data was small. RAG and an agent were unnecessary: the information needed is already in each review, and no external action is required.

The final workflow returns one primary category, one of ten fixed topics, severity, a user need and an exact quote. The categories are BUG, ACCOUNT, PAYMENT and FEATURE_UX. Severity uses stated impact: blocked core tasks or wrongful charges are high, concrete disruption is medium, and minor inconveniences or optional requests are low. Fixed topics make aggregation easier than free text.

| Layer | Choice and reason |

| --- | --- |

| Interface and serving | Own HTML and Python; control the workflow without extra packages. |

| Orchestration | Own sequential batches, pause, explicit retry and local history. |

| Model | Rent GPT-4o-mini through OpenRouter; avoid training and hosting. |

| Data and evaluation | Own labels, frozen references and scoring; use MHARD review text. |

| Observability | Own raw-response logs, token records and output checks. |

## 3 Data and evaluation

I first used 40 synthetic smoke-test comments, clearly labelled synthetic. The real source is MHARD, a public research dataset [2]; its original ratings are not my issue labels. AI assistance supported coding and draft annotation, and I approved the references.

The category-only pilot used 120 reviews, 30 per class. Labels were drafted before scoring; my later review retained all labels but was not blind. A separate 20-review development subset supported prompt revisions, so I do not present its best score as final performance.

For the full V5 workflow, I approved 20 fresh reviews, five per class, before running the model. Source IDs and exact review text did not overlap with the previous 260 candidates. Both prompt and reference hashes were frozen. Selection was keyword-screened and purposive, within the same five apps.

## 4 Results and errors

On the same 120 pilot reviews, keyword accuracy was 59.2% and macro-F1 0.526; the zero-shot LLM reached 90.0% and 0.900. Accuracy improved by 30.8 percentage points. Always choosing one class scores 25% on this balanced sample.

The final V5 run evaluated the expanded workflow separately:

| Final V5 measure | Result |

| --- | --- |

| Category accuracy | 19/20 (95%) |

| Fixed topic accuracy | 17/20 (85%) |

| Severity accuracy | 16/20 (80%) |

| Complete output validity | 19/20 (95%) |

Invalid complete outputs count as failures in these scores. H018 changed the quote's initial If to if and was rejected despite otherwise correct fields. H005 chose a generic function topic for reminders. H014 treated a displayed price mismatch as high severity without a reported debit. My qualitative content review accepted the outputs, but H011's added phrase after uninstallation shows why formatting alone cannot establish faithful interpretation. I have not measured independent human agreement or a per-field human pass rate.

## 5 Cost and practical trade offs

The final 20 calls used 25,239 input and 875 output tokens, averaging 1.843 seconds per review. At the listed prices of US$0.15 and US$0.60 per million tokens [3], model cost is approximately US$0.00431: about US$0.000216 per review or US$0.000227 per valid complete output. These estimates exclude human review, maintenance, provider fees and failed requests with unknown usage.

I chose Python's standard library for transparent scoring and file control, rather than adding a workflow platform. I did not run a low-code comparison, so I cannot claim this route was faster to develop. Renting the model reduces setup effort but introduces network and provider dependence. Human checking is likely to dominate model cost.

## 6 Usability safeguards and limitations

The local website supports single reviews, CSV batches, distributions, filtering, history and exports, with keyword and AI results side by side. English and Chinese pages share local history. Weekly reports compare saved batches by app and review week, showing sample counts, share changes and source comments without extra model calls. One successful saved single-review AI run is visible in local history; I have not verified every new web control end to end.

Wrong priorities can silently pass format checks, so original comments remain visible and users can filter high-severity cases for review. Invalid outputs are explicitly flagged: rejection was 1/20, or 5%, in V5. This is not calibrated confidence-based abstention. Unexpected interruptions are not automatically resent, reducing duplicate charges.

Keys stay in a private local file, which is plaintext rather than encrypted. History is local, but AI input goes to the model service; sensitive customer information needs screening. Human oversight follows the principle discussed in IMDA's Model AI Governance Framework [4], without claiming compliance certification.

The evaluation is small, balanced, from one domain and reviewed by one owner. Each prompt had one recorded pass; I cannot establish run-to-run stability. The tool selects one primary issue and does not cover every possible topic. Its scores do not prove production reliability.

## 7 What I learned

The main lesson was that adding more outputs does not automatically improve the system. Fixed topics initially caused category/topic mixing, and severity remained harder than broad classification. I would keep the current version as a local assistant, with manual decisions. The next useful work is an independently annotated, broader sample and a measured review-time study, rather than more features or repeated tuning on the same examples.

## References

[1] Appbot. How To Use Topics. https://support.appbot.co/help-docs/how-to-use-topics/

[2] Sensify-Lab. MHARD dataset. Source commit 6a492efa0eaf9a27e2593a4a370349f91e1e044d. https://github.com/Sensify-Lab/MHARD

[3] OpenRouter. GPT-4o-mini model pricing. Accessed 2 October 2026. https://openrouter.ai/openai/gpt-4o-mini/overview

[4] IMDA. Model AI Governance Framework. https://www.imda.gov.sg/about-imda/emerging-technologies-and-research/artificial-intelligence
