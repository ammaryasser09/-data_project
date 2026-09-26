# Nile Pearl Hotel — Official Business Rules

Nile Pearl Hotel is a **synthetic property**. Every rule below was defined for this project
and is the single authoritative interpretation. Any implementation that disagrees with this
document is wrong, not the other way round.

These rules govern: the data generator, all validators, the database, the backend, the
agent's booking tools, the knowledge base, the RAG corpus, and the tests.

---

## RULE A — Room capacity

**Children count toward room capacity.**

```
adults + children <= room_type.capacity
```

| Room type | Capacity | Max guests |
|---|---|---|
| Single | 1 | 1 |
| Double | 2 | 2 |
| Twin | 2 | 2 |
| Deluxe | 3 | 3 |
| Family | 4 | 4 |
| Suite | 4 | 4 |

2 adults + 1 child in a Deluxe (capacity 3) is **valid**.
2 adults + 2 children in a Deluxe is **invalid**.

`adults <= capacity` on its own is **not** a valid check anywhere in the system.

**Bookings larger than 4 guests cannot be made.** The schema holds one room per booking and
no room exceeds capacity 4. A party of five or more needs two bookings.

---

## RULE B — Overlap and back-to-back

Two bookings on the same room conflict when **both** occupy inventory and:

```
a.check_in < b.check_out  AND  b.check_in < a.check_out
```

Strict `<` on both sides. `<=` is wrong and breaks valid back-to-back stays.

```
A: 2026-05-01 → 2026-05-05
B: 2026-05-05 → 2026-05-10     VALID — B starts the day A ends

A: 2026-05-01 → 2026-05-05
B: 2026-05-04 → 2026-05-10     CONFLICT
```

The dataset contains **8,846 valid back-to-back pairs**. Any implementation that reports
them as conflicts is defective.

---

## RULE C — No-show

**Grace period: a Confirmed booking is held until 23:59 on its check-in date.**

After that point, if the guest has not arrived the booking becomes `No-show`.

A `No-show` booking:

- **does not block** room availability — the inventory is released
- **remains** in the booking history and is never deleted
- stays **distinguishable** from `Cancelled` (withdrawn before arrival) and `Completed`
  (guest stayed)

This is the only no-show policy in the project. No penalty, charge or refund rule is defined
by it; those remain outside scope.

---

## RULE D — Booking status semantics

| Status | Meaning | Occupies inventory |
|---|---|---|
| `Confirmed` | Reserved, stay not yet completed | **Yes**, for its stay dates |
| `Completed` | Guest stayed and departed | **Yes**, for its historical dates |
| `Cancelled` | Withdrawn before arrival | **No** |
| `No-show` | Guest did not arrive by the RULE C deadline | **No** |

```
Confirmed ──▶ Completed     guest stayed
    ├──────▶ Cancelled      withdrawn before arrival
    └──────▶ No-show        grace period expired without arrival
```

### Validation

| Rule | Violation |
|---|---|
| `Completed` requires `check_in` in the past | a future stay cannot be complete |
| `No-show` requires `check_in` in the past | cannot fail to arrive for a future date |
| `Confirmed` with `check_out` in the past | grace period long expired |

**Synthetic normalisation.** The dataset carries no arrival record, so a `Confirmed` booking
whose check-out has passed is recorded as `Completed`. Availability is unaffected: both
states block their own dates. 4,907 rows were normalised this way, each logged.

**In-progress stays.** `Completed` means the guest stayed *and departed*. A booking whose
check-out is after SYSTEM_DATE is therefore `Confirmed` (73 rows corrected in v3), and a
booking whose check-in *is* SYSTEM_DATE cannot yet be a `No-show` — its grace period runs to
23:59 that day (1 row corrected).

---

## RULE E — Room assignment order

