> **SUPERSEDED / HISTORICAL — NOT SOURCE OF TRUTH.** Kept for audit history only. Figures here describe an earlier state of the data. See `07_Audits/Final/` for the current certification.

# HOTELAI DATA AUDIT REPORT

**Scope:** `HotelAI_Dataset.zip` as delivered — 79 files
**Method:** independent inspection. No prior audit report, "Gold" label or filename was
trusted. Every figure below comes from reading the actual files.
**Nothing was modified.**

---

## 1. Executive Summary

The dataset is **strong as static knowledge and weak as an agent dataset**. It would support
a multilingual FAQ bot today. It would not support the reservation agent described in the
project specification, because the data needed to run and evaluate a booking conversation is
either missing from the package or absent entirely.

Four findings block the stated architecture:

1. **The five core operational tables are not in the package.** No `customers.csv`,
   `bookings.csv`, `payments.csv`, `customer_requests.csv`, `customer_feedback.csv`. Without
   them the agent cannot check availability, look up a reservation, or report payment status
   — three capabilities the specification lists as required.
2. **No booking conversation exists.** All 360 multi-turn conversations cover six intents
   (INT009-INT014). The specification's own worked example — "I want to book a room" →
   dates → guests → confirm — has zero examples in the data.
3. **Intent distribution is 7.6:1.** INT004 has 182 rows, INT032 has 24. Eleven intents sit
   below 50 rows. A classifier trained on this will be biased toward the eight original
   intents.
4. **Six knowledge-base facts required by the specification are absent**, including the
   hotel's phone number, email and street address — which a customer service agent is asked
   for constantly.

What is genuinely solid: language balance (1.035), knowledge-base section coverage (156/156),
split hygiene (zero group or question leakage), out-of-scope handling (105 rows, four
categories), and factual consistency between answers and the reference tables.

**Gold quality: PASS WITH ISSUES. Project coverage: PARTIAL.**

---

## 2. Complete Dataset Inventory

### Authoritative / Source of Truth

| Path | Rows | Role | Notes |
|---|---|---|---|
| `1_FAQ/faq_master_3497.csv` | 3,497 | Gold FAQ master | 14 columns, FAQ1-FAQ3497, no gaps |
| `2_Knowledge_Base/*.txt` | 40 docs, 156 sections | RAG source of truth | 4 are corrected versions |
| `4_Database/reference/room_types.csv` | 6 | Authoritative room inventory | Single, Double, Twin, Deluxe, Family, Suite |
| `4_Database/reference/rooms.csv` | 150 | Physical rooms | RT001×20, RT002×35, RT003×30, RT004×30, RT005×20, RT006×15 |
| `4_Database/reference/services.csv` | 8 | Service catalogue | Breakfast, Room Service, Airport Transfer, Laundry, Spa, Gym, Extra Bed, Late Checkout |

### Derived / Generated

| Path | Rows | Role | Notes |
|---|---|---|---|
| `3_Training/corpus.jsonl` | 165 | RAG chunks | Derived from KB; regenerate after any KB edit |
| `3_Training/{train,val,test}.csv` | 2,373 / 589 / 535 | Splits | Group-based |
| `3_Training/{train,val,test}.jsonl` | same | Chat format | Context inlined |
| `3_Training/retrieval_eval.jsonl` | 1,456 | Retrieval ground truth | Covers 42% of master rows |
| `1_FAQ/conversations_360.csv` | 360 | Multi-turn | 30 unique flows |

### Duplicate / Redundant

`1_FAQ/by_layer/*.csv` (1,145 rows across 5 files) duplicate content already in the master.
Documented as optional. **Risk:** a future edit to the master will silently diverge from
these; there is no check that they stay in sync.

### Obsolete

