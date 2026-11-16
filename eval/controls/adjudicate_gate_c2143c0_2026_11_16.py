# -*- coding: utf-8 -*-
"""GATE c2143c0 -- THE 23 FALSE-PASS AND 6 FALSE-FAIL CANDIDATES ADJUDICATED BY HAND, AND EVERY MISS CLASSIFIED (2026-11-16).

    python eval/controls/adjudicate_gate_c2143c0_2026_11_16.py

Method (R12b): each row read against question, gold and reply, and the SERVED index row read FIRST. Outcomes for the
false-pass queue: FALSE_PASS / PARTIAL / FALSE_ALARM / WRONG_GOLD. For the false-fail queue: UPHELD (reply acceptable, the
regex was wrong) / PARTIAL / REJECTED (the reply is wrong, the judge was wrong). The false-fail direction is reported and
NOT applied to either bound (R12b). Miss classes: ROUTE / CORPUS / MODEL / GOLD -- GOLD here means "the key or the scorer
is the defect, the reply is acceptable". Presence of the governing fact in the served index was checked by me for the
rows marked `idx: yes`; `idx: ?` means NOT checked and the class is provisional.
"""
import io
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def L(p):
    return json.load(io.open(os.path.join(REPO, p), encoding="utf-8"))


FP = {  # the 23 reliable regex-PASS rows the judge called wrong
    "eval_065": ("PARTIAL", "core right (approved supplier); adds a VFD route from TRA that index row 85 only half supports"),
    "eval_085": ("FALSE_PASS", "TZS 22,000/month late penalty (and 264,000/yr) -- 22,000 is the filing FEE, the penalty is 2,500/month (rows 99,100). Baseline text had 2,500: A NEW REGRESSION"),
    "eval_120": ("PARTIAL", "765,900/energy right; then calls it 'not the highest' -- contradicts row 74. Baseline text was right"),
    "eval_126": ("FALSE_PASS", "'Hapana' right; invents a 31 Jul speech, a PM attribution and 'not yet official'. No served row on the 500,000 public-sector figure. Baseline text was right"),
    "eval_129": ("FALSE_PASS", "garbled order ('nyumba na gari', everything due on the 7th). Baseline text was acceptable"),
    "eval_132": ("PARTIAL", "omits backpay, the central instruction; no wrong figure; labour.go.tz domain unverified. Regex flipped FAIL->PASS"),
    "eval_145": ("PARTIAL", "Hapana right; gives the non-citizen penalty to the user, never states the citizen's 5M/3m (rows 22,92 have it). Same text as baseline"),
    "eval_162": ("FALSE_PASS", "invents criteria that make a citizen a 'mgeni' -- row 91 says the opposite. Same text as baseline"),
    "eval_171": ("FALSE_PASS", "advises restructuring ownership with a Tanzanian -- i.e. the facilitation GN487A prohibits. No served row on grandfathered licences. Same text as baseline"),
    "eval_185": ("PARTIAL", "distinction right; never answers 'which first'; says OSHA before starting. Baseline text identical in substance"),
    "eval_186": ("PARTIAL", "never answers 'do I hire an officer' (row 87: no); asserts >=2 reps, unsupported at 60 staff office-side"),
    "eval_206": ("FALSE_ALARM", "reply matches gold exactly; judge 5/5 wrong"),
    "eval_210": ("PARTIAL", "Hapana + GN605A right; says the 2022 rates ended 31 Dec 2022 -- row 72: no force after 31 Dec 2025. Baseline text was right"),
    "eval_218": ("WRONG_GOLD", "ITA First Schedule para 4(b)(ii) (locked fact rent_wht_rate, read from the Act 2026-09-26) gives 10% to residents AND non-residents; the reply says exactly that, the gold says 'not verified'. Gold is the stale claim (R28 direction)"),
    "eval_223": ("FALSE_PASS", "SCO, SCD, CET, 'verification' -- two of four invented; NO STR row in the served index (tier 1B unbuilt). Same defect as baseline"),
    "eval_230": ("FALSE_ALARM", "no separate personal relief; 0% to 270,000 -- matches gold; the 26,000/27,000 appear only to be denied"),
    "eval_237": ("FALSE_PASS", "'siku 7 baada ya mwisho wa mwezi UNAOFUATA' is a month late; row 37 says 7 days after the end of the calendar month. Text differs from baseline, same defect"),
    "eval_304": ("FALSE_PASS", "invents a 20-employee / TZS 100M rule; row 82 says the choice does not depend on either. Same text as baseline"),
    "eval_315": ("FALSE_ALARM", "6%, 180,000 on 3,000,000 -- exactly the gold; 540,000 is the VAT, also correct (row 65)"),
    "eval_318": ("FALSE_PASS", "SDL/NSSF right (engine) but TELLS A TZS 205,000,000 BUSINESS IT NEED NOT REGISTER FOR VAT. Baseline text said Ndiyo. VAT limb unrouted"),
    "eval_324": ("FALSE_PASS", "SDL 168,000 right; then invents NSSF/WCF totals ('jumla 252,000' = 168+960+24 is 1,152,000) and a 'faida 760,000'. Added fabrication on a correct core"),
    "eval_338": ("PARTIAL", "'Hapana' right; never states the 6%/3% asked about (rows 17,65). Same text as baseline"),
    "eval_398": ("FALSE_PASS", "5% of 700,000 stated as 70,000 (35,000); total 175,000. Question names no levy so the NSSF engine is not reached"),
}
FF = {  # the 6 regex-FAIL rows the judge called correct
    "eval_026": ("REJECTED", "reply says register within 14 days; the applicant's own deadline is 30 (row 106 states 14 only for the notification AFTER the Commissioner registers someone). Judge wrong"),
    "eval_069": ("UPHELD", "row 95 names every action listed incl. closing premises and suspending the device"),
    "eval_094": ("UPHELD", "NSSF, with interest and penalties -- matches gold"),
    "eval_187": ("PARTIAL", "says contact OSHA; never says register"),
    "eval_332": ("PARTIAL", "content right (prohibited; 10M or 6m; helper 5M/3m) but opens 'Ndiyo' on a can-I question"),
    "eval_390": ("REJECTED", "opens 'Hapana, si sahihi' on a negated premise whose answer is yes, then states the right content -- self-contradictory (same class as eval_388, eval_394)"),
}

