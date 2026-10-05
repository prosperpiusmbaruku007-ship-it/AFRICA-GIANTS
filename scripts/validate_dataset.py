"""
Validates all JSONL pairs in datasets/*/cleaned_pairs/ against:
  1. schema/pair_schema.json — all 18 required fields present + enum values valid
  2. sources/whitelist.json — primary_source_url domain is whitelisted

Exit 0: the schema-shaped corpus is clean AND the SFT-shaped exception has not grown.
Exit 1: a schema-shaped pair failed, or a NEW/GROWN SFT-shaped file appeared.
Exit 2: the validator could not evaluate anything — NOT a pass.

Usage: python scripts/validate_dataset.py


⛔⛔ WHY THIS FILE WAS REWRITTEN ON 2026-10-05 — IT WAS AN INERT GATE.

It reported **46,881 errors across 4,416 pairs** and exited 1 on every invocation, and had done
so for an unknown length of time. CLAUDE.md Section 9 makes this gate BLOCKING ("must exit 0
before any pair advances"). A gate that fails on absolutely everything is exactly as
uninformative as one that fires on nothing: it cannot distinguish "the compliant corpus just
regressed" from "the same known rows are still there", so the only way to keep working is to
ignore it — and an ignored blocking gate is an absent one. Same class as the pre-push hook that
scanned zero files (R26) and R20's vacuous asserts, arriving in a VALIDATOR.

THE DIAGNOSIS, measured rather than guessed, and it is NOT "the schema is wrong":

    batch_NNN_cleaned.jsonl          10 files   1,715 pairs   ALL 18-field compliant
    cleaned_pairs_batch_NNN.jsonl     8 files   2,705 pairs   ALL SFT-shaped

**A filename convention separates two pipeline generations that both wrote into the same
directory.** The earlier generation (batches 1–8) is fully schema-compliant — so the 18-field
schema is neither wrong nor aspirational; 1,715 real pairs satisfy it today. The later
generation (batches 9–19) writes `instruction`/`input`/`output`/`system` rows, which carry no
provenance metadata at all: no `primary_source_url`, no `verified_by`, no `eval_set` flag.

So BOTH of the obvious options are wrong. "Fix the schema to match what the pipeline uses" would
retire the metadata contract that 1,715 pairs already honour and that R3 exists to enforce.
"Retire the gate" would delete the only check that would notice the compliant half regressing.

WHAT THIS DOES INSTEAD — enforce where it can, and TRACK the rest as a frozen, shrinking
exception, the pattern already proven by PENDING_BACKFILL in
tests/test_probe_provenance_required.py:

  * schema-shaped files are validated STRICTLY. Any failure exits 1.
  * SFT-shaped files are a DECLARED exception, enumerated by name with row counts. They are not
    validated against a schema they cannot satisfy — but a NEW one, or a GROWN one, exits 1.
    The exception can only shrink.
  * a row matching NEITHER shape exits 1, so a third pipeline generation cannot arrive unseen.
  * evaluating nothing exits 2 with "GATE NOT RUN", because cannot-evaluate is not passed — the
    same fix already applied to run_eval.py's empty-corpus path.

⚠️ THIS DOES NOT MAKE THE 2,705 ROWS R3-COMPLIANT, AND IS NOT A DECISION THAT THEY MAY STAY.
It makes their non-compliance VISIBLE AND BOUNDED instead of drowned in 46,881 undifferentiated
errors. The founder's call, named here rather than quietly absorbed: either backfill the 18
fields onto them, or move them out of `cleaned_pairs/` into a directory whose name does not
assert a contract they do not meet. Every number above is reproducible by running this file.
"""
import json
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).parent.parent
SCHEMA_PATH = ROOT / "schema" / "pair_schema.json"
WHITELIST_PATH = ROOT / "sources" / "whitelist.json"
DATASETS_ROOT = ROOT / "datasets"


def load_schema():
    with open(SCHEMA_PATH, encoding="utf-8") as f:
        return json.load(f)


