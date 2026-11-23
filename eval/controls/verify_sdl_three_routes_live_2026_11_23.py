# -*- coding: utf-8 -*-
"""LIVE VERIFICATION (R16, R12c) of the FIFTH 2026-11-23 `chike-inference` window: THREE model-free SDL statement routes -- the presupposition-correcting one ("Mfanyakazi analipa SDL wapi?" was answered live by the model AGREEING the employee pays
and the employer deducts 3.5%), the SDL+NSSF party composite ("SDL na NSSF zinakatwa kwa mfanyakazi?" -> "Mfanyakazi hakatiwi chochote katika SDL au NSSF", wrong for NSSF) and the filing/payment statement (form NOT asserted). Both founding specimens VERBATIM, more
phrasings, the vetoes (where the money GOES, an audit, a calculation, another levy, an amount, two-part) and unchanged-route controls (payer statement, exemptions, mining, SDL engine, rate, NHIF, annual return, an NSSF-only deduction, a multi-levy COMPUTE that the fan-out change must not touch).
Production chike-inference via the Modal SDK; artifact written atomically after EVERY row, errors captured, resume re-derives every verdict. `must` / `must_not` are INDICATIVE (R38); EVERY reply is READ. COMMITTED BEFORE ITS RUN (R18).

    EXPECT_BUILD=<sha> python eval/controls/verify_sdl_three_routes_live_2026_11_23.py   ->  eval/results/sdl_three_routes_live_2026_11_23.json
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
OUT = os.path.join(REPO, "eval", "results", "sdl_three_routes_live_2026_11_23.json")
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
PENALTY_INVENTED = r"(?i)adhabu\s+kwa\s+mwajiri|kuajiri\s+wafanyakazi\s+wengi|bila\s+kusajiliwa"
PEN = r"(?i)adhabu\s+kwa\s+mwajiri|kuajiri\s+wafanyakazi\s+wengi|bila\s+kusajiliwa"
AGREES = r"(?i)mfanyakazi\s+anachangia|kukata\s+3\.5|mfanyakazi\s+hakatiwi\s+chochote|hakatiwi\s+chochote"
FORM = r"ITX|300\.01"
PREM = [r"MWAJIRI pekee", r"Haikatwi kwenye mshahara", r"IDRAS", r"Mkoa wa Kodi", r"havijathibitishwa"]
FILE = [r"IDRAS", r"Mkoa wa Kodi", r"tarehe 7", r"havijathibitishwa"]
NSSF = [r"MWAJIRI pekee", r"HUKATWA", r"asilimia 20", r"asilimia 10"]
CASES = [
    # ---- THE TWO FOUNDING SPECIMENS, verbatim (live, build a67462c) and more phrasings: the statement, 0 model calls
    ("PREMISE", "Mfanyakazi analipa SDL wapi?", PREM, [AGREES, FORM, PEN], None, STMT, 0),
    ("PREMISE", "SDL inakatwa kwa mfanyakazi, nalipa wapi?", PREM, [AGREES, FORM, PEN], None, STMT, 0),
    ("PREMISE", "Mimi ni mfanyakazi, SDL yangu nalipa wapi na kwa fomu gani?", PREM, [AGREES, FORM, PEN], None, STMT, 0),
    ("PREMISE", "Does the employee pay SDL, and where is it paid?", PREM, [AGREES, FORM, PEN], None, STMT, 0),
    ("NSSF", "SDL na NSSF zinakatwa kwa mfanyakazi?", NSSF, [AGREES, PEN], None, STMT, 0),
    ("NSSF", "Nani analipa SDL na NSSF?", NSSF, [AGREES, PEN], None, STMT, 0),
    ("NSSF", "Is SDL and NSSF deducted from the employee?", NSSF, [AGREES, PEN], None, STMT, 0),
    ("FILE", "Nalipa SDL wapi?", FILE, [FORM, AGREES], None, STMT, 0),
    ("FILE", "Fomu gani ya SDL?", FILE, [FORM], None, STMT, 0),
    ("FILE", "SDL inalipwa kwa benki gani?", FILE, [FORM], None, STMT, 0),
    ("FILE", "Nawezaje kuwasilisha ritani ya SDL?", FILE, [FORM], None, STMT, 0),
    ("FILE", "Where do I pay SDL?", FILE, [FORM], None, STMT, 0),
    # ---- VETOES: must NOT reach any of the three (each goes to its own route or the model; the reply is READ)
    ("VETO", "Pesa za SDL zinakwenda wapi na zinatumika kwa nini?", [], [], STMT, None, None),
    ("VETO", "How does TRA conduct an SDL audit and what do they examine?", [], [], STMT, None, None),
    ("VETO", "How does an employer calculate the SDL amount payable each month?", [], [], STMT, None, None),
    ("VETO", "SDL na PAYE nalipa wapi?", [], [], STMT, None, None),
    ("VETO", "SDL ni asilimia ngapi na nalipa wapi?", [], [], STMT, None, None),
    ("VETO", "SDL, NSSF na PAYE zinakatwa kwa mfanyakazi?", [], [], STMT, None, None),
    # ---- unchanged routes
    ("PAYER", "Mwajiri au mfanyakazi analipa SDL?", [r"MWAJIRI pekee", r"si adhabu", r"Haikatwi kwenye mshahara"], [PEN, r"IDRAS"], None, STMT, 0),
    ("PAYER", "SDL inakatwa kwa mfanyakazi?", [r"MWAJIRI pekee", r"Haikatwi kwenye mshahara"], [PEN, r"IDRAS"], None, STMT, 0),
    ("EXEMPT", "Ni waajiri gani hawalipi SDL?", [r"ruzuku ya Serikali", r"Gazeti"], [r"Act No\. 9"], None, STMT, 0),
    ("EXEMPT", "Je, kampuni ya madini lazima ilipe SDL?", [r"Waziri wa Fedha", r"hutozwa SDL"], [r"Sheria ya Madini", r"(?i)msamaha maalum"], None, STMT, 0),
    ("SDL-CMP", "Nina wafanyakazi 15, je natakiwa kulipa SDL?", [r"(?i)ndiyo"], [SDL_DENIAL], None, "engine:sdl", None),
    ("MULTI-CMP", "Nina wafanyakazi 15 na mishahara jumla TZS 6,000,000 kwa mwezi. SDL na NSSF ni kiasi gani?", [r"(?i)SDL", r"(?i)NSSF"], [r"IDRAS"], STMT, "engine:", None),
    ("RATE", "Kiwango cha SDL ni asilimia ngapi?", [], [], STMT, None, None),
    ("NSSF-ONLY", "NSSF inakatwa kwa mfanyakazi?", [], [r"IDRAS", r"MWAJIRI pekee"], STMT, None, None),
    ("CTRL", "NHIF inakatwa asilimia ngapi pamoja na NSSF kwenye mshahara?", [NHIF_LINE], [NHIF_FIG], None, None, None),
    ("CTRL", "Annual return ya BRELA inapaswa kuwasilishwa lini?", [r"(?i)siku 28"], [r"(?i)siku 42"], None, STMT, 0),
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
