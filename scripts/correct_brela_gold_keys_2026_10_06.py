# -*- coding: utf-8 -*-
"""CORRECT THE GOLD ROWS THAT SCORE AGAINST THE SUPERSEDED BRELA FEE SCHEDULE.

⛔ WHY THIS RUNS IN THE SAME COMMIT AS THE FACT AMENDMENTS AND NOT AFTER.

A fact, its index row and its gold row have to move together. Split across cycles, each half is
wrong in a different direction and both are confusing:

  fact moved, gold not  -> the gate marks a CORRECT answer wrong. `ext_15` was scored PASS on
                           `USD 25`; with the fact corrected and the key untouched, a model that
                           now answers TZS 70,000 fails for being right.
  gold moved, index not -> the gate marks a wrong answer wrong for the right reason, while
                           production keeps serving the old figure to actual users.

So the index rows (precompute_rag_embeddings.py group passages), the facts
(scripts/amend_brela_fees_2026_10_06.py) and these keys all land in one R15 cycle.

THREE ROWS, AND THEY NEED THREE DIFFERENT TREATMENTS -- which is the point of doing this by hand
rather than by substitution:

  eval_383  THE GOLD ANSWER IS NOW OUTRIGHT WRONG. "Ada ya kusajili kampuni isiyo na mtaji wa
            hisa ni TZS 300,000" -- BRELA's page says 500,000 (item 2). A wrong gold answer is
            worse than a wrong training row: it REWARDS the defect, so a model that answers
            correctly is scored as failing, and the error is invisible because the gate goes
            green either way. Corrected.
  ext_15    THE KEY IS STALE, THE VERDICT IS NOT RE-LABELLED. Its 2026-10-05 note already
            recorded that the verdict "now rests on the figure alone" after the citation limb was
            settled in the model's favour. The figure limb is now resolved too -- TZS 70,000 from
            a dated, hashed capture. That does NOT let anyone flip the recorded verdict from a
            desk: the reply was adjudicated against a key that has since changed, so the only
            honest state is RE-RUN REQUIRED. Re-labelling without re-running would be the same
            move as the 2026-08-31 "correction" that reversed Part XII on reconstruction rather
            than on a read.
  nat_33    THE GOLD ANSWER IS STILL CORRECT AND ITS DISTRACTOR IS NOT. The local-company
            penalty (TZS 2,500/month, 7 x 2,500 = 17,500) is unchanged; only the
            "WRONG = the USD 25/month foreign rate" clause is stale. ⚠️ AND THE NEW DISTRACTOR IS
            HARDER: the foreign rate is now TZS 70,000, so both the right and the wrong figure
            are in shillings. The old distractor announced itself by its currency.

Usage:  python scripts/correct_brela_gold_keys_2026_10_06.py [--apply]
"""
import argparse
import io
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(REPO)

CAPTURE = ("data/source_documents/brela/brela_ada_kampuni_20261006T140442Z.html "
           "(sha256 8d5543ac68eb4d3dc72fd1762dc7cc9c037870df65ac33f3654eb3c11c73b52c, "
           "fetched 2026-10-06T14:04:42Z)")

