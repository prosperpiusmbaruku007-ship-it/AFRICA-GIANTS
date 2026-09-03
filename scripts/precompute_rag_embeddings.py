#!/usr/bin/env python3
"""
Rebuild the RAG index from scripts/locked_facts.json (Fix 2 — concise bilingual).

High-stakes facts are embedded as SHORT, Swahili-dominant strings that contain the
value in both Swahili number words and TZS digits. Short text keeps the mean-pooled
embedding close to short Swahili queries (a long English tail dilutes it — that was
why the GN487A 10M penalty sank to rank 8). Bare citations / exemption lists / the
low-value signatory fact are dropped as noise.

build_fact_texts() is importable (used by the dry-run) WITHOUT triggering a rebuild;
embedding + save only runs under `__main__`.

STANDING RULE FOR CONCISE_BILINGUAL_FACTS TEXT (added 2026-08-17, C4 reachability
cycle): do not put effective dates, Act/section citations, or statutory-basis phrasing
("Finance Act 2023", "gross cash emoluments", "effective 1 July 2023") in the embedded
text. Measured directly: folding sdl_rate_2025's citation precision into sdl_rate's
CONCISE text pulled it toward legal-citation-shaped neighbours and away from the
conversational question a real user asks (nat_05 only reached rank 59/217 with that
material included; a version with it stripped reached rank 24; an overfit probe with
it stripped and the query's own tokens echoed reached rank 1 -- see
scratch/factpath_ceiling_and_topk.py). That precision is not lost: it belongs in
locked_facts.json's own fields (verified_by, effective_date, primary_source), which
downstream training-pair generation (R13, generate-from-facts) reads directly and
does not go through this embedding at all. Every future fact will be tempted to
include this material for good reasons (it IS more complete, more auditable) --
resist it here specifically, in the text that gets embedded for retrieval.

Run: python scripts/precompute_rag_embeddings.py
"""
import json
import os
import re
import numpy as np

FACTS_PATH   = 'scripts/locked_facts.json'
OUTPUT_NPY   = 'chike-inference/rag_embeddings.npy'
OUTPUT_TEXTS = 'chike-inference/rag_facts_text.json'
# intfloat/multilingual-e5-base: 768-dim, trained for multilingual retrieval.
# e5 REQUIRES an asymmetric prefix — facts are 'passage: ', queries are 'query: '
# (the query prefix is applied at retrieval time in chike-inference/modal_app.py).
EMBED_MODEL  = 'intfloat/multilingual-e5-base'
E5_PASSAGE_PREFIX = 'passage: '

