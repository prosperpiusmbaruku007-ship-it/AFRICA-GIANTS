# -*- coding: utf-8 -*-
"""LIVE VERIFICATION (R16 steps 2-3, R12c) of the 2026-11-16/17 np_ batch (commit c6570e4): a targeted check of the ENUMERATED blast radius, not another full gate.

Calls the PRODUCTION `chike-inference` ChikeModel through the Modal SDK. Arms:
  IDENTITY   served index == committed (211 rows); build == HEAD.
  ROUTE      the premise phrasings of the four original constants (np_12, np_05, set #2 #10/#11/#12/#14 verbatim) and np_28: must now be MODEL-FREE (path engine:..., model_calls 0).
  GUARD      np_13 / np_20 / np_26: the live replies must no longer carry "31 Machi", "miaka mitatu", "Hakuna siku maalum". NOTE: a guard fires only when the model errs, so a clean reply may be the model being right
             this time; the unit tests (planted, verbatim specimens) are what prove the wiring, and `guards` / `path` are stored so a REPLACED reply is visible.
  AUTHORITY  np_19 / GN 605A / SDL-"mafunzo": no wrong host may reach the user.
  NEGATIVE   TanzLII on GN 487A, a KRA refusal, a multi-levy answer keeping BOTH hosts, the severance TAX question staying OFF the severance statement, and the earlier routes unchanged (how-much overtime still the
             statement, plain computes still compute).
`must` / `must_not` are INDICATIVE (R38): replies, path, model_calls and guards are stored in full for READING. The artifact is written after EVERY row and resumes.

    python eval/controls/verify_np_batch_deploy_live_2026_11_17.py
"""
import hashlib
import json
import os
import re
import sys
import time

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import atomic_artifact  # noqa: E402  (2026-11-17: the artifact is written ATOMICALLY: temp file + os.replace)
REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
OUT = os.path.join(REPO, "eval", "results", "np_batch_deploy_live_2026_11_17.json")
FS = "engine:fixed_statement"