# Every regex-FAIL row (65) plus the 11 false passes. class / idx / A (confident wrong A1, none, or acceptable) / note
CLS = {
 # --- the 65 regex fails
 "eval_025": ("MODEL", "yes", "wrong reason given; row 208 names professional service providers"),
 "eval_026": ("CORPUS", "neg-only", "30-day own-application deadline appears only inside a negation in row 106"),
 "eval_028": ("GOLD", "yes", "gold's 4-step voluntary procedure is the unread-KPMG claim (4y); reply defers to the Commissioner"),
 "eval_029": ("GOLD", "?", "reply right but omits carry-forward; acceptable"),
 "eval_044": ("MODEL", "yes", "3% for IT services; rows 17,65"),
 "eval_048": ("MODEL", "yes", "supplier/TRA shares inverted; judge said correct and was wrong"),
 "eval_051": ("GOLD", "?", "'TZS 0' = no minimum; acceptable"),
 "eval_069": ("GOLD", "yes", "reply acceptable (row 95)"),
 "eval_071": ("MODEL", "yes", "'KUMI' forms; row 82 says three"),
 "eval_074": ("CORPUS", "?", "no BRELA-cert + TIN minimum row; reply lists five bodies"),
 "eval_094": ("GOLD", "?", "reply acceptable"),
 "eval_106": ("CORPUS", "?", "what NSSF issues on registration is not in the index"),
 "eval_108": ("ROUTE", "yes", "a penalty question diverted to the compute clarification; nssf_penalty exists"),
 "eval_127": ("MODEL", "?", "SDL 'not necessarily the 7th'; prompt-only LOSS"),
 "eval_131": ("CORPUS", "?", "no 'find your sector' row; reply names PKF at a wrong domain"),
 "eval_144": ("GOLD", "yes", "reply right; scorer wants the 'La' opener"),
 "eval_155": ("MODEL", "?", "enforcement 'ongoing'; exercise ended 8 Oct 2025"),
 "eval_163": ("MODEL", "yes", "states no penalty; row 92 has 5M/3m"),
 "eval_174": ("MODEL", "?", "invents a prosecution and conviction"),
 "eval_183": ("MODEL", "?", "asserts OSHA closure power; gold says none"),
 "eval_187": ("MODEL", "?", "thin: never says register"),
 "eval_205": ("CORPUS", "?", "objection prerequisite (undisputed / one-third, 15 days) not served"),
 "eval_208": ("ROUTE", "yes", "'milioni 95 katika miezi 6' not extracted; the VAT engine answers it correctly. A1"),
 "eval_220": ("CORPUS", "?", "residence-permit classes unserved; invents TZS 10M. A1"),
 "eval_224": ("CORPUS", "neg-only", "same as eval_026; invents '14 working days / first Monday'. A1"),
 "eval_228": ("GOLD", "n/a", "gold wants a hedged number; stamp duty is on the OOC list (R11) and is refused by design"),
 "eval_229": ("MODEL", "yes", "invents 8 PAYE bands; the band row is served. A1; routable as a statement"),
 "eval_236": ("CORPUS", "?", "90 days vs 6 months; objection-decision period unserved. A1"),
 "eval_239": ("MODEL", "yes", "collapses the two-stage chain (row 46) to 14 working days; prompt-only LOSS"),
 "eval_257": ("ROUTE", "yes", "engine reads 'mapato' as a wage and computes 20% of business income. A1 from an ENGINE"),
 "eval_260": ("GOLD", "yes", "reply right"),
 "eval_267": ("GOLD", "yes", "clarification matches the gold's own clarification; harness hard-codes clarified => FAIL"),
 "eval_270": ("GOLD", "yes", "same"), "eval_271": ("GOLD", "yes", "same"), "eval_272": ("GOLD", "yes", "same"),
 "eval_273": ("GOLD", "yes", "same"), "eval_275": ("GOLD", "yes", "same"), "eval_276": ("GOLD", "yes", "same"),
 "eval_277": ("GOLD", "yes", "defensible: asks headcount, gold is conditional"),
 "eval_281": ("ROUTE", "yes", "'TZS 920,000 hivi' not extracted; gold computes 108,000"),
 "eval_291": ("GOLD", "yes", "same"), "eval_292": ("GOLD", "yes", "same"),
 "eval_294": ("GOLD", "yes", "defensible"), "eval_295": ("GOLD", "yes", "same"),
 "eval_297": ("GOLD", "yes", "same"), "eval_298": ("GOLD", "yes", "same"), "eval_299": ("GOLD", "yes", "same"), "eval_300": ("GOLD", "yes", "same"),
 "eval_278": ("ROUTE", "yes", "KES figure; invents a 'reverse charge'; not routed. A1"),
 "eval_301": ("MODEL", "yes", "invents a 10-employee BRELA rule; row 82. A1"),
 "eval_302": ("MODEL", "yes", "invents a TZS 10M wage threshold for VAT. A1"),
 "eval_317": ("GOLD", "n/a", "right substance, no 'Hapana'; judge correct"),
 "eval_326": ("ROUTE", "yes", "both salaries given; clarified instead of computing 158,000 / 165,000"),
 "eval_332": ("MODEL", "yes", "'Ndiyo' opener on a compound can-I question (polarity)"),
 "eval_334": ("ROUTE", "yes", "allowance + bonus; clarified instead of computing 115,500"),
 "eval_347": ("GOLD", "yes", "reply states the right answer via D-FIDELITY-7 replacement copy; scored FAIL because clarified. The owed answer was delivered"),
 "eval_348": ("MODEL", "yes", "negated premise answered 'Ndiyo, no other split' -- row 78. A1; routable as a statement"),
 "eval_355": ("MODEL", "yes", "'chini ya kizingiti cha TZS 11M' -- the fabricated EFD threshold. D-FIDELITY-7 did NOT fire: it keys on a subject named in the BODY and the body never says EFD. A1. prompt-only LOSS"),
 "eval_364": ("GOLD", "yes", "reply right; row marked unreliable"),
 "eval_365": ("GOLD", "yes", "reply right"),
 "eval_375": ("MODEL", "yes", "says withholding still applies for an unregistered supplier. A1"),
 "eval_376": ("ROUTE", "yes", "no employees => TZS 0; clarified"),
 "eval_383": ("MODEL", "yes", "row 181 states 500,000 for a company with no share capital; reply says 95,000. A1"),
 "eval_388": ("MODEL", "yes", "negated-premise polarity, same class as 390/394"),
 "eval_390": ("MODEL", "yes", "negated-premise polarity"),
 # --- the 11 false passes
 "eval_085": ("MODEL", "yes", "FALSE_PASS; regression"), "eval_126": ("CORPUS", "no", "FALSE_PASS"),
 "eval_129": ("CORPUS", "?", "FALSE_PASS"), "eval_162": ("MODEL", "yes", "FALSE_PASS"),
 "eval_171": ("CORPUS", "no", "FALSE_PASS; advises the prohibited act -- guardable"),
 "eval_223": ("CORPUS", "no", "FALSE_PASS; tier 1B unbuilt"), "eval_237": ("MODEL", "yes", "FALSE_PASS"),
 "eval_304": ("MODEL", "yes", "FALSE_PASS"), "eval_318": ("ROUTE", "yes", "FALSE_PASS; VAT limb unrouted (4 phrasings tried)"),
 "eval_324": ("MODEL", "yes", "FALSE_PASS; added fabrication"), "eval_398": ("ROUTE", "yes", "FALSE_PASS; no levy named"),
}


