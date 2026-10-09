# -*- coding: utf-8 -*-
"""THE 17 FALSE-PASS CANDIDATES OF GATE 0e11c3d, ADJUDICATED ROW BY ROW.

⛔ WHY THIS DECIDES GATE 1 AND NOTHING ELSE IN THE RUN DOES.

`ALL_400` A2 came in at 82.3%, below R7's 85%. The `fact_path_190` bucket came in at **85.2%
raw / 85.8% reliable** — above the line, and it is the bucket a first-time user's question lands
in. So "the fact path clears Gate 1" was the one quotable claim in the run.

The judge overlay flags **17 rows where the regex scorer PASSED a row it was CONFIDENT about
(`reliable=True`) and the judge says the answer is wrong**. Seven of those sit in the fact-path
bucket. If they hold, the bucket is **not** above 85%, and the claim evaporates. That is why
this adjudication had to happen before anyone quoted 85.2%.

⛔ AND THE PRIOR RUNS BOTH WAYS. R38: a probe can encode a wrong expected answer, so a judge
disagreement is a CANDIDATE, not a verdict — the judge is a model too. But R28's mirror applies
equally: the thing telling you the incumbent is wrong carries the same burden as the incumbent.
So each row was read in full — question, gold, generated reply, vote split — and classified into
four outcomes, not two:

    FALSE_PASS   the judge is right; the regex verdict is wrong and A2 must fall
    PARTIAL      the answer to the question ASKED is right, but the reply carries a wrong
                 adjacent fact or omits a part the question explicitly asked for. The judge's
                 call is defensible; so was the regex pass. Reported separately so the headline
                 can be read with and without them.
    FALSE_ALARM  the judge is wrong; the regex pass stands
    WRONG_GOLD   the GOLD is the wrong one and the model was right. Not a false pass (the regex
                 pass was CORRECT) and not a false alarm (the judge's disagreement was
                 reasonable against the key it was handed). It must move A2 UP.

**Result: 10 FALSE_PASS, 5 PARTIAL, 1 FALSE_ALARM, 1 WRONG_GOLD.** The judge is right or
defensible on 15 of 17. The single false alarm (`eval_206`) had the weakest vote split in the
set (3-2), and that is the only row where the split predicted the outcome.

⛔⛔ TWO OF MY OWN CALLS WERE CORRECTED ON RE-READ, BOTH IN THE DIRECTION THAT ACCUSES THE MODEL
OF FABRICATING SOMETHING ITS OWN SERVED INDEX STATES WITH A CITATION. `eval_239` went
FALSE_PASS → WRONG_GOLD (index row 46 asserts the two-stage chain with GN 185/2016 Reg.16, and
the GOLD's flat 7 days is the stale claim); `eval_186` went FALSE_PASS → PARTIAL (index row 87 is
specific and sourced where I called the gold a hedge). **The check that found both is: READ THE
INDEX ROW BEFORE CLASSIFYING THE ROW.** It is now the first step of this file's method rather
than an afterthought, and it is the same asymmetry R26 records — a fabricated defect generates
an edit, a missed one does not.

⚠️ WHAT THIS IS NOT. This adjudicates only rows the regex scorer PASSED. It says nothing about
the 24 rows where regex failed and the judge said `correct` — the opposite direction, which
would move A2 UP and is a separate job. Naming that rather than letting "adjudicated" imply
both directions (R22: name the population).

Usage:  python eval/controls/adjudicate_false_passes_0e11c3d.py
Artifact: eval/results/false_pass_adjudication_0e11c3d.json
Exit 0 always — this is an adjudication, not a gate.
"""
import io
import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
GATE = os.path.join(REPO, "eval", "results", "gate_production_0e11c3d.json")
OUT = os.path.join(REPO, "eval", "results", "false_pass_adjudication_0e11c3d.json")

