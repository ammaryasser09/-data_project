#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Run the whole data pipeline in the only correct order, then the final audit.

    python3 06_Scripts/rebuild_all.py

  1 repair/apply_business_rules.py      raw bookings → bookings.csv (+ blocks_inventory)
  2 repair/repair_operational_v3.py     payments, requests, complaints, feedback, codes, rooms, loyalty
  3 repair/policy_update_v4.py         Gold FAQ: v4 policies and prices (repair_gold_v3.py is a completed
                                        migration, captured in 01_Raw/hotel_faq_gold_pre_v4.csv)
  4 build/merge_candidate.py            only if 02_Data/03_Candidate/ holds a CSV
  5 build/build_rag_corpus.py           03_Knowledge_Base → 04_RAG/corpus.jsonl
  6 build/build_splits.py               Gold → intent splits + retrieval_eval.jsonl
  7 generation/generate_conversations.py  conversations grounded in the tables
    generation/realistic_test_v1.py       200 realistic Egyptian test questions, facts from the tables
  8 validation/validate_availability.py (rewrites 05_Evaluation/availability_test_cases.csv)
  9 validation/final_audit.py           exit 0 = READY FOR DEVELOPMENT

Every step is idempotent: running this twice gives byte-identical data files.
"""
import glob, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
STEPS = ['repair/apply_business_rules.py', 'repair/repair_operational_v3.py', 'repair/policy_update_v4.py',
         'build/merge_candidate.py', 'build/build_rag_corpus.py', 'build/build_splits.py',
         'generation/generate_conversations.py', 'generation/realistic_test_v1.py', 'validation/validate_availability.py',
         'validation/final_audit.py']
for s in STEPS:
    if s == 'build/merge_candidate.py' and not glob.glob('02_Data/03_Candidate/*.csv'):
        print(f'-- skip {s} (no candidate file)'); continue
    print(f'== {s}')
    r = subprocess.run([sys.executable, f'06_Scripts/{s}'], capture_output=True, text=True)
    tail = [l for l in r.stdout.strip().splitlines() if l.strip()][-2:]
    print('   ' + '\n   '.join(tail))
    if r.returncode != 0:
        print(r.stderr[-2000:]); sys.exit(f'step failed: {s}')
print('\nPipeline complete.')
