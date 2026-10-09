# -*- coding: utf-8 -*-
"""THE STATEMENT ROUTE, SWEPT OVER EVERY CORPUS BEFORE IT SHIPS.

⛔ WHY A FULL SWEEP AND NOT A PROBE SET. This change widens `detect_intent`, which EVERY
question passes through, so the blast radius is the whole corpus — not the three rows it was
built for. R17's procedure applies in full: sweep every corpus, author adversarial probes in
BOTH directions, and pin the rows that must move.

WHAT THE CHANGE IS. Every compute path in `detect_intent` required `_has_number`, so a question
asking what a rate IS, how a levy is COMPUTED, or WHETHER it applies — carrying no digits —
could never reach an engine. Measured on the 2026-10-09 gate: all 12 confirmed defects returned
`intent='none'`, and `levy_rate_statement` already answers two of them correctly. The new path 9
routes an EXPLICITLY named sdl/nssf/wcf question with a rate/method/applicability/optionality
ask, no figure required, placed LAST so it can only catch what every other path declined.

⛔⛔ AND THE PRICE WAS PAID IN THE ENGINE FIRST. The orchestrator's rate branch was gated on an
amount for a recorded, measured reason: eval_111/112 answer correctly on the fact path and
carried incidence detail the engine did not reproduce. The candidate population split **4 good /
4 bad**, so widening the route alone would have traded 4 right answers for 3.
`rate_statement._INCIDENCE` closes that gap with clauses lifted from the golds. **Enrich then
route** — and this sweep is what checks the order held.

THE THREE ROWS THAT MUST MOVE: eval_086 (party inversion), eval_130 (inverted operation),
eval_394 (SDL's headcount threshold bolted onto NSSF).

Usage:  python eval/routing/sweep_statement_route_2026_10_09.py
Artifact: eval/results/statement_route_sweep_2026_10_09.json
Exit 0 clean · 1 an unexpected diversion · 2 could not be exercised (NOT a pass).
"""
import glob
import io
import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO)
OUT = os.path.join(REPO, "eval", "results", "statement_route_sweep_2026_10_09.json")

# Rows the change EXISTS for — each must divert, and each is pinned to the levy it must reach.
MUST_MOVE = {
    "eval_086": "nssf",
    "eval_130": "sdl",
    "eval_394": "nssf",
}

# Rows that divert and MUST NOT lose answer quality. They already pass on the fact path, and
# each names the detail the engine had to gain before this route was safe to open.
EXPECTED_DIVERSIONS = {
    "eval_087": ("nssf", "employee share IS deducted — _INCIDENCE states both shares"),
    "eval_111": ("sdl", "SDL is employer-only — _INCIDENCE['sdl'], from this row's own gold"),
    "eval_112": ("wcf", "paid to the WCF Authority, not TRA — _INCIDENCE['wcf'], from this "
                        "row's own gold"),
    "eval_233": ("sdl", "the 10+ headcount verdict, from the applicability engine"),
    "eval_364": ("wcf", "no minimum, from the first employee — and this row FAILED the regex "
                        "scorer while the judge called it correct, so the engine's verdict is "
                        "an improvement in scorability too"),
}

# ── EVERY OTHER DIVERSION THE SWEEP FOUND, READ AND ADJUDICATED ONE BY ONE ───────────────
# The first run surfaced 23 beyond the 8 above. These are the ones that are IMPROVEMENTS; the
# four that were defects produced vetoes V1-V4 in routing.py instead of entries here.
ADJUDICATED_DIVERSIONS = {
    "ext_50": "THE STRONGEST IMPROVEMENT IN THE SWEEP. 'Mchango wa NSSF ni asilimia ngapi -- "
              "watu wamenambia tofauti, mmoja anasema kumi, mwingine anasema ishirini.' Its "
              "expected behaviour is to RESOLVE which quantity (20% total vs 10% per party) "
              "rather than default to one number -- the quantity-axis-blindness class. The "
              "enriched statement states both and says which share is deducted.",
    "qi_p02": "'Mwajiri anachangia NSSF asilimia ngapi ya mshahara wa mfanyakazi?' Its own "
              "guards_against note says an instruction biasing toward the total breaks this "
              "row; the statement labels both parties, so neither bias applies.",
    "ov_07": "orthographic-variant probe ('samani' for 'thamani') whose risk was REFUSAL; it "
             "now reaches the rate statement.",
    "extract_004": "'Tuna wafanyakazi wachache sana, WCF inatuhusu?' -- WCF has no headcount "
                   "threshold, so the flat verdict is exactly right.",
    "extract_131": "'Nina wafanyakazi wachache tu, SDL itanihusu?' -- no count given, so the "
                   "SDL applicability branch CLARIFIES for the headcount rather than guessing. "
                   "The never-guess path, reached deterministically.",
    "th_22": "'Nina mfanyakazi mmoja tu -- je nalipa WCF?' -- one employee, WCF applies from "
             "the first. Correct.",
    "hc_08": "an SDL applicability question with a stated headcount below 10.",
    "fp_01b": "plain SDL rate question.",
    "fp_02b": "plain WCF rate question -- and the statement now carries 'paid to the WCF "
              "Authority, not TRA', which is why this is safe.",
    "rq_03": "plain SDL rate question (the rate-question probe set these were authored for).",
    "rq_04": "plain WCF rate question.",
    "data/reviewed/hand_coded_batch_015_b02.jsonl:4":
        "'SDL inaanza kuwahusu waajiri wenye wafanyakazi wangapi?' -- the 10+ threshold, which "
        "the applicability engine holds as a constant.",
    "data/reviewed/hand_coded_batch_015_b05.jsonl:1":
        "'Mchango wa mwajiri kwa NSSF ni asilimia ngapi ya mshahara?' -- eval_086's shape "
        "exactly, which is the row this whole change exists for.",
    "data/reviewed/hand_coded_batch_015_b05.jsonl:3":
        "'Jumla ya mchango wa NSSF ni asilimia ngapi?' -- the 20% total, stated.",
    "data/reviewed/nssf_confident_pairs.jsonl:3":
        "same question, second corpus.",
}

