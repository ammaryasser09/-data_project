#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Stage 2 of the repair pipeline — cross-table consistency (v3).

Stage 1 (apply_business_rules.py) repairs bookings.csv alone. It changed 3,293 room types
and 581 guest counts, which changed total_amount, but never propagated anything to the
tables that point at bookings. This stage does, and fixes defects found in the v3 audit:

  RULE H  payments agree with their booking   (amount and status)          → payments.csv
  RULE K  a ticket or request belongs to the booking's owner                → complaint_tickets.csv,
                                                                              special_requests_history.csv
  RULE L  feedback exists only for a finished stay                           → customer_feedback.csv
  RULE M  discount codes are unique, within usage limits, status from dates → discount_codes.csv
  RULE N  rooms.status is the SYSTEM_DATE snapshot of bookings              → rooms.csv
  RULE O  loyalty total_stays >= stays recorded in this dataset             → loyalty_members.csv
  RULE P  a service request is dated when it could have been made          → customer_requests.csv
  RULE R  rooms: 15 guest floors, room numbers floor*100+n, Nile / City view → rooms.csv
  RULE S  Arabic spelling of Arab guests' names, for voice lookups          → customers.csv
  RULE T  rate plan (Flexible / Non-refundable) and refunds per the v4
          cancellation and no-show policy                                  → bookings.csv, payments.csv
  RULE Q  complaints and special requests are consistent with the stay     → complaint_tickets.csv,
          (a room complaint needs a stay; "Fulfilled" needs a stay that       special_requests_history.csv
          happened; resolved/fulfilled dates follow the created date)