def main():
    d = L("eval/results/gate_production_c2143c0.json")
    rows = {r["id"]: r for r in d["rows"]}
    pj = d["judge_overlay"]["per_id"]
    fp_set = sorted(i for i, r in rows.items() if str(r["pass"]) == "True" and r.get("reliable") in (True, "True") and pj.get(i, {}).get("verdict") == "wrong")
    ff_set = sorted(i for i, r in rows.items() if str(r["pass"]) != "True" and r.get("reliable") in (True, "True") and pj.get(i, {}).get("verdict") == "correct")
    assert fp_set == sorted(FP), (set(fp_set) ^ set(FP))
    assert ff_set == sorted(FF), (set(ff_set) ^ set(FF))
    fails = sorted(i for i, r in rows.items() if r["subdomain"] != "out_of_corpus" and str(r["pass"]) != "True")
    assert len(fails) == 65, len(fails)
    fpc = [i for i, v in FP.items() if v[0] == "FALSE_PASS"]
    missing = [i for i in fails + fpc if i not in CLS]
    assert not missing, missing
    tally = {k: sum(1 for v in FP.values() if v[0] == k) for k in ("FALSE_PASS", "PARTIAL", "FALSE_ALARM", "WRONG_GOLD")}
    ff_t = {k: sum(1 for v in FF.values() if v[0] == k) for k in ("UPHELD", "PARTIAL", "REJECTED")}
    inc = [r for r in rows.values() if r["subdomain"] != "out_of_corpus"]
    raw = sum(str(r["pass"]) == "True" for r in inc)
    n = len(inc)
    rate = lambda right, den: {"right": right, "n": den, "rate": round(right / den, 4)}
    rep = d["judge_overlay"]["report"]
    ja = rep["judge_augmented"]
    impact = {
        "ALL_400_like_for_like_with_0e11c3d_adjudication": {
            "as_published": rate(raw, n),
            "confirmed_removed": rate(raw - tally["FALSE_PASS"], n),
            "confirmed_and_partial_removed": rate(raw - tally["FALSE_PASS"] - tally["PARTIAL"], n),
            "baseline_0e11c3d_same_convention": {"as_published": 0.8229, "confirmed_removed": 0.7969, "confirmed_and_partial_removed": 0.7839},
        },
        "judge_bracket_closed_by_hand": {
            "upper_judge_augmented": rate(ja["pass"], ja["total"]),
            "lower_queue_fully_upheld": rep["bar_a_headline_bracket"]["lower"],
            "adjudicated_confirmed_removed": rate(ja["pass"] - tally["FALSE_PASS"], ja["total"]),
            "adjudicated_confirmed_and_partial_removed": rate(ja["pass"] - tally["FALSE_PASS"] - tally["PARTIAL"], ja["total"]),
        },
        "false_fail_direction_NOT_APPLIED": {"would_add_if_upheld": ff_t["UPHELD"], "per_R12b": "reported, applied to neither bound"},
    }
    by = {}
    for i in fails + fpc:
        by.setdefault(CLS[i][0], []).append(i)
    clar = sorted(i for i in fails if str(rows[i]["clarified"]) == "True")
    out = {"gate": "gate_production_c2143c0.json", "tally_false_pass_queue": tally, "tally_false_fail_queue": ff_t,
           "false_pass": {i: {"verdict": v[0], "why": v[1]} for i, v in FP.items()},
           "false_fail": {i: {"verdict": v[0], "why": v[1]} for i, v in FF.items()},
           "impact": impact,
           "miss_classes": {k: {"n": len(v), "ids": v} for k, v in sorted(by.items())},
           "per_row_class": {i: {"class": CLS[i][0], "idx_checked": CLS[i][1], "note": CLS[i][2]} for i in sorted(CLS)},
           "clarified_rows": {"n": len(clar), "ids": clar,
                              "scorer_rule": "kaggle/eval_gate_production_2026_10_09.py::_score_both_keys: `if clarified: new_pass = False` -- EVERY clarification is a miss whatever the gold says",
                              "gold_is_itself_a_clarification_and_reply_matches": sorted(i for i in clar if CLS[i][0] == "GOLD" and i != "eval_347"),
                              "clarified_where_an_answer_was_owed": sorted(i for i in clar if CLS[i][0] == "ROUTE")}}
    json.dump(out, io.open(os.path.join(REPO, "eval/results/gate_c2143c0_adjudication_2026_11_16.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("false-pass queue", tally, "| false-fail queue", ff_t)
    print(json.dumps(impact, indent=1))
    print({k: len(v) for k, v in sorted(by.items())}, "clarified", len(clar), "GOLD-clarified", len(out["clarified_rows"]["gold_is_itself_a_clarification_and_reply_matches"]))


if __name__ == "__main__":
    main()
