# -*- coding: utf-8 -*-
"""RESTORE THE FOUR PHASE-2 OVER-REMOVALS, after reading each one WHOLE (2026-10-08).

Authorised by the founder on the same condition as the first three: re-read each row in
full first. Here that condition changed two verdicts, in both directions, which is the
argument for it.

⛔ AND THE RECORD-WIDE RE-READ THE FOUNDER ASKED FOR PRODUCED THE CLEANEST RESULT OF THE
WHOLE AUDIT. `paye_defect_quarantine_2026_08_25.jsonl`, 75 record lines, 22 DISTINCT bodies,
every one read individually:

        ADVERSARIAL rows:      4   correctly removed: 0   OVER-REMOVED: 4
        NON-adversarial rows: 18   correctly removed: 18  OVER-REMOVED: 0

    The presence-keyed sweep was right about EVERY row except the ones whose entire purpose
    is to contain the wrong value. 100% precision outside the adversarial subdomain, 0%
    inside it. That is not a bias to watch for -- it is a hard gate: a presence sweep must
    never remove a `pair_type: adversarial` / `subdomain: *_adversarial` row without a human
    reading it, because for that population containing the wrong value is the design.

    ⚠️ AND MY OWN FIRST READ OF THAT RECORD WAS WRONG, TWICE, FROM EXCERPTS. The two
    `out_of_corpus_refusal` rows (`b008_refusal_001`/`_002`) looked like over-removals: they
    refuse correctly and the 200-character excerpt contained no relief claim. Read WHOLE,
    both VOLUNTEER it after refusing -- "Ninajua viwango vya PAYE (... punguzo la kibinafsi
    TZS 26,000)" and "punguzo la kibinafsi la TZS 26,000/mwezi litapunguza kiasi". Removals
    correct. R34 again, on my own instrument's truncated output, in the session where I
    wrote R34 up twice.

WHAT THE FOUR RESTORED ROWS ARE, and note that THREE of them were removed for something
THE QUESTION said rather than something the answer claimed:

  b008_paye_adv_005 -- "Mfumo wa PAYE Tanzania una bendi ya kiwango cha sifuri kwa TZS
    270,000 za kwanza ... HAKUNA punguzo la kibinafsi tofauti la TZS 26,000 kwa mwezi."
    That is verbatim what CLAUDE.md s.11 says is correct. Removed for asserting it.

  b008_paye_adv_007 -- "TZS 1 x 8% = TZS 0.08 ... Kumbuka: HAKUNA punguzo la kibinafsi
    tofauti la TZS 26,000 kwa mwezi katika mfumo wa PAYE Tanzania." Band 2 at 8%, correct,
    plus an explicit denial of the phantom relief.

  the VAT_JULY2024 row -- removed for "dating the VAT 100M->200M increase to July 2024".
    ⛔ THE ANSWER DOES NOT CONTAIN THE DATE AT ALL; it is the QUESTION that says
    "ninaambiwa ni kuanzia Julai 2024". Verified: no match for `Julai\\s*2024` anywhere in
    the body. The sweep matched the `instruction` field. That is R36's first lesson --
    "MATCH ON THE ANSWER, NEVER THE QUESTION" -- inverted into a REMOVAL sweep, where it
    deletes instead of merely reporting.

  the tarehe-muafaka row -- removed for "asserting the 20th". The question asks "...ifikapo
    TAREHE 20?" and the answer pointedly declines to endorse it: "...endapo utashindwa
    kuwasilisha VAT withholding ifikapo TAREHE MUAFAKA." The answer is MORE careful than the
    question. Same shape as the "nilizolipia 250,000" row kept on 2026-10-08: the user's own
    figure is not the model's claim.

NOT RESTORED, deliberately: the 7-day VATWH row (removed for the wrong reason -- it does not
assert the 20th -- but still wrong, because FA2026 s.95 is 10 days, not 7) and
`stamp_duty_138` (a WEAK removal, repairable by striking one word, which is a corpus edit
rather than a restoration). Both are recorded, neither is quietly bundled in here.

WHERE IT GOES: the AUTHORED corpus, then `generate_sft.py` (R36's converse). `train_sft_
balanced.jsonl` appears in one row's provenance and is NOT restored -- it is not produced by
generate_sft.py and is not an authored source.

REPORT-ONLY by default; writes under --write.
"""
import json
import os
import re
import shutil
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(REPO, "eval", "results", "overremoval_restoration_phase2_2026_10_08.json")
WRITE = "--write" in sys.argv

