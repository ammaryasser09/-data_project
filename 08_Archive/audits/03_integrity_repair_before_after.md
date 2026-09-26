> **SUPERSEDED / HISTORICAL — NOT SOURCE OF TRUTH.** Kept for audit history only. Figures here describe an earlier state of the data. See `07_Audits/Final/` for the current certification.

# Critical Data Integrity — Before / After

All figures produced by `07_Scripts/Validation/validate_database.py` and
`07_Scripts/Validation/validate_availability.py`. Source data was never modified; the
repaired copy lives at `02_Data/03_Structured/Bookings/bookings.csv`.

| Issue | Before | After | Remaining | Explanation |
|---|---|---|---|---|
| Overlapping pairs (all) | 25,039 | — | — | earlier audit reported 9,307 using adjacent-pair comparison, which undercounted; the interval rule over all pairs gives 25,039 |
| **Active booking overlaps** | **17,080 pairs** | **0** | 0 | resolved by room reassignment within the same type |
| Non-blocking overlaps | 7,959 | 7,959 | 7,959 | not defects: one side is Cancelled or No-show |
| Duplicate bookings | 0 | 0 | 0 | no same-customer, same-room, same-date pairs exist |
| **Capacity violations** | **3,563** | **3,563** | **3,563** | reclassified, not repaired — see below |
| Invalid booking states | 8,518 | **4,907** | 4,907 | 3,611 corrected deterministically, rest ambiguous |
| Invalid dates | 0 | 0 | 0 | no check-out before check-in, all dates parse |
| Orphan records / FK violations | 0 | 0 | 0 | all nine relationships intact |
| Bookings deleted | — | **0** | — | nothing was deleted |
| Availability engine tests | not runnable | **15/15** | 0 | including the back-to-back boundary case |
| No-show policy | missing | missing | **MISSING_SOURCE** | cannot be invented |

## The capacity finding

The earlier audit called this 3,563 invalid bookings. Investigation shows something else.

**In 3,563 of 3,563 cases, the adults alone fit within the room capacity.** Only the
children push the count over. Zero cases exist where adults alone exceed capacity.

That distribution cannot occur by chance. It indicates the data generator enforced
`adults <= capacity` while the knowledge base states `guests <= capacity`. Two different
business rules, and the data follows the generator's.

Classification: **D — CAPACITY DEFINITION ERROR**, not invalid bookings.

Nothing was changed. The specification forbids altering capacity, guest counts, or moving
bookings to a different room type, and the hotel's real rule is unknown. If the hotel
counts only adults toward capacity — which is common practice — then the correct violation
count is **0** and the knowledge base wording needs fixing instead.

One question to the hotel resolves 3,563 rows: *do children count toward room capacity?*

## Occupancy note

After repair the dataset runs at **90% occupancy** (100,656 room-nights demanded against
111,450 available over 743 days). Only 2 of 743 days are fully sold out. High, but the
availability engine returns correct results on it. The 3,004 unplaceable bookings are what
remains of the over-generation.

## Data generation audit — BLOCKED

All eight notebooks in `scripts/` contain `"cells": []`. They are empty. The generation
logic does not exist in the repository, so it cannot be inspected or fixed, and the data
cannot be regenerated with constraints.

Any future regeneration will reproduce the same corruption. The constraints a rebuilt
generator must enforce are documented in `05_Database/Validation/generator_constraints.md`.
