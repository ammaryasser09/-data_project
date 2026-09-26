# V4 Report — realistic hotel terms, RAG code, realistic evaluation — 2026-09-26

## ملخص بالمصري

الإصدار ده بيحوّل الداتا من "سليمة" لـ "فندق حقيقي"، وبيضيف الكود والاختبارات اللي الفريق هيشتغل بيها.

- **السياسات والأسعار:** كل اللي اتفقنا عليه بقى مكتوب في الـ KB ومطابق للداتابيز:
  - الإلغاء قبل 48 ساعة، ونوعين أسعار (مرن و Non-refundable)، ورسوم عدم الحضور، ومدة الاسترداد.
  - التأمين 3,000 جنيه في الليلة، والدخول بدري والخروج متأخر، والأطفال، والولاء، والمجموعات، والهوية.
  - الأسعار اتضربت في حوالي 3.2 عشان تقرب من فنادق القاهرة، والأوضة بقت من 6,000 لـ 20,000 جنيه.
  - الـ validator بيتأكد إن كل سعر مكتوب في أي إجابة موجود في الداتابيز.
- **حاجات جديدة:**
  - منيو روم سيرفس فيه 23 صنف (حلال، ومعاه علامات الحساسية، ومنيو ليلي).
  - ملف عن موقع الفندق والمنطقة (المطار، والأماكن القريبة، والمترو، والصيدليات).
  - قاعدة التحقق من الهوية قبل الكلام في أي حجز.
  - 15 دور، وأوض على النيل وأوض على المدينة.
  - أسماء العملاء العرب بالعربي، عشان البحث بالصوت يلاقيهم.
- **الـ Gold:** 3,965 سؤال، ومفيش إجابة مصري بتقول "مش محدد" في حاجة بقت محددة. اتصلحت كمان 10 مجموعات إجابات مصرية كانت بتبدأ بـ "أيوة" أو "نعم" على سؤال مايتجاوبش كده. أخطرهم "من غير بطاقة ينفع أدخل؟ ← أيوة".
- **المحادثات:** 630 محادثة (50 flow) بالأسعار الجديدة والتواريخ بصيغة الكلام. فيها flows جديدة: طلب روم سيرفس، وكود خصم، وخروج متأخر، والتأمين.
- **كود الـ RAG** في `09_Application/rag`:
  - retriever بيدور في الـ KB وفي أسئلة الـ FAQ مع بعض.
  - برومبت مكتوب للصوت.
  - 9 tools بتقرا من الداتابيز، بتسمح للفريق يجرب الـ agent كامل من غير Backend.
  - تقييم لكل لغة.
- **النتيجة المهمة:** الـ FAQ index رفع نسبة إن المستند الصح يطلع في أول 5 نتايج (بـ BM25 من غير أي موديل):
  - العربي: من 0.8% لـ 45%.
  - المصري: من 2.4% لـ 48%.
  - الأسئلة الواقعية: من 4% لـ 58%.
- **test set واقعي:** 200 سؤال مصري في 10 أنواع، ولكل سؤال المسار الصح، والإجابة المتوقعة محسوبة من الداتابيز، واللي ممنوع الـ agent يقوله.
- **ملف مراجعة Excel** للفريق: 211 إجابة، و360 رد في المحادثات، و200 سؤال.

كله بيتبني بأمر واحد (`rebuild_all.py`)، و**9/9 gates**، والإعادة بتطلع نفس الملفات بالظبط.

---

## 1. Verification

| Check | Result |
|---|---|
| `final_audit.py` | 9/9 gates — READY FOR DEVELOPMENT |
| `validate_dataset.py` | 64/64 (prices in every answer exist in the tables; conversations grounded in the database) |
| `validate_database.py` | 59/59 (rate plans vs payments, room layout, loyalty tables) |
| `validate_availability.py` | 15/15 |
| `coverage_audit.py` | 99.1% (remaining partials are runtime logic) |
| Rerun of `rebuild_all.py` | byte-identical data files |

## 2. What changed

### Knowledge base (44 documents, `01_Docs/KB_CHANGELOG.md`)
27 documents rewritten with the approved terms, 3 new (`in_room_dining_menu.txt`,
`location_and_surroundings.txt`, `reservation_security.txt`). Deliberately still unspecified:
compensation amounts, detailed accessibility features, medical billing.

### Database
| Table | Change | Rule |
|---|---|---|
| `room_types.csv` | v4 prices (6,000–20,000), `size_sqm`; old list in `01_Raw/room_types_raw.csv` | — |
| `bookings.csv` | prices rescaled per type (seasonal factor kept), `rate_plan` column | STEP 0, RULE T |
| `payments.csv` | 229 Flexible late cancellations / no-shows refund all but the first night | RULE T |
| `rooms.csv` | 15 floors, `room_number = floor×100+n`, `view` Nile/City; `room_id` unchanged | RULE R |
| `customers.csv` | `first_name_ar`, `last_name_ar` for 7,120 Arab guests | RULE S |
| `discount_codes.csv` | fixed amounts ×3 | RULE M |
| New | `fees.csv` (10), `menu_items.csv` (23), `loyalty_tiers.csv` (4), `loyalty_rules.csv` (7); `services.csv` 8 → 16 | — |

### Gold FAQ (`06_Scripts/repair/policy_update_v4.py`, log `gold_repair_log_v4.csv`)
Rebuilt from the frozen pre-v4 snapshot on every run, so it is idempotent.
P1 price remap (232 cells) · P2 47 facts restated in 5 languages (572 cells) · P3 ID documents ·
P4/P4b Egyptian answers brought to v4 and fitted to every paired question (132) · P5 25 rows
`escalate_to_human` · P6 `question_style` (1,872 templated) · P7 96 new questions for the new
documents · P7s sync of renamed questions.

### Conversations
630 (126 × 5 languages), identity check before booking details, dates spoken ("14 October"),
cancellation and payment flows quote the booking's real rate plan and amounts, 4 new flows.

### Application and evaluation
`09_Application/rag/` (see its README) · `05_Evaluation/realistic_test/` (200 questions) ·
`05_Evaluation/review/egyptian_review.xlsx`.

## 3. Retrieval (BM25, `retrieval_results_v4.txt`)

| Recall@5 | KB only | KB + FAQ index |
|---|---|---|
| English (test) | 0.495 | 0.604 |
| Arabic (test) | 0.008 | 0.450 |
| Egyptian (test) | 0.024 | 0.476 |
| Realistic Egyptian set | 0.043 | 0.583 |

541 of the 573 test questions ask about a fact that has no train question in the same
language, so the gain is not memorisation.

## 4. Open items for the team

1. **Run BGE-M3**: `python3 -m 09_Application.rag.evaluate --mode hybrid` (needs internet once).
2. **Native review** of the Egyptian text with the workbook; apply corrections in
   `policy_update_v4_data.py` / `conv_templates_v4.py`, then `rebuild_all.py`.
3. **Add real callers' questions** to the realistic set — it was written by an AI.
4. **Occupancy is high** (about 90%): many date ranges are fully booked. That is the data, not a
   tool bug; the tools return alternatives when other types are free.
5. BOOK_F8 (booking change) still has no identity check in its script.
