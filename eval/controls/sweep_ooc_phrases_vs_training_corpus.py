# -*- coding: utf-8 -*-
"""The SAME OOC-collision sweep, over the population the existing one cannot see: our own
TRAINING pairs under datasets/.

WHY THIS EXISTS, AND IT IS AN R22 FINDING ABOUT AN INSTRUMENT RATHER THAN ABOUT THE SYSTEM.
eval/controls/sweep_ooc_phrases_vs_inscope.py globs `eval/**/*.jsonl` only -- 1,280 questions.
The bare-`mrabaha` collision closed on 2026-09-29 was found over 14,766 questions, and the
single most damning row in it was `tier1a_wh_007_20260603`, OUR OWN TRAINING PAIR, which lives
in `datasets/`. So the sweep this project built specifically to catch over-broad refusal phrases
could not have caught the most recent one, and nobody had stated its population.

That is R22 exactly, applied to a control instead of to a measurement: the population swept was
the one that was cheapest to glob, not the one an over-broad refusal phrase harms. A training
pair refused by our own gate is worse than a gate row refused by it -- it means we authored the
answer, shipped the answer, and then declined to give it.

R21 BOUND, and it is the SAME bound the sibling harness states: these pairs were authored from
the same source families as the facts, so they share vocabulary with them by construction. A
clean result here is a LOWER BOUND on collision cost, never a statement that the lists are safe.
Adding 13,000 more questions widens the population; it does not make it a sample of what
strangers type. That still needs transcripts.

The OOC-by-design classifier and the accepted-collision register are IMPORTED from the sibling
harness rather than copied, so the two sweeps cannot drift apart on what counts as a collision.

R18: committed before the write-up that cites it.
Artifact: eval/results/ooc_phrase_training_corpus_sweep.json

Usage:  python eval/controls/sweep_ooc_phrases_vs_training_corpus.py
Exit 0 = no unexplained collision; 1 = at least one needs a decision.
"""
import glob
import importlib.util
import json
import os
import sys
from datetime import date

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
CONFIG = os.path.join(REPO, "kaggle", "chike_config.json")
OUT = os.path.join(REPO, "eval", "results", "ooc_phrase_training_corpus_sweep.json")

# Import the sibling sweep for its OOC-by-design classifier and accepted-collision register.
# One definition of "this row is meant to be refused", used by both sweeps.
_sib = os.path.join(HERE, "sweep_ooc_phrases_vs_inscope.py")
_spec = importlib.util.spec_from_file_location("_ooc_inscope_sweep", _sib)
sib = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sib)

sys.path.insert(0, REPO)
from chike import classification                                    # noqa: E402

# Pair files carry the question under different keys than the probe fixtures do.
QUESTION_KEYS = ("question_sw", "question", "instruction", "q", "prompt")
# And their ANSWER under others -- which is the only field that can classify an SFT row.
ANSWER_KEYS = ("output", "answer_sw", "answer", "completion", "response")

# ⚠️ THE FIRST RUN OF THIS SWEEP REPORTED 17 UNEXPLAINED COLLISIONS AND EVERY ONE WAS A FALSE
# POSITIVE -- reproducing, exactly, the failure the sibling harness's own docstring records
# ("The first version of this function knew only about `expected_refusal` and an `ooc_` prefix,
# and reported 34 colliding phrases. Thirty-three of those were OOC questions this function had
# mislabelled as in-scope"). Written down because reproducing a documented trap while holding
# the document open is the R30 decay shape, and because of what a false INERT/false-collision
# verdict causes someone to do next: narrow a refusal phrase that is doing its job, which opens
# a real leak (R26's asymmetry -- only false positives generate edits).
#
# WHY THE SIBLING'S CLASSIFIER CANNOT WORK HERE, and it is a property of the FILE FORMAT, not an
# oversight in it. datasets/**/sft/*.jsonl rows have exactly four keys -- instruction, input,
# output, system. No `pair_type`, no `subdomain`, no `expected_refusal`. Every metadata field
# the sibling reads is ABSENT, so every OOC refusal pair in the training set looks in-scope.
# The only field that can classify such a row is the ANSWER: an out_of_corpus_refusal pair's
# output IS a refusal. So the answer is what gets read, using the same refusal_phrases list
# production uses, and `tier1a_refusal_005` is caught by its id as well.
#
# THE DIRECTION OF THIS CHECK IS DELIBERATELY CONSERVATIVE. Misreading a refusal pair as
# in-scope invents a collision; misreading an in-scope pair as a refusal HIDES one. The phrases
# below are answer-side refusal formulae ("liko nje ya mada yangu") that an in-scope compliance
# answer has no reason to contain -- but note `sina uhakika` and `mshauri wa kodi` from the
# config list are NOT used here: a legitimate in-scope answer can hedge or refer to a tax
# adviser, so matching on those would suppress real collisions.
#
# TWO FORMULA FAMILIES, and the second was missed on the first corrected run. The corpus refuses
# in two templates -- a `mada` one ("liko nje ya mada yangu") and a `mipaka` one ("iko nje ya
# mipaka ya msaada wangu" / "yanazidi mipaka yangu ya sasa"). Adding the second is NOT the
# per-axis patch R33 retires: it is the same refusal template in different words, with 10+
# instances, and the list is closed by reading the corpus rather than by guessing at variants.
_REFUSAL_ANSWER_MARKERS = (
    # the `mada` family
    "nje ya mada yangu", "nje ya maarifa yangu", "haiko katika mada", "haliko katika mada",
    "yako nje ya mada", "liko nje ya mada",
    # the `mipaka` family
    "nje ya mipaka", "mipaka ya msaada wangu", "mipaka yangu ya sasa",
    "yanazidi mipaka", "zinazidi mipaka", "inazidi mipaka",
    # English
    "outside my current knowledge", "beyond my knowledge",
)

