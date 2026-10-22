"""Build the complete English editorial master with backend-only tags."""
import argparse
from collections import Counter
import contextlib
import csv
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import re
import runpy
editorial_spec=importlib.util.spec_from_file_location('editorial',Path(__file__).resolve().parents[1]/'question-bank/editorial.py')
editorial=importlib.util.module_from_spec(editorial_spec);editorial_spec.loader.exec_module(editorial)

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / 'provided-916/TriviTV-EU-Filtered-Test/Server'
OUT = ROOT / 'question-bank'
RULES = {
    'LEGACY_REGION': 'legacy-us-region-cue', 'EU01': 'us-sports',
    'EU02': 'broadway', 'EU03': 'us-tv-and-broadcasting', 'EU04': 'us-presidents',
    'EU05': 'us-local-knowledge', 'EU06': 'us-local-culture-and-brands',
    'EU07': 'country-music', 'EU08': 'excluded-franchise',
    'Q01': 'obscure-or-specialist', 'Q02': 'numeric-choices-or-calculation',
    'Q03': 'song-identification-or-detail', 'Q04': 'missing-media',
    'Q05': 'wording-or-answer-quality', 'Q06': 'category-mismatch',
    'UA01': 'uk-terminology', 'UA02': 'uk-names-and-titles',
    'UA03': 'uk-wordplay', 'UA04': 'unit-localization',
    'EU09': 'unit-localization', 'UA_REPAIR': 'uk-repair-needed',
    'OLD_MEDIA_REVIEW': 'older-entertainment', 'AGE_REVIEW': 'sensitive-content',
    'NEW_RELIGION_CATEGORY': 'religion-category',
    'NEW_UA_WORD_MEANING': 'uk-word-meaning',
    'REVIEW_OVERRIDE': 'saved-editorial-decision', 'UNASSESSED': 'unassessed',
    'NO_TRANSLATION': 'uk-translation-missing', 'EN_REASSESS': 'english-reassessment',
    'UA_CORRUPT_TRANSLATION': 'uk-corrupt-translation',
}

def slug(value):
    return re.sub(r'[^a-z0-9]+', '-', value.lower()).strip('-')

def merge_sources(source_tags):
    """Rebuild rather than union with last output, so removed tags disappear."""
    return sorted({tag for tags in source_tags.values() for tag in tags})

def eu_tags(en, uk):
    return (['EU'] if en or uk else []) + (['EU:en'] if en else []) + (['EU:uk'] if uk else [])

# English is a subtractive pool: lack of prior assessment does not remove it.
# Localization-only blocks remain in the Ukrainian evidence, not English filters.
EN_NONBLOCKING = {'UNASSESSED','EN_REASSESS','NO_TRANSLATION','UA01','UA02','UA03','UA04','UA_REPAIR','EU09'}

def english_filters(q, assessment, fresh_hits, human_keep=False):
    rules = set(assessment['rules']) if assessment['outcome'] != 'candidate' else set()
    if not human_keep:
        for hit in fresh_hits:
            rules.update(hit['rules'])
    rules -= EN_NONBLOCKING
    if q['category'] == 'Religion & Faith':
        rules.add('NEW_RELIGION_CATEGORY')
    return sorted(rules)

def apply_extra(contributions, files):
    for path, doc in files:
        owner = 'custom:' + path.stem
        for qid, tags in doc.items():
            if qid not in contributions:
                raise ValueError(f'Unknown question ID in {path.name}: {qid}')
            if not isinstance(tags, list) or any(not isinstance(t, str) or not re.fullmatch(r'custom:[a-z0-9][a-z0-9:_-]*', t) for t in tags):
                raise ValueError(f'Custom tags must use custom: namespace: {path.name}/{qid}')
            contributions[qid][owner] = sorted(set(tags))

