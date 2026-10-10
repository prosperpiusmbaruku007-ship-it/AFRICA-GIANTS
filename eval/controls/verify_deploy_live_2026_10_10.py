# -*- coding: utf-8 -*-
"""LIVE VERIFICATION OF THE 2026-10-10 DEPLOY — the party renderer, the optionality premise,
and D-FIDELITY-9, each with a negative beside it.

⛔ "✓ App deployed" IS NOT VERIFICATION (R16). Warm containers serve the old code, and a
config-only change has no diff to remind you a deploy happened. Every probe below is a request
whose behaviour is DIFFERENT before and after this deploy, or one that must be UNCHANGED.

⛔ TWO LIMBS, SEPARATED, BECAUSE A DEPLOY VERDICT AND AN ANSWER-QUALITY VERDICT ARE DIFFERENT
CLAIMS (R38). `limb: deploy` probes decide whether the new code is live; `limb: answer_quality`
probes record how good the answer is. A row can fail the second while the first is proven — and
a probe that cannot distinguish them will eventually block a good deploy or pass a dead one.

⛔ AND THE PROBES ARE A GOLD ANSWER, SO THEY ARE SOURCED LIKE ONE (R38 again). Two of the three
failures in the first run of the 2026-10-07 live verify were THE HARNESS, not the system: one
promoted a retrieval anchor to a model-answer requirement, and one scored a guard WORKING as a
regression while its own `note` described the correct handling three lines above. Each
`must_match` below is a property this deploy's own code produces deterministically, not a
judgement about what a good answer looks like.

⚠️ NEVER A CROSS-HOST BYTE COMPARISON (R24b). Production no longer reproduces the gate
harness's bytes — measured 2026-10-10, eval_162 differs by one space with a prompt proven
identical. Every assertion here is a substring or a structural property of THIS host's reply.

Writes its artifact after EVERY row and resumes from it, so a dropped Tanzanian link costs one
row and never the run. A resume carries DATA forward and re-derives every verdict.

Usage:  python eval/controls/verify_deploy_live_2026_10_10.py
Artifact: eval/results/deploy_verify_2026_10_10.json
Exit 0 all limbs pass · 1 a failure · 2 could not be exercised (NOT a pass).
"""
import io
import json
import os
import subprocess
import sys
import urllib.request

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO)
OUT = os.path.join(REPO, "eval", "results", "deploy_verify_2026_10_10.json")
ENDPOINT = "https://prosperpiusmbaruku007--chike-inference-web-endpoint.modal.run"
HEALTH = "https://prosperpiusmbaruku007--chike-inference-health.modal.run"
DEPLOY_PATHS = ["chike", "chike-inference", "kaggle/rag_facts_text.json",
                "kaggle/chike_config.json"]

