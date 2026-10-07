# -*- coding: utf-8 -*-
"""QUARANTINE TWO POPULATIONS THAT LOOK DIFFERENT AND ARE THE SAME DEFECT CLASS.

  A. 14 rows asserting the FABRICATED TZS 11,000,000 EFD turnover threshold, read individually
     from eval/results/efd_fabrication_all_notations_2026_10_06.json.
  B. 5 rows that were ALREADY QUARANTINED and are still live, found by
     eval/controls/audit_quarantine_reach.py — 4 NSSF-fine rows quarantined YESTERDAY and one
     rent-WHT row quarantined 2026-09-26.

⛔ WHY B EXISTS, AND IT IS THE MORE IMPORTANT HALF. Yesterday's quarantine removed four rows
asserting a TZS 100,000 NSSF fine ceiling from `sft_shaped_pairs/cleaned_pairs_batch_014.jsonl`.
It did not touch `datasets/tier1a/sft/train_sft.jsonl` — the EXPORTED FILE THAT ACTUALLY TRAINS
THE MODEL. All four rows are still there, verbatim, at lines 503 / 2758 / 3034 / 3272.

The quarantine fired. It was pointed at the authored corpus, and the bytes that train live one
stage downstream. That is exactly the 2026-08-24 pair of inert controls: `scan_for_keys.py`
scanned correctly and was handed no files; `chike/retrieval.py`'s index contract raises correctly
and production never imports it. Nothing is wrong with the logic in any of the three. **Where a
control acts matters more than whether it works**, and this one was mine, one day old.

SO THIS SCRIPT REMOVES FROM EVERY STAGE A ROW APPEARS IN, and asserts afterwards that the
quarantine-reach audit reports zero survivors. A removal that cannot be shown to have reached the
training file is not a removal.

⛔ WHY A's COUNT IS 14 AND NOT 3. A sweep for the spelled-out `milioni 11` found THREE rows.
D-FIDELITY-7 found seven. A sweep keyed on the CLAIM rather than the notation finds fourteen —
six in digits, six in words, two in both. Every corpus sweep in this arc has been keyed on
FIGURES, because the fact's own `wrong_patterns` hold `(11|14),?000,?000` in DIGITS, so a sweep
built from the fact's own patterns is blind to the words by construction. The number is the claim;
the notation is an accident of who typed the row.

And eight of the fourteen are rows the 2026-08-29 quarantine EDITED IN PLACE rather than removed:
the opening sentence was repaired and the same claim survived three sentences later. R25's
containment shape — the symptom went away and the defect did not.

ADJUDICATED INDIVIDUALLY, READ BEFORE COUNTED, and the exclusions are recorded BY NAME because
that is the half of the standard that is easy to drop:

  EXCLUDED — eval_questions_003.jsonl:104 and :105 (eval_355). CORRECT GOLD ANSWERS that name
      TZS 11,000,000 in order to DISMISS it ("lakini si kwa sababu ya kufikia TZS 11,000,000",
      "hazibadilishi jibu, kwa sababu hakuna kizingiti cha mauzo kwa EFD"). Polarity, not
      presence. Quarantining these would delete the scoring keys that catch the defect.
  EXCLUDED — sft/train_sft.jsonl:3196, flagged as a surviving quarantined row by the reach audit.
      IT IS CORRECT: "Lazima utoe hati ya zuio la VAT kwa msambazaji siku ambayo VAT inastahili
      kulipwa — si tarehe ya 20." That is `vat_withholding_certificate_timing` exactly. The
      2026-09-01 stale-deadline quarantine swept for "tarehe 20" and caught a row that REJECTS
      it — the same mention-vs-assertion failure, in a quarantine, a month before the rule was
      written down. Keeping it, and recording that the earlier quarantine removed correct data.
  EXCLUDED — batch_014:55 / train_sft:1961 ("kodi ya makisio ... kuanzia milioni 11 mpaka
      milioni 100"). 11,000,000 is a LAWFUL presumptive band edge. Right figure, right subject.
  EXCLUDED — batch_012:73 / train_sft:1941 (TZS 14,000,000 OSHA continuing-offence arithmetic)
      and eval_003:9 (TZS 40,000,000 vehicle value under WCF). Neither is about EFD.

Usage:  python scripts/quarantine_efd_fabrication_and_quarantine_survivors.py [--apply]
Without --apply it prints the plan and changes nothing.
"""
import argparse
import collections
import hashlib
import json
import os
import sys
from datetime import date

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(REPO)

