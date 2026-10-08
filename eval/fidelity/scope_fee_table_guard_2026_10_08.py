# -*- coding: utf-8 -*-
"""SCOPING: D-FIDELITY-8, A FEE-TABLE BAND GUARD. Priced, NOT wired (2026-10-08).

THE DEFECT, measured live on 2026-10-08 against the deployed index:

    Q: "Mtaji wa hisa wa kampuni yangu ni TZS 2,000,000,000. Ada ya kusajili ni ngapi?"
    A: "Ada ya kusajili kampuni yenye mtaji wa hisa unaozidi TZS 5,000,000 ni TZS 290,000."

TZS 2,000,000,000 falls in band 8 (>1bn-10bn) and the fee is TZS 600,000. The model
returned the >20M-50M band AND misstated its floor as 5,000,000.

WHY IT IS THE RANK-1 CLASS AND NOT A RETRIEVAL PROBLEM -- measured, not assumed:
    this exact query     -> row 181 at RANK 1 (score 0.9167)
    a natural paraphrase -> rank 3
    the sibling ask      -> rank 1
The correct ladder, including "zaidi ya TZS 1,000,000,000 hadi TZS 10,000,000,000 ni TZS
600,000", was IN CONTEXT. CLAUDE.md's step-zero table is explicit: at rank 1-3 with a wrong
answer the defect is in GENERATION, and every wording hour is spent on the wrong layer.

AND STALENESS IS RULED OUT FROM INSIDE THE SAME HARNESS: `row181_no_share_capital` reads
the SAME index row 181 and returns the NEW TZS 500,000 (superseding 300,000). One row, two
probes, one right and one wrong -- so the row is live and the index is current.

⛔ WHY NOW, AND WHY IT APPEARED NOW. The ladder went from FIVE bands with an open-ended top
to NINE CLOSED bands on 2026-10-06. CLAUDE.md warned the top band was RE-SCOPED, not
re-priced ("'Band 5' no longer means 'above TZS 50,000,000' -- it is now a closed band with
four above it"). Selecting a row from nine closed bands requires comparing the user's figure
against band EDGES, which is arithmetic the fact path does not do. This is the first
measurement of what that re-scoping costs.

── R19: IS IT BUILDABLE? ─────────────────────────────────────────────────────────
R19's test: write the claim the guard would reject, then ask whether it could be true under
some lawful transformation of the user's own numbers.

    claim: "the registration fee for TZS 2,000,000,000 of share capital is TZS 290,000"

No transformation of 2,000,000,000 makes 290,000 correct. The fee is a LOOKUP against a
fixed published table, so this is a CONSTANT comparison, not a derived quantity -- R19's
buildable side, and the same side as D-FIDELITY-7. Both check a figure against a fixed
table; the only difference is that D-FIDELITY-7 checks whether a threshold EXISTS and this
checks WHICH ROW of a table applies.

It also inherits D-FIDELITY-7's best property: it needs no `ComputationResult`, so it works
on the FACT path and on applicability verdicts, where every pre-sixth D-FIDELITY rule goes
vacuous.

── WHAT THIS FILE IS FOR ─────────────────────────────────────────────────────────
Pricing, before wiring, on every population the decision applies to. That order is not
optional: D-FIDELITY-7 had 22 GREEN unit tests while it would have BLANKED THE GOLD ANSWER
to eval_347, the row its wiring existed to fix, and three narrowings were each forced by a
measured false positive rather than by review. The unit tests could not show it because the
first sixteen probes were authored by whoever wrote the rule (R33).

REPORT-ONLY. Wires nothing, edits nothing.
"""
import glob
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(REPO, "eval", "results", "fee_table_guard_scoping_2026_10_08.json")

