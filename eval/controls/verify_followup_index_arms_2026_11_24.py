# -*- coding: utf-8 -*-
"""SUPPLEMENT to verify_followup_deploy_live_2026_11_24.py: its two INDEX arms did not exercise RETRIEVAL (one was split by the decomposer so part 1 reached the medical statement; the other routed to the sdl_base statement), so the NEW index rows (218 the SDL base, 219 medical VAT) were not
shown to be served through the fact path. These are SINGLE-SENTENCE phrasings that each carry a veto word (a medicine word, NSSF, PAYE) so they MUST fall to the fact path. Offline each is asserted NOT to reach a statement route; live, EVERY reply is READ and `served_rows` (the facts retrieval handed the model) is recorded, so the question 'was row 218/219 in context' is answered by the artifact, not inferred.
COMMITTED BEFORE ITS RUN (R18). Artifact written atomically after EVERY row, errors captured, resume re-derives.

    EXPECT_BUILD=<sha> python eval/controls/verify_followup_index_arms_2026_11_24.py   ->  eval/results/followup_index_arms_live_2026_11_24.json"""
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import atomic_artifact  # noqa: E402
REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, REPO)
OUT = os.path.join(REPO, "eval", "results", "followup_index_arms_live_2026_11_24.json")
ROW218 = "posho zote (safari, malazi, burudani)"
ROW219 = "Huduma za afya ni msamaha zikitolewa"
QS = [
    ("MED", "Huduma za afya na dawa zinatozwa VAT?", ROW219),
    ("MED", "Hospitali ya binafsi inauza dawa na pia inatoa huduma za afya, VAT inahusu mauzo gani?", ROW219),
    ("MED", "Kliniki yangu inatoa huduma za afya na inauza vifaa tiba, je VAT inatozwa?", ROW219),
    ("BASE", "Posho za safari na malazi zinaingia kwenye SDL na pia kwenye NSSF?", ROW218),
    ("BASE", "Je, posho ya nyumba ni sehemu ya msingi wa SDL na wa NSSF?", ROW218),
    ("BASE", "Bonasi na kamisheni zinahesabiwa kwenye SDL, na PAYE inakokotolewa kwa msingi gani?", ROW218),
]


def main():
    from chike import routing
    for arm, q, _ in QS:
        assert routing.fixed_statement_topic(q) is None, f"{q!r} reaches a statement route offline: it would not exercise retrieval"
    import modal
    m = modal.Cls.from_name("chike-inference", "ChikeModel")()
    art = json.load(open(OUT, encoding="utf-8")) if os.path.exists(OUT) else {"identity": None, "rows": []}
    art["rows"] = [r for r in art["rows"] if "error" not in r]
    done = {r["q"] for r in art["rows"]}
    save = lambda: atomic_artifact.write_json(OUT, art, ensure_ascii=False, indent=1)
    if not art.get("identity"):
        art["identity"] = m.served_index_identity.remote()
        save()
    print("served identity:", {k: art["identity"].get(k) for k in ("build", "rag_rows_loaded")})
    for arm, q, anchor in QS:
        if q in done:
            continue
        try:
            out = m.run.remote(q)
            facts = out.get("facts") or out.get("served_facts") or []
            row = dict(arm=arm, q=q, reply=out.get("reply", ""), path=out.get("answer_path") or out.get("path"), model_calls=out.get("model_calls"), guards=out.get("guards"),
                       anchor=anchor, anchor_in_served_context=any(anchor in str(f) for f in facts), n_served_facts=len(facts), served_heads=[str(f)[:70] for f in facts][:6])
        except Exception as e:                                                 # noqa: BLE001
            row = dict(arm=arm, q=q, error=repr(e)[:300])
        art["rows"].append(row)
        save()
        print(f"[{'ERR' if 'error' in row else 'ok '}] {arm} path={row.get('path')} calls={row.get('model_calls')} anchor_in_context={row.get('anchor_in_served_context')} | {q[:70]!r}")
    bad = [r for r in art["rows"] if "error" in r]
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
