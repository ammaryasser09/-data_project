> **SUPERSEDED / HISTORICAL — NOT SOURCE OF TRUTH.** Kept for audit history only. Figures here describe an earlier state of the data. See `07_Audits/Final/` for the current certification.

# Review report — HotelAI_FINAL_DATASET_3461_GOLD

Independent audit of the uploaded package, treating every claim in
`FINAL_CERTIFICATION.txt` as unverified until checked against the data.

## Verified as claimed

| Claim | Result |
|---|---|
| 3,461 master rows | PASS |
| 3,461 unique IDs, FAQ1-FAQ3461 with no gaps | PASS |
| 3,461 unique questions, no duplicates | PASS |
| No empty questions or answers | PASS |
| Language balance 1.035 across the four languages | PASS |
| RAG corpus: 156 sections from 40 documents | PASS |
| Layer counts (1344 + 1008 + 96 + 864 + 100 + 49) | PASS |
| Every price quoted matches the database | PASS |

The `response_mode` and `requires_tool` columns added in this version are a genuine
improvement — they let a router decide whether a question needs the knowledge base, a tool
call, a safe refusal or a human, which the earlier structure could not express.

The `star rating` answer was also corrected here. An earlier out-of-scope row claimed the
hotel information does not state a star rating; `hotel_information.txt` does state
`5-Star Hotel`, so that correction was right and is now reflected.

## Defects found and fixed

**1. Two knowledge documents still contained room types that do not exist (CRITICAL)**

`room_types.txt` and `booking_policy.txt` carried the corrected inventory, but
`room_policies.txt` and `room_amenities.txt` still listed Standard, Superior and Executive
rooms. All four documents are in the RAG corpus, so a question about room capacity could
retrieve a passage describing rooms the hotel does not have, contradicting both the database
and the other two documents.

Both files rewritten against `data/room_types.csv` (Single, Double, Twin, Deluxe, Family,
Suite) with capacities 1 / 2 / 2 / 3 / 4 / 4.

**2. Training splits covered only 2,448 of 3,461 rows (CRITICAL)**

`05_Training_Data` was a stale snapshot taken before the coverage work was merged. It was
missing 1,013 rows: the entire transaction-path and policy coverage (864), the Egyptian
dialect layer (49), and **all 100 out-of-scope rows**. Anyone training from that folder
would have silently lost every safe-refusal example in the dataset — the exact data that
stops the system answering confidently and wrongly.

Splits rebuilt from the full master, grouped by the fact each row teaches and merged on
near-duplicate questions (Jaccard >= 0.8) so paraphrases of one fact cannot straddle the
split. Result: train 2,342 / val 577 / test 542, all 34 intents in every split, out-of-scope
and Egyptian rows present in all three, zero group or question leakage.

**3. Twenty-seven rows answered in the wrong language (HIGH)**

All from the original 1,344. Twelve Russian questions answered with
`Hotel reception operates 24/7.`, twelve with `Standard check-out time is 12:00 PM.`, one
Arabic row answered in French, and two rows labelled Russian whose questions were in French.
In a voice system this trains the model to reply to a Russian caller in English.

Answers translated into the declared language; the two French questions translated into
Russian to match their answers. Language mismatches now zero across all 3,461 rows.

## Not changed, but worth a decision

- **The room inventory decision still rests on an assumption.** The database was treated as
  authoritative because 20,000 bookings reference RT001-RT006. If the hotel's real inventory
  is Standard / Superior / Executive, the corrections run the other way.
- **`escalate_human` answers promise an action.** They say "I am escalating this now" and
  "I am logging this as a formal complaint". If the agent is not wired to
  `complaint_tickets.csv`, the system is promising something it does not do.
- **Questions remain template-generated.** Accuracy measured on this data will read higher
  than live performance. Production logs are the fix, and they only exist after launch.

## Status

The three defects above were all invisible to the certification file, which reported PASS.
Two of them would have caused real failures: contradictory retrieval answers, and training
without any safety data. With them fixed, the package is consistent and ready to build on.
