#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EVERY CACHED SOURCE CARRIES ITS EDITION, AND ANY CHECK AGAINST ONE ASSERTS THE EDITION FIRST.

Usage:
    python scripts/check_source_editions.py            # verify the manifest (exit 1 on drift)
    python scripts/check_source_editions.py --build     # regenerate the manifest from content
    assert_edition("data/source_documents/nssf/nssf_act_cap50.pdf", "R.E. 2015")   # from code

WHY, and it is not hypothetical. `fine_limit` said TZS 100,000 because it was read from
data/source_documents/nssf/nssf_act_cap50.pdf -- which is REVISED EDITION 2015, where s.72(1)
genuinely says "one hundred thousand shillings". R.E.2023 s.76(1) says ten million. The fact
was not unchecked; it was CHECKED AGAINST THE WRONG EDITION, and nothing in the filename, the
`source` field or the fact's own metadata said which edition the file was.

⛔ THE TWO FORMS OF THE RENUMBERING TRAP, both present in Cap.50, and the reason an edition
assertion has to come FIRST rather than alongside:

    POINTS AT NOTHING ....... s.5A does not exist in R.E.2023. Four facts cited the First
                              Schedule as made under "ss.5A(c), 12(1)"; R.E.2023's own rubric
                              reads "sections 5(2)(c) and 12(1) and (5)". A reader checking
                              s.5A finds no such section. FAILS LOUDLY.
    POINTS AT THE WRONG THING  The offences clause is s.72 in R.E.2015 and s.76 in R.E.2023.
                              In R.E.2015, s.76 is "Protection of contributions" -- a
                              different provision. A reader checking "s.76(1)" against the
                              cached R.E.2015 PDF reads the wrong section and comes away
                              CONFIDENTLY CONFIRMED.

The second is the form that was actually operating, and it means **checking a citation against
a cached PDF can certify an error**. A verification pass that does not first establish which
edition it is holding is not a verification pass; it is a coin flip whose result is reported as
evidence.

WHAT AN "EDITION" IS, PER KIND -- because most of these files are not statutes:
    statute   the Revised Edition printed on its cover ("REVISED EDITION OF 2015")
    gazette   the GN number and publication date printed on it
    portal    the CAPTURE DATE -- a regulator's page has no edition, so the only honest answer
              is when we fetched it. Where the page embeds dated news items, those bound the
              capture from below and are recorded as evidence rather than asserted.
    advisory  the tax year on its cover ("2025/2026")

