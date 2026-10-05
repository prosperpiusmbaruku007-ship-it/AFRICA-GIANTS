# -*- coding: utf-8 -*-
"""DID THE WRONG NSSF FINE (TZS 100,000) PROPAGATE INTO TRAINING ROWS OR GOLD ANSWERS?

Ordered before quarantining anything: "a never-checked fact this wrong has usually propagated,
and every other correction this arc has had training rows asserting the old value. Report the
count before quarantining."

WHAT CHANGED THE DIAGNOSIS, and it changes what this sweep is looking for. The Cap.50 report
called `fine_limit` an ungrounded fact that nobody had ever checked. Reading the objects rather
than one field shows otherwise:

  fine_limit.source  = data/source_documents\\nssf\\nssf_act_cap50.pdf   <- REVISED EDITION 2015
  R.E.2015 s.72(1):  "a fine not exceeding ONE HUNDRED THOUSAND shillings ... two years"
  R.E.2023 s.76(1):  "a fine not exceeding TEN MILLION shillings ... two years"

So 100,000 is not an invention. It is a FAITHFUL TRANSCRIPTION OF A SUPERSEDED EDITION -- R29
mode 2 (OUT-OF-DATE), not mode 1 (UNTRACEABLE). That matters here because a transcription from a
real document tends to be quoted CONFIDENTLY and in the document's own words, which is the kind
of value that propagates; a fabrication tends to sit in one place.

NARROW BY CONSTRUCTION (R17 step 4), with the unbounded count reported beside it so the bound is
visible rather than implied. "100,000" is an everyday figure in this corpus -- PAYE band edges,
wages, turnover. A bare count would be noise. Rows are scored on three axes:
  - the figure (100,000 / 100000 / laki moja / one hundred thousand)
  - a penalty word  (faini | adhabu | fine | penalty | kifungo | imprisonment | offence | kosa)
  - an NSSF/Cap.50 word
and only rows carrying ALL THREE within one row are reported as candidates. Rows carrying the
figure and a penalty word but NO NSSF word are reported separately as NEAR -- not as hits, but
visible, because that is where a miss would hide if the Swahili says "shirika la hifadhi" rather
than "NSSF".
"""
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(REPO, "eval", "results", "nssf_fine_100k_propagation.json")

# ⚠️ THE NEGATIVE LOOKAHEAD IS LOAD-BEARING, and the first version of this sweep lacked it.
# `100[,.\s]?000` matches INSIDE `100,000,000` -- the VAT six-month registration threshold,
# which appears all over this corpus next to the word `adhabu`. Without `(?![,.\d])` the sweep
# reported VAT-threshold rows as NSSF-fine propagation: a substring collision of exactly the
# kind CLAUDE.md records three times in the OOC lists, arriving in a measurement instead.
FIGURE = re.compile(
    r"100[,.\s]?000(?![,.\d])|\blaki\s+moja\b|elfu\s+mia\s+moja|one\s+hundred\s+thousand", re.I)
PENALTY = re.compile(r"faini|adhabu|fine\b|penalt|kifungo|imprison|offence|kosa\b|jela", re.I)
NSSF = re.compile(r"\bnssf\b|hifadhi\s+ya\s+jamii|social\s+security|cap\.?\s*50", re.I)
# The two other levies that legitimately carry a TZS 100,000 penalty figure in this corpus, so
# a hit can be attributed rather than merely counted. OSHA's 100,000/day continuing-offence
# charge is CORRECT and must not be quarantined; it is the single largest source of noise here.
OTHER_SUBJECT = re.compile(r"\bosha\b|usalama\s+kazini|\bvat\b|\bbrela\b|\btra\b", re.I)

# Everything a training row or a gold answer could live in. Listed explicitly rather than
# globbed from the repo root so that a directory added later is a visible omission, not a
# silently-missing population (R20's mis-composed-fixture arrival point).
SEARCH_DIRS = [
    ("training", "datasets/tier1a/cleaned_pairs"),
    ("training", "datasets/tier1a/sft_shaped_pairs"),
    ("training", "datasets/tier1a/eval_set"),
    ("training", "datasets/tier1a/adversarial"),
    ("gold", "eval/accuracy_gate"),
    ("gold", "eval/refusal_gate"),
    ("gold", "eval/fidelity"),
    ("gold", "eval/routing"),
    ("gold", "eval/grounding"),
    ("index", "scripts"),          # locked_facts.json + precompute_rag_embeddings.py
    ("index", "kaggle"),           # rag_facts_text.json
    ("index", "chike-inference"),
]


