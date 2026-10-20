#!/usr/bin/env python3
"""Build auditable, conservative EU pools without network calls or source edits."""
import argparse
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'
OUTPUT = DATA / 'editorial/eu-eligibility.json'
INPUTS = ['data/opentriviaqa/questions.json', 'data/translations/uk.json',
          'data/editorial/eu-ua/policy.json', 'data/editorial/eu-en/policy.json',
          'data/editorial/eu-ua/review-decisions.json',
          'data/editorial/eu-en/review-decisions.json',
          'data/editorial/eu-ua/quality-flags.json',
          'data/editorial/eu-evidence/prior-screening.json',
          'docs/eu-ua-editorial-rules.md', 'docs/eu-english-editorial-rules.md']


def load(name):
    return json.loads((ROOT / name).read_text())


def fingerprint(text, choices):
    return hashlib.sha256(json.dumps([text, choices], ensure_ascii=False,
                                    separators=(',', ':')).encode()).hexdigest()


def assessment(outcome, rules, evidence, origin):
    return dict(outcome=outcome, rules=rules, evidence=evidence, origin=origin)


# Match full entity identities, not isolated city/team nicknames. These are
# retrieval/hold rules, not a claim to have classified every possible entity.
PRESIDENTS = ('George Washington|John Adams|Thomas Jefferson|James Madison|James Monroe|'
    'John Quincy Adams|Andrew Jackson|Martin Van Buren|William Henry Harrison|John Tyler|'
    'James Polk|Zachary Taylor|Millard Fillmore|Franklin Pierce|James Buchanan|Abraham Lincoln|'
    'Andrew Johnson|Ulysses(?: S\\.)? Grant|Rutherford Hayes|James Garfield|Chester Arthur|'
    'Grover Cleveland|Benjamin Harrison|William McKinley|Theodore Roosevelt|William Howard Taft|'
    'Woodrow Wilson|Warren Harding|Calvin Coolidge|Herbert Hoover|Franklin(?: D\\.)? Roosevelt|'
    'Harry Truman|Dwight Eisenhower|John(?: F\\.)? Kennedy|Lyndon Johnson|Richard Nixon|'
    'Gerald Ford|Jimmy Carter|Ronald Reagan|George(?: H\\. W\\.| W\\.)? Bush|Bill Clinton|'
    'Barack Obama|Donald Trump|Joe Biden')
SPORT_ENTITIES = ('Tom Brady|Michael Jordan|LeBron James|Kobe Bryant|Pete Rose|Gilbert Arenas|'
    'Wayne Gretzky|Shaquille O.?Neal|Babe Ruth|Joe DiMaggio|Derek Jeter|Peyton Manning|'
    'New England Patriots|Green Bay Packers|Dallas Cowboys|Kansas City Chiefs|'
    'Los Angeles Lakers|Boston Celtics|Chicago Bulls|Golden State Warriors|'
    'New York Yankees|Boston Red Sox|Los Angeles Dodgers|Chicago Cubs|'
    'Toronto Maple Leafs|Montreal Canadiens|Detroit Red Wings|Pittsburgh Penguins')


