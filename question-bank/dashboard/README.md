# TriviTV question-bank dashboard

Local URL: http://127.0.0.1:8791/

Start with `start-dashboard.ps1`, or run `python question-bank/dashboard/server.py` from the project root and open the URL. No packages, account or external services are required. The server binds only to loopback. Keep it running while using the dashboard. Restart after rebuilding question-bank tags to load updated data.

- **Main:** all 38,926 English records, including excluded and held questions.
- **EU:** 27,948 English survivors (`EU:en`): Main minus audience/content filters. Translation-only issues and absence of prior semantic review do not remove a question. Includes 882 previously screened drafts and 27,066 unassessed/reopened questions.
- **UA:** all 36,614 Ukrainian translations; initially filtered to the 24,932 potential questions. Pool options allow all translations, 799 screened drafts, or 24,133 unassessed potentials.

Search prompts, answers or IDs; filter category, language-scoped editorial outcome, pool, translation availability, tags (AND/OR) and excluded tags. Sort and page results. Click a question to inspect English and Ukrainian side by side, correct choices, tags and source attribution. Export **all filtered results** as CSV or JSON, not just the visible page.

Category, EU status and tag-count cells now open the editable bilingual detail panel. Choose a category, set English/Ukrainian review status independently, add/remove personal tags and press Save changes. Saving regenerates the master and category-sensitive Fun Bank; it can take a short while. Automatic source/filter tags remain evidence-managed; personal tags use `custom:manual:*`. EU membership follows the review status. Automatic/Original restores inherited values. The original imported text, answers and source categories remain recoverable in the preserved archive.

Edits persist in `../editorial-overrides.json` with per-ID before/after history and a revision guard against stale concurrent edits. The server accepts edits only from the local dashboard origin and serializes saves. A rebuild failure is reported without claiming success; the saved override/history is retained for recovery by rerunning the tag builder. Filters/exports themselves do not change data. Changes do not publish a website, rebuild an APK or alter running games. Tags and answers are backend/editorial data. Counts do not establish factual verification.

Question IDs are links to `/?question=<id>`, opening the English and linked Ukrainian text/answers directly. Missing translations are explicitly labelled. CSV exports include a `translation_link` column; the local server must be running for those links.

Validation: `python -m unittest discover -s question-bank/dashboard -p test_dashboard.py -v`.

Answer options A-D are displayed directly below every question in all three sheets. The correct option is marked in green with a Correct label; bilingual details remain available by clicking the question.
