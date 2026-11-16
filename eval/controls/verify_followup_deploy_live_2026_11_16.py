# -*- coding: utf-8 -*-
"""LIVE VERIFICATION (R16 steps 2-3, R12c) of the 2026-11-16 follow-up regen deploy (211-row index).

Calls the PRODUCTION `chike-inference` ChikeModel through the Modal SDK. Arms:
  IDENTITY   `served_index_identity()` must equal the committed index (211 rows, sha256).
  NEW        each changed answer: voluntary VAT registration (hedged, no invented route), the WCF accident chain (clock from RECEIPT, never "from the accident
             date"), construction withholding (hedged), VAT-withholding mixed supply (3:2, no "whole value").
  R44        replies that used to cite a consolidated-Act section number must not (no `Kifungu N` outside an amending Act).
  NEGATIVE   things that must behave as before: SDL, a PAYE compute, pure-goods VAT withholding (no 3:2 injected), the standard VAT rate, a fixed
             statement still model-free (path engine:fixed_statement, model_calls 0).
`must` / `must_not` are INDICATIVE (R38: a probe encodes an expected answer): replies, path and model_calls are stored in full for READING.
Writes the artifact after EVERY row and resumes from it.

    python eval/controls/verify_followup_deploy_live_2026_11_16.py
"""
import hashlib
import json
import os
import re
import sys
import time

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
OUT = os.path.join(REPO, "eval", "results", "followup_deploy_live_2026_11_16.json")
NO_SECTION = r"(?i)(?<!20\d\d )(?<!20\d\d, )\b(kifungu|vifungu)\s+\d"          # consolidated-Act section numbers (R44)

# (arm, question, must [all], must_not [none], expect_path_prefix or None, expect_model_calls_zero)
CASES = [
    # FIRST RUN LESSON (R38, in the probe layer): my must_not here was `ndiyo,? (unaweza|naweza) kujisajili kwa hiari` and the live reply was "Ndiyo, kwa mujibu wa
    # sheria, unaweza kujisajili VAT kwa hiari" -- one word (VAT) between, so the automated limb printed ok on an answer the row exists to prevent. A bare `Ndiyo` /
    # "hata ukiwa chini ya kiwango" is the thing to forbid: the Act names no route and TRA names no activities, so an unhedged yes is unsupported.
    ("NEW", "Je naweza kujisajili VAT kwa hiari ukiwa chini ya kiwango?", [r"(?i)TRA"], [r"(?i)ndiyo", r"(?i)hata ukiwa chini ya kiwango"], None, False),
    ("NEW", "Nina mauzo madogo, naweza kusajili VAT ingawa sijafikia kiwango?", [r"(?i)TRA|Kamishna"], [r"(?i)ndiyo", r"(?i)ili usajiliwe kwa hiari"], None, False),
    ("NEW", "Mfanyakazi ameumia jana nina siku ngapi za kupeleka taarifa ya ajali", [r"siku 7"], [r"(?i)(?<!si )tangu tarehe ya ajali", r"(?i)(?<!si )kutoka tarehe ya ajali"], None, False),
    ("NEW", "Ajali ya kazini nitoe taarifa WCF ndani ya siku ngapi?", [r"siku 7"], [r"(?i)(?<!si )tangu tarehe ya ajali"], None, False),
    ("NEW", "Mfanyakazi amepata ajali kazini, taarifa WCF inaanza kuhesabiwa lini?", [r"(?i)apokee|kupokea|ajue|taarifa"], [r"(?i)(?<!si )tangu tarehe ya ajali", r"(?i)(?<!si )tangu siku ya ajali"], None, False),
    ("NEW", "Namlipa mkandarasi wa ujenzi, nakata kodi ya zuio asilimia ngapi?", [r"(?i)TRA|3:2"], [], None, False),
    # the Act apportions the VALUE subject to withholding, not the RATE: "kiwango kinagawanywa 3:2" (first run) states the wrong object.
    ("NEW", "VAT ya zuio kwa mauzo ya bidhaa na huduma pamoja inakatwaje?", [r"3:2"], [r"(?i)thamani yote", r"(?i)kiwango kinagawanywa"], None, False),
    ("NEW", "Mkandarasi anatoa vifaa na kazi, VAT ya zuio inahesabiwaje?", [r"3:2"], [], None, False),
    ("R44", "Notisi ya kuachisha mfanyakazi wa kila mwezi ni siku ngapi?", [r"siku 28"], [NO_SECTION], "engine:fixed_statement", True),
    ("R44", "Likizo ya uzazi ni siku ngapi?", [r"84"], [NO_SECTION], None, False),
    ("R44", "PAYE inalipwa lini?", [r"(?i)tarehe 7|siku 7"], [NO_SECTION], None, False),
    ("R44", "Kodi ya zuio kwa mshauri wa kodi ni asilimia ngapi?", [r"5"], [NO_SECTION], None, False),
    ("R44", "Je, mfanyabiashara mpya mwenye TIN mpya ana msamaha wa kodi ya makadirio?", [r"(?i)Kamishna|ombi|aombe"], [NO_SECTION, r"(?i)First Schedule"], None, False),
    ("R44", "Nikichelewa kulipa PAYE adhabu ni nini?", [r"(?i)adhabu|asilimia|%"], [NO_SECTION], None, False),
    ("NEGATIVE", "SDL ni asilimia ngapi?", [r"3\.5"], [NO_SECTION], None, False),
    ("NEGATIVE", "Kiwango cha VAT ni asilimia ngapi?", [r"18"], [NO_SECTION], None, False),
    ("NEGATIVE", "VAT ya zuio kwa bidhaa ni asilimia ngapi?", [r"3"], [r"3:2"], None, False),
    ("NEGATIVE", "Mshahara wa mfanyakazi ni TZS 800,000 kwa mwezi. PAYE ni kiasi gani?", [r"(?i)PAYE|TZS"], [NO_SECTION], None, False),
    ("NEGATIVE", "Overtime inalipwa kiasi gani?", [r"1\.5"], [NO_SECTION], "engine:fixed_statement", True),
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

    for arm, q, must, must_not, path_prefix, zero_calls in CASES:
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
