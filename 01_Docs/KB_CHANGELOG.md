# Knowledge Base Changelog

The files in `03_Knowledge_Base/` are customer-facing: the agent may read any sentence of
them to a guest. Provenance notes therefore live here, not inside the documents.

## v4 — 2026-09-26

Research-based commercial terms (Cairo 5-star practice) approved by the team. 27 documents
rewritten, 3 added; the tables carry the same numbers and the validators check agreement.

| Area | Change |
|---|---|
| Prices | Rooms 6,000–20,000 EGP (×~3.2, per type), sizes in m²; breakfast 1,200; transfer 2,500 / 4,000; spa 3,500 / 4,800; laundry 500/kg; extra bed 2,500; late check-out 1,500; gym free; all prices include service and taxes |
| Rate plans | Flexible (free cancellation to 48 h) and Non-refundable (15% less, prepaid) |
| Policies now stated | cancellation fee and deadline, no-show charge, refund timing, deposit, early/late check-out fees, children's rates, ID documents, minimum age, modification rules, group terms, loyalty tiers/earning/expiry/transfer, lost-and-found period, confirmation by email + SMS, parking, Wi-Fi password, laundry turnaround, spa menu, celebrations |
| New documents | `in_room_dining_menu.txt` (23 dishes, halal, allergen codes, night menu), `location_and_surroundings.txt` (airport, landmarks, metro, everyday needs), `reservation_security.txt` (identity check) |
| Rooms | 15 guest floors, Nile or city view, guaranteed Nile view 2,000 EGP |
| Left unspecified on purpose | compensation amounts (management decision), detailed accessibility features, medical billing |

## v3 — 2026-09-25

| File | Change | Why |
|---|---|---|
| `room_types.txt`, `room_policies.txt`, `room_amenities.txt`, `booking_policy.txt` | Removed the "CORRECTED VERSION — aligned with data/room_types.csv…" header block | Internal note inside a guest-facing document. It named room types that do not exist (Standard, Superior, Executive) and would have been retrieved by RAG. |
| `contact_information.txt` | Removed "All contact details below are synthetic…" | Same reason. The synthetic nature of all contact data is recorded in BUSINESS_RULES, RULE F. |
| `payment_methods.txt` | Section 2 now lists the accepted methods: credit cards, debit cards, cash, digital wallets, bank transfer. Section 5 keeps only what is still unspecified (card brands, wallet providers, currency restrictions). | The KB said the methods were unknown while `payments.csv` records exactly these five methods across 20,000 payments. The database is the operational truth (as for room types). |
| `payment_policy.txt` | "Accepted payment cards" → "Which card brands or networks are accepted" | Consistency with the above. |

## Earlier (v2)

Room types, capacities and prices in `room_types.txt`, `room_policies.txt`,
`room_amenities.txt` and `booking_policy.txt` were rewritten to match
`02_Data/02_Operational/room_types.csv` (RT001–RT006). The original files listed Standard,
Superior and Executive rooms that the reservation database does not contain.
