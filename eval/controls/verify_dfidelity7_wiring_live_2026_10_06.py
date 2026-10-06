# -*- coding: utf-8 -*-
"""R16 LIVE VERIFICATION OF THE D-FIDELITY-7 WIRING (2026-10-06).

"✓ App deployed in 6.5s" is NOT verification, and a 6-second deploy is precisely the condition
R16 was written for — image and mounts cached, so it is the deploy most likely to be serving what
was already there. `modal app stop chike-inference --yes` ran first, so containers are cold.

THE PRIMARY CHECK IS eval_347 VERBATIM, because that exact string is what failed six hours ago:

    "Hapana. Kizingiti cha kuanza kutumia EFD ni mauzo ya TZS 11,000,000 (TZS 10M +).
     Si TZS 200,000,000. Thibitisha na TRA (tra.go.tz)."

Row 57 had already been corrected and sits at RANK 1 for both phrasings, so there is no
index-side headroom: the fabrication is generated, and the guard layer is the only one that can
reach it. After wiring, this question must no longer carry an 11M assertion.

THE NEGATIVES ARE THE POINT OF THIS RUN, not an afterthought. This guard REMOVES TEXT, and on
the fact path removal means replacement copy instead of an answer. A false positive therefore
costs a whole answer, and the cost lands on a user where we cannot see it (the ⛔ block above
R17). So:

  * BOTH EFD PHRASINGS. The second phrasing already answered CORRECTLY before the wiring; if the
    guard catches it, the wiring has traded one wrong answer for one destroyed right answer.
  * THE THREE GOLD ANSWERS the unnarrowed rule would have blanked are asked live, not just
    checked offline — eval_347, eval_355, eval_331. Offline the guard sees the gold TEXT; live it
    sees what the model generates for that question, which is a different string.
  * The VAT registration threshold, which must still be answerable with 200,000,000. It is a
    lawful threshold and the guard must never touch it.
  * Yesterday's NSSF fine ship, re-confirmed.

SCORING IS POLARITY-BASED, through the same tested helper as the row-57 run: a reply that names
TZS 11,000,000 in order to REJECT it is correct, and a presence check would fail the behaviour
being verified. A shell-quoting bug in exactly this pattern produced one false "ASSERTED" verdict
on 2026-10-06 already.

STRUCTURAL WRITE DISCIPLINE: artifact rewritten after EVERY row, per-row errors captured, never
fatal. A long live run whose artifact is written once at the end can lose everything to anything.
"""
import json
import os
import re
import sys
import urllib.request

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(REPO, "eval", "results", "dfidelity7_wiring_live_2026_10_06.json")
ENDPOINT = "https://prosperpiusmbaruku007--chike-inference-web-endpoint.modal.run"

NEGATED = (r"(?:\bsi\b|\bsio\b|\bsiyo\b|\bnot\b|\bhapana\b|\bhakuna\b|\bhaina\b)"
           r"[\s:,—–-]*(?:TZS\s*)?$")
FABRICATION = r"11[,.]?000[,.]?000|milioni\s+kumi\s+na\s+moja|\b11\s*M\b|milioni\s+11"
# The replacement copy the fact-path branch returns. Matching it is how a REPLACED reply is told
# apart from a reply that merely happens not to contain the figure.
WITHHELD = r"sikiwezi kukithibitisha|sitakisii kiwango kingine"


def token():
    p = os.path.expanduser("~/.chike_modal_token.txt")
    return (os.environ.get("CHIKE_MODAL_TOKEN")
            or (open(p, encoding="utf-8").read().strip() if os.path.exists(p) else ""))


def asserted(pattern, text):
    """Occurrences NOT preceded by a negation. 'si TZS 11,000,000' is CORRECT."""
    return [m.group(0) for m in re.finditer(pattern, text, re.I)
            if not re.search(NEGATED, text[max(0, m.start() - 16):m.start()], re.I)]


