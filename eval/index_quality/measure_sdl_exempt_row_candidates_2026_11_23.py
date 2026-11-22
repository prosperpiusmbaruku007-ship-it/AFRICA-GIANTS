# -*- coding: utf-8 -*-
"""R15 length/wording measurement for the REVISED consolidated SDL exemption row (sdl_exemption_categories). The first draft is 291 characters and ranked 3 for its authored question; this measures the DEPLOYED (old) row and shorter candidates, against the
FULL prospective index with the other rows fixed, on the authored question AND the nat-style paraphrases (R17), so a length win on one phrasing is not mistaken for a general one.
    HF_HUB_OFFLINE=1 python eval/index_quality/measure_sdl_exempt_row_candidates_2026_11_23.py  ->  eval/results/measure_sdl_exempt_row_candidates_2026_11_23.json"""
import importlib.util, io, json, os, sys
os.environ.setdefault("HF_HUB_OFFLINE", "1"); os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(REPO, "scripts"))
import numpy as np  # noqa: E402
import precompute_rag_embeddings as pre  # noqa: E402
from sentence_transformers import SentenceTransformer  # noqa: E402

QUERIES = ["Ni waajiri gani hawalipi SDL?", "Nani amesamehewa SDL?", "SDL haitozwi kwa taasisi zipi?", "Je, shule inalipa SDL?", "Mamlaka ya maji inalipa SDL kwa vibarua wa miradi?"]
OLD = ("Waajiri/taasisi zisizolipa SDL (msamaha): idara za Serikali, mamlaka za Serikali za Mitaa, taasisi za kidiplomasia, Umoja wa Mataifa na taasisi zake, mashirika ya kimataifa ya misaada, taasisi za kidini (kwa shughuli za kiroho tu), "
       "taasisi za elimu zilizosajiliwa, mashirika ya misaada (charitable), wanafunzi wa TaESA, na waajiri wa mashambani kwa wafanyakazi wanaolima moja kwa moja.")
CANDS = {
    "A_draft_291": "Nani hatozwi SDL? Walioorodheshwa kisheria: Serikali (ruzuku), balozi, UN, misaada ya kimataifa, taasisi za dini, hisani, elimu iliyosajiliwa, halmashauri, wanafunzi wa TaESA, mashamba (wafanyakazi wa kilimo), mamlaka ya maji (vibarua wa miradi); Waziri wa Fedha anaweza kusamehe kwa Gazeti.",
    "B_short": "Nani hatozwi SDL? Serikali (ruzuku), balozi, UN, misaada ya kimataifa, dini, hisani, elimu iliyosajiliwa, halmashauri, wanafunzi wa TaESA, mashamba, mamlaka ya maji (vibarua); Waziri wa Fedha anaweza kusamehe kwa Gazeti.",
    "C_shorter": "Nani hatozwi SDL? Serikali (ruzuku), balozi, UN, misaada, dini, hisani, shule, halmashauri, TaESA, mashamba, mamlaka ya maji; Waziri wa Fedha anaweza kusamehe kwa Gazeti.",
}

def main():
    texts, keys, _ = pre.build_fact_texts()
    i = keys.index("sdl_exemption_categories")
    model = SentenceTransformer(pre.EMBED_MODEL)
    def ranks(row_text):
        t = list(texts); t[i] = row_text
        emb = model.encode([f"passage: {x}" for x in t], batch_size=16, normalize_embeddings=True)
        q = model.encode([f"query: {x}" for x in QUERIES], normalize_embeddings=True)
        out = []
        for qi in range(len(QUERIES)):
            order = np.argsort(-(emb @ q[qi]))
            out.append(int(np.where(order == i)[0][0]) + 1)
        return out
    res = {"old_deployed": {"chars": len(OLD), "ranks": ranks(OLD)}}
    for k, v in CANDS.items():
        res[k] = {"chars": len(v), "ranks": ranks(v)}
    print(json.dumps({"queries": QUERIES, **res}, ensure_ascii=False, indent=1))
    io.open(os.path.join(REPO, "eval", "results", "measure_sdl_exempt_row_candidates_2026_11_23.json"), "w", encoding="utf-8").write(json.dumps({"queries": QUERIES, **res}, ensure_ascii=False, indent=1))

main()