# Collisions on THIS population, examined individually and left alone. R20: "no change needed
# here" is a valid recordable outcome, and recording it at the site is what stops the next run
# re-raising it and the next reader narrowing a phrase that is working. Keyed (phrase, row id).
TRAINING_ACCEPTED = {
    ("vat zanzibar", "datasets/tier1a/sft/train_sft.jsonl:3861"):
        "NOT A COLLISION. The pair's answer IS a refusal, written as a substantive 'Hapana' "
        "rather than in either template formula: 'Zanzibar ina mfumo wake tofauti... "
        "Ninashughulikia maswali ya Tanzania Bara (Mainland) tu.' Zanzibar tax is a named OOC "
        "topic under R11 and the gate refusing it is correct. Registered by hand rather than by "
        "widening _REFUSAL_ANSWER_MARKERS, because a marker broad enough to catch a bare "
        "'Hapana' would suppress real collisions -- and hiding a collision is the expensive "
        "direction here (R26: only false positives generate edits, but a false NEGATIVE in a "
        "refusal sweep leaves a real user blocked).",
    ("kodi za zanzibar", "datasets/tier1a/sft/train_sft.jsonl:1625"):
        "Same topic, same decision. The answer opens 'Zanzibar ina mfumo wake wa kodi na "
        "usimamizi tofauti na Tanzania Bara -- hii iko nje ya mipaka yangu ya sasa', so it is "
        "caught by the mipaka family; registered here too in case that marker is ever narrowed.",
    ("thamani ya ardhi", "tier1a_stamp_duty_131_20260609"):
        "A REAL collision, and the phrase is NOT the thing to fix. The pair answers "
        "substantively -- stamp duty of 1% on the combined land-and-buildings value -- so our "
        "own training set teaches an answer the gate refuses. But stamp duty is a named OOC "
        "topic under R11, and the already-accepted `stempu`/eval_228 decision covers the same "
        "ground: narrowing the phrase to rescue this row opens a live capital-taxes leak, and "
        "eval_228's own gold answer is a referral. THE DEFECT HERE IS THE TRAINING PAIR, not "
        "the refusal phrase -- a pair asserting a stamp-duty rate inside an OOC topic. Recorded "
        "as a corpus candidate for the fix phase, deliberately not as a phrase narrowing.",
}

# datasets/ subtrees that are NOT live training content. `rejected/` and the quarantines hold
# rows kept for the audit trail precisely because they are WRONG -- a refusal phrase matching
# one of those is not a cost. Excluded by path, and the exclusion is listed in the artifact so
# it cannot be mistaken for a clean population.
EXCLUDED_DIRS = ("rejected", "flagged", "eval_family_quarantine", "quarantine")


def answer_is_a_refusal(row):
    """True when the pair's own ANSWER is an out-of-corpus refusal.

    This is the discriminator for SFT-format rows, which carry no metadata at all. Reading the
    answer is not a heuristic here: an out_of_corpus_refusal pair is DEFINED by its output
    being a refusal, so the field being read is the one that carries the fact.
    """
    ans = next((row[k] for k in ANSWER_KEYS
                if isinstance(row.get(k), str) and row[k].strip()), "")
    low = ans.lower()
    return any(m in low for m in _REFUSAL_ANSWER_MARKERS)


def load_training_corpus():
    items = []
    for path in sorted(glob.glob(os.path.join(REPO, "datasets", "**", "*.jsonl"),
                                 recursive=True)):
        rel = os.path.relpath(path, REPO).replace("\\", "/")
        if any(f"/{d}/" in f"/{rel}" for d in EXCLUDED_DIRS):
            continue
        with open(path, encoding="utf-8") as fh:
            for ln, line in enumerate(fh, 1):
                if not line.strip():
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    continue
                q = next((row[k] for k in QUESTION_KEYS
                          if isinstance(row.get(k), str) and row[k].strip()), None)
                if not q:
                    continue
                rid = str(row.get("id", f"{rel}:{ln}"))
                items.append({
                    "file": rel, "line": ln, "id": rid, "question": q,
                    "pair_type": row.get("pair_type", ""),
                    "ooc_by_design": (
                        sib.is_ooc_by_design(rel, row)
                        or row.get("pair_type") == "out_of_corpus_refusal"
                        # id-side: tier1a_refusal_005_20260608 and its kin
                        or "refusal" in rid.lower()
                        # answer-side: the ONLY signal an SFT row carries
                        or answer_is_a_refusal(row))})
    return items


