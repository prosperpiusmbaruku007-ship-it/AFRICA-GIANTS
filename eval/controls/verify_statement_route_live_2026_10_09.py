# -*- coding: utf-8 -*-
"""R16 LIVE VERIFICATION OF THE STATEMENT ROUTE + THE ROW-9 REWORDING (deploy 8d7ebd2).

Two changes shipped in one deploy and they must be verified separately, because they fail
differently:

  * **THE STATEMENT ROUTE** (`chike/routing.py` path 9 + the orchestrator's threshold and
    optionality branches). Questions asking for a RATE, a METHOD, a THRESHOLD or an
    APPLICABILITY RULE now reach the deterministic engines with no figure in the text. Measured
    cause: all 12 confirmed defects of gate `0e11c3d` returned `detect_intent='none'`, and the
    engines already answer several of them correctly.
  * **INDEX ROW 9** (`nssf_employer_rate`), reworded so the BASE is not readable as the SOURCE.

⛔ WHAT THIS HARNESS CAN AND CANNOT SEE, STATED FIRST BECAUSE IT BOUNDS EVERY ROW BELOW.
`/web_endpoint` returns `{'reply': text}` and nothing else — no intent, no computation record.
So **the live route is not directly observable.** It is established two ways, neither of which
is a guess:

  1. `detect_intent` is re-derived HERE, locally, against a tree whose relationship to the
     deployed commit is checked rather than assumed: `/health`'s build must be an ANCESTOR of
     HEAD and no serving path (`chike/`, `chike-inference/`, the index files) may have moved
     since it. Deterministic function, same code, provable provenance.
  2. Each routed row carries a `route_evidence` pattern taken from the ENGINE'S OWN output
     string (printed and pasted, not invented) — a clause the fact path does not produce. That
     is positive evidence the deterministic text reached the user.

⛔ R38 — A PROBE ENCODES AN EXPECTED ANSWER, SO IT CAN ENCODE A WRONG ONE. Two of three
failures in the 2026-10-07 live verify were the harness. Here:
  * every `must_match` is quoted from a COMMITTED source — the row's gold answer, the engine's
    emitted working, or `rates.py` — and the source is named in the row;
  * where a question admits two correct answers, BOTH are accepted and the reason is recorded
    (`eval_394` can be answered with the gold's "lazima" or the engine's "haina kizingiti …
    mfanyakazi wa kwanza");
  * the `limb` field separates a DEPLOY verdict from an ANSWER-QUALITY observation, so a row
    whose answer is merely imperfect cannot falsify the deploy;
  * **`nipe … ili nihesabu` is NOT used as a global clarification signature**, because SDL's own
    threshold statement legitimately ends with it. Using it everywhere would have failed the
    threshold probe for containing the correct answer — the trap caught before the run this time.

⛔ QUESTIONS ARE LOADED VERBATIM FROM THE COMMITTED CORPORA, NEVER RETYPED. R26's rule,
mechanised: a five-word paraphrase was once enough to flip a correct body into a flagged one.
`eval_086` / `eval_130` / `eval_394` come out of the gate files and `adv_06` out of
`eval/refusal_gate/ooc_adversarial_in_scope_015.jsonl`, each looked up by id and asserted found.

⛔ NOTHING HERE IS A TYPED PIN. The expected served digest is COMPUTED from the committed
index the same way `served_index_identity` computes it, and the build is checked by ANCESTRY plus
a serving-path diff rather than by equality to anything. The 2026-10-08 harness hand-copied both
constants, which is a stale pin waiting to happen (R18's first incident); the first run of THIS
harness then proved that even a *derived* equality against HEAD is wrong, because committing the
harness before running it moved HEAD one commit past the deploy.

Usage:  python eval/controls/verify_statement_route_live_2026_10_09.py
Artifact: eval/results/statement_route_live_2026_10_09.json  (written after EVERY row, and
          resumed from, so a dropped Tanzanian link costs one row and never the run)
Exit 0 if every `deploy`-limb row passes and health agrees · 1 otherwise · 2 if not exercisable.
"""
import hashlib
import io
import json
import os
import re
import subprocess
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, REPO)

OUT = os.path.join(REPO, "eval", "results", "statement_route_live_2026_10_09.json")
ENDPOINT = "https://prosperpiusmbaruku007--chike-inference-web-endpoint.modal.run"
HEALTH = "https://prosperpiusmbaruku007--chike-inference-health.modal.run"

