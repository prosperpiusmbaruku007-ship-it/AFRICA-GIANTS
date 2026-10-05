# -*- coding: utf-8 -*-
"""RE-SOURCE THE 43 PAIRS CITING mlywf.go.tz, A DOMAIN THAT NO LONGER RESOLVES.

THE PROBLEM, and it is worse than an absent citation. All 43 carry
`primary_source_url: https://www.mlywf.go.tz` -- the Ministry of Labour, Youth, Women and
Special Groups. The host has NO DNS RECORD (getaddrinfo failed, bare and www, on 2026-10-04 and
2026-10-05), while kazi.go.tz, wcf.go.tz and portal.wcf.go.tz all resolved in the same breath on
the same connection -- so it is the domain, not the link. A URL that reads as a citation and
cannot be fetched by anyone is strictly worse than a blank field: blank is visibly unverified,
whereas this looks checked and silently is not -- including to the TRA-registered consultant
whose sign-off R7's Gate 2 depends on.

⚠️ AND THEY WERE NEVER CHECKABLE EVEN WHEN THE DOMAIN LIVED. Every one of the 43 cites the bare
HOMEPAGE, not a page carrying the claim. So "repoint to the new domain" would move 43
unverifiable homepage citations to a different homepage and change nothing that matters. The
only repoint worth making is to the specific document that actually carries the claim.

WHAT THE 43 ARE:
    wcf_compliance        31
    gn605a_minimum_wage   10
    gn605a_adversarial     2

TWO DESTINATIONS CONSIDERED, both tested rather than assumed:

  ✅ wcf.go.tz/pages/contributions -- HTTP 200, 96,129 bytes, 17,974 chars of text, and it
     carries the WCF subject matter directly (0.5% rate, "asilimia sifuri nukta tano", "siku
     thelathini" / "mfanyakazi wa kwanza" for the 30-day registration, "siku saba" for the
     7-day reporting, "mapato ghafi" for the contribution base). Now whitelisted
     (tier1a_wcf_001/002) after ownership was verified from the site itself.
     NOTE: every /pages/* path on this host returns the IDENTICAL visible text (17,974 chars;
     contributions, compensation, huduma and faq all byte-length-equal and text-identical, the
     hashes differing only by a per-request nonce). So the path adds no specificity -- but this
     IS the document the content lives in, where `wcf.go.tz/` is the landing page.

  ⛔ kazi.go.tz -- UNUSABLE AS A CITATION TARGET TODAY, and this is a server fault, not ours.
     DNS resolves (196.192.79.159). https:// returns 000 with `Recv failure: Connection was
     reset`. http://www.kazi.go.tz/ returns 302 to `https://www.www.kazi.go.tz/` -- a MALFORMED
     redirect with a doubled `www.`, which cannot resolve. Tried three scheme/host combinations.
     A pair repointed there would be as uncheckable as it is now, so repointing to it would be
     laundering the problem rather than fixing it.

THEREFORE the 12 GN 605A pairs are marked UNSOURCED, not repointed. GN 605A's primary home is
TanzLII, which is behind a genuine Cloudflare Turnstile challenge (not a tool bug -- confirmed
with a real browser User-Agent). Marking them unsourced makes them COUNT as unverified, which is
the honest state and the point of the exercise.

⚠️ OVER-ASSIGNMENT IS THE RISK HERE AND IT RAN AT 14% ON THE LAST MECHANICAL SOURCING PASS
(3 wrong of 21). The specific hazard: proposing a WCF repoint for a pair whose claim the WCF
document does not actually support, which would manufacture a cited-and-contradicted row -- a
citation pointing at a page that does not say what the pair says. So the decision is made
PER CLAIM against the fetched document's text, NEVER from the `subdomain` field. A pair in
`wcf_compliance` whose distinctive terms are absent from the document is marked unsourced like
any other.

REPORT_ONLY by default. `--write` applies. Nothing reaches a file without the report being read.
"""
import json
import os
import re
import sys
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, "eval", "results", "mlywf_resourcing.json")
WCF_DOC = os.path.join(
    r"C:\Users\jhjh\AppData\Local\Temp\claude\C--Users-jhjh-AFRICA-GIANTS"
    r"\d8f91321-e9cf-4aa8-a380-2afc9441133f\scratchpad", "dom", "wcf_pages_contributions.html")

