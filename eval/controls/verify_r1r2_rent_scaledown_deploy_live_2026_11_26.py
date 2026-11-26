# -*- coding: utf-8 -*-
"""LIVE VERIFICATION (R16, R12c) of the 2026-11-26 `chike-inference` window: R1/R2 route recall (+ the first-person keep-veto and its residency line), the rent fix (R44 strip,
conditional line) and scaledown_window 600. COMMITTED BEFORE ITS RUN (R18). `must` / `must_not` are INDICATIVE (R38): EVERY REPLY IS READ BY A PERSON, and that reading is the verdict.
Identity: /health `build` == EXPECT_BUILD and `build_matches`; served index unchanged (224 rows, same sha as the committed file).
`WARM=1` runs the scaledown check INSTEAD: one question, a 7-minute wait, a second (must be warm: fast), recorded as latencies.
The AUTO-SEND exclusion cannot be exercised through this endpoint (it lives in chike-whatsapp's 15-minute sweep): it is checked separately from the test phone.
    EXPECT_BUILD=<sha> python eval/controls/verify_r1r2_rent_scaledown_deploy_live_2026_11_26.py  ->  eval/results/r1r2_rent_scaledown_deploy_live_2026_11_26.json"""
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
OUT = os.path.join(REPO, "eval", "results", "r1r2_rent_scaledown_deploy_live_2026_11_26.json")
WARM_OUT = os.path.join(REPO, "eval", "results", "scaledown_warm_check_2026_11_26.json")
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
    ("R1", R1, [r"UKAAZI WA KIKODI", r"183"], [r"Ili nikuhesabie"], None, STMT, 0),
    ("R1", "Mgeni anayefanya kazi Tanzania analipa PAYE kiasi gani?", [r"UKAAZI WA KIKODI"], [r"Ili nikuhesabie"], None, STMT, 0),
    ("R2", R2, [r"asilimia 15", r"tax credit|kupunguza kodi"], [], None, STMT, 0),
    ("R2", "Ada ya wakurugenzi hukatwa kodi kiasi gani?", [r"asilimia 15"], [], None, STMT, 0),
    ("REGIME", RS04, [r"UKAAZI WA KIKODI", r"183"], [r"Ili nikuhesabie"], None, STMT, 0),                       # rs_04: first person, a REGIME question: MUST keep its statement
    ("FIRSTPERSON", FP, [r"Ili nikuhesabie", re.escape(RESIDENCY_LINE)], [], STMT, None, 0),                         # clarification + the residency line
    ("FIRSTPERSON", "Nikatwe PAYE kiasi gani mimi?", [r"Ili nikuhesabie"], [re.escape(RESIDENCY_LINE)], STMT, None, 0),  # not foreign: NO extra line
    ("RENT", "Kodi ya zuio kwenye pango la ofisi ni asilimia ngapi?", [r"asilimia 10", r"Sheria ya Kodi ya Mapato"], [r"×", r"4\(b\)\(ii\)", r"Cap\."], None, RENT, 0),
    ("RENT", "Nalipa kodi ya pango TZS 800,000 kwa mwezi, nikate withholding kiasi gani?",
     [re.escape("Ikiwa wewe ni wakala wa kuzuia: 10% × TZS 800,000 = TZS 80,000.")], [r"4\(b\)\(ii\)", r"Cap\."], None, RENT, 0),
    ("RENT", "Pango la ofisi ni TZS 8,000,000 kwa mwezi, nikate kiasi gani?", [re.escape("10% × TZS 8,000,000 = TZS 800,000.")], [], None, RENT, 0),
    ("RENT-NEG", "Mauzo yangu ni TZS 50,000,000, nikate WHT ya pango?", [], [r"×"], None, None, None),                  # a lone non-rent figure must not be multiplied
    ("CTRL", "Mshahara wa TZS 800,000, PAYE ni kiasi gani?", [r"78,000"], [r"UKAAZI WA KIKODI"], None, "engine:paye", None),   # PAYE computation control
    ("NEG", "Mfanyakazi mgeni analipwa TZS 2,000,000, PAYE kiasi gani?", [], [r"Ili nikuhesabie"], STMT, "engine:paye", None),   # amount present: unchanged
    ("NEG", "Ada ya mkurugenzi ni TZS 5,000,000, WHT ni kiasi gani?", [], [], STMT, None, None),                      # amount present: model path for now
    ("NEG", "Mgeni wa Kenya analipa PAYE kiasi gani?", [], [], STMT, None, None),
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
    ident_ok = ((not EXPECT_BUILD or (ident.get("build") == EXPECT_BUILD and h.get("build") == EXPECT_BUILD)) and h.get("build_matches") is True
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