# Negation window for mention-vs-assertion, word-bounded throughout. A bare `si\s` matches
# inside the ordinary word `kiasi `, which on 2026-10-07 silently deleted the one real finding
# in a quarantine audit — the deleting direction of filter failure (R39).
NEGATED = (r"(?:\bsi\b|\bsio\b|\bsiyo\b|\bnot\b|\bhapana\b|\bhakuna\b|\bhaina\b|\bhakitumiki\b"
           r"|\bsupersedes\b|\bya\s+zamani\b)[\s:,—-]*(?:TZS\s*|USD\s*|asilimia\s*)?$")


def _sh(*args):
    return subprocess.run(args, cwd=REPO, capture_output=True, text=True).stdout.strip()


# ⛔ THE DEPLOYED COMMIT, NOT HEAD — AND THE FIRST RUN PROVED WHY. Deriving this as
# `rev-parse HEAD` read `build_is_this_working_tree: false` for a reason that is not a defect:
# this harness was COMMITTED (R18) after the deploy, so HEAD had legitimately moved one commit
# on. An equality against HEAD therefore fails on every deploy followed by any commit at all —
# the same shape as the provenance limb in the freshness test, which had to be re-pointed for
# the same reason an hour earlier. What matters is not "is the build HEAD" but:
#   (a) is the deployed commit an ANCESTOR of HEAD (not a fork, not something newer), and
#   (b) has any SERVING path moved since it — chike/, chike-inference/, the index files.
# A doc or harness commit landing after a deploy is not a stale deploy, and treating it as one
# teaches the reflex of overriding the check.
DEPLOY_PATHS = ["chike", "chike-inference", "kaggle/rag_facts_text.json",
                "kaggle/rag_embeddings.npy", "kaggle/chike_config.json"]
HEAD = _sh("git", "rev-parse", "--short", "HEAD")


def expected_served_sha256():
    """Computed from the COMMITTED index, exactly as `served_index_identity` computes it.

    Derived rather than pinned: a hand-copied digest is a stale-pin waiting to happen, and the
    repo file is the single thing both this harness and the deployed image are supposed to agree
    about. Both deploy dirs are hashed and asserted equal — two dirs committed separately is a
    distinct defect the R15 dual-commit step exists to prevent.
    """
    digests = {}
    for d in ("chike-inference", "kaggle"):
        with io.open(os.path.join(REPO, d, "rag_facts_text.json"), encoding="utf-8") as fh:
            rows = json.load(fh)
        blob = json.dumps(rows, ensure_ascii=False).encode("utf-8")
        digests[d] = (hashlib.sha256(blob).hexdigest(), len(rows))
    assert len(set(digests.values())) == 1, f"the two deploy dirs disagree: {digests}"
    return digests["chike-inference"][0], digests["chike-inference"][1]


EXPECTED_SHA256, EXPECTED_ROWS = expected_served_sha256()


# ── QUESTIONS, VERBATIM FROM THE COMMITTED CORPORA ──────────────────────────────────────
_CORPORA = (
    "eval/accuracy_gate/eval_questions_001.jsonl",
    "eval/accuracy_gate/eval_questions_002_additions.jsonl",
    "eval/accuracy_gate/eval_questions_003.jsonl",
    "eval/refusal_gate/ooc_adversarial_in_scope_015.jsonl",
)


def _corpus_rows():
    out = {}
    for rel in _CORPORA:
        for line in io.open(os.path.join(REPO, rel), encoding="utf-8"):
            if line.strip():
                r = json.loads(line)
                r["_file"] = rel
                out[r["id"]] = r
    return out


ROWS_BY_ID = _corpus_rows()


def q(qid):
    r = ROWS_BY_ID.get(qid)
    assert r, f"{qid} is not in any named corpus — this harness is stale, not the system"
    text = r.get("question_sw") or r.get("question")
    assert text, f"{qid} has no question text: {sorted(r)}"
    return text


def gold(qid):
    return (ROWS_BY_ID[qid].get("correct_answer_sw") or "").strip()


# ── THE ENGINE'S OWN WORDS, so route_evidence is sourced rather than guessed ─────────────
from chike import routing                                                    # noqa: E402
from chike import rules_engine                                               # noqa: E402
from chike.rules_engine import rates                                         # noqa: E402

