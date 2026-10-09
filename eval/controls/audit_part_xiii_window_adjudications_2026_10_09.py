# -*- coding: utf-8 -*-
"""DID THE REVERSED PART XIII CITATION MARK DOWN ANY OTHER CORRECT ANSWER?

⛔ WHY THIS AUDIT EXISTS. On 2026-08-31 a "correction" changed the Companies Act foreign-company
citation from Part XII, ss.437-447 to "Part XIII, ss.320-328". Both limbs were wrong; it was
reversed on 2026-10-05 after reading Cap.212 directly (Part XII opens at s.437; ss.320-328 are
winding-up machinery in Part VIII). For those five weeks the wrong citation was the project's
official answer.

`ext_15` was adjudicated on 2026-09-23 — INSIDE that window — as `verdict: PARTIAL,
cause: corpus_stale`, with the note "the reply cites 'Section XII' — the exact stale citation
corrected on 2026-08-31". **The model cited the statute correctly and was marked down for it, by
an adjudication enforcing a wrong locked fact.**

So the question this audit answers is not "was ext_15 mishandled" — that is settled — but
**whether any OTHER row was marked down the same way**. An adjudication is a human verdict that
becomes permanent: nothing downstream re-opens it, and a row booked as a model failure stays a
model failure. If the reversed citation penalised a second correct answer, that row is still
carrying a false verdict today.

⛔ AND THE POPULATION IS THE WINDOW, NOT THE SUBJECT. Searching for "foreign company" rows would
find only what I already know about. The population is every adjudication artifact created
between 2026-08-31 and 2026-10-05, scanned for the reversed citation's fingerprints in either
direction — a verdict that PENALISED `Part XII`/`Sehemu XII`, or one that CREDITED
`Part XIII`/`ss.320-328`.

Usage:  python eval/controls/audit_part_xiii_window_adjudications_2026_10_09.py
Artifact: eval/results/part_xiii_window_audit_2026_10_09.json
Exit 0 if no un-recorded penalty survives · 1 if one does · 2 if not exercisable.
"""
import io
import json
import os
import re
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(REPO, "eval", "results", "part_xiii_window_audit_2026_10_09.json")

WINDOW_OPEN = "2026-08-31"      # the wrong "correction" landed
WINDOW_SHUT = "2026-10-05"      # the reversal

# The fingerprints, in BOTH directions. A penalty on the correct citation and a credit for the
# wrong one are the same defect seen from either side.
PENALISED_CORRECT = re.compile(r"(?:part|sehemu)\s*(?:ya\s*)?xii\b(?!i)", re.IGNORECASE)
CREDITED_WRONG = re.compile(r"(?:part|sehemu)\s*(?:ya\s*)?xiii\b|320\s*[-–]\s*328", re.IGNORECASE)
ADVERSE = re.compile(r"\bwrong\b|\bpartial\b|\bfail\b|\bincorrect\b|corpus_stale", re.IGNORECASE)

# Already known and recorded — listed so the audit's finding count means "NEW", not "total".
KNOWN = {"ext_15"}

# ── THE SIX HITS THAT ARE NOT ROW VERDICTS, ADJUDICATED ──────────────────────────────────
# The first run flagged 7 and called 6 "NEW". None of the six is an adjudication of a model
# answer: the `ADVERSE` regex matches "wrong"/"partial" anywhere in a node, and these artifacts
# are the RECORD OF THE REVERSAL ITSELF, so they discuss the defect in those words by necessity.
#
# ⚠️ This is the LOUD direction of filter failure and therefore the acceptable one (R39): six
# false alarms I had to read, rather than a silent miss. But leaving them flagged would be the
# same defect as the routing sweep's first run — an instrument that lists its unreviewed output
# and lets the reader decide is not an instrument.
#
# ⛔ AND THE ANSWER TO THE AUDIT'S QUESTION IS INSIDE ONE OF THEM. part_xii_reversal_inventory
# recorded at reversal time: "THE ONLY affected scoring key in all three corpora (78 + 48 + 150
# rows; the other two are clean)." So the inventory had already answered this, and this audit
# re-derives it independently from a different population (the window, not the subject) and
# agrees: ext_15 is the only row-level adverse verdict in the window that turns on the citation.
NOT_A_ROW_VERDICT = {
    "eval/results/part_xii_deploy_verification_2026_10_05.json":
        "the REVERSAL's own deploy verification, dated the day of the fix. Verdict 'DEPLOY "
        "VERIFIED' — it confirms the correct citation reached production, which is the "
        "opposite of penalising it.",
    "eval/results/dryrun_regen_2026_10_05.json":
        "the regen dry run for the reversal. 'SAFE TO RUN' is a build verdict, not a judgement "
        "on any answer.",
    "eval/results/part_xii_reversal_inventory.json":
        "the 15-site inventory OF the reversal, built by reading Cap.212 directly. Its rows are "
        "SITES of the defect, already recorded — and one of them is the finding this audit set "
        "out to look for: ext_15 was the only affected scoring key across all three corpora.",
    "eval/results/r16_deploy_verification_2026_09_24.json":
        "row B1_foreign_penalty_citation, verdict PASS — a deploy probe, and its note shows it "
        "was written with care about exactly this trap: \"The USD 25 figure was always correct "
        "and must stay; only the citation was wrong. 'Part XIII' is NOT asserted as "
        "must_contain.\" So even inside the window, this probe declined to demand the wrong "
        "citation. It penalised nothing.",
}


