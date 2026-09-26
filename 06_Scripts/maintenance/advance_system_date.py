#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Move the frozen SYSTEM_DATE forward and bring every status in line with it.

    python3 06_Scripts/maintenance/advance_system_date.py 2026-10-15

Rewrites SYSTEM_DATE in 06_Scripts/config.py, then runs 06_Scripts/rebuild_all.py:
booking statuses are recomputed from the raw file (a Confirmed stay whose check-out has
passed becomes Completed, RULE C/D), payments / rooms / feedback / requests follow, and the
conversations are regenerated so the in-house rooms and upcoming bookings they quote are
still true. Use it at the start of a demo period, not in the middle of one.
"""
import os, re, subprocess, sys
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(ROOT)
if len(sys.argv) != 2: sys.exit(__doc__)
new = date.fromisoformat(sys.argv[1])
p = '06_Scripts/config.py'
s = open(p, encoding='utf-8').read()
s2 = re.sub(r'SYSTEM_DATE = date\(\d+, \d+, \d+\)', f'SYSTEM_DATE = date({new.year}, {new.month}, {new.day})', s)
assert s2 != s or f'date({new.year}, {new.month}, {new.day})' in s
open(p, 'w', encoding='utf-8').write(s2)
print(f'SYSTEM_DATE set to {new}')
sys.exit(subprocess.run([sys.executable, '06_Scripts/rebuild_all.py']).returncode)