def rule_matches(q, language):
    text = q['text']
    choices = q['choices']
    all_text = text + ' ' + ' '.join(choices)
    hits = []
    def match(pattern, haystack=text):
        return re.search(pattern, haystack, re.I)
    def add(outcome, rule, evidence):
        hits.append(assessment(outcome, [rule], evidence, 'deterministic_policy_screen'))
    if match(r'\b(?:NFL|NBA|MLB|NHL|NCAA|Super Bowl|Pro Bowl|World Series|Major League Baseball)\b', all_text) or match(r'\b(?:' + SPORT_ENTITIES + r")(?:s|'s|’s)?\b"):
        add('exclude', 'EU01', 'US league/college-sport context or associated entity identified.')
    if match(r'\bBroadway\b'):
        add('exclude', 'EU02', 'Broadway production/performer topic.')
    if match(r'\b(?:Saturday Night Live|SNL|Oprah|Ellen DeGeneres|The Tonight Show|Late Night|Late Show|Jimmy Kimmel|Jimmy Fallon|CBS|NBC|ABC|Fox News)\b'):
        add('exclude', 'EU03', 'US talk/late-night/channel topic.')
    if match(r'\b(?:' + PRESIDENTS + r")(?:s|'s|’s)?\b") or match(r'\b(?:US|U\.S\.|United States|American) president\b'):
        add('exclude', 'EU04', 'US president is part of the question subject, including possessive spellings.')
    if match(r'\b(?:state (?:motto|gemstone|bird|flower|nickname|capital)|US cities|U\.S\. state|US state|state of (?:Arkansas|Alabama|Texas|Ohio|Maine))\b'):
        add('exclude', 'EU05', 'US state/local identity or comparison knowledge.')
    if match(r'\b(?:country (?:music|singer|musician)|country-and-western)\b'):
        add('exclude', 'EU07', 'Country-music topic.')
    if match(r'\b(?:Pok[eé]mon|Guitar Hero)\b'):
        add('exclude', 'EU08', 'Explicitly excluded franchise.')
    if match(r'\b(?:pictured|shown (?:above|below|here)|sound clip|audio clip|listen to|this (?:is (?:the )?)?(?:victory )?theme|in the (?:picture|photo|video clip))\b'):
        add('exclude', 'Q04', 'Question appears to require absent media.')
    if match(r'\b(?:song|songs|lyrics?|single|singles|track|tracks|composition|compositions)\b') and (q['category'] == 'Music' or match(r'\b(?:singer|band|music|musical|composer|performed|sang|sung|lyrics?|composition)\b')):
        add('exclude', 'Q03', 'Song/recording/composition identification or detail without audio.')
    if all(re.fullmatch(r'(?:c\.?\s*)?(?:\d{1,4}(?:s)?|[IVXLC]+)(?:[–-](?:\d{1,4}|[IVXLC]+))?(?:\s*(?:BC|BCE|AD|CE|century|centuries|р\.?|року))?', c.strip(), re.I) for c in choices):
        is_date = bool(match(r'\b(?:year|date|century|centuries|decade|when)\b'))
        add('exclude' if is_date else 'hold', 'Q02', 'Four chronological choices.' if is_date else 'Four numerical/symbol choices require party-suitability review.')
    elif all(re.search(r'\d', c) and len(c.split()) <= 7 for c in choices):
        add('hold', 'Q02', 'Four numerical measurements, counts or ranges require review.')
    if match(r'\b(?:what number comes next|following sequence|correct solution|solution to this problem)\b'):
        add('hold', 'Q02', 'Calculation/sequence task requires party-suitability review.')
    if match(r'\b(?:how many|how long|how tall|how old|how much)\b'):
        add('hold', 'Q02', 'Numerical recall or measurement question requires party-suitability review.')
    if match(r'\b(?:episode|season [1-9]|season one|quest|middle name|first round pick)\b'):
        add('hold', 'Q01', 'Fan-level event/character/biographical detail requires review.')
    if match(r'\b(?:feet|foot rungs|miles|pounds|fahrenheit)\b'):
        add('hold', 'EU09' if language == 'en' else 'UA04', 'Incidental imperial units need European-unit review.')
    if language == 'uk' and match(r'\b(?:spelled|spelling|license plate|number plate|the English word|rhymes with|anagram)\b'):
        add('hold', 'UA03', 'English-dependent lexical clue requires Ukrainian semantic review.')
    return hits


