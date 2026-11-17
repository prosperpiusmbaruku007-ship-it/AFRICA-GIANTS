# -*- coding: utf-8 -*-
"""LIVE VERIFICATION (R16, R12c) of the 2026-11-17 BATCH 2 deploy: the fabricated-name guard (incl. GN 605A issuer BY OFFICE), the licence "siku 90" duration guard, the "Leseni yangu ya biashara" authority cue, severance + "kodi gani" -> TRA,
the individual-return and licence-validity model-free statement routes (incl. premise phrasings), lga.go.tz replaced -- and NEGATIVES that must behave as before (a fee + renewal two-part question still on the MODEL path; a WCF / office question untouched).
Production chike-inference via the Modal SDK; artifact written after EVERY row, errors captured, resume re-derives every verdict. `must` / `must_not` are INDICATIVE (R38); replies, path, model_calls and guards are stored for READING.

    python eval/controls/verify_batch5_deploy_live_2026_11_17.py   ->  eval/results/batch5_deploy_live_2026_11_17.json
"""
import hashlib
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import atomic_artifact  # noqa: E402  (2026-11-17: the artifact is written ATOMICALLY: temp file + os.replace)
REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
OUT = os.path.join(REPO, "eval", "results", "batch5_deploy_live_2026_11_17.json")
EXPECT_ROWS = 215
EXPECT_BUILD = os.environ.get("EXPECT_BUILD", "")
PERSON = r"Simbachawene|Majaliwa|Kikwete|MHE\.|Mheshimiwa|Samia Suluhu|Mwigulu|Kidata"
# (arm, question, must, must_not, path_forbidden_prefix, path_required_prefix, model_calls_expected)
CASES = [
    # --- the two regressions, VERBATIM from the gold files: model-free, each figure against its OWN limb ---
    ("PAIR", "Mapato yangu ni TZS 120,000,000 katika miezi 6 lakini kwa mwaka mzima ni TZS 190,000,000 — je nasajili VAT na kwa kigezo kipi?", [r"(?i)ndiyo", r"120,000,000", r"(?i)miezi 6", r"(?i)kigezo kimoja tu kinatosha"], [r"(?i)niambie jumla"], None, "engine:vat_registration", 0),
    ("PAIR", "Mapato yangu ni TZS 199,000,000 kwa mwaka na TZS 99,000,000 kwa miezi 6 — je nasajili VAT?", [r"(?i)hapana", r"(?i)vigezo vyote viwili", r"(?i)ukivuka kimojawapo"], [r"(?i)niambie jumla"], None, "engine:vat_registration", 0),
    ("PAIR", "Mauzo yangu ni TZS 250,000,000 kwa mwaka na TZS 150,000,000 kwa miezi 6. Nijisajili VAT?", [r"(?i)ndiyo", r"(?i)vigezo vyote viwili"], [], None, "engine:vat_registration", 0),
    # --- what must STILL ask / behave as before ---
    ("STILL-ASKS", "Mauzo yangu ni milioni 150 kwa mwaka na milioni 80 kwa mwaka. Je nijisajili VAT?", [r"(?i)ili nikwambie|niambie"], [r"(?i)ndiyo, unatakiwa"], None, None, 0),
    ("STILL-ASKS", "Nauza milioni 25 kila mwezi. Je nijisajili VAT?", [r"(?i)sitakisii mauzo ya mwaka"], [r"300,000,000"], None, None, 0),
    ("EARLIER", "Mimi nina biashara ya kuuza vifaa, mauzo yangu ya mwaka bado hayajafika milioni 200 lakini ndani ya miezi 6 nimeuza milioni 110. Sihitaji kujisajili VAT kwa sababu mwaka bado haujaisha, siyo?", [r"110,000,000", r"(?i)lazima"], [], None, "engine:vat_registration", 0),
    ("EARLIER", "Biashara yangu inauza kwa wastani wa milioni 18 kila mwezi. Je nijisajili VAT?", [r"216,000,000", r"× 12"], [r"(?i)sitakisii"], None, "engine:vat_registration", 0),
    ("EARLIER", "Mauzo yangu ni milioni 250 kwa mwaka. Nijisajili VAT?", [r"(?i)lazima|unatakiwa"], [], None, "engine:vat_registration", 0),
    ("D19", "Kama biashara yangu inauza kwa wastani wa milioni 18 kila mwezi, hiyo hela ipo chini ya milioni 200 kwa mwaka?", [], [r"216,000,000[^.]{0,80}\.\s*Hii ni chini ya", r"216,000,000 ni chini ya"], None, None, None),
    ("NEGATIVE", "Naomba TIN lini baada ya kuanza biashara?", [r"siku 15"], [], None, "engine:fixed_statement", 0),
    ("NEGATIVE", "Nahitaji leseni ya biashara, inagharimu kiasi gani na inaisha lini?", [r"miezi 12", r"(?i)ada"], [r"lga\.go\.tz"], None, "engine:fixed_statement", 0),
    ("NEGATIVE", "Nani alisaini GN 605A?", [], [r"VELMA", r"PKF Eastern Africa au"], None, None, None),
    ("NEGATIVE", "Nina wafanyakazi 12, mishahara yao yote ni TZS 4,000,000 kwa mwezi, SDL ni ngapi?", [r"140,000"], [], None, "engine:sdl", None),
    ("NEGATIVE", "Mshahara wangu ni TZS 800,000 kwa mwezi, PAYE ni kiasi gani?", [r"(?i)paye"], [], None, None, None),
]


