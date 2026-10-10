# -*- coding: utf-8 -*-
r"""THE MIRROR SWEEP — EVERY DETERMINISTIC YES/NO LEAD, ASKED IN BOTH POLARITIES.

⛔ WHAT THIS EXISTS FOR. On 2026-10-10 `"Je, NSSF ni ya hiari?"` was answered **"Ndiyo."** —
*yes, NSSF is voluntary* — flatly wrong, on a compulsory levy, in the deterministic engine's
own voice. It was found by hand, by negating the premise of a gate row that had just been
fixed, and it is in NO gate corpus. One question, one mirror, the worst single answer of the
week. This harness asks that question of the whole population instead of one row.

⛔⛔ THE INVARIANT IS LAW-FREE, WHICH IS THE WHOLE REASON IT IS CHEAP AND MECHANICAL:

        A QUESTION AND ITS POLARITY MIRROR MUST NOT RECEIVE THE SAME YES/NO LEAD.

No truth table, no gold answers, no adjudication of what the law says — and therefore no
R38 exposure, which is the trap a sweep like this would otherwise walk into (*"a probe
encodes an expected answer, so a probe can encode a wrong one"*). The direction is pinned by
the POSITIVE side, which the gate and the existing suites already measure; the mirror only
has to disagree with it. When a pair comes back with one lead, **one of the two answers is
wrong and the engine cannot be right about both** — which half is wrong is the adjudication,
and it is reported, not fixed (this pass does not touch the engine).

⚠️ THE CORPUS CANNOT ANSWER THIS QUESTION, WHICH IS WHY THE MIRRORS ARE GENERATED (R17 step
2, applied to a PREMISE instead of a cue list). Measured: of the 135 corpus questions that
receive a deterministic yes/no lead, **6 carry a negated premise.** The population is ~96%
positive-premise by construction — authored by people writing natural questions, who
overwhelmingly write them the plain way — so a sweep over the corpus as it stands is not a
lower bound on this defect class, it is silent about it.

⚠️ FORMS ARE LISTED, NEVER ASSEMBLED FROM OPTIONAL MORPHEMES (R37). Every pair below was read
out of the harvested population (scratch/harvest_yesno.py), not constructed: a built
`(?:ha)?(?:na)?lazimik\w*` generates strings Swahili does not use and misses ones it does,
which is exactly how the 2026-10-07 `uliyalipia`/`uliyolipia` miss happened.

⚠️ AND THE PLANTED SPECIMEN IS THE PRE-FIX eval_394 PAIR (R26). A clean sweep from an inert
classifier is byte-identical to a clean sweep from a sound one, and this classifier's failure
direction is SILENT: a transform that matches nothing, or a mirror that falls off the
deterministic path, produces FEWER findings and reads as health (R39). So the recorded
pre-fix leads — both `Ndiyo.` — are fed to the classifier and it must flag them, in the same
run that reports the live population.

PRIOR ART, and this is a different axis: eval/accuracy_gate/false_premise_pairs_016.jsonl
varies the FRAME (a value asserted with a confirmation tag vs the same fact asked plainly) on
the MODEL path. This varies the PREMISE POLARITY on the DETERMINISTIC path. Neither subsumes
the other.

Usage:  python eval/controls/mirror_premise_sweep_2026_10_10.py
Artifact: eval/results/mirror_premise_sweep_2026_10_10.json
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
OUT = os.path.join(REPO, "eval", "results", "mirror_premise_sweep_2026_10_10.json")

_LEAD = re.compile(r"^\s*(Ndiyo|Hapana)\b", re.IGNORECASE)

# ── THE TRANSFORM TABLE ──────────────────────────────────────────────────────────────────
# (positive form, negated form, frame name, where the form was harvested from).
#
# Bidirectional: a corpus row in EITHER polarity gets its opposite. The 6 negated corpus
# rows are as much a part of the population as the 129 positive ones — eval_393 and eval_394
# are both negated, and both are rows this project has already had to fix.
#
# ⚠️ EVERY PAIR MUST BE EXERCISED BY THE RUN OR DECLARED AUTHORED-ONLY. A transform that
# matches nothing is a dead anchor: it costs nothing, reports nothing, and makes the
# transform list look more thorough than it is. The run asserts coverage per pair.
TRANSFORMS = [
    # applicability, 1sg/1pl/3pl object concord — the plainest and commonest frame
    ("inanihusu", "hainihusu", "applies-to-me", "ap_13, ap_14, ap_16, et_02, eval_363"),
    ("inatuhusu", "haituhusu", "applies-to-us", "hc_10"),
    ("inawahusu", "haiwahusu", "applies-to-them", "oc_09"),
    ("inahusika", "haihusiki", "applies", "sdl_applies working, corpus-adjacent"),
    # obligation / modality
    ("nalazimika", "silazimika", "i-am-obliged", "eval_308, eval_351, probe_14, hcb015_b02:5"),
    ("tunalazimika", "hatulazimika", "we-are-obliged", "authored mirror of the 1pl form"),
    ("natakiwa", "sitakiwi", "i-am-required", "eval_351-adjacent"),
    ("tunatakiwa", "hatutakiwi", "we-are-required", "ext_05"),
    ("inatakiwa", "haitakiwi", "it-is-required", "eval_124, eval_393, os_06"),
    ("ana wajibu", "hana wajibu", "has-a-duty", "eval_121"),
    ("ni lazima", "si lazima", "is-compulsory", "nat_38, edge_p08"),
    # payment / contribution
    ("nalipa", "silipi", "i-pay", "th_11, th_22, ext_12, hc_03"),
    ("tunalipa", "hatulipi", "we-pay", "smn_12, ext_05"),
    ("nachangia", "sichangii", "i-contribute", "eval_311"),
    ("nahitaji", "sihitaji", "i-need", "nat_36, th_02"),
    # lawfulness — minimum_wage's own two frames, which already carry a polarity table
    ("ni halali", "si halali", "is-lawful", "mw_01..mw_05, th_15"),
    ("nakiuka", "sikiuki", "i-am-breaking", "mw_06, mw_07"),
    # optionality — the founding specimen's own frame
    ("ni ya hiari", "si ya hiari", "is-voluntary", "eval_394 (negated side in corpus)"),
    # threshold crossing
    ("nimevuka", "sijavuka", "i-have-crossed", "eval_370"),
    ("yamefika", "hayajafika", "has-reached", "eval_351, th_02"),
    # confirmation of a stated claim
    ("ni kweli", "si kweli", "is-it-true", "edge_p08"),
]

# ⛔ THE PLANTED SPECIMEN (R26 limb 1). The recorded PRE-FIX behaviour of the founding pair:
# both polarities led "Ndiyo.". The classifier must flag it. Provenance is the orchestrator
# comment block at chike/orchestrator.py:_answer_applicability and
# tests/test_optionality_premise.py, which record the pre-fix text verbatim.
PLANTED_PRE_FIX = {
    "question": "Je, NSSF si ya hiari kwa mwajiri anayestahili?",
    "mirror": "Je, NSSF ni ya hiari kwa mwajiri anayestahili?",
    "lead_q": "Ndiyo",
    "lead_m": "Ndiyo",
    # The verbatim pre-fix reply, which is the applicability verdict's own `working` —
    # reproducible today as rules_engine.applicability("nssf").working, so this specimen is
    # not retyped from a write-up.
    "reply": "Ndiyo. NSSF haina kizingiti cha idadi ya wafanyakazi — inahusu mwajiri kutoka "
             "mfanyakazi wa kwanza.",
    "provenance": "eval_394 and its mirror, as served until 2026-10-10. The applicability "
                  "verdict's lead is written for the plain frame 'does this levy apply?', so "
                  "both premises got 'Ndiyo.' — agreeing with the negated premise correctly "
                  "by accident, and with the positive one catastrophically.",
}

# ⛔ R26 limb 2: a clean case the classifier must PASS. Positive-only certifies a classifier
# that flags everything, which is the half the pre-push secret scan was missing.
PLANTED_CLEAN = {"lead_q": "Ndiyo", "lead_m": "Hapana"}


def _load_corpora():
    """Every question in every corpus, file-by-file. Lifted verbatim from
    eval/routing/sweep_levy_party_2026_10_10.py: two sweeps that disagree about what "every
    corpus question" means are two populations, and the whole point is that this is one."""
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
                except Exception:                                        # noqa: BLE001
                    continue
                q = (r.get("question_sw") or r.get("question") or r.get("instruction")
                     or r.get("q") or "")
                if isinstance(q, str) and q.strip():
                    out.append({"file": rel, "line": i + 1,
                                "id": r.get("id") or f"{rel}:{i + 1}", "q": q})
    return out


