# -*- coding: utf-8 -*-
"""THE BODY AND THE WORKING DISAGREE IN THE SAME REPLY. HOW OFTEN, AND WHO IS WRONG.

⛔ THIS IS A SCOPING MEASUREMENT, NOT A GUARD, AND IT IS DELIBERATELY NOT ONE YET. Two
specimens prompted it:

  th_22     body: "Kwa mfanyakazi MMOJA: WCF = TZS 50,000 kwa mwaka (0.5% ya mshahara)"
            working: "WCF ni asilimia 0.5 ya jumla ya mishahara."
            -> the body invents an ANNUAL SHILLING AMOUNT from a salary nobody gave. The
               engine sentence beside it is correct, and the judge voted CORRECT 5/5.

  eval_394  body: "Hapana, si ya hiari."     working: "Ndiyo."
            -> reads as a flat self-contradiction in two adjacent sentences.

D-FIDELITY-5's precedent is the reason this file exists before any blanking code: price the
rule over every stored reply FIRST, because the unnarrowed D-FIDELITY-7 would have BLANKED THE
GOLD ANSWER to the row it was built to fix, with 22 unit tests green.

⛔⛔ AND THE SCOPING ALREADY OVERTURNS THE PREMISE OF THE TASK, WHICH IS WHY IT RAN FIRST.
"Blank the body when it disagrees with the working" is the wrong remedy for eval_394, because
**the body is the correct half.** The question is "Je, NSSF si ya hiari?" — a NEGATED premise.
"Hapana, si ya hiari" (no, it is not optional) is right; the engine's bare "Ndiyo" is answering
the un-negated question. `rules_engine.agree_with_negated_premise` exists for exactly this and
the applicability renderer does not consult it. Blanking the body there would DELETE THE RIGHT
ANSWER and keep the confusing one — R37's direction, manufactured on purpose.

So the two specimens are two different defects wearing one symptom, and a single rule aimed at
"disagreement" would get one of them backwards. That is the finding, and it is the kind that
only a population measurement produces: th_22 is a FABRICATION in the body (the body is wrong)
and eval_394 is a POLARITY defect in the working (the working is wrong).

POPULATION, re-derived rather than guessed. `_render` returns `body\nworking` for a compute
answer, so the split point is not inferable from the text — a body can contain newlines. This
runs the REAL orchestrator offline with a sentinel body, which yields the exact deterministic
`working` string for each question, then checks whether the stored live reply ends with it. If
it does, the prefix IS the body, exactly. No regex guesses where the engine starts.

⚠️ BOUND. The offline tree is HEAD, the stored replies were served by build 054fb19, so a
question whose working changed between them is reported as `WORKING_MOVED` and excluded from
the detector arms rather than silently mis-split. That exclusion is counted, because a
population that quietly drops what it cannot handle reports a cleaner result than it earned.

Usage:  python eval/fidelity/scope_render_body_working_disagreement_2026_10_10.py
Artifact: eval/results/render_disagreement_scoping_2026_10_10.json
Exit 0 — a measurement, not a gate. Exit 2 if it could not be exercised.
"""
import glob
import io
import json
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO)
OUT = os.path.join(REPO, "eval", "results",
                   "render_disagreement_scoping_2026_10_10.json")

SENTINEL = "⁣SENTINEL-BODY⁣"

# Artifacts that record a question AND the reply that was served for it. Named file by file:
# "whatever the glob found" is not a population, and a measurement script is not a route to a
# user so it does not belong in one.
REPLY_ARTIFACTS = [
    "eval/results/gate_production_0e11c3d.json",
    "eval/results/targeted_route_verification_2026_10_09.json",
    "eval/results/statement_route_live_2026_10_09.json",
    "eval/results/diverted_rows_live_2026_10_09.json",
]

_MONEY = re.compile(r"(?:TZS|shilingi)\s*([\d][\d,\.]{2,})|([\d][\d,\.]{5,})", re.I)
_YES = re.compile(r"^\s*(?:ndiyo|ndio|hakika)\b", re.I)
_NO = re.compile(r"^\s*(?:hapana|la,|si\b)", re.I)


