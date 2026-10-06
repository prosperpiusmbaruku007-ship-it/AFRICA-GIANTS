# -*- coding: utf-8 -*-
"""R16 LIVE VERIFICATION OF THE ROW-57 DEPLOY (2026-10-06).

"✓ App deployed" is NOT verification, and this deploy returned in 6.1 SECONDS against 150s for
the previous one -- the image and mounts were cached. That is precisely the condition R16 was
written for: a fast deploy is the one most likely to be serving what was already there.

THE THREE ORDERED CHECKS:
  1. row 57 must no longer ASSERT an 11M threshold
  2. its sibling (efd_not_every_business) must still say EFD applies regardless of turnover
  3. the new critical query's claim must be what the corrected row answers with

plus a config-only probe and two negatives.

⚠️ POLARITY, NOT PRESENCE, on check 1. Row 57 deliberately NAMES TZS 11,000,000 in order to
reject it ("Na SI TZS 11,000,000"), because corpus rows assert the figure and an explicit
contradiction is what overrides a trained prior. A presence check would fail the very behaviour
being verified -- and a shell-quoting bug in exactly this pattern already produced one false
"ASSERTED" verdict during the pre-commit check, so the rule is applied here through the same
tested helper rather than re-typed.

BASELINE, from the committed artifact rather than memory (R24): index row 57 at 59cf784 read
"Kizingiti cha kuanza kutumia mashine ya EFD: mauzo ya TZS 11,000,000 (milioni kumi na moja)
kwa mwaka." -- a fabricated threshold (TAA Cap.438 R.E.2023 s.44 sets none), live for five and
a half weeks after the 2026-08-29 re-verification found it invented.

STRUCTURAL WRITE DISCIPLINE: artifact rewritten after EVERY row, per-row errors captured.
"""
import json
import os
import re
import sys
import urllib.request

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(REPO, "eval", "results", "row57_deploy_verification_2026_10_06.json")
ENDPOINT = "https://prosperpiusmbaruku007--chike-inference-web-endpoint.modal.run"