ENGINE_TEXT = {
    "nssf": rules_engine.levy_rate_statement("nssf").working,
    "sdl": rules_engine.levy_rate_statement("sdl").working,
    "sdl_threshold": rules_engine.levy_rate_statement("sdl", None).working,
    "nssf_applies": rules_engine.nssf_applies().working,
}
# Each clause used below as route_evidence must really be in the engine's output. A pattern that
# matches nothing is a check that cannot fail (R20), and this is the cheapest place to find out.
_EVIDENCE = {
    "nssf_not_deducted": (r"HAIKATWI\s+kwenye\s+mshahara|haikatwi\s+kwenye\s+mshahara", "nssf"),
    "sdl_whole_payroll": (r"JUMLA\s+ya\s+mishahara|jumla\s+ya\s+mishahara", "sdl"),
    "sdl_ten_or_more": (r"wafanyakazi\s+10\s+au\s+zaidi", "sdl_threshold"),
    "nssf_first_employee": (r"mfanyakazi\s+wa\s+kwanza", "nssf_applies"),
}
for _name, (_pat, _src) in _EVIDENCE.items():
    assert re.search(_pat, ENGINE_TEXT[_src], re.I), (
        f"route_evidence {_name!r} matches nothing in the engine's own output for {_src!r}. "
        f"The engine wording changed and this harness would have reported a route failure that "
        f"is really a stale pattern: {ENGINE_TEXT[_src]!r}")


