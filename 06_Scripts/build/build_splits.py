#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rebuild every file derived from Gold:
    05_Evaluation/intent/{train,val,test}.csv + .jsonl     intent / answer training splits
    04_RAG/retrieval_eval.jsonl                            retrieval ground truth

Run after any Gold edit (repair_gold_v3.py, merge_candidate.py) and after
build_rag_corpus.py, because the jsonl prompts embed the corpus text.

Splits are split by fact group (group_id), so no fact appears in both train and eval.
Assignments are stable: a row that already has a split keeps it; a new group is placed by a
hash of its id (≈70 / 15 / 15). Egyptian rows are trained to answer in Egyptian
(answer_egyptian), because the system prompt says "reply in the same language".

    python3 06_Scripts/build/build_splits.py
"""
import csv, hashlib, json, os
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(ROOT)
D = '05_Evaluation/intent'
SPLITS = ('train', 'val', 'test')
SYSTEM = ('You are the customer service assistant for Nile Pearl Hotel in Cairo, Egypt. Answer only '
          'from the provided hotel information. If the information does not cover the question, say '
          'the hotel does not specify it and direct the guest to customer service. Reply in the same '
          'language the guest used.')
COLS = ['faq_id', 'intent_id', 'intent_name', 'language', 'question_type', 'question_style', 'question', 'answer',
        'answer_egyptian', 'category', 'source', 'origin', 'response_mode', 'requires_tool', 'group_id']

def h(s): return int(hashlib.sha256(s.encode()).hexdigest(), 16)
def new_group(r):
    if r['language'] == 'Arabic-Egyptian':
        return 'G' + hashlib.sha256('|'.join(('egy3', r['intent_id'], r['answer_egyptian'])).encode()).hexdigest()[:10]
    return 'G' + hashlib.sha256('|'.join(('core3', r['intent_id'], r['language'], r['answer'])).encode()).hexdigest()[:10]
def place(g):
    x = h('split|' + g) % 100
    return 'train' if x < 70 else 'val' if x < 85 else 'test'

def main():
    gold = list(csv.DictReader(open('02_Data/04_Gold/hotel_faq_gold.csv', encoding='utf-8-sig')))
    prev, gsplit = {}, {}
    for s in SPLITS:
        p = f'{D}/{s}.csv'
        if os.path.exists(p):
            for r in csv.DictReader(open(p, encoding='utf-8')):
                prev[r['faq_id']] = (s, r['group_id']); gsplit[r['group_id']] = s
    corpus = defaultdict(list)
    for l in open('04_RAG/corpus.jsonl', encoding='utf-8'):
        c = json.loads(l); corpus[c['doc_id']].append(c['text'])
    out = {s: [] for s in SPLITS}
    kept = placed = 0
    for r in gold:
        if r['faq_id'] in prev:
            s, g = prev[r['faq_id']]; kept += 1
        else:
            g = new_group(r); s = gsplit.setdefault(g, place(g)); placed += 1
        row = {c: r.get(c, '') for c in COLS}; row['group_id'] = g
        out[s].append(row)
    for s in SPLITS:
        with open(f'{D}/{s}.csv', 'w', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, fieldnames=COLS); w.writeheader(); w.writerows(out[s])
        with open(f'{D}/{s}.jsonl', 'w', encoding='utf-8') as f:
            for r in out[s]:
                q = r['question']
                user = (f"Hotel information:\n{chr(10).join([chr(10) + '---' + chr(10)]).join(corpus[r['source']])}\n\nGuest question: {q}"
                        if r['source'] in corpus else f'Guest question: {q}')
                ans = r['answer_egyptian'] if r['language'] == 'Arabic-Egyptian' and r['answer_egyptian'] else r['answer']
                f.write(json.dumps({'id': r['faq_id'], 'language': r['language'], 'intent_id': r['intent_id'],
                                    'response_mode': r['response_mode'], 'requires_tool': r['requires_tool'],
                                    'messages': [{'role': 'system', 'content': SYSTEM},
                                                 {'role': 'user', 'content': user},
                                                 {'role': 'assistant', 'content': ans}]},
                                   ensure_ascii=False) + '\n')
    n = 0
    with open('04_RAG/retrieval_eval.jsonl', 'w', encoding='utf-8') as f:
        for s in SPLITS:
            for r in out[s]:
                if r['source'] not in corpus: continue
                ans = r['answer_egyptian'] if r['language'] == 'Arabic-Egyptian' and r['answer_egyptian'] else r['answer']
                f.write(json.dumps({'query_id': r['faq_id'], 'query': r['question'], 'language': r['language'],
                                    'intent_id': r['intent_id'], 'gold_doc_id': r['source'],
                                    'gold_answer': ans, 'split': s}, ensure_ascii=False) + '\n'); n += 1
    print(f'splits: {{{", ".join(f"{s}: {len(out[s])}" for s in SPLITS)}}} | kept {kept}, newly placed {placed}')
    print(f'Egyptian per split: {{{", ".join(f"{s}: {sum(r["language"]=="Arabic-Egyptian" for r in out[s])}" for s in SPLITS)}}}')
    print(f'retrieval_eval.jsonl: {n} queries | by language {dict(Counter(r["language"] for s in SPLITS for r in out[s] if r["source"] in corpus))}')

if __name__ == '__main__':
    main()
