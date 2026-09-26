# Source of Truth

Exactly one authoritative file per category. Nothing in `08_Archive/` is read by code.
The whole dataset is a snapshot at **SYSTEM_DATE = 2026-09-19** (`06_Scripts/config.py`).

| Category | File | Rows | Status |
|---|---|---|---|
| Hotel knowledge | `03_Knowledge_Base/*.txt` | 44 docs | **ACTIVE** — v4 policies, prices, menu, location, reservation security |
| FAQ Gold | `02_Data/04_Gold/hotel_faq_gold.csv` | 3,965 | **ACTIVE** — EN 910, FR 898, RU 891, AR 881, Egyptian 385 (all 35 intents); `question_style` marks 1,872 templated rows |
| FAQ Gold baseline | `02_Data/04_Gold/hotel_faq_1344_baseline.csv` | 1,344 | **PROTECTED** — every id must still exist in Gold (`final_audit.py`) |
| Conversations | `02_Data/04_Gold/conversations_gold.csv` | 630 | **ACTIVE** — 126 per language × 5 languages, 50 flows |
| Bookings | `02_Data/02_Operational/bookings.csv` | 20,000 | **ACTIVE** — `blocks_inventory` decides occupancy; `rate_plan` Flexible 14,531 / Non-refundable 5,469 |
| Bookings, raw | `02_Data/01_Raw/bookings_raw.csv` | 20,000 | **RAW** — stage-1 input, never modified |
| Other tables, raw | `02_Data/01_Raw/*_raw.csv` | — | **RAW** — stage-2 inputs, frozen before v3, never modified |
| Customers | `02_Data/02_Operational/customers.csv` | 10,000 | **ACTIVE** — Arabic spelling for 7,120 Arab guests (RULE S) |
| Payments | `02_Data/02_Operational/payments.csv` | 20,000 | **ACTIVE** — one per booking, agrees with it (RULE H) |
| Rooms / room types | `rooms.csv`, `room_types.csv` | 150 / 6 | **ACTIVE** — 15 floors, Nile/City view (RULE R); v4 prices and sizes; `rooms.status` is the SYSTEM_DATE snapshot |
| Services / fees / menu | `services.csv`, `fees.csv`, `menu_items.csv` | 16 / 10 / 23 | **ACTIVE** — v4 price list; the KB quotes the same numbers |
| Loyalty rules | `loyalty_tiers.csv`, `loyalty_rules.csv` | 4 / 7 | **ACTIVE** — tiers, earning, redemption |
| Requests | `customer_requests.csv` | 15,000 | **ACTIVE** |
| Complaints / special requests / feedback | `complaint_tickets.csv`, `special_requests_history.csv`, `customer_feedback.csv` | 75 / 125 / 5,000 | **ACTIVE** |
| Loyalty / discount codes / pricing tiers | `loyalty_members.csv`, `discount_codes.csv`, `pricing_tiers.csv` | 100 / 29 / 10 | **ACTIVE** |
| Business rules | `01_Docs/BUSINESS_RULES.md` | — | **ACTIVE** — RULES A–U + v4 commercial terms |
| Realistic test set | `05_Evaluation/realistic_test/realistic_test_egyptian.csv` | 200 | **DERIVED** — `06_Scripts/generation/realistic_test_v1.py`; facts computed from the tables |
| Egyptian review | `05_Evaluation/review/egyptian_review.xlsx` | 211 + 360 + 200 | **FOR THE TEAM** — `06_Scripts/generation/build_review_file.py` |
| RAG application | `09_Application/rag/` | — | **CODE** — retriever, prompt, tools, evaluation |
| RAG chunks | `04_RAG/corpus.jsonl` | 146 | **DERIVED** — `06_Scripts/build/build_rag_corpus.py` |
| Retrieval ground truth | `04_RAG/retrieval_eval.jsonl` | 3,908 | **DERIVED** — `06_Scripts/build/build_splits.py` |
| Intent splits | `05_Evaluation/intent/` | 3,965 (train 2,709 / val 675 / test 581) | **DERIVED** — `06_Scripts/build/build_splits.py` |

## Derived files go stale

Edit a source → run `python3 06_Scripts/rebuild_all.py`. It runs every repair, build and
validation step in order and is idempotent (a second run is byte-identical).

## Names do not carry row counts

Earlier versions were named `hotel_faq_3557_gold.csv`, `conversations_424.csv` and so on.
Every addition changed the filename and broke every script that referenced it. Current
names are stable; row counts live in this document and in the validators.