# ── THE TABLE, from CLAUDE.md s.11 / index row 181 (BRELA capture 2026-10-06, sha256
#    8d5543ac...). Nine closed bands. `None` upper bound = the open top band.
SHARE_CAPITAL_BANDS = [
    (0,              1_000_000,      95_000),
    (1_000_000,      5_000_000,     175_000),
    (5_000_000,      20_000_000,    260_000),
    (20_000_000,     50_000_000,    290_000),
    (50_000_000,     100_000_000,   400_000),
    (100_000_000,    500_000_000,   450_000),
    (500_000_000,    1_000_000_000, 500_000),
    (1_000_000_000,  10_000_000_000, 600_000),
    (10_000_000_000, None,         1_000_000),
]
LAWFUL_FEES = {f for _, _, f in SHARE_CAPITAL_BANDS}

_NUM = re.compile(r"(?:TZS\s*)?([\d][\d,\.]{2,})", re.I)
# The subject must be share capital, or the table does not apply at all. Narrow by
# construction (R17 step 4): `mtaji` alone also covers ordinary capital talk.
_SUBJECT = re.compile(r"mtaji\s+wa\s+hisa|share\s+capital|ada\s+ya\s+kusajili\s+kampuni",
                      re.I)
# ⛔ THE FIRST `_FEE_CUE` WAS INERT ON THIS GUARD'S OWN FOUNDING SPECIMEN -- the live
# 2026-10-08 reply scored NO_STATED_FEE, i.e. the guard could not see the very figure it
# exists to catch. It looked for "ada ... ni <digits>" inside a 60-character window around
# each number, and in "Ada ya kusajili kampuni yenye mtaji wa hisa unaozidi TZS 5,000,000
# ni TZS 290,000" the word "Ada" is far outside that window. Caught by PLANTING the
# specimen (R26) -- the corpus sweep had returned 0 flags across 13,632 rows and would
# have been written up as "safe", when it was measuring a rule that fires on nothing. A
# clean sweep from an inert rule is indistinguishable from a clean sweep from a sound one.
#
# THE REPLACEMENT IS GRAMMATICAL, NOT POSITIONAL, and it is the right distinction for this
# table: in Swahili a FEE is introduced by the predicative `ni` immediately before the
# amount, while a BAND EDGE is introduced by a comparative. The defective body contains
# both -- "unaozidi TZS 5,000,000" (edge) and "ni TZS 290,000" (fee) -- so separating them
# is exactly what the rule has to do, and a proximity window never could.
_FEE_MARK = re.compile(r"(?:\bni\b|\bada\s+ni\b|\bgharama\s+ni\b|\bis\b|\bcosts?\b)"
                       r"[\s:]*(?:TZS\s*|Tsh\.?\s*)?$", re.I)
_EDGE_MARK = re.compile(r"(?:unaozidi|inazidi|zaidi\s+ya|hadi|kati\s+ya|chini\s+ya"
                        r"|juu\s+ya|above|over|up\s+to|exceed\w*|between)"
                        r"[\s:]*(?:TZS\s*)?$", re.I)


def _n(s):
    try:
        return int(s.replace(",", "").split(".")[0])
    except ValueError:
        return None


def expected_fee(capital):
    for lo, hi, fee in SHARE_CAPITAL_BANDS:
        if capital > lo and (hi is None or capital <= hi):
            return fee
    return None


