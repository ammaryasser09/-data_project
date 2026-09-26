# Rule Consistency Matrix

Every cell verified by `final_audit.py` reading the actual file, not by assertion.

| Rule | Rules doc | Generator | Repair pipeline | DB validator | Availability | Knowledge Base | Gold FAQ |
|---|---|---|---|---|---|---|---|
| **A — children count toward capacity** | Y | Y | Y | Y | Y | Y | Y |
| **B — back-to-back valid, strict `<`** | Y | Y | Y | Y | Y | — | — |
| **C — no-show non-blocking, 23:59 grace** | Y | Y | Y | Y | Y | Y | Y |
| **D — status semantics** | Y | Y | Y | Y | Y | Y | — |
| **E — assignment order** | Y | Y | Y | — | — | — | — |
| **F — synthetic contact data** | Y | — | — | — | — | Y | Y |
| **I — one frozen SYSTEM_DATE** | Y | Y | Y | Y | Y | — | — |
| **J — occupancy = `blocks_inventory`** | Y | — | Y | Y | Y | — | — |
| **H, K–Q — cross-table consistency** | Y | — | Y (`repair_operational_v3.py`) | Y (checks 12–19) | — | — | — |

Cells marked `—` are components where the rule does not apply.

## Where each rule lives

| Rule | File | Line of evidence |
|---|---|---|
| A | `06_Scripts/generation/generate_bookings.py` | `assert adults + children <= cap  # RULE A` |
| A | `06_Scripts/repair/apply_business_rules.py` | `int(r['adults']) + int(r['children']) > CAP[...]` |
| A | `03_Knowledge_Base/room_policies.txt` and 3 others | "Children count toward room capacity" |
| A | Gold FAQ | 20 rows, 4 languages, intents INT023 / INT032 / INT033 |
| B | all four scripts | `co <= s or ci >= e` — strict, back-to-back free |
| C | `03_Knowledge_Base/no_show_policy.txt` | 23:59 grace period, room released |
| C | all validators | `NON_BLOCKING = {'Cancelled', 'No-show'}` |
| E | `apply_business_rules.py` | STEP 1b status → STEP 5 assignment |
| I | `06_Scripts/config.py` | `SYSTEM_DATE`, imported by every script and validator |
| J | `apply_business_rules.py` STEP 11 | `blocks_inventory` written; read by `validate_availability.py`, `validate_database.py`, `final_audit.py` |
| H, K–Q | `repair_operational_v3.py` | one section per rule, each change logged in `repair_log_v3.csv` |

No conflicting implementation of any rule was found in the repository.