def build():
    # Refresh the preliminary screen from the saved source and current notes.
    with contextlib.redirect_stdout(io.StringIO()):
        runpy.run_path(str(ROOT / 'scripts/screen-ukrainian-candidates.py'))
    spec = importlib.util.spec_from_file_location('saved_screen', ARCHIVE / 'scripts/build_eu_eligibility.py')
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    eligibility = module.build()
    records = {r['id']: r for r in eligibility['records']}
    source = module.load('data/opentriviaqa/questions.json')
    category_difficulty = json.loads((ROOT / 'game-rules/category-difficulty.json').read_text(encoding='utf-8'))
    translations = {q['id']: q for q in module.load('data/translations/uk.json')['questions']}
    reviews = {q['id']: q for q in module.load('data/editorial/eu-ua/review-decisions.json')['decisions']}
    screen_path = ROOT / 'artifacts/question-bank-screen-2026-10-21/decisions.csv'
    with screen_path.open(encoding='utf-8-sig', newline='') as f:
        screened = {r['id']: r for r in csv.DictReader(f)}
    contributions, provenance = {}, {}
    for q in source:
        qid = q['id']; row = records[qid]; s = screened.get(qid)
        en_blocks = english_filters(q, row['en'], module.rule_matches(q,'en'), reviews.get(qid,{}).get('decision') == 'Keep')
        en = not en_blocks
        uk = s is not None and s['status'] == 'previously_screened_draft'
        base = ['source:opentriviaqa', 'category:' + slug(q['category']), 'difficulty:unrated', 'verification:not-fact-checked']
        base.extend(['difficulty:category-default:' + str(category_difficulty[q['category']]), 'difficulty:method:category-estimate'])
        base.append('translation:uk:' + (translations[qid]['status'] if qid in translations else 'missing'))
        auto = eu_tags(en, uk)
        if en:
            auto.append('pool:eu-en:' + ('previously-screened' if row['en']['outcome'] == 'candidate' else 'potential-unassessed'))
        if s and s['status'] == 'unassessed_potential':
            auto.append('pool:eu-uk:potential-unassessed')
        evidence = {}
        for lang in ('en', 'uk'):
            a = row[lang]
            outcome = a['outcome']
            if lang == 'en':
                outcome = ('exclude' if row['en']['outcome'] == 'exclude' or 'NEW_RELIGION_CATEGORY' in en_blocks else 'hold') if en_blocks else ('candidate' if a['outcome'] == 'candidate' else 'hold')
            if q['category'] == 'Religion & Faith':
                outcome = 'exclude'
            if lang == 'uk' and s and s['status'] == 'filtered_or_held' and a['outcome'] == 'candidate':
                outcome = 'hold'
            auto.append(f'screen:eu:{lang}:{outcome}')
            for rule in a['rules']:
                if lang == 'en' and rule in EN_NONBLOCKING and rule != 'UNASSESSED':
                    continue
                auto.append(f'rule:eu:{lang}:{rule}')
                if rule in RULES and a['outcome'] != 'candidate':
                    auto.append(f'reason:eu:{lang}:' + RULES[rule])
            evidence[lang] = a
        for rule in en_blocks:
            auto.extend([f'rule:eu:en:{rule}', 'reason:eu:en:' + RULES.get(rule,slug(rule))])
        if q['category'] == 'Religion & Faith':
            for lang in ('en','uk'):
                auto.extend([f'rule:eu:{lang}:NEW_RELIGION_CATEGORY', f'reason:eu:{lang}:religion-category'])
        if s and 'NEW_UA_WORD_MEANING' in s['rules'].split('|'):
            auto.extend(['rule:eu:uk:NEW_UA_WORD_MEANING', 'reason:eu:uk:uk-word-meaning'])
        if s and 'UA_CORRUPT_TRANSLATION' in s['rules'].split('|'):
            auto.extend(['rule:eu:uk:UA_CORRUPT_TRANSLATION', 'reason:eu:uk:uk-corrupt-translation'])
        if qid in reviews:
            auto.append('review:eu:uk:' + reviews[qid]['decision'].lower())
        contributions[qid] = {'source-metadata': base, 'editorial-screen': auto}
        provenance[qid] = {'eligibilityEvidence': evidence, 'preliminaryUkScreen': s, 'englishPool': {'included': en, 'blockingRules': en_blocks, 'method': 'main-minus-content-and-audience-filters'}}
    extra = [(p, json.loads(p.read_text(encoding='utf-8'))) for p in sorted((OUT / 'tag-sources').glob('*.json'))]
    apply_extra(contributions, extra)
    master = [{**q, 'tags': merge_sources(contributions[q['id']])} for q in source]
    edits=editorial.load()['records']
    master=[editorial.apply(q,edits.get(q['id'],{}),category_difficulty) for q in master]
    for qid,edit in edits.items():
        if qid in provenance:provenance[qid]['editorialOverride']=edit
    counts = dict(sorted(Counter(tag for q in master for tag in q['tags']).items()))
    audit = {'schemaVersion': 1, 'backendOnly': True, 'records': {qid: {'sources': sources, **provenance[qid]} for qid, sources in contributions.items()}}
    summary = {'questions': len(master), 'tagCounts': counts, 'eligibilityMeaning': 'English EU is main minus audience/content filters, including unassessed survivors. Ukrainian EU tags remain screened draft membership. Neither is factual approval or deployed membership.', 'sourceSha256': hashlib.sha256((ARCHIVE / 'data/opentriviaqa/questions.json').read_bytes()).hexdigest()}
    return source, master, audit, summary

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    source, master, audit, summary = build()
    assert len(master) == 38926 and len({q['id'] for q in master}) == len(master)
    for original,effective in zip(source,master):
        assert {k:v for k,v in effective.items() if k not in ('tags','category')} == {k:v for k,v in original.items() if k!='category'}
    assert all(('EU' in q['tags']) == any(t in q['tags'] for t in ['EU:en','EU:uk']) for q in master)
    assert all('EU' not in q['tags'] for q in master if q['category'] == 'Religion & Faith')
    outputs = {'questions.json': master, 'tag-provenance.json': audit, 'tag-summary.json': summary}
    buffer = io.StringIO(newline='')
    fields = ['id','category','text','choice_a','choice_b','choice_c','choice_d','correct_index','tags']
    writer = csv.DictWriter(buffer, fieldnames=fields); writer.writeheader()
    for q in master:
        writer.writerow({'id':q['id'],'category':q['category'],'text':q['text'], **dict(zip(fields[3:7],q['choices'])), 'correct_index':q['correct'], 'tags':json.dumps(q['tags'],ensure_ascii=False,separators=(',',':'))})
    serialized = {name: json.dumps(value,ensure_ascii=False,separators=(',',':'))+'\n' for name,value in outputs.items()}
    serialized['questions.csv'] = '\ufeff' + buffer.getvalue()
    for name, text in serialized.items():
        path = OUT / name
        if args.check:
            if not path.exists() or path.read_bytes() != text.encode('utf-8'):
                raise SystemExit(f'Stale tagged bank: {name}; rebuild required.')
        else:
            path.write_bytes(text.encode('utf-8'))
    print(json.dumps({'questions':len(master),'EU':summary['tagCounts'].get('EU',0),'EU:en':summary['tagCounts'].get('EU:en',0),'EU:uk':summary['tagCounts'].get('EU:uk',0),'check':args.check}))

if __name__ == '__main__':
    main()