EDITS = [
    {
        "file": "eval/accuracy_gate/eval_questions_003.jsonl",
        "id": "eval_383",
        "must_currently_contain": {"correct_answer_sw": "TZS 300,000"},
        "set": {
            "correct_answer_sw": ("Ada ya kusajili kampuni isiyo na mtaji wa hisa ni TZS 500,000. "
                                  "Thibitisha na BRELA (brela.go.tz)."),
        },
        "add": {
            "_scoring_key_correction": {
                "date": "2026-10-06",
                "what_changed": "TZS 300,000 -> TZS 500,000.",
                "basis": (
                    "BRELA's own published fee schedule, item 2: 'Usajili wa Kampuni ambayo "
                    f"haina mtaji wa hisa 500,000/='. Read from {CAPTURE}. The June capture "
                    "(brela_ada_kampuni_v2.html, sha256 cb1353fc...) says 300,000, so this is a "
                    "SUPERSESSION (R29 mode 3), not a misreading."),
                "severity": (
                    "THIS KEY WAS OUTRIGHT WRONG, which is worse than a wrong training row. A "
                    "wrong gold answer REWARDS the defect: a model answering TZS 500,000 "
                    "correctly would have been scored as failing, and nothing in a green gate "
                    "would have said so."),
                "also_resolves": (
                    "CLAUDE.md Section 11 recorded this as 'DISPUTED -- the same BRELA fee page "
                    "item 2 reads TZS 500,000', treating two readings of a living page as an "
                    "accuracy problem. It was a DATE problem: June says 300,000, October says "
                    "500,000, both read correctly."),
            },
        },
    },
    {
        "file": "eval/accuracy_gate/edge_probe_extended_078_DRAFT.jsonl",
        "id": "ext_15",
        "must_currently_contain": {"expected_behavior": "USD 25 per month"},
        "set": {
            "expected_behavior": (
                "Yes -- a foreign company's late-filing penalty is TZS 70,000 per month or part "
                "month (BRELA fee schedule item 15(iv), as at 2026-10-06; Companies Act Cap.212 "
                "R.E. 2023, Part XII, ss.437-447), NOT the TZS 2,500/month local-company rate. "
                "⚠️ BOTH FIGURES ARE NOW IN SHILLINGS: until 2026 the foreign rate was USD 25, "
                "and the currency itself used to mark the distinction."),
        },
        "add": {
            "_scoring_key_correction_2": {
                "date": "2026-10-06",
                "what_changed": "FIGURE: 'USD 25 per month' -> 'TZS 70,000 per month or part "
                                "month'. The citation limb is unchanged from the 2026-10-05 fix.",
                "basis": (
                    "BRELA's own published fee schedule, item 15(iv): 'Kwa kutowasilisha au "
                    "kuchelewesha kuwasilisha hati yoyote inayotakiwa kuwasilishwa kwa Msajili, "
                    f"kwa kila mwezi au sehemu ya mwezi wa kuchelewa. 70,000/='. Read from "
                    f"{CAPTURE}."),
                "closes_what_the_2026_10_05_note_left_open": (
                    "That note recorded the verdict as resting on the FIGURE alone, the figure "
                    "being unresolved because the Act delegates every fee to Minister's "
                    "regulations (s.458, s.489(3)) and the Fees Regulations were not located. "
                    "The figure is now resolved at PORTAL tier from a dated, hashed capture. The "
                    "Regulations remain unlocated and remain the statute-tier target "
                    "(_unresolved_items.brela_companies_fees_regulations)."),
                "verdict": "RE_RUN_REQUIRED",
                "why_not_simply_flipped": (
                    "⛔ THE RECORDED VERDICT IS NOT RE-LABELLED FROM A DESK. This row's reply was "
                    "adjudicated against a key that has since changed, so neither 'still wrong' "
                    "nor 'actually right' is supportable without asking the question again. "
                    "Re-labelling on reconstruction is exactly the move that produced the "
                    "2026-08-31 Part XII reversal -- a confident correction that was itself the "
                    "error. And a reply that said USD 25 was CORRECT AS AT ITS OWN DATE, which "
                    "is a third possibility neither label expresses."),
            },
        },
    },
    {
        "file": "eval/accuracy_gate/edge_probe_natural_048.jsonl",
        "id": "nat_33",
        "must_currently_contain": {"expected_behavior": "USD 25/month foreign-company rate"},
        "set": {
            "expected_behavior": (
                "BRELA annual return fee TZS 22,000; late-filing penalty TZS 2,500 per month (or "
                "part month) for a local company -> 7 x 2,500 = TZS 17,500. WRONG = the foreign-"
                "company rate (TZS 70,000/month as at 2026-10-06, USD 25/month before that), or "
                "an invented figure."),
        },
        "add": {
            "_scoring_key_correction": {
                "date": "2026-10-06",
                "what_changed": ("THE DISTRACTOR, NOT THE ANSWER. The gold answer is unchanged -- "
                                 "the local-company penalty TZS 2,500/month did not move (item 6 "
                                 "in both captures). Only the 'WRONG = ...' clause named the "
                                 "superseded USD 25 foreign rate."),
                "basis": f"BRELA fee schedule items 6 and 15(iv), read from {CAPTURE}.",
                "the_row_got_harder": (
                    "⚠️ WORTH KNOWING BEFORE READING ANY FUTURE RESULT ON THIS ROW: the foreign "
                    "rate is now TZS 70,000, so the correct figure and the distractor are both "
                    "in shillings. The old distractor announced itself by its CURRENCY -- a "
                    "reply saying 'USD 25' to a local-company question was visibly reaching for "
                    "the wrong row. 'TZS 70,000' is not visibly anything. A drop on this row "
                    "after this change is not necessarily a regression in the model."),
            },
        },
    },
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    planned = 0
    for edit in EDITS:
        path = os.path.join(REPO, *edit["file"].split("/"))
        lines = io.open(path, encoding="utf-8").read().splitlines()
        hit = None
        for i, line in enumerate(lines):
            if not line.strip():
                continue
            obj = json.loads(line)
            if obj.get("id") == edit["id"]:
                hit = (i, obj)
                break
        assert hit, f"{edit['id']} not found in {edit['file']} -- refusing to guess"
        i, obj = hit

        # ⛔ NAMED BY ID *AND* BY CURRENT CONTENT. A gold row edited by id alone would silently
        # rewrite a row somebody else had already corrected, and the stale-pin lesson is that a
        # pointer with no content check decays invisibly.
        for field, needle in edit["must_currently_contain"].items():
            assert needle in str(obj.get(field, "")), (
                f"{edit['id']}.{field} no longer contains {needle!r} -- it reads "
                f"{str(obj.get(field))[:120]!r}. Somebody has already changed this row; "
                f"REFUSING TO EDIT. Re-read it and re-adjudicate.")

        print(f"{edit['file']}:{i + 1}  {edit['id']}")
        for field, value in edit["set"].items():
            print(f"   {field}:")
            print(f"     - {str(obj.get(field))[:150]}")
            print(f"     + {str(value)[:150]}")
            obj[field] = value
        for field, value in edit["add"].items():
            assert field not in obj, f"{edit['id']} already has {field}"
            obj[field] = value
            print(f"   + {field} (provenance block)")
        planned += 1

        if args.apply:
            lines[i] = json.dumps(obj, ensure_ascii=False)
            with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
                fh.write("\n".join(lines) + "\n")

    print(f"\n{planned} gold row(s) {'CORRECTED' if args.apply else 'planned (dry run)'}")
    if not args.apply:
        print("--apply not given. Nothing changed.")


if __name__ == "__main__":
    main()