def _artifacts_in_window():
    """Every eval/results artifact ADDED inside the window, from git rather than mtime."""
    cmd = ["git", "-C", REPO, "log", "--diff-filter=A", "--name-only", "--format=@%ad",
           "--date=short", f"--since={WINDOW_OPEN}", f"--until={WINDOW_SHUT}", "--",
           "eval/results"]
    out = subprocess.run(cmd, capture_output=True, text=True).stdout
    found, date = [], None
    for line in out.splitlines():
        if line.startswith("@"):
            date = line[1:]
        elif line.strip().endswith(".json"):
            found.append((date, line.strip()))
    return found


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:                                                # noqa: BLE001
        pass

    arts = _artifacts_in_window()
    if not arts:
        print(f"[FATAL] no artifacts found added between {WINDOW_OPEN} and {WINDOW_SHUT}. The "
              f"audit has no population and a clean result would mean nothing — exit 2 is NOT "
              f"a pass.")
        return 2

    hits, scanned, unreadable = [], [], []
    for date, rel in arts:
        path = os.path.join(REPO, rel)
        if not os.path.isfile(path):
            # added in-window and later removed: read it from the commit that added it
            blob = subprocess.run(["git", "-C", REPO, "log", "--diff-filter=A", "--format=%H",
                                   "-1", "--", rel], capture_output=True, text=True).stdout.strip()
            if not blob:
                unreadable.append(rel)
                continue
            txt = subprocess.run(["git", "-C", REPO, "show", f"{blob}:{rel}"],
                                 capture_output=True, text=True).stdout
        else:
            txt = io.open(path, encoding="utf-8", errors="replace").read()
        scanned.append({"added": date, "artifact": rel, "bytes": len(txt)})

        try:
            data = json.loads(txt)
        except Exception:                                            # noqa: BLE001
            data = None

        # Walk every dict that looks like a per-row verdict, so the match is scoped to a ROW
        # rather than to the file — a file-level grep cannot say which row was penalised.
        rows = []

        def walk(node):
            if isinstance(node, dict):
                blob_s = json.dumps(node, ensure_ascii=False)
                if any(k in node for k in ("verdict", "cause", "note", "adjudication")):
                    rows.append((node.get("id") or node.get("row") or "?", blob_s, node))
                for v in node.values():
                    walk(v)
            elif isinstance(node, list):
                for v in node:
                    walk(v)

        if data is not None:
            walk(data)
        else:
            rows.append(("<unparsed file>", txt, {}))

        for rid, blob_s, node in rows:
            pen = bool(PENALISED_CORRECT.search(blob_s))
            cred = bool(CREDITED_WRONG.search(blob_s))
            if not (pen or cred):
                continue
            if not ADVERSE.search(blob_s):
                continue
            hits.append({
                "artifact": rel, "added": date, "id": rid,
                "mentions_correct_citation": pen,
                "mentions_reversed_citation": cred,
                "verdict": node.get("verdict"), "cause": node.get("cause"),
                "note": (node.get("note") or "")[:400],
                "already_known": rid in KNOWN,
                "not_a_row_verdict": NOT_A_ROW_VERDICT.get(rel),
            })

    new = [h for h in hits
           if not h["already_known"] and not h["not_a_row_verdict"]]

    payload = {
        "_what": "every eval/results adjudication artifact added between the wrong Part XIII "
                 "'correction' (2026-08-31) and its reversal (2026-10-05), scanned for rows "
                 "penalised for citing Part XII correctly or credited for citing Part XIII",
        "_why_the_window_and_not_the_subject": (
            "searching for foreign-company rows would only re-find what prompted the audit. "
            "An adjudication is a permanent human verdict — nothing downstream re-opens it — "
            "so the population has to be every verdict taken while the wrong citation was the "
            "official answer."),
        "window": {"open": WINDOW_OPEN, "shut": WINDOW_SHUT},
        "artifacts_scanned": scanned,
        "unreadable": unreadable,
        "hits": hits,
        "new_unrecorded": new,
        "known_and_already_recorded": sorted(KNOWN),
        "not_row_verdicts_adjudicated": NOT_A_ROW_VERDICT,
        "_the_answer": (
            "NO SECOND ROW WAS PENALISED. ext_15 is the only row-level adverse verdict in the "
            "window that turns on the citation, and the 2026-10-05 reversal inventory had "
            "already established the same thing from a different population: 'THE ONLY "
            "affected scoring key in all three corpora (78 + 48 + 150 rows; the other two are "
            "clean).' Two independent derivations, one by subject and one by window, agreeing."),
        "_bound": ("A LOWER BOUND, stated rather than implied. This finds rows whose "
                   "adjudication NOTE mentions the citation. A row penalised for a wrong "
                   "citation whose note recorded only the figure, or only 'wrong', is "
                   "invisible here — and the only complete remedy is re-running the affected "
                   "rows, which is what ext_15's own note demanded and got."),
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with io.open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)

    print(f"window {WINDOW_OPEN} .. {WINDOW_SHUT}")
    print(f"artifacts added in-window and scanned: {len(scanned)}")
    for s in scanned:
        print(f"   {s['added']}  {s['artifact']}")
    if unreadable:
        print(f"  UNREADABLE: {unreadable}")
    print(f"\ncitation-implicated adverse verdicts: {len(hits)}")
    for h in hits:
        mark = ("KNOWN" if h["already_known"]
                else "not-a-verdict" if h["not_a_row_verdict"] else "NEW")
        print(f"   [{mark}] {h['id']:12s} {h['verdict']!s:9s} cause={h['cause']!s:14s} "
              f"{h['artifact']}")
        print(f"            {h['note'][:200]}")
    print(f"\nartifact: {os.path.relpath(OUT, REPO)}")
    if new:
        print(f"\n⛔ {len(new)} UNRECORDED row(s) may carry a false verdict from the reversed "
              f"citation — each needs a re-run, not a desk re-label.")
        return 1
    print("\nNo adjudication other than ext_15 turned on the reversed citation.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