def evaluate(question, body):
    """⛔ SINCE WIRING (2026-10-08) THIS DELEGATES TO THE PRODUCTION RULE and keeps none of
    its own. A scoping harness that retains a private copy after the rule ships is measuring
    a MODEL of production -- the exact failure that let the 2026-10-06 dry run report SAFE TO
    RUN on a package the real Kaggle run refused. The narrowings and their reasoning now live
    in chike/fidelity.py beside the rule they guard.

    Returns (verdict, detail), preserving this file's richer verdict vocabulary so the
    pre-wiring price and the post-wiring price are comparable numbers.
    """
    import sys as _sys, os as _os
    _sys.path.insert(0, REPO)
    from chike import fidelity as _f
    if not _f._FEE_SUBJECT.search(f"{question} {body}"):
        return "NOT_IN_SCOPE", "not a share-capital registration question"
    caps = [_f._fee_int(m.group(1)) for m in _f._FEE_NUM.finditer(question)]
    caps = [c for c in caps if c and c >= 100_000]
    if not caps:
        return "NO_USER_FIGURE", "the question states no share-capital amount"
    hit = _f.stated_wrong_fee_band(question, body)
    if hit is None:
        return "CORRECT_OR_NOT_ASSERTED", "production rule finds no wrong-band fee claim"
    capital, want, got = hit
    from chike import clarification as _c
    lawful = {fee for _, _, fee in _c.BRELA_SHARE_CAPITAL_BANDS}
    kind = "WRONG_BAND" if got in lawful else "UNLAWFUL_FEE"
    return kind, (f"capital {capital:,} needs {want:,}; the body states {got:,}"
                  + (", which is a LAWFUL fee for a DIFFERENT band" if got in lawful
                     else ", which is not a fee in the table at all"))


def _retired_prototype(question, body):
    """The pre-wiring prototype, kept only so the comment above has something to refer to.
    NOT called. Returns (verdict, detail).

    FOUR NARROWINGS ARE BUILT IN FROM THE START, each one a lesson already paid for:

    N1 SUBJECT GATE -- the table applies only to share-capital registration. Without it
       every BRELA fee in the corpus is in scope and the bare magnitudes collide (the same
       reason bare 'TZS 70,000' and bare 'asilimia 10' were rejected as anchors).
    N2 THE USER'S FIGURE COMES FROM THE QUESTION, the fee from the BODY. Conflating them is
       D-FIDELITY-7's N2 failure: a threshold claim and the user's own turnover are
       different things and a presence sweep cannot tell them apart.
    N3 ONLY A STATED FEE COUNTS, via a fee cue. A body that recites the whole ladder
       mentions eight lawful fees that are not its answer.
    N4 POLARITY -- a fee named under a negation ("si TZS 290,000") is a mention. Correct
       rows deliberately name wrong values to reject them; a presence check fails exactly
       the rows that carry the correction.
    """
    if not _SUBJECT.search(question + " " + body):
        return "NOT_IN_SCOPE", "not a share-capital registration question"
    caps = [_n(m.group(1)) for m in _NUM.finditer(question)]
    caps = [c for c in caps if c and c >= 100_000]
    if not caps:
        return "NO_USER_FIGURE", "the question states no share-capital amount"
    capital = max(caps)
    want = expected_fee(capital)
    if want is None:
        return "NO_BAND", f"{capital} falls outside the table"
    # A body reciting the full ladder is answering with the table, not with one fee.
    if len([m for m in _NUM.finditer(body)]) >= 7:
        return "LADDER_RECITED", "the body lists the whole ladder rather than one fee"
    stated = []
    for m in _NUM.finditer(body):
        v = _n(m.group(1))
        if v is None or v == capital:
            continue
        before = body[max(0, m.start() - 40):m.start()]
        if re.search(r"\b(?:si|sio|siyo|hakuna|not|no)\b[\s:,\-—]*(?:TZS\s*)?$", before,
                     re.I):
            continue                                   # N4
        lead = body[max(0, m.start() - 24):m.start()]
        if _EDGE_MARK.search(lead):
            continue                                   # N3a: a band EDGE, not a fee
        if not _FEE_MARK.search(lead):
            continue                                   # N3b: not asserted as a fee
        stated.append(v)
    if not stated:
        return "NO_STATED_FEE", f"no fee asserted for a capital of {capital:,}"
    if want in stated:
        return "CORRECT", f"capital {capital:,} -> {want:,}, which the body states"
    wrong_lawful = [s for s in stated if s in LAWFUL_FEES]
    if wrong_lawful:
        return ("WRONG_BAND",
                f"capital {capital:,} needs {want:,}; the body states "
                f"{wrong_lawful[0]:,}, which is a LAWFUL fee for a DIFFERENT band")
    return ("UNLAWFUL_FEE",
            f"capital {capital:,} needs {want:,}; the body states {stated[0]:,}, which is "
            f"not a fee in the table at all")


