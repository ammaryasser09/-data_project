# RAG package — `09_Application/rag/`

Retrieval, prompt and reference tools for the Nile Pearl voice agent. Run everything from
the project root.

```
speech (Whisper) → text → retriever.search() → prompt.build_messages() → LLM (+ tools) → text → TTS
```

| File | What it does |
|---|---|
| `retriever.py` | `HybridRetriever(mode='bm25'|'dense'|'hybrid')`. Searches the KB chunks **and** the answered FAQ questions (train split, all 5 languages); fuses 2–4 rankings with reciprocal-rank fusion; returns the top documents, their best chunks, similar answered questions, and an `out_of_scope` flag. |
| `text.py`, `bm25.py` | BM25 with Arabic normalisation (أ/إ/آ→ا, ى→ي, ة→ه, no tashkeel), so Egyptian and MSA spellings meet. |
| `embedder.py` | `BAAI/bge-m3` via sentence-transformers, embeddings cached in `index/`. `'hashing'` is an offline smoke test only. |
| `prompt.py` | The system prompt (language/dialect, facts only from context, tools for live data, identity check, voice style, escalation, emergencies) and `build_messages()`. |
| `tools.py` | Read-only reference tools over the CSVs + `TOOL_SCHEMAS` for function calling: availability, booking lookup with identity check, cancellation quote, late check-out quote, discount code, loyalty, menu, room-service quote, escalation. |
| `evaluate.py` | Recall@1/3/5 and MRR per language on the held-out test split, plus an "unseen fact" subset; `--realistic` runs the 200-question Egyptian set. |
| `demo.py` | Prints what the LLM would receive for one question. |

## Why the FAQ index

The KB is English; callers speak Egyptian Arabic. Lexically an Arabic question cannot meet an
English document. The FAQ index holds answered questions in every language, each pointing to
its source document, so an Egyptian question meets an Egyptian question. BM25 results
(`07_Audits/Final/retrieval_results_v4.txt`), Recall@5:

| | KB only | KB + FAQ index |
|---|---|---|
| Arabic (test split) | 0.008 | 0.450 |
| Egyptian (test split) | 0.024 | 0.476 |
| Realistic Egyptian set | 0.043 | 0.583 |

Next step for the team: run `--mode hybrid` with BGE-M3 (needs internet once). If Arabic
stays well below English, add an Arabic translation of the KB as a third index.

## Rules the tools enforce

- "Today" is `SYSTEM_DATE` (06_Scripts/config.py).
- A booking is shown only when the reference matches the last name (English or Arabic) or the
  last four phone digits (`reservation_security.txt`).
- Occupancy uses `blocks_inventory` only; capacity counts children (RULE A).
- Tools never write. The backend performs bookings, changes and cancellations after the agent
  has quoted the cost and the caller has said yes.