# --- Concise, Swahili-dominant text for high-stakes facts (SHORT, no long English tail) ---
CONCISE_BILINGUAL_FACTS = {
    'gn487a_penalty_noncitizen':
        'Faini kwa mgeni (raia wa kigeni) anayevunja GN487A: si chini ya TZS 10,000,000 (milioni kumi), na/au kifungo miezi 6, na kufutwa kwa visa.',

    # Swahili-first grounding for the phone-repair activity. The 15 prohibited-activity
    # facts are otherwise English-only (key: value fallback) and match Swahili queries
    # only cross-lingually (weak e5 signal) — see PROGRESS.md systemic-gap note. This
    # entry gives activity 3 real same-language tokens (mgeni/kutengeneza/simu) so it
    # wins its own query on grounding, not luck, instead of being displaced by any
    # Swahili-dense GN487A fact. English tail keeps the 'phone'/'activity 3' guard keys.
    'gn487a_prohibited_activity_3':
        'Kutengeneza au ukarabati wa simu na vifaa vya kielektroniki ni shughuli '
        'iliyozuiliwa kwa wasio raia chini ya GN487A. Mgeni hawezi kufanya biashara '
        'ya kutengeneza simu. (Prohibited activity 3: repair of mobile phones and '
        'electronic devices.)',

    'gn487a_penalty_citizen_facilitator':
        'Adhabu kwa raia wa Tanzania anayemsaidia mgeni kukiuka GN487A: faini si zaidi ya TZS 5,000,000 (milioni tano), au kifungo si zaidi ya miezi 3.',

    # Retrieval-targeted restatement of the facilitator penalty using the exact
    # 'kukopesha leseni' collocation. lv_01/fp_01 showed the model overrides the
    # generic 'anayemsaidia mgeni' fact with a parametric 'licensed Tanzanian may
    # operate' prior for THIS phrasing only (2x2 factorial: swapping either the verb
    # or the object alone fixes it). Same TZS 5M/3-month figure — no new claim.
    # NARROWED (v2): the first draft carried generic GN487A-penalty mass
    # (kumsaidia/kukiuka/msaidizi/adhabu/faini prose) that made it a generic Swahili
    # GN487A-penalty magnet — it displaced gn487a_prohibited_activity_3 from the
    # 'Mgeni anaweza kutengeneza simu?' top-3 (caught by the regen verification gate).
    # This version concentrates the embedding centroid on license-transfer (kukopesha/
    # kukodisha/kukabidhi + leseni — tokens absent from every competing fact, so lv_01
    # still wins) and drops the generic penalty/facilitation prose.
    # NARROWED AGAIN (v3): v2 still carried the explicit 'faini ya TZS 5,000,000 au
    # kifungo cha miezi 3' penalty-amount tail. That residual penalty-amount vocabulary
    # made it rank #2 (in top-3) for eval_380's non-citizen-penalty-AMOUNT query
    # ('Faini ya chini kabisa ... asiye raia ... TZS ngapi?'), injecting a SECOND 5M
    # figure alongside the correct 10M non-citizen fact (which is already rank 0). Two
    # 5M facts vs one 10M in context tipped the model to answer 5M — a wrong number
    # (10M->5M gate regression at 19fce68, eval_380). Dropping the figure tail and
    # ending on 'anaadhibiwa kama msaidizi wa mgeni' keeps the kukopesha+leseni
    # collocation (lv_01/eval_213 still retrieves it at rank 0 and stays faithful) while
    # pushing it OUT of eval_380's top-3 (verified rank 3). The 5M figure for eval_213's
    # answer is still available from gn487a_penalty_citizen_facilitator (idx 21).
    'gn487a_license_lending_is_facilitation':
        'Kukopesha, kukodisha au kukabidhi leseni yako ya biashara kwa mgeni ni kosa chini ya GN487A. '
        'Raia anayekopesha leseni yake kwa mgeni anaadhibiwa kama msaidizi wa mgeni.',

    # Swahili grounding for the marriage-exemption fact. Like the 15 prohibited-activity
    # facts, gn487a_marriage_no_exemption was English-only (key:value fallback) — it
    # ranked ~5 (outside top-3) for the Swahili marriage query, so eval_175 lost its
    # correct fact and the model deflected to a vague 'apply for citizenship' answer
    # (True->False at 19fce68). This gives it real same-language tokens (kuoa/kuolewa/
    # Mtanzania/msamaha/rejareja) so it wins its own query (verified rank 0), pulled
    # forward from the queued systemic English-only batch because it has a measured
    # gate cost. Same figure-free, action/status statement pattern as activity_3.
    'gn487a_marriage_no_exemption':
        'Kuoa au kuolewa na raia wa Tanzania HAKUKUPI msamaha wa GN487A wala uraia. '
        'Mgeni aliyeoa Mtanzania bado ni mgeni na hawezi kufanya biashara ya rejareja iliyozuiliwa. '
        'Tafuta ushauri wa wakili wa uhamiaji.',

    # C4 reachability rewrite, round 2 (2026-08-17). The round-1 draft folded in the
    # merged sdl_rate_2025 duplicate's legal-citation precision (effective date, Finance
    # Act reference, "gross cash emoluments") directly into this text and measured WORSE
    # (nat_05 rank 150->59, barely better than baseline) than a version with that material
    # stripped out. STANDING RULE (see module docstring): citation clutter belongs in
    # locked_facts.json's other fields for audit/training-pair generation, never in the
    # embedded CONCISE text -- it pulls the embedding toward legal-citation-shaped
    # neighbours and away from the conversational question a real user asks. This version
    # (lean, "mafunzo" colloquial anchor, word-form + digit-form rate) measured nat_05
    # rank 150->24. Ceiling-tested separately (scratch/factpath_ceiling_and_topk.py): an
    # overfit version of this same row reached rank 1, so the mechanism is real; this
    # text is the readable, general point on that curve, not the maximum.
    'sdl_rate':
        'SDL, ambayo huitwa pia "mafunzo": kiwango cha mafunzo ni asilimia tatu na nusu '
        '(asilimia 3.5) ya mishahara ya wafanyakazi. Si asilimia 4, si asilimia 2.',

    'sdl_employee_threshold':
        'Kizingiti cha SDL: mwajiri mwenye wafanyakazi 10 AU ZAIDI analipa SDL. Mwenye wafanyakazi 10 YUKO NDANI ya kizingiti na analipa SDL. Chini ya 10 (yaani 9 au pungufu) hawalipi SDL.',

    # NOT rewritten this round (2026-08-17). nat_24 targets this row and moved 41->44->37
    # across two rounds of substantially different wording -- flat, unlike nat_05 (same
    # SDL cluster, same rewrite discipline, 150->24). Named as its own finding, not folded
    # into this pass: see PROGRESS "THE THREE FLAT ROWS". Text held at its pre-2026-08-17
    # wording deliberately, pending a ceiling test run ON nat_24 itself rather than on
    # nat_05, to establish whether the mechanism here is even reachable by phrasing.
    'sdl_threshold':
        'Kizingiti cha SDL ni wafanyakazi 10 au zaidi. Wafanyakazi 10 hasa wanalipa SDL (wako ndani). Si 11, si 4.',

    # NEW CONTENT (2026-08-17). Consolidates 10 individual exemption_category_* keys
    # (real content, not fragments -- verified by reading each value) that a blanket
    # noise regex (`^exemption_category_`) was previously dropping wholesale. One
    # retrievable Swahili fact instead of 10 English fallback rows that would have
    # recreated the ranking problem this whole cycle exists to fix. The 10 individual
    # keys stay in locked_facts.json for training-pair generation; they are excluded
    # from the RAG index by an explicit, individually-reviewed list in
    # _NOISE_KEYS_REVIEWED below, not by the prefix pattern that swept them up before.
    'sdl_exemption_categories':
        'Waajiri/taasisi zisizolipa SDL (msamaha): idara za Serikali, mamlaka za Serikali '
        'za Mitaa, taasisi za kidiplomasia, Umoja wa Mataifa na taasisi zake, mashirika ya '
        'kimataifa ya misaada, taasisi za kidini (kwa shughuli za kiroho tu), taasisi za '
        'elimu zilizosajiliwa, mashirika ya misaada (charitable), wanafunzi wa TaESA, na '
        'waajiri wa mashambani kwa wafanyakazi wanaolima moja kwa moja.',

    'sdl_payment_deadline':
        'SDL inalipwa ifikapo siku ya 7 ya mwezi unaofuata.',

    'nssf_employer_rate':
        'NSSF: mwajiri analipa asilimia 10 ya mshahara wa mfanyakazi kila mwezi. Tovuti sahihi ni nssf.go.tz (si nssf.or.tz).',

    'nssf_total_rate':
        'NSSF jumla: asilimia 20 ya mshahara (10% mwajiri + 10% mfanyakazi). Tovuti sahihi ni nssf.go.tz (si nssf.or.tz).',

    'nssf_payment_deadline':
        'NSSF inalipwa ifikapo tarehe 10 ya mwezi unaofuata.',

    # Ask-aligned rewrites, 2026-09-03 (R15's topic-alignment lever): both were bare
    # "key: five %" / "key: 100 %" context-free fragments before this, and both were found
    # crowding nat_27's (unrelated VAT-rate query) and/or nat_36's (unrelated EFD-threshold
    # query) post-regen top-3 alongside contribution_rate_emplyees (dropped as noise, see
    # _NOISE_KEYS_REVIEWED) -- the SAME fragment-displacement class the fee-schedule
    # consolidations were built to fix. NOT consolidation candidates the way the fee rows
    # were, though: a fee LADDER is naturally one composite answer ("what are BRELA's fees");
    # these two are independently-askable, unrelated NSSF questions (maternity benefit vs.
    # late-payment penalty) that happen to share only a bare-percentage shape and a source
    # document. Merging them would not address why they crowd unrelated queries -- it would
    # still be a bare-percentage passage. The remedy that already worked on this exact defect
    # shape (sdl_rate, efd_threshold_tzs_11m, nssf_total_rate) is ask-aligned rewriting, not
    # grouping, so that is what is applied here. Values unchanged from locked_facts.json's
    # existing correct_value -- no new claims added beyond restating the verified figure in
    # a natural Swahili question-shaped sentence.
    'maternity_cash_benefit_rate':
        'NSSF likizo ya uzazi (maternity benefit): mfanyakazi analipwa ASILIMIA 100 ya '
        'mshahara wakati wa likizo ya uzazi.',

    'unpaid_contribution_penalty_rate':
        'Ukichelewesha kulipa mchango wa NSSF, adhabu (penalty) ni ASILIMIA 5 ya kiasi '
        'kisicholipwa.',

    'vat_registration_threshold_annual':
        'Kizingiti cha kusajili VAT: mauzo ya TZS 200,000,000 kwa miezi 12.',

    # vat_withholding_goods / vat_withholding_services: HELD BACK, not applied
    # (2026-08-17). A round-2 rewrite (adding 'bidhaa'/'ushauri' vocabulary, the same
    # pattern that worked for every other C4 row) measured nat_44 33->4 and nat_28's
    # rate half 33->8 -- a real win. But local dry-run verification
    # (scratch/local_regen_verify.py) caught a cost the earlier stage-1/round-2 passes
    # never tested for: it also pulls nat_27 (a currently CORRECT row asking the
    # STANDARD 18% rate, not withholding) into the same neighbourhood and displaces the
    # 18% fact out of its own top-3. Three phrasings were tried to reconcile this (bare
    # rewrite, an explicit "Si kiwango cha kawaida (18%)" contrast -- which also
    # produced a FALSE keyword-match PASS, since the guard's '18%' substring check
    # matched the contrast clause itself while the actual retrieved content was still
    # wrong -- and a "makato"/deduction-framing variant); all three still displaced
    # nat_27. Both keys are left OUT of this dict, on the original fallback text,
    # rather than ship a nat_44/28 win that breaks a currently-correct row for zero net
    # gain in what production is allowed to answer. See PROGRESS "THE VAT WITHHOLDING
    # TRADEOFF" for the measured numbers on each attempt.

    # EFD-threshold Swahili grounding (eval_347). efd_threshold_tzs_11m was English-only
    # (key:value fallback), so a query naming EFD + "mauzo ya TZS 200,000,000" was hijacked
    # by the concise Swahili vat_registration_threshold_annual fact (same 200M magnitude, same
    # 'Kizingiti cha ... mauzo ya' phrasing). Probe v2 (ca2a0cf): the number-stripped arm DID
    # surface the EFD fact, but only at s#2 — it lost the single append-only promotion slot to
    # efd_approved_supplier_verification (s#1) by one rank. This concise, Swahili-first entry
    # (value at front, distinctive 'kuanza kutumia EFD' tokens) lifts it so it wins its own
    # query; the explicit '200M = VAT-registration, si EFD' contrast targets eval_347's exact
    # false premise. Same figure (TZS 11M) — no new claim. NOTE: the 200M/kusajili-VAT tokens
    # carry a displacement risk toward genuine VAT-registration queries (as the GN487A concise
    # facts did) — guarded by the two verification tuples in regenerate_rag_e5.py; narrow this
    # text (trim the 200M contrast) if the regen gate flags displacement.
    # KEPT PRISTINE (value-at-front + tight 200M-contrast) — this exact text was the
    # deployed 213-fact index and PASSES the adversarial eval_347 'EFD threshold' tuple.
    # Do NOT add applicability prose here; the "not every business" correction lives in
    # the separate 200M-free efd_not_every_business key below (adding it here tipped
    # eval_347 out of top-3 — see PROGRESS §FACT-ACCURACY / regen b54eb23).
    'efd_threshold_tzs_11m':
        'Kizingiti cha kuanza kutumia mashine ya EFD: mauzo ya TZS 11,000,000 '
        '(milioni kumi na moja) kwa mwaka. Si TZS 200,000,000 — hiyo ni kizingiti '
        'cha kusajili VAT, si EFD. Biashara zote zilizosajiliwa VAT hutumia EFD '
        'bila kujali kiwango cha mauzo.',

    # Q16 fix (200M-FREE by design, so it does NOT intrude on eval_347's 200M-heavy
    # adversarial query while still winning the "kila duka bila kujali mauzo?" query).
    # Counters the model's over-generalization that every shop needs an EFD regardless
    # of sales, by injecting the explicit "Si kila biashara" + manual-receipts nuance.
    'efd_not_every_business':
        'Duka dogo au biashara ndogo yenye mauzo madogo, je inahitaji mashine ya risiti '
        '(EFD)? Si lazima. Si kila biashara inalazimika kutumia mashine ya risiti za '
        'kielektroniki (EFD): biashara ndogo yenye mauzo chini ya TZS 11,000,000 kwa mwaka '
        'na isiyosajiliwa VAT inaweza kutumia risiti za mkono badala ya mashine ya EFD. '
        'Waliosajiliwa VAT na wenye mauzo ya TZS 11,000,000 au zaidi ndio hulazimika '
        'kutumia mashine ya risiti za EFD.',

    # Q14 companion — SHORT + high-concentration so it out-ranks the "minimum shareholders:
    # 2 employees" company-incorporation distractor that hijacked "wafanyakazi wawili tu...
    # nasajiliwa" (Q14). Registration-obligation framing (distinct from wcf_threshold_no_minimum,
    # which is about the 0.5% LEVY threshold, and from minimum_shareholders, which is company
    # incorporation) — no contradiction/duplication; see PROGRESS §FACT-ACCURACY guardrail 2.
    'small_headcount_still_register':
        'Nina wafanyakazi wawili tu (au mmoja) dukani — je bado najisajili mahali fulani? '
        'Ndiyo. OSHA husajili maeneo YOTE ya kazi bila kikomo cha idadi ya wafanyakazi, na '
        'WCF huanza tangu mfanyakazi wa kwanza. Idadi ndogo ya wafanyakazi HAIONDOI wajibu '
        'wa kujisajili OSHA na WCF (mfuko wa fidia).',

    'vat_registration_threshold_six_months':
        'Kizingiti cha kusajili VAT: mauzo ya TZS 100,000,000 kwa miezi 6.',

    # C4 reachability, round 2 (2026-08-17). nat_33 best-of-two rank 113->25. Added
    # 'ritani' as the colloquial synonym for 'annual return' -- nat_33's own question
    # says 'ritani', not 'annual return'. Landed alongside the brela_annual_return_fee
    # duplicate-key deletion (that key bundled the same TZS 22,000 + TZS 2,500/month
    # content under a third name plus one genuine unique detail -- foreign Section XII
    # USD 25/month -- now its own key, brela_foreign_late_filing_penalty, below).
    'annual_return_filing_fee':
        'BRELA: ada ya kuwasilisha ritani (annual return) ya kampuni kila mwaka ni '
        'TZS 22,000.',

    'late_filing_penalty_monthly_fee':
        'BRELA: ukichelewa kuwasilisha ritani (annual return) ya kampuni, faini ni '
        'TZS 2,500 kwa kila mwezi wa kuchelewa.',

    'brela_foreign_late_filing_penalty':
        'Kampuni ya kigeni (Section XII) ikichelewa kuwasilisha ritani ya mwaka: faini '
        'ni USD 25 kwa kila mwezi (tofauti na kampuni za ndani ambazo hulipa TZS 2,500 '
        'kwa mwezi).',

    'osha_registration_threshold_b004':
        'OSHA Tanzania: kila mwajiri lazima asajili mahali pa kazi na OSHA. Sheria inahusu maeneo yote ya kazi bila kikomo cha idadi ya wafanyakazi.',

    # NEW CONTENT, not a rewrite (2026-08-17). nat_41 ("nimefungua karakana mpya nina
    # muda gani wa kusajili sehemu ya kazi") was classified RANKING against rows 53/72
    # (no minimum headcount) -- but those answer a DIFFERENT question. nat_41 asks about
    # a DEADLINE; no locked fact stated one. Verified against OSH Act 2003 s.16(2) via
    # two independent Tanzania government sources before writing this (see PROGRESS,
    # "nat_41 flips back to ABSENCE"). Genuinely absent content, not a phrasing gap --
    # ceiling-tested to rank 5/217 on the round-2 text, the closest of the non-clearing
    # rows, but still new rather than reachable-by-rewording.
    'osha_registration_before_operations':
        'Umefungua karakana au sehemu mpya ya kazi? Usajili wa OSHA lazima ufanyike '
        'KABLA ya kuanza biashara — hakuna muda wa siku baada ya kufungua. (Kifungu '
        '16(2), Sheria ya Afya na Usalama Mahali pa Kazi Na.5 ya 2003.)',

    'OSHA_annual_inspection':
        'OSHA hufanya ukaguzi wa lazima kila mwaka (mara moja kwa mwaka) katika maeneo yote ya kazi Tanzania.',

    'wcf_rate_0_5_percent_confirmed':
        'WCF (Workers Compensation Fund): mwajiri analipa asilimia 0.5 ya jumla ya mishahara yote kila mwezi. Si kiasi kisichobadilika — inategemea mishahara.',

    # C4 reachability, round 2 (2026-08-17). nat_43 ("mimi ni mkulima ... je kima cha
    # chini kinatofautiana kwa sekta") rank 127->1 -- the row that CLEARS top-3, the
    # only one of nine. Added 'mkulima'/'kilimo' because that is nat_43's own framing
    # (a farmer asking whether agriculture has its own rate). Wired as a positive
    # critical_queries guard in regenerate_rag_e5.py.
    'GN605A_sector_count':
        'Kima cha chini cha mshahara (GN 605A): hakina kiwango kimoja kwa nchi nzima — '
        'kila sekta ina chake, sekta 16 na sekta ndogo 46. Mkulima / sekta ya kilimo ina '
        'kiwango chake tofauti na sekta nyingine.',

    'paye_bands_with_examples':
        'PAYE kwa mshahara wa TZS 800,000 ni TZS 78,000 kamili. Hii ni jibu la mwisho, si mahesabu ya ziada.',

    'sdl_calculation_example':
        'Mfano wa hesabu ya SDL: mfanyakazi mmoja mwenye mshahara TZS 600,000, SDL ni asilimia 3.5 = TZS 21,000. Kwa wafanyakazi 12 wenye mshahara huo huo, SDL jumla ni TZS 252,000 (12 × 21,000).',

    'nssf_calculation_example':
        'Kwa wafanyakazi 12 wenye mshahara TZS 600,000 kila mmoja, NSSF jumla ni TZS 1,440,000 (SI TZS 120,000 — hiyo ni kwa mfanyakazi mmoja tu). Hesabu: kila mfanyakazi analipa NSSF ya TZS 120,000 (asilimia 20 ya mshahara wake), kisha zidisha kwa wafanyakazi 12 = TZS 1,440,000 jumla.',

    # Swahili-first grounding for the BRELA striking-off rule (edge Q13). The model
    # fabricated a "company must finish its term first" bar (companies have no term);
    # the correct rule is the non-filing -> defunct -> 30-day notice -> strike-off
    # procedure. English-only would match the Swahili query only cross-lingually.
    'brela_striking_off_non_filing':
        'Naweza kufuta, kufunga au kuondoa kampuni yangu iliyosajiliwa kwenye daftari la '
        'BRELA? Ndiyo — HAKUNA sharti la "kumaliza muda" kwanza, kwa sababu kampuni haina '
        'muda maalum. Kampuni isipowasilisha ritani za mwaka (annual returns) inaweza '
        'kuhesabiwa haifanyi kazi (defunct) na kufutwa kwenye Daftari la Makampuni: Msajili '
        'hutoa notisi ya siku 30, kisha jina hufutwa chini ya Sheria ya Makampuni (Sura 212). '
        'Kurejesha kampuni iliyofutwa kunahitaji Mahakama Kuu.',

    # Swahili-first grounding for the OSHA-vs-WCF role distinction (edge Q14). The model
    # answered the wrong agency and fabricated a 2-employee WCF threshold after retrieval
    # pulled a company-shareholders fact for a WCF question — a same-language grounding
    # entry stops that cross-lingual displacement.
    'osha_vs_wcf_roles':
        'OSHA na WCF ni taasisi mbili tofauti. OSHA husajili mahali pa kazi (kifungu 16, Sheria '
        'ya OSHA Na.5 ya 2003), hukagua, na hutoa leseni ya utii kila mwaka — OSHA HAILIPI fidia '
        'ya ajali. Fidia ya ajali na magonjwa ya kazini hulipwa na WCF (mwajiri huchangia 0.5% ya '
        'mishahara). Usajili wa OSHA na wa WCF ni tofauti; vyote vinahitajika. WCF huanza tangu '
        'mfanyakazi wa kwanza — HAKUNA kizingiti cha wafanyakazi wawili.',

    # ASK-ALIGNED FROM THE FIRST DRAFT, not retrofitted after a rank-check failure — the nat_34
    # cost (five candidates, two rank-check passes) is what re-leading AFTER the fact costs, so
    # this was written topic-word-first per the standing rule (CLAUDE.md, "SWAHILI-FIRST IS
    # NECESSARY AND NOT SUFFICIENT"). Leads with 'Kodi ya kampuni' (what a company owner types),
    # not the regulatory label ('First Schedule para 3'); the citation stays in locked_facts.json
    # only, per the standing "no citation clutter in the embedded text" rule two entries above.
    'corporate_tax_rate':
        'Kodi ya kampuni Tanzania ni asilimia 30 kwa kampuni za kawaida. Kampuni zilizoorodheshwa '
        'DSE (Soko la Hisa la Dar es Salaam) zenye angalau asilimia 25 ya hisa zao kwa umma '
        'hulipa asilimia 25 kwa miaka mitatu tangu tarehe ya kuorodheshwa.',

    # ASK-ALIGNED FROM THE FIRST DRAFT. Leads with the SITUATION a company owner would describe
    # ('kampuni yenye hasara miaka mitatu mfululizo') rather than the technical term 'Alternative
    # Minimum Tax' or 'AMT', which is not vocabulary a Tanzanian trader searches in. Includes the
    # s.4(8) exemptions found missing from both source facts during the 2026-09-01 corporate/
    # partnership source pass — an omitted exemption is as misleading as a wrong rate, so it
    # belongs in the retrieval-facing text too, not only in locked_facts.json's fuller `fact`
    # field.
    'minimum_turnover_tax':
        'Kampuni yenye hasara miaka mitatu mfululizo hulipa kodi ya chini (AMT) ya asilimia 1 '
        'ya mauzo ya mwaka wa tatu, tangu Julai 2025 (awali ilikuwa asilimia 0.5). Haitumiki kwa '
        'kampuni za kilimo, afya, elimu, wala kampuni za usindikaji chai hadi Juni 2027.',
}