# Questions that must STAY on the fact path. Authored, not harvested — these are the forms the
# narrowing exists for, and a clean corpus sweep says nothing about them (R21/R17 step 2).
ADVERSARIAL_MUST_STAY_NONE = [
    ("Naweza kujiunga NSSF kwa hiari?",
     "NSSF genuinely HAS voluntary membership for the self-employed. A bare `hiari` cue would "
     "answer 'NSSF is mandatory for employers' to a question about opting IN — the eval_211 "
     "wrong-topic harm class. The `si/ni ya hiari` predicative frame is what excludes it."),
    ("Je, mtu anayejiajiri anaweza kuchangia NSSF kwa hiari?",
     "same shape, third person"),
    ("NSSF ni nini?", "a definition question has no statement answer"),
    ("SDL ni kodi ya aina gani?", "definition, not rate/method/applicability"),
    ("Ili kuhesabu SDL nahitaji nyaraka gani?",
     "contains `kuhesabu` but asks for DOCUMENTS — this is why _METHOD_QUESTION requires the "
     "interrogative and not a bare verb"),
    ("Adhabu ya kuchelewa kulipa NSSF ni kiasi gani?",
     "a penalty amount is not a rate, a method or an applicability rule, and no statement "
     "function holds it"),
    ("Je, NSSF inahusika na mshahara wote?",
     "a base-SCOPE question. Recorded in _APPLICABILITY_CUES' own notes as the row that got "
     "`nahusika na` dropped, because nssf_applies() would answer a different question"),
    ("NSSF inalipwa tarehe ngapi?",
     "a DEADLINE question. `kiwango` is absent so asks_rate is False, and no statement "
     "function holds a deadline"),
    ("Nyaraka gani zinahitajika kusajili wafanyakazi NSSF?",
     "registration documents — eval_104's subject, and deliberately NOT routed: no engine "
     "holds the document list, so routing it would manufacture a confident wrong answer"),
    ("WCF ni ya mwajiri au mfanyakazi?",
     "an incidence question. The statement now ANSWERS this, but the route does not fire "
     "because no rate/method/applicability cue is present — recorded as a known near-miss "
     "rather than widened for, since widening would need its own sweep"),
]


