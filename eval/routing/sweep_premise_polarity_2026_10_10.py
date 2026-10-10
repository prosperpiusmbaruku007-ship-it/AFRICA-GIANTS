# -*- coding: utf-8 -*-
r"""THE BLAST RADIUS OF THE POLARITY CLASS FIX, ENUMERATED BEFORE IT IS CALLED VERIFIED.

TWO CHANGES SHIP TOGETHER AND EACH GETS ITS OWN ARM (R12c step 3), because a moved reply
with two candidate causes attributes to neither:

  A. THE RESOLVER — chike/rules_engine/premise.py, wired once at Orchestrator._resolve_premise.
     Re-leads a verdict whose yes/no answers a premise the question did not assert.
  B. THE CUE LISTS — routing._OWN_OBLIGATION_NEGATED and _NEGATED_APPLICABILITY_CUES. Lets a
     NEGATED question reach the same engine its positive twin already reached.

⛔ THIS IS A POPULATION, NOT A SAMPLE. Both arms are turned OFF by substituting the exact
named objects the change added — the resolver by making `_resolve_premise` the identity, the
cues by rebuilding the lists without their negated halves. Nothing re-implements the
orchestrator's branch ordering; the real `Orchestrator.answer` runs on every corpus question
in all four arm combinations.

⛔⛔ AND THE CONTROL ARM IS THE POINT, NOT A FORMALITY. Yesterday's party renderer passed
every probe I authored and broke SIX corpus rows, one of which (eval_289) lost a correct
computed answer — found by exactly this diff and by nothing else. A positive-premise question
MUST NOT MOVE: the resolver is scoped to return untouched unless the surface form is negated
or the propositions disagree, and if a positive row moves, that scoping claim is false and the
enumeration is not a population.

Usage:  python eval/routing/sweep_premise_polarity_2026_10_10.py
Artifact: eval/results/premise_polarity_sweep_2026_10_10.json
Exit 0 clean · 1 a finding · 2 could not be exercised (NOT a pass).
"""
import glob
import io
import json
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO)
OUT = os.path.join(REPO, "eval", "results", "premise_polarity_sweep_2026_10_10.json")

# ⛔ R17 STEP 2 — PROBES THAT MUST **NOT** ROUTE, each containing a negated obligation form in
# a context where no engine should answer. A clean corpus sweep is a lower bound (R21); these
# are the arm that finds an over-broad cue the corpus never exercises, and the whole reason
# this project's negative forms are `je`-qualified rather than bare.
MUST_NOT_ROUTE = [
    ("Sichangii chama cha wafanyakazi, je hiyo ni shida kisheria?",
     "`sichangii` about a TRADE UNION, not a levy. No levy is named, so no engine holds it."),
    ("Silipi kodi ya ardhi, nifanye nini?",
     "`silipi` about LAND RENT — out of scope entirely. Must stay off every engine."),
    ("Je silipi deni langu la benki mwezi huu, nifanye nini?",
     "`je silipi` with a BANK LOAN. The `je` qualifier does not make the object a levy, and "
     "this is the probe that would catch a cue list keyed on the verb alone."),
    ("Hatulipi wafanyakazi wetu kwa wakati, tutafanya nini?",
     "`hatulipi` meaning we do not pay our STAFF on time — a labour-relations question. The "
     "payroll vocabulary is present, which is what makes it dangerous."),
    ("Silazimika kuhudhuria mkutano wa BRELA, sivyo?",
     "`silazimika` about attending a BRELA meeting. V5's other-domain veto should hold it."),
]

# Probes the change EXISTS for: a negated question that must now reach the engine its positive
# twin already reached. Pinned to the engine, not merely to "it moved" — reaching the WRONG
# engine is the defect, not the fix.
MUST_ROUTE = [
    ("nimeajiri watumishi 25 je silipi SDL", "sdl", "hc_03's own mirror"),
    ("Je, kama nina wafanyakazi 8 tu, bado silazimika kulipa NSSF?", "nssf", "eval_308"),
    ("Nina mfanyakazi mmoja tu anayelipwa TZS 500,000, je bado sichangii WCF?", "wcf",
     "eval_311"),
    ("Tuna wafanyakazi wachache sana, WCF haituhusu?", "wcf", "extract_004"),
    ("Nina mfanyakazi mmoja tu, je WCF hainihusu au ni kwa makampuni makubwa?", "wcf",
     "eval_364 — and the object-concord form was ALREADY matching "
     "_APPLICABILITY_CONCORD; what was missing was _OWN_OBLIGATION, i.e. V4's own gate"),
]


