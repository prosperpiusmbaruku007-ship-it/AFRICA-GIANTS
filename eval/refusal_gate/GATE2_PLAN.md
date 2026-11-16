# Gate 2 — the plan (approved by the founder 2026-11-16, with one change: the set is authored by a person other than the assistant)

**Not built, and not to be built before the set exists: any new refusal mechanism.** Five designs are dead (absolute score, margin, re-ranked index, term overlap, the coverage gate); each
was chosen because a signal was lying around, and none was ever shown to separate right answers from wrong ones. The order below is the whole point.

1. **A frozen held-out set, authored by someone else, committed alone BEFORE anything is measured.** Instructions and the shape validator: `heldout/AUTHORING_INSTRUCTIONS.md`,
   `heldout/heldout_outofscope_TEMPLATE.jsonl`, `validate_heldout_set.py` (≥ 60 out-of-scope + ≥ 30 in-scope control rows, ≥ 8 per axis, ≤ 3 per topic, the assistant never the author).
   The assistant writes no question, no answer key and no edit. `--freeze` pins the file's sha256; a test fails if the bytes ever change.
2. **First measurement = the full production path** (classifier + retrieval + model, the thing a participant meets), reported as three numbers that are never blended:
   *leak rate* (out-of-scope questions the classifier does not intercept), *model refusal rate on the leaks*, and *wrongful-refusal rate on the in-scope controls*. With Wilson intervals;
   at n = 60/30 the interval is wide and the report says so.
3. **Hedging versus refusing is evaluated ONLY on that set** and only after (2): on the leaks, compare the current refusal copy with a hedge ("this is outside what CHIKE covers — confirm with
   <authority>"). The hedge costs far less when it is wrong than a wrongful refusal, which is invisible to us (a refused real question looks exactly like a question nobody asked).
   The decision metric is wrongful-refusal on the controls, not refusal on the OOC rows.
4. **The set is burned once its results are read.** Reading the failures turns every later rule into a fit to this set. A second iteration of any mechanism needs a NEW set from a new author.
5. **What this does not settle:** which phrasings real users produce is a traffic-frequency claim no offline set can establish; the pilot transcripts are the only evidence for it. The set measures
   coverage of the mechanism, not realism, and the report states who wrote it and whether they had seen system output (`seen_system_output`).