# --- FACT GROUPS: many `key: number` rows collapsed into ONE contextual passage ------------
#
# THIS IS NOT NOISE-DROPPING. Every figure below stays in locked_facts.json (it is still the
# truth table that check_locked_facts.py enforces) and every figure stays IN THE INDEX -- what
# changes is that 42 context-free rows become 3 rows that say what the numbers are about.
#
# ⛔ THE TRADE I EXPECTED DID NOT EXIST, and that is the finding worth recording here rather
# than in a commit message. Deletion vs consolidation was framed as "crowding removed" against
# "answer lost". Measured (eval/results/feerow_curation.json, eval/results/feegroup_curation.json,
# 2026-08-25) the second half is not real:
#
#     a `key: number` row is retrieved for the WRONG questions AND fails the RIGHT ones.
#
# Deleting 17 trademark rows moved 6/7 buried anchors and REGRESSED 1 control. Consolidating all
# 42 moved 7/7 (nat_23: 86 -> 45, nat_05: 24 -> 8) and GAINED 2 controls with 0 regressed --
# including a trademark-fee question the BASELINE index could not answer, because "trademark fee
# for single mark registration: 60,000 TZS" does not look like the question a person types. So
# there was never a coverage cost to weigh against the crowding: consolidation wins on BOTH sides
# and the deliberation about the trade-off was deliberation about a trade that does not exist.
#
# ⚠️ FOUR OF THE ABSORBED ROWS ARE TRACEABLE SOURCES OF NAMED LIVE DEFECTS:
#   [167] `registration certificate processing time new: 1 days`  -> nat_41's fabricated "siku 1"
#         for OSHA registration. It is a BRELA row; [155] says 3 days for a same-sounding thing.
#         (Absorbed by no group below -- see the BOARDED note at the bottom of this block.)
#   [120] `company registration fee 3: 260,000 TZS`               -> nat_05's fabricated BRELA fee
#         offered in answer to an SDL question.
#   [209] `contribution rate emplyees: 10 %`                      -> the NSSF 10%-vs-20% collapse.
#   [157] `beneficial owner information penalty maximum: 10000000 TZS` -> HYPOTHESIS ONLY for
#         pic_11's "milioni 10" presumptive-ceiling belief. Untested; do not cite as established.
#
# 🔑 AND [209] DESERVES ITS OWN LINE: THE KEY IS MISSPELLED -- `contribution_rate_emplyees`.
# A typo in a key is not cosmetic here, because build_fact_text() renders the KEY as the
# retrievable label: the row a user's NSSF question matches literally reads "contribution rate
# emplyees: 10 %". It is context-free (no "of 20% total", no "employee share"), it is highly
# retrievable on any NSSF rate question, and it is one of the two rows behind a live wrong
# answer. That argues for a KEY-HYGIENE PASS across all 252 locked facts -- boarded, not done
# here, because renaming keys moves what the drift check and the guards match on and deserves
# its own measured cycle. [209] and [167] are NOT in the groups below for the same reason:
# they are not fee-schedule rows and each needs its own fix, not absorption.
FACT_GROUPS = {
    'trademark_fees': {
        'keys': [
            'trademark_fee_for_single_mark_registration',
            'trademark_fee_for_renewal_of_registration',
            'trademark_fee_for_series_of_marks_first_mark',
            'trademark_fee_for_series_of_marks_subsequent_mark',
            'trademark_fee_for_renewal_of_series_of_marks_first_mark',
            'trademark_fee_for_renewal_of_series_of_marks_subsequent_mark',
            'trademark_fee_for_opposition_notice',
            'trademark_fee_for_responding_to_opposition',
            'trademark_fee_for_hearing_opposition',
            'trademark_fee_for_explanation_of_decision',
            'trademark_fee_for_registration_of_subsequent_proprietor',
            'trademark_fee_for_change_of_proprietor_or_user_same_address',
            'trademark_fee_for_change_of_business_address',
            'trademark_fee_for_dissolution_of_partnership',
            'trademark_fee_for_refund_of_fee',
            'trademark_fee_for_additional_fee_by_regulation_54',
            'trademark_fee_for_any_other_entry',
        ],
        'text': (
            'Ada za alama ya biashara (trademark) BRELA: kusajili alama moja TZS 60,000; kuhuisha '
            '(renewal) TZS 30,000; mfululizo wa alama — ya kwanza TZS 60,000, zinazofuata TZS '
            '30,000; kuhuisha mfululizo — ya kwanza TZS 30,000, zinazofuata TZS 10,000; taarifa '
            'ya pingamizi TZS 60,000; kujibu pingamizi TZS 50,000; kusikiliza pingamizi TZS '
            '70,000; maelezo ya uamuzi TZS 50,000; kusajili mmiliki mpya TZS 50,000; kubadili '
            'mmiliki au mtumiaji TZS 50,000; kubadili anwani ya biashara TZS 20,000; kuvunja '
            'ubia TZS 50,000; kurejeshewa ada TZS 30,000; ada ya nyongeza kanuni 54 TZS 30,000; '
            'kiingizo kingine chochote TZS 10,000.'),
    },
    'company_registration_ladder': {
        # A LADDER belongs in one passage anyway: the fee is meaningless without the share-capital
        # band it attaches to, and split across 14 rows the bands and fees can be paired wrongly
        # by whatever retrieves three of them.
        'keys': [
            'company_share_value_threshold_1_max', 'company_registration_fee_1',
            'company_share_value_threshold_2_min', 'company_share_value_threshold_2_max',
            'company_registration_fee_2',
            'company_share_value_threshold_3_min', 'company_share_value_threshold_3_max',
            'company_registration_fee_3',
            'company_share_value_threshold_4_min', 'company_share_value_threshold_4_max',
            'company_registration_fee_4',
            'company_share_value_threshold_5_min', 'company_registration_fee_5',
            'company_registration_fee_no_share_capital',
        ],
        # RE-LED 2026-08-26 (nat_34 retrieval regression, R15 ask-alignment lever -- see
        # PROGRESS.md "nat_34 rank-4 fix"). The prior text opened with the regulatory frame
        # ("hutegemea thamani ya hisa / share capital") and buried the number nat_34 actually
        # asks for -- "gharama ya kuanzia" (starting cost) -- inside the band table. Consolidation
        # then let a neighboring untouched row (business_name_maintenance_fee) climb into the
        # competing top-3 slot, and topic alignment (not the numbers, which never changed) is
        # what wins that competition. Re-opening with nat_34's own words -- "kusajili kampuni",
        # "gharama ya kuanzia", "kuhifadhi jina" -- in that order, values up front, mirrors the
        # question almost verbatim. All 14 group-member figures are still present verbatim
        # (checked by _grouped_verdict's substring containment, order-independent).
        #
        # WORDING SEARCH, not the first attempt (2026-08-26, eval/results/
        # nat34_reledger_probe.json). A softer lead that kept qualifying phrases ("kwa mtaji
        # wa hisa hadi...", "hizi ni ada mbili tofauti") still lost, rank 4 -- filler words
        # dilute the embedding toward the ladder's other content and away from the two
        # numbers the question asks for. Only the SHORT, filler-free lead (values right after
        # each named concept, qualifiers moved later) cleared rank 3. Five phrasings measured
        # against the fixed remainder of the prospective index; this is the only one that won.
        'text': (
            'Kusajili kampuni gharama ya kuanzia ni TZS 95,000; kuhifadhi jina ni TZS 50,000. '
            'Ngazi za ada kwa mtaji wa hisa (share capital): hadi TZS 1,000,000 ni TZS 95,000; '
            'zaidi ya TZS 1,000,000 hadi TZS 5,000,000 ni TZS 175,000; zaidi ya TZS 5,000,000 '
            'hadi TZS 20,000,000 ni TZS 260,000; zaidi ya TZS 20,000,000 hadi TZS 50,000,000 ni '
            'TZS 290,000; zaidi ya TZS 50,000,000 ni TZS 440,000. Kampuni isiyo na mtaji wa hisa '
            'ni TZS 300,000. Kubadili jina ni TZS 22,000.'),
    },
    'brela_filing_fees': {
        'keys': [
            'memorandum_articles_of_association_filing_fee',
            'stamp_duty_per_copy_memorandum_articles_copy',
            'stamp_duty_form_14b_fee',
            'document_acceptance_registration_fee',
            'document_certification_fee_per_page',
            'file_search_fee', 'file_search_report_fee',
            'certified_copy_certificate_of_registration_fee',
            'document_filing_fee_section_12_act_excluding_balance_sheet',
            'balance_sheet_filing_fee_section_12_act',
            'late_filing_penalty_monthly_fee_section_12_act',
        ],
        'text': (
            'Ada nyingine za kuwasilisha nyaraka BRELA: kuwasilisha memorandum na articles ni TZS '
            '66,000; stempu kwa kila nakala ya memorandum TZS 10,000; fomu 14B TZS 1,200; '
            'kupokea/kusajili nyaraka TZS 22,000; kuthibitisha nyaraka kwa ukurasa TZS 3,000; '
            'kutafuta faili TZS 3,000 na ripoti ya utafutaji TZS 22,000; nakala iliyothibitishwa '
            'ya cheti cha usajili TZS 4,000. Kampuni ya kigeni (kifungu 12): kuwasilisha nyaraka '
            'USD 220, mizania USD 220, na faini ya kuchelewa USD 25 kwa mwezi.'),
    },
    'electrical_test_fee_reduction': {
        # Found 2026-09-03: the R15 regen packaged in fc9b0c8 self-retrieval-failed on this
        # pair -- electrical_test_fee_reduction_initial retrieves its OWN sibling (_final) at
        # 0.925 cosine instead of itself. Both facts open with near-identical sentences
        # ("TZS N was/is the [OLD/REDUCED] fee for OSHA electrical-system inspection at RURAL
        # FUEL STATIONS specifically... NOT a general/universal OSHA electrical inspection
        # fee") -- the two texts differ mainly in the single number and OLD/REDUCED adjective,
        # which is exactly the shape e5-base collapses to a near-duplicate embedding. A fact
        # that cannot retrieve itself can never be served; per instruction this must be fixed,
        # not left as a tolerated <10% self-retrieval failure. Merged into one passage, the
        # same treatment as the fee-schedule groups above -- a before/after fee pair is a
        # single retrievable fact ("the fee dropped from X to Y"), not two competing rows for
        # the same underlying question. Both figures verified to survive verbatim (checked by
        # _figure_of's substring containment below).
        'keys': ['electrical_test_fee_reduction_initial', 'electrical_test_fee_reduction_final'],
        'text': (
            'Ada ya ukaguzi wa umeme OSHA kwa VITUO VYA MAFUTA VIJIJINI (majaribio manne: '
            'Polarity, Continuity, Earth Resistance, Insulation Test) ilipunguzwa mwaka 2025 '
            'kutoka TZS 650,000 hadi TZS 150,000 ili kuhamasisha uwekezaji vijijini. Hii SI ada '
            'ya jumla ya ukaguzi wa umeme kwa maeneo yote ya kazi -- kila kiwanda/eneo la kazi '
            'linalotumia umeme linahitajika kukaguliwa KILA MWAKA chini ya Cap.297 kifungu '
            '66(2), kwa ada tofauti isiyothibitishwa (si TZS 650,000 wala 150,000).'),
    },
}

