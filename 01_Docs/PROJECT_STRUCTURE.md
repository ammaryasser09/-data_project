# Project Structure

```
HotelAI/
├── README.md
├── .gitignore
├── 01_Docs/                 how the system and data work
├── 02_Data/
│   ├── 01_Raw/              pipeline inputs, never modified
│   ├── 02_Operational/      the 13 database tables
│   ├── 03_Candidate/        intake for new FAQ rows (empty by design)
│   └── 04_Gold/             certified FAQ, conversations, protected baseline
├── 03_Knowledge_Base/       44 documents — the RAG source of truth (English)
├── 04_RAG/                  chunked corpus + retrieval ground truth
├── 05_Evaluation/           intent splits, availability cases, realistic Egyptian test set, review workbook
├── 06_Scripts/
│   ├── config.py            SYSTEM_DATE — the single frozen "today"
│   ├── rebuild_all.py       runs the whole pipeline + final audit
│   ├── repair/              stage 1 bookings, stage 2 cross-table, Gold v4 policy update
│   ├── build/               RAG corpus, splits, candidate merge
│   ├── generation/          booking generator, conversations, realistic test set, review workbook
│   ├── evaluation/          retrieval evaluation (BM25 baseline, --dense for BGE-M3)
│   ├── maintenance/         advance_system_date.py
│   └── validation/          five validators
├── 07_Audits/
│   ├── Final/               current certification, v3 report, hashes, results
│   ├── Coverage/            coverage and consistency matrices
│   └── Repair_Logs/         every change made to the data
├── 08_Archive/              historical only, never read by code
└── 09_Application/rag/      retriever (BM25 + BGE-M3 over KB + FAQ), prompt, reference tools, evaluation
```

## Pipeline

```
02_Data/01_Raw/bookings_raw.csv ─apply_business_rules.py─▶ 02_Operational/bookings.csv   (+ blocks_inventory)
02_Data/01_Raw/*_raw.csv ────────repair_operational_v3.py─▶ payments, rooms, requests, complaints,
                                                            special requests, feedback, codes, loyalty
02_Data/01_Raw/hotel_faq_gold_pre_v4.csv ─policy_update_v4.py─▶ hotel_faq_gold.csv (v4 terms, idempotent)
02_Data/03_Candidate/*.csv ──────merge_candidate.py ───────▶ hotel_faq_gold.csv
03_Knowledge_Base ───────────────build_rag_corpus.py ──────▶ 04_RAG/corpus.jsonl
hotel_faq_gold + corpus ─────────build_splits.py ──────────▶ 05_Evaluation/intent/ + 04_RAG/retrieval_eval.jsonl
operational tables ──────────────generate_conversations.py ▶ 04_Gold/conversations_gold.csv
operational tables + tools ──────realistic_test_v1.py ─────▶ 05_Evaluation/realistic_test/
```

`python3 06_Scripts/rebuild_all.py` runs all of it in this order and ends with
`final_audit.py`. Every step is idempotent.

## Where things go

| Adding | Put it in |
|---|---|
| A new hotel fact or policy | `03_Knowledge_Base/`, note it in `01_Docs/KB_CHANGELOG.md`, then `rebuild_all.py` |
| New FAQ rows | `02_Data/03_Candidate/`, then `06_Scripts/build/merge_candidate.py`, then `rebuild_all.py` |
| A new operational table | `02_Data/02_Operational/`, add its checks to `validate_database.py` |
| A validator | `06_Scripts/validation/` |
| A generator | `06_Scripts/generation/` |
| Audit output | `07_Audits/` — current only; move the superseded version to `08_Archive/audits/` |
| Application code | `09_Application/` (the RAG package is `09_Application/rag/`) |
| A correction from the Egyptian review | FAQ: `06_Scripts/repair/policy_update_v4_data.py`; conversations: `06_Scripts/generation/conv_templates_v4.py`; then `rebuild_all.py` |

## Rules

- Scripts run from the project root: `python3 06_Scripts/validation/final_audit.py`
- "Today" is `SYSTEM_DATE` from `06_Scripts/config.py`, never the machine clock
- File names do not carry row counts; counts belong in `SOURCE_OF_TRUTH.md`
- Nothing active reads from `08_Archive/`