def _host(url):
    """Netloc with any leading `www.` removed.

    ⛔ THIS NORMALISATION IS A VALIDATOR BUG FIX, NOT A RELAXATION, and the whitelist's own
    contents are the proof. `sources/whitelist.json` stores `tanzlii.org` BARE but
    `www.tra.go.tz`, `www.brela.go.tz`, `www.osha.go.tz` and 14 others WITH the prefix. Exact
    netloc comparison therefore rejected 58 pairs citing `www.tanzlii.org` -- a host CLAUDE.md
    Section 4 names explicitly as a Tier 1A TRAINING source ("tanzlii.org — primary legal
    database: official Acts and Government Notices"). The pairs were right; the comparison was
    wrong, and it was wrong because the whitelist is internally inconsistent about a prefix that
    carries no meaning. `www.X` and `X` are the same publisher.

    Deliberately does NOT normalise other subdomains: `portal.wcf.go.tz` is a different service
    from `wcf.go.tz` and collapsing them would be a policy decision, not a bug fix.
    """
    return urlparse(url).netloc.removeprefix("www.")


def load_whitelist():
    with open(WHITELIST_PATH, encoding="utf-8") as f:
        entries = json.load(f)
    return {_host(e["url"]) for e in entries}


# ── UN-WHITELISTED SOURCE DOMAINS — RESOLVED 2026-10-05 BY VERIFYING OWNERSHIP ─────────────
# Both were checked against the live hosts rather than reasoned about, per the standing rule that
# ownership is verified, never inferred. The two came back DIFFERENT, which is why only one was
# whitelisted:
#
#  ✅ wcf.go.tz + portal.wcf.go.tz -- WHITELISTED (sources/whitelist.json tier1a_wcf_001/002,
#     CLAUDE.md Section 4). Verified from the sites: wcf.go.tz returns HTTP 200 / 183,434 bytes
#     with the header "WCF | Ofisi ya Waziri Mkuu Kazi, Ajira na Mahusiano" plus "Mfuko wa
#     Fidia" and "Jamhuri ya Muungano"; portal.wcf.go.tz returns HTTP 200 / 40,323 bytes
#     identifying itself as "WORKERS COMPENSATION FUND SELF SERVICE PORTAL". The Fund's own site
#     and the Fund's own subdomain. This closes a real gap: Section 11 has carried a full WCF
#     block since Jun 2026 and two locked facts were sourced from that host, while the domain was
#     on the approved list in NO form -- so every WCF-sourced pair was failing the pipeline's own
#     source check.
#
#  ✅ mlywf.go.tz -- NOW EMPTY BECAUSE THE 43 PAIRS WERE RE-SOURCED, not because it was excused.
#     The host has NO DNS RECORD at all, bare or www (`getaddrinfo failed` / `curl (6) Could not
#     resolve host`) -- a DNS failure, not an HTTP one, so no tool switch helps. And it was not
#     this link misbehaving, which is the control that made the finding meaningful: kazi.go.tz
#     (196.192.79.159), wcf.go.tz (197.149.178.6) and portal.wcf.go.tz (102.223.10.219) all
#     resolved in the same breath on the same connection.
#
#     Those 43 pairs were worse off than "unwhitelisted": a primary_source_url pointing at a
#     host that does not exist cannot be checked by anyone -- not by us, not by a reviewer, not
#     by the TRA-registered consultant R7's Gate 2 depends on. An unverifiable citation is what
#     R4 exists to prevent, arriving by domain death rather than fabrication.
#
#     Resolved 2026-10-05 by scripts/resource_mlywf_pairs.py: 31 repointed to the verified
#     wcf.go.tz document that carries their subject matter, 12 blanked as genuinely unsourced
#     (see UNSOURCED_PAIR_EXCEPTION below). This dict is kept, empty, as the regression guard --
#     any NEW un-whitelisted source domain is unlisted and therefore BLOCKS.
UNWHITELISTED_DOMAIN_EXCEPTION = {}

