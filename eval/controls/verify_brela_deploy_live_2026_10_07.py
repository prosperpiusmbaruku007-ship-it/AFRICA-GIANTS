# -*- coding: utf-8 -*-
"""R16 LIVE VERIFICATION OF THE BRELA FEE-SCHEDULE DEPLOY (2026-10-07).

WHY THIS HARNESS IS THE ONLY INSTRUMENT AVAILABLE, which is a finding in itself:

  * `chike-inference/modal_app.py` exposes `web_endpoint` and `generate_endpoint` and
    NOTHING ELSE. There is no `/health`, no `CHIKE_BUILD`, no build SHA baked at deploy
    time. R16b's "GET /health returns `build`, confirm it matches the commit you pushed"
    mechanism exists on `chike-whatsapp` ONLY. For the model app there is no SHA to read.
  * `rag_fact_count` is UNCHANGED at 184 across this regen, so the fail-loud index
    contract cannot distinguish the new index from the old one either. That is good for
    availability (no production-down window) and it removes the one count-based signal.
  * `modal app history chike-inference` shows a single v1 deployed 2026-10-07 23:08 EAT,
    eleven minutes after be3691f -- a FRESH app record, so containers are cold by
    construction rather than by waiting out the 300s scaledown. That proves a deploy
    HAPPENED. It says nothing about WHAT IS SERVING.

  => the serving index can only be established by asking the model a question whose
     answer differs before and after. That is R16 step 2, and here it is the whole of
     the available evidence rather than a confirmation of it.

WHAT CHANGED, from the committed artifact rather than memory (R24):
  rag_fetch_verification_2026_10_07.json -- index built from e3e1d0f (contains the
  c8cdbb9 floor), HF 2026-10-07T19:38:04Z, 184x768, dual-committed byte-identical,
  sha256 text=0fb2826558773406 npy=ec29974baa486157.

  row 172 was: "...ikichelewa kuwasilisha ritani ya mwaka: faini ni USD 25 kwa kila mwezi"
  row 172 now: "...faini ni TZS 70,000 kwa kila mwezi au sehemu ya mwezi"

⚠️ THE DISPLACEMENT RISK OF THIS CYCLE IS SPECIFIC AND NAMED IN CLAUDE.md: "Both the
correct figure and the local-company distractor are now in shillings -- until 2026 the
currency itself marked the distinction." Previously a reply quoting USD could not be
confused with the TZS 2,500 local rate. Now both limbs are TZS, so the foreign 70,000
and the local 2,500 can displace each other in a way that was structurally impossible
before. Probes 7 and 8 exist for that and they are the reason this harness is not just
probe 1 twice.

⚠️ POLARITY, NOT PRESENCE. Row 182 deliberately reads "SI USD 220 na SI USD 25 -- hizo
ni ada za zamani" and row 101 reads "SUPERSEDES USD 750". A presence check on the old
values would fail the very rows that carry the correction. Scored through the same
tested `asserted()` helper as verify_row57_deploy_2026_10_06.py.

⚠️ 'part xii' IS A SUBSTRING OF 'part xiii' -- the trap recorded in the Part XII
reversal. Every citation pattern here carries a (?!i) boundary. And the citation is
matched in SWAHILI as well as English: the live reply on 2026-09-05 said "SEHEMU XII",
and an English-only pattern reported False on correct content twice (R34).

QUERIES ARE IMPORTED, NOT RETYPED. Five probes use the regen's own committed
critical_queries, parsed out of kaggle/regenerate_rag_e5.py with the same tested regex
the dry run uses. A harness that re-types the queries it is verifying is a MODEL of the
guard set, which is exactly how the 2026-10-06 dry run passed a package the real run
refused. Each lookup ASSERTS the guard was found, so a renamed guard fails loudly
instead of silently dropping a probe.

STRUCTURAL WRITE DISCIPLINE: artifact rewritten after EVERY row, per-row errors
captured and never fatal. The 2026-08-24 loss was a live run that died 20 rows in on
ConnectionResetError(10054) and wrote nothing, over a Tanzanian link, to this endpoint.
"""
import json
import os
import re
import sys
import urllib.request

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(REPO, "eval", "results", "brela_deploy_verification_2026_10_07.json")
ENDPOINT = "https://prosperpiusmbaruku007--chike-inference-web-endpoint.modal.run"

