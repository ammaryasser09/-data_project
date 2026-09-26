#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build 04_RAG/corpus.jsonl from 03_Knowledge_Base/*.txt. Run after any KB edit.

One chunk per numbered section. Each chunk starts with "Nile Pearl Hotel / <DOC TITLE> /
<section>" so a retrieved chunk carries its own context. Fixes over the previous corpus:
  * the doc title the KB files repeat before every section is a separator, not content;
    it used to be glued to the END of the previous chunk
  * a leading "Overview" line is no longer repeated as both header and body
  * a section shorter than MIN_BODY characters is merged into its neighbour in the same
    document instead of becoming a near-empty chunk

    python3 06_Scripts/build/build_rag_corpus.py
"""
import json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(ROOT)
KB, OUT, MIN_BODY = '03_Knowledge_Base', '04_RAG/corpus.jsonl', 120
SEC = re.compile(r'^\s*\d+\.\s+\S')

def sections(path):
    lines = open(path, encoding='utf-8').read().split('\n')
    title = lines[1].strip()
    body = [l.rstrip() for l in lines[2:] if l.strip() != title]
    out, name, buf = [], None, []
    for l in body:
        if SEC.match(l):
            if name or any(x.strip() for x in buf): out.append((name, buf))
            name, buf = l.strip(), []
        else:
            buf.append(l)
    out.append((name, buf))
    res = []
    for name, buf in out:
        text = '\n'.join(buf).strip()
        if name is None:                       # content before the first numbered section
            first, _, rest = text.partition('\n')
            name, text = (first.strip(), rest.strip()) if len(first) < 40 and first.strip() else ('Overview', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        if text: res.append([name, text])
    return title, res

def main():
    chunks = []
    for fn in sorted(f for f in os.listdir(KB) if f.endswith('.txt')):
        title, secs = sections(f'{KB}/{fn}')
        merged = []
        for name, text in secs:
            if merged and (len(text) < MIN_BODY or len(merged[-1][1]) < MIN_BODY):
                merged[-1][0] += ' + ' + name
                merged[-1][1] += f'\n\n{name}\n\n{text}'
            else:
                merged.append([name, text])
        for i, (name, text) in enumerate(merged):
            full = f'Nile Pearl Hotel\n{title}\n{name}\n\n{text}'
            chunks.append({'chunk_id': f'{fn[:-4]}::{i:02d}', 'doc_id': fn, 'doc_title': title,
                           'section': name, 'language': 'English', 'text': full,
                           'char_len': len(full)})
    with open(OUT, 'w', encoding='utf-8') as f:
        for c in chunks: f.write(json.dumps(c, ensure_ascii=False) + '\n')
    bodies = [len(c['text'].split('\n\n', 1)[1]) for c in chunks]
    print(f'{OUT}: {len(chunks)} chunks from {len({c["doc_id"] for c in chunks})} documents | '
          f'body chars min {min(bodies)} / max {max(bodies)} | full chunk max {max(c["char_len"] for c in chunks)}')

if __name__ == '__main__':
    main()
