#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Retrieval evaluation on 04_RAG/retrieval_eval.jsonl, per language.

The knowledge base is written in English only, while guests ask in five languages
(English, Arabic, Egyptian Arabic, French, Russian). This script measures whether the
retriever still finds the right document for a non-English question.

    python3 06_Scripts/evaluation/evaluate_retrieval.py                 # BM25 lexical baseline, no dependencies
    python3 06_Scripts/evaluation/evaluate_retrieval.py --dense BAAI/bge-m3
        # multilingual dense retrieval; needs:  pip install sentence-transformers

Metrics are document-level (a hit = any chunk of gold_doc_id ranked in the top k):
Recall@1, Recall@3, Recall@5 and MRR@10. Use --split test for the held-out split only.
"""
import argparse, json, math, os, re
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(ROOT)
TOK = re.compile(r'[\w\u0600-\u06FF]+', re.U)
def toks(t): return [w.lower() for w in TOK.findall(t)]

class BM25:
    def __init__(self, docs, k1=1.5, b=0.75):
        self.docs = [toks(d) for d in docs]; self.k1, self.b = k1, b
        self.avg = sum(map(len, self.docs)) / len(self.docs)
        df = Counter(w for d in self.docs for w in set(d)); n = len(self.docs)
        self.idf = {w: math.log(1 + (n - c + .5) / (c + .5)) for w, c in df.items()}
        self.tf = [Counter(d) for d in self.docs]
    def scores(self, q):
        q = toks(q); out = []
        for tf, d in zip(self.tf, self.docs):
            s = 0.0
            for w in q:
                if w in tf:
                    f = tf[w]; s += self.idf[w] * f * (self.k1 + 1) / (f + self.k1 * (1 - self.b + self.b * len(d) / self.avg))
            out.append(s)
        return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dense', help='sentence-transformers model name, e.g. BAAI/bge-m3')
    ap.add_argument('--split', choices=['train', 'val', 'test'], help='evaluate one split only')
    a = ap.parse_args()
    corpus = [json.loads(l) for l in open('04_RAG/corpus.jsonl', encoding='utf-8')]
    evalq = [json.loads(l) for l in open('04_RAG/retrieval_eval.jsonl', encoding='utf-8')]
    if a.split: evalq = [q for q in evalq if q['split'] == a.split]
    texts = [c['text'] for c in corpus]; ids = [c['doc_id'] for c in corpus]
    if a.dense:
        from sentence_transformers import SentenceTransformer
        m = SentenceTransformer(a.dense)
        C = m.encode(texts, normalize_embeddings=True, batch_size=32)
        Q = m.encode([q['query'] for q in evalq], normalize_embeddings=True, batch_size=64, show_progress_bar=True)
        score = lambda i, q: (Q[i] @ C.T).tolist()
        name = a.dense
    else:
        bm = BM25(texts); score = lambda i, q: bm.scores(q['query']); name = 'BM25 (lexical baseline)'
    agg = defaultdict(lambda: Counter())
    for i, q in enumerate(evalq):
        s = score(i, q)
        ranked, seen = [], set()
        for j in sorted(range(len(s)), key=lambda j: -s[j]):
            if ids[j] not in seen: seen.add(ids[j]); ranked.append(ids[j])
            if len(ranked) == 10: break
        r = ranked.index(q['gold_doc_id']) + 1 if q['gold_doc_id'] in ranked else None
        for L in (q['language'], 'ALL'):
            c = agg[L]; c['n'] += 1
            for k in (1, 3, 5): c[f'r{k}'] += bool(r and r <= k)
            c['mrr'] += 1 / r if r else 0
    print(f'Retriever: {name} | corpus {len(corpus)} chunks / {len(set(ids))} docs | queries {len(evalq)}')
    print(f'{"language":18} {"n":>5} {"R@1":>6} {"R@3":>6} {"R@5":>6} {"MRR@10":>7}')
    for L in ['English', 'French', 'Russian', 'Arabic', 'Arabic-Egyptian', 'ALL']:
        c = agg.get(L)
        if not c: continue
        n = c['n']; print(f'{L:18} {n:>5} {c["r1"]/n:6.3f} {c["r3"]/n:6.3f} {c["r5"]/n:6.3f} {c["mrr"]/n:7.3f}')

if __name__ == '__main__':
    main()
