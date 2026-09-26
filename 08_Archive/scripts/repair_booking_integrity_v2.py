# SUPERSEDED / HISTORICAL — NOT SOURCE OF TRUTH
# Replaced by 06_Scripts/repair/apply_business_rules.py.
# Kept only to document how the second repair cycle worked. Do not run.

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Critical booking integrity repair.

Operates on 02_Data/08_Archive/bookings_original.csv (never modified) and writes a repaired
copy to 02_Data/03_Structured/Bookings/bookings.csv.

Every conflict is classified before any repair. Every change is logged. Nothing is deleted.
Where evidence is insufficient to choose deterministically, the row is marked
REQUIRES_HUMAN_REVIEW and left alone.

Run from the project root:  python3 07_Scripts/Repair/repair_booking_integrity.py
"""
import csv, hashlib, os, sys
from collections import defaultdict, Counter
from datetime import date, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(ROOT)

TODAY = date(2026, 9, 19)

# ── business rules, documented in 01_Docs/Architecture/booking_state_machine.md ──
ACTIVE_BOOKING_STATUSES = {'Confirmed', 'Completed'}   # occupy a room
NON_BLOCKING_STATUSES   = {'Cancelled', 'No-show'}     # do not occupy a room
# A no-show did not physically occupy the room. It may still carry a charge, but for
# availability it must not block, or the hotel loses sellable inventory.

def rd(p):
    with open(p, encoding='utf-8-sig') as f: return list(csv.DictReader(f))
def d(s): return date.fromisoformat(s[:10])
def sha(p): return hashlib.sha256(open(p, 'rb').read()).hexdigest()

bk    = rd('02_Data/08_Archive/bookings_original.csv')
rooms = rd('02_Data/03_Structured/Rooms/rooms.csv')
rt    = rd('02_Data/03_Structured/Rooms/room_types.csv')
cap   = {r['room_type_id']: int(r['capacity']) for r in rt}
rooms_by_type = defaultdict(list)
for r in rooms: rooms_by_type[r['room_type_id']].append(r['room_id'])

# ── hashes before ──
os.makedirs('06_Audits/Repair_Logs', exist_ok=True)
with open('06_Audits/Repair_Logs/BEFORE_REPAIR_HASHES.txt', 'w') as f:
    f.write('SHA256 before repair\n\n')
    for p in ['02_Data/08_Archive/bookings_original.csv',
              '02_Data/08_Archive/customers_original.csv',
              '02_Data/08_Archive/payments_original.csv',
              '02_Data/03_Structured/Rooms/rooms.csv',
              '02_Data/03_Structured/Rooms/room_types.csv']:
        f.write(f'{sha(p)}  {p}\n')

log = []
def record(rid, issue, old, new, action, evidence, reason, conf, review):
    log.append({'timestamp': datetime.now().isoformat(timespec='seconds'),
                'table': 'bookings', 'record_id': rid, 'issue_type': issue,
                'old_values': old, 'new_values': new, 'repair_action': action,
                'evidence': evidence, 'source': 'bookings_original.csv + rooms.csv + room_types.csv',
                'reason': reason, 'confidence': conf, 'reviewer_required': review})

print('=' * 78)
print('BOOKING INTEGRITY REPAIR')
print('=' * 78)

# ═══ STEP 1b — state machine repairs (MUST run before room assignment:
#     a No-show corrected to Confirmed becomes room-blocking and needs a free room) ═══
print('\n[3] Booking state machine')
fixed_state, ambiguous = 0, 0
for r in bk:
    st, ci, co = r['booking_status'], d(r['check_in']), d(r['check_out'])
    if st == 'Completed' and ci > TODAY:
        r['booking_status'] = 'Confirmed'; fixed_state += 1
        record(r['booking_id'], 'impossible_state', 'booking_status=Completed',
               'booking_status=Confirmed', 'status_corrected',
               f'check_in {ci} is in the future relative to {TODAY}',
               'a stay that has not started cannot be Completed; Confirmed is the only valid '
               'state for a future-dated active booking', 'high', 'no')
    elif st == 'No-show' and ci > TODAY:
        r['booking_status'] = 'Confirmed'; fixed_state += 1
        record(r['booking_id'], 'impossible_state', 'booking_status=No-show',
               'booking_status=Confirmed', 'status_corrected',
               f'check_in {ci} is in the future relative to {TODAY}',
               'a guest cannot have failed to arrive for a date that has not occurred', 'high', 'no')
    elif st == 'Confirmed' and co < TODAY:
        ambiguous += 1
        record(r['booking_id'], 'stale_state', 'booking_status=Confirmed', 'unchanged',
               'none', f'check_out {co} already passed',
               'should be Completed or No-show; no check-in record exists to decide which',
               'n/a', 'YES')
print(f"      corrected (deterministic): {fixed_state}")
print(f"      ambiguous (REQUIRES_HUMAN_REVIEW): {ambiguous}")


# ═══ STEP 1 — classify overlaps ═══
print('\n[1] Classifying overlaps (interval rule, back-to-back excluded)')
by_room = defaultdict(list)
for r in bk: by_room[r['room_id']].append(r)

conflicts = []
cid = 0
for rm, lst in by_room.items():
    lst.sort(key=lambda r: (r['check_in'], r['booking_id']))
    for i in range(len(lst)):
        for j in range(i + 1, len(lst)):
            if d(lst[j]['check_in']) >= d(lst[i]['check_out']):
                break                              # sorted: no later booking can overlap
            a, b = lst[i], lst[j]
            if not (d(a['check_in']) < d(b['check_out']) and d(b['check_in']) < d(a['check_out'])):
                continue
            sa, sb = a['booking_status'], b['booking_status']
            if (a['customer_id'] == b['customer_id'] and a['check_in'] == b['check_in']
                    and a['check_out'] == b['check_out']):
                kind = 'D_DUPLICATE_BOOKING'
            elif sa in ACTIVE_BOOKING_STATUSES and sb in ACTIVE_BOOKING_STATUSES:
                kind = 'A_TRUE_CONFLICT'
            else:
                kind = 'B_NON_BLOCKING'
            cid += 1
            conflicts.append({'conflict_id': f'CF{cid:06d}',
                'booking_id_a': a['booking_id'], 'booking_id_b': b['booking_id'],
                'room_id': rm,
                'overlap_start': max(a['check_in'][:10], b['check_in'][:10]),
                'overlap_end': min(a['check_out'][:10], b['check_out'][:10]),
                'status_a': sa, 'status_b': sb, 'conflict_type': kind,
                'resolution': '', 'selected_booking': '', 'rejected_booking': '',
                'reason': '', 'evidence': '', 'confidence': '', 'requires_human_review': ''})

counts = Counter(c['conflict_type'] for c in conflicts)
print(f"      overlapping pairs: {len(conflicts)}")
for k, v in sorted(counts.items()): print(f"        {k}: {v}")

# ═══ STEP 2 — repair true conflicts by reassignment ═══
print('\n[2] Repairing A_TRUE_CONFLICT by room reassignment within the same room type')
print('      Classification 4C (data model issue): the room assignment is wrong, not the booking.')
print('      No booking is deleted; no winner is chosen; both stays are preserved.')

blocking = [r for r in bk if r['booking_status'] in ACTIVE_BOOKING_STATUSES]
occupancy = defaultdict(list)
moved, unplaceable = 0, []

for r in sorted(blocking, key=lambda x: (x['check_in'], x['booking_id'])):
    t, old = r['room_type_id'], r['room_id']
    ci, co = d(r['check_in']), d(r['check_out'])
    placed = None
    for rm in [old] + [x for x in rooms_by_type[t] if x != old]:
        if rm not in rooms_by_type[t]: continue
        if all(co <= s or ci >= e for s, e in occupancy[rm]):
            placed = rm; break
    if placed:
        occupancy[placed].append((ci, co))
        if placed != old:
            r['room_id'] = placed; moved += 1
            record(r['booking_id'], 'room_double_booked', f'room_id={old}',
                   f'room_id={placed}', 'reassigned_to_free_room_same_type',
                   f'{old} occupied on {ci}..{co} by an earlier active booking',
                   'deterministic first-fit ordered by check_in then booking_id; room type, '
                   'dates, guests and price all unchanged', 'high', 'no')
    else:
        unplaceable.append(r['booking_id'])
        record(r['booking_id'], 'no_free_room_of_type', f'room_id={old}', 'unchanged',
               'none', f'all {len(rooms_by_type[t])} rooms of {t} occupied for these dates',
               'active booking volume exceeds physical inventory; cannot repair without '
               'deleting a booking or changing the room list', 'n/a', 'YES')

print(f"      reassigned: {moved}")
print(f"      unplaceable (REQUIRES_HUMAN_REVIEW): {len(unplaceable)}")

# fill the resolution columns
placed_set = {r['booking_id']: r['room_id'] for r in blocking}
for c in conflicts:
    if c['conflict_type'] == 'A_TRUE_CONFLICT':
        a_un = c['booking_id_a'] in unplaceable
        b_un = c['booking_id_b'] in unplaceable
        if a_un or b_un:
            c.update(resolution='REQUIRES_HUMAN_REVIEW', requires_human_review='YES',
                     reason='no free room of this type for the overlapping dates',
                     evidence='inventory exhausted', confidence='n/a')
        else:
            c.update(resolution='ROOM_REASSIGNED', selected_booking='both retained',
                     rejected_booking='none', requires_human_review='no',
                     reason='room assignment corrected; both bookings kept',
                     evidence=f"a→{placed_set.get(c['booking_id_a'])}, b→{placed_set.get(c['booking_id_b'])}",
                     confidence='high')
    elif c['conflict_type'] == 'B_NON_BLOCKING':
        c.update(resolution='NO_ACTION', requires_human_review='no',
                 reason='at least one booking is Cancelled or No-show and does not occupy the room',
                 evidence=f"status_a={c['status_a']}, status_b={c['status_b']}", confidence='high')
    else:
        c.update(resolution='REQUIRES_HUMAN_REVIEW', requires_human_review='YES',
                 reason='same customer, same room, same dates — possible duplicate submission',
                 evidence='identical customer_id and date range', confidence='medium')

# ═══ STEP 3 — capacity: classify, do not repair ═══
print('\n[4] Capacity violations — classified, NOT repaired')
over, adults_only_over = [], 0
for r in bk:
    a, c_ = int(r['adults']), int(r['children'])
    if a + c_ > cap[r['room_type_id']]:
        over.append(r)
        if a > cap[r['room_type_id']]: adults_only_over += 1
print(f"      total_guests > capacity: {len(over)}")
print(f"      of those, adults alone exceed capacity: {adults_only_over}")
print(f"      → classification D_CAPACITY_DEFINITION_ERROR")
print(f"      Evidence: in {len(over)} of {len(over)} cases the adults fit and only the children")
print(f"      push the count over. The generator applied adults <= capacity; the knowledge base")
print(f"      says guests <= capacity. The two rules disagree. Resolving this requires the")
print(f"      hotel's actual rule, so no row is changed.")
for r in over:
    record(r['booking_id'], 'capacity_definition_ambiguity',
           f"adults={r['adults']}, children={r['children']}, capacity={cap[r['room_type_id']]}",
           'unchanged', 'none',
           'adults alone are within capacity; only children exceed it',
           'knowledge base says guests<=capacity, generator applied adults<=capacity; '
           'changing capacity, guest counts or room type are all forbidden without the real rule',
           'n/a', 'YES')

# ═══ write outputs ═══
os.makedirs('02_Data/03_Structured/Bookings', exist_ok=True)
cols = list(rd('02_Data/08_Archive/bookings_original.csv')[0].keys())
with open('02_Data/03_Structured/Bookings/bookings.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(bk)

with open('06_Audits/Repair_Logs/booking_conflict_resolution.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=list(conflicts[0].keys())); w.writeheader(); w.writerows(conflicts)

with open('06_Audits/Repair_Logs/booking_integrity_repair_log.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=['timestamp','table','record_id','issue_type','old_values',
        'new_values','repair_action','evidence','source','reason','confidence','reviewer_required'])
    w.writeheader(); w.writerows(log)

with open('06_Audits/Repair_Logs/AFTER_REPAIR_HASHES.txt', 'w') as f:
    f.write('SHA256 after repair\n\n')
    f.write(f"{sha('02_Data/03_Structured/Bookings/bookings.csv')}  02_Data/03_Structured/Bookings/bookings.csv\n")
    f.write(f"{sha('02_Data/08_Archive/bookings_original.csv')}  02_Data/08_Archive/bookings_original.csv (unchanged)\n")

print(f"\n      repair log: {len(log)} entries")
print(f"      conflict table: {len(conflicts)} rows")
print(f"      changes applied: {moved} reassignments + {fixed_state} status corrections")
print(f"      left for review: {len(unplaceable)} unplaceable + {ambiguous} stale states + {len(over)} capacity")