R26 both directions: tests/test_source_editions.py plants a swapped file (must block) and a
clean tree (must pass).
"""
import argparse
import hashlib
import html
import io
import json
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.join(REPO, "data", "source_documents")
MANIFEST = os.path.join(ROOT, "MANIFEST.json")

# ── EDITION FACTS, each READ FROM THE DOCUMENT and quoted, never inferred from a filename ──
# A file absent from here is reported as UNDECLARED rather than skipped: an undeclared cached
# source is exactly the state fine_limit was verified against.
DECLARED = {
    "nssf/nssf_act_cap50.pdf": {
        "kind": "statute",
        "edition": "R.E. 2015",
        "edition_evidence": "cover: 'CHAPTER 50 THE NATIONAL SOCIAL SECURITY FUND ACT, "
                            "[PRINCIPAL LEGISLATION] REVISED EDITION OF 2015 ... incorporates "
                            "all amendments made up to and including 31st December, 2015'",
        "superseded": True,
        "superseded_by": "Cap.50 R.E. 2023 (OAG 2025 compilation), sha256 2a820e67ed109cd36059, "
                         "773,203 bytes, 50pp, at "
                         "https://www.nssf.go.tz/uploads/publications/"
                         "en-1771921274-NSSF%20ACT%20CAP%2050%20RE.%202023.pdf and "
                         "https://oagmis.oag.go.tz/portal/acts/revised/155/download "
                         "(byte-identical)",
        "do_not_verify_against": "THIS FILE PRODUCED THE fine_limit 100x ERROR. s.72(1) here is "
                                 "s.76(1) in R.E.2023, and this edition's s.76 is a DIFFERENT "
                                 "provision ('Protection of contributions'). Renumbering "
                                 "offsets confirmed from R.E.2023's own bracketed notes: "
                                 "s.23<-[21] s.25<-[23] s.29<-[27] s.46<-[44] s.47<-[45] "
                                 "s.50<-[48] s.51<-[49] s.76<-[72]; s.11/s.12/s.14 unmoved.",
    },
    "immigration/gn487a_official_gazette.pdf": {
        "kind": "gazette",
        "edition": "GN No. 487A, published 28/7/2025",
        "edition_evidence": "page 1: 'GOVERNMENT NOTICE No. 487A published on 28/7/2025 THE "
                            "BUSINESS LICENSING ACT, (CAP. 101)'",
        "superseded": False,
    },
    "brela/brela_ada_kampuni.html": {
        "kind": "portal",
        "edition": "capture of brela.go.tz/pages/tozo-za-kampuni, not earlier than 10 Jun 2026",
        "edition_evidence": "embedded news items dated '10 Jun 2026' and '02 Jun 2026' bound "
                            "the capture from below. A regulator's page has no edition, so the "
                            "capture date is the only honest answer and is recorded as a BOUND, "
                            "not as a date we know.",
        "superseded": False,
        "note": "⭐ THIS CAPTURE BEARS ON THREE DISPUTES OPEN IN CLAUDE.md Section 11, and is "
                "quoted here so the next reader does not have to re-derive it:\n"
                "  item 14 ('Ada zinazolipwa na kampuni ambapo KIFUNGU XII cha Sheria "
                "kinahusika'), fourth bullet: 'Ada ya kuchelewa kufungua jalada/usajili wa "
                "waraka wowote inalipwa kwa Msajili (kwa mwezi au sehemu ya siku za mwezi) ni "
                "Dola za Kimarekani 25 /=' -- USD 25, under PART XII. The string '70,000' "
                "appears NOWHERE in this capture.\n"
                "  item 2: 'Usajili wa kampuni ambayo haina mtaji wa hisa ... Tsh. 300,000 /=' "
                "-- and '500,000' appears NOWHERE in this capture.\n"
                "  item 10: 'Gharama za kujaza taarifa ya mwaka Tsh. 22,000 /=' and item 9: "
                "late filing 'TSHS 2,500 /=' per month -- both already locked, re-confirmed.\n"
                "⚠️ THIS DOES NOT DISPROVE THE 2026-10-04 READING of TZS 70,000. It establishes "
                "that NO CACHED ARTIFACT SUPPORTS IT and that the one capture we hold says USD "
                "25. A live page can change; an unsaved live reading cannot be checked by "
                "anyone, which is the whole argument for capturing before citing.",
    },
    "brela/brela_ada_kampuni_v2.html": {
        "kind": "portal",
        "edition": "BYTE-IDENTICAL to brela_ada_kampuni.html -- NOT a second capture",
        "edition_evidence": "sha256 equal to brela/brela_ada_kampuni.html.",
        "superseded": False,
        "note": "⛔ THE '_v2' SUFFIX ASSERTS A SECOND OBSERVATION THAT DOES NOT EXIST. Two "
                "files, one capture. Anything that reads these as two readings of the page at "
                "two times is reading a filename, not a document (R34). Kept rather than "
                "deleted so the duplication is recorded instead of quietly resolved.",
    },
    "nssf/nssf_ulipaji_mchango.txt": {
        "kind": "portal",
        "edition": "NONE -- THE FILE IS 0 BYTES",
        "edition_evidence": "size 0. There is no content and therefore no edition.",
        "superseded": False,
        "note": "⛔ AN EMPTY CACHED SOURCE IS THE R26 INERT-CONTROL SHAPE IN THE SOURCE LAYER. "
                "Anything recorded as 'verified against' this path was verified against "
                "nothing, and the verification would have looked exactly like a successful one. "
                "Kept and declared rather than deleted so the gap is visible; re-fetch or "
                "remove deliberately.",
    },
    "nssf/nssf_go_contributions.html": {
        "kind": "portal",
        "edition": "capture of nssf.go.tz/pages/payment-of-contributions; the page itself "
                   "cites 'R.E. 2018'",
        "edition_evidence": "the string 'R.E. 2018' appears in the page body.",
        "superseded": False,
        "note": "The Fund's own portal cites R.E.2018 on this page and R.E 2023 on "
                "nssf_go_registration.html -- TWO EDITIONS OF ITS OWN ACT across two pages of "
                "one site. Neither is the statute; use Cap.50 R.E.2023 for any section number.",
    },
    "nssf/nssf_go_registration.html": {
        "kind": "portal",
        "edition": "capture of nssf.go.tz registration overview; the page itself cites "
                   "'R.E 2023'",
        "edition_evidence": "the string 'R.E 2023' appears in the page body.",
        "superseded": False,
    },
    "tra/tra_taxes_duties_2025_2026.pdf": {
        "kind": "advisory",
        "edition": "TRA 'Taxes and Duties at a Glance' July 2025 (FY 2025/2026)",
        "edition_evidence": "cover: 'TAXES FOR OUR DEVELOPMENT JULY, 2025'",
        "superseded": False,
        "note": "A regulator SUMMARY, not the statute. CLAUDE.md Section 4 records that this "
                "family's Class A transport row could not be verified against primary text.",
    },
    "tra/habib_advisory_tax_guide_2025_26.pdf": {
        "kind": "advisory",
        "edition": "Hanif Habib & Co. tax guide 2025/2026",
        "edition_evidence": "cover text names the firm and the 2025/2026 year.",
        "superseded": False,
    },
}

# Files whose edition is simply "the capture", with no in-document marker to quote. Declared as
# a CLASS rather than individually, because inventing a per-file date we do not have would be
# worse than saying plainly that we do not have one.
UNDATED_PORTAL_CAPTURE = (
    "A portal/press capture with no edition or date marker in the document. The honest edition "
    "is 'whenever this was fetched', and that is NOT recorded anywhere -- so it may not be used "
    "to settle a figure on its own. Capture provenance was not kept when these were saved; "
    "re-fetch with a dated record if one of them needs to carry a claim.")


def _hash(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def _walk():
    out = []
    for root, _, files in os.walk(ROOT):
        for f in sorted(files):
            if f in (".gitkeep", "MANIFEST.json"):
                continue
            full = os.path.join(root, f)
            rel = os.path.relpath(full, ROOT).replace("\\", "/")
            out.append((rel, full))
    return sorted(out)


def build():
    entries = {}
    for rel, full in _walk():
        d = DECLARED.get(rel)
        size = os.path.getsize(full)
        entries[rel] = {
            "sha256": _hash(full),
            "bytes": size,
            "kind": d["kind"] if d else "portal",
            "edition": d["edition"] if d else "UNDECLARED",
            "edition_evidence": d["edition_evidence"] if d else UNDATED_PORTAL_CAPTURE,
            "superseded": bool(d and d.get("superseded")),
        }
        for opt in ("superseded_by", "do_not_verify_against", "note"):
            if d and d.get(opt):
                entries[rel][opt] = d[opt]
    payload = {
        "_what": "Edition manifest for every cached source document. An edition is a property "
                 "of the DOCUMENT, read from it and quoted -- never inferred from a filename.",
        "_why": "fine_limit said TZS 100,000 because it was read from nssf_act_cap50.pdf, which "
                "is R.E.2015. Checking a citation against a cached PDF CAN CERTIFY AN ERROR "
                "when the edition renumbered: Cap.50's offences clause is s.72 in R.E.2015 and "
                "s.76 in R.E.2023, and R.E.2015's s.76 is a different provision entirely.",
        "_contract": "Any check that reads a cached source MUST call assert_edition(path, "
                     "expected) first. A file whose edition is UNDECLARED may not be used to "
                     "settle a figure.",
        "_generated_by": "scripts/check_source_editions.py --build",
        "counts": {
            "files": len(entries),
            "declared": sum(1 for e in entries.values() if e["edition"] != "UNDECLARED"),
            "undeclared": sum(1 for e in entries.values() if e["edition"] == "UNDECLARED"),
            "superseded": sum(1 for e in entries.values() if e["superseded"]),
        },
        "files": entries,
    }
    with io.open(MANIFEST, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    return payload


def load_manifest():
    with io.open(MANIFEST, encoding="utf-8") as fh:
        return json.load(fh)


def assert_edition(path, expected):
    """THE CONTRACT. Call this BEFORE reading a cached source to settle anything.

    `path` may be absolute, repo-relative, or relative to data/source_documents/.
    Raises AssertionError if the file is unknown, if its bytes no longer match the manifest
    (someone swapped the file under its name), or if the declared edition does not contain
    `expected`.
    """
    man = load_manifest()["files"]
    norm = str(path).replace("\\", "/")
    for cand in (norm, norm.split("data/source_documents/")[-1]):
        if cand in man:
            rel = cand
            break
    else:
        raise AssertionError(
            f"{path} is not in the source manifest. An undeclared cached source has no known "
            f"edition, and an unknown edition is how the fine_limit 100x error happened. Add it "
            f"to DECLARED in scripts/check_source_editions.py, with the edition QUOTED from the "
            f"document.")
    entry = man[rel]
    full = os.path.join(ROOT, rel)
    actual = _hash(full)
    assert actual == entry["sha256"], (
        f"{rel} no longer matches the manifest (sha256 {actual[:12]} vs {entry['sha256'][:12]}) "
        f"-- the FILE CHANGED UNDER ITS NAME, so its declared edition is not a claim about "
        f"these bytes. Re-read the document and rebuild the manifest before using it.")
    assert expected.lower() in entry["edition"].lower(), (
        f"{rel} is edition {entry['edition']!r}, not {expected!r}.\n"
        f"  evidence: {entry['edition_evidence']}\n"
        + (f"  ⛔ {entry['do_not_verify_against']}\n"
           if entry.get("do_not_verify_against") else "")
        + "Reading a renumbered edition returns a CONFIDENT WRONG confirmation, not an error.")
    return entry


def check():
    if not os.path.exists(MANIFEST):
        print("[FATAL] no MANIFEST.json -- run with --build")
        return 2
    man = load_manifest()
    declared_files = man["files"]
    on_disk = {rel for rel, _ in _walk()}
    problems = []

    for rel in sorted(on_disk - set(declared_files)):
        problems.append(("UNMANIFESTED", rel, "present on disk, absent from the manifest"))
    for rel in sorted(set(declared_files) - on_disk):
        problems.append(("MISSING", rel, "in the manifest, absent from disk"))
    for rel in sorted(on_disk & set(declared_files)):
        actual = _hash(os.path.join(ROOT, rel))
        if actual != declared_files[rel]["sha256"]:
            problems.append(("CHANGED", rel,
                             f"sha256 {actual[:12]} != manifest {declared_files[rel]['sha256'][:12]}"))

    undeclared = sorted(r for r, e in declared_files.items() if e["edition"] == "UNDECLARED")
    superseded = sorted(r for r, e in declared_files.items() if e["superseded"])

    print(f"source documents: {len(on_disk)}")
    print(f"  edition declared : {len(declared_files) - len(undeclared)}")
    print(f"  UNDECLARED       : {len(undeclared)}  (may NOT settle a figure on their own)")
    print(f"  SUPERSEDED       : {len(superseded)} -> {superseded}")
    if problems:
        print("\nPROBLEMS:")
        for kind, rel, why in problems:
            print(f"  [{kind}] {rel}: {why}")
        return 1
    print("\nMANIFEST OK -- every cached source accounted for and unchanged.")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", action="store_true")
    a = ap.parse_args()
    if a.build:
        p = build()
        print(json.dumps(p["counts"], indent=2))
        print(f"[built] {MANIFEST}")
        return 0
    return check()


if __name__ == "__main__":
    sys.exit(main())
