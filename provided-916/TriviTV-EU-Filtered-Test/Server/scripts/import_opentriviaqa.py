"""Build a deterministic, source-attributed OpenTriviaQA snapshot. No network access."""
from pathlib import Path
import argparse
import collections
import hashlib
import html
import json
import re
import unicodedata

ROOT = Path(__file__).resolve().parents[1]
BANK = ROOT / 'data/opentriviaqa'
# These are conservative prompt cues, not editorially verified regional tags.
EUROPE = r'\b(?:Europe|European|Britain|British|United Kingdom|England|Scotland|Scottish|Wales|Welsh|Ireland|Irish|France|French|Germany|German|Italy|Italian|Spain|Spanish|Portugal|Portuguese|Belgium|Belgian|Netherlands|Dutch|Denmark|Danish|Sweden|Swedish|Norway|Norwegian|Finland|Finnish|Iceland|Icelandic|Austria|Austrian|Switzerland|Swiss|Poland|Polish|Hungary|Hungarian|Romania|Romanian|Bulgaria|Bulgarian|Greece|Greek|Ukraine|Ukrainian|Czech|Slovakia|Slovenia|Croatia|Estonia|Latvia|Lithuania|Luxembourg|London|Paris|Rome|Berlin|Madrid|Lisbon|Vienna|Budapest|Athens|Danube|Thames|Seine|Eurovision|Wimbledon)\b'
US = r'\b(?:United States|U\.S\.|USA|(?<!South )(?<!North )American|California|Texas|Florida|New York|Los Angeles|Chicago|Washington|Boston|Philadelphia|Seattle|Alaska|Hawaii|NFL|NBA|MLB|NHL|Super Bowl|World Series|Potomac|Hollywood|White House|US president|U\.S\. president)\b'
META = re.compile(r'\b(?:all|none|both) (?:of )?(?:the above|the answers|the choices|the options|these|those|them)\b|\b(?:the )?(?:first|last) (?:two|three)\b|\bboth [a-f] and [a-f]\b|\b[ABCDEF] (?:and|or) [ABCDEF]\b', re.I)
TIME_SENSITIVE = re.compile(r'\b(?:currently|current|today|nowadays|most recent|latest|this year|last year|how old is|present president)\b', re.I)
MEDIA = re.compile(r'\b(?:pictured|shown (?:here|above|below)|in (?:this|the) (?:picture|photo|image)|listen to (?:this|the))\b', re.I)

def clean(text):
    text = html.unescape(text)
    text = re.sub(r'</?[A-Za-z][^>]*>', ' ', text)
    return ' '.join(unicodedata.normalize('NFKC', text).split()).strip()

def key(text):
    return re.sub(r'[^\w]+', ' ', clean(text).casefold()).strip()

def parse(text, filename):
    records = []
    record = None
    for line_no, line in enumerate(text.splitlines(), 1):
        line = line.strip()
        if line.startswith('#Q'):
            if record: records.append(record)
            record = {'text': line[2:].strip(), 'answers': [], 'choices': [], 'line': line_no, 'file': filename, 'record': len(records) + 1}
        elif record and line.startswith('^'):
            record['answers'].append(line[1:].strip())
        elif record and re.match(r'^[A-Z]\s+', line):
            record['choices'].append(re.sub(r'^[A-Z]\s+', '', line))
        elif record and line and not line.startswith('#'):
            record.setdefault('unparsed', []).append(line)
    if record: records.append(record)
    return records

def normalize(record):
    source_text = ' '.join([record['text'], *record['answers'], *record['choices']])
    if any(0xDC80 <= ord(c) <= 0xDCFF for c in source_text) or re.search(r'[\x80-\x9f]|â€|Ã[\x80-\xff]', source_text): return None, 'invalid-source-encoding'
    prompt = clean(record['text'])
    choices = [clean(c) for c in record['choices']]
    if record.get('unparsed'): return None, 'unparsed-lines'
    if len(record['answers']) != 1: return None, 'answer-count'
    correct = clean(record['answers'][0])
    if not prompt or not correct: return None, 'empty-text'
    if not 10 <= len(prompt) <= 320 or any(not c or len(c) > 120 for c in choices): return None, 'tv-length'
    if len(choices) < 4: return None, 'fewer-than-four-choices'
    if len({key(c) for c in choices}) != len(choices): return None, 'duplicate-choices'
    matches = [c for c in choices if key(c) == key(correct)]
    if len(matches) != 1: return None, 'answer-not-in-choices'
    if META.search(prompt) or any(META.search(c) for c in choices): return None, 'position-dependent-options'
    if TIME_SENSITIVE.search(prompt): return None, 'time-sensitive'
    if MEDIA.search(prompt): return None, 'missing-media'
    wrong = [c for c in choices if key(c) != key(correct)]
    # Keep four source-supplied choices, never fabricate distractors.
    return {'text': prompt, 'choices': [matches[0], *wrong[:3]], 'correct': 0}, None

