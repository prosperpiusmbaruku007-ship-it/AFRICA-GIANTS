# -*- coding: utf-8 -*-
"""LIVE VERIFICATION (R16, R12c) of the SECOND 2026-11-23 `chike-inference` window: the widened D-FIDELITY-27/28, the model-free SDL-EXEMPTIONS statement route, and the NHIF-named append. RE-ASKS all SIX of today's live misses VERBATIM, plus
the negatives the founder named and the unchanged-route controls. Production chike-inference via the Modal SDK; artifact written atomically after EVERY row, errors captured, resume re-derives every verdict. `must` / `must_not` are INDICATIVE (R38); EVERY reply
is READ. The run also reports, from the guards list of each reply, whether D-FIDELITY-26 and D-FIDELITY-25b have FIRED LIVE (they had not, in the first window). COMMITTED BEFORE ITS RUN (R18).

    EXPECT_BUILD=<sha> python eval/controls/verify_exemptions_nhif_deploy_live_2026_11_23.py   ->  eval/results/exemptions_nhif_deploy_live_2026_11_23.json
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
OUT = os.path.join(REPO, "eval", "results", "exemptions_nhif_deploy_live_2026_11_23.json")
EXPECT_ROWS = 218
EXPECT_BUILD = os.environ.get("EXPECT_BUILD", "")
REFUSED = r"nje ya mada yangu"
NHIF_LINE = r"NHIF haijafunikwa na Chike"
NHIF_FIG = r"(?i)nhif[^.?!]{0,100}(?:\d+(?:[.,]\d+)?\s*%|asilimia\s*\d)"
PREMISES = r"(?i)maeneo\s+ya\s+biashara\W*\(?commercial|inalenga[^.?!]{0,100}ene(?:o|no)\s+la\s+biashara|inalenga[^.?!]{0,100}maeneo\s+ya\s+biashara|commercial\s+premises"
AGE60 = (r"(?i)michango[^.?!]{0,80}(?:huendelea|zinaendelea|inaendelea)[^.?!]{0,40}(?:hadi|mpaka)[^.?!]{0,20}60"
         r"|(?:huisha|zinaisha|inaisha|hukoma|zinakoma)[^.?!]{0,60}(?:anapofikia|ukifikia|ukifika|akifika|anapofika)[^.?!]{0,30}60"
         r"|michango[^.?!]{0,60}(?:huisha|zinaisha|inaisha|hukoma)[^.?!]{0,40}(?:miezi\s+180|miaka\s+15)")
SCHOOL_WRONG = r"(?i)shule[^.?!]{0,60}(?:zinatozwa|inatozwa|inalipa)\s+SDL"
SDL_DENIAL = r"(?i)hauhitaji kulipa SDL|huna wajibu wa kulipa SDL|haitozwi|haihitaji kulipa SDL|haulipi SDL"
STMT = "engine:fixed_statement"
# (arm, question, must, must_not, path_forbidden_prefix, path_required_prefix, model_calls_expected)
CASES = [
    # ---- THE SIX MISSES, VERBATIM ----
    ("MISS1", "SDL inahusu biashara tu au hata waajiri wa nyumbani?", [r"(?i)haijathibitishwa|hakuna kinachotuonyesha|thibitisha na TRA"], [PREMISES], None, None, None),
    ("MISS2", "Kama mfanyakazi anafikisha umri wa miaka 60, je bado anatakiwa kuchangia NSSF?", [], [AGE60], None, None, None),
    ("MISS3", "Michango ya NSSF inaisha ukifika miaka 60?", [], [AGE60], None, None, None),
    ("MISS4", "Ni waajiri gani hawalipi SDL?", [r"ruzuku ya Serikali", r"Gazeti", r"taasisi za elimu zilizosajiliwa"], [r"Act No\. 9", r"(?i)chini ya miaka 18"], None, STMT, 0),
    ("MISS5", "Shule binafsi inalipa SDL?", [r"taasisi za elimu zilizosajiliwa"], [SCHOOL_WRONG], None, STMT, 0),
    ("MISS6", "NHIF inakatwa asilimia ngapi pamoja na NSSF kwenye mshahara?", [NHIF_LINE, r"asilimia 10"], [NHIF_FIG], None, None, None),
    ("MISS6b", "Nani amesamehewa SDL?", [r"ruzuku ya Serikali"], [], None, STMT, 0),
    # ---- the founder's category example, and corpus-held diversions
    ("CAT", "Taasisi ya dini inalipa SDL?", [r"taasisi za dini"], [], None, STMT, 0),
    ("CAT", "Halmashauri inalipa SDL?", [r"halmashauri"], [], None, STMT, 0),
    # ---- NHIF: the line is appended whenever NHIF is named; NSSF-only gets none; NHIF-only (verb-qualified) is still refused
    ("NHIF", "NSSF na NHIF — ni mifumo tofauti au moja?", [NHIF_LINE], [NHIF_FIG], None, None, None),
    ("NHIF-NEG", "NSSF ya mfanyakazi ni asilimia ngapi?", [r"(?i)mfanyakazi"], [NHIF_LINE], None, None, None),
    ("NHIF-NEG", "Makato ya NHIF kwa mshahara wa TZS 800,000 ni kiasi gani?", [REFUSED], [NHIF_LINE], None, None, None),
    # ---- vetoes: these must NOT reach the exemptions statement
    ("VETO", "Nina shule yenye wafanyakazi 15, je natakiwa kulipa SDL?", [], [], STMT, None, None),
    ("VETO", "Wafanyakazi wa nyumbani (domestic workers) — wanaathiri kizingiti cha SDL?", [], [PREMISES], STMT, None, None),
    ("VETO", "SDL inaanzia wafanyakazi wangapi?", [r"10"], [], None, "engine:sdl", 0),
    ("VETO", "Je, kampuni ya madini lazima ilipe SDL kwa wafanyakazi wake?", [], [], STMT, None, None),
    ("VETO", "Waajiri wa EPZ (Export Processing Zone) wanaweza kusamehewa SDL?", [], [], STMT, None, None),
    # ---- D-FIDELITY-25b / the SDL engine: both directions
    ("SDL-CMP", "Nina wafanyakazi 15, je natakiwa kulipa SDL?", [r"(?i)ndiyo"], [SDL_DENIAL], None, "engine:sdl", None),
    ("SDL-CMP", "Wafanyakazi wangu ni 20 na jumla ya mishahara ni TZS 8,000,000 kwa mwezi, SDL ni kiasi gani?", [r"280,000"], [SDL_DENIAL], None, "engine:sdl", None),
    ("SDL-CMP-NEG", "Tuna wafanyakazi 6, je tunatakiwa kulipa SDL?", [r"(?i)chini ya 10|hapana"], [r"(?i)^ndiyo"], None, None, None),
    # ---- UNCHANGED-ROUTE CONTROLS
    ("CTRL", "Annual return ya BRELA inapaswa kuwasilishwa lini?", [r"(?i)siku 28"], [r"(?i)siku 42"], None, STMT, 0),
    ("CTRL", "Kima cha chini cha mshahara kwa mfanyakazi wa nyumbani ni kiasi gani?", [r"328,000", r"80,000"], [r"(?i)karibu"], None, STMT, 0),
    ("CTRL", "Kiwango cha VAT kitakuwa asilimia ngapi 2028?", [r"hakijulikani"], [], None, STMT, 0),
    ("CTRL", "Mshahara wa chini wa sekta ya madini ni kiasi gani kwa mujibu wa GN 605A?", [r"695,000", r"333,500"], [r"(?i)madini na nishati ni karibu"], None, None, None),
    ("CTRL", "Kizingiti cha SDL ni wafanyakazi 4, sivyo?", [r"(?i)hapana|10"], [r"(?i)^ndiyo"], None, None, None),
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
    # DID THE TWO UNEXERCISED GUARDS FIRE? Read from the guards list of every reply: D-FIDELITY-26 is a REPAIR ('repaired'), D-FIDELITY-25b a BLANKING ('blanked') on the SDL compute path.
    art["guards_seen"] = sorted({str(g) for r in art["rows"] for g in (r.get("guards") or [])})
    save()
    live_qs = {c[1] for c in CASES}
    bad = [r for r in art["rows"] if r["q"] in live_qs and (r.get("ok") is False or "error" in r)]
    print(f"\n{len(art['rows'])} rows; identity_ok={ident_ok}; automated misses {len(bad)} (READ every reply); guards seen on any reply: {art['guards_seen']}")
    sys.exit(0 if ident_ok and not bad else 1)


if __name__ == "__main__":
    main()
