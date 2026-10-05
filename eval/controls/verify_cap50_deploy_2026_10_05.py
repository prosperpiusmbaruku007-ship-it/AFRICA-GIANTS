# -*- coding: utf-8 -*-
"""R16 LIVE VERIFICATION OF THE Cap.50 R.E.2023 DEPLOY (second ship of 2026-10-05).

"✓ App deployed" is NOT verification (R16). Each probe exercises a specific change, with two
prior-ship regression probes, one config-only probe, and two standard negatives.

THE TWO ROWS THAT MATTER, both LIVE AND WRONG until this deploy:
  row 159  `fine limit: one hundred thousand TZS`  -- 100x understated. R.E.2015 s.72(1)'s
           actual text; R.E.2023 s.76(1) reads "ten million shillings".
  row  63  `NSSF inalipwa ifikapo tarehe 10 ...`   -- a date that appears in NO source. The
           fact was corrected on 2026-09-02 and its own verified_by said so, so this row has
           been serving a value its own fact contradicted since at least September.

⚠️ BASELINE LIMITATION, STATED RATHER THAN GLOSSED (R24). No pre-deploy LIVE capture was taken
for these two rows, so the BEFORE here is the committed index text -- what the warm container
was demonstrably retrieving -- and not a recorded reply. That is decisive about what was
RETRIEVABLE (`git show 7d46df1:kaggle/rag_facts_text.json` rows 63 and 159) and silent about
what the model said on top of it. Do not read a PASS below as a measured before/after delta on
the reply; read it as "the corrected row is now reaching the answer".

POLARITY, NOT PRESENCE, on the two must_not checks. Both new index rows deliberately name the
superseded value under a negation, so a correct reply may legitimately say "si TZS 100,000" or
"si tarehe 10". A presence check would fail the very behaviour being verified. Matches are
therefore scored only when NOT preceded by a negation -- the same rule the regen's payload gate
and the dry run both apply, re-derived here against live text.

STRUCTURAL WRITE DISCIPLINE (CLAUDE.md R16's general form): the artifact is rewritten after
EVERY row and errors are captured per row rather than aborting. A codec fault, a dropped
Tanzanian link or a Ctrl-C then costs one row instead of the run.
"""
import json
import os
import re
import sys
import urllib.request

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(REPO, "eval", "results", "cap50_deploy_verification_2026_10_05.json")
ENDPOINT = "https://prosperpiusmbaruku007--chike-inference-web-endpoint.modal.run"

NEGATED = r"(?:\bsi\b|\bsio\b|\bnot\b|\bhapana\b|\bsiyo\b)[\s:,]*(?:TZS\s*)?$"


def token():
    p = os.path.expanduser("~/.chike_modal_token.txt")
    return (os.environ.get("CHIKE_MODAL_TOKEN")
            or (open(p, encoding="utf-8").read().strip() if os.path.exists(p) else ""))


