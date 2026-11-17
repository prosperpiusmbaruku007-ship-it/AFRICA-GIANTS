# -*- coding: utf-8 -*-
"""LIVE VERIFICATION (R16, R12c) of the 2026-11-17 BATCH 2 deploy: the fabricated-name guard (incl. GN 605A issuer BY OFFICE), the licence "siku 90" duration guard, the "Leseni yangu ya biashara" authority cue, severance + "kodi gani" -> TRA,
the individual-return and licence-validity model-free statement routes (incl. premise phrasings), lga.go.tz replaced -- and NEGATIVES that must behave as before (a fee + renewal two-part question still on the MODEL path; a WCF / office question untouched).
Production chike-inference via the Modal SDK; artifact written after EVERY row, errors captured, resume re-derives every verdict. `must` / `must_not` are INDICATIVE (R38); replies, path, model_calls and guards are stored for READING.

    python eval/controls/verify_batch2_deploy_live_2026_11_17.py   ->  eval/results/batch2_deploy_live_2026_11_17.json
"""
import hashlib
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
OUT = os.path.join(REPO, "eval", "results", "batch2_deploy_live_2026_11_17.json")
EXPECT_ROWS = 215
EXPECT_BUILD = os.environ.get("EXPECT_BUILD", "")
PERSON = r"Simbachawene|Majaliwa|Kikwete|MHE\.|Mheshimiwa|Samia Suluhu|Mwigulu|Kidata"
# (arm, question, must, must_not, path_forbidden_prefix, path_required_prefix, model_calls_expected)
CASES = [
    # --- the fabricated person / issuer by office ---
    ("NAME", "GN 605A ilitolewa na nani?", [r"(?i)waziri|amri|order"], [PERSON, r"Mawasiliano na Uchukuzi", r"PKF Eastern Africa ilitoa"], None, None, None),
    ("NAME", "Nani alisaini GN 605A?", [], [PERSON, r"Mawasiliano na Uchukuzi"], None, None, None),
    ("NAME", "Kima cha chini cha mshahara GN 605A kilitangazwa na waziri yupi?", [], [PERSON, r"Mawasiliano na Uchukuzi"], None, None, None),
    # --- licence validity: statement route, plain + premise phrasings (model-free) ---
    ("LICENCE-STMT", "Leseni ya biashara inaisha lini?", [r"miezi 12"], [r"ifikapo tarehe 30 Juni"], None, "engine:fixed_statement", 0),
    ("LICENCE-STMT", "Leseni yangu ya biashara haiishi kila mwaka, inadumu mpaka niifute, sivyo?", [r"miezi 12"], [r"ifikapo tarehe 31 Machi", r"inatakiwa kuwa updated"], None, "engine:fixed_statement", 0),   # the first draft said [r"31 Machi"]: the CORRECT statement names it under negation (R38: the probe was wrong)
    ("LICENCE-STMT", "Leseni ya biashara yangu niliyoipata mwaka huu bado ni ileile. Si lazima niifanyie upya kabla ya tarehe 30 Juni, ndiyo?", [r"miezi 12"], [r"ifikapo tarehe 30 Juni"], None, "engine:fixed_statement", 0),
    ("LICENCE-STMT", "Leseni ya biashara ya LGA inahuishwa lini?", [r"miezi 12", r"halmashauri"], [r"siku 90", r"lga\.go\.tz"], None, "engine:fixed_statement", 0),
    ("LICENCE-STMT", "Leseni ya duka langu inaisha mwezi gani?", [r"miezi 12"], [], None, "engine:fixed_statement", 0),
    # --- individual return: statement route ---
    ("RETURN-STMT", "Return ya kodi ya mapato ya mtu binafsi ni lini?", [r"miezi 6", r"30 Juni"], [r"asilimia 0"], None, "engine:fixed_statement", 0),
    ("RETURN-STMT", "Mwisho wa kuwasilisha return ya kodi ya mapato kwa mtu binafsi ni lini?", [r"miezi 6", r"30 Juni"], [], None, "engine:fixed_statement", 0),
    ("RETURN-STMT", "Nina biashara binafsi na mwaka wangu wa hesabu umeishia tarehe 31 Desemba. Kwa hiyo return ya income tax sihitaji kusubiri miezi 12 mingine, naweza kuwasilisha ndani ya miezi 6, sivyo?", [r"miezi 6"], [], None, "engine:fixed_statement", 0),
    # --- authority cue / lga.go.tz on the MODEL path (a phrasing the routes decline) ---
    ("AUTHORITY", "Nataka leseni ya biashara ya duka langu, nipate wapi?", [r"(?i)halmashauri"], [r"tra\.go\.tz", r"lga\.go\.tz"], None, None, None),
    ("AUTHORITY", "Leseni yangu ya biashara nikiipoteza nifanyeje?", [], [r"lga\.go\.tz", r"mlywf\.go\.tz"], None, None, None),
    # --- severance + "kodi gani" -> TRA ---
    ("SEVERANCE", "Nikiachishwa kazi nitakatwa kodi gani kwenye malipo ya severance?", [r"(?i)tra\.go\.tz|TRA"], [r"kazi\.go\.tz", r"asilimia 15 \(PAYE\)"], None, None, None),
    ("SEVERANCE", "Severance ni siku ngapi?", [], [], None, "engine:fixed_statement", 0),
    # --- NEGATIVES ---
    ("NEGATIVE", "Nahitaji leseni ya biashara, inagharimu kiasi gani na inaisha lini?", [], [r"lga\.go\.tz", r"siku 90", r"ifikapo tarehe 30 Juni"], "engine:fixed_statement", None, 1),
    ("NEGATIVE", "Ada ya leseni ya biashara ni kiasi gani?", [], [r"lga\.go\.tz"], "engine:fixed_statement", None, 1),
    ("NEGATIVE", "Nikate WCF kwenye mshahara wa mfanyakazi?", [r"(?i)hapana|haikatwi|mwajiri"], [r"unapaswa kuikata", PERSON], None, None, None),
    ("NEGATIVE", "Kamishna Mkuu wa TRA anafanya nini?", [], [PERSON], None, None, None),
    ("NEGATIVE", "Return ya kodi ya mapato ya kampuni ni lini?", [r"miezi 6|miezi sita|30 Juni"], [r"ndani ya miezi 12 baada", r"30 Septemba ya mwaka"], "engine:fixed_statement", None, None),
    ("NEGATIVE", "Kodi ya awamu (provisional tax) inalipwa lini?", [r"(?i)septemba|awamu"], [], "engine:fixed_statement", None, None),
    ("NEGATIVE", "Ada ya huduma kwa kampuni ya nje ni asilimia ngapi kodi ya zuio?", [r"15"], [], "engine:fixed_statement", None, None),
    ("NEGATIVE", "Gawio kwa mwekezaji asiye mkazi linakatwa zuio asilimia ngapi?", [r"5|10"], [r"15% kwa wasio wakazi"], "engine:fixed_statement", None, None),
    ("NEGATIVE", "Nina wafanyakazi 12, mishahara yao yote ni TZS 4,000,000 kwa mwezi, SDL ni ngapi?", [r"140,000"], [], None, "engine:sdl", None),
    ("NEGATIVE", "Nawezaje kusajili kampuni?", [], [r"halmashauri yako, au BRELA kwa kundi A"], None, None, None),
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
    save = lambda: json.dump(art, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
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
