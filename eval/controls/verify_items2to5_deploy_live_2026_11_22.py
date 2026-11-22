# -*- coding: utf-8 -*-
"""LIVE VERIFICATION (R16, R12c) of the 2026-11-22 third deploy (chike-inference only): item 4 (excise duty / verb-qualified NHIF out of scope), item 5 (future-year rate statement), item 3 (no-figure sector-wage statement; pay cues
`anayelipwa` / `nampa`) -- each with its NEGATIVES (must behave as before) and UNCHANGED-ROUTE CONTROLS (the enumerated blast radius is tested, not assumed). Founding specimens are regression specimens, never a measure (the preliminary
Gate 2 set is BURNED). Production chike-inference via the Modal SDK; artifact written atomically after EVERY row, errors captured, resume re-derives every verdict. `must` / `must_not` are INDICATIVE (R38); EVERY reply is READ.
COMMITTED BEFORE ITS RUN (R18).

    EXPECT_BUILD=<sha> python eval/controls/verify_items2to5_deploy_live_2026_11_22.py   ->  eval/results/items2to5_deploy_live_2026_11_22.json
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
OUT = os.path.join(REPO, "eval", "results", "items2to5_deploy_live_2026_11_22.json")
EXPECT_ROWS = 216
EXPECT_BUILD = os.environ.get("EXPECT_BUILD", "")
REFUSED = r"nje ya mada yangu"
# (arm, question, must, must_not, path_forbidden_prefix, path_required_prefix, model_calls_expected)
CASES = [
    # item 4 -- OOC additions, then the in-scope collisions that must NOT be refused
    ("OOC", "Excise duty ya bia na pombe ni asilimia ngapi?", [REFUSED], [], None, None, None),
    ("OOC", "Vinywaji ninavyouza vina ushuru wa bidhaa, kiwango chake ni kipi?", [REFUSED], [], None, None, None),
    ("OOC", "Makato ya NHIF kwa mshahara wa TZS 800,000 ni kiasi gani?", [REFUSED], [], None, None, None),
    ("OOC", "Mkuu, kwa wafanyakazi wangu NSSF nachangia kama kawaida, ila NHIF ya mwajiri na mfanyakazi inakatwa asilimia ngapi?", [REFUSED], [], None, None, None),
    ("OOC-NEG", "NSSF na NHIF — ni mifumo tofauti au moja?", [], [REFUSED], None, None, None),
    ("OOC-NEG", "Mfanyakazi wangu ana bima ya afya ninayomlipia, je malipo hayo yanaingia kwenye PAYE yake?", [], [REFUSED], None, None, None),
    ("OOC-NEG", "Makato ya NSSF ya mfanyakazi ni asilimia ngapi ya mshahara?", [r"(?i)mfanyakazi"], [REFUSED], None, None, None),
    ("OOC-NEG", "Ninauza bidhaa za duka, kiwango cha VAT ni asilimia ngapi?", [r"18"], [REFUSED], None, None, None),
    # item 5 -- future-year rate statement
    ("FUT", "Nina kampuni mpya na nataka kupanga bajeti ya mwaka ujao. Naomba unipe kiwango rasmi cha VAT kitakachotumika Tanzania mwaka 2028/2029.", [r"hakijulikani", r"asilimia 18"], [r"(?i)rasmi cha VAT.{0,40}2028.{0,20}ni asilimia"], None, "engine:fixed_statement", 0),
    ("FUT", "Kiwango cha SDL itakuwa ngapi mwaka 2027?", [r"hakijulikani", r"3\.5"], [], None, "engine:fixed_statement", 0),
    ("FUT", "What will the VAT rate be in 2028?", [r"hakijulikani"], [], None, "engine:fixed_statement", 0),
    ("FUT-NEG", "Kiwango cha VAT ni asilimia ngapi?", [r"18"], [r"hakijulikani"], "engine:fixed_statement", None, None),
    ("FUT-NEG", "Nitasajiliwa VAT 2028 ikiwa mauzo ni 200M, kiwango ni kipi?", [], [r"hakijulikani"], "engine:fixed_statement", None, None),
    ("FUT-NEG", "Kiwango cha kodi ya mapato ya kampuni mwaka 2025 kilikuwa asilimia ngapi?", [], [r"hakijulikani"], "engine:fixed_statement", None, None),
    # item 3 -- sector-wage statement, the two figure-bearing reaches, and negatives
    ("WAGE", "Kima cha chini cha mshahara kwa mfanyakazi wa nyumbani ni kiasi gani?", [r"328,000", r"265,000", r"160,000", r"80,000"], [r"(?i)karibu TZS 80,000"], None, "engine:fixed_statement", 0),
    ("WAGE", "Mshahara wa chini kwa dada wa kazi za nyumbani ni kiasi gani?", [r"328,000", r"80,000"], [r"(?i)karibu"], None, "engine:fixed_statement", 0),
    ("WAGE", "Kima cha chini cha mshahara kwa mlinzi ni kiasi gani?", [r"(?i)ulinzi"], [], None, "engine:fixed_statement", 0),
    ("WAGE-FIG", "Dada wa kazi anayelipwa 150000 kwa mwezi, je ni halali?", [r"328,000", r"80,000"], [], None, "engine:minimum_wage", 0),
    ("WAGE-FIG", "Mfanyakazi wangu wa nyumbani nampa 90000 kwa mwezi, ni sawa?", [r"328,000", r"80,000"], [], None, "engine:minimum_wage", 0),
    ("WAGE-NEG", "Wafanyakazi wa nyumbani (domestic workers) hawamo kwenye GN 605A — ni kweli?", [], [r"328,000"], "engine:fixed_statement", None, None),
    ("WAGE-NEG", "GN 605A inahusu wafanyakazi wa sekta ya kilimo?", [], [r"(?i)viwango zaidi ya kimoja"], "engine:fixed_statement", None, None),
    ("WAGE-NEG", "mteja amenunua kwa shilingi 2000 tu nampa risiti ya mashine au inaruhusiwa kuandika kwa mkono", [], [r"(?i)GN 605A|mshahara wa chini"], "engine:minimum_wage", None, None),
    # UNCHANGED-ROUTE CONTROLS: the engine / statement routes the sweeps say cannot have moved
    ("CTRL", "Annual return ya BRELA inapaswa kuwasilishwa lini?", [r"(?i)siku 28"], [r"(?i)siku 42"], None, "engine:fixed_statement", 0),
    ("CTRL", "Namlipa mlinzi wangu 200000 kwa mwezi, je ni halali?", [r"(?i)ulinzi|mlinzi"], [], None, "engine:minimum_wage", 0),
    ("CTRL", "Nina wafanyakazi 15, je natakiwa kulipa SDL?", [r"(?i)10 au zaidi|ndiyo"], [], None, "engine:sdl", None),
    ("CTRL", "Mshahara wa chini wa sekta ya madini ni kiasi gani kwa mujibu wa GN 605A?", [r"695,000", r"333,500"], [r"(?i)madini na nishati ni karibu"], None, None, None),
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
        print(f"[{'ERR' if 'error' in row else 'ok ' if row['ok'] else 'MISS'}] {arm:<9} {row.get('path')} calls={row.get('model_calls')} guards={row.get('guards')} | {q[:70]!r}")
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