PROBES = [
    {
        "id": "nssf_fine_ten_million",
        "proves": "THE DEPLOY'S FIRST PURPOSE: row 159 no longer serves "
                  "'one hundred thousand'. Cap.50 R.E.2023 s.76(1) reads ten million.",
        "source": "kaggle/regenerate_rag_e5.py critical_queries (verbatim, the new guard)",
        "question": "Nisipolipa michango ya NSSF kabisa, nitatozwa faini ya kiasi gani?",
        "before_committed_index": "row 159 = 'fine limit: one hundred thousand TZS'",
        "must_match": r"10,?000,?000|milioni\s+kumi",
        "must_not_assert": r"100[,.]?000(?![,.\d])|laki\s+moja|elfu\s+mia\s+moja",
        "observe": r"kifungo|jela|miaka\s+miwili|miaka\s+2",
        "note": "observe looks for the imprisonment limb -- the statutory sentence is "
                "disjunctive (fine OR imprisonment OR both), so a reply naming only the fine "
                "is correct but incomplete.",
    },
    {
        "id": "nssf_deadline_one_month",
        "proves": "THE DEPLOY'S SECOND PURPOSE: row 63 no longer serves 'tarehe 10'. "
                  "s.14(1) is within one month after the end of the payroll month. This row "
                  "has been live and wrong since at least September.",
        "source": "kaggle/regenerate_rag_e5.py critical_queries (verbatim, the new guard)",
        "question": "Michango ya NSSF ya mwezi huu inatakiwa kulipwa lini?",
        "before_committed_index": "row 63 = 'NSSF inalipwa ifikapo tarehe 10 ya mwezi unaofuata.'",
        "must_match": r"mwezi\s+mmoja|mwisho\s+wa\s+mwezi",
        "must_not_assert": r"tarehe\s+10\b|the\s+10th",
        "observe": r"asilimia\s*5|5\s*%",
        "note": "observe looks for the 5% late-payment penalty, which the corrected row also "
                "carries.",
    },
    {
        "id": "regression_part_xii",
        "proves": "PRIOR-SHIP REGRESSION CHECK. The index changed under the Part XII fix that "
                  "shipped hours earlier; production served the REVERSED citation for five "
                  "weeks, so confirming it survived this ship is not a formality.",
        "source": "eval/accuracy_gate/edge_probe_extended_078_DRAFT.jsonl ext_15 (verbatim)",
        "question": "Tawi letu la kampuni ya kigeni limechelewa kuwasilisha ripoti ya mwaka. "
                    "Adhabu ni tofauti na kampuni za huku?",
        "must_not_assert": r"part\s*xiii\b|ss?\.?\s*320\s*[-–]\s*328",
        # Swahili FIRST. An English-only pattern reported observed=False on the correct
        # "Companies Act SEHEMU XII" during the previous deploy's verification -- which is the
        # exact mistake act_section_12's own _pattern_note records from 2026-09-23.
        "observe": r"sehemu\s*(?:ya\s*)?xii\b(?!i)|part\s*xii\b(?!i)|ss?\.?\s*437",
        "note": "Scored on must_not_assert; the Part XII citation itself is OBSERVED separately "
                "so 'cites no Part' is not conflated with 'cites the wrong Part'.",
    },
    {
        "id": "regression_rent_wht",
        "proves": "SECOND PRIOR-SHIP REGRESSION CHECK, on a different fact, so 'the earlier "
                  "ship survived' is not evidenced by one lucky row.",
        "source": "eval/accuracy_gate/edge_probe_extended_078_DRAFT.jsonl ext_44 (verbatim)",
        "question": "Nikimlipa mwenye nyumba kodi ya pango ofisini, ni lazima nikate kodi "
                    "kabla ya kumpa fedha?",
        "must_match": r"asilimia\s*10|10\s*%",
        "observe": r"wakala|agent|ukaazi|mkazi",
        "note": "The two qualifiers the locked fact carries: withholding-agent only, and no "
                "residency split.",
    },
    {
        "id": "config_only_phrase",
        "proves": "CONFIG LOADING, separately from code. This phrase is in "
                  "kaggle/chike_config.json's OOC list and NOT in modal_app.py's hardcoded "
                  "fallback, so a correct refusal proves the container read the FETCHED config "
                  "-- the diagnostic that on 2026-08-07 separated a config failure from a "
                  "stale warm container.",
        "source": "chike_config.json ooc_phrases (config-only)",
        "question": "Nataka kuuza kiwanja changu, kodi ya mapato ni kiasi gani?",
        "must_match": r"sina uhakika|thibitisha|siwezi|nje ya",
        "note": "Land sale is out of corpus by design.",
    },
    {
        "id": "negative_sdl_unchanged",
        "proves": "NEGATIVE CASE: six rows changed and none of them is SDL. If this moved, a "
                  "rewritten row displaced something it had no business touching.",
        "source": "eval/accuracy_gate/edge_probe_natural_048.jsonl nat_06 class",
        "question": "Nina wafanyakazi 25, mishahara yote ni milioni 15 kwa mwezi. SDL ni "
                    "kiasi gani?",
        "must_match": r"3\.5|525,?000",
        "note": "3.5% of 15,000,000 = 525,000.",
    },
    {
        "id": "negative_nssf_employer_rate",
        "proves": "SECOND NEGATIVE, chosen deliberately on NSSF itself -- the domain this ship "
                  "rewrote four rows in. The employer SHARE must still be 10% and must not "
                  "have been dragged to the 20% total (D-NSSF-1 party resolution), and it must "
                  "not have picked up the new ten-million figure either.",
        "source": "kaggle/regenerate_rag_e5.py critical_queries 'NSSF employer' (verbatim)",
        "question": "Mwajiri analipa asilimia ngapi NSSF kila mwezi?",
        "must_match": r"asilimia\s*10|10\s*%",
        "must_not_assert": r"asilimia\s*20|20\s*%",
        "note": "The nearest-neighbour risk this ship creates: four NSSF rows changed around "
                "this one.",
    },
]


def ask(question, tok, timeout=300):
    req = urllib.request.Request(
        f"{ENDPOINT}?token={tok}",
        data=json.dumps({"message": question}).encode("utf-8"),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def asserted(pattern, text):
    """Occurrences NOT preceded by a negation. A reply saying 'si TZS 100,000' is CORRECT."""
    return [m.group(0) for m in re.finditer(pattern, text, re.I)
            if not re.search(NEGATED, text[max(0, m.start() - 14):m.start()], re.I)]


def save(rows):
    failed = [r for r in rows if r.get("verdict") == "FAIL"]
    errored = [r for r in rows if r.get("verdict") == "ERROR"]
    payload = {
        "_what": "R16 live verification of the Cap.50 R.E.2023 deploy (second ship, 2026-10-05).",
        "_endpoint": ENDPOINT,
        "_deployed_index": "184 rows, (184, 768), HF commit 69e514f2c7 built from 9093762, "
                           "dual-committed in 335624b. rag_fact_count unchanged at 184.",
        "_baseline_limitation": "No pre-deploy LIVE capture was taken for rows 63/159. BEFORE "
                                "is the committed index text (git show 7d46df1:kaggle/"
                                "rag_facts_text.json), decisive about what was RETRIEVABLE and "
                                "silent about what the model said on top of it.",
        "_scoring": "must_not_assert is POLARITY-checked: a superseded value named under a "
                    "negation is correct behaviour, not a failure, because both new index rows "
                    "deliberately contradict the old value.",
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
        row = {k: p[k] for k in ("id", "proves", "source", "question", "note")
               if k in p}
        if "before_committed_index" in p:
            row["before_committed_index"] = p["before_committed_index"]
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
        except Exception as exc:                       # per-row, never fatal
            row["verdict"] = "ERROR"
            row["error"] = f"{type(exc).__name__}: {str(exc)[:200]}"
        rows.append(row)
        save(rows)                                     # after EVERY row
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