NEGATED = r"(?:\bsi\b|\bsio\b|\bsiyo\b|\bnot\b|\bhapana\b|\bhakuna\b|\bhaina\b)[\s:,—-]*(?:TZS\s*)?$"


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
        "id": "row57_no_11m_assertion",
        "proves": "CHECK 1: row 57 no longer ASSERTS an 11M EFD turnover threshold. Scored on "
                  "polarity -- the row names the figure to reject it, by design.",
        "source": "eval/accuracy_gate/eval_questions_003.jsonl eval_347 (verbatim)",
        "question": "Kizingiti cha kuanza kutumia EFD ni mauzo ya TZS 200,000,000, sivyo?",
        "baseline_committed_row": "row 57 @ 59cf784 = 'Kizingiti cha kuanza kutumia mashine ya "
                                  "EFD: mauzo ya TZS 11,000,000 (milioni kumi na moja) kwa "
                                  "mwaka.'",
        "must_not_assert": r"11[,.]?000[,.]?000|milioni\s+kumi\s+na\s+moja|14[,.]?000[,.]?000",
        "must_match": r"haina\s+kizingiti|hakuna\s+kizingiti|bila\s+kujali|hakitumiki",
        "observe": r"200,?000,?000",
        "note": "eval_347 is a FALSE-PREMISE question. must_match looks for the no-threshold "
                "claim; observe records whether the 200M/VAT contrast survived.",
    },
    {
        "id": "row57_new_guard_claim",
        "proves": "CHECK 3: the new critical query's anchor ('EFD haina kizingiti cha mauzo') "
                  "is what the corrected row actually answers with -- a retrieval guard can "
                  "pass while the reply says something else, so this asks the model, not the "
                  "index.",
        "source": "kaggle/regenerate_rag_e5.py critical_queries 'EFD threshold' (new anchor)",
        "question": "EFD inaanza kutumika kwa mauzo ya kiasi gani kwa mwaka?",
        "must_not_assert": r"11[,.]?000[,.]?000|milioni\s+kumi\s+na\s+moja",
        "must_match": r"haina\s+kizingiti|hakuna\s+kizingiti|bila\s+kujali|kila\s+mfanyabiashara",
        "note": "Deliberately NOT the guard's own query -- a second phrasing of the same "
                "question, so a pass is not an artefact of one wording (R33).",
    },
    {
        "id": "sibling_unchanged",
        "proves": "CHECK 2: efd_not_every_business must STILL say EFD applies regardless of "
                  "turnover. It was the correct row of the contradictory pair, and the whole "
                  "risk of rewriting its sibling is displacing it.",
        "source": "kaggle/regenerate_rag_e5.py critical_queries 'EFD not-every-business "
                  "(Q16 verbatim)'",
        "question": "Duka langu dogo halifikishi mauzo makubwa kila siku, bado nahitaji "
                    "mashine ya risiti?",
        "must_match": r"ndiyo|unahitaji|lazima|bila\s+kujali|hakuna\s+kizingiti",
        "must_not_assert": r"11[,.]?000[,.]?000|milioni\s+kumi\s+na\s+moja",
        "observe": r"kamishna|commissioner|tangazo|taarifa\s+rasmi",
        "note": "observe looks for the exemption mechanism (CG public notice), which is the "
                "limb this row carries and row 57 deliberately does not.",
    },
    {
        "id": "negative_vat_threshold_not_displaced",
        "proves": "NEGATIVE: the genuine VAT-registration threshold must NOT have been "
                  "displaced by row 57's 200M contrast. The old comment flagged exactly this "
                  "risk, and correcting the figure does not remove it.",
        "source": "kaggle/regenerate_rag_e5.py anti-displacement bracket guard",
        "question": "Kizingiti cha kusajili VAT ni mauzo ya kiasi gani kwa mwaka?",
        "must_match": r"200,?000,?000|milioni\s+mia\s+mbili",
        "must_not_assert": r"11[,.]?000[,.]?000",
        "note": "VAT registration is TZS 200M/12mo. If this moved, narrow row 57's 200M "
                "contrast (the GN487A narrowing precedent).",
    },
    {
        "id": "config_only_phrase",
        "proves": "CONFIG LOADING, separately from code -- the diagnostic that distinguishes a "
                  "config failure from a stale warm container, which a 6-second deploy makes "
                  "the live question.",
        "source": "chike_config.json ooc_phrases (config-only, not in the code fallback)",
        "question": "Nataka kuuza kiwanja changu, kodi ya mapato ni kiasi gani?",
        "must_match": r"sina uhakika|thibitisha|siwezi|nje ya",
        "note": "Land sale is out of corpus by design.",
    },
    {
        "id": "negative_nssf_fine_unchanged",
        "proves": "SECOND NEGATIVE, on the rows shipped YESTERDAY. One row changed in this "
                  "regen; the Cap.50 corrections must be exactly where they were.",
        "source": "eval/controls/verify_cap50_deploy_2026_10_05.py fine_ceiling_reachable",
        "question": "Faini ya juu kabisa kwa kosa la NSSF ni shilingi ngapi?",
        "must_match": r"10,?000,?000|milioni\s+kumi",
        "must_not_assert": r"100[,.]?000(?![,.\d])|laki\s+moja",
        "note": "Ten million, s.76(1). Also re-confirms yesterday's ship survived this one.",
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
        "_what": "R16 live verification of the row-57 deploy (2026-10-06).",
        "_endpoint": ENDPOINT,
        "_deployed_index": "184 rows, HF commit 63dfb0cbdd built from 59cf784, dual-committed. "
                           "rag_fact_count unchanged at 184.",
        "_why_r16_matters_here": "this deploy returned in 6.1s against 150s for the previous "
                                 "one -- image and mounts cached, which is exactly when a "
                                 "deploy is most likely to be serving what was already there.",
        "_scoring": "must_not_assert is POLARITY-checked. Row 57 names TZS 11,000,000 under a "
                    "negation by design; a presence check would fail the behaviour being "
                    "verified, and a quoting bug in this very pattern already produced one "
                    "false ASSERTED verdict today.",
        "_write_discipline": "rewritten after EVERY row; per-row errors captured, never fatal",
        "totals": {"probes": len(PROBES), "run": len(rows),
                   "pass": len([r for r in rows if r.get("verdict") == "PASS"]),
                   "fail": len(failed), "error": len(errored)},
        "verdict": ("DEPLOY VERIFIED" if rows and not failed and not errored
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
                                 "baseline_committed_row") if k in p}
        try:
            resp = ask(p["question"], tok)
            reply = str(resp.get("reply") or resp.get("answer") or resp)
            row["reply"] = reply
            checks = {}
            if p.get("must_match"):
                checks["must_match"] = bool(re.search(p["must_match"], reply, re.I))
            if p.get("must_not_assert"):
                bad = asserted(p["must_not_assert"], reply)
                checks["superseded_value_not_asserted"] = not bad
                if bad:
                    row["asserted_superseded"] = bad
                row["mentions_under_negation"] = bool(
                    re.search(p["must_not_assert"], reply, re.I)) and not bad
            if p.get("observe"):
                row["observed"] = bool(re.search(p["observe"], reply, re.I))
            row["checks"] = checks
            row["verdict"] = "PASS" if all(checks.values()) else "FAIL"
        except Exception as exc:
            row["verdict"] = "ERROR"
            row["error"] = f"{type(exc).__name__}: {str(exc)[:200]}"
        rows.append(row)
        save(rows)
        print(f"[{row['verdict']:5s}] {row['id']}")
        if row.get("reply"):
            print(f"        {' '.join(row['reply'].split())[:230]}")
        if row.get("checks"):
            extra = ""
            if "observed" in row:
                extra += f" observed={row['observed']}"
            if row.get("mentions_under_negation"):
                extra += " (old value mentioned under a negation -- correct)"
            print(f"        checks={row['checks']}{extra}")
        if row.get("asserted_superseded"):
            print(f"        ⛔ ASSERTED SUPERSEDED: {row['asserted_superseded']}")
        if row.get("error"):
            print(f"        {row['error']}")

    payload = save(rows)
    print(f"\n{payload['totals']}")
    print(f"VERDICT: {payload['verdict']}")
    print(f"wrote {OUT}")
    sys.exit(0 if payload["verdict"] == "DEPLOY VERIFIED" else 1)


if __name__ == "__main__":
    main()
