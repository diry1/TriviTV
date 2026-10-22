"""Local candidate-only screen; preserves acquired bank and live game data."""
from pathlib import Path
from collections import Counter
import csv
import hashlib
import importlib.util
import json
import re

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'provided-916/TriviTV-EU-Filtered-Test/Server'
OUT = ROOT / 'artifacts/question-bank-screen-2026-10-21'
spec = importlib.util.spec_from_file_location('saved_screen', SOURCE / 'scripts/build_eu_eligibility.py')
screen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(screen)
load = screen.load
bank = load('data/opentriviaqa/questions.json')
translations = {q['id']: q for q in load('data/translations/uk.json')['questions']}
previous = {q['id']: q for q in screen.build()['records']}
# Match vocabulary/definition/etymology tasks, not ordinary factual uses of "means".
lexical = re.compile(
    r'\b(?:etymolog\w*|word origin|literal(?:ly)? (?:mean\w*|translat\w*)|'
    r'meaning of (?:the |a |an )?(?:word|term|name|phrase|expression)|'
    r'(?:word|term|name|phrase|expression).{0,90}\b(?:mean(?:s|ing)?|translat\w*|derived|come from)|'
    r'(?:what|which).{0,60}\b(?:mean|means|meaning)\b|'
    r'(?:word|term) (?:for|describ\w*|denot\w*)|'
    r'definition of|defined as|synonym|antonym|opposite (?:of|in meaning)|'
    r'(?:French|Spanish|Italian|German|Latin|Greek|English|Japanese|Danish|Russian|Ukrainian) for)\b', re.I)
uk_lexical = re.compile(r'етимолог|значення (?:слова|термін|назв|вислов)|що означає|буквально означ|перекладається як|синонім|антонім', re.I)
rows, survivors, lexical_rows = [], [], []
for q in bank:
    if q['id'] not in translations:
        continue
    t = translations[q['id']]
    old = previous[q['id']]['uk']
    reasons = []
    words=t['text'].casefold().split()
    if len(t['text'])>500 or (len(words)>=20 and max(Counter(words).values())/len(words)>.35):
        reasons.append('UA_CORRUPT_TRANSLATION')
    if old['outcome'] == 'exclude' or (old['outcome'] == 'hold' and old['rules'] != ['UNASSESSED']):
        reasons.extend(old['rules'])
    if q['category'] == 'Religion & Faith':
        reasons.append('NEW_RELIGION_CATEGORY')
    match = lexical.search(q['text']) or uk_lexical.search(t['text'])
    if match:
        reasons.append('NEW_UA_WORD_MEANING')
        lexical_rows.append({'id': q['id'], 'source': q['text'], 'uk': t['text'], 'match': match.group()})
    reasons = sorted(set(reasons))
    status = 'filtered_or_held' if reasons else ('previously_screened_draft' if old['outcome'] == 'candidate' else 'unassessed_potential')
    rows.append({'id': q['id'], 'category': q['category'], 'status': status, 'rules': '|'.join(reasons), 'previous_outcome': old['outcome']})
    if not reasons:
        survivors.append({'id': q['id'], 'category': q['category'], 'text': t['text'], 'choices': t['choices'], 'source': q, 'translation': t, 'screenStatus': status})
OUT.mkdir(parents=True, exist_ok=True)
summary = {
    'sourceCount': len(bank), 'ukrainianDraftCount': len(translations),
    'status': 'preliminary_retrieval_not_full_semantic_or_translation_approval',
    'counts': dict(Counter(r['status'] for r in rows)),
    'potentialTotal': len(survivors),
    'categories': dict(sorted(Counter(q['category'] for q in survivors).items())),
    'ruleMatchesOverlapping': dict(Counter(rule for r in rows for rule in r['rules'].split('|') if rule)),
    'limitations': ['Existing human decisions and saved deterministic rules reused; unassessed survivors still require semantic audience screening.', 'Word-meaning detection is a retrieval heuristic and can miss cases or match false positives.', 'Movie/book translated-title verification remains pending; surviving titles are not verified.', 'Source, translation and live game files remain unchanged.'],
    'inputHashes': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in [SOURCE / 'data/opentriviaqa/questions.json', SOURCE / 'data/translations/uk.json', ROOT / 'docs/question-bank-notes.md']},
}
(OUT / 'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
(OUT / 'potential-ukrainian-questions.json').write_text(json.dumps(survivors, ensure_ascii=False), encoding='utf-8')
(OUT / 'word-meaning-matches.json').write_text(json.dumps(lexical_rows, ensure_ascii=False, indent=2), encoding='utf-8')
with (OUT / 'decisions.csv').open('w', encoding='utf-8-sig', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
print(json.dumps(summary, ensure_ascii=False, indent=2))