# ⛔⛔ THE FRAME MUST SIT IN THE CLAUSE THAT CARRIES THE ASK, AND THE FIRST DRAFT DID NOT
# REQUIRE THAT — WHICH PRODUCED FOUR CONFIDENT FALSE FINDINGS OUT OF 46 (R26's second half:
# when a control fires, eliminate the specimen before recording a defect).
#
# The worst of them, `extract_087`: "Uzalishaji TUNALIPA jumla milioni nne, mauzo tunalipa
# jumla milioni tatu, SDL ya kampuni nzima ni NGAPI?" — an AMOUNT question whose yes/no lead
# comes from base_rejection ("the figure you named is not a payroll"). Flipping `tunalipa` in
# the first clause changes a statement about production spending and asks NOTHING different;
# the identical lead is therefore CORRECT, and reporting it would have sent someone to repair
# a working renderer. R34's asymmetry: a fabricated defect generates an edit, a missed one
# does not.
#
# Separators are split on with the digit guard `(?<!\d),(?!\d)` so "TZS 450,000" survives;
# the trailing confirmation tag is stripped with routing's OWN regex (not a second copy) and
# re-appended, because ", sivyo?" is part of the ask rather than a clause after it — without
# that, eval_393 loses its frame and drops out of the population it belongs to.
_SEP = re.compile(r"(?<!\d),(?!\d)|[;—–]|\.\s+|\?\s+")


