"""Separate, conservative Fun Bank v1: full English master minus requested gates."""
from pathlib import Path
from collections import Counter
import csv
import importlib.util
import json
import re

ROOT=Path(__file__).resolve().parents[1]
ARCHIVE=ROOT/'provided-916/TriviTV-EU-Filtered-Test/Server'
OUT=ROOT/'question-bank/fun-bank'
spec=importlib.util.spec_from_file_location('prior_rules',ARCHIVE/'scripts/build_eu_eligibility.py')
prior=importlib.util.module_from_spec(spec);spec.loader.exec_module(prior)
STATES='Alabama|Alaska|Arizona|Arkansas|California|Colorado|Connecticut|Delaware|Florida|Georgia|Hawaii|Idaho|Illinois|Indiana|Iowa|Kansas|Kentucky|Louisiana|Maine|Maryland|Massachusetts|Michigan|Minnesota|Mississippi|Missouri|Montana|Nebraska|Nevada|New Hampshire|New Jersey|New Mexico|New York|North Carolina|North Dakota|Ohio|Oklahoma|Oregon|Pennsylvania|Rhode Island|South Carolina|South Dakota|Tennessee|Texas|Utah|Vermont|Virginia|Washington|West Virginia|Wisconsin|Wyoming'
US=re.compile(r'\b(?:NFL|NBA|MLB|NHL|NCAA|American football|National Football League|National Basketball Association|National Hockey League|Major League Baseball|Super Bowl|World Series|Stanley Cup|Heisman|college football|college basketball|NASCAR|ESPN|Broadway|Saturday Night Live|SNL|Oprah|Ellen DeGeneres|Jimmy Fallon|Jimmy Kimmel|Jay Leno|David Letterman|Conan O.?Brien|CBS|NBC|Fox News|(?:US|U\.S\.|United States|American) (?:president|state|senat\w*|governor|congress\w*)|'+prior.PRESIDENTS+'|'+prior.SPORT_ENTITIES+r')\b',re.I)
STATE=re.compile(r'\b(?:'+STATES+r')\b',re.I)
CULTURE_CATEGORIES={'Arts & Humanities','Celebrities','Entertainment','Literature','Movies','Music','Television','Video Games'}
CULTURE_CUES=re.compile(r'\b(?:actor|actress|movie|film|cinema|singer|musician|album|band|sitcom|television|TV show|novel|novelist|poet|poem|author|playwright|song|lyrics|director|comedian|comic book|superhero|video game)\b',re.I)
YEAR=re.compile(r'\b(?:1[0-9]{3}|20[0-9]{2})(?:[sS]|[’\x27]s)?\b')
OLD=re.compile(r'\b19[5-8][0-9](?:s|[’\x27]s)?\b|\b(?:nineteen[- ](?:fifties|sixties|seventies|eighties)|1950s|1960s|1970s|1980s)\b',re.I)
DATE=re.compile(r'^(?:(?:c\.?|circa)\s*)?(?:\d{3,4}(?:\s*(?:BC|BCE|AD|CE))?|\d{4}\s*[-–/]\s*\d{2,4}|\d{1,2}[./-]\d{1,2}[./-]\d{2,4}|(?:\d{1,2}\s+)?(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)(?:\s+\d{1,2},?)?(?:\s+\d{4})?|\d{1,2}\s+(?:Jan\w*|Feb\w*|Mar\w*|Apr\w*|May|Jun\w*|Jul\w*|Aug\w*|Sep\w*|Oct\w*|Nov\w*|Dec\w*)(?:\s+\d{4})?|\d{3,4}s)$',re.I)


def multiple_item_choices(choices):
    # All four alternatives must contain a list separator; ordinary multiword
    # names such as New Zealand do not match. Ambiguous comma pairs are held.
    separator=re.compile(r'[,;]|\s+(?:and|&|та|і|й)\s+',re.I)
    return len(choices)==4 and all(len([v for v in separator.split(c) if v.strip()])>=2 for c in choices)