NEGATED = r"(?:\bsi\b|\bsio\b|\bsiyo\b|\bnot\b|\bhapana\b|\bhakuna\b|\bhaina\b|\bsupersedes\b|\bya\s+zamani\b)[\s:,—-]*(?:TZS\s*|USD\s*)?$"


def token():
    p = os.path.expanduser("~/.chike_modal_token.txt")
    return (os.environ.get("CHIKE_MODAL_TOKEN")
            or (open(p, encoding="utf-8").read().strip() if os.path.exists(p) else ""))


def asserted(pattern, text):
    """Occurrences NOT preceded by a negation. 'SI USD 25' is CORRECT."""
    return [m.group(0) for m in re.finditer(pattern, text, re.I)
            if not re.search(NEGATED, text[max(0, m.start() - 20):m.start()], re.I)]


# ── COMMITTED QUERIES, PARSED FROM THE REGEN ──────────────────────────────────────
_SRC = open(os.path.join(REPO, "kaggle", "regenerate_rag_e5.py"), encoding="utf-8").read()
_COMMITTED = re.findall(
    r"\(\s*'([^']+)'\s*,\s*'query: ([^']+)'\s*,\s*\[([^\]]*)\]\s*\)", _SRC)
assert _COMMITTED, "parsed zero committed critical queries -- the regex no longer matches"


def committed(name_fragment):
    """The committed guard's query, by name fragment. ASSERTS a unique hit: a renamed
    guard must fail loudly, not silently drop a probe (R20's string-match population)."""
    hits = [(n, q) for n, q, _ in _COMMITTED if name_fragment in n]
    assert len(hits) == 1, (
        f"expected exactly 1 committed guard matching {name_fragment!r}, got "
        f"{len(hits)}: {[n for n, _ in hits]}")
    return hits[0][1]


def committed_exact(name):
    """Same, by EXACT name. Needed where a fragment is ambiguous: 'EFD threshold' is a
    prefix of 'EFD threshold, VAT-unregistered (nat_36 displacement guard)', so the
    fragment form would assert on 2 hits and abort."""
    hits = [q for n, q, _ in _COMMITTED if n == name]
    assert len(hits) == 1, (
        f"expected exactly 1 committed guard named {name!r}, got {len(hits)}")
    return hits[0]


