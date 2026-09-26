# -*- coding: utf-8 -*-
"""
Single source of the project's frozen "today".

Every script, validator and — during development — the backend must read the current
date from here instead of calling date.today(). The dataset is a snapshot: booking
statuses (Confirmed / Completed / No-show), room status and the availability tests are
all consistent with THIS date, not with the real calendar.

To move the snapshot forward, run
    python3 06_Scripts/maintenance/advance_system_date.py YYYY-MM-DD
which rolls statuses forward and rewrites this constant. Never edit it by hand.
"""
from datetime import date

SYSTEM_DATE = date(2026, 9, 19)
