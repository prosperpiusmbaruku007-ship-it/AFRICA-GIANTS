# -*- coding: utf-8 -*-
"""LIVE VERIFICATION (R16, R12c) of the 2026-11-17 BATCH 2 deploy: the fabricated-name guard (incl. GN 605A issuer BY OFFICE), the licence "siku 90" duration guard, the "Leseni yangu ya biashara" authority cue, severance + "kodi gani" -> TRA,
the individual-return and licence-validity model-free statement routes (incl. premise phrasings), lga.go.tz replaced -- and NEGATIVES that must behave as before (a fee + renewal two-part question still on the MODEL path; a WCF / office question untouched).
Production chike-inference via the Modal SDK; artifact written after EVERY row, errors captured, resume re-derives every verdict. `must` / `must_not` are INDICATIVE (R38); replies, path, model_calls and guards are stored for READING.

    python eval/controls/verify_batch3_deploy_live_2026_11_17.py   ->  eval/results/batch3_deploy_live_2026_11_17.json
"""
import hashlib
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
OUT = os.path.join(REPO, "eval", "results", "batch3_deploy_live_2026_11_17.json")
EXPECT_ROWS = 215
EXPECT_BUILD = os.environ.get("EXPECT_BUILD", "")
PERSON = r"Simbachawene|Majaliwa|Kikwete|MHE\.|Mheshimiwa|Samia Suluhu|Mwigulu|Kidata"
# (arm, question, must, must_not, path_forbidden_prefix, path_required_prefix, model_calls_expected)
CASES = [
    # --- TIN window: statement route, the three premise rows VERBATIM (np_14, np_26, s2_08) + a plain window question (model-free) ---
    ("TIN-STMT", "Sina haja ya kuwa na TIN kwa sababu biashara yangu ni ndogo na ndiyo kwanza naanza, sivyo?", [r"siku 15"], [r"(?i)hapana, hakuna siku 15"], None, "engine:fixed_statement", 0),
    ("TIN-STMT", "Nimefungua saluni yangu mwezi huu. Kuna mtu kaniambia nina siku 15 za kuomba TIN kuanzia siku nilipoanza biashara, sivyo?", [r"siku 15"], [r"(?i)hapana, hakuna siku 15", r"si kweli"], None, "engine:fixed_statement", 0),
    ("TIN-STMT", "Nimeanza biashara ya kuuza vifaa vya ujenzi wiki iliyopita. Nimesikia nina siku 15 za kuomba TIN, kwa hiyo sihitaji kuwa nayo siku ya kwanza kabisa, ni kweli?", [r"siku 15"], [r"(?i)hapana, si kweli"], None, "engine:fixed_statement", 0),
    ("TIN-STMT", "Naomba TIN lini baada ya kuanza biashara?", [r"siku 15"], [], None, "engine:fixed_statement", 0),
    # --- VAT: np_22 verbatim, the engine must answer (register), and the MONTHLY-rate question must still ASK ---
    ("VAT", "Mimi nina biashara ya kuuza vifaa, mauzo yangu ya mwaka bado hayajafika milioni 200 lakini ndani ya miezi 6 nimeuza milioni 110. Sihitaji kujisajili VAT kwa sababu mwaka bado haujaisha, siyo?", [r"(?i)lazima|unapaswa|unatakiwa|ndiyo"], [r"(?i)tafadhali taja|niambie mauzo"], None, "engine:", 0),
    ("VAT-NEG", "Kama biashara yangu inauza kwa wastani wa milioni 18 kila mwezi, hiyo hela ipo chini ya milioni 200 kwa mwaka?", [], [r"(?i)hauhitaji kujisajili|huhitaji kujisajili|chini ya kiwango"], None, None, None),
    ("VAT-NEG", "Nauza milioni 20 kwa mwezi, na mauzo yangu hayajafika milioni 200. Je VAT?", [], [r"(?i)hauhitaji kujisajili|huhitaji kujisajili"], None, None, None),
    # --- fee + renewal two-part: BOTH limbs, model-free; a fee-only question stays on the model path ---
    ("TWO-PART", "Nahitaji leseni ya biashara, inagharimu kiasi gani na inaisha lini?", [r"(?i)ada", r"miezi 12"], [r"lga\.go\.tz", r"siku 90", r"ifikapo tarehe 30 Juni"], None, "engine:fixed_statement", 0),
    ("TWO-PART", "Ada ya leseni ya duka langu ni ngapi na huisha lini?", [r"(?i)ada", r"miezi 12"], [r"lga\.go\.tz"], None, "engine:fixed_statement", 0),
    ("NEGATIVE", "Ada ya leseni ya biashara ni kiasi gani?", [], [r"lga\.go\.tz"], "engine:fixed_statement", None, 1),
    ("NEGATIVE", "Leseni ya biashara inaisha lini?", [r"miezi 12"], [r"ifikapo tarehe 30 Juni"], None, "engine:fixed_statement", 0),
    # --- TIN how-to must stay on the MODEL path ---
    ("TIN-HOWTO", "Nitapataje TIN?", [], [], "engine:fixed_statement", None, 1),
    ("TIN-HOWTO", "TIN ni nini?", [], [], "engine:fixed_statement", None, 1),
    ("TIN-HOWTO", "Je, ninahitaji TIN kufungua akaunti ya benki ya biashara?", [], [], "engine:fixed_statement", None, 1),
    # --- firm as the authority (GN 605A signer) and the lost-licence reply ---
    ("FIRM", "Nani alisaini GN 605A?", [], [r"VELMA", r"PKF Eastern Africa au", r"Bowmans", r"Clyde"], None, None, None),
    ("FIRM", "GN 605A ilianza kutumika lini?", [r"2026"], [r"VELMA", r"Thibitisha na PKF", r"Thibitisha na VELMA"], None, None, None),
    ("FIRM", "Mshahara wa chini kwa sekta binafsi umepanda kwa wastani gani?", [r"33"], [r"Thibitisha na PKF", r"Thibitisha na VELMA"], None, None, None),
    ("DEDUPE", "Leseni yangu ya biashara nikiipoteza nifanyeje?", [], [r"lga\.go\.tz", r"mlywf\.go\.tz"], None, None, None),
    # --- untouched negatives from earlier batches ---
    ("NEGATIVE", "Nina wafanyakazi 12, mishahara yao yote ni TZS 4,000,000 kwa mwezi, SDL ni ngapi?", [r"140,000"], [], None, "engine:sdl", None),
    ("NEGATIVE", "Nikate WCF kwenye mshahara wa mfanyakazi?", [r"(?i)hapana|haikatwi|mwajiri"], [r"unapaswa kuikata"], None, None, None),
    ("NEGATIVE", "Leseni ya biashara ya LGA inahuishwa lini?", [r"miezi 12", r"halmashauri"], [r"siku 90", r"lga\.go\.tz"], None, "engine:fixed_statement", 0),
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
    save = lambda: json.dump(art, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
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
