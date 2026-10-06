# -*- coding: utf-8 -*-
"""CHOOSE ROW 57'S REPLACEMENT TEXT BY MEASUREMENT, NOT BY DRAFTING.

Row 57 asserted a FABRICATED TZS 11,000,000 EFD turnover threshold (TAA Cap.438 R.E.2023 s.44
sets none; re-verified 2026-08-29). The correctness fix is not in doubt. What IS in doubt is the
rank, and the comment that stood above the row said so in advance: adding the applicability
correction "tipped eval_347 out of top-3".

It was right. The first rewrite measured REGRESSED -- the old (wrong) row won eval_347's query
on the deployed index at rank 1, and the corrected draft fell out of the top 3 entirely, losing
to the two `Kizingiti cha kusajili VAT: mauzo ya TZS ...` rows. That is the hijack the original
comment described, re-appearing the moment the row stopped being short and dense.

⛔ SO THE TRADE IS REAL AND MUST BE RESOLVED, NOT CHOSEN. "Correct but unretrievable" is not a
fix: eval_347 asks a false-premise question, and if the corrected row does not win it, the
answer comes from a VAT row that will confirm a 200M figure. The old state served a fabrication;
a bad fix would serve a DIFFERENT wrong answer with a clean conscience.

R15's lever is ask-alignment, so the candidates below vary ONE thing -- how densely the row
carries the asker's own tokens near the front -- while all of them state the same correct
content. Measured against the real prospective index with the production builder, patched one
row at a time.

Every candidate is also checked for the two collisions that would block the regen:
  - it must NOT contain 'HAKUNA kizingiti cha mauzo' (efd_not_every_business's committed anchor,
    used by two guards)
  - its own new anchor must resolve to exactly one row
"""
import importlib.util
import json
import os
import sys

import numpy as np

os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(REPO, "eval", "results", "row57_candidates.json")

# eval_347 VERBATIM, from eval/accuracy_gate/eval_questions_003.jsonl. Never a paraphrase: the
# regen's own notes record a 2-vs-17 rank swing between a guard's phrasing and the verbatim
# gate text, so a candidate chosen on a paraphrase proves nothing about the row that ships.
QUERY = ("query: Kizingiti cha kuanza kutumia EFD ni mauzo ya TZS 200,000,000, sivyo?")

# The second query that must not break: nat_26's genuine VAT-registration question. The old
# comment warned that this row's 200M tokens risk displacing the real VAT fact, and that risk
# is unchanged by correcting the figure.
VAT_QUERY = "query: Kizingiti cha kusajili VAT ni mauzo ya kiasi gani kwa mwaka?"
VAT_ANCHOR = "Kizingiti cha kusajili VAT: mauzo ya TZS 200,000,000"

FORBIDDEN_SUBSTRING = "hakuna kizingiti cha mauzo"      # another guard's committed anchor

CANDIDATES = {
    "A_shipped_draft_too_long": (
        'Kizingiti cha kuanza kutumia mashine ya EFD: HAKITUMIKI — EFD haina kizingiti cha '
        'mauzo hata kidogo. Mashine ya risiti inahitajika kwa DEFAULT kwa kila anayeuza bidhaa '
        'au kutoa huduma, bila kujali mauzo. Msamaha hutolewa TU kwa tangazo rasmi la Kamishna '
        'Mkuu linalotaja jina lako au kundi lako. SI TZS 11,000,000 — kiwango hicho si cha EFD '
        'kabisa. Na SI TZS 200,000,000 — hiyo ni kizingiti cha kusajili VAT, si EFD.'),
    "B_short_negation_first": (
        'Kizingiti cha kuanza kutumia mashine ya EFD: EFD haina kizingiti cha mauzo. SI TZS '
        '200,000,000 — hiyo ni kizingiti cha kusajili VAT, si EFD. Na SI TZS 11,000,000. '
        'Mashine ya risiti inahitajika kwa kila mfanyabiashara bila kujali mauzo.'),
    "C_mirrors_old_shape": (
        'Kizingiti cha kuanza kutumia mashine ya EFD: HAKUNA — EFD haina kizingiti cha mauzo '
        'kwa mwaka. SI TZS 200,000,000 (hiyo ni kizingiti cha kusajili VAT, si EFD) na SI TZS '
        '11,000,000. Biashara zote hutumia EFD bila kujali kiwango cha mauzo.'),
    "D_shortest": (
        'Kizingiti cha kuanza kutumia mashine ya EFD: EFD haina kizingiti cha mauzo kwa mwaka. '
        'SI TZS 200,000,000 — hiyo ni kizingiti cha kusajili VAT, si EFD. Na SI TZS 11,000,000.'),
}

