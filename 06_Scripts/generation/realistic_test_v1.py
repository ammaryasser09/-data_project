#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Realistic Egyptian-Arabic test set — 200 questions the way callers actually talk.

    python3 06_Scripts/generation/realistic_test_v1.py
    → 05_Evaluation/realistic_test/realistic_test_egyptian.csv

Unlike the Gold FAQ, these questions are not templated: they carry code-switching, typos,
relative dates, spoken digits, missing details, several requests at once, anger, and
emergencies. Questions about a specific booking use real bookings; their expected facts are
computed with the same reference tools the agent uses (09_Application/rag/tools.py), so the
file stays true when SYSTEM_DATE moves.

route: RAG | DATABASE | TOOL | ACTION | CLARIFY | REFUSE | ESCALATE | EMERGENCY (may combine: TOOL+RAG)
  DATABASE  read a specific booking after the identity check
  TOOL      a read-only tool (availability, discount code, room-service quote)
  ACTION    something must be done for the guest (complaint ticket, service request, change)
expected_doc: KB file(s) that hold the answer, ';'-separated ('out_of_scope_policy' for REFUSE)
must_not: what a correct answer must avoid.
"""
import csv, importlib, json, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(ROOT); sys.path.insert(0, ROOT)
T = importlib.import_module('09_Application.rag.tools')
from datetime import date, timedelta
TODAY = T.SYSTEM_DATE

def rd(p): return list(csv.DictReader(open(p, encoding='utf-8-sig')))
bk = rd('02_Data/02_Operational/bookings.csv'); cu = {c['customer_id']: c for c in rd('02_Data/02_Operational/customers.csv')}
pay = {p['booking_id']: p for p in rd('02_Data/02_Operational/payments.csv')}
members = {m['customer_id'] for m in rd('02_Data/02_Operational/loyalty_members.csv') if m['status'] == 'Active'}
used = set(re.findall(r'B\d{6}', open('02_Data/04_Gold/conversations_gold.csv', encoding='utf-8').read()))
D = date.fromisoformat

def pick(cond):
    for b in sorted(bk, key=lambda b: b['booking_id']):
        c = cu[b['customer_id']]
        if b['booking_id'] not in used and c['last_name_ar'] and cond(b, pay[b['booking_id']]):
            used.add(b['booking_id']); return b
    raise SystemExit('no booking for a pick')
fut = lambda b: b['booking_status'] == 'Confirmed' and D(b['check_in']) > TODAY + timedelta(days=10)
P = {
 'FLEX':  pick(lambda b, p: fut(b) and b['rate_plan'] == 'Flexible' and p['payment_status'] == 'Paid'),
 'NR':    pick(lambda b, p: fut(b) and b['rate_plan'] == 'Non-refundable'),
 'SOON':  pick(lambda b, p: b['booking_status'] == 'Confirmed' and D(b['check_in']) == TODAY + timedelta(days=1) and b['rate_plan'] == 'Flexible'),
 'PEND':  pick(lambda b, p: fut(b) and p['payment_status'] == 'Pending'),
 'FAIL':  pick(lambda b, p: fut(b) and p['payment_status'] == 'Failed'),
 'CREF':  pick(lambda b, p: b['booking_status'] == 'Cancelled' and p['payment_status'] == 'Refunded' and D(b['check_in']) > TODAY - timedelta(days=60)),
 'CPART': pick(lambda b, p: b['booking_status'] == 'Cancelled' and p['payment_status'] == 'Partially Refunded'),
 'DONE':  pick(lambda b, p: b['booking_status'] == 'Completed' and TODAY - timedelta(days=20) <= D(b['check_out']) <= TODAY),
 'INH':   pick(lambda b, p: b['blocks_inventory'] == 'True' and D(b['check_in']) <= TODAY < D(b['check_out']) - timedelta(days=1)),
 'MEM':   pick(lambda b, p: fut(b) and b['customer_id'] in members),
}
V = {}
for k, b in P.items():
    c = cu[b['customer_id']]
    V[k] = b['booking_id']; V[k + '_LN'] = c['last_name_ar']; V[k + '_FN'] = c['first_name_ar']; V[k + '_PH'] = c['phone'][-4:]
def ln(k): return {'last_name': cu[P[k]['customer_id']]['last_name']}
def fb(k): r = T.find_booking(V[k], **ln(k)); return f"status={r['status']}; {r['check_in']}..{r['check_out']}; {r['room_type']}; rate_plan={r['rate_plan']}; total={r['total']:,.2f}; payment={r['payment_status']}; paid={r['amount_paid']:,.2f}; refunded={r['refund_amount']:,.2f}"
def qc(k): r = T.quote_cancellation(V[k], **ln(k)); return f"{r['rule']}; charge={r['charge']:,.2f}; refund={r['refund']:,.2f}; charged_to_card={r.get('charged_to_guarantee_card', 0):,.2f}" if r['ok'] else r['reason']
def lc(k, until): r = T.late_checkout_quote(V[k], until, **ln(k)); return f"until {r['until']}: {r['price']:,.2f} EGP ({r['rule']}); subject to availability"
def av(t, ci, co, g):
    r = T.check_availability(t, ci, co, g)
    if not r['ok']: return r['reason'] + (f"; types that fit: {r.get('room_types_that_fit')}" if r.get('room_types_that_fit') else '')
    alt = f"; alternatives: {[(a['room_type'], a['rooms_free']) for a in r['alternatives']]}" if not r['rooms_free'] else ''
    return f"{r['room_type']} {ci}..{co} ({r['nights']} nights): {r['rooms_free']} free ({r['nile_view_free']} Nile view); standard {r['flexible_total']:,.0f} EGP flexible / {r['non_refundable_total']:,.0f} non-refundable{alt}"
def dc(code): r = T.check_discount_code(code); return f"{r.get('status', r.get('reason'))}" + (f"; {r['discount']}" if 'discount' in r else '')
def ls(k): r = T.loyalty_status(V[k], **ln(k)); return f"tier={r.get('tier')}; points={r.get('points')}; worth={r.get('points_worth_egp')} EGP" if r.get('member') else 'not a member'
def rs(items): r = T.room_service_quote(items); return f"items {sum(l['price'] for l in r['lines']):,} + delivery {r['delivery']} = {r['total']:,} EGP; 30-45 min"
def nxt_tier(k):
    tiers = rd('02_Data/02_Operational/loyalty_tiers.csv'); cur = T.loyalty_status(V[k], **ln(k))['tier']
    i = [t['tier'] for t in tiers].index(cur)
    return f"next tier {tiers[i + 1]['tier']} at {tiers[i + 1]['min_nights_per_year']} nights in a calendar year" if i + 1 < len(tiers) else 'already the top tier'
def room(k): r = T.find_booking(V[k], **ln(k)); return f"room {r['room_number']}"
nxt = lambda wd: TODAY + timedelta(days=(wd - TODAY.weekday()) % 7 or 7)   # next given weekday
SUN = nxt(6)
NOVERIFY = 'reveal any booking detail before the booking reference AND last name / phone digits match'

Q = [
# ── 1. information ──
('information', 'الفندق فين بالظبط؟', 'INT001', 'RAG', 'hotel_information.txt;location_and_surroundings.txt', '', '14 Corniche El Nil Street, Garden City, Cairo', '', ''),
('information', 'انتوا بعيد عن المطار قد ايه؟', 'INT001', 'RAG', 'location_and_surroundings.txt;airport_transfer.txt', '', 'about 25 km; 35-60 minutes by car', '', 'typo'),
('information', 'من عندكم للأهرامات بتاخد وقت قد إيه بالعربية؟', 'INT001', 'RAG', 'location_and_surroundings.txt', '', 'about 17 km; 40-60 minutes', '', ''),
('information', 'الفندق كام نجمة؟', 'INT002', 'RAG', 'hotel_information.txt', '', '5-star', '', ''),
('information', 'الريسبشن بيبقى فاتح بالليل؟', 'INT003', 'RAG', 'hotel_information.txt', '', 'reception 24/7', '', 'code_switch'),
('information', 'الـ check in الساعة كام؟', 'INT004', 'RAG', 'check_in_check_out.txt', '', '3:00 PM', '', 'code_switch'),
('information', 'لازم أسيب الأوضة امتى يوم السفر؟', 'INT005', 'RAG', 'check_in_check_out.txt', '', 'check-out 12:00 PM', '', ''),
('information', 'البيسين بيفتح امتى وبيقفل امتى؟', 'INT013', 'RAG', 'hotel_facilities.txt', '', '7:00 AM - 9:00 PM', '', ''),
('information', 'الجيم بفلوس ولا ببلاش؟', 'INT013', 'RAG', 'gym.txt;hotel_facilities.txt', '', 'free for hotel guests; open 24/7', '', ''),
('information', 'الواي فاي عندكم ببلاش؟ والباسورد بلاقيه فين؟', 'INT013', 'RAG', 'hotel_facilities.txt', '', 'free; network and password on the key-card holder', '', 'code_switch'),
('information', 'في جراج؟ وبكام الركنة؟', 'INT013', 'RAG', 'hotel_facilities.txt', '', 'free for guests; valet 24/7', '', ''),
('information', 'الفطار بوفيه ولا بتطلب من منيو؟', 'INT031', 'RAG', 'breakfast.txt', '', 'buffet 7:00-10:30; 1,200 EGP per adult', '', ''),
('information', 'الفطار فيه فول وطعمية؟', 'INT031', 'RAG', 'breakfast.txt', '', 'Egyptian specialities such as foul and taameya', '', ''),
('information', 'المطعم بيقدم عشا لحد الساعة كام؟', 'INT031', 'RAG', 'restaurant.txt', '', 'dinner 7:00-11:00 PM', '', ''),
('information', 'عندكم أكل نباتي؟', 'INT031', 'RAG', 'restaurant.txt;in_room_dining_menu.txt', '', 'vegetarian dishes marked V; vegan and gluten-free on request', '', ''),
('information', 'البرجر عندكم بكام في الروم سيرفس؟', 'INT031', 'RAG', 'in_room_dining_menu.txt;room_service.txt', '', 'beef burger 1,150 EGP + 300 EGP delivery per order', '', 'code_switch'),
('information', 'في كشري في المنيو؟', 'INT031', 'RAG', 'in_room_dining_menu.txt', '', 'koshary 350 EGP', '', ''),
('information', 'السبا فيه مساج ساعة ونص؟ بكام؟', 'INT013', 'RAG', 'spa.txt', '', '90-minute massage 4,800 EGP', '', ''),
('information', 'السبا مفتوح لحد امتى؟', 'INT013', 'RAG', 'spa.txt;hotel_facilities.txt', '', '9:00 AM - 10:00 PM', '', ''),
('information', 'الغسيل بياخد قد إيه وقت؟', 'INT031', 'RAG', 'laundry.txt', '', 'handed in before 10 AM: same day by 7 PM; express 4 h +50%', '', ''),
('information', 'المكوى والغسيل بكام؟', 'INT031', 'RAG', 'laundry.txt', '', '500 EGP per kilogram', '', 'typo'),
('information', 'عربية المطار تاخد كام فرد بالشنط؟', 'INT031', 'RAG', 'airport_transfer.txt', '', 'sedan up to 3 guests with luggage 2,500; minivan up to 6 guests 4,000', '', ''),
('information', 'لو طيارتي اتأخرت السواق هيستناني؟', 'INT031', 'RAG', 'airport_transfer.txt', '', 'driver waits up to 60 minutes after landing at no extra charge', '', ''),
('information', 'الأوضة الدبل مساحتها قد إيه؟', 'INT024', 'RAG', 'room_types.txt', '', '34 m²', '', ''),
('information', 'الجناح فيه صالة لوحدها؟', 'INT024', 'RAG', 'room_types.txt', '', 'separate living area; 85 m²; Nile view', '', ''),
('information', 'كل الأوض فيها تكييف وتلفزيون؟', 'INT025', 'RAG', 'room_amenities.txt', '', 'air conditioning, TV, private bathroom in every room', '', ''),
('information', 'في أوض مجهزة للكراسي المتحركة؟', 'INT028', 'RAG', 'accessibility.txt;special_requests.txt', '', 'accessible rooms available; request when booking', '', ''),
('information', 'أقرب مترو ليكم إيه؟', 'INT001', 'RAG', 'location_and_surroundings.txt', '', 'Saad Zaghloul and Sadat, about 1 km', '', ''),
('information', 'بتتكلموا فرنساوي؟ ماما مش بتعرف عربي كويس', 'INT013', 'RAG', 'hotel_information.txt', '', 'Arabic, English, French, Russian', '', ''),
('information', 'رقم الريسبشن كام؟', 'INT032', 'RAG', 'contact_information.txt', '', '+20 2 2794 5500, 24/7', '', ''),
# ── 2. policy ──
('policy', 'لو لغيت قبل ميعادي بأسبوع هدفع حاجة؟', 'INT018', 'RAG', 'cancellation_policy.txt', '', 'Flexible: free until 48 h before arrival; Non-refundable: nothing refunded', 'state one universal fee', ''),
('policy', 'الـ non refundable ده يعني إيه بالظبط؟', 'INT018', 'RAG', 'cancellation_policy.txt;pricing_and_rates.txt', '', 'paid in full at booking; no cancellation, change or refund; 15% cheaper', '', 'code_switch'),
('policy', 'إيه الفرق بين الحجز المرن واللي مش بيترد؟', 'INT026', 'RAG', 'pricing_and_rates.txt', '', 'Flexible: free cancellation 48 h, pay at hotel; Non-refundable: 15% less, prepaid, no refund', '', ''),
('policy', 'الفلوس بترجع بعد قد إيه لو لغيت؟', 'INT022', 'RAG', 'refund_policy.txt', '', 'processed within 3 business days; card 7-14 business days; transfer up to 14', '', ''),
('policy', 'لو ماجيتش خالص هيحصل إيه؟', 'INT033', 'RAG', 'no_show_policy.txt', '', 'held until 23:59; Flexible: first night charged; Non-refundable: nothing refunded', '', ''),
('policy', 'هوصل 2 بالليل، الحجز هيتلغي؟', 'INT033', 'RAG', 'no_show_policy.txt;special_requests.txt', '', 'tell the hotel in advance and the booking is held; reception 24/7', '', 'numbers'),
('policy', 'ينفع أغير التاريخ بعد ما حجزت؟', 'INT009', 'RAG', 'booking_modification.txt', '', 'Flexible: free until 48 h before arrival, subject to availability and rate difference; Non-refundable cannot be changed', '', ''),
('policy', 'حاجز من بوكينج، أعدل منكم ولا منهم؟', 'INT009', 'RAG', 'booking_modification.txt', '', 'booking-platform reservations are changed through that platform', '', ''),
('policy', 'ينفع أغير اسم اللي نازل في الحجز؟', 'INT009', 'RAG', 'booking_modification.txt', '', 'free until 48 h before arrival; new guest shows valid ID', '', ''),
('policy', 'لو مشيت بدري يوم هتحسبوه عليا؟', 'INT009', 'RAG', 'booking_modification.txt;cancellation_policy.txt', '', 'one extra night charged unless reception is told at check-in', '', ''),
('policy', 'بتاخدوا تأمين وقت الدخول؟', 'INT021', 'RAG', 'payment_policy.txt', '', '3,000 EGP per night, card hold or cash, released at check-out', '', ''),
('policy', 'الأسعار دي فيها ضرايب ولا هتتزود؟', 'INT026', 'RAG', 'pricing_and_rates.txt', '', 'prices include 12% service, 14% VAT and 1% city tax', 'add taxes on top', ''),
('policy', 'بتقبلوا فودافون كاش؟', 'INT020', 'RAG', 'payment_methods.txt', '', 'yes; also Apple Pay, cards, cash, bank transfer', '', ''),
('policy', 'ينفع أحول انستا باي؟', 'INT020', 'RAG', 'payment_methods.txt', '', 'bank transfer including InstaPay', '', 'typo'),
('policy', 'ينفع أدفع بالدولار كاش؟', 'INT021', 'RAG', 'payment_policy.txt;payment_methods.txt', '', 'payments in EGP; cash in EGP; foreign cards charged in EGP', '', ''),
('policy', 'لازم أدفع كله وأنا بحجز؟', 'INT021', 'RAG', 'payment_policy.txt', '', 'Flexible: card guarantee, pay at the hotel; Non-refundable: full at booking', '', ''),
('policy', 'الدخول بدري الساعة 10 الصبح بكام؟', 'INT006', 'RAG', 'check_in_check_out.txt', '', 'before 12:00: 50% of the nightly rate; from 12:00 free if available', '', 'numbers'),
('policy', 'الخروج الساعة 5 العصر هيتحسب كام؟', 'INT007', 'RAG', 'check_in_check_out.txt', '', 'until 6 PM: 50% of the nightly rate (until 4 PM: 1,500)', '', 'numbers'),
('policy', 'ولو فضلت لحد 8 بالليل؟', 'INT007', 'RAG', 'check_in_check_out.txt', '', 'after 6 PM: a full night', '', 'context_dependent'),
('policy', 'الأطفال بيدفعوا فطار؟ عندي ولد 8 سنين وبنت 4', 'INT030', 'RAG', 'children_policy.txt;breakfast.txt', '', '8-year-old: 600 EGP; 4-year-old: free', '', 'numbers'),
('policy', 'سرير البيبي بفلوس؟', 'INT030', 'RAG', 'children_policy.txt', '', 'baby cot free', '', ''),
('policy', 'السرير الإضافي بكام؟', 'INT023', 'RAG', 'room_policies.txt;pricing_and_rates.txt', '', '2,500 EGP per night; does not raise capacity', '', ''),
('policy', 'النقط بتاعة الولاء بتخلص امتى؟', 'INT012', 'RAG', 'loyalty_programs.txt', '', 'after 24 months without earning or using points', '', ''),
('policy', 'أوصل للجولد إزاي؟', 'INT012', 'RAG', 'loyalty_programs.txt', '', '25 nights in a calendar year', '', 'code_switch'),
('policy', 'ينفع أحول نقطي لأخويا؟', 'INT012', 'RAG', 'loyalty_programs.txt', '', 'points are not transferable', '', ''),
('policy', 'ينفع أستخدم كود خصم مع سعر الأعضاء؟', 'INT027', 'RAG', 'discounts_and_promotions.txt;loyalty_programs.txt', '', 'only one discount per booking; the best applicable rate is used', '', ''),
('policy', 'لو حجزت 12 أوضة لفرح في خصم؟', 'INT015', 'RAG', 'booking_policy.txt', '', 'group rate 18% off for 10+ rooms; 30% deposit; free release until 30 days before', '', 'numbers'),
('policy', 'الحاجات اللي بتضيع بتحتفظوا بيها قد إيه؟', 'INT030', 'RAG', 'lost_and_found.txt', '', '90 days; valuables in the safe', '', ''),
('policy', 'التأكيد بيوصل ازاي؟', 'INT017', 'RAG', 'booking_confirmation.txt', '', 'email and SMS immediately; reference B + 6 digits', '', ''),
('policy', 'ليه بتطلبوا مني آخر 4 أرقام من التليفون؟', 'INT017', 'RAG', 'reservation_security.txt', '', 'identity check before discussing a booking', '', ''),
# ── 3. booking request ──
('booking_request', f'عايز أوضة دبل من 24 لـ 27 ديسمبر لاتنين', 'INT015', 'TOOL', 'pricing_and_rates.txt', 'check_availability', av('Double', '2026-12-24', '2026-12-27', 2), '', 'dates'),
('booking_request', 'في فاميلي فاضية من 10 لـ 14 أكتوبر؟ إحنا 4', 'INT015', 'TOOL', 'room_types.txt', 'check_availability', av('Family', '2026-10-10', '2026-10-14', 4), '', 'code_switch;dates'),
('booking_request', 'محتاج سويت ليلة راس السنة لاتنين', 'INT015', 'TOOL', 'room_types.txt', 'check_availability', av('Suite', '2026-12-31', '2027-01-01', 2), '', 'relative_date'),
('booking_request', 'عايز أحجز سينجل تلات ليالي من الحد الجاي', 'INT015', 'TOOL', 'room_types.txt', 'check_availability', av('Single', str(SUN), str(SUN + timedelta(days=3)), 1), 'guess a date without saying which Sunday', 'relative_date'),
('booking_request', 'في أوضة تاخد خمسة أفراد؟', 'INT023', 'RAG', 'booking_policy.txt;children_policy.txt;room_policies.txt', '', 'no room holds more than 4; two rooms needed', 'offer an extra bed as a way to fit 5', ''),
('booking_request', 'عايز دبل لتلاتة، أنا ومراتي وابننا 5 سنين', 'INT023', 'CLARIFY+RAG', 'children_policy.txt;room_types.txt', 'check_availability', 'children count toward capacity; Double holds 2; Deluxe holds 3; ask the dates', 'book a Double for 3', ''),
('booking_request', 'بكام الليلة في الديلوكس؟', 'INT026', 'RAG', 'room_types.txt;pricing_and_rates.txt', '', '12,000 EGP per night standard rate, room only', '', ''),
('booking_request', 'عايز أوضة على النيل من 5 لـ 8 نوفمبر لفردين', 'INT015', 'TOOL+RAG', 'room_types.txt', 'check_availability', av('Double', '2026-11-05', '2026-11-08', 2) + '; guaranteed Nile view +2,000 EGP per night', '', 'dates'),
('booking_request', 'الأسبوع الجاي عندكم مكان؟', 'INT015', 'CLARIFY', '', 'check_availability', 'ask exact dates, number of guests, room type', 'answer availability without dates', 'relative_date'),
('booking_request', 'عايز أحجز بس مش عارف أنهي أوضة تنفعني، إحنا اتنين وطفل', 'INT024', 'CLARIFY+RAG', 'room_types.txt;children_policy.txt', '', 'Deluxe holds 3 (children count); ask dates and child age', '', ''),
('booking_request', 'لو حجزت 8 ليالي في خصم؟', 'INT027', 'RAG', 'discounts_and_promotions.txt', '', 'extended stay 7+ nights: 12% off', '', 'numbers'),
('booking_request', 'عايز أحجز توين من بكرة', 'INT015', 'CLARIFY', 'room_types.txt', 'check_availability', f'check-in {TODAY + timedelta(days=1)}; ask number of nights and guests', '', 'relative_date'),
('booking_request', 'أحجز ازاي من غير ما أكلمكم؟', 'INT016', 'RAG', 'booking_policy.txt;booking_process.txt', '', 'hotel website, booking platforms, email', '', ''),
('booking_request', 'ينفع أحجز النهارده وأدفع لما أوصل؟', 'INT021', 'RAG', 'payment_policy.txt;pricing_and_rates.txt', '', 'yes with the Flexible rate: card guarantee, pay at the hotel', '', ''),
('booking_request', 'كود PEARL100 شغال؟', 'INT027', 'TOOL', 'discounts_and_promotions.txt', 'check_discount_code', dc('PEARL100'), '', 'code_switch'),
('booking_request', 'جربت كود PEARL750 مش راضي يشتغل ليه؟', 'INT027', 'TOOL', 'discounts_and_promotions.txt', 'check_discount_code', dc('PEARL750') + '; usage limit reached', '', ''),
('booking_request', 'عندي كود PEARL888 ينفع أستخدمه دلوقتي؟', 'INT027', 'TOOL', 'discounts_and_promotions.txt', 'check_discount_code', dc('PEARL888') + '; not valid yet', '', ''),
('booking_request', 'الكود PEARL123 شغال؟', 'INT027', 'TOOL', 'discounts_and_promotions.txt', 'check_discount_code', dc('PEARL123'), 'invent a discount', ''),
('booking_request', 'عايز أحجز من 3 لـ 5 سبتمبر', 'INT015', 'CLARIFY', '', 'check_availability', f'those dates have passed (today {TODAY}); ask whether September next year is meant', 'check the past dates', 'past_date'),
('booking_request', 'توين من 20 لـ 22 نوفمبر لاتنين، والفطار بكام؟', 'INT015', 'TOOL+RAG', 'breakfast.txt', 'check_availability', av('Twin', '2026-11-20', '2026-11-22', 2) + '; breakfast 1,200 EGP per adult', '', 'multi'),
('booking_request', 'في أوض فاضية الويك إند ده؟', 'INT015', 'CLARIFY', '', 'check_availability', 'ask which nights, guests and room type', '', 'relative_date;code_switch'),
('booking_request', 'بكام السويت تلات ليالي؟', 'INT026', 'RAG', 'pricing_and_rates.txt;room_types.txt', '', '3 x 20,000 = 60,000 EGP at the standard rate; confirmed rate depends on dates', '', 'numbers'),
# ── 4. specific booking ──
('specific_booking', f'حجزي رقم {V["FLEX"]} اتأكد ولا لأ؟', 'INT017', 'CLARIFY', 'reservation_security.txt', 'find_booking', 'ask for the last name or last 4 phone digits first', NOVERIFY, 'verification'),
('specific_booking', f'رقم الحجز {V["FLEX"]} باسم {V["FLEX_LN"]}، عايز أتأكد من المواعيد', 'INT017', 'DATABASE', '', 'find_booking', fb('FLEX'), '', 'arabic_name'),
('specific_booking', f'أنا {V["FLEX_FN"]} {V["FLEX_LN"]}، حجز {V["FLEX"]}، دفعت ولا لسه؟', 'INT021', 'DATABASE', '', 'find_booking', fb('FLEX'), '', 'arabic_name'),
('specific_booking', f'عايز ألغي حجز {V["NR"]}، الاسم {V["NR_LN"]}، هيرجعلي كام؟', 'INT018', 'DATABASE+ACTION', 'cancellation_policy.txt', 'quote_cancellation', qc('NR'), 'promise any refund', 'arabic_name'),
('specific_booking', f'حجز {V["FLEX"]} باسم {V["FLEX_LN"]}، لو لغيت دلوقتي هدفع حاجة؟', 'INT018', 'DATABASE', 'cancellation_policy.txt', 'quote_cancellation', qc('FLEX'), '', 'arabic_name'),
('specific_booking', f'حجزي {V["SOON"]} بكرة وعايز ألغيه، آخر أربع أرقام {V["SOON_PH"]}', 'INT018', 'DATABASE+ACTION', 'cancellation_policy.txt', 'quote_cancellation', qc('SOON'), 'say the cancellation is free', 'numbers'),
('specific_booking', f'حجز {V["PEND"]} باسم {V["PEND_LN"]}، الدفع لسه معلق ليه؟', 'INT021', 'DATABASE', 'payment_policy.txt', 'find_booking', fb('PEND') + '; Flexible rate is paid at the hotel', '', 'arabic_name'),
('specific_booking', f'الكارت اترفض في حجز {V["FAIL"]}، الاسم {V["FAIL_LN"]}، أعمل إيه؟', 'INT021', 'DATABASE+RAG', 'payment_methods.txt', 'find_booking', fb('FAIL') + '; use another card or method', 'ask for card details in the call', 'arabic_name'),
('specific_booking', f'لغيت حجز {V["CREF"]} من فترة، فلوسي رجعت؟ الاسم {V["CREF_LN"]}', 'INT022', 'DATABASE', 'refund_policy.txt', 'find_booking', fb('CREF'), '', 'arabic_name'),
('specific_booking', f'حجز {V["CPART"]} اتلغى ومرجعليش كل الفلوس ليه؟ باسم {V["CPART_LN"]}', 'INT022', 'DATABASE+RAG', 'cancellation_policy.txt;refund_policy.txt', 'find_booking', fb('CPART') + '; late Flexible cancellation keeps the first night', '', 'arabic_name'),
('specific_booking', f'أنا في الأوضة دلوقتي، حجز {V["INH"]} باسم {V["INH_LN"]}، عايز أخرج الساعة 4 بدل 12', 'INT007', 'DATABASE+ACTION', 'check_in_check_out.txt', 'late_checkout_quote', lc('INH', '16:00'), '', 'numbers'),
('specific_booking', f'رقم حجزي {V["INH"]}، الاسم {V["INH_LN"]}، ممكن أفضل لحد 7 بالليل؟', 'INT007', 'DATABASE', 'check_in_check_out.txt', 'late_checkout_quote', lc('INH', '19:00'), '', 'numbers'),
('specific_booking', f'عايز أعرف نقطي، حجز {V["MEM"]} باسم {V["MEM_LN"]}', 'INT012', 'DATABASE', 'loyalty_programs.txt', 'loyalty_status', ls('MEM'), '', 'arabic_name'),
('specific_booking', f'أنا في مستوى إيه، ومحتاج كام ليلة عشان أطلع المستوى اللي بعده؟ حجز {V["MEM"]}، {V["MEM_LN"]}', 'INT012', 'DATABASE+RAG', 'loyalty_programs.txt', 'loyalty_status', ls('MEM') + '; ' + nxt_tier('MEM'), '', ''),
('specific_booking', 'حجز B999999 باسم محمد', 'INT017', 'DATABASE', '', 'find_booking', 'BOOKING_NOT_FOUND; ask the caller to check the reference in the confirmation email or SMS', 'invent a booking', ''),
('specific_booking', f'حجز {V["FLEX"]} باسم أحمد', 'INT017', 'DATABASE', 'reservation_security.txt', 'find_booking', 'IDENTITY_NOT_VERIFIED; ask again or for the phone digits', NOVERIFY, 'verification'),
('specific_booking', f'عايز أغير حجز {V["FLEX"]} لسويت، الاسم {V["FLEX_LN"]}', 'INT009', 'DATABASE+TOOL', 'booking_modification.txt', 'check_availability', fb('FLEX') + ' -> check Suite availability for the same dates; Suite rate applies', '', 'arabic_name'),
('specific_booking', f'عايز أزود ليلة في حجز {V["INH"]}، الاسم {V["INH_LN"]}', 'INT009', 'DATABASE+TOOL', 'booking_modification.txt', 'check_availability', fb('INH') + ' -> check one more night from the current check-out', '', ''),
('specific_booking', f'حجز {V["DONE"]} باسم {V["DONE_LN"]}، عايز أعرف اتحاسبت كام', 'INT021', 'DATABASE', '', 'find_booking', fb('DONE'), '', 'arabic_name'),
('specific_booking', f'عايز فاتورة حجز {V["DONE"]}', 'INT021', 'CLARIFY', 'reservation_security.txt', 'find_booking', 'verify first; invoice goes to the email on the booking', NOVERIFY, 'verification'),
('specific_booking', f'حجز {V["FLEX"]} باسم {V["FLEX_LN"]}، ينفع أضيف فطار؟', 'INT031', 'DATABASE+RAG', 'breakfast.txt', 'find_booking', 'breakfast 1,200 EGP per adult per day; children 6-11 600; under 6 free', '', ''),
('specific_booking', f'حجزي {V["NR"]} مش قابل للاسترداد، ينفع أغير التاريخ بس؟', 'INT009', 'RAG', 'booking_modification.txt;cancellation_policy.txt', '', 'Non-refundable reservations cannot be changed', 'offer a free date change', ''),
('specific_booking', f'أنا حاجز باسم {V["FLEX_FN"]} {V["FLEX_LN"]} بس مش فاكر رقم الحجز', 'INT017', 'CLARIFY', 'booking_confirmation.txt;reservation_security.txt', 'find_booking', 'reference is in the confirmation email/SMS; ask for it or the phone digits', NOVERIFY, 'arabic_name'),
('specific_booking', f'اتخصم مني أول ليلة في حجز {V["CPART"]} وأنا لاغي قبلها بتلات أيام!', 'INT010', 'ACTION', 'complaints_resolution.txt;cancellation_policy.txt', 'find_booking', 'verify; 3 days is more than 48 h so a Flexible cancellation should be free; log a billing complaint', 'dismiss the claim', 'emotional'),
('specific_booking', f'عايز أكنسل الريزيرفيشن {V["FLEX"]} لو سمحت', 'INT018', 'CLARIFY', 'reservation_security.txt', 'quote_cancellation', 'verify identity, then quote before cancelling', NOVERIFY, 'code_switch;verification'),
('specific_booking', 'رقم الحجز بي زيرو واحد اتنين تلاتة أربعة خمسة', 'INT017', 'CLARIFY', 'reservation_security.txt', 'find_booking', 'read back B012345 and ask for the last name', NOVERIFY, 'spoken_digits'),
('specific_booking', f'الأوضة رقم كام في حجز {V["INH"]}؟ الاسم {V["INH_LN"]}', 'INT017', 'DATABASE', '', 'find_booking', room('INH'), '', ''),
('specific_booking', f'ممكن أعرف حجز مراتي؟ الحجز باسمها {V["FLEX_LN"]}', 'INT017', 'CLARIFY', 'reservation_security.txt', 'find_booking', 'ask for the booking reference', NOVERIFY, 'verification'),
# ── 5. complaints ──
('complaint', 'التكييف في أوضتي مش شغال من امبارح', 'INT010', 'ACTION', 'complaints_resolution.txt', '', 'apologise; send maintenance now; offer a room change', 'blame the guest', ''),
('complaint', 'الأوضة ريحتها سجاير وأنا طالب غير مدخنين', 'INT010', 'ACTION', 'complaints_resolution.txt;smoking_policy.txt', '', 'apologise; offer another room; rooms are non-smoking', '', ''),
('complaint', 'المية السخنة مش بتيجي', 'INT010', 'ACTION', 'complaints_resolution.txt', '', 'apologise; maintenance priority', '', ''),
('complaint', 'الجيران عاملين دوشة ومش عارف أنام', 'INT010', 'ACTION', 'noise_policy.txt', '', 'quiet hours 11 PM - 7 AM; reception will act; room change if needed', '', ''),
('complaint', 'الواي فاي بيقطع كل شوية', 'INT010', 'ACTION', 'complaints_resolution.txt', '', 'apologise; report to reception / IT', '', ''),
('complaint', 'طلبت روم سيرفس من ساعة ولسه ماجاش', 'INT010', 'ACTION', 'room_service.txt', '', 'usual delivery 30-45 min; chase the order now', '', 'code_switch'),
('complaint', 'اتحاسبت على ميني بار ماشربتش منه', 'INT010', 'ACTION', 'complaints_resolution.txt', '', 'billing dispute handled as a complaint; review the charge', '', ''),
('complaint', 'لقيت الملايات مش نضيفة', 'INT010', 'ACTION', 'complaints_resolution.txt', '', 'apologise; housekeeping now', '', ''),
('complaint', 'الموظف في الريسبشن كلمني بطريقة وحشة', 'INT010', 'ESCALATE', 'complaints_resolution.txt', 'escalate_to_human', 'apologise; staff complaint to management', 'defend or name the employee', 'emotional'),
('complaint', 'عايز تعويض عن اليوم اللي باظ ده', 'INT010', 'ESCALATE', 'complaints_resolution.txt', 'escalate_to_human', 'compensation is a management decision; escalate', 'promise an amount', 'emotional'),
('complaint', 'نسيت ساعتي في الأوضة وأنا خارج', 'INT030', 'ACTION', 'lost_and_found.txt', '', 'lost and found: kept 90 days; collect with ID or courier at guest cost', '', ''),
('complaint', 'الأسانسير عطلان وأنا في الدور 14 ومعايا عربية أطفال', 'INT010', 'ACTION', 'complaints_resolution.txt', '', 'urgent maintenance; staff help now', '', 'numbers'),
('complaint', 'دي تالت مرة أشتكي من نفس المشكلة', 'INT010', 'ESCALATE', 'complaints_resolution.txt', 'escalate_to_human', 'escalate to management', '', 'emotional'),
('complaint', 'طلبت فيو نيل واديتوني أوضة على الشارع', 'INT011', 'ACTION', 'special_requests.txt;room_types.txt', '', 'free view requests depend on availability; try to move; guaranteed Nile view is 2,000 EGP per night', 'promise a Nile room', ''),
('complaint', 'الفطار خلص وأنا نازل الساعة 10', 'INT010', 'ACTION', 'breakfast.txt', '', 'breakfast runs until 10:30; apologise and report to the restaurant', '', 'numbers'),
('complaint', 'ركنت العربية والفاليه خبطها', 'INT010', 'ESCALATE', 'complaints_resolution.txt', 'escalate_to_human', 'damage claim goes to management', 'accept liability', ''),
('complaint', 'الأوضة أصغر من اللي في الصور', 'INT010', 'ACTION', 'room_types.txt;complaints_resolution.txt', '', 'state the room size; offer a change or upgrade subject to availability', '', ''),
('complaint', 'السرير بيزيّق ومش عارفين ننام', 'INT010', 'ACTION', 'complaints_resolution.txt', '', 'maintenance or room change', '', ''),
# ── 6. clarification ──
('clarification', 'بكام؟', '', 'CLARIFY', '', '', 'ask what the price is for', 'guess a price', 'vague'),
('clarification', 'عندكم أوض؟', 'INT015', 'CLARIFY', '', 'check_availability', 'ask dates, guests, room type', '', 'vague'),
('clarification', 'عايز أحجز', 'INT015', 'CLARIFY', '', '', 'ask dates, guests, room type', '', 'vague'),
('clarification', 'هو ينفع؟', '', 'CLARIFY', '', '', 'ask what the caller wants to do', '', 'vague'),
('clarification', 'عايز أكلم حد', '', 'CLARIFY', '', 'escalate_to_human', 'ask what it is about; offer the transfer', '', 'vague'),
('clarification', 'الأوضة', '', 'CLARIFY', '', '', 'ask what about the room', '', 'vague'),
('clarification', 'ألو؟ سامعني؟', '', 'CLARIFY', '', '', 'confirm you hear them; ask how to help', '', 'voice'),
('clarification', 'عايز حاجة للأوضة', 'INT031', 'CLARIFY', '', '', 'ask what: room service, housekeeping, amenities', '', 'vague'),
('clarification', 'هو الموضوع ده بفلوس؟', '', 'CLARIFY', '', '', 'ask which service', 'guess', 'vague;context_dependent'),
('clarification', 'كنت كلمتكم امبارح بخصوص الموضوع', '', 'CLARIFY', '', '', 'no memory of past calls; ask for details and the booking reference', 'pretend to remember', 'vague'),
('clarification', 'عايز أغير', 'INT009', 'CLARIFY', '', '', 'ask what to change and the booking reference', '', 'vague'),
('clarification', 'إمتى؟', '', 'CLARIFY', '', '', 'ask what time they mean', '', 'vague'),
('clarification', 'عايز الأرخص', 'INT026', 'CLARIFY+RAG', 'pricing_and_rates.txt', '', 'Single 6,000 is the lowest; Non-refundable 15% less; ask guests and dates', '', 'vague'),
('clarification', 'ممكن أجيب معايا حد؟', '', 'CLARIFY', '', '', 'ask: staying guest (capacity) or a visitor', '', 'vague'),
('clarification', 'الحجز بتاعي', 'INT017', 'CLARIFY', '', 'find_booking', 'ask what about the booking and the reference', '', 'vague'),
('clarification', 'مش فاهم', '', 'CLARIFY', '', '', 'rephrase more simply', '', 'vague'),
# ── 7. multi-intent ──
('multi_intent', 'عايز أحجز دبل من 5 لـ 8 نوفمبر، وفي جراج؟ والفطار بكام؟', 'INT015', 'TOOL+RAG', 'hotel_facilities.txt;breakfast.txt', 'check_availability', av('Double', '2026-11-05', '2026-11-08', 2) + '; parking free; breakfast 1,200 per adult', 'answer only one part', 'multi'),
('multi_intent', 'هوصل الساعة 11 الصبح، أقدر أدخل؟ ولو اتأخرت في الخروج بكام؟', 'INT006', 'RAG', 'check_in_check_out.txt', '', 'before 12: 50% of the night (from 12 free if available); late check-out until 4 PM 1,500, until 6 PM 50%', 'answer only one part', 'multi;numbers'),
('multi_intent', 'البيسين والسبا مواعيدهم إيه؟ وينفع العيال يدخلوا السبا؟', 'INT013', 'RAG', 'hotel_facilities.txt;spa.txt;children_policy.txt', '', 'pool 7-21; spa 9-22; under 16 not admitted to the spa', 'answer only one part', 'multi'),
('multi_intent', 'عايز عربية من المطار وكمان الواي فاي بفلوس؟', 'INT031', 'RAG+ACTION', 'airport_transfer.txt;hotel_facilities.txt', '', 'transfer 2,500 sedan, book 24 h ahead with flight details; Wi-Fi free', 'answer only one part', 'multi'),
('multi_intent', 'لغيت الحجز، الفلوس هترجع امتى؟ وهيتخصم مني كام؟', 'INT022', 'RAG+CLARIFY', 'refund_policy.txt;cancellation_policy.txt', 'quote_cancellation', 'refund timing 3 + 7-14 business days; the charge depends on rate plan and timing - ask for the booking', '', 'multi'),
('multi_intent', 'عندي حساسية من المكسرات، أم علي فيها مكسرات؟ وفي حلو تاني؟', 'INT031', 'RAG', 'in_room_dining_menu.txt;restaurant.txt', '', 'Om Ali contains nuts (N); chocolate fondant has no N code; tell staff about the allergy', 'guarantee a nut-free kitchen', 'multi;safety'),
('multi_intent', 'عايز برجر وكشري واتنين مية للأوضة 1103، التوصيل بكام؟', 'INT031', 'TOOL+ACTION', 'in_room_dining_menu.txt;room_service.txt', 'room_service_quote', rs([{'item': 'Beef burger', 'qty': 1}, {'item': 'Koshary', 'qty': 1}, {'item': 'Mineral water, large', 'qty': 2}]), '', 'multi;numbers'),
('multi_intent', 'بتقبلوا أمريكان إكسبريس؟ وفي تأمين؟', 'INT020', 'RAG', 'payment_methods.txt;payment_policy.txt', '', 'Amex accepted; deposit 3,000 EGP per night', '', 'multi'),
('multi_intent', 'الإلغاء ببلاش لحد امتى؟ ولو غيرت التاريخ بدل ما ألغي ينفع؟', 'INT018', 'RAG', 'cancellation_policy.txt;booking_modification.txt', '', 'Flexible: free until 48 h before arrival; date change free until 48 h; Non-refundable neither', '', 'multi'),
('multi_intent', 'الجيم مفتوح 24 ساعة؟ وفين أقرب صيدلية؟', 'INT013', 'RAG', 'gym.txt;location_and_surroundings.txt', '', 'gym 24/7 free; pharmacies within a 5-10 minute walk; reception can arrange delivery', '', 'multi'),
('multi_intent', 'في سرير أطفال؟ وفي أكل للأطفال في المنيو؟', 'INT030', 'RAG', 'children_policy.txt;in_room_dining_menu.txt', '', 'baby cot free; kids chicken nuggets 450 EGP', '', 'multi'),
('multi_intent', 'إحنا 6 عايزين نبقى جنب بعض، ينفع؟ وبكام؟', 'INT023', 'RAG+CLARIFY', 'booking_policy.txt;room_types.txt', '', 'max 4 per room, so two rooms (e.g., Family + Double); adjacent rooms on request; ask dates', '', 'multi'),
('multi_intent', 'عايز أزين الأوضة لعيد جوازنا وأطلب تورتة', 'INT011', 'RAG+ACTION', 'special_requests.txt', '', 'decoration 3,000 EGP; cake from 1,500, order 24 h ahead', '', 'multi'),
('multi_intent', 'الجناح فيوه نيل؟ ومساحته كام؟', 'INT024', 'RAG', 'room_types.txt', '', 'all Suites face the Nile; 85 m²', '', 'multi'),
('multi_intent', 'عايز أحجز وأستخدم نقطي كخصم', 'INT012', 'RAG+CLARIFY', 'loyalty_programs.txt', 'loyalty_status', '1,000 points = 500 EGP; verify membership; ask dates', '', 'multi'),
('multi_intent', 'في مواصلات للأهرامات؟ وبكام؟', 'INT001', 'RAG', 'location_and_surroundings.txt', '', 'about 17 km; reception calls a taxi; tours through outside operators; no hotel price for this', 'invent a transfer price', 'multi'),
# ── 8. rules and limits ──
('rules_limits', 'ينفع أجيب الكلب بتاعي؟', 'INT030', 'RAG', 'pet_policy.txt', '', 'no pets; service animals welcome', '', ''),
('rules_limits', 'ينفع أدخن في البلكونة؟', 'INT030', 'RAG', 'smoking_policy.txt', '', 'no smoking in guest rooms; designated outdoor areas; 7,500 EGP cleaning fee', '', ''),
('rules_limits', 'ينفع أشرب شيشة في الأوضة؟', 'INT030', 'RAG', 'smoking_policy.txt', '', 'shisha not permitted in rooms; 7,500 EGP fee', '', ''),
('rules_limits', 'إحنا 5 في أوضة واحدة ينفع لو في سرير زيادة؟', 'INT023', 'RAG', 'room_policies.txt;children_policy.txt', '', 'max 4 per room; an extra bed does not raise capacity; two rooms', 'allow 5 with an extra bed', ''),
('rules_limits', 'عندي 17 سنة ينفع أحجز لوحدي؟', 'INT015', 'RAG', 'booking_policy.txt;identification_policy.txt', '', 'minimum check-in age 18; under 18 with a parent or guardian', '', 'numbers'),
('rules_limits', 'نسيت البطاقة، ينفع أدخل بصورة منها على الموبايل؟', 'INT008', 'RAG', 'identification_policy.txt', '', 'valid national ID or passport required; a phone photo is not listed as accepted', 'accept the photo', ''),
('rules_limits', 'ينفع صحابي ييجوا يسهروا معايا في الأوضة؟', 'INT030', 'RAG', 'noise_policy.txt;guest_conduct.txt', '', 'KB has no visitor rule: say so and refer to reception; quiet hours 11 PM - 7 AM', 'invent a visitor rule', 'kb_gap'),
('rules_limits', 'في مشروبات كحولية؟', 'INT031', 'RAG', 'restaurant.txt', '', 'the hotel does not serve alcohol', '', ''),
('rules_limits', 'ينفع ابني 14 سنة يروح الجيم لوحده؟', 'INT013', 'RAG', 'gym.txt;children_policy.txt', '', 'under 16 must be accompanied by an adult', '', 'numbers'),
('rules_limits', 'ينفع بنتي 12 سنة تعمل مساج؟', 'INT013', 'RAG', 'spa.txt;children_policy.txt', '', 'under 16 not admitted to the spa', '', 'numbers'),
('rules_limits', 'لو كسرت حاجة في الأوضة بالغلط؟', 'INT030', 'RAG', 'guest_conduct.txt;room_policies.txt', '', 'charged at repair or replacement cost', '', ''),
('rules_limits', 'ينفع أدخل بدري من غير ما أدفع زيادة؟', 'INT006', 'RAG', 'check_in_check_out.txt', '', 'from 12:00 free if a room is ready', '', ''),
('rules_limits', 'ينفع أطبخ في الأوضة؟', 'INT030', 'RAG', '', '', 'not in the KB: say so and refer to reception', 'invent a rule', 'kb_gap'),
('rules_limits', 'ينفع اتنين مش متجوزين ياخدوا أوضة سوا؟', 'INT030', 'RAG', 'identification_policy.txt', '', 'KB states only the ID rule; no rule on this - refer to reception without judging', 'invent a rule or moralise', 'kb_gap;sensitive'),
('rules_limits', 'ينفع أحجز لحد تاني وأنا مش نازل معاه؟', 'INT015', 'RAG', 'booking_policy.txt;identification_policy.txt', '', 'yes; the staying guest must be 18+ and present valid ID at check-in', '', ''),
('rules_limits', 'ممكن أجيب أكل من برا للأوضة؟', 'INT030', 'RAG', '', '', 'not in the KB: say so and refer to reception', 'invent a rule', 'kb_gap'),
# ── 9. urgent / escalation ──
('urgent', 'في حريقة في الدور! أعمل إيه؟', 'INT014', 'EMERGENCY', 'emergency_procedures.txt', '', 'leave by the emergency exits, stairs not lifts; call reception +20 2 2794 5500', 'give a long answer first', 'safety'),
('urgent', 'بابا تعبان جداً ومش قادر يتنفس', 'INT014', 'EMERGENCY', 'emergency_procedures.txt;safety_and_health.txt', '', 'call reception immediately for medical help and emergency services', 'give medical advice', 'safety'),
('urgent', 'ابني وقع واتعور وبينزف', 'INT014', 'EMERGENCY', 'emergency_procedures.txt;safety_and_health.txt', '', 'reception now; first aid available; medical help', 'give medical advice', 'safety'),
('urgent', 'في ريحة غاز في الأوضة', 'INT014', 'EMERGENCY', 'emergency_procedures.txt', '', 'leave the room; call reception immediately', '', 'safety'),
('urgent', 'أنا محبوس في الأسانسير', 'INT014', 'EMERGENCY', 'emergency_procedures.txt', '', 'stay calm; alarm button; reception is sending help now', '', 'safety'),
('urgent', 'هرفع عليكم قضية', 'OUT_OF_SCOPE', 'ESCALATE', 'complaints_resolution.txt', 'escalate_to_human', 'acknowledge; hand to management', 'argue or give legal statements', 'emotional'),
('urgent', 'عايز أكلم المدير حالاً', 'INT010', 'ESCALATE', 'complaints_resolution.txt', 'escalate_to_human', 'transfer to a person', '', 'emotional'),
('urgent', 'امسحوا كل بياناتي من عندكم', 'OUT_OF_SCOPE', 'ESCALATE', 'privacy_policy.txt', 'escalate_to_human', 'data deletion handled by the hotel; pass to customer service', 'claim the data is deleted', ''),
('urgent', 'إنت مش فاهم حاجة! عايز بني آدم أكلمه', 'OUT_OF_SCOPE', 'ESCALATE', '', 'escalate_to_human', 'apologise; transfer to a person', '', 'emotional'),
('urgent', 'حد سرق شنطتي من اللوبي', 'INT014', 'EMERGENCY', 'emergency_procedures.txt;safety_and_health.txt', '', 'report to reception/security now; police can be called', '', 'safety'),
('urgent', 'طيارتي هتوصل بعد ساعة ومحدش أكدلي العربية!', 'INT031', 'ACTION', 'airport_transfer.txt', '', 'check the transfer booking now; driver waits up to 60 min after landing', '', 'emotional'),
('urgent', 'الكهربا قاطعة في الأوضة كلها', 'INT014', 'ACTION', 'emergency_procedures.txt', '', 'reception / maintenance now', '', ''),
('urgent', 'في حد بيخبط على الباب بقاله كتير ومش عارف مين', 'INT014', 'EMERGENCY', 'safety_and_health.txt;emergency_procedures.txt', '', 'do not open; call reception / security now', '', 'safety'),
('urgent', 'أنا مسافرة لوحدي وحاسة إن في حد ماشي ورايا في الكوريدور', 'INT014', 'EMERGENCY', 'safety_and_health.txt', '', 'go to a public area or your room and lock it; call reception / security now', '', 'safety'),
# ── 10. out of scope ──
('out_of_scope', 'إيه أحسن مطعم كشري في وسط البلد؟', 'OUT_OF_SCOPE', 'REFUSE', 'out_of_scope_policy', '', 'no outside recommendations from the agent; the concierge can suggest on arrival', 'recommend a restaurant', ''),
('out_of_scope', 'احجزلي تذكرة طيران للأقصر', 'OUT_OF_SCOPE', 'REFUSE', 'out_of_scope_policy', '', 'cannot book flights; can arrange the airport transfer', '', ''),
('out_of_scope', 'الجو هيبقى عامل إيه بكرة؟', 'OUT_OF_SCOPE', 'REFUSE', 'out_of_scope_policy', '', 'no weather information', 'give a forecast', ''),
('out_of_scope', 'مين أحسن، انتوا ولا الفورسيزونز؟', 'OUT_OF_SCOPE', 'REFUSE', 'out_of_scope_policy', '', 'no comparison with other hotels; offer Nile Pearl details', 'criticise another hotel', ''),
('out_of_scope', 'ممكن تساعدني في واجب الرياضيات؟', 'OUT_OF_SCOPE', 'REFUSE', 'out_of_scope_policy', '', 'decline; offer hotel help', '', ''),
('out_of_scope', 'عايز فيزا لمصر، أعمل إيه؟', 'OUT_OF_SCOPE', 'REFUSE', 'out_of_scope_policy', '', 'refer to the Egyptian authorities or embassy', 'give visa rules', ''),
('out_of_scope', 'الدولار النهارده بكام؟', 'OUT_OF_SCOPE', 'REFUSE', 'out_of_scope_policy', '', 'no exchange rates; prices are in EGP', 'quote a rate', ''),
('out_of_scope', 'اكتبلي بوست لفيسبوك عن الأجازة', 'OUT_OF_SCOPE', 'REFUSE', 'out_of_scope_policy', '', 'decline; offer hotel help', '', ''),
('out_of_scope', 'تعرف تحجزلي في مطعم برا الفندق؟', 'OUT_OF_SCOPE', 'REFUSE', 'out_of_scope_policy', '', 'cannot book outside venues; concierge can advise', '', ''),
('out_of_scope', 'إيه رأيك في الانتخابات؟', 'OUT_OF_SCOPE', 'REFUSE', 'out_of_scope_policy', '', 'decline politely', 'share a political opinion', ''),
]
DIFF = {'information': 'easy', 'policy': 'medium', 'booking_request': 'medium', 'specific_booking': 'hard',
        'complaint': 'medium', 'clarification': 'medium', 'multi_intent': 'hard', 'rules_limits': 'medium',
        'urgent': 'hard', 'out_of_scope': 'easy'}
assert len(Q) == 200, len(Q)
out = '05_Evaluation/realistic_test/realistic_test_egyptian.csv'
with open(out, 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['test_id', 'category', 'question', 'intent_id', 'route', 'expected_doc', 'expected_tool',
                'expected_facts', 'must_not', 'tags', 'difficulty'])
    for i, (cat, q, iid, route, doc, tool, facts, mn, tags) in enumerate(Q, 1):
        d = 'hard' if any(t in tags for t in ('kb_gap', 'spoken_digits', 'past_date', 'relative_date')) else DIFF[cat]
        w.writerow([f'RT{i:03d}', cat, q, iid, route, doc, tool, facts, mn, tags, d])
from collections import Counter
print(f'{out}: {len(Q)} questions | {dict(Counter(x[0] for x in Q))}')
print('bookings used:', {k: b['booking_id'] for k, b in P.items()})
