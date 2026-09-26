> **SUPERSEDED / HISTORICAL — NOT SOURCE OF TRUTH.** Replaced by the v4 audit (`07_Audits/Final/V4_AUDIT_REPORT.md`). Kept as the record of v3.

# V3 Audit and Repair Report — 2026-09-25

## ملخص بالمصري

الداتا كانت بتعدّي الـ audit القديم 8/8، بس الفحص لقى مشاكل الـ validators القديمة ماكانتش بتشوفها:

- **3,468 حجز (17%) متداخلين مع حجوزات تانية على نفس الأوضة.** الـ audit القديم كان بيستبعدهم من ملف log، فأي Backend بيقرا `bookings.csv` مباشرة هيلاقي 7,856 double booking. اتضاف عمود `blocks_inventory`، والـ availability بقت شرط واحد.
- **المدفوعات مش متسقة مع الحجوزات:** 5,511 مبلغ قديم (قبل تعديل نوع الأوضة)، و3,246 حالة دفع متناقضة زي Confirmed + Refunded.
- **الـ Gold FAQ:** 912 سؤال سياسات عامة كانوا `requires_tool=True`، و60 سؤال in-scope زي "Cancel my booking" متصنفين OUT_OF_SCOPE، وإجابة غلط بتقول إن الفندق مالوش نجوم، و26 إجابة عربي كانت بالإنجليزي أو فيها حروف ملخبطة.
- **اللهجة المصرية:** زادت من 85 لـ 353 سؤال بتغطي كل الـ 35 intent، ومن 0 لـ 106 محادثة.
- **المحادثات:** الـ 360 محادثة القديمة كانت متركبة من جمل عشوائية، فاتكتبت من جديد مربوطة بالداتا الحقيقية.
- **الـ Knowledge Base:** اتشالت ملاحظات داخلية من 5 ملفات كانت هتدخل الـ RAG وتقرا للعميل أنواع أوض مش موجودة، واتضافت وسائل الدفع.
- **الـ RAG:** الـ chunks بقت 138 بدل 177، من غير chunks فاضية، واتصلح bug كان بيلزق عنوان الـ section اللي بعدها في آخر كل chunk.
- **تاريخ النظام:** بقى في مكان واحد، `06_Scripts/config.py` = 2026-09-19.

كل تغيير متسجل، وكل سكريبت idempotent، و`rebuild_all.py` بيطلع **9/9 gates**.

---

## 1. How to verify

```bash
python3 06_Scripts/rebuild_all.py      # rebuilds everything from the raw inputs, ends with final_audit
```

| Validator | Result |
|---|---|
| `final_audit.py` | 9/9 gates PASS — READY FOR DEVELOPMENT |
| `validate_database.py` | 52/52 |
| `validate_dataset.py` | 64/64 |
| `validate_availability.py` | 15/15 |
| `coverage_audit.py` | 99.1% — the remaining partials are runtime logic (live queries, tool execution) |

A second run of `rebuild_all.py` is byte-identical on every data file.

## 2. Findings and fixes

### Database (stage 1 `apply_business_rules.py`, stage 2 `repair_operational_v3.py`, log `repair_log_v3.csv`)

| # | Finding | Rows | Fix | Rule |
|---|---|---|---|---|
| D1 | Active bookings the v2 repair could not place still sat on an occupied room; only `repair_log.csv` said to ignore them. Reading `bookings.csv` directly gave **7,856 overlapping pairs**. | 3,468 | New column `blocks_inventory`; every validator and the routing matrix use it. Rows kept for their payment/request/feedback history. | J |
| D2 | `Completed` stays whose check-out is after SYSTEM_DATE (still in progress); one `No-show` on its own check-in day | 74 | → `Confirmed` | D, C |
| D3 | Payments still carried the pre-repair total after stage 1 changed the room type or guest count | 5,511 | `amount_paid` = booking total; refund share preserved | H |
| D4 | Payment status impossible for the booking (Confirmed + Refunded, Completed + Pending/Failed, Cancelled/No-show + Pending) | 3,246 | Mapped to the one compatible state | H |
| D5 | Complaint / special request filed by a customer who does not hold the booking | 187 | `customer_id` = the booking's owner | K |
| D6 | Feedback on stays that never happened or had not finished | 2,849 | Re-attached to finished stays without feedback; text/rating kept | L |
| D7 | Discount codes: one code used twice, 7 over `max_usage`, none valid on SYSTEM_DATE | 12 | Duplicate renamed, usage capped, status derived from dates; 4 codes added (Active ×2, Exhausted, Scheduled) | M |
| D8 | `rooms.status` contradicted the bookings (74 "Available" rooms had a guest in them) | 96 | Snapshot recomputed on SYSTEM_DATE | N |
| D9 | In-stay service requests dated outside any stay | 2,571 re-dated, 2,027 detached | Re-dated inside the stay; requests on stays that never happened kept without a booking link | P |
| D10 | Room complaints on stays that never happened, tickets resolved before creation, "Fulfilled" requests on cancelled or future stays | 141 changes | Dates and statuses aligned with the stay | Q |
| D11 | SYSTEM_DATE hard-coded in 4 scripts | — | `06_Scripts/config.py`; `maintenance/advance_system_date.py` moves it and recomputes everything | I |

### Gold FAQ (`repair_gold_v3.py`, log `gold_repair_log_v3.csv`)

