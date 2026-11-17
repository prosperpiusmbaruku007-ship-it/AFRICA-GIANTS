# -*- coding: utf-8 -*-
"""READ-ONLY PROPOSALS (2026-11-17, "propose per row, nothing edited before I approve") for the rows the first pass left:

  (1) firm-tail rows: the final "Thibitisha na <firm>" clause, in the authored sft_shaped_pairs, the export and the gold keys that scripts/repair_tail_pairs_2026_11_17.py did not cover;
  (2) every 765,900 row that attributes the rate to "madini" (mining): GN 605A (kazi.go.tz official copy, edition asserted, read 2026-11-17) gives ENERGY / international companies 765,900 and
      MINING and prospecting minerals 695,000. cleaned_pairs/ (schema-valid corpus), authored, export, gold and the eval-expectation text of nat_42.

WRITES ONLY eval/results/tail_conflation_proposals_2026_11_17.json. Nothing in datasets/ or eval/accuracy_gate/ is touched. Each row carries OLD, NEW, and the action (repair | quarantine) with the reason.

    python scripts/propose_tail_conflation_repairs_2026_11_17.py
"""
import glob
import hashlib
import io
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)
OUT = os.path.join(REPO, "eval", "results", "tail_conflation_proposals_2026_11_17.json")
BS = chr(92)
FIRM = re.compile(r"(?i)\b(PKF|VELMA|Bowmans|Clyde|KPMG|EY\b|PwC|Deloitte|Dentons|DLA Piper|Habib)")
AUTH_SW = "Ofisi ya Kazi (kazi.go.tz) au TanzLII."
AUTH_EN = "the Labour Office (kazi.go.tz) or TanzLII."
STAGES = (("cleaned", "datasets/tier1a/cleaned_pairs/*.jsonl"), ("authored_sft", "datasets/tier1a/sft_shaped_pairs/*.jsonl"), ("export", "datasets/tier1a/sft/*.jsonl"))
CONFLATION = [
    ("kwa sekta ya madini ya kimataifa na nishati", "kwa sekta ya nishati (kampuni za kimataifa)"),
    ("inayohusu sekta ya madini ya kimataifa na nishati", "inayohusu sekta ya nishati (kampuni za kimataifa)"),
    ("(madini ya kimataifa na nishati)", "(nishati, kampuni za kimataifa)"),
    ("sekta ya madini ya kimataifa na nishati peke yake", "sekta ya nishati (kampuni za kimataifa) peke yake"),
    ("Sekta ya madini ya kimataifa na nishati (international mining and energy)", "Sekta ya nishati (kampuni za kimataifa)"),
    ("Wafanyakazi wa sekta ya madini ya kimataifa wana haki", "Wafanyakazi wa sekta ya nishati (kampuni za kimataifa) wana haki"),
    ("sekta za madini ya kimataifa zinaweza kufikia", "sekta ya nishati (kampuni za kimataifa) inaweza kufikia"),
    ("for the international mining and energy sector", "for the energy sector (international companies)"),
    ("international mining/energy", "energy, international companies"),
    ("the international mining and energy sector", "the energy sector (international companies)"),
    ("international mining and energy sector", "energy sector (international companies)"),
]
# specific rewrites where the QUESTION is about mining, so the repair needs the mining figure rather than a relabel
REWRITE = {
    "Mshahara wa chini kwa sekta ya madini ya kimataifa ni Shilingi ngapi?": (
        "Kwa uchimbaji na utafutaji wa madini (mining and prospecting minerals), mshahara wa chini chini ya GN 605A ni TZS 695,000 kwa mwezi. Kiwango cha juu zaidi katika agizo lote ni TZS 765,900 kwa sekta ya nishati (kampuni za kimataifa). Viwango hivi vilianza kutumika Januari 2026. Thibitisha viwango vya subsekta yako ya madini kwenye GN 605A.",
        "For mining and prospecting minerals the GN 605A minimum wage is TZS 695,000 per month. The highest rate in the entire order is TZS 765,900, for the energy sector (international companies). These rates took effect in January 2026. Confirm your mining sub-sector's rate in GN 605A."),
}
QUARANTINE = {
    "Mshahara wa chini wa sekta ya madini ya kimataifa ni Shilingi 400,000 — je, namba hii ni sahihi?":
        "Premise-denial with a wrong figure: answers 'Hapana ... 765,900 -- si 400,000' for mining. Mining and prospecting minerals is 695,000 (the Order), and the mining sector has further sub-sector rates (primary mining licence, dealer and broker licences) that were NOT verified, so 'si 400,000' is not safe to assert; a corrected replacement is a separate authorable job.",
}
FLOOR = re.compile(r"karibu (TZS|Shilingi) 175,000|175,000")


TAX_Q = re.compile(r"(?i)(?<![a-z])(SDL|PAYE|VAT|NSSF|kodi|tax)(?![a-z])")


def _fix_tail(text, en=False, question=""):
    """replace what follows the LAST ' na ' / ' with ' of the final confirm sentence when that sentence names a firm"""
    marker = "Confirm" if en else "Thibitisha"
    i = text.rfind(marker)
    if i < 0:
        return text
    sent = text[i:]
    if not FIRM.search(sent):
        return text
    sep = " with " if en else " na "
    j = sent.rfind(sep) if not en else sent.find(sep)
    if j < 0:
        return text
    tax = bool(TAX_Q.search(question))      # a TAX question (SDL, PAYE, VAT) is confirmed with TRA first, never only the labour office (D-FIDELITY-17 tax-over-labour)
    auth = ("TRA (tra.go.tz) or the Labour Office (kazi.go.tz)." if tax else AUTH_EN) if en else ("TRA (tra.go.tz) au Ofisi ya Kazi (kazi.go.tz)." if tax else AUTH_SW)
    return text[:i] + sent[: j + len(sep)] + auth


