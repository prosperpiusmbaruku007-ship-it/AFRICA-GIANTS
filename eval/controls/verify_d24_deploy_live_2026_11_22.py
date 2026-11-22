# -*- coding: utf-8 -*-
"""LIVE VERIFICATION (R16, R12c) of the 2026-11-22 deploy (chike-inference only): D-FIDELITY-24, another sector's minimum wage (765,900, energy / international) stated as a MINING rate under GN 605A --
and NEGATIVES that must behave as before (a correct energy question, a domestic-worker wage, the D-FIDELITY-21/23 GN 605A guards, the annual-return statement).
Production chike-inference via the Modal SDK; artifact written atomically after EVERY row, errors captured, resume re-derives every verdict. `must` / `must_not` are INDICATIVE (R38); replies, path, model_calls and guards are stored
and every reply is READ. COMMITTED BEFORE ITS RUN (R18).

    EXPECT_BUILD=<sha> python eval/controls/verify_d24_deploy_live_2026_11_22.py   ->  eval/results/d24_deploy_live_2026_11_22.json
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
OUT = os.path.join(REPO, "eval", "results", "d24_deploy_live_2026_11_22.json")
EXPECT_ROWS = 216
EXPECT_BUILD = os.environ.get("EXPECT_BUILD", "")
# (arm, question, must, must_not, path_forbidden_prefix, path_required_prefix, model_calls_expected)
FOUR = [r"333,500", r"397,600", r"595,000", r"695,000"]
MINING_RESTATEMENT = r"Sekta ya Madini katika GN 605A \(kipengele cha 10\)"
CASES = [
    # D-FIDELITY-24: the founding question verbatim, and three mining phrasings
    ("D24", "Mshahara wa chini wa sekta ya madini ni kiasi gani kwa mujibu wa GN 605A?", FOUR, [r"(?i)madini na nishati ni karibu"], None, None, None),
    ("D24", "Kima cha chini cha mshahara kwa mchimbaji madini ni kiasi gani?", [], [r"(?i)madini[^.]{0,60}765,900"], None, None, None),
    ("D24", "Mgodi wangu mdogo wa dhahabu, kima cha chini cha mshahara kwa wachimbaji ni shilingi ngapi kwa mwezi?", [], [r"(?i)(mgodi|madini|wachimbaji)[^.]{0,60}765,900"], None, None, None),
    ("D24", "Kiwango cha chini cha mshahara sekta ya madini kwa mwezi?", [], [r"(?i)madini[^.]{0,60}765,900"], None, None, None),
    # NEGATIVES: must NOT show the mining restatement, and must behave as before
    ("D24-NEG", "Kima cha chini cha mshahara sekta ya nishati ni kiasi gani?", [], [MINING_RESTATEMENT], None, None, None),
    ("D24-NEG", "Kima cha chini cha mshahara kwa mfanyakazi wa nyumbani ni kiasi gani?", [], [MINING_RESTATEMENT], None, None, None),
    ("D23-NEG", "GN 605A inashughulikia sekta ngapi na sekta ndogo ngapi za mishahara ya chini?", [r"(?i)sekta 16"], [r"(?i)sekta 15", MINING_RESTATEMENT], None, None, None),
    ("D23-NEG", "Sekta ya madini ina sekta ndogo ngapi kwenye GN 605A?", [r"vipengele vinne"], [r"(?i)sekta ndogo 46 katika sekta ya madini"], None, None, None),
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