# ADJUDICATION OF EACH HIT, keyed by file:line and asserted against what the sweep finds, so a
# changed hit set FAILS THE RUN rather than carrying a stale verdict forward -- the stale-pins
# lesson (CLAUDE.md R18 item 1), where human verdicts were pinned to positions that moved
# underneath them and kept asserting the old answer.
#
# R26's second half: a match is a candidate, not a defect. One of these five is a FALSE POSITIVE
# and quarantining it would have damaged a correct row.
ADJUDICATED = {
    "datasets/tier1a/sft_shaped_pairs/cleaned_pairs_batch_009.jsonl:216": {
        "verdict": "FALSE POSITIVE -- DO NOT QUARANTINE",
        "why": "The row is about the 5% LATE-PAYMENT penalty (s.14(3), confirmed correct) and "
               "uses TZS 100,000 as an ILLUSTRATIVE UNPAID CONTRIBUTION: '5% x 100,000 x 3 = "
               "TZS 15,000'. 100,000 is the base of a worked example, not a fine ceiling. The "
               "arithmetic is right and the rate is the statutory one.",
    },
    "datasets/tier1a/sft_shaped_pairs/cleaned_pairs_batch_014.jsonl:693": {
        "verdict": "GENUINE PROPAGATION",
        "why": "'Kifungu cha sheria kinasema faini ya shilingi elfu mia moja (TZS 100,000) "
               "inaweza kutozwa' -- asserts the superseded R.E.2015 ceiling as the current one, "
               "and attributes it to 'the section of the law' without naming one.",
    },
    "datasets/tier1a/sft_shaped_pairs/cleaned_pairs_batch_014.jsonl:694": {
        "verdict": "GENUINE PROPAGATION",
        "why": "Same superseded ceiling, framed as applying to compliance offences generally.",
    },
    "datasets/tier1a/sft_shaped_pairs/cleaned_pairs_batch_014.jsonl:695": {
        "verdict": "GENUINE PROPAGATION",
        "why": "Same superseded ceiling, framed inside the NSSF benefits system.",
    },
    "datasets/tier1a/sft_shaped_pairs/cleaned_pairs_batch_014.jsonl:696": {
        "verdict": "GENUINE PROPAGATION",
        "why": "Same superseded ceiling, with payment instructions built on top of it.",
    },
}


def _rows(path):
    """Yield (lineno, text) for jsonl / json / py alike -- the index text lives in a .py
    literal and in a .json array, and a sweep that only reads jsonl would miss both."""
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            if path.endswith(".jsonl"):
                for i, line in enumerate(fh, 1):
                    if line.strip():
                        yield i, line
            else:
                body = fh.read()
                for i, line in enumerate(body.splitlines(), 1):
                    yield i, line
    except OSError:
        return


