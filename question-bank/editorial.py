"""Persistent editorial overrides; original imported question records stay intact."""
from pathlib import Path
import json
import re

ROOT=Path(__file__).resolve().parents[1]
PATH=ROOT/'question-bank/editorial-overrides.json'

def load():
    return json.loads(PATH.read_text(encoding='utf8')) if PATH.exists() else {'revision':0,'records':{},'history':[]}

def apply(q, edit, defaults):
    q={**q,'tags':list(q['tags'])};tags=set(q['tags'])
    if edit.get('category'):
        q['category']=edit['category']
        tags={t for t in tags if not t.startswith(('category:','difficulty:category-default:'))}
        tags.add('category:'+re.sub(r'[^a-z0-9]+','-',q['category'].lower()).strip('-'))
        tags.add('difficulty:category-default:'+str(defaults[q['category']]))
    for lang,outcome in edit.get('status',{}).items():
        tags={t for t in tags if not t.startswith(f'screen:eu:{lang}:')}
        tags.add(f'screen:eu:{lang}:{outcome}')
        tags.add(f'custom:manual:reviewed-{lang}')
        tags.discard(f'EU:{lang}')
        tags={t for t in tags if not t.startswith(f'pool:eu-{lang}:')}
        if outcome=='candidate':tags.add(f'EU:{lang}')
    if q['category']=='Religion & Faith':
        tags.discard('EU:en');tags.discard('EU:uk')
        tags={t for t in tags if not t.startswith(('pool:eu-en:','pool:eu-uk:','screen:eu:en:','screen:eu:uk:'))}
        tags.update(['screen:eu:en:exclude','screen:eu:uk:exclude'])
    tags.discard('EU')
    if 'EU:en' in tags or 'EU:uk' in tags:tags.add('EU')
    tags.update(edit.get('tags',[]))
    q['tags']=sorted(tags)
    return q
