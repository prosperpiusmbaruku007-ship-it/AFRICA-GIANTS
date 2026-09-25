# -*- coding: utf-8 -*-
"""v11: quarantine corpus rows asserting a 15% NON-RESIDENT withholding rate on rent.

Root cause: there is NO residency split for rent. Income Tax Act Cap.332 R.E.2023, First
Schedule para 4(b)(ii) names the non-resident limb explicitly and gives it the SAME ten
percent: "in the case of interest, rent or a commuted pension paid to a resident withholdee
or interest or rent paid to a non-resident withholdee - ten percent". TRA's own table agrees
(10% | 10% under headers 'Rate for Resident' / 'Rate for Non Resident'). Locked as
rent_wht_rate on 2026-09-26. Harness for the finding:
eval/sources/verify_rent_wht_residency_split.py.

The emblem row, tier1a_wh_009_20260603, cites primary_source_url
https://www.tra.go.tz/page/withholding-tax -- THE PAGE THAT CONTRADICTS IT. This is the
cited-and-contradicted shape: the citation is real, live, whitelisted and current, and every
provenance check passes it because the citation resolves.

WHY THIS ONE IS RISKIER THAN v10 AND IS BUILT DIFFERENTLY. v10 matched an exact instruction
string, so it could not over-match. This defect has no single phrasing -- it is a claim
spread across Swahili and English rows -- so detection is by pattern, and a pattern can
quarantine a CORRECT row. Three consequences, all deliberate:

  * DRY-RUN BY DEFAULT. Mutating 10 files requires --apply. Look at the target before
    overwriting it.
  * R17 PROBES, INCLUDING ONES THAT MUST COME BACK CLEAN. The probes that matter are the
    CORRECT bodies (a correct 15% for OTHER payments; a correct 10%/10% statement; a row
    that NEGATES the error). If the detector flags any of those it is over-broad and the
    run aborts. "Write the probes that should come back CLEAN, not just the ones that
    should flag."
  * NEGATION GUARDS. A row saying "si asilimia 15" is teaching the correction, not the
    defect, and must survive.

R18: committed before running. Artifact: eval/results/corpus_correction_v11.json
"""
import glob
import io
import json
import os
import re
import sys
from collections import defaultdict

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
QUARANTINE_PATH = os.path.join(REPO, "datasets", "tier1a", "rejected",
                               "rent_wht_nonresident_15pct_quarantine_2026_09_26.jsonl")
OUT = os.path.join(REPO, "eval", "results", "corpus_correction_v11.json")
DEFECT = "RENT_WHT_NONRESIDENT_15PCT"

_RENT = re.compile(r"\b(pango|rent)\w*", re.I)
_NONRES = re.compile(r"wasio wakazi|asiye mkazi|non.?residents?", re.I)
_FIFTEEN = re.compile(r"asilimia 15\b|\b15\s*%", re.I)
# A row that negates or corrects the error is teaching the fix, not the defect.
_NEGATION = re.compile(r"si asilimia 15|sio asilimia 15|not 15%|15% is wrong|si 15|"
                       r"asilimia 15 ni kosa|bila ubaguzi", re.I)

# Rows the PATTERN cannot reach, listed individually WITH the reason rather than by widening
# it -- R17 step 4 (prefer the narrowest form that closes the case) and R20 (record the
# judgement at the site so the next reader neither re-raises it nor re-widens the regex).
EXPLICIT_IDS = {
    # "...inayolipwa kwa mkazi Tanzania ni asilimia 10, si asilimia 15. Kwa asiye mkazi,
    # kiwango ni asilimia 15."  The defective assertion is in a clause that never repeats
    # the word 'pango' -- it inherits the rent subject from the preceding sentence. Reaching
    # it by pattern would mean matching non-resident+15 with NO rent term in the clause,
    # which flags the CORRECT service-fee (4(c)) and royalty (15% both) rows that the diff
    # confirmed are right. Narrow beats clever: one id, one reason.
    "tier1a_income_tax_adv_089_20260609":
        "asserts 'Kwa asiye mkazi, kiwango ni asilimia 15' for rent, in a clause carrying "
        "the rent subject only by anaphora from the previous sentence.",
}


