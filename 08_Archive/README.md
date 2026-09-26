# 08_Archive — non-active

**Nothing here is source of truth, and no active script reads from this folder.**
Verified: `grep -rn 08_Archive 06_Scripts/` returns nothing.

| Folder | Contents | Why kept |
|---|---|---|
| `audits/` | Reports from each repair cycle, numbered in the order they were produced | They show how 17,080 conflicts, 3,563 capacity violations and 8,518 impossible states were found and resolved. The final certification summarises them; these carry the detail. |
| `audits/05_v2_*` | The v2 certification, cleanup report, validation results and hashes | Superseded by the v3 audit (`07_Audits/Final/V3_AUDIT_REPORT.md`). The v2 certification reported READY while 3,468 overlapping bookings, stale payments and the other v3 findings were present; kept as a record of that. |
| `audits/06_v3_*` | The v3 audit report, certification, validation results and hashes | Superseded by v4 (new prices, rate plans, policies, rooms layout, RAG code). The v3 findings remain valid history; `V4_AUDIT_REPORT.md` builds on them. |
| `reports/` | The package certification and discovery report from before restructuring | Their figures were superseded, and one of them (`00_package_certification.txt`) reported PASS while three real defects were present. Kept as a record of that. |
| `scripts/` | `repair_booking_integrity_v2.py` | The second repair cycle. It classified conflicts but predates the business rules and contains the status-ordering bug fixed in the current script. Do not run. |

Every file carries a `SUPERSEDED / HISTORICAL — NOT SOURCE OF TRUTH` banner.