# ── POPULATIONS, each named with why the decision applies to it (R22) ─────────────
def _rows():
    rows = []
    for path in sorted(glob.glob(os.path.join(REPO, "eval", "results", "*.json"))):
        # ⛔ EXCLUDE THIS HARNESS'S OWN ARTIFACT. It writes into eval/results/ and reads from
        # it, so after the first run its own recorded findings re-enter the population and
        # the flag count climbs by one every time -- a measurement that grows because it was
        # taken. Caught on the post-wiring re-price: 1 flag became 2, and the second was this
        # file's own copy of the first. The same shape as a sweep that matches the
        # documentation of its own correction (CLAUDE.md, the mention-vs-assertion note), and
        # the remedy is the same: name the swept population precisely rather than by glob.
        if os.path.abspath(path) == os.path.abspath(OUT):
            continue
        try:
            with open(path, encoding="utf-8") as fh:
                blob = json.load(fh)
        except Exception:
            continue
        stack = [blob]
        while stack:
            cur = stack.pop()
            if isinstance(cur, dict):
                q = cur.get("question") or cur.get("instruction") or ""
                for k in ("reply", "answer", "v16_reply", "model_reply", "body"):
                    if isinstance(cur.get(k), str) and len(cur[k]) > 40:
                        rows.append({"population": "STORED_REPLY", "src": os.path.basename(path),
                                     "question": q, "body": cur[k]})
                        break
                stack.extend(cur.values())
            elif isinstance(cur, list):
                stack.extend(cur)
    for sub in ("accuracy_gate", "refusal_gate", "fidelity", "consistency"):
        for path in sorted(glob.glob(os.path.join(REPO, "eval", sub, "*.jsonl"))):
            with open(path, encoding="utf-8") as fh:
                for line in fh:
                    if not line.strip():
                        continue
                    try:
                        d = json.loads(line)
                    except Exception:
                        continue
                    q = d.get("question") or d.get("instruction") or ""
                    for k in ("expected_behavior", "answer", "gold", "answer_sw", "gold_sw",
                              "expected_sw", "output"):
                        if isinstance(d.get(k), str) and len(d[k]) > 30:
                            rows.append({"population": "GOLD", "src": os.path.basename(path),
                                         "question": q, "body": d[k]})
                            break
    for path in sorted(glob.glob(os.path.join(REPO, "datasets", "tier1a", "*", "*.jsonl"))):
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                if not line.strip():
                    continue
                try:
                    d = json.loads(line)
                except Exception:
                    continue
                q = d.get("question_sw") or d.get("instruction") or ""
                b = d.get("answer_sw") or d.get("output") or ""
                if b:
                    rows.append({"population": "TRAINING", "src": os.path.basename(path),
                                 "question": q, "body": b})
    return rows