# (arm, question, must [all], must_not [none], path_prefix|None, path_forbidden_prefix|None, model_calls_zero, min_calls)
CASES = [
    ("ROUTE", "Likizo ya mwaka haizidi wiki mbili kwa mujibu wa sheria, sivyo?", [r"28"], [r"siku 30"], FS, None, True, 0),
    ("ROUTE", "Mfanyakazi aliyefanya kazi miezi 8 tu akiachishwa, hastahili malipo ya kuachishwa kazi, sivyo?", [r"12"], [r"miezi 10"], FS, None, True, 0),
    ("ROUTE", "Mfanyakazi wangu hajatumia likizo yake ya mwaka huu. Nimeambiwa ana haki ya siku 28 mfululizo za likizo yenye malipo, siyo?", [r"28"], [], FS, None, True, 0),
    ("ROUTE", "Nina mfanyakazi wa kulipwa kwa wiki ambaye amefanya kazi kwangu miaka miwili. Nikitaka kusitisha ajira yake, notice ya siku 7 bado inatosha, sivyo?", [r"siku 4"], [], FS, None, True, 0),
    ("ROUTE", "Mfanyakazi wangu amefanya kazi miezi 8 tu. Nikisitisha ajira yake sasa, sihitajiki kumlipa severance pay, au siyo?", [r"12"], [], FS, None, True, 0),
    ("ROUTE", "Mfanyakazi wangu anafanya overtime baada ya muda wa kawaida. Nimeambiwa siwezi kumlipa kiwango kilekile cha saa za kawaida, lazima iwe angalau mara moja na nusu, ni kweli?", [r"1\.5"], [], FS, None, True, 0),
    ("ROUTE", "Nina wafanyakazi 6, naomba unisaidie kujua ni asilimia ngapi ya mishahara yao inapaswa kwenda kwenye WCF?", [r"0\.5"], [r"30,000"], "engine:wcf", None, True, 0),
    ("ROUTE", "Mwajiri analipa asilimia ngapi NSSF kila mwezi?", [r"asilimia 10"], [], "engine:nssf", None, True, 0),
    ("GUARD", "Leseni yangu ya biashara haiishi kila mwaka, inadumu mpaka niifute, sivyo?", [r"30 Juni"], [r"31 Machi"], None, None, False, 0),
    ("GUARD", "Kumbukumbu za biashara natakiwa kuzihifadhi kwa muda gani?", [r"miaka 5|miaka mitano"], [r"mitatu|miaka 3\b"], None, None, False, 0),
    ("GUARD", "Nimefungua saluni yangu mwezi huu. Kuna mtu kaniambia nina siku 15 za kuomba TIN kuanzia siku nilipoanza biashara, sivyo?", [r"15"], [r"Hakuna siku maalum"], None, None, False, 0),
    ("GUARD", "Nina vitabu vya mauzo na manunuzi vya duka langu. Nikivihifadhi kwa miaka mitatu tu halafu nikavitupa, hakuna tatizo siyo?", [r"5|tano"], [], None, None, False, 0),
    ("GUARD", "Leseni ya biashara ya LGA inahuishwa lini?", [r"30 Juni"], [r"31 Machi"], None, None, False, 0),
    ("AUTHORITY", "Mfanyakazi akijifungua, likizo ya uzazi ni siku ngapi?", [r"84"], [r"immigration\.go\.tz"], None, None, False, 0),
    ("AUTHORITY", "Mwajiri anagundua vipi kiwango cha mshahara wa chini cha GN 605A kinachofaa kwa kila mfanyakazi wake?", [], [r"wcf\.go\.tz", r"(?i)PKF", r"osha\.go\.tz"], None, None, False, 0),
    ("AUTHORITY", "nimeajiri watu watano tu je nalipa ile ya mafunzo", [], [r"nssf\.go\.tz", r"brela\.go\.tz"], None, None, False, 0),
    ("NEGATIVE", "GN 487A ilianza kutumika tarehe ngapi?", [r"28 Julai 2025"], [r"kazi\.go\.tz"], None, None, False, 0),
    ("NEGATIVE", "Nina biashara Nairobi Kenya, nalipa kodi ya mapato kwa KRA kiasi gani?", [], [r"tra\.go\.tz"], None, None, False, 0),
    ("NEGATIVE", "Kuna tofauti gani kati ya tarehe za NSSF na SDL za kulipa?", [], [], None, None, False, 0),
    ("NEGATIVE", "Malipo ya fidia ya kuachishwa kazi (severance pay) hayapigwi kodi — je, ni kweli?", [], [], None, FS, False, 0),
    ("NEGATIVE", "Overtime inalipwa kiasi gani?", [r"1\.5"], [], FS, None, True, 0),
    ("NEGATIVE", "Likizo ya mwaka ni siku ngapi?", [r"28"], [], FS, None, True, 0),
    ("NEGATIVE", "Mshahara wa mfanyakazi ni TZS 800,000 kwa mwezi, NSSF ni ngapi?", [r"80,000"], [], "engine:nssf", None, False, 0),
    ("NEGATIVE", "Mapato yangu ya ajira ni TZS 800,000 kwa mwezi, PAYE ni ngapi?", [r"78,000"], [], "engine:paye", None, False, 0),
    ("NEGATIVE", "Mishahara ya wafanyakazi wangu ni TZS 4,000,000 kwa mwezi, WCF ni ngapi?", [r"20,000"], [], "engine:wcf", None, False, 0),
    ("NEGATIVE", "Nina wafanyakazi 7 tu, bado sihusiki na SDL, sivyo?", [], [], None, FS, False, 0),
    ("NEGATIVE", "Mfanyakazi wa mshahara wa kila mwezi aliyekaa zaidi ya mwezi mmoja, siwezi kumpa notisi ya siku 7 tu, sivyo?", [r"28"], [], FS, None, True, 0),
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
        atomic_artifact.write_json(OUT, art, ensure_ascii=False, indent=1)

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
            row = dict(arm=arm, q=q, reply=reply, path=path, model_calls=calls, guards=tr.get("guards"), checks=checks, ok=all(checks.values()), took_s=round(time.time() - t0, 1))
        except Exception as e:                                           # noqa: BLE001
            row = dict(arm=arm, q=q, error=repr(e)[:300])
        art["rows"].append(row)
        save()
        flag = "ERR" if "error" in row else ("ok " if row["ok"] else "MISS")
        print(f"[{flag}] {arm:<9} {row.get('took_s', '?'):>6}s {row.get('path')} calls={row.get('model_calls')} guards={row.get('guards')} {[k for k, v in row.get('checks', {}).items() if not v]}  {q[:60]}\n        -> {(row.get('reply') or row.get('error') or '')[:230]!r}")
    bad = [r for r in art["rows"] if r.get("ok") is False or "error" in r]
    sv = ident["served"] if isinstance(ident["served"], dict) else {}
    id_ok = sv.get("rag_rows_loaded") == ident["committed_rows"] and sv.get("rag_facts_text_sha256") == ident["committed_sha256"]
    print(f"\n{len(art['rows'])} rows; automated-limb misses/errors {len(bad)}; identity rows match: {id_ok}  (READ the replies)")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