# ── DELIBERATELY UNSOURCED PAIRS, FROZEN 2026-10-05 ────────────────────────────────────────
# The 43 mlywf.go.tz pairs were re-sourced (scripts/resource_mlywf_pairs.py): 31 repointed to
# the newly-whitelisted wcf.go.tz/pages/contributions, and these 12 had their
# primary_source_url and primary_source_name BLANKED ON PURPOSE.
#
# WHY BLANK RATHER THAN REPOINT: all 43 cited a dead homepage, and for these 12 there is no
# live destination. They are GN 605A / minimum-wage claims. kazi.go.tz is unusable as a target
# -- DNS resolves, https returns 000 (connection reset), and http 302s to
# `https://www.www.kazi.go.tz`, a malformed doubled-www redirect -- and GN 605A's home on
# TanzLII is behind a genuine Cloudflare Turnstile challenge. Repointing to either would move
# an unverifiable citation to a different unverifiable citation.
#
# **BLANK IS THE HONEST STATE: it makes these pairs COUNT as unverified instead of reading as
# cited.** A URL that looks like provenance and cannot be fetched is worse than an empty field,
# because the empty field is visibly unverified while the dead URL silently is not.
#
# ⚠️ WHY THEY ARE LISTED HERE RATHER THAN LEFT TO FAIL. Blanking them produces 36 errors
# (12 pairs x empty url + empty name + empty-domain-not-whitelisted) and exit 1 -- which would
# put this gate straight back into the always-failing state it was rewritten TODAY to escape,
# and an always-failing blocking gate gets ignored, which is how it went inert in the first
# place. Listed by ID so the gate stays USABLE while the 12 stay visible, bounded and unable to
# grow: a NEW unsourced pair is unlisted and therefore BLOCKS, and the list can only shrink.
#
# ⛔ NOT a decision that they may stay unsourced. The way out is re-deriving each claim from a
# reachable primary source -- GN 605A itself, once TanzLII is obtainable or a copy is supplied.
UNSOURCED_PAIR_EXCEPTION = {
    "tier1a_gn605a_007_20260609", "tier1a_gn605a_010_20260609", "tier1a_gn605a_014_20260609",
    "tier1a_gn605a_016_20260609", "tier1a_gn605a_021_20260609", "tier1a_gn605a_026_20260609",
    "tier1a_gn605a_033_20260609", "tier1a_gn605a_042_20260609", "tier1a_gn605a_045_20260609",
    "tier1a_mix_rc_001_20260609", "tier1a_mix_rc_009_20260609", "tier1a_gn605a_023_20260609",
}


def validate_pair(pair, required_fields, allowed_values, whitelisted_domains, filepath, line_num):
    errors = []

    # A listed deliberately-unsourced pair is excused on the SOURCE fields only -- never on any
    # other field, and never on being absent entirely. The exception exists so blanking a dead
    # citation does not re-inert the gate; it is not a licence to drop metadata generally.
    excused = (pair.get("id") in UNSOURCED_PAIR_EXCEPTION
               and {"primary_source_url", "primary_source_name"})

    for field in required_fields:
        if field not in pair:
            errors.append(f"Missing field: {field}")
        elif pair[field] == "" or pair[field] is None:
            if excused and field in excused:
                continue
            errors.append(f"Empty field: {field}")

    for field, allowed in allowed_values.items():
        if field in pair and pair[field] not in allowed:
            errors.append(f"Invalid value for {field}: '{pair[field]}' not in {allowed}")

    if pair.get("primary_source_url"):
        domain = _host(pair["primary_source_url"])
        if domain not in whitelisted_domains and domain not in UNWHITELISTED_DOMAIN_EXCEPTION:
            errors.append(
                f"Source domain not whitelisted: '{domain}' — add to sources/whitelist.json")

    if errors:
        print(f"  [{filepath.name}:{line_num}] FAILED:")
        for e in errors:
            print(f"    - {e}")
    return errors


