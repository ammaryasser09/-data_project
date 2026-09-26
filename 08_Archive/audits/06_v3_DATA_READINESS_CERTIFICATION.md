> **SUPERSEDED / HISTORICAL — NOT SOURCE OF TRUTH.** Replaced by the v4 audit (`07_Audits/Final/V4_AUDIT_REPORT.md`). Kept as the record of v3.

# HotelAI — Data Readiness Certification (v3)

## FINAL STATUS: **READY FOR DEVELOPMENT** — 9/9 gates, SYSTEM_DATE 2026-09-19

```bash
python3 06_Scripts/rebuild_all.py     # rebuild from raw inputs + audit (idempotent)
```

| Gate | Evidence (recomputed on every run) |
|---|---|
| 1 Database integrity | PKs unique, 0 FK violations, 0 impossible or stale statuses |
| 2 Availability integrity | 0 conflicts among `blocks_inventory=True`, 8,848 back-to-back pairs allowed, 15/15 availability tests |
| 3 Capacity logic | RULE A implemented in rules, generator, repair, validators, KB and Gold; 0 violations |
| 4 Booking integrity | totals = rate × nights, rates within the seasonal band, one payment per booking |
| 5 Gold integrity | 3,869 rows, 0 duplicates, 0 language mismatches, every row grounded in a KB document (or the out-of-scope policy), Egyptian rows for all 35 intents |
| 6 Knowledge base | 41 documents, every one covered by Gold, no non-existent room type, no editorial notes |
| 7 RAG readiness | 138 chunks from 41 documents, none empty, oversized or thin |
| 8 Project coverage | 15/15 capabilities, 6/6 booking flows, conversations in 5 languages |
| 9 Validators | `validate_database` 52/52, `validate_dataset` 64/64 |

Coverage audit: 99.1% (remaining partials are runtime logic: live availability, live occupancy, tool execution).

What changed and why: `V3_AUDIT_REPORT.md`. Every change: `07_Audits/Repair_Logs/`.
Superseded v2 certification: `08_Archive/audits/05_v2_DATA_READINESS_CERTIFICATION.md`.

Open item before relying on RAG in Arabic: run
`06_Scripts/evaluation/evaluate_retrieval.py --dense BAAI/bge-m3` (see report §3).
