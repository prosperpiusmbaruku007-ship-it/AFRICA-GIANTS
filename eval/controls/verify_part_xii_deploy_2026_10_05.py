# -*- coding: utf-8 -*-
"""R16 LIVE VERIFICATION OF THE 2026-10-05 PART XII / rent_wht_rate DEPLOY.

"✓ App deployed" is NOT verification (R16). This exercises the specific changes, includes
negatives, and includes a CONFIG-ONLY probe -- the diagnostic that on 2026-08-07 separated "the
config did not load" from "a warm container is serving old code", which are indistinguishable
from the deploy log alone.

THE ROW THAT MATTERS IS ext_15. Production served the REVERSED foreign-company citation from
2026-08-31 to 2026-10-05 -- five weeks. Everything else here is supporting evidence.

PRE-DEPLOY BASELINE, captured live before `modal app stop` (so the comparison is against the
system as it actually was, not against memory):
  ext_15 -> "Kampuni za kigeni zinapata adhabu ya USD 25 kwa mwezi (au TZS 60,000)."
            NO Part cited at all -- and an invented "au TZS 60,000" conversion.
  ext_44 -> "kodi ya zuio ya asilimia 10 kwa malipo ya pango la MAKAZI" -- residential rent,
            where the locked fact is about COMMERCIAL rent, with no withholding-agent qualifier
            and no no-residency-split clause. The new fact was not reaching, as expected of a
            container running the 183-row index.

STRUCTURAL WRITE DISCIPLINE (CLAUDE.md R16's general form): the artifact is rewritten after
EVERY row and errors are captured per row rather than aborting. A codec fault, a dropped
Tanzanian link, or a Ctrl-C then costs one row instead of the run -- the failure that lost a
live A/B 20 rows in on 2026-08-24 because its artifact was dumped once at the end.
"""
import json
import os
import re
import sys
import urllib.request

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(REPO, "eval", "results", "part_xii_deploy_verification_2026_10_05.json")
ENDPOINT = "https://prosperpiusmbaruku007--chike-inference-web-endpoint.modal.run"


def token():
    p = os.path.expanduser("~/.chike_modal_token.txt")
    return (os.environ.get("CHIKE_MODAL_TOKEN")
            or (open(p, encoding="utf-8").read().strip() if os.path.exists(p) else ""))


# Each probe: id, what it proves, the question (VERBATIM from a committed fixture where one
# exists), and a predicate over the reply.
PROBES = [
    {
        "id": "ext_15_part_xii",
        "proves": "THE DEPLOY'S WHOLE PURPOSE: the foreign-company citation is now Part XII, "
                  "ss.437-447 and no longer the reversed Part XIII / ss.320-328.",
        "source": "eval/accuracy_gate/edge_probe_extended_078_DRAFT.jsonl ext_15 (verbatim)",
        "question": "Tawi letu la kampuni ya kigeni limechelewa kuwasilisha ripoti ya mwaka. "
                    "Adhabu ni tofauti na kampuni za huku?",
        "must_not_match": r"part\s*xiii\b|ss?\.?\s*320\s*[-–]\s*328",
        "note": "A reply that cites NO Part is not a pass and not a failure of the citation "
                "fix -- the pre-deploy baseline cited none either. Scored on must_not_match "
                "plus a separate observation of whether Part XII appears, so the two are not "
                "conflated.",
        # ⚠️ THE SWAHILI FORM MUST BE IN THIS PATTERN, and the first version of it was not.
        # The live reply says "chini ya Companies Act SEHEMU XII" -- correct, and the same form
        # BRELA's own page uses ("Sehemu ya XII"). My pattern looked only for English
        # `part xii` / `ss.437` and so reported observed=False on a CORRECT citation.
        # That is precisely the mistake act_section_12's own _pattern_note documents from
        # 2026-09-23 -- patterns written in English guarding text served in Swahili -- repeated
        # here by the same person who wrote that note down. Both languages now, `sehemu` first.
        "observe": r"sehemu\s*(?:ya\s*)?xii\b(?!i)|part\s*xii\b(?!i)|ss?\.?\s*437",
    },
    {
        "id": "ext_44_rent_wht",
        "proves": "rent_wht_rate is reachable for the first time -- it was in ZERO rows of the "
                  "183-row index.",
        "source": "eval/accuracy_gate/edge_probe_extended_078_DRAFT.jsonl ext_44 (verbatim)",
        "question": "Nikimlipa mwenye nyumba kodi ya pango ofisini, ni lazima nikate kodi "
                    "kabla ya kumpa fedha?",
        "must_match": r"asilimia\s*10|10\s*%",
        "observe": r"wakala|agent|ukaazi|mkazi|biashara",
        "note": "Baseline said 'pango la MAKAZI' (residential) for a commercial-rent question. "
                "The observe limb looks for the two qualifiers the new fact carries.",
    },
    {
        "id": "nssf_employer_new_anchor",
        "proves": "The re-anchored NSSF employer guard's subject still answers correctly after "
                  "rent_wht_rate joined the index with its own 10% rate -- the ambiguity that "
                  "blocked the first regen attempt was in the GUARD, and this confirms the "
                  "underlying answer did not move.",
        "source": "kaggle/regenerate_rag_e5.py critical_queries 'NSSF employer' (verbatim)",
        "question": "Mwajiri analipa asilimia ngapi NSSF kila mwezi?",
        "must_match": r"asilimia\s*10|10\s*%",
        "must_not_match": r"asilimia\s*20|20\s*%",
        "note": "must_not_match 20% is the D-NSSF-1 party defect: the employer SHARE is 10%, "
                "the 20% is the combined total.",
    },
    {
        "id": "config_only_phrase",
        "proves": "CONFIG LOADING, separately from code. This phrase exists in "
                  "kaggle/chike_config.json's OOC list and NOT in modal_app.py's hardcoded "
                  "fallback, so a correct refusal here proves the container read the FETCHED "
                  "config -- the exact diagnostic that on 2026-08-07 distinguished a config "
                  "failure from a stale warm container.",
        "source": "chike_config.json ooc_phrases (config-only, not in the code fallback)",
        "question": "Nataka kuuza kiwanja changu, kodi ya mapato ni kiasi gani?",
        "must_match": r"sina uhakika|thibitisha|siwezi|nje ya",
        "note": "Property/land sale is out of corpus by design.",
    },
    {
        "id": "negative_sdl_unchanged",
        "proves": "NEGATIVE CASE: a question the deploy must NOT have changed. The index grew "
                  "by one row; nothing about SDL should move.",
        "source": "eval/accuracy_gate/edge_probe_natural_048.jsonl nat_06 class",
        "question": "Nina wafanyakazi 25, mishahara yote ni milioni 15 kwa mwezi. SDL ni "
                    "kiasi gani?",
        "must_match": r"3\.5|525,?000",
        "note": "3.5% of 15,000,000 = 525,000. If this moved, the new row displaced something "
                "it had no business touching.",
    },
    {
        "id": "negative_paye_unchanged",
        "proves": "SECOND NEGATIVE, on a different engine, so 'unchanged' is not evidenced by "
                  "one lucky row.",
        "source": "eval/accuracy_gate/edge_probe_natural_048.jsonl nat_13 class",
        "question": "Mshahara wangu ni TZS 900,000 kwa mwezi, PAYE ni kiasi gani?",
        "must_match": r"103,?000|68,?000",
        "note": "Band 4: 68,000 + 25% x (900,000-760,000) = 103,000.",
    },
]