PAYE_Q = "datasets/tier1a/rejected/paye_defect_quarantine_2026_08_25.jsonl"
TIER2_Q = "datasets/tier1a/rejected/tier2_confirmed_wrong_quarantine_2026_08_31.jsonl"
VATWH_Q = "datasets/tier1a/rejected/vat_withholding_deadline_stale_quarantine_2026_09_01.jsonl"

CP8 = "datasets/tier1a/cleaned_pairs/batch_008_cleaned.jsonl"
RS8 = "datasets/tier1a/raw_sources/raw_pairs_batch_008.jsonl"
SP14 = "datasets/tier1a/sft_shaped_pairs/cleaned_pairs_batch_014.jsonl"

RESTORATIONS = [
    {"key": "b008_paye_adv_005_20260612", "record": PAYE_Q, "to": [CP8, RS8],
     "why": "states there is NO separate TZS 26,000 personal relief, which is what CLAUDE.md "
            "s.11 says is correct, and was removed for asserting it. subdomain "
            "paye_adversarial."},
    {"key": "b008_paye_adv_007_20260612", "record": PAYE_Q, "to": [CP8, RS8],
     "why": "band 2 at 8% plus 'Kumbuka: HAKUNA punguzo la kibinafsi tofauti la TZS 26,000'. "
            "subdomain paye_adversarial."},
    {"key": "Hicho kiasi cha TZS 200M au TZS 100M", "record": TIER2_Q, "to": [SP14],
     "match_on": "body",
     "why": "removed for dating the increase to July 2024. THE ANSWER CONTAINS NO DATE; the "
            "QUESTION says 'ninaambiwa ni kuanzia Julai 2024'. The sweep matched the "
            "instruction field."},
    {"key": "tarehe muafaka", "record": VATWH_Q, "to": [SP14], "match_on": "body",
     "why": "removed for asserting the 20th. The QUESTION names the 20th; the answer says "
            "'tarehe muafaka' and declines to endorse it."},
]

# Read, and NOT restored. Recorded at the site so no later pass re-raises either (R20: "no
# action needed here" is a valid, recordable outcome).
READ_AND_NOT_RESTORED = [
    {"row": "the 7-day VATWH row (vat_withholding record, line 21)",
     "verdict": "removed for the WRONG REASON but STILL WRONG -- do not restore",
     "basis": "It does not assert the 20th: it contrasts them explicitly ('analipa TRA ndani "
              "ya siku 7 ... Hii ni tofauti na kuwasilisha VAT return ya kawaida (tarehe "
              "20)'). So the record's stated reason is not true of it. But 7 days is not "
              "right either -- FA2026 s.95 replaced VAT Act s.71(5) with TEN days after the "
              "end of the tax period, and 7 days is the general WHT deadline (`wht_deadline`) "
              "conflated with the VAT-withholding one. Restoring it would put a wrong figure "
              "back. The right fix is a new row teaching s.95."},
    {"row": "stamp_duty_138 (tier2 record, 4 lines)",
     "verdict": "WEAK removal -- repairable, not restorable as-is",
     "basis": "Its subject is first-time-buyer relief and its answer is correct (Tanzania has "
              "none). The 1% appears once in passing with no flatness claim, so the record's "
              "reason ('asserts a flat 1% stamp duty') is not true of it. But the word is "
              "still wrong, so restoring it verbatim re-imports a defect. Striking one word "
              "is a corpus EDIT and needs authorising as one."},
]


def load(record):
    rows = []
    with open(os.path.join(REPO, record), encoding="utf-8") as fh:
        for ln, line in enumerate(fh, 1):
            if line.strip():
                rows.append((ln, json.loads(line)))
    return rows


def body_of(o):
    for k in ("output", "answer_sw", "response"):
        if isinstance(o.get(k), str) and o[k].strip():
            return o[k]
    if isinstance(o.get("row"), dict):
        return body_of(o["row"])
    return ""


def q_of(o):
    for k in ("instruction", "question_sw", "question"):
        if isinstance(o.get(k), str) and o[k].strip():
            return o[k]
    if isinstance(o.get("row"), dict):
        return q_of(o["row"])
    return ""


def payload_of(o):
    """The row as AUTHORED. `_quarantine` is the removal's bookkeeping and must not travel
    back into the corpus: a restored row carrying it would be read by every later audit as
    still removed. Nested `row` shapes are unwrapped to the pair itself."""
    src = o["row"] if isinstance(o.get("row"), dict) else o
    drop = {"_quarantine", "row", "population", "adjudicated_at", "row_sha256",
            "quarantined", "removed_from", "excluded_false_positives", "source_file",
            "source_line_at_quarantine", "defect_class", "reason", "why", "adjudicated",
            "correct_value", "superseded_value_source", "originally_quarantined_in"}
    return {k: v for k, v in src.items() if k not in drop}