def _text(obj):
    return " ".join(str(obj.get(k, "")) for k in
                    ("instruction", "output", "question_sw", "answer_sw",
                     "question_en", "answer_en", "response"))


def is_defect(obj):
    """True when the row ATTRIBUTES a 15% rate to NON-RESIDENT rent.

    CLAUSE-SCOPED, not proximity-scoped, and the difference is not cosmetic. The first
    version used a +/-120 character window and flagged a CORRECT body -- "For other payments
    to non-residents the rate is 15%; rent is separate at 10%" -- because `rent` sits twelve
    characters after the `15%`. Every token was present and the attribution was still wrong,
    which is the D-FIDELITY-6 lesson (a proximity rule cannot tell which levy owns a figure).
    Requiring all three in ONE clause separates them: there, clause 1 has non-resident+15 and
    no rent, clause 2 has rent and no 15. Found by an authored probe, not by the corpus.
    """
    if obj.get("id") in EXPLICIT_IDS:
        return True
    t = _text(obj)
    for clause in re.split(r"[.;!?\n]+", t):
        # Negation is judged PER CLAUSE, not over the whole row. tier1a_income_tax_adv_089
        # negates the wrong RESIDENT rate ("ni asilimia 10, si asilimia 15") and then asserts
        # the wrong NON-RESIDENT one in the next sentence. A whole-row negation guard reads
        # the first half and spares the second -- a correction and a defect in one body.
        if _NEGATION.search(clause):
            continue
        if _RENT.search(clause) and _NONRES.search(clause) and _FIFTEEN.search(clause):
            return True
    return False


# --- R17 probes. The CLEAN ones are the half that does the work. -----------------------
PROBES = [
    # must FLAG
    ({"answer_sw": "Kiwango cha kodi ya zuio ya pango la kibiashara ni asilimia 10 kwa "
                   "wakazi na asilimia 15 kwa wasio wakazi."}, True,
     "the exact corpus defect, Swahili"),
    ({"answer_en": "The withholding tax rate on commercial rent is 10% for residents and "
                   "15% for non-residents."}, True, "the exact corpus defect, English"),
    # must be CLEAN
    ({"answer_en": "Rent withholding is 10% for both residents and non-residents."}, False,
     "the CORRECT statement -- must survive"),
    ({"answer_sw": "Kodi ya zuio ya pango ni asilimia 10 kwa wakazi na wasio wakazi pia."},
     False, "the CORRECT statement in Swahili -- must survive"),
    ({"answer_en": "For other payments to non-residents the rate is 15%; rent is separate "
                   "at 10%."}, False,
     "a CORRECT 15% for the para 4(b)(iv) catch-all, in a reply that also mentions rent"),
    ({"answer_sw": "Si asilimia 15 kwa wasio wakazi kwenye pango -- ni asilimia 10."},
     False, "a row NEGATING the error -- teaching the fix, must survive"),
    ({"answer_en": "Service fees are 5% for a resident and 15% for a non-resident."},
     False, "a CORRECT residency split for a DIFFERENT payment type, no rent mention"),
    ({"answer_sw": "Ada za mkurugenzi ni asilimia 15 kwa wakazi na wasio wakazi."},
     False, "director fees 15% flat -- correct, and must not be swept in"),
    ({"answer_sw": "Kiwango cha WHT kwa royalties ni asilimia 15 kwa wakazi NA wasio "
                   "wakazi."}, False,
     "royalties 15% both -- matches locked royalties_wht_rate, must survive"),
    ({"answer_sw": "Ada za huduma za kiufundi zinazolipwa kwa mtu asiye mkazi ni asilimia "
                   "15."}, False,
     "service fees to a non-resident, para 4(c)(i) -- CORRECT, must survive"),
    ({"id": "tier1a_income_tax_adv_089_20260609",
      "answer_sw": "ni asilimia 10, si asilimia 15. Kwa asiye mkazi, kiwango ni asilimia 15."},
     True, "the anaphora row -- reached by EXPLICIT_IDS, not by pattern"),
]


