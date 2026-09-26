# -*- coding: utf-8 -*-
"""Paths and retrieval settings. Everything is relative to the project root."""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CORPUS = os.path.join(ROOT, '04_RAG', 'corpus.jsonl')                 # KB chunks
FAQ = os.path.join(ROOT, '04_RAG', 'retrieval_eval.jsonl')            # FAQ questions + split
OPS = os.path.join(ROOT, '02_Data', '02_Operational')                 # database tables (CSV)
INDEX_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'index')

DENSE_MODEL = 'BAAI/bge-m3'     # multilingual: Arabic, Egyptian, English, French, Russian
TOP_DOCS = 3                    # documents passed to the LLM
CHUNKS_PER_DOC = 2              # best chunks taken from each document
FAQ_EXAMPLES = 3                # similar answered questions shown to the LLM
RRF_K = 60                      # reciprocal-rank-fusion constant