DEAD = "mlywf.go.tz"
WCF_URL = "https://www.wcf.go.tz/pages/contributions"
WCF_NAME = "Workers Compensation Fund (Mfuko wa Fidia kwa Wafanyakazi)"

# A claim is supportable by the WCF document only if at least one of its DISTINCTIVE subject
# terms appears there. Deliberately subject terms, not bare numbers: "10" or "12" appear in any
# document and would wave anything through -- the bare-figure match that produced the ext_15
# over-assignment on the provenance backfill.
#
# ⛔ NARROWED AFTER THE FIRST DRY RUN, WHICH PRODUCED 4 OVER-ASSIGNMENTS OUT OF 35 PROPOSED
# REPOINTS -- 11%, against 14% on the last mechanical sourcing pass. Every one of the four was a
# `gn605a_minimum_wage` claim matched on the single word **`mwajiri`** (employer):
#     "Adhabu ya kulipa chini ya mshahara wa chini wa GN 605A ni nini?"        -> ['mwajiri']
#     "Boss wangu analipa chini ya GN 605A -- ninafanya nini?"                 -> ['mwajiri']
#     "...mfanyakazi aliyeajiriwa kupitia wakala wa ajira ana haki ya GN 605A?" -> ['mwajiri']
#     "...ana haki ya kuuliza mwajiri wa zamani mshahara wake wote?"           -> ['mwajiri']
# A minimum-wage claim citing the WCF contributions page is a cited-and-contradicted row: the
# citation would point at a document that says nothing about minimum wage.
#
# `mwajiri`, `mfanyakazi`, `kujisajili`, `mchango`, `mfuko` are all REMOVED. They appear in
# essentially any labour claim AND in the WCF document, so they carry no discriminating power --
# the bare-figure mistake in word form, which is the same defect that attached a BRELA fee page
# to ext_15 on a "2,500" the gold only mentions to refute.
#
# Bare `0.5` is also removed for the same reason and replaced by the rate IN WORDS plus the
# explicit "asilimia 0.5" form: a lone decimal matches too much.
#
# What survives is WCF-DISTINCTIVE: the levy's own name, its compensation vocabulary, its
# contribution base, and its two statutory clocks.
WCF_SUBJECT_TERMS = [
    "wcf", "fidia", "mapato ghafi",
    "asilimia sifuri nukta tano", "asilimia 0.5",
    "mfanyakazi wa kwanza", "siku thelathini", "siku saba",
    "ajali", "ugonjwa", "matibabu",
]


def _text(path):
    import html as _html
    t = open(path, encoding="utf-8", errors="replace").read()
    t = re.sub(r"<script.*?</script>|<style.*?</style>", "", t, flags=re.S)
    return " ".join(_html.unescape(re.sub(r"<[^>]+>", " ", t)).split())