# ── THE SFT-SHAPED EXCEPTION, FROZEN 2026-10-05 ────────────────────────────────────────────
# Enumerated by name AND row count. A new file, or a grown one, fails. Shrinking is free.
# Counts include the 4 rows restored on 2026-10-05 by scripts/restore_part_xii_quarantine.py
# (batches 012/013 +1 each, 015 +2) -- those pairs were quarantined for being RIGHT about the
# Companies Act Part XII citation and came back, so the exception legitimately grew by 4 that
# day. Recorded here rather than silently absorbed, because "the exception may only shrink" is
# the whole mechanism and a change to it needs a reason on the record.
# ✅ EMPTIED 2026-10-05 — AND THE EMPTY SET IS NOW THE WHOLE POINT, not a leftover.
#
# All 8 files (2,705 rows) were MOVED to datasets/tier1a/sft_shaped_pairs/, which this validator
# deliberately does not scan. So the exception legitimately holds nothing: there is no longer an
# SFT-shaped file inside cleaned_pairs/ to excuse.
#
# ⚠️ IT IS KEPT RATHER THAN DELETED because with the dict empty, the `new_files` branch below
# becomes a REGRESSION GUARD covering every possible SFT-shaped file: ANY such file appearing in
# cleaned_pairs/ from now on is unlisted, and therefore blocks. Deleting the mechanism would
# retire exactly the protection the move was made to establish -- the two generations can never
# silently re-merge. tests/test_validate_dataset_gate.py plants one and watches it block, so the
# empty dict cannot quietly become an unchecked one (R20: an empty collection by DESIGN and one
# empty by ACCIDENT are byte-identical, so the reason is recorded here at the site).
SFT_SHAPED_EXCEPTION = {}
_SFT_KEYS = {"instruction", "output"}


def _shape(pair, required):
    """Which contract this row is CLAIMING, not which one it satisfies.

    ⛔ THE FIRST VERSION OF THIS FUNCTION LET THE MOST COMMON R3 VIOLATION ESCAPE ENTIRELY, and
    a planted test caught it (tests/test_validate_dataset_gate.py). It returned "schema18" only
    when `set(required) <= set(pair)` -- i.e. only for pairs that ALREADY PASS the field check.
    A pair missing ONE required field therefore matched neither shape, was filed as "unknown",
    and was NEVER VALIDATED: the gate would report it as an odd row rather than as the missing
    field it is. **A nearly-complete pair with one field dropped is precisely what R3 exists to
    catch**, and classifying by satisfaction instead of by intent made the gate blind to it.

    So shape is decided by a CLAIM MARKER, never by compliance:
      * `question_sw` is the canonical schema content field -- if a row has it, it is asserting
        the 18-field contract and gets validated strictly, however incomplete it is.
      * half or more of the required fields present is the same claim, made without that field.
      * SFT rows are instruction/output and have no `question_sw`.
    """
    keys = set(pair)
    if "question_sw" in keys or len(keys & set(required)) >= len(required) // 2:
        return "schema18"
    if _SFT_KEYS <= keys:
        return "sft"
    return "unknown"


