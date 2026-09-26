#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dataset validation — Nile Pearl Hotel AI Voice System

Run from the project root:

    python3 06_Scripts/validation/validate_dataset.py

Exit code 0 means every check passed. Run it again after any edit to the data; it is the
regression test for this dataset. Nothing outside this folder is required.
"""
import csv, json, os, re, sys
from collections import Counter, defaultdict

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
results = []

def check(name, ok, detail=''):
    results.append((name, ok, detail))
    print(f"  {'PASS' if ok else 'FAIL'}  {name}" + (f"  — {detail}" if detail else ''))

def read(rel, enc='utf-8-sig'):
    with open(os.path.join(BASE, rel), encoding=enc) as f:
        return list(csv.DictReader(f))

def jsonl(rel):
    with open(os.path.join(BASE, rel), encoding='utf-8') as f:
        return [json.loads(l) for l in f if l.strip()]

# language detection by script
AR  = re.compile(r'[\u0600-\u06FF]')
CYR = re.compile(r'[\u0400-\u04FF]')
FR  = set("àâäçèéêëîïôùûüœæÀÂÄÇÈÉÊËÎÏÔÙÛÜŒÆ")

def detect(t):
    if AR.search(t):  return 'Arabic'
    if CYR.search(t): return 'Russian'
    if any(c in FR for c in t): return 'French'
    return 'Latin'

def lang_ok(t, d):
    x = detect(t)
    if d in ('Arabic', 'Arabic-Egyptian'): return x == 'Arabic'
    if d == 'Russian': return x == 'Russian'
    if d == 'French':  return x in ('French', 'Latin')
    if d == 'English': return x == 'Latin'
    return False

print('=' * 78)
print('DATASET VALIDATION — Nile Pearl Hotel AI Voice System')
print('=' * 78)

MASTER = '02_Data/04_Gold/hotel_faq_gold.csv'
m = read(MASTER)

# ── 1. master file ──────────────────────────────────────────────────────────
print(f'\n[1] Master FAQ file — {len(m)} rows')
REQUIRED = ['faq_id','intent_id','intent_name','language','question_type','question',
            'answer','status','category','source','origin','response_mode','requires_tool']
check('all required columns present', set(REQUIRED) <= set(m[0].keys()),
      f'missing: {sorted(set(REQUIRED) - set(m[0].keys()))}')
ids = [r['faq_id'] for r in m]
check('every faq_id unique', len(set(ids)) == len(ids), f'{len(set(ids))} unique')
nums = sorted(int(i[3:]) for i in ids)
gaps = [b for a, b in zip(nums, nums[1:]) if b != a + 1]
check('faq_id sequence continuous', not gaps,
      f'{len(gaps)} gaps, FAQ{nums[0]}-FAQ{nums[-1]}')
qs = [r['question'].strip().lower() for r in m]
check('no duplicate questions', len(set(qs)) == len(qs), f'{len(qs)-len(set(qs))} duplicates')
empty = [r['faq_id'] for r in m if not r['question'].strip() or not r['answer'].strip()]
check('no empty questions or answers', not empty, f'{len(empty)} empty')
short = [r['faq_id'] for r in m if len(r['answer'].strip()) < 15]
check('no stub answers', not short, f'{len(short)} under 15 chars')

# ── 2. language ─────────────────────────────────────────────────────────────
print('\n[2] Language')
core = Counter(r['language'] for r in m if r['language'] != 'Arabic-Egyptian')
ratio = max(core.values()) / min(core.values())
check('four project languages within 1.10x', ratio <= 1.10,
      f'max/min = {ratio:.3f}  {dict(sorted(core.items()))}')
bad_q = [r['faq_id'] for r in m if not lang_ok(r['question'], r['language'])]
bad_a = [r['faq_id'] for r in m if not lang_ok(r['answer'], r['language'])]
check('question written in its declared language', not bad_q, f'{len(bad_q)} mismatched')
check('answer written in its declared language', not bad_a, f'{len(bad_a)} mismatched')
egy = sum(1 for r in m if r['language'] == 'Arabic-Egyptian')
print(f'      Egyptian dialect seed: {egy} rows (counted separately by design)')

# ── 3. routing columns ──────────────────────────────────────────────────────
print('\n[3] Routing columns')
modes = Counter(r['response_mode'] for r in m)
check('response_mode populated on every row',
      all(r['response_mode'].strip() for r in m), f'{dict(modes)}')
check('requires_tool is boolean',
      all(r['requires_tool'] in ('True','False') for r in m),
      f"{dict(Counter(r['requires_tool'] for r in m))}")
oos = [r for r in m if r['origin'] == 'out_of_scope_100']
check('out-of-scope layer present', len(oos) == 100, f'{len(oos)} rows')
check('out-of-scope balanced across languages',
      len(set(Counter(r['language'] for r in oos).values())) == 1,
      f"{dict(Counter(r['language'] for r in oos))}")

# ── 4. knowledge base ───────────────────────────────────────────────────────
print('\n[4] Knowledge base')
KB = os.path.join(BASE, '03_Knowledge_Base')
docs = sorted(f for f in os.listdir(KB) if f.endswith('.txt'))
check('all knowledge documents present', len(docs) == 44, f'{len(docs)} files')
bad_hdr = [d for d in docs
           if not open(os.path.join(KB, d), encoding='utf-8').read().startswith('NILE PEARL HOTEL')]
check('all use the NILE PEARL HOTEL header', not bad_hdr, f'{bad_hdr}')

SEC = re.compile(r'^\s*(\d+)\.\s+(.+?)\s*$')
sections = {d: (len([1 for l in open(os.path.join(KB, d), encoding='utf-8')
                     if SEC.match(l)]) or 1) for d in docs}
srcs = {r['source'] for r in m}
uncovered = [d for d in docs if d not in srcs]
check('every document has FAQ coverage', not uncovered,
      f'{len(docs)-len(uncovered)}/{len(docs)} covered' + (f' — missing {uncovered}' if uncovered else ''))
print(f'      {sum(sections.values())} sections across {len(docs)} documents')

# ── 5. room inventory consistency ───────────────────────────────────────────
print('\n[5] Room inventory consistency')
rt = read('02_Data/02_Operational/room_types.csv')
db_rooms = {r['room_type_name'].strip() for r in rt}
db_caps  = {r['room_type_name'].strip(): int(r['capacity']) for r in rt}
print(f'      database: {sorted(db_rooms)}')
GHOST = ('Standard Room', 'Superior Room', 'Executive Room')
ghost_docs = [d for d in docs
              if any(g in open(os.path.join(KB, d), encoding='utf-8').read() for g in GHOST)]
check('no knowledge document lists a non-existent room type', not ghost_docs, f'{ghost_docs}')
ghost_rows = [r['faq_id'] for r in m
              if r['origin'] != 'original_1344' and any(g in r['answer'] for g in GHOST)]
check('no answer mentions a non-existent room type', not ghost_rows, f'{len(ghost_rows)} rows')

# capacities stated in the knowledge base must match the database
cap_txt = open(os.path.join(KB, 'room_policies.txt'), encoding='utf-8').read()
mismatch = []
for name, cap in db_caps.items():
    mm = re.search(rf'{re.escape(name)}:\s*\nMaximum capacity:\s*(\d+)', cap_txt)
    if mm and int(mm.group(1)) != cap:
        mismatch.append(f'{name}: db {cap} vs kb {mm.group(1)}')
check('stated room capacities match the database', not mismatch, '; '.join(mismatch))

# ── 6. prices ───────────────────────────────────────────────────────────────
print('\n[6] Prices')
svc = read('02_Data/02_Operational/services.csv')
canon = {int(r['base_price']) for r in rt}
for r in svc:
    for k in ('price','service_price','cost','base_price'):
        if r.get(k):
            try: canon.add(int(float(r[k]))); break
            except ValueError: pass
# v4: every EGP amount must come from a price table — room types, services, menu, fees
canon |= {int(float(r['price'])) for r in read('02_Data/02_Operational/menu_items.csv', 'utf-8')}
canon |= {int(float(r['amount'])) for r in read('02_Data/02_Operational/fees.csv', 'utf-8') if r['unit'].startswith('EGP')}
canon |= {int(float(r['value'])) for r in read('02_Data/02_Operational/loyalty_rules.csv', 'utf-8') if r['unit'].startswith('EGP')}
PRICE = re.compile(r'(?<![\d:,])(\d{1,3}(?:[,\u00a0\u202f ]\d{3})*|\d+)\s*(?:EGP|جنيه)')
stray = [(r['faq_id'], n) for r in m if r['origin'] != 'original_1344'
         for n in PRICE.findall(r['answer'])
         if int(re.sub(r'[,\u00a0\u202f ]', '', n)) not in canon]
check('every price quoted in an answer exists in the database', not stray,
      f'{len(stray)} stray values')

# ── 7. RAG corpus ───────────────────────────────────────────────────────────
print('\n[7] RAG corpus')
corpus = jsonl('04_RAG/corpus.jsonl')
check('chunk ids unique', len({c['chunk_id'] for c in corpus}) == len(corpus),
      f'{len(corpus)} chunks')
check('every knowledge document represented',
      {c['doc_id'] for c in corpus} == set(docs),
      f"{len({c['doc_id'] for c in corpus})}/{len(docs)}")
check('no empty chunks', all(c['text'].strip() for c in corpus))
oversized = [c['chunk_id'] for c in corpus if len(c['text']) > 2500]
check('no oversized chunks', not oversized, f'{len(oversized)} over 2500 chars')

# ── 8. splits ───────────────────────────────────────────────────────────────
print('\n[8] Train / val / test splits')
sp = {s: read(f'05_Evaluation/intent/{s}.csv', 'utf-8') for s in ('train','val','test')}
total = sum(len(v) for v in sp.values())
check('splits cover every master row', total == len(m), f'{total} of {len(m)}')
g = {s: {r['group_id'] for r in sp[s]} for s in sp}
check('no fact group shared train/test', not (g['train'] & g['test']),
      f"{len(g['train'] & g['test'])} shared")
check('no fact group shared train/val', not (g['train'] & g['val']),
      f"{len(g['train'] & g['val'])} shared")
tr = {r['question'].strip().lower() for r in sp['train']}
leak = [r['faq_id'] for s in ('val','test') for r in sp[s]
        if r['question'].strip().lower() in tr]
check('no question appears in both train and eval', not leak, f'{len(leak)} leaked')
N_INTENTS = len({r['intent_id'] for r in m})
for s in ('train','val','test'):
    ints = {r['intent_id'] for r in sp[s]}
    check(f'{s}: all {N_INTENTS} intents present', len(ints) == N_INTENTS,
          f'{len(ints)}/{N_INTENTS}')
    n_oos = sum(1 for r in sp[s] if r['origin'] == 'out_of_scope_100')
    check(f'{s}: contains out-of-scope examples', n_oos > 0, f'{n_oos} rows')
for s in ('train','val','test'):
    j = jsonl(f'05_Evaluation/intent/{s}.jsonl')
    check(f'{s}.jsonl matches {s}.csv', len(j) == len(sp[s]), f'{len(j)} vs {len(sp[s])}')
shapes = all(len(x['messages']) == 3 and
             [mm['role'] for mm in x['messages']] == ['system','user','assistant'] and
             all(mm['content'].strip() for mm in x['messages'])
             for s in ('train','val','test') for x in jsonl(f'05_Evaluation/intent/{s}.jsonl'))
check('every jsonl example is system/user/assistant with content', shapes)

# ── 9. conversations ────────────────────────────────────────────────────────
print('\n[9] Multi-turn conversations')
cv = read('02_Data/04_Gold/conversations_gold.csv', 'utf-8')
check('conversations present', len(cv) >= 400, f'{len(cv)}')
check('all unique', len({r['conversation_json'] for r in cv}) == len(cv))
check('conversation_id populated on every row',
      all(r['conversation_id'].strip() for r in cv),
      f"{sum(1 for r in cv if not r['conversation_id'].strip())} empty")
check('conversation_id unique',
      len({r['conversation_id'] for r in cv}) == len(cv),
      f"{len({r['conversation_id'] for r in cv})} of {len(cv)}")
check('balanced across the five conversation languages',
      len(set(Counter(r['language'] for r in cv).values())) == 1 and len(set(r['language'] for r in cv)) == 5,
      f"{dict(Counter(r['language'] for r in cv))}")
bad_roles, bad_lang = [], []
for r in cv:
    t = json.loads(r['conversation_json'])
    roles = [x['role'] for x in t]
    if roles[0] != 'user' or any(roles[i] == roles[i+1] for i in range(len(roles)-1)):
        bad_roles.append(r['conversation_id'])
    # a turn that is only an identifier or a number ("B003377.") carries no language
    def has_letters(s):
        return bool(re.search(r'[^\W\d_]{3,}', s))
    if any(has_letters(x['message']) and not lang_ok(x['message'], r['language']) for x in t):
        bad_lang.append(r['conversation_id'])
check('roles alternate and start with user', not bad_roles, f'{len(bad_roles)} malformed')
check('all turns in the declared language', not bad_lang, f'{len(bad_lang)} mixed')
placeholders = [r['conversation_id'] for r in cv
                if re.search(r'\{(bid|room|price|d1|d2|guests|room_no)\}', r['conversation_json'])]
check('no unfilled template slots', not placeholders, f'{len(placeholders)}')

# ── 10. operational data ────────────────────────────────────────────────────
print('\n[10] Operational data')
for rel, key in [('02_Data/02_Operational/pricing_tiers.csv','pricing_tier_id'),
                 ('02_Data/02_Operational/discount_codes.csv','code_id'),
                 ('02_Data/02_Operational/loyalty_members.csv','member_id'),
                 ('02_Data/02_Operational/complaint_tickets.csv','ticket_id'),
                 ('02_Data/02_Operational/special_requests_history.csv','request_id')]:
    fname = os.path.basename(rel)
    rows = read(rel, 'utf-8')
    check(f'{fname}: unique primary key',
          len({r[key] for r in rows}) == len(rows), f'{len(rows)} rows')


# ── 11. v3 Gold quality ─────────────────────────────────────────────────────
print('\n[11] Gold quality (v3)')
kb_ok = set(docs) | {'out_of_scope_policy'}
check('every row cites a knowledge-base document (or the out-of-scope policy)',
      all(r['source'] in kb_ok for r in m), f"{sum(r['source'] not in kb_ok for r in m)} rows")
LAT = re.compile(r'[A-Za-z]{4,}')
ALLOWED_LAT = re.compile(r'Nile|Pearl|Hotel|EGP|Wi-?Fi|nilepearlhotel|example|reservations|guestrelations|info|www|PEARL\d+|Single|Double|Twin|Deluxe|Family|Suite|Standard|Silver|Gold|Platinum|Marriott|Corniche|Street|Garden|City|Cairo|Visa|Mastercard|American|Express|Apple|Vodafone|Cash|InstaPay|Rewards')
def foreign_sentence(t):
    return len(LAT.findall(ALLOWED_LAT.sub(' ', t))) >= 3
bad = [r['faq_id'] for r in m if r['language'] in ('Arabic', 'Russian') and foreign_sentence(r['answer'])]
check('no Arabic or Russian answer carries an English sentence', not bad, f'{len(bad)} rows {bad[:5]}')
bad = [r['faq_id'] for r in m if r['requires_tool'] == 'True' and r['origin'] in ('enhanced_1008', 'complete_coverage')]
check('templated policy questions are not routed to a tool (DATA_ROUTING_MATRIX)', not bad, f'{len(bad)} rows')
egy = [r for r in m if r['language'] == 'Arabic-Egyptian']
per = Counter(r['intent_id'] for r in egy)
thin = {i: per.get(i, 0) for i in {r['intent_id'] for r in m} if per.get(i, 0) < 8}
check('Egyptian dialect covers every intent (>= 8 rows each)', not thin, f'{len(egy)} rows; thin: {thin}')
check('every Egyptian row has an Egyptian answer', all(r.get('answer_egyptian', '').strip() for r in egy))
bad = [r['faq_id'] for r in m if r['category'] == 'Egyptian Dialect']
check('category is the domain, never the language', not bad, f'{len(bad)} rows')

cats = {}
for r in m: cats.setdefault(r['intent_id'], set()).add(r['category'])
check('each intent has exactly one category', all(len(v) == 1 for v in cats.values()),
      f"{ {k: sorted(v) for k, v in cats.items() if len(v) > 1} }")

# ── 12. conversations grounded in the database ─────────────────────────────
print('\n[12] Conversations grounded in the database')
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'generation'))
import conv_templates_v4 as TPL
bk_ = {r['booking_id']: r for r in read('02_Data/02_Operational/bookings.csv', 'utf-8')}
room_no = {r['room_number'] for r in read('02_Data/02_Operational/rooms.csv', 'utf-8')}
ROOMRE = re.compile(r'(?:[Rr]oom|الغرفة|أوضة|[Cc]hambre|номере|[Нн]омер)\s+(\d{3,4})\b')
DATE = re.compile(r'\d{4}-\d{2}-\d{2}')
missing, badroom, baddate = [], [], []
for r in cv:
    j = json.loads(r['conversation_json'])
    text = ' '.join(t['message'] for t in j)
    for bid in set(re.findall(r'B\d{6}', text)):
        if bid not in bk_ and r['flow_id'] != 'BOOK_F7_not_found': missing.append((r['conversation_id'], bid))
    for n in ROOMRE.findall(text):
        if n not in room_no: badroom.append((r['conversation_id'], n))
    bids = set(re.findall(r'B\d{6}', text)) & set(bk_)
    if len(bids) == 1:
        b = bk_[bids.pop()]
        said = ' '.join(t['message'] for t in j if t['role'] == 'assistant')
        months = TPL.MONTHS[r['language']] if r['language'] in TPL.MONTHS else []
        mentions_date = DATE.search(said) or any(mn in said for mn in months)
        own = {TPL.spoken_date(b['check_in'], r['language']), TPL.spoken_date(b['check_out'], r['language']),
               b['check_in'], b['check_out']} if months else set()
        if mentions_date and own and not any(x in said for x in own):
            baddate.append(r['conversation_id'])
check('every booking id quoted in a conversation exists', not missing, f'{len(missing)} {missing[:3]}')
check('every room number quoted exists in rooms.csv', not badroom, f'{len(badroom)} {badroom[:3]}')
check('dates the assistant quotes for a booking match bookings.csv', not baddate, f'{len(baddate)} {baddate[:3]}')

# ── 13. RAG corpus hygiene ──────────────────────────────────────────────────
print('\n[13] RAG corpus hygiene')
check('no chunk ends with the next section\'s title', not [c for c in corpus if c['text'].rstrip().endswith(c['doc_title'])])
check('no thin chunk (< 120 characters of body)',
      not [c for c in corpus if len(c['text'].split('\n\n', 1)[-1]) < 120])
NOTE = re.compile(r'CORRECTED VERSION|\.csv|reserved for documentation|RT00\d')
check('no editorial note inside a customer-facing KB document',
      not [d for d in docs if NOTE.search(open(os.path.join(KB, d), encoding='utf-8').read())])

# ── summary ─────────────────────────────────────────────────────────────────
print('\n' + '=' * 78)
passed = sum(1 for _, ok, _ in results if ok)
failed = len(results) - passed
print(f'RESULT: {passed}/{len(results)} checks passed' + (f', {failed} FAILED' if failed else ''))
print('=' * 78)
if failed:
    print('\nFailed checks:')
    for n, ok, d in results:
        if not ok:
            print(f'  - {n}: {d}')
sys.exit(1 if failed else 0)