PROBES = [
    {
        "id": "PRIMARY_eval_347_verbatim",
        "proves": "THE PRIMARY CHECK. The exact question whose live reply asserted a fabricated "
                  "TZS 11,000,000 EFD threshold six hours ago, with the corrected row at rank 1.",
        "source": "eval/accuracy_gate/eval_questions_003.jsonl eval_347 (verbatim)",
        "question": "Kizingiti cha kuanza kutumia EFD ni mauzo ya TZS 200,000,000, sivyo?",
        "pre_wiring_reply": "Hapana. Kizingiti cha kuanza kutumia EFD ni mauzo ya TZS 11,000,000 "
                            "(TZS 10M +). Si TZS 200,000,000. Thibitisha na TRA (tra.go.tz).",
        "pre_wiring_artifact": "eval/results/row57_deploy_verification_2026_10_06.json",
        "must_not_assert": FABRICATION,
        "note": "PASS = the fabrication is gone. It may be gone because the answer is now "
                "correct OR because the guard replaced it; `outcome` below records which, and "
                "the second is a STOP, not a fix -- it still scores as a gate miss.",
    },
    {
        "id": "NEGATIVE_efd_second_phrasing",
        "proves": "THE LOAD-BEARING NEGATIVE. This phrasing answered CORRECTLY before the "
                  "wiring. If the guard catches it, the wiring traded one wrong answer for one "
                  "DESTROYED right answer -- the expensive direction, and invisible to us.",
        "source": "eval/controls/verify_row57_deploy_2026_10_06.py row57_new_guard_claim",
        "question": "EFD inaanza kutumika kwa mauzo ya kiasi gani kwa mwaka?",
        "pre_wiring_reply": "Hakuna kizingiti cha mauzo kilichowekwa...",
        "must_match": r"haina\s+kizingiti|hakuna\s+kizingiti|bila\s+kujali|kila\s+mfanyabiashara",
        "must_not_match": WITHHELD,
        "must_not_assert": FABRICATION,
        "note": "must_not_match is the withheld copy: a correct answer must NOT be replaced.",
    },
    {
        "id": "NEGATIVE_gold_eval_355_live",
        "proves": "A gold question the UNNARROWED rule would have blanked. Asked live, because "
                  "offline the guard sees the gold TEXT while live it sees what the model "
                  "generates -- a different string.",
        "source": "eval/accuracy_gate/eval_questions_003.jsonl eval_355 (verbatim)",
        "question": "Mauzo yangu ni TZS 10,999,000 kwa mwaka. Je, EFD ni lazima kwangu?",
        "must_not_match": WITHHELD,
        "note": "The gold answer states both 10,999,000 and 11,000,000 and says neither changes "
                "the answer. N2 clears it: no frame reaches either without crossing the other.",
    },
    {
        "id": "NEGATIVE_gold_eval_331_live",
        "proves": "The second gold the unnarrowed rule flagged -- via a NEGATED FRAME "
                  "('Hakuna kizingiti cha mauzo kwa EFD (TZS 9,000,000 ...)'). N1 applied to the "
                  "frame rather than only to the amount is the limb that clears it.",
        "source": "eval/accuracy_gate/eval_questions_003.jsonl eval_331 (verbatim)",
        "question": "Mauzo yangu ya mwaka ni TZS 9,000,000. Nahitaji mashine ya EFD?",
        "must_not_match": WITHHELD,
        "must_not_assert": FABRICATION,
    },
    {
        "id": "NEGATIVE_vat_threshold_untouched",
        "proves": "The genuine VAT registration threshold is a LAWFUL constant and the guard "
                  "must never touch it. If this is replaced, N3 regressed.",
        "source": "kaggle/regenerate_rag_e5.py anti-displacement bracket guard",
        "question": "Kizingiti cha kusajili VAT ni mauzo ya kiasi gani kwa mwaka?",
        "must_match": r"200,?000,?000|milioni\s+mia\s+mbili",
        "must_not_match": WITHHELD,
    },
    {
        "id": "NEGATIVE_sdl_compute_still_answers",
        "proves": "A COMPUTE-path question, because the guard was wired into that branch too "
                  "(where it blanks). The engine's working must still render -- a blanked body "
                  "with a working is fine, a missing figure is not.",
        "source": "standard compute negative",
        "question": "Nina wafanyakazi 25 na mishahara ya TZS 15,000,000 kwa mwezi, SDL ni ngapi?",
        "must_match": r"525,?000|3\.5",
        "must_not_match": WITHHELD,
    },
    {
        "id": "NEGATIVE_config_only_phrase",
        "proves": "CONFIG LOADING, separately from code -- the diagnostic that distinguishes a "
                  "config failure from a stale warm container.",
        "source": "chike_config.json ooc_phrases (config-only, not in the code fallback)",
        "question": "Nataka kuuza kiwanja changu, kodi ya mapato ni kiasi gani?",
        "must_match": r"sina uhakika|thibitisha|siwezi|nje ya",
    },
    {
        "id": "NEGATIVE_nssf_fine_still_ten_million",
        "proves": "Yesterday's Cap.50 ship, re-confirmed. One code change in this deploy; the "
                  "2026-10-05 corrections must be exactly where they were.",
        "source": "eval/controls/verify_cap50_deploy_2026_10_05.py fine_ceiling_reachable",
        "question": "Faini ya juu kabisa kwa kosa la NSSF ni shilingi ngapi?",
        "must_match": r"10,?000,?000|milioni\s+kumi",
        "must_not_assert": r"100[,.]?000(?![,.\d])|laki\s+moja",
    },
]