| Path | Issue |
|---|---|
| `3_Training/stats.json` | Reports `total_faqs: 3461`. Actual count is 3,497. **Stale.** |
| `5_Docs/FINAL_CERTIFICATION.txt` | Reports 3,461 and pre-correction figures throughout |
| `5_Docs/coverage_matrix.csv`, `language_balance.csv`, `egyptian_dialect_coverage_map.csv` | Generated before the Egyptian expansion; counts no longer match |

### Missing from the package entirely

`customers.csv` · `bookings.csv` · `payments.csv` · `customer_requests.csv` ·
`customer_feedback.csv` — approximately 70,000 rows that exist in the source repository but
were not included here.

---

## 3. Project Requirement Coverage Matrix

| Requirement | Required data | Existing | Coverage | Missing |
|---|---|---|---|---|
| General hotel questions | KB + FAQ | 40 docs, 3,497 FAQs | **COMPLETE** | — |
| Hotel information | `hotel_information.txt` | present | **PARTIAL** | phone, email, address, website |
| Rooms / room types | `room_types.txt` + CSV | 6 types, prices, capacity | **PARTIAL** | room size, bed configuration detail, view |
| Room facilities | `room_amenities.txt` | 6 categories | **COMPLETE** | — |
| Prices | KB + `room_types.csv` | consistent, verified | **COMPLETE** | taxes not itemised |
| **Availability** | booking calendar | **none in package** | **MISSING** | `bookings.csv` required |
| Booking (create) | flow + conversations | 148 FAQs, **0 conversations** | **PARTIAL** | booking dialogue data |
| Booking modification | INT009 | 175 FAQs + 60 convs | **COMPLETE** | — |
| Booking cancellation | INT018/019 | 96 FAQs, **0 convs** | **PARTIAL** | cancellation dialogue |
| Payment questions | INT020/021 | 102 FAQs, **0 convs** | **PARTIAL** | payment dialogue |
| **Payment status lookup** | `payments.csv` | **none in package** | **MISSING** | table required |
| Cancellation policies | `cancellation_policy.txt` | present | **COMPLETE** | no-show policy absent |
| Hotel services | INT031 | 87 FAQs, 7 services | **COMPLETE** | — |
| Complaints | INT010 | 172 FAQs + 60 convs | **COMPLETE** | — |
| Special requests | INT011 | 173 FAQs + 60 convs | **COMPLETE** | — |
| Policies | INT023/030 | 148 FAQs | **COMPLETE** | no-show, age limits |
| Check-in / check-out | INT004-007 | 694 FAQs | **REDUNDANT** | over-represented |
| Location / transport | INT001, airport_transfer | 177 + 12 | **PARTIAL** | no address, no distances |
| Human handover | escalate_human | 20 FAQs × 4 langs | **NEEDS VALIDATION** | promises an action not wired |
| **Reservation lookup** | `bookings.csv` | **none in package** | **MISSING** | table required |
| Guest information | `customers.csv` | **none in package** | **MISSING** | table required |

---

## 4. Knowledge Base Coverage

40 documents, 156 sections, all with FAQ coverage. Format is uniform (`NILE PEARL HOTEL`
header, numbered sections) and chunks cleanly.

**Required facts absent (specification §5):**

| Fact | Status | Impact |
|---|---|---|
| Street address | **MISSING** | Agent cannot answer "where exactly are you?" |
| Phone number | **MISSING** | Cannot give a callback number or verify identity by phone |
| Email address | **MISSING** | Cannot direct a written complaint |
| Website | **MISSING** | Cannot point to online booking |
| Room size (m²) | **MISSING** | Common pre-booking question |
| No-show policy | **MISSING** | A guest who does not arrive is an unhandled billing case |

`contact_information.txt` names the channels (Reception, Front Desk, Customer Service) but
contains **no actual contact details**. For a customer service agent this is a serious gap:
"what's your number?" is among the most common calls a hotel receives.