def main():
    results, planned = [], {}
    for spec in RESTORATIONS:
        rows = load(spec["record"])
        if spec.get("match_on") == "body":
            hits = [(ln, o) for ln, o in rows if spec["key"] in body_of(o)]
        else:
            hits = [(ln, o) for ln, o in rows
                    if (o.get("id") or (o.get("row") or {}).get("id")) == spec["key"]]
        assert hits, f"{spec['key']!r} not found in {spec['record']}"
        obj = payload_of(hits[0][1])
        body, q = body_of(hits[0][1]), q_of(hits[0][1])
        assert body and q, f"{spec['key']}: empty body or question after unwrapping"
        row = {"key": spec["key"], "record": spec["record"],
               "record_lines": [ln for ln, _ in hits], "why": spec["why"],
               "fields": sorted(obj.keys()), "to": [], }
        for rel in spec["to"]:
            dest = os.path.join(REPO, rel)
            assert os.path.exists(dest), f"missing destination {rel}"
            existing = [json.loads(l) for l in open(dest, encoding="utf-8") if l.strip()]
            dup = [i for i, e in enumerate(existing, 1)
                   if body_of(e).strip() == body.strip()]
            if dup:
                row["to"].append({"path": rel, "action": "SKIPPED -- already present",
                                  "at": dup})
            else:
                row["to"].append({"path": rel,
                                  "action": "RESTORE" if WRITE else "WOULD RESTORE"})
                planned.setdefault(dest, []).append(obj)
        results.append(row)
        print(f"[{'RESTORE' if WRITE else 'DRY-RUN'}] {spec['key'][:44]:44s} -> "
              f"{', '.join(os.path.basename(t['path']) for t in row['to'])}")

    if WRITE:
        for dest, objs in planned.items():
            shutil.copy2(dest, dest + ".pre_restore2_bak")
            with open(dest, "a", encoding="utf-8") as fh:
                for o in objs:
                    fh.write(json.dumps(o, ensure_ascii=False) + "\n")
            print(f"  appended {len(objs)} row(s) to {os.path.relpath(dest, REPO)}")

    payload = {
        "_what": "Restoration of the four over-removals found by the phase-2 audit.",
        "_authorised": "founder, 2026-10-08, conditional on reading each row whole",
        "_mode": "WRITE" if WRITE else "REPORT_ONLY",
        "_the_record_wide_reread": {
            "record": PAYE_Q,
            "record_lines": 75,
            "distinct_bodies": 22,
            "adversarial_rows": 4,
            "adversarial_over_removed": 4,
            "non_adversarial_rows": 18,
            "non_adversarial_over_removed": 0,
            "finding": "The sweep was right about EVERY row except the ones whose purpose is "
                       "to contain the wrong value. 100% precision outside the adversarial "
                       "subdomain, 0% inside it. A presence sweep must not remove an "
                       "adversarial row without a human reading it.",
            "my_own_error": "I first read b008_refusal_001/_002 as over-removals from a "
                            "200-character excerpt. Read WHOLE, both VOLUNTEER the phantom "
                            "relief after refusing correctly. Removals correct. R34 on my "
                            "own instrument's truncated output.",
        },
        "_three_of_four_were_removed_for_what_the_QUESTION_said": (
            "The VAT_JULY2024 answer contains no date at all (the question says 'ninaambiwa "
            "ni kuanzia Julai 2024'); the tarehe-muafaka answer declines to endorse the 20th "
            "the question names; and the two PAYE rows explicitly DENY the value. R36's first "
            "lesson -- match on the answer, never the question -- inverted into a REMOVAL "
            "sweep, where it deletes rather than merely reporting."),
        "_read_and_not_restored": READ_AND_NOT_RESTORED,
        "restorations": results,
        "totals": {"rows": len(RESTORATIONS),
                   "destinations": sum(len(r["to"]) for r in results),
                   "restored": sum(1 for r in results for t in r["to"]
                                   if t["action"].startswith("RESTORE")),
                   "skipped": sum(1 for r in results for t in r["to"]
                                  if "SKIPPED" in t["action"]),
                   "read_and_not_restored": len(READ_AND_NOT_RESTORED)},
    }
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
    print(f"\n{payload['totals']}")
    print(f"wrote {OUT}")
    if not WRITE:
        print("REPORT-ONLY. Re-run with --write to apply.")


if __name__ == "__main__":
    main()
