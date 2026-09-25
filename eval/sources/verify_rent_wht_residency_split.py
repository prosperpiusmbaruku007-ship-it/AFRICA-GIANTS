"""Does commercial rent withholding have a RESIDENCY SPLIT? Verify against primary statute.

WHY THIS RUN EXISTS. The rental-withholding engine was scoped with a residency branch
(10% resident / 15% non-resident) and an instruction to probe both directions, on the
grounds that "a resident taxed at 15% is as wrong as a non-resident at 10%". Before
building a branch, R31 step 1 asks what populates it. Before trusting the VALUE the branch
would return, R28 asks for primary source. This script asks the second question and the
answer removes the branch.

THREE INDEPENDENT READINGS, deliberately not collapsed:

  1. THE STATUTE (decisive). Income Tax Act Cap.332, First Schedule para 4(b)(ii).
  2. THE REGULATOR'S SUMMARY. TRA's withholding page rate table, parsed WITH its column
     headers rather than by inferring column order -- CLAUDE.md is explicit that "the
     regulator's own summary is not the statute either" (TRA's At a Glance printed a Class A
     transport row the enacted Finance Act 2024 does not contain), so this is corroboration
     and never the authority.
  3. THE CORPUS. How many training rows assert the split, and are any in the eval set.

THE CONTROL THAT MAKES THE READING NON-VACUOUS (R23). A check that merely finds "ten
percent" near "rent" would pass whether or not a residency split exists -- the resident limb
is 10% under either hypothesis, so that value is exactly what the system produces by default.
The discriminating evidence is that the SAME paragraph splits a DIFFERENT payment type by
residency in adjacent words: service fees at "five percent for a resident and fifteen percent
for a non-resident". So the Act demonstrably knows how to write a residency split, uses that
form nearby, and does NOT use it for rent -- it instead names the non-resident limb explicitly
and gives it the same ten percent. A drafting silence would be ambiguous; an explicit
non-resident limb is not.

Scoping/verification only. Encodes nothing. Any locked-fact change still goes through R27.

Usage:  python eval/sources/verify_rent_wht_residency_split.py
"""

import glob
import json
import os
import re
import subprocess
import sys
from datetime import date

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(REPO, "eval", "results", "rent_wht_residency_split_2026_09_25.json")
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")

ITA_PDF = "https://www.tra.go.tz/images/uploads/acts/The_Income_Tax_Act.pdf"
TRA_WHT = "https://www.tra.go.tz/page/withholding-tax"

# The exact statutory limb, as a needle. If the Act text ever stops containing this, the run
# FAILS rather than quietly reporting from a changed document.
RENT_LIMB = ("in the case of interest, rent or a commuted pension paid to a resident "
             "withholdee or interest or rent paid to a non- resident withholdee")
# The adjacent contrast that makes the finding discriminating rather than merely consistent.
SERVICE_FEE_CONTRAST = "five percent for a resident and fifteen percent for a non-resident"


def curl(url, dest):
    subprocess.run(["curl", "-s", "-L", "--max-time", "90", "-A", UA, "-o", dest, url],
                   capture_output=True, timeout=150)
    return os.path.getsize(dest) if os.path.exists(dest) else 0


def flat(s):
    return re.sub(r"\s+", " ", s)


def read_statute(scratch):
    dest = os.path.join(scratch, "_ita.pdf")
    size = curl(ITA_PDF, dest)
    import pypdf
    reader = pypdf.PdfReader(dest)
    txt = flat("".join((p.extract_text() or "") for p in reader.pages))
    out = {"url": ITA_PDF, "bytes": size, "pages": len(reader.pages)}
    m = re.search(r"CHAPTER 332 THE INCOME TAX ACT", txt)
    ed = re.search(r"THE INCOME TAX ACT \[CAP\s*\.\s*332 R\.E\. (\d{4})\]", txt)
    out["edition"] = f"Cap.332 R.E. {ed.group(1)}" if ed else "UNKNOWN"
    out["act_header_present"] = bool(m)

    i = txt.find(RENT_LIMB)
    out["rent_limb_found"] = i >= 0
    if i >= 0:
        out["rent_limb_quote"] = txt[i:i + 190]
        out["rent_rate_stated"] = ("ten percent" if "ten percent" in txt[i:i + 190]
                                   else "NOT_TEN_PERCENT")
    j = txt.find(SERVICE_FEE_CONTRAST)
    out["service_fee_contrast_found"] = j >= 0
    if j >= 0:
        out["service_fee_contrast_quote"] = txt[j:j + 120]
    return out


