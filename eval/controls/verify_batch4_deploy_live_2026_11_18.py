# -*- coding: utf-8 -*-
"""LIVE VERIFICATION (R16, R12c) of the 2026-11-18 BATCH 4 deploy (chike-inference only): (a) the model-free annual-return deadline statement and (b) D-FIDELITY-23 ("46" as the sub-sector count of ONE GN 605A sector) --
and NEGATIVES that must behave as before (a BRELA fee, a late-filing penalty amount, the corporate income-tax return, the overall 46 total, a mining wage question, eval_072 "Mara ngapi").
Production chike-inference via the Modal SDK; artifact written atomically after EVERY row, errors captured, resume re-derives every verdict. `must` / `must_not` are INDICATIVE (R38); replies, path, model_calls and guards are stored
and every reply is READ.

    EXPECT_BUILD=<sha> python eval/controls/verify_batch4_deploy_live_2026_11_18.py   ->  eval/results/batch4_deploy_live_2026_11_18.json
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
OUT = os.path.join(REPO, "eval", "results", "batch4_deploy_live_2026_11_18.json")
EXPECT_ROWS = 216
EXPECT_BUILD = os.environ.get("EXPECT_BUILD", "")
# (arm, question, must, must_not, path_forbidden_prefix, path_required_prefix, model_calls_expected)
STMT = "engine:fixed_statement"
CASES = [
    # (a) the statement route: the two live wrong phrasings of 4az plus the four others
    ("AR-STMT", "Annual return ya BRELA inapaswa kuwasilishwa lini?", [r"(?i)siku 28", r"(?i)maadhimisho"], [r"(?i)siku 42", r"(?i)mwaka wa kalenda unaofuatia"], None, STMT, 0),
    ("AR-STMT", "Annual return ya kampuni inatakiwa kuwasilishwa ndani ya muda gani?", [r"(?i)siku 28", r"(?i)maadhimisho"], [r"(?i)siku 42", r"(?i)mwaka wa kalenda unaofuatia"], None, STMT, 0),
    ("AR-STMT", "Je, annual return ya BRELA inawasilishwa ndani ya miezi 12 baada ya usajili?", [r"(?i)siku 28", r"(?i)si miezi 12"], [r"(?i)^ndiyo"], None, STMT, 0),
    ("AR-STMT", "Annual return ya BRELA ni mwisho wa mwaka wa fedha, sivyo?", [r"(?i)siku 28", r"(?i)maadhimisho"], [r"(?i)^ndiyo"], None, STMT, 0),
    ("AR-STMT", "Kampuni ilisajiliwa tarehe 10 Machi 2025. Annual return inapaswa kuwasilishwa lini?", [r"(?i)siku 28", r"(?i)maadhimisho"], [r"(?i)ndani ya miezi 12"], None, STMT, 0),
    ("AR-STMT", "Nimeambiwa annual return ya BRELA inaisha 30 Septemba — ni kweli?", [r"(?i)si 30 Septemba"], [r"(?i)^ndiyo"], None, STMT, 0),
    # NEGATIVES: each has its own fact and must stay on the MODEL path
    ("AR-NEG", "Ada ya annual return BRELA ni shilingi ngapi?", [r"22,000|22000"], [r"(?i)siku 28"], STMT, None, None),
    ("AR-NEG", "Nikichelewa kuwasilisha annual return, faini ni kiasi gani kwa mwezi?", [], [r"(?i)siku 42"], STMT, None, None),
    ("AR-NEG", "Return ya kodi ya mapato ya kampuni ni lini?", [r"(?i)miezi 6"], [r"(?i)maadhimisho"], STMT, None, None),
    ("AR-NEG", "Mara ngapi kampuni iliyosajiliwa na BRELA inahitajika kuwasilisha annual return (ripoti ya kila mwaka)?", [r"(?i)kila mwaka"], [], STMT, None, None),
    # (b) D-FIDELITY-23
    ("D23", "Sekta ya madini ina sekta ndogo ngapi kwenye GN 605A?", [], [r"(?i)sekta ndogo 46 katika sekta ya madini", r"(?i)46 .{0,30}madini peke"], None, None, None),
    ("D23-NEG", "GN 605A inashughulikia sekta ngapi na sekta ndogo ngapi za mishahara ya chini?", [r"(?i)sekta 16"], [r"(?i)sekta 15"], None, None, None),
    ("D23-NEG", "Mshahara wa chini wa sekta ya madini ni kiasi gani kwa mujibu wa GN 605A?", [r"695,000"], [], None, None, None),
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
