#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Merge a candidate FAQ file into Gold after the six Gold gates
(structural, metadata, source, language, duplicate, ground truth).
See 02_Data/03_Candidate/README.md for the intake process.

    python3 06_Scripts/build/merge_candidate.py [02_Data/03_Candidate/<file>.csv ...]

With no argument every CSV in 02_Data/03_Candidate/ is merged. On success the candidate
file is deleted (its rows now live in Gold) and new faq_ids continue the Gold sequence.
Afterwards rebuild the derived files:  python3 06_Scripts/build/build_splits.py
"""
import csv, glob, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(ROOT)
GOLD = '02_Data/04_Gold/hotel_faq_gold.csv'
AR, CYR = re.compile(r'[\u0600-\u06FF]'), re.compile(r'[\u0400-\u04FF]')
FR = set('àâäçèéêëîïôùûüœæÀÂÄÇÈÉÊËÎÏÔÙÛÜŒÆ')
def detect(t):
    if AR.search(t): return 'Arabic'
    if CYR.search(t): return 'Russian'
    if any(c in FR for c in t): return 'French'
    return 'Latin'
def lang_ok(t, l):
    x = detect(t)
    return {'Arabic': x == 'Arabic', 'Arabic-Egyptian': x == 'Arabic', 'Russian': x == 'Russian',
            'French': x in ('French', 'Latin'), 'English': x == 'Latin'}.get(l, False)

def main(paths):
    with open(GOLD, encoding='utf-8-sig') as f:
        gold = list(csv.DictReader(f)); cols = list(gold[0].keys())
    labels = json.load(open('05_Evaluation/intent/label_map.json'))['label_to_id']
    names = {}
    for r in gold: names.setdefault(r['intent_id'], r['intent_name'])
    kb = {f for f in os.listdir('03_Knowledge_Base') if f.endswith('.txt')} | {'out_of_scope_policy'}
    canon = {int(r['base_price']) for r in csv.DictReader(open('02_Data/02_Operational/room_types.csv', encoding='utf-8-sig'))}
    canon |= {int(float(r['price'])) for r in csv.DictReader(open('02_Data/02_Operational/services.csv', encoding='utf-8-sig'))}
    canon |= {int(float(r['price'])) for r in csv.DictReader(open('02_Data/02_Operational/menu_items.csv', encoding='utf-8-sig'))}
    canon |= {int(float(r['amount'])) for r in csv.DictReader(open('02_Data/02_Operational/fees.csv', encoding='utf-8-sig')) if r['unit'].startswith('EGP')}
    canon |= {int(float(r['value'])) for r in csv.DictReader(open('02_Data/02_Operational/loyalty_rules.csv', encoding='utf-8-sig')) if r['unit'].startswith('EGP')}
    PRICE = re.compile(r'(?<![\d:,])(\d{1,3}(?:[,\u00a0\u202f ]\d{3})*|\d+)\s*(?:EGP|جنيه)')
    seen = {r['question'].strip().lower() for r in gold}
    nxt = max(int(r['faq_id'][3:]) for r in gold) + 1
    for p in paths:
        rows = list(csv.DictReader(open(p, encoding='utf-8-sig')))
        errs = []
        for i, r in enumerate(rows, 2):
            miss = [c for c in cols if c != 'faq_id' and c not in r]
            if miss: errs.append(f'row {i}: structural — missing {miss}')
            if r['intent_id'] not in labels: errs.append(f'row {i}: metadata — unknown intent {r["intent_id"]}')
            if names.get(r['intent_id']) not in (None, r['intent_name']): errs.append(f'row {i}: metadata — intent_name')
            if r['response_mode'] not in ('knowledge_answer', 'customer_service', 'edge_case_answer', 'safe_refusal_or_redirect', 'escalate_to_human'):
                errs.append(f'row {i}: metadata — response_mode')
            if r['requires_tool'] not in ('True', 'False'): errs.append(f'row {i}: metadata — requires_tool')
            if r['source'] not in kb: errs.append(f'row {i}: source — {r["source"]} is not a KB document')
            for c in ('question', 'answer') + (('answer_egyptian',) if r['language'] == 'Arabic-Egyptian' else ()):
                if not r[c].strip() or not lang_ok(r[c], r['language']): errs.append(f'row {i}: language — {c}')
            q = r['question'].strip().lower()
            if q in seen: errs.append(f'row {i}: duplicate — {r["question"]}')
            seen.add(q)
            for c in ('answer', 'answer_egyptian'):
                for n in PRICE.findall(r.get(c, '')):
                    if int(re.sub(r'[,\u00a0\u202f ]', '', n)) not in canon:
                        errs.append(f'row {i}: ground truth — price {n} not in the database')
        if errs:
            print(f'{p}: {len(errs)} gate failures — nothing merged'); print('\n'.join(errs[:40])); sys.exit(1)
        for r in rows:
            new = {c: r.get(c, '') for c in cols}; new['faq_id'] = f'FAQ{nxt:04d}'; nxt += 1
            gold.append(new)
        print(f'{p}: {len(rows)} rows passed all gates and were merged')
        os.remove(p)
    with open(GOLD, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(gold)
    print(f'Gold now {len(gold)} rows. Rebuild derived files: python3 06_Scripts/build/build_splits.py')

if __name__ == '__main__':
    main(sys.argv[1:] or sorted(glob.glob('02_Data/03_Candidate/*.csv')))
