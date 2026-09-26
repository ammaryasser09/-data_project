#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Reference booking generator — enforces every rule in 01_Docs/BUSINESS_RULES.md.

The original generators in the source repository are empty notebooks ("cells": []), so the
corruption in the delivered data could not be traced to source. This is the replacement:
a generator that cannot produce the defects that were found.

    python3 06_Scripts/generation/generate_bookings.py --n 2000 --out /tmp/bookings_test.csv

It is a reference implementation, not the producer of the shipped data. The shipped data was
repaired rather than regenerated, to preserve 20,000 bookings and their payment and request
relationships.
"""
import argparse, csv, os, random, sys
from collections import defaultdict
from datetime import date, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import SYSTEM_DATE as TODAY   # single frozen 'today' — see 06_Scripts/config.py
BLOCKING = {'Confirmed', 'Completed'}

def rd(p):
    with open(os.path.join(ROOT, p), encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))

def generate(n, seed=42, horizon=540, target_occupancy=0.70):
    random.seed(seed)
    rt    = rd('02_Data/02_Operational/room_types.csv')
    rooms = rd('02_Data/02_Operational/rooms.csv')
    cus   = rd('02_Data/02_Operational/customers.csv')
    CAP  = {r['room_type_id']: int(r['capacity']) for r in rt}
    BASE = {r['room_type_id']: float(r['base_price']) for r in rt}
    BY_TYPE = defaultdict(list)
    for r in rooms: BY_TYPE[r['room_type_id']].append(r['room_id'])
    cust_ids = [c['customer_id'] for c in cus]

    start = TODAY - timedelta(days=horizon // 2)
    occ = defaultdict(list)
    out, attempts, rejected = [], 0, defaultdict(int)
    capacity_nights = len(rooms) * horizon * target_occupancy
    used_nights = 0

    while len(out) < n and attempts < n * 50:
        attempts += 1
        # RULE: volume ceiling — never generate past the occupancy target
        if used_nights >= capacity_nights:
            rejected['occupancy_ceiling'] += 1
            break

        t = random.choice(list(CAP))
        cap = CAP[t]
        # RULE A: children count toward room capacity, so adults + children <= capacity.
        # Draw a total that already fits, then split it into adults and children.
        total = random.randint(1, cap)
        adults = random.randint(1, total)
        children = total - adults
        assert adults + children <= cap       # RULE A: adults + children <= capacity

        ci = start + timedelta(days=random.randint(0, horizon - 1))
        nights = random.randint(1, 10)
        co = ci + timedelta(days=nights)
        # RULE: check_in < check_out
        assert co > ci

        # RULE C / D: status must agree with the dates
        if ci > TODAY:
            status = random.choices(['Confirmed', 'Cancelled'], [0.85, 0.15])[0]
        else:
            status = random.choices(['Completed', 'Cancelled', 'No-show'],
                                    [0.72, 0.18, 0.10])[0]

        room = None
        if status in BLOCKING:
            # RULE B: strict inequality, back-to-back allowed
            for rm in BY_TYPE[t]:
                if all(co <= s or ci >= e for s, e in occ[rm]):
                    room = rm; break
            if room is None:
                rejected['no_free_room'] += 1
                continue
            occ[room].append((ci, co))
            used_nights += nights
        else:
            room = random.choice(BY_TYPE[t])

        factor = round(random.uniform(0.85, 1.30), 2)
        rate = round(BASE[t] * factor, 2)
        out.append({
            'booking_id': f'B{len(out)+1:06d}',
            'customer_id': random.choice(cust_ids),
            'room_id': room, 'room_type_id': t,
            'check_in': ci.isoformat(), 'check_out': co.isoformat(),
            'nights': nights, 'adults': adults, 'children': children,
            'booking_status': status,
            'booking_channel': random.choice(['Website','Mobile App','Phone',
                                              'Booking Platform','Travel Agent']),
            'price_per_night': f'{rate:.2f}',
            'total_amount': f'{rate * nights:.2f}',
        })
    return out, dict(rejected), CAP, BY_TYPE


def validate(rows, CAP, BY_TYPE):
    """Every constraint the repair pass had to fix, checked at generation time."""
    d = date.fromisoformat
    checks = {}
    checks['dates valid'] = all(d(r['check_out']) > d(r['check_in']) for r in rows)
    checks['nights correct'] = all(
        int(r['nights']) == (d(r['check_out']) - d(r['check_in'])).days for r in rows)
    # RULE A: adults + children <= capacity (children count toward room capacity)
    checks['RULE A capacity'] = all(
        int(r['adults']) + int(r['children']) <= CAP[r['room_type_id']] for r in rows)
    checks['room belongs to type'] = all(
        r['room_id'] in BY_TYPE[r['room_type_id']] for r in rows)
    checks['totals consistent'] = all(
        abs(float(r['total_amount']) - float(r['price_per_night']) * int(r['nights'])) < 0.01
        for r in rows)
    checks['states possible'] = all(
        not (r['booking_status'] in ('Completed','No-show') and d(r['check_in']) > TODAY)
        and not (r['booking_status'] == 'Confirmed' and d(r['check_out']) < TODAY)
        for r in rows)
    idx = defaultdict(list)
    for r in rows:
        if r['booking_status'] in BLOCKING:
            idx[r['room_id']].append((d(r['check_in']), d(r['check_out'])))
    clash = b2b = 0
    for rm, lst in idx.items():
        lst.sort()
        for i in range(len(lst)):
            for j in range(i+1, len(lst)):
                if lst[j][0] >= lst[i][1]:
                    if lst[j][0] == lst[i][1]: b2b += 1
                    break
                if lst[i][0] < lst[j][1] and lst[j][0] < lst[i][1]: clash += 1
    checks['RULE B no overlap'] = clash == 0
    checks['back-to-back produced'] = b2b > 0
    return checks, b2b


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--n', type=int, default=2000)
    ap.add_argument('--out', default='')
    a = ap.parse_args()
    rows, rejected, CAP, BY_TYPE = generate(a.n)
    checks, b2b = validate(rows, CAP, BY_TYPE)
    print(f'generated {len(rows)} bookings; rejected: {rejected}')
    for k, v in checks.items():
        print(f"  {'PASS' if v else 'FAIL'}  {k}")
    print(f'  back-to-back pairs produced: {b2b}')
    if a.out and rows:
        with open(a.out, 'w', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
        print(f'  written to {a.out}')
    sys.exit(0 if all(checks.values()) else 1)
