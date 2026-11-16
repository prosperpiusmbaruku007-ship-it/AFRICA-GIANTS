# -*- coding: utf-8 -*-
"""LIVE VERIFICATION (R16 steps 2-3, R12c) of the 2026-11-16 safety batch: a targeted check of the ENUMERATED blast radius, not another full gate.

Calls the PRODUCTION `chike-inference` ChikeModel through the Modal SDK. Arms:
  IDENTITY   served index == committed (211 rows); build == HEAD.
  NONWAGE_D  a figure that is not a wage, readable by the DETERMINISTIC extractor (loan, business income, a customer's payment, a deposit) on NSSF / WCF / PAYE: no computation may come back.
  NONWAGE_M  the same, in a notation the parser cannot read ("800k"), so the figure reaches the MODEL FALLBACK extractor. `min_calls` records that the question actually reached the model (R26: a probe that
             never reached the branch proves nothing); no computation may come back.
  SPLIT / TABLE / DISEASE / E318  the NSSF 15/5 split, the PAYE band table, the WCF occupational-disease chain, eval_318's own question.
  NEGATIVE   plain computes with wage evidence still compute (deterministic AND model-fallback), the previous routes unchanged.
`must` / `must_not` are INDICATIVE (R38: a probe encodes an expected answer): replies, path, model_calls and guards are stored in full for READING. The artifact is written after EVERY row and resumes.

    python eval/controls/verify_safety_batch_deploy_live_2026_11_16.py
"""
import hashlib
import json
import os
import re
import sys
import time

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
OUT = os.path.join(REPO, "eval", "results", "safety_batch_deploy_live_2026_11_16.json")
FS = "engine:fixed_statement"
COMPUTED = r"=\s*TZS\s*[\d,]+"                       # an engine working with a result
E318 = "Nina wafanyakazi 11 na mishahara TZS 5,500,000 na nataka kujua SDL na NSSF na pia je nasajili VAT kama mapato ni TZS 205,000,000?"