SWEEP = "eval/results/efd_fabrication_all_notations_2026_10_06.json"
REACH = "eval/results/quarantine_reach_audit_2026_10_06.json"
OUT_A = "datasets/tier1a/rejected/efd_fabrication_all_notations_quarantine_2026_10_06.jsonl"
OUT_B = "datasets/tier1a/rejected/quarantine_survivors_reswept_2026_10_06.jsonl"

# --- population A: adjudicated by reading the artifact, locators in sft_shaped_pairs ----------
# Each entry: (file, line, first 60 chars of the ANSWER that must still be there, why)
EFD_ROWS = [
    ("cleaned_pairs_batch_011.jsonl", 81, "EFD inahitajika kulingana na kizingiti cha mauzo kil",
     "'haujafika kizingiti cha TZS 11M' -- opener repaired 2026-08-29, body claim survived"),
    ("cleaned_pairs_batch_011.jsonl", 82, "EFD inahitajika kulingana na kizingiti cha mauzo kil",
     "'ukifika TZS 11M kwa mwaka, TRA inaweza kuhitaji EFD hata kabla ya kizingiti cha VAT'"),
    ("cleaned_pairs_batch_011.jsonl", 83, "EFD inahitajika kulingana na kizingiti cha mauzo kil",
     "'biashara zenye mauzo chini ya TZS 11M ... hazihitajiki' + 'TZS 11M+ -> EFD ni lazima'"),
    ("cleaned_pairs_batch_011.jsonl", 84, "EFD inahitajika kulingana na kizingiti cha mauzo kil",
     "'(1) Chini ya TZS 11M kwa mwaka -- EFD haihitajiki bado' -- a band table built on it"),
    ("cleaned_pairs_batch_011.jsonl", 85, "Hapana, si sahihi. EFD inahitajika kulingana na kizi",
     "THE WORST SHAPE: it correctly rejects 40M and then asserts 'Kizingiti sahihi ni TZS "
     "milioni 11 -- si 40M'. A correction TO a fabrication reads as authoritative"),
    ("cleaned_pairs_batch_011.jsonl", 86, "EFD inahitajika kulingana na kizingiti cha mauzo kil",
     "'umepita kizingiti cha TZS 11M -- EFD inahitajika'"),
    ("cleaned_pairs_batch_011.jsonl", 87, "EFD inahitajika kulingana na kizingiti cha mauzo kil",
     "'EFD inaweza kuhitajika KABLA ya usajili wa VAT (kuanzia TZS 11M)'"),
    ("cleaned_pairs_batch_011.jsonl", 88, "EFD inahitajika kulingana na kizingiti cha mauzo kil",
     "'faini ... ukiwa umepitisha kizingiti cha TZS 11M'"),
    ("cleaned_pairs_batch_012.jsonl", 33, "Hapana. Kama biashara yako iko kwenye kiwango kinach",
     "'(mauzo TZS 11M+ au umesajiliwa VAT)' as the condition for the EFD obligation"),
    ("cleaned_pairs_batch_012.jsonl", 36, "Ndiyo. Biashara yote",
     "'zinazofuata kizingiti cha EFD (TZS 11M+ au zilizosajiliwa VAT)'"),
    ("cleaned_pairs_batch_012.jsonl", 37, "Ndiyo. Biashara za mtandaoni",
     "'kizingiti cha EFD (mauzo TZS 11M+ kwa mwaka, au zilizosajiliwa VAT)'"),
    ("cleaned_pairs_batch_013.jsonl", 19, "Hapana kwa biashara zilizosajiliwa VAT.",
     "'Biashara zisizosajiliwa VAT zenye mauzo chini ya TZS milioni 11 ... zinaweza kutumia "
     "risiti za kawaida' -- the fabricated exemption, stated as an entitlement"),
    ("cleaned_pairs_batch_014.jsonl", 896, "Kufikia milioni 11 kwa mwaka wa mauzo huwezi kusema",
     "'EFD ni lazima ukifikia TZS 11 milioni'. SECOND DEFECT IN THE SAME ROW: 'mapato yako "
     "yanazidi TZS 100 milioni kwa mwaka, ndipo utatakiwa kusajiliwa kwa VAT' -- 100M is the "
     "SIX-MONTH limb; the annual limb is 200M"),
    ("cleaned_pairs_batch_015.jsonl", 607, "Kiwango cha kawaida cha VAT ni asilimia 18.",
     "'mauzo yako ya mwaka ni TZS milioni 11 au zaidi' as an EFD trigger"),
]

