#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rebuild 02_Data/04_Gold/conversations_gold.csv.

Why: the 360 "Enhanced Multi-Turn v3" conversations were stitched from random turns —
a guest asking for vegetarian food answered "I am staying in room 101 and the problem is
still there", room numbers that do not exist (the hotel has rooms 101–250), booking facts
that contradict bookings.csv (a 4-night stay quoted as 10 months, a check-out before the
check-in), and an extra bed promised for three guests in a Double. They are replaced by
coherent flows (conv_templates_v4.py) whose every booking, room, date, rate and member is
drawn from the operational tables at SYSTEM_DATE. Egyptian Arabic is added as a fifth
language.

The 64 hand-written booking/coverage flows are kept; the booking ids they quote are
replaced where the booking's real state contradicted the story (a "cancel" flow on a
completed stay, a "card declined" flow on a 2025 cancellation), and the Family Room offered
as an alternative in BOOK_F3 is moved to dates when it is actually free.

    python3 06_Scripts/generation/generate_conversations.py
"""
import csv, hashlib, json, os, re, sys
from collections import Counter, defaultdict
from datetime import date, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.dirname(HERE))
from config import SYSTEM_DATE as TODAY
import conv_templates_v4 as TPL

ROOT = os.path.dirname(os.path.dirname(HERE))
os.chdir(ROOT)
OP = '02_Data/02_Operational'
OUT = '02_Data/04_Gold/conversations_gold.csv'
COLS = ['conversation_id', 'flow_id', 'intent_id', 'language', 'turn_count', 'complexity',
        'resolved', 'conversation_json', 'source', 'category']
CATEGORY = {'INT009': 'Booking', 'INT010': 'Customer Service', 'INT011': 'Customer Service',
            'INT012': 'Loyalty', 'INT013': 'Facilities', 'INT014': 'Safety & Emergency',
            'INT031': 'Services', 'INT027': 'Pricing', 'INT007': 'Booking', 'INT021': 'Payment'}

def rd(p): return list(csv.DictReader(open(p, encoding='utf-8-sig')))
def d(s): return date.fromisoformat(s[:10])
def h(s): return int(hashlib.sha256(s.encode()).hexdigest(), 16)

BK = rd(f'{OP}/bookings.csv'); B = {b['booking_id']: b for b in BK}
ROOMS = {r['room_id']: r for r in rd(f'{OP}/rooms.csv')}
RT = {r['room_type_id']: r for r in rd(f'{OP}/room_types.csv')}
PAY = {p['booking_id']: p for p in rd(f'{OP}/payments.csv')}
LOY = rd(f'{OP}/loyalty_members.csv'); MEMBER = {m['customer_id']: m for m in LOY}
CUST = {c['customer_id']: c for c in rd(f'{OP}/customers.csv')}
MENU = {m['item_id']: int(float(m['price'])) for m in rd(f'{OP}/menu_items.csv')}
CODES = {c['discount_code']: c for c in rd(f'{OP}/discount_codes.csv')}
CAP = {k: int(v['capacity']) for k, v in RT.items()}
BASE = {k: int(float(v['base_price'])) for k, v in RT.items()}
BIGGER = {'RT001': 'RT002', 'RT002': 'RT004', 'RT003': 'RT004', 'RT004': 'RT005', 'RT005': 'RT006'}
def fits(n): return min((t for t in CAP if CAP[t] >= n), key=lambda t: BASE[t])
def guests(b): return int(b['adults']) + int(b['children'])

used = set()
def pick(tag, pred, n=1):
    pool = sorted((b for b in BK if b['booking_id'] not in used and pred(b)),
                  key=lambda b: h(tag + b['booking_id']))
    assert len(pool) >= n, tag
    for b in pool[:n]: used.add(b['booking_id'])
    return pool[:n]
def future(b, lead=14):
    return (b['booking_status'] == 'Confirmed' and b['blocks_inventory'] == 'True'
            and d(b['check_in']) >= TODAY + timedelta(days=lead))
def flex(b): return future(b) and b['rate_plan'] == 'Flexible'
def pst(b): return PAY[b['booking_id']]['payment_status']
def inhouse(b):
    return (b['booking_status'] == 'Confirmed' and b['blocks_inventory'] == 'True'
            and d(b['check_in']) <= TODAY < d(b['check_out']))
def recent_done(b, days):
    return (b['booking_status'] == 'Completed' and b['blocks_inventory'] == 'True'
            and TODAY - timedelta(days=days) <= d(b['check_out']) <= TODAY)

def base_slots(b):
    return {'BID': b['booking_id'], 'T': b['room_type_id'], 'CI': b['check_in'], 'CO': b['check_out'],
            'N': b['nights'], 'G': guests(b), 'CAP': CAP[b['room_type_id']],
            'RATE': float(b['price_per_night']), 'TOTAL': float(b['total_amount']),
            'RP': b['rate_plan'], 'PAID': float(PAY[b['booking_id']]['amount_paid']),
            'LASTEN': CUST[b['customer_id']]['last_name'],
            'LASTAR': CUST[b['customer_id']]['last_name_ar'] or CUST[b['customer_id']]['last_name']}

def slots_for(flow):
    """Return three (slots, branch) tuples, or None for opener-only flows."""
    if flow in TPL.OPENERS: return None
    out = []
    if flow == 'INT009_F1':
        for b, k in zip(pick(flow, flex, 3), (3, 7, 14)):
            s = base_slots(b); s['NCI'] = str(d(b['check_in']) + timedelta(k)); s['NCO'] = str(d(b['check_out']) + timedelta(k)); out.append((s, None))
    elif flow == 'INT009_F2':
        for b in pick(flow, lambda b: flex(b) and int(b['nights']) >= 3, 3):
            s = base_slots(b); s['NCO'] = str(d(b['check_out']) - timedelta(1)); s['N2'] = int(b['nights']) - 1; out.append((s, None))
    elif flow == 'INT009_F3':
        for b in pick(flow, lambda b: flex(b) and b['room_type_id'] in BIGGER and CAP[BIGGER[b['room_type_id']]] >= guests(b), 3):
            s = base_slots(b); a = BIGGER[b['room_type_id']]; s.update(ALT=a, ALTCAP=CAP[a], ALTBASE=BASE[a]); out.append((s, None))
    elif flow in ('INT009_F4', 'INT011_F4'):
        fit = lambda b: flex(b) and b['room_type_id'] != 'RT001' and guests(b) >= 2 and guests(b) + 1 <= CAP[b['room_type_id']]
        over = lambda b: flex(b) and b['room_type_id'] != 'RT001' and guests(b) >= 2 and guests(b) == CAP[b['room_type_id']] and guests(b) + 1 <= 4
        for b in pick(flow + 'fit', fit, 2):
            s = base_slots(b); s['NEWG'] = guests(b) + 1; out.append((s, 'fit'))
        for b in pick(flow + 'over', over, 1):
            s = base_slots(b); s['NEWG'] = guests(b) + 1; a = fits(s['NEWG']); s.update(ALT=a, ALTCAP=CAP[a], ALTBASE=BASE[a]); out.append((s, 'over'))
    elif flow == 'INT009_F5':
        for b in pick(flow, flex, 3):
            s = base_slots(b); s['NCO'] = str(d(b['check_out']) + timedelta(2)); out.append((s, None))
    elif flow in ('INT010_F1', 'INT010_F4', 'INT014_F1', 'INT014_F2', 'INT014_F3', 'INT014_F4', 'INT010_F2'):
        for b in pick(flow, inhouse, 3):
            s = base_slots(b); s['ROOM'] = ROOMS[b['room_id']]['room_number']; out.append((s, None))
    elif flow == 'INT010_F3':
        for b in pick(flow, lambda b: recent_done(b, 30), 3): out.append((base_slots(b), None))
    elif flow == 'INT010_F5':
        for b in pick(flow, lambda b: recent_done(b, 14), 3): out.append((base_slots(b), None))
    elif flow in ('INT011_F1', 'INT011_F2', 'INT011_F3', 'INT011_F5', 'INT013_F3', 'INT013_F4'):
        for b in pick(flow, future, 3): out.append((base_slots(b), None))
    elif flow == 'INT012_F4':
        for b in pick(flow + 'mem', lambda b: future(b) and b['customer_id'] in MEMBER and b['room_type_id'] != 'RT006', 2):
            s = base_slots(b); s['TIERK'] = MEMBER[b['customer_id']]['tier']; out.append((s, 'mem'))
        for b in pick(flow + 'non', lambda b: future(b) and b['customer_id'] not in MEMBER, 1):
            out.append((base_slots(b), 'non'))
    elif flow == 'INT012_F5':
        for m in sorted(LOY, key=lambda m: h(flow + m['member_id']))[:3]:
            out.append(({'MID': m['member_id'], 'TIERK': m['tier'], 'POINTS': m['points_balance'], 'STAYS': m['total_stays']}, None))
    elif flow == 'INT031_F1':
        for b, (i1, i2) in zip(pick(flow, inhouse, 3), (('M07', 'M23'), ('M15', 'M20'), ('M04', 'M17'))):
            s = base_slots(b); s.update(ROOM=ROOMS[b['room_id']]['room_number'], I1=i1, I2=i2, P1=MENU[i1], P2=MENU[i2],
                                        SUM=MENU[i1] + MENU[i2] + 300); out.append((s, None))
    elif flow == 'INT027_F1':
        for code, br in (('PEARL100', 'active'), ('PEARL750', 'exhausted'), ('PEARL888', 'scheduled')):
            c = CODES[code]; assert c['status'].lower() == br, (code, c['status'])
            out.append(({'CODE': code, 'START': c['start_date'], 'END': c['end_date'],
                         'DISCT': c['discount_type'], 'DISCV': c['discount_value']}, br))
    elif flow == 'INT007_F1':
        leaving = lambda b: inhouse(b) and d(b['check_out']) > TODAY
        pool = sorted((b for b in BK if b['booking_id'] not in used and leaving(b)
                       and MEMBER.get(b['customer_id'], {}).get('tier') == 'Platinum'), key=lambda b: h(flow + b['booking_id']))[:1]
        for b in pool: used.add(b['booking_id'])
        for b in pool + pick(flow, leaving, 3 - len(pool)):
            s = base_slots(b); s['ROOM'] = ROOMS[b['room_id']]['room_number']
            out.append((s, 'plat' if b in pool else 'pay'))
    elif flow == 'INT021_F1':
        for b in pick(flow + 'flex', lambda b: flex(b) and pst(b) == 'Pending', 2):
            s = base_slots(b); s['DEP'] = 3000 * int(b['nights']); out.append((s, 'flex'))
        for b in pick(flow + 'nr', lambda b: future(b) and b['rate_plan'] == 'Non-refundable', 1):
            s = base_slots(b); s['DEP'] = 3000 * int(b['nights']); out.append((s, 'nr'))
    elif flow == 'CANCEL_F1_standard':
        for b in pick(flow + 'paid', lambda b: flex(b) and pst(b) == 'Paid', 2): out.append((base_slots(b), 'paid'))
        for b in pick(flow + 'unpaid', lambda b: flex(b) and pst(b) == 'Pending', 1): out.append((base_slots(b), 'unpaid'))
    elif flow == 'CANCEL_F2_nonrefundable':
        for b in pick(flow, lambda b: future(b) and b['rate_plan'] == 'Non-refundable', 3): out.append((base_slots(b), None))
    elif flow == 'PAY_F1_status':
        for b in pick(flow + 'paid', lambda b: future(b) and pst(b) == 'Paid', 2): out.append((base_slots(b), 'paid'))
        for b in pick(flow + 'pending', lambda b: flex(b) and pst(b) == 'Pending', 1): out.append((base_slots(b), 'pending'))
    elif flow == 'PAY_F2_declined':
        for b in pick(flow, lambda b: flex(b) and pst(b) == 'Failed', 3): out.append((base_slots(b), None))
    assert len(out) == 3, flow
    return out

def money(x, lang):
    s = f'{x:,.2f}'.replace('.00', '') if x != int(x) else f'{int(x):,}'
    if lang in ('French', 'Russian'):
        s = s.replace(',', ' ').replace('.', ',')
    return s

def fill(text, s, lang):
    v = {}
    for k, x in s.items():
        if k in ('RATE', 'TOTAL', 'ALTBASE', 'PAID', 'P1', 'P2', 'SUM', 'DEP'): v[k] = money(float(x), lang)
        elif k in ('CI', 'CO', 'NCI', 'NCO', 'START', 'END'): v[k] = TPL.spoken_date(str(x), lang, TODAY.year)
        elif k == 'T': v['TYPE'] = TPL.TYPE[lang][x]
        elif k == 'ALT': v['ALT'] = TPL.TYPE[lang][x]
        elif k == 'TIERK': v['TIER'] = TPL.TIER[lang][x]
        elif k == 'RP': v['RP'] = TPL.RATE[lang][x]
        elif k in ('I1', 'I2'): v[k] = TPL.ITEM[x][lang]
        elif k == 'LASTEN': v['LAST'] = x if lang not in ('Arabic', 'Arabic-Egyptian') else s['LASTAR']
        elif k == 'DISCT':
            val = s['DISCV'] if x == 'PERCENTAGE' else money(float(s['DISCV']), lang)
            v['DISC'] = TPL.DISC[lang][x].replace('{V}', val)
        else: v[k] = str(x)
    return re.sub(r'\{([A-Z0-9]+)\}', lambda m: v[m.group(1)], text)

def build(flow, lang, variant, s, branch):
    turns = []
    for i, t in enumerate(TPL.T[flow][lang]):
        if t is None: t = TPL.OPENERS[flow][lang][variant]
        if isinstance(t, dict): t = t[branch]
        turns.append({'turn': i + 1, 'role': 'user' if i % 2 == 0 else 'assistant',
                      'message': fill(t, s or {}, lang)})
    return turns

# ── Egyptian versions of the 16 hand-written booking / coverage flows ──
EGY_KEPT = {
'BOOK_F1_full': ["عايز أحجز أوضة.", "أكيد. إيه التواريخ اللي عايزها، وهتكونوا كام فرد؟", "من 12 لـ 15 نوفمبر، اتنين كبار.",
 "يعني 3 ليالي لفردين. الأوضة الدبل بـ 2,500 جنيه في الليلة، واللي بسريرين منفصلين بـ 2,700. تحب أنهي؟", "اللي بسريرين لو سمحت.",
 "الأوضة اللي بسريرين 3 ليالي إجماليها 8,100 جنيه. محتاج اسمك بالكامل وبيانات التواصل عشان أكمل الحجز، وشروط الدفع بتعتمد على الحجز وهأكدهالك قبل ما يتخصم أي حاجة.",
 "تمام، اسمي على الحساب اللي عندكم.", "شكراً، ببعت الحجز دلوقتي وهيوصلك تأكيد تحتفظ بيه. محتاج أي حاجة تانية؟"],
'BOOK_F2_missing_info': ["عندكم أوضة الجمعة الجاية؟", "أشوفلك. هتقعد كام ليلة، وكام فرد؟", "اتنين.", "تمام، وكام ليلة؟", "3 ليالي.",
 "3 ليالي لفردين. عندنا الدبل بـ 2,500 جنيه في الليلة أو اللي بسريرين بـ 2,700. أشوفلك المتاح في الاتنين؟", "أيوة لو سمحت."],
'BOOK_F3_unavailable_alternative': ["عايز جناح أول أسبوع في يناير.", "ثانية أشوف. ممكن تأكدلي التواريخ بالظبط وعدد الأفراد؟", "من 1 لـ 5 يناير، إحنا 4.",
 "الجناح مش متاح في التواريخ دي. الأوضة العائلية برضه بتاخد 4 وسعرها 4,500 جنيه في الليلة بدل 6,500، وهي أوضة كبيرة للعائلات بس من غير الصالة المنفصلة. تناسبك؟",
 "أيوة، احجزلي العائلية.", "الأوضة العائلية 4 ليالي إجماليها 18,000 جنيه. هبعت الحجز وهيوصلك التأكيد."],
'BOOK_F4_capacity_reject': ["ينفع أحجز أوضة سينجل ليا أنا ومراتي؟", "الأوضة السينجل بتاخد فرد واحد بس، فمش هتنفع لاتنين. لفردين في الدبل بـ 2,500 جنيه في الليلة، واللي بسريرين منفصلين بـ 2,700.",
 "خلاص الدبل. إيه التواريخ المتاحة؟", "المتاح بيعتمد على التواريخ اللي انت عايزها. في بالك تواريخ إيه؟", "تاني أسبوع في يناير.", "أقدر أشوف. ممكن تقولي تاريخ الوصول والمغادرة بالظبط؟"],
'BOOK_F5_past_date': ["احجزلي أوضة يوم الاتنين اللي فات.", "التاريخ ده عدّى خلاص فمينفعش أحجزه. قصدك الاتنين الجاي ولا تاريخ تاني؟", "آسف، قصدي الاتنين الجاي.",
 "ولا يهمك. كام ليلة وكام فرد؟", "ليلتين، فرد واحد.", "لفرد واحد الأوضة السينجل بـ 1,800 جنيه في الليلة، يعني 3,600 لليلتين. أشوفلك المتاح؟"],
'BOOK_F6_changed_mind': ["عايز أحجز أوضة ديلوكس 3 ليالي.", "الديلوكس بـ 3,800 جنيه في الليلة وبتاخد لحد 3 أفراد، يعني 3 ليالي بـ 11,400. إيه التواريخ وكام فرد؟",
 "بصراحة ده أكتر من اللي كنت عامل حسابه. في حاجة أرخص؟", "السينجل بـ 1,800 جنيه في الليلة لفرد واحد، والدبل بـ 2,500 واللي بسريرين بـ 2,700 والاتنين لفردين. هتكونوا كام؟",
 "اتنين. خليها الدبل.", "الدبل 3 ليالي إجماليها 7,500 جنيه. تحب تواريخ إيه؟"],
'BOOK_F7_not_found': ["ممكن تطلعلي الحجز بتاعي؟ الرقم B999999.", "مالقيتش حجز بالرقم ده. ممكن تتأكد من الرقم، أو تقولي الاسم اللي الحجز باسمه وتاريخ الوصول عشان أدور بطريقة تانية؟",
 "الحجز باسم مراتي، والوصول يوم 20 أكتوبر.", "شكراً. محتاج اسمها بالكامل زي ما هو مكتوب في الحجز عشان أدور بالاسم والتاريخ.", "هجيبه وأكلمك تاني.", "تحت أمرك. الاستقبال موجود 24 ساعة في أي وقت."],
'BOOK_F8_modify_dates': ["محتاج أأخر الحجز بتاعي يومين.", "أقدر أطلبهولك. ممكن رقم الحجز عشان ألاقيه؟", "الرقم B004512.",
 "شكراً. تغيير التواريخ على حسب المتاح في التواريخ الجديدة وموافقة الفندق، وسعر الليلة ممكن يختلف في الفترة الجديدة. أبعت الطلب؟", "أيوة، وهدفع زيادة؟",
 "سعر التواريخ الجديدة هيتحسب لما التغيير يتوافق عليه، وخدمة العملاء هتأكدلك الفرق قبل ما يتخصم أي حاجة."],
'CANCEL_F1_standard': ["محتاج ألغي الحجز بتاعي.", "أقدر أساعدك. ممكن رقم الحجز والاسم اللي الحجز باسمه؟", "B007841، باسمي أنا.",
 "شكراً. شروط الإلغاء بتعتمد على شروط الحجز ده، وأي استرداد بيمشي حسب سياسة الدفع والاسترداد في الفندق. هشوف إيه اللي بينطبق على حجزك وأبعت طلب الإلغاء. أكمّل؟",
 "أيوة. هتترجعلي فلوسي؟", "الاسترداد بيعتمد على شروط حجزك، والفندق مش معلن نسبة ثابتة، فخدمة العملاء هتأكدلك المبلغ والمدة بعد ما الإلغاء يتنفذ."],
'CANCEL_F2_nonrefundable': ["حجزي مكتوب عليه مش قابل للاسترداد. ينفع ألغيه برضه؟", "تقدر تطلب الإلغاء، بس الحجز اللي مش قابل للاسترداد شروطه مختلفة عن الحجز العادي. ممكن رقم الحجز عشان أشوف الشروط بالظبط؟",
 "B012003. يعني هخسر كل حاجة؟", "مقدرش أقولك ده من معلومات الفندق بس، لأن شروط الحجوزات اللي مش بتترد بتختلف من حجز للتاني. هحوّل الموضوع لخدمة العملاء يقروا شروط الحجز B012003 ويقولولك بالظبط إيه اللي بينطبق.",
 "تمام، اعمل كده لو سمحت.", "تم. خدمة العملاء هتكلمك بخصوص الحجز B012003."],
'PAY_F1_status': ["الدفع بتاعي عدّى؟", "أشوفلك. ممكن رقم الحجز؟", "B003377.",
 "شكراً، الحجز قدامي. هتأكد من حالة الدفع عليه وأرد عليك، ولو في حاجة لسه مادفعتش خدمة العملاء ممكن ترتبلك طريقة دفع تانية.", "شكراً."],
'PAY_F2_declined': ["الكارت اترفض وأنا بدفع. أعمل إيه؟", "آسفين على كده. ممكن رقم الحجز عشان أشوف الحجز وحالة الدفع؟", "B008120. الأوضة لسه محجوزالي؟",
 "شروط الدفع بتعتمد على الحجز وسياسة الدفع في الفندق، فمش عايز أخمن بخصوص الحجز. هحوّل الموضوع لخدمة العملاء بالرقم عشان يأكدولك حالة الحجز B008120 ويرتبولك طريقة دفع تانية.",
 "لو سمحت، الموضوع مستعجل.", "علّمته إنه مستعجل. والاستقبال موجود 24 ساعة لو تحب تكلم حد حالاً."],
'AMB_F1_ambiguous_room': ["عايز الأوضة الكبيرة الويك إند الجاي.", "عايز أتأكد إني بشوف الصح. قصدك بالأوضة الكبيرة العائلية، اللي بتاخد 4 بـ 4,500 جنيه في الليلة، ولا الجناح اللي برضه بياخد 4 بس فيه صالة منفصلة بـ 6,500؟",
 "اللي فيها صالة.", "يبقى الجناح. إيه التواريخ بالظبط، وهتكونوا كام فرد؟", "من الجمعة للحد، إحنا 3.",
 "3 أفراد ينفعوا في الجناح لأنه بياخد 4. ليلتين بـ 6,500 يبقى 13,000 جنيه. أشوفلك المتاح في التواريخ دي؟"],
'CAP_F1_split_rooms': ["إحنا 6 أفراد، عيلتين. ينفع ناخد أوضة واحدة كبيرة؟", "مفيش أوضة واحدة بتاخد 6. أكبر أوض العائلية والجناح وكل واحدة بتاخد 4، الكبار والأطفال محسوبين مع بعض. فالـ 6 محتاجين أوضتين. تحب أشوفلك أوضتين في نفس التواريخ؟",
 "أيوة. 3 و3.", "كل 3 ينفعوا في أوضة ديلوكس، بتاخد 3 بـ 3,800 جنيه في الليلة. أوضتين ديلوكس يبقوا 7,600 جنيه في الليلة. إيه التواريخ؟", "أول أسبوع في مارس.",
 "محتاج تاريخ الوصول والمغادرة بالظبط عشان أشوف في أوضتين ديلوكس فاضيين مع بعض ولا لأ."],
'ESC_F1_misunderstanding': ["أنا قلتلك مرتين. مش ده اللي أنا سألت عليه.", "آسف، ماقدرتش أفهمك صح. وبدل ما أخمن للمرة التالتة هحوّلك لحد من فريق الفندق.", "أخيراً. هياخد قد إيه؟",
 "الاستقبال موجود 24 ساعة، فيه حد متاح دلوقتي. ولو مش عايز تستنى هنا تقدر تكلم الاستقبال على طول وهيكون معاهم تفاصيل المحادثة دي.", "هكلمهم."],
'SRV_F1_service_request': ["الأوضة ماتنضفتش النهارده.", "آسفين على ده. ممكن رقم الأوضة عشان أسجل طلب للهاوس كيبينج؟", "أوضة 212. ومحتاج فوط نضيفة.",
 "اتسجل طلب هاوس كيبينج لأوضة 212: تنضيف وفوط نضيفة. محتاج أي حاجة تانية وهما عندك؟", "لأ، كده تمام.", "الطلب عند الهاوس كيبينج. لو ماتعملش قريب، الاستقبال موجود 24 ساعة ويقدر يتابعه."],
}

def main():
    old = rd('02_Data/01_Raw/conversations_gold_pre_v4.csv')   # pristine input: reruns are idempotent
    kept = [r for r in old if r['source'] != 'Enhanced Multi-Turn v3']
    freed = sorted(r['conversation_id'] for r in old if r['source'] == 'Enhanced Multi-Turn v3')
    nxt = max(int(r['conversation_id'][4:]) for r in old) + 1
    def new_id():
        nonlocal nxt
        if freed: return freed.pop(0)
        i = f'CONV{nxt:05d}'; nxt += 1; return i

    TEMPLATED_KEPT = {'CANCEL_F1_standard', 'CANCEL_F2_nonrefundable', 'PAY_F1_status', 'PAY_F2_declined'}
    meta = {r['flow_id']: r for r in kept}
    for b in ('B003377', 'B004512', 'B007841', 'B012003', 'B008120'): used.add(b)
    repl = {'B004512': pick('BOOK_F8', flex)[0]['booking_id']}
    MONTH = {'English': [('first week of December', 'first week of January'), ('1 to 5 December', '1 to 5 January')],
             'Arabic': [('ديسمبر', 'يناير')], 'French': [('décembre', 'janvier')],
             'Russian': [('первую неделю декабря', 'первую неделю января'), ('С 1 по 5 декабря', 'С 1 по 5 января')]}
    PRICE_V4 = {'BOOK_F1_full': {2500: 8000, 2700: 8500, 8100: 25500}, 'BOOK_F2_missing_info': {2500: 8000, 2700: 8500},
                'BOOK_F3_unavailable_alternative': {4500: 14000, 6500: 20000, 18000: 56000},
                'BOOK_F4_capacity_reject': {2500: 8000, 2700: 8500}, 'BOOK_F5_past_date': {1800: 6000, 3600: 12000},
                'BOOK_F6_changed_mind': {3800: 12000, 11400: 36000, 1800: 6000, 2500: 8000, 2700: 8500, 7500: 24000},
                'AMB_F1_ambiguous_room': {4500: 14000, 6500: 20000, 13000: 40000},
                'CAP_F1_split_rooms': {3800: 12000, 7600: 24000}}
    room212 = next(r['room_number'] for r in ROOMS.values() if r['room_id'] == 'R212')
    NUM = re.compile(r'(?<![\d,.:/])(\d{1,3}(?:[,\u00a0\u202f ]\d{3})+|\d{4,5})(?![\d:/%])')
    def v4(flow, j):
        mp = PRICE_V4.get(flow, {})
        def sub(m):
            v = int(re.sub(r'[,\u00a0\u202f ]', '', m.group(1)))
            if v not in mp: return m.group(0)
            sep = next((c for c in m.group(1) if c in ',\u00a0\u202f '), None)
            return f'{mp[v]:,}'.replace(',', sep) if sep else str(mp[v])
        j = NUM.sub(sub, j)
        if flow == 'SRV_F1_service_request': j = re.sub(r'\b212\b', room212, j)
        for a, b in repl.items(): j = j.replace(a, b)
        return j
    rows = []
    for flow in sorted(TPL.T):
        sl = slots_for(flow)
        if flow in TEMPLATED_KEPT:
            iid, cat, src = meta[flow]['intent_id'], meta[flow]['category'], 'multi_turn_v4'
        else:
            iid, cat, src = flow[:6], CATEGORY[flow[:6]], 'multi_turn_v4'
        for lang in TPL.L:
            for v in range(3):
                s_, br = (None, None) if sl is None else sl[v]
                turns = build(flow, lang, v, s_, br)
                rows.append({'conversation_id': new_id(), 'flow_id': flow, 'intent_id': iid, 'language': lang,
                             'turn_count': len(turns), 'complexity': 'Complex' if len(turns) >= 6 else 'Medium',
                             'resolved': 'Yes', 'conversation_json': json.dumps(turns, ensure_ascii=False),
                             'source': src, 'category': cat})
    by_flow = defaultdict(list)
    for r in kept:
        if r['flow_id'] not in TEMPLATED_KEPT: by_flow[r['flow_id']].append(r)
    for flow, grp in by_flow.items():
        for r in grp:
            j = r['conversation_json']
            if flow == 'BOOK_F3_unavailable_alternative':
                for a, b in MONTH[r['language']]: j = j.replace(a, b)
            r = dict(r); r['conversation_json'] = v4(flow, j); rows.append(r)
        t0 = grp[0]
        turns = [{'turn': i + 1, 'role': 'user' if i % 2 == 0 else 'assistant', 'message': m}
                 for i, m in enumerate(EGY_KEPT[flow])]
        rows.append({'conversation_id': new_id(), 'flow_id': flow, 'intent_id': t0['intent_id'],
                     'language': 'Arabic-Egyptian', 'turn_count': len(turns), 'complexity': t0['complexity'],
                     'resolved': 'Yes', 'conversation_json': v4(flow, json.dumps(turns, ensure_ascii=False)),
                     'source': t0['source'], 'category': t0['category']})
    left = [r['conversation_id'] for r in rows if re.search(r'\{[A-Z0-9]+\}', r['conversation_json'])]
    assert not left, left[:5]
    with open(OUT, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=COLS); w.writeheader(); w.writerows(rows)
    print(f'{OUT}: {len(rows)} conversations | by language {dict(Counter(r["language"] for r in rows))}')
    print(f'by source {dict(Counter(r["source"] for r in rows))}')
    print('booking id replaced in BOOK_F8:', repl)

if __name__ == '__main__':
    main()