def run_probes():
    failures = []
    for obj, expect, why in PROBES:
        got = is_defect(obj)
        if got != expect:
            failures.append({"probe": why, "expected_flag": expect, "got": got,
                             "text": _text(obj)[:160]})
    return failures


def main():
    apply = "--apply" in sys.argv

    probe_failures = run_probes()
    if probe_failures:
        print("ABORT: detector failed its own probes -- over-broad or under-broad.")
        for f in probe_failures:
            print("  ", json.dumps(f, ensure_ascii=False))
        return 2
    print(f"probes: {len(PROBES)}/{len(PROBES)} pass "
          f"({sum(1 for p in PROBES if not p[1])} of them must-be-CLEAN)")

    files = sorted(set(glob.glob(os.path.join(REPO, "datasets", "**", "*.jsonl"),
                                 recursive=True) +
                       glob.glob(os.path.join(REPO, "data", "**", "*.jsonl"),
                                 recursive=True)))
    quarantined, per_file = [], defaultdict(int)
    eval_set_hits = 0

    for fp in files:
        if "/rejected/" in fp.replace("\\", "/"):
            continue
        with io.open(fp, encoding="utf-8") as fh:
            lines = fh.readlines()
        kept, removed = [], 0
        for line in lines:
            s = line.rstrip("\n")
            if not s.strip():
                kept.append(line)
                continue
            try:
                obj = json.loads(s)
            except Exception:
                kept.append(line)
                continue
            if is_defect(obj):
                if obj.get("eval_set"):
                    eval_set_hits += 1
                quarantined.append({
                    "source_file": os.path.relpath(fp, REPO).replace("\\", "/"),
                    "defect_class": DEFECT,
                    "reason": ("asserts a 15% NON-RESIDENT rate on rent; Cap.332 First "
                               "Schedule para 4(b)(ii) gives the non-resident limb the same "
                               "TEN percent, and TRA's table reads 10%|10%."),
                    "row": obj})
                removed += 1
            else:
                kept.append(line)
        if removed:
            per_file[os.path.relpath(fp, REPO).replace("\\", "/")] = removed
            if apply:
                with io.open(fp, "w", encoding="utf-8", newline="\n") as fh:
                    fh.writelines(kept)

    report = {"measured": "2026-09-26", "harness": "scripts/correct_corpus_defects_v11.py",
              "defect_class": DEFECT, "mode": "APPLIED" if apply else "DRY_RUN",
              "probes_passed": len(PROBES), "rows_matched": len(quarantined),
              "rows_in_eval_set": eval_set_hits, "per_file": dict(per_file),
              "locked_fact": "rent_wht_rate (added 2026-09-26)",
              "quarantine_file": os.path.relpath(QUARANTINE_PATH, REPO).replace("\\", "/")}

    if apply and quarantined:
        os.makedirs(os.path.dirname(QUARANTINE_PATH), exist_ok=True)
        with io.open(QUARANTINE_PATH, "w", encoding="utf-8") as fh:
            for row in quarantined:
                fh.write(json.dumps(row, ensure_ascii=False) + "\n")
        remaining = 0
        for fp in files:
            if "/rejected/" in fp.replace("\\", "/"):
                continue
            with io.open(fp, encoding="utf-8") as fh:
                for line in fh:
                    if line.strip():
                        try:
                            if is_defect(json.loads(line)):
                                remaining += 1
                        except Exception:
                            pass
        report["remaining_live_after_fix"] = remaining

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(report, io.open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if not apply:
        print("\nDRY RUN -- nothing written. Re-run with --apply to quarantine.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