def main():
    write = "--write" in sys.argv
    assert os.path.exists(WCF_DOC), (
        f"the fetched WCF document is missing ({WCF_DOC}). This pass decides repoints by "
        f"reading it, so without it every verdict would default to 'unsourced' and look like a "
        f"finding rather than a missing input.")
    doc = _text(WCF_DOC).lower()
    assert len(doc) > 5000, f"WCF document text is only {len(doc)} chars -- fetch looks wrong"

    import glob
    rows, files = [], {}
    for f in sorted(glob.glob(os.path.join(REPO, "datasets", "*", "cleaned_pairs", "*.jsonl"))):
        kept = []
        dirty = False
        for ln, line in enumerate(open(f, encoding="utf-8"), 1):
            if not line.strip():
                continue
            r = json.loads(line)
            if DEAD not in str(r.get("primary_source_url", "")):
                kept.append(r)
                continue

            claim = " ".join(str(r.get(k, "")) for k in
                             ("question_sw", "answer_sw", "question_en", "answer_en")).lower()
            matched = [t for t in WCF_SUBJECT_TERMS if t in claim and t in doc]
            is_wcf_claim = bool(matched)

            if is_wcf_claim:
                verdict, new_url, new_name = "REPOINT_WCF", WCF_URL, WCF_NAME
                r["primary_source_url"] = WCF_URL
                r["primary_source_name"] = WCF_NAME
                r["_resourced"] = {
                    "date": "2026-10-05",
                    "from": "https://www.mlywf.go.tz (NO DNS RECORD -- unfetchable by anyone)",
                    "to": WCF_URL,
                    "basis": f"claim's WCF subject terms {matched[:5]} are present in the "
                             f"fetched wcf.go.tz document (HTTP 200, 17,974 chars of text)",
                    "harness": "scripts/resource_mlywf_pairs.py",
                    "⚠️": "The destination is a PAGE-LEVEL citation, not a quote-level one. It "
                          "is where this subject matter is published; it is not proof this "
                          "exact sentence appears there. Better than a dead host, weaker than "
                          "a verbatim quote.",
                }
                dirty = True
            else:
                verdict, new_url, new_name = "MARK_UNSOURCED", "", ""
                r["primary_source_url"] = ""
                r["primary_source_name"] = ""
                r["_resourced"] = {
                    "date": "2026-10-05",
                    "from": "https://www.mlywf.go.tz (NO DNS RECORD -- unfetchable by anyone)",
                    "to": "UNSOURCED -- deliberately blank",
                    "basis": "no WCF subject term shared between the claim and the fetched "
                             "wcf.go.tz document; and kazi.go.tz is unusable as a target "
                             "(302 -> https://www.www.kazi.go.tz, a malformed doubled-www "
                             "redirect), while GN 605A's home on TanzLII is behind a real "
                             "Cloudflare Turnstile challenge.",
                    "harness": "scripts/resource_mlywf_pairs.py",
                    "⚠️": "BLANK IS THE HONEST STATE AND IS THE POINT: it makes the pair count "
                          "as unverified instead of reading as cited. It will now FAIL "
                          "validate_dataset's empty-field check, which is correct -- an "
                          "unsourced pair should not sit in cleaned_pairs/ claiming otherwise.",
                }
                dirty = True

            rows.append({"id": r.get("id"), "file": os.path.relpath(f, REPO), "line": ln,
                         "subdomain": r.get("subdomain"), "verdict": verdict,
                         "matched_terms": matched[:6], "new_url": new_url,
                         "question": str(r.get("question_sw", ""))[:110]})
            kept.append(r)
        if dirty:
            files[f] = kept

    assert rows, f"no pairs cite {DEAD} -- already re-sourced, or the field moved"

    by = Counter(r["verdict"] for r in rows)
    cross = Counter((r["subdomain"], r["verdict"]) for r in rows)

    if write:
        for f, kept in files.items():
            with open(f, "w", encoding="utf-8") as fh:
                for r in kept:
                    fh.write(json.dumps(r, ensure_ascii=False) + "\n")

    payload = {
        "_what": f"Re-sourcing the {len(rows)} pairs citing {DEAD}, a domain with no DNS record.",
        "_mode": "WRITE" if write else "REPORT_ONLY",
        "_why_not_just_repoint": "All 43 cited the bare HOMEPAGE, so they were never checkable "
                                 "even while the domain lived. Repointing a homepage to another "
                                 "homepage changes nothing that matters.",
        "_destinations_tested": {
            "wcf.go.tz/pages/contributions": "HTTP 200, 96,129 bytes, 17,974 chars of text, "
                                             "carries the WCF subject matter. Whitelisted "
                                             "2026-10-05 after verifying ownership on the site.",
            "kazi.go.tz": "UNUSABLE: DNS resolves but https returns 000 (connection reset) and "
                          "http 302s to https://www.www.kazi.go.tz -- a malformed doubled-www "
                          "redirect. Three combinations tried. A pair sent there would be as "
                          "uncheckable as it is now.",
        },
        "_over_assignment_guard": "Verdicts are decided PER CLAIM against the fetched "
                                  "document's text, never from the `subdomain` field, and only "
                                  "on distinctive SUBJECT terms -- never bare figures, which "
                                  "match any document and produced the ext_15 over-assignment "
                                  "on the last mechanical sourcing pass (3 wrong of 21, 14%).",
        "totals": dict(by),
        "by_subdomain_and_verdict": {f"{k[0]} / {k[1]}": v for k, v in sorted(cross.items())},
        "rows": rows,
    }
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)

    print(f"mode: {payload['_mode']}   pairs citing {DEAD}: {len(rows)}")
    print(f"totals: {dict(by)}")
    print("\nby subdomain:")
    for k, v in sorted(cross.items()):
        print(f"   {v:3d}  {k[0]} -> {k[1]}")
    print("\nMARK_UNSOURCED rows (these will now fail validate_dataset, correctly):")
    for r in rows:
        if r["verdict"] == "MARK_UNSOURCED":
            print(f"   {r['id']}  [{r['subdomain']}]  {r['question'][:84]}")
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
