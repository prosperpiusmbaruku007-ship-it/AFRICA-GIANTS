# -*- coding: utf-8 -*-
"""ext_15 RE-ADJUDICATED BY ASKING THE QUESTION AGAIN — THE ROW THAT STARTED THE BRELA WORK.

⛔ WHY THIS COULD NOT BE DONE FROM A DESK, IN THE ROW'S OWN WORDS. Its 2026-10-06 note reads:
"THE RECORDED VERDICT IS NOT RE-LABELLED FROM A DESK. This row's reply was adjudicated against a
key that has since changed, so neither 'still wrong' nor 'actually right' is supportable without
asking the question again. Re-labelling on reconstruction is exactly the move that produced the
2026-08-31 Part XII reversal — a confident correction that was itself the error."

So the verdict was `RE_RUN_REQUIRED`, and this is the re-run.

THE KEY MOVED TWICE AND BOTH LIMBS MATTER:
  2026-10-05  CITATION: 'Part XIII, ss.320-328' -> 'Part XII, ss.437-447'. The 2026-08-31
              "correction" that put Part XIII there was itself the error; BRELA's own page,
              labelled 'Sehemu ya XII', was right and we overruled it.
  2026-10-06  FIGURE: 'USD 25 per month' -> 'TZS 70,000 per month or part month', from BRELA's
              published schedule item 15(iv), sha256-pinned capture 8d5543ac…

⚠️ THE ROW IS NOT REGEX-SCORABLE AND THAT IS WHY IT NEEDS A HUMAN. It lives in
eval/accuracy_gate/edge_probe_extended_078_DRAFT.jsonl, which carries `expected_behavior` PROSE
and no `correct_answer_sw`/`answer_type` — `chike.scoring.score_question` cannot score it at all.
It is also NOT in the 400, was never scored at 1476caa, and therefore has no baseline verdict to
take a delta against. Adjudication, not a gate arm.

⛔ THE DISCRIMINATION THIS ROW EXISTS FOR, and it got HARDER in 2026. The question is whether a
foreign company's late-filing penalty differs from a local company's. Until 2026 the currency
itself marked the distinction (USD 25 vs TZS 2,500). Now BOTH are in shillings — TZS 70,000 vs
TZS 2,500 — so a reply that says "70,000" has to be checked for whether it attributes it to the
FOREIGN company, and a reply saying "2,500" for a foreign branch is the defect.

Usage:  CHIKE_MODAL_TOKEN=... python eval/controls/readjudicate_ext_15_2026_10_09.py
Artifact: eval/results/ext_15_readjudication_2026_10_09.json
Exit 0 — an adjudication. Exit 2 if the live ask could not be made (NOT a pass).
"""
import io
import json
import os
import re
import sys
import time
import urllib.request

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROBES = os.path.join(REPO, "eval", "accuracy_gate", "edge_probe_extended_078_DRAFT.jsonl")
OUT = os.path.join(REPO, "eval", "results", "ext_15_readjudication_2026_10_09.json")
ENDPOINT = "https://prosperpiusmbaruku007--chike-inference-web-endpoint.modal.run"
HEALTH = "https://prosperpiusmbaruku007--chike-inference-health.modal.run"

# The 2026-09-05 recorded live reply, so "did it change" is a comparison and not a memory.
PRIOR_REPLY_SOURCE = "eval/results/extended_078_live_replies_2026_09_05.json"


def token():
    p = os.path.expanduser("~/.chike_modal_token.txt")
    return (os.environ.get("CHIKE_MODAL_TOKEN")
            or (io.open(p, encoding="utf-8").read().strip() if os.path.exists(p) else ""))