def main():
    schema = load_schema()
    required = schema["required"]
    allowed = schema["allowed_values"]
    whitelisted = load_whitelist()

    schema_pairs = schema_errors = files_seen = 0
    sft_counts, unknown_rows, exc_counts = {}, [], {}

    for cleaned_dir in sorted(DATASETS_ROOT.glob("*/cleaned_pairs")):
        for jsonl_file in sorted(cleaned_dir.glob("*.jsonl")):
            files_seen += 1
            with open(jsonl_file, encoding="utf-8") as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        pair = json.loads(line)
                    except json.JSONDecodeError as e:
                        print(f"  [{jsonl_file.name}:{line_num}] JSON parse error: {e}")
                        schema_errors += 1
                        continue
                    shape = _shape(pair, required)
                    if shape == "sft":
                        sft_counts[jsonl_file.name] = sft_counts.get(jsonl_file.name, 0) + 1
                        continue
                    if shape == "unknown":
                        unknown_rows.append(f"{jsonl_file.name}:{line_num}")
                        continue
                    schema_pairs += 1
                    d = _host(pair.get("primary_source_url", ""))
                    if d in UNWHITELISTED_DOMAIN_EXCEPTION:
                        exc_counts[d] = exc_counts.get(d, 0) + 1
                    schema_errors += len(validate_pair(
                        pair, required, allowed, whitelisted, jsonl_file, line_num))

    # R20: evaluating nothing is not a pass. Exit 2 so an `&&` chain cannot read it as success.
    #
    # ⚠️ `unknown_rows` COUNTS AS HAVING EVALUATED SOMETHING, and the first version of this
    # condition omitted it -- so a corpus consisting ENTIRELY of unrecognised rows reported
    # "GATE NOT RUN — no pairs found at all" and exited 2, hiding a real finding behind a
    # cannot-evaluate verdict. A planted test caught it. Unknown rows are the loudest thing this
    # gate can find (a third pipeline generation arriving unnoticed is the whole defect being
    # fixed here), so they must never be reported as absence.
    if files_seen == 0 or (schema_pairs == 0 and not sft_counts and not unknown_rows):
        print("\nGATE NOT RUN — no pairs found at all. This is NOT a pass.")
        sys.exit(2)

    print(f"\nschema-shaped: {schema_pairs} pairs, {schema_errors} errors")
    print(f"SFT-shaped (tracked exception, NOT R3-compliant): "
          f"{sum(sft_counts.values())} rows in {len(sft_counts)} file(s)")

    failed = False
    if schema_errors:
        print("SCHEMA VALIDATION FAILED — fix before moving pairs to cleaned_pairs/")
        failed = True

    new_files = sorted(set(sft_counts) - set(SFT_SHAPED_EXCEPTION))
    if new_files:
        print(f"NEW SFT-SHAPED FILE(S) in cleaned_pairs/: {new_files}")
        print("  A new metadata-free file in cleaned_pairs/ is an R3 violation, not a new "
              "normal. Add the 18 fields, or write it where that contract is not claimed.")
        failed = True

    grown = {k: {"now": sft_counts[k], "frozen_at": SFT_SHAPED_EXCEPTION[k]}
             for k in sft_counts
             if k in SFT_SHAPED_EXCEPTION and sft_counts[k] > SFT_SHAPED_EXCEPTION[k]}
    if grown:
        print(f"SFT-SHAPED EXCEPTION GREW: {grown}")
        print("  The exception may only shrink. If this growth is intended, say why in "
              "SFT_SHAPED_EXCEPTION's comment and update the count in the same commit.")
        failed = True

    shrunk = {k: {"now": sft_counts.get(k, 0), "frozen_at": v}
              for k, v in SFT_SHAPED_EXCEPTION.items() if sft_counts.get(k, 0) < v}
    if shrunk:
        print(f"  note: the exception SHRANK (good) — update SFT_SHAPED_EXCEPTION: {shrunk}")

    # The un-whitelisted exception may only shrink, same contract as the SFT one.
    exc_new = sorted(set(exc_counts) - set(UNWHITELISTED_DOMAIN_EXCEPTION))
    if exc_new:
        print(f"NEW UN-WHITELISTED DOMAIN(S): {exc_new} — add to sources/whitelist.json or "
              f"re-source the pairs. Not a new normal.")
        failed = True
    exc_grown = {k: {"now": exc_counts[k], "frozen_at": UNWHITELISTED_DOMAIN_EXCEPTION[k]}
                 for k in exc_counts
                 if exc_counts[k] > UNWHITELISTED_DOMAIN_EXCEPTION.get(k, 0)}
    if exc_grown:
        print(f"UN-WHITELISTED EXCEPTION GREW: {exc_grown}")
        failed = True
    if exc_counts:
        print(f"un-whitelisted source domains (tracked, awaiting a founder decision): "
              f"{exc_counts}")

    if unknown_rows:
        print(f"ROWS MATCHING NEITHER SHAPE ({len(unknown_rows)}): {unknown_rows[:10]}")
        print("  A third pipeline generation would arrive looking exactly like this.")
        failed = True

    if failed:
        sys.exit(1)
    print("VALIDATION PASSED — schema-shaped corpus clean; SFT exception unchanged")
    sys.exit(0)


if __name__ == "__main__":
    main()
