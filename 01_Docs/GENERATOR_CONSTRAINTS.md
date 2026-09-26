# Generator Constraints

The original generators are empty notebooks, so this is the specification a rebuilt
generator must satisfy. Each constraint maps to a check in
`06_Scripts/validation/validate_database.py`.

## Hard constraints

```
check_in  <  check_out
nights    == (check_out - check_in).days
total_amount == price_per_night * nights
price_per_night within 0.80..1.35 of room_types.base_price

booking.customer_id   ∈ customers.customer_id
booking.room_id       ∈ rooms.room_id
booking.room_type_id  ∈ room_types.room_type_id
rooms.room_type_id    ∈ room_types.room_type_id
payment.booking_id    ∈ bookings.booking_id

for each room, for all bookings with status ∈ {Confirmed, Completed}:
    no pair where a.check_in < b.check_out AND b.check_in < a.check_out
    (check_out == next check_in is allowed)
```

## State constraints

```
Completed  ⇒ check_in <= today AND check_out <= today
No-show    ⇒ check_in  < today
Confirmed  ⇒ check_out >= today
blocks_inventory ⇔ status ∈ {Confirmed, Completed} AND placed without overlap

today = SYSTEM_DATE from 06_Scripts/config.py
```

## Capacity constraint — decided

```
adults + children <= room_type.capacity        (BUSINESS_RULES, RULE A)
```

Children count toward capacity. The repaired data, the knowledge base, the Gold FAQ and every
validator agree (final_audit Gate 3).

## Volume constraint

```
sum(nights of active bookings) <= rooms * horizon_days * target_occupancy
```

The original data ignored this: demand exceeded the 150 rooms, and 3,468 active bookings
could not be placed at all. They are kept with `blocks_inventory = False` (RULE J). A
realistic hotel target is 65–75%.

## Missing columns

Add these; without them 4,907 stale bookings could only be normalised by convention:

```
created_at       when the booking was made
cancelled_at     when it was cancelled, if applicable
checked_in_at    actual arrival, distinguishes Completed from No-show
```
