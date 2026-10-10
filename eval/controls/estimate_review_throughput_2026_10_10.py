# -*- coding: utf-8 -*-
r"""HOW LONG WOULD CLEARING THE SUPERVISED QUEUE ACTUALLY TAKE?

⛔ ASKED BEFORE RECRUITING, BECAUSE THE FOUNDER ASKED FOR IT BEFORE RECRUITING: "if clearing
it takes more than a few minutes a day for ten users, tell me before we recruit — a
supervision step that's too slow becomes rubber-stamping, and then it's the thing R7
forbids." That is the right test to apply and it is answerable now rather than after.

⚠️ THIS IS AN ESTIMATE WITH STATED ASSUMPTIONS, NOT A MEASUREMENT, AND THE DIFFERENCE IS
LOAD-BEARING (R22: name the population a number came from). What IS measured here:

  * REPLY LENGTH — read from this project's own stored replies, not guessed.
  * THE EDIT RATE — from the adjudicated Bar A figures: A2 ≈ 82%, so ~18% of in-scope
    answers are not usable as drafted. Measured on the gate corpus, which is OUR OWN
    authored population, so it is a LOWER bound on what real traffic will produce (R21/R33:
    42 of 42 OOC probes leak across two variation axes, and real users are not writing from
    our source families).

What is NOT measured, and cannot be offline:

  * MESSAGES PER USER PER DAY. There is no traffic data — that is the pilot's whole purpose.
    Three volumes are therefore reported, not one, and the decision should be read off the
    row that matches the cohort being proposed.
  * SECONDS PER DECISION. Modelled from reading speed plus a fixed check cost. The pilot
    measures this directly: `decision_latency_s` per item and `median_decision_latency_s` in
    review_summary(), which exist precisely so this estimate gets replaced by a number
    within the first week.

Usage:  python eval/controls/estimate_review_throughput_2026_10_10.py
Artifact: eval/results/review_throughput_estimate_2026_10_10.json
"""
import glob
import io
import json
import os
import statistics
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO)
OUT = os.path.join(REPO, "eval", "results",
                   "review_throughput_estimate_2026_10_10.json")

# ── the modelled costs, each with its reasoning in the open ─────────────────────────────
# Swahili prose read carefully by a fluent native reader. 180 wpm is an ordinary careful
# reading rate; this is NOT skimming, because skimming a compliance answer is the
# rubber-stamping the founder's own test is about.
WPM = 180.0
CHARS_PER_WORD = 6.0

# The fixed cost per item beyond reading the draft: open the card, read the question, glance
# at the engine working and the served facts, decide, tap. The review page is built to make
# this small — the evidence is on the same card, so there is no lookup — but it is not zero.
FIXED_CHECK_S = 25.0

# An EDIT costs far more than a send: the reviewer has to compose the correction in Swahili
# AND write the reason, and the reason is the field the whole mechanism exists to capture.
EDIT_EXTRA_S = 150.0

# Measured: A2 ≈ 82.3% of in-scope questions answered correctly (gate 0e11c3d, adjudicated).
# So ~18% of drafts need an edit or a withhold. Stated as a LOWER bound.
EDIT_RATE = 0.177

VOLUMES = [
    (10, 1, "ten employers, one question each per day — the quiet case"),
    (10, 2, "ten employers, two each — the planning case"),
    (10, 3, "ten employers, three each — a busy day, or the first week when the "
            "novelty is high"),
    (5, 2, "five employers, two each — the cohort that fits a 'few minutes a day' budget"),
    (3, 2, "three employers, two each — the cohort that fits comfortably"),
]


