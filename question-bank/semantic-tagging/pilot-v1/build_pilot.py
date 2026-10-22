"""Render and validate this fixed manually annotated pilot; no automatic classification."""
import argparse, collections, hashlib, html, importlib.util, json, re
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
BASE=HERE.parent
ALIASES=dict(t='topic',s='subject',f='form',y='style',a='audience',u='translation-uk-risk',e='entity-kind',l='location-mention',d='era')
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def canonical(value):return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'))
def fingerprint(value):return hashlib.sha256(canonical(value).encode()).hexdigest()
def dump(value):return json.dumps(value,ensure_ascii=False,indent=2)+'\n'
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');parser.add_argument('--publish',action='store_true');args=parser.parse_args()
    assert not(args.check and args.publish)
    sample=load(HERE/'sample.json');vocab=load(BASE/'vocabulary-v2.json')
    spec=importlib.util.spec_from_file_location('pilot_annotations',HERE/'annotations.py');annotations=importlib.util.module_from_spec(spec);spec.loader.exec_module(annotations)
    by_number={r['number']:r for r in annotations.ROWS}
    master=load(ROOT/'question-bank/questions.json');by_id={q['id']:q for q in master}
    translations={q['id']:q for q in load(ROOT/'provided-916/TriviTV-EU-Filtered-Test/Server/data/translations/uk.json')['questions']}
    reviews={q['id']:q for q in load(ROOT/'provided-916/TriviTV-EU-Filtered-Test/Server/data/editorial/eu-ua/review-decisions.json')['decisions']}
    assert len(sample)==len(by_number)==50 and len({q['id'] for q in sample})==50
    strata=collections.Counter(r['english']['category'] for r in sample if r['selection']=='category-stratum')
    assert len(strata)==20 and set(strata.values())=={2}
    audit=[];source={}
    for row in sample:
        n=row['number'];ann=by_number[n];q=by_id[row['id']];u=translations.get(q['id'])
        assert row['english']=={k:q[k] for k in ('category','text','choices','correct')},'Stale English sample'
        assert row['ukrainian']==u,'Stale translation sample'
        tags=[]
        for group in ann['tags'].split(';'):
            key,values=group.split('=');family=ALIASES[key]
            for value in values.split(','):
                assert (re.fullmatch(r'[0-9]{3}0s',value) if family=='era' else value in vocab['families'][family]),(n,family,value)
                assert family+':'+value not in vocab.get('deprecatedValues',{}),(n,value)
                tags.append('custom:semantic:'+family+':'+value)
        assert len(tags)==len(set(tags)) and len(tags)<=12
        assert any(':topic:' in t for t in tags)
        for entity in ann['entities']:
            role=entity['role'];text=q['text'] if role=='prompt' else q['choices'][int(role.split(':')[1])]
            assert entity['surface'] in text,(n,entity)
            if entity['kind'] in vocab['families']['entity-kind']:
                assert 'custom:semantic:entity-kind:'+entity['kind'] in tags,(n,entity)
            for region in entity['regions']:assert 'custom:semantic:location-mention:'+region in tags,(n,entity)
        for era in ann['eraRoles']:
            assert era['role'] in vocab['dynamicFamilies']['era']['roles']
            assert 'custom:semantic:era:'+era['value'] in tags
        assert len(ann['eraRoles'])==sum(':era:' in t for t in tags)
        assignments=[]
        for tag in sorted(tags):
            uk=':translation-uk-risk:' in tag
            assignments.append(dict(tag=tag,confidence='high',basis='source-and-linked-uk' if uk and u else 'source-content',evidenceRefs=['english.text','english.choices']+(['ukrainian.text','ukrainian.choices'] if uk and u else []),rationale=ann['rationale']))
        prior=reviews.get(q['id'])
        audit.append(dict(**row,sourceFingerprint=fingerprint({k:q[k] for k in ('id','text','choices','correct')}),translationFingerprint=fingerprint(u) if u else None,vocabularyVersion=2,tagSource='semantic-pilot-v1',method='manual-content-classification-and-second-consistency-pass',translationExamined=bool(u),assignments=assignments,entities=ann['entities'],eraRoles=ann['eraRoles'],issues=ann['issues'],proposals=ann['proposals'],priorReview={k:prior[k] for k in ('decision','reason','review_author')} if prior else None))
        source[q['id']]=sorted(tags)
    get=lambda n:set(source[sample[n-1]['id']])
    # Explicit regression contrasts from the manual consistency pass.
    for n in (14,17,23,34,37,43,50):assert 'custom:semantic:audience:us-specific' not in get(n)
    for n in (13,33,44,46):assert 'custom:semantic:audience:us-specific' in get(n)
    for n in (3,18,26,50):assert 'custom:semantic:location-mention:usa' not in get(n)
    for n in (6,48):assert not any(':audience:' in t for t in get(n))
    assert 'custom:semantic:era:1980s' not in get(46)
    assert 'custom:semantic:era:1950s' not in get(39)
    assert 'custom:semantic:form:negative-question' not in get(17)
    assert 'custom:semantic:form:negative-question' in get(47)
    assert not any(':location-mention:' in t for t in get(49))
    baseline=dict(records=len(master),contentAndOtherTagsSha256=fingerprint([{**q,'tags':[t for t in q['tags'] if not t.startswith('custom:semantic:')]} for q in master]),membershipCounts={tag:sum(tag in q['tags'] for q in master) for tag in ['EU','EU:en','EU:uk','custom:fun-bank:candidate']})
    if (HERE/'baseline.json').exists():assert load(HERE/'baseline.json')==baseline,'Content, eligibility or unrelated tags changed; inspect before refreshing baseline.'
    counts=collections.Counter(t for tags in source.values() for t in tags)
    summary=dict(sample=50,categoryStrata=40,targeted=10,categories=len(strata),linkedTranslations=sum(r['translationExamined'] for r in audit),assignments=sum(counts.values()),uniqueTags=len(counts),recordsWithProposals=sum(bool(r['proposals']) for r in audit),recordsWithNotes=sum(bool(r['issues']) for r in audit),priorReviewCounts=dict(collections.Counter(r['priorReview']['decision'] for r in audit if r['priorReview'])),tagCounts=dict(sorted(counts.items())),validation='Vocabulary, evidence spans, live fingerprints, source-owned tags, key cross-case contrasts and unchanged eligibility verified. No independent accuracy estimate or factual verification.')
    outputs={'audit.json':dump(dict(schemaVersion=1,date='2026-10-22',backendOnly=True,records=audit)),'summary.json':dump(summary),'baseline.json':dump(baseline)}
    esc=lambda x:html.escape(str(x))
    def choices(q,correct):return '<div class="choices">'+''.join('<div class="'+('correct' if i==correct else '')+'">'+esc(chr(65+i)+'. '+c)+(' ✓' if i==correct else '')+'</div>' for i,c in enumerate(q['choices']))+'</div>'
    cards=[]
    for r in audit:
        q=r['english'];u=r['ukrainian'];tags=source[r['id']]
        cards.append('<article id="q'+str(r['number'])+'"><h2>'+str(r['number'])+'. '+esc(q['category'])+'</h2><a href="http://127.0.0.1:8791/?question='+esc(r['id'])+'">'+esc(r['id'])+'</a><small>'+esc(r['selection'])+(' · prior '+esc(r['priorReview']['decision']) if r['priorReview'] else '')+'</small><div class="bilingual"><section><h3>English</h3><p>'+esc(q['text'])+'</p>'+choices(q,q['correct'])+'</section><section><h3>Українська · draft</h3><p>'+esc(u['text'] if u else 'No linked translation')+'</p>'+(choices(u,q['correct']) if u else '')+'</section></div><div class="tags">'+''.join('<span>'+esc(t.removeprefix('custom:semantic:'))+'</span>' for t in tags)+'</div><p>'+esc(by_number[r['number']]['rationale'])+'</p>'+('<ul class="notes">'+''.join('<li>'+esc(x)+'</li>' for x in r['issues'])+'</ul>' if r['issues'] else '')+('<details><summary>Unpublished proposals ('+str(len(r['proposals']))+')</summary><ul>'+''.join('<li>'+esc(x['family']+':'+x['value']+' — '+x['reason'])+'</li>' for x in r['proposals'])+'</ul></details>' if r['proposals'] else '')+'</article>')
    outputs['review.html']='<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Semantic tagging pilot · 50 questions</title><style>body{margin:0;background:#f3f6f3;color:#243c3b;font:16px/1.55 system-ui}main{max-width:1300px;margin:auto;padding:24px}article,header{background:white;border:1px solid #d7e2df;border-radius:12px;padding:24px;margin-bottom:20px}h1,h2,h3{margin:0 0 8px}h2{font-size:21px}small{display:block;color:#6a7977}.bilingual{display:grid;grid-template-columns:1fr 1fr;gap:24px}.choices{display:grid;gap:6px}.choices div{border:1px solid #dde5e3;border-radius:5px;padding:6px 10px}.choices .correct{background:#e4f2e9;border-color:#acd1b8}.tags{display:flex;flex-wrap:wrap;gap:6px;margin-top:20px}.tags span{background:#ecf1f6;color:#364e6c;border-radius:5px;padding:3px 8px;font-size:13px}.notes{color:#865d25}a{color:#19746e}details{border-top:1px solid #ddd;padding-top:10px}@media(max-width:750px){.bilingual{grid-template-columns:1fr}main{padding:10px}article{padding:16px}}</style><main><header><h1>Semantic tagging pilot</h1><p>50 questions · all 20 categories · '+str(summary['assignments'])+' assignments · '+str(summary['linkedTranslations'])+' linked Ukrainian drafts.</p><p>Two deterministic selections per category, plus ten targeted edge cases. This is a coverage/calibration sample, not a prevalence estimate or independent accuracy benchmark. Correct markers preserve original answer keys; they are not factual approval. Proposals are not active tags. Question-ID links open the local dashboard.</p></header>'+''.join(cards)+'</main></html>'
    for name,text in outputs.items():
        path=HERE/name
        if args.check:assert path.read_text(encoding='utf-8')==text,'Stale '+name
        else:path.write_text(text,encoding='utf-8')
    target=ROOT/'question-bank/tag-sources/semantic-pilot-v1.json'
    if args.publish:target.write_text(dump(source),encoding='utf-8')
    if args.check:
        assert load(target)==source,'Stale published source'
        for q in master:
            actual={t for t in q['tags'] if t.startswith('custom:semantic:')}
            if q['id'] in source:assert set(source[q['id']])<=actual,('Unmerged pilot semantic tags',q['id'])
    print(json.dumps({k:v for k,v in summary.items() if k!='tagCounts'},ensure_ascii=False))
if __name__=='__main__':main()