def build():
    source = load('data/opentriviaqa/questions.json')
    translations = {q['id']: q for q in load('data/translations/uk.json')['questions']}
    human = {q['id']: q for q in load('data/editorial/eu-ua/review-decisions.json')['decisions']}
    english = {q['id']: q for q in load('data/editorial/eu-en/review-decisions.json')['decisions']}
    history = load('data/editorial/eu-evidence/prior-screening.json')['records']
    flags = {}
    for flag in load('data/editorial/eu-ua/quality-flags.json')['flags']:
        if flag['blocking'] and flag['status'] == 'pending':
            flags.setdefault(flag['id'], []).append(flag)
    # English source assessments of language-exempt records; no Ukrainian repair
    # is required for these, and audience/quality constraints were checked here.
    english_reassessments = {
        'otqa:0a86d73a5e3313b5f4f387c2': ('candidate', [], 'Shamrock identification: familiar Irish cultural reference; English wording usable.'),
        'otqa:09a304201733d3e8d7cedcfe': ('candidate', [], 'Hans Gruber: central villain of a broadly familiar film; original English names usable.'),
        'otqa:53d90d0aed07653ee690559b': ('candidate', [], 'Circus Maximus: major historical landmark; original English name usable.'),
        'otqa:23f7c2f220cd10fdd6bf0fc3': ('candidate', [], 'Little Prince central quotation/character: original English remains a draft for factual checking.'),
        'otqa:0c262cec679c9b567f9ad780': ('candidate', [], 'Penelope Cruz identification through prominent film credits; no Ukrainian-title gate in English.'),
        'otqa:03c5d7c34dce95f59627806e': ('candidate', [], 'Prominent ensemble-film identification; original English title choices remain usable.'),
    }
    records = []
    for q in source:
        qid = q['id']; h = fingerprint(q['text'], q['choices'])
        record = dict(id=qid, sourceHash=h)
        prior = history.get(qid)
        if prior and prior['sourceHash'] != h:
            raise ValueError('Stale historical evidence: ' + qid)
        for lang in ('en', 'uk'):
            r = human.get(qid)
            if r and r['source_hash'] != h:
                raise ValueError('Stale human review: ' + qid)
            if r:
                if lang == 'uk':
                    a = assessment({'Keep':'candidate','Exclude':'exclude','Revise':'hold','Unreviewed':'hold'}[r['decision']], ['REVIEW_OVERRIDE'], r['decision'] + ': ' + r['reason'], 'human_review')
                else:
                    e = english[qid]
                    a = assessment(e['englishOutcome'] if e['englishOutcome'] != 'reassess' else 'hold', ['REVIEW_OVERRIDE'], e['explanation'], 'projected_human_review')
                    if e['englishOutcome'] == 'reassess':
                        decision = english_reassessments.get(qid)
                        a = assessment(*decision, 'english_source_reassessment') if decision else assessment('hold', ['EN_REASSESS'], 'Translation-only block removed; shared English audience/source assessment still required.', 'english_source_reassessment')
            elif prior:
                # Prior screening considered Ukrainian wording. Only explicitly
                # language-scoped holds are exempted in English; never auto-pass.
                rules = prior['rules']
                if lang == 'en' and prior['outcome'] != 'candidate' and rules and all(rule in ('UA01','UA02','UA03') for rule in rules):
                    a = assessment('hold', ['EN_REASSESS'], 'Prior concern is Ukrainian-only; English shared-rule assessment still required.', 'historical_evidence_projection')
                else:
                    a = assessment(prior['outcome'], rules, prior['evidence'], 'historical_assisted_screening')
            else:
                a = assessment('hold', ['UNASSESSED'], 'No semantic EU audience assessment yet; not admitted by absence of keyword matches.', 'unassessed')
            # Explicit positive human decisions remain calibration overrides.
            # Known repair flags still apply separately in Ukrainian below.
            if not (r and r['decision'] == 'Keep'):
                hits = rule_matches(q, lang)
                if q['region'] == 'US':
                    hits.append(assessment('exclude', ['LEGACY_REGION'], 'Source explicitly tagged US; withheld from EU.', 'legacy_region'))
                if hits:
                    strongest = next((x for x in hits if x['outcome'] == 'exclude'), hits[0])
                    if a['outcome'] != 'exclude':
                        a = {**strongest, 'rules': sorted(set(rule for hit in hits for rule in hit['rules']))}
            if lang == 'uk':
                if qid not in translations:
                    a = assessment('hold', ['NO_TRANSLATION'], 'No retained Ukrainian translation; no English fallback.', 'translation_coverage')
                elif flags.get(qid) and a['outcome'] != 'exclude':
                    a = assessment('hold', ['UA_REPAIR'], '; '.join(f['note'] for f in flags[qid]), 'quality_flag')
                if qid in translations:
                    t = translations[qid]
                    a['translationHash'] = fingerprint(t['text'], t['choices'])
            record[lang] = a
        records.append(record)
    categories = sorted({q['category'] for q in source})
    byid = {q['id']: q for q in source}
    summary = {lang: dict(Counter(r[lang]['outcome'] for r in records)) for lang in ('en','uk')}
    coverage = {lang: {c: sum(r[lang]['outcome'] == 'candidate' and byid[r['id']]['category'] == c for r in records) for c in categories} for lang in ('en','uk')}
    return dict(schemaVersion=1, builderVersion=1, audience='Europe',
                status='conservative_draft_pools_not_independently_verified',
                policyVersions={'en':1,'uk':2},
                inputHashes={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in INPUTS},
                summary=summary, categoryCoverage=coverage, records=records)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--report-dir', type=Path)
    args = parser.parse_args()
    document = build()
    if args.check:
        if json.loads(OUTPUT.read_text()) != document:
            raise SystemExit('EU eligibility snapshot is stale; rebuild it.')
    else:
        OUTPUT.write_text(json.dumps(document, ensure_ascii=False, separators=(',', ':')) + '\n')
    if args.report_dir:
        args.report_dir.mkdir(parents=True, exist_ok=True)
        with (args.report_dir/'question-decisions.csv').open('w', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f); writer.writerow(['ID','Language','Outcome','Rules','Evidence','Origin'])
            for r in document['records']:
                for lang in ('en','uk'):
                    a=r[lang];writer.writerow([r['id'],lang,a['outcome'],','.join(a['rules']),a['evidence'],a['origin']])
        (args.report_dir/'summary.json').write_text(json.dumps({k:v for k,v in document.items() if k!='records'},ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'summary':document['summary'],'categories':document['categoryCoverage']},ensure_ascii=False))


if __name__ == '__main__':
    main()
