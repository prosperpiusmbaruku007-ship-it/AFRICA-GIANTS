# -*- coding: utf-8 -*-
"""APPLY THE FOUNDER-APPROVED KEY CHANGES (2026-11-16) AND SCORE OLD BESIDE NEW.

  eval_013, eval_028  re-keyed as the HEDGED answer, never a flat "no": the VAT Act (Cap.148 R.E.2023) names no voluntary route for an existing below-threshold trader (0 occurrences of "voluntar*"); the routes it
                      names are s.28 threshold, s.29(1) professional services, s.29(2) Government entities, s.29(3) intending trader at the Commissioner General's discretion; the TRA FAQ allows voluntary registration for
                      "certain specific economic activities" and names none; confirm with TRA.
  eval_218            ITA Cap.332 R.E.2023 First Schedule para 4(b)(ii): rent paid to a non-resident withholdee -- ten percent (the old key called the non-resident rate unconfirmed).
  eval_228            MOVED to the out-of-scope set (stamp duty is a deliberate refusal, CLAUDE.md R11): subdomain out_of_corpus, answer_type out_of_corpus_refusal, house text of eval_312.

Only the four rows change; every other line of each file is byte-identical. The OLD key of each row is kept inside the row's `_scoring_key_correction` (the history is never deleted). Idempotent: a row already carrying
the 2026-11-16 correction is left alone. Writes eval/results/gold_key_corrections_2026_11_16.json (old and new, and each scored under both keys), including eval_228's gate figures under BOTH placements, once.

    python eval/controls/apply_key_changes_2026_11_16.py
"""
import io
import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO)
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from chike import scoring                                                    # noqa: E402

DATE = "2026-11-16"
F1, F2 = "eval/accuracy_gate/eval_questions_001.jsonl", "eval/accuracy_gate/eval_questions_002_additions.jsonl"
NEW = {
    "eval_013": (F1, {
        "answer_type": "definition",
        "correct_answer_sw": "Sheria ya VAT haitaji usajili wa hiari kwa mfanyabiashara aliyepo aliye chini ya kizingiti. Njia ilizotaja ni: kufikia kiwango, watoa huduma za kitaalamu, taasisi za Serikali, na anayetarajia kuanza biashara (kwa uamuzi wa Kamishna Mkuu). TRA inasema usajili wa hiari unaruhusiwa kwa shughuli maalum za kiuchumi bila kuzitaja. Thibitisha na TRA (tra.go.tz) kabla ya kuomba.",
        "correct_answer_en": "The VAT Act names no voluntary registration route for an existing trader below the threshold. The routes it names are: reaching the threshold, professional service providers, Government entities, and an intending trader (at the Commissioner General's discretion). TRA states voluntary registration is allowed for certain specific economic activities without naming them. Confirm with TRA (tra.go.tz) before applying."},
        "VAT Act Cap.148 R.E.2023 (0 occurrences of 'voluntar*'; ss.28, 29(1)-(3)); TRA FAQ (tra_faq_57_2026_11_16.html); locked fact vat_voluntary_registration. The old key asserted an unconditional 'Ndiyo' citing a KPMG URL that returns 404 and was never read."),
    "eval_028": (F1, {
        "answer_type": "definition",
        "correct_answer_sw": "Hakuna utaratibu wa usajili wa hiari ulioandikwa kwa mfanyabiashara aliyepo aliye chini ya kizingiti. Njia pekee iliyoandikwa ni mfanyabiashara anayetarajia kuanza shughuli: anawasilisha ushahidi (mikataba, zabuni, ramani za jengo, mpango wa biashara, ufadhili wa benki) na kutaja muda ambao uzalishaji wa bidhaa zinazotozwa VAT utaanza; Kamishna Mkuu ndiye anayeamua. Thibitisha na TRA (tra.go.tz).",
        "correct_answer_en": "No application procedure for voluntary registration is written for an existing trader below the threshold. The only written route is an intending trader about to commence activity: they submit evidence (contracts, tenders, building plans, a business plan, bank financing) and state the period within which taxable production will start; the Commissioner General decides. Confirm with TRA (tra.go.tz)."},
        "VAT Act Cap.148 R.E.2023 s.29(3), read 2026-11-16 (edition asserted); TRA FAQ. The old key's 4-step procedure (BRELA certificate, TIN, TRA reviews, VAT number) was the same unread KPMG claim."),
    "eval_218": (F2, {
        "answer_type": "number",
        "correct_answer_sw": "Asilimia 10 — kiwango kimoja kwa wakazi na wasio wakazi kwenye pango la kibiashara. Mlipaji lazima awe wakala wa kuzuia kodi. Thibitisha na TRA (tra.go.tz).",
        "correct_answer_en": "10% -- one rate for residents and non-residents on commercial rent. The payer must be a withholding agent. Confirm with TRA (tra.go.tz)."},
        "ITA Cap.332 R.E.2023 First Schedule para 4(b)(ii), read 2026-11-16 (edition asserted): 'interest or rent paid to a non-resident withholdee -- ten percent'; TRA withholding page 'Rental income (commercial) 10% | 10%'; locked fact rent_wht_rate. The old key said the non-resident rate was not confirmed."),
    "eval_228": (F2, {
        "subdomain": "out_of_corpus",
        "answer_type": "out_of_corpus_refusal",
        "correct_answer_sw": "Samahani, ushuru wa stempu (stamp duty) kwa Hati ya Makubaliano (Memorandum of Association) uko nje ya mada yangu na huduma yangu. Tafadhali thibitisha na TRA (tra.go.tz).",
        "correct_answer_en": "Sorry, stamp duty on a Memorandum of Association is outside my scope. Please confirm with TRA."},
        "CLAUDE.md R11 / chike_config.json: stamp duty is a deliberate refusal topic (ooc_phrases); the Stamp Duty Act is not on the source whitelist. The old key hedged a figure ('10,000 is often cited') while production refuses by design -- a design conflict, resolved by the founder 2026-11-16 by moving the row to the out-of-scope set."),
}
OLD_FIELDS = ("subdomain", "answer_type", "correct_answer_sw", "correct_answer_en")