def _ask_clause(question):
    """(ask clause, prefix, suffix) — the last clause, which is where the ask lives."""
    from chike import routing
    stripped = routing._CONFIRMATION_TAG.sub("", question.strip())
    tag = question.strip()[len(stripped):]
    parts = [p for p in _SEP.split(stripped) if p is not None]
    parts = [p for p in parts if p.strip()]
    if not parts:
        return stripped, "", tag
    last = parts[-1]
    cut = stripped.rfind(last)
    return last, stripped[:cut], stripped[cut + len(last):] + tag


def mirror(question):
    """The question with the polarity of ITS OWN ASK flipped, plus which transform did it.

    Returns (mirrored_text, frame, ask_clause) or (None, None, ask_clause). Word-bounded,
    longest-first, and ONE transform — applying two would flip the polarity back and yield a
    mirror that is semantically the original, which the sweep would then score as a finding.
    """
    ask, prefix, suffix = _ask_clause(question)
    for pos, neg, frame, _src in sorted(TRANSFORMS, key=lambda t: -len(t[0])):
        for src, dst in ((neg, pos), (pos, neg)):       # negated side first: it is narrower
            pat = re.compile(r"(?<![a-z])" + re.escape(src) + r"(?![a-z])", re.IGNORECASE)
            if pat.search(ask):
                flipped = pat.sub(dst, ask, count=1)
                if flipped != ask:
                    return prefix + flipped + suffix, frame, ask
    return None, None, ask


def frame_anywhere(question):
    """The frame a whole-text match WOULD have found — the rejected-specimen bucket.

    R39: when a narrowing drops findings, say which ones and why, per row. A count that falls
    silently is indistinguishable from an instrument that has gone blind.
    """
    for pos, neg, frame, _src in sorted(TRANSFORMS, key=lambda t: -len(t[0])):
        for src in (neg, pos):
            if re.search(r"(?<![a-z])" + re.escape(src) + r"(?![a-z])", question, re.I):
                return frame
    return None


def classify(lead_q, lead_m):
    """The whole adjudication, and it needs no knowledge of the law.

    SAME_LEAD is the finding: one question, two opposite premises, one answer. Exactly one of
    the two replies can be right, and the engine has asserted both.
    """
    if lead_q is None and lead_m is None:
        return "NEITHER_DETERMINISTIC"
    if lead_q is None:
        return "ONLY_MIRROR_DETERMINISTIC"
    if lead_m is None:
        return "MIRROR_LEFT_THE_ENGINE"
    return "FLIPS" if lead_q.lower() != lead_m.lower() else "SAME_LEAD"