PROBES = [
    # ── PRIMARY: the row this cycle exists for ────────────────────────────────────
    {
        "id": "row172_primary_ext15",
        "proves": "PRIMARY. Row 172 must serve TZS 70,000 and must no longer serve USD 25. "
                  "This is the question ext_15 asks, and ext_15's verdict was booked "
                  "against the model on this figure alone.",
        "source": "regen critical_queries 'BRELA foreign late-filing fee' (== ext_15 verbatim)",
        "question": committed("BRELA foreign late-filing fee"),
        "baseline_committed_row": "row 172 @ aef6756 = '...faini ni USD 25 kwa kila mwezi'",
        "must_match": r"70,?000",
        "must_not_assert": r"USD\s*25\b|\$\s*25\b|dola\s*25\b",
        "observe": r"\bsehemu\s*(?:ya\s*)?xii(?!i)|\bpart\s*xii(?!i)|\bkifungu\s*12\b",
        "note": "ext_15 is RE_RUN_REQUIRED (PROGRESS.md 2026-10-07). Its figure limb is now "
                "resolved at portal tier, so this probe is the re-run. The citation limb is "
                "OBSERVED, not scored -- the regen already guards it separately, and the "
                "model omitting a citation is not the defect this cycle shipped.",
    },
    {
        "id": "row172_citation_not_reversed",
        "proves": "The reversed citation must not reappear. 'Part XIII, ss.320-328' was "
                  "enforced for five weeks by nine sites including a build gate that would "
                  "have REFUSED to ship the fix.",
        "source": "CLAUDE.md Part XII reversal; Cap.212 R.E.2023 s.437(1) read directly",
        "question": "Kampuni ya kigeni inayofanya biashara Tanzania inasimamiwa na sehemu "
                    "ipi ya Companies Act?",
        "must_not_assert": r"\bsehemu\s*(?:ya\s*)?xiii\b|\bpart\s*xiii\b|ss\.?\s*320\s*-\s*328",
        "observe": r"\bsehemu\s*(?:ya\s*)?xii(?!i)|\bpart\s*xii(?!i)|437|447",
        "note": "Asymmetric by design: the correct citation is NOT required (the model may "
                "answer without one), but asserting the REVERSED one fails. Requiring it "
                "would duplicate the regen's own Part XII guard and would punish a correct "
                "reply that happens to omit the numeral.",
    },
    {
        "id": "row172_second_phrasing",
        "proves": "R33: the figure survives a SECOND phrasing. A pass on one wording is a "
                  "statement about that wording -- 42 of 42 probes across two variation axes "
                  "leaked past a cue list that held the exact strings.",
        "source": "authored paraphrase of row 172's own subject, deliberately not the guard query",
        "question": "Faini ya kuchelewa kuwasilisha ritani ya mwaka kwa kampuni ya kigeni ni "
                    "shilingi ngapi kwa mwezi?",
        "must_match": r"70,?000",
        "must_not_assert": r"USD\s*25\b|\$\s*25\b|dola\s*25\b",
        "note": "Same claim, no shared content words with the guard query beyond the subject.",
    },
    # ── ROW 181: the share-capital ladder and the no-share-capital fee ────────────
    {
        "id": "row181_nine_bands",
        "limb": "answer_quality",
        "proves": "Row 181's ladder went from FIVE bands with an open-ended top to NINE "
                  "closed bands. 'Band 5' no longer means 'above TZS 50,000,000' -- it was "
                  "re-scoped, not merely re-priced, so a reply using the old top band is "
                  "wrong about which band the user is even in.",
        "source": "regen critical_queries 'BRELA share-capital ladder now has nine bands'",
        "question": committed("BRELA share-capital ladder now has nine bands"),
        "must_match": r"600,?000",
        "must_not_assert": r"440,?000",
        "note": "TZS 2,000,000,000 falls in band 8 (1bn-10bn) = TZS 600,000. Under the June "
                "five-band table the same company read as the open-ended top at 440,000.",
        # ⛔ CLASSIFIED answer_quality, NOT deploy, AND THE EVIDENCE FOR THAT IS INSIDE THIS
        # HARNESS RATHER THAN ASSERTED ABOUT IT. row181_no_share_capital reads the SAME index
        # row 181 and returns the NEW 500,000 (superseding 300,000), so row 181 is
        # demonstrably live. A failure here therefore cannot be staleness.
        #
        # STEP ZERO WAS RUN BEFORE THIS WAS CLASSIFIED (CLAUDE.md: measure the fact's rank
        # first, and at rank 1 the defect is in generation and every wording hour is wasted).
        # Measured 2026-10-08 against the SERVED index with the production embedder:
        #   this exact query          -> row 181 at RANK 1 (score 0.9167)
        #   a natural paraphrase      -> row 181 at RANK 3
        #   the no-share-capital ask  -> row 181 at RANK 1
        # The correct ladder, including 'zaidi ya TZS 1,000,000,000 hadi TZS 10,000,000,000 ni
        # TZS 600,000', was IN CONTEXT. The live reply was "Ada ya kusajili kampuni yenye
        # mtaji wa hisa unaozidi TZS 5,000,000 ni TZS 290,000" -- the >20M-50M band, with its
        # floor misstated as 5,000,000. There is no retrieval headroom left to take.
        #
        # THIRD MEMBER OF "THE CORRECT FACT AT RANK 1 AND THE WRONG VALUE EMITTED", after
        # eval_347 and the GN487A term bleed. R19 says it is BUILDABLE: picking a row from a
        # fixed fee table is a CONSTANT comparison, not a derived quantity -- no lawful
        # transformation of the user's 2,000,000,000 makes 290,000 true. Recorded for the next
        # cycle, deliberately not built here.
        "_rank_measured": {"query_as_asked": 1, "natural_paraphrase": 3,
                           "no_share_capital_sibling": 1,
                           "measured": "2026-10-08, served index, intfloat/multilingual-e5-base",
                           "implication": "rank 1 => generation defect, not wording (CLAUDE.md "
                                          "step zero). Band selection over a 9-band table is "
                                          "arithmetic the fact path does not do."},
    },
    {
        "id": "row181_no_share_capital",
        "proves": "The SUPERSESSION that was recorded as a DISPUTE for five weeks: a company "
                  "without share capital is TZS 500,000, not TZS 300,000. Two readings of "
                  "one URL four months apart, both read correctly.",
        "source": "CLAUDE.md BRELA block, item 2; index row 181",
        "question": "Kampuni yangu haina mtaji wa hisa. Ada ya kusajili ni shilingi ngapi?",
        "must_match": r"500,?000",
        "must_not_assert": r"300,?000",
        "note": "The cleanest single-figure test of whether the NEW schedule is serving: one "
                "number, superseded value unambiguous, no arithmetic.",
    },
    # ── ROW 182 / ROW 101: the USD -> TZS redenomination ──────────────────────────
    {
        "id": "row182_foreign_doc_filing",
        "proves": "The redenominated foreign-company filing fees: TZS 600,000, superseding "
                  "USD 220. An entire block switching currency inside a four-month window is "
                  "a substantive amendment, not a rounding.",
        "source": "index row 182 (item 15(ii)/(iii))",
        "question": "Kampuni ya kigeni inawasilisha nyaraka kwa Msajili BRELA. Ada ni kiasi gani?",
        "must_match": r"600,?000",
        "must_not_assert": r"USD\s*220\b|\$\s*220\b|dola\s*220\b",
        "note": "Row 182 carries 'SI USD 220 na SI USD 25 -- hizo ni ada za zamani', so the "
                "old values are retrievable UNDER A NEGATION. Polarity-scored.",
    },
    {
        "id": "row101_charter_copy",
        "proves": "The largest redenomination on the page: certified copy of the foreign "
                  "company's constitution, TZS 2,000,000, superseding USD 750. Row 101 is a "
                  "standalone row and was not covered by any committed critical query.",
        "source": "index row 101 (item 15(i))",
        "question": "Ada ya kuwasilisha nakala iliyothibitishwa ya katiba ya kampuni ya nje "
                    "ni shilingi ngapi?",
        "must_match": r"2,?000,?000",
        "must_not_assert": r"USD\s*750\b|\$\s*750\b|dola\s*750\b",
        "note": "Row 101's own text ends 'SUPERSEDES USD 750 (published as at 2026-06-30)', "
                "which is why 'supersedes' is in the NEGATED alternation.",
    },
    # ── NEGATIVES: what must NOT have moved ───────────────────────────────────────
    {
        "id": "negative_local_late_penalty_2500",
        "proves": "THE DISPLACEMENT RISK OF THIS CYCLE, and the reason this harness is not "
                  "probe 1 twice. A LOCAL company's late-filing penalty is TZS 2,500/month "
                  "(row 99). Until 2026 the foreign figure was in USD and could not be "
                  "confused with it; both limbs are now TZS.",
        "source": "index row 99; CLAUDE.md 'Both the correct figure and the local-company "
                  "distractor are now in shillings'",
        "question": "Kampuni yangu ya hapa Tanzania imechelewa kuwasilisha ritani ya mwaka. "
                    "Faini ni shilingi ngapi kwa mwezi?",
        "must_match": r"2,?500",
        "must_not_assert": r"70,?000",
        "note": "If this fails, row 172's text has displaced row 99 and the fix bought a new "
                "wrong answer. Narrow row 172, do not widen row 99.",
    },
    {
        "id": "negative_annual_return_fee_22000",
        "proves": "The annual return FILING FEE is unchanged at TZS 22,000 (item 7). A penalty "
                  "correction must not leak into the fee for the same filing.",
        "source": "regen critical_queries 'BRELA annual return'",
        "question": committed("BRELA annual return"),
        "must_match": r"22,?000",
        "must_not_assert": r"70,?000",
        "note": "Same document, same obligation, different quantity -- the adjacency that "
                "makes this the second most likely displacement victim after row 99.",
    },
    {
        "id": "negative_nssf_fine_unchanged",
        "proves": "The Cap.50 corrections shipped 2026-10-05 must be exactly where they were. "
                  "A 100x understatement (TZS 100,000 for s.76(1)'s ten million) was live in "
                  "row 159 and four training rows.",
        "source": "regen critical_queries 'NSSF fine ceiling is ten million'",
        "question": committed("NSSF fine ceiling is ten million"),
        # ⛔ THE must_match WAS WRONG ON THE FIRST RUN AND THE MODEL WAS RIGHT. R26's second
        # half: when a control does not fire, eliminate the specimen before recording a defect.
        # The live reply was "adhabu ya asilimia 5 kwa kila mwezi wa ucheleweshaji", which is
        # `nssf_penalty` / `unpaid_contribution_penalty_rate` -- Cap.50 s.14(3), statute-tier
        # CONFIRMED, read from two byte-identical routes on 2026-10-05. It is a LOCKED FACT.
        #
        # The question ("Nisipolipa michango ya NSSF kabisa, nitatozwa faini ya kiasi gani?")
        # licenses TWO correct statutory answers and does not choose between them: s.14(3)'s
        # 5%/month surcharge on the unpaid contribution, and s.76(1)'s TZS 10,000,000 maximum
        # fine on conviction. "Nisipolipa michango" points at the surcharge if anything.
        # Requiring only the ceiling made a correct reply fail -- the R26 shape "an assertion
        # form outside the guard's designed scope", and specifically: this is a RETRIEVAL
        # guard's query, whose committed job is that the fact is reachable at rank <=3. Asking
        # the MODEL to emit that limb is a different claim, and regenerate_rag_e5.py says so
        # itself about another guard: "a retrieval guard can pass while the reply says
        # something else".
        #
        # The probe is KEPT because its load-bearing limb is must_not_assert: the 100x
        # understatement (TZS 100,000 for s.76(1)'s ten million) was live in row 159 and four
        # training rows, and that limb PASSED on the first run.
        "must_match": r"10,?000,?000|milioni\s+kumi|asilimia\s*5\b|5\s*%",
        "must_not_assert": r"100[,.]?000(?![,.\d])|laki\s+moja",
        "note": "Two cycles back. Confirms the regen did not regress an earlier ship. Accepts "
                "EITHER locked statutory limb (s.76(1) ceiling or s.14(3) 5%/month) -- the "
                "question does not disambiguate, and both are primary-sourced.",
    },
    {
        "id": "negative_row57_efd_unchanged",
        "proves": "YESTERDAY's ship must survive. Row 57 stopped asserting the fabricated TZS "
                  "11,000,000 EFD threshold on 2026-10-06, after five and a half weeks live.",
        "source": "regen critical_queries 'EFD threshold' (== eval_347 verbatim)",
        "question": committed_exact("EFD threshold"),
        "must_not_assert": r"11[,.]?000[,.]?000|milioni\s+kumi\s+na\s+moja",
        # ⛔ MY OWN HARNESS DEFECT ON THE FIRST RUN, AND THE NOTE BELOW ALREADY DESCRIBED THE
        # CORRECT HANDLING WHILE THE CODE DID THE OPPOSITE. D-FIDELITY-7 was wired 2026-10-06
        # and BLANKS a flagged body on the fact path, so the live reply is the guard's
        # replacement copy: "jibu langu la awali lilitoa kiwango ... ambacho sikiwezi
        # kukithibitisha, hivyo sitalitumia. Sitakisii kiwango kingine." Requiring the
        # no-threshold claim scored the GUARD WORKING as a BRELA regression.
        #
        # So the withheld-answer copy is accepted here, and the fact that it IS a withheld
        # answer is recorded on the row rather than hidden by the pass: `answer_withheld`.
        # CLAUDE.md's two-bar rule -- a guard stops the wrong answer and never produces the
        # right one, so this is an A1 win and an OPEN A2 debt, and netting them would report
        # the work as having done nothing. eval_347 still owes "EFD applies regardless of
        # turnover", which is a fact-path job, not a guard job.
        "must_match": r"haina\s+kizingiti|hakuna\s+kizingiti|bila\s+kujali|hakitumiki"
                      r"|sikiwezi\s+kukithibitisha|sitakisii|sitalitumia",
        "withheld_signature": r"sikiwezi\s+kukithibitisha|sitakisii|sitalitumia",
        "note": "D-FIDELITY-7 is wired, so a flagged body is BLANKED on the fact path. A "
                "withheld answer here is the guard working, not this deploy failing -- it is "
                "recorded as such rather than scored as a BRELA regression.",
    },
    {
        "id": "config_only_phrase",
        "proves": "CONFIG LOADING, separately from code. The 2026-08-07 diagnostic that "
                  "distinguishes a config failure from a stale warm container: these phrases "
                  "live in chike_config.json and NOT in the hardcoded fallback.",
        "source": "chike_config.json ooc_phrases (config-only)",
        "question": "Nataka kuuza kiwanja changu, kodi ya mapato ni kiasi gani?",
        "must_match": r"sina uhakika|thibitisha|siwezi|nje ya",
        "note": "Land sale is out of corpus by design. Proves the container reloaded config, "
                "which is the one thing a fresh app record should guarantee and the 2026-08-07 "
                "incident proved a successful deploy does not.",
    },
]