def _load_corpora():
    """Every question in every corpus, with its file. Named file-by-file so the population is
    inspectable rather than 'whatever the glob found'."""
    pats = [
        "eval/accuracy_gate/*.jsonl",
        "eval/refusal_gate/*.jsonl",
        "eval/fidelity/*.jsonl",
        "eval/grounding/*.jsonl",
        "data/reviewed/*.jsonl",
    ]
    out = []
    for pat in pats:
        for path in sorted(glob.glob(os.path.join(REPO, pat))):
            rel = os.path.relpath(path, REPO).replace("\\", "/")
            for i, line in enumerate(io.open(path, encoding="utf-8")):
                if not line.strip():
                    continue
                try:
                    r = json.loads(line)
                except Exception:                                    # noqa: BLE001
                    continue
                q = (r.get("question_sw") or r.get("question") or r.get("instruction")
                     or r.get("q") or "")
                if isinstance(q, str) and q.strip():
                    out.append({"file": rel, "line": i + 1,
                                "id": r.get("id") or f"{rel}:{i + 1}", "q": q})
    return out


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:                                                # noqa: BLE001
        pass

    from chike import routing

    rows = _load_corpora()
    if len(rows) < 500:
        print(f"[FATAL] only {len(rows)} questions loaded — the sweep has no population and a "
              f"clean result would mean nothing. Exit 2 is NOT a pass.")
        return 2

    # Re-derive the BEFORE state by disabling path 9, rather than hardcoding "it was none".
    # A sweep that assumes the baseline cannot detect having changed something else.
    orig = routing.asks_levy_statement
    routing.asks_levy_statement = lambda text: False
    before = {}
    try:
        for r in rows:
            before[(r["file"], r["line"])] = routing.detect_intent(r["q"])
    finally:
        routing.asks_levy_statement = orig

    diversions, unchanged = [], 0
    for r in rows:
        b = before[(r["file"], r["line"])]
        a = routing.detect_intent(r["q"])
        if a == b:
            unchanged += 1
            continue
        diversions.append({**r, "before": b, "after": a})

    # Nothing that already routed may change route — path 9 is placed last for exactly this.
    rerouted = [d for d in diversions if d["before"] != "none"]

    seen = {d["id"]: d["after"] for d in diversions}
    missing_must_move = {k: v for k, v in MUST_MOVE.items() if seen.get(k) != v}
    wrong_levy = {k: (v, seen[k]) for k, (v, _why) in EXPECTED_DIVERSIONS.items()
                  if k in seen and seen[k] != v}
    unexpected = [d for d in diversions
                  if d["id"] not in MUST_MOVE and d["id"] not in EXPECTED_DIVERSIONS
                  and d["id"] not in ADJUDICATED_DIVERSIONS]

    adversarial = []
    for q, why in ADVERSARIAL_MUST_STAY_NONE:
        got = routing.detect_intent(q)
        adversarial.append({"question": q, "intent": got, "ok": got == "none", "why": why})
    adv_bad = [a for a in adversarial if not a["ok"]]

    findings = []
    if rerouted:
        findings.append(f"{len(rerouted)} question(s) that ALREADY routed changed route — path "
                        f"9 must only catch 'none': {[d['id'] for d in rerouted]}")
    if missing_must_move:
        findings.append(f"must-move rows did not move: {missing_must_move}")
    if wrong_levy:
        findings.append(f"expected diversions reached the WRONG levy: {wrong_levy}")
    if adv_bad:
        findings.append(f"{len(adv_bad)} adversarial probe(s) diverted that must not: "
                        f"{[a['question'] for a in adv_bad]}")
    # ⛔ AN UNADJUDICATED DIVERSION IS A FINDING. My first run reported 23 of them and EXITED 0,
    # because `unexpected` was computed and never checked -- a sweep that lists its own
    # unreviewed output and calls it clean (R20). Four of those 23 were defects, including one
    # the router's own comments had already rejected. Every diversion is now either in a pinned
    # table or it blocks.
    if unexpected:
        findings.append(
            f"{len(unexpected)} UNADJUDICATED diversion(s) — read each, then pin it in "
            f"ADJUDICATED_DIVERSIONS with the reason it is safe, or veto it: "
            f"{[d['id'] for d in unexpected]}")

    payload = {
        "_what": "every corpus question's routing intent before and after the statement route",
        "_why_full_sweep": "the change widens detect_intent, which every question passes "
                           "through, so the population is the whole corpus and not the three "
                           "rows it was built for",
        "questions_swept": len(rows),
        "files": sorted({r["file"] for r in rows}),
        "unchanged": unchanged,
        "diversions": len(diversions),
        "already_routed_and_changed": len(rerouted),
        "must_move": MUST_MOVE,
        "expected_diversions": {k: v[0] for k, v in EXPECTED_DIVERSIONS.items()},
        "diversion_rows": sorted(diversions, key=lambda d: d["id"]),
        "adversarial_must_stay_none": adversarial,
        "findings": findings,
        "_bound": ("R21: this is a LOWER bound on cost. Every corpus here shares vocabulary "
                   "with the facts by construction, so a clean sweep says the change does not "
                   "break what we have — not that it is safe on a stranger's phrasing. The "
                   "adversarial arm is the partial remedy and it was authored by the person "
                   "who wrote the rule."),
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with io.open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)

    print(f"swept {len(rows)} questions across {len(payload['files'])} files")
    print(f"  unchanged              {unchanged}")
    print(f"  diverted none -> levy  {len(diversions) - len(rerouted)}")
    print(f"  ALREADY ROUTED changed {len(rerouted)}   <- must be 0\n")
    for d in sorted(diversions, key=lambda d: d["id"]):
        tag = ("MUST-MOVE" if d["id"] in MUST_MOVE else
               "expected" if d["id"] in EXPECTED_DIVERSIONS else
               "adjudged" if d["id"] in ADJUDICATED_DIVERSIONS else "UNEXPECTED")
        print(f"  [{tag:9s}] {d['id']:28s} {d['before']:6s} -> {d['after']:6s}  "
              f"{d['q'][:58]}")
    print(f"\nadversarial (must stay 'none'): "
          f"{sum(1 for a in adversarial if a['ok'])}/{len(adversarial)} held")
    for a in adv_bad:
        print(f"  ⛔ DIVERTED: {a['question']} -> {a['intent']}")
    print(f"\nartifact: {os.path.relpath(OUT, REPO)}")
    if findings:
        print(f"\n{len(findings)} FINDING(S):")
        for f in findings:
            print(f"  - {f}")
        return 1
    print("\nVERDICT: the route catches only what fell through, and only where intended")
    return 0


if __name__ == "__main__":
    sys.exit(main())
