# -*- coding: utf-8 -*-
"""WHY DIDN'T THE CORRECTION-SYNC GATE CATCH ROW 63?

The gate exists to answer exactly this question for exactly this shape: a fact corrected in
locked_facts.json whose RAG-embedded text keeps serving the superseded value. `nssf_payment_
deadline` was corrected on 2026-09-02 (hedge -> s.14(1) "within one month after the end of the
month"); index row 63 kept serving "NSSF inalipwa ifikapo tarehe 10 ya mwezi unaofuata" -- the
10th -- until 2026-10-05. Every regen in between reported correction_sync=CLEAN.

THREE HYPOTHESES TO SEPARATE, each with a different fix:
  (a) the row comes from a DIFFERENT KEY, so the gate never associated it with this fact
  (b) the fact's own WRONG_PATTERNS never named the old value as the row actually phrased it
  (c) the gate is SOFT and a flag was read past

This does not reason about them. It reconstructs the PRE-FIX state from git -- the locked fact
as of eb12e70 and the deployed index as of 7d46df1 -- and runs the REAL
`check_facts_and_index` against it. If the gate reports CLEAN on the exact inputs it had, the
miss is reproduced rather than inferred, and each hypothesis can then be tested directly
against the same inputs.

R24: the reconstruction is asserted to reproduce the known historical state (row 63's exact
stale text, the fact's exact wrong_patterns) before any conclusion is drawn from it. A
diagnosis built on an arm that does not match what actually shipped is a diagnosis of
something we never ran.
"""
import importlib.util
import json
import os
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(REPO, "eval", "results", "correction_sync_miss_row63.json")

FACTS_SHA = "eb12e70"     # last commit before the Cap.50 amendments
INDEX_SHA = "7d46df1"     # the 184-row index that was deployed while row 63 was stale
KEY = "nssf_payment_deadline"
STALE_ROW_TEXT = "NSSF inalipwa ifikapo tarehe 10 ya mwezi unaofuata."


def git_show(sha, path):
    return subprocess.run(["git", "show", f"{sha}:{path}"], cwd=REPO,
                          capture_output=True, check=True).stdout.decode("utf-8")


def load_checker():
    """⛔ THE GATE MUST BE RECONSTRUCTED AT THE SAME SHA AS ITS INPUTS, AND THE FIRST VERSION
    OF THIS FUNCTION LOADED THE CURRENT ONE. That produced a confident WRONG answer:
    `nssf_payment_deadline` came back `unresolved`, which read as "the gate never associated
    the row with the key" -- hypothesis (a) SUPPORTED.

    It is unresolved only because `check_correction_sync` imports PINNED from
    `check_facts_index_sync`, and PINNED is a THIRD INPUT I had just edited hours earlier:
    the old pin needle was 'ifikapo tarehe 10' (which IS in the old index, so the key
    resolved), and the new one is 'ndani ya MWEZI MMOJA...' (which is NOT in the old index,
    so it does not). Pairing today's pin table with September's index describes a system that
    never existed.

    R24 again, and from the direction R24 explicitly warns about: I asserted that TWO inputs
    reproduced -- the index row and the fact's wrong_patterns -- and drew a conclusion about a
    THIRD I had not checked. "The baseline reproduces" is only as strong as the list of things
    it was checked against, and an unlisted input is where the error goes.

    Everything is now loaded from FACTS_SHA: the two checker modules, the facts and the index.
    """
    tmp = os.path.join(REPO, ".git", "diagnose_cs_tmp")
    os.makedirs(tmp, exist_ok=True)
    mods = {}
    # precompute_rag_embeddings too: check_facts_index_sync imports FACT_GROUPS and
    # CONCISE_BILINGUAL_FACTS from it, and those are part of the resolution path. A FOURTH
    # input, reconstructed at the same SHA for the same reason as the third.
    for name in ("precompute_rag_embeddings", "check_facts_index_sync",
                 "check_correction_sync"):
        src = git_show(FACTS_SHA, f"scripts/{name}.py")
        p = os.path.join(tmp, f"{name}.py")
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(src)
    if tmp not in sys.path:
        sys.path.insert(0, tmp)
    for name in ("precompute_rag_embeddings", "check_facts_index_sync",
                 "check_correction_sync"):
        sys.modules.pop(name, None)
        spec = importlib.util.spec_from_file_location(name, os.path.join(tmp, f"{name}.py"))
        mod = importlib.util.module_from_spec(spec)
        sys.modules[name] = mod
        spec.loader.exec_module(mod)
        mods[name] = mod
    return mods["check_correction_sync"], mods["check_facts_index_sync"]


