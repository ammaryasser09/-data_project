#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Apply the official Nile Pearl Hotel business rules to the booking dataset.

Rules implemented (see 01_Docs/BUSINESS_RULES.md):
  RULE A  adults + children <= room_type.capacity          (children count)
  RULE B  overlap iff  a.check_in < b.check_out AND b.check_in < a.check_out
          (back-to-back is valid and must be preserved)
  RULE C  No-show is non-blocking; grace period ends 23:59 on the check-in date
  RULE D  blocking = {Confirmed, Completed during its own stay}; non-blocking = {Cancelled, No-show}
  RULE E  pipeline order: dates → guests → status → blocking → capacity → availability
          → assign room → verify no overlap → final validation

Source:  02_Data/01_Raw/bookings_raw.csv   (never modified)
Output:  02_Data/02_Operational/bookings.csv

Run from the project root:
    python3 06_Scripts/repair/apply_business_rules.py
"""
import csv, hashlib, os, sys
from collections import defaultdict, Counter
from datetime import date, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(ROOT)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import SYSTEM_DATE as TODAY   # single frozen 'today' — see 06_Scripts/config.py

BLOCKING     = {'Confirmed', 'Completed'}
NON_BLOCKING = {'Cancelled', 'No-show'}

def rd(p):
    with open(p, encoding='utf-8-sig') as f: return list(csv.DictReader(f))
def d(s): return date.fromisoformat(str(s)[:10])
def sha(p): return hashlib.sha256(open(p, 'rb').read()).hexdigest()

src   = '02_Data/01_Raw/bookings_raw.csv'
bk    = rd(src)
rooms = rd('02_Data/02_Operational/rooms.csv')
rt    = rd('02_Data/02_Operational/room_types.csv')

CAP   = {r['room_type_id']: int(r['capacity']) for r in rt}
BASE  = {r['room_type_id']: float(r['base_price']) for r in rt}
NAME  = {r['room_type_id']: r['room_type_name'] for r in rt}
MAXCAP = max(CAP.values())
BY_TYPE = defaultdict(list)
for r in rooms: BY_TYPE[r['room_type_id']].append(r['room_id'])
# smallest room type that can hold n guests
LADDER = sorted(CAP.items(), key=lambda x: (x[1], BASE[x[0]]))

# ── STEP 0 — price list v4 ──
# room_types.csv carries the v4 price list; the raw bookings were priced on the original
# list (02_Data/01_Raw/room_types_raw.csv). Each booking keeps its seasonal factor: the
# nightly rate is rescaled by new_base / old_base of its (raw) room type.
OLD_BASE = {r['room_type_id']: float(r['base_price']) for r in rd('02_Data/01_Raw/room_types_raw.csv')}
for r in bk:
    f = BASE[r['room_type_id']] / OLD_BASE[r['room_type_id']]
    p = round(float(r['price_per_night']) * f, 2)
    r['price_per_night'] = f'{p:.2f}'
    r['total_amount'] = f'{round(p * int(r["nights"]), 2):.2f}'

log = []
def rec(rid, issue, old, new, action, reason, conf, review):
    log.append({'timestamp': datetime.now().isoformat(timespec='seconds'),
                'file': 'bookings.csv', 'table': 'bookings', 'record_id': rid,
                'issue': issue, 'old_value': old, 'new_value': new,
                'reason': reason, 'source': 'room_types.csv + BUSINESS_RULES.md',
                'repair_type': action, 'confidence': conf, 'reviewer_required': review})

with open('07_Audits/Repair_Logs/before_repair_hashes.txt', 'w') as f:
    f.write(f'{sha(src)}  {src}\n')

print('=' * 78)
print('APPLYING OFFICIAL BUSINESS RULES')
print('=' * 78)

# ── STEP 1 — validate dates (nothing to repair, verify only) ──
bad = [r['booking_id'] for r in bk if d(r['check_out']) <= d(r['check_in'])]
print(f'\n[1] Dates            — invalid ranges: {len(bad)}')
assert not bad, bad[:5]

# ── STEP 2 — validate guest count against RULE A, repair room type ──
print('[2] Guests (RULE A)  — adults + children <= capacity')
upgraded = capped = 0
for r in bk:
    a, c = int(r['adults']), int(r['children'])
    total = a + c
    t = r['room_type_id']
    if total <= CAP[t]:
        continue
    if total > MAXCAP:
        # No room in the hotel holds this many. The synthetic generator produced a guest
        # count the property cannot accommodate. Reduce children to the largest capacity
        # and record the original value; adults are never touched.
        new_children = MAXCAP - a
        rec(r['booking_id'], 'guest_count_exceeds_every_room',
            f'adults={a}, children={c}, total={total}',
            f'adults={a}, children={new_children}, total={MAXCAP}',
            'guest_count_capped',
            f'largest room holds {MAXCAP}; no single-room booking can host {total} guests. '
            f'Adults preserved, children reduced to fit. Multi-room bookings are not '
            f'supported by the schema.', 'medium', 'no')
        r['children'] = str(new_children)
        total = MAXCAP
        capped += 1
    fit = next((k for k, v in LADDER if v >= total), None)
    if fit and fit != t:
        old_price = float(r['price_per_night'])
        factor = old_price / BASE[t]                 # preserve the seasonal factor
        new_price = round(BASE[fit] * factor, 2)
        rec(r['booking_id'], 'capacity_violation_rule_a',
            f'room_type={t} (cap {CAP[t]}), price_per_night={old_price}',
            f'room_type={fit} (cap {CAP[fit]}), price_per_night={new_price}',
            'room_type_upgraded',
            f'{total} guests do not fit {NAME[t]}; upgraded to the smallest type that fits. '
            f'Seasonal price factor {factor:.3f} preserved.', 'high', 'no')
        r['room_type_id'] = fit
        r['price_per_night'] = f'{new_price:.2f}'
        r['total_amount'] = f'{round(new_price * int(r["nights"]), 2):.2f}'
        upgraded += 1
print(f'      room type upgraded : {upgraded}')
print(f'      guest count capped : {capped}')

# ── STEP 3 — determine booking status (RULE C and RULE D) ──
print('[3] Status (RULE C/D)')
state_fixed = stale_fixed = 0
for r in bk:
    st, ci, co = r['booking_status'], d(r['check_in']), d(r['check_out'])
    if st in ('Completed', 'No-show') and ci > TODAY:
        rec(r['booking_id'], 'impossible_state', f'booking_status={st}',
            'booking_status=Confirmed', 'status_corrected',
            f'check_in {ci} has not occurred; a future stay cannot be Completed or a No-show',
            'high', 'no')
        r['booking_status'] = 'Confirmed'; state_fixed += 1
    elif st == 'No-show' and ci == TODAY:
        # RULE C: the booking is held until 23:59 on the check-in date, so on that date it
        # cannot yet be a no-show.
        rec(r['booking_id'], 'premature_no_show', 'booking_status=No-show',
            'booking_status=Confirmed', 'status_corrected',
            f'check_in is SYSTEM_DATE {TODAY}; the grace period runs until 23:59 today',
            'high', 'no')
        r['booking_status'] = 'Confirmed'; state_fixed += 1
    elif st == 'Completed' and co > TODAY:
        # RULE D: Completed means the guest stayed AND departed. A stay whose check-out is
        # still ahead is in progress, which this schema records as Confirmed. Both states
        # block the same dates, so occupancy is unaffected.
        rec(r['booking_id'], 'stay_in_progress', 'booking_status=Completed',
            'booking_status=Confirmed', 'status_corrected',
            f'check_out {co} is after SYSTEM_DATE {TODAY}; the stay has not finished',
            'high', 'no')
        r['booking_status'] = 'Confirmed'; state_fixed += 1
    elif st == 'Confirmed' and co < TODAY:
        # RULE C: the grace period ended long ago. Without an arrival record the synthetic
        # convention is that a confirmed historical stay was honoured.
        rec(r['booking_id'], 'stale_state', 'booking_status=Confirmed',
            'booking_status=Completed', 'status_normalised',
            f'check_out {co} passed; RULE C grace period expired. Synthetic convention: a '
            f'confirmed historical stay is recorded as Completed. Occupancy is unaffected '
            f'because both states block their own dates.', 'medium', 'no')
        r['booking_status'] = 'Completed'; stale_fixed += 1
print(f'      impossible states corrected : {state_fixed}')
print(f'      stale states normalised     : {stale_fixed}')

# ── STEP 4/5 — determine blocking set ──
blocking = [r for r in bk if r['booking_status'] in BLOCKING]
print(f'[4] Blocking set     — {len(blocking)} of {len(bk)} bookings occupy inventory')

# ── STEP 6/7/8 — capacity re-check, availability, room assignment ──
print('[5] Room assignment (RULE E order, RULE B overlap)')
occ = defaultdict(list)
moved, unplaceable = 0, []
for r in sorted(blocking, key=lambda x: (x['check_in'], x['booking_id'])):
    t, old = r['room_type_id'], r['room_id']
    ci, co = d(r['check_in']), d(r['check_out'])
    assert int(r['adults']) + int(r['children']) <= CAP[t], r['booking_id']   # RULE A holds
    placed = None
    for rm in [old] + [x for x in BY_TYPE[t] if x != old]:
        if rm not in BY_TYPE[t]: continue
        # RULE B: strict inequality on both sides, so co == other.ci is free
        if all(co <= s or ci >= e for s, e in occ[rm]):
            placed = rm; break
    if placed:
        occ[placed].append((ci, co))
        if placed != old:
            rec(r['booking_id'], 'room_reassignment', f'room_id={old}', f'room_id={placed}',
                'room_reassigned',
                f'{old} is not free for {ci}..{co}, or the room type changed under RULE A. '
                f'First-fit within the correct type, ordered by check_in then booking_id.',
                'high', 'no')
            r['room_id'] = placed; moved += 1
    else:
        unplaceable.append(r['booking_id'])
        rec(r['booking_id'], 'no_free_room_of_type', f'room_id={old}', 'unchanged', 'none',
            f'all {len(BY_TYPE[t])} rooms of {t} are occupied for these dates; active demand '
            f'exceeds physical inventory', 'n/a', 'YES')
print(f'      reassigned  : {moved}')
print(f'      unplaceable : {len(unplaceable)}  (excluded from the occupancy index, logged)')

# ── STEP 8b — non-blocking bookings whose room type changed under RULE A ──
# Cancelled and No-show bookings take no part in the occupancy index, but their room_id must
# still point at a room of their (possibly upgraded) type or the FK is semantically wrong.
nb_fixed = 0
for r in bk:
    nb = r['booking_status'] in NON_BLOCKING or r['booking_id'] in unplaceable
    if nb and r['room_id'] not in BY_TYPE[r['room_type_id']]:
        old = r['room_id']
        # Deterministic pick. Python's built-in hash() is randomised per process for strings
        # (PYTHONHASHSEED), which made this step produce a different room on every run.
        pick = int(hashlib.sha256(r['booking_id'].encode()).hexdigest(), 16)
        new = BY_TYPE[r['room_type_id']][pick % len(BY_TYPE[r['room_type_id']])]
        rec(r['booking_id'], 'room_type_room_mismatch', f'room_id={old}', f'room_id={new}',
            'room_realigned_no_occupancy',
            f"room type changed to {r['room_type_id']} under RULE A; {old} belongs to another "
            f'type. Booking takes no part in the occupancy index, so no availability '
            f'constraint applies.', 'high', 'no')
        r['room_id'] = new; nb_fixed += 1
print(f'      non-occupying rooms realigned : {nb_fixed}')

# ── STEP 9 — verify no overlap, preserve back-to-back ──
print('[6] Overlap verification (RULE B)')
idx = defaultdict(list)
for r in blocking:
    if r['booking_id'] not in unplaceable:
        idx[r['room_id']].append((d(r['check_in']), d(r['check_out']), r['booking_id']))
conflicts = b2b = 0
for rm, lst in idx.items():
    lst.sort()
    for i in range(len(lst)):
        for j in range(i + 1, len(lst)):
            if lst[j][0] >= lst[i][1]:
                if lst[j][0] == lst[i][1]: b2b += 1
                break
            if lst[i][0] < lst[j][1] and lst[j][0] < lst[i][1]: conflicts += 1
print(f'      active conflicts       : {conflicts}')
print(f'      back-to-back preserved : {b2b}')
assert conflicts == 0, 'overlap remains after assignment'

# ── STEP 10 — final validation ──
print('[7] Final validation')
viol_a = sum(1 for r in bk if int(r['adults']) + int(r['children']) > CAP[r['room_type_id']])
mismatch = sum(1 for r in bk
               if abs(float(r['total_amount']) - float(r['price_per_night']) * int(r['nights'])) > 0.01)
wrong_room = sum(1 for r in bk
                 if r['room_id'] not in BY_TYPE[r['room_type_id']])
print(f'      RULE A violations      : {viol_a}')
print(f'      total ≠ rate × nights  : {mismatch}')
print(f'      room/type mismatches   : {wrong_room}')
assert viol_a == 0 and mismatch == 0 and wrong_room == 0

# ── STEP 11 — make occupancy explicit in the table itself ──
# Earlier versions left the unplaceable bookings indistinguishable from placed ones inside
# bookings.csv; only repair_log.csv knew which to ignore, so any backend reading the table
# directly saw thousands of double bookings. blocks_inventory is the single column an
# availability query needs:  WHERE blocks_inventory = 'True' AND <RULE B overlap>.
unpl = set(unplaceable)
for r in bk:
    r['blocks_inventory'] = 'True' if (r['booking_status'] in BLOCKING
                                       and r['booking_id'] not in unpl) else 'False'
print(f"      blocks_inventory=True : {sum(r['blocks_inventory'] == 'True' for r in bk)}")

# ── write ──
cols = list(rd(src)[0].keys()) + ['blocks_inventory']
with open('02_Data/02_Operational/bookings.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(bk)
with open('07_Audits/Repair_Logs/repair_log.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=['timestamp','file','table','record_id','issue','old_value',
        'new_value','reason','source','repair_type','confidence','reviewer_required'])
    w.writeheader(); w.writerows(log)
with open('07_Audits/Repair_Logs/after_repair_hashes.txt', 'w') as f:
    f.write(f"{sha('02_Data/02_Operational/bookings.csv')}  bookings.csv\n")
    f.write(f'{sha(src)}  {src} (unchanged)\n')

print(f'\n      repair log entries: {len(log)}')
print(f'      by type: {dict(Counter(x["repair_type"] for x in log))}')
print(f'      status distribution now: {dict(Counter(r["booking_status"] for r in bk))}')