**Thin documents (under 60 words, weak retrieval targets):** 11 documents, including
`pet_policy.txt` (35 words), `noise_policy.txt` (36), `smoking_policy.txt` (38),
`emergency_policy.txt` (43), `gym.txt` (48). These retrieve as single short chunks with
little context, and embedding similarity on such short text is noisy.

---

## 5. FAQ Coverage

3,497 rows. Verified: unique IDs, continuous FAQ1-FAQ3497, 3,497 unique questions, no empty
fields, no stub answers, every `source` resolves to a real document, every quoted price
matches `room_types.csv` or `services.csv`, zero language mismatches between a row's
declared language and the script of its question and answer.

`response_mode` distribution: `knowledge_answer` 2,260 · `customer_service` 1,036 ·
`safe_refusal_or_redirect` 105 · `edge_case_answer` 96.
`requires_tool`: 954 rows marked True.

**Concern:** 1,036 rows (30%) resolve to "contact customer service". This is honest where
the knowledge base is genuinely silent, but it means nearly a third of the dataset teaches
the model to deflect rather than answer. The underlying cause is gaps in hotel policy, not
in the dataset construction — but the effect on a demo is that the agent deflects often.

---

## 6. Gold Dataset Audit

**Structural gate — PASS.** Schema consistent, no corrupted rows, no malformed values.

**Metadata gate — PASS.** Language, category, intent, question type and source all validate.

**Semantic gate — PASS WITH ISSUES.** Answers match questions and are grounded in the cited
source. Issue: 11 test rows (2%) carry an answer string that also appears verbatim in train.
Not question leakage — the grouping prevented that — but if you evaluate generation with
exact-match, those 11 are effectively memorised. Use them for retrieval evaluation, not
generation scoring.

**Duplicate gate — PASS.** Zero exact duplicates. Near-duplicates were merged before
splitting (Jaccard ≥ 0.8 within intent and language).

**Coverage gate — FAIL.** See §3 and §10. High row quality does not compensate for absent
booking conversations and absent operational tables.

---

## 7. Intent Coverage

34 intents. **Distribution ratio 7.6:1** (INT004 = 182, INT032 = 24).

Eleven intents below 50 rows: INT016, INT017, INT018, INT019, INT023, INT025, INT026,
INT027, INT028, INT029, INT032.

The eight original intents (INT001-INT008, 1,365 rows) all describe arrival and departure
logistics and hold 39% of the dataset. The 26 intents added to cover the rest of the hotel
hold the remaining 61% between them. For intent classification this skews the prior heavily
toward check-in and check-out.

**`OUT_OF_SCOPE` is 105 rows, all `question_type = Direct`.** Real out-of-scope questions
arrive as scenarios and paraphrases too. A classifier that has only seen direct phrasings of
out-of-scope questions will misroute an indirect one — and misrouting an out-of-scope
question means the RAG answers it confidently and wrongly, which is the failure this layer
exists to prevent.

---

## 8. Multilingual Coverage

English 868 · French 856 · Russian 849 · Arabic 839 — ratio **1.035**. Plus 85
`Arabic-Egyptian` rows across 22 intents, each carrying both an MSA answer and a colloquial
`answer_egyptian`.

Every intent has all four languages present. Verified by Unicode script matching: zero rows
where the question or answer is written in a script other than its declared language.

**Not verifiable by script matching:** naturalness and terminology. A review pass corrected
two substantive Russian errors (`Доступные номера` reading as "available rooms" rather than
"accessible rooms"; `формат номера` ambiguous between "number" and "hotel room") and one
Arabic error (reception and front desk translated as two distinct entities). Residual risk of
machine-like phrasing remains and is **NOT CALCULABLE** without a native reviewer.

---

## 9. Question Type Coverage

Direct 1,266 · Paraphrased 1,109 · Scenario 1,122 — reasonable.

**Present:** direct, paraphrased, scenario, complaints, requests, clarification
(`need_info`, 20 rows × 4 languages), ambiguous ("the big room"), informal phrasing
(85 Egyptian rows).

