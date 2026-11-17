# -*- coding: utf-8 -*-
"""LIVE VERIFICATION (R16, R12c) of the 2026-11-17 deploy (build a2e6611): the 215-row index (licence validity, dividend, four new rows), the flipped licence guard, D-FIDELITY-16, the two repairs -- and NEGATIVES that must
still behave as before. Production chike-inference via the Modal SDK; artifact written after EVERY row, errors captured, resume re-derives every verdict. `must` / `must_not` are INDICATIVE (R38: a probe encodes an expected
answer and can encode a wrong one); replies, path, model_calls and guards are stored for READING -- the replies are the deliverable, not the verdict column (R12b caveat).

The WhatsApp holding line is NOT exercised here: it is sent by a sweep on a real queued draft (needs a webhook message from a test sender). Its evidence is the build match + tests/test_review_timeout.py.

    python eval/controls/verify_licence_followup_deploy_live_2026_11_17.py     ->  eval/results/licence_followup_deploy_live_2026_11_17.json
"""
import hashlib
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
OUT = os.path.join(REPO, "eval", "results", "licence_followup_deploy_live_2026_11_17.json")
EXPECT_BUILD = "a2e6611"
EXPECT_ROWS = 215
# (arm, question, must, must_not, path_forbidden_prefix, path_required_prefix)
CASES = [
    ("LICENCE", "Leseni ya biashara inaisha lini?", [r"12|kumi na mbili"], [], None, None),
    ("LICENCE", "Leseni yangu ya biashara huisha tarehe 30 Juni kila mwaka, sivyo?", [r"12|kumi na mbili"], [r"(?<![Ss]i )(?<!wala )huisha[^.]{0,40}30 Juni"], None, None),
    ("LICENCE", "Leseni ya biashara yangu niliyoipata mwaka huu bado ni ileile. Si lazima niifanyie upya kabla ya tarehe 30 Juni, ndiyo?", [r"12|kumi na mbili"], [r"ifikapo tarehe 30 Juni"], None, None),
    ("LICENCE", "Leseni yangu ya biashara haiishi kila mwaka, inadumu mpaka niifute, sivyo?", [r"12|kumi na mbili"], [r"31 Machi", r"ifikapo tarehe 30 Juni"], None, None),
    ("LICENCE", "Leseni ya biashara ya LGA inahuishwa lini?", [r"12|kumi na mbili"], [r"ifikapo tarehe 30 Juni"], None, None),
    ("AUTHORITY", "Nataka leseni ya biashara ya duka langu, nipate wapi?", [r"(?i)halmashauri"], [r"tra\.go\.tz"], None, None),
    ("DIVIDEND", "Gawio kwa mwekezaji asiye mkazi linakatwa zuio asilimia ngapi?", [r"5|10"], [r"15% kwa wasio wakazi", r"wasio wakazi[^.]{0,20}15"], "engine:corporate_tax", None),
    ("DIVIDEND", "Kampuni yangu haijaorodheshwa kwenye soko la hisa la DSE. Nikigawa gawio kwa wanahisa, withholding tax yake ni 10%, si ndiyo?", [r"10"], [r"15% kwa wasio wakazi"], "engine:corporate_tax", None),
    ("RETURN", "Muda wa mwisho wa kuwasilisha return ya kodi ya mapato ya kampuni TRA ni lini?", [r"miezi 6|miezi sita|30 Juni"], [r"ndani ya miezi 12 baada"], "engine:corporate_tax", None),
    ("RETURN", "Kampuni yangu ina mwaka wa kalenda. Return ya kodi ya mapato ninaiwasilisha lini?", [r"miezi 6|miezi sita|30 Juni"], [r"30 Septemba ya mwaka unaofuata"], None, None),
    ("SEVERANCE", "Malipo ya fidia ya kuachishwa kazi (severance pay) hayapigwi kodi — je, ni kweli?", [], [r"inatozwa kodi ya asilimia 15"], None, None),
    ("SEVERANCE", "Nikiachishwa kazi nitakatwa kodi gani kwenye malipo ya severance?", [r"(?i)mapato ya ajira|viwango vya kawaida|PAYE|TRA"], [r"asilimia 15 \(PAYE\)"], None, None),
    ("PKF", "Mwajiri anagundua vipi kiwango cha mshahara wa chini cha GN 605A kinachofaa kwa kila mfanyakazi wake?", [], [r"lililotolewa na PKF"], None, None),
    ("PKF", "GN 605A ilitolewa na nani?", [r"(?i)serikali|amri|order|sheria ya taasisi"], [r"iliyotolewa na PKF", r"ilitolewa na PKF"], None, None),
    # ---- NEGATIVES: must behave as before ----
    ("NEGATIVE", "Return ya kodi ya mapato ya mtu binafsi ni lini?", [r"30 Juni|miezi 6|miezi sita"], [], None, None),
    ("NEGATIVE", "Kodi ya awamu (provisional tax) inalipwa lini?", [r"(?i)septemba|awamu"], [], None, None),
    ("NEGATIVE", "Ada ya huduma kwa kampuni ya nje ni asilimia ngapi kodi ya zuio?", [r"15"], [], None, None),
    ("NEGATIVE", "Nawezaje kusajili kampuni?", [], [r"halmashauri yako, au BRELA kwa kundi A"], None, None),
    ("NEGATIVE", "Kodi ya mapato ya kampuni ni asilimia ngapi?", [r"30"], [], None, "engine:corporate_tax"),
    ("NEGATIVE", "Nina wafanyakazi 12, mishahara yao yote ni TZS 4,000,000 kwa mwezi, SDL ni ngapi?", [r"140,000"], [], None, "engine:sdl"),   # the first draft omitted the headcount; the engine correctly ASKED for it (R38: the probe was wrong)
    ("NEGATIVE", "Mshahara wa mfanyakazi ni TZS 800,000 kwa mwezi, NSSF ni ngapi?", [r"80,000"], [], None, "engine:nssf"),
    ("NEGATIVE", "Nikate WCF kwenye mshahara wa mfanyakazi?", [r"(?i)hapana|haikatwi|mwajiri"], [r"unapaswa kuikata"], None, None),
]


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
    print("served identity:", {k: ident.get(k) for k in ("build", "rag_rows_loaded", "rag_facts_text_sha256", "config_rag_fact_count")})
    ident_ok = ident.get("build") == EXPECT_BUILD and ident.get("rag_rows_loaded") == EXPECT_ROWS and ident.get("rag_facts_text_sha256") == local_sha
    print(f"IDENTITY build=={EXPECT_BUILD}: {ident.get('build') == EXPECT_BUILD}; rows=={EXPECT_ROWS}: {ident.get('rag_rows_loaded') == EXPECT_ROWS}; served digest == local digest: {ident.get('rag_facts_text_sha256') == local_sha}")
    for arm, q, must, must_not, forbid, require in CASES:
        if q in done:
            continue
        try:
            out = m.run.remote(q)
            reply = out.get("reply", "")
            path = out.get("answer_path") or out.get("path")
            ck = {"must": all(re.search(p, reply) for p in must), "must_not": not any(re.search(p, reply) for p in must_not)}
            if forbid:
                ck["path_not_" + forbid] = not (path and str(path).startswith(forbid))
            if require:
                ck["path"] = bool(path and str(path).startswith(require))
            row = dict(arm=arm, q=q, reply=reply, path=path, model_calls=out.get("model_calls"), guards=out.get("guards"), checks=ck, ok=all(ck.values()))
        except Exception as e:                                           # noqa: BLE001
            row = dict(arm=arm, q=q, error=repr(e)[:300])
        art["rows"].append(row)
        save()
        print(f"[{'ERR' if 'error' in row else 'ok ' if row['ok'] else 'MISS'}] {arm:<9} {row.get('path')} calls={row.get('model_calls')} guards={row.get('guards')} {[k for k, v in row.get('checks', {}).items() if not v]} {q[:60]}\n     -> {(row.get('reply') or row.get('error') or '')[:330]!r}")
    # every verdict is RE-DERIVED here, never carried from a resumed row
    for r in art["rows"]:
        if "reply" in r:
            case = [c for c in CASES if c[1] == r["q"]]
            if case:
                _, _, must, must_not, forbid, require = case[0]
                ck = {"must": all(re.search(p, r["reply"]) for p in must), "must_not": not any(re.search(p, r["reply"]) for p in must_not)}
                if forbid:
                    ck["path_not_" + forbid] = not (r.get("path") and str(r["path"]).startswith(forbid))
                if require:
                    ck["path"] = bool(r.get("path") and str(r["path"]).startswith(require))
                r["checks"], r["ok"] = ck, all(ck.values())
    art["identity_ok"] = ident_ok
    save()
    live_qs = {c[1] for c in CASES}
    bad = [r for r in art["rows"] if r["q"] in live_qs and (r.get("ok") is False or "error" in r)]   # a row whose probe was superseded (the headcount-less SDL question) stays in the artifact for reading but is not counted
    print(f"\n{len(art['rows'])} rows; identity_ok={ident_ok}; automated misses {len(bad)} (READ every reply)")
    sys.exit(0 if ident_ok and not bad else 1)


if __name__ == "__main__":
    main()
