"""Does the claimed 'five-fact fabricated-section family (s.19-s.32)' exist? Measured: NO.

WHY THIS RUN EXISTS. An instruction was given to correct five facts to the hedge shape on the
grounds that they cite ss.19-32 of a statute "whose numbering ends at 18 and which has no
amending instrument", and that all five carried fabricated, citation-shaped sources. Acting on
that would REPLACE VERBATIM-VERIFIED STATUTORY TEXT WITH "WE DO NOT KNOW", so it is checked
against primary legislation first, exactly as R28 requires of any correction candidate -- "a
pass that only ever edits never earns the confidence to also NOT edit when the evidence says
not to."

THE EVIDENCE SAYS NOT TO, on every limb:

  * The s.19 references are the VETA Act (Vocational Education and Training Act) Cap.82 s.19(1)
    SDL EXEMPTION CATEGORIES. There are 11 such facts, not 5.
  * Cap.82 s.19 EXISTS. Proven not from our own corpus but from the enacted Finance Act 2026
    (Act No.2 of 2026), Part XXVII s.98, fetched from tra.go.tz: "The principal Act is amended
    in section 19(1) by deleting the words 'by the Government' appearing in paragraph (a) and
    substituting for them the words 'through Government subvention'." Parliament cannot amend
    a section that does not exist.
  * "No amending instrument" is false twice over: FA2026 s.98 is one, and the corpus already
    tracks FA2024 s.112 as another. Both amend s.19 specifically.
  * The amendment's substituted wording -- "through Government subvention" -- appears VERBATIM
    in exemption_category_government_departments' recorded fact text. The corpus is not merely
    defensible here; it is current to the most recent Finance Act.
  * These facts carry `verified_by` records of direct reads dated 2026-09-02, with verbatim
    paragraph quotes ("(h) local government authority;"). They are among the best-evidenced
    facts in the corpus, which is the opposite of the property alleged.

WHY THIS IS WORTH A COMMITTED HARNESS AND NOT A REPLY. R26's second half: an audit's false
positives cost more than its false negatives, because only false positives generate edits. A
missed defect leaves the system where it was; a fabricated defect gets ACTED ON, and here the
action was to hedge eleven correct, primary-sourced statutory facts. The instruction to "hedge"
sounds conservative and is not: on a verified fact, a hedge is a REGRESSION that withdraws a
correct answer a user would otherwise get.

ALSO CHECKED AND ABSENT: `_infer_sector_for_licence`. No such function, and no `infer_sector`
of any name, exists anywhere in the package -- so the described dispatcher-collapse finding has
no site. The general shape it describes (a correct extractor whose value is collapsed
downstream) is real and worth watching; it simply is not instantiated here, and a rule should
not be written from an instance that does not exist (the 42/42 correction of 2026-09-25 is the
precedent).

Usage:  python eval/sources/verify_s19_family_claim.py
"""

import json
import os
import re
import subprocess
import sys
from datetime import date

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(REPO, "eval", "results", "s19_family_claim_2026_09_26.json")
FA2026 = "https://www.tra.go.tz/images/uploads/acts/THE_FINANCE_ACT%2C_2026.pdf"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")

# The verbatim amending text. If the Act stops containing this, the run FAILS rather than
# reporting a verdict from a document that changed underneath it (R24).
AMEND_NEEDLE = "amended in section 19(1) by deleting the words"


def main():
    art = {"measured": str(date.today()),
           "harness": "eval/sources/verify_s19_family_claim.py",
           "claim_under_test": ("five facts cite ss.19-32 of a statute whose numbering ends at "
                                "18 and which has no amending instrument; all five fabricated"),
           "action_the_claim_requested": "correct all five to the hedge shape"}

    facts = json.load(open(os.path.join(REPO, "scripts", "locked_facts.json"), encoding="utf-8"))
    real = {k: v for k, v in facts.items() if not k.startswith("_")}

    fam = {}
    for k, v in real.items():
        blob = json.dumps(v, ensure_ascii=False)
        if re.search(r"Cap\.?\s*82\b", blob) and re.search(r"s\.?\s*19\b|section 19", blob):
            fam[k] = {"has_verified_by": bool(v.get("verified_by")) if isinstance(v, dict) else False,
                      "verified_as_at": v.get("verified_as_at") if isinstance(v, dict) else None,
                      "primary_source": (v.get("primary_source") or "")[:150]
                      if isinstance(v, dict) else None}
    art["veta_cap82_s19_facts"] = fam
    art["family_size_actual"] = len(fam)
    art["family_size_claimed"] = 5
    art["with_verification_record"] = sum(1 for f in fam.values() if f["has_verified_by"])

    # Independent proof that s.19 exists: Parliament amended it.
    pdf = os.path.join(REPO, "scratch", "_fa2026.pdf")
    if not os.path.exists(pdf):
        subprocess.run(["curl", "-s", "-L", "--max-time", "120", "-A", UA, "-o", pdf, FA2026],
                       capture_output=True, timeout=180)
    import pypdf
    txt = re.sub(r"\s+", " ", "".join((p.extract_text() or "")
                                      for p in pypdf.PdfReader(pdf).pages))
    i = txt.find(AMEND_NEEDLE)
    art["finance_act_2026"] = {
        "url": FA2026, "bytes": os.path.getsize(pdf),
        "amending_text_found": i >= 0,
        "quote": txt[max(0, i - 120):i + 260] if i >= 0 else None,
        "proves": "Cap.82 s.19 EXISTS and HAS an amending instrument (FA2026 s.98).",
    }
    if i < 0:
        print("ABORT: the amending text is not in the fetched Act. Verdict withheld.")
        json.dump(art, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        return 2

    # Does the substituted wording appear in our fact? That is currency, not just existence.
    gov = real.get("exemption_category_government_departments", {})
    art["substituted_wording_present_in_our_fact"] = (
        "through Government subvention" in json.dumps(gov, ensure_ascii=False))

    # The named function from the dispatcher claim.
    pkg = os.path.join(REPO, "chike")
    hits = []
    for root, _, files in os.walk(pkg):
        for fn in files:
            if fn.endswith(".py"):
                src = open(os.path.join(root, fn), encoding="utf-8", errors="replace").read()
                if "infer_sector" in src:
                    hits.append(os.path.relpath(os.path.join(root, fn), REPO))
    art["infer_sector_for_licence_sites"] = hits

    art["verdict"] = {
        "family_exists_as_described": False,
        "sections_fabricated": False,
        "statute_numbering_ends_at_18": False,
        "statute_has_no_amending_instrument": False,
        "named_function_exists": bool(hits),
        "recommended_action": ("DO NOT HEDGE. On a verified fact a hedge is a REGRESSION: it "
                               "withdraws a correct, primary-sourced answer. These facts are "
                               "current to the most recent Finance Act."),
    }
    json.dump(art, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    print(f"VETA Cap.82 s.19 facts found : {len(fam)} (claim said 5)")
    print(f"  carrying a verified_by     : {art['with_verification_record']}")
    print(f"FA2026 amending text found   : {art['finance_act_2026']['amending_text_found']}")
    print(f"  -> {art['finance_act_2026']['proves']}")
    print(f"substituted wording in fact  : {art['substituted_wording_present_in_our_fact']}")
    print(f"infer_sector_for_licence     : {hits or 'NOT FOUND ANYWHERE IN chike/'}")
    print(f"\nVERDICT: {art['verdict']['recommended_action']}")
    print("artifact:", OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
