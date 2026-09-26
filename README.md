# HotelAI — Nile Pearl Hotel

Data foundation and RAG code for an Egyptian-Arabic voice customer-service agent.
The hotel and all data are synthetic but modelled on Cairo 5-star hotels. The data is a
snapshot at **SYSTEM_DATE = 2026-09-19** (`06_Scripts/config.py`) — use it as "today" in
development, not the machine clock.

## Verify

```bash
python3 06_Scripts/rebuild_all.py                          # full pipeline → 9/9 gates → READY FOR DEVELOPMENT
python3 -m 09_Application.rag.evaluate --mode bm25          # retrieval per language, no downloads
pip install sentence-transformers
python3 -m 09_Application.rag.evaluate --mode hybrid        # BM25 + BGE-M3 — the target setup
python3 -m 09_Application.rag.demo "لو لغيت الحجز هيتخصم مني كام؟" --show-prompt
```

## Start here

1. `07_Audits/Final/V4_AUDIT_REPORT.md` — what changed in v4 and why (Egyptian summary first)
2. `09_Application/rag/README.md` — how the retriever, prompt and tools fit together
3. `01_Docs/DATA_ROUTING_MATRIX.md` — RAG vs database vs tool vs escalation, per request
4. `01_Docs/BUSINESS_RULES.md` — RULES A–U and the hotel's commercial terms
5. `01_Docs/SOURCE_OF_TRUTH.md` — one authoritative file per category, with row counts

## Contents at a glance

| | |
|---|---|
| Knowledge base | 44 English documents → 146 RAG chunks |
| Gold FAQ | 3,965 rows — English, Arabic, French, Russian + 385 Egyptian Arabic, 35 intents |
| Conversations | 630 — 126 each in English, Arabic, French, Russian, Egyptian Arabic |
| Database | 17 tables — 20,000 bookings and payments, 10,000 customers, 150 rooms, menu, fees, loyalty |
| Realistic test set | 200 Egyptian questions in 10 categories with routes and expected facts |
| Review workbook | Egyptian text for the team's native check |
