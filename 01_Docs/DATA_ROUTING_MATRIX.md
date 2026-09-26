# Data Routing Matrix

Which source answers which request. Getting this wrong is the difference between an agent
that says "the pool is open 7 AM to 9 PM" (static, correct from RAG) and one that says
"room 205 is free" without checking anything.

| User request | Source | Tool / table | Read/Write |
|---|---|---|---|
| What time is check-in? | **RAG** | `03_Knowledge_Base/check_in_check_out.txt` | Read |
| Do you have a pool? What are its hours? | **RAG** | `hotel_facilities.txt`, `spa.txt` | Read |
| What is your cancellation policy? | **RAG** | `cancellation_policy.txt` | Read |
| Are pets allowed? | **RAG** | `pet_policy.txt` | Read |
| How much is a Deluxe Room? | **RAG or DATABASE** | `pricing_and_rates.txt` = `room_types.csv.base_price` (validated identical) | Read |
| What room types do you have? | **RAG or DATABASE** | `room_types.txt` = `room_types.csv` (validated identical) | Read |
| How many guests fit in a Family Room? | **DATABASE** | `room_types.csv.capacity` | Read |
| Is a Double free 12–15 November? | **DATABASE** | `bookings.csv` (`blocks_inventory = 'True'`) × `rooms.csv` date overlap | Read |
| What will three nights cost? | **DATABASE** | `room_types.csv` + `pricing_tiers.csv` + nights | Read |
| Book that room for me | **AGENT → DB** | insert into `bookings.csv` | **Write** |
| Pull up my reservation B004512 | **DATABASE** (after the identity check) | `bookings.csv` by `booking_id`; caller gives the last name (English or Arabic) or the last 4 phone digits — `reservation_security.txt` | Read |
| Is my booking refundable? | **DATABASE** | `bookings.csv.rate_plan` (Flexible / Non-refundable) | Read |
| What would cancelling cost me now? | **DATABASE** | `rate_plan` + 48-hour rule + `payments.csv` — tool `quote_cancellation` | Read |
| Change my dates | **AGENT → DB** | update `bookings.csv`, re-check overlap | **Write** |
| Cancel my booking | **AGENT → DB** | quote first, confirm with the caller, then update `bookings.csv.booking_status` | **Write** |
| What's on the room-service menu? How much is a burger? | **RAG or DATABASE** | `in_room_dining_menu.txt` = `menu_items.csv` (validated identical prices) | Read |
| Order a burger to room 1103 | **AGENT → DB** | `menu_items.csv` + 300 EGP delivery (`services.csv` S002) — tool `room_service_quote` | **Write** |
| Can I stay until 5 PM? | **DATABASE** | `check_in_check_out.txt` rules + nightly rate + member tier (`loyalty_tiers.csv`) — tool `late_checkout_quote` | Read |
| How many points do I have? | **DATABASE** | `loyalty_members.csv`; value from `loyalty_rules.csv` — tool `loyalty_status` | Read |
| How far is the airport? Is there a pharmacy nearby? | **RAG** | `location_and_surroundings.txt` | Read |
| Has my payment gone through? | **DATABASE** | `payments.csv` by `booking_id` | Read |
| Am I a loyalty member? | **DATABASE** | `loyalty_members.csv` by `customer_id` | Read |
| Is discount code PEARL100 valid? | **DATABASE** | `discount_codes.csv` (`status` is derived on SYSTEM_DATE) | Read |
| Which payment methods do you accept? | **RAG** | `payment_methods.txt` | Read |
| I want to file a complaint | **AGENT → DB** | insert into `complaint_tickets.csv` | **Write** |
| I need a vegetarian breakfast | **AGENT → DB** | insert into `special_requests_history.csv` | **Write** |
| What's the weather? | **REFUSE** | out-of-scope handler | — |
| I'm suing the hotel / your employee was rude / I want compensation / delete my data | **ESCALATE** | human handover (`response_mode = escalate_to_human` in Gold) — tool `escalate_to_human` | — |
| Fire, someone collapsed, a stranger at my door | **EMERGENCY** | first sentence: call reception +20 2 2794 5500 now; `emergency_procedures.txt` | — |

## The rule

Anything that can change between two phone calls comes from the database. Anything printed
in a brochure comes from RAG.

**Never route through RAG:** availability, a specific booking, payment status, loyalty
balance, complaint status. The knowledge base has no way to know these and will answer from
the nearest-looking passage.

`hotel_faq_gold.csv` marks this per row in `requires_tool`: **True only when the answer
needs live data or an action** — a specific booking, availability, payment status, a
loyalty balance, a discount-code check, or a request to change, cancel or file something
(100 rows). A general policy question ("What is the cancellation policy?", "Could you
clarify how refunds work?") is **False** even when it belongs to a customer-service intent:
its answer is fixed text in the knowledge base. Before v3, 912 such policy questions were
marked True, which would have trained the router to ask for a booking number before
answering a brochure question.

## The availability query

```sql
SELECT r.room_id FROM rooms r
WHERE r.room_type_id = :type
  AND NOT EXISTS (SELECT 1 FROM bookings b
                  WHERE b.room_id = r.room_id
                    AND b.blocks_inventory = 'True'
                    AND b.check_in < :check_out AND :check_in < b.check_out);   -- RULE B, strict <
```

Never filter on `booking_status` alone. 3,468 Confirmed/Completed bookings are overbooked
records (`blocks_inventory = 'False'`); counting them produces 7,856 phantom double bookings.
"Today" is `SYSTEM_DATE` from `06_Scripts/config.py`, not the machine clock.

## Reference tools

`09_Application/rag/tools.py` implements the read-only rows of this matrix over the CSVs
(`check_availability`, `find_booking`, `quote_cancellation`, `late_checkout_quote`,
`check_discount_code`, `loyalty_status`, `menu`, `room_service_quote`, `escalate_to_human`)
with JSON schemas in `TOOL_SCHEMAS`. The FastAPI backend reproduces the same behaviour on
the real database; write actions are performed by the backend, never by the LLM directly.
