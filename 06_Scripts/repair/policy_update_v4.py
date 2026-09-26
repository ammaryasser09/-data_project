#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gold FAQ v4: apply the approved policies and the v4 price list to every answer, in all
five languages, and add the questions the new knowledge-base content needs.

  P1  prices: every old list price in a price context is replaced by its v4 value
      (1,800 → 6,000 … 450 → 1,200 …), in every language and number format
  P2  policy facts that were "not specified" are now answered (cancellation, refunds,
      deposits, loyalty, laundry, airport, parking, room sizes …) — texts in
      policy_update_v4_data.py, located in each language through the Gold block layout
  P3  accepted identification documents (Egyptian nationals / foreign nationals)
  P4  Egyptian rows written before v3, one by one
  P5  response_mode escalate_to_human for requests that need a person, not a refusal
  P6  question_style column: templated / natural
  P7  new questions for the new documents (menu, location, reservation security, rate
      plans, taxes, early / late check-out, Nile view, deposit, spa, minimum age …)

Idempotent: rows that existed before v4 are rebuilt from the frozen snapshot
02_Data/01_Raw/hotel_faq_gold_pre_v4.csv; rows added later are kept as they are.
    python3 06_Scripts/repair/policy_update_v4.py
"""
import csv, os, re, shutil, sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'build'))
from policy_update_v4_data import FACTS, IDS, EGY_ROWS, NEW, RENAMED, EGY_GROUPS
ROOT = os.path.dirname(os.path.dirname(HERE)); os.chdir(ROOT)
GOLD, PRE = '02_Data/04_Gold/hotel_faq_gold.csv', '02_Data/01_Raw/hotel_faq_gold_pre_v4.csv'
LOG = '07_Audits/Repair_Logs/gold_repair_log_v4.csv'
CORE = ('English', 'Arabic', 'French', 'Russian')
def rd(p):
    with open(p, encoding='utf-8-sig') as f: return list(csv.DictReader(f))
if not os.path.exists(PRE): shutil.copyfile(GOLD, PRE)
pre, cur = rd(PRE), rd(GOLD)
pre_ids = {r['faq_id'] for r in pre}
rows = [dict(r) for r in pre] + [r for r in cur if r['faq_id'] not in pre_ids]
R = {r['faq_id']: r for r in rows}
cols = list(pre[0].keys()) + (['question_style'] if 'question_style' not in pre[0] else [])
log, touched = [], set()
def setv(fid, col, new, rule, why):
    r = R[fid]
    if r.get(col, '') == new: return
    log.append({'faq_id': fid, 'column': col, 'old_value': r.get(col, ''), 'new_value': new, 'rule': rule, 'reason': why})
    r[col] = new

# ── P2 policy facts ──
for fid, text in FACTS.items():
    a = R[fid]; assert a['language'] == 'English', fid
    old = {'English': a['answer']}
    base, org = int(fid[3:]), a['origin']
    n_block = sum(1 for r in rows if r['language'] == 'English' and r['answer'] == a['answer'] and r['origin'] == org
                  and abs(int(r['faq_id'][3:]) - base) < 4)
    offs = {'enhanced_1008': (3, 6, 9), 'complete_coverage': (3, 6, 9)}.get(org) or \
           ((n_block, 2 * n_block, 3 * n_block) if org == 'coverage_fill_v3' else (1, 2, 3))
    for k, L in zip(offs, CORE[1:]):
        o = R[f'FAQ{base + k:04d}']; assert o['language'] == L and o['intent_id'] == a['intent_id'], (fid, L)
        old[L] = o['answer']
    for r in rows:
        L = r['language']
        if L in CORE and r['answer'] == old[L]:
            setv(r['faq_id'], 'answer', text[L], 'P2', 'v4 policy: the fact is now stated in the knowledge base'); touched.add(r['faq_id'])
        elif L == 'Arabic-Egyptian' and r['answer'] == old['Arabic']:
            setv(r['faq_id'], 'answer', text['Arabic'], 'P2', 'v4 policy (MSA ground truth)')
            setv(r['faq_id'], 'answer_egyptian', text['Arabic-Egyptian'], 'P2', 'v4 policy (Egyptian reply)'); touched.add(r['faq_id'])

# ── P3 identification documents ──
IDPAT = {'English': 'does not specify the exact', 'Arabic': r'لا تحدد قاعدة (المعرفة|معلومات)',
         'French': 'ne précise pas les types', 'Russian': 'не указывает точные виды'}
YES = {'English': ('Yes', 'Yes. '), 'French': ('Oui', 'Oui. '), 'Russian': ('Да', 'Да. '), 'Arabic': ('نعم', 'نعم، ')}
for r in rows:
    if r['intent_id'] != 'INT008' or r['faq_id'] in touched: continue
    L = r['language']; key = 'Arabic' if L == 'Arabic-Egyptian' else L
    if key in IDPAT and re.search(IDPAT[key], r['answer']):
        pre_ = YES[key][1] if r['answer'].startswith(YES[key][0]) and L != 'Arabic-Egyptian' else ''
        setv(r['faq_id'], 'answer', pre_ + IDS[key], 'P3', 'identification_policy.txt now lists the accepted documents')
        if L == 'Arabic-Egyptian': setv(r['faq_id'], 'answer_egyptian', IDS['Arabic-Egyptian'], 'P3', 'accepted documents')
        touched.add(r['faq_id'])

# ── P4 older Egyptian rows ──
for fid, (msa, egy) in EGY_ROWS.items():
    assert R[fid]['language'] == 'Arabic-Egyptian', fid
    setv(fid, 'answer', msa, 'P4', 'v4 policy and price list'); setv(fid, 'answer_egyptian', egy, 'P4', 'v4 policy and price list')
    touched.add(fid)

# ── P4b Egyptian answers that lagged behind v4 (groups share one pre-v4 Egyptian answer) ──
egy_rows = [r for r in rows if r['language'] == 'Arabic-Egyptian']
for fid, (msa, egy) in EGY_GROUPS.items():
    key = R[fid]['answer_egyptian']
    for r in egy_rows:
        if r['faq_id'] in touched or r['answer_egyptian'] != key: continue
        if r['answer'] != msa: setv(r['faq_id'], 'answer', msa, 'P4b', 'v4 terms; the answer fits every paired question')
        setv(r['faq_id'], 'answer_egyptian', egy, 'P4b', 'v4 terms; the answer fits every paired question')
        touched.add(r['faq_id'])

# ── P1 price list ──
OLD2NEW = {1800: 6000, 2500: 8000, 2700: 8500, 3800: 12000, 4500: 14000, 6500: 20000,
           450: 1200, 800: 2500, 200: 500, 1200: 3500, 600: 2500, 500: 1500, 150: 300}
NUM = re.compile(r'(?<![\d,.:/])(\d{1,3}(?:[,\u00a0\u202f ]\d{3})+|\d{3,4})(?![\d:/%])')
CUR = re.compile(r'EGP|جنيه|ج\.م')
def fmt(v, orig):
    sep = next((c for c in orig if c in ',\u00a0\u202f '), None)
    return f'{v:,}'.replace(',', sep) if sep else str(v)
def remap(text):
    out = []
    for s in re.split(r'(?<=[.!?؟;])(\s+)', text):
        cur_ = bool(CUR.search(s))
        def sub(m):
            v = int(re.sub(r'[,\u00a0\u202f ]', '', m.group(1)))
            if v not in OLD2NEW: return m.group(0)
            if not cur_ and not re.search(r'(بـ|بسعر)\s*$', s[max(0, m.start() - 6):m.start()]): return m.group(0)
            return fmt(OLD2NEW[v], m.group(1))
        out.append(NUM.sub(sub, s))
    return ''.join(out)
for r in rows:
    if r['faq_id'] in touched or r['faq_id'] not in pre_ids: continue
    for c in ('answer', 'answer_egyptian'):
        new = remap(r.get(c, ''))
        if new != r.get(c, ''): setv(r['faq_id'], c, new, 'P1', 'v4 price list')

# ── P5 escalation ──
esc = set()
for fid in ('FAQ2509', 'FAQ2517', 'FAQ2521', 'FAQ2525', 'FAQ3554'):
    for k in range(4):
        o = R[f'FAQ{int(fid[3:]) + k:04d}']; esc.add((o['language'], o['answer']))
ar_esc = {a for L, a in esc if L == 'Arabic'}
for r in rows:
    if (r['language'], r['answer']) in esc or (r['language'] == 'Arabic-Egyptian' and r['answer'] in ar_esc) or r['faq_id'] == 'FAQ3496':
        setv(r['faq_id'], 'response_mode', 'escalate_to_human', 'P5', 'the request needs a person (legal, staff, compensation, data deletion, repeated misunderstanding), not a refusal')

# ── P6 question style ──
for r in rows:
    r['question_style'] = 'templated' if r['origin'] in ('enhanced_1008', 'complete_coverage') else 'natural'

# ── P7s keep already-merged v4 questions in step with the data file ──
want = {}
for iid, src, core, (eq, ea) in NEW:
    for L in CORE: want[core[L][0]] = (core[L][1], '')
    for q in eq: want[q] = (core['Arabic'][1], ea)
for r in rows:
    if r['origin'] != 'policy_v4': continue
    if r['question'] in RENAMED:
        setv(r['faq_id'], 'question', RENAMED[r['question']], 'P7s', 'a paired question must fit the shared answer')
    if r['question'] in want:
        a, ea = want[r['question']]
        if r['answer'] != a: setv(r['faq_id'], 'answer', a, 'P7s', 'answer follows policy_update_v4_data.py')
        if r['language'] == 'Arabic-Egyptian' and r['answer_egyptian'] != ea:
            setv(r['faq_id'], 'answer_egyptian', ea, 'P7s', 'answer follows policy_update_v4_data.py')

with open(GOLD, 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rows)
with open(LOG, 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=['faq_id', 'column', 'old_value', 'new_value', 'rule', 'reason']); w.writeheader(); w.writerows(log)
print(f'v4 changes: {len(log)} {dict(Counter(x["rule"] for x in log))}')

# ── P7 new questions through the normal candidate intake ──
have = {r['question'].strip().lower() for r in rows}
NAMES = {r['intent_id']: (r['intent_name'], r['category']) for r in rows if r['language'] == 'English'}
MODE = {i: 'customer_service' for i in ('INT009', 'INT010', 'INT011', 'INT012', 'INT013', 'INT014')}
cand = []
for iid, src, core, (eq, ea) in NEW:
    base = {'intent_id': iid, 'intent_name': NAMES[iid][0], 'status': 'valid', 'category': NAMES[iid][1],
            'source': src, 'response_mode': MODE.get(iid, 'knowledge_answer'), 'requires_tool': 'False', 'question_style': 'natural'}
    for L in CORE:
        q, a = core[L]
        cand.append({**base, 'language': L, 'question_type': 'Direct', 'question': q, 'answer': a,
                     'origin': 'policy_v4', 'answer_egyptian': ''})
    for k, q in enumerate(eq):
        cand.append({**base, 'language': 'Arabic-Egyptian', 'question_type': 'Direct' if k == 0 else 'Paraphrased',
                     'question': q, 'answer': core['Arabic'][1], 'origin': 'policy_v4', 'answer_egyptian': ea})
cand = [c for c in cand if c['question'].strip().lower() not in have]
if cand:
    p = '02_Data/03_Candidate/policy_v4.csv'
    with open(p, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=[c for c in cols if c != 'faq_id']); w.writeheader(); w.writerows(cand)
    import merge_candidate; merge_candidate.main([p])
else:
    print('P7: new questions already merged')