def _norm(s):
    return re.sub(r"\s+", " ", (s or "")).strip()


def _walk(obj):
    if isinstance(obj, dict):
        yield obj
        for v in obj.values():
            yield from _walk(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from _walk(v)


def _stored_replies():
    """[(source, id, question, reply)] — deduplicated on (id, question, reply)."""
    rows, seen = [], set()
    for rel in REPLY_ARTIFACTS:
        path = os.path.join(REPO, rel)
        if not os.path.exists(path):
            continue
        try:
            blob = json.load(io.open(path, encoding="utf-8"))
        except Exception:                                                # noqa: BLE001
            continue
        for item in _walk(blob):
            q = next((item[k] for k in ("question", "question_sw", "instruction")
                      if isinstance(item.get(k), str) and item[k].strip()), "")
            r = next((item[k] for k in ("generated", "reply", "answer", "output")
                      if isinstance(item.get(k), str) and item[k].strip()), "")
            if not q or not r:
                continue
            rid = str(item.get("id") or item.get("qid") or "?")
            fp = (rid, _norm(q)[:120], _norm(r)[:120])
            if fp in seen:
                continue
            seen.add(fp)
            rows.append({"source": rel, "id": rid, "question": q, "reply": r})
    return rows


def _money(text):
    out = []
    for m in _MONEY.finditer(text or ""):
        tok = (m.group(1) or m.group(2) or "").strip(".,")
        digits = tok.replace(",", "").replace(".", "")
        if digits.isdigit() and int(digits) >= 1000:
            out.append(int(digits))
    return out


def _polarity(text):
    head = _norm(text)[:40]
    if _YES.search(head):
        return "yes"
    if _NO.search(head):
        return "no"
    return None


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:                                                    # noqa: BLE001
        pass

    from chike.model_abstraction import FakeBackend
    from chike.orchestrator import Orchestrator

    rows = _stored_replies()
    if len(rows) < 200:
        print(f"[FATAL] only {len(rows)} stored replies found — a clean result would mean "
              f"nothing. Exit 2 is NOT a pass.")
        return 2

    pairs, no_working, working_moved = [], 0, []
    for r in rows:
        fake = FakeBackend(scripted_reply=SENTINEL)
        try:
            local = Orchestrator(backend=fake, retriever=lambda _q: []).answer(r["question"])
        except Exception as exc:                                         # noqa: BLE001
            working_moved.append({**r, "why": f"{type(exc).__name__}: {str(exc)[:100]}"})
            continue
        text = local.text or ""
        if SENTINEL not in text:
            # No model body in the rendered answer at all — a pure deterministic reply or a
            # clarification. There is no body/working pair to disagree.
            no_working += 1
            continue
        working = _norm(text.split(SENTINEL, 1)[1])
        if not working:
            no_working += 1
            continue
        stored = _norm(r["reply"])
        if not stored.endswith(working):
            working_moved.append({**r, "why": "the stored reply does not end with the locally "
                                              "derived working — the engine text moved between "
                                              "build 054fb19 and HEAD, so the split point is "
                                              "unknown and this row is NOT guessed at",
                                  "local_working": working})
            continue
        pairs.append({**r, "body": _norm(stored[:len(stored) - len(working)]),
                      "working": working})

    polarity_flags, orphan_flags, unsupported_flags = [], [], []
    for p in pairs:
        pb, pw = _polarity(p["body"]), _polarity(p["working"])
        if pb and pw and pb != pw:
            polarity_flags.append({**p, "body_polarity": pb, "working_polarity": pw})
        body_money = set(_money(p["body"]))
        work_money = set(_money(p["working"]))
        orphans = sorted(body_money - work_money)
        if orphans:
            orphan_flags.append({**p, "orphan_figures": orphans})
            # ⛔ THE NARROWING THE ADJUDICATION PRODUCED, and it is R19's line exactly.
            #
            # Of the 14 orphan flags, 13 are figures the user THEMSELVES supplied or a correct
            # step derived from one: eval_092's per-head 40,000, eval_296's TZS 18,000/day,
            # eval_395's net pay (which the question explicitly ASKED for and the engine cannot
            # produce). Blanking those is D-FIDELITY-7's unnarrowed shape — deleting the half of
            # the answer that was requested.
            #
            # th_22 is the one true positive and it differs in ONE respect: the question gives
            # NO figure at all ("Nina mfanyakazi mmoja tu — je nalipa WCF?"), so TZS 50,000 per
            # year cannot be derived from anything. That makes it a CONSTANT comparison, not a
            # derived-quantity one: with no input amount, any money figure in the body is
            # unsupported by construction, and no lawful transformation of the user's numbers
            # can make it true because there are no numbers. R19 says the first is buildable and
            # the second is not, and this is the first.
            if not _money(p["question"]):
                unsupported_flags.append({**p, "orphan_figures": orphans,
                                          "why": "the question supplies no figure, so no "
                                                 "arithmetic on the user's own numbers can "
                                                 "produce this one"})

    payload = {
        "_what": "how often a reply's model BODY disagrees with its engine WORKING, and which "
                 "half is wrong",
        "_why_not_a_guard_yet": "D-FIDELITY-5's precedent — price the rule over every stored "
                                "reply before writing blanking code. The unnarrowed "
                                "D-FIDELITY-7 would have blanked the gold answer to the row it "
                                "was built to fix, with 22 unit tests green.",
        "_the_finding_that_changes_the_design": (
            "the two founding specimens are OPPOSITE defects. th_22's BODY is wrong (it "
            "invents an annual shilling amount from a salary nobody gave) and eval_394's "
            "WORKING is wrong (a bare 'Ndiyo' answering the un-negated form of a 'si ya hiari' "
            "question, where `agree_with_negated_premise` already exists and the applicability "
            "renderer does not consult it). A single rule that blanks the body on disagreement "
            "would delete the correct half of eval_394."),
        "_population_and_why": (
            "every stored reply in the four named artifacts, re-run through the REAL "
            "orchestrator with a sentinel body so the deterministic working is derived rather "
            "than pattern-matched out of the merged text. A body can contain newlines, so no "
            "regex can find the split point; the sentinel can."),
        "_bound": ("R21/R22: the stored replies come from our own corpora and gate runs, and "
                   "the detectors below were written by the person who read the two specimens. "
                   "The flag counts are a LOWER bound on the false-positive surface, and the "
                   "population on which a blanking rule would act is this one — which is why "
                   "it is reported before any rule is written, not after."),
        "offline_tree_note": ("the working is derived at HEAD while the replies were served by "
                             "build 054fb19; rows whose working moved are excluded and counted "
                             "rather than mis-split"),
        "stored_replies": len(rows),
        "with_a_body_and_a_working": len(pairs),
        "no_working_to_disagree_with": no_working,
        "excluded_working_moved": len(working_moved),
        "detector_polarity_flags": len(polarity_flags),
        "detector_orphan_figure_flags": len(orphan_flags),
        "detector_unsupported_figure_flags": len(unsupported_flags),
        "_adjudication": {
            "_how": "every orphan flag read by hand against its question, its body and its "
                    "working — the three together, because an orphan figure is only a "
                    "fabrication relative to what the question supplied",
            "orphan_figure": {
                "flags": 14,
                "true_positive": ["th_22"],
                "false_positive_correct_body": [
                    "eval_092 — per-head breakdown reaching the working's own total",
                    "eval_280 — 18 x TZS 480,000, with the per-employee share",
                    "eval_296 — the TZS 18,000 DAILY wage the question gave",
                    "eval_360 / eval_377 / eval_191 — PAYE band edges from the band table",
                    "eval_361 — the intermediate 30% x TZS 10,000 = TZS 3,000",
                    "eval_371 / eval_372 / eval_378 — the payroll quoted while correctly "
                    "answering SDL = 0",
                    "eval_386 — TZS 250,000 + TZS 250,000 = TZS 500,000",
                    "eval_395 — NET PAY, which the question explicitly asked for and the "
                    "engine's working cannot contain",
                ],
                "false_positive_but_defective_for_another_reason": [
                    "eval_324 — 'Faida = 1,000,000 - madeni - NSSF - WCF = TZS 760,000' is "
                    "arithmetic that does not hold, and 760,000 is a PAYE band edge. A real "
                    "defect, invisible to THIS detector's logic and unbuildable per R19 "
                    "(a wrong DERIVED quantity).",
                    "eval_191 — the band LABELS are muddled ('Kanda 2 (8%): TZS 250,000' then "
                    "'Kanda 3 (20%)') while the final figure is right.",
                ],
                "precision": "1/14 = 7%",
                "verdict": "DO NOT BUILD. 11 of the 13 false positives are CORRECT bodies, and "
                           "two of them (eval_092, eval_395) would lose the exact thing the "
                           "user asked for. This is D-FIDELITY-7's unnarrowed shape.",
            },
            "unsupported_figure_narrowed": {
                "flags": len(unsupported_flags),
                "verdict": "the candidate worth designing. On this population it isolates the "
                           "one true positive and drops all 13 false positives, because every "
                           "one of them derives from a figure the question supplied.",
                "_what_it_still_does_not_do": "it stops the fabrication; it does not produce "
                           "the right answer. th_22's body would lose a sentence and keep the "
                           "engine's correct one — cheap here BECAUSE a working exists. The "
                           "same rule on the fact path would ship silence (R35's path "
                           "asymmetry), so any wiring must be compute-path only.",
                "_before_wiring": "price it over the gold answers and the training corpus too, "
                                  "not only these 64 pairs. A rule measured on 64 rows has "
                                  "been measured on 64 rows.",
            },
            "polarity": {
                "flags": len(polarity_flags),
                "distinct_rows": ["eval_394"],
                "verdict": "A REAL DISAGREEMENT WHOSE WRONG HALF IS THE WORKING. Blanking the "
                           "body here deletes the correct answer. The fix is in the "
                           "applicability renderer: 'Je, NSSF si ya hiari?' is a negated "
                           "premise and the engine answers the un-negated form. "
                           "`rules_engine.agree_with_negated_premise` already exists for this "
                           "and the renderer does not call it — R31's shape, a capability with "
                           "no caller.",
            },
        },
        "polarity_rows": polarity_flags,
        "unsupported_figure_rows": unsupported_flags,
        "orphan_figure_rows": orphan_flags[:60],
        "orphan_figure_rows_truncated_at": 60,
        "excluded_rows": working_moved[:40],
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with io.open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)

    print(f"stored replies read            {len(rows)}")
    print(f"  body + working pair          {len(pairs)}")
    print(f"  no working (fact/clarify)    {no_working}")
    print(f"  excluded, working moved      {len(working_moved)}")
    print(f"POLARITY disagreement flags    {len(polarity_flags)}")
    for f in polarity_flags[:12]:
        print(f"  {f['id']:14s} body={f['body_polarity']:3s} working={f['working_polarity']:3s}"
              f"  {f['body'][:70]}")
    print(f"ORPHAN FIGURE flags            {len(orphan_flags)}  "
          f"(adjudicated: 1 true positive, 13 false — DO NOT BUILD)")
    for f in orphan_flags:
        print(f"  {f['id']:14s} {f['orphan_figures']}  {f['body'][:70]}")
    print(f"NARROWED — no figure in the question: {len(unsupported_flags)}")
    for f in unsupported_flags:
        print(f"  {f['id']:14s} {f['orphan_figures']}  {f['body'][:70]}")
    print("\nEvery flag above needs reading by hand before any blanking rule is designed. "
          "That is the deliverable, not a verdict.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
