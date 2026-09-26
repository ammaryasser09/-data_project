# HotelAI — Data Readiness Certification (v4)

## FINAL STATUS: **READY FOR DEVELOPMENT** — 9/9 gates, SYSTEM_DATE 2026-09-19

```bash
python3 06_Scripts/rebuild_all.py     # rebuild from raw inputs + audit (idempotent, byte-identical rerun)
```

| Gate | Evidence (recomputed on every run) |
|---|---|
| 1 Database integrity | PKs unique, 0 FK violations across 10 relationships, 0 invalid or impossible states |
| 2 Availability integrity | 0 conflicts among `blocks_inventory=True`, 8,848 back-to-back pairs allowed, 15/15 availability tests |
| 3 Capacity logic | RULE A consistent across rules, generator, repair, validators, KB and Gold; 0 violations |
| 4 Booking integrity | totals = rate × nights, rates within the seasonal band of the v4 price list, one payment per booking |
| 5 Gold integrity | 3,965 rows, 0 duplicates, 0 language mismatches, every row grounded in a KB document or the out-of-scope policy, Egyptian rows for all 35 intents |
| 6 Knowledge base | 44 documents / 222 sections, all covered by Gold, no non-existent room type, no editorial notes |
| 7 RAG readiness | 146 chunks from 44 documents, none empty, oversized or thin |
| 8 Project coverage | 15/15 capabilities, 6/6 booking flows, 630 conversations in 5 languages |
| 9 Validators | `validate_database` 59/59, `validate_dataset` 64/64 |

Coverage audit: 99.1%. Retrieval (BM25, no model): `retrieval_results_v4.txt`.

What changed and why: `V4_AUDIT_REPORT.md`. Every change: `07_Audits/Repair_Logs/`.
Superseded: `08_Archive/audits/06_v3_*`.

Open before relying on RAG in Arabic: run `python3 -m 09_Application.rag.evaluate --mode hybrid` (BGE-M3).
