"""Auditable stricter rule-based extrapolation of the 400 sample reviews.

Flags uncertain matches as holds, never claims semantic or factual approval.
Does not change the runtime or original eligibility; this is a comparison pass.
"""
from collections import Counter
import csv
import difflib
import hashlib
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'provided-916/TriviTV-EU-Filtered-Test/Server/data'
OUT=ROOT/'artifacts/sample-feedback-screen-2026-10-21'
source=json.loads((BASE/'opentriviaqa/questions.json').read_text(encoding='utf8'))
translations={q['id']:q for q in json.loads((BASE/'translations/uk.json').read_text(encoding='utf8'))['questions']}
review=json.loads((BASE/'editorial/eu-ua/review-decisions.json').read_text(encoding='utf8'))['decisions']
kept={q['id'] for q in review if q['decision']=='Keep'}
baseline=json.loads((ROOT/'artifacts/question-bank-screen-2026-10-21/potential-ukrainian-questions.json').read_text(encoding='utf8'))
baseline_ids={q['id'] for q in baseline}

# These detect specific reviewable features, not a blanket ban by category,
# nationality, age of work, or presence of a number/person name.
PATTERNS={
 'us_specific': r'\b(?:American football|National Football League|National Basketball Association|National Hockey League|college football|college basketball|Stanley Cup|Heisman|March Madness|NASCAR|Daytona 500|New York Mets|New York Knicks|San Antonio Spurs|Miami Heat|Dallas Mavericks|Philadelphia Eagles|Pittsburgh Steelers|San Francisco 49ers|Chicago Bears|Washington Redskins|Boston Bruins|New York Rangers|New York Giants|Cleveland Browns|Indianapolis Colts|Denver Broncos|Minnesota Vikings|Michael Phelps college|ESPN|PBS|MTV USA|Jay Leno|David Letterman|Conan O.?Brien|Garfield|Odie|Jon Arbuckle)\b',
 'us_state_detail': r'\b(?:state (?:capital|bird|flower|tree|song|seal|motto|nickname|flag|gem|insect)|official (?:bird|flower|tree|song|gem|insect) of (?:the )?(?:US|U\.S\.|American|state)|(?:Alabama|Alaska|Arizona|Arkansas|California|Colorado|Connecticut|Delaware|Florida|Georgia|Hawaii|Idaho|Illinois|Indiana|Iowa|Kansas|Kentucky|Louisiana|Maine|Maryland|Massachusetts|Michigan|Minnesota|Mississippi|Missouri|Montana|Nebraska|Nevada|Ohio|Oklahoma|Oregon|Pennsylvania|Tennessee|Texas|Utah|Vermont|Virginia|Wisconsin|Wyoming).{0,45}(?:governor|state capital|county|state park|state university))\b',
 'song_or_album_detail': r'\b(?:album|albums|lyric|lyrics|discography|B-side|b side|debut single|hit single|charted|chart-topping|Billboard|Grammy.{0,25}(?:song|album)|sing(?:s|ing)? (?:these|the following)|sang (?:these|the following))\b',
 'fan_or_biography_minutiae': r'\b(?:maiden name|birth name|real name|full name|middle initial|date of birth|birth date|birthday|married to|first wife|second wife|third wife|first husband|second husband|divorce|dated|boyfriend|girlfriend|school did|college did|university did|attended.{0,25}(?:school|college|university)|parents? names?|mother.s name|father.s name|cousin|nephew|niece|grandson|granddaughter|maternal|paternal|guest star|guest appearance|played the (?:part|role) of|portrayed the (?:part|role)|(?:episode|season|quest|level) (?:called|named|number)|what (?:colour|color).{0,45}(?:wear|shirt|dress|hat)|(?:pet|dog|cat).{0,25}(?:name|called))\b',
 'specialist_detail': r'\b(?:binomial name|scientific name|Latin name|taxonomic|taxonomical|subspecies|subfamily|genus|genera|chemical formula|molecular formula|atomic number|electron configuration|oxidation state|half-life|half life|differential equation|natural logarithm|logarithm|derivative|integral of|chemical symbol|mitochondrial DNA|chromosomal|chromosome number)\b',
 'precise_dates_or_records': r'\b(?:exact date|on what date|what date|which date|what day of the (?:week|month)|on which day|first (?:person|man|woman|player|athlete) to win|world record|record holder|holds the record|won the.{0,50}(?:in 18\d\d|in 19\d\d|in 20\d\d))\b',
 'missing_media_or_context': r'\b(?:this (?:sound|audio|photograph|image|picture)|following (?:clip|image|picture|audio)|hear (?:this|the)|seen (?:here|above|below)|shown in (?:this|the) (?:image|picture|photo)|as (?:pictured|illustrated)|in the previous question|above question|these pictures)\b',
}
compiled={k:re.compile(v,re.I) for k,v in PATTERNS.items()}
NUMBER_WORDS=set('zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen twenty thirty forty fifty sixty seventy eighty ninety hundred thousand million billion'.split())

