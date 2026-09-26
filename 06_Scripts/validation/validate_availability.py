#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Availability engine and its test suite.

Run from the project root:  python3 06_Scripts/validation/validate_availability.py

The engine is the reference implementation the backend should mirror. The test suite proves
it handles the boundary cases that break naive implementations — in particular that a
check-out on the same day as the next check-in is NOT an overlap.
"""
import csv, os, sys
from collections import defaultdict
from datetime import date, timedelta
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import SYSTEM_DATE as TODAY   # single frozen 'today' — see 06_Scripts/config.py

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(ROOT)

ACTIVE_BOOKING_STATUSES = {'Confirmed', 'Completed'}
NON_BLOCKING_STATUSES   = {'Cancelled', 'No-show'}

def rd(p):
    with open(p, encoding='utf-8-sig') as f: return list(csv.DictReader(f))
def d(s): return date.fromisoformat(str(s)[:10])

bookings = rd('02_Data/02_Operational/bookings.csv')
rooms    = rd('02_Data/02_Operational/rooms.csv')
rtypes   = rd('02_Data/02_Operational/room_types.csv')
# Occupancy comes from the table itself (RULE J). The repair log is no longer consulted.
flagged  = {r['booking_id'] for r in bookings if r['blocks_inventory'] != 'True'}

CAP  = {r['room_type_id']: int(r['capacity']) for r in rtypes}
NAME = {r['room_type_id']: r['room_type_name'] for r in rtypes}
ROOMS_BY_TYPE = defaultdict(list)
for r in rooms: ROOMS_BY_TYPE[r['room_type_id']].append(r['room_id'])

OCC = defaultdict(list)
for b in bookings:
    if b['booking_status'] in ACTIVE_BOOKING_STATUSES and b['booking_id'] not in flagged:
        OCC[b['room_id']].append((d(b['check_in']), d(b['check_out']), b['booking_id']))
for k in OCC: OCC[k].sort()


def is_room_available(room_id, ci, co, extra=None):
    """A room is free when no blocking booking overlaps [ci, co).
    Back-to-back is allowed: co == next_ci does not overlap."""
    if co <= ci:
        raise ValueError('check_out must be after check_in')
    for s, e, _ in OCC.get(room_id, []) + (extra or []):
        if ci < e and s < co:
            return False
    return True


def find_available_rooms(room_type_id, ci, co, guests=None, today=None):
    """Returns (rooms, reason). Empty list with a reason when the request is not satisfiable."""
    today = today or TODAY
    if co <= ci:
        return [], 'INVALID_DATE_RANGE: check-out must be after check-in'
    if ci < today:
        return [], 'PAST_DATE: check-in is in the past'
    if room_type_id not in CAP:
        return [], f'INVALID_ROOM_TYPE: {room_type_id} does not exist'
    if guests is not None and guests > CAP[room_type_id]:
        return [], (f'CAPACITY_EXCEEDED: {NAME[room_type_id]} holds {CAP[room_type_id]} '
                    f'guests, {guests} requested')
    free = [r for r in ROOMS_BY_TYPE[room_type_id] if is_room_available(r, ci, co)]
    if not free:
        return [], 'NO_AVAILABILITY: every room of this type is occupied for these dates'
    return free, 'OK'


# ────────────────────────── test suite ──────────────────────────
results = []
def t(name, inp, expected, actual, ok, reason):
    results.append((name, inp, expected, actual, ok, reason))
    print(f"  {'PASS' if ok else 'FAIL'}  {name}")
    print(f"        input    : {inp}")
    print(f"        expected : {expected}")
    print(f"        actual   : {actual}")
    if not ok: print(f"        reason   : {reason}")

print('=' * 78)
print('AVAILABILITY ENGINE — TEST SUITE')
print('=' * 78)
print()

# The hotel data runs at ~90% occupancy, so a fixed probe date may legitimately be full.
# Search the horizon for a date with an RT002 room free: we are testing the engine, not
# the occupancy of one arbitrary day. If no date in two years has a free room, that is a
# genuine failure worth reporting.
def first_free_date(rtid, nights=2, start=TODAY + timedelta(days=1), days=700):
    for i in range(days):
        ci = start + timedelta(days=i)
        co = ci + timedelta(days=nights)
        for r in ROOMS_BY_TYPE[rtid]:
            if is_room_available(r, ci, co):
                return ci, co, r
    return None, None, None

FUTURE, FUTURE_OUT, FREE_RT002 = first_free_date('RT002')
probe_room = ROOMS_BY_TYPE['RT002'][0]

# 1 — completely free room
free_room, ci, co = FREE_RT002, FUTURE, FUTURE_OUT
t('1. completely free room', f'{free_room}, {ci}..{co}', 'available',
  'available' if free_room and is_room_available(free_room, ci, co) else 'unavailable',
  bool(free_room), 'no free RT002 room found on the probe dates')

# 2 — fully occupied room
busy = next(((r, o) for r, o in OCC.items() if o), (None, None))
rid, occ = busy
if occ:
    s, e, bid = occ[0]
    got = is_room_available(rid, s, e)
    t('2. fully occupied room', f'{rid}, {s}..{e} (booked by {bid})', 'unavailable',
      'available' if got else 'unavailable', got is False, 'engine reported a booked room free')

# 3 — partial overlap
if occ:
    s, e, bid = occ[0]
    ps, pe = s - timedelta(days=1), s + timedelta(days=1)
    got = is_room_available(rid, ps, pe)
    t('3. partial overlap', f'{rid}, {ps}..{pe} over booking {s}..{e}', 'unavailable',
      'available' if got else 'unavailable', got is False, 'partial overlap not detected')

# 4 — exact check-out / check-in boundary  ← the one naive engines get wrong
if occ:
    s, e, bid = occ[0]
    nxt_e = e + timedelta(days=2)
    blocked_by_later = any(x[0] < nxt_e and e < x[1] for x in OCC[rid])
    got = is_room_available(rid, e, nxt_e)
    expected_free = not blocked_by_later
    t('4. back-to-back boundary (check_out == next check_in)',
      f'{rid}, {e}..{nxt_e} directly after booking ending {e}',
      'available' if expected_free else 'unavailable (a later booking also overlaps)',
      'available' if got else 'unavailable', got == expected_free,
      'check_out == check_in was treated as an overlap')

# 5 — cancelled booking must not block
canc = next((b for b in bookings if b['booking_status'] == 'Cancelled'), None)
blocks = any(bid == canc['booking_id'] for o in OCC.values() for *_, bid in o)
t('5. cancelled booking does not block', f"{canc['booking_id']} ({canc['room_id']})",
  'not in occupancy index', 'in occupancy index' if blocks else 'not in occupancy index',
  not blocks, 'a cancelled booking is blocking inventory')

# 6 — no-show must not block
ns = next((b for b in bookings if b['booking_status'] == 'No-show'), None)
blocks = any(bid == ns['booking_id'] for o in OCC.values() for *_, bid in o)
t('6. no-show does not block', f"{ns['booking_id']} ({ns['room_id']})",
  'not in occupancy index', 'in occupancy index' if blocks else 'not in occupancy index',
  not blocks, 'a no-show is blocking inventory')

# 7 — completed historical booking still blocks its own dates
comp = next((b for b in bookings if b['booking_status'] == 'Completed'
             and b['booking_id'] not in flagged), None)
got = is_room_available(comp['room_id'], d(comp['check_in']), d(comp['check_out']))
t('7. completed booking blocks its historical dates',
  f"{comp['room_id']}, {comp['check_in'][:10]}..{comp['check_out'][:10]}", 'unavailable',
  'available' if got else 'unavailable', got is False,
  'historical occupancy not recorded')

# 8 — multiple rooms of one type
res, why = find_available_rooms('RT002', FUTURE, FUTURE_OUT, guests=2)
t('8. multiple rooms searchable', f'RT002, {FUTURE}, 2 nights, 2 guests',
  'one or more rooms', f'{len(res)} rooms ({why})', len(res) > 0, why)

# 9 — multiple room types
per = {k: len(find_available_rooms(k, FUTURE, FUTURE_OUT)[0]) for k in CAP}
t('9. all room types searchable', f'all types on {FUTURE}',
  '6 types return a count', f'{per}', len(per) == 6, 'a room type is missing')

# 10 — capacity violation rejected
res, why = find_available_rooms('RT001', FUTURE, FUTURE_OUT, guests=2)
t('10. capacity violation rejected', 'RT001 (capacity 1), 2 guests', 'CAPACITY_EXCEEDED',
  why.split(':')[0], why.startswith('CAPACITY_EXCEEDED'), why)

# 11 — invalid date range rejected
res, why = find_available_rooms('RT002', FUTURE + timedelta(days=3), FUTURE)
t('11. invalid date range rejected', 'check_out before check_in', 'INVALID_DATE_RANGE',
  why.split(':')[0], why.startswith('INVALID_DATE_RANGE'), why)

# 12 — past date rejected
res, why = find_available_rooms('RT002', date(2020, 1, 1), date(2020, 1, 3))
t('12. past date rejected', '2020-01-01', 'PAST_DATE', why.split(':')[0],
  why.startswith('PAST_DATE'), why)

# 13 — same-day booking supported
res, why = find_available_rooms('RT002', TODAY, TODAY + timedelta(days=1))
t('13. same-day booking supported', 'check_in == today', 'not rejected as past',
  why.split(':')[0], not why.startswith('PAST_DATE'), why)

# 14 — invalid room type rejected
res, why = find_available_rooms('RT999', FUTURE, FUTURE_OUT)
t('14. invalid room type rejected', 'RT999', 'INVALID_ROOM_TYPE', why.split(':')[0],
  why.startswith('INVALID_ROOM_TYPE'), why)

# 15 — no overlap remains anywhere in the index
clashes = []
for rm, lst in OCC.items():
    for i in range(len(lst) - 1):
        if lst[i][1] > lst[i + 1][0]:
            clashes.append((rm, lst[i][2], lst[i + 1][2]))
t('15. occupancy index internally consistent', 'all blocking bookings',
  '0 overlaps', f'{len(clashes)} overlaps', not clashes,
  f'examples: {clashes[:3]}')

print('\n' + '=' * 78)
passed = sum(1 for *_, ok, _ in results if ok)
print(f'RESULT: {passed}/{len(results)} availability tests passed')
print('=' * 78)

with open('05_Evaluation/availability_test_cases.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['test', 'input', 'expected', 'actual', 'result', 'reason'])
    for n, i, e, a, ok, r in results:
        w.writerow([n, i, e, a, 'PASS' if ok else 'FAIL', '' if ok else r])

sys.exit(0 if passed == len(results) else 1)