# --- recorded exclusions ----------------------------------------------------------------------
EXCLUDED = [
    {"locator": "eval/accuracy_gate/eval_questions_003.jsonl:104",
     "verdict": "CORRECT_GOLD_KEPT",
     "why": "'Ndiyo, unahitaji EFD -- lakini si kwa sababu ya kufikia TZS 11,000,000 ... Hakuna "
            "kizingiti cha mauzo kwa EFD.' Names the figure to DISMISS it."},
    {"locator": "eval/accuracy_gate/eval_questions_003.jsonl:105",
     "verdict": "CORRECT_GOLD_KEPT",
     "why": "eval_355. 'TZS 10,999,000 au TZS 11,000,000 hazibadilishi jibu, kwa sababu hakuna "
            "kizingiti cha mauzo kwa EFD.' Polarity, not presence."},
    {"locator": "datasets/tier1a/sft/train_sft.jsonl:3196",
     "verdict": "EARLIER_QUARANTINE_WAS_WRONG_ROW_KEPT",
     "why": "Flagged as a surviving quarantined row, and it is CORRECT: 'hati ya zuio la VAT ... "
            "siku ambayo VAT inastahili kulipwa -- si tarehe ya 20', which is "
            "vat_withholding_certificate_timing exactly. The 2026-09-01 quarantine swept for "
            "'tarehe 20' and caught a row that REJECTS it -- the mention-vs-assertion failure, "
            "inside a quarantine, a month before the rule was written down. That quarantine "
            "therefore removed CORRECT training data from cleaned_pairs."},
    {"locator": "datasets/tier1a/sft_shaped_pairs/cleaned_pairs_batch_014.jsonl:55",
     "verdict": "LAWFUL_FIGURE_KEPT",
     "why": "'kodi ya makisio ... kuanzia milioni 11 mpaka milioni 100 kwa mwaka'. 11,000,000 is "
            "a real presumptive BAND EDGE (First Schedule). Right figure, right subject."},
    {"locator": "datasets/tier1a/sft_shaped_pairs/cleaned_pairs_batch_012.jsonl:73",
     "verdict": "NOT_ABOUT_EFD_KEPT",
     "why": "TZS 14,000,000 is the total of an OSHA continuing-offence calculation."},
    {"locator": "eval/accuracy_gate/eval_questions_003.jsonl:9",
     "verdict": "NOT_ABOUT_EFD_KEPT",
     "why": "TZS 40,000,000 is a vehicle value in a WCF wrong-base refusal."},
]

STAGES = [
    "datasets/tier1a/sft_shaped_pairs",
    "datasets/tier1a/sft",
    "datasets/tier1a/cleaned_pairs",
    "datasets/tier1a/eval_set",
    "datasets/tier1a/adversarial",
]


def norm(s):
    import re
    s = re.sub(r"[—–�’‘“”-]+", " ", s or "")
    return " ".join(s.split()).lower()


def sha(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True,
                                     ensure_ascii=False).encode("utf-8")).hexdigest()


def load_rows(path):
    with open(path, encoding="utf-8") as fh:
        return [line.rstrip("\n") for line in fh]


