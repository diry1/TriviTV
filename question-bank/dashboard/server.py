"""Loopback-only question-bank explorer and audited editorial overrides."""
import csv
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import io
import json
import importlib.util
import subprocess
import sys
import threading
import re
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parents[2]
WEB = Path(__file__).resolve().parent / 'dist'
MASTER = json.loads((ROOT/'question-bank/questions.json').read_text(encoding='utf-8'))
TRANSLATIONS = {q['id']:q for q in json.loads((ROOT/'provided-916/TriviTV-EU-Filtered-Test/Server/data/translations/uk.json').read_text(encoding='utf-8'))['questions']}
BY_ID = {q['id']:q for q in MASTER}
spec=importlib.util.spec_from_file_location('editorial',ROOT/'question-bank/editorial.py')
editorial=importlib.util.module_from_spec(spec);spec.loader.exec_module(editorial)
EDIT_LOCK=threading.Lock()
ORIGINALS={q['id']:q for q in json.loads((ROOT/'provided-916/TriviTV-EU-Filtered-Test/Server/data/opentriviaqa/questions.json').read_text(encoding='utf8'))}

def reload_bank():
    global MASTER,BY_ID,META
    MASTER=json.loads((ROOT/'question-bank/questions.json').read_text(encoding='utf8'))
    BY_ID={q['id']:q for q in MASTER}
    META=metadata()

def validate_edit(body):
    qid=body.get('id');current=BY_ID.get(qid)
    if not current:raise ValueError('Unknown question ID.')
    category=body.get('category') or None
    if category and category not in {q['category'] for q in ORIGINALS.values()}:raise ValueError('Choose a known category.')
    statuses=body.get('status',{})
    if not isinstance(statuses,dict) or any(k not in ('en','uk') or v not in ('candidate','hold','exclude') for k,v in statuses.items()):raise ValueError('Invalid review status.')
    if statuses.get('uk')=='candidate' and qid not in TRANSLATIONS:raise ValueError('Ukrainian inclusion requires a translation.')
    if statuses.get('uk')=='candidate' and 'rule:eu:uk:UA_CORRUPT_TRANSLATION' in current['tags']:raise ValueError('Repair the corrupted Ukrainian translation before including it.')
    if (category or ORIGINALS[qid]['category'])=='Religion & Faith' and 'candidate' in statuses.values():raise ValueError('Religion is excluded from EU pools by policy.')
    raw=body.get('tags',[])
    if not isinstance(raw,list) or len(raw)>50:raise ValueError('Use up to 50 personal tags.')
    tags=[]
    for tag in raw:
        if not isinstance(tag,str):raise ValueError('Tags must be text.')
        tag=tag.strip().lower()
        if not tag:continue
        if not tag.startswith('custom:manual:'):tag='custom:manual:'+re.sub(r'[^a-z0-9:_-]+','-',tag).strip('-')
        if not re.fullmatch(r'custom:manual:[a-z0-9][a-z0-9:_-]{0,90}',tag):raise ValueError('Use letters, numbers, dashes or colons in tags.')
        tags.append(tag)
    return qid,{'category':category,'status':statuses,'tags':sorted(set(tags))}

def state(q, lang):
    return next((t.rsplit(':',1)[1] for t in q['tags'] if t.startswith(f'screen:eu:{lang}:')), 'unknown')

def potential(q):
    return 'EU:uk' in q['tags'] or 'pool:eu-uk:potential-unassessed' in q['tags']

def select(params):
    get = lambda k,d='': params.get(k,[d])[0]
    sheet, search = get('sheet','main'), get('search').casefold().strip()
    required, excluded = params.get('tag',[]), params.get('without',[])
    lang = 'uk' if sheet == 'ua' else 'en'
    result = []
    for q in MASTER:
        t = q['tags']; uk = TRANSLATIONS.get(q['id'])
        if sheet == 'eu' and 'EU:en' not in t: continue
        if sheet == 'fun' and 'custom:fun-bank:candidate' not in t: continue
        if sheet == 'ua' and not uk: continue
        if get('category') and q['category'] != get('category'): continue
        if get('status') and state(q,lang) != get('status'): continue
        if get('pool') == 'potential' and not potential(q): continue
        if get('pool') == 'included' and f'EU:{lang}' not in t: continue
        if get('pool') == 'unassessed' and 'pool:eu-uk:potential-unassessed' not in t: continue
        if get('translation') == 'present' and not uk: continue
        if get('translation') == 'missing' and uk: continue
        if required and not (any(x in t for x in required) if get('match') == 'any' else all(x in t for x in required)): continue
        if any(x in t for x in excluded): continue
        text, choices = (uk['text'],uk['choices']) if lang == 'uk' and uk else (q['text'],q['choices'])
        if search and search not in (' '.join([q['id'],text,*choices,q['text'],*q['choices']])).casefold(): continue
        result.append({**q,'text':text,'choices':choices,'language':lang,'status':state(q,lang),'translationStatus':uk['status'] if uk else 'missing'})
    sort = get('sort','id')
    if sort in ('id','category','text'): result.sort(key=lambda q:q[sort].casefold())
    return result

def metadata():
    return {'counts':{'main':len(MASTER),'eu':sum('EU:en' in q['tags'] for q in MASTER),'fun':sum('custom:fun-bank:candidate' in q['tags'] for q in MASTER),'ua':len(TRANSLATIONS),'uaPotential':sum(potential(q) for q in MASTER)},'categories':sorted({q['category'] for q in ORIGINALS.values()}),'tags':sorted({t for q in MASTER for t in q['tags']})}
