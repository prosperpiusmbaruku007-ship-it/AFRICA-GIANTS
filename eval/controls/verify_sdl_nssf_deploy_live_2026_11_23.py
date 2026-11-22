# -*- coding: utf-8 -*-
"""LIVE VERIFICATION (R16, R12c) of the 2026-11-23 `chike-inference` window: the 218-row index (SDL household-employer hedge, NSSF age-60 hedge, REVISED SDL exemption row) plus D-FIDELITY-25b (SDL compute path), -26 (NHIF figure repair), -27 (SDL scope by
premises) and -28 (NSSF contributions tied to age 60) -- each with NEGATIVES that must behave as before and UNCHANGED-ROUTE CONTROLS. The founding live specimens are regression specimens, never a measure. Production chike-inference via the Modal SDK;
artifact written atomically after EVERY row, errors captured, resume re-derives every verdict. `must` / `must_not` are INDICATIVE (R38); EVERY reply is READ. COMMITTED BEFORE ITS RUN (R18).

    EXPECT_BUILD=<sha> python eval/controls/verify_sdl_nssf_deploy_live_2026_11_23.py   ->  eval/results/sdl_nssf_deploy_live_2026_11_23.json
"""
import hashlib
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import atomic_artifact  # noqa: E402
REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
OUT = os.path.join(REPO, "eval", "results", "sdl_nssf_deploy_live_2026_11_23.json")
EXPECT_ROWS = 218
EXPECT_BUILD = os.environ.get("EXPECT_BUILD", "")
REFUSED = r"nje ya mada yangu"
NHIF_FIG = r"(?i)nhif[^.?!]{0,100}(?:\d+(?:[.,]\d+)?\s*%|asilimia\s*\d)"
PREMISES = r"(?i)maeneo\s+ya\s+biashara\W*\(?commercial|inalenga[^.?!]{0,100}maeneo\s+ya\s+biashara|commercial\s+premises"
AGE60_CLAIM = r"(?i)michango[^.?!]{0,80}(?:huendelea|zinaendelea|inaendelea)[^.?!]{0,40}(?:hadi|mpaka)[^.?!]{0,20}60|(?:ukifikisha|ukifika|akifikisha)[^.?!]{0,30}60[^.?!]{0,60}(?:hahitaji|huhitaji|hauhitaji)"
SDL_DENIAL = r"(?i)hauhitaji kulipa SDL|huna wajibu wa kulipa SDL|haitozwi|haihitaji kulipa SDL|haulipi SDL"
# (arm, question, must, must_not, path_forbidden_prefix, path_required_prefix, model_calls_expected)
CASES = [
    # D-FIDELITY-26 -- the founding mixed question (verbatim), another NHIF phrasing that reaches the model, and NHIF mentioned WITHOUT a figure
    ("NHIF", "NSSF na NHIF — ni mifumo tofauti au moja?", [r"(?i)nssf"], [NHIF_FIG], None, None, None),
    ("NHIF", "NHIF inakatwa asilimia ngapi pamoja na NSSF kwenye mshahara?", [], [NHIF_FIG], None, None, None),
    ("NHIF-NEG", "NHIF ni bima ya afya au pensheni?", [], [NHIF_FIG], None, None, None),
    ("NHIF-NEG", "Makato ya NHIF kwa mshahara wa TZS 800,000 ni kiasi gani?", [REFUSED], [], None, None, None),
    # D-FIDELITY-27 + the new row 216
    ("SDL-HH", "Wafanyakazi wa nyumbani (domestic workers) — wanaathiri kizingiti cha SDL?", [r"(?i)haijathibitishwa|hakuna kinachotuonyesha|thibitisha na TRA"], [PREMISES], None, None, None),
    ("SDL-HH", "Je, mfanyakazi wa nyumbani anahesabiwa kwenye wafanyakazi 10 wa SDL?", [], [PREMISES], None, None, None),
    ("SDL-HH", "SDL inahusu biashara tu au hata waajiri wa nyumbani?", [], [PREMISES], None, None, None),
    # D-FIDELITY-28 + the new row 217
    ("NSSF-60", "Kama mfanyakazi anafikisha umri wa miaka 60, je bado anatakiwa kuchangia NSSF?", [r"(?i)haisemi|umri wa pensheni|thibitisha na NSSF"], [AGE60_CLAIM], None, None, None),
    ("NSSF-60", "Mfanyakazi wangu ana miaka 61, nimuache kumchangia NSSF?", [], [AGE60_CLAIM], None, None, None),
    ("NSSF-60", "Michango ya NSSF inaisha ukifika miaka 60?", [], [AGE60_CLAIM], None, None, None),
    # D-FIDELITY-25b -- SDL COMPUTE path: the body must never contradict the engine
    ("SDL-CMP", "Nina wafanyakazi 15, je natakiwa kulipa SDL?", [r"(?i)ndiyo"], [SDL_DENIAL], None, "engine:sdl", None),
    ("SDL-CMP", "Wafanyakazi wangu ni 20 na jumla ya mishahara ni TZS 8,000,000 kwa mwezi, SDL ni kiasi gani?", [r"280,000"], [SDL_DENIAL], None, "engine:sdl", None),
    ("SDL-CMP-NEG", "Tuna wafanyakazi 6, je tunatakiwa kulipa SDL?", [r"(?i)chini ya 10|hapana"], [r"(?i)^ndiyo"], None, None, None),
    # the REVISED row 174
    ("SDL-EXEMPT", "Ni waajiri gani hawalipi SDL?", [r"(?i)gazeti|mamlaka ya maji|taesa"], [r"Kifungu|Vifungu"], None, None, None),
    ("SDL-EXEMPT", "Nani amesamehewa SDL?", [], [r"Kifungu|Vifungu"], None, None, None),
    ("SDL-EXEMPT", "Shule binafsi inalipa SDL?", [], [r"Kifungu|Vifungu"], None, None, None),
    # UNCHANGED-ROUTE CONTROLS
    ("CTRL", "Kizingiti cha SDL ni wafanyakazi 4, sivyo?", [r"(?i)hapana|10"], [r"(?i)^ndiyo"], None, None, None),
    ("CTRL", "Annual return ya BRELA inapaswa kuwasilishwa lini?", [r"(?i)siku 28"], [r"(?i)siku 42"], None, "engine:fixed_statement", 0),
    ("CTRL", "Kima cha chini cha mshahara kwa mfanyakazi wa nyumbani ni kiasi gani?", [r"328,000", r"80,000"], [r"(?i)karibu"], None, "engine:fixed_statement", 0),
    ("CTRL", "NSSF ya mfanyakazi ni asilimia ngapi?", [r"(?i)mfanyakazi"], [r"^Sehemu ya mwajiri"], None, None, None),
    ("CTRL", "Mshahara wa chini wa sekta ya madini ni kiasi gani kwa mujibu wa GN 605A?", [r"695,000", r"333,500"], [r"(?i)madini na nishati ni karibu"], None, None, None),
    ("CTRL", "Kiwango cha VAT kitakuwa asilimia ngapi 2028?", [r"hakijulikani"], [], None, "engine:fixed_statement", 0),
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
    print(f"identity_ok={ident_ok}")
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
        print(f"[{'ERR' if 'error' in row else 'ok ' if row['ok'] else 'MISS'}] {arm:<11} {row.get('path')} calls={row.get('model_calls')} guards={row.get('guards')} | {q[:70]!r}")
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