```
1  generate / read booking
2  validate dates          check_in < check_out
3  validate guests         RULE A
4  determine status        RULE C / RULE D
5  determine blocking      RULE D
6  validate capacity       RULE A against the final room type
7  check availability      RULE B against the current index
8  assign room             first-fit within the correct type
9  verify no overlap       RULE B across the whole index
10 final validation        re-check 2, 3, 6, 9 on the output
```

**Step 4 must precede step 8.** Changing a status after assignment can turn a non-blocking
record into a blocking one with no room allocated. That exact bug occurred earlier in this
project and left 654 hidden overlaps.

Non-blocking bookings take no part in step 8, but their `room_id` must still belong to their
room type or the foreign key is semantically wrong.

---

## RULE F — Contact information

All contact data is **synthetic**. No real person's details appear anywhere.

**Guests** (`customers.csv`): E.164 phone numbers, `example.com` email addresses, both
unique across 10,000 rows. No postal addresses are stored — the schema does not need them.

**Hotel** (`hotel_information.txt`, `contact_information.txt`): a synthetic Cairo address,
a `+20 2` landline in Egyptian format, and `@nilepearlhotel.example` addresses, which use a
reserved-for-documentation TLD and can never reach a real mailbox.

---

## RULE G — Data generation

The original generators are empty notebooks and cannot be fixed. The constraint
specification a rebuilt generator must satisfy is
`01_Docs/GENERATOR_CONSTRAINTS.md`, and
`06_Scripts/generation/generate_bookings.py` is a working reference implementation that
enforces every rule above.

Data was repaired rather than regenerated, because regeneration would discard 20,000
bookings and their payment and request relationships for no gain.


---

## RULE I — The frozen "today"

Every status in the data is correct relative to **SYSTEM_DATE = 2026-09-19**, defined once
in `06_Scripts/config.py`. Scripts, validators and — during development — the backend read
it from there; nothing calls `date.today()`. To move it, run
`06_Scripts/maintenance/advance_system_date.py YYYY-MM-DD`, which recomputes every status.

## RULE J — Occupancy is a column

`bookings.blocks_inventory` is `True` exactly when the booking occupies its room:
status `Confirmed` or `Completed` **and** the booking could be placed without overlap.
The 3,468 bookings the repair could not place (demand exceeded the 150 rooms) keep their
status and history but carry `False`. Availability = `blocks_inventory = 'True'` + RULE B.

## RULE H — Payments agree with bookings

| Booking status | Allowed payment status |
|---|---|
| Confirmed | Paid, Pending, Failed, Partially Refunded |
| Completed | Paid, Partially Refunded |
| Cancelled | Paid (non-refundable), Refunded, Partially Refunded, Failed |
| No-show | Paid, Refunded, Partially Refunded, Failed |

`amount_paid` equals the booking's `total_amount` whenever money was collected, and 0 when
it was not (Pending, Failed). `refund_amount` equals `amount_paid` for Refunded, lies
strictly between 0 and it for Partially Refunded, and is 0 otherwise.

## RULE K — Ownership

A complaint, special request, service request or feedback row that names a booking is filed
by that booking's `customer_id`.

## RULE L — Feedback needs a finished stay

Feedback points at a `Completed` booking whose check-out is on or before SYSTEM_DATE.

## RULE M — Discount codes

`discount_code` is unique; `usage_count <= max_usage`; `status` is derived on SYSTEM_DATE:
Expired (end date passed) → Scheduled (start date ahead) → Exhausted (usage reached) → Active.

## RULE N — Room status

`rooms.status` is the SYSTEM_DATE snapshot: `Occupied` exactly when a blocking booking covers
that night; otherwise `Maintenance` if the room was in maintenance, else `Available`.
Availability for future dates never reads `rooms.status`.

## RULE O — Loyalty

`total_stays` counts lifetime stays, so it is never lower than the `Completed` bookings this
dataset records for the member; `join_date` is not after SYSTEM_DATE.

## RULE P — Service request timing