# Every member key must exist, and every member's FIGURE must survive into the group text.
# R20: this assertion can fail -- drop a band from the ladder text and the build stops. That is
# the only thing standing between "consolidated" and "silently lost a fee".
_GROUP_MEMBERS = {k: g for g, spec in FACT_GROUPS.items() for k in spec['keys']}


def _figure_of(value: str):
    """The number a fee row asserts, normalised for containment in the group text."""
    m = re.search(r'([\d][\d,]*(?:\.\d+)?)', value or '')
    return m.group(1) if m else None


# --- Noise keys to drop, two different mechanisms ---
#
# SHAPE-BASED (regex): safe to guess by pattern because the SHAPE alone -- bare
# citation, bare section number, no independent value -- determines low retrieval
# value regardless of what the content says. These patterns target structure, not
# subject matter, so a new key matching one of them is safe to drop unread.
_NOISE_KEY_PATTERNS = [
    r'^legal_citation_',
    r'_act_citation$',
    r'_act_section$',
    r'_rules_section$',
    r'_act_reference$',
    r'_act_chapter$',
    r'^order_made_under_section$',
    r'^offence_penalty_mention$',
    r'^prohibited_business_activities_for_non_citizens_order_year$',
    r'^gn487a_signatory$',  # low-value (who signed the order) — was outranking the 10M penalty
]