def main():
    cfg = json.load(open(CONFIG, encoding="utf-8"))
    phrases = cfg["ooc_phrases"]
    items = load_training_corpus()
    in_scope = [it for it in items if not it["ooc_by_design"]]

    # R20: a loader that silently returns nothing reports ZERO collisions, which is
    # indistinguishable from a clean sweep. The whole point of this file is the size of the
    # population, so the population is what the assertion guards.
    assert len(items) > 2000, (
        f"training-corpus loader returned only {len(items)} questions -- this sweep exists "
        f"BECAUSE the sibling one swept 1,280, so a small number here means the glob or the "
        f"question keys are wrong, not that the corpus is small")
    assert phrases, "ooc_phrases is empty"

    collisions, unexplained = {}, {}
    for phrase in phrases:
        hits = [{"id": it["id"], "file": it["file"], "question": it["question"],
                 "accepted": (sib.ACCEPTED_COLLISIONS.get((phrase, it["id"]))
                              or TRAINING_ACCEPTED.get((phrase, it["id"]))
                              or TRAINING_ACCEPTED.get(
                                  (phrase, f'{it["file"]}:{it["line"]}')))}
                for it in in_scope if phrase in it["question"].lower()]
        if hits:
            collisions[phrase] = hits
            new = [h for h in hits if not h["accepted"]]
            if new:
                unexplained[phrase] = new

    # The conjunctive rules are checked separately: they are not substrings, so the loop above
    # cannot see them, and the 2026-09-29 narrowing is exactly the kind of change whose cost
    # has to be re-measured on THIS population rather than assumed from the other one.
    conj_hits = [{"id": it["id"], "file": it["file"], "question": it["question"]}
                 for it in in_scope
                 if classification._matches_conjunction(it["question"].lower())]

    print(f"training corpus: {len(items)} questions, {len(in_scope)} in-scope, "
          f"{len(items) - len(in_scope)} OOC-by-design")
    print(f"ooc phrases swept: {len(phrases)}")
    print(f"phrases colliding with an in-scope TRAINING pair: {len(collisions)}")
    print(f"  UNEXPLAINED -- these need a decision: {len(unexplained)}")
    print(f"conjunctive-rule hits on in-scope training pairs: {len(conj_hits)}\n")
    for phrase, hits in sorted(collisions.items(), key=lambda kv: -len(kv[1])):
        tag = "ACCEPTED" if phrase not in unexplained else "*** UNEXPLAINED ***"
        print(f'  [{len(hits):>3}] "{phrase}"   {tag}')
        for h in hits[:3]:
            print(f'         {h["id"]}: {h["question"][:94]}')
        if len(hits) > 3:
            print(f"         ... and {len(hits) - 3} more")
    for h in conj_hits:
        print(f'  [CONJ] {h["id"]}: {h["question"][:94]}')

    blob = {
        "measured": str(date.today()),
        "harness": "eval/controls/sweep_ooc_phrases_vs_training_corpus.py",
        "config": "kaggle/chike_config.json",
        "population": "datasets/**/*.jsonl, excluding " + ", ".join(EXCLUDED_DIRS),
        "why_this_population": (
            "The sibling sweep globs eval/** only -- 1,280 questions. The bare-`mrabaha` "
            "collision closed 2026-09-29 was found over 14,766, and its worst row was our own "
            "TRAINING pair tier1a_wh_007_20260603, which lives here and not there. So the "
            "control built to catch over-broad refusal phrases could not have caught the most "
            "recent one. R22: the population swept was the cheapest to glob, not the one the "
            "harm lands in."),
        "bound": (
            "R21 LOWER BOUND. These pairs were authored from the same source families as the "
            "facts and share their vocabulary by construction. Widening the population from "
            "1,280 to this size does not make it a sample of what strangers type."),
        "totals": {"questions": len(items), "in_scope": len(in_scope),
                   "ooc_by_design": len(items) - len(in_scope), "phrases": len(phrases),
                   "phrases_colliding": len(collisions),
                   "phrases_unexplained": len(unexplained),
                   "conjunction_hits_on_in_scope": len(conj_hits)},
        "collisions": collisions,
        "unexplained": unexplained,
        "conjunction_hits": conj_hits,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(blob, fh, ensure_ascii=False, indent=2)
    print(f"\n[saved] {os.path.relpath(OUT, REPO)}")
    return 1 if unexplained or conj_hits else 0


if __name__ == "__main__":
    sys.exit(main())