Inputs are the pristine copies in 02_Data/01_Raw/*_raw.csv (created on the first run and
never modified afterwards) plus bookings.csv from stage 1, so the script is idempotent:
running it twice gives byte-identical output.

Run from the project root, after stage 1:
    python3 06_Scripts/repair/apply_business_rules.py
    python3 06_Scripts/repair/repair_operational_v3.py
"""
import csv, hashlib, os, shutil, sys
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import SYSTEM_DATE as TODAY   # single frozen 'today' — see 06_Scripts/config.py

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(ROOT)
OP, RAW = '02_Data/02_Operational', '02_Data/01_Raw'
STAMP = '2026-09-25T12:00:00'   # fixed so reruns are byte-identical

def rd(p):
    with open(p, encoding='utf-8-sig') as f: return list(csv.DictReader(f))
def wr(p, rows, cols):
    with open(p, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rows)
def d(s): return date.fromisoformat(str(s)[:10])
def h(s): return int(hashlib.sha256(s.encode()).hexdigest(), 16)

def raw_copy(name):
    """First run: freeze the pre-v3 table in 01_Raw. Later runs: read the frozen copy."""
    raw = f'{RAW}/{name[:-4]}_raw.csv'
    if not os.path.exists(raw):
        shutil.copyfile(f'{OP}/{name}', raw)
    return rd(raw), list(rd(raw)[0].keys())

log = []
def rec(table, rid, issue, old, new, reason, rule):
    log.append({'timestamp': STAMP, 'file': table, 'table': table[:-4], 'record_id': rid,
                'issue': issue, 'old_value': old, 'new_value': new, 'reason': reason,
                'source': f'BUSINESS_RULES.md {rule}', 'repair_type': issue,
                'confidence': 'high', 'reviewer_required': 'no'})

bk = rd(f'{OP}/bookings.csv')
assert 'blocks_inventory' in bk[0], 'run apply_business_rules.py first (stage 1)'
B = {r['booking_id']: r for r in bk}

# ─────────────────────────── RULE H — payments ───────────────────────────
pay, pcols = raw_copy('payments.csv')
MONEY_IN = {'Paid', 'Refunded', 'Partially Refunded'}
ALLOWED = {
    'Confirmed': {'Paid', 'Pending', 'Failed', 'Partially Refunded'},
    'Completed': {'Paid', 'Partially Refunded'},
    'Cancelled': {'Paid', 'Refunded', 'Partially Refunded', 'Failed'},
    'No-show':   {'Paid', 'Refunded', 'Partially Refunded', 'Failed'},
}
REMAP = {('Confirmed', 'Refunded'): 'Paid',   ('Completed', 'Pending'): 'Paid',
         ('Completed', 'Failed'): 'Paid',     ('Completed', 'Refunded'): 'Paid',
         ('Cancelled', 'Pending'): 'Failed',  ('No-show', 'Pending'): 'Failed'}
WHY = {
 ('Confirmed', 'Refunded'): 'a fully refunded reservation cannot still be Confirmed; the reservation is the source of truth, so the payment is Paid',
 ('Completed', 'Pending'):  'the guest stayed and departed; settlement at check-out means the stay is Paid',
 ('Completed', 'Failed'):   'the guest stayed and departed; settlement at check-out means the stay is Paid',
 ('Completed', 'Refunded'): 'a full refund of a delivered stay is not a state the knowledge base describes; recorded as Paid',
 ('Cancelled', 'Pending'):  'a payment can no longer be pending on a withdrawn reservation; it was never collected',
 ('No-show', 'Pending'):    'the arrival date has passed; a payment still pending was never collected',
}
amt_fix = st_fix = 0
for p in pay:
    b = B[p['booking_id']]
    total = float(b['total_amount'])
    old_st, st = p['payment_status'], p['payment_status']
    key = (b['booking_status'], st)
    if key in REMAP:
        st = REMAP[key]
        rec('payments.csv', p['payment_id'], 'payment_status_incompatible',
            f'payment_status={old_st} for booking_status={b["booking_status"]}',
            f'payment_status={st}', WHY[key], 'RULE H')
        st_fix += 1
    paid_old, ref_old = float(p['amount_paid']), float(p['refund_amount'])
    if st in MONEY_IN:
        paid = total
        if st == 'Refunded':
            ref = paid
        elif st == 'Partially Refunded':
            ratio = ref_old / paid_old if paid_old else 0.45
            ref = round(paid * ratio, 2)
        else:
            ref = 0.0
    else:
        paid, ref = 0.0, 0.0
    if abs(paid - paid_old) > 0.005 or abs(ref - ref_old) > 0.005:
        rec('payments.csv', p['payment_id'], 'payment_amount_stale',
            f'amount_paid={p["amount_paid"]}, refund_amount={p["refund_amount"]}',
            f'amount_paid={paid:.2f}, refund_amount={ref:.2f}',
            'stage 1 changed this booking (room type or guest count) and its total; the payment '
            'still carried the pre-repair total. Refund share preserved.' if old_st == st else
            'amount aligned with the corrected payment status', 'RULE H')
        amt_fix += 1
    # keep the file's historical numeric style ("0.0", "16025.7", "22554.72")
    p['payment_status'] = st
    for k, v in (('amount_paid', round(paid, 2)), ('refund_amount', round(ref, 2))):
        p[k] = repr(v) if v != int(v) else f'{v:.1f}'
# ─────────────────────────── RULE T — rate plans and the v4 refund policy ───────────────────────────
# A booking paid in full and then cancelled or not used with nothing refunded can only be
# Non-refundable; other confirmed and completed paid stays are Non-refundable 20% of the time
# (deterministic). Flexible cancellations inside 48 h and Flexible no-shows keep the first
# night and refund the rest (cancellation_policy.txt, no_show_policy.txt).
PB = {p['booking_id']: p for p in pay}
for b in bk:
    stp = PB[b['booking_id']]['payment_status']
    if b['booking_status'] in ('Cancelled', 'No-show'):
        rp = 'Non-refundable' if stp == 'Paid' else 'Flexible'
    else:
        rp = 'Non-refundable' if stp == 'Paid' and h('rp' + b['booking_id']) % 100 < 20 else 'Flexible'
    b['rate_plan'] = rp
aligned = 0
for p in pay:
    b = B[p['booking_id']]
    if b['rate_plan'] != 'Flexible' or b['booking_status'] not in ('Cancelled', 'No-show'): continue
    st = p['payment_status']
    late = ((b['booking_status'] == 'Cancelled' and st == 'Partially Refunded') or
            (b['booking_status'] == 'No-show' and st in ('Refunded', 'Partially Refunded')))
    if not late: continue
    total, night = float(b['total_amount']), float(b['price_per_night'])
    new_st, ref = ('Partially Refunded', round(total - night, 2)) if int(b['nights']) >= 2 else ('Paid', 0.0)
    old_v = f'payment_status={st}, refund_amount={p["refund_amount"]}'
    p['payment_status'] = new_st
    for k, v in (('amount_paid', round(total, 2)), ('refund_amount', ref)):
        p[k] = repr(v) if v != int(v) else f'{v:.1f}'
    if old_v != f'payment_status={new_st}, refund_amount={p["refund_amount"]}':
        rec('payments.csv', p['payment_id'], 'refund_per_policy_v4', old_v,
            f'payment_status={new_st}, refund_amount={p["refund_amount"]}',
            f'Flexible {b["booking_status"].lower()} inside the deadline: the first night '
            f'({night:.2f}) is kept and the other nights refunded', 'RULE T'); aligned += 1
bcols = list(bk[0].keys())
wr(f'{OP}/bookings.csv', bk, bcols)
print(f'[T] rate plans: {dict(Counter(b["rate_plan"] for b in bk))} | refunds aligned: {aligned}')
wr(f'{OP}/payments.csv', pay, pcols)
print(f'[H] payments   status remapped: {st_fix:5d} | amounts realigned: {amt_fix:5d}')


def rule_q(name, rows):
    """RULE Q — complaint / special-request dates and statuses against the booking's stay."""
    n = 0
    def stayed(b): return b['booking_status'] in ('Completed', 'Confirmed') and d(b['check_in']) <= TODAY
    def setf(r, col, new, why):
        nonlocal n
        rec(name, r[cols_id], f'{col}_inconsistent', f'{col}={r[col]}', f'{col}={new}', why, 'RULE Q')
        r[col] = new; n += 1
    cols_id = 'ticket_id' if name.startswith('complaint') else 'request_id'
    for r in rows:
        if not r.get('booking_id'): continue
        b = B[r['booking_id']]; ci, co = d(b['check_in']), d(b['check_out'])
        tod = r['created_at'][10:]; cday = d(r['created_at'])
        if name.startswith('complaint'):
            if r['complaint_type'] in ('Room Issue', 'Service Issue', 'Facility Issue'):
                if not stayed(b):
                    setf(r, 'booking_id', '', f'a {r["complaint_type"]} needs a stay; {b["booking_id"]} ({b["booking_status"]}, '
                         f'{ci}..{co}) was never stayed on SYSTEM_DATE, so the ticket is kept without a booking link')
                    continue
                if not ci <= cday <= TODAY:
                    new = min(ci + timedelta(days=h(r[cols_id]) % max(int(b['nights']), 1)), TODAY)
                    setf(r, 'created_at', f'{new}{tod}', f'a {r["complaint_type"]} is raised during or after the stay {ci}..{co}')
                    cday = new
        else:
            if cday > co or cday > TODAY:
                new = min(ci, TODAY + timedelta(days=1)) - timedelta(days=1 + h(r[cols_id]) % 14)
                setf(r, 'created_at', f'{new}{tod}', f'a special request is made before or during the stay {ci}..{co}')
                cday = new
            st = r['request_status']
            if st == 'Fulfilled' and b['booking_status'] in ('Cancelled', 'No-show'):
                setf(r, 'request_status', 'Cancelled', f'the stay never happened ({b["booking_status"]}); a request cannot be fulfilled')
            elif st == 'Fulfilled' and not stayed(b):
                setf(r, 'request_status', 'Approved', f'the stay starts {ci}, after SYSTEM_DATE; it can be approved, not yet fulfilled')
            if r['request_status'] != 'Fulfilled' and r['fulfilled_at']:
                setf(r, 'fulfilled_at', '', f'status is {r["request_status"]}; only a Fulfilled request has a fulfilment date')
            if r['request_status'] == 'Fulfilled':
                lo, hi = max(ci, cday), min(co, TODAY)
                fd = d(r['fulfilled_at']) if r['fulfilled_at'] else None
                if fd is None or not lo <= fd <= hi:
                    new = lo + timedelta(days=h(r[cols_id] + 'f') % (max((hi - lo).days, 0) + 1))
                    setf(r, 'fulfilled_at', f'{new}{(r["fulfilled_at"] or r["created_at"])[10:]}',
                         f'fulfilment happens during the stay {ci}..{co}, after the request')
    if name.startswith('complaint'):          # every ticket, with or without a booking
        for r in rows:
            cday = d(r['created_at'])
            if r['resolved_at'] and d(r['resolved_at']) < cday:
                gap = (cday - d(r['resolved_at'])).days
                new = min(cday + timedelta(days=gap), TODAY)
                setf(r, 'resolved_at', f'{new}{r["resolved_at"][10:]}', 'a ticket cannot be resolved before it was created')
    return n

# ─────────────────────────── RULE K — ownership ───────────────────────────
for name in ('complaint_tickets.csv', 'special_requests_history.csv'):
    rows, cols = raw_copy(name)
    n = 0
    for r in rows:
        own = B[r['booking_id']]['customer_id'] if r.get('booking_id') else None
        if own and r['customer_id'] != own:
            rec(name, r[cols[0]], 'owner_mismatch', f'customer_id={r["customer_id"]}',
                f'customer_id={own}', f'booking {r["booking_id"]} belongs to {own}; a ticket or '
                'request is filed by the guest who holds the reservation', 'RULE K')
            r['customer_id'] = own; n += 1
    q = rule_q(name, rows)
    wr(f'{OP}/{name}', rows, cols)
    print(f'[K] {name:30} owner corrected: {n} | [Q] timing/status corrected: {q}')

# ─────────────────────────── RULE L — feedback ───────────────────────────
fb, fcols = raw_copy('customer_feedback.csv')
def finished(b): return b['booking_status'] == 'Completed' and d(b['check_out']) <= TODAY
valid_ids = {r['booking_id'] for r in fb if finished(B[r['booking_id']])}
pool = sorted((b for b in bk if finished(b) and b['booking_id'] not in valid_ids),
              key=lambda b: h('fb' + b['booking_id']))
moved = 0
for r in fb:
    b = B[r['booking_id']]
    if finished(b): continue
    nb = pool.pop()
    rec('customer_feedback.csv', r['feedback_id'], 'feedback_on_unfinished_stay',
        f'booking_id={r["booking_id"]} ({b["booking_status"]}, {b["check_in"]}..{b["check_out"]}), '
        f'customer_id={r["customer_id"]}',
        f'booking_id={nb["booking_id"]}, customer_id={nb["customer_id"]}',
        'feedback describes a stay; only a Completed booking whose check-out has passed has one. '
        'Text, rating and sentiment kept; reattached to a finished stay without feedback.', 'RULE L')
    r['booking_id'], r['customer_id'] = nb['booking_id'], nb['customer_id']; moved += 1
wr(f'{OP}/customer_feedback.csv', fb, fcols)
print(f'[L] feedback   reattached to finished stays: {moved}')

# ─────────────────────────── RULE M — discount codes ───────────────────────────
dc, dcols = raw_copy('discount_codes.csv')
seen = {}
used_codes = {r['discount_code'] for r in dc}
for r in dc:
    c = r['discount_code']
    if c in seen:
        n = int(c[5:])
        while f'PEARL{n}' in used_codes: n += 1
        new = f'PEARL{n}'; used_codes.add(new)
        rec('discount_codes.csv', r['code_id'], 'duplicate_code', f'discount_code={c}',
            f'discount_code={new}', f'{c} was also {seen[c]} with a different value; a code must '
            'identify exactly one offer', 'RULE M')
        r['discount_code'] = new
    seen[r['discount_code']] = r['code_id']
    if r['discount_type'] == 'FIXED_AMOUNT':
        nv = str(int(float(r['discount_value'])) * 3)
        rec('discount_codes.csv', r['code_id'], 'price_list_v4', f'discount_value={r["discount_value"]}',
            f'discount_value={nv}', 'fixed-amount discounts scale with the v4 price list (x3)', 'RULE M')
        r['discount_value'] = nv
    if r['max_usage'] != 'Unlimited' and int(r['usage_count']) > int(r['max_usage']):
        rec('discount_codes.csv', r['code_id'], 'usage_over_limit', f'usage_count={r["usage_count"]}',
            f'usage_count={r["max_usage"]}', 'a code cannot be redeemed beyond max_usage', 'RULE M')
        r['usage_count'] = r['max_usage']
# Every historical code expired in 2025, so the "valid code" path of the agent had no data
# at all. Four synthetic codes around SYSTEM_DATE give one example of every state.
NEW = [('DC026', 'PEARL100', 'PERCENTAGE', '10', '37', '500', '2026-09-01', '2026-12-31'),
       ('DC027', 'PEARL500', 'FIXED_AMOUNT', '1500', '12', '100', '2026-08-15', '2026-11-30'),
       ('DC028', 'PEARL750', 'PERCENTAGE', '15', '200', '200', '2026-07-01', '2026-10-31'),
       ('DC029', 'PEARL888', 'PERCENTAGE', '20', '0', 'Unlimited', '2026-12-15', '2027-01-15')]
for cid, code, typ, val, used, mx, s, e in NEW:
    assert code not in used_codes
    dc.append({'code_id': cid, 'discount_code': code, 'discount_type': typ, 'discount_value': val,
               'usage_count': used, 'max_usage': mx, 'start_date': s, 'end_date': e, 'status': ''})
    rec('discount_codes.csv', cid, 'coverage_addition', '', code,
        'no code was valid on SYSTEM_DATE; added so availability of each code state can be tested',
        'RULE M')
def code_status(r):
    if d(r['end_date']) < TODAY: return 'Expired'
    if d(r['start_date']) > TODAY: return 'Scheduled'
    if r['max_usage'] != 'Unlimited' and int(r['usage_count']) >= int(r['max_usage']): return 'Exhausted'
    return 'Active'
for r in dc:
    st = code_status(r)
    if r['status'] and r['status'] != st:
        rec('discount_codes.csv', r['code_id'], 'status_inconsistent', r['status'], st,
            'status is derived from dates and usage on SYSTEM_DATE', 'RULE M')
    r['status'] = st
wr(f'{OP}/discount_codes.csv', dc, dcols)
print(f'[M] discount codes: {dict(Counter(r["status"] for r in dc))}')

# ─────────────────────────── RULE N — room status snapshot ───────────────────────────
rooms, rcols = raw_copy('rooms.csv')
# RULE R — 150 rooms on 15 guest floors (2-16), ten per floor, numbered floor*100 + n.
# Rooms 1-5 of each floor face the Nile, 6-10 the city; every Suite faces the Nile.
# room_id (R101…) is an internal key and does not change, so no booking moves.
ORDER = ['RT001', 'RT002', 'RT003', 'RT004', 'RT005', 'RT006']
for pos, r in enumerate(sorted(rooms, key=lambda r: (ORDER.index(r['room_type_id']), r['room_id']))):
    fl, n = 2 + pos // 10, pos % 10 + 1
    num = str(fl * 100 + n); view = 'Nile' if n <= 5 or r['room_type_id'] == 'RT006' else 'City'
    if r['room_number'] != num:
        rec('rooms.csv', r['room_id'], 'room_layout_v4', f'room_number={r["room_number"]}, floor={r["floor"]}',
            f'room_number={num}, floor={fl}, view={view}', 'a 5-star Nile hotel does not put 150 rooms '
            'on two floors; room_id is unchanged', 'RULE R')
    r['room_number'], r['floor'], r['view'] = num, str(fl), view
rcols = ['room_id', 'room_number', 'floor', 'room_type_id', 'view', 'status']
inhouse = {b['room_id'] for b in bk if b['blocks_inventory'] == 'True'
           and d(b['check_in']) <= TODAY < d(b['check_out'])}
n = 0
for r in rooms:
    new = 'Occupied' if r['room_id'] in inhouse else (
          'Maintenance' if r['status'] == 'Maintenance' else 'Available')
    if new != r['status']:
        rec('rooms.csv', r['room_id'], 'room_status_snapshot', f'status={r["status"]}',
            f'status={new}', f'status must describe the room on SYSTEM_DATE {TODAY}: '
            + ('a blocking booking covers that night' if new == 'Occupied' else
               'no blocking booking covers that night'), 'RULE N')
        r['status'] = new; n += 1
wr(f'{OP}/rooms.csv', rooms, rcols)
print(f'[N] rooms      status corrected: {n} | now {dict(Counter(r["status"] for r in rooms))}')

# ─────────────────────────── RULE O — loyalty ───────────────────────────
lm, lcols = raw_copy('loyalty_members.csv')
stays = Counter(b['customer_id'] for b in bk if b['booking_status'] == 'Completed')
n = 0
for r in lm:
    if int(r['total_stays']) < stays[r['customer_id']]:
        rec('loyalty_members.csv', r['member_id'], 'stays_below_recorded', r['total_stays'],
            str(stays[r['customer_id']]), 'lifetime stays cannot be fewer than the completed '
            'stays recorded in this dataset', 'RULE O')
        r['total_stays'] = str(stays[r['customer_id']]); n += 1
    if d(r['join_date']) > TODAY:
        rec('loyalty_members.csv', r['member_id'], 'join_in_future', r['join_date'], str(TODAY),
            'a member cannot join after SYSTEM_DATE', 'RULE O')
        r['join_date'] = str(TODAY); n += 1
wr(f'{OP}/loyalty_members.csv', lm, lcols)
print(f'[O] loyalty    corrected: {n}')

# ─────────────────────────── RULE P — request timing ───────────────────────────
# In-stay requests (room service, housekeeping, extra bed, late checkout) happen during a
# stay; pre-arrival requests (booking inquiry, modification, cancellation, airport transfer,
# early check-in) happen before it. The raw table dated them at random, so 3,584 of 3,617
# in-stay requests fell outside the stay or on a stay that never happened.
rq, qcols = raw_copy('customer_requests.csv')
INSTAY = {'Room Service', 'Housekeeping', 'Late Checkout', 'Extra Bed'}
PRE = {'Booking Inquiry', 'Modification Request', 'Cancellation Request', 'Airport Transfer', 'Early Check-in'}
retimed = detached = 0
for r in rq:
    bid = r['booking_id']
    if not bid: continue
    b = B[bid]; ci, co = d(b['check_in']), d(b['check_out'])
    day, tod = d(r['created_at']), r['created_at'][10:]
    new, why = None, None
    if r['request_type'] in INSTAY:
        stayed = b['booking_status'] in ('Completed', 'Confirmed') and ci <= TODAY
        if not stayed:
            rec('customer_requests.csv', r['request_id'], 'request_without_stay', f'booking_id={bid}', 'booking_id=',
                f'{r["request_type"]} is made during a stay, and {bid} ({b["booking_status"]}, {ci}..{co}) was never '
                'stayed on SYSTEM_DATE; kept as a general request not tied to a booking', 'RULE P')
            r['booking_id'] = ''; detached += 1; continue
        last = min(co, TODAY)
        if not (ci <= day <= last):
            span = max((last - ci).days, 0)
            new = co - timedelta(days=1) if r['request_type'] == 'Late Checkout' and co <= TODAY else \
                  ci + timedelta(days=h(r['request_id']) % (span + 1))
            why = f'{r["request_type"]} is made during the stay {ci}..{co}'
    elif r['request_type'] in PRE:
        if day > ci or day > TODAY:
            new = min(ci, TODAY + timedelta(days=1)) - timedelta(days=1 + h(r['request_id']) % 14)
            why = f'{r["request_type"]} is made before arrival on {ci}'
    elif day > TODAY:
        new, why = TODAY, 'a request cannot be dated after SYSTEM_DATE'
    if new:
        rec('customer_requests.csv', r['request_id'], 'request_timing', f'created_at={r["created_at"]}',
            f'created_at={new}{tod}', why + '; time of day kept', 'RULE P')
        r['created_at'] = f'{new}{tod}'; retimed += 1
wr(f'{OP}/customer_requests.csv', rq, qcols)
print(f'[P] requests   re-dated: {retimed} | detached from a stay that never happened: {detached}')

# ─────────────────────────── RULE S — Arabic names ───────────────────────────
# A caller who says "الحجز باسم محمد المنصوري" must match "Mohamed Almansoori". The voice
# agent needs the Arabic spelling of Arab guests' names to look them up.
FIRST = {'Abdullah': 'عبدالله', 'Ahmad': 'أحمد', 'Ahmed': 'أحمد', 'Aisha': 'عائشة', 'Amr': 'عمرو', 'Aya': 'آية',
 'Dana': 'دانة', 'Dina': 'دينا', 'Fahad': 'فهد', 'Fatima': 'فاطمة', 'Fatma': 'فاطمة', 'Hamdan': 'حمدان', 'Hana': 'هنا',
 'Hassan': 'حسن', 'Hessa': 'حصة', 'Hossam': 'حسام', 'Huda': 'هدى', 'Karim': 'كريم', 'Khaled': 'خالد', 'Khalid': 'خالد',
 'Khalifa': 'خليفة', 'Laith': 'ليث', 'Layan': 'ليان', 'Lina': 'لينا', 'Mahmoud': 'محمود', 'Mariam': 'مريم', 'Menna': 'منة',
 'Michael': 'مايكل', 'Mina': 'مينا', 'Mohamed': 'محمد', 'Mohammed': 'محمد', 'Mostafa': 'مصطفى', 'Noora': 'نورة',
 'Nour': 'نور', 'Noura': 'نورة', 'Omar': 'عمر', 'Rana': 'رنا', 'Reem': 'ريم', 'Saeed': 'سعيد', 'Salem': 'سالم',
 'Salma': 'سلمى', 'Sara': 'سارة', 'Saud': 'سعود', 'Sherif': 'شريف', 'Tarek': 'طارق', 'Yousef': 'يوسف', 'Youssef': 'يوسف'}
LAST = {'Abdelrahman': 'عبدالرحمن', 'Ahmed': 'أحمد', 'Alajmi': 'العجمي', 'Alenezi': 'العنزي', 'Alghamdi': 'الغامدي',
 'Alharbi': 'الحربي', 'Ali': 'علي', 'Alkaabi': 'الكعبي', 'Almansoori': 'المنصوري', 'Almazrouei': 'المزروعي',
 'Almheiri': 'المهيري', 'Almutairi': 'المطيري', 'Alnuaimi': 'النعيمي', 'Alotaibi': 'العتيبي', 'Alqahtani': 'القحطاني',
 'Alrashid': 'الراشد', 'Alshammari': 'الشمري', 'Alshamsi': 'الشامسي', 'Alzahrani': 'الزهراني', 'Farouk': 'فاروق',
 'Fathy': 'فتحي', 'Gamal': 'جمال', 'Haddad': 'حداد', 'Hamed': 'حامد', 'Hassan': 'حسن', 'Ibrahim': 'إبراهيم',
 'Khalil': 'خليل', 'Mahmoud': 'محمود', 'Mansour': 'منصور', 'Mostafa': 'مصطفى', 'Nasser': 'ناصر', 'Odeh': 'عودة',
 'Said': 'سعيد', 'Saleh': 'صالح', 'Salem': 'سالم', 'Youssef': 'يوسف', 'Zaki': 'زكي'}
cus, ccols = raw_copy('customers.csv')
named = 0
for c in cus:
    fa, la = FIRST.get(c['first_name'], ''), LAST.get(c['last_name'], '')
    c['first_name_ar'], c['last_name_ar'] = (fa, la) if fa and la else ('', '')
    named += bool(fa and la)
wr(f'{OP}/customers.csv', cus, ccols + ['first_name_ar', 'last_name_ar'])
print(f'[S] customers  Arabic name added: {named}')

cols = ['timestamp','file','table','record_id','issue','old_value','new_value','reason',
        'source','repair_type','confidence','reviewer_required']
wr('07_Audits/Repair_Logs/repair_log_v3.csv', log, cols)
print(f'\nrepair_log_v3.csv: {len(log)} entries  {dict(Counter(x["issue"] for x in log))}')