def _fix_all_tails(text, en=False, question=""):
    """EVERY confirm sentence that names a firm gets the authority; two consecutive confirm sentences that end up identical in authority collapse to the first (eval_126 carried two)"""
    marker = "Confirm" if en else "Thibitisha"
    parts = re.split(r"(?<=[.!?])\s+", text)
    out, last_auth = [], None
    for sent in parts:
        if sent.startswith(marker) and FIRM.search(sent):
            fixed = _fix_tail(sent, en=en, question=question)
            auth = fixed[fixed.rfind(" with " if en else " na "):]
            if last_auth == auth:
                continue
            last_auth = auth
            out.append(fixed)
        else:
            out.append(sent)
    return " ".join(out)


def _conflate(text):
    for old, new in CONFLATION:
        text = text.replace(old, new)
    return text


def propose(question, sw, en=None):
    if question in QUARANTINE:
        return "quarantine", None, None, QUARANTINE[question]
    reasons = []
    new_sw, new_en = sw, en
    if question in REWRITE:
        new_sw, new_en = REWRITE[question]
        reasons.append("question is about MINING: the answer gave the energy rate; rewritten to 695,000 (mining and prospecting minerals) with 765,900 named as the energy-sector maximum")
    else:
        c = _conflate(new_sw)
        if c != new_sw:
            new_sw, reasons = c, reasons + ["765,900 relabelled energy / international companies (not 'madini')"]
        if new_en is not None:
            new_en = _conflate(new_en)
    t = _fix_tail(new_sw, question=question)
    if t != new_sw:
        new_sw, reasons = t, reasons + ["tail: a consultancy named as the authority -> Ofisi ya Kazi (kazi.go.tz) / TanzLII"]
    if new_en is not None:
        new_en = _fix_tail(new_en, en=True, question=question)
    return ("repair" if (new_sw != sw or new_en != en) else "none"), new_sw, new_en, "; ".join(reasons)


def main():
    rows = []
    done = set()
    for stage, pat in STAGES:
        for p in sorted(glob.glob(os.path.join(REPO, pat))):
            for n, l in enumerate(io.open(p, encoding="utf-8"), 1):
                if not l.strip():
                    continue
                try:
                    r = json.loads(l)
                except ValueError:
                    continue
                q = r.get("question_sw") or r.get("instruction") or ""
                a = r.get("answer_sw") or r.get("output") or ""
                if not ("765,900" in a or FIRM.search(a)):
                    continue
                act, new_sw, new_en, why = propose(q, a, r.get("answer_en"))
                if act == "none":
                    continue
                rows.append({"stage": stage, "file": os.path.relpath(p, REPO).replace(BS, "/"), "line": n, "question": q, "action": act, "reason": why,
                             "old_sw": a, "new_sw": new_sw, "old_en": r.get("answer_en"), "new_en": new_en, "old_sha256": hashlib.sha256(a.encode("utf-8")).hexdigest()[:16]})
    gold = []
    for l in io.open(os.path.join(REPO, "eval/accuracy_gate/eval_questions_001.jsonl"), encoding="utf-8"):
        r = json.loads(l)
        if r["id"] in ("eval_116", "eval_117", "eval_120", "eval_126"):
            sw, en = r["correct_answer_sw"], r["correct_answer_en"]
            nsw, nen = _fix_all_tails(sw, question=r["question_sw"]), _fix_all_tails(en, en=True, question=r["question_sw"])
            if r["id"] == "eval_120":
                nsw = nsw.replace("kwa sekta ya madini na nishati ya kimataifa (international mining/energy)", "kwa sekta ya nishati, kampuni za kimataifa (international energy companies)")
                nen = nen.replace("for the international mining and energy sector", "for the energy sector (international companies)")
            gold.append({"id": r["id"], "question": r["question_sw"], "answer_type": r["answer_type"], "old_sw": sw, "new_sw": nsw, "old_en": en, "new_en": nen})
    nat42 = None
    for l in io.open(os.path.join(REPO, "eval/accuracy_gate/edge_probe_natural_048.jsonl"), encoding="utf-8"):
        r = json.loads(l)
        if r.get("id") == "nat_42":
            nat42 = {"id": "nat_42", "old": r["expected_behavior"], "new": r["expected_behavior"].replace("(international mining/energy)", "(energy, international companies)")}
    floor_rows = []
    for stage, pat in STAGES:
        for p in sorted(glob.glob(os.path.join(REPO, pat))):
            for n, l in enumerate(io.open(p, encoding="utf-8"), 1):
                if "175,000" in l and "605A" in l and ("chini kabisa" in l or "lowest" in l or "175,000-765,900" in l or "175,000 hadi" in l):
                    floor_rows.append(os.path.relpath(p, REPO).replace(BS, "/") + ":" + str(n))
    res = {"date": "2026-11-17", "read_only": True, "n_rows": len(rows), "rows": rows, "gold": gold, "nat_42": nat42,
           "floor_note": "The Order's lowest monthly rate is TZS 80,000 (4(d) other domestic workers); 175,000 is the default for sectors the Order does not specify. These rows state 175,000 as the lowest / the range's low end:", "floor_rows": floor_rows}
    io.open(OUT, "w", encoding="utf-8").write(json.dumps(res, ensure_ascii=False, indent=1))
    from collections import Counter
    print(len(rows), "stage rows;", Counter((r["stage"], r["action"]) for r in rows))
    print(len({r["old_sha256"] for r in rows}), "distinct answers;", len(gold), "gold keys; nat_42:", bool(nat42), "; floor rows:", len(floor_rows))


if __name__ == "__main__":
    main()
