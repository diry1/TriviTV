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
python3 scripts/translate_questions.py --translate --model gpt-4.1-mini --limit 100 --batch-size 10
```

This command sends public source question text/choices to OpenAI and incurs API charges on your account. Each valid batch is saved atomically. Rerunning skips existing translations and recorded exclusions. Interrupted/failed batches leave previously saved work intact. API output is draft material; structural checks cannot verify translation quality or semantic preservation of choice order. Check current provider pricing before a full run; no cost estimate is implied here.

To translate the remainder after reviewing a sample, raise `--limit` (for example, `--limit 38926`). English-dependent wordplay, spelling or ambiguous questions are recorded under `excluded` with a reason, rather than silently replaced. Revisit exclusions and source changes editorially before rerunning; excluded fingerprints are stored for auditing.

Alternatively translate with another service or human translators and import a file following the same metadata and question-record schema:

```sh
python3 scripts/translate_questions.py --import-file /path/to/uk-translations.json
```

Import validates and merges by source ID; an incoming record deliberately replaces an existing translation with that ID. Restart the server after changing the bank.

## Editorial checks

Review names and established Ukrainian titles, grammar, transliteration, distinct distractors, time-sensitive wording and whether the same answer is still correct. Do not translate English spelling/wordplay literally when the premise breaks. Exclude it or explicitly adapt and review it. Mark a translation `reviewed` only after an independent person checks it; machine-generated records stay `draft`. Inherited source factual errors are not fixed automatically.

The UI dictionary is `web/i18n.js`. Translated labels are separate from canonical category keys. DOM localization excludes question/choice text and player names; those must never be translated by matching UI labels. The server delivers translations before shuffling, so all participants see consistent question and answer ordering. The Android WebView uses the same language selector; no Android-specific language pack is required.
