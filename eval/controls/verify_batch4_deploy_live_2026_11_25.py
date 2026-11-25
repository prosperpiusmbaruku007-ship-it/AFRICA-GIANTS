# -*- coding: utf-8 -*-
"""LIVE VERIFICATION (R16, R12c) of the THIRD 2026-11-25 `chike-inference` window: batch 3 + batch 4 (the paye_residency route with "ukaazi wa kikodi", D-FIDELITY-34 and its holding line, replacement by LIMBS, the sourced VAT exempt-sales-threshold statement in the registration limb, the foreign-authority repair, six repaired training pairs)
against the behaviour PREDICTED in PROGRESS 4bs / 4bt BEFORE the run. COMMITTED BEFORE ITS RUN (R18). `must` / `must_not` are INDICATIVE (R38: suspect the probe first); EVERY REPLY IS READ BY A PERSON, and the report gives the exact text, path, model calls and guards for each.

    EXPECT_BUILD=<sha> python eval/controls/verify_batch4_deploy_live_2026_11_25.py   ->  eval/results/batch4_deploy_live_2026_11_25.json
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
OUT = os.path.join(REPO, "eval", "results", "batch4_deploy_live_2026_11_25.json")
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
HOLD_PHRASE = r"peke yake si kigezo"
FOREIGN_15 = r"(?i)(?:mgeni|wageni|foreign|expat)[^.?!]{0,80}(?:15\s*%|asilimia\s+15)|(?:15\s*%|asilimia\s+15)[^.?!]{0,80}(?:mgeni|wageni|foreign|expat)"
FOREIGN_AUTH = r"(?i)tra\.go\.ke|\.go\.ke|(?<![a-z])kra(?![a-z])|kenya revenue|(?<![a-z])ura(?![a-z])|hmrc"
BARE_UKAZI = r"(?i)(?<![a-z])ukazi(?![a-z])|(?<![a-z])mkazi(?![a-z])"
NOT_MED_STMT = r"MSAMAHA wa VAT, si zero-rated"
THRESHOLD = r"HAYAHESABIWI"
CASES = [
    # (arm, question, must, must_not, path_forbidden_prefix, path_required_prefix, model_calls_expected)
    # ---- THE FOREIGN EMPLOYEE (the live defect of build 16f0a43), now a model-free statement
    ("FOREIGN", "Does a foreign employee pay PAYE at a different rate from a citizen?", [r"UKAAZI WA KIKODI", r"kodi ya mwisho \(final\)", r"siku 183", r"si 15%"], [BARE_UKAZI, FOREIGN_15], None, STMT, 0),
    # PROBE ERROR FIXED 2026-11-25 (R38, found by reading): the `must` wanted lowercase "mkaazi" but the statement begins that sentence "Mkaazi wa kikodi ...": case, not content. (?i) now.
    ("RESIDENT_FOREIGNER", "Is a resident foreigner taxed on the PAYE bands?", [r"UKAAZI WA KIKODI", r"(?i)mkaazi wa kikodi analipa PAYE kwa mabano"], [BARE_UKAZI], None, STMT, 0),
    ("RESIDENT_FOREIGNER", "Mgeni mwenye makazi ya kudumu Tanzania analipa PAYE kwa bendi au 15%?", [r"UKAAZI WA KIKODI", r"makazi ya kudumu"], [BARE_UKAZI], None, STMT, 0),
    # ---- THE BACKSTOP: a phrasing the route declines (a named month), so D-FIDELITY-34 and its holding line are the layer under test
    ("BACKSTOP", "Mgeni anayefanya kazi Tanzania, kiwango chake cha PAYE ni nini mwezi Januari?", [], [FOREIGN_15], "engine:fixed_statement", None, None),
    # ---- KENYA: never a foreign authority or URL
    ("KENYA", "Kiwango cha PAYE Kenya ni asilimia ngapi?", [], [FOREIGN_AUTH], "engine:fixed_statement", None, None),
    # ---- IMPORTED health + medicines, PHARMACY, CHINA medicines (replacement by limbs, the sourced threshold statement)
    ("IMPORT_HM", "Huduma za afya na dawa zinazoingizwa kutoka nje zinatozwa VAT?", [], [r"(?i)(?:dawa|vifaa\s+tiba)[^.?!;:]{0,50}(?<!si )(?<!not )zero[- ]rated", r"(?<![\d.,])18\s*%"], "engine:fixed_statement", None, None),
    ("PHARMACY", "Duka la dawa linatakiwa kusajili VAT, na dawa zinatozwa VAT gani?", [], [r"(?i)(?:dawa|vifaa\s+tiba)[^.?!;:]{0,50}(?<!si )(?<!not )zero[- ]rated"], "engine:fixed_statement", None, None),
    ("CHINA", "Dawa zinazoingizwa kutoka China zinatozwa VAT?", [], [r"(?i)(?:dawa|vifaa\s+tiba)[^.?!;:]{0,50}(?<!si )(?<!not )zero[- ]rated", r"(?<![\d.,])18\s*%"], "engine:fixed_statement", None, None),
    # ---- NEGATIVES that must NOT hit the foreign guard or the residency route
    ("NEG_DIRECTOR", "Mkurugenzi mgeni anapokea ada ya mkurugenzi, WHT ni asilimia ngapi?", [], [HOLD_PHRASE, r"UKAAZI WA KIKODI"], "engine:fixed_statement", None, None),
    ("NEG_NONRESIDENT", "PAYE ya mfanyakazi asiye mkazi ni asilimia ngapi?", [r"asilimia 15 tambarare"], [HOLD_PHRASE], None, STMT, 0),
    ("NEG_COMPUTE", "Mshahara wangu ni TZS 800,000 kwa mwezi, PAYE ni kiasi gani?", [r"78,000"], [r"UKAAZI WA KIKODI"], "engine:fixed_statement", "engine:paye", None),
    # ---- THE TWO GATE ROWS the batch can move (R12c: 2 of 400): eval_344 and eval_392, verbatim
    ("GATE", "PAYE ya mfanyakazi asiye mkazi ni asilimia 30, sivyo?", [r"asilimia 15 tambarare"], [], None, STMT, 0),
    ("GATE", "Je, mfanyakazi asiye mkazi HALIPI mabano ya kawaida ya PAYE?", [r"asilimia 15 tambarare", r"si 15%|mabano"], [], None, STMT, 0),
    # ---- CONTROLS: every route still owns its own question
    ("CTRL", "PAYE ni asilimia ngapi?", [r"PAYE HAINA kiwango kimoja"], [r"UKAAZI WA KIKODI"], None, STMT, 0),
    ("CTRL", "Bendi za PAYE ni zipi?", [r"kiwango cha 1", r"270,000"], [r"UKAAZI WA KIKODI"], None, STMT, 0),
    ("CTRL", "Huduma za afya zinatozwa VAT? Na dawa je?", [r"YOTE MAWILI", NOT_MED_STMT], [], None, STMT, 0),
    ("CTRL", "WCF inakatwa kwenye nini, mshahara wa msingi tu au pamoja na posho?", [r"ZISIZOBADILIKA"], [], None, STMT, 0),
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
