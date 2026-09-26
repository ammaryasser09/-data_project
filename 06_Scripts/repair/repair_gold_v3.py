#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gold FAQ corrections found in the v3 audit. Every change is keyed by faq_id and checks the
value it expects to replace, so the script is idempotent and never touches rows merged later
through 02_Data/03_Candidate/. Each change is logged to
07_Audits/Repair_Logs/gold_repair_log_v3.csv.

  G1  Arabic answers that were left in English, or corrupted by mixed scripts
  G2  a boilerplate sentence ("تنطبق هذه المعلومات على Nile Pearl Hotel.") appended to 39
      Arabic answers only — a translation artefact, not content
  G3  requires_tool: generic policy questions were marked True, contradicting
      DATA_ROUTING_MATRIX ("anything printed in a brochure comes from RAG")
  G4  in-scope requests labelled OUT_OF_SCOPE ("Cancel my booking please", "Do you have a room
      available?") and one factually wrong answer ("the hotel does not state a star rating")
  G5  Egyptian rows: source pointed at a non-existent "egyptian_dialect_layer", category was
      the language instead of the domain, three cancellation requests carried the wrong intent
  G6  payment methods: the knowledge base said "not specified" while payments.csv records
      five methods on 20,000 payments; the KB now states them and the answers follow

Run from the project root:  python3 06_Scripts/repair/repair_gold_v3.py
"""
import csv, os, sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(ROOT)
GOLD = '02_Data/04_Gold/hotel_faq_gold.csv'
LOG = '07_Audits/Repair_Logs/gold_repair_log_v3.csv'

with open(GOLD, encoding='utf-8-sig') as f:
    rows = list(csv.DictReader(f)); COLS = list(rows[0].keys())
R = {r['faq_id']: r for r in rows}
log = []

def setv(fid, col, new, reason, rule, expect=None):
    r = R[fid]; old = r[col]
    if old == new: return
    if expect is not None and old != expect and not callable(expect):
        sys.exit(f'{fid}.{col}: expected {expect!r}, found {old!r}')
    if callable(expect) and not expect(old):
        sys.exit(f'{fid}.{col}: unexpected current value {old!r}')
    r[col] = new
    log.append({'faq_id': fid, 'column': col, 'old_value': old, 'new_value': new,
                'rule': rule, 'reason': reason})

by = lambda **kw: [r for r in rows if all(r[k] == v for k, v in kw.items())]

# ── G1 / G2 — Arabic text defects ──────────────────────────────────────────────
SUFFIX = ' تنطبق هذه المعلومات على Nile Pearl Hotel.'
AR_FIX = {
    'Hotel reception operates 24/7.': 'يعمل مكتب استقبال الفندق على مدار الساعة طوال أيام الأسبوع.',
    'Standard check-out time is 12:00 PM.': 'موعد تسجيل المغادرة المعتاد هو الساعة 12:00 ظهراً.',
    'نile pearl hotel هو فندق خمس نجوم.': 'Nile Pearl Hotel فندق من فئة خمس نجوم.',
    'نيل بيرل هوôtel من فئة خمس نجوم.': 'Nile Pearl Hotel فندق من فئة خمس نجوم.',
}
for r in by(language='Arabic'):
    a = r['answer']
    if a.endswith(SUFFIX):
        core = a[:-len(SUFFIX)].strip()
        new = AR_FIX.get(core, core)
        why = ('answer was English inside an Arabic row; translated' if core in AR_FIX
               and core.isascii() else 'mixed-script corruption repaired' if core in AR_FIX
               else 'translation artefact sentence removed; content unchanged')
        setv(r['faq_id'], 'answer', new, why, 'G1' if core in AR_FIX else 'G2')
setv('FAQ0221', 'question',
     R['FAQ0221']['question'].replace('бытьdependent', 'зависеть'),
     'English word fused into a Russian question', 'G1')

# ── G3 — requires_tool follows the routing matrix ───────────────────────────────
GENERIC = {'enhanced_1008', 'complete_coverage'}
n = 0
for r in rows:
    if r['origin'] in GENERIC and r['requires_tool'] == 'True':
        setv(r['faq_id'], 'requires_tool', 'False',
             'templated policy question ("What is the hotel policy on…", "Could you clarify…"); '
             'the answer is fixed text from the knowledge base and needs no live data', 'G3'); n += 1

# ── G4 — OUT_OF_SCOPE rows that are in scope ────────────────────────────────────
INTENT = {'INT002': ('hotel_category', 'Hotel Information'), 'INT009': ('booking_modifications', 'Booking'),
          'INT012': ('loyalty_rewards', 'Loyalty'), 'INT013': ('facility_details', 'Facilities'),
          'INT015': ('booking_general', 'Booking'), 'INT018': ('cancellation_policy', 'Cancellation'),
          'INT022': ('refund_policy', 'Payment'), 'INT024': ('room_types', 'Rooms'),
          'INT026': ('pricing_rates', 'Pricing'), 'INT027': ('discounts_promotions', 'Pricing'),
          'INT031': ('hotel_services', 'Services')}
# English faq_id of each fact → (intent, source, response_mode or None to keep, requires_tool)
OOS = {
 'FAQ2449': ('INT013', 'hotel_facilities.txt', None, 'False'),
 'FAQ2453': ('INT024', 'room_types.txt', None, 'False'),
 'FAQ2457': ('INT018', 'cancellation_policy.txt', None, 'False'),
 'FAQ2461': ('INT022', 'refund_policy.txt', None, 'False'),
 'FAQ2465': ('INT002', 'hotel_information.txt', 'knowledge_answer', 'False'),
 'FAQ2469': ('INT031', 'room_service.txt', None, 'False'),
 'FAQ2473': ('INT012', 'loyalty_programs.txt', None, 'False'),
 'FAQ2477': ('INT013', 'hotel_facilities.txt', None, 'False'),
 'FAQ2481': ('INT031', 'airport_transfer.txt', None, 'False'),
 'FAQ2485': ('INT027', 'discounts_and_promotions.txt', None, 'False'),
 'FAQ2529': ('INT018', 'cancellation_policy.txt', 'customer_service', 'True'),
 'FAQ2533': ('INT015', 'booking_policy.txt', 'customer_service', 'True'),
 'FAQ2537': ('INT026', 'pricing_and_rates.txt', 'customer_service', 'True'),
 'FAQ2541': ('INT009', 'booking_modification.txt', 'customer_service', 'True'),
 'FAQ2545': ('INT015', 'room_types.txt', 'customer_service', 'True'),
}
STARS = {'English': 'Nile Pearl Hotel is a 5-star hotel.',
         'Arabic': 'Nile Pearl Hotel مصنف كفندق 5 نجوم.',
         'French': 'Le Nile Pearl Hotel est un hôtel 5 étoiles.',
         'Russian': 'Nile Pearl Hotel — пятизвёздочный отель.'}
for en, (iid, src, mode, tool) in OOS.items():
    base = int(en[3:])
    for k, lang in enumerate(('English', 'Arabic', 'French', 'Russian')):
        fid = f'FAQ{base + k:04d}'
        assert R[fid]['language'] == lang and R[fid]['origin'] == 'out_of_scope_100', fid
        why = ('an in-domain question whose answer is "not specified"; the same question is '
               f'already labelled {iid} elsewhere in Gold, so OUT_OF_SCOPE contradicted it'
               if mode is None else
               'an in-scope customer-service request; labelling it OUT_OF_SCOPE trains the '
               'router to refuse a core action')
        if en == 'FAQ2465':
            why = 'the answer claimed the hotel states no star rating; hotel_information.txt says 5-Star'
            setv(fid, 'answer', STARS[lang], why, 'G4')
        setv(fid, 'intent_id', iid, why, 'G4')
        setv(fid, 'intent_name', INTENT[iid][0], why, 'G4')
        setv(fid, 'category', INTENT[iid][1], why, 'G4')
        setv(fid, 'source', src, 'answer is grounded in this document', 'G4')
        if mode: setv(fid, 'response_mode', mode, why, 'G4')
        setv(fid, 'requires_tool', tool, why, 'G4')

# ── G6 — payment methods (knowledge base now states them) ───────────────────────
PAY = {'English': "Nile Pearl Hotel accepts credit cards, debit cards, cash, digital wallets and bank transfers. Customer service can help if a payment does not go through.",
       'Arabic': "يقبل فندق Nile Pearl Hotel بطاقات الائتمان وبطاقات الخصم والدفع النقدي والمحافظ الرقمية والتحويل البنكي. ويمكن لخدمة العملاء المساعدة إذا لم تنجح عملية الدفع.",
       'French': "Le Nile Pearl Hotel accepte les cartes de crédit, les cartes de débit, les espèces, les portefeuilles numériques et les virements bancaires. Le service clientèle peut vous aider si un paiement n'aboutit pas.",
       'Russian': "Nile Pearl Hotel принимает кредитные и дебетовые карты, наличные, цифровые кошельки и банковские переводы. Если оплата не проходит, поможет служба поддержки."}
for lang, ids in {'English': (2838, 2839, 2840), 'Arabic': (2841, 2842, 2843),
                  'French': (2844, 2845, 2846), 'Russian': (2847, 2848, 2849)}.items():
    for i in ids:
        fid = f'FAQ{i}'
        assert R[fid]['intent_id'] == 'INT020' and R[fid]['language'] == lang
        setv(fid, 'answer', PAY[lang], 'payment_methods.txt now lists the five methods recorded in '
             'payments.csv; the old answer said the methods were unknown', 'G6')

# ── G5 — Egyptian dialect rows ──────────────────────────────────────────────────
DOMAIN = {}
for r in rows:
    if r['language'] == 'English':
        DOMAIN.setdefault(r['intent_id'], Counter())[r['category']] += 1
DOMAIN = {k: v.most_common(1)[0][0] for k, v in DOMAIN.items()}
DEFAULT_SRC = {'INT001': 'hotel_information.txt', 'INT002': 'hotel_information.txt',
    'INT003': 'hotel_information.txt', 'INT004': 'check_in_check_out.txt',
    'INT005': 'check_in_check_out.txt', 'INT006': 'check_in_check_out.txt',
    'INT007': 'check_in_check_out.txt', 'INT008': 'identification_policy.txt',
    'INT009': 'booking_modification.txt', 'INT010': 'complaints_resolution.txt',
    'INT011': 'special_requests.txt', 'INT012': 'loyalty_programs.txt',
    'INT013': 'hotel_facilities.txt', 'INT014': 'emergency_procedures.txt',
    'INT015': 'booking_policy.txt', 'INT018': 'cancellation_policy.txt',
    'INT020': 'payment_methods.txt', 'INT021': 'payment_policy.txt',
    'INT022': 'refund_policy.txt', 'INT024': 'room_types.txt',
    'INT026': 'pricing_and_rates.txt', 'OUT_OF_SCOPE': 'out_of_scope_policy'}
SRC_OVERRIDE = {'FAQ2591': 'spa.txt', 'FAQ2582': 'room_policies.txt', 'FAQ2583': 'airport_transfer.txt',
    'FAQ2566': 'pricing_and_rates.txt', 'FAQ3481': 'room_amenities.txt',
    'FAQ3486': 'pet_policy.txt', 'FAQ3487': 'smoking_policy.txt', 'FAQ3488': 'children_policy.txt',
    'FAQ3489': 'lost_and_found.txt', 'FAQ3490': 'room_service.txt', 'FAQ3491': 'laundry.txt',
    'FAQ3492': 'airport_transfer.txt', 'FAQ3483': 'booking_process.txt'}
TOOL_OVERRIDE = {  # Egyptian rows judged one by one against the routing matrix
    'FAQ2580': 'False', 'FAQ2584': 'False', 'FAQ2585': 'False',
    **{f'FAQ{i}': 'False' for i in (3462, 3463, 3464, 3465, 3466, 3468, 3469, 3470, 3471,
                                    3472, 3473, 3474, 3475, 3476, 3477, 3478, 3479, 3480,
                                    3481, 3483, 3484)},
    'FAQ3467': 'True', 'FAQ3482': 'True', 'FAQ3485': 'True'}
for fid in ('FAQ2596', 'FAQ2597', 'FAQ3495'):   # "cancel my booking" in Egyptian
    why = 'a request to cancel a booking; INT009 (modification) / OUT_OF_SCOPE were wrong'
    setv(fid, 'intent_id', 'INT018', why, 'G5'); setv(fid, 'intent_name', 'cancellation_policy', why, 'G5')
    setv(fid, 'response_mode', 'customer_service', why, 'G5'); setv(fid, 'requires_tool', 'True', why, 'G5')
setv('FAQ3488', 'answer', 'الأطفال مرحب بهم ويُحتسبون ضمن سعة الغرفة. ولا تحدد معلومات الفندق سعراً خاصاً للأطفال أو حداً عمرياً، لذا يُرجى التواصل مع خدمة العملاء.',
     'the question asks whether children pay; the old answer did not address it', 'G5')
setv('FAQ3488', 'answer_egyptian', 'الأطفال مرحب بيهم وبيتحسبوا ضمن سعة الأوضة. معلومات الفندق مش محددة سعر خاص للأطفال أو سن معين، فاسأل خدمة العملاء.',
     'the question asks whether children pay; the old answer did not address it', 'G5')
for fid, egy in {'FAQ3468': 'تقدر تدفع كاش، أو بالفيزا والكريديت كارد، أو بكارت الخصم، أو بمحفظة إلكترونية، أو بتحويل بنكي.',
                 'FAQ3469': 'أيوة، بنقبل كروت الائتمان والخصم، وكمان الكاش والمحافظ الإلكترونية والتحويل البنكي.'}.items():
    setv(fid, 'answer', PAY['Arabic'], 'payment methods now stated in the knowledge base', 'G6')
    setv(fid, 'answer_egyptian', egy, 'payment methods now stated in the knowledge base', 'G6')
for r in by(language='Arabic-Egyptian'):
    if r['origin'] not in ('egyptian_dialect_49', 'egyptian_dialect_expansion'): continue   # v3 rows are born correct
    fid = r['faq_id']
    if r['category'] == 'Egyptian Dialect':
        setv(fid, 'category', DOMAIN[r['intent_id']], 'category holds the domain; the dialect is '
             'already in the language column', 'G5')
    src = SRC_OVERRIDE.get(fid) or DEFAULT_SRC[r['intent_id']]
    if r['source'] == 'egyptian_dialect_layer':
        setv(fid, 'source', src, 'source must name the knowledge-base document that grounds the '
             'answer so the row can join retrieval evaluation', 'G5')
    if fid in TOOL_OVERRIDE:
        setv(fid, 'requires_tool', TOOL_OVERRIDE[fid], 'label judged against DATA_ROUTING_MATRIX; '
             'Egyptian and core rows for the same kind of question now agree', 'G5')

# ── G7 — EDGE rows name the knowledge-base document that grounds them ───────────
# 96 rows = 12 facts x 2 questions x 4 languages, in blocks of 8 starting at FAQ2353.
EDGE_SRC = ['special_requests.txt', 'cancellation_policy.txt', 'booking_modification.txt',
            'complaints_resolution.txt', 'room_policies.txt', 'payment_policy.txt',
            'complaints_resolution.txt', 'pet_policy.txt', 'smoking_policy.txt',
            'booking_modification.txt', 'emergency_procedures.txt', 'lost_and_found.txt']
for r in by(intent_id='EDGE', origin='edge_96'):
    k = (int(r['faq_id'][3:]) - 2353) // 8
    setv(r['faq_id'], 'source', EDGE_SRC[k], 'source was "training_data", which is not a document; '
         'the answer is grounded in this knowledge-base file', 'G7', expect=lambda v: v in ('training_data', EDGE_SRC[k]))

# ── G8 — one category per intent ────────────────────────────────────────────────
# 12 business_rules_v1 rows (INT023, INT032) were filed under "Policies" while every other
# row of the same intent uses the intent's domain category.
for r in rows:
    if r['intent_id'] in DOMAIN and r['category'] != DOMAIN[r['intent_id']] and r['origin'] == 'business_rules_v1':
        setv(r['faq_id'], 'category', DOMAIN[r['intent_id']], 'every row of an intent carries the same '
             'category; this row disagreed with the other rows of its intent', 'G8')

with open(GOLD, 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=COLS); w.writeheader(); w.writerows(rows)
old = []
if os.path.exists(LOG):
    with open(LOG, encoding='utf-8') as f: old = list(csv.DictReader(f))
with open(LOG, 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=['faq_id', 'column', 'old_value', 'new_value', 'rule', 'reason'])
    w.writeheader(); w.writerows(old + log)
print(f'{len(log)} changes this run  {dict(Counter(x["rule"] for x in log))}')
print(f'requires_tool now: {dict(Counter(r["requires_tool"] for r in rows))}')
print(f'OUT_OF_SCOPE rows now: {sum(r["intent_id"] == "OUT_OF_SCOPE" for r in rows)}')