# ⚠️⚠️ THE SEVERITY AXIS, AND MY FIRST ONE WAS WRONG IN A WAY THAT WOULD HAVE MISPRIORITISED
# THE WHOLE REPORT. I first split on whether the LEAD SENTENCE restates the proposition
# ("Hapana, si halali." vs a bare "Ndiyo."). That puts `ap_13` — *"Ndiyo. Una wafanyakazi 15
# (10 au zaidi), hivyo SDL inatozwa"* — in the same bucket as the NSSF catastrophe, and the
# two are not comparable: ap_13's NEXT CLAUSE says SDL is charged, so an inverted particle is
# contradicted by the engine's own next breath and a reader can recover the right answer.
#
# What made the NSSF reply catastrophic was not the bare particle. It was that NOTHING in the
# reply addressed VOLUNTARINESS at all — *"Ndiyo. NSSF haina kizingiti cha idadi ya
# wafanyakazi"* answers a HEADCOUNT question, so the "Ndiyo." stood alone as the only thing
# in the reply responsive to what was asked, and it was inverted.
#
#   UNCORRECTED  nothing in the reply addresses the asserted proposition → the particle IS
#                the answer, and it is wrong. eval_394's class.
#   CORRECTED    the reply states the proposition's own substance somewhere, so the particle
#                is inverted and the substance recoverable. Confusing, not misinforming.
#
# ⚠️ A PROXY, AND LABELLED ONE. "The reply mentions the proposition's vocabulary" is not "the
# reply answers it correctly" — per frame, these are the words the correct substance cannot
# be stated without, so an absence is strong evidence and a presence is weak evidence. The
# strict pair is is-voluntary/is-compulsory, which demands `hiari|lazima`: that is the limb
# that separates the founding specimen from everything else.
# ⚠️ ONE SHARED LIST FOR THE OBLIGATION FAMILY, AND SEPARATE STRICT LISTS FOR THE OTHERS —
# which is R20's borrowed-detector question answered deliberately rather than by habit.
# "Does SDL apply to me", "must I pay SDL" and "do I need to register" are THE SAME
# PROPOSITION asked three ways, and the correct substance is one statement, so sharing the
# list is right. `is-voluntary` is NOT in that family however adjacent it looks: a levy can
# apply to you and the question of whether it is optional is a different claim — which is the
# entire content of the eval_394 defect — so it keeps its own two words and would be ruined
# by the merge.
_OBLIGATION = (r"unatakiwa|hutakiwi|haitakiwi|inatakiwa|hutozwa|inatozwa|haihusiki|"
               r"inahusika|inahusu|wajibu|unalipa|hulipi|unachangia|unahitaji|"
               # ⚠️ THE AMT ENGINE SAYS `haitumiki`/`inatumika`, NOT `haihusiki`. Omitting
               # them put ext_05 and smn_12 in the severe bucket when "AMT haitumiki" IS the
               # substance of "must we pay it" — a proxy miss, not a defect, and it would
               # have been reported as the second and third worst findings of the sweep.
               r"haitumiki|inatumika|zimesamehewa")
_FRAME_SUBJECT = {
    "applies-to-me": _OBLIGATION,
    "applies-to-us": _OBLIGATION,
    "applies-to-them": _OBLIGATION,
    "applies": _OBLIGATION,
    "i-am-obliged": _OBLIGATION,
    "we-are-obliged": _OBLIGATION,
    "i-am-required": _OBLIGATION,
    "we-are-required": _OBLIGATION,
    "it-is-required": _OBLIGATION,
    "has-a-duty": _OBLIGATION,
    "i-pay": _OBLIGATION,
    "we-pay": _OBLIGATION,
    "i-contribute": _OBLIGATION,
    "i-need": _OBLIGATION,
    "is-compulsory": r"hiari|lazima",
    "is-voluntary": r"hiari|lazima",
    "is-lawful": r"halali",
    "i-am-breaking": r"halali|kiuka",
    "i-have-crossed": r"kizingiti|umevuka|hujavuka|umefika|unatakiwa",
    "has-reached": r"kizingiti|umevuka|hujavuka|umefika|unatakiwa",
    "is-it-true": r"kweli|unatakiwa|hutakiwi|lazima",
}
_BARE = re.compile(r"^\s*(?:Ndiyo|Hapana)\s*\.", re.IGNORECASE)


def lead_form(reply):
    """Secondary, and free: is the lead SENTENCE bare, or does it restate in the same breath?"""
    return "BARE" if _BARE.match(reply or "") else "RESTATED"


