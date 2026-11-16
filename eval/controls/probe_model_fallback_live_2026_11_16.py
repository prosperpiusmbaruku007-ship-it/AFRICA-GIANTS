# -*- coding: utf-8 -*-
"""DOES PRODUCTION'S MODEL FALLBACK EXTRACTOR EVER RETURN A CONFIDENT AMOUNT FOR A NON-WAGE FIGURE THE PARSER CANNOT READ? (2026-11-16, after the safety batch deploy.)

The offline test scripts the model to answer {"gross_monthly_payroll": 800000, "high"}; that proves the fix works WHEN the model does so, not that production's model ever does. This probes live, for the notations the
deterministic parser misses, and classifies each reply by the COPY it carries:
  COMPUTED      an engine working with a result           -> the live hole (must be none)
  BASE_CHECK    "kuthibitisha ... MSHAHARA" or "si mshahara" -> the new fallback check (or the deterministic one) fired: the model DID return a confident amount and it was stopped
  GENERIC_ASK   "nahitaji kiasi cha mshahara ..."          -> no usable amount came back at all (the model declined / low confidence): the branch was not exercised
  OTHER         anything else (a fact answer, a statement)
Controls carry wage evidence and should COMPUTE when the model supplies the figure. Artifact written after every row; resumes.

    python eval/controls/probe_model_fallback_live_2026_11_16.py
"""
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
OUT = os.path.join(REPO, "eval", "results", "model_fallback_live_probe_2026_11_16.json")
PROBES = [
    ("nonwage", "Nina amana ya shilingi 800 elfu, NSSF ni ngapi?"),
    ("nonwage", "Nimekopa shilingi elfu 800 benki, WCF ni ngapi?"),
    ("nonwage", "Mteja amenilipa sh. 800.000/= kwa oda, PAYE ni ngapi?"),
    ("nonwage", "Nina akiba ya 800,000/- , NSSF ni ngapi?"),
    ("nonwage", "Mapato ya biashara yangu yalikuwa Tsh800000 mwezi jana, NSSF ni ngapi?"),
    ("nonwage", "Biashara imepata pato la shilingi laki 8 na nusu mwezi huu, WCF yake ni ngapi?"),
    ("nonwage", "Mkopo wangu wa benki ni mil 12 na laki 3, NSSF ni ngapi?"),
    ("nonwage", "Pesa za amana ni 2.5m, PAYE ni ngapi?"),
    ("wage_control", "Mshahara wake ni shilingi 800 elfu kwa mwezi, NSSF ni ngapi?"),
    ("wage_control", "Mfanyakazi analipwa sh. 800.000/= kwa mwezi, PAYE ni ngapi?"),
    ("wage_control", "Mshahara wa mfanyakazi ni Tsh800000 kwa mwezi, WCF ni ngapi?"),
]


def classify(reply):
    if re.search(r"=\s*TZS\s*[\d,]+", reply):
        return "COMPUTED"
    if re.search(r"kuthibitisha kwamba kiasi|si mshahara", reply):
        return "BASE_CHECK"
    if "nahitaji kiasi cha mshahara" in reply:
        return "GENERIC_ASK"
    return "OTHER"


def main():
    import modal
    m = modal.Cls.from_name("chike-inference", "ChikeModel")()
    art = json.load(open(OUT, encoding="utf-8")) if os.path.exists(OUT) else {"rows": []}
    art["rows"] = [r for r in art["rows"] if "error" not in r]
    done = {r["q"] for r in art["rows"]}
    for kind, q in PROBES:
        if q in done:
            continue
        try:
            out = m.run.remote(q)
            reply = out.get("reply", "") if isinstance(out, dict) else str(out)
            row = dict(kind=kind, q=q, reply=reply, path=out.get("answer_path") if isinstance(out, dict) else None, model_calls=out.get("model_calls") if isinstance(out, dict) else None, cls=classify(reply))
        except Exception as e:                                           # noqa: BLE001
            row = dict(kind=kind, q=q, error=repr(e)[:300])
        art["rows"].append(row)
        json.dump(art, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(f"[{row.get('cls', 'ERR'):<11}] {kind:<12} calls={row.get('model_calls')} {q}\n        -> {(row.get('reply') or row.get('error') or '')[:200]!r}")
    tally = {}
    for r in art["rows"]:
        tally[(r["kind"], r.get("cls"))] = tally.get((r["kind"], r.get("cls")), 0) + 1
    print("\n", {f"{k[0]}:{k[1]}": v for k, v in sorted(tally.items(), key=str)})
    bad = [r for r in art["rows"] if r["kind"] == "nonwage" and r.get("cls") == "COMPUTED"]
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