# CONTENT-REVIEWED (explicit list, not a pattern): `^exemption_category_` used to be
# a regex here. It swept up all 10 exemption_category_* keys on the strength of their
# NAME alone -- but their CONTENT is real (ten genuine exempt-employer categories, verified
# 2026-08-17 by reading each value), not the bare-citation shape the other patterns
# target. A prefix guess cannot tell those apart; only reading the content can. These
# 10 are excluded here because they are now consolidated into ONE retrievable fact
# (sdl_exemption_categories, in CONCISE_BILINGUAL_FACTS above) -- not because the
# prefix looks like the other noise patterns. THE LESSON, for whoever names the next
# family: a key-name pattern is only safe for shape (a citation is always low-value no
# matter what it cites); it is never safe for a content-bearing family -- add those
# here, individually, after reading them, not as a regex.
_NOISE_KEYS_REVIEWED = {
    # 'contribution_rate_emplyees' -- traced as one of FOUR named live-defect sources in the
    # FACT_GROUPS comment above ([209], "THE NSSF 10%-vs-20% collapse"), still live as of the
    # fc9b0c8 regen (2026-09-03): confirmed reshuffled into nat_27's post-regen top-3 alongside
    # unrelated NSSF rows, still misspelled, still rendering as the context-free, unqualified
    # "contribution rate emplyees: 10 %" this comment already predicted would keep happening.
    # R25 test: (1) what defect does dropping this repair? An unqualified employee-only 10%
    # figure with no "of 20% total" framing, highly retrievable on ANY NSSF-rate question,
    # competing against the correctly-framed nssf_employer_rate/nssf_total_rate facts. (2) what
    # correct output could dropping it damage? None -- nssf_total_rate's own CONCISE text
    # ("NSSF jumla: asilimia 20 ya mshahara (10% mwajiri + 10% mfanyakazi)") already states the
    # employee's 10% share, correctly disambiguated from the employer's and the total. This key
    # adds no reachable content that isn't already better-stated elsewhere; dropped as noise
    # rather than merged (it has no fee-schedule sibling to consolidate with, and its content is
    # a strict subset of an existing fact -- see the FACT_GROUPS comment's own note that [209]
    # "needs its own fix, not absorption").
    'contribution_rate_emplyees',
    # 'penalty_fine_non_citizen' -- found 2026-09-03 while re-adjudicating nat_36's post-regen
    # top-3, the SAME shape and same discovery route as contribution_rate_emplyees above: an
    # old-schema, context-free bare fragment ("penalty fine non citizen: ten million TZS") that
    # is a strict, less-precise SUBSET of the existing gn487a_penalty_noncitizen CONCISE fact
    # (which already states the figure in both digit and word form, PLUS the imprisonment term
    # and visa-revocation consequence, PLUS wrong_patterns guarding against the 5M/3-month
    # confusions). R25 test: (1) defect repaired -- an unqualified "ten million TZS" fragment
    # was crowding nat_36's top-3 (an EFD-threshold question, nothing to do with GN487A
    # penalties). (2) correct output damaged by dropping it -- none; gn487a_penalty_noncitizen
    # already carries every fact this key states and more, and already has its own dedicated
    # displacement guard in kaggle/regenerate_rag_e5.py.
    'penalty_fine_non_citizen',
    'exemption_category_government_departments',
    'exemption_category_diplomatic_missions',
    'exemption_category_religious_institutions',
    'exemption_category_educational_institutions',
    'exemption_category_farm_employers_agriculture',
    'exemption_category_charitable_organizations',
    'exemption_category_local_government_authorities',
    'exemption_category_trainees_under_TAESA',
    'exemption_category_un_and_agencies',
    'exemption_category_international_organizations_aid',
}