PROBES = [
    {
        "id": "eval_086_nssf_employer_rate_and_party",
        "limb": "deploy",
        "pinned": True,
        "proves": "⛔ PINNED MUST-MOVE ROW #1, and it is BOTH changes at once. The 0e11c3d gate "
                  "served 'Kiasi kinachokatwa na mwajiri KWENYE MSHAHARA wa mfanyakazi … ni "
                  "asilimia 10' — the rate right, the party inverted, which makes an employer "
                  "deduct 10% from wages unlawfully on top of the employee's own 10%. The route "
                  "now reaches levy_rate_statement('nssf'), which states both shares AND their "
                  "incidence; index row 9 no longer invites the inversion either.",
        "question": q("eval_086"),
        "source": "question verbatim from eval_questions_001.jsonl; expectation from its own "
                  "gold ('haikatwi kutoka mshahara wa mfanyakazi') and from the engine working",
        "baseline_committed_row": "gate_production_0e11c3d.json, adjudicated FALSE_PASS",
        "must_match": r"asilimia\s*10|10\s*%",
        "must_not_assert": r"(?:kinachokatwa|hukatwa|inakatwa|hukatwa)[^.]{0,80}"
                           r"mshahara\s+wa\s+mfanyakazi[^.]{0,40}(?:asilimia\s*10|10\s*%)",
        "route_evidence": "nssf_not_deducted",
        "note": "must_not_assert targets the INVERSION (the employer's share described as a "
                "deduction from the employee's wage), not the words 'kukatwa' or '10' — the "
                "correct answer necessarily contains both, and so does the engine's own text.",
    },
    {
        "id": "eval_130_sdl_method",
        "limb": "deploy",
        "pinned": True,
        "proves": "⛔ PINNED MUST-MOVE ROW #2. The 0e11c3d reply described the INVERSE operation "
                  "— dividing the payroll by 3.5% — which no figure-comparing fidelity rule can "
                  "see, because the reply produces no figure at all (R19: this is a method "
                  "claim, not a derived quantity). It turned out ROUTABLE, not merely guardable: "
                  "levy_rate_statement('sdl') already answers 'how is SDL computed'.",
        "question": q("eval_130"),
        "source": "question verbatim from eval_questions_001.jsonl; gold says 'Zidisha jumla ya "
                  "mishahara … kwa asilimia 3.5'",
        "must_match": r"3[.,]5\s*%|asilimia\s*3[.,]5",
        "must_not_match": r"\bgawanya\b|\bkugawanya\b|\bgawa\b\s+(?:kwa|na)\s*(?:asilimia\s*)?3",
        "route_evidence": "sdl_whole_payroll",
        "note": "must_not_match is the inverted operation. 'Zidisha' is not required: the engine "
                "states the base and the rate without using the imperative, and demanding the "
                "gold's verb would fail a correct engine rendering.",
    },
    {
        "id": "eval_394_nssf_not_optional",
        "limb": "deploy",
        "pinned": True,
        "proves": "⛔ PINNED MUST-MOVE ROW #3 — AND THE SECOND OF MY TWO REGRESSIONS. After the "
                  "route opened, this yes/no question fell through to the AMOUNT path and asked "
                  "the user for a payroll figure, which no payroll can answer. The orchestrator's "
                  "applicability gate was widened with asks_levy_optionality to fix it. Both "
                  "limbs are checked here: a substantive verdict AND no request for a figure.",
        "question": q("eval_394"),
        "source": "question verbatim from eval_questions_003.jsonl. TWO correct answers accepted "
                  "and that is deliberate (R38): the gold says 'si ya hiari … ni lazima', the "
                  "engine says 'haina kizingiti … kutoka mfanyakazi wa kwanza'. Both answer it.",
        "must_match": r"\blazima\b|si\s+ya\s+hiari|haina\s+kizingiti|mfanyakazi\s+wa\s+kwanza",
        "must_not_match": r"nipe\s+(?:jumla|mshahara|kiasi)|ili\s+ni(?:hesabu|kuhesabu)",
        "route_evidence": "nssf_first_employee",
        "observe": r"\bndiyo\b",
        "note": "must_not_match is the amount-path clarification shape. It is scoped to THIS row "
                "on purpose: SDL's threshold statement legitimately ends 'nipe jumla ya mishahara "
                "… ili nihesabu', so the same pattern as a global signature would fail a correct "
                "answer two rows down.",
    },
    {
        "id": "threshold_question_ANSWERS_rather_than_clarifies",
        "limb": "deploy",
        "proves": "⛔ MY FIRST REGRESSION, caught end-to-end and invisible to the route check. "
                  "With path 9 open and no threshold branch, 'how many employees' reached the "
                  "clarification path — which then ASKED for the headcount while its own text "
                  "contained the answer. The orchestrator now answers from rates.py before "
                  "clarifying.",
        "question": "Mwajiri analazimika kulipa SDL akiwa na wafanyakazi wangapi?",
        "source": f"rates.SDL_MIN_EMPLOYEES = {rates.SDL_MIN_EMPLOYEES}; engine working "
                  f"says 'wafanyakazi 10 au zaidi'. NOT a corpus row — authored, and said so.",
        "must_match": r"\b10\b",
        "route_evidence": "sdl_ten_or_more",
        "note": "THE CHECK IS THE PRESENCE OF THE THRESHOLD, and that is the whole test: a "
                "clarification is precisely a reply that asks for the headcount WITHOUT stating "
                "10. No forbidden phrase is used, because the correct answer ends by inviting "
                "the payroll figure — forbidding that would fail the fix.",
    },
    {
        "id": "adv_06_stays_OFF_the_route",
        "limb": "deploy",
        "proves": "⛔ THE OVER-BREADTH ROW, and the one that matters most. V3 (the sufficiency / "
                  "alternative frame) exists for it: path 2b's own note had ALREADY rejected this "
                  "diversion and my first draft reintroduced it. Routing it would answer 'WCF is "
                  "0.5%' to an employer asking whether accident insurance suffices — a confident "
                  "answer to a question nobody asked. It must be ANSWERED (expected_refusal is "
                  "false) and must NOT receive the WCF rate statement.",
        "question": q("adv_06"),
        "source": "verbatim from eval/refusal_gate/ooc_adversarial_in_scope_015.jsonl, which "
                  "records expected_refusal=false and guards_against bare 'bima'",
        "must_not_match": r"Kiwango\s+cha\s+WCF\s+ni\s+asilimia\s*0[.,]5|sina\s+uhakika",
        "must_match": r"WCF|fidia|wcf\.go\.tz",
        "local_intent_must_be": "none",
        "note": "must_not_match carries BOTH failure directions — the engine signature (routed "
                "when it must not be) and the refusal phrase (refused when it must not be). The "
                "committed probe asserts the second; the sweep asserts the first.",
    },
    {
        "id": "negative_compute_path_still_computes",
        "limb": "deploy",
        "proves": "NEGATIVE: removing the rate branch's `amount is not None` gate must not have "
                  "taken the AMOUNT path with it. A question WITH figures must still return the "
                  "computed figure, not a rate statement. 12 employees × TZS 10,000,000 → 350,000.",
        "question": "Nina wafanyakazi 12 na jumla ya mishahara yao ni TZS 10,000,000 kwa mwezi. "
                    "SDL ni kiasi gani?",
        "source": "rates.SDL_RATE = 3.5% of total payroll; 0.035 × 10,000,000 = 350,000. "
                  "detect_intent returns 'sdl' here via the NUMBER path, not path 9 — "
                  "asks_levy_statement is False because the question carries a money ask.",
        "must_match": r"350,?000",
        "_probe_was_corrected_mid_run": (
            "⛔ MY PROBE WAS THE DEFECT, and it is R38's exact shape. The first wording — "
            "'Mishahara ya wafanyakazi wangu 12 ni TZS 10,000,000 kwa mwezi' — is genuinely "
            "AMBIGUOUS between per-employee and total, and production correctly asked which: "
            "'Ili nihesabu SDL, niambie kama kiasi ni kwa kila mfanyakazi au ni jumla ya wote'. "
            "My must_match demanded 350,000, i.e. it encoded ONE reading of a question that has "
            "two, and scored a correct clarification as a broken compute path. Suspect the "
            "specimen before the system (R26), and hardest when the probe is newer than the "
            "thing it tests — the clarification copy is from 2026-07-23 (5239190), eleven weeks "
            "older than the statement route, and `git merge-base --is-ancestor` confirms it "
            "predates 7b15756, so it cannot be a regression from this change. The failing "
            "wording is kept as its own answer_quality observation below rather than deleted."),
        "note": "If this fails while the three pinned rows pass, the statement route has "
                "SWALLOWED the compute path — the expensive failure mode of widening a gate "
                "every question passes through.",
    },
    {
        "id": "per_vs_total_ambiguity_fires_even_when_the_user_said_JUMLA",
        "limb": "answer_quality",
        "proves": "⛔ A REAL NEAR-MISS, FOUND BY MY OWN BAD PROBE AND KEPT BECAUSE IT IS REAL. "
                  "The per-vs-total clarification is correct on the bare wording, and it ALSO "
                  "fires on 'Jumla ya mishahara ya wafanyakazi wangu 12 ni TZS 10,000,000' — "
                  "where the user has already said JUMLA (total). The same figures asked as "
                  "'Nina wafanyakazi 12 na jumla ya mishahara yao ni …' compute 350,000 "
                  "correctly, so the sensitivity is to where 'jumla' sits in the sentence, not "
                  "to whether it is present. NOT a regression (copy predates this change by "
                  "eleven weeks) and NOT fixed here: it is the compute path, it needs its own "
                  "R17 sweep, and a clarification is the SAFE direction of this error.",
        "question": "Jumla ya mishahara ya wafanyakazi wangu 12 ni TZS 10,000,000 kwa mwezi. "
                    "SDL ni kiasi gani?",
        "source": "found while adjudicating this harness's own FAIL on 2026-10-09; "
                  "clarification copy from chike/clarification.py:270 (commit 5239190, "
                  "2026-07-23)",
        "observe": r"niambie\s+kama\s+kiasi|kwa\s+kila\s+mfanyakazi\s+au",
        "note": "OBSERVED, never asserted. Recording it as a deploy requirement would demand a "
                "fix nobody has scoped, and asserting the clarification is correct would freeze "
                "a behaviour that may well be worth narrowing later.",
    },
    {
        "id": "negative_row57_efd_guard_still_holds",
        "limb": "deploy",
        "proves": "NEGATIVE: D-FIDELITY-7 must still stop the fabricated TZS 11,000,000 EFD "
                  "threshold. Accepts the withheld-answer copy, which is the guard WORKING — "
                  "scoring that as a regression was my error on 2026-10-07 (R38).",
        "question": "Kizingiti cha kuanza kutumia EFD ni mauzo ya TZS 200,000,000, sivyo?",
        "source": "regen critical_queries 'EFD threshold' (eval_347 verbatim); index row 57",
        "must_not_assert": r"11[,.]?000[,.]?000|milioni\s+kumi\s+na\s+moja",
        "must_match": r"haina\s+kizingiti|hakuna\s+kizingiti|bila\s+kujali|hakitumiki"
                      r"|siwezi\s+kukithibitisha|sitakisii|sitalitumia",
        "withheld_signature": r"siwezi\s+kukithibitisha|sitakisii|sitalitumia",
    },
    {
        "id": "negative_row172_brela_foreign_penalty",
        "limb": "deploy",
        "proves": "NEGATIVE: the BRELA foreign late-filing figure shipped two cycles ago must "
                  "still be TZS 70,000. A redeploy is exactly when a prior ship silently "
                  "regresses, and this row's index neighbours moved in this index build.",
        "question": "Tawi letu la kampuni ya kigeni limechelewa kuwasilisha ripoti ya mwaka. "
                    "Adhabu ni tofauti na kampuni za huku?",
        "source": "regen critical_queries 'BRELA foreign late-filing fee' (ext_15 verbatim)",
        "must_match": r"70,?000",
        "must_not_assert": r"USD\s*25\b|\$\s*25\b|dola\s*25\b",
    },
    {
        "id": "negative_nssf_fine_either_statutory_limb",
        "limb": "deploy",
        "proves": "NEGATIVE: the Cap.50 corrections must be where they were. Accepts EITHER "
                  "locked limb — s.76(1)'s ten-million ceiling or s.14(3)'s 5%/month — because "
                  "the question licenses both, and demanding one made a CORRECT reply fail on "
                  "2026-10-07. The 100,000 understatement is what must not return.",
        "question": "Nisipolipa michango ya NSSF kabisa, nitatozwa faini ya kiasi gani?",
        "source": "regen critical_queries 'NSSF fine ceiling is ten million'; Cap.50 R.E.2023",
        "must_match": r"10,?000,?000|milioni\s+kumi|asilimia\s*5\b|5\s*%",
        "must_not_assert": r"100[,.]?000(?![,.\d])|laki\s+moja",
    },
    {
        "id": "negative_config_only_ooc_phrase",
        "limb": "deploy",
        "proves": "CONFIG LOADING, separately from code — the 2026-08-07 diagnostic that "
                  "distinguishes a config failure from a stale warm container. This phrase is in "
                  "chike_config.json and NOT in the hardcoded fallback.",
        "question": "Nataka kuuza kiwanja changu, kodi ya mapato ni kiasi gani?",
        "source": "chike_config.json ooc_phrases (config-only)",
        "must_match": r"sina uhakika|thibitisha|siwezi|nje ya",
    },
    {
        "id": "wcf_incidence_known_near_miss",
        "limb": "answer_quality",
        "proves": "A RECORDED NEAR-MISS, not a requirement. 'WCF ni ya mwajiri au mfanyakazi?' "
                  "is an incidence question the statement now ANSWERS, but no rate/method/"
                  "applicability cue is present so path 9 does not fire. Observed rather than "
                  "asserted, because widening for it needs its own sweep — and because an "
                  "answer-quality row must never be able to falsify a deploy verdict (R38).",
        "question": "WCF ni ya mwajiri au mfanyakazi?",
        "source": "ADVERSARIAL_MUST_STAY_NONE in sweep_statement_route_2026_10_09.py, entry 11",
        "observe": r"mwajiri",
        "local_intent_must_be": "none",
    },
]


