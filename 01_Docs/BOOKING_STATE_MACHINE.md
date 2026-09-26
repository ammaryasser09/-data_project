# Booking State Machine

Derived from the four statuses present in `bookings.csv`. The dataset carries no
`created_at`, `cancelled_at` or `checked_in_at` column, so transitions are inferred from
status plus date ranges only. That limitation shapes every repair decision below.

## States

| Status | Meaning | Blocks a room? |
|---|---|---|
| `Confirmed` | Reserved, stay not yet completed | **Yes** |
| `Completed` | Guest stayed and departed | **Yes** (for its own historical dates) |
| `Cancelled` | Reservation withdrawn before arrival | **No** |
| `No-show` | Guest did not arrive | **No** |

```
   Confirmed ──────────▶ Completed      (guest stayed)
       │
       ├──────────────▶ Cancelled       (withdrawn before arrival)
       │
       └──────────────▶ No-show         (arrival date passed, guest never came)
```

There is no `Pending` or `Checked-in` state in this schema, so neither is modelled.

## Why No-show does not block

A no-show guest did not physically occupy the room. If no-shows blocked inventory, the
hotel would lose 555 bookings' worth of sellable nights to rooms nobody slept in.

A no-show may still carry a charge, but `no_show_policy.txt` states that the knowledge base
does not specify one; the agent says so and refers the guest to customer service.

## Validation rules

| Rule | Violation |
|---|---|
| `Completed` requires `check_in` in the past | a stay that has not started cannot be complete |
| `No-show` requires `check_in` in the past | a guest cannot fail to arrive for a future date |
| `Confirmed` with `check_out` in the past | stale — should have become `Completed` or `No-show` |
| `Completed` with `check_out` after today | the stay is still in progress — `Confirmed` |
| `No-show` with `check_in` = today | the grace period runs to 23:59 — `Confirmed` |

## What was repaired, and what was not

**Repaired deterministically (3,611 rows).** `Completed` or `No-show` with a future
`check_in`. Only one valid state exists for a future-dated active booking, so `Confirmed`
is not a guess.

**Normalised (4,907 rows).** `Confirmed` with a past `check_out`. The schema records no
check-in event, so `Completed` and `No-show` cannot be told apart; the synthetic convention
(BUSINESS_RULES, RULE D) records them as `Completed`. Both states block their own historical
dates, so availability is unaffected. Each row is logged in `repair_log.csv`.

**In progress (73 rows) and premature no-show (1 row), v3.** `Completed` with a future
check-out → `Confirmed`; `No-show` on the check-in date itself → `Confirmed`.

**Overbooked (3,468 rows).** Active bookings that no free room of their type could hold.
They keep their status and carry `blocks_inventory = False` (RULE J).

## Ordering matters

State repair must run **before** room assignment. Correcting a `No-show` to `Confirmed`
turns a non-blocking record into a blocking one that then needs a free room. Running the
repair in the wrong order left 654 overlaps in the occupancy index on the first pass; the
availability test suite caught it.