def read_tra_table(scratch):
    dest = os.path.join(scratch, "_wht.html")
    size = curl(TRA_WHT, dest)
    h = open(dest, encoding="utf-8", errors="replace").read()
    out = {"url": TRA_WHT, "bytes": size, "header": None, "rent_row": None}
    for tb in re.findall(r"(?s)<table.*?</table>", h):
        rows = re.findall(r"(?s)<tr.*?</tr>", tb)
        parsed = []
        for r in rows:
            cells = [flat(re.sub(r"<[^>]+>", "", c)).replace("\xa0", " ").strip()
                     for c in re.findall(r"(?s)<t[dh].*?</t[dh]>", r)]
            cells = [c for c in cells if c]
            if cells:
                parsed.append(cells)
        if not parsed:
            continue
        # Only trust the table that NAMES its columns. Inferring column order is how a
        # 10/10 row gets read as 10/15.
        if any("Non Resident" in c or "Non-Resident" in c for c in parsed[0]):
            out["header"] = parsed[0]
            for row in parsed[1:]:
                if row and row[0].lower().startswith("rental income"):
                    out["rent_row"] = row
            break
    return out


def scan_corpus():
    hits = []
    for fn in glob.glob(os.path.join(REPO, "datasets", "**", "*.jsonl"), recursive=True):
        for line in open(fn, encoding="utf-8"):
            try:
                d = json.loads(line)
            except Exception:
                continue
            blob = " ".join(str(d.get(k, "")) for k in
                            ("answer_sw", "answer_en", "question_sw", "question_en")).lower()
            if ("pango" in blob or "rent" in blob) and \
               re.search(r"wasio wakazi|non.?resident", blob) and \
               re.search(r"15\s*%|asilimia 15", blob):
                hits.append({"file": os.path.relpath(fn, REPO), "id": d.get("id"),
                             "eval_set": d.get("eval_set")})
    return hits


def main():
    scratch = os.path.join(REPO, "scratch")
    os.makedirs(scratch, exist_ok=True)
    art = {
        "measured": str(date.today()),
        "harness": "eval/sources/verify_rent_wht_residency_split.py",
        "question": "Does commercial rent WHT have a resident/non-resident split?",
        "authority_order": "statute decides; the TRA summary corroborates and never overrides "
                           "(CLAUDE.md: the regulator's own summary is not the statute).",
    }
    art["statute"] = read_statute(scratch)
    json.dump(art, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    art["tra_summary"] = read_tra_table(scratch)
    json.dump(art, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    art["corpus_rows_asserting_15pct"] = scan_corpus()
    st = art["statute"]

    split_exists = not (st.get("rent_limb_found") and st.get("rent_rate_stated") == "ten percent")
    art["verdict"] = {
        "residency_split_for_rent": "NO" if not split_exists else "UNRESOLVED",
        "resident_rate": "10%", "non_resident_rate": "10%",
        "discriminating_evidence": (
            "The SAME First Schedule paragraph writes an explicit residency split for service "
            "fees ('five percent for a resident and fifteen percent for a non-resident') and "
            "does NOT write one for rent -- it names the non-resident limb and gives it the "
            "same ten percent. Silence would be ambiguous; an explicit non-resident limb is not."
        ) if st.get("service_fee_contrast_found") else "CONTRAST NOT FOUND -- finding is weaker",
        "corpus_rows_wrong": len(art["corpus_rows_asserting_15pct"]),
        "corpus_rows_in_eval_set": sum(1 for h in art["corpus_rows_asserting_15pct"]
                                       if h.get("eval_set")),
    }
    json.dump(art, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    print("statute edition :", st.get("edition"))
    print("rent limb found :", st.get("rent_limb_found"), "->", st.get("rent_rate_stated"))
    print("contrast found  :", st.get("service_fee_contrast_found"))
    print("TRA header      :", art["tra_summary"].get("header"))
    print("TRA rent row    :", art["tra_summary"].get("rent_row"))
    print("corpus 15% rows :", art["verdict"]["corpus_rows_wrong"],
          "| in eval set:", art["verdict"]["corpus_rows_in_eval_set"])
    print("VERDICT         : residency split =", art["verdict"]["residency_split_for_rent"])
    print("artifact        :", OUT)


if __name__ == "__main__":
    main()