| # | Finding | Rows | Fix |
|---|---|---|---|
| G1 | Arabic answers written in English ("Hotel reception operates 24/7.") or corrupted ("نile pearl hotel", "هوôtel"); one Russian question with an English word | 27 | Translated / repaired |
| G2 | Translation artefact "تنطبق هذه المعلومات على Nile Pearl Hotel." appended to Arabic answers | 13 more (39 in total with G1) | Removed |
| G3 | `requires_tool=True` on templated policy questions, contradicting DATA_ROUTING_MATRIX | 912 | → False. True now means live data or an action: 100 rows |
| G4 | In-scope requests labelled OUT_OF_SCOPE ("Cancel my booking please", "Do you have a room available?", "How long does a refund take?"…), one wrong answer ("does not state a star rating") | 60 rows (15 facts × 4 languages) | Correct intent, source and routing; star rating answered from `hotel_information.txt` |
| G5 | Egyptian rows: source "egyptian_dialect_layer" (not a document), category "Egyptian Dialect", 3 cancellations under the wrong intent, one answer that ignored the question | 85 | Grounded in KB documents, domain categories, intents fixed |
| G6 | Payment methods "not specified" in the KB while `payments.csv` records five | 14 | KB and answers state the five methods |
| G7 | EDGE rows cited "training_data" instead of a document | 96 | Grounded in the KB file behind each answer |
| G8 | Two intents had rows under two categories | 12 | One category per intent |

### Additions

| What | Before | After |
|---|---|---|
| Egyptian FAQ rows (every `answer` copied verbatim from a validated Arabic row) | 85, 22 intents | 353, all 35 intents |
| INT033 no-show policy / INT032 contact rows (4 languages) | 8 / 28 | 40 / 56 |
| Conversations | 424 in 4 languages | 530 = 106 × 5 languages |

### Conversations (`generate_conversations.py`)

The 360 "Enhanced Multi-Turn v3" conversations were stitched from random turns: a guest asking
for vegetarian food answered "I am staying in room 101 and the problem is still there", rooms
415 / 301 / 318 / 402 do not exist (the hotel has rooms 101–250), booking facts contradicted
the database (a 4-night stay quoted as ten months, a check-out before its check-in), and an
extra bed was promised to three guests in a Double. All 30 flows were rewritten with every
booking, room, date, rate and loyalty member drawn from the tables; flows that test capacity
now include a case where the room is too small. In the 64 hand-written flows, four booking ids
whose real state contradicted the story were replaced, and the alternative room offered in
BOOK_F3 was moved to dates when it is actually free. `validate_dataset.py` [12] now checks every
booking id, room number and quoted date against the database.

### Knowledge base and RAG

- 5 documents carried internal editorial notes (naming non-existent room types) — removed;
  provenance moved to `01_Docs/KB_CHANGELOG.md`.
- The corpus had no build script. `build_rag_corpus.py` now builds it: the section separator
  that ended up at the end of every chunk is dropped, "Overview" is no longer duplicated, and
  28 near-empty sections are merged into their neighbours: 177 → 138 chunks, none thin.
- Intent splits and `retrieval_eval.jsonl` had no build script either. `build_splits.py`
  keeps every existing split assignment, places new fact groups by hash, and trains Egyptian
  rows to answer in Egyptian. `retrieval_eval.jsonl` now includes the Egyptian queries
  (3,272 → 3,812).

### Documentation

`DATA_ROUTING_MATRIX` pointed at a file that no longer exists and described the availability
query without the occupancy flag; `BOOKING_STATE_MACHINE` said 4,907 rows were left unchanged
(they were normalised), counted 1,004 no-shows (there are 555) and said the KB has no no-show
policy (it does); `GENERATOR_CONSTRAINTS` said the capacity rule was undecided (RULE A
settled it). All corrected; RULES H–Q added to `BUSINESS_RULES.md`.

## 3. Retrieval across languages

The KB is English; guests will speak Arabic and Egyptian. A lexical retriever cannot bridge
that (`retrieval_baseline_bm25.txt`):

| | English | French | Russian | Arabic | Egyptian |
|---|---|---|---|---|---|
| BM25 Recall@5 | 0.736 | 0.302 | 0.167 | 0.128 | 0.171 |

So the retriever must be multilingual. Measure it before relying on it:

```bash
pip install sentence-transformers
python3 06_Scripts/evaluation/evaluate_retrieval.py --dense BAAI/bge-m3
```

This could not be run while preparing the package (no internet access). If Arabic or Egyptian
Recall@5 stays well below English with BGE-M3, translate the KB into Arabic as a second corpus.

## 4. Decisions for the team to confirm

1. **Payment methods** added to the KB from `payments.csv` (credit card, debit card, cash, digital wallet, bank transfer).
2. **Four discount codes** added so each code state can be tested: PEARL100, PEARL500 (Active), PEARL750 (Exhausted), PEARL888 (Scheduled).
3. **`requires_tool` meaning:** True only for live data or actions.
4. **Overbooked bookings kept** with `blocks_inventory=False` rather than deleted.
5. **Egyptian text** (268 FAQ rows, 106 conversations) was written for this release; a native
   review pass by the team is worth doing before fine-tuning on it.
6. **Room service price:** `services.csv` says 150 EGP per order; the KB says "depends on the order". Left as is — decide which the agent should quote.
