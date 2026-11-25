# -*- coding: utf-8 -*-
"""LIVE VERIFICATION (R16, R12c) of the 2026-11-25 `chike-inference` window: the 224-row index (medicines, PAYE base, SDL deemed month, WCF base; row 66 revised), the fragment-merge decomposer, D-FIDELITY-32 and the two model-free routes (vat_medicines, paye_base).
COMMITTED BEFORE ITS RUN (R18). `must` / `must_not` are INDICATIVE (R38: suspect the probe first, and a flat column proves nothing on wrong-base or added-fabrication defects); EVERY REPLY IS READ BY A PERSON. The FOLLOW-UP arm records the exact reply, and the founder's rule for it is: if either limb is wrong, do NOT patch in the window.

    EXPECT_BUILD=<sha> python eval/controls/verify_two_routes_deploy_live_2026_11_25.py   ->  eval/results/two_routes_deploy_live_2026_11_25.json
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
OUT = os.path.join(REPO, "eval", "results", "two_routes_deploy_live_2026_11_25.json")
EXPECT_ROWS = 224
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
STMT = "engine:fixed_statement"
WRONG_YES = r"(?i)^ndiyo[^.?!]{0,120}anatakiwa\s+kusajili"
NSSF7 = r"(?i)nssf[^.?!]{0,80}(?:siku|tarehe)\s+(?:ya\s+)?7(?![0-9])|zote\s+mbili\s+zinalipwa\s+ndani\s+ya\s+siku\s+7|michango\s+ya\s+NSSF[^.?!]{0,60}tarehe\s+7"
CASH = r"(?i)cash\s+basis|si\s+pamoja\s+na\s+posho|bila\s+posho|posho[^.?!]{0,40}(?:hazihesabiwi|hazijumuishwi)"
ZR_MED = r"(?i)(?:dawa|vifaa\s+tiba|medicines?)[^.?!;:]{0,50}(?<!si )(?<!not )zero[- ]rated"
BASIC_ONLY = r"(?i)PAYE[^.?!;]{0,90}(?<!si )(?<!not )(?:mshahara\s+wa\s+msingi\s+pekee|basic\s+salary\s+only)"
OLD_DEEMED = r"(?i)si\s+Desemba\s+wala\s+miezi\s+mingine|mishahara\s+ya\s+mwezi\s+husika\s+tu"
CASH_BASE = r"(?i)gross\s+cash|cash\s+emoluments|fedha\s+taslimu\s+pekee"
NOT_MED_STMT = r"MSAMAHA wa VAT, si zero-rated"
CASES = [
    # (arm, question, must, must_not, path_forbidden_prefix, path_required_prefix, model_calls_expected)
    # ---- MEDICINES, the model-free statement (the live defect: "zero-rated (tozo 0%)")
    ("MEDICINES", "Dawa zinatozwa VAT?", [r"MSAMAHA wa VAT, si zero-rated", r"kwa matumizi ya sehemu hugawanywa kwa fomula"], [r"tozo 0%", ZR_MED], None, STMT, 0),
    ("MEDICINES", "Vifaa tiba vinatozwa VAT?", [r"MSAMAHA wa VAT"], [ZR_MED], None, STMT, 0),
    ("MEDICINES", "Are medicines VAT-exempt in Tanzania?", [r"MSAMAHA wa VAT"], [ZR_MED], None, STMT, 0),
    ("MEDICINES", "Dawa zinazouzwa nje ya nchi zinatozwa VAT?", [r"zero-rated", r"msamaha"], [], None, STMT, 0),
    # ---- THE MERGED FOLLOW-UP: exact reply recorded; the founder's rule: either limb wrong -> do not patch in the window
    ("FOLLOWUP", "Huduma za afya zinatozwa VAT? Na dawa je?", [], [ZR_MED, r"(?i)duka\s+la\s+dawa"], None, None, None),
    # ---- PAYE BASE, the model-free statement
    ("PAYEBASE", "Posho ya nyumba inahesabiwa kwenye SDL, na tofauti yake na PAYE ni ipi?", [r"MAPATO YA AJIRA", r"Kwa SDL:"], [BASIC_ONLY], None, STMT, 0),
    ("PAYEBASE", "PAYE inakokotolewa kwa mshahara wa msingi tu au pamoja na posho?", [r"MAPATO YA AJIRA", r"si mshahara wa msingi pekee"], [BASIC_ONLY, r"Kwa SDL:"], None, STMT, 0),
    ("PAYEBASE", "Bonasi na kamisheni zinaingia kwenye PAYE?", [r"MAPATO YA AJIRA", r"bonasi"], [BASIC_ONLY], None, STMT, 0),
    # ---- INDEX ARMS: phrasings the routes VETO, so the new rows are reached through RETRIEVAL (the 4bn lesson: an arm that the route answers does not test the index)
    ("INDEX", "PAYE ya mwezi Januari inakokotolewa kwa mshahara wa msingi tu au pamoja na posho?", [], [BASIC_ONLY], "engine:fixed_statement", None, None),
    ("INDEX", "SDL ya mwezi Januari inahesabiwa kwa mshahara wa Januari au Desemba?", [], [OLD_DEEMED], None, None, None),
    ("INDEX", "WCF inakatwa kwenye nini, mshahara wa msingi tu au pamoja na posho?", [r"(?i)posho"], [CASH_BASE], None, None, None),
    ("INDEX", "Mwajiri anaweza kumkata mfanyakazi mchango wa WCF kwenye mshahara wake?", [r"(?i)hap|haruhusiwi|hakati|hakatwi|si\s+mfanyakazi|mwajiri\s+pekee"], [r"(?i)ndiyo[^.?!]{0,60}anaweza\s+kumkata"], None, None, None),
    ("INDEX", "Duka la dawa linatakiwa kusajili VAT, na dawa zinatozwa VAT gani?", [], [ZR_MED], None, None, None),
    # ---- SEVERANCE (the founder's check: miezi 12, mwaka mmoja, and the vague phrasing that ranked 5)
    ("SEVERANCE", "Mfanyakazi amefanya kazi miezi 12 mfululizo, nikimwachisha nimlipe severance kiasi gani?", [r"siku 7"], [], None, None, None),
    ("SEVERANCE", "Nimefanya kazi mwaka mmoja na nimeachishwa kazi, nina haki ya malipo gani ya kuachishwa?", [r"(?i)siku 7|angalau"], [], None, None, None),
    ("SEVERANCE", "Naomba maelezo ya severance pay kwa mfanyakazi aliyeachishwa.", [], [], None, None, None),
    # ---- NEGATIVES: each must NOT reach the new statements
    ("NEG", "Daktari anayetoa huduma za kitaalamu anatakiwa kusajili VAT?", [r"MSAMAHA", r"YOTE MAWILI"], [NOT_MED_STMT], None, STMT, 0),
    ("NEG", "Dawa za TZS 5,000,000 nimeuza, VAT ni ngapi?", [], [NOT_MED_STMT], "engine:fixed_statement", None, None),
    ("NEG", "PAYE ni asilimia ngapi?", [], [r"MAPATO YA AJIRA"], None, None, None),
    ("NEG", "Mshahara wangu TZS 1,200,000 na posho TZS 200,000, PAYE ni kiasi gani?", [r"(?i)paye"], [r"MAPATO YA AJIRA"], "engine:fixed_statement", None, None),
    ("NEG", "Mhandisi anatakiwa kusajili VAT bila kujali mauzo?", [], [NOT_MED_STMT], None, None, None),
    ("CTRL", "Msingi wa kukokotoa SDL ni nini — posho zinaingia?", [r"POSHO ZOTE", r"ZIMO kwenye msingi"], [], None, STMT, 0),
    ("CTRL", "Nina wafanyakazi 15, je natakiwa kulipa SDL?", [r"(?i)ndiyo"], [], None, "engine:sdl", None),
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