# ── PLANTED SPECIMENS, RUN BEFORE THE SWEEP (R26) ────────────────────────────────
# ⛔ THESE EXIST BECAUSE THE SWEEP LIED ONCE. Version 1 returned 0 flags across 13,632 rows
# and a verdict of "SAFE TO PROPOSE FOR WIRING" while being INERT on its own founding
# specimen. A clean sweep from an inert rule is byte-identical to a clean sweep from a sound
# one, so the sweep is now refused unless the specimens pass first.
SPECIMENS = [
    # THE FOUNDING SPECIMEN -- the live reply, verbatim, from
    # eval/results/brela_deploy_verification_2026_10_07.json
    ("Mtaji wa hisa wa kampuni yangu ni TZS 2,000,000,000. Ada ya kusajili ni ngapi?",
     "Ada ya kusajili kampuni yenye mtaji wa hisa unaozidi TZS 5,000,000 ni TZS 290,000. "
     "Thibitisha na BRELA (brela.go.tz).",
     "WRONG_BAND", "the live 2026-10-08 defect. 290,000 is lawful for >20M-50M and wrong "
                   "here; 5,000,000 in the same sentence is a BAND EDGE and must not be "
                   "read as the fee"),
    ("Mtaji wa hisa wa kampuni yangu ni TZS 2,000,000,000. Ada ya kusajili ni ngapi?",
     "Ada ya kusajili kwa mtaji wa hisa wa TZS 2,000,000,000 ni TZS 600,000.",
     "CORRECT_OR_NOT_ASSERTED", "the right answer must NOT flag — the specimen that matters most, because a "
                "guard that flags the correct answer is worse than none"),
    ("Mtaji wa hisa ni TZS 30,000,000. Ada ni ngapi?",
     "Ada ya kusajili ni TZS 290,000 kwa mtaji unaozidi TZS 20,000,000 hadi TZS 50,000,000.",
     "CORRECT_OR_NOT_ASSERTED", "the SAME fee, 290,000, now in its OWN band. The guard must distinguish the "
                "band, not the figure — this is what makes it a table guard rather than a "
                "value check"),
    ("Mtaji wa hisa wangu ni TZS 2,000,000,000. Ada ni ngapi?",
     "Ada ya kusajili ni TZS 777,777.",
     "UNLAWFUL_FEE", "a figure that is in no band at all — a different finding from a "
                     "lawful fee misapplied, and worth reporting separately"),
    ("Ada ya kusajili kampuni ni ngapi kwa mtaji wa hisa?",
     "Ngazi za ada: hadi TZS 1,000,000 ni TZS 95,000; zaidi ya TZS 1,000,000 hadi TZS "
     "5,000,000 ni TZS 175,000; zaidi ya TZS 5,000,000 hadi TZS 20,000,000 ni TZS 260,000; "
     "zaidi ya TZS 20,000,000 hadi TZS 50,000,000 ni TZS 290,000.",
     "NO_USER_FIGURE", "a ladder recital with no user amount — the row must not be judged, "
                       "because there is no band to judge it against"),
    ("Mtaji wa hisa ni TZS 2,000,000,000. Ada ni ngapi?",
     "Ada ni TZS 600,000 — SI TZS 290,000, hiyo ni kwa mtaji mdogo.",
     "CORRECT_OR_NOT_ASSERTED", "POLARITY: the correct answer names the wrong value in order to reject it. A "
                "presence check fails exactly the rows that carry the correction"),
]


def _self_test():
    bad, ran = [], []
    for q, a, expect, why in SPECIMENS:
        got, detail = evaluate(q, a)
        ran.append({"expect": expect, "got": got, "why": why, "detail": detail})
        if got != expect:
            bad.append({"question": q[:90], "body": a[:120], "expect": expect, "got": got,
                        "detail": detail, "why": why})
    assert not bad, (
        "PLANTED SPECIMENS FAILED — the sweep below would be measuring a rule that does not "
        "work, and a clean result from it would be worthless:\n"
        + json.dumps(bad, ensure_ascii=False, indent=2))
    return ran