# (arm, question, must [all], must_not [none], path_prefix|None, path_forbidden_prefix|None, model_calls_zero, min_calls)
CASES = [
    ("NONWAGE_D", "Mapato ya biashara yangu yalifika TZS 12,300,000 mwezi jana, NSSF ya jumla ni ngapi?", [], [COMPUTED, r"2,460,000"], None, None, False, 0),
    ("NONWAGE_D", "Nimekopa benki mkopo wa TZS 20,000,000, WCF ni ngapi?", [], [COMPUTED, r"100,000"], None, None, False, 0),
    ("NONWAGE_D", "Mteja amenilipa TZS 6,000,000 kwa oda, PAYE ni ngapi?", [], [COMPUTED, r"1,628,000"], None, None, False, 0),
    ("NONWAGE_D", "Nina amana ya TZS 15,000,000, NSSF ni ngapi?", [], [COMPUTED, r"3,000,000"], None, None, False, 0),
    ("NONWAGE_D", "Ada ya shule ni TZS 2,500,000, WCF ni ngapi?", [], [COMPUTED], None, None, False, 0),
    ("NONWAGE_M", "Nina amana ya 800k, NSSF ni ngapi?", [], [COMPUTED, r"160,000|80,000"], None, None, False, 1),
    ("NONWAGE_M", "Nimekopa 800k kutoka benki, WCF ni ngapi?", [], [COMPUTED, r"4,000"], None, None, False, 1),
    ("NONWAGE_M", "Mteja amenilipa 800k kwa oda, PAYE ni ngapi?", [], [COMPUTED, r"78,000"], None, None, False, 1),
    ("NONWAGE_M", "Mapato ya biashara yangu yalikuwa 800k mwezi jana, NSSF ni ngapi?", [], [COMPUTED, r"160,000|80,000"], None, None, False, 1),
    ("SPLIT", "Mshahara ni TZS 700,000 na tumekubaliana mgao wa 15% mwajiri na 5% mfanyakazi — kila upande ni ngapi?", [r"105,000", r"35,000"], [r"70,000 \+ mfanyakazi TZS 70,000"], "engine:nssf", None, False, 0),
    ("SPLIT", "Mshahara ni TZS 700,000, NSSF — mwajiri 10% na mfanyakazi 5%, kila upande ni ngapi?", [r"haujumlishi asilimia 20"], [COMPUTED], None, None, False, 0),
    ("SPLIT", "Naweza kulipa NSSF kwa mgawanyo wa 15 kwa 5?", [r"si mgawanyo pekee halali"], [], FS, None, True, 0),
    ("TABLE", "Mfumo wa mabano ya PAYE ya kila mwezi unafuata mpangilio gani wa viwango?", [r"kiwango cha 3: TZS 520,001 hadi TZS 760,000 = TZS 20,000 \+ 20%", r"15% tambarare"], [r"ngazi 8", r"35%"], FS, None, True, 0),
    ("DISEASE", "Ugonjwa wa kazini unapaswa kutolewa taarifa WCF ndani ya muda gani tangu kugunduliwa?", [r"siku 14 za kazi", r"siku 7 za kazi", r"APOKEE", r"siku 21"], [], FS, None, True, 0),
    ("E318", E318, [r"TZS 192,500", r"TZS 1,100,000", r"kipindi"], [r"huhitajiwi", r"hayazidi", r"si lazima kusajili"], None, None, False, 0),
    ("E318", "Kampuni yenye mapato ya TZS 205,000,000 inahitaji kusajili VAT?", [], [r"huhitajiwi", r"hayazidi kizingiti", r"si lazima kusajili"], None, None, False, 0),
    ("E318", "Biashara yangu imepata mauzo ya TZS milioni 95 katika miezi 6 — je nimevuka kizingiti cha lazima cha VAT?", [r"miezi 12", r"hayajafikia"], [r"Ndiyo — umefikia"], "engine:vat_registration", None, False, 0),
    ("E318", "Mauzo yangu ni TZS 10,999,000 kwa mwaka, je EFD ni lazima kwangu?", [r"(?i)EFD"], [r"11M", r"11,000,000"], None, None, False, 0),
    ("NEGATIVE", "Mshahara wa mfanyakazi ni TZS 800,000 kwa mwezi, NSSF ni ngapi?", [r"80,000"], [], "engine:nssf", None, False, 0),
    ("NEGATIVE", "Mapato yangu ya ajira ni TZS 800,000 kwa mwezi, PAYE ni ngapi?", [r"78,000"], [], "engine:paye", None, False, 0),
    ("NEGATIVE", "Watu 5 wanapata 700,000, watu 4 wanapata 550,000, watu 6 wanapata 300,000 — NSSF ya jumla ni ngapi?", [COMPUTED], [], "engine:nssf", None, False, 0),
    ("NEGATIVE", "Mishahara ya wafanyakazi wangu ni TZS 4,000,000 kwa mwezi, WCF ni ngapi?", [r"20,000"], [], "engine:wcf", None, False, 0),
    ("NEGATIVE", "Mshahara wa mfanyakazi ni 800k kwa mwezi, NSSF ni ngapi?", [], [], None, None, False, 1),
    ("NEGATIVE", "Je naweza kujisajili VAT kwa hiari ukiwa chini ya kiwango?", [r"(?i)TRA|Kamishna"], [r"(?i)^ndiyo"], FS, None, True, 0),
    ("NEGATIVE", "Overtime inalipwa kiasi gani?", [r"1\.5"], [], FS, None, True, 0),
    ("NEGATIVE", "Kizingiti cha kusajili VAT ni kiasi gani?", [r"200"], [], None, FS, False, 0),
    ("NEGATIVE", "PAYE inalipwa lini?", [r"(?i)tarehe 7|siku 7"], [], None, FS, False, 0),
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
    print("served index identity:", {k: ident["served"].get(k) for k in ("build", "rag_rows_loaded", "rag_facts_text_sha256")} if isinstance(ident["served"], dict) else ident["served"])
    print("committed             :", ident["committed_rows"], ident["committed_sha256"])

    for arm, q, must, must_not, path_prefix, forbid, zero_calls, min_calls in CASES:
        if q in done:
            continue
        t0 = time.time()
        try:
            out = m.run.remote(q)
            reply = out.get("reply", "") if isinstance(out, dict) else str(out)
            tr = out if isinstance(out, dict) else {}
            path, calls = tr.get("answer_path") or tr.get("path"), tr.get("model_calls")
            checks = {"must": all(re.search(p, reply) for p in must), "must_not": not any(re.search(p, reply) for p in must_not)}
            if path_prefix:
                checks["path"] = bool(path and str(path).startswith(path_prefix))
            if forbid:
                checks["path_not_" + forbid] = not (path and str(path).startswith(forbid))
            if zero_calls:
                checks["model_calls_0"] = calls == 0
            if min_calls:
                checks["reached_model_fallback"] = isinstance(calls, int) and calls >= min_calls
            row = dict(arm=arm, q=q, reply=reply, path=path, model_calls=calls, guards=tr.get("guards"), checks=checks, ok=all(checks.values()), took_s=round(time.time() - t0, 1))
        except Exception as e:                                           # noqa: BLE001
            row = dict(arm=arm, q=q, error=repr(e)[:300])
        art["rows"].append(row)
        save()
        flag = "ERR" if "error" in row else ("ok " if row["ok"] else "MISS")
        print(f"[{flag}] {arm:<9} {row.get('took_s', '?'):>6}s {row.get('path')} calls={row.get('model_calls')} {[k for k, v in row.get('checks', {}).items() if not v]}  {q[:60]}\n        -> {(row.get('reply') or row.get('error') or '')[:230]!r}")
    bad = [r for r in art["rows"] if r.get("ok") is False or "error" in r]
    sv = ident["served"] if isinstance(ident["served"], dict) else {}
    id_ok = sv.get("rag_rows_loaded") == ident["committed_rows"] and sv.get("rag_facts_text_sha256") == ident["committed_sha256"]
    print(f"\n{len(art['rows'])} rows; automated-limb misses/errors {len(bad)}; identity rows match: {id_ok}  (READ the replies)")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
