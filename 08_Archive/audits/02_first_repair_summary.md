> **SUPERSEDED / HISTORICAL — NOT SOURCE OF TRUTH.** Kept for audit history only. Figures here describe an earlier state of the data. See `07_Audits/Final/` for the current certification.

# Repair Summary

## Files created

| Path | What |
|---|---|
| `02_Data/03_Structured/Bookings/bookings.csv` | 20,000 bookings, 10,830 room reassignments |
| `02_Data/03_Structured/Customers/customers.csv` | 10,000, copied unmodified |
| `02_Data/03_Structured/Payments/payments.csv` | 20,000, copied unmodified |
| `02_Data/03_Structured/Requests/customer_requests.csv` | 15,000, copied unmodified |
| `02_Data/03_Structured/Requests/customer_feedback.csv` | 5,000, copied unmodified |
| `02_Data/03_Structured/FAQ/conversations_booking_48.csv` | 48 new booking conversations |
| `02_Data/03_Structured/FAQ/conversations_408.csv` | merged conversation set |
| `06_Audits/Repair_Logs/repair_log.csv` | 10,830 rows, one per reassignment |
| `06_Audits/Data_Quality/booking_integrity_issues.csv` | 6,239 rows requiring human review |
| `07_Scripts/Validation/validate_dataset.py` | 49 checks |
| `07_Scripts/Validation/validate_database.py` | 27 checks |
| `01_Docs/Architecture/DATA_ROUTING_MATRIX.md` | RAG vs DB vs Tool |
| `01_Docs/Source_of_Truth/SOURCE_OF_TRUTH.md` | authoritative file per category |
| `06_Audits/Gold_Certification/gold_hashes.txt` | SHA256 of protected Gold |

## Files changed

**`bookings.csv` only.** 10,830 rows had `room_id` reassigned to a free room of the same
type, first-fit by check-in date. No other column was touched, no booking was deleted, and
the original is preserved at `02_Data/08_Archive/bookings_original.csv`.

**Reason:** 9,307 date-range conflicts meant the same physical room was occupied by
overlapping confirmed bookings. Any availability query built on that data returns nonsense.
Reassignment is deterministic and preserves every booking.

## Files moved

All data files were relocated into the target structure. Both validation scripts were
rewritten against the new paths and both pass, so no reference is broken.

## Files archived

`02_Data/08_Archive/` — the original 1,344 Gold FAQ, five original operational tables,
five by-layer FAQ copies.
`09_Archive/Old_Versions/` — `FINAL_CERTIFICATION.txt`, `coverage_matrix.csv`,
`language_balance.csv`, superseded because their figures no longer match the data.

## Files NOT changed

`hotel_faq_3497_gold.csv` — no defect was proven, so Gold was left intact. SHA recorded.
`03_Knowledge_Base/*.txt` — no repair possible without inventing hotel facts.

## REQUIRES_HUMAN_REVIEW

| Issue | Count | Why not repaired |
|---|---|---|
| Bookings exceeding room capacity | 3,563 | Upgrading changes the price and the financial record. A data decision, not a data error. |
| Active bookings that cannot be placed | 2,676 | Demand exceeds the 150-room inventory. Either the bookings or the room list is wrong; both are source data. |

Both are listed row by row in `06_Audits/Data_Quality/booking_integrity_issues.csv`.

## BLOCKED_BY_MISSING_SOURCE

Rule 1 forbids inventing hotel facts. These stay open:

| Missing | Needed for |
|---|---|
| Hotel phone number | Customer service, callback, escalation |
| Hotel email | Written complaints |
| Street address | "Where exactly are you?" |
| Website | Online booking referral |
| Room size in m² | Pre-booking questions |
| **No-show policy** | 1,004 bookings carry status `No-show` and the hotel has no documented policy for them |
| Tax and fee breakdown | Quoted totals may be incomplete |

The no-show gap is the sharpest: the database records the event, the knowledge base cannot
explain it, so the agent has no answer for 1,004 real cases.
