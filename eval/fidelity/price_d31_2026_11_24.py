"""PRICE D-FIDELITY-31 (a money figure in a compute body that no engine produced and no one-step arithmetic reaches) over every stored reply that has a body AND a working, and over every GOLD answer that routes to compute, BEFORE it is wired (R22, R25).
Founder's condition (2026-11-24): wire ONLY with 0 gold flags and every flag read; otherwise report and do not wire. A hit in GOLD is the alarm. The founding specimen (the live SDL+NSSF compute reply, TZS 150,000) MUST flag or the run exits 1 (R26).
The population and the sentinel split are the memo's (scope_render_body_working_disagreement_2026_10_10.py), IMPORTED rather than re-implemented (R24: a harness that re-derives the real thing prices a paraphrase); the artifact list is extended with the newer live runs.

    python eval/fidelity/price_d31_2026_11_24.py  ->  eval/results/price_d31_2026_11_24.json
"""
import glob
import importlib.util
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, REPO)
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from chike import fidelity  # noqa: E402
from chike.model_abstraction import FakeBackend  # noqa: E402
from chike.orchestrator import Orchestrator  # noqa: E402

spec = importlib.util.spec_from_file_location("_scope", os.path.join(HERE, "scope_render_body_working_disagreement_2026_10_10.py"))
scope = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scope)
scope.REPLY_ARTIFACTS = scope.REPLY_ARTIFACTS + [
    "eval/results/gate_production_c2143c0.json", "eval/results/sdl_three_routes_live_2026_11_23.json", "eval/results/ten_more_statements_live_2026_11_23.json",
    "eval/results/batch4_deploy_live_2026_11_18.json", "eval/results/sdl_nssf_deploy_live_2026_11_23.json", "eval/results/d25_deploy_live_2026_11_22.json"]
SENT = scope.SENTINEL
SPECIMEN_Q = "Nina wafanyakazi 15 na mishahara jumla TZS 6,000,000 kwa mwezi. SDL na NSSF ni kiasi gani?"


def working_of(q):
    """The deterministic workings of the request (every sub-answer's), derived by the REAL orchestrator with a sentinel body."""
    local = Orchestrator(backend=FakeBackend(scripted_reply=SENT), retriever=lambda _q: []).answer(q)
    text = local.text or ""
    return text if SENT in text else None, text


def main():
    rows = scope._stored_replies()
    assert len(rows) >= 300, len(rows)
    pairs, moved = [], 0
    for r in rows:
        try:
            has, text = working_of(r["question"])
        except Exception:                                                      # noqa: BLE001
            moved += 1
            continue
        if not has:
            continue
        stored = scope._norm(r["reply"])
        w = scope._norm(text.split(SENT, 1)[1]) if SENT in text else ""
        if not w or not stored.endswith(w):
            moved += 1
            continue
        pairs.append({**r, "body": scope._norm(stored[:len(stored) - len(w)]), "workings": scope._norm(text.replace(SENT, " "))})
    # the founding specimen: the live reply, VERBATIM, with the workings the engine derives for its question
    live = json.load(io.open(os.path.join(REPO, "eval", "results", "sdl_three_routes_live_2026_11_23.json"), encoding="utf-8"))
    live = live.get("rows") or live
    spec_reply = next(x["reply"] for x in live if "SDL na NSSF ni kiasi gani" in (x.get("question") or x.get("q") or ""))
    _, spec_text = working_of(SPECIMEN_Q)
    spec_hits = fidelity.unproduced_figures(SPECIMEN_Q, spec_reply, scope._norm(spec_text.replace(SENT, " ")) + " " + spec_reply.split("\n")[-1])
    spec_flags_150 = any(a == 150000 for a, _ in spec_hits)
    print("founding specimen flags 150,000:", spec_flags_150, [a for a, _ in spec_hits])
    stored_flags = [{"src": p["source"], "id": p["id"], "q": p["question"][:140], "unproduced": [[a, s[:200]] for a, s in fidelity.unproduced_figures(p["question"], p["body"], p["workings"])]}
                    for p in pairs if fidelity.unproduced_figures(p["question"], p["body"], p["workings"])]
    gold_flags, gold_checked = [], 0
    for path in sorted(glob.glob(os.path.join(REPO, "eval", "accuracy_gate", "*.jsonl")) + glob.glob(os.path.join(REPO, "eval", "refusal_gate", "*.jsonl"))):
        for n, line in enumerate(io.open(path, encoding="utf-8"), 1):
            if not line.strip():
                continue
            try:
                o = json.loads(line)
            except ValueError:
                continue
            q = o.get("question_sw") or o.get("question") or ""
            gold = next((o[k] for k in ("correct_answer_sw", "expected_answer_sw", "answer_sw", "gold_sw") if isinstance(o.get(k), str) and o[k].strip()), "")
            if not q or not gold:
                continue
            try:
                has, text = working_of(q)
            except Exception:                                                  # noqa: BLE001
                continue
            if not has:
                continue
            gold_checked += 1
            hits = fidelity.unproduced_figures(q, gold, scope._norm(text.replace(SENT, " ")))
            if hits:
                gold_flags.append({"id": o.get("id") or f"{os.path.basename(path)}:{n}", "q": q[:140], "gold": gold[:240], "unproduced": [[a, s[:160]] for a, s in hits]})
    res = {"population": {"stored_replies": len(rows), "with_body_and_working": len(pairs), "excluded_working_moved_or_error": moved, "gold_checked": gold_checked},
           "founding_specimen_flags_150000": spec_flags_150, "stored_flags": len(stored_flags), "gold_flags": len(gold_flags),
           "stored_rows": stored_flags, "gold_rows": gold_flags,
           "decision_rule": "wire ONLY if gold_flags == 0 AND the founding specimen flags AND every stored flag has been read and is a genuine unproduced figure (or is a priced, stated, KNOWN-LIMIT two-step derivation)"}
    json.dump(res, io.open(os.path.join(REPO, "eval", "results", "price_d31_2026_11_24.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"stored: {len(rows)} replies, {len(pairs)} with a body and a working (excluded {moved}); flags {len(stored_flags)}")
    print(f"gold: {gold_checked} answers route to compute; GOLD FLAGS {len(gold_flags)}")
    for x in stored_flags:
        print("  STORED", x["src"].split("/")[-1], x["id"], "|", x["q"][:70], "|", x["unproduced"])
    for x in gold_flags:
        print("  GOLD", x["id"], "|", x["q"][:70], "|", x["unproduced"])
    return 1 if not spec_flags_150 else 0


if __name__ == "__main__":
    sys.exit(main())