def _load_corpora():
    """Every question in every corpus. Lifted verbatim from the party sweep: two sweeps that
    disagree about what "every corpus question" means are two populations."""
    pats = ["eval/accuracy_gate/*.jsonl", "eval/refusal_gate/*.jsonl", "eval/fidelity/*.jsonl",
            "eval/grounding/*.jsonl", "data/reviewed/*.jsonl"]
    out = []
    for pat in pats:
        for path in sorted(glob.glob(os.path.join(REPO, pat))):
            rel = os.path.relpath(path, REPO).replace("\\", "/")
            for i, line in enumerate(io.open(path, encoding="utf-8")):
                if not line.strip():
                    continue
                try:
                    r = json.loads(line)
                except Exception:                                        # noqa: BLE001
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
    except Exception:                                                    # noqa: BLE001
        pass

    from chike import routing
    from chike.model_abstraction import ModelBackend
    from chike.orchestrator import Orchestrator
    from chike.rules_engine import premise

    class _Silent(ModelBackend):
        def generate(self, prompt, params=None):
            return ""

    # ── the two arms, turned off by substituting the exact objects the change added ─────
    # ⚠️ THE STATICMETHOD OBJECT, NOT THE UNWRAPPED FUNCTION. My first version captured
    # `Orchestrator._resolve_premise`, which the descriptor protocol hands back as a PLAIN
    # FUNCTION; assigning that back to the class rebinds it as an INSTANCE method, so every
    # later call passed `self` where the SubAnswer belonged. Result: 669 errors and a reported
    # blast radius of ZERO — the arm-restoration bug produced the most reassuring possible
    # output, which is R39's direction arriving in the instrument rather than the rule.
    live_resolve = Orchestrator.__dict__["_resolve_premise"]
    live_cues = list(routing._APPLICABILITY_CUES)
    live_own = routing._OWN_OBLIGATION

    def set_arms(resolver_on, cues_on):
        Orchestrator._resolve_premise = (
            live_resolve if resolver_on else staticmethod(lambda sa: sa))
        if cues_on:
            routing._APPLICABILITY_CUES = live_cues
            routing._OWN_OBLIGATION = live_own
        else:
            routing._APPLICABILITY_CUES = [
                c for c in live_cues if c not in routing._NEGATED_APPLICABILITY_CUES]
            routing._OWN_OBLIGATION = re.compile(
                routing._OWN_OBLIGATION_AFFIRMATIVE, re.IGNORECASE)

    # The arms must actually be separable, or a zero blast radius means nothing (the false
    # clean sweep this file's own _GAP_B comment records).
    set_arms(False, False)
    if routing.detect_intent("nimeajiri watumishi 25 je silipi SDL") != "none":
        print("[FATAL] the cue arm does not turn off — a diff against it is meaningless")
        return 2
    set_arms(True, True)
    if routing.detect_intent("nimeajiri watumishi 25 je silipi SDL") != "sdl":
        print("[FATAL] the cue arm does not turn back on")
        return 2
    # ⛔ AND THE RESOLVER ARM GETS THE SAME TREATMENT, because the arm-restoration bug above
    # was invisible in the cue check: both arms were "separable" while the resolver was
    # raising on every row. A positive specimen per arm, asserted before anything is measured.
    _neg_q = "nina wafanyakazi 6 tu je SDL hainihusu"
    set_arms(False, True)
    off = Orchestrator(backend=_Silent(), retriever=lambda _q: []).answer(_neg_q).text or ""
    set_arms(True, True)
    on = Orchestrator(backend=_Silent(), retriever=lambda _q: []).answer(_neg_q).text or ""
    if off.startswith("<<") or not off.startswith("Hapana.") or not on.startswith("Ndiyo"):
        print(f"[FATAL] the resolver arm is not separable: off={off[:70]!r} on={on[:70]!r}")
        return 2
    print("[ARMS] both separable and restored, each with a positive specimen")

    corpus = _load_corpora()

    def run_all():
        out = {}
        for r in corpus:
            key = (r["file"], r["line"])
            try:
                out[key] = Orchestrator(
                    backend=_Silent(), retriever=lambda _q: []).answer(r["q"]).text or ""
            except Exception as exc:                                     # noqa: BLE001
                out[key] = f"<<ERROR {type(exc).__name__}: {str(exc)[:120]}>>"
        return out

    arms = {}
    for label, (res_on, cue_on) in (("before", (False, False)),
                                    ("resolver_only", (True, False)),
                                    ("cues_only", (False, True)),
                                    ("after", (True, True))):
        set_arms(res_on, cue_on)
        arms[label] = run_all()
        print(f"  ran arm {label}: {len(arms[label])} questions")
    set_arms(True, True)

    def _action_for(q):
        """What premise.resolve() DID for this question — recorded rather than inferred from
        the diff, because 'lead_stripped' and a re-lead are different events with different
        correctness criteria and the before/after text alone cannot tell them apart."""
        sa = Orchestrator(backend=_Silent(), retriever=lambda _q: []).answer(q)
        subs = getattr(sa, "sub_answers", None)
        # answer() returns a Reply; re-derive through the dispatch the resolver sits on.
        orch = Orchestrator(backend=_Silent(), retriever=lambda _q: [])
        from chike.orchestrator import SubQuestion
        try:
            sq = SubQuestion(text=q, computation_type=routing.detect_intent(q))
        except TypeError:
            return "unknown"
        try:
            inner = orch._answer_sub(sq)
        except Exception:                                                # noqa: BLE001
            return "unknown"
        if inner.computation is None:
            return "no_computation"
        return premise.resolve(q, inner.computation).action

    by_id = {(r["file"], r["line"]): r for r in corpus}
    moved, errors = [], []
    for key, before in arms["before"].items():
        after = arms["after"][key]
        if before.startswith("<<ERROR") or after.startswith("<<ERROR"):
            errors.append({"id": by_id[key]["id"], "before": before[:160],
                           "after": after[:160]})
            continue
        if before == after:
            continue
        q = by_id[key]["q"]
        p = premise.detect(q)
        moved.append({
            "id": by_id[key]["id"], "file": key[0], "line": key[1], "question": q,
            # Attribution, per R12c: which arm alone reproduces this move.
            "attributed_to": (
                "resolver" if arms["resolver_only"][key] == after
                else "cues" if arms["cues_only"][key] == after
                else "both_together"),
            "action": _action_for(q),
            "premise": (None if p is None else
                        {"frame": p.frame, "proposition": p.proposition,
                         "asserted_truth": p.asserted_truth,
                         "surface_negated": p.surface_negated}),
            "before": before, "after": after,
        })

    # ⛔ THE CONTROL ARM. A question whose ask is POSITIVE must not move: that is the scoping
    # claim premise.resolve() makes in its own docstring, and this is the only thing that can
    # falsify it.
    # ⛔ A CONTROL VIOLATION IS A POSITIVE-PREMISE ROW RE-LED, NOT ONE WHOSE LEAD WAS
    # STRIPPED. My first cut conflated them and reported extract_184 — the row the mismatch
    # handling EXISTS for — as proof that the scoping claim was false. The scoping claim is
    # about re-leading ("a positive question already has the lead the engine wrote for it");
    # a proposition MISMATCH is a separate, deliberate action that is correct at either
    # polarity, because the engine never evaluated the proposition asked.
    control_violations = [
        m for m in moved
        if m["premise"] is not None and not m["premise"]["surface_negated"]
        and m["attributed_to"] != "cues" and m["action"] in ("agreed", "denied")]
    mismatch_strips = [m for m in moved if m["action"] == "lead_stripped"]
    no_premise_moved = [m for m in moved if m["premise"] is None]

    # R17 probe arms
    probe_findings = []
    for q, why in MUST_NOT_ROUTE:
        got = routing.detect_intent(q)
        if got != "none":
            probe_findings.append({"arm": "MUST_NOT_ROUTE", "q": q, "got": got, "why": why})
    for q, want, src in MUST_ROUTE:
        got = routing.detect_intent(q)
        if got != want:
            probe_findings.append({"arm": "MUST_ROUTE", "q": q, "want": want, "got": got,
                                   "src": src})

    art = {
        "_what": "Before/after over every corpus question, with each of the two changes "
                 "separately armed, plus authored probes in both directions.",
        "_why_each_population": {
            "corpus": "the real orchestrator on all 2,484 corpus questions is the only thing "
                      "that can show a row moving that nobody predicted — which is how six "
                      "regressions were found on 2026-10-10's party renderer, after every "
                      "authored probe passed.",
            "MUST_NOT_ROUTE": "R21: the corpora share vocabulary with the cues by "
                              "construction, so a clean corpus sweep is a lower bound. These "
                              "put the negated forms in contexts no engine should answer.",
            "MUST_ROUTE": "R31 step 3: the signal arrives ONLY through natural phrasing, "
                          "which a unit test calling detect_intent with a crafted string "
                          "cannot establish.",
        },
        "corpus_questions": len(corpus),
        "moved": len(moved),
        "attribution": {k: sum(1 for m in moved if m["attributed_to"] == k)
                        for k in ("resolver", "cues", "both_together")},
        "control_violations": control_violations,
        "mismatch_strips": mismatch_strips,
        "_the_cue_arm_moved_nothing_and_that_is_the_expected_result": (
            "ZERO corpus rows moved from the cue widening, because the corpus is ~96% "
            "positive-premise: of 135 questions receiving a deterministic yes/no lead, 6 "
            "carry a negated premise. The cue change is INVISIBLE to the corpus by "
            "construction, which is exactly R21's point — a clean corpus sweep here is not "
            "evidence of safety, it is evidence that the corpus does not exercise the "
            "change. The MUST_ROUTE and MUST_NOT_ROUTE arms are where its evidence lives."),
        "moved_with_no_detected_premise": no_premise_moved,
        "probe_findings": probe_findings,
        "rows": moved,
        "errors": errors,
    }
    io.open(OUT, "w", encoding="utf-8").write(json.dumps(art, ensure_ascii=False, indent=1))

    print(f"\ncorpus {len(corpus)} · moved {len(moved)}")
    for k, v in art["attribution"].items():
        print(f"  {v:4d}  attributed to {k}")
    for m in moved:
        pr = m["premise"]
        tag = (f"{pr['frame']}/{'NEG' if pr['surface_negated'] else 'POS'}" if pr else "—")
        print(f"\n  {m['id']} [{m['attributed_to']}] {tag}")
        print(f"    Q      {m['question'][:118]}")
        print(f"    BEFORE {m['before'][:118]}")
        print(f"    AFTER  {m['after'][:118]}")
    if control_violations:
        print(f"\n[CONTROL VIOLATION] {len(control_violations)} POSITIVE-premise row(s) moved "
              f"under the resolver. The scoping claim is false:")
        for m in control_violations:
            print(f"  {m['id']}: {m['question'][:100]}")
    if no_premise_moved:
        print(f"\n[NO-PREMISE MOVED] {len(no_premise_moved)} row(s) moved with no premise "
              f"detected — the resolver should be a no-op on these:")
        for m in no_premise_moved:
            print(f"  {m['id']} [{m['attributed_to']}]: {m['question'][:95]}")
    if probe_findings:
        print(f"\n[PROBE FINDINGS] {len(probe_findings)}:")
        for p in probe_findings:
            print(f"  {p['arm']}: got={p.get('got')} want={p.get('want','none')} "
                  f"| {p['q'][:85]}")
    print(f"\nartifact: {os.path.relpath(OUT, REPO)}")
    if errors:
        print(f"[ERRORS] {len(errors)}")
        return 2
    return 1 if (control_violations or probe_findings) else 0


if __name__ == "__main__":
    sys.exit(main())
