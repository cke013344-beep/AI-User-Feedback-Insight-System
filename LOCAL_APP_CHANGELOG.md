# Personal local workspace changes

Added a double-click macOS launcher, Chinese single/batch review interface, sequential processing, pause/resume and explicit retry, per-run local JSON persistence, history, counts/distributions, filters, side-by-side keyword/AI details, and CSV/JSON export. The launcher saves a user-entered API key only to a private local configuration file. Browser API requests require a page token; non-local hosts additionally require an access code. Input lengths, counts, CSV schema, and output fields are validated.

The one-worker design intentionally limits throughput to one AI run at a time. Pause cannot undo an in-flight external request. Interrupted requests are flagged rather than silently repeated. Individual attempts and raw invalid outputs are retained. Changes to model/prompt prevent resuming an old run under different settings.

The insight prompt, frozen evaluation references, and existing model outputs are unchanged. Historical backend/frontend copies are retained in work/. No new evaluation rounds, automated tests, or live paid calls were run during implementation. This is an implemented local app, not a claim of completed runtime validation or public deployment.