def is_noise_key(key: str) -> bool:
    return key in _NOISE_KEYS_REVIEWED or any(re.search(p, key) for p in _NOISE_KEY_PATTERNS)


def fact_value(v) -> str:
    if isinstance(v, dict):
        return (v.get('fact') or v.get('correct_value') or '').strip()
    return str(v).strip()


def build_fact_text(key: str, value: str) -> str:
    # Concise Swahili-dominant text for high-stakes facts (short — no long English tail).
    if key in CONCISE_BILINGUAL_FACTS:
        return CONCISE_BILINGUAL_FACTS[key]
    # All other facts: readable key + value.
    key_readable = key.replace('_', ' ')
    return f'{key_readable}: {value}'


def build_fact_texts():
    """Return (kept_texts, kept_keys, dropped_keys) — importable without side effects.

    Rows are emitted per fact key, EXCEPT that FACT_GROUPS members are absorbed into one
    consolidated passage per group, appended after the per-key rows (the position the
    2026-08-25 measurement used).
    """
    with open(FACTS_PATH, encoding='utf-8') as f:
        facts = json.load(f)

    missing = [k for k in _GROUP_MEMBERS if k not in facts]
    assert not missing, (
        f'FACT_GROUPS names {len(missing)} key(s) absent from locked_facts.json: {missing}. '
        f'A renamed or removed fact would otherwise be silently dropped from the index.')

    texts, keys, dropped, absorbed = [], [], [], []
    for k, v in facts.items():
        if k == '_meta':
            continue
        if is_noise_key(k):
            dropped.append(k)
            continue
        if k in _GROUP_MEMBERS:
            absorbed.append(k)
            continue
        texts.append(build_fact_text(k, fact_value(v)))
        keys.append(k)

    for gname, spec in FACT_GROUPS.items():
        lost = [k for k in spec['keys']
                if (fig := _figure_of(fact_value(facts[k]))) and fig not in spec['text']]
        assert not lost, (
            f"group '{gname}' drops the figure asserted by {lost} — consolidation must carry "
            f'every absorbed value into the passage, or the index has lost a fee.')
        texts.append(spec['text'])
        keys.append(gname)

    assert len(absorbed) == len(_GROUP_MEMBERS), (absorbed, sorted(_GROUP_MEMBERS))
    return texts, keys, dropped


