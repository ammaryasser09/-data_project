> **SUPERSEDED / HISTORICAL — NOT SOURCE OF TRUTH.** Replaced by the v3 audit (`07_Audits/Final/V3_AUDIT_REPORT.md`). Kept as the record of the v2 certification.

# Final Structure Cleanup Report

## FINAL STATUS: STRUCTURE CLEAN — READY

---

## Before

| | Count |
|---|---|
| Files | 121 |
| Folders | 42 |
| Empty folders | 4 |
| Byte-identical duplicate pairs | 4 |
| Row-level duplicates of Gold | 5 files, 1,145 rows |
| Superseded datasets | 2 (candidate already promoted, 48-conversation copy) |
| Stale reports | 9 (four before/after reports, two certifications, discovery report, review, summary) |
| Junk | 1 (error output from a script that does not exist) |
| **Active scripts reading from the archive** | **3** |
| Separate archive locations | 2 (`02_Data/08_Archive`, `09_Archive`) |
| Filenames carrying row counts | 3 |

## Actions

**Deleted — 13 files, each proven redundant before removal**

| File | Proof |
|---|---|
| customers, payments, customer_requests, customer_feedback `_original.csv` | SHA-256 identical to the active table; never modified, so no history to keep |
| edge_cases_96, egyptian_dialect_86, out_of_scope_100, rooms_policies_services_480, transaction_path_384 | Every row verified present in Gold — 1,145 of 1,145 |
| coverage_fill_candidate.csv | 40 of 40 rows already promoted to Gold |
| conversations_booking_48_superseded.csv | 48 of 48 conversations present in the active set |
| validation_final_audit.txt | Contained only a "file not found" error |
| language_balance.csv, old coverage_matrix.csv | Figures from a superseded package, reproducible by `coverage_audit.py` |
| 5 validation output snapshots, 3 superseded hash files | Regenerable; replaced by one current `validation_results.txt` and `final_hashes.txt` |
| 4 empty folders | Nothing inside |

**Moved** — 57 operations into the new structure. Full list in the appendix.

**Renamed**

| Before | After | Why |
|---|---|---|
| `hotel_faq_3557_gold.csv` | `hotel_faq_gold.csv` | Count in the name changed with every addition and broke every script |
| `conversations_424.csv` | `conversations_gold.csv` | Same |
| `hotel_faq_1344_original_gold.csv` | `hotel_faq_1344_baseline.csv` | Moved out of the archive — `final_audit.py` depends on it |
| `bookings_original.csv` | `01_Raw/bookings_raw.csv` | Moved out of the archive — the repair pipeline reads it |
| `final_repair_log.csv` | `repair_log.csv` | One log, no "final" |
| `booking_state_machine.md` | `BOOKING_STATE_MACHINE.md` | Consistent with the other docs |

**Folders merged**

- Seven entity subfolders under `03_Structured/` held one to four files each → one `02_Operational/`
- `02_Data/08_Archive/` and `09_Archive/` → one `08_Archive/`
- `06_Audits/` with five subfolders → `07_Audits/` with three

**References updated** — 12 files, 93 path references, plus the dynamic `f'{S}/Sub/…'`
paths and two `glob` patterns that no longer need to exist now that names are stable.

## Defect found during cleanup

**The repair pipeline was not reproducible.** Re-running `apply_business_rules.py` from
raw produced a different `bookings.csv`: 1,378 rows had a different `room_id`.

Cause: the step that realigns non-occupying bookings to a room of their type used Python's
built-in `hash()`, which is randomised per process for strings. Every run picked
different rooms.

Fix: replaced with a SHA-256 of the booking ID. Three consecutive runs now produce an
identical file. All 1,378 affected rows were Cancelled, No-show, or unplaceable, so none
took part in the occupancy index and availability results were never affected.

This was only found because restructuring required proving the pipeline still worked from
its raw input.

## After

| | Count |
|---|---|
| Files | 105 |
| Folders | 23 |
| Archive files | 13, each bannered `SUPERSEDED / HISTORICAL — NOT SOURCE OF TRUTH` |
| Empty folders | 0 |
| Empty files | 0 |
| Cache / temp files | 0 |
| Duplicate active files | **0** |
| Broken references | **0** |
| Active scripts reading from the archive | **0** |
| Files claiming to be the final certification | **1** |

## Validation after cleanup

| Script | Result |
|---|---|
| `validate_dataset.py` | 51/51 |
| `validate_database.py` | 27/27 |
| `validate_availability.py` | 15/15 |
| `final_audit.py` | 8/8 — READY FOR DEVELOPMENT |
| `coverage_audit.py` | 99.1% — HIGH |
| `generate_bookings.py` | 8/8 |
| `apply_business_rules.py` | reproducible — identical output across 3 runs |

Data preserved: 72 data files carried over byte-identical; every change is accounted for
above.

## Appendix — moves