def asserted(pattern, text):
    """Matches of `pattern` that are NOT preceded by a negation — mention vs assertion."""
    return [m.group(0) for m in re.finditer(pattern, text, re.I)
            if not re.search(NEGATED, text[max(0, m.start() - 24):m.start()], re.I)]


def ask(question, tok, timeout=600):
    req = urllib.request.Request(
        f"{ENDPOINT}?token={tok}",
        data=json.dumps({"message": question}).encode("utf-8"),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def token():
    p = os.path.expanduser("~/.chike_modal_token.txt")
    return (os.environ.get("CHIKE_MODAL_TOKEN")
            or (io.open(p, encoding="utf-8").read().strip() if os.path.exists(p) else ""))


def health(tok):
    try:
        with urllib.request.urlopen(f"{HEALTH}?deep=1&token={tok}", timeout=600) as r:
            h = json.loads(r.read().decode("utf-8"))
    except Exception as exc:                                                 # noqa: BLE001
        return {"error": f"{type(exc).__name__}: {str(exc)[:200]}"}
    served = h.get("served") or {}
    build = h.get("build") or ""
    is_ancestor = bool(build) and subprocess.run(
        ["git", "merge-base", "--is-ancestor", build, "HEAD"],
        cwd=REPO, capture_output=True).returncode == 0
    moved = [p for p in (_sh("git", "diff", "--name-only", f"{build}..HEAD", "--", *DEPLOY_PATHS)
                         .splitlines()) if p.strip()] if is_ancestor else []
    h["_checks"] = {
        "build_is_an_ancestor_of_head": is_ancestor,
        "no_serving_path_moved_since_the_build": not moved,
        "web_and_gpu_tiers_agree": h.get("build_matches") is True,
        "served_digest_equals_committed_index": (
            served.get("rag_facts_text_sha256") == EXPECTED_SHA256),
        "served_rows_equal_committed_rows": served.get("rag_rows_loaded") == EXPECTED_ROWS,
        "rows_match_config": served.get("rag_rows_loaded") == served.get(
            "config_rag_fact_count"),
    }
    h["_provenance"] = {
        "deployed_build": build, "head": HEAD, "serving_paths_moved_since_build": moved,
        "deploy_paths_watched": DEPLOY_PATHS,
        "_why_not_equality_to_head": (
            "committing this harness before running it (R18) moved HEAD one commit past the "
            "deploy, and an equality check called that a stale deploy. Ancestry plus a "
            "serving-path diff is the question that was actually meant: a doc or harness commit "
            "after a deploy is not staleness, and a changed chike/ file is."),
        "expected_sha256": EXPECTED_SHA256, "expected_rows": EXPECTED_ROWS,
        "_derived": "the digest is computed from the committed index, not typed, so there is no "
                    "pin here to go stale.",
    }
    return h


def _resume():
    """Rows already measured, by id. A long or live run writes after every row AND resumes, so a
    dropped link costs one row rather than the run (R16's structural fix, not a defensive one)."""
    if not os.path.exists(OUT):
        return {}
    try:
        prev = json.load(io.open(OUT, encoding="utf-8"))
    except Exception:                                                        # noqa: BLE001
        return {}
    return {r["id"]: r for r in prev.get("rows", []) if r.get("verdict") == "PASS"}


def save(rows, h):
    deploy_bad = [r for r in rows if r.get("limb") == "deploy"
                  and r.get("verdict") in ("FAIL", "ERROR")]
    hc = (h or {}).get("_checks") or {}
    payload = {
        "_what": "R16 live verification of the statement route (routing path 9 + the "
                 "orchestrator's threshold and optionality branches) and of index row 9's "
                 "rewording. Deployed build and HEAD are both recorded under health._provenance.",
        "_endpoint": ENDPOINT,
        "_what_this_cannot_see": (
            "the endpoint returns {'reply': text} only — no intent, no computation record. The "
            "live ROUTE is therefore established by (a) re-deriving detect_intent locally while "
            "asserting /health's build equals this tree's HEAD, and (b) route_evidence patterns "
            "taken from the engine's own emitted working, each asserted to match that working "
            "before any request is sent. Neither is the same claim as reading the route off the "
            "wire, and saying so is the point."),
        "_why_these_rows": (
            "three pinned must-move rows from the 0e11c3d closability classification; the two "
            "regressions the change itself introduced and that only an end-to-end run found; the "
            "over-breadth row V3 exists for; and the standard negatives — the compute path, both "
            "wired guards, a prior ship, and config loading."),
        "health": h,
        "local_intents": {p["id"]: routing.detect_intent(p["question"]) for p in PROBES},
        "engine_text": ENGINE_TEXT,
        "totals": {"probes": len(PROBES), "run": len(rows),
                   "pass": len([r for r in rows if r.get("verdict") == "PASS"]),
                   "fail": len([r for r in rows if r.get("verdict") == "FAIL"]),
                   "error": len([r for r in rows if r.get("verdict") == "ERROR"]),
                   "observed_only": len([r for r in rows
                                         if r.get("verdict") == "OBSERVED"])},
        "verdict": ("DEPLOY VERIFIED"
                    if (rows and not deploy_bad and len(rows) == len(PROBES)
                        and hc and all(hc.values()))
                    else "INCOMPLETE OR FAILED"),
        "answer_withheld_by_guard": [r["id"] for r in rows if r.get("answer_withheld")],
        "rows": rows,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with io.open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
    return payload


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:                                                        # noqa: BLE001
        pass

    tok = token()
    if not tok:
        print("NO TOKEN — cannot verify live. This is NOT a pass (R16).")
        return 2

    h = health(tok)
    print(f"[health] {json.dumps(h.get('_checks', h.get('error')), ensure_ascii=False)}")
    _pv = h.get("_provenance") or {}
    print(f"[health] deployed build={_pv.get('deployed_build')} head={HEAD}  "
          f"digest={EXPECTED_SHA256[:16]}… rows={EXPECTED_ROWS}")
    if _pv.get("serving_paths_moved_since_build"):
        print(f"[health] ⛔ serving paths moved since the build: "
              f"{_pv['serving_paths_moved_since_build']}")

    # The route claim, re-derived here before anything is asked.
    for p in PROBES:
        got = routing.detect_intent(p["question"])
        if "local_intent_must_be" in p:
            assert got == p["local_intent_must_be"], (
                f'{p["id"]}: detect_intent returned {got!r}, expected '
                f'{p["local_intent_must_be"]!r} — the route changed under this harness')
        p["_local_intent"] = got

    done = _resume()
    if done:
        print(f"[resume] {len(done)} row(s) already passed in a previous run: {sorted(done)}")

    rows = []
    for p in PROBES:
        if p["id"] in done:
            rows.append(done[p["id"]])
            save(rows, h)
            print(f"[resumed] {p['id']}")
            continue
        row = {k: p[k] for k in ("id", "limb", "pinned", "proves", "source", "question", "note",
                                 "baseline_committed_row", "_local_intent") if k in p}
        try:
            resp = ask(p["question"], tok)
            reply = str(resp.get("reply") or resp.get("answer") or resp)
            row["reply"] = reply
            checks = {}
            if p.get("must_match"):
                checks["must_match"] = bool(re.search(p["must_match"], reply, re.I))
            if p.get("must_not_match"):
                checks["must_not_match"] = not re.search(p["must_not_match"], reply, re.I)
            if p.get("must_not_assert"):
                bad = asserted(p["must_not_assert"], reply)
                checks["not_asserted"] = not bad
                if bad:
                    row["asserted_bad"] = bad
            if p.get("route_evidence"):
                pat = _EVIDENCE[p["route_evidence"]][0]
                row["route_evidence_seen"] = bool(re.search(pat, reply, re.I))
                row["route_evidence_pattern"] = pat
                # Positive evidence the DETERMINISTIC text reached the user. Recorded as a check
                # on deploy-limb rows, because that is the claim the change is making.
                checks["engine_text_reached_the_user"] = row["route_evidence_seen"]
            if p.get("observe"):
                row["observed"] = bool(re.search(p["observe"], reply, re.I))
            if p.get("withheld_signature"):
                row["answer_withheld"] = bool(
                    re.search(p["withheld_signature"], reply, re.I))
            row["checks"] = checks
            if p["limb"] == "answer_quality":
                row["verdict"] = "OBSERVED" if not checks else (
                    "PASS" if all(checks.values()) else "FAIL")
            else:
                row["verdict"] = "PASS" if all(checks.values()) else "FAIL"
        except Exception as exc:                                             # noqa: BLE001
            row["verdict"] = "ERROR"
            row["error"] = f"{type(exc).__name__}: {str(exc)[:200]}"
        rows.append(row)
        save(rows, h)                                   # after EVERY row, never once at the end
        print(f"[{row['verdict']:8s}] {row['id']:46s} intent={row.get('_local_intent')}")
        if row.get("reply"):
            print(f"           {' '.join(row['reply'].split())[:260]}")
        if row.get("checks"):
            print(f"           checks={row['checks']}")
        for k in ("asserted_bad", "error"):
            if row.get(k):
                print(f"           ⛔ {k}: {row[k]}")

    payload = save(rows, h)
    print(f"\n{payload['totals']}")
    for i in payload["answer_withheld_by_guard"]:
        print(f"  ANSWER WITHHELD BY GUARD (an A1 win; the A2 answer is still owed): {i}")
    print(f"artifact: {os.path.relpath(OUT, REPO)}")
    print(f"VERDICT: {payload['verdict']}")
    return 0 if payload["verdict"] == "DEPLOY VERIFIED" else 1


if __name__ == "__main__":
    sys.exit(main())