def edit(path, changes):
    raw = io.open(os.path.join(REPO, path), encoding="utf-8", newline="").read()
    lines = raw.splitlines(keepends=True)
    out, done = [], {}
    for ln in lines:
        body = ln.rstrip("\r\n")
        eol = ln[len(body):]
        try:
            r = json.loads(body) if body.strip() else None
        except ValueError:
            r = None
        if r and r.get("id") in changes:
            rid = r["id"]
            fields, basis = changes[rid]
            old = {k: r.get(k) for k in OLD_FIELDS}
            corr = r.get("_scoring_key_correction")
            if isinstance(corr, dict) and corr.get("date") == DATE:
                out.append(ln)
                done[rid] = ("already applied", old, {k: r.get(k) for k in OLD_FIELDS})
                continue
            new = dict(r)
            new.update(fields)
            entry = {"date": DATE, "what_changed": "founder-approved key change", "basis": basis, "old": old}
            if corr:
                entry["earlier_correction"] = corr
            new["_scoring_key_correction"] = entry
            out.append(json.dumps(new, ensure_ascii=False) + eol)
            done[rid] = ("applied", old, {k: new.get(k) for k in OLD_FIELDS})
        else:
            out.append(ln)
    io.open(os.path.join(REPO, path), "w", encoding="utf-8", newline="").write("".join(out))
    return done


def L(p):
    return json.load(io.open(os.path.join(REPO, p), encoding="utf-8"))


