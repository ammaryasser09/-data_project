#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FINAL RE-AUDIT — recalculated from zero.

Reads nothing from previous audit outputs. Every number below is computed fresh from the
data files. Run from the project root:

    python3 06_Scripts/validation/final_audit.py

Exit code 0 = READY FOR DEVELOPMENT, 1 = NOT READY.
"""
import csv, hashlib, json, os, re, sys
from collections import Counter, defaultdict
from datetime import date, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(ROOT)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import SYSTEM_DATE as TODAY   # single frozen 'today' — see 06_Scripts/config.py

BLOCKING     = {'Confirmed', 'Completed'}
NON_BLOCKING = {'Cancelled', 'No-show'}

def rd(p):
    with open(p, encoding='utf-8-sig') as f: return list(csv.DictReader(f))
def jl(p):
    with open(p, encoding='utf-8') as f: return [json.loads(l) for l in f if l.strip()]
def d(s): return date.fromisoformat(str(s)[:10])
def sha(p): return hashlib.sha256(open(p,'rb').read()).hexdigest()

gates = {}
findings = []
def gate(n, status, evidence):
    gates[n] = (status, evidence)
    mark = {'PASS':'PASS','FAIL':'FAIL','BLOCKED':'BLOCKED'}[status]
    print(f'  {mark:8} {n}')
    print(f'           {evidence}')

S = '02_Data/02_Operational'
bk    = rd(f'{S}/bookings.csv')
cus   = rd(f'{S}/customers.csv')
pay   = rd(f'{S}/payments.csv')
rooms = rd(f'{S}/rooms.csv')
rt    = rd(f'{S}/room_types.csv')
svc   = rd(f'{S}/services.csv')
creq  = rd(f'{S}/customer_requests.csv')
comp  = rd(f'{S}/complaint_tickets.csv')
sreq  = rd(f'{S}/special_requests_history.csv')
loyal = rd(f'{S}/loyalty_members.csv')
gold  = rd('02_Data/04_Gold/hotel_faq_gold.csv')
orig_gold = rd('02_Data/04_Gold/hotel_faq_1344_baseline.csv')
conv  = rd('02_Data/04_Gold/conversations_gold.csv')
corpus = jl('04_RAG/corpus.jsonl')

cap = {r['room_type_id']: int(r['capacity']) for r in rt}

print('=' * 78)
print('FINAL RE-AUDIT — computed from zero')
print('=' * 78)

# ───────────────────────── GATE 1 — database integrity ─────────────────────────
print('\nGATE 1 — Database Integrity')
pk_ok = all([
    len({r['booking_id'] for r in bk}) == len(bk),
    len({r['customer_id'] for r in cus}) == len(cus),
    len({r['payment_id'] for r in pay}) == len(pay),
    len({r['room_id'] for r in rooms}) == len(rooms),
    len({r['room_type_id'] for r in rt}) == len(rt),
])
cid = {r['customer_id'] for r in cus}
bid = {r['booking_id'] for r in bk}
rid = {r['room_id'] for r in rooms}
tid = {r['room_type_id'] for r in rt}
fk = {
    'bookings→customers':  sum(1 for r in bk if r['customer_id'] not in cid),
    'bookings→rooms':      sum(1 for r in bk if r['room_id'] not in rid),
    'bookings→room_types': sum(1 for r in bk if r['room_type_id'] not in tid),
    'rooms→room_types':    sum(1 for r in rooms if r['room_type_id'] not in tid),
    'payments→bookings':   sum(1 for r in pay if r['booking_id'] not in bid),
    'loyalty→customers':   sum(1 for r in loyal if r['customer_id'] not in cid),
    'complaints→customers':sum(1 for r in comp if r['customer_id'] not in cid),
    'complaints→bookings': sum(1 for r in comp if r['booking_id'] and r['booking_id'] not in bid),
    'requests→customers':  sum(1 for r in sreq if r['customer_id'] not in cid),
    'requests→bookings':   sum(1 for r in sreq if r['booking_id'] not in bid),
}
fk_total = sum(fk.values())
bad_dates = sum(1 for r in bk if d(r['check_out']) <= d(r['check_in']))
bad_nights = sum(1 for r in bk if int(r['nights']) != (d(r['check_out']) - d(r['check_in'])).days)
nulls = sum(1 for r in bk for v in r.values() if v is None or str(v).strip() == '')
impossible = sum(1 for r in bk
                 if (r['booking_status'] == 'Completed' and d(r['check_in']) > TODAY)
                 or (r['booking_status'] == 'No-show'   and d(r['check_in']) > TODAY))
stale = sum(1 for r in bk if r['booking_status'] == 'Confirmed' and d(r['check_out']) < TODAY)

ok1 = pk_ok and fk_total == 0 and bad_dates == 0 and bad_nights == 0 and nulls == 0 and impossible == 0
gate('Database Integrity', 'PASS' if ok1 else 'FAIL',
     f'PKs unique: {pk_ok} | FK violations: {fk_total} across 10 relationships | '
     f'invalid dates: {bad_dates} | nights mismatch: {bad_nights} | empty fields: {nulls} | '
     f'impossible states: {impossible} | stale-but-valid states flagged: {stale}')

# ───────────────────────── GATE 2 — availability integrity ─────────────────────────
print('\nGATE 2 — Availability Integrity')
by_room = defaultdict(list)
for r in bk:
    if r['blocks_inventory'] == 'True':
        by_room[r['room_id']].append((d(r['check_in']), d(r['check_out']), r['booking_id']))

pairs = 0
for rm, lst in by_room.items():
    lst.sort()
    for i in range(len(lst)):
        for j in range(i + 1, len(lst)):
            if lst[j][0] >= lst[i][1]: break
            if lst[i][0] < lst[j][1] and lst[j][0] < lst[i][1]: pairs += 1

# back-to-back must not be counted
b2b = 0
for rm, lst in by_room.items():
    lst.sort()
    for i in range(len(lst) - 1):
        if lst[i][1] == lst[i + 1][0]: b2b += 1

# rerun the availability suite
import subprocess
av = subprocess.run([sys.executable, '06_Scripts/validation/validate_availability.py'],
                    capture_output=True, text=True)
m = re.search(r'RESULT: (\d+)/(\d+)', av.stdout)
av_pass, av_total = (int(m.group(1)), int(m.group(2))) if m else (0, 0)

ok2 = pairs == 0 and av_pass == av_total and av_total > 0
gate('Availability Integrity', 'PASS' if ok2 else 'FAIL',
     f'active room conflicts: {pairs} | back-to-back pairs correctly allowed: {b2b} | '
     f'availability suite: {av_pass}/{av_total} | blocks_inventory=False on active bookings '
     f'(overbooked, never block a room): {sum(1 for r in bk if r["booking_status"] in BLOCKING and r["blocks_inventory"] != "True")}')

# ───────────────────────── GATE 3 — capacity logic ─────────────────────────
print('\nGATE 3 — Capacity Logic')
kb_text = ' '.join(open(f'03_Knowledge_Base/{f}', encoding='utf-8').read()
                   for f in os.listdir('03_Knowledge_Base') if f.endswith('.txt')).lower()
ruleB = [r for r in bk if int(r['adults']) + int(r['children']) > cap[r['room_type_id']]]
ruleA = [r for r in bk if int(r['adults']) > cap[r['room_type_id']]]

# The rule counts as defined only when it is stated in the rules document AND every
# implementation agrees with it. Each cell below is verified by reading the actual file.
def has(path, pattern):
    if not os.path.exists(path): return False
    return bool(re.search(pattern, open(path, encoding='utf-8').read(), re.I))

CAP_EXPR = r"adults\s*\+\s*children\s*<=\s*(room_type\.|room_)?capacity|adults'?\]?\)?\s*\+\s*int\(r\['children'\]\)\s*>\s*CAP|children count toward room capacity"
matrix = {
    'rules document': has('01_Docs/BUSINESS_RULES.md', CAP_EXPR),
    'generator':      has('06_Scripts/generation/generate_bookings.py', CAP_EXPR),
    'repair pipeline':has('06_Scripts/repair/apply_business_rules.py', CAP_EXPR),
    'db validator':   has('06_Scripts/validation/validate_database.py', CAP_EXPR),
    'availability':   has('06_Scripts/validation/validate_availability.py',
                          r'CAPACITY_EXCEEDED|guests > CAP'),
    'knowledge base': any(has(f'03_Knowledge_Base/{f}', r'children count toward room capacity')
                          for f in os.listdir('03_Knowledge_Base') if f.endswith('.txt')),
    'gold FAQ':       any('children count toward room capacity' in r['answer'].lower()
                          for r in gold),
}
rule_defined = all(matrix.values()) and len(ruleB) == 0
gate('Capacity Logic', 'PASS' if rule_defined else 'BLOCKED',
     f'Rule B (adults+children<=cap) violations in data: {len(ruleB)} | '
     f'Rule A-only violations: {len(ruleA)} | consistency matrix: '
     + ', '.join(f"{k}={'Y' if v else 'N'}" for k, v in matrix.items()))
if not rule_defined:
    missing_impl = [k for k, v in matrix.items() if not v]
    findings.append(('EXTERNAL DECISION REQUIRED' if not matrix['rules document']
                     else 'INCONSISTENT IMPLEMENTATION', 'child capacity rule',
        f'data violations: {len(ruleB)}; components not implementing the rule: '
        f'{missing_impl or "none"}'))

# ───────────────────────── GATE 4 — booking integrity ─────────────────────────
print('\nGATE 4 — Booking Integrity')
cap_room = {r['room_id']: r['room_type_id'] for r in rooms}
wrong_type = sum(1 for r in bk if cap_room.get(r['room_id']) != r['room_type_id'])
bad_total = sum(1 for r in bk
                if abs(float(r['total_amount']) - float(r['price_per_night']) * int(r['nights'])) > 0.01)
base = {r['room_type_id']: float(r['base_price']) for r in rt}
out_band = sum(1 for r in bk
               if not 0.80 <= float(r['price_per_night']) / base[r['room_type_id']] <= 1.35)
pay_by = defaultdict(int)
for p in pay: pay_by[p['booking_id']] += 1
multi_pay = sum(1 for k, v in pay_by.items() if v > 1)
status_ok = set(r['booking_status'] for r in bk) <= (BLOCKING | NON_BLOCKING)
dupes = len(bk) - len({(r['customer_id'], r['room_id'], r['check_in'], r['check_out']) for r in bk})

ok4 = wrong_type == 0 and bad_total == 0 and out_band == 0 and status_ok and dupes == 0
gate('Booking Integrity', 'PASS' if ok4 else 'FAIL',
     f'room_id/room_type_id mismatches: {wrong_type} | total≠rate×nights: {bad_total} | '
     f'rate outside seasonal band: {out_band} | duplicate bookings: {dupes} | '
     f'multi-payment bookings: {multi_pay} | status vocabulary valid: {status_ok}')

# ───────────────────────── GATE 5 — Gold integrity ─────────────────────────
print('\nGATE 5 — Gold Integrity')
AR = re.compile(r'[\u0600-\u06FF]'); CYR = re.compile(r'[\u0400-\u04FF]')
FR = set('àâäçèéêëîïôùûüœæÀÂÄÇÈÉÊËÎÏÔÙÛÜŒÆ')
def detect(t):
    if AR.search(t): return 'Arabic'
    if CYR.search(t): return 'Russian'
    if any(c in FR for c in t): return 'French'
    return 'Latin'
def lang_ok(t, l):
    x = detect(t)
    if l in ('Arabic','Arabic-Egyptian'): return x == 'Arabic'
    if l == 'Russian': return x == 'Russian'
    if l == 'French':  return x in ('French','Latin')
    if l == 'English': return x == 'Latin'
    return False

g_ids   = len({r['faq_id'] for r in gold}) == len(gold)
nums    = sorted(int(r['faq_id'][3:]) for r in gold)
g_gaps  = sum(1 for a,b in zip(nums, nums[1:]) if b != a+1)
g_dupq  = len(gold) - len({r['question'].strip().lower() for r in gold})
g_null  = sum(1 for r in gold if not r['question'].strip() or not r['answer'].strip())
g_lang  = sum(1 for r in gold if not lang_ok(r['question'], r['language'])
                              or not lang_ok(r['answer'], r['language']))
kb_files = {f for f in os.listdir('03_Knowledge_Base') if f.endswith('.txt')}
g_src   = sum(1 for r in gold if r['source'] in kb_files)
g_1344  = all(r['faq_id'] in {x['faq_id'] for x in gold} for r in orig_gold)
lc = Counter(r['language'] for r in gold if r['language'] != 'Arabic-Egyptian')
g_bal = max(lc.values())/min(lc.values())
qt = Counter(r['question_type'] for r in gold)

g_untraced = sum(1 for r in gold if r['source'] not in kb_files and r['source'] != 'out_of_scope_policy')
egy_int = Counter(r['intent_id'] for r in gold if r['language'] == 'Arabic-Egyptian')
g_egy_thin = [i for i in {r['intent_id'] for r in gold} if egy_int.get(i, 0) < 8]
ok5 = (g_ids and g_gaps==0 and g_dupq==0 and g_null==0 and g_lang==0 and g_1344 and g_bal<=1.10
       and g_untraced == 0 and not g_egy_thin)
gate('Gold Integrity', 'PASS' if ok5 else 'FAIL',
     f'{len(gold)} rows | unique IDs: {g_ids} | ID gaps: {g_gaps} | duplicate questions: {g_dupq} | '
     f'empty fields: {g_null} | language mismatches: {g_lang} | original 1,344 all present: {g_1344} | '
     f'language ratio: {g_bal:.3f} | rows traceable to a KB document: {g_src} (untraced, excluding the out-of-scope policy: {g_untraced}) | '
     f'Egyptian rows: {sum(egy_int.values())} across {len(egy_int)} intents (intents under 8: {len(g_egy_thin)})')
print(f'           question types: {dict(qt)}')
print(f'           languages: {dict(sorted(lc.items()))}')

# ───────────────────────── GATE 6 — knowledge base ─────────────────────────
print('\nGATE 6 — Knowledge Base')
docs = sorted(f for f in os.listdir('03_Knowledge_Base') if f.endswith('.txt'))
SEC = re.compile(r'^\s*(\d+)\.\s+(.+?)\s*$')
sections = {x: (len([1 for l in open(f'03_Knowledge_Base/{x}', encoding='utf-8') if SEC.match(l)]) or 1)
            for x in docs}
srcs = {r['source'] for r in gold}
uncovered = [x for x in docs if x not in srcs]
GHOST = ('Standard Room','Superior Room','Executive Room')
ghost = [x for x in docs if any(g in open(f'03_Knowledge_Base/{x}',encoding='utf-8').read() for g in GHOST)]
CRITICAL_FACTS = {
  'phone number': r'\+?\d[\d\s\-()]{7,}',
  'email address': r'[\w.\-]+@[\w.\-]+\.\w+',
  'street address': r'(street|avenue|road|district|شارع)',
  'no-show policy': r'no[- ]show',
}
missing_facts = [k for k, pat in CRITICAL_FACTS.items() if not re.search(pat, kb_text, re.I)]
ok6 = not uncovered and not ghost and not missing_facts
gate('Knowledge Base', 'PASS' if ok6 else 'FAIL',
     f'{len(docs)} documents, {sum(sections.values())} sections | uncovered documents: {len(uncovered)} | '
     f'documents citing a non-existent room type: {len(ghost)} | '
     f'critical customer-facing facts missing: {missing_facts}')
for f in missing_facts:
    findings.append(('MISSING_KNOWLEDGE_SOURCE', f,
        'cannot be invented; the agent has no answer for this question'))

# ───────────────────────── GATE 7 — RAG readiness ─────────────────────────
print('\nGATE 7 — RAG Readiness')
c_ids = len({c['chunk_id'] for c in corpus}) == len(corpus)
c_docs = {c['doc_id'] for c in corpus} == set(docs)
c_empty = sum(1 for c in corpus if not c['text'].strip())
c_big = sum(1 for c in corpus if len(c['text']) > 2500)
c_thin = sum(1 for c in corpus if c['char_len'] < 120)
c_attr = all('doc_id' in c and 'section' in c for c in corpus)
ok7 = c_ids and c_docs and c_empty == 0 and c_big == 0 and c_attr and c_thin == 0
gate('RAG Readiness', 'PASS' if ok7 else 'FAIL',
     f'{len(corpus)} chunks from {len({c["doc_id"] for c in corpus})}/{len(docs)} documents | '
     f'unique ids: {c_ids} | empty: {c_empty} | oversized: {c_big} | thin (<120 chars): {c_thin} | '
     f'source attribution on every chunk: {c_attr}')

# ───────────────────────── GATE 8 — project coverage ─────────────────────────
print('\nGATE 8 — Project Coverage')
conv_intents = {r['intent_id'] for r in conv}
BOOKING_FLOWS = {'create_booking','check_availability','get_booking','modify_booking',
                 'cancel_booking','get_payment_status'}
have_flows = BOOKING_FLOWS & conv_intents
conv_langs = Counter(r['language'] for r in conv)
oos = sum(1 for r in gold if r['response_mode'] == 'safe_refusal_or_redirect')
tools = sum(1 for r in gold if r['requires_tool'] == 'True')
CAPS = {
 'hotel information':  any(r['intent_id']=='INT001' for r in gold),
 'room information':   any(r['intent_id']=='INT024' for r in gold),
 'prices':             any(r['intent_id']=='INT026' for r in gold),
 'availability':       'check_availability' in conv_intents,
 'create booking':     'create_booking' in conv_intents,
 'retrieve booking':   'get_booking' in conv_intents,
 'modify booking':     'modify_booking' in conv_intents,
 'cancel booking':     'cancel_booking' in conv_intents,
 'payment status':     'get_payment_status' in conv_intents,
 'complaints':         any(r['intent_id']=='INT010' for r in gold),
 'special requests':   any(r['intent_id']=='INT011' for r in gold),
 'human handover':     oos > 0,
 'out-of-scope':       oos > 0,
 'four languages':     len(lc) == 4,
 'Egyptian dialect':   len(conv_langs) == 5 and 'Arabic-Egyptian' in conv_langs,
}
missing_caps = [k for k,v in CAPS.items() if not v]
ok8 = not missing_caps
gate('Project Coverage', 'PASS' if ok8 else 'FAIL',
     f'{len(CAPS)-len(missing_caps)}/{len(CAPS)} target capabilities have data | '
     f'booking flows present: {len(have_flows)}/6 | conversations: {len(conv)} across '
     f'{len(conv_intents)} intents | out-of-scope rows: {oos} | tool-routed rows: {tools} | '
     f'missing: {missing_caps or "none"}')

# ───────────────────────── GATE 9 — validators ─────────────────────────
print('\nGATE 9 — Cross-table and dataset validators')
res = {}
for v in ('validate_database', 'validate_dataset'):
    out = subprocess.run([sys.executable, f'06_Scripts/validation/{v}.py'], capture_output=True, text=True).stdout
    mm = re.search(r'RESULT: (\d+)/(\d+)', out); res[v] = (int(mm.group(1)), int(mm.group(2))) if mm else (0, 1)
ok9 = all(a == b for a, b in res.values())
gate('Validators', 'PASS' if ok9 else 'FAIL', ' | '.join(f'{k}: {a}/{b}' for k, (a, b) in res.items()))

# ───────────────────────── decision ─────────────────────────
print('\n' + '=' * 78)
crit = [n for n,(s,_) in gates.items() if s == 'FAIL']
blocked = [n for n,(s,_) in gates.items() if s == 'BLOCKED']
ready = not crit and not blocked

print('GATE SUMMARY')
for n,(s,_) in gates.items(): print(f'  {s:8} {n}')
print('=' * 78)
print()
print('FINAL STATUS:')
print('READY FOR DEVELOPMENT' if ready else 'NOT READY FOR DEVELOPMENT')
print()
if crit:    print(f'Failed gates: {crit}')
if blocked: print(f'Blocked gates: {blocked}')
for kind, what, why in findings:
    print(f'\n  [{kind}] {what}\n    {why}')
print('=' * 78)
sys.exit(0 if ready else 1)
