# -*- coding: utf-8 -*-
"""LIVE VERIFICATION (R16, R12c) of Fix A (`baed3f5`): a first-person figure-free PAYE ask, or `kodi` with a deduction verb, gets the plain salary clarification and never reaches the model
(on 066a995 "Nikatwe PAYE kiasi gani mimi?" fabricated TZS 800,000 -> 78,000). Four specimens + negatives that must behave as before (the founder's shop owner "Nilipe kodi kiasi gani mimi?", another levy,
a rate ask, a question WITH a figure) + unchanged controls. COMMITTED BEFORE ITS RUN (R18). `must` / `must_not` are INDICATIVE (R38): EVERY REPLY IS READ BY A PERSON, and that reading is the verdict.
Identity is read from the GPU class (`served_index_identity`): build == EXPECT_BUILD (and the web tier's), 224 rows, digest == the committed file. A NEW artifact, so no row of the previous window is resumed.
    EXPECT_BUILD=<sha> python eval/controls/verify_fix_a_deploy_live_2026_11_26.py  ->  eval/results/fix_a_deploy_live_2026_11_26.json"""
import hashlib
import json
import os
import re
import sys
import time
import urllib.request

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import atomic_artifact  # noqa: E402

REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
OUT = os.path.join(REPO, "eval", "results", "fix_a_deploy_live_2026_11_26.json")
WARM_OUT = os.path.join(REPO, "eval", "results", "fix_a_unused_warm_2026_11_26.json")
HEALTH = "https://prosperpiusmbaruku007--chike-inference-health.modal.run"
EXPECT_ROWS = 224
EXPECT_BUILD = os.environ.get("EXPECT_BUILD", "")
STMT = "engine:fixed_statement"
RENT = "engine:rent_wht"
RESIDENCY_LINE = "UKAAZI WA KIKODI wa mfanyakazi, si uraia wala kuwa mgeni"
R1, R2 = "Mfanyakazi mgeni analipa PAYE kiasi gani?", "Ada ya mkurugenzi inakatwa kodi ya zuio kiasi gani?"
RS04 = "Nikikaa nchini siku 183, PAYE yangu ni ya mkazi au asiye mkazi?"
FP = "Mshahara wa mgeni ni mkubwa, nikatwe PAYE kiasi gani mimi?"
CASES = [
    # (arm, question, must, must_not, path_forbidden_prefix, path_required_prefix, model_calls_expected)
    # FIX A: a first-person figure-free PAYE ask (or kodi + a deduction verb) gets the plain salary clarification; the model never answers it (it invented TZS 800,000 -> 78,000 on 066a995)
    ("FIXA", "Nikatwe PAYE kiasi gani mimi?", [r"Ili nikuhesabie"], [re.escape(RESIDENCY_LINE), r"800,000", r"78,000"], None, "clarification", 0),
    ("FIXA", "Nikatwe PAYE kiasi gani?", [r"Ili nikuhesabie"], [re.escape(RESIDENCY_LINE), r"78,000"], None, "clarification", 0),
    ("FIXA", "PAYE yangu ni kiasi gani?", [r"Ili nikuhesabie"], [re.escape(RESIDENCY_LINE), r"78,000"], None, "clarification", 0),
    ("FIXA", "Ninakatwa kodi kiasi gani mimi?", [r"Ili nikuhesabie"], [re.escape(RESIDENCY_LINE), r"78,000"], None, "clarification", 0),
    # NEGATIVES: must behave as before the fix
    ("FIXA-NEG", "Nilipe kodi kiasi gani mimi?", [], [r"Ili nikuhesabie"], "clarification", None, None),                      # FOUNDER: a shop owner's kodi, no deduction verb
    ("FIXA-NEG", "Nilipe VAT kiasi gani mimi?", [], [r"Ili nikuhesabie"], "clarification", None, None),
    ("FIXA-NEG", "PAYE yangu ni asilimia ngapi?", [], [r"Ili nikuhesabie"], "clarification", None, None),                      # a RATE ask
    ("FIXA-NEG", "Nikatwe PAYE kiasi gani mimi, mshahara 800,000?", [r"78,000"], [r"Ili nikuhesabie"], "clarification", "engine:paye", None),   # a figure: the engine, as before
    ("UNCHANGED", "Mshahara wa mgeni ni mkubwa, nikatwe PAYE kiasi gani mimi?", [r"Ili nikuhesabie", re.escape(RESIDENCY_LINE)], [], None, "clarification", 0),   # already clarified: still gets the residency line
    ("UNCHANGED", R1, [r"UKAAZI WA KIKODI", r"183"], [r"Ili nikuhesabie"], None, STMT, 0),
    ("UNCHANGED", RS04, [r"UKAAZI WA KIKODI", r"183"], [r"Ili nikuhesabie"], None, STMT, 0),
    ("UNCHANGED", "Kodi ya zuio kwenye pango la ofisi ni asilimia ngapi?", [r"asilimia 10"], [r"×", r"Cap\."], None, RENT, 0),
    ("UNCHANGED", "Mshahara wa TZS 800,000, PAYE ni kiasi gani?", [r"78,000"], [r"Ili nikuhesabie"], None, "engine:paye", None),
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


def _health():
    with urllib.request.urlopen(HEALTH, timeout=120) as r:
        return json.loads(r.read().decode("utf-8"))


def warm_check(m):
    art = {"started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "runs": []}
    for label, wait in (("first", 0), ("second_after_7_min", 420)):
        time.sleep(wait)
        t = time.time()
        out = m.run.remote("Kodi ya zuio kwenye pango la ofisi ni asilimia ngapi?")
        art["runs"].append({"label": label, "elapsed_s": round(time.time() - t, 1), "at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                            "path": out.get("answer_path") or out.get("path")})
        atomic_artifact.write_json(WARM_OUT, art, ensure_ascii=False, indent=1)
        print(art["runs"][-1])
    print("READ: a second call after 7 minutes that is fast (single-digit seconds, like warm p90 9.8 s) proves the 600 s window; a cold start is 60-216 s. The 300 s window would have been cold.")


def main():
    import modal
    m = modal.Cls.from_name("chike-inference", "ChikeModel")()
    if os.environ.get("WARM"):
        return warm_check(m)
    art = json.load(open(OUT, encoding="utf-8")) if os.path.exists(OUT) else {"identity": None, "health": None, "rows": []}
    art["rows"] = [r for r in art["rows"] if "error" not in r]
    done = {r["q"] for r in art["rows"]}
    save = lambda: atomic_artifact.write_json(OUT, art, ensure_ascii=False, indent=1)
    h = _health()
    art["health"] = {k: h.get(k) for k in ("build", "build_matches", "web_build", "gpu_build", "status")}
    if not art.get("identity"):
        art["identity"] = m.served_index_identity.remote()
    save()
    ident = art["identity"]
    local = json.load(open(os.path.join(REPO, "chike-inference", "rag_facts_text.json"), encoding="utf-8"))
    local_sha = hashlib.sha256(json.dumps(local, ensure_ascii=False).encode("utf-8")).hexdigest()
    # identity is read from the GPU class (served_index_identity), the method the founder named; the web /health only reports build_matches in token-gated deep mode, so it is not a conjunct here
    ident_ok = ((not EXPECT_BUILD or (ident.get("build") == EXPECT_BUILD and h.get("build") == EXPECT_BUILD))
                and ident.get("rag_rows_loaded") == EXPECT_ROWS and ident.get("rag_facts_text_sha256") == local_sha)
    print("health:", art["health"], "| served identity:", {k: ident.get(k) for k in ("build", "rag_rows_loaded", "rag_facts_text_sha256")})
    print(f"identity_ok={ident_ok}")
    for case in CASES:
        arm, q = case[0], case[1]
        if q in done:
            continue
        try:
            t = time.time()
            out = m.run.remote(q)
            row = dict(arm=arm, q=q, reply=out.get("reply", ""), path=out.get("answer_path") or out.get("path"), model_calls=out.get("model_calls"),
                       guards=out.get("guards"), elapsed_s=round(time.time() - t, 1))
        except Exception as e:                                           # noqa: BLE001
            row = dict(arm=arm, q=q, error=repr(e)[:300])
        if "reply" in row:
            row["checks"] = _checks(row, case)
            row["ok"] = all(row["checks"].values())
        art["rows"].append(row)
        save()
        print(f"[{'ERR' if 'error' in row else 'ok ' if row['ok'] else 'MISS'}] {arm:<11} {row.get('path')} calls={row.get('model_calls')} guards={row.get('guards')} "
              f"{row.get('elapsed_s')}s | {q[:70]!r}")
    for r in art["rows"]:                                                # every verdict RE-DERIVED, never carried from a resumed row
        c = [x for x in CASES if x[1] == r["q"]]
        if "reply" in r and c:
            r["checks"] = _checks(r, c[0])
            r["ok"] = all(r["checks"].values())
    art["identity_ok"] = ident_ok
    save()
    bad = [r for r in art["rows"] if r.get("ok") is False or "error" in r]
    print(f"\n{len(art['rows'])} rows; identity_ok={ident_ok}; automated misses {len(bad)} (READ every reply)")
    sys.exit(0 if ident_ok and not bad else 1)


if __name__ == "__main__":
    main()