def main():
    hits, near, production = [], [], []
    files_read = 0
    for kind, rel in SEARCH_DIRS:
        d = os.path.join(REPO, rel)
        if not os.path.isdir(d):
            print(f"  [absent] {rel}")
            continue
        for name in sorted(os.listdir(d)):
            if not name.endswith((".jsonl", ".json", ".py")):
                continue
            path = os.path.join(d, name)
            files_read += 1
            for lineno, text in _rows(path):
                if not FIGURE.search(text):
                    continue
                if not PENALTY.search(text):
                    continue
                flat = " ".join(text.split())
                # PROXIMITY, not mere co-occurrence. A 2,000-line SFT row can mention NSSF in
                # its system prompt and OSHA's 100,000/day in its answer; co-occurrence then
                # attributes OSHA's correct figure to NSSF. Attribute to whichever subject word
                # sits NEAREST the matched figure -- the same proximity discipline D-FIDELITY-6
                # uses, and for the same reason.
                fig = FIGURE.search(flat)
                window = flat[max(0, fig.start() - 220): fig.end() + 220]
                nssf_near = NSSF.search(window)
                other_near = OTHER_SUBJECT.search(window)
                rec = {"kind": kind, "file": f"{rel}/{name}", "line": lineno,
                       "figure_matched": fig.group(0),
                       "subject_in_window": ("nssf" if nssf_near else
                                             other_near.group(0).lower() if other_near
                                             else None),
                       "excerpt": flat[:400]}
                # ⚠️ THE SHIPPED INDEX NEEDS ITS OWN BUCKET, and the three-axis bound could
                # never have put it in `hits` -- which is R20's mis-composed-fixture shape in a
                # sweep. Index rows are terse `key: value` text by construction (see CLAUDE.md
                # R15's note on CONCISE_BILINGUAL_FACTS), so `fine limit: one hundred thousand
                # TZS` carries the figure and the word "fine" and NO SUBJECT WORD AT ALL. It
                # therefore scored NEAR -- filed next to ten correct OSHA rows -- while being
                # the single most consequential hit in the sweep, because it is LIVE: retrieved
                # and served to users now, not merely trained on once.
                if "rag_facts_text.json" in name and not other_near:
                    rec["why_production"] = (
                        "shipped RAG index text -- retrievable in production NOW. Subject-less "
                        "terse row, so the three-axis bound cannot see it; bucketed by FILE.")
                    production.append(rec)
                elif nssf_near and not other_near:
                    hits.append(rec)
                else:
                    near.append(rec)

    # The unbounded figure count, so the narrowing is auditable rather than asserted.
    bare = 0
    for kind, rel in SEARCH_DIRS:
        d = os.path.join(REPO, rel)
        if not os.path.isdir(d):
            continue
        for name in sorted(os.listdir(d)):
            if name.endswith((".jsonl", ".json", ".py")):
                for _, text in _rows(os.path.join(d, name)):
                    if FIGURE.search(text):
                        bare += 1

    # Attach the adjudication, and refuse to report from a stale one.
    found = {f"{h['file']}:{h['line']}" for h in hits}
    assert found == set(ADJUDICATED), (
        "the HIT set no longer matches the adjudicated set -- re-read each row before trusting "
        f"any verdict here.\n  new, unadjudicated: {sorted(found - set(ADJUDICATED))}\n"
        f"  adjudicated but gone: {sorted(set(ADJUDICATED) - found)}")
    for h in hits:
        h.update(ADJUDICATED[f"{h['file']}:{h['line']}"])
    genuine = [h for h in hits if h["verdict"] == "GENUINE PROPAGATION"]

    payload = {
        "_what": "Propagation sweep for the superseded NSSF fine ceiling (TZS 100,000, "
                 "R.E.2015 s.72(1)) now that R.E.2023 s.76(1) reads ten million shillings.",
        "_diagnosis": "R29 mode 2 (OUT-OF-DATE EDITION), not mode 1. fine_limit.source points "
                      "at a locally cached R.E.2015 PDF in which 100,000 is the correct text. "
                      "The fact is a faithful transcription of a superseded edition.",
        "_bound": "Three-axis match within one row: figure AND penalty word AND NSSF word. "
                  "NEAR = figure AND penalty but no NSSF word -- reported, not counted, since "
                  "that is where a Swahili paraphrase without the acronym would hide.",
        "files_read": files_read,
        "unbounded_figure_rows": bare,
        "totals": {"production_live_index_rows": len(production),
                   "candidates_matched": len(hits),
                   "genuine_propagation": len(genuine),
                   "false_positives_adjudicated_out": len(hits) - len(genuine),
                   "near_other_levy_mostly_correct_osha": len(near)},
        "production": production,
        "hits": hits,
        "near": near,
    }
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)

    print(f"\nfiles read                : {files_read}")
    print(f"rows containing the figure: {bare}  (unbounded -- noise, shown for the bound)")
    print(f"PRODUCTION (shipped index rows): {len(production)}")
    for h in production:
        print(f"\n  [LIVE] {h['file']}:{h['line']}\n         {h['excerpt'][:200]}")
    print(f"\nHITS  (figure+penalty+NSSF): {len(hits)}")
    print(f"NEAR  (figure+penalty, no NSSF word): {len(near)}")
    for h in hits:
        print(f"\n  [HIT ] {h['file']}:{h['line']}\n         {h['excerpt'][:300]}")
    for h in near[:12]:
        print(f"\n  [near] {h['file']}:{h['line']}\n         {h['excerpt'][:220]}")
    if len(near) > 12:
        print(f"\n  ... {len(near) - 12} more NEAR rows in the artifact")
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