def hits(q):
    found=[]
    for rule,pattern in compiled.items():
        m=pattern.search(q['text'])
        if m:found.append({'rule':rule,'evidence':m.group(),'confidence':'pattern-match-not-semantic-verification'})
    normalized=[re.sub(r'[^\w\s]','',c.lower()).strip() for c in q['choices']]
    if all(c and (any(ch.isdigit() for ch in c) or all(w in NUMBER_WORDS for w in c.split())) for c in normalized):
        found.append({'rule':'numeric_or_number_word_choices','evidence':'All four alternatives are numeric or spelled-out numbers.','confidence':'deterministic-feature'})
    # Similar multiword alternatives: preserve as a hold rather than a rejection.
    if all(len(c.split())>=3 for c in normalized):
        pairs=[difflib.SequenceMatcher(None,a,b).ratio() for i,a in enumerate(normalized) for b in normalized[i+1:]]
        if min(pairs)>.68:found.append({'rule':'near_identical_answer_choices','evidence':'All multiword answer pairs have >0.68 normalized text similarity.','confidence':'heuristic-hold'})
    t=translations.get(q['id'])
    if t:
        if len(t['text'])>500 or any(len(c)>180 for c in t['choices']):
            found.append({'rule':'uk_corrupt_or_excessive_text','evidence':'Translated prompt exceeds 500 characters or an option exceeds 180.','confidence':'deterministic-length-feature'})
        words=t['text'].casefold().split()
        if len(words)>=20 and max(Counter(words).values())/len(words)>.35:
            found.append({'rule':'uk_repetitive_translation','evidence':'One word accounts for more than 35% of a translation of at least 20 words.','confidence':'deterministic-feature'})
        if len(set(c.strip().casefold() for c in t['choices']))<4:
            found.append({'rule':'uk_duplicate_choices','evidence':'Translation has case-insensitive duplicate choices.','confidence':'deterministic-feature'})
        if any(not c.strip() for c in t['choices']) or not t['text'].strip():
            found.append({'rule':'uk_missing_text','evidence':'Empty translated question or option.','confidence':'deterministic-feature'})
    return found

records=[]; conflicts=[]
for q in source:
    matches=hits(q)
    if not matches:continue
    r={'id':q['id'],'category':q['category'],'text':q['text'],'matches':matches,'outcome':'preserved-human-keep' if q['id'] in kept else 'hold','sourceHash':hashlib.sha256(json.dumps([q['text'],q['choices']],ensure_ascii=False,separators=(',',':')).encode()).hexdigest()}
    records.append(r)
    if q['id'] in kept:conflicts.append(r)
blocked={r['id'] for r in records if r['outcome']=='hold'}
new=baseline_ids & blocked
survivors=baseline_ids-new
summary={'baselinePotential':len(baseline_ids),'newHolds':len(new),'remainingPotential':len(survivors),'reductionPercent':round(100*len(new)/len(baseline_ids),2),'overlappingNewReasons':dict(Counter(m['rule'] for r in records if r['id'] in new for m in r['matches'])),'humanKeepConflictsPreserved':len(conflicts),'fullMainBankPatternsMatched':len(records),'method':'Deterministic/heuristic generalization of sample feedback; NOT complete semantic review. Surviving questions are not approved.','runtimeChanged':False}
OUT.mkdir(parents=True,exist_ok=True)
(OUT/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf8')
(OUT/'decisions.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf8')
(OUT/'keep-conflicts.json').write_text(json.dumps(conflicts,ensure_ascii=False,indent=2),encoding='utf8')
(OUT/'remaining-ids.json').write_text(json.dumps(sorted(survivors)),encoding='utf8')
with (OUT/'new-holds.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.writer(f);w.writerow(['ID','Category','Source question','Reason tags','Matched evidence'])
    for r in records:
        if r['id'] in new:w.writerow([r['id'],r['category'],r['text'],'|'.join(m['rule'] for m in r['matches']),' | '.join(m['evidence'] for m in r['matches'])])
assert len(survivors)+len(new)==len(baseline_ids)
assert not new & kept
print(json.dumps(summary,ensure_ascii=False,indent=2))
