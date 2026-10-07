# -*- coding: utf-8 -*-
"""THE PAYLOAD GATES FOR AN R15 RAG REGEN — ONE DEFINITION, EXECUTED BY BOTH RUNS.

⛔ WHY THIS FILE EXISTS, AND IT IS A DRY-RUN DEFECT, NOT A GATE DEFECT.

On 2026-10-06 the local dry run (eval/index_quality/dryrun_regen_2026_10_06.py) reported
`VERDICT: SAFE TO RUN` — 0 displacement across 40 committed guards, both new guards hit, 184 -> 184
rows. The Kaggle regen then aborted, on the same commit, on a payload gate:

    [FATAL] brela_foreign_late_filing_penalty ASSERTS the superseded value ['USD 25']

Nothing uploaded, so the gate earned its place. But the founder's question is the one that matters:
how did the dry run pass? **Because it did not execute these gates at all.** It hand-wrote payload
assertions for the two rows whoever wrote it remembered changing, and a third row had moved.

That is R33 in the validator layer: a check authored by the author of the change, scoped to the
change the author had in mind. And it is sharper than a plain omission, because the dry run ALREADY
KNEW not to re-derive the regen's tables — it parses ACCEPTED_AMBIGUOUS and the committed critical
queries straight out of regenerate_rag_e5.py precisely so the two cannot disagree. It applied that
discipline to two tables and hand-wrote the third.

**A dry run that cannot see the gate the real run enforces is not a dry run of that run.** So the
gates moved here, verbatim, and both callers import them:

    kaggle/regenerate_rag_e5.py                      — the real run, on Kaggle
    eval/index_quality/dryrun_regen_2026_10_06.py    — the local dry run

⚠️ THE MOVE IS PURE. Every line below is byte-identical to what ran on Kaggle, including the
commentary, which is the institutional record of four distinct defect classes and one inverted
gate. The only change is that `fact_keys` and `fact_texts_to_embed` arrive as parameters instead of
module globals — asserted by the extractor that performed the move: the block referenced no other
free name.

⚠️ AND THE IMPORT MUST ABORT, NEVER SKIP. This file is now a hard dependency of the regen and is
listed in its SOURCE_FILES. A clone or raw-fetch that lacks it must fail loudly: a regen that
silently runs with no payload gates is the inert-control shape this project keeps finding — the
run would succeed, print nothing missing, and upload whatever it built. R36's lesson in the gate
layer: ask where the control ACTS, not whether it works.
"""
import re


