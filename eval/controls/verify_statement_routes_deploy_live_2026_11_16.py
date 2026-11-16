# -*- coding: utf-8 -*-
"""LIVE VERIFICATION (R16 steps 2-3, R12c) of the 2026-11-16 deploy of 32572c9: three more model-free statement routes + D-FIDELITY-10 ext. + D-FIDELITY-11.

Calls the PRODUCTION `chike-inference` ChikeModel through the Modal SDK (R12c: a targeted check of the ENUMERATED blast radius, not another full gate).
  IDENTITY  served index == committed (211 rows).   ROUTE  each new topic must go engine:fixed_statement with model_calls 0.
  NEAR      near-neighbours that must NOT divert to the new routes (threshold, NSSF "ya hiari", occupational disease, pure-goods withholding).
  NEGATIVE  an existing fixed statement stays model-free; SDL and a PAYE compute behave as before.
`must`/`must_not` are INDICATIVE (R38): replies, path, model_calls and guards are stored in full for READING. Artifact written after EVERY row, resumes.

    python eval/controls/verify_statement_routes_deploy_live_2026_11_16.py
"""

import hashlib
import json
import os
import re
import sys
import time

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
OUT = os.path.join(REPO, "eval", "results", "statement_routes_deploy_live_2026_11_16.json")
FS = "engine:fixed_statement"
# (arm, question, must, must_not, path_prefix, path_forbidden_prefix, model_calls_zero)
CASES = [
    ("ROUTE", "Je naweza kujisajili VAT kwa hiari ukiwa chini ya kiwango?", [r"(?i)TRA|Kamishna"], [r"(?i)ndiyo", r"(?i)hata ukiwa chini ya kiwango"], FS, None, True),
    ("ROUTE", "Nina mauzo madogo, naweza kusajili VAT ingawa sijafikia kiwango?", [r"(?i)TRA|Kamishna"], [r"(?i)ndiyo"], None, None, False),
    ("ROUTE", "Mfanyakazi ameumia jana nina siku ngapi za kupeleka taarifa ya ajali", [r"siku 7"], [r"(?i)(?<!si )tangu tarehe ya ajali", r"(?i)(?<!si )tangu siku ya ajali"], FS, None, True),
    ("ROUTE", "Ajali ya kazini nitoe taarifa WCF ndani ya siku ngapi?", [r"siku 7"], [r"(?i)(?<!si )tangu tarehe ya ajali"], FS, None, True),
    ("ROUTE", "VAT ya zuio kwa mauzo ya bidhaa na huduma pamoja inakatwaje?", [r"3:2"], [r"(?i)thamani yote", r"(?i)kiwango kinagawanywa"], FS, None, True),
    ("ROUTE", "Mkandarasi anatoa vifaa na kazi, VAT ya zuio inahesabiwaje?", [r"3:2"], [r"(?i)thamani yote"], FS, None, True),
    ("NEAR", "Kizingiti cha kusajili VAT ni kiasi gani?", [r"200"], [], None, FS, False),
    ("NEAR", "Je, NSSF ni ya hiari?", [r"(?i)NSSF"], [], None, FS, False),
    ("NEAR", "Ugonjwa wa kazini unapaswa kutolewa taarifa WCF ndani ya muda gani tangu kugunduliwa?", [r"(?i)WCF"], [], None, FS, False),
    ("NEAR", "VAT ya zuio kwa bidhaa ni asilimia ngapi?", [r"3"], [r"3:2"], None, FS, False),
    ("NEAR", "Naomba kufuta usajili wa VAT nikifunga biashara, nafanyaje?", [r"(?i)TRA|VAT"], [], None, FS, False),
    ("NEGATIVE", "Overtime inalipwa kiasi gani?", [r"1\.5"], [], FS, None, True),
    ("NEGATIVE", "SDL ni asilimia ngapi?", [r"3\.5"], [], None, None, False),
    ("NEGATIVE", "Mshahara wa mfanyakazi ni TZS 760,000 kwa mwezi. PAYE ni kiasi gani?", [r"(?i)PAYE|TZS"], [r"(?i)bendi ya pili.{0,40}760,000"], None, None, False),
]


def committed_digest():
    rows = json.load(open(os.path.join(REPO, "chike-inference", "rag_facts_text.json"), encoding="utf-8"))
    return len(rows), hashlib.sha256(json.dumps(rows, ensure_ascii=False).encode("utf-8")).hexdigest()


def main():
    import modal
    m = modal.Cls.from_name("chike-inference", "ChikeModel")()
    art = json.load(open(OUT, encoding="utf-8")) if os.path.exists(OUT) else {"identity": None, "rows": []}
    art["rows"] = [r for r in art["rows"] if "error" not in r]
    done = {r["q"] for r in art["rows"]}

    def save():
        json.dump(art, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    if not art.get("identity"):
        t0 = time.time()
        ident = m.served_index_identity.remote()
        n, dg = committed_digest()
        art["identity"] = dict(served=ident, committed_rows=n, committed_sha256=dg, took_s=round(time.time() - t0, 1))
        save()
    ident = art["identity"]
    print("served index identity:", ident["served"])
    print("committed             :", ident["committed_rows"], ident["committed_sha256"])

    for arm, q, must, must_not, path_prefix, path_forbid, zero_calls in CASES:
        if q in done:
            continue
        t0 = time.time()
        try:
            out = m.run.remote(q)
            reply = out.get("reply", "") if isinstance(out, dict) else str(out)
            tr = out if isinstance(out, dict) else {}
            path = tr.get("answer_path") or tr.get("path")
            calls = tr.get("model_calls")
            checks = {"must": all(re.search(p, reply) for p in must), "must_not": not any(re.search(p, reply) for p in must_not)}
            if path_prefix:
                checks["path"] = bool(path and str(path).startswith(path_prefix))
            if path_forbid:
                checks["path_not_" + path_forbid] = not (path and str(path).startswith(path_forbid))
            if zero_calls:
                checks["model_calls_0"] = calls == 0
            row = dict(arm=arm, q=q, reply=reply, path=path, model_calls=calls, guards=tr.get("guards"), checks=checks,
                       ok=all(checks.values()), took_s=round(time.time() - t0, 1))
        except Exception as e:                                           # noqa: BLE001
            row = dict(arm=arm, q=q, error=repr(e)[:300])
        art["rows"].append(row)
        save()
        flag = "ERR" if "error" in row else ("ok " if row["ok"] else "MISS")
        print(f"[{flag}] {arm:<8} {row.get('took_s', '?'):>6}s {row.get('path')} calls={row.get('model_calls')}  {q[:58]}\n        -> {(row.get('reply') or row.get('error') or '')[:220]!r}")
    bad = [r for r in art["rows"] if r.get("ok") is False or "error" in r]
    sv = ident["served"] if isinstance(ident["served"], dict) else {}
    id_ok = sv.get("rag_rows_loaded") == ident["committed_rows"] and sv.get("rag_facts_text_sha256") == ident["committed_sha256"]
    print(f"\n{len(art['rows'])} rows; automated-limb misses/errors {len(bad)}; identity rows match: {id_ok}  (READ the replies)")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