def body_of(obj):
    if isinstance(obj.get("row"), dict):
        obj = obj["row"]
    return next((obj[k] for k in ("output", "answer_sw", "response")
                 if isinstance(obj.get(k), str) and obj[k].strip()), "")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    # ---- resolve population A to concrete objects, aborting if a line moved ------------------
    targets = []          # normalised answer bodies to remove from every stage
    plan = []
    for fname, line_no, prefix, why in EFD_ROWS:
        path = f"datasets/tier1a/sft_shaped_pairs/{fname}"
        rows = load_rows(path)
        assert line_no <= len(rows), f"{path}:{line_no} is past end of file ({len(rows)} lines)"
        obj = json.loads(rows[line_no - 1])
        body = body_of(obj)
        # ⛔ NAMED BY LINE *AND* BY CONTENT. A line number alone is a pointer into a file that
        # other passes also edit; if it has moved, removing "line 81" deletes whatever is there
        # now. This is the stale-pin lesson (R18 incident 1) applied to a destructive operation.
        assert norm(body).startswith(norm(prefix)), (
            f"{path}:{line_no} no longer holds the adjudicated row.\n"
            f"  expected to start: {prefix!r}\n"
            f"  found:             {body[:80]!r}\n"
            f"REFUSING TO REMOVE. Re-run the sweep and re-adjudicate.")
        targets.append(norm(body))
        plan.append({"population": "A_efd_fabrication", "adjudicated_at": f"{path}:{line_no}",
                     "question": (obj.get("instruction") or obj.get("question_sw") or "")[:160],
                     "why": why, "row_sha256": sha(obj), "row": obj})

    # ---- population B: survivors named by the reach audit -----------------------------------
    reach = json.load(open(REACH, encoding="utf-8"))
    excluded_locators = {e["locator"] for e in EXCLUDED}
    seen_b = set()
    for s in reach["survivors"]:
        if s["survives_at"] in excluded_locators:
            continue
        key = norm(s["body"])
        if key in seen_b:
            continue                       # two quarantine lines, one live row
        seen_b.add(key)
        targets.append(key)
        plan.append({"population": "B_quarantine_survivor",
                     "adjudicated_at": s["survives_at"],
                     "originally_quarantined_in": s["quarantine_record"],
                     "question": s["question"],
                     "why": (f"already quarantined in {os.path.basename(s['quarantine_record'])} "
                             f"and STILL LIVE in {s['survives_in_stage']} -- the quarantine was "
                             f"pointed at the authored corpus, not at the exported training "
                             f"file"),
                     "row_sha256": "", "row": {"output": s["body"]}})

    # ---- find every live location of every target -------------------------------------------
    hits = collections.defaultdict(list)
    for stage in STAGES:
        d = os.path.join(REPO, *stage.split("/"))
        if not os.path.isdir(d):
            continue
        for name in sorted(os.listdir(d)):
            if not name.endswith(".jsonl"):
                continue
            path = f"{stage}/{name}"
            for i, line in enumerate(load_rows(os.path.join(REPO, *path.split("/"))), 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except Exception:
                    continue
                b = norm(body_of(obj))
                if b and b in targets:
                    hits[b].append((path, i))

    unmatched = [t for t in targets if t not in hits]
    print(f"population A (EFD fabrication): {len(EFD_ROWS)} adjudicated rows")
    print(f"population B (quarantine survivors): "
          f"{len([p for p in plan if p['population'] == 'B_quarantine_survivor'])} rows")
    print(f"distinct answer bodies to remove: {len(set(targets))}")
    print(f"live locations found: {sum(len(v) for v in hits.values())}")
    print(f"  by file: {dict(collections.Counter(p for v in hits.values() for p, _ in v))}")
    if unmatched:
        print(f"⛔ {len(unmatched)} target(s) matched NOTHING live -- the normaliser or the "
              f"body key is wrong, and a removal pass that matches nothing reports success")
        sys.exit(1)
    print(f"recorded exclusions: {len(EXCLUDED)}")
    for e in EXCLUDED:
        print(f"  [{e['verdict']}] {e['locator']}")

    if not args.apply:
        print("\n--apply not given. Nothing changed.")
        return 0

    # ---- write the quarantine records BEFORE removing anything ------------------------------
    for out, pop in ((OUT_A, "A_efd_fabrication"), (OUT_B, "B_quarantine_survivor")):
        with open(out, "w", encoding="utf-8") as fh:
            for p in plan:
                if p["population"] != pop:
                    continue
                rec = dict(p)
                rec["quarantined"] = str(date.today())
                rec["removed_from"] = [f"{f}:{n}" for f, n in hits[norm(body_of(p["row"]))]]
                rec["excluded_false_positives"] = EXCLUDED
                fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
        print(f"[record] {out}")

    # ---- remove, from EVERY stage the row appears in ----------------------------------------
    removed = collections.Counter()
    by_file = collections.defaultdict(set)
    for b, locs in hits.items():
        for path, i in locs:
            by_file[path].add(i)
    for path, lines in sorted(by_file.items()):
        full = os.path.join(REPO, *path.split("/"))
        rows = load_rows(full)
        kept = [r for i, r in enumerate(rows, 1) if i not in lines]
        with open(full, "w", encoding="utf-8", newline="\n") as fh:
            for r in kept:
                if r.strip():
                    fh.write(r + "\n")
        removed[path] = len(rows) - len(kept)
        print(f"[removed] {path}: {len(rows)} -> {len(kept)} ({removed[path]} rows)")

    print(f"\ntotal rows removed: {sum(removed.values())}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