**Absent:**

| Type | Status | Why it matters |
|---|---|---|
| Typos / misspellings | **0 rows** | Text channel input always contains them |
| ASR error patterns | **0 rows** | STT output contains systematic errors — this is a voice system |
| Negative phrasing | not systematically covered | "Isn't breakfast included?" inverts the answer |
| Customer changing their mind | **0 conversations** | A guest who reverses mid-flow breaks a naive agent |

---

## 10. Conversational Coverage — CRITICAL

360 conversations, 30 unique dialogue flows, 90 per language, 5-6 turns each.

**They cover six intents: INT009, INT010, INT011, INT012, INT013, INT014.**

| Flow the specification requires | Conversations |
|---|---|
| Booking a room (§15 worked example) | **0** |
| Checking availability | **0** |
| Cancellation flow | **0** |
| Payment problem | **0** |
| Room type / pricing enquiry | **0** |
| Booking modification | 60 |
| Complaint | 60 |
| Special request | 60 |
| Loyalty / facilities / emergency | 180 |

**Only two role patterns exist:** `uauau` and `uauaua`. Every conversation alternates
strictly, every conversation resolves successfully. There are no conversations where the
agent asks twice, where the guest supplies the wrong information, where the request fails, or
where the guest changes their mind. A model trained on this learns that every dialogue
succeeds in five turns.

Context retention, clarification and confirmation are demonstrated. Correction, failure paths
and mind-changing are not.

---

## 11. Voice AI Readiness

Average answer length is 114 characters — good for speech. Only 3 answers exceed 300
characters.

**78 answers contain long enumerations** that do not work spoken. Example (`booking_process.txt`):

> The cancellation process runs in seven steps: provide the reservation details, review the
> cancellation conditions, submit the request to customer service, check whether cancellation
> is permitted and whether fees apply, process the cancellation, process any refund, and
> retain the cancellation confirmation.

Read aloud, a guest retains roughly the first two steps. These need a spoken variant that
gives one step and waits.

**The Egyptian layer is the only part with a spoken register.** 85 rows carry
`answer_egyptian`. The other 3,412 rows have one register that serves both text and voice —
functional, but stiff when spoken.

**No ASR-error data.** For a system whose input is speech recognition output, the absence of
misrecognition patterns is a measurable gap: the agent will be evaluated on clean text and
deployed on noisy text.

---

## 12. RAG Readiness

**Strong.** 165 chunks, each opening with hotel name, document title and section heading, so
a retrieved passage identifies itself. Metadata carries `chunk_id`, `doc_id`, `doc_title`,
`section`, `char_len`. Source attribution runs from every FAQ row through `source` to a real
document. No contradictions detected between chunks after the room-type corrections.

`retrieval_eval.jsonl` provides 1,456 query-to-document pairs — but that is only 42% of the
master. The other 58% (rows whose `source` is not a document, mainly `customer_service` and
out-of-scope rows) have no retrieval ground truth, which is correct, since they should not
trigger retrieval at all.

**Weakness:** the 11 thin documents produce single short chunks. Short-text embedding
similarity is unstable, so `pet_policy.txt` (35 words) may lose retrieval to a longer
document that merely mentions pets.

**Correctly classified as NOT RAG** (`requires_tool = True`, 954 rows): availability, booking
creation, reservation lookup, payment status, loyalty balance. The distinction the
specification asks for is made explicitly in the data.

---

## 13. Database / Backend Readiness

