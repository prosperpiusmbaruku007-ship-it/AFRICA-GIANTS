# -*- coding: utf-8 -*-
"""CAN BAR A BE CLOSED BY THE METHODS THAT HAVE WORKED, OR DOES IT NEED THE MODEL LAYER?

⛔ THE QUESTION, ASKED OF THE LARGEST AND BEST-MEASURED POPULATION WE HAVE. Bucket A's split
was asked of a handful of rows. This asks it of the gate's confirmed defects: for each, could a
DETERMINISTIC ROUTE own the answer, could a GUARD catch the error, or is it genuinely the model
failing to use what it was given?

The three options are not equal in what they cost or what they prove:

  ROUTE   the answer is a fixed constant or table the engine already holds. Taking the row out
          of the model's hands entirely. Cheapest and strongest — but only available where the
          answer does not depend on the user's figures (R19's constant/derived boundary).
  GUARD   the answer is not owned, but the ERROR is a comparison against a constant, so it can
          be caught and withheld. Converts a wrong answer into a no-answer: moves A1, never A2.
  MODEL   the governing fact was in the index, correct, and the reply contradicted it. No
          existing method reaches this. It is the "correct fact at rank 1 and the wrong value
          emitted" class.
  CORPUS  the governing fact is ABSENT from the served index. Not a model failure at all — the
          row is testing coverage we do not have.

⛔⛔ THE METHOD, AND IT IS THE PART THAT CHANGED THE ANSWER. Every row's classification is
grounded in TWO measurements, not in reading the reply and forming a view:

  1. `routing.detect_intent(question)` — does any deterministic route fire? **All twelve
     returned `none`.** Every one took the fact path; not one reached an engine.
  2. IS THE GOVERNING FACT IN THE SERVED 184-ROW INDEX? Checked by reading candidate rows, not
     by a narrow regex — a first pass with tight patterns reported 9 of 12 facts "ABSENT" and
     was WRONG about most of them (R34: a defect inferred from a pattern is not a defect).

Step 2 is what caught two bad adjudications of my own: `eval_239`'s index row asserts the
two-stage WCF chain with a regulation citation, so the GOLD was the stale claim; `eval_186`'s
row is specific where I had called the gold a hedge.

Usage:  python eval/controls/classify_bar_a_closability_2026_10_09.py
Artifact: eval/results/bar_a_closability_2026_10_09.json
Exit 0 — a classification, not a gate. Exit 1 if a claim here no longer reproduces.
"""
import io
import json
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO)
INDEX = os.path.join(REPO, "kaggle", "rag_facts_text.json")
ADJ = os.path.join(REPO, "eval", "results", "false_pass_adjudication_0e11c3d.json")
OUT = os.path.join(REPO, "eval", "results", "bar_a_closability_2026_10_09.json")

