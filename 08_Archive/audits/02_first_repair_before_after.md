> **SUPERSEDED / HISTORICAL — NOT SOURCE OF TRUTH.** Kept for audit history only. Figures here describe an earlier state of the data. See `07_Audits/Final/` for the current certification.

# Before / After Report

Measured on the delivered package before repair and on this structure after repair.
Every figure is reproducible by the two validation scripts.

| Metric | Before | After | Δ | How calculated |
|---|---|---|---|---|
| Operational tables present | 5 of 10 | **10 of 10** | +5 | file count under `02_Data/03_Structured/` |
| Dangling foreign keys | 3 tables unresolvable | **0** | fixed | `validate_database.py` §3 |
| Room double-booking conflicts | **9,307** | **0** (2,676 flagged) | −9,307 | overlapping date ranges per `room_id` among Confirmed/Completed |
| Availability computable | **NO** | **YES** | fixed | `validate_database.py` §9 returns 20/150 free on a probe date |
| Conversations | 360 | **408** | +48 | row count |
| Intents with conversations | 6 of 34 | **12** | +6 | distinct `intent_id` in conversation files |
| Booking-flow conversations | **0** | **48** | +48 | `conversations_booking_48.csv` |
| Dialogue role patterns | 2 | **6** | +4 | distinct role sequences |
| Dataset checks passing | 49/49 | **49/49** | — | `validate_dataset.py` |
| Database checks passing | not runnable | **27/27** | new | `validate_database.py` |
| Stale metadata files | 5 | **0 active** | archived | moved to `09_Archive/Old_Versions/` |
| Gold rows | 3,497 | **3,497** | unchanged | Gold not regenerated; SHA recorded |

## Coverage scores, recalculated

Scores use the same method as the pre-repair audit so they are comparable.

| Metric | Before | After | Basis |
|---|---|---|---|
| Functional coverage | 62% | **86%** | 18 of 21 requirements COMPLETE (was 13), 0 MISSING (was 4) |
| Backend readiness | 40% | **95%** | 7 of 7 capabilities supported; 2,676 flagged bookings are the residual |
| Reservation coverage | 35% | **88%** | FAQ + conversations + tables all present |
| Conversational coverage | 25% | **62%** | 12 of 34 intents (was 6); booking, cancellation, payment flows added; still no conversations for 22 intents |
| Data consistency | 97% | **99%** | double-booking removed; room-type decision still an assumption |
| RAG readiness | 88% | **88%** | unchanged — no KB repair was possible without inventing facts |
| Knowledge-base coverage | 80% | **80%** | unchanged — 6 required facts still absent, see blockers |
| Voice readiness | 55% | **55%** | unchanged — no ASR data, 78 enumerated answers |
| Intent coverage | 75% | **75%** | unchanged — 7.6:1 imbalance not addressed |
| Language coverage | 95% | **95%** | unchanged |
| Data quality | 93% | **96%** | database now validates; capacity issues flagged not hidden |

**Not improved, and why:** knowledge-base gaps (phone, email, address, room size, no-show
policy) cannot be closed without inventing hotel facts, which Rule 1 forbids. Intent
imbalance and ASR data were deprioritised below the two CRITICAL gaps.