| Capability | Table needed | In package | Status |
|---|---|---|---|
| Room inventory | `room_types.csv`, `rooms.csv` | yes | **READY** |
| Service catalogue | `services.csv` | yes | **READY** |
| Pricing tiers | `pricing_tiers.csv` | yes | **READY** |
| Discount codes | `discount_codes.csv` | yes | **READY** |
| Loyalty | `loyalty_members.csv` | yes | **READY** but `customer_id` values reference an absent table |
| Complaints | `complaint_tickets.csv` | yes | same |
| Special requests | `special_requests_history.csv` | yes | same |
| **Availability check** | `bookings.csv` | **no** | **BLOCKED** |
| **Reservation lookup** | `bookings.csv` | **no** | **BLOCKED** |
| **Guest lookup** | `customers.csv` | **no** | **BLOCKED** |
| **Payment status** | `payments.csv` | **no** | **BLOCKED** |

Three of the five operational tables present contain `customer_id` and `booking_id` foreign
keys pointing at tables that are not in the package. Loaded as-is, every one of those
references is dangling.

---

## 14. Data Consistency

| Fact | Source A | Source B | Conflict | Source of truth |
|---|---|---|---|---|
| Room types | `room_types.csv`: Single, Double, Twin, Deluxe, Family, Suite | KB (original): Standard, Deluxe, Superior, Executive, Family | **Resolved** — 4 KB docs rewritten | `room_types.csv`, on the basis that 20,000 bookings reference RT001-RT006. **This is a decision, not a verified fact.** |
| Deluxe capacity | CSV: 3 | KB (original): 2 | **Resolved** to 3 | same |
| Prices | CSV + `services.csv` | all KB docs and answers | none | verified: every quoted price matches |
| Hours | KB | KB | none | check-in 15:00, check-out 12:00, breakfast 07:00-10:30, pool 07:00-21:00, spa 09:00-22:00, gym 24/7 |
| Currency | all files | — | none | EGP only |
| Star rating | `hotel_information.txt`: 5-Star | FAQ answers | none | consistent |

No unresolved contradictions remain in the delivered files.

---

## 15. Data Leakage / Contamination

| Check | Result |
|---|---|
| Identical question in train and eval | **0** |
| Fact group shared train/test | **0** |
| Fact group shared train/val | **0** |
| Near-duplicate questions across splits | 0 (merged at Jaccard ≥ 0.8 before splitting) |
| **Answer string shared train→test** | **11 rows (2%)** |

The split methodology is sound: rows are grouped by the fact they teach, so paraphrases of
one fact cannot straddle the split.

**The contamination that cannot be fixed by splitting:** every question was generated from
seven phrasing templates per language and question type. Train and test share the *template
distribution* even where they share no fact. Any accuracy measured here reflects performance
on template-generated text, not on guest speech. **This is the single largest threat to the
validity of every number the project will report.**

---

## 16. Data Balance

| Dimension | Ratio | Assessment |
|---|---|---|
| Languages | 1.035 | **Excellent** |
| Question types | 1.14 | **Good** |
| Intents | **7.6:1** | **Serious imbalance** |
| Response modes | 21:1 | Acceptable — reflects real traffic shape |
| Conversations by intent | **∞** (0 for 28 of 34 intents) | **Serious gap** |
| Egyptian dialect | 85 of 3,497 (2.4%) | Seed only, not coverage |

---

## 17. Critical Gaps

### GAP-1 — Operational tables absent from the package · **CRITICAL**
Availability, reservation lookup, guest lookup and payment status are all impossible.
Three included tables carry dangling foreign keys.
**Component:** Agent, backend, tool calling.
**Evidence:** `4_Database/` contains 8 files; `customers.csv`, `bookings.csv`,
`payments.csv`, `customer_requests.csv`, `customer_feedback.csv` are not among them.
**Action:** copy the five tables from the source repository into `4_Database/operational/`
and re-verify foreign keys.

### GAP-2 — No booking conversation data · **CRITICAL**
The core flow of a reservation agent has no dialogue examples. The specification's own
example in §15 cannot be tested against this dataset.
**Component:** Agent, dialogue management, evaluation.
**Evidence:** `conversations_360.csv`, `intent_id` column — values are INT009-INT014 only.
**Action:** add flows for availability search, booking creation, cancellation and payment
problems; approximately 20 flows × 4 languages.