PROBES = [
    # ── THE PARTY RENDERER (eval_086 / eval_087, verbatim) ───────────────────────────
    {
        "id": "pv_01_eval_086_employer",
        "limb": "deploy",
        "question": ("Kiwango cha mchango wa NSSF kwa upande wa mwajiri ni asilimia ngapi ya "
                     "mshahara wa jumla wa mfanyakazi?"),
        "must_match": ["Sehemu ya mwajiri ni asilimia 10"],
        "must_not_match": [],
        "starts_with": "Sehemu ya mwajiri",
        "note": ("eval_086 verbatim. Before this deploy it was answered 'Kiwango cha NSSF ni "
                 "asilimia 20 …' with the asked-for 10% in a parenthetical. A reply opening "
                 "with the employer's own share can only come from levy_party_share_statement, "
                 "which exists only in this build."),
    },
    {
        "id": "pv_02_eval_087_employee",
        "limb": "deploy",
        "question": ("Kiwango cha mchango wa NSSF kwa upande wa mfanyakazi ni asilimia ngapi "
                     "ya mshahara wake wa jumla?"),
        "must_match": ["Sehemu ya mfanyakazi ni asilimia 10"],
        "must_not_match": [],
        "starts_with": "Sehemu ya mfanyakazi",
        "note": ("THE REGRESSION THIS DEPLOY FIXES. eval_087 went from CORRECT to a "
                 "2-wrong/2-correct/1-undetermined judge split when the statement route began "
                 "answering it total-first. eval_086 survived the identical text only because "
                 "the clause after the parenthetical happens to lead with the employer, so the "
                 "two rows differed by luck rather than by handling."),
    },
    # ── THE OPTIONALITY PREMISE, BOTH POLARITIES ────────────────────────────────────
    {
        "id": "pv_03_eval_394_negated_premise",
        "limb": "deploy",
        "question": "Je, NSSF si ya hiari kwa mwajiri anayestahili?",
        "must_match": ["Ndiyo, ni kweli", "si ya hiari", "LAZIMA"],
        "must_not_match": ["Hapana"],
        "starts_with": "Ndiyo, ni kweli",
        "note": ("eval_394. The engine's applicability lead is written for 'does this levy "
                 "apply?', so it answered 'Ndiyo.' to a question about COMPULSION and "
                 "contradicted the model body's 'Hapana, si ya hiari' one sentence later. The "
                 "body is now blanked and the verdict re-led, so no 'Hapana' may survive."),
    },
    {
        "id": "pv_04_mirror_positive_premise",
        "limb": "deploy",
        "question": "Je, NSSF ni ya hiari kwa mwajiri anayestahili?",
        "must_match": ["Hapana.", "si ya hiari", "LAZIMA"],
        "must_not_match": [],
        "starts_with": "Hapana.",
        "note": ("⛔ THE WORSE HALF, AND IT WAS NEVER IN ANY GATE. The un-negated form asserts "
                 "the levy IS voluntary; before this deploy it was answered 'Ndiyo.' — yes, "
                 "NSSF is voluntary — on a compulsory levy, in the engine's own voice. Found by "
                 "asking the mirror of the gate row."),
    },
    # ── D-FIDELITY-9 ────────────────────────────────────────────────────────────────
    {
        "id": "pv_05_th_22_no_fabricated_figure",
        "limb": "deploy",
        "question": "Nina mfanyakazi mmoja tu — je nalipa WCF?",
        "must_match": ["WCF inahusu waajiri wote"],
        "must_not_match": ["TZS 50,000", "50,000 kwa mwaka"],
        "starts_with": None,
        "note": ("th_22. The live reply carried 'Kwa mfanyakazi MMOJA: WCF = TZS 50,000 kwa "
                 "mwaka' — a shilling amount invented from a salary nobody gave — and the "
                 "judge voted CORRECT 5/5 on it. The engine's working must still render, so "
                 "this also checks that blanking did not ship silence."),
    },
    # ── NEGATIVES: THE CONTROL ARM OF THE SWEEP, LIVE ───────────────────────────────
    {
        "id": "pv_06_negative_eval_111_aggregate_base",
        "limb": "deploy",
        "question": ("Kiwango cha SDL ni asilimia ngapi ya jumla ya mishahara ya jumla ya "
                     "wafanyakazi wote?"),
        "must_match": ["asilimia 3.5", "JUMLA ya mishahara"],
        "must_not_match": ["Sehemu ya mfanyakazi ni asilimia",
                           "Sehemu ya mwajiri ni asilimia"],
        "starts_with": "Kiwango cha SDL",
        "note": ("⛔ THE NEGATIVE THAT MATTERS MOST. This asks for a RATE on the aggregate "
                 "BASE and contains the word 'wafanyakazi'. If the party extractor were one "
                 "notch wider it would answer a base question with one party's share — and the "
                 "diversion count would have gone UP, which reads as the change working."),
    },
    {
        "id": "pv_07_negative_eval_112_wcf_base",
        "limb": "deploy",
        "question": "Kiwango cha WCF ni asilimia ngapi ya jumla ya mishahara ya jumla?",
        "must_match": ["asilimia 0.5", "JUMLA ya mishahara ghafi ya wafanyakazi wote"],
        "must_not_match": ["Sehemu ya"],
        "starts_with": "Kiwango cha WCF",
        "note": ("eval_112 — the row whose BASE was wrong two days ago, and which the judge "
                 "called CORRECT both before and after that fix. It must keep the aggregate "
                 "base and the rate renderer."),
    },
    {
        "id": "pv_08_negative_amount_question_still_clarifies",
        "limb": "deploy",
        "question": "Mfanyakazi alifanya kazi siku 26 mwezi huu, NSSF yake ni kiasi gani basi?",
        "must_match": [],
        "must_not_match": ["Sehemu ya mfanyakazi ni asilimia 10 ya mshahara wake ghafi"],
        "starts_with": None,
        "note": ("⛔ ONE OF THE SIX REGRESSIONS MY FIRST VERSION OF THE PARTY BRANCH SHIPPED. "
                 "A party is named in every AMOUNT question about a levy. This asks for a "
                 "figure, has none, and must keep asking for the salary rather than being "
                 "answered with a rate. `asks_rate` is the gate that fixed it."),
    },
    {
        "id": "pv_09_negative_voluntary_opt_in_untouched",
        "limb": "deploy",
        "question": "Naweza kujiunga NSSF kwa hiari?",
        "must_match": [],
        "must_not_match": ["LAZIMA", "Ndiyo, ni kweli"],
        "starts_with": None,
        "note": ("⛔ THE REAL COUNTER-EXAMPLE. NSSF genuinely HAS voluntary membership for the "
                 "self-employed, so this asks about opting IN. Answering it 'NSSF is mandatory "
                 "for employers' is the eval_211 wrong-topic harm class, and it is why the cue "
                 "is the predicative `si/ni ya hiari` frame and not a bare `hiari`."),
    },
    {
        "id": "pv_10_negative_eval_130_method_still_leads_with_the_operation",
        "limb": "deploy",
        "question": "Mwajiri anahesabu kiasi cha SDL cha kulipa kwa mwezi vipi?",
        "must_match": ["Zidisha"],
        "must_not_match": ["Sehemu ya"],
        "starts_with": "Zidisha",
        "note": ("The branch ORDER, live. A method ask names the employer and must still reach "
                 "the method renderer, not the party one — the more specific renderer wins."),
    },
    {
        "id": "pv_11_negative_eval_233_threshold_still_rate_free",
        "limb": "deploy",
        "question": ("Ni idadi gani ya waajiriwa inayofanya mwajiri kuwa na wajibu wa kulipa "
                     "SDL Tanzania Bara?"),
        "must_match": ["wafanyakazi 10 au zaidi"],
        "must_not_match": ["asilimia"],
        "starts_with": "Mwajiri mwenye wafanyakazi 10",
        "note": ("The threshold renderer, unchanged by this deploy and asserted anyway: it is "
                 "the row whose regression produced the renderer split, and the rate's ABSENCE "
                 "is its contract."),
    },
]