def ask(question, tok, timeout=300):
    req = urllib.request.Request(
        f"{ENDPOINT}?token={tok}",
        data=json.dumps({"message": question}).encode("utf-8"),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def save(rows):
    failed = [r for r in rows if r.get("verdict") == "FAIL"]
    errored = [r for r in rows if r.get("verdict") == "ERROR"]
    payload = {
        "_what": "R16 live verification of the D-FIDELITY-7 wiring (2026-10-06).",
        "_endpoint": ENDPOINT,
        "_deploy": ("app stop --yes then deploy; '✓ App deployed in 6.5s' (cached image/mounts), "
                    "which is exactly when R16 says a deploy is most likely to be stale. "
                    "Containers forced cold by the stop."),
        "_change_under_test": ("chike/orchestrator.py: fidelity.body_states_wrong_threshold "
                               "wired on BOTH paths -- compute blanks, fact replaces with "
                               "clarification.wrong_threshold_withheld."),
        "_why_the_negatives_matter_most": (
            "this guard REMOVES TEXT, and on the fact path removal means a non-answer. A false "
            "positive costs a whole answer and the cost lands on a user invisibly. Both EFD "
            "phrasings and all three gold rows the UNNARROWED rule would have blanked are asked "
            "live."),
        "_scoring": ("must_not_assert is POLARITY-checked through the same helper the row-57 run "
                     "used; naming a figure under a negation is correct behaviour."),
        "_write_discipline": "rewritten after EVERY row; per-row errors captured, never fatal",
        "totals": {"probes": len(PROBES), "run": len(rows),
                   "pass": len([r for r in rows if r.get("verdict") == "PASS"]),
                   "fail": len(failed), "error": len(errored)},
        "verdict": ("WIRING VERIFIED" if rows and not failed and not errored
                    and len(rows) == len(PROBES) else "INCOMPLETE OR FAILED"),
        "rows": rows,
    }
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
    return payload


def main():
    tok = token()
    if not tok:
        print("NO TOKEN -- cannot verify live. This is NOT a pass (R16).")
        sys.exit(2)

    rows = []
    for p in PROBES:
        row = {k: p[k] for k in ("id", "proves", "source", "question", "note",
                                 "pre_wiring_reply", "pre_wiring_artifact") if k in p}
        try:
            resp = ask(p["question"], tok)
            reply = str(resp.get("reply") or resp.get("answer") or resp)
            row["reply"] = reply
            checks = {}
            if p.get("must_match"):
                checks["must_match"] = bool(re.search(p["must_match"], reply, re.I))
            if p.get("must_not_match"):
                checks["not_replaced_by_guard"] = not re.search(p["must_not_match"], reply, re.I)
            if p.get("must_not_assert"):
                bad = asserted(p["must_not_assert"], reply)
                checks["superseded_value_not_asserted"] = not bad
                if bad:
                    row["asserted_superseded"] = bad
                row["mentions_under_negation"] = bool(
                    re.search(p["must_not_assert"], reply, re.I)) and not bad
            # WHICH outcome produced the pass: a correct answer, or the guard stopping a wrong
            # one? They are not the same result and conflating them would read a stopped wrong
            # answer as a fixed one.
            row["outcome"] = ("REPLACED_BY_GUARD" if re.search(WITHHELD, reply, re.I)
                              else "MODEL_ANSWERED")
            row["checks"] = checks
            row["verdict"] = "PASS" if all(checks.values()) else "FAIL"
        except Exception as exc:
            row["verdict"] = "ERROR"
            row["error"] = f"{type(exc).__name__}: {str(exc)[:200]}"
        rows.append(row)
        save(rows)
        print(f"[{row['verdict']:5s}] {row['id']}  ({row.get('outcome', '-')})")
        if row.get("reply"):
            print(f"        {' '.join(row['reply'].split())[:240]}")
        if row.get("checks"):
            extra = " (old value mentioned under a negation — correct)" if row.get(
                "mentions_under_negation") else ""
            print(f"        checks={row['checks']}{extra}")
        if row.get("asserted_superseded"):
            print(f"        ⛔ ASSERTED SUPERSEDED: {row['asserted_superseded']}")
        if row.get("error"):
            print(f"        {row['error']}")

    payload = save(rows)
    print(f"\n{payload['totals']}")
    print(f"VERDICT: {payload['verdict']}")
    print(f"wrote {OUT}")
    sys.exit(0 if payload["verdict"] == "WIRING VERIFIED" else 1)


if __name__ == "__main__":
    main()
