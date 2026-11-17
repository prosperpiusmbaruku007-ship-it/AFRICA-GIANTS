# -*- coding: utf-8 -*-
"""APPLY THE FOUNDER-APPROVED GOLD-KEY TAIL CORRECTIONS (2026-11-17) AND SCORE OLD BESIDE NEW.

  eval_115, 118, 119, 125, 135   the key's closing "Thibitisha na PKF Eastern Africa / VELMA Law" names practitioner firms as the authority to confirm with (D-FIDELITY-18). The tail becomes
                                 "Thibitisha na Ofisi ya Kazi (kazi.go.tz) au TanzLII." (and its English twin). The SUBSTANCE of each key is unchanged; `source_url` stays on the practitioner page (R6: the eval
                                 family's provenance is the page the substance came from -- the tail was the only place it was also posed as the authority a user should ask).
  eval_119                       ALSO the conflation "(madini/nishati ya kimataifa)" for TZS 765,900. READ FROM THE ORDER (data/source_documents/labour/gn605a_2025_kazi_go_tz_official.pdf, GN No. 605A,
                                 13/10/2025, edition asserted via assert_edition first): ENERGY sector, international companies: monthly 765,900 (daily 29,458 x 26 = 765,908); MINING and prospecting minerals: monthly
                                 695,000 (daily 26,731 x 26 = 695,006). The key now says so. The "karibu TZS 175,000" LOW end is NOT touched (see `floor_note`).

Only the five rows change; every other line is byte-identical. The OLD key of each row is kept in the row's `_scoring_key_correction` (history is never deleted). Idempotent. Writes
eval/results/gold_key_tails_2026_11_17.json: old and new keys, and each row scored under BOTH on the stored replies of the last two gates (regex), plus --judge to re-judge ONLY these five rows (old and new
key, majority-of-5, the project's pinned judge).

    python eval/controls/apply_key_tails_2026_11_17.py [--judge]
"""
import io
import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, "scripts"))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from chike import scoring                                                    # noqa: E402

DATE = "2026-11-17"
F1 = "eval/accuracy_gate/eval_questions_001.jsonl"
GN = "data/source_documents/labour/gn605a_2025_kazi_go_tz_official.pdf"
TAIL_SW = "Thibitisha na Ofisi ya Kazi (kazi.go.tz) au TanzLII."
TAIL_EN = "Confirm with the Labour Office (kazi.go.tz) or TanzLII."
BASIS = ("D-FIDELITY-18: a practitioner firm is not the authority a user confirms with; tail now the Labour Office (kazi.go.tz) and TanzLII, the two whitelisted hosts for GN 605A. Substance unchanged.")
BASIS_119 = (" eval_119 ALSO: the parenthetical '(madini/nishati ya kimataifa)' after TZS 765,900 conflated two sectors. GN 605A (kazi.go.tz official copy, edition asserted; read 2026-11-17): energy / international "
             "companies monthly 765,900 (daily 29,458 x 26 = 765,908); mining and prospecting minerals monthly 695,000 (daily 26,731 x 26 = 695,006). The served index (rows 74-75) already states it correctly.")
FLOOR_NOTE = ("NOT CHANGED, recorded: the key's low end 'karibu TZS 175,000' is the default for sectors the Order does not specify; the lowest monthly rate in the Order is TZS 80,000 (Domestic Work, 4(d) other "
              "domestic workers; read 2026-11-17). Left for a separate decision.")
OLD_FIELDS = ("correct_answer_sw", "correct_answer_en")


def _swap(text, old_tail, new_tail):
    assert text.rstrip().endswith(old_tail), (text[-90:], old_tail)
    return text.rstrip()[: -len(old_tail)] + new_tail


# (old tail sw, old tail en) per row; the body of each key is edited in code from the live row so the rest stays byte-identical
OLD_TAILS = {
    "eval_115": ("Thibitisha na PKF Eastern Africa au VELMA Law.", "Confirm with PKF Eastern Africa or VELMA Law."),
    "eval_118": ("Thibitisha na PKF Eastern Africa.", "Confirm with PKF Eastern Africa."),
    "eval_119": ("Thibitisha na VELMA Law au PKF.", "Confirm with VELMA Law or PKF."),
    "eval_125": ("Thibitisha na PKF Eastern Africa au VELMA Law.", "Confirm with PKF Eastern Africa or VELMA Law."),
    "eval_135": ("Thibitisha na VELMA Law au PKF.", "Confirm with VELMA Law or PKF."),
}
OLD_119_SW = "TZS 765,900 (madini/nishati ya kimataifa)."
NEW_119_SW = "TZS 765,900 (nishati, kampuni za kimataifa); madini na utafutaji wa madini ni TZS 695,000."
OLD_119_EN = "TZS 765,900 (international mining/energy)."
NEW_119_EN = "TZS 765,900 (energy, international companies); mining and prospecting minerals is TZS 695,000."