if __name__ == '__main__':
    from sentence_transformers import SentenceTransformer

    fact_texts, fact_keys, dropped = build_fact_texts()
    print(f'[rag] kept {len(fact_texts)} facts, dropped {len(dropped)} noise')

    print(f'[rag] Loading model: {EMBED_MODEL}')
    model = SentenceTransformer(EMBED_MODEL)

    # e5 asymmetric retrieval: embed facts as passages. The plain fact_texts are
    # still what gets saved + injected into the prompt; only the embedded copy is
    # prefixed. Queries get the 'query: ' prefix at retrieval time in modal_app.py.
    print(f'[rag] Embedding {len(fact_texts)} facts (with e5 passage prefix)...')
    fact_texts_prefixed = [E5_PASSAGE_PREFIX + t for t in fact_texts]
    embeddings = np.array(model.encode(fact_texts_prefixed, show_progress_bar=True))

    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    embeddings = embeddings / (norms + 1e-10)
    print('[rag] normalized embeddings for cosine similarity')

    np.save(OUTPUT_NPY, embeddings)
    with open(OUTPUT_TEXTS, 'w', encoding='utf-8') as f:
        json.dump(fact_texts, f, ensure_ascii=False, indent=2)

    print(f'[rag] Saved {OUTPUT_NPY} ({embeddings.shape})')
    print(f'[rag] Saved {OUTPUT_TEXTS} ({len(fact_texts)} facts)')
