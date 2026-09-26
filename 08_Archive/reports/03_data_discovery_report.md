> **SUPERSEDED / HISTORICAL — NOT SOURCE OF TRUTH.** Kept for audit history only. Figures here describe an earlier state of the data. See `07_Audits/Final/` for the current certification.

# Data Discovery Report

Complete inventory: **107 files** across 25 directories.

| Path | Size | Content |
|---|---|---|
| `01_Docs/Architecture/DATA_ROUTING_MATRIX.md` | 2 KB |  |
| `01_Docs/Architecture/booking_state_machine.md` | 2 KB |  |
| `01_Docs/Source_of_Truth/SOURCE_OF_TRUTH.md` | 2 KB |  |
| `02_Data/03_Structured/Bookings/bookings.csv` | 1833 KB | 20000 rows |
| `02_Data/03_Structured/Customers/customers.csv` | 1030 KB | 10000 rows |
| `02_Data/03_Structured/Customers/loyalty_members.csv` | 4 KB | 100 rows |
| `02_Data/03_Structured/FAQ/conversations_408.csv` | 341 KB | 408 rows |
| `02_Data/03_Structured/FAQ/conversations_booking_48.csv` | 48 KB | 48 rows |
| `02_Data/03_Structured/Payments/payments.csv` | 1649 KB | 20000 rows |
| `02_Data/03_Structured/Requests/complaint_tickets.csv` | 8 KB | 75 rows |
| `02_Data/03_Structured/Requests/customer_feedback.csv` | 489 KB | 5000 rows |
| `02_Data/03_Structured/Requests/customer_requests.csv` | 1480 KB | 15000 rows |
| `02_Data/03_Structured/Requests/special_requests_history.csv` | 17 KB | 125 rows |
| `02_Data/03_Structured/Rooms/room_types.csv` | 1 KB | 6 rows |
| `02_Data/03_Structured/Rooms/rooms.csv` | 4 KB | 150 rows |
| `02_Data/03_Structured/Services/discount_codes.csv` | 1 KB | 25 rows |
| `02_Data/03_Structured/Services/pricing_tiers.csv` | 1 KB | 10 rows |
| `02_Data/03_Structured/Services/services.csv` | 1 KB | 8 rows |
| `02_Data/04_Gold/hotel_faq_3497_gold.csv` | 1347 KB | 3497 rows |
| `02_Data/08_Archive/bookings_original.csv` | 1832 KB | 20000 rows |
| `02_Data/08_Archive/customer_feedback_original.csv` | 489 KB | 5000 rows |
| `02_Data/08_Archive/customer_requests_original.csv` | 1480 KB | 15000 rows |
| `02_Data/08_Archive/customers_original.csv` | 1030 KB | 10000 rows |
| `02_Data/08_Archive/edge_cases_96.csv` | 56 KB | 96 rows |
| `02_Data/08_Archive/egyptian_dialect_86.csv` | 49 KB | 85 rows |
| `02_Data/08_Archive/hotel_faq_1344_original_gold.csv` | 458 KB | 1344 rows |
| `02_Data/08_Archive/out_of_scope_100.csv` | 56 KB | 100 rows |
| `02_Data/08_Archive/payments_original.csv` | 1649 KB | 20000 rows |
| `02_Data/08_Archive/rooms_policies_services_480.csv` | 298 KB | 480 rows |
| `02_Data/08_Archive/transaction_path_384.csv` | 230 KB | 384 rows |
| `04_RAG/Chunks/corpus.jsonl` | 76 KB | 165 lines |
| `04_RAG/Evaluation/retrieval_eval.jsonl` | 613 KB | 1456 lines |
| `05_Database/Validation/generator_constraints.md` | 1 KB |  |
| `06_Audits/Coverage/CRITICAL_DATA_INTEGRITY_BEFORE_AFTER.md` | 3 KB |  |
| `06_Audits/Coverage/FINAL_BEFORE_AFTER_REPORT.md` | 2 KB |  |
| `06_Audits/Coverage/audit_before_repair.md` | 26 KB |  |
| `06_Audits/Coverage/final_audit_result.txt` | 3 KB | 71 lines |
| `06_Audits/Data_Quality/REVIEW_REPORT.md` | 4 KB |  |
| `06_Audits/Data_Quality/validation_availability.txt` | 2 KB | 68 lines |
| `06_Audits/Data_Quality/validation_database.txt` | 2 KB | 64 lines |
| `06_Audits/Data_Quality/validation_dataset.txt` | 3 KB | 79 lines |
| `06_Audits/Gold_Certification/FINAL_HASHES.txt` | 1 KB | 11 lines |
| `06_Audits/Gold_Certification/gold_hashes.txt` | 1 KB | 7 lines |
| `06_Audits/Repair_Logs/AFTER_REPAIR_HASHES.txt` | 1 KB | 4 lines |
| `06_Audits/Repair_Logs/BEFORE_REPAIR_HASHES.txt` | 1 KB | 7 lines |
| `06_Audits/Repair_Logs/booking_conflict_resolution.csv` | 5012 KB | 25039 rows |
| `06_Audits/Repair_Logs/booking_integrity_repair_log.csv` | 8616 KB | 26119 rows |
| `06_Audits/Repair_Logs/final_repair_log.csv` | 8616 KB | 26119 rows |
| `06_Audits/Repair_Logs/repair_log.csv` | 2781 KB | 10830 rows |
| `06_Audits/Repair_Logs/repair_summary.md` | 3 KB |  |
| `07_Scripts/Repair/repair_booking_integrity.py` | 12 KB |  |
| `07_Scripts/Validation/final_audit.py` | 15 KB |  |
| `07_Scripts/Validation/validate_availability.py` | 9 KB |  |
| `07_Scripts/Validation/validate_database.py` | 7 KB |  |
| `07_Scripts/Validation/validate_dataset.py` | 13 KB |  |
| `08_Evaluation/Intent/label_map.json` | 2 KB |  |
| `08_Evaluation/Intent/test.csv` | 209 KB | 535 rows |
| `08_Evaluation/Intent/test.jsonl` | 1136 KB | 535 lines |
| `08_Evaluation/Intent/train.csv` | 934 KB | 2373 rows |
| `08_Evaluation/Intent/train.jsonl` | 5039 KB | 2373 lines |
| `08_Evaluation/Intent/val.csv` | 223 KB | 589 rows |
| `08_Evaluation/Intent/val.jsonl` | 1212 KB | 589 lines |
| `08_Evaluation/Test_Data/availability_test_cases.csv` | 1 KB | 15 rows |
| `09_Archive/Old_Versions/FINAL_CERTIFICATION.txt` | 1 KB | 42 lines |
| `09_Archive/Old_Versions/coverage_matrix.csv` | 1 KB | 34 rows |
| `09_Archive/Old_Versions/language_balance.csv` | 1 KB | 5 rows |
| `HOTELAI_DATA_FINAL_CERTIFICATION.md` | 5 KB |  |
| `03_Knowledge_Base/` | 42 KB | 40 .txt documents, 161 sections |

## Classification

| Class | Files |
|---|---|
| **Authoritative** | Gold FAQ, 10 structured tables, 40 KB documents, 408 conversations |
| **Derived** | `corpus.jsonl`, `retrieval_eval.jsonl`, intent splits — regenerate after source edits |
| **Archived** | `02_Data/08_Archive/` (original 1,344 Gold, 5 pre-repair tables, 5 by-layer copies) |
| **Obsolete** | `09_Archive/Old_Versions/` (superseded certification and coverage files) |
| **Empty / unusable** | 8 generator notebooks in the source repo, all `"cells": []` |

## Dependencies

Three validation scripts read the data. All paths were updated after reorganization and all
three pass, so no reference is broken:

```
07_Scripts/Validation/validate_dataset.py      → Gold, KB, corpus, splits, conversations
07_Scripts/Validation/validate_database.py     → all 10 structured tables
07_Scripts/Validation/validate_availability.py → bookings, rooms, room_types, repair log
07_Scripts/Validation/final_audit.py           → everything, recomputed from zero
07_Scripts/Repair/repair_booking_integrity.py  → archive → structured
```
