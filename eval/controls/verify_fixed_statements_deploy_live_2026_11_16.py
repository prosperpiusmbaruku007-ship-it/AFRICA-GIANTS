# -*- coding: utf-8 -*-
"""LIVE VERIFICATION (R16 steps 2-3, R12c) of the 2026-11-16 fixed-statement deploy.

Calls the PRODUCTION `chike-inference` ChikeModel through the Modal SDK. Three populations, each with its own arm:
  ROUTE      the five live questions that were wrong on 2026-11-13: must now return path `engine:fixed_statement`, model_calls 0, no guard, and
             state every figure of the verified statement (for notice: all of 4, 7 and 28 -- never one limb).
  FALLTHRU   phrasings that MISS the routes (and still reach the model): the reply must be CORRECT, either because the model got it right or
             because D-FIDELITY-10 replaced it (guards == ['replaced'] and the statement present). The wrong live specimens must not appear.
  PRIOR      the 24 probes of the 2026-11-13 verification, re-run (R12c: the enumerated population plus the controls on unchanged routes).
Writes the artifact after EVERY row and resumes from it. A pass on `must` is indicative; replies are stored in full for READING.

    python eval/controls/verify_fixed_statements_deploy_live_2026_11_16.py
"""
import json
import os
import re
import sys
import time

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, REPO)
import verify_coverage_deploy_live_2026_11_13 as prior          # noqa: E402

# CHIKE_VERIFY_OUT lets a RE-RUN against a later deploy write its own artifact (this harness resumes from OUT, so re-running over the old file would skip every
# row): 2026-11-16 ran it again after the 211-row follow-up deploy (statement text changed under R44) into ..._after_211.json.
OUT = os.environ.get("CHIKE_VERIFY_OUT") or os.path.join(REPO, "eval", "results", "fixed_statements_deploy_live_2026_11_16.json")

# (arm, question, [regexes that must ALL match], [regexes that must NOT match], expect_path_prefix or None)
CASES = [
    ("ROUTE", "Notisi ya kuachisha mfanyakazi wa kila mwezi ni siku ngapi?", [r"siku 7", r"siku 4", r"siku 28"], [], "engine:fixed_statement"),
    ("ROUTE", "Severance pay inahesabiwaje?", [r"siku 7", r"miaka 10"], [r"25"], "engine:fixed_statement"),
    ("ROUTE", "Overtime inalipwa kiasi gani?", [r"1\.5", r"saa 50"], [r"asilimia 25"], "engine:fixed_statement"),
    ("ROUTE", "Likizo ya mwaka ni siku ngapi?", [r"siku 28"], [r"Ndiyo, unatakiwa"], "engine:fixed_statement"),
    ("ROUTE", "Nimeuza kwa mkopo, VAT inalipwa lini?", [r"mapema zaidi", r"tarehe 20"], [r"kidogo kidogo"], "engine:fixed_statement"),
    ("FALLTHRU", "Mfanyakazi wa kila mwezi nikimwachisha, notisi ni ya siku zipi?", [r"siku 28"], [r"notisi ni siku 4\."], None),
    ("FALLTHRU", "Naomba maelezo ya severance pay kwa mfanyakazi aliyeachishwa.", [r"siku 7"], [r"asilimia 25"], None),
    ("FALLTHRU", "Naomba kujua kuhusu overtime ya wafanyakazi wangu.", [r"1\.5|150|50"], [r"asilimia 25"], None),
    ("FALLTHRU", "Likizo ya mwaka na overtime ni siku ngapi?", [r"28"], [r"Ndiyo, unatakiwa"], None),
    ("FALLTHRU", "Nimeuza kwa mkopo, kuhusu VAT nifanyeje?", [], [r"kidogo kidogo|kwa awamu"], None),
]


def main():
    import modal
    m = modal.Cls.from_name("chike-inference", "ChikeModel")()
    art = json.load(open(OUT, encoding="utf-8")) if os.path.exists(OUT) else {"identity": None, "rows": []}
    art["rows"] = [r for r in art["rows"] if "error" not in r]
    done = {r["q"] for r in art["rows"]}

    def save():
        json.dump(art, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    if not art.get("identity"):
        ident = m.served_index_identity.remote()
        n, dg = prior.committed_digest()
        art["identity"] = dict(served=ident, committed_rows=n, committed_sha256=dg)
        save()
    print("identity:", art["identity"]["served"] if not isinstance(art["identity"]["served"], dict)
          else {k: v for k, v in art["identity"]["served"].items() if k != "build"})

    todo = [(a, q, ok, bad, p) for a, q, ok, bad, p in CASES] + \
           [("PRIOR:" + k, q, [must] if must else [], [], None) for k, q, must, _n in prior.PROBES]
    for arm, q, must_all, must_not, path_prefix in todo:
        if q in done:
            continue
        t0 = time.time()
        try:
            out = m.run.remote(q)
            reply = out.get("reply", "") if isinstance(out, dict) else str(out)
            path, calls, guards = out.get("path"), out.get("model_calls"), out.get("guards")
            checks = {"must_all": all(re.search(x, reply) for x in must_all),
                      "must_not": not any(re.search(x, reply) for x in must_not)}
            if arm == "FALLTHRU":
                # a phrasing that MISSES the route reaches the model: the reply is acceptable if the guard replaced it with the statement
                # (then the statement's figures are what `must_all` reads) OR the guard has nothing to object to. R38: do not demand a
                # particular wording from a question that asked nothing specific.
                from chike import fidelity
                clean = not fidelity.fixed_figure_violations(q, reply)
                checks["must_all"] = checks["must_all"] or (clean and not must_all) or guards == ["replaced"]
                checks["no_violation_left"] = clean
            if path_prefix:
                checks["path"] = str(path or "").startswith(path_prefix)
                checks["model_free"] = calls == 0 and guards == []
            row = dict(arm=arm, q=q, reply=reply, path=path, model_calls=calls, guards=guards, checks=checks,
                       ok=all(checks.values()), took_s=round(time.time() - t0, 1),
                       facts=[f[:90] for f in (out.get("facts") or [])][:3] if isinstance(out, dict) else None)
        except Exception as e:                                       # noqa: BLE001 -- a per-row error must not lose the run
            row = dict(arm=arm, q=q, error=repr(e)[:300])
        art["rows"].append(row)
        save()
        flag = "ERR " if "error" in row else ("ok  " if row["ok"] else "MISS")
        print(f"[{flag}] {arm:<14} {row.get('took_s', '?'):>6}s path={row.get('path')} calls={row.get('model_calls')} "
              f"guards={row.get('guards')} :: {q[:60]}\n        -> {(row.get('reply') or row.get('error') or '')[:200]!r}")
    miss = [r for r in art["rows"] if r.get("ok") is False]
    err = [r for r in art["rows"] if "error" in r]
    print(f"\n{len(art['rows'])} rows; misses {len(miss)}; errors {len(err)}  (READ the replies; a pass is indicative)")
    sys.exit(1 if (miss or err) else 0)


if __name__ == "__main__":
    main()
