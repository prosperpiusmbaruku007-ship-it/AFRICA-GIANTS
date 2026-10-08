# -*- coding: utf-8 -*-
"""R16 LIVE VERIFICATION OF THE D-FIDELITY-8 DEPLOY (2026-10-08).

⛔ READ THIS FIRST: THE DEPLOY THAT PRECEDED THIS RUN TOOK PRODUCTION DOWN FOR ~3 MINUTES,
AND IT WAS MY ERROR. `modal app stop chike-inference --yes` succeeded instantly; the
replacing deploy then ABORTED because `.env({'CHIKE_BUILD': BUILD})` had been chained AFTER
`add_local_file`/`add_local_dir`, and Modal requires local-file adds to be the last
operations in an image chain. Fixed by moving `.env()` before them; redeploy succeeded in
8.6s. Recorded in modal_app.py at the site.

The generalisable half: R16's step 1 is usually read as "force fresh containers". It is
really "force fresh containers AND be certain the replacing deploy BUILDS", because the stop
is instant and irreversible while the deploy is not. This is the SECOND time that window has
cost real downtime -- 2026-08-10 was a console-encoding abort on the CLI's own ✓ glyph. Two
different causes, one window.

⛔ AND THIS IS THE FIRST VERIFICATION IN THIS PROJECT THAT DOES NOT HAVE TO INFER WHAT IS
SERVING. `/health` was added hours ago to close a gap R16b left open for eight weeks, and it
answered on first use:

    build                 5d1ed71   == the deployed commit
    build_matches         true      == web tier and GPU tier agree, so no warm container
    rag_rows_loaded       184
    rag_facts_text_sha256 19bcfabb… == EXPECTED_SERVED_SHA256 in the committed test

So the index identity is an EQUALITY CHECK rather than a probe whose discriminating power
depends on someone thinking of the right question. The probes below test BEHAVIOUR, which is
a different claim and still needed.

THE PROBES, as the founder specified them:
  1. the 2B share-capital question -- PRIMARY. Must now return the TABLE, not TZS 290,000.
  2. the no-share-capital question -- must STILL return TZS 500,000. That answer was CORRECT
     in the same live run and reads the SAME index row 181, so the guard must not touch it.
     This is the probe that would catch an over-broad guard, and it is the one that matters
     most: a guard that replaces a correct answer is worse than no guard.
  3. row 172 -- TZS 70,000, the row the previous cycle shipped.
  4. the standard negatives -- local 2,500; annual return 22,000; NSSF; row 57; config-only.

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
OUT = os.path.join(REPO, "eval", "results", "fee_band_guard_live_2026_10_08.json")
ENDPOINT = "https://prosperpiusmbaruku007--chike-inference-web-endpoint.modal.run"
HEALTH = "https://prosperpiusmbaruku007--chike-inference-health.modal.run"
EXPECTED_BUILD = "5d1ed71"
EXPECTED_SERVED_SHA256 = (
    "19bcfabb887c49643268b9a5659ae31d90d31a982fb42930a250b23d6f5ae405")

NEGATED = (r"(?:\bsi\b|\bsio\b|\bsiyo\b|\bnot\b|\bhapana\b|\bhakuna\b|\bhaina\b"
           r"|\bsupersedes\b|\bya\s+zamani\b)[\s:,—-]*(?:TZS\s*|USD\s*)?$")

# The replacement copy's signature: the RULE sentence plus the ladder opener. Matched on the
# rule rather than on any single figure, because a figure could appear in a wrong answer too.
LADDER_SIGNATURE = r"inategemea\s+mtaji\s+wa\s+hisa.{0,80}ngazi|Ngazi\s+za\s+ada:"


def token():
    p = os.path.expanduser("~/.chike_modal_token.txt")
    return (os.environ.get("CHIKE_MODAL_TOKEN")
            or (open(p, encoding="utf-8").read().strip() if os.path.exists(p) else ""))


def asserted(pattern, text):
    return [m.group(0) for m in re.finditer(pattern, text, re.I)
            if not re.search(NEGATED, text[max(0, m.start() - 20):m.start()], re.I)]


PROBES = [
    {
        "id": "fee_band_guard_PRIMARY_2bn",
        "limb": "deploy",
        "proves": "PRIMARY. The question that produced the defect must now return the TABLE, "
                  "not TZS 290,000. This is the row D-FIDELITY-8 exists for.",
        "source": "regen critical_queries 'BRELA share-capital ladder now has nine bands'",
        "question": "Mtaji wa hisa wa kampuni yangu ni TZS 2,000,000,000. "
                    "Ada ya kusajili ni ngapi?",
        "baseline_committed_row": "live 2026-10-08 BEFORE the guard: 'Ada ya kusajili kampuni "
                                  "yenye mtaji wa hisa unaozidi TZS 5,000,000 ni TZS 290,000.'",
        "must_match": LADDER_SIGNATURE,
        "must_not_assert": r"ni\s+TZS\s*290,?000\s*\.|ada\s+(?:yako\s+)?ni\s+TZS\s*290,?000",
        "observe": r"600,?000",
        "note": "must_not_assert targets 290,000 STATED AS THE FEE, not its appearance in the "
                "ladder, where it is correct for the >20M-50M band. A presence check would "
                "fail the replacement copy itself -- the deleting-direction trap in reverse.",
    },
    {
        "id": "no_share_capital_UNTOUCHED",
        "limb": "deploy",
        "proves": "⛔ THE OVER-BREADTH PROBE, and the one that matters most. This answer was "
                  "CORRECT in the same live run (TZS 500,000, superseding 300,000) and reads "
                  "the SAME index row 181. The guard must not touch it: the question states "
                  "no share-capital AMOUNT, so there is no band to be wrong about. A guard "
                  "that replaces a correct answer is worse than no guard.",
        "source": "verify_brela_deploy_live_2026_10_07.py row181_no_share_capital",
        "question": "Kampuni yangu haina mtaji wa hisa. Ada ya kusajili ni shilingi ngapi?",
        "must_match": r"500,?000",
        "must_not_match": LADDER_SIGNATURE,
        "note": "must_not_match is the guard NOT firing. If the ladder copy appears here, "
                "D-FIDELITY-8 is over-broad and has replaced a right answer with a table.",
    },
    {
        "id": "row172_brela_foreign_penalty",
        "limb": "deploy",
        "proves": "The row the previous cycle shipped must still serve TZS 70,000. A redeploy "
                  "is exactly when a prior ship silently regresses.",
        "source": "regen critical_queries 'BRELA foreign late-filing fee' (ext_15 verbatim)",
        "question": "Tawi letu la kampuni ya kigeni limechelewa kuwasilisha ripoti ya mwaka. "
                    "Adhabu ni tofauti na kampuni za huku?",
        "must_match": r"70,?000",
        "must_not_assert": r"USD\s*25\b|\$\s*25\b|dola\s*25\b",
    },
    {
        "id": "negative_local_late_penalty_2500",
        "limb": "deploy",
        "proves": "NEGATIVE: a LOCAL company's late-filing penalty is TZS 2,500/month. Both "
                  "limbs are now in shillings, so they can displace each other.",
        "source": "index row 99",
        "question": "Kampuni yangu ya hapa Tanzania imechelewa kuwasilisha ritani ya mwaka. "
                    "Faini ni shilingi ngapi kwa mwezi?",
        "must_match": r"2,?500",
        "must_not_assert": r"70,?000",
    },
    {
        "id": "negative_annual_return_fee_22000",
        "limb": "deploy",
        "proves": "NEGATIVE: the annual return FILING FEE is unchanged at TZS 22,000, and it "
                  "sits on the same BRELA schedule the guard now reads.",
        "source": "regen critical_queries 'BRELA annual return'",
        "question": "Ada ya annual return BRELA ni shilingi ngapi?",
        "must_match": r"22,?000",
        "must_not_match": LADDER_SIGNATURE,
        "note": "must_not_match: a BRELA fee question that is NOT about share capital must "
                "not trip the guard. N1, the subject gate, tested live.",
    },
    {
        "id": "negative_nssf_fine_unchanged",
        "limb": "deploy",
        "proves": "NEGATIVE: the Cap.50 corrections from 2026-10-05 must be where they were. "
                  "Accepts EITHER locked statutory limb -- s.76(1)'s ceiling or s.14(3)'s "
                  "5%/month -- because the question licenses both and demanding one made a "
                  "correct reply fail on 2026-10-07 (R38).",
        "source": "regen critical_queries 'NSSF fine ceiling is ten million'",
        "question": "Nisipolipa michango ya NSSF kabisa, nitatozwa faini ya kiasi gani?",
        "must_match": r"10,?000,?000|milioni\s+kumi|asilimia\s*5\b|5\s*%",
        "must_not_assert": r"100[,.]?000(?![,.\d])|laki\s+moja",
    },
    {
        "id": "negative_row57_efd_unchanged",
        "limb": "deploy",
        "proves": "NEGATIVE: row 57 must not re-assert the fabricated TZS 11,000,000 EFD "
                  "threshold. Accepts D-FIDELITY-7's withheld-answer copy, which is that "
                  "guard WORKING -- scoring it as a regression was my error on 2026-10-07.",
        "source": "regen critical_queries 'EFD threshold' (eval_347 verbatim)",
        "question": "Kizingiti cha kuanza kutumia EFD ni mauzo ya TZS 200,000,000, sivyo?",
        "must_not_assert": r"11[,.]?000[,.]?000|milioni\s+kumi\s+na\s+moja",
        "must_match": r"haina\s+kizingiti|hakuna\s+kizingiti|bila\s+kujali|hakitumiki"
                      r"|sikiwezi\s+kukithibitisha|sitakisii|sitalitumia",
        "withheld_signature": r"sikiwezi\s+kukithibitisha|sitakisii|sitalitumia",
    },
    {
        "id": "config_only_phrase",
        "limb": "deploy",
        "proves": "CONFIG LOADING, separately from code -- the diagnostic that distinguishes a "
                  "config failure from a stale warm container.",
        "source": "chike_config.json ooc_phrases (config-only, not in the code fallback)",
        "question": "Nataka kuuza kiwanja changu, kodi ya mapato ni kiasi gani?",
        "must_match": r"sina uhakika|thibitisha|siwezi|nje ya",
    },
]


def ask(question, tok, timeout=600):
    req = urllib.request.Request(
        f"{ENDPOINT}?token={tok}",
        data=json.dumps({"message": question}).encode("utf-8"),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def health(tok):
    """The new build endpoint, read rather than inferred. Its whole purpose is that this
    verification no longer has to deduce what is serving from behaviour."""
    try:
        with urllib.request.urlopen(f"{HEALTH}?deep=1&token={tok}", timeout=600) as r:
            h = json.loads(r.read().decode("utf-8"))
    except Exception as exc:
        return {"error": f"{type(exc).__name__}: {str(exc)[:200]}"}
    served = h.get("served") or {}
    h["_checks"] = {
        "build_is_the_deployed_commit": h.get("build") == EXPECTED_BUILD,
        "web_and_gpu_tiers_agree": h.get("build_matches") is True,
        "served_index_digest_matches": (
            served.get("rag_facts_text_sha256") == EXPECTED_SERVED_SHA256),
        "rows_match_config": served.get("rag_rows_loaded") == served.get(
            "config_rag_fact_count"),
    }
    return h


def save(rows, h):
    deploy_bad = [r for r in rows if r.get("limb", "deploy") == "deploy"
                  and r.get("verdict") in ("FAIL", "ERROR")]
    hc = (h or {}).get("_checks") or {}
    payload = {
        "_what": "R16 live verification of the D-FIDELITY-8 (fee-band guard) deploy.",
        "_endpoint": ENDPOINT,
        "_downtime_incident": (
            "The deploy preceding this run took production down ~3 minutes: `modal app stop` "
            "succeeded and the replacing deploy ABORTED because `.env()` was chained after "
            "`add_local_*`, which Modal requires to be last. My error, fixed at the site. "
            "R16 step 1 is 'force fresh containers AND be certain the replacing deploy "
            "BUILDS' -- the stop is instant and irreversible, the deploy is not. Second time "
            "this window has cost downtime (2026-08-10 was a console-encoding abort)."),
        "_health_is_read_not_inferred": (
            "First verification in this project that does not deduce what is serving. "
            "/health was added hours ago to close a gap R16b left open for eight weeks, and "
            "the served index identity is now an EQUALITY against a committed digest rather "
            "than a probe whose power depends on someone thinking of the right question."),
        "health": h,
        "totals": {"probes": len(PROBES), "run": len(rows),
                   "pass": len([r for r in rows if r.get("verdict") == "PASS"]),
                   "fail": len([r for r in rows if r.get("verdict") == "FAIL"]),
                   "error": len([r for r in rows if r.get("verdict") == "ERROR"])},
        "verdict": ("DEPLOY VERIFIED"
                    if (rows and not deploy_bad and len(rows) == len(PROBES)
                        and all(hc.values()) and hc)
                    else "INCOMPLETE OR FAILED"),
        "answer_withheld_by_guard": [r["id"] for r in rows if r.get("answer_withheld")],
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

    h = health(tok)
    print("health:", json.dumps(h.get("_checks", h.get("error")), ensure_ascii=False))
    rows = []
    for p in PROBES:
        row = {k: p[k] for k in ("id", "limb", "proves", "source", "question", "note",
                                 "baseline_committed_row") if k in p}
        try:
            resp = ask(p["question"], tok)
            reply = str(resp.get("reply") or resp.get("answer") or resp)
            row["reply"] = reply
            checks = {}
            if p.get("must_match"):
                checks["must_match"] = bool(re.search(p["must_match"], reply, re.I))
            if p.get("must_not_match"):
                checks["guard_did_not_fire"] = not re.search(
                    p["must_not_match"], reply, re.I)
            if p.get("must_not_assert"):
                bad = asserted(p["must_not_assert"], reply)
                checks["superseded_value_not_asserted"] = not bad
                if bad:
                    row["asserted_superseded"] = bad
            if p.get("observe"):
                row["observed"] = bool(re.search(p["observe"], reply, re.I))
            if p.get("withheld_signature"):
                row["answer_withheld"] = bool(
                    re.search(p["withheld_signature"], reply, re.I))
            row["checks"] = checks
            row["verdict"] = "PASS" if all(checks.values()) else "FAIL"
        except Exception as exc:
            row["verdict"] = "ERROR"
            row["error"] = f"{type(exc).__name__}: {str(exc)[:200]}"
        rows.append(row)
        save(rows, h)
        print(f"[{row['verdict']:5s}] {row['id']}")
        if row.get("reply"):
            print(f"        {' '.join(row['reply'].split())[:250]}")
        if row.get("checks"):
            extra = f" observed={row['observed']}" if "observed" in row else ""
            print(f"        checks={row['checks']}{extra}")
        if row.get("asserted_superseded"):
            print(f"        ⛔ ASSERTED SUPERSEDED: {row['asserted_superseded']}")
        if row.get("error"):
            print(f"        {row['error']}")

    payload = save(rows, h)
    print(f"\n{payload['totals']}")
    print(f"VERDICT: {payload['verdict']}")
    for i in payload["answer_withheld_by_guard"]:
        print(f"  ANSWER WITHHELD BY GUARD (A1 win, A2 still owed): {i}")
    print(f"wrote {OUT}")
    sys.exit(0 if payload["verdict"] == "DEPLOY VERIFIED" else 1)


if __name__ == "__main__":
    main()