def _stored_reply_lengths():
    """Character counts of this project's own stored replies. Population named file by file
    so it is inspectable, per R22."""
    lengths, sources = [], {}
    for pat in ("eval/results/gate_*.json",
                "eval/results/targeted_route_verification_*.json"):
        for path in sorted(glob.glob(os.path.join(REPO, pat))):
            rel = os.path.relpath(path, REPO).replace("\\", "/")
            try:
                art = json.load(io.open(path, encoding="utf-8"))
            except Exception:                                        # noqa: BLE001
                continue
            found = 0
            for rows in (art.get("rows"), art.get("results"), art.get("generated")):
                if not isinstance(rows, list):
                    continue
                for r in rows:
                    if not isinstance(r, dict):
                        continue
                    text = r.get("generated") or r.get("reply") or r.get("answer")
                    if isinstance(text, str) and text.strip():
                        lengths.append(len(text))
                        found += 1
            if found:
                sources[rel] = found
    return lengths, sources


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:                                                # noqa: BLE001
        pass

    lengths, sources = _stored_reply_lengths()
    if not lengths:
        print("[FATAL] no stored replies found — the length input would be invented")
        return 2
    median = statistics.median(lengths)
    p90 = sorted(lengths)[int(0.9 * (len(lengths) - 1))]

    def read_s(chars):
        return (chars / CHARS_PER_WORD) / WPM * 60.0

    per_send = read_s(median) + FIXED_CHECK_S
    per_send_p90 = read_s(p90) + FIXED_CHECK_S
    per_edit = per_send + EDIT_EXTRA_S

    rows = []
    for users, per_user, note in VOLUMES:
        n = users * per_user
        edits = n * EDIT_RATE
        sends = n - edits
        total_s = sends * per_send + edits * per_edit
        total_p90 = sends * per_send_p90 + edits * (per_send_p90 + EDIT_EXTRA_S)
        rows.append({
            "users": users, "questions_per_user_per_day": per_user,
            "questions_per_day": n,
            "expected_edits_or_withholds_per_day": round(edits, 1),
            "minutes_per_day_median_length": round(total_s / 60.0, 1),
            "minutes_per_day_p90_length": round(total_p90 / 60.0, 1),
            "note": note,
        })

    verdict_row = rows[1]                                   # ten users, two each
    exceeds = verdict_row["minutes_per_day_median_length"] > 5.0

    art = {
        "_what": "Estimated daily cost of clearing the supervised review queue, asked "
                 "before recruiting because a supervision step that is too slow becomes "
                 "rubber-stamping.",
        "_measured_inputs": {
            "reply_length_chars": {
                "n": len(lengths), "median": median, "p90": p90,
                "sources": sources,
                "_why_this_population": "these are replies this system actually produced, "
                                        "so the reading cost is derived from real output "
                                        "length rather than an assumed one",
            },
            "edit_rate": {
                "value": EDIT_RATE,
                "derivation": "1 - A2 (0.823), gate 0e11c3d, hand-adjudicated",
                "_why_this_is_a_LOWER_bound": "A2 was measured on our own authored corpora, "
                                              "which share vocabulary and framing with our "
                                              "facts by construction (R21/R33). Real traffic "
                                              "is a different population and every time this "
                                              "project has measured one, the mechanism did "
                                              "worse on it — 1.9% vs 71% on the coverage "
                                              "gate, 42/42 OOC leaks across two axes.",
            },
        },
        "_modelled_inputs": {
            "words_per_minute": WPM, "chars_per_word": CHARS_PER_WORD,
            "fixed_check_seconds": FIXED_CHECK_S,
            "edit_extra_seconds": EDIT_EXTRA_S,
            "_not_measured": "seconds per decision is MODELLED, not measured. "
                             "decision_latency_s is recorded on every item and "
                             "review_summary() reports the median, so the pilot replaces "
                             "this estimate with a real number inside the first week.",
        },
        "seconds_per_decision": {
            "send_median_length": round(per_send, 1),
            "send_p90_length": round(per_send_p90, 1),
            "edit_median_length": round(per_edit, 1),
        },
        "rows": rows,
        "verdict": {
            "question_asked": "does clearing it take more than a few minutes a day for ten "
                              "users?",
            "answer": "YES" if exceeds else "NO",
            "at_ten_users_two_questions_each_minutes_per_day":
                verdict_row["minutes_per_day_median_length"],
            "_the_second_cost_no_estimate_captures": (
                "LATENCY, not minutes. A supervised answer cannot arrive faster than the "
                "reviewer, so a 9pm question waits until morning. That changes what the "
                "pilot MEASURES — a user who waits twelve hours for their first answer may "
                "simply stop asking, and the transcripts would then under-report demand "
                "rather than reveal it. The acks say a person is checking, which is honest, "
                "but honesty is not immediacy."),
        },
    }
    io.open(OUT, "w", encoding="utf-8").write(json.dumps(art, ensure_ascii=False, indent=1))

    print(f"reply length: n={len(lengths)} median={median} p90={p90} chars")
    print(f"per decision: send {per_send:.0f}s (p90 {per_send_p90:.0f}s) · "
          f"edit {per_edit:.0f}s")
    print(f"edit/withhold rate: {EDIT_RATE:.1%} (lower bound)\n")
    print(f"{'users':>6} {'q/user':>7} {'q/day':>6} {'edits':>6} {'min/day':>8} "
          f"{'min/day p90':>12}")
    for r in rows:
        print(f"{r['users']:>6} {r['questions_per_user_per_day']:>7} "
              f"{r['questions_per_day']:>6} "
              f"{r['expected_edits_or_withholds_per_day']:>6} "
              f"{r['minutes_per_day_median_length']:>8} "
              f"{r['minutes_per_day_p90_length']:>12}")
    print(f"\nVERDICT — more than a few minutes a day at ten users? "
          f"{art['verdict']['answer']} "
          f"({verdict_row['minutes_per_day_median_length']} min/day)")
    print(f"artifact: {os.path.relpath(OUT, REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
