# -*- coding: utf-8 -*-
"""What the REVIEW CARD must show: which path answered, the engine's working, and the facts served.

WHY THIS MODULE EXISTS (2026-11-12). `Orchestrator.answer` returns a `Reply` whose sub-answers carry the facts
retrieval served and the engine's computation -- but `ChikeModel.run` returned only `{'reply': text}`, so the
handler's `ask_capturing` (which looks for `working` and `facts`) never found either. Measured: ALL 7 real
queue items have `engine_working: null` and `facts: []`. The reviewer has NEVER been shown the evidence the
whole review design rests on, including for the EFD answer approved on 2026-11-11 -- where the runbook said
the contradicting fact "was on the card". It was not. This is the one function that turns a Reply into what
the card shows, so the container and the tests cannot disagree about it.

PURE: no I/O, no model. `path` names WHICH SOURCE produced the answer, because "a bare Ndiyo with no figure"
(the 02:47 answer) cannot be told from an engine answer without it:
    engine:<type>          the deterministic rules engine answered (working is attached)
    engine:<type>:ask      the engine declined to compute and asked for a figure (never-guess)
    fact                   the model answered from retrieved facts -- NO engine, no arithmetic checked
    clarification          a clarification that is not tied to an engine
    coverage_refusal       the corpus holds nothing on the topic
    refusal                out of scope
"""


def trace(reply) -> dict:
    """{'working': str|None, 'facts': [str], 'path': str} for an orchestrator Reply."""
    subs = list(getattr(reply, "sub_answers", None) or ())
    if getattr(reply, "refused", False) and not subs:
        return {"working": None, "facts": [], "path": "refusal"}
    working_parts, facts, seen, paths = [], [], set(), []
    for sa in subs:
        comp = getattr(sa, "computation", None)
        if comp is not None:
            w = getattr(comp, "working", None)
            if w:
                working_parts.append(str(w))
        for f in (getattr(sa, "facts", None) or ()):
            f = str(f)
            if f not in seen:
                seen.add(f)
                facts.append(f)
        sq = getattr(sa, "sub_question", None)
        ctype = getattr(sq, "computation_type", None) if sq is not None else None
        if getattr(sa, "coverage_refused", False):
            p = "coverage_refusal"
        elif getattr(sq, "kind", None) == "compute" and ctype:
            p = f"engine:{ctype}" + (":ask" if getattr(sa, "needs_clarification", False) else "")
        elif getattr(sa, "needs_clarification", False):
            p = "clarification"
        else:
            p = "fact"
        if p not in paths:
            paths.append(p)
    if not paths:
        paths = ["refusal"] if getattr(reply, "refused", False) else ["fact"]
    return {"working": "\n".join(working_parts) or None, "facts": facts, "path": "+".join(paths)}