def main():
    chk, sync = load_checker()
    locked = json.loads(git_show(FACTS_SHA, "scripts/locked_facts.json"))
    index = json.loads(git_show(INDEX_SHA, "kaggle/rag_facts_text.json"))

    # The THIRD input, asserted like the other two. The pin is what resolves a CONCISE row to
    # its key, so getting it from the wrong SHA silently changes which bucket the fact lands in.
    old_pin = sync.PINNED.get(KEY)
    assert old_pin == ("present_elsewhere", "ifikapo tarehe 10"), (
        f"PINNED[{KEY}] at {FACTS_SHA} is {old_pin!r}, not the historical pin. The "
        f"reconstruction is mixing SHAs and every bucket below would be unreliable.")
    print(f"reconstruction OK: PINNED[{KEY}] = {old_pin!r}  (the SEPTEMBER pin)")

    # --- R24: the reconstruction must match what actually shipped ---------------------------
    assert index[63] == STALE_ROW_TEXT, (
        f"reconstruction mismatch: index[63] at {INDEX_SHA} is {index[63]!r}, expected the "
        f"known stale text. Every conclusion below would be about a system we never ran.")
    fact = locked[KEY]
    wrong_patterns = fact.get("wrong_patterns") or []
    assert wrong_patterns, f"{KEY} had no wrong_patterns at {FACTS_SHA} -- re-check the SHA"
    print(f"reconstruction OK: index[63] = {index[63]!r}")
    print(f"                   {KEY}.wrong_patterns = {wrong_patterns}")
    print(f"                   has correction_note = {'correction_note' in fact}")

    # --- reproduce the miss with the REAL gate ----------------------------------------------
    ok, report = chk.check_facts_and_index(locked, index)
    buckets = {k: (len(v) if isinstance(v, list) else v) for k, v in report.items()}
    where = next((b for b, rows in report.items()
                  if isinstance(rows, list)
                  and any((r.get("key") if isinstance(r, dict) else r) == KEY for r in rows)),
                 None)
    print(f"\nREAL GATE on the real pre-fix inputs: ok={ok}  buckets={buckets}")
    print(f"{KEY} landed in bucket: {where!r}")

    # --- (a) is the row attributed to this key at all? --------------------------------------
    slugs = [f.split(":")[0].strip().lower() for f in index]
    resolved = chk.resolve_row_texts(KEY, index, slugs)
    hyp_a = {
        "hypothesis": "(a) the row comes from a different key, so the gate never associated it",
        "rows_resolved_for_the_key": resolved,
        "stale_row_among_them": STALE_ROW_TEXT in resolved,
        "verdict": ("REFUTED -- the gate resolved the key TO the stale row"
                    if STALE_ROW_TEXT in resolved else
                    "SUPPORTED -- the key did not resolve to the stale row"),
    }

    # --- (b) do the fact's own wrong_patterns match the stale text? -------------------------
    per_pattern = []
    for wp in wrong_patterns:
        m = re.search(wp, STALE_ROW_TEXT, re.I)
        per_pattern.append({
            "pattern": wp,
            "matches_the_stale_row": bool(m),
            "matched_text": m.group(0) if m else None,
        })
    hyp_b = {
        "hypothesis": "(b) wrong_patterns never named the old value AS THE ROW PHRASED IT",
        "per_pattern": per_pattern,
        "any_pattern_matches": any(p["matches_the_stale_row"] for p in per_pattern),
        "what_the_patterns_require": "the literal conjunction 'au' plus 'mwishoni/mwisho wa "
                                     "mwezi' -- i.e. the AMBIGUOUS '10th OR end of month' "
                                     "formulation",
        "what_the_row_actually_said": "'ifikapo tarehe 10 ya mwezi unaofuata' -- a BARE "
                                      "assertion of the 10th, with no 'au' and no mention of "
                                      "month-end at all",
        "verdict": ("REFUTED -- a pattern does match, so the gate had the signal"
                    if any(p["matches_the_stale_row"] for p in per_pattern) else
                    "SUPPORTED -- no pattern matches the text that was actually served"),
    }

    # --- (c) was it flagged and read past? --------------------------------------------------
    regen = open(os.path.join(REPO, "kaggle", "regenerate_rag_e5.py"), encoding="utf-8").read()
    blocking = re.search(r"CORRECTION_SYNC_BLOCKING\s*=\s*(\w+)", regen)
    hyp_c = {
        "hypothesis": "(c) the gate is soft and a flag was read past",
        "CORRECTION_SYNC_BLOCKING": blocking.group(1) if blocking else "not found",
        "key_was_flagged": where == "stale_wrong_pattern",
        "verdict": ("SUPPORTED -- it was flagged and the gate is non-blocking"
                    if where == "stale_wrong_pattern" else
                    "REFUTED -- the gate never flagged it, so softness is irrelevant to this "
                    "miss. Softness would only matter had there been a flag to ignore; the "
                    "gate reported CLEAN, which a BLOCKING posture would also have passed."),
    }

    payload = {
        "_question": "Why didn't the correction-sync gate catch index row 63?",
        "_method": "Reconstructed the PRE-FIX state from git (locked_facts @ eb12e70, deployed "
                   "index @ 7d46df1) and ran the REAL check_facts_and_index against it, with "
                   "the reconstruction asserted against the known stale row text first (R24).",
        "reconstruction": {
            "facts_sha": FACTS_SHA, "index_sha": INDEX_SHA,
            "index_row_63": index[63],
            "fact_had_correction_note": "correction_note" in fact,
            "fact_wrong_patterns": wrong_patterns,
        },
        "real_gate_verdict": {"ok": ok, "buckets": buckets, "key_bucket": where},
        "hypotheses": [hyp_a, hyp_b, hyp_c],
        "_answer": None,          # filled below
    }

    supported = [h["hypothesis"] for h in (hyp_a, hyp_b, hyp_c)
                 if h["verdict"].startswith("SUPPORTED")]
    payload["_answer"] = supported

    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)

    print()
    for h in (hyp_a, hyp_b, hyp_c):
        print(f"  {h['hypothesis']}\n      -> {h['verdict']}")
    print(f"\nSUPPORTED: {supported}")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