def run_payload_gates(fact_keys, fact_texts_to_embed):
    """Assert the built index carries the payload this regen exists to ship.

    Raises AssertionError / SystemExit on any failure. Returns the number of gates exercised, so a
    caller can refuse a run in which the gate count silently fell to zero.
    """
    _gates_run = 0
    # ── PAYLOAD GATE: is the change THIS RUN EXISTS FOR actually in the built texts? ─────
    # HARD, and hard is defensible here in a way the correction-sync gate below is not. That
    # gate is a LEXICAL match over free text whose own first-run false-positive rate was 7 of 8,
    # so a hard fail there could block a regen over a CORRECT fact (R21: a mechanism that can
    # refuse is expensive to get wrong). This gate asserts an exact string in text THIS REPO
    # AUTHORS, in a row identified by KEY, not by pattern matching. There is no sentence it can
    # misread: either the corrected citation is in the row or it is not.
    #
    # WHY IT EXISTS (2026-09-24). `brela_foreign_late_filing_penalty` said "(Section XII)" for
    # the entire life of the corpus. The fact was corrected 2026-08-31, the training corpus was
    # swept 2026-09-01, CLAUDE.md was fixed -- and the string still shipped, because this row is
    # hand-authored in precompute_rag_embeddings.py and is NOT derived from locked_facts.json.
    # It reached a live user reply on 2026-09-05 (ext_15). THREE standing checks were green on
    # it: check_facts_index_sync (content-shaped -- the USD 25 figure was present),
    # check_rag_index_freshness (time-shaped -- the index HAD been rebuilt after the correction;
    # the string survived a regeneration), and check_correction_sync (blind, because its
    # patterns assumed English word order and this row is Swahili, and because it resolves each
    # fact to its OWN row while the patterns live under a different key).
    #
    # So this is deliberately NOT another general detector. It is a per-run payload assertion:
    # name the exact thing this regen is for and refuse to upload without it. The cost of
    # carrying it forward is one line per shipped correction; the cost of not having it was five
    # weeks of a wrong citation served under three green checks.
    #
    # ⛔⛔ THIS GATE WAS INVERTED ON 2026-10-05, AND IT IS THE MOST IMPORTANT ENTRY IN THIS FILE.
    # As written on 2026-09-24 it asserted `'part xiii' in row` and refused to upload without it.
    # The Companies Act Cap.212 R.E. 2023, read directly (brela.go.tz, HTTP 200, 394pp, 2026-10-04),
    # says `PART XII COMPANIES INCORPORATED OUTSIDE TANZANIA`, ss.437-447. So this gate would have
    # REFUSED TO BUILD THE CORRECTED INDEX and demanded the wrong citation as its entry price.
    #
    # Everything in the paragraph above it is well-reasoned: it is keyed, not lexical; it fails
    # loudly on absence rather than passing by it; it was built in direct response to a real live
    # defect. NONE OF THAT PROTECTED IT, because a control can only be as right as the fact it
    # encodes -- and this one encoded a reversed fact. A better-built gate on a wrong premise is
    # strictly WORSE than a weak one: it has more power to keep the error in place. That is the
    # whole shape of the Part XII reversal in one control.
    #
    # ⚠️ SUBSTRING TRAP, and it is why this uses a regex and not `in`: 'part xii' IS A SUBSTRING OF
    # 'part xiii'. A naive `'part xii' in row.lower()` passes on the STALE text and would have made
    # the inverted gate vacuous in exactly the R20 way -- a check that cannot fail. The `(?!i)`
    # boundary is the same device act_section_12's wrong_patterns already needed for the same reason.
    _XII_KEY = 'brela_foreign_late_filing_penalty'
    if _XII_KEY in fact_keys:
        _xii_row = fact_texts_to_embed[fact_keys.index(_XII_KEY)]
        _stale_xiii = re.search(r'part\s*xiii\b|ss?\.?\s*320\s*[-–]\s*328', _xii_row, re.I)
        assert not _stale_xiii, (
            f'[FATAL] {_XII_KEY} carries the REVERSED citation "Part XIII / ss.320-328":\n'
            f'  {_xii_row}\n'
            f'The Act says PART XII, ss.437-447 (s.437(1), Cap.212 R.E.2023). The clone predates '
            f'the 2026-10-05 reversal, or it was reverted. Refusing to build.')
        assert re.search(r'part\s*xii\b(?!i)', _xii_row, re.I), (
            f'[FATAL] {_XII_KEY} no longer names Part XII:\n  {_xii_row}\n'
            f'The reversed citation is gone but the correct one is missing -- a different defect, '
            f'not a pass.')
        _gates_run += 1
        print(f'[OK] payload gate: {_XII_KEY} carries Part XII, no "Part XIII"/ss.320-328')
    else:
        # NOT a silent skip. If the key is renamed or dropped, this gate stops watching the
        # thing it was built for and must say so rather than passing by absence (R20: a check
        # that cannot fail is worse than the gap it replaced).
        raise SystemExit(
            f'[FATAL] {_XII_KEY} is not in the built fact set at all. Either it was renamed '
            f'(update this gate) or dropped (a regression). A payload gate that silently stops '
            f'applying is exactly the inert-control shape this project keeps finding.')

    # Nothing anywhere else in the built texts may carry the stale citation either -- the row
    # above is the one known instance, not a guarantee it is the only one.
    # INVERTED 2026-10-05 with the gate above. This swept for "Section XII" across every built row
    # and refused to upload if it found any -- i.e. it banned the CORRECT numeral corpus-wide. It now
    # sweeps for the reversed citation instead. Note it never fired in its original form on anything
    # but the one known row, so inverting it loses no coverage.
    _stale = [k for k, t in zip(fact_keys, fact_texts_to_embed)
              if re.search(r'part\s*xiii\b.{0,60}(?:foreign|kigeni)|'
                           r'(?:foreign|kigeni).{0,60}part\s*xiii\b|'
                           r'ss?\.?\s*320\s*[-–]\s*328', t, re.I)]
    assert not _stale, (f'[FATAL] the reversed "Part XIII / ss.320-328" foreign-company citation is '
                        f'still present in: {_stale}. The Act says PART XII, ss.437-447.')
    _gates_run += 1
    print('[OK] payload gate: no row in the built index carries the reversed Part XIII citation')

    # SECOND PAYLOAD IN THIS RUN. 9c43143 (2026-09-05) also reworded `minimum_turnover_tax`, and
    # it has been sitting unshipped since: "kodi ya chini (AMT) ya asilimia 1" was intended as
    # "the MINIMUM tax (AMT), of 1%" but "ya chini ya asilimia 1" is equally the ordinary Swahili
    # for "LESS THAN 1%", and a live reply resolved it the wrong way -- a rate a user could act on
    # wrongly (eval/controls/corporate_domain_live_probe_2026_09_05.json). Gated here for the same
    # reason as the citation above: this regen is the first to carry it, so "did it actually get
    # in" is a question worth answering before upload rather than after a user finds out.
    _AMT_KEY = 'minimum_turnover_tax'
    if _AMT_KEY in fact_keys:
        _amt_row = fact_texts_to_embed[fact_keys.index(_AMT_KEY)]
        assert 'kodi ya chini' not in _amt_row.lower(), (
            f'[FATAL] {_AMT_KEY} still carries the ambiguous "kodi ya chini" gloss, which reads '
            f'as "less than 1%":\n  {_amt_row}')
        assert 'alternative minimum tax' in _amt_row.lower(), (
            f'[FATAL] {_AMT_KEY} no longer names Alternative Minimum Tax:\n  {_amt_row}')
        _gates_run += 1
        print(f'[OK] payload gate: {_AMT_KEY} reworded, ambiguous gloss gone')
    else:
        raise SystemExit(f'[FATAL] {_AMT_KEY} absent from the built fact set -- gate cannot apply.')

    # THIRD PAYLOAD (2026-09-24, ext_31). Carried forward at the stated cost of one line per
    # shipped correction. DIFFERENT DEFECT CLASS FROM THE TWO ABOVE, and that is the point worth
    # noting: both of those shipped a WRONG STRING. This one's fact was entirely CORRECT and
    # still failed, because the served row was the `key: value` fallback -- English-first and
    # LABEL-LED ('OSHA safety officer threshold: Occupational Health and Safety Act Cap.297
    # s.11(1)...'). It measured at BOUNDARY (rank 4-16) for the real user phrasing 'Kiwandani
    # kwetu tuna wafanyakazi zaidi ya ishirini. Ni lazima tuwe na afisa maalum wa usalama
    # kazini?' while the live reply asserted exactly the phrasing the fact's own text forbids.
    #
    # So the gate asserts REACHABILITY-SHAPED content, not correctness: that the row now LEADS
    # with the asker's vocabulary rather than the regulatory label. A payload gate that only ever
    # checked for wrong strings would pass this row in both its broken and its fixed state.
    _OSHA_REP_KEY = 'OSHA_safety_officer_threshold'
    if _OSHA_REP_KEY in fact_keys:
        _rep_row = fact_texts_to_embed[fact_keys.index(_OSHA_REP_KEY)]
        assert not _rep_row.lower().startswith('osha safety officer threshold:'), (
            f'[FATAL] {_OSHA_REP_KEY} is still the label-led `key: value` fallback:\n  '
            f'{_rep_row[:160]}\nThis regen exists to replace it with the ask-aligned Swahili '
            f'text. The clone predates bb2c1ff, or the CONCISE_BILINGUAL_FACTS entry was '
            f'removed.')
        assert _rep_row.lower().startswith('afisa wa usalama kazini'), (
            f'[FATAL] {_OSHA_REP_KEY} no longer LEADS with the asker\'s vocabulary:\n  '
            f'{_rep_row[:160]}\nLeading with the user\'s words is the entire mechanism here '
            f'(the nat_36 lever, rank 17 -> 1). A row that merely CONTAINS them is not the fix.')
        assert 'cap.297' not in _rep_row.lower() and 's.11' not in _rep_row.lower(), (
            f'[FATAL] {_OSHA_REP_KEY} carries a statutory citation in the EMBEDDED text:\n  '
            f'{_rep_row[:160]}\nThe standing rule in precompute_rag_embeddings.py forbids this '
            f'-- folding citations in cost nat_05 ranks 24 -> 59. Citations belong in '
            f'locked_facts.json, which R13 reads directly.')
        assert "NOT a professionally hired/dedicated 'safety officer'" in _rep_row, (
            f'[FATAL] {_OSHA_REP_KEY} lost the ext_31 needle:\n  {_rep_row[:160]}\n'
            f'eval/grounding/bucket_e_reach_probes_014.jsonl matches on that exact substring. '
            f'Dropping it silently breaks the fixture that MEASURED this defect, so the next '
            f'reach run would report on a probe that can no longer resolve.')
        _gates_run += 1
        print(f'[OK] payload gate: {_OSHA_REP_KEY} is ask-aligned, uncited, needle intact')
    else:
        raise SystemExit(
            f'[FATAL] {_OSHA_REP_KEY} absent from the built fact set -- gate cannot apply.')

    # FOURTH PAYLOAD (2026-10-05, rent_wht_rate). A FOURTH DEFECT CLASS, and naming it is the
    # point: the first two shipped a WRONG STRING, the third shipped CORRECT TEXT THAT WAS NEVER
    # REACHED, and this one was NEVER IN THE INDEX AT ALL. Measured, not assumed: the deployed
    # 183-row index contains ZERO rows mentioning pango/rental/rent, so `rent_wht_rate` has been
    # unretrievable for its entire life since being locked in b5bb445 -- the rate engine was fixed
    # (1f32973, 0/5 -> 5/5 natural reach) while the FACT behind it could not be retrieved.
    #
    # The gate asserts presence, ask-alignment and both qualifiers, because the two qualifiers ARE
    # the defect this fact exists to prevent: a residency split that does not exist, and a
    # withholding duty asserted against someone who is not an agent.
    _RENT_KEY = 'rent_wht_rate'
    if _RENT_KEY in fact_keys:
        _rent_row = fact_texts_to_embed[fact_keys.index(_RENT_KEY)]
        assert not _rent_row.lower().startswith('rent wht rate:'), (
            f'[FATAL] {_RENT_KEY} is the label-led `key: value` fallback:\n  {_rent_row[:160]}\n'
            f'This regen exists to ship the ask-led CONCISE entry. The clone predates it, or the '
            f'CONCISE_BILINGUAL_FACTS entry was removed.')
        assert _rent_row.lower().startswith('unalipa pango'), (
            f'[FATAL] {_RENT_KEY} no longer LEADS with the asker\'s vocabulary:\n  '
            f'{_rent_row[:160]}\nThe nat_36 lever is the whole mechanism; a row that merely '
            f'CONTAINS "pango" is not the fix.')
        assert 'hakuna tofauti ya ukaazi kwenye pango' in _rent_row.lower(), (
            f'[FATAL] {_RENT_KEY} lost the no-residency-split clause:\n  {_rent_row[:200]}\n'
            f'That clause is the DEFECT the locked fact exists to prevent (there is no '
            f'resident/non-resident split on rent), and it is the critical-query guard\'s anchor '
            f'-- dropping it breaks the guard too.')
        assert 'wakala wa kuzuia' in _rent_row.lower(), (
            f'[FATAL] {_RENT_KEY} lost the withholding-agent qualifier:\n  {_rent_row[:200]}\n'
            f'Without it the row tells every ordinary payer to withhold 10%, which is wrong and '
            f'is the second defect the locked fact exists to prevent.')
        assert 'cap.332' not in _rent_row.lower() and 'first schedule' not in _rent_row.lower(), (
            f'[FATAL] {_RENT_KEY} carries a statutory citation in the EMBEDDED text:\n  '
            f'{_rent_row[:200]}\nForbidden by the standing rule in precompute_rag_embeddings.py '
            f'-- folding citations in cost nat_05 ranks 24 -> 59.')
        _gates_run += 1
        print(f'[OK] payload gate: {_RENT_KEY} present, ask-led, both qualifiers intact, uncited')
    else:
        raise SystemExit(
            f'[FATAL] {_RENT_KEY} absent from the built fact set -- this regen exists to ADD it, '
            f'so its absence is the whole failure, not a skippable gate.')

    # ── PAYLOAD GATE: THE TWO Cap.50 ROWS THAT WERE WRONG IN THE DEPLOYED INDEX ─────
    # Both of these were LIVE and wrong in the 184-row index this regen replaces, and both are the
    # same shape: locked_facts.json was corrected and the embedded text was not. A retrieval guard
    # cannot catch that -- a row can be reached perfectly and still state the superseded value --
    # so each needs a TEXT gate here as well as its critical query below.
    #
    # ⚠️ THESE GATES MUST CHECK POLARITY, NOT PRESENCE, and the first draft of them did not -- it
    # would have failed on the very rows it was written to protect. BOTH new rows deliberately NAME
    # the superseded value under a negation ('SI TZS 100,000', 'si tarehe 10'), because four training
    # rows assert the old fine and the model therefore carries a prior for it; a retrieved row that
    # merely states the right number competes with that prior, while one that explicitly contradicts
    # the wrong number overrides it. So the superseded figure APPEARING is correct and expected --
    # what must never happen is it appearing as the ASSERTION.
    #
    # A presence gate and a polarity gate are indistinguishable until the protected text contains
    # the thing being banned, and then they are opposites. Same lesson as the citation-attached-to-a-
    # no-threshold-gold limb: no subject or quantity pattern can see polarity, so it has to be
    # checked for directly.
    _NEGATED = r'(?:\bsi\b|\bnot\b|\bsio\b|\bhapana\b)[\s:,]*(?:TZS\s*|USD\s*)?$'
    # ⛔ FIFTH ELEMENT ADDED 2026-10-06: `require_contradiction`.
    #
    # The first four gates all protect rows that DELIBERATELY NAME the superseded value under a
    # negation, because training rows assert the old figure and an explicit contradiction is what
    # overrides that prior. For those, the third assertion below -- "the row must still CONTRADICT the
    # old value" -- is load-bearing: it stops a tidy-up silently deleting the override.
    #
    # The BRELA fee rows added today are not all like that, and forcing them to be would have been
    # the wrong call in two directions at once:
    #   * `company_registration_ladder` never mentioned 440,000 or 300,000 as wrong -- it simply
    #     stated them as right. There is no prior to override, and the row is ALREADY LONG (nine
    #     bands). Adding "SI TZS 440,000" would lengthen a row whose rank is measured (nat_34's
    #     displacement guard), and the row-57 measurement showed length is what costs rank, not
    #     correctness. So: presence-ban only, no contradiction required.
    #   * `brela_filing_fees` DOES carry the contradiction ("SI USD 220 na SI USD 25"), because the
    #     USD figures were live in the deployed index and were the live wrong answer on ext_15.
    #
    # Demanding a contradiction clause everywhere would have been R20's vacuous-fix shape in reverse:
    # a uniform rule inserted because it is uniform, costing rank on a row that needed nothing.
    for _k, _must_not, _must, _require_contradiction, _why in [
        ('fine_limit',
         r'one\s+hundred\s+thousand|laki\s+moja|100[,.]?000(?![,.\d])',
         r'10,000,000|milioni\s+kumi',
         True,
         'Cap.50 R.E.2023 s.76(1) reads "ten million shillings". TZS 100,000 is R.E.2015 s.72(1) '
         '-- superseded, and it was row 159 of the deployed index, understated 100x.'),
        ('nssf_payment_deadline',
         # `tarehe 10`, NOT `ifikapo tarehe 10` -- the ban pattern must match the CLAIM (the date),
         # not the one phrasing the replaced row happened to use. Caught in the dry run: the longer
         # form reported "does not contradict it" on a row reading "si tarehe 10".
         r'tarehe\s+10\b|the\s+10th',
         r'mwezi\s+mmoja',
         True,
         'Cap.50 R.E.2023 s.14(1): "within one month after the end of the month in respect of '
         'which the contributions are due and payable". The 10th appears in NO source -- the '
         'fact\'s own verified_by says so -- and was row 63 of the deployed index.'),
        # Added 2026-10-06. Row 57 asserted a FABRICATED TZS 11,000,000 EFD turnover threshold for
        # five and a half weeks after the 2026-08-29 re-verification found it invented -- while the
        # critical query above DEMANDED that figure be retrievable, and the comment above the row
        # told maintainers not to change it. Three things defending one fabrication.
        ('efd_threshold_tzs_11m',
         r'11[,.]?000[,.]?000|milioni\s+kumi\s+na\s+moja|14[,.]?000[,.]?000',
         r'haina\s+kizingiti|hakitumiki',
         True,
         'TAA Cap.438 R.E.2023 s.44(1) makes fiscal-receipt issuance the DEFAULT for every person '
         'supplying goods or rendering services; s.44(2) allows exemption ONLY by a '
         'Commissioner-General public notice naming a person or class. NO turnover figure appears '
         'in the section or anywhere in the Act. TZS 11M and TZS 14M are adjacent PRESUMPTIVE '
         'INCOME TAX band edges (Income Tax Act First Schedule para.2(3)) -- a different provision.'),
        # ── BRELA REPLACED ITS PUBLISHED FEE SCHEDULE, 2026-10-06 ──────────────────────
        # Not a correction of a misreading: BRELA's own 'Ada za Kampuni' page changed between two
        # dated, hashed captures (brela_ada_kampuni_v2.html sha256 cb1353fc..., 2026-06-30 ->
        # brela_ada_kampuni_20261006T140442Z.html sha256 8d5543ac..., 2026-10-06T14:04:42Z). The
        # whole foreign-company block moved from USD into TZS, the share-capital table went from five
        # bands to nine, and several local fees moved. R29 mode 3 -- the June figures were correct as
        # at their own date, which is why the gold row ext_15 is STALE rather than the model wrong.
        #
        # Rows 181 and 182 of the deployed index are serving USD 220 / USD 25 / 440,000 / 300,000.
        ('brela_filing_fees',
         r'USD\s*220|USD\s*25\b',
         r'faini ya kuchelewa TZS 70,000',
         True,
         'BRELA fee schedule items 15(ii)/(iii)/(iv) now read 600,000/600,000/70,000 in SHILLINGS. '
         'This group passage was the live source of the USD figures. The contradiction clause IS '
         'required here: the USD values were live in the deployed index and were the figure ext_15 '
         'was scored against, so a trained prior for them exists.'),
        ('company_registration_ladder',
         r'(?<![\d,])440,000(?![\d,])|(?<![\d,])300,000(?![\d,])',
         r'hadi TZS 100,000,000 ni TZS 400,000',
         False,
         'BRELA fee schedule item 1 now has NINE bands: the old open-ended "above TZS 50,000,000 = '
         '440,000" became 50M-100M = 400,000 with four bands above it, and item 2 (no share capital) '
         'went 300,000 -> 500,000. require_contradiction is FALSE on purpose -- this row never named '
         'those figures as wrong, so there is no override to preserve, and it is already nine bands '
         'long where length is what costs rank (the row-57 measurement).'),
        ('brela_foreign_late_filing_penalty',
         r'USD\s*25\b|Dola\s*za\s*Kimarekani\s*25',
         r'TZS\s*70,000',
         False,
         'The standalone row for this fact. Its PINNED needle in check_facts_index_sync used to be '
         '"faini ni USD 25 kwa kila mwezi" -- a pin REQUIRING the superseded figure -- and was '
         're-pinned pending_r15 today after scripts/check_anchor_provenance.py caught it. '
         'require_contradiction is FALSE: this CONCISE row states the current figure plainly and the '
         'group passage above carries the explicit USD contradiction for the trained prior.'),
    ]:
        assert _k in fact_keys, (
            f'[FATAL] {_k} absent from the built fact set -- it was present in the 184-row index '
            f'this regen replaces, so its disappearance is a defect, not a skippable gate.')
        _row = fact_texts_to_embed[fact_keys.index(_k)]
        _asserted = [m.group(0) for m in re.finditer(_must_not, _row, re.I)
                     if not re.search(_NEGATED, _row[max(0, m.start() - 14):m.start()], re.I)]
        assert not _asserted, (
            f'[FATAL] {_k} ASSERTS the superseded value {_asserted!r} (not under a negation):\n'
            f'  {_row}\n{_why}\nThis gate exists so the correction cannot silently revert.')
        assert re.search(_must, _row, re.I), (
            f'[FATAL] {_k} does not state the current value:\n  {_row}\n{_why}')
        # And the negation device itself is asserted, so a future "tidy-up" that simply deletes the
        # "SI TZS 100,000" clause fails here rather than quietly weakening the override.
        if _require_contradiction:
            assert re.search(_must_not, _row, re.I), (
                f'[FATAL] {_k} no longer CONTRADICTS the superseded value at all:\n  {_row}\n'
                f'The explicit contradiction is deliberate -- it is what overrides the trained prior '
                f'from the rows that assert the old value. Stating the right number is not enough.')
        elif re.search(_must_not, _row, re.I):
            # NOT an error: the ban above already proved it is not ASSERTED. Printed rather than
            # silent so a row that GROWS a contradiction clause is visible -- the opposite direction
            # from the one the assertion guards, and equally worth seeing.
            print(f'[note] payload gate: {_k} mentions the superseded value under a negation; no '
                  f'contradiction clause was required for this row.')
        _gates_run += 1
        print(f'[OK] payload gate: {_k} states the current value and contradicts the superseded '
              f'one (polarity-checked, not presence-checked)')
    return _gates_run