### GAP-3 — Contact details absent · **HIGH**
No phone, email, address or website anywhere in the knowledge base.
**Component:** RAG, customer service, escalation.
**Evidence:** `contact_information.txt` names channels but lists no contact values.
**Action:** obtain from the hotel; four facts close it.

### GAP-4 — Intent imbalance 7.6:1 · **HIGH**
Eleven intents under 50 rows against INT004's 182.
**Component:** Intent classifier.
**Evidence:** §7 table.
**Action:** either raise the thin intents to ~100 rows, or apply class weighting and report
per-class F1 rather than accuracy.

### GAP-5 — `escalate_human` promises an unwired action · **HIGH**
20 rows × 4 languages state "I am escalating this now" and "I am logging this as a formal
complaint". If the agent is not connected to `complaint_tickets.csv`, the system asserts an
action it does not perform.
**Component:** Agent, trust.
**Action:** wire the tool, or change the wording to "I will pass this to management".

### GAP-6 — No typo or ASR-error data · **HIGH**
Zero rows contain misspellings or speech-recognition error patterns in a voice-first system.
**Component:** STT→NLU, intent classifier.
**Action:** inject realistic ASR errors into a held-out evaluation set; do not train on them
until real STT output is available.

### GAP-7 — Out-of-scope layer is Direct-only · **MEDIUM**
105 rows, all one question type.
**Component:** Router, safety.
**Action:** add paraphrased and scenario phrasings of the same 25 scenarios.

### GAP-8 — Stale metadata files · **MEDIUM**
`stats.json`, `FINAL_CERTIFICATION.txt`, `coverage_matrix.csv`, `language_balance.csv`,
`egyptian_dialect_coverage_map.csv` all report 3,461 or pre-correction figures against an
actual 3,497.
**Component:** documentation, examiner credibility.
**Action:** regenerate, or delete and rely on `validate.py` output.

### GAP-9 — Long enumerated answers unsuitable for speech · **MEDIUM**
78 answers list five to seven items in one sentence.
**Component:** TTS, user experience.
**Action:** add a short spoken variant for these, as was done for the Egyptian layer.

### GAP-10 — Eleven thin knowledge documents · **MEDIUM**
Under 60 words each; unstable as retrieval targets.
**Component:** RAG.
**Action:** merge into thematic parents, or expand with the detail guests actually ask for.

### GAP-11 — Six edge cases from §20 uncovered · **MEDIUM**
Invalid dates, past dates, invalid room type, unavailable service, invalid booking number,
duplicate booking, conflicting requests.
**Component:** Agent robustness.
**Action:** add to the edge-case layer with the existing `scenario_key` structure.

### GAP-12 — `by_layer/` duplicates can drift · **LOW**
1,145 rows duplicated from the master with no sync check.
**Action:** add a `validate.py` check that each layer file is a subset of the master, or
delete the folder.

---

## 18. Missing Data Requirements

| # | Missing data | Why | Structure | Priority | Used by |
|---|---|---|---|---|---|
| 1 | `bookings.csv`, `customers.csv`, `payments.csv` | Availability, lookup, payment status | existing repo schema | **P0** | Agent, backend |
| 2 | Booking / availability / cancellation / payment conversations | Core agent flow untested | as `conversations_360.csv`, ~20 flows × 4 langs | **P0** | Agent, evaluation |
| 3 | Hotel contact details | Constantly asked | 4 lines in `contact_information.txt` | **P1** | RAG |
| 4 | No-show policy | Unhandled billing case | one KB section | **P1** | RAG, backend |
| 5 | FAQs for the 11 thin intents | Classifier bias | ~50 rows each, 4 langs | **P1** | Classifier |
| 6 | Out-of-scope paraphrase + scenario rows | Router robustness | 25 scenarios × 2 types × 4 langs | **P1** | Router |
| 7 | ASR-error evaluation set | Voice-first system | held-out only, ~200 rows | **P1** | STT→NLU |
| 8 | Spoken variants for 78 enumerated answers | TTS quality | `answer_spoken` column | **P2** | TTS |
| 9 | Seven remaining §20 edge cases | Robustness | existing edge schema | **P2** | Agent |
| 10 | Room size, bed configuration, view | Common pre-booking questions | KB + `room_types.csv` columns | **P2** | RAG |
| 11 | Tax and fee breakdown | Quoted totals may be wrong | KB section + CSV | **P2** | RAG, backend |