def classify(q):
    matches=[];text=q['text'];tags=q.get('tags',[])
    def add(rule,evidence,outcome='exclude'):matches.append({'rule':rule,'evidence':evidence,'outcome':outcome})
    senator=re.search(r'\b(?:senators?|senate|senatorial|congressmen|congresswomen)\b|сенатор\w*|сенат\w*',text+' '+' '.join(q['choices']),re.I)
    if senator:
        clearly_other=re.search(r'\b(?:ancient Rome|Roman senate|Roman senator|Canadian|Australian|French|Italian|Brazilian)\b',text,re.I)
        if not clearly_other:add('us-senators-and-senate',senator.group())
    if multiple_item_choices(q['choices']):add('multiple-item-answer-choices','All four English choices contain list separators.','hold')
    if q['category']=='Religion & Faith':add('religion-category','Source category is Religion & Faith.')
    date_context=bool(re.search(r'\b(?:year|date|when|century|decade|month|born|died|released|published|founded|established)\b',text,re.I))
    dates=[]
    for c in q['choices']:
        if not DATE.fullmatch(c.strip()):continue
        if re.fullmatch(r'\d{3,4}',c.strip()) and not date_context:continue
        if not re.search(r'\d',c) and not re.search(r'\bmonth\b',text,re.I):continue
        dates.append(c)
    # Numeric-looking book/film titles are ambiguous, not verified dates.
    if dates:
        numeric_title=q['category'] in CULTURE_CATEGORIES and re.search(r'\b(?:title|novel|book|film|movie|album|song)\b',text,re.I) and not re.search(r'\b(?:year|date|when|released|published|born|died)\b',text,re.I)
        add('date-or-year-answers','Date/year-looking option(s): '+' | '.join(dates),'hold' if numeric_title else 'exclude')
    us=US.search(text)
    existing=[t for t in tags if re.fullmatch(r'reason:eu:en:(?:us-.+|legacy-us-region-cue|broadway|country-music)',t)]
    if us or existing:add('us-specific',us.group() if us else 'Saved audience flags: '+', '.join(existing))
    # Heavy state/local gate; ambiguous common words require contextual evidence.
    state=STATE.search(text)
    if state:
        ambiguous=state.group().lower() in {'georgia','washington','new york'}
        if not ambiguous or re.search(r'\b(?:state|US|U\.S\.|American|United States|city|New York City|governor|county)\b',text,re.I):
            add('us-state-or-local',state.group())
        else:add('us-place-ambiguous',state.group(),'hold')
    if q['category'] in CULTURE_CATEGORIES or CULTURE_CUES.search(text):
        # A performer's birth date alone does not date the work referenced.
        era_text=re.sub(r'\b(?:born|birth|birthday)\b[^.;!?]{0,90}', '',text,flags=re.I)
        old=OLD.search(era_text)
        if old:add('culture-1950-1989',old.group())
        elif not YEAR.search(era_text):add('culture-era-unverified','No explicit work/era year in the prompt; manual or sourced entity-era check needed.','hold')
    # Strict Fun policy: content cuts plus unresolved Ukrainian localization holds.
    sem={t.removeprefix('custom:semantic:') for t in tags if t.startswith('custom:semantic:')}
    for tag in sorted(sem):
        if tag.startswith('translation-uk-risk:'):
            add('translation-risk',tag,'hold')
        if tag in {'audience:us-specific','subject:us-sports-leagues','subject:us-presidents','subject:us-states','topic:religion','form:wordplay','audience:specialist-knowledge','subject:song-lyrics','form:quote-identification','form:number-recall','form:date-recall'}:
            add('semantic-content-restriction',tag)
    if {'form:definition','topic:language'}<=sem:add('word-meaning','Language definition')
    if {'form:biography-detail','subject:celebrity-biography'}<=sem:add('celebrity-personal-detail','Biography detail + celebrity biography')
    if 'form:event-detail' in sem and sem & {'subject:oscars','subject:film-awards'}:add('award-detail','Award event detail')
    culture=sem & {'topic:movies','topic:television','topic:music','topic:books','topic:actors','topic:visual-art','topic:theatre','topic:comics','topic:animation','topic:radio','topic:video-games'}
    if culture and sem & {'era:1950s','era:1960s','era:1970s','era:1980s'}:add('semantic-old-culture',', '.join(sorted(culture | {t for t in sem if t.startswith('era:')})))
    if sem & {'entity-kind:movie-title','entity-kind:book-title'}:add('unverified-translated-title','Movie/book title requires Ukrainian title verification','hold')
    for tag in tags:
        if tag.startswith('reason:eu:uk:') and tag.split(':')[-1] in {'uk-word-meaning','uk-wordplay','uk-corrupt-translation','missing-media','wording-or-answer-quality','uk-repair-needed','uk-names-and-titles','uk-terminology','unit-localization'}:add('saved-uk-quality-hold',tag,'hold')
    if not any(t.startswith('topic:') for t in sem):add('unresolved-topic','No definite semantic topic','hold')
    outcome='exclude' if any(m['outcome']=='exclude' for m in matches) else 'hold' if matches else 'candidate'
    return {'id':q['id'],'category':q['category'],'outcome':outcome,'matches':matches}