def ask(question, tok, timeout=240):
    req = urllib.request.Request(
        f"{ENDPOINT}?token={tok}",
        data=json.dumps({"message": question}).encode("utf-8"),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def save(rows):
    passed = [r for r in rows if r.get("verdict") == "PASS"]
    failed = [r for r in rows if r.get("verdict") == "FAIL"]
    errored = [r for r in rows if r.get("verdict") == "ERROR"]
    payload = {
        "_what": "R16 live verification of the 2026-10-05 Part XII / rent_wht_rate deploy.",
        "_endpoint": ENDPOINT,
        "_deployed_index": "184 rows, (184, 768), shipped in 7d46df1; "
                           "chike_config.json rag_fact_count=184 in the same commit",
        "_r16": "'App deployed' is not verification. Each probe exercises a specific change, "
                "with two negatives and one config-only probe.",
        "_write_discipline": "rewritten after EVERY row; per-row errors captured, never fatal",
        "totals": {"probes": len(PROBES), "run": len(rows), "pass": len(passed),
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
        row = {k: p[k] for k in ("id", "proves", "source", "question", "note")}
        try:
            resp = ask(p["question"], tok)
            reply = str(resp.get("reply") or resp.get("answer") or resp)
            row["reply"] = reply
            checks = {}
            if p.get("must_match"):
                checks["must_match"] = bool(re.search(p["must_match"], reply, re.I))
            if p.get("must_not_match"):
                checks["must_not_match_absent"] = not re.search(
                    p["must_not_match"], reply, re.I)
            if p.get("observe"):
                row["observed"] = bool(re.search(p["observe"], reply, re.I))
            row["checks"] = checks
            row["verdict"] = "PASS" if all(checks.values()) else "FAIL"
        except Exception as exc:                       # per-row, never fatal
            row["verdict"] = "ERROR"
            row["error"] = f"{type(exc).__name__}: {str(exc)[:200]}"
        rows.append(row)
        save(rows)                                     # after EVERY row
        print(f"[{row['verdict']:5s}] {row['id']}")
        if row.get("reply"):
            print(f"        {' '.join(row['reply'].split())[:200]}")
        if row.get("checks"):
            print(f"        checks={row['checks']}"
                  + (f" observed={row['observed']}" if "observed" in row else ""))
        if row.get("error"):
            print(f"        {row['error']}")

    payload = save(rows)
    print(f"\n{payload['totals']}")
    print(f"VERDICT: {payload['verdict']}")
    print(f"wrote {OUT}")
    sys.exit(0 if payload["verdict"] == "DEPLOY VERIFIED" else 1)


if __name__ == "__main__":
    main()