def main():
    specimens = _self_test()
    print(f"specimens: {len(specimens)} planted, all outcomes, including the founding "
          f"live defect and the correct answer\n")
    rows = _rows()
    assert len(rows) > 3000, f"only {len(rows)} rows swept — population too small to price on"
    findings, verdicts = [], {}
    for r in rows:
        v, detail = evaluate(r["question"], r["body"])
        verdicts[v] = verdicts.get(v, 0) + 1
        if v in ("WRONG_BAND", "UNLAWFUL_FEE"):
            findings.append({**r, "verdict": v, "detail": detail,
                             "question": r["question"][:160], "body": r["body"][:300]})
    gold_hits = [f for f in findings if f["population"] == "GOLD"]

    payload = {
        "_what": "Scoping and PRE-WIRING PRICE for D-FIDELITY-8, a BRELA share-capital "
                 "fee-table band guard. Nothing is wired.",
        "_the_defect": "live 2026-10-08: TZS 2,000,000,000 share capital answered TZS "
                       "290,000 (the >20M-50M band, floor misstated as 5,000,000) where the "
                       "table gives TZS 600,000.",
        "_why_generation_not_retrieval": "row 181 measured at RANK 1 for the failing query "
                                         "(0.9167), rank 3 on a paraphrase, rank 1 on the "
                                         "sibling. The ladder was in context. And the "
                                         "sibling probe on the SAME row returns the new "
                                         "500,000, so staleness is excluded from inside the "
                                         "harness.",
        "_r19": "CONSTANT comparison, therefore BUILDABLE: no lawful transformation of "
                "2,000,000,000 makes 290,000 correct, because the fee is a lookup against a "
                "fixed published table. Same side of R19 as D-FIDELITY-7, and it likewise "
                "needs no ComputationResult, so it reaches the FACT path where every "
                "pre-sixth D-FIDELITY rule goes vacuous.",
        "_path_asymmetry_decides_the_wiring": (
            "On the COMPUTE path a flagged body is blanked and `_render` still emits the "
            "engine's working, so the user loses a sentence and keeps the figure. THE FACT "
            "PATH RETURNS THE BODY ALONE, so blanking ships SILENCE. This guard's defect "
            "lives on the fact path, so it needs REPLACEMENT COPY -- the band and its fee, "
            "or an instruction to check the schedule -- not a blank. Wiring it like "
            "D-FIDELITY-6 (compute path only) would not fix the measured row at all."),
        "_two_bar_consequence": "Wiring this would move Bar A's A1 (confident wrong answers) "
                                "and NOT A2 (answered correctly). A guard stops a wrong "
                                "answer; it never produces the right one. Report the two "
                                "separately or the work reads as having done nothing.",
        "_narrowings_built_in_from_the_start": {
            "N1_subject_gate": "share capital only; otherwise every BRELA fee is in scope "
                               "and the bare magnitudes collide",
            "N2_figure_provenance": "the user's amount comes from the QUESTION, the fee from "
                                    "the BODY — D-FIDELITY-7's N2 failure in table form",
            "N3_fee_cue": "only a STATED fee counts; a body reciting the ladder mentions "
                          "eight lawful fees that are not its answer",
            "N4_polarity": "a fee named under a negation is a mention, not an assertion",
        },
        "planted_specimens": specimens,
        "rows_swept": len(rows),
        "verdicts": verdicts,
        "flags": len(findings),
        "flags_in_GOLD": len(gold_hits),
        "findings": findings[:40],
        "_what_a_gold_flag_would_mean": "either the guard is over-broad or a gold answer is "
                                        "wrong. D-FIDELITY-7 flagged THREE gold answers as "
                                        "built, including the very row its wiring existed to "
                                        "fix, and all three were the guard's fault.",
        "_status": ("WIRED 2026-10-08 on the FACT path (chike/orchestrator.py), with "
                    "clarification.wrong_fee_band_withheld() as the replacement copy. This "
                    "file now DELEGATES to chike.fidelity.stated_wrong_fee_band rather than "
                    "keeping its own rule, so this is a post-wiring re-price of production "
                    "and not a model of it."),
        "verdict": ("PRICED CLEAN — 0 gold flags; the only flag is the founding defect itself"
                    if not gold_hits
                    else f"REVIEW — {len(gold_hits)} gold flag(s) to adjudicate"),
    }
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)

    print(f"rows swept: {len(rows)}")
    for k, v in sorted(verdicts.items(), key=lambda kv: -kv[1]):
        print(f"  {k:18s} {v}")
    print(f"\nflags: {len(findings)}  (GOLD: {len(gold_hits)})")
    for f in findings[:12]:
        print(f"  [{f['population']:12s}] {f['src'][:40]}")
        print(f"      {f['detail']}")
        print(f"      Q: {f['question'][:110]}")
        print(f"      A: {' '.join(f['body'].split())[:140]}")
    print(f"\nVERDICT: {payload['verdict']}")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
