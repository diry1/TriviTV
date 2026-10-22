# Semantic tagging pilot — consistency review

Completed 2026-10-22. **50 questions, all 20 categories, 48 linked Ukrainian drafts.** Applied **296 confirmed tag assignments (84 distinct tags)** to these 50 IDs only in the English master. Tags remain backend-only. No question text, answer key, eligibility, Fun pool, APK or live game changed.

## Sampling and limits

40 records are deterministic selections: two per original category, ordered by a fixed hash seed. Ten extra records exercise wordplay, film/history, book titles, brands, US places, Lake Victoria, date answers, negation, awards and ambiguous Georgia. Six also have saved user reviews (3 Keep, 3 Exclude), used as calibration contrasts, not an independent test set. This small, deliberately balanced sample cannot estimate error prevalence across the bank.

See [bilingual review](review.html), [auditable classifications](audit.json), [selection recipe](selection-manifest.json) and [counts](summary.json). Each ID in the HTML opens its bilingual dashboard entry when the local dashboard is running. Ukrainian remains draft text; a green correct marker reproduces the source answer key and is not factual approval.

## Consistency decisions

| Boundary | Applied rule and examples |
| --- | --- |
| Mention versus audience | Eight questions mention USA; only four require US-specific familiarity. The worldwide mountain comparison (#14), Swedish skater with a US distractor (#34), and Halo setting choices (#37) get mention tags without US-audience tags. |
| Brand versus geography | Adidas/Puma (#50), Nintendo (#38), and SeaWorld (#47) get brand tags without inferred nationality. A commercial team name can count as a brand; company-like invented distractors are not certified as real brands. |
| What is tested versus category | General Knowledge #42 is tagged movies/history/sport; Kids Trivia #19–20 is books, not animal facts from fictional characters. Arts & Humanities #4 and General Knowledge #11 receive religion/mythology tags. This does not change source categories or exclusion policy. |
| Dates and eras | Tag the relevant work/event date, with role retained. #23 has 1990s original and 2000s remake; #48 has 1990s award-year. #39 and #46 use the correct-answer decade, not every dated distractor. #18's 1000-year duration creates no decade. Undated festival/mission eras remain proposals. |
| Negation | #17 says food is not in fact American but asks its origin: identification. #47 asks which creature is not in an exhibit: negative-question. |
| Translation scope | Wordplay/English spelling/quotes/titles/name rendering are UK risk tags, not English exclusion reasons. Missing translation is distinct from a safe translation. |
| Fiction and ambiguity | Georgia in a song (#49), New Mombasa/Voi in Halo (#37), Elbrus boundary conventions (#14), and mythological Olympia (#4) remain partly unresolved. No guessed region is published. |
| Character/title types | Use screen-characters for both film and TV; distinguish movie, book, TV, game and song titles. Silver Bullet and The Tommyknockers work-type ambiguities stay in review. |

## Vocabulary adjustments

Preserved v1 and created vocabulary-v2.json. Added topics philosophy/comics/business, form missing-word, TV/game/song title entity kinds, proverb-localization risk, and screen-characters. The older film-characters subject is deprecated for new assignments. These are pilot-derived draft changes, not automatic remapping of every bank record.

Remaining expansion proposals: comic-title, ethnic-groups, rivers-and-lakes. No one-off entity names have been turned into tags.

## Issues exposed, not corrected

- **#22, The Amber Spyglass:** Ukrainian title appears semantically suspicious; John Parry is rendered as Джон Гаррі. Needs authoritative title/name checking.
- **#49, song/TV question:** Georgia is rendered as the country Грузія; intended referent needs checking. English Family Guy corresponds to Ukrainian Американський тато, a possible distinct-show mismatch.
- **#41, sausage pun:** wurst/worst depends on English sound; Ukrainian wrong-option correspondence also needs review.
- **#32, teeth:** source and translation omit adult/child and wisdom-teeth scope. This is a source-context issue as well as localization risk.
- **#16, Soyuz:** prompt calls the answer a space station; possible source terminology issue. No factual fix was inferred during tagging.
- **#4, Norse gods:** Ukrainian wording uses Norwegian rather than the broader Norse concept; flag for terminology review.

These are review observations, not newly verified facts or permission to change correct answers. Title/attribution/source claims were not externally fact-checked.

## Validation and result

- 40 records have one or more UK-risk tags; a risk tag is not a confirmed translation error.
- 16 records retain unpublished proposals; 24 have explanatory/review notes.
- Verified IDs and full source/translation fingerprints, allowed vocabulary, unique tags, named-entity evidence spans, era roles, and explicit cross-case rules.
- Confirmed all non-semantic tags and all question content are unchanged, including EU/Fun membership.
- All three saved Keep cases remain included as before; all three saved Exclude cases remain unchanged. No automatic decision follows from these tags.
- Confidence is a judgement of content-based assignment, not a calibrated probability. This is a second pass by the same reviewer, not independent inter-rater agreement.

**Recommendation:** proceed with a larger 200-question calibration batch after reviewing the boundary decisions above; include more location ambiguities, localized works and non-US specialist topics. Do not run the full bank from a lexical keyword rule or extrapolate the sample's tag rates to 38,926 records.

## Rebuild

From the project root, run the project Python with `question-bank/semantic-tagging/pilot-v1/build_pilot.py --check` to verify this pilot. To regenerate its report/source after an intentional reviewed edit, run `build_pilot.py --publish`, then `scripts/build-question-tags.py`. A fingerprint mismatch requires review, not automatic baseline replacement. Source ownership is `custom:semantic-pilot-v1`; tags use `custom:semantic:*`. Removing the owned source and rebuilding withdraws this pilot's assignments without touching other tag sources.
