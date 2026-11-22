# -*- coding: utf-8 -*-
"""LIVE VERIFICATION (R16, R12c) of the 2026-11-22 second deploy (chike-inference only): the SDL routing fixes (first-person "natakiwa kulipa", number-free threshold ask), the noun-first headcount, the NSSF EMPLOYER party
resolution and D-FIDELITY-25 (SDL "not payable" told to an employer whose own stated headcount is 10 or more) -- and NEGATIVES that must behave as before. The two founding rows are the preliminary Gate 2 controls gp_24 and gp_22
(that set is BURNED: they are regression specimens here, never a measure); every other row is a different phrasing.
Production chike-inference via the Modal SDK; artifact written atomically after EVERY row, errors captured, resume re-derives every verdict. `must` / `must_not` are INDICATIVE (R38); replies, path, model_calls and guards are stored
and every reply is READ. COMMITTED BEFORE ITS RUN (R18).

    EXPECT_BUILD=<sha> python eval/controls/verify_d25_deploy_live_2026_11_22.py   ->  eval/results/d25_deploy_live_2026_11_22.json
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
OUT = os.path.join(REPO, "eval", "results", "d25_deploy_live_2026_11_22.json")
EXPECT_ROWS = 216
EXPECT_BUILD = os.environ.get("EXPECT_BUILD", "")
# (arm, question, must, must_not, path_forbidden_prefix, path_required_prefix, model_calls_expected)
DENIAL = r"(?i)haihitaji malipo ya SDL|huna wajibu wa kulipa SDL|hauhitaji kulipa SDL|SDL haitozwi"
CASES = [
    # SDL: the founding control verbatim, then other phrasings of the same two defects
    ("SDL", "Naagiza vipuri vya magari kutoka Japan na kuviuza hapa Dar. Wafanyakazi wangu ni 12, je, natakiwa kulipa SDL na inaanzia wafanyakazi wangapi?", [r"(?i)10 au zaidi"], [DENIAL], None, "engine:sdl", None),
    ("SDL", "Nina wafanyakazi 15, je natakiwa kulipa SDL?", [r"(?i)10 au zaidi|ndiyo"], [DENIAL], None, "engine:sdl", None),
    ("SDL", "Duka langu lina wafanyakazi 22 na huuza nguo zilizoagizwa kutoka China. Je, tunatakiwa kulipa SDL?", [r"(?i)10 au zaidi|ndiyo"], [DENIAL], None, "engine:sdl", None),
    ("SDL", "SDL inaanzia wafanyakazi wangapi?", [r"(?i)10 au zaidi"], [], None, "engine:sdl", 0),
    ("SDL-NEG", "Tuna wafanyakazi 6, je tunatakiwa kulipa SDL?", [r"(?i)chini ya 10|hapana"], [r"(?i)^ndiyo"], None, None, None),
    # NSSF party: the founding control verbatim, then other phrasings
    ("PARTY", "Habari, kwa mfanyakazi mmoja mwajiri anatakiwa kuchangia asilimia ngapi ya mshahara wake NSSF?", [r"Sehemu ya mwajiri"], [r"^Sehemu ya mfanyakazi"], None, "engine:nssf", 0),
    ("PARTY", "Kwa mfanyakazi mmoja, mwajiri anapaswa kuchangia kiasi gani NSSF?", [r"(?i)mwajiri"], [r"^Sehemu ya mfanyakazi"], None, None, None),
    ("PARTY-NEG", "NSSF ya mfanyakazi ni asilimia ngapi?", [r"(?i)mfanyakazi"], [r"^Sehemu ya mwajiri"], None, None, None),
    # NEGATIVES that must not move
    ("NEG", "Kama mfanyakazi anafikisha umri wa miaka 60, je bado anatakiwa kuchangia NSSF?", [], [r"^Sehemu ya mwajiri", r"NSSF haina kizingiti"], "engine:", None, None),
    ("NEG", "Kizingiti cha SDL ni wafanyakazi 4, sivyo?", [r"(?i)hapana|10"], [r"(?i)^ndiyo"], None, None, None),
    ("NEG", "Wafanyakazi wa nyumbani (domestic workers) \u2014 wanaathiri kizingiti cha SDL?", [], [r"^Mwajiri mwenye wafanyakazi 10 au zaidi ana wajibu wa kulipa SDL\. Mwenye wafanyakazi chini ya 10 hana wajibu wa kulipa SDL\.$"], None, None, None),
    ("D24-NEG", "Mshahara wa chini wa sekta ya madini ni kiasi gani kwa mujibu wa GN 605A?", [r"695,000", r"333,500"], [r"(?i)madini na nishati ni karibu"], None, None, None),
    ("AR-NEG", "Annual return ya BRELA inapaswa kuwasilishwa lini?", [r"(?i)siku 28"], [r"(?i)siku 42"], None, "engine:fixed_statement", 0),
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