META=metadata()

class Handler(BaseHTTPRequestHandler):
    def send(self, body, mime='application/json; charset=utf-8', attachment=None):
        if not isinstance(body,bytes): body = body.encode('utf-8')
        self.send_response(200); self.send_header('Content-Type',mime)
        self.send_header('Content-Length',str(len(body))); self.send_header('Cache-Control','no-store')
        self.send_header('X-Content-Type-Options','nosniff')
        if attachment: self.send_header('Content-Disposition',f'attachment; filename="{attachment}"')
        self.end_headers(); self.wfile.write(body)

    def do_GET(self):
        url = urlparse(self.path); params = parse_qs(url.query)
        if url.path == '/api/meta': return self.send(json.dumps(META))
        if url.path == '/api/detail':
            q = BY_ID.get(params.get('id',[''])[0])
            if not q: return self.send_error(404)
            edits=editorial.load()
            return self.send(json.dumps({'source':q,'ukrainian':TRANSLATIONS.get(q['id']),'originalCategory':ORIGINALS[q['id']]['category'],'edit':edits['records'].get(q['id'],{}),'editRevision':edits['revision'],'editHistory':[e for e in edits['history'] if e['id']==q['id']]},ensure_ascii=False))
        if url.path in ('/api/questions','/api/export'):
            rows = select(params)
            if url.path == '/api/questions':
                try: page=max(1,int(params.get('page',['1'])[0])); size=min(100,max(10,int(params.get('size',['50'])[0])))
                except ValueError: return self.send_error(400)
                return self.send(json.dumps({'total':len(rows),'page':page,'size':size,'rows':rows[(page-1)*size:page*size]},ensure_ascii=False))
            sheet=params.get('sheet',['main'])[0]
            if params.get('format',['csv'])[0]=='json': return self.send(json.dumps(rows,ensure_ascii=False,indent=2),'application/json; charset=utf-8',f'trivitv-{sheet}-filtered.json')
            buffer=io.StringIO(newline=''); fields=['id','category','language','text','A','B','C','D','correct','status','tags','source_attribution','translation_link']
            w=csv.DictWriter(buffer,fieldnames=fields); w.writeheader()
            # Neutralize spreadsheet formulas in text cells when opening the CSV.
            safe=lambda s: "'"+s if s.lstrip().startswith(('=','+','-','@')) else s
            for q in rows: w.writerow({'id':q['id'],'category':q['category'],'language':q['language'],'text':safe(q['text']),**{c:safe(v) for c,v in zip('ABCD',q['choices'])},'correct':'ABCD'[q['correct']],'status':q['status'],'tags':json.dumps(q['tags'],ensure_ascii=False),'source_attribution':json.dumps(q['source'],ensure_ascii=False),'translation_link':'http://127.0.0.1:8791/?question='+q['id']})
            return self.send('\ufeff'+buffer.getvalue(),'text/csv; charset=utf-8',f'trivitv-{sheet}-filtered.csv')
        files={'/':'index.html','/app.js':'app.js','/style.css':'style.css'}
        if url.path not in files: return self.send_error(404)
        path=WEB/files[url.path]
        mime={'html':'text/html','js':'text/javascript','css':'text/css'}[path.suffix[1:]]
        self.send(path.read_bytes(),mime+'; charset=utf-8')

    def do_POST(self):
        if self.path!='/api/edit':return self.send_error(404)
        if self.headers.get('Origin')!='http://127.0.0.1:8791' or self.headers.get('Content-Type')!='application/json':return self.send_error(403)
        try:
            length=int(self.headers.get('Content-Length','0'))
            if not 0<length<=16384:raise ValueError('Invalid edit size.')
            body=json.loads(self.rfile.read(length));qid,edit=validate_edit(body)
        except (ValueError,TypeError,AttributeError) as error:
            return self.send(json.dumps({'error':str(error)}))
        if not EDIT_LOCK.acquire(blocking=False):return self.send(json.dumps({'error':'Another edit is being saved; retry shortly.'}))
        try:
            doc=editorial.load()
            if body.get('revision')!=doc['revision']:return self.send(json.dumps({'error':'This record is stale. Close and reopen the editor before saving.'}))
            doc['revision']+=1;before=doc['records'].get(qid,{})
            doc['records'][qid]=edit
            doc['history'].append({'id':qid,'at':datetime.now(timezone.utc).isoformat(),'revision':doc['revision'],'before':before,'after':edit})
            tmp=editorial.PATH.with_suffix('.tmp');tmp.write_text(json.dumps(doc,ensure_ascii=False,indent=2),encoding='utf8');tmp.replace(editorial.PATH)
            # Regenerate derived data, including category-sensitive Fun membership.
            for script in ('build-question-tags.py','build-fun-bank.py','build-question-tags.py'):
                result=subprocess.run([sys.executable,'-X','utf8',str(ROOT/'scripts'/script)],cwd=ROOT,capture_output=True,timeout=120)
                if result.returncode:raise RuntimeError('The edit was saved, but rebuilding derived files failed. Restart/rebuild is required.')
            reload_bank()
            self.send(json.dumps({'saved':True,'revision':doc['revision']}))
        except (RuntimeError,subprocess.TimeoutExpired,OSError) as error:
            self.send(json.dumps({'error':str(error)}))
        finally:EDIT_LOCK.release()

if __name__ == '__main__':
    print('TriviTV bank dashboard: http://127.0.0.1:8791',flush=True)
    ThreadingHTTPServer(('127.0.0.1',8791),Handler).serve_forever()