NEW_ANCHOR = "EFD haina kizingiti cha mauzo"


def main():
    path = os.path.join(REPO, "scripts", "precompute_rag_embeddings.py")
    spec = importlib.util.spec_from_file_location("precompute_rag_embeddings", path)
    pre = importlib.util.module_from_spec(spec)
    sys.modules["precompute_rag_embeddings"] = pre
    spec.loader.exec_module(pre)

    texts, keys, _ = pre.build_fact_texts()
    idx = keys.index("efd_threshold_tzs_11m")
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer(pre.EMBED_MODEL)

    def rank_of(all_texts, query, needle):
        emb = model.encode([f"passage: {t}" for t in all_texts], batch_size=16,
                           show_progress_bar=False, convert_to_numpy=True)
        emb = emb / (np.linalg.norm(emb, axis=1, keepdims=True) + 1e-10)
        q = model.encode([query], convert_to_numpy=True)[0]
        q = q / (np.linalg.norm(q) + 1e-10)
        order = np.argsort(emb @ q)[::-1]
        r = next((n for n, i in enumerate(order, 1)
                  if needle.lower() in all_texts[i].lower()), None)
        return r, [all_texts[i][:95] for i in order[:3]]

    rows = []
    for name, text in CANDIDATES.items():
        trial = list(texts)
        trial[idx] = text
        collides = FORBIDDEN_SUBSTRING in text.lower()
        anchor_rows = [i for i, t in enumerate(trial) if NEW_ANCHOR.lower() in t.lower()]
        r_efd, top_efd = rank_of(trial, QUERY, NEW_ANCHOR)
        r_vat, top_vat = rank_of(trial, VAT_QUERY, VAT_ANCHOR)
        rows.append({
            "candidate": name,
            "chars": len(text),
            "eval_347_rank": r_efd,
            "eval_347_in_top3": bool(r_efd and r_efd <= 3),
            "eval_347_top3": top_efd,
            "vat_query_rank": r_vat,
            "vat_query_in_top3": bool(r_vat and r_vat <= 3),
            "anchor_unique": len(anchor_rows) == 1,
            "anchor_rows": anchor_rows,
            "collides_with_other_guard_anchor": collides,
            "text": text,
        })
        print(f"  [{name}] chars={len(text):4d}  eval_347 rank={r_efd}  "
              f"vat rank={r_vat}  anchor_unique={len(anchor_rows) == 1}  "
              f"collides={collides}")

    # The deployed baseline, for the comparison that matters: the OLD row won at rank 1 with a
    # FABRICATED figure. Any candidate must be judged against that, not against zero.
    deployed = json.load(open(os.path.join(REPO, "kaggle", "rag_facts_text.json"),
                              encoding="utf-8"))
    r_old, _ = rank_of(deployed, QUERY, "milioni kumi na moja")

    ok = [r for r in rows if r["eval_347_in_top3"] and r["vat_query_in_top3"]
          and r["anchor_unique"] and not r["collides_with_other_guard_anchor"]]
    payload = {
        "_what": "Candidate texts for index row 57, measured against the real prospective "
                 "index with the production builder.",
        "_why": "The first corrected draft measured REGRESSED on eval_347 -- the old, WRONG row "
                "won that query at rank 1 and the corrected draft fell out of the top 3, losing "
                "to the two VAT-registration rows. 'Correct but unretrievable' is not a fix "
                "here: eval_347 is a false-premise question, so if the corrected row does not "
                "win it the answer comes from a VAT row that will confirm a 200M figure.",
        "_deployed_baseline": {
            "old_row_rank_on_eval_347": r_old,
            "note": "the OLD row won this query with the FABRICATED 'milioni kumi na moja'. "
                    "That is the rank a candidate has to match, and it is why the trade had to "
                    "be resolved rather than accepted.",
        },
        "_queries": {"eval_347_verbatim": QUERY, "vat_displacement_guard": VAT_QUERY},
        "candidates": rows,
        "passing": [r["candidate"] for r in ok],
    }
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
    print(f"\nold (wrong) row's rank on this query, deployed: {r_old}")
    print(f"passing candidates: {payload['passing']}")
    print(f"wrote {OUT}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