def region(prompt):
    eu, us = bool(re.search(EUROPE, prompt, re.I)), bool(re.search(US, prompt, re.I))
    if eu and not us: return 'Europe'
    if us and not eu: return 'US'
    return 'Unclassified'

def build(source, config):
    records = []
    hashes = {}
    for filename in sorted(config['categoryMap']):
        path = source / filename
        raw = path.read_bytes()
        hashes[filename] = hashlib.sha256(raw).hexdigest()
        text = raw.decode('utf-8', errors='surrogateescape')
        records.extend(parse(text, filename))
    if hashes != config['sourceHashes']: raise ValueError('Source checksums differ from the pinned snapshot; verify the upstream revision before updating config.')
    grouped = collections.defaultdict(list)
    rejected = []
    for record in records:
        question, reason = normalize(record)
        if reason:
            rejected.append({'file': record['file'], 'record': record['record'], 'line': record['line'], 'reason': reason})
        else:
            grouped[key(question['text'])].append((record, question))
    questions = []
    duplicates = 0
    for group in grouped.values():
        if len({key(q['choices'][0]) for _, q in group}) > 1:
            for record, _ in group: rejected.append({'file': record['file'], 'record': record['record'], 'line': record['line'], 'reason': 'conflicting-correct-answers'})
            continue
        # Preserve real topic categories over overlapping/newest/rated collections.
        group.sort(key=lambda entry: (entry[0]['file'] in ('newest', 'rated', 'general', 'world'), entry[0]['file']))
        record, question = group[0]
        duplicates += len(group) - 1
        identity = key(question['text']) + '|' + key(question['choices'][0])
        questions.append({
            'id': 'otqa:' + hashlib.sha256(identity.encode()).hexdigest()[:24],
            'category': config['categoryMap'][record['file']],
            'sourceCategories': sorted({r['file'] for r, _ in group}),
            'region': region(question['text']), 'regionMethod': 'prompt-keywords-v1',
            'difficulty': None, 'reviewStatus': 'structurally-validated-only',
            **question,
            'source': {'name': 'OpenTriviaQA', 'revision': config['revision'], 'license': config['license'],
                       'records': [{'file': r['file'], 'record': r['record'], 'line': r['line']} for r, _ in group]}
        })
    questions.sort(key=lambda q: q['id'])
    category_counts = dict(sorted(collections.Counter(q['category'] for q in questions).items()))
    summary = {'source': config, 'sourceHashes': hashes, 'sourceRecordCount': len(records),
               'questionCount': len(questions), 'duplicateRecordsMerged': duplicates,
               'rejectedCount': len(rejected), 'rejectionCounts': dict(sorted(collections.Counter(r['reason'] for r in rejected).items())),
               'categories': category_counts, 'regions': dict(sorted(collections.Counter(q['region'] for q in questions).items())),
               'difficulty': 'Not provided by OpenTriviaQA; no ratings have been invented.',
               'modifications': ['HTML entities decoded, markup/whitespace normalized', 'Duplicate questions merged; conflicting keys excluded', 'Four choices retained from source; extra distractors omitted', 'Category labels normalized; newest/rated treated as collections', 'Conservative prompt keyword regions; unclassified shared between audiences', 'Unrated difficulty and unreviewed factual accuracy disclosed']}
    assert len(records) == len(questions) + duplicates + len(rejected)
    return questions, summary, rejected

def render(source):
    config = json.loads((BANK / 'config.json').read_text())
    if hashlib.sha256((BANK / 'LICENSE.txt').read_bytes()).hexdigest() != config['licenseSha256']: raise ValueError('Pinned source license checksum mismatch.')
    questions, summary, rejected = build(source, config)
    return {'questions.json': json.dumps(questions, ensure_ascii=False, separators=(',', ':')) + '\n',
            'manifest.json': json.dumps(summary, ensure_ascii=False, indent=2) + '\n',
            'rejections.json': json.dumps(rejected, ensure_ascii=False, separators=(',', ':')) + '\n'}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=BANK / 'source')
    parser.add_argument('--check', action='store_true', help='Verify outputs match the retained pinned source, without writing files.')
    args = parser.parse_args()
    for name, content in render(args.source).items():
        path = BANK / name
        if args.check:
            if not path.exists() or path.read_text() != content: raise SystemExit(f'Out of date: {path}')
        else: path.write_text(content, encoding='utf-8', newline='\n')
    summary = json.loads((BANK / 'manifest.json').read_text())
    print(json.dumps({k: summary[k] for k in ['sourceRecordCount', 'questionCount', 'duplicateRecordsMerged', 'rejectedCount', 'categories', 'regions']}, indent=2))

if __name__ == '__main__': main()
