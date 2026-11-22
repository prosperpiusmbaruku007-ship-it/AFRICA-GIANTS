# -*- coding: utf-8 -*-
"""RETRAIN-DECISION MEMO, evidence arm (read-only, no deploy, nothing sent to Hugging Face): for every logged MODEL-class error, what does the CURRENT code do with the model reply that was logged?

Method (offline, no GPU): the real `Orchestrator` with a STUB backend that returns the STORED raw model reply for every model call it makes, a stub retriever, and production's OOC/in-scope phrase lists. Each row is classified by what the
current code does with it:
  ROUTE    -- the question now reaches a model-free route (`model_calls == 0`): the stored reply is never produced again
  GUARD    -- the question still reaches the model, and a guard changed or replaced the stored reply (`guards` non-empty and the text differs)
  OPEN     -- the question still reaches the model and the stored reply comes out UNCHANGED: nothing covers it
  REFUSED  -- the OOC list refuses it
POPULATION AND ITS LIMITS (R22): (1) the 26 MODEL rows of the c2143c0 gate adjudication (eval/results/gate_c2143c0_adjudication_2026_11_16.json) -- NOT 23: 23 is the size of that gate's false-pass QUEUE, a different population; (2) this week's
model contradictions of a served rank-1..3 row, with the reply text taken VERBATIM from the committed live artifacts. A stub that returns the same stored reply for every model call is an APPROXIMATION on the compute path (the slot extractor's model
fallback also receives it): the route and guard columns are what the code does; "OPEN" is an upper bound on what a guard would not touch, and it says nothing about whether the live model would repeat the reply (it is greedy, so it usually does, R24).
The gate's replies came from a Kaggle host (R24b); this arm never compares text across hosts for correctness, only asks what today's code does with a text.

    python eval/controls/retrain_memo_coverage_2026_11_23.py   ->  eval/results/retrain_memo_coverage_2026_11_23.json
"""
import io
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, REPO)
sys.path.insert(0, HERE)
from chike import answer_trace, classification, routing  # noqa: E402
from chike.orchestrator import Orchestrator  # noqa: E402
import atomic_artifact  # noqa: E402

OUT = os.path.join(REPO, "eval", "results", "retrain_memo_coverage_2026_11_23.json")
RES = os.path.join(REPO, "eval", "results")


class _Replay:
    def __init__(self, text):
        self.text, self.calls = text, 0

    def generate(self, prompt, params=None):
        self.calls += 1
        return self.text


def _load(name):
    with io.open(os.path.join(RES, name), encoding="utf-8") as fh:
        return json.load(fh)


def replay(question, stored_reply):
    ooc, ins = classification.resolve_phrases(classification.load_local_config())
    b = _Replay(stored_reply)
    o = Orchestrator(b, retriever=lambda q: ["f"], ooc_phrases=ooc, in_scope_phrases=ins)
    r = o.answer(question)
    t = answer_trace.trace(r)
    path, calls, guards = t.get("path"), t.get("model_calls"), list(t.get("guards") or [])
    text = r.text or ""
    if r.refused and path in (None, "refusal"):
        cls = "REFUSED"
    elif calls == 0:
        cls = "ROUTE"
    elif guards and text.strip() != (stored_reply or "").strip():
        cls = "GUARD"
    else:
        cls = "OPEN"
    return dict(cls=cls, path=path, model_calls=calls, guards=guards, intent=routing.detect_intent(question),
                topic=routing.fixed_statement_topic(question), now=text[:300], text_changed=text.strip() != (stored_reply or "").strip())


def main():
    adj = _load("gate_c2143c0_adjudication_2026_11_16.json")
    gate = {r["id"]: r for r in _load("gate_production_c2143c0.json")["rows"]}
    rows = []
    for rid in adj["miss_classes"]["MODEL"]["ids"]:
        g = gate[rid]
        stored = g.get("raw_generated") or g.get("generated") or ""
        out = replay(g["question_sw"], stored)
        rows.append(dict(set="GATE c2143c0 MODEL", id=rid, q=g["question_sw"], stored=stored[:300], why=adj["per_row_class"].get(rid), **out))
        print(f"{out['cls']:<8} {rid} path={out['path']} calls={out['model_calls']} guards={out['guards']} | {g['question_sw'][:80]!r}")
    # this week's contradictions of a served rank-1..3 row: VERBATIM replies from the committed live artifacts
    wk = []
    a = _load("sdl_nssf_deploy_live_2026_11_23.json")["rows"]
    b = _load("exemptions_nhif_deploy_live_2026_11_23.json")["rows"]
    c = _load("widened_exemptions_live_2026_11_23.json")["rows"]
    pick = lambda rows_, q: [r for r in rows_ if r["q"] == q][0]
    for label, rows_, q in [
        ("private-school SDL (d997d4d)", a, "Shule binafsi inalipa SDL?"),
        ("exemption list, fabricated (d997d4d)", a, "Ni waajiri gani hawalipi SDL?"),
        ("exemption category ask, non-answer (d997d4d)", a, "Nani amesamehewa SDL?"),
        ("NHIF with NSSF (d997d4d)", a, "NHIF inakatwa asilimia ngapi pamoja na NSSF kwenye mshahara?"),
        ("household SDL premises claim (d997d4d)", a, "SDL inahusu biashara tu au hata waajiri wa nyumbani?"),
        ("age-60 'huisha' (d997d4d)", a, "Kama mfanyakazi anafikisha umri wa miaka 60, je bado anatakiwa kuchangia NSSF?"),
        ("age-60 'miezi 180' (d997d4d)", a, "Michango ya NSSF inaisha ukifika miaka 60?"),
        ("mining exemption invented (56af98b)", b, "Je, kampuni ya madini lazima ilipe SDL kwa wafanyakazi wake?"),
    ]:
        r = pick(rows_, q)
        out = replay(q, r["reply"])
        wk.append(dict(set="THIS WEEK", id=label, q=q, stored=r["reply"][:300], **out))
        print(f"{out['cls']:<8} {label} path={out['path']} calls={out['model_calls']} guards={out['guards']}")
    adhabu = pick(c, "Mwajiri au mfanyakazi analipa SDL?") if any(r["q"] == "Mwajiri au mfanyakazi analipa SDL?" for r in c) else None
    if adhabu:
        out = replay(adhabu["q"], adhabu["reply"])
        wk.append(dict(set="THIS WEEK", id="'adhabu' sentence on the payer question (a8a0274)", q=adhabu["q"], stored=adhabu["reply"][:300], **out))
        print(f"{out['cls']:<8} adhabu path={out['path']} calls={out['model_calls']} guards={out['guards']}")
    allrows = rows + wk
    tally = {}
    for r in allrows:
        tally.setdefault(r["set"], {}).setdefault(r["cls"], 0)
        tally[r["set"]][r["cls"]] += 1
    art = {"harness": "eval/controls/retrain_memo_coverage_2026_11_23.py", "tally": tally, "rows": allrows,
           "limits": ["stub backend returns the stored reply for every model call (approximation on the compute path)", "OPEN is an upper bound on 'not covered'", "gate replies are from a Kaggle host (R24b)"]}
    atomic_artifact.write_json(OUT, art, ensure_ascii=False, indent=1)
    print(json.dumps(tally))


if __name__ == "__main__":
    main()