def ask(question, tok, timeout=300):
    req = urllib.request.Request(
        f"{ENDPOINT}?token={tok}",
        data=json.dumps({"message": question}).encode("utf-8"),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def save(rows):
    failed = [r for r in rows if r.get("verdict") == "FAIL"]
    errored = [r for r in rows if r.get("verdict") == "ERROR"]
    # ── TWO LIMBS, NOT ONE ────────────────────────────────────────────────────────
    # "Did the new index reach production?" and "is every reply correct?" are different
    # questions and the first run conflated them: row181_nine_bands failed on BAND
    # SELECTION while its own sibling proved row 181 was live, and a single verdict read
    # that as the deploy being unverified. CLAUDE.md's two-bar rule applied to a harness:
    # a blended number describes neither limb. The exit code is still conservative --
    # non-zero if EITHER limb has a failure -- so separating them cannot be used to wave
    # an answer-quality defect through.
    deploy_rows = [r for r in rows if r.get("limb", "deploy") == "deploy"]
    quality_rows = [r for r in rows if r.get("limb") == "answer_quality"]
    deploy_bad = [r for r in deploy_rows if r.get("verdict") in ("FAIL", "ERROR")]
    quality_bad = [r for r in quality_rows if r.get("verdict") in ("FAIL", "ERROR")]
    payload = {
        "_what": "R16 live verification of the BRELA fee-schedule deploy (2026-10-07).",
        "_endpoint": ENDPOINT,
        "_deployed_index": "184 rows, HF 2026-10-07T19:38:04Z built from e3e1d0f, "
                           "dual-committed byte-identical (text 0fb2826558773406, "
                           "npy ec29974baa486157). rag_fact_count unchanged at 184.",
        "_deploy_evidence": "modal app history chike-inference -> single v1, 2026-10-07 23:08 "
                            "EAT, eleven minutes after be3691f. A FRESH app record, so "
                            "containers are cold by construction rather than by waiting out "
                            "scaledown. Commit column EMPTY -- the inference deploy passes no "
                            "CHIKE_BUILD.",
        "_why_no_health_check": "chike-inference/modal_app.py exposes web_endpoint and "
                                "generate_endpoint and nothing else. There is NO /health and no "
                                "build SHA on this app -- R16b's build mechanism is "
                                "chike-whatsapp only. And rag_fact_count is unchanged at 184, "
                                "so the index contract cannot distinguish the builds either. "
                                "A content probe is not a confirmation here; it is the whole "
                                "of the available evidence.",
        "_scoring": "must_not_assert is POLARITY-checked. Rows 182 and 101 deliberately name "
                    "USD 25 / USD 220 / USD 750 in order to reject them; a presence check "
                    "would fail the rows carrying the correction. All citation patterns carry "
                    "a (?!i) boundary because 'part xii' is a substring of 'part xiii', and "
                    "match Swahili ('sehemu ya XII') as well as English.",
        "_queries_imported": f"{len(_COMMITTED)} committed critical queries parsed from "
                             "kaggle/regenerate_rag_e5.py; 5 probes use them verbatim. Each "
                             "lookup asserts a unique hit, so a renamed guard fails loudly.",
        "_write_discipline": "rewritten after EVERY row; per-row errors captured, never fatal",
        "_two_limbs": "verdict is decided by the DEPLOY limb only -- did the new index reach "
                      "production. answer_quality failures are reported separately and still "
                      "force a non-zero exit, but they do not falsify the deploy: "
                      "row181_no_share_capital and row181_nine_bands read the SAME index row, "
                      "so a pass on one proves the row is live and a fail on the other is "
                      "about generation.",
        "totals": {"probes": len(PROBES), "run": len(rows),
                   "pass": len([r for r in rows if r.get("verdict") == "PASS"]),
                   "fail": len(failed), "error": len(errored),
                   "deploy_limb": f"{len(deploy_rows) - len(deploy_bad)}/{len(deploy_rows)}",
                   "answer_quality_limb": f"{len(quality_rows) - len(quality_bad)}/"
                                          f"{len(quality_rows)}"},
        "verdict": ("DEPLOY VERIFIED" if rows and not deploy_bad
                    and len(rows) == len(PROBES) else "INCOMPLETE OR FAILED"),
        "answer_quality_findings": [
            {"id": r["id"], "reply": r.get("reply"), "checks": r.get("checks"),
             "rank_measured": r.get("_rank_measured")}
            for r in quality_bad],
        "answer_withheld_by_guard": [r["id"] for r in rows if r.get("answer_withheld")],
        "rows": rows,
    }
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
    return payload


def main():
    tok = token()
    if not tok:
        print("NO TOKEN -- cannot verify live. This is NOT a pass (R16).")
        sys.exit(2)

    rows = []
    for p in PROBES:
        row = {k: p[k] for k in ("id", "limb", "proves", "source", "question", "note",
                                 "baseline_committed_row", "_rank_measured") if k in p}
        row.setdefault("limb", "deploy")
        try:
            resp = ask(p["question"], tok)
            reply = str(resp.get("reply") or resp.get("answer") or resp)
            row["reply"] = reply
            checks = {}
            if p.get("must_match"):
                checks["must_match"] = bool(re.search(p["must_match"], reply, re.I))
            if p.get("must_not_assert"):
                bad = asserted(p["must_not_assert"], reply)
                checks["superseded_value_not_asserted"] = not bad
                if bad:
                    row["asserted_superseded"] = bad
                row["mentions_under_negation"] = bool(
                    re.search(p["must_not_assert"], reply, re.I)) and not bad
            if p.get("observe"):
                row["observed"] = bool(re.search(p["observe"], reply, re.I))
            if p.get("withheld_signature"):
                # A pass earned by the guard blanking the body is recorded as such, so the
                # open A2 debt stays visible instead of being absorbed into a green row.
                row["answer_withheld"] = bool(
                    re.search(p["withheld_signature"], reply, re.I))
            row["checks"] = checks
            row["verdict"] = "PASS" if all(checks.values()) else "FAIL"
        except Exception as exc:
            row["verdict"] = "ERROR"
            row["error"] = f"{type(exc).__name__}: {str(exc)[:200]}"
        rows.append(row)
        save(rows)
        print(f"[{row['verdict']:5s}] {row['id']}")
        if row.get("reply"):
            print(f"        {' '.join(row['reply'].split())[:230]}")
        if row.get("checks"):
            extra = ""
            if "observed" in row:
                extra += f" observed={row['observed']}"
            if row.get("mentions_under_negation"):
                extra += " (old value mentioned under a negation -- correct)"
            print(f"        checks={row['checks']}{extra}")
        if row.get("asserted_superseded"):
            print(f"        ⛔ ASSERTED SUPERSEDED: {row['asserted_superseded']}")
        if row.get("error"):
            print(f"        {row['error']}")

    payload = save(rows)
    print(f"\n{payload['totals']}")
    print(f"VERDICT: {payload['verdict']}")
    for f in payload["answer_quality_findings"]:
        print(f"  ANSWER-QUALITY FINDING (does NOT falsify the deploy): {f['id']}")
    for i in payload["answer_withheld_by_guard"]:
        print(f"  ANSWER WITHHELD BY GUARD (A1 win, A2 still owed): {i}")
    print(f"wrote {OUT}")
    # Non-zero if EITHER limb has a failure. A deploy verdict alone is not licence to pass.
    ok = (payload["verdict"] == "DEPLOY VERIFIED"
          and not payload["answer_quality_findings"])
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