def new_key(rid, r):
    sw, en = r["correct_answer_sw"], r["correct_answer_en"]
    if rid == "eval_119":
        assert OLD_119_SW in sw and OLD_119_EN in en
        sw = sw.replace(OLD_119_SW, NEW_119_SW)
        en = en.replace(OLD_119_EN, NEW_119_EN)
    o_sw, o_en = OLD_TAILS[rid]
    return {"correct_answer_sw": _swap(sw, o_sw, TAIL_SW), "correct_answer_en": _swap(en, o_en, TAIL_EN)}


def edit():
    from check_source_editions import assert_edition
    assert_edition(os.path.join(REPO, GN), "GN No. 605A, published 13/10/2025")
    raw = io.open(os.path.join(REPO, F1), encoding="utf-8", newline="").read()
    out, done = [], {}
    for ln in raw.splitlines(keepends=True):
        body = ln.rstrip("\r\n")
        eol = ln[len(body):]
        try:
            r = json.loads(body) if body.strip() else None
        except ValueError:
            r = None
        if r and r.get("id") in OLD_TAILS:
            rid = r["id"]
            corr = r.get("_scoring_key_correction")
            old = {k: r.get(k) for k in OLD_FIELDS}
            if isinstance(corr, dict) and corr.get("date") == DATE:
                out.append(ln)
                done[rid] = ("already applied", corr["old"], old)
                continue
            fields = new_key(rid, r)
            new = dict(r)
            new.update(fields)
            entry = {"date": DATE, "what_changed": "founder-approved gold-key tail correction" + (" + sector conflation" if rid == "eval_119" else ""),
                     "basis": BASIS + (BASIS_119 if rid == "eval_119" else ""), "old": old}
            if rid == "eval_119":
                entry["floor_note"] = FLOOR_NOTE
            if corr:
                entry["earlier_correction"] = corr
            new["_scoring_key_correction"] = entry
            out.append(json.dumps(new, ensure_ascii=False) + eol)
            done[rid] = ("applied", old, fields)
        else:
            out.append(ln)
    io.open(os.path.join(REPO, F1), "w", encoding="utf-8", newline="").write("".join(out))
    assert set(done) == set(OLD_TAILS), set(OLD_TAILS) - set(done)
    return done


def L(p):
    return json.load(io.open(os.path.join(REPO, p), encoding="utf-8"))


def main():
    done = edit()
    refusal = json.load(io.open(os.path.join(REPO, "kaggle", "chike_config.json"), encoding="utf-8")).get("refusal_phrases", [])
    rows = {json.loads(l)["id"]: json.loads(l) for l in io.open(os.path.join(REPO, F1), encoding="utf-8") if l.strip()}
    gates = {"c2143c0": L("eval/results/gate_production_c2143c0.json"), "0e11c3d": L("eval/results/gate_production_0e11c3d.json")}
    out = {"date": DATE, "applied": {k: v[0] for k, v in done.items()}, "rows": {}}
    for rid, (_st, old, new) in done.items():
        q = rows[rid]
        rec = {"question": q["question_sw"], "answer_type": q["answer_type"], "old_key": old, "new_key": new, "scores": {}}
        for gname, g in gates.items():
            row = next((x for x in g["rows"] if x["id"] == rid), None)
            if not row:
                continue
            base = {"id": rid, "answer_type": q["answer_type"]}
            rec["scores"][gname] = {"reply": row["generated"], "regex_old_key": bool(scoring.score_question({**base, **old}, row["generated"], refusal)),
                                    "regex_new_key": bool(scoring.score_question({**base, **new}, row["generated"], refusal)), "stored_judge_old_key": row.get("judge")}
        out["rows"][rid] = rec
    if "--judge" in sys.argv:
        from chike import judge
        key = os.environ.get("OPENROUTER_API_KEY", "")
        assert key, "OPENROUTER_API_KEY not set"
        for rid, rec in out["rows"].items():
            for gname, s in rec["scores"].items():
                s["judge_new_key"] = judge.judge_majority(rec["question"], rec["new_key"]["correct_answer_sw"], s["reply"], api_key=key)
                s["judge_old_key_rerun"] = judge.judge_majority(rec["question"], rec["old_key"]["correct_answer_sw"], s["reply"], api_key=key)
                io.open(os.path.join(REPO, "eval", "results", "gold_key_tails_2026_11_17.json"), "w", encoding="utf-8").write(json.dumps(out, ensure_ascii=False, indent=1))
    io.open(os.path.join(REPO, "eval", "results", "gold_key_tails_2026_11_17.json"), "w", encoding="utf-8").write(json.dumps(out, ensure_ascii=False, indent=1))
    print("applied:", out["applied"])
    for rid, rec in out["rows"].items():
        for g, s in rec["scores"].items():
            j = ""
            if "judge_new_key" in s:
                jn, jo = s["judge_new_key"], s["judge_old_key_rerun"]
                j = f" | judge old={jo.get('verdict') if isinstance(jo, dict) else jo} new={jn.get('verdict') if isinstance(jn, dict) else jn}"
            print(rid, g, "regex old/new:", s["regex_old_key"], s["regex_new_key"], "stored judge:", s["stored_judge_old_key"], j)


if __name__ == "__main__":
    main()