def build():
    bank=json.loads((ROOT/'question-bank/questions.json').read_text(encoding='utf8'))
    translations={q['id']:q for q in json.loads((ARCHIVE/'data/translations/uk.json').read_text(encoding='utf8'))['questions']}
    audit_path=ROOT/'question-bank/semantic-tagging/luna-finish-v1/all-audit.json'
    audit={r['id']:r for r in json.loads(audit_path.read_text(encoding='utf8'))['records']}
    decisions=[]
    for q in bank:
        decision=classify(q)
        translated=translations.get(q['id'])
        if translated and multiple_item_choices(translated['choices']) and not any(m['rule']=='multiple-item-answer-choices' for m in decision['matches']):
            decision['matches'].append(dict(rule='multiple-item-answer-choices',evidence='All four Ukrainian choices contain list separators.',outcome='hold'))
            if decision['outcome']=='candidate':decision['outcome']='hold'
        for proposal in audit.get(q['id'],{}).get('proposals',[]):
            tag=proposal.get('tag') or proposal.get('family','')+':'+proposal.get('value','')
            if tag.startswith('translation-uk-risk:') or tag in {'entity-kind:movie-title','entity-kind:book-title'}:
                decision['matches'].append(dict(rule='uncertain-localization-review',evidence=tag,outcome='hold'))
                if decision['outcome']=='candidate':decision['outcome']='hold'
        decisions.append(decision)
    included={r['id'] for r in decisions if r['outcome']=='candidate'}
    questions=[{**q,'tags':sorted(set([t for t in q.get('tags',[]) if not t.startswith(('custom:fun-bank:','custom:fun-reason:'))]+['custom:fun-bank:candidate']))} for q in bank if q['id'] in included]
    linked=[translations[q['id']] for q in questions if q['id'] in translations]
    summary={'name':'Fun Bank','version':3,'language':'en','sourceCount':len(bank),'outcomes':dict(Counter(r['outcome'] for r in decisions)),'linkedUkrainianTranslations':len(linked),'matchedReasonsOverlapping':dict(Counter(m['rule'] for r in decisions for m in r['matches'])),'categories':dict(sorted(Counter(q['category'] for q in questions).items())),'method':'Strict v3: senator/senate questions and multi-item alternatives held out; original gates plus semantic content restrictions, all Ukrainian translation risks and unverified movie/book titles held. Not factual certification.','runtimeChanged':False}
    OUT.mkdir(parents=True,exist_ok=True)
    for filename,value in [('questions.en.json',questions),('translations.uk.json',{'language':'uk','linkedBy':'id','license':'CC-BY-SA-4.0','sourceRevision':'dcc1cdf36c2985ed5c849d1f2265c5041ffcdfb9','questions':linked}),('decisions.json',decisions),('summary.json',summary)]:
        (OUT/filename).write_text(json.dumps(value,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf8')
    with (OUT/'questions.en.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.writer(f);w.writerow(['id','category','question','A','B','C','D','correct_index','tags','translation_link'])
        for q in questions:w.writerow([q['id'],q['category'],q['text'],*q['choices'],q['correct'],json.dumps(q['tags'],ensure_ascii=False),'http://127.0.0.1:8791/?question='+q['id']])
    contributions={r['id']:['custom:fun-bank:'+r['outcome']]+['custom:fun-reason:'+m['rule'] for m in r['matches']] for r in decisions}
    (ROOT/'question-bank/tag-sources/fun-bank.json').write_text(json.dumps(contributions,separators=(',',':'))+'\n',encoding='utf8')
    assert sum(summary['outcomes'].values())==len(bank)
    assert all(q['category']!='Religion & Faith' for q in questions)
    assert all(t['id'] in included for t in linked)
    print(json.dumps(summary,ensure_ascii=False,indent=2))

if __name__=='__main__':build()