In-stay requests (room service, housekeeping, extra bed, late checkout) are dated inside a
stay that happened; otherwise the request is kept without a booking link. Pre-arrival
requests (booking inquiry, modification, cancellation, airport transfer, early check-in) are
dated before the check-in. No request is dated after SYSTEM_DATE.

## RULE Q — Complaints and special requests vs the stay

A room, service or facility complaint needs a stay that happened and is raised during or
after it; a ticket is never resolved before it was created. A special request is made before
or during its stay; it is `Fulfilled` only for a stay that happened, with `fulfilled_at`
inside the stay and after the request; only `Fulfilled` rows carry `fulfilled_at`.


---

## v4 — the hotel's commercial terms

The guest-facing terms live in the knowledge base; the tables hold the same numbers and the
validators check that they agree. Prices are in EGP and include 12% service, 14% VAT and 1%
city tax. Room types: `room_types.csv`; services: `services.csv`; fees and percentages:
`fees.csv`; menu: `menu_items.csv`; loyalty: `loyalty_tiers.csv`, `loyalty_rules.csv`.

| Term | Rule | KB document |
|---|---|---|
| Flexible rate | card guarantee, pay at the hotel; free cancellation until 48 h before 3 PM on arrival day; later = first night | `cancellation_policy.txt` |
| Non-refundable rate | 15% below Flexible, prepaid, no cancellation, change or refund | `pricing_and_rates.txt` |
| No-show | held to 23:59; Flexible = first night, Non-refundable = nothing refunded | `no_show_policy.txt` |
| Refunds | processed in 3 business days; card 7–14 business days | `refund_policy.txt` |
| Deposit | 3,000 EGP per night at check-in, released at check-out | `payment_policy.txt` |
| Early check-in | free from 12:00 if available; before 12:00 = 50% of the night | `check_in_check_out.txt` |
| Late check-out | to 16:00 = 1,500; to 18:00 = 50%; after = full night; Silver 13:00 / Gold 14:00 / Platinum 16:00 free | `check_in_check_out.txt` |
| Children | under 6 free incl. breakfast; 6–11 breakfast 600; 12+ adult; children count toward capacity (RULE A) | `children_policy.txt` |
| Loyalty | Silver 10 / Gold 25 / Platinum 50 nights a year; 1 point per 10 EGP; 1,000 points = 500 EGP; expire after 24 months idle | `loyalty_programs.txt` |
| Discounts | one discount, code or special rate per booking | `discounts_and_promotions.txt` |
| Groups | 10+ rooms: 18% off, 30% deposit, free release to 30 days before | `booking_policy.txt` |
| Identity | adults show national ID (Egyptians) or passport; minimum check-in age 18 | `identification_policy.txt` |

## RULE R — Room layout

150 rooms on 15 guest floors (2–16), ten per floor, `room_number = floor × 100 + n`. Rooms
1–5 of each floor face the Nile, 6–10 the city; every Suite faces the Nile (`rooms.view`).
`room_id` (R101…) is an internal key and never changes, so no booking moves.

## RULE S — Arabic names

Arab guests carry `first_name_ar` / `last_name_ar` in `customers.csv`, so a caller who says
"الحجز باسم المنصوري" is matched to "Almansoori". Other guests keep only the Latin spelling.

## RULE T — Rate plans and refunds

`bookings.rate_plan` is Flexible or Non-refundable. A booking paid in full and cancelled or
unused with nothing refunded is Non-refundable; 20% of other paid confirmed/completed stays are
Non-refundable (deterministic). A Flexible late cancellation or no-show keeps the first night:
`refund_amount = total − price_per_night` (a one-night stay keeps everything: status Paid).

## RULE U — Identity check before booking details

The agent discusses or changes an existing booking only after the booking reference matches
together with the last name (either spelling) or the last four phone digits. It reads booking
references, dates and amounts back and gets a "yes" before any change, and quotes the cost
before any cancellation.