# ── THE ADJUDICATION. One entry per candidate, each quoting the sentence that decides it ───
# `defect` is the class, so the rows can be counted by failure mode rather than only totalled.
ADJ = {
    # ───────────────── fact_path_190 — these seven decide Gate 1 ─────────────────
    "eval_086": dict(
        verdict="FALSE_PASS", defect="party_inversion",
        why="The RATE is right and the PARTY is inverted. Gold: 10% is the employer's own "
            "contribution and 'haikatwi kutoka mshahara wa mfanyakazi' (is NOT deducted from "
            "the employee's salary). The reply says exactly the opposite — 'Kiasi "
            "kinachokatwa na mwajiri KWENYE MSHAHARA wa mfanyakazi ... ni asilimia 10'. The "
            "regex scorer matched `asilimia 10` and passed. An employer following this "
            "deducts 10% from wages unlawfully, on top of the employee's own 10%. This is "
            "D-NSSF-1's party-resolution defect, live, on a reliable row."),
    "eval_104": dict(
        verdict="FALSE_PASS", defect="wrong_instrument_named",
        why="Names 'fomu ya NSSF P9' as an NSSF registration document. The P9 is a PAYE "
            "annual tax-deduction card, not an NSSF form. It also omits two of the four "
            "items the gold requires (TIN, BRELA certificate) while adding unsourced "
            "'picha za pasipoti'. A procedure answer naming the wrong form is not a pass."),
    "eval_130": dict(
        verdict="FALSE_PASS", defect="operation_inverted",
        why="'kuchukua jumla ya mishahara ... na KUIGAWANYA kwa 3.5%' — DIVIDE by 3.5%, where "
            "the gold multiplies. On the gold's own example that is 10,000,000 / 0.035 = "
            "285,714,286 instead of 350,000. The rate is correct and the operation is "
            "inverted, so every magnitude-based check passes. No D-FIDELITY rule can see "
            "this: it describes a METHOD and computes no amount (R19's derived-quantity "
            "boundary, from the other side)."),
    "eval_145": dict(
        verdict="PARTIAL", defect="penalty_misattributed",
        why="The verdict is right ('Hapana') and the prohibition is correctly identified as "
            "facilitation. But it states 'faini ya TZS milioni 10 AU kifungo cha miezi 6' "
            "without saying whose, then says the friend faces 'adhabu tofauti' and never "
            "names them — and the friend's TZS 5M / 3 months IS the gold's point. Defensible "
            "both ways: 10M/6mo is correct for the ASKER, who is the non-citizen. Weakest of "
            "the seven."),
    "eval_162": dict(
        verdict="FALSE_PASS", defect="definition_inverted_with_fabricated_criteria",
        why="Flagrant. Gold: 'mgeni' is anyone who is not a Tanzanian citizen, and marriage "
            "to a citizen does not change status. The reply inverts it — a Tanzanian CITIZEN "
            "is a 'mgeni' if they meet three invented numbered criteria (citizenship by "
            "marriage only, 15+ years' residence, a full-status passport). None exists. This "
            "is the 'mgeni definition inverted' defect the v9 root-cause analysis recorded, "
            "still live, now with fabricated structure attached."),
    "eval_171": dict(
        verdict="FALSE_PASS", defect="advises_the_prohibited_act",
        why="THE MOST HARMFUL OF THE SEVEN. Asked what to do now, it advises changing the "
            "ownership structure — 'ubia na raia wa Tanzania, kununua biashara hiyo na "
            "Mtanzania' — which is the facilitation GN487A criminalises, and the very thing "
            "eval_145 asks about. It never says to stop the activity, and omits the "
            "pre-28-Jul-2025 licence run-off that is the gold's actual relief. Counsels a "
            "workaround carrying TZS 10M + 6 months for the asker and 5M + 3 months for the "
            "Tanzanian."),
    "eval_186": dict(
        verdict="PARTIAL", defect="polarity_error_on_a_row_whose_GOLD_is_also_stale",
        why="⚠️ RECLASSIFIED FROM FALSE_PASS, for the same reason as eval_239: I called it "
            "'a confident answer where the gold is a hedge', and THE INDEX IS NOT A HEDGE. Row "
            "87 is specific and sourced: 'Afisa wa usalama kazini: HAPANA, mwajiri halazimiki "
            "kumwajiri afisa maalum. Ukiwa na wafanyakazi zaidi ya 20, unateua mwakilishi wa "
            "usalama na afya kutoka kwa wafanyakazi ulio nao -- ni kuteua, si kuajiri mtu "
            "mpya. Kiwandani: mwakilishi 1 kwa kila wafanyakazi 50... (NOT a professionally "
            "hired/dedicated safety officer.)' So the GOLD's 'kizingiti ... hakijathibitishwa "
            "waziwazi' is weaker than what we actually hold and is itself a candidate stale "
            "key. The model's answer is HALF right -- appointing a representative is correct "
            "at 60 staff -- but it opens 'Ndiyo' to a question about an AFISA WA USALAMA, "
            "where its own row says HAPANA and draws exactly that officer/representative "
            "distinction. A real polarity defect on a row that also needs its gold re-sourced, "
            "so it is not a clean false pass in either direction."),
    # ───────────────── the other ten ─────────────────
    "eval_206": dict(
        verdict="FALSE_ALARM", defect=None,
        why="THE JUDGE IS WRONG AND THE REGEX PASS STANDS. 'Hapana — BRELA inasajili "
            "makampuni na majina ya biashara; OSHA inasajili MAHALI PA KAZI. Ni usajili "
            "tofauti kabisa.' That is the gold's content. It omits the explicit 'you must do "
            "both', which is an incompleteness and not an error. Vote split 3-2, the weakest "
            "in the set — and the only row where the split predicted the outcome."),
    "eval_223": dict(
        verdict="FALSE_PASS", defect="wrong_member_of_a_closed_set",
        why="The STR's four instruments are a CLOSED list. The reply keeps the count at four "
            "and substitutes 'One Stop Border Post' for the USD 2,000 consignment threshold — "
            "a real EAC concept that is not an STR instrument — thereby dropping the one "
            "operative NUMBER a trader needs. Right shape, wrong member, missing threshold."),
    "eval_235": dict(
        verdict="PARTIAL", defect="half_of_a_two_part_question",
        why="The question asks age AND contribution months. The reply gives 180 months "
            "correctly and OMITS THE AGE entirely (60, or 55 for mining/early). Nothing "
            "stated is wrong; half of what was asked is absent."),
    "eval_237": dict(
        verdict="FALSE_PASS", defect="one_word_date_shift",
        why="'ndani ya siku 7 baada ya mwisho wa MWEZI UNAOFUATA' — within 7 days after the "
            "end of the FOLLOWING month. The gold is 7 days after the end of the calendar "
            "month, and goes out of its way to say 'si tarehe 7 ya mwezi unaofuata'. One word "
            "(`unaofuata`) moves the deadline a full month late; the regex matched 'siku 7'."),
    "eval_239": dict(
        verdict="WRONG_GOLD", defect="gold_is_the_stale_claim",
        why="⛔ MY OWN FIRST ADJUDICATION OF THIS ROW WAS WRONG, AND IT WAS WRONG IN THE "
            "DIRECTION THAT ACCUSES THE MODEL. I recorded it as 'fabricated process structure "
            "— invents a two-stage reporting process with a 14-day worker-to-employer step "
            "that appears in no locked fact'. It appears in a locked fact, verbatim, WITH a "
            "regulation citation, and it is SERVED: index row 46 reads 'Occupational disease "
            "reporting to WCF is a TWO-STAGE chain, not a flat 7-day deadline. Per the Workers "
            "Compensation Regulations, 2016 (GN 185/2016), Reg.16: the EMPLOYEE must notify the "
            "EMPLOYER within 14 working days of diagnosis (Reg.16(1)); the EMPLOYER must then "
            "notify WCF within 7 working days of RECEIVING that employee notice (Reg.16(2)) -- "
            "so the true worst-case window from diagnosis to WCF notification is up to 21 "
            "working days, NOT 7.' The model reproduced its own index row correctly. "
            "THE GOLD ('ndani ya siku 7 za kazi tangu kugunduliwa') IS THE STALE CLAIM, and so "
            "is CLAUDE.md Section 11's 'Occupational disease reporting: 7 working days from "
            "date of diagnosis'. The judge agreed with the gold, so the judge was wrong here "
            "too. Found only by checking whether the governing fact was IN THE INDEX before "
            "classifying the row — which is the step that should have come first, and which "
            "R28 already prescribes from the correction side: the thing telling you the "
            "incumbent is wrong carries the same burden as the incumbent."),
    "eval_304": dict(
        verdict="FALSE_PASS", defect="fabricated_threshold_rule",
        why="CORRECTION-SHAPED WRONGNESS — it reads as rigour. Gold: the company-vs-business-"
            "name choice does not depend on headcount or capital, and the question's 20 "
            "employees and TZS 50,000,000 are irrelevant. The reply invents a rule ('business "
            "name if <=20 employees and capital up to TZS 100,000,000, company above that') "
            "and applies it confidently. Exactly the fabrication-on-a-plausible-question "
            "shape the 2026-09-23 adjudication identified as the floor problem."),
    "eval_330": dict(
        verdict="PARTIAL", defect="contradictory_values_offered_plus_omission",
        why="The arithmetic is right (10% x 450,000 = 45,000) and the 20% split is correct. "
            "But it offers TWO contradictory penalties — 'Taarifa #1: asilimia 5 ... Taarifa "
            "#2: shilingi 2000' — where Cap.50 s.14(3)'s 5%/month is the statute-tier "
            "confirmed figure and the 2,000 is unsourced; and it never answers the DEADLINE, "
            "which the question explicitly asked for. The gold itself hedges the penalty, so "
            "the hedge is not the defect — the fabricated alternative and the omission are."),
    "eval_338": dict(
        verdict="FALSE_PASS", defect="refuses_then_confirms_the_false_premise",
        why="Opens 'Hapana' and then CONFIRMS the premise it just denied: 'Kiwango cha VAT kwa "
            "huduma ni asilimia 18 kama kiwango cha kawaida pia ... Bidhaa na huduma "
            "zinatozwa 18%'. It never states the actual withholding rates (6% services / 3% "
            "goods, FA2025). The regex passed on the leading 'Hapana' — the refusal-then-"
            "elaborate pattern, with the elaboration restoring the error."),
    "eval_345": dict(
        verdict="PARTIAL", defect="correct_answer_plus_a_new_adjacent_error",
        why="The question — is SDL due on the 20th? — is answered correctly (no, the 7th). It "
            "then says 'Tarehe 20 ni kwa VAT withholding na PAYE'. PAYE is the 7th, not the "
            "20th, so it introduces a fresh wrong deadline while correcting one. The gold "
            "names the 20th as VAT withholding and the VAT return. Defensible both ways."),
    "eval_394": dict(
        verdict="FALSE_PASS", defect="cross_levy_threshold_bleed",
        why="Gold: NSSF is mandatory, full stop, for eligible employers. The reply bolts on a "
            "threshold — 'lazima kwa waajiri wenye wafanyakazi 10 au zaidi' — which is SDL's "
            "threshold, not NSSF's. NSSF has no such minimum, so this tells an employer with "
            "nine staff that NSSF is optional. The 'Ndiyo' passed the yes/no check while the "
            "qualifier reversed the answer for a whole class of employer."),
}


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:                                                # noqa: BLE001
        pass
    d = json.load(io.open(GATE, encoding="utf-8"))
    rows = {r["id"]: r for r in d["rows"]}
    per = d["judge_overlay"]["per_id"]

    inc = [r for r in d["rows"] if r["subdomain"] != "out_of_corpus"]
    candidates = sorted(r["id"] for r in inc
                        if r["pass"] and r["judge"] == "wrong" and r["reliable"])
    assert set(candidates) == set(ADJ), (
        f"the candidate set moved: unadjudicated {sorted(set(candidates) - set(ADJ))}, "
        f"stale {sorted(set(ADJ) - set(candidates))}. An adjudication keyed to a population "
        f"that has changed is a stale pin")

    fact_path = {r["id"] for r in d["rows"]
                 if r["source"] == "gate_001" and not r["compute"]
                 and r["subdomain"] != "out_of_corpus"}

    out_rows = []
    for qid in candidates:
        r, a = rows[qid], ADJ[qid]
        out_rows.append({
            "id": qid, "verdict": a["verdict"], "defect": a["defect"], "why": a["why"],
            "subdomain": r["subdomain"], "answer_type": r["answer_type"],
            "source": r["source"], "in_fact_path": qid in fact_path,
            "judge_votes": per.get(qid, {}).get("votes"),
            "question_sw": r["question_sw"], "gold_sw": r["correct_answer_sw"],
            "generated": r["generated"],
        })

    def rate(bucket_ids, drop):
        base = [r for r in d["rows"] if r["id"] in bucket_ids]
        right = sum(1 for r in base if r["pass"] and not r["clarified"] and not r["error"])
        n = len(base)
        return {"right": right - len(drop & bucket_ids), "n": n,
                "rate": (right - len(drop & bucket_ids)) / n}

    all_ids = {r["id"] for r in inc}
    confirmed = {q for q in candidates if ADJ[q]["verdict"] == "FALSE_PASS"}
    partial = {q for q in candidates if ADJ[q]["verdict"] == "PARTIAL"}
    alarm = {q for q in candidates if ADJ[q]["verdict"] == "FALSE_ALARM"}
    # ⛔ A FOURTH OUTCOME, ADDED ON RE-READ: the GOLD is the wrong one and the model was right.
    # It is not a false pass (the regex pass was CORRECT) and not a false alarm (the judge's
    # disagreement was reasonable against the key it was given) -- it is a key defect, and it
    # must move A2 UP, not down. Keeping it in its own bucket is what stops it being quietly
    # absorbed into either of the other two.
    wrong_gold = {q for q in candidates if ADJ[q]["verdict"] == "WRONG_GOLD"}

    impact = {
        "ALL_400": {
            "as_published": rate(all_ids, set()),
            "confirmed_removed": rate(all_ids, confirmed),
            "confirmed_and_partial_removed": rate(all_ids, confirmed | partial),
        },
        "fact_path_190": {
            "as_published": rate(fact_path, set()),
            "confirmed_removed": rate(fact_path, confirmed),
            "confirmed_and_partial_removed": rate(fact_path, confirmed | partial),
        },
    }

    payload = {
        "_what": "the 17 reliable=True rows where the regex scorer passed and the judge said "
                 "wrong, adjudicated one by one against question, gold and reply",
        "_population": "regex pass AND judge 'wrong' AND reliable=True, in-corpus. NOT the 19 "
                       "further candidates on reliable=False rows, and NOT the opposite "
                       "direction (regex fail + judge correct), which would move A2 UP and is "
                       "a separate job.",
        "gate": "gate_production_0e11c3d.json", "gate_commit": d["clone_head"],
        "tally": {"FALSE_PASS": len(confirmed), "PARTIAL": len(partial),
                  "FALSE_ALARM": len(alarm), "WRONG_GOLD": len(wrong_gold),
                  "total": len(candidates)},
        "judge_right_or_defensible": len(confirmed) + len(partial),
        "_corrections_to_this_adjudication": (
            "eval_239 FALSE_PASS -> WRONG_GOLD and eval_186 FALSE_PASS -> PARTIAL, both on "
            "2026-10-09 after checking whether the governing fact was IN THE INDEX. Both of my "
            "original calls accused the model of fabricating something its own served index "
            "states with a citation. The check that found them -- read the index row before "
            "classifying the row -- is now the first step, not the last."),
        "defect_classes": sorted({a["defect"] for a in ADJ.values() if a["defect"]}),
        "impact_on_bar_a": impact,
        "_the_gate_1_conclusion": (
            "fact_path_190 was published at 85.2% raw, above R7's 85%. Removing only the "
            "CONFIRMED false passes puts it at "
            f"{impact['fact_path_190']['confirmed_removed']['rate']:.1%}; including the "
            f"partials, {impact['fact_path_190']['confirmed_and_partial_removed']['rate']:.1%}."
            " BOTH ARE BELOW 85%. No bucket of this run clears Gate 1 once the false passes "
            "are removed, and 85.2% must not be quoted as a Gate 1 result."),
        "rows": out_rows,
    }
    with io.open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)

    print(f"adjudicated {len(candidates)} candidates: FALSE_PASS {len(confirmed)} · "
          f"PARTIAL {len(partial)} · FALSE_ALARM {len(alarm)} · WRONG_GOLD {len(wrong_gold)}")
    for q in candidates:
        mark = {"FALSE_PASS": "FP", "PARTIAL": "~~", "FALSE_ALARM": "ok",
                "WRONG_GOLD": "GOLD"}[ADJ[q]["verdict"]]
        print(f"  [{mark}] {q:10s} {'(fact path)' if q in fact_path else '':12s} "
              f"{ADJ[q]['defect'] or '-'}")
    print()
    for bucket, v in impact.items():
        print(f"{bucket}:")
        for k, s in v.items():
            print(f"   {k:32s} {s['right']:3d}/{s['n']:3d} = {s['rate']:6.1%}"
                  f"{'   <- BELOW 85%' if s['rate'] <= 0.85 else '   above 85%'}")
    print(f"\nartifact: {os.path.relpath(OUT, REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