def main():
    status = {}
    for path in (F1, F2):
        status.update(edit(path, {k: (v[1], v[2]) for k, v in NEW.items() if v[0] == path}))
    assert set(status) == set(NEW), set(NEW) - set(status)
    refusal = json.load(io.open(os.path.join(REPO, "kaggle", "chike_config.json"), encoding="utf-8")).get("refusal_phrases", [])
    gates = {"c2143c0": L("eval/results/gate_production_c2143c0.json"), "0e11c3d": L("eval/results/gate_production_0e11c3d.json")}
    out = {"date": DATE, "applied": {k: v[0] for k, v in status.items()}, "rows": {}, "eval_228_both_placements": {}}
    for rid, (st, old, new) in status.items():
        rec = {"old_key": old, "new_key": new, "scores": {}}
        for gname, g in gates.items():
            row = next((x for x in g["rows"] if x["id"] == rid), None)
            if not row:
                continue
            q_old = {"id": rid, **old}
            q_new = {"id": rid, **new}
            rec["scores"][gname] = {"reply": row["generated"][:240],
                                    "old_key": bool(scoring.score_question(q_old, row["generated"], refusal)),
                                    "new_key": bool(scoring.score_question(q_new, row["generated"], refusal)),
                                    "harness_pass_under_old_key": str(row["pass"])}
        out["rows"][rid] = rec
    # eval_013's reply AS PRODUCTION NOW SERVES IT (the model-free voluntary-VAT statement), scored under both keys
    from chike.model_abstraction import ModelBackend
    from chike.orchestrator import Orchestrator

    class _E(ModelBackend):
        def generate(self, prompt, params=None):
            return ""
    q013 = next(json.loads(l) for l in io.open(os.path.join(REPO, F1), encoding="utf-8") if json.loads(l)["id"] == "eval_013")
    served = Orchestrator(backend=_E(), retriever=lambda *a, **k: [], system_prompt="x").answer(q013["question_sw"]).text
    old013 = {"id": "eval_013", **status["eval_013"][1]}
    out["eval_013_as_served_now"] = {"reply": served[:300], "old_key": bool(scoring.score_question(old013, served, refusal)),
                                     "new_key": bool(scoring.score_question({"id": "eval_013", **status["eval_013"][2]}, served, refusal))}
    # eval_228 under BOTH placements, once, for continuity (c2143c0, regex raw; adjudication from gate_c2143c0_adjudication_2026_11_16.json)
    g = gates["c2143c0"]
    inc = [r for r in g["rows"] if r["subdomain"] != "out_of_corpus"]
    ooc = [r for r in g["rows"] if r["subdomain"] == "out_of_corpus"]
    r228 = next(r for r in g["rows"] if r["id"] == "eval_228")
    raw_pass = sum(str(r["pass"]) == "True" for r in inc)
    ref_pass_228 = bool(scoring.score_question({"id": "eval_228", "answer_type": "out_of_corpus_refusal"}, r228["generated"], refusal))
    ooc_pass = sum(str(r["pass"]) == "True" for r in ooc)
    adj = L("eval/results/gate_c2143c0_adjudication_2026_11_16.json")["tally_false_pass_queue"]
    clar = L("eval/results/clarified_policy_gate_production_c2143c0.json")
    promoted = len(clar["promoted"])
    n_old, n_new = len(inc), len(inc) - 1

    def pct(a, b):
        return round(100 * a / b, 1)
    fp, pa = adj["FALSE_PASS"], adj["PARTIAL"]
    out["eval_228_both_placements"] = {
        "as_it_was_in_corpus": {"gate1_raw": f"{raw_pass}/{n_old} = {pct(raw_pass, n_old)}%", "gate1_confirmed_false_passes_removed": f"{raw_pass - fp}/{n_old} = {pct(raw_pass - fp, n_old)}%",
                                "gate1_with_partials_removed": f"{raw_pass - fp - pa}/{n_old} = {pct(raw_pass - fp - pa, n_old)}%",
                                "gate1_raw_matching_clarification_policy": f"{raw_pass + promoted}/{n_old} = {pct(raw_pass + promoted, n_old)}%", "gate2_refusal": f"{ooc_pass}/{len(ooc)}"},
        "moved_out_of_scope": {"gate1_raw": f"{raw_pass}/{n_new} = {pct(raw_pass, n_new)}%", "gate1_confirmed_false_passes_removed": f"{raw_pass - fp}/{n_new} = {pct(raw_pass - fp, n_new)}%",
                               "gate1_with_partials_removed": f"{raw_pass - fp - pa}/{n_new} = {pct(raw_pass - fp - pa, n_new)}%",
                               "gate1_raw_matching_clarification_policy": f"{raw_pass + promoted}/{n_new} = {pct(raw_pass + promoted, n_new)}%",
                               "gate2_refusal": f"{ooc_pass + int(ref_pass_228)}/{len(ooc) + 1}", "eval_228_refusal_reply_passes": ref_pass_228, "eval_228_reply": r228["generated"][:160]},
        "note": "228 was a regex FAIL in corpus (the reply refused, the old key wanted 10,000); moved out of scope it is a refusal PASS. Gate 1 loses one miss and Gate 2 gains one pass: the in-corpus denominator shrinks 384 -> 383.",
    }
    io.open(os.path.join(REPO, "eval", "results", "gold_key_corrections_2026_11_16.json"), "w", encoding="utf-8").write(json.dumps(out, ensure_ascii=False, indent=1))
    print("applied:", out["applied"])
    for rid, rec in out["rows"].items():
        print(rid, {g: (s["old_key"], s["new_key"]) for g, s in rec["scores"].items()})
    print("eval_013 as served now (old key, new key):", out["eval_013_as_served_now"]["old_key"], out["eval_013_as_served_now"]["new_key"])
    print(json.dumps(out["eval_228_both_placements"], ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
