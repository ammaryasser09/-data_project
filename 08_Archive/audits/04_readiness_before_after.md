> **SUPERSEDED / HISTORICAL — NOT SOURCE OF TRUTH.** Kept for audit history only. Figures here describe an earlier state of the data. See `07_Audits/Final/` for the current certification.

# Final Data — Before / After

Every figure recomputed from zero by `07_Scripts/Validation/final_audit.py`. No number is
carried forward from an earlier audit.

| Metric | Before | After | Status |
|---|---|---|---|
| Active booking conflicts | 17,080 pairs | **0** | **RESOLVED** |
| Back-to-back pairs wrongly counted as conflicts | (undetermined) | **9,352 correctly allowed** | **VERIFIED** |
| Capacity violations (Rule B) | 3,563 | 3,563 | **BLOCKED_BY_MISSING_BUSINESS_RULE** |
| Capacity violations (Rule A) | 0 | **0** | data satisfies Rule A exactly |
| Invalid dates | 0 | **0** | PASS |
| Nights ≠ date difference | 0 | **0** | PASS |
| Orphan records / FK violations | 3 tables unusable | **0 across 10 relationships** | **RESOLVED** |
| Duplicate primary keys | 0 | **0** | PASS |
| Duplicate bookings | 0 | **0** | PASS |
| Impossible booking states | 8,518 | **0** | **RESOLVED** (3,611 corrected) |
| Stale booking states | — | 4,907 | **REQUIRES_HUMAN_REVIEW** |
| Bookings deleted | — | **0** | nothing destroyed |
| Gold failures | 0 | **0** | 3,497 rows, all gates pass |
| Gold language mismatches | 27 | **0** | **RESOLVED** |
| Knowledge base documents uncovered | 31 of 40 | **0** | **RESOLVED** |
| Documents citing non-existent room types | 4 | **0** | **RESOLVED** |
| Critical customer-facing facts missing | 6 | **4** | **MISSING_KNOWLEDGE_SOURCE** |
| Availability test failures | not runnable | **0 of 15** | **RESOLVED** |
| Conversations | 360 | **408** | improved |
| Intents with conversation data | 6 | **12** | improved |
| Booking flows with conversations | 0 of 6 | **6 of 6** | **RESOLVED** |

## Corrections to earlier audits

Two numbers this project reported earlier were wrong and are corrected here:

**9,307 booking conflicts** — produced by comparing only adjacent bookings per room. The
interval rule across all pairs gives 25,039 overlapping pairs, of which **17,080** are true
conflicts between two room-blocking bookings. The original figure understated the problem
by roughly half.

**3,563 "capacity violations"** — these are not violations. In all 3,563 cases the adults
fit within capacity and only the children exceed it. Rule A violations: **0**. This is a
rule mismatch, not corrupt data.

## The repair-order bug, independently verified

A previous repair converted `No-show` → `Confirmed` **after** assigning rooms, turning
non-blocking records into blocking ones with no room allocated. That left 654 overlaps.

Verified independently by inspecting the script source: the state-machine step is now
`STEP 1b`, positioned before both the classification step and the assignment step, and the
assignment step reads `booking_status` from the already-corrected records. The final audit
independently recomputes conflicts from the output data and finds **0**.