```
01_Docs/Architecture/BUSINESS_RULES.md → 01_Docs/BUSINESS_RULES.md
01_Docs/Architecture/DATA_ROUTING_MATRIX.md → 01_Docs/DATA_ROUTING_MATRIX.md
01_Docs/Architecture/booking_state_machine.md → 01_Docs/BOOKING_STATE_MACHINE.md
01_Docs/Source_of_Truth/SOURCE_OF_TRUTH.md → 01_Docs/SOURCE_OF_TRUTH.md
05_Database/Validation/generator_constraints.md → 01_Docs/GENERATOR_CONSTRAINTS.md
02_Data/08_Archive/bookings_original.csv → 02_Data/01_Raw/bookings_raw.csv
02_Data/03_Structured/Bookings/bookings.csv → 02_Data/02_Operational/bookings.csv
02_Data/03_Structured/Customers/customers.csv → 02_Data/02_Operational/customers.csv
02_Data/03_Structured/Customers/loyalty_members.csv → 02_Data/02_Operational/loyalty_members.csv
02_Data/03_Structured/Payments/payments.csv → 02_Data/02_Operational/payments.csv
02_Data/03_Structured/Requests/complaint_tickets.csv → 02_Data/02_Operational/complaint_tickets.csv
02_Data/03_Structured/Requests/customer_feedback.csv → 02_Data/02_Operational/customer_feedback.csv
02_Data/03_Structured/Requests/customer_requests.csv → 02_Data/02_Operational/customer_requests.csv
02_Data/03_Structured/Requests/special_requests_history.csv → 02_Data/02_Operational/special_requests_history.csv
02_Data/03_Structured/Rooms/room_types.csv → 02_Data/02_Operational/room_types.csv
02_Data/03_Structured/Rooms/rooms.csv → 02_Data/02_Operational/rooms.csv
02_Data/03_Structured/Services/services.csv → 02_Data/02_Operational/services.csv
02_Data/03_Structured/Services/pricing_tiers.csv → 02_Data/02_Operational/pricing_tiers.csv
02_Data/03_Structured/Services/discount_codes.csv → 02_Data/02_Operational/discount_codes.csv
02_Data/04_Gold/hotel_faq_3557_gold.csv → 02_Data/04_Gold/hotel_faq_gold.csv
02_Data/08_Archive/hotel_faq_1344_original_gold.csv → 02_Data/04_Gold/hotel_faq_1344_baseline.csv
02_Data/03_Structured/FAQ/conversations_424.csv → 02_Data/04_Gold/conversations_gold.csv
03_Knowledge_Base/*.txt (41) → 03_Knowledge_Base/
04_RAG/Chunks/corpus.jsonl → 04_RAG/corpus.jsonl
04_RAG/Evaluation/retrieval_eval.jsonl → 04_RAG/retrieval_eval.jsonl
08_Evaluation/Intent/train.csv → 05_Evaluation/intent/train.csv
08_Evaluation/Intent/train.jsonl → 05_Evaluation/intent/train.jsonl
08_Evaluation/Intent/val.csv → 05_Evaluation/intent/val.csv
08_Evaluation/Intent/val.jsonl → 05_Evaluation/intent/val.jsonl
08_Evaluation/Intent/test.csv → 05_Evaluation/intent/test.csv
08_Evaluation/Intent/test.jsonl → 05_Evaluation/intent/test.jsonl
08_Evaluation/Intent/label_map.json → 05_Evaluation/intent/label_map.json
08_Evaluation/Test_Data/availability_test_cases.csv → 05_Evaluation/availability_test_cases.csv
07_Scripts/Generation/generate_bookings.py → 06_Scripts/generation/generate_bookings.py
07_Scripts/Repair/apply_business_rules.py → 06_Scripts/repair/apply_business_rules.py
07_Scripts/Validation/validate_dataset.py → 06_Scripts/validation/validate_dataset.py
07_Scripts/Validation/validate_database.py → 06_Scripts/validation/validate_database.py
07_Scripts/Validation/validate_availability.py → 06_Scripts/validation/validate_availability.py
07_Scripts/Validation/final_audit.py → 06_Scripts/validation/final_audit.py
07_Scripts/Validation/coverage_audit.py → 06_Scripts/validation/coverage_audit.py
HOTELAI_FINAL_DATA_READINESS_AND_COVERAGE_CERTIFICATION.md → 07_Audits/Final/DATA_READINESS_CERTIFICATION.md
06_Audits/Coverage/coverage_matrix.csv → 07_Audits/Coverage/coverage_matrix.csv
06_Audits/Consistency/CONSISTENCY_MATRIX.md → 07_Audits/Coverage/CONSISTENCY_MATRIX.md
06_Audits/Repair_Logs/final_repair_log.csv → 07_Audits/Repair_Logs/repair_log.csv
06_Audits/Repair_Logs/BEFORE_RULES_HASHES.txt → 07_Audits/Repair_Logs/before_repair_hashes.txt
06_Audits/Repair_Logs/AFTER_RULES_HASHES.txt → 07_Audits/Repair_Logs/after_repair_hashes.txt
06_Audits/Gold_Certification/FINAL_HASHES.txt → 07_Audits/Final/final_hashes.txt
06_Audits/Coverage/audit_before_repair.md → 08_Archive/audits/01_initial_coverage_audit.md
06_Audits/Coverage/FINAL_BEFORE_AFTER_REPORT.md → 08_Archive/audits/02_first_repair_before_after.md
06_Audits/Coverage/CRITICAL_DATA_INTEGRITY_BEFORE_AFTER.md → 08_Archive/audits/03_integrity_repair_before_after.md
06_Audits/Coverage/FINAL_DATA_BEFORE_AFTER_REPORT.md → 08_Archive/audits/04_readiness_before_after.md
06_Audits/Data_Quality/REVIEW_REPORT.md → 08_Archive/audits/00_package_review.md
06_Audits/Repair_Logs/repair_summary.md → 08_Archive/audits/02_first_repair_summary.md
09_Archive/Old_Versions/FINAL_CERTIFICATION.txt → 08_Archive/reports/00_package_certification.txt
06_Audits/Repair_Logs/booking_conflict_resolution.csv → 08_Archive/audits/03_booking_conflict_classification.csv
07_Scripts/Repair/repair_booking_integrity.py → 08_Archive/scripts/repair_booking_integrity_v2.py
01_Docs/Data_Dictionary/DATA_DISCOVERY_REPORT.md → 08_Archive/reports/03_data_discovery_report.md
```