---

## 19. Gold Certification

| Dataset | Gold quality | Project coverage |
|---|---|---|
| `faq_master_3497.csv` | **PASS** | **PARTIAL** — intent imbalance, no typo data |
| `2_Knowledge_Base/` | **PASS WITH ISSUES** — 11 thin docs | **PARTIAL** — 6 required facts absent |
| `conversations_360.csv` | **PASS** | **FAIL** — 6 of 34 intents, no booking flow |
| `3_Training/` splits | **PASS** | **PASS** |
| `corpus.jsonl` | **PASS** | **PASS** |
| `4_Database/reference/` | **PASS** | **PASS** |
| `4_Database/operational/` | **PASS WITH ISSUES** — dangling FKs | **FAIL** — 5 core tables absent |
| `5_Docs/` | **FAIL** — stale figures throughout | n/a |
| Egyptian layer | **PASS** | **PARTIAL** — 85 rows, seed not coverage |

---

## 20. Final Project Coverage Assessment

| Metric | Score | Basis |
|---|---|---|
| Functional coverage | **62%** | 13 of 21 requirements COMPLETE, 4 MISSING, 4 PARTIAL (§3) |
| Intent coverage | **75%** | 34 intents, all languages present, but 7.6:1 imbalance and 11 intents under 50 rows |
| Language coverage | **95%** | 1.035 ratio, zero script mismatches; naturalness unverified |
| Scenario coverage | **70%** | 1,122 scenario rows; 7 of 15 §20 edge cases uncovered |
| Conversational coverage | **25%** | 6 of 34 intents; 2 role patterns; no booking, cancellation or payment flow |
| Knowledge-base coverage | **80%** | 156/156 sections covered, but 6 required facts absent and 11 docs thin |
| Reservation coverage | **35%** | FAQ present, conversations and operational tables absent |
| Policy coverage | **90%** | all major policies present; no-show and age limits absent |
| Payment coverage | **55%** | FAQ present; `payments.csv` absent; taxes not itemised |
| RAG readiness | **88%** | strong structure and attribution; 11 thin chunks |
| Backend readiness | **40%** | 3 of 7 capabilities supported; 4 blocked by absent tables |
| Voice readiness | **55%** | good answer length; no ASR data; 78 unspoken-friendly answers; one register outside the Egyptian layer |
| Data quality | **93%** | 49/49 automated checks pass; 11 answer-string overlaps |
| Consistency | **97%** | no unresolved contradictions; room-type resolution is a decision, not verification |

**Overall functional readiness: PARTIAL.**

### The one-sentence answer

If HotelAI is built on this dataset as delivered, **the customer-service half of the system
is genuinely covered and the reservation half is not** — the agent can answer what the hotel
is and what it charges in four languages with safe refusals when it does not know, but it
cannot check availability, retrieve a booking, confirm a payment, or hold a booking
conversation, because the tables and the dialogue data for those four things are absent.

### Closing the gap

GAP-1 and GAP-2 are the whole difference between a FAQ bot and the specified system.
GAP-1 is a file copy from the source repository. GAP-2 is roughly the same effort as the
existing conversation layer. Everything else on the list is refinement.

---

*Audit performed by independent inspection of the delivered package. No files were modified.
Every figure is reproducible from the cited paths.*
