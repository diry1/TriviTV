# Ukrainian translation

Choose **Українська** in the header before creating a room. Language is independent of Europe/US region and category settings. The host chooses the room's question language; joining phones adopt it. The language is fixed for the room, and the setup preference is saved locally.

## Current scope

The interface is localized and **40 of 38,926** source questions have draft Ukrainian translations covering all 20 categories. This is a playable preview, not a fully translated bank. No translations have been independently reviewed. Small category/region combinations can have fewer than 10/15 questions or no eligible questions. The setup shows translation coverage. Ukrainian games never fall back silently to English questions. English remains the full original bank. Region tags and unrated difficulty are inherited from the source adaptation.

Translation text and choices live in `data/translations/uk.json`, under CC BY-SA 4.0, with source IDs, source revision, per-question source fingerprints and translation method/status. Canonical correct-answer indexes are never accepted from a translation. The game shuffles translated choices and the corresponding answer key together. Stale fingerprints, duplicate IDs/choices and malformed records prevent loading. Technical names and original work titles can remain in Latin script.

## Completing the bank

A translation provider/account is still needed for the remaining questions. No external translation API has been called or charged during this implementation. Do not paste API keys into chat or commit them.

Validate current translations:

```sh
python3 scripts/translate_questions.py --check
```

The resumable OpenAI workflow uses Python's standard library. Set `OPENAI_API_KEY` securely in your environment, choose your model and begin with a small sample:

```sh
python3 scripts/translate_questions.py --translate --model gpt-4.1-mini --limit 100 --batch-size 10 --stratified --budget-usd 15
```

This command sends public source question text/choices to OpenAI and incurs API charges on your account. The 100-question trial is distributed across all 20 categories. `TRIVITV_TRANSLATION_KEY` is also accepted for a managed environment secret binding. Each valid batch is saved atomically. Rerunning skips existing translations and recorded exclusions. Interrupted/failed batches leave previously saved work intact. API-reported input/output token usage is saved before validating translation content, so failed or incomplete output still counts. Estimated USD cost is calculated at the configured model rates. API output is draft material; structural checks cannot verify translation quality or semantic preservation of choice order. Check current provider pricing before a full run; no cost estimate is implied here.

To translate the remainder after reviewing a sample, raise `--limit` (for example, `--limit 38926`). English-dependent wordplay, spelling or ambiguous questions are recorded under `excluded` with a reason, rather than silently replaced. Revisit exclusions and source changes editorially before rerunning; excluded fingerprints are stored for auditing.

Alternatively translate with another service or human translators and import a file following the same metadata and question-record schema:

```sh
python3 scripts/translate_questions.py --import-file /path/to/uk-translations.json
```

Import validates and merges by source ID; an incoming record deliberately replaces an existing translation with that ID. Restart the server after changing the bank.

## Editorial checks

Review names and established Ukrainian titles, grammar, transliteration, distinct distractors, time-sensitive wording and whether the same answer is still correct. Do not translate English spelling/wordplay literally when the premise breaks. Exclude it or explicitly adapt and review it. Mark a translation `reviewed` only after an independent person checks it; machine-generated records stay `draft`. Inherited source factual errors are not fixed automatically.

The UI dictionary is `web/i18n.js`. Translated labels are separate from canonical category keys. DOM localization excludes question/choice text and player names; those must never be translated by matching UI labels. The server delivers translations before shuffling, so all participants see consistent question and answer ordering. The Android WebView uses the same language selector; no Android-specific language pack is required.

## Cumulative $15 budget and usage report

The default `--budget-usd 15` applies across the trial and subsequent runs via `.translation-usage.json` in the repository root. This local ledger is gitignored; retain it when resuming. Before every paid request, the script saves a conservative reservation based on request size and the configured output token limit. Successful responses replace that reservation with cost estimated from API-reported token usage. Interrupted/failed requests retain their full reservation because billing is uncertain. Invalid translation output still counts against the budget. A concurrent-run lock prevents two instances from independently spending the same remaining budget.

Inspect saved usage without making API calls:

```sh
python3 scripts/translate_questions.py --usage-report
```

After assessing the trial, process all remaining questions under the same cumulative allowance:

```sh
python3 scripts/translate_questions.py --translate --limit 38926 --batch-size 10 --budget-usd 15
```

Do not delete/reset the ledger between runs or move the job to a different machine without copying the ledger too. After an actual process crash, confirm the process is stopped before removing a stale `.translation-usage.json.lock`; keep the JSON ledger. All source and translation files are read/written as UTF-8, including on Windows.

The configured GPT-4.1 mini rates are $0.40/million input tokens and $1.60/million output tokens. Confirm current provider pricing before paid execution. Cached-input discounts are deliberately ignored, making the estimate conservative. This is a script-side estimate limit, not an account-wide billing control or a guarantee against provider pricing changes. Charges from other API clients or missing/deleted ledgers cannot be tracked. The script stops if funds under this allowance are insufficient; it does not guarantee completion for $15. No paid API trial or bulk translation has been executed from the cloud session while credentials remain unavailable.