def severity(frame, reply):
    """UNCORRECTED when nothing in the reply addresses the asserted proposition.

    Returns (verdict, matched_token). ⛔ THE TOKEN IS RETURNED SO EVERY DEMOTION IS
    AUDITABLE. This rule DEMOTES findings, so widening it shortens the severe list and a
    shorter severe list is indistinguishable from progress (R39) — the four polarity-rule
    failures of 2026-10-07 were all this shape. Naming the word that demoted each row is
    what lets the next reader re-adjudicate instead of inheriting the count.
    """
    subj = _FRAME_SUBJECT.get(frame)
    if subj is None:
        return "UNKNOWN_FRAME", None
    hit = re.search(subj, reply or "", re.IGNORECASE)
    return ("CORRECTED", hit.group(0)) if hit else ("UNCORRECTED", None)


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:                                                    # noqa: BLE001
        pass

    # ── R26, BEFORE ANYTHING IS MEASURED ────────────────────────────────────────────────
    planted = classify(PLANTED_PRE_FIX["lead_q"], PLANTED_PRE_FIX["lead_m"])
    clean = classify(PLANTED_CLEAN["lead_q"], PLANTED_CLEAN["lead_m"])
    if planted != "SAME_LEAD" or clean != "FLIPS":
        print(f"[FATAL] classifier is not sound: planted={planted} clean={clean}")
        return 2
    # And the transform must actually reach the specimen's own frame.
    m, frame, _ask = mirror(PLANTED_PRE_FIX["question"])
    if m != PLANTED_PRE_FIX["mirror"] or frame != "is-voluntary":
        print(f"[FATAL] the transform does not reproduce the founding mirror: {m!r} ({frame})")
        return 2
    # ⛔ AND THE NARROWING'S OWN SPECIMEN, both limbs. The real row that produced a false
    # finding in the first draft must be REJECTED, and a row whose frame IS the ask must
    # still be accepted — a narrowing asserted only in the rejecting direction is how a
    # filter quietly empties a population (R39).
    _bad = ("Uzalishaji tunalipa jumla milioni nne, mauzo tunalipa jumla milioline tatu, "
            "SDL ya kampuni nzima ni ngapi?")
    if mirror(_bad)[0] is not None or frame_anywhere(_bad) != "we-pay":
        print(f"[FATAL] the ask-clause narrowing does not reject extract_087's shape")
        return 2
    if mirror("Je, mwajiri mwenye wafanyakazi 8 ana wajibu wa kulipa SDL?")[1] != "has-a-duty":
        print("[FATAL] the ask-clause narrowing rejects a frame that IS the ask")
        return 2
    # ⛔ AND THE SEVERITY AXIS GETS ITS OWN TWO LIMBS, because it is the field the report's
    # prioritisation rests on and my first version of it was wrong. The founding specimen
    # must come back UNCORRECTED (nothing in it addresses voluntariness) and ap_13's reply
    # must come back CORRECTED (its next clause says SDL is charged).
    if severity("is-voluntary", PLANTED_PRE_FIX["reply"])[0] != "UNCORRECTED":
        print("[FATAL] the severity axis does not flag the founding specimen")
        return 2
    if severity("applies-to-me",
                "Ndiyo. Una wafanyakazi 15 (10 au zaidi), hivyo SDL inatozwa.")[0] != "CORRECTED":
        print("[FATAL] the severity axis calls a self-correcting reply uncorrected")
        return 2
    missing = [f for f in {t[2] for t in TRANSFORMS} if f not in _FRAME_SUBJECT]
    if missing:
        print(f"[FATAL] frames with no severity subject: {missing}")
        return 2
    print(f"[R26] planted pre-fix pair -> {planted} · clean pair -> {clean} · "
          f"founding mirror reproduced · ask-clause narrowing rejects extract_087 and "
          f"keeps eval_121")

    from chike import routing as _routing
    from chike.model_abstraction import ModelBackend
    from chike.orchestrator import Orchestrator

    class _Silent(ModelBackend):
        """Returns nothing, so a row that reaches the model is identified by empty text and
        the deterministic population is separable without a GPU."""

        def generate(self, prompt, params=None):
            return ""

    def ask(q):
        try:
            text = Orchestrator(backend=_Silent(), retriever=lambda _q: []).answer(q).text or ""
        except Exception as exc:                                         # noqa: BLE001
            return None, f"<<ERROR {type(exc).__name__}: {str(exc)[:120]}>>"
        hit = _LEAD.match(text)
        return (hit.group(1).capitalize() if hit else None), text

    corpus = _load_corpora()
    rows, buckets, frame_hits, errors = [], {}, {}, []
    no_transform, rejected = [], []

    for r in corpus:
        lead_q, text_q = ask(r["q"])
        if text_q.startswith("<<ERROR"):
            errors.append({"id": r["id"], "where": "original", "text": text_q})
            continue
        if lead_q is None:
            continue                                    # not a deterministic yes/no at all
        mir, frame, ask_clause = mirror(r["q"])
        if mir is None:
            elsewhere = frame_anywhere(r["q"])
            rec = {"id": r["id"], "file": r["file"], "line": r["line"], "q": r["q"],
                   "ask_clause": ask_clause, "lead": lead_q, "lead_form": lead_form(text_q),
                   "reply": text_q[:200]}
            if elsewhere:
                # Itemised, not averaged away: this row WOULD have been a finding under the
                # first draft's whole-text match, and it is dropped for a stated reason.
                rec["frame_found_outside_the_ask"] = elsewhere
                rejected.append(rec)
            else:
                no_transform.append(rec)
            continue
        lead_m, text_m = ask(mir)
        if text_m.startswith("<<ERROR"):
            errors.append({"id": r["id"], "where": "mirror", "text": text_m})
            continue
        verdict = classify(lead_q, lead_m)
        sev, sev_tok = severity(frame, text_m) if verdict == "SAME_LEAD" else (None, None)
        frame_hits[frame] = frame_hits.get(frame, 0) + 1
        buckets[verdict] = buckets.get(verdict, 0) + 1
        rows.append({
            "id": r["id"], "file": r["file"], "line": r["line"], "frame": frame,
            "verdict": verdict,
            "severity": sev, "severity_demoted_by": sev_tok,
            "question": r["q"], "lead": lead_q, "lead_form": lead_form(text_q),
            "reply": text_q,
            # The diagnostic, recorded so the artifact is self-sufficient: an asymmetric pair
            # is almost always `detect_intent` resolving one polarity and not the other.
            "intent": _routing.detect_intent(r["q"]),
            "intent_mirror": _routing.detect_intent(mir),
            "mirror": mir, "mirror_lead": lead_m,
            "mirror_lead_form": lead_form(text_m), "mirror_reply": text_m,
        })

    # ⚠️ A TRANSFORM THAT MATCHED NOTHING IS A DEAD ANCHOR, reported by name rather than
    # averaged away. The list looking thorough is not the same as the list being exercised.
    #
    # ⛔ AND DEAD IS SPLIT FROM SHADOWED, because they are different facts and my first draft
    # reported both as "dead". `yamefika/hayajafika` names eval_351 and th_02 as its source
    # and both rows ARE in the population — they matched `nalazimika`/`nahitaji` first, since
    # mirror() applies exactly one transform per question. That is the harness working as
    # designed, not an unexercised pair, and calling it dead would send someone looking for a
    # form Swahili does use.
    corpus_text = " | ".join(r["q"] for r in corpus).lower()
    dead, shadowed = [], []
    for pos, neg, fr, _src in TRANSFORMS:
        if fr in frame_hits:
            continue
        present = any(re.search(r"(?<![a-z])" + re.escape(form) + r"(?![a-z])", corpus_text)
                      for form in (pos, neg))
        (shadowed if present else dead).append(f"{pos}/{neg} ({fr})")

    findings = [r for r in rows if r["verdict"] == "SAME_LEAD"]
    bare = [r for r in findings if r["severity"] == "UNCORRECTED"]
    restated = [r for r in findings if r["severity"] == "CORRECTED"]
    asym = [r for r in rows if r["verdict"] in
            ("MIRROR_LEFT_THE_ENGINE", "ONLY_MIRROR_DETERMINISTIC")]

    art = {
        "_what": "Every corpus question receiving a deterministic yes/no lead, asked again "
                 "with its premise polarity flipped. The invariant is that the two leads "
                 "must differ; it needs no ground truth about the law, so the direction is "
                 "pinned by the positive side the gate already measures.",
        "_population": {
            "corpus_questions": len(corpus),
            "deterministic_yes_no_leads": len(rows) + len(no_transform),
            "paired_by_a_listed_transform": len(rows),
            "no_listed_transform_matched": len(no_transform),
            "_why_this_population": "A yes/no lead in the engine's voice is the only thing "
                                    "this invariant can judge. A row that reaches the model "
                                    "has no engine lead to be inconsistent with, and a row "
                                    "with no polarity frame asserts no premise to flip.",
        },
        "_r26": {"planted_pre_fix": planted, "planted_clean": clean,
                 "planted_provenance": PLANTED_PRE_FIX["provenance"]},
        "verdicts": buckets,
        "severity": {
            "UNCORRECTED_same_lead": len(bare),
            "CORRECTED_same_lead": len(restated),
            "_why_the_split": "UNCORRECTED means NOTHING in the mirror's reply addresses the "
                              "proposition the question asserted, so the inverted particle "
                              "is the only responsive thing in it — eval_394's class, and "
                              "the only one that misinforms. CORRECTED means the reply "
                              "states the substance somewhere, so the particle is inverted "
                              "and the right answer is recoverable from the next clause. "
                              "Same defect, two prices, and my first cut at this axis "
                              "(bare vs restated LEAD SENTENCE) got it wrong.",
        },
        "frames_exercised": frame_hits,
        "transforms_absent_from_the_corpus": dead,
        "transforms_shadowed_by_another_frame_in_the_same_row": shadowed,
        "pairs_that_flip_correctly": [r for r in rows if r["verdict"] == "FLIPS"],
        "findings_same_lead": findings,
        "route_asymmetry": asym,
        "rejected_frame_outside_the_ask": rejected,
        "no_transform_matched": no_transform,
        "errors": errors,
    }
    io.open(OUT, "w", encoding="utf-8").write(
        json.dumps(art, ensure_ascii=False, indent=1))

    print(f"\ncorpus {len(corpus)} · deterministic yes/no "
          f"{len(rows) + len(no_transform) + len(rejected)} · paired {len(rows)} · "
          f"no frame {len(no_transform)} · frame outside the ask {len(rejected)}")
    for k in sorted(buckets):
        print(f"  {buckets[k]:4d}  {k}")
    print(f"  severity of SAME_LEAD: UNCORRECTED {len(bare)} · CORRECTED {len(restated)}")
    flips = [r for r in rows if r["verdict"] == "FLIPS"]
    print(f"\n[POSITIVE LIMB] {len(flips)} pair(s) flip correctly — the limb that shows this "
          f"harness can report health and not only findings:")
    for r in flips:
        print(f"  {r['id']:20s} {r['frame']:16s} {r['lead']} / {r['mirror_lead']}")
    if dead:
        print(f"\n[ABSENT FROM THE CORPUS] {len(dead)}: {', '.join(dead)}")
    if shadowed:
        print(f"[SHADOWED by another frame in the same row] {len(shadowed)}: "
              f"{', '.join(shadowed)}")
    for label, group in (
            ("UNCORRECTED — nothing in the reply addresses what was asked", bare),
            ("CORRECTED — particle inverted, substance recoverable", restated)):
        if not group:
            continue
        print(f"\n[FINDING · {label}] {len(group)} pair(s):")
        for f in group:
            print(f"\n  {f['id']} @ {f['file']}:{f['line']} ({f['frame']})")
            print(f"    Q  {f['question'][:130]}")
            print(f"    -> {f['reply'][:150]}")
            print(f"    M  {f['mirror'][:130]}")
            print(f"    -> {f['mirror_reply'][:150]}")
            if f["severity_demoted_by"]:
                print(f"    .. demoted to CORRECTED by {f['severity_demoted_by']!r}")
    if rejected:
        print(f"\n[SPECIMEN REJECTED · frame present but NOT in the ask] {len(rejected)} — "
              f"each would have been a finding under a whole-text match:")
        for r in rejected:
            print(f"  {r['id']:46s} {r['frame_found_outside_the_ask']:16s} "
                  f"ask={r['ask_clause'][:60]!r}")
    if asym:
        print(f"\n[ASYMMETRY] {len(asym)} pair(s) where one polarity left the engine:")
        for a in asym:
            print(f"  {a['id']:46s} {a['verdict']:26s} {a['frame']:16s} {a['lead_form']}")
    print(f"\nartifact: {os.path.relpath(OUT, REPO)}")
    if errors:
        print(f"[ERRORS] {len(errors)}")
        return 2
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
