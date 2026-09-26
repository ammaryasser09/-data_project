# 03_Candidate — intake for new FAQ data

New rows go here first, never straight into Gold.

1. Write the new rows as a CSV with the same columns as `04_Gold/hotel_faq_gold.csv`
   (without `faq_id`; ids are assigned on merge). For Egyptian rows, `answer` holds the
   MSA ground truth and `answer_egyptian` the dialect reply.
2. Run `python3 06_Scripts/build/merge_candidate.py`. It applies the six Gold gates —
   structural, metadata, source, language, duplicate, ground truth (prices must exist in
   the database) — and merges only if every row passes.
3. On success the candidate file is deleted: its rows now live in Gold.
4. Rebuild the derived files: `python3 06_Scripts/rebuild_all.py`.

The v3 additions (268 Egyptian rows, 44 core-language rows) came through this path; their
source is `06_Scripts/generation/faq_additions_v3.py`.