# ── THE CLASSIFICATION ───────────────────────────────────────────────────────────────────
# `fact_row` is the index row that governs the answer; `None` means genuinely absent. Each is
# asserted below against the live index, so a row number that moves fails loudly rather than
# decaying into a stale pin.
C = {
    "eval_086": dict(
        verdict="ROUTE", fact_row=9, needle="asilimia 10",
        engine="rules_engine.levy_rate_statement('nssf')",
        evidence="THE ENGINE ALREADY EMITS THE CORRECT ANSWER: 'Kiwango cha NSSF ni asilimia 20 "
                 "ya mshahara ghafi ... (asilimia 10 mwajiri + asilimia 10 mfanyakazi).' And "
                 "`routing.asks_rate()` ALREADY RETURNS TRUE for this question. The blocker is "
                 "`detect_intent`, which returns 'none' without an amount in the text, so the "
                 "rate branch at orchestrator.py:393 is unreachable — it is gated on "
                 "`computation_type`, which is None. R31's FIFTH INSTANCE: an engine reachable "
                 "only by a question carrying a figure the asker had no reason to supply.",
        also="⚠️ AND THE INDEX ROW INVITES THE ERROR. Row 9 reads 'mwajiri analipa asilimia 10 "
             "YA MSHAHARA WA MFANYAKAZI' — 'of the employee's salary' — which is exactly the "
             "phrasing the reply echoed as 'deducted FROM the employee's salary'. Row 9 needs "
             "the gold's own clause: the employer pays it from its own funds and it is not "
             "deducted. That is a one-row wording fix, not a model problem.",
        guard_possible=True,
        guard_note="Also guardable: party-vs-constant is a constant comparison (R19), the "
                   "D-FIDELITY-6 shape. But the route is strictly better — it ANSWERS."),
    "eval_130": dict(
        verdict="ROUTE", fact_row=5, needle="asilimia 3.5",
        engine="rules_engine.levy_rate_statement('sdl')",
        evidence="The engine's SDL branch already answers 'how does an employer compute SDL' "
                 "correctly and completely: 'Kiwango cha SDL ni asilimia 3.5 — hakitegemei "
                 "mshahara wa mtu mmoja. SDL hutozwa kwa JUMLA ya mishahara ya wafanyakazi "
                 "wote, na tu kwa mwajiri mwenye wafanyakazi 10 au zaidi ... nipe jumla ya "
                 "mishahara na idadi ya wafanyakazi ili nihesabu.' `detect_intent('Mwajiri "
                 "anahesabu kiasi cha SDL cha kulipa kwa mwezi vipi?')` = 'none'.",
        guard_possible=True,
        guard_note="A guard IS available and it is narrower than it looks: 'divide by a "
                   "percentage rate' is never correct for a levy, so 'kugawanya ... kwa "
                   "<rate>%' is a comparison against a fixed RULE, not against a derived "
                   "amount. It escapes R19's impossibility because the thing being checked is "
                   "the OPERATION, not the quantity — which is why no figure-comparing rule "
                   "can see it and a verb-level one can."),
    "eval_394": dict(
        verdict="CORPUS+ROUTE", fact_row=None,
        engine="rules_engine.supports_applicability('nssf') is already True",
        evidence="NO INDEX ROW STATES THAT NSSF HAS NO HEADCOUNT THRESHOLD — and the exact "
                 "analogue exists for WCF at row 66: 'WCF applies to ALL employers in Mainland "
                 "Tanzania from the first employee. There is NO minimum employee count "
                 "threshold. Contrast with SDL which requires 10+ employees.' rates.py carries "
                 "`SDL_MIN_EMPLOYEES = 10` and `WCF_MIN_EMPLOYEES = 1  # no threshold` and NO "
                 "NSSF equivalent, so the contrast the reply got wrong is already modelled for "
                 "the neighbouring levy and simply absent for this one. One index row mirroring "
                 "row 66, plus the applicability route, closes it.",
        guard_possible=True,
        guard_note="Guardable as a constant comparison: any headcount qualifier attached to "
                   "NSSF is wrong, because NSSF has no such constant. D-FIDELITY-7's shape (a "
                   "threshold asserted where none exists), pointed at a levy instead of a tax."),
    "eval_304": dict(
        verdict="MODEL", fact_row=82, needle="NOT on the number of employees",
        evidence="THE SHARPEST INSTANCE IN THE SET. Index row 82 contains the denial VERBATIM: "
                 "'The choice between a business name and a company depends on the desired "
                 "legal structure and liability, NOT on the number of employees or the amount "
                 "of capital — there is no employee-count or capital threshold that forces "
                 "incorporation.' The reply invented precisely that threshold ('business name "
                 "if <=20 employees and capital up to TZS 100,000,000'). The fact was served "
                 "and contradicted.",
        guard_possible=True,
        guard_note="Guardable, and the guard already exists in another subject: D-FIDELITY-7 "
                   "flags a turnover threshold asserted where none exists. Extending its "
                   "subject table to the BRELA form choice is the natural move and needs the "
                   "same pre-wiring price (sweep every stored reply and gold first)."),
    "eval_338": dict(
        verdict="MODEL", fact_row=17, needle="6%",
        evidence="TWO DEDICATED ROWS, both correct and both cited: row 16 'VAT withholding on "
                 "goods is 3% ... (Finance Act 2025, VAT Act s.5(5))' and row 17 'on services "
                 "is 6% ...'. The reply opened 'Hapana' and then confirmed 18% for services, "
                 "never mentioning 6% or 3%.",
        guard_possible=True,
        guard_note="Constant comparison, D-FIDELITY-6's exact shape: a rate attributed to the "
                   "wrong levy. 18 is the VAT rate, not the VAT WITHHOLDING rate. Note "
                   "rate_statement.py deliberately omits VAT withholding because it has no "
                   "constant in rates.py — adding one is a locked_facts sync job, which is why "
                   "this is not already a ROUTE."),
    "eval_237": dict(
        verdict="MODEL", fact_row=37, needle="7 DAYS after end of the calendar month",
        evidence="Index row 37 is unambiguous and pre-empts the exact error: 'wht deadline: "
                 "Withholding tax must be remitted within 7 DAYS after end of the calendar "
                 "month — NOT 7th of following month'. The reply said 'siku 7 baada ya mwisho "
                 "wa MWEZI UNAOFUATA' — one word, a month late.",
        guard_possible=True,
        guard_note="Guardable but harder than a figure check: the defect is a PERIOD QUALIFIER "
                   "('unaofuata'), not a number, so the rule has to parse the phrase rather "
                   "than compare a magnitude. Still a constant comparison, so still buildable."),
    "eval_162": dict(
        verdict="MODEL", fact_row=91, needle="Cap.357",
        evidence="Index row 91 defines it by statute: \"GN487A defines 'non-citizen' by "
                 "reference to the Tanzania Citizenship Act Cap.357 R.E.2023...\". The reply "
                 "inverted the definition — asserting a Tanzanian CITIZEN is a 'mgeni' under "
                 "three invented numbered criteria.",
        guard_possible=False,
        guard_note="Not cleanly guardable: the error is a DEFINITION inversion with fabricated "
                   "structure, not a constant comparison. A lexical rule for 'raia wa Tanzania "
                   "ni mgeni' would be narrow and brittle, and the fabricated criteria are "
                   "open-ended. This is model-layer work."),
    "eval_171": dict(
        verdict="MODEL", fact_row=56, needle="licence expiry",
        evidence="Index row 56 IS the gold's relief: 'gn487a transitional provision: "
                 "Non-citizens with valid licences at 28 July 2025 may continue until licence "
                 "expiry. No renewal permitted.' The reply never mentioned it and instead "
                 "advised restructuring — partnering with or selling to a Tanzanian — which "
                 "rows 21 and 22 identify as the facilitation offence.",
        guard_possible=True,
        guard_note="GUARDABLE AND THE HIGHEST-VALUE ONE IN THE SET, because the harm is "
                   "concrete: recommending partnership/sale/licence-transfer to a Tanzensian "
                   "in a GN487A context contradicts a stated PROHIBITION, which is a constant. "
                   "Narrow, checkable, and it stops advice that carries TZS 10M + 6 months."),
    "eval_104": dict(
        verdict="MODEL", fact_row=3, needle="'Form P9' is Kenyan",
        evidence="The index does not merely lack the P9 — IT EXPLICITLY FORBIDS IT. Row 3: "
                 "\"'Form P9' is Kenyan (KRA) terminology -- Tanzania's TRA has no form by that "
                 "name; do not use it.\" Row 4 repeats it for the P45. The reply named 'fomu ya "
                 "NSSF P9' anyway. ⚠️ The DOCUMENT LIST itself (employer form, BRELA "
                 "certificate, TIN, national IDs) is absent from the index, so the row is part "
                 "coverage gap and part instruction-ignored.",
        guard_possible=True,
        guard_note="A named-instrument check is trivially a constant comparison: P9/P45 must "
                   "never appear as a Tanzanian form. The index already asserts it."),
    "eval_223": dict(
        verdict="CORPUS", fact_row=None,
        evidence="GENUINELY ABSENT. No index row carries the USD 2,000 consignment threshold, "
                 "the Common List, or the Simplified Certificate of Origin. This is **Tier 1B "
                 "(EAC STR), which CLAUDE.md Section 5 records as NOT STARTED and gated behind "
                 "the Tier 1A gate passing.** The row is testing an unbuilt tier.",
        guard_possible=False,
        guard_note="Nothing to guard against — there is no constant in the system. ⛔ The real "
                   "finding is CORPUS COMPOSITION: an in-corpus accuracy bucket should not "
                   "contain questions about a tier we have deliberately not built. It depresses "
                   "A2 without naming a defect anyone can fix, which is the opposite of what "
                   "Bar A is for."),
    # PARTIAL / WRONG_GOLD rows, carried so the population is the whole adjudicated set
    "eval_186": dict(
        verdict="GOLD", fact_row=87, needle="halazimiki kumwajiri afisa maalum",
        evidence="Row 87 is specific and sourced where the GOLD says the threshold is "
                 "unconfirmed: 'HAPANA, mwajiri halazimiki kumwajiri afisa maalum. Ukiwa na "
                 "wafanyakazi zaidi ya 20, unateua mwakilishi ... ni kuteua, si kuajiri'. So "
                 "the gold needs re-sourcing. The model still erred on POLARITY — 'Ndiyo' to "
                 "an afisa question its own row answers 'HAPANA'.",
        guard_possible=False, guard_note="Fix the gold first; the polarity error is model-layer."),
    "eval_239": dict(
        verdict="GOLD", fact_row=46, needle="GN 185/2016",
        evidence="The model reproduced row 46 correctly, citation and all. THE GOLD is the "
                 "stale claim, and so is CLAUDE.md Section 11's 'Occupational disease "
                 "reporting: 7 working days from date of diagnosis'.",
        guard_possible=False,
        guard_note="Nothing to guard — correct the gold and the locked fact."),
}


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:                                                # noqa: BLE001
        pass
    idx = json.load(io.open(INDEX, encoding="utf-8"))
    adj = json.load(io.open(ADJ, encoding="utf-8"))

    from chike import routing

    findings = []
    rows_out = []
    adj_by_id = {r["id"]: r for r in adj["rows"]}

    for qid, c in C.items():
        a = adj_by_id.get(qid)
        if not a:
            findings.append(f"{qid} is not in the adjudication artifact")
            continue
        # 1. the route measurement, re-derived every run
        intent = routing.detect_intent(a["question_sw"])
        if intent != "none":
            findings.append(f"{qid}: detect_intent is now {intent!r}, not 'none' — a route "
                            f"has become reachable and this classification is stale")
        # 2. the index claim, asserted against the live index
        fr = c.get("fact_row")
        if fr is None:
            pass
        elif fr >= len(idx):
            findings.append(f"{qid}: claimed fact row {fr} is out of range")
        elif c.get("needle") and c["needle"].lower() not in idx[fr].lower():
            findings.append(
                f"{qid}: row {fr} no longer contains {c['needle']!r} — the index moved under "
                f"this classification (stale pin)")
        rows_out.append({
            "id": qid, "closability": c["verdict"],
            "adjudication": a["verdict"], "defect": a["defect"],
            "detect_intent": intent,
            "governing_fact_row": fr,
            "fact_in_served_index": fr is not None,
            "engine": c.get("engine"),
            "guard_possible": c.get("guard_possible"),
            "guard_note": c.get("guard_note"),
            "evidence": c["evidence"], "also": c.get("also"),
            "in_fact_path": a["in_fact_path"],
        })

    from collections import Counter
    tally = Counter(r["closability"] for r in rows_out)
    in_index = sum(1 for r in rows_out if r["fact_in_served_index"])
    guardable = sum(1 for r in rows_out if r["guard_possible"])

    payload = {
        "_what": "every adjudicated defect of gate 0e11c3d classified by what could take it "
                 "out of the model's hands: a deterministic route, a guard, or nothing we have",
        "_method": ["routing.detect_intent(question) — re-derived every run",
                    "is the governing fact IN the served 184-row index — read, not regexed"],
        "gate": "gate_production_0e11c3d.json",
        "tally": dict(tally),
        "facts_present_in_served_index": f"{in_index}/{len(rows_out)}",
        "guardable": f"{guardable}/{len(rows_out)}",
        "all_twelve_routed_to_fact_path": True,
        "_the_conclusion": (
            "EVERY ONE of the twelve returned detect_intent='none' — not one reached an "
            "engine. And for 10 of the 12 the governing fact was IN the served index, often "
            "stating the denial verbatim (row 82 denies eval_304's invented threshold; row 3 "
            "forbids eval_104's P9; row 37 pre-empts eval_237's month shift). So Bar A's "
            "residue is NOT a retrieval or corpus problem: it is the model contradicting what "
            "it was handed. TWO ROUTES and ONE CORPUS ROW aside, the methods that have worked "
            "here (index content, retrieval wording) do not reach any of it. 8 of 12 are "
            "guardable, which closes the WRONG-ANSWER half (A1) and moves A2 not at all — so "
            "guards make this safe, not correct. Closing Bar A's A2 needs the model layer or a "
            "much wider deterministic surface."),
        "_what_this_does_not_settle": (
            "RANK. Whether each present fact was RETRIEVED into the context is unmeasured here "
            "— the standing diagnosis order says measure rank first, and that needs the e5 "
            "harness in eval/index_quality/, which is `integration`-marked for segfault risk. "
            "If a present fact was at a bad rank, the row is retrieval work after all. 'In the "
            "index' is a necessary condition for 'the model ignored it', not a sufficient one."),
        "rows": sorted(rows_out, key=lambda r: (r["closability"], r["id"])),
        "findings": findings,
    }
    with io.open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)

    print(f"classified {len(rows_out)} rows\n")
    for v in ("ROUTE", "CORPUS+ROUTE", "CORPUS", "MODEL", "GOLD"):
        sel = [r for r in rows_out if r["closability"] == v]
        if not sel:
            continue
        print(f"{v}  ({len(sel)})")
        for r in sel:
            g = "guardable" if r["guard_possible"] else "not guardable"
            fr = f"row {r['governing_fact_row']}" if r["fact_in_served_index"] else "ABSENT"
            print(f"   {r['id']:10s} {'(fact path)' if r['in_fact_path'] else '':12s} "
                  f"fact {fr:9s} · {g} · {r['defect']}")
        print()
    print(f"governing fact present in the served index: {in_index}/{len(rows_out)}")
    print(f"guardable (A1 only, never A2):              {guardable}/{len(rows_out)}")
    print(f"deterministic routes reached:               0/{len(rows_out)}")
    print(f"\nartifact: {os.path.relpath(OUT, REPO)}")
    if findings:
        print(f"\n{len(findings)} STALE CLAIM(S):")
        for f in findings:
            print(f"  - {f}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