def _checks(row, case):
    _, _, must, must_not, forbid, require, calls = case
    reply, path = row["reply"], row.get("path")
    ck = {"must": all(re.search(p, reply) for p in must), "must_not": not any(re.search(p, reply) for p in must_not)}
    if forbid:
        ck["path_not_" + forbid] = not (path and str(path).startswith(forbid))
    if require:
        ck["path"] = bool(path and str(path).startswith(require))
    if calls is not None:
        ck["model_calls"] = (row.get("model_calls") == calls) if calls == 0 else bool(row.get("model_calls"))
    return ck


def main():
    import modal
    m = modal.Cls.from_name("chike-inference", "ChikeModel")()
    art = json.load(open(OUT, encoding="utf-8")) if os.path.exists(OUT) else {"identity": None, "rows": []}
    art["rows"] = [r for r in art["rows"] if "error" not in r]
    done = {r["q"] for r in art["rows"]}
    save = lambda: atomic_artifact.write_json(OUT, art, ensure_ascii=False, indent=1)
    if not art.get("identity"):
        art["identity"] = m.served_index_identity.remote()
        save()
    ident = art["identity"]
    local = json.load(open(os.path.join(REPO, "chike-inference", "rag_facts_text.json"), encoding="utf-8"))
    local_sha = hashlib.sha256(json.dumps(local, ensure_ascii=False).encode("utf-8")).hexdigest()
    ident_ok = (not EXPECT_BUILD or ident.get("build") == EXPECT_BUILD) and ident.get("rag_rows_loaded") == EXPECT_ROWS and ident.get("rag_facts_text_sha256") == local_sha
    print("served identity:", {k: ident.get(k) for k in ("build", "rag_rows_loaded", "rag_facts_text_sha256", "config_rag_fact_count")})
    print(f"IDENTITY build=={EXPECT_BUILD or '(unchecked)'}: {EXPECT_BUILD in ('', ident.get('build'))}; rows=={EXPECT_ROWS}: {ident.get('rag_rows_loaded') == EXPECT_ROWS}; served digest == local digest: {ident.get('rag_facts_text_sha256') == local_sha}")
    for case in CASES:
        arm, q = case[0], case[1]
        if q in done:
            continue
        try:
            out = m.run.remote(q)
            row = dict(arm=arm, q=q, reply=out.get("reply", ""), path=out.get("answer_path") or out.get("path"), model_calls=out.get("model_calls"), guards=out.get("guards"))
        except Exception as e:                                           # noqa: BLE001
            row = dict(arm=arm, q=q, error=repr(e)[:300])
        if "reply" in row:
            row["checks"] = _checks(row, case)
            row["ok"] = all(row["checks"].values())
        art["rows"].append(row)
        save()
        print(f"[{'ERR' if 'error' in row else 'ok ' if row['ok'] else 'MISS'}] {arm:<12} {row.get('path')} calls={row.get('model_calls')} guards={row.get('guards')} {[k for k, v in row.get('checks', {}).items() if not v]} {q[:60]}\n     -> {(row.get('reply') or row.get('error') or '')[:330]!r}")
    for r in art["rows"]:                                                # every verdict RE-DERIVED, never carried from a resumed row
        c = [x for x in CASES if x[1] == r["q"]]
        if "reply" in r and c:
            r["checks"] = _checks(r, c[0])
            r["ok"] = all(r["checks"].values())
    art["identity_ok"] = ident_ok
    save()
    live_qs = {c[1] for c in CASES}
    bad = [r for r in art["rows"] if r["q"] in live_qs and (r.get("ok") is False or "error" in r)]
    print(f"\n{len(art['rows'])} rows; identity_ok={ident_ok}; automated misses {len(bad)} (READ every reply)")
    sys.exit(0 if ident_ok and not bad else 1)


if __name__ == "__main__":
    main()
