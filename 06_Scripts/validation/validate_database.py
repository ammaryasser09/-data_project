#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database integrity validation.

Run from the project root:
    python3 06_Scripts/validation/validate_database.py

Checks keys, dates, capacity, room double-booking, money and cross-table consistency
across the operational tables, against the frozen SYSTEM_DATE in 06_Scripts/config.py.
Exit 0 = every check passed.

Occupancy is read from bookings.blocks_inventory (RULE J). The 3,468 bookings that could
not be placed without a double booking carry blocks_inventory=False; they stay in the table
for their payment, request and feedback history but never block a room.
"""
import csv, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import SYSTEM_DATE as TODAY   # single frozen 'today' — see 06_Scripts/config.py
from collections import defaultdict, Counter
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
results = []

def check(name, ok, detail=''):
    results.append((name, ok, detail))
    print(f"  {'PASS' if ok else 'FAIL'}  {name}" + (f"  — {detail}" if detail else ''))

def read(rel):
    with open(os.path.join(ROOT, rel), encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))

S = '02_Data/02_Operational'
cus   = read(f'{S}/customers.csv')
loyal = read(f'{S}/loyalty_members.csv')
bk    = read(f'{S}/bookings.csv')
pay   = read(f'{S}/payments.csv')
rooms = read(f'{S}/rooms.csv')
rt    = read(f'{S}/room_types.csv')
svc   = read(f'{S}/services.csv')
req   = read(f'{S}/customer_requests.csv')
comp  = read(f'{S}/complaint_tickets.csv')
sreq  = read(f'{S}/special_requests_history.csv')

# Bookings the repair could not place, and capacity rows left for the hotel to rule on.
# Read from the repair log so the two scripts can never disagree.
_log = read('07_Audits/Repair_Logs/repair_log.csv')
known = {r['record_id'] for r in _log if r['reviewer_required'] == 'YES'}
unplaceable = {r['record_id'] for r in _log if r['issue'] == 'no_free_room_of_type'}

print('=' * 78)
print('DATABASE INTEGRITY')
print('=' * 78)

print(f'\n[1] Table sizes')
for n, t in [('customers',cus),('bookings',bk),('payments',pay),('rooms',rooms),
             ('room_types',rt),('services',svc),('requests',req),
             ('loyalty_members',loyal),('complaint_tickets',comp),
             ('special_requests_history',sreq)]:
    print(f'      {n:26} {len(t):>6}')

print('\n[2] Primary keys')
for n, t, k in [('customers',cus,'customer_id'),('bookings',bk,'booking_id'),
                ('payments',pay,'payment_id'),('rooms',rooms,'room_id'),
                ('room_types',rt,'room_type_id'),('loyalty_members',loyal,'member_id'),
                ('complaint_tickets',comp,'ticket_id'),
                ('special_requests_history',sreq,'request_id')]:
    check(f'{n}: unique', len({r[k] for r in t}) == len(t), f'{len(t)} rows')

print('\n[3] Foreign keys')
cid = {r['customer_id'] for r in cus}
bid = {r['booking_id'] for r in bk}
rid = {r['room_id'] for r in rooms}
tid = {r['room_type_id'] for r in rt}
for name, tbl, col, ref in [('bookings→customers',bk,'customer_id',cid),
                            ('bookings→rooms',bk,'room_id',rid),
                            ('bookings→room_types',bk,'room_type_id',tid),
                            ('payments→bookings',pay,'booking_id',bid),
                            ('loyalty→customers',loyal,'customer_id',cid),
                            ('complaints→customers',comp,'customer_id',cid),
                            ('complaints→bookings',comp,'booking_id',bid),
                            ('special_requests→customers',sreq,'customer_id',cid),
                            ('special_requests→bookings',sreq,'booking_id',bid)]:
    dangling = [r for r in tbl if r.get(col) and r[col] not in ref]
    check(name, not dangling, f'{len(dangling)} dangling')

print('\n[4] Date logic')
bad_order = bad_nights = bad_parse = 0
for r in bk:
    try:
        ci = date.fromisoformat(r['check_in'][:10])
        co = date.fromisoformat(r['check_out'][:10])
        if co <= ci: bad_order += 1
        if int(r['nights']) != (co - ci).days: bad_nights += 1
    except Exception:
        bad_parse += 1
check('check_out after check_in', not bad_order, f'{bad_order} violations')
check('nights matches the date difference', not bad_nights, f'{bad_nights} mismatched')
check('all dates parse', not bad_parse, f'{bad_parse} unparseable')

print('\n[5] Room occupancy')
occ = defaultdict(list)
for r in bk:
    if r['blocks_inventory'] == 'True':
        occ[r['room_id']].append((date.fromisoformat(r['check_in'][:10]),
                                  date.fromisoformat(r['check_out'][:10]),
                                  r['booking_id']))
clash = []
for rm, lst in occ.items():
    lst.sort()
    for i in range(len(lst) - 1):
        if lst[i][1] > lst[i+1][0]:
            clash.append((rm, lst[i][2], lst[i+1][2]))
check('no room double-booked among blocks_inventory=True', not clash, f'{len(clash)} overlaps')

print('\n[6] Capacity')
cap = {r['room_type_id']: int(r['capacity']) for r in rt}
over = [r['booking_id'] for r in bk
        if int(r['adults']) + int(r['children']) > cap[r['room_type_id']]]
unflagged = [b for b in over if b not in known]
check('every over-capacity booking is flagged for review', not unflagged,
      f'{len(over)} over capacity, {len(unflagged)} unflagged')

print('\n[7] Financial consistency')
bad_total = [r['booking_id'] for r in bk
             if abs(float(r['total_amount']) - float(r['price_per_night']) * int(r['nights'])) > 0.01]
check('total_amount = price_per_night × nights', not bad_total, f'{len(bad_total)} mismatched')
base = {r['room_type_id']: float(r['base_price']) for r in rt}
outside = [r['booking_id'] for r in bk
           if not 0.80 <= float(r['price_per_night']) / base[r['room_type_id']] <= 1.35]
check('nightly rate within 0.80–1.35 of base price (seasonal band)', not outside,
      f'{len(outside)} outside the band')
neg = [r['booking_id'] for r in bk if float(r['total_amount']) <= 0]
check('no zero or negative totals', not neg, f'{len(neg)}')

print('\n[8] Status vocabularies')
print(f"      booking_status : {dict(Counter(r['booking_status'] for r in bk))}")
print(f"      payment_status : {dict(Counter(r['payment_status'] for r in pay))}")
check('booking_status values known',
      set(r['booking_status'] for r in bk) <= {'Confirmed','Cancelled','Completed','No-show'})

print('\n[9] Availability is computable')
horizon = sorted({r['check_in'][:10] for r in bk})
free = 0
probe = horizon[len(horizon)//2]
d = date.fromisoformat(probe)
busy = {r['room_id'] for r in bk
        if r['blocks_inventory'] == 'True'
        and date.fromisoformat(r['check_in'][:10]) <= d < date.fromisoformat(r['check_out'][:10])}
free = len(rid) - len(busy)
check('availability query returns a sane number', 0 <= free <= len(rid),
      f'{free} of {len(rid)} rooms free on {probe}')

# ═════════════════════ v3 cross-table checks ═════════════════════
def D(x): return date.fromisoformat(str(x)[:10])
B = {r['booking_id']: r for r in bk}
fb   = read(f'{S}/customer_feedback.csv')
dc   = read(f'{S}/discount_codes.csv')

print('\n[10] Occupancy flag (RULE J)')
wrong = [r['booking_id'] for r in bk
         if r['blocks_inventory'] == 'True' and r['booking_status'] not in ('Confirmed', 'Completed')]
check('blocks_inventory is False for Cancelled / No-show', not wrong, f'{len(wrong)} wrong')
flag_unpl = {r['booking_id'] for r in bk if r['booking_status'] in ('Confirmed', 'Completed')
             and r['blocks_inventory'] != 'True'}
check('every non-blocking active booking is an unplaceable one from the repair log',
      flag_unpl == unplaceable, f'{len(flag_unpl)} flagged vs {len(unplaceable)} in log')

print('\n[11] Status vs SYSTEM_DATE (RULE C / D)')
bad = [r['booking_id'] for r in bk if
       (r['booking_status'] == 'Completed' and not (D(r['check_in']) <= TODAY and D(r['check_out']) <= TODAY)) or
       (r['booking_status'] == 'No-show' and not D(r['check_in']) < TODAY) or
       (r['booking_status'] == 'Confirmed' and D(r['check_out']) < TODAY)]
check(f'statuses consistent with SYSTEM_DATE {TODAY}', not bad, f'{len(bad)} inconsistent')

print('\n[12] Payments agree with bookings (RULE H)')
ALLOWED = {'Confirmed': {'Paid', 'Pending', 'Failed', 'Partially Refunded'},
           'Completed': {'Paid', 'Partially Refunded'},
           'Cancelled': {'Paid', 'Refunded', 'Partially Refunded', 'Failed'},
           'No-show':   {'Paid', 'Refunded', 'Partially Refunded', 'Failed'}}
inc = [p['payment_id'] for p in pay if p['payment_status'] not in ALLOWED[B[p['booking_id']]['booking_status']]]
check('payment status compatible with booking status', not inc, f'{len(inc)} incompatible')
amt = [p['payment_id'] for p in pay if
       (p['payment_status'] in ('Paid', 'Refunded', 'Partially Refunded')
        and abs(float(p['amount_paid']) - float(B[p['booking_id']]['total_amount'])) > 0.01) or
       (p['payment_status'] in ('Pending', 'Failed') and float(p['amount_paid']) != 0)]
check('amount_paid equals the booking total (0 when nothing was collected)', not amt, f'{len(amt)} mismatched')
ref = [p['payment_id'] for p in pay if
       (p['payment_status'] == 'Refunded' and abs(float(p['refund_amount']) - float(p['amount_paid'])) > 0.01) or
       (p['payment_status'] == 'Partially Refunded' and not 0 < float(p['refund_amount']) < float(p['amount_paid'])) or
       (p['payment_status'] in ('Paid', 'Pending', 'Failed') and float(p['refund_amount']) != 0)]
check('refund_amount consistent with payment status', not ref, f'{len(ref)} inconsistent')

print('\n[13] Ownership (RULE K)')
for name, tbl in (('complaint_tickets', comp), ('special_requests_history', sreq),
                  ('customer_feedback', fb), ('customer_requests', req)):
    bad = [r for r in tbl if r.get('booking_id') and r['booking_id'] in B
           and r['customer_id'] != B[r['booking_id']]['customer_id']]
    check(f'{name}: filed by the guest who holds the booking', not bad, f'{len(bad)} mismatched')

print('\n[14] Feedback describes a finished stay (RULE L)')
bad = [r['feedback_id'] for r in fb if not (B[r['booking_id']]['booking_status'] == 'Completed'
                                             and D(B[r['booking_id']]['check_out']) <= TODAY)]
check('every feedback row points at a Completed booking whose check-out has passed', not bad, f'{len(bad)} rows')

print('\n[15] Discount codes (RULE M)')
check('discount_code values unique', len({r['discount_code'] for r in dc}) == len(dc))
over = [r['code_id'] for r in dc if r['max_usage'] != 'Unlimited' and int(r['usage_count']) > int(r['max_usage'])]
check('usage_count never exceeds max_usage', not over, f'{len(over)} over')
def st(r):
    if D(r['end_date']) < TODAY: return 'Expired'
    if D(r['start_date']) > TODAY: return 'Scheduled'
    if r['max_usage'] != 'Unlimited' and int(r['usage_count']) >= int(r['max_usage']): return 'Exhausted'
    return 'Active'
bad = [r['code_id'] for r in dc if r['status'] != st(r)]
check('status derived from dates and usage on SYSTEM_DATE', not bad, f'{len(bad)} wrong')
check('at least one code is Active on SYSTEM_DATE', any(r['status'] == 'Active' for r in dc))

print('\n[16] Room status snapshot (RULE N)')
inh = {r['room_id'] for r in bk if r['blocks_inventory'] == 'True' and D(r['check_in']) <= TODAY < D(r['check_out'])}
bad = [r['room_id'] for r in rooms if (r['status'] == 'Occupied') != (r['room_id'] in inh)]
check(f'rooms.status Occupied exactly when a blocking booking covers {TODAY}', not bad, f'{len(bad)} rooms')

print('\n[17] Loyalty (RULE O)')
done = Counter(r['customer_id'] for r in bk if r['booking_status'] == 'Completed')
bad = [m['member_id'] for m in loyal if int(m['total_stays']) < done[m['customer_id']] or D(m['join_date']) > TODAY]
check('total_stays >= completed stays recorded; join_date not in the future', not bad, f'{len(bad)} members')

print('\n[18] Request timing (RULE P)')
INSTAY = {'Room Service', 'Housekeeping', 'Late Checkout', 'Extra Bed'}
PRE = {'Booking Inquiry', 'Modification Request', 'Cancellation Request', 'Airport Transfer', 'Early Check-in'}
bad_in = [r['request_id'] for r in req if r['booking_id'] and r['request_type'] in INSTAY and not (
          B[r['booking_id']]['booking_status'] in ('Completed', 'Confirmed')
          and D(B[r['booking_id']]['check_in']) <= D(r['created_at']) <= min(D(B[r['booking_id']]['check_out']), TODAY))]
check('in-stay requests dated inside a stay that happened', not bad_in, f'{len(bad_in)} rows')
bad_pre = [r['request_id'] for r in req if r['booking_id'] and r['request_type'] in PRE
           and D(r['created_at']) > D(B[r['booking_id']]['check_in'])]
check('pre-arrival requests dated before check-in', not bad_pre, f'{len(bad_pre)} rows')
check('no request dated after SYSTEM_DATE', all(D(r['created_at']) <= TODAY for r in req))

print('\n[19] Complaints and special requests vs the stay (RULE Q)')
def stayed(b): return b['booking_status'] in ('Completed', 'Confirmed') and D(b['check_in']) <= TODAY
bad = [c['ticket_id'] for c in comp if c['booking_id'] and c['complaint_type'] in ('Room Issue', 'Service Issue', 'Facility Issue')
       and not (stayed(B[c['booking_id']]) and D(B[c['booking_id']]['check_in']) <= D(c['created_at']) <= TODAY)]
check('room / service / facility complaints raised during or after a real stay', not bad, f'{len(bad)} tickets')
bad = [c['ticket_id'] for c in comp if c['resolved_at'] and D(c['resolved_at']) < D(c['created_at'])]
check('no ticket resolved before it was created', not bad, f'{len(bad)} tickets')
bad = [r['request_id'] for r in sreq if r['request_status'] == 'Fulfilled' and not (
       stayed(B[r['booking_id']]) and r['fulfilled_at']
       and max(D(B[r['booking_id']]['check_in']), D(r['created_at'])) <= D(r['fulfilled_at']) <= min(D(B[r['booking_id']]['check_out']), TODAY))]
check('Fulfilled special requests fulfilled during a real stay, after being made', not bad, f'{len(bad)} requests')
bad = [r['request_id'] for r in sreq if r['request_status'] != 'Fulfilled' and r['fulfilled_at']]
check('only Fulfilled requests carry fulfilled_at', not bad, f'{len(bad)} requests')
bad = [r['request_id'] for r in sreq if D(r['created_at']) > min(D(B[r['booking_id']]['check_out']), TODAY)]
check('special requests made before or during the stay', not bad, f'{len(bad)} requests')

print('\n[20] Rate plans and the v4 refund policy (RULE T)')
check('rate_plan is Flexible or Non-refundable on every booking',
      all(r.get('rate_plan') in ('Flexible', 'Non-refundable') for r in bk))
P = {p['booking_id']: p for p in pay}
bad = [r['booking_id'] for r in bk if r['rate_plan'] == 'Non-refundable'
       and not (P[r['booking_id']]['payment_status'] == 'Paid' and float(P[r['booking_id']]['refund_amount']) == 0)]
check('Non-refundable bookings are paid in full and never refunded', not bad, f'{len(bad)} bookings')
def ok_flex(r):
    p = P[r['booking_id']]; st = p['payment_status']; tot = float(r['total_amount']); night = float(r['price_per_night'])
    if r['booking_status'] == 'Cancelled':
        return (st in ('Refunded', 'Failed') or (st == 'Partially Refunded' and abs(float(p['refund_amount']) - (tot - night)) < 0.02)
                or (st == 'Paid' and int(r['nights']) == 1))
    if r['booking_status'] == 'No-show':
        return (st == 'Failed' or (st == 'Partially Refunded' and abs(float(p['refund_amount']) - (tot - night)) < 0.02)
                or (st == 'Paid' and int(r['nights']) == 1))
    return True
bad = [r['booking_id'] for r in bk if r['rate_plan'] == 'Flexible' and not ok_flex(r)]
check('Flexible cancellations / no-shows refunded per policy (all, or all but the first night)', not bad, f'{len(bad)} bookings')
room_nums = [r['room_number'] for r in rooms]
check('room numbers unique, floors 2-16, view Nile or City',
      len(set(room_nums)) == len(room_nums) and all(2 <= int(r['floor']) <= 16 and r['view'] in ('Nile', 'City') for r in rooms))
check('every Suite faces the Nile', all(r['view'] == 'Nile' for r in rooms if r['room_type_id'] == 'RT006'))

print('\n[21] Loyalty programme tables')
lt = read(f'{S}/loyalty_tiers.csv')
tiers = {r['tier'] for r in lt}
check('every member tier is defined in loyalty_tiers.csv', {m['tier'] for m in loyal} <= tiers,
      f"{sorted({m['tier'] for m in loyal} - tiers)}")
check('tier thresholds increase with the tier', [int(r['min_nights_per_year']) for r in lt] == sorted(int(r['min_nights_per_year']) for r in lt))

print('\n' + '=' * 78)
passed = sum(1 for _, ok, _ in results if ok)
failed = len(results) - passed
print(f'RESULT: {passed}/{len(results)} checks passed' + (f', {failed} FAILED' if failed else ''))
print('=' * 78)
if failed:
    print('\nFailed:')
    for n, ok, d in results:
        if not ok: print(f'  - {n}: {d}')
sys.exit(1 if failed else 0)