def _sh(*args):
    return subprocess.run(args, cwd=REPO, capture_output=True, text=True).stdout.strip()


def _tok():
    p = os.path.expanduser("~/.chike_modal_token.txt")
    return (os.environ.get("CHIKE_MODAL_TOKEN")
            or (io.open(p, encoding="utf-8").read().strip() if os.path.exists(p) else ""))


def ask(question, tok, timeout=600):
    req = urllib.request.Request(
        f"{ENDPOINT}?token={tok}",
        data=json.dumps({"message": question}).encode("utf-8"),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def health(tok):
    head = _sh("git", "rev-parse", "--short", "HEAD")
    try:
        with urllib.request.urlopen(f"{HEALTH}?deep=1&token={tok}", timeout=600) as r:
            h = json.loads(r.read().decode("utf-8"))
    except Exception as exc:                                             # noqa: BLE001
        return {"error": f"{type(exc).__name__}: {str(exc)[:200]}"}, head
    build = h.get("build") or ""
    moved = [p for p in _sh("git", "diff", "--name-only", f"{build}..HEAD", "--",
                            *DEPLOY_PATHS).splitlines() if p.strip()] if build else ["?"]
    h["_checks"] = {
        "build_is_HEAD": build == head,
        "web_and_gpu_tiers_agree": h.get("build_matches") is True,
        "no_serving_path_moved_since_the_build": not moved,
    }
    h["_provenance"] = {"deployed_build": build, "head": head, "serving_paths_moved": moved}
    return h, head


def classify(rec):
    """Re-derived every run from the stored reply — never restored from a previous run."""
    if rec.get("error"):
        return "ERROR"
    reply = rec.get("reply") or ""
    missing = [m for m in rec["must_match"] if m not in reply]
    present = [m for m in rec["must_not_match"] if m in reply]
    lead = rec.get("starts_with")
    bad_lead = bool(lead) and not reply.strip().startswith(lead)
    rec["missing"], rec["forbidden_present"], rec["bad_lead"] = missing, present, bad_lead
    return "PASS" if not (missing or present or bad_lead) else "FAIL"


def save(rows, h):
    payload = {
        "_what": "live verification of the 2026-10-10 deploy — party renderer, optionality "
                 "premise, D-FIDELITY-9, each with a negative",
        "_why_two_limbs": ("a deploy verdict and an answer-quality verdict are different "
                           "claims; a probe that cannot tell them apart will block a good "
                           "deploy or pass a dead one (R38)"),
        "_no_cross_host_byte_comparison": ("production no longer reproduces the gate harness's "
                                           "bytes (R24b, measured 2026-10-10), so every "
                                           "assertion here is a substring or structure of THIS "
                                           "host's reply"),
        "endpoint": ENDPOINT,
        "health": h,
        "totals": {
            "rows": len(PROBES),
            "measured": len([r for r in rows if r.get("reply") or r.get("error")]),
            "by_verdict": {v: len([r for r in rows if r.get("verdict") == v])
                           for v in sorted({r.get("verdict") for r in rows if r.get("verdict")})},
        },
        "deploy_limb_verdict": (
            "PASS" if all(r.get("verdict") == "PASS"
                          for r in rows if r.get("limb") == "deploy") and rows else "PENDING"),
        "rows": rows,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with io.open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)


def _resume():
    if not os.path.exists(OUT):
        return {}
    try:
        prev = json.load(io.open(OUT, encoding="utf-8"))
    except Exception:                                                    # noqa: BLE001
        return {}
    return {r["id"]: r for r in prev.get("rows", []) if r.get("reply")}


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:                                                    # noqa: BLE001
        pass

    tok = _tok()
    if not tok:
        print("NO TOKEN — the live check cannot run. This is NOT a pass.")
        return 2

    h, head = health(tok)
    print(f"[health] {json.dumps(h.get('_checks', h.get('error')), ensure_ascii=False)}")
    print(f"[health] deployed={h.get('_provenance', {}).get('deployed_build')} head={head}")
    if h.get("error") or not all(h.get("_checks", {}).values()):
        print("HEALTH GATE FAILED — not verifying answers against a build that is not HEAD.")
        save([], h)
        return 2

    done = _resume()
    if done:
        print(f"[resume] {len(done)} row(s) already measured")

    rows = []
    for probe in PROBES:
        rec = dict(probe)
        prev = done.get(rec["id"])
        if prev is not None and prev.get("health_build") == h.get("build"):
            # DATA forward, CONCLUSION re-derived. A resumed row that carried its old verdict
            # could never be relabelled by a corrected classifier, and a re-run would reprint
            # the old labels just as confidently.
            rec["reply"] = prev["reply"]
            rec["_resumed"] = True
        else:
            try:
                rec["reply"] = str(ask(rec["question"], tok).get("reply") or "")
            except Exception as exc:                                     # noqa: BLE001
                rec["error"] = f"{type(exc).__name__}: {str(exc)[:200]}"
        rec["health_build"] = h.get("build")
        rec["verdict"] = classify(rec)
        rows.append(rec)
        save(rows, h)
        tag = " (resumed)" if rec.get("_resumed") else ""
        print(f"[{rec['verdict']:6s}] {rec['id']:48s} {rec['limb']}{tag}")
        if rec["verdict"] != "PASS":
            for m in rec.get("missing") or []:
                print(f"         missing: {m!r}")
            for m in rec.get("forbidden_present") or []:
                print(f"         forbidden present: {m!r}")
            if rec.get("bad_lead"):
                print(f"         lead != {rec['starts_with']!r}: {rec['reply'][:110]!r}")

    deploy_bad = [r for r in rows if r["limb"] == "deploy" and r["verdict"] != "PASS"]
    quality_bad = [r for r in rows if r["limb"] == "answer_quality" and r["verdict"] != "PASS"]
    save(rows, h)
    print()
    print(f"DEPLOY LIMB        : {'PASS' if not deploy_bad else 'FAIL'} "
          f"({len(rows) - len(deploy_bad) - len(quality_bad)}/"
          f"{len([r for r in rows if r['limb'] == 'deploy'])})")
    if quality_bad:
        print(f"ANSWER QUALITY     : {len(quality_bad)} row(s) short — recorded, does not "
              f"falsify the deploy")
    print(f"[saved] {OUT}")
    return 1 if (deploy_bad or quality_bad) else 0


if __name__ == "__main__":
    sys.exit(main())