def ask(q, tok, timeout=600):
    req = urllib.request.Request(
        f"{ENDPOINT}?token={tok}",
        data=json.dumps({"message": q}).encode("utf-8"),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


_NEG = r"(?:\bsi\b|\bsio\b|\bhakuna\b|\bhaina\b|\bnot\b)[\s:,]*(?:TZS\s*|USD\s*)?$"


def asserted(text, needle):
    """Present AND not immediately under a negation — the same polarity discipline the index
    sweep uses, because a reply saying 'SI USD 25' is denying it, not asserting it."""
    out = []
    for m in re.finditer(re.escape(needle), text, re.I):
        if not re.search(_NEG, text[max(0, m.start() - 14):m.start()], re.I):
            out.append(m.group(0))
    return out


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:                                                # noqa: BLE001
        pass

    row = None
    for line in io.open(PROBES, encoding="utf-8"):
        if '"ext_15"' in line:
            row = json.loads(line)
    if row is None:
        print("[FATAL] ext_15 not found in the probe set")
        return 2
    q = row["question"]

    tok = token()
    if not tok:
        print("[FATAL] no CHIKE_MODAL_TOKEN and no ~/.chike_modal_token.txt — the live ask is "
              "the whole point of this file. Exit 2 is NOT a pass.")
        return 2

    try:
        with urllib.request.urlopen(HEALTH, timeout=180) as r:
            h = json.loads(r.read().decode("utf-8"))
    except Exception as exc:                                         # noqa: BLE001
        print(f"[FATAL] /health unreachable: {type(exc).__name__}")
        return 2

    t0 = time.time()
    try:
        out = ask(q, tok)
    except Exception as exc:                                         # noqa: BLE001
        print(f"[FATAL] live ask failed: {type(exc).__name__}: {exc}")
        return 2
    reply = out.get("reply") or out.get("response") or json.dumps(out, ensure_ascii=False)
    took = time.time() - t0

    # ── THE LIMBS, SCORED SEPARATELY. "Half a correction must not flip a count" was this
    # row's own instruction on 2026-10-05, and it cuts both ways: half a right answer must
    # not either.
    limbs = {
        "discrimination_foreign_differs": {
            "asks": "does it say the foreign penalty DIFFERS from the local one?",
            "hit": bool(re.search(r"tofauti|haifanani|si sawa", reply, re.I)),
        },
        "figure_70000_for_the_FOREIGN_company": {
            "asks": "TZS 70,000 per month/part month, attributed to the foreign company",
            "hit": bool(asserted(reply, "70,000")),
        },
        "local_rate_2500_not_applied_to_the_branch": {
            "asks": "2,500 must appear (if at all) as the LOCAL comparator, never as the "
                    "foreign branch's own rate",
            "hit": None,   # adjudicated by hand below
        },
        "superseded_usd_25_absent": {
            "asks": "the pre-2026 USD 25 must not be asserted",
            "hit": not bool(asserted(reply, "USD 25")),
        },
        "citation_part_XII": {
            "asks": "Part XII / Sehemu ya XII (NOT Part XIII, NOT ss.320-328)",
            "hit": bool(re.search(r"(part|sehemu)\s*(ya\s*)?XII\b", reply, re.I)),
        },
        "citation_not_the_reversed_part_XIII": {
            "asks": "the 2026-08-31 reversal must not reappear",
            "hit": not bool(re.search(r"(part|sehemu)\s*(ya\s*)?XIII\b|320-328", reply, re.I)),
        },
    }

    payload = {
        "_what": "ext_15 re-adjudicated by asking the live system again, because its own note "
                 "refuses re-labelling from a desk",
        "measured": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "serving": {"build": h.get("build"), "adapter_repo": h.get("adapter_repo")},
        "question": q,
        "expected_behavior": row["expected_behavior"],
        "key_corrections": [row.get("_scoring_key_correction"),
                            row.get("_scoring_key_correction_2")],
        "prior_verdict": "RE_RUN_REQUIRED (2026-10-06)",
        "prior_reply_source": PRIOR_REPLY_SOURCE,
        "live_reply": reply,
        "wall_seconds": round(took, 1),
        "limbs": limbs,
        "_not_regex_scorable": (
            "this row's gold is `expected_behavior` prose with no correct_answer_sw/answer_type, "
            "so score_question cannot score it. It is also not in the 400 and has no 1476caa "
            "baseline. Hence hand adjudication, and hence no delta against the gate."),
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with io.open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)

    print(f"serving build {h.get('build')}   ask took {took:.0f}s")
    print(f"\nQ: {q}\n")
    print(f"LIVE REPLY:\n{reply}\n")
    print("LIMBS (mechanical; the verdict is still written by hand):")
    for k, v in limbs.items():
        print(f"  {str(v['hit']):5s}  {k}")
        print(f"         {v['asks']}")
    print(f"\nartifact: {os.path.relpath(OUT, REPO)}")
    print("\n⛔ VERDICT NOT SET BY THIS SCRIPT. Read the reply above against expected_behavior "
          "and write the verdict into the artifact by hand — that is what RE_RUN_REQUIRED asked "
          "for, and a script that auto-labels it would be the desk re-labelling the row forbids.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
