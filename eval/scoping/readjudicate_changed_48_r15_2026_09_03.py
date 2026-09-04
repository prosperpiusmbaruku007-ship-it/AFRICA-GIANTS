# -*- coding: utf-8 -*-
"""⛔ CORRECTED 2026-09-04 -- the original "GROUNDING" claim below for nat_28/nat_44 was
WRONG, found while building the pilot re-derivation and checking the claim instead of
repeating it (R22's own standing lesson, applied to this file by its author one day
later). Reproducing production retrieval for both questions shows the actual VAT-
withholding RATE facts (rows 16/17) rank 7th-16th -- never in production's top-3/pooled-9
window. Neither reply is grounded in retrieved content; both are UNGROUNDED, correct from
weights despite an irrelevant retrieved context -- the SAME shape as nat_37's regression,
not its opposite. See nat_28's and nat_44's VERDICTS entries below for the full account
and eval/results/natural48_readjudicated_2026_09_03.json's corrected `cause` fields (the
artifact was re-generated from this corrected script, not hand-edited). The headline
"zero of the 48 touch corporate tax" finding is UNAFFECTED (still true, still checked) --
only the causal story for WHY nat_28/nat_44/nat_30 improved is corrected: it is retrieval-
noise reshuffling between regens producing a different irrelevant context each time, and
three of four moved rows this cycle happened to land right where one (nat_37) landed
wrong. That is a materially different, more sobering finding than "grounding delivered
wins," and PROGRESS.md's pilot re-derivation (2026-09-04) carries the corrected account.

Re-adjudication of the 48 natural probes against chike-inference redeployed at c9b2425
(the R15 regen -- 183-row content-keyed index, landed efe5956 -- plus the corporate-tax
ask-alignment rewrite from 4974cbc/0fce8b6, plus the content-keyed pin redesign, c9b2425).

METHOD, same discipline as eval/scoping/readjudicate_changed_48.py (2026-08-24): fetch fresh
live replies for all 48 questions (eval/results/raw/natural48_live_replies_2026_09_03_c9b2425.json,
via ChikeModel().run.remote(), greedy decoding so this is reproducible, not sampling noise),
diff against the most recent PRIOR known state (eval/results/natural48_readjudicated_2026_08_24.json's
verdict_2026_08_24/reply_2026_08_24 -- the correct baseline to diff against, not the raw
2026-08-17 file, since three rows already moved between those two dates). Byte-identical
replies cannot have changed verdict and are carried forward unadjudicated; only the rows
whose reply text changed are re-read against their own rubric
(eval/accuracy_gate/edge_probe_natural_048.jsonl's expected_behavior).

14 of 48 replies changed. Adjudicator: Claude (Sonnet 5), against each row's own committed
rubric, reasoning recorded in full below rather than as a bare verdict.

WHY THIS MATTERS BEYOND THE TALLY, per explicit instruction: separate any movement into
GROUNDING (the verification arc's fact corrections landing in the R15 index -- VAT
withholding rates, the EFD-threshold fabrication fix) versus the CORPORATE-TAX
ASK-ALIGNMENT REWRITE (corporate_tax_rate / minimum_turnover_tax), since both landed in the
same regen cycle and attributing a shift to the wrong cause is a standing project lesson
(R22). Finding: ZERO of the 48 natural questions touch corporate tax or the Alternative
Minimum Tax at all -- the ask-alignment rewrite has no natural-48 touchpoint, so it
contributed NOTHING to any movement measured here (it was separately verified live and
correct via the R16 canary run, eval/results/raw/r16_canary_c9b2425.json -- just not through
this fixture). Every row that moved traces to grounding: VAT-withholding facts (nat_28,
nat_44) and the EFD-threshold-fabrication fix (nat_36) becoming retrievable/correctly worded
as the wider verification arc's fact corrections landed in this regen's index.

One regression found and NOT explained by either mechanism: nat_37 moved CORRECT -> WRONG,
a newly fabricated small-transaction EFD exemption. Recorded as an open finding, not
root-caused here -- out of this pass's scope (R16 redeploy verification + probe re-run),
flagged for follow-up.

R18: committed before its result is written up.
Source live replies: eval/results/raw/natural48_live_replies_2026_09_03_c9b2425.json
Prior state: eval/results/natural48_readjudicated_2026_08_24.json
Artifact: eval/results/natural48_readjudicated_2026_09_03.json
"""
import json
import os
import sys
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(REPO, 'eval', 'results', 'natural48_readjudicated_2026_09_03.json')

PRIOR = os.path.join(REPO, 'eval', 'results', 'natural48_readjudicated_2026_08_24.json')
LIVE = os.path.join(REPO, 'eval', 'results', 'raw',
                     'natural48_live_replies_2026_09_03_c9b2425.json')
FIXTURE = os.path.join(REPO, 'eval', 'accuracy_gate', 'edge_probe_natural_048.jsonl')

# --- The 14 verdicts. Adjudicator: Claude (Sonnet 5), against each row's own committed
# rubric (edge_probe_natural_048.jsonl's expected_behavior). ---
VERDICTS = {
    'nat_27': {
        'new': 'CORRECT', 'cause': 'no change in substance',
        'why': 'Still states 18% VAT, the rubric\'s only requirement. Reply text changed '
               '(dropped "%" glyph and the "kiwango cha kawaida" clause, lowercased '
               '"tra.go.tz") but the asserted figure and its correctness are identical -- a '
               'generation-formatting difference, not a retrieval or fact change. Flagged '
               'because this is the exact row named in the standing "nat_27 top-3 has never '
               'contained the intended fact across three regens" finding -- the ANSWER stays '
               'right despite that, which is worth recording as its own separate fact (the '
               'model is not solely dependent on this fact ranking top-3 to answer correctly '
               'here), not evidence the ranking problem is resolved.',
    },
    'nat_28': {
        'new': 'CORRECT', 'cause': 'CORRECTED 2026-09-04 -- NOT grounding. See note.',
        'why': 'WRONG -> CORRECT. Old reply answered a different tax entirely (15% royalties '
               'withholding -- wrong topic). New reply states VAT withholding 6% for services '
               '(Finance Act 2025) AND the correct certificate-timing rule (issued the day VAT '
               'becomes payable, not the 20th) -- both rubric requirements met exactly.\n\n'
               'CORRECTION, 2026-09-04, found while building the pilot re-derivation and '
               'checking this claim rather than repeating it: "GROUNDING" was asserted here '
               'without checking whether the VAT-withholding RATE facts (vat_withholding_goods '
               '/ vat_withholding_services, rows 16/17) are actually within retrieval reach for '
               'this question. Checked directly: they are NOT. Reproducing production retrieval '
               '(decompose_query + top-3-per-subquestion pooling) for this exact question '
               'returns rows 11/149/156 (an NSSF penalty fact, a contribution-frequency '
               'fragment, a retirement-fund deadline) -- zero VAT-withholding content of any '
               'kind. Row 17 (the 6% services fact) ranks 10th; row 16 (3% goods) ranks 15th -- '
               'both well outside production\'s top-3/pooled-9 window. This reply is UNGROUNDED: '
               'correct despite retrieval not surfacing the relevant fact, the same shape as '
               'nat_26/27/36 (weights-answered) -- and the same shape as nat_37\'s regression, '
               'which is the more important point: this is not "grounding delivered a win", it '
               'is retrieval-noise reshuffling between regens producing a DIFFERENT irrelevant '
               'context, and this time the model\'s own weights landed on the right answer '
               'anyway rather than the wrong one. Three of the four rows that moved this cycle '
               '(nat_28, nat_30, nat_44) share this shape; only nat_37 landed the other way. '
               'See the pilot re-derivation (PROGRESS.md, 2026-09-04) for the full, corrected '
               'account -- this was reported to the founder as "GROUNDING" before this check was '
               'done, and that was wrong.',
    },
    'nat_29': {
        'new': 'PARTIAL', 'cause': 'no verdict change',
        'why': 'Still PARTIAL. Correctly says mobile money transfer is prohibited for '
               'non-citizens regardless of the Tanzanian partner\'s citizenship (an '
               'improvement in clarity over the old reply\'s bare citation), but still never '
               'states the FACILITATION penalty (TZS 5,000,000 or 3 months for the Tanzanian '
               'fronting) that the rubric requires for CORRECT.',
    },
    'nat_30': {
        'new': 'CORRECT', 'cause': 'unclear -- not attributable to either named mechanism',
        'why': 'PARTIAL -> CORRECT. Old reply reached the right conclusion (no) through '
               'confusing, reversed-subject prose ("dada yako hawezi kumruhusu mumewe..." -- '
               'literally "your sister cannot ALLOW her husband..."). New reply states the '
               'prohibition directly and cites GN487A. Rubric\'s only WRONG condition '
               '("yes, because married to a citizen") does not appear in either version, so '
               'this move is a PROSE-CLARITY fix, not a fact fix -- neither grounding nor the '
               'corporate-tax rewrite plausibly explain it (this is a GN487A row, untouched by '
               'both); most likely ordinary generation variance on a correct-but-messy answer.',
    },
    'nat_31': {
        'new': 'CORRECT', 'cause': 'no change in substance',
        'why': 'Still states TZS 10,000,000 minimum + 6 months + visa revocation. "AU" '
               '(old) vs "isiyo pungua" / not-less-than (new) is a precision improvement, not '
               'a correctness change.',
    },
    'nat_34': {
        'new': 'CORRECT', 'cause': 'no change in substance',
        'why': 'Still states name reservation 50,000 + incorporation 95,000. Reordered and '
               'tightened, same figures.',
    },
    'nat_35': {
        'new': 'PARTIAL', 'cause': 'no verdict change (weaker within the bucket)',
        'why': 'Still PARTIAL -- no fabricated member limit or fee (the rubric\'s only WRONG '
               'trigger), so this cannot be scored WRONG. But the new reply ("Kampuni au '
               'ushirika unaweza kuwasilisha taarifa kwa BRELA") is materially thinner than '
               'the old one -- it no longer explains the partnership-vs-company tradeoff at '
               'all, just that both file with BRELA. Recorded as a quality regression worth '
               'watching even though it does not cross into WRONG.',
    },
    'nat_36': {
        'new': 'CORRECT', 'cause': 'GROUNDING -- but the verdict LABEL is misleading; read this one',
        'why': 'Labelled CORRECT on both sides of this diff, which conceals the real story. '
               'The rubric in edge_probe_natural_048.jsonl now reads "EFD is required BY '
               'DEFAULT regardless of turnover ... WRONG = citing any turnover figure '
               '(11,000,000 or otherwise) as a threshold." That rubric text postdates the '
               '2026-08-29 finding that efd_threshold_tzs_11m was FABRICATED (CLAUDE.md '
               '"failure modes" table) -- the 08-24 old_reply ("mauzo yako ... yamefikia au '
               'kuzidi kizingiti cha TZS 11,000,000") cites EXACTLY the turnover-threshold '
               'framing the CURRENT rubric calls WRONG, and would fail if re-adjudicated '
               'against it today; it was scored CORRECT on 08-24 against the rubric as it '
               'existed then, before the fabrication was found. The new reply states the '
               'CORRECT current framing: no turnover threshold, exemption only via a '
               'Commissioner-General public notice. So the honest read is WRONG-under-today\'s-'
               'rubric -> CORRECT, not CORRECT -> CORRECT. Attributed to GROUNDING: the '
               'efd_threshold_tzs_11m fabrication fix, plus this session\'s own pin-needle '
               'disambiguation (c9b2425, separating this fact\'s row 56 from the unrelated '
               'efd_not_every_business row 57 that shared the same "TZS 11,000,000" substring) '
               '-- this is the exact fragment-displacement/guard-specificity issue named in '
               'this session\'s brief as still open, and this result is evidence it is now '
               'closed, not merely diagnosed.',
    },
    'nat_37': {
        'new': 'WRONG', 'cause': 'REGRESSION -- NOT explained by grounding or the corporate-tax rewrite',
        'why': 'CORRECT -> WRONG. Old reply correctly stated an EFD receipt is required for '
               'every transaction regardless of amount. New reply invents a minimum-value '
               'exemption ("Kwa mauzo chini ya TZS 500, risiti ya kawaida ya biashara '
               'inatosha") -- exactly the fabrication the rubric names as its WRONG condition. '
               'This is a real regression, greedy decoding so not sampling noise, and its '
               'cause is NOT identified by this pass: it touches neither the VAT-withholding '
               'facts (nat_28/44\'s grounding fix) nor the EFD-threshold fix (nat_36) nor the '
               'corporate-tax rewrite. Flagged as an open finding for follow-up, not '
               'root-caused here -- out of scope for an R16 deploy-verification + probe-rerun '
               'pass.',
    },
    'nat_38': {
        'new': 'CORRECT', 'cause': 'no change in substance',
        'why': 'Still states VAT-registered businesses always need EFD regardless of '
               'turnover; new reply adds the same CG-notice-only-exemption clarification seen '
               'in nat_36, consistent with that fix, not a separate change.',
    },
    'nat_40': {
        'new': 'CORRECT', 'cause': 'no change in substance',
        'why': 'Still correctly distinguishes OSHA (inspects, does not pay) from WCF (pays '
               'compensation). "Mamlaka" vs "Ofisi" wording only.',
    },
    'nat_42': {
        'new': 'PARTIAL', 'cause': 'no verdict change (different failure mode within the bucket)',
        'why': 'Still PARTIAL, but the failure shape changed. Old reply gave the sector '
               'AVERAGE (358,322) to a question asking the general minimum-wage floor -- '
               'reasonable but not sector-specific. New reply gives 765,900, the TOP of the '
               'range (international mining/energy) -- a real figure, not the revoked 2022 '
               'figure the rubric explicitly forbids, but a confusing answer to a general '
               'question since it implies the ceiling is the floor. Neither version explains '
               'the sector-dependency the rubric actually asks for, so both stay PARTIAL. Also '
               'noting a citation-source change worth a separate look: new reply cites "VELMA '
               'LAW" where old cited "PKF Eastern Africa au TanzLII" -- VELMA is a Tier 1A '
               'EVAL-family source (CLAUDE.md R6), not meant to surface as a training-facing '
               'citation.',
    },
    'nat_43': {
        'new': 'CORRECT', 'cause': 'no change in substance (citation concern flagged separately)',
        'why': 'Still correctly says minimum wage varies by sector under GN605A -- the '
               'rubric\'s only requirement. Separately concerning: new reply cites "MLYWF '
               '(mlywf.go.tz)" where old cited "GN 605A" directly -- mlywf.go.tz does not '
               'appear in CLAUDE.md\'s Section 4 primary-source whitelist (the labour source '
               'listed there is kazi.go.tz). Possibly a real ministry domain not yet '
               'whitelisted, or a hallucinated one -- not verified here, flagged for a source-'
               'enforcer pass rather than adjudicated as WRONG (the rubric is about content, '
               'not citation domain).',
    },
    'nat_44': {
        'new': 'CORRECT', 'cause': 'CORRECTED 2026-09-04 -- NOT grounding. Same correction as nat_28.',
        'why': 'WRONG -> CORRECT. Old reply gave 6% (the services rate) for a goods-sale '
               'question. New reply states both rates correctly labelled: 3% for goods, 6% '
               'for services, answering the goods question right.\n\n'
               'CORRECTION, 2026-09-04, same check as nat_28 (see its note for the full '
               'account): reproducing production retrieval for this exact question returns '
               'rows 75/107/63 (a VAT-withholding-BASE dispute-resolution note, the '
               'late_payment_penalty_rate noise fact this same session dropped as harmful '
               'elsewhere, and a withholding-formula fact) -- NOT the rate facts themselves. '
               'Row 16 (3% goods) ranks 7th, row 17 (6% services) ranks 16th -- outside '
               'production\'s retrieval window. UNGROUNDED, not GROUNDING -- correct from '
               'weights despite an irrelevant retrieved context, the same shape as nat_28 and '
               'nat_37\'s regression.',
    },
}


def main():
    with open(PRIOR, encoding='utf-8') as f:
        prior = json.load(f)
    with open(LIVE, encoding='utf-8') as f:
        live = {r['id']: r for r in json.load(f)}
    with open(FIXTURE, encoding='utf-8') as f:
        fixture = {json.loads(l)['id']: json.loads(l) for l in f}

    prior_by_id = {r['id']: r for r in prior['rows']}

    rows = []
    for rid in sorted(fixture, key=lambda k: int(k.split('_')[1])):
        p = prior_by_id[rid]
        l = live[rid]
        reply_changed = (l['reply'] or '').strip() != (p['reply_2026_08_24'] or '').strip()
        rec = {
            'id': rid, 'path': p['path'], 'question': fixture[rid]['question'],
            'expected_behavior': fixture[rid]['expected_behavior'],
            'verdict_2026_08_24': p['verdict_2026_08_24'],
            'reply_2026_08_24': p['reply_2026_08_24'],
            'reply_2026_09_03': l['reply'],
            'reply_changed': reply_changed,
        }
        if reply_changed:
            v = VERDICTS[rid]
            rec['verdict_2026_09_03'] = v['new']
            rec['cause'] = v['cause']
            rec['adjudication'] = v['why']
        else:
            rec['verdict_2026_09_03'] = p['verdict_2026_08_24']
            rec['cause'] = 'unchanged reply -- carried forward, not re-adjudicated'
            rec['adjudication'] = None
        rows.append(rec)

    before = Counter(r['verdict_2026_08_24'] for r in rows)
    after = Counter(r['verdict_2026_09_03'] for r in rows)
    moved = [r['id'] for r in rows if r['verdict_2026_08_24'] != r['verdict_2026_09_03']]
    causes = Counter(VERDICTS[rid]['cause'] for rid in moved)

    out = {
        'readjudicated': '2026-09-03',
        'harness': os.path.relpath(__file__, REPO).replace('\\', '/'),
        'deploy': 'chike-inference @ c9b2425 (183-row R15 index, content-keyed pin redesign)',
        'live_replies_source': os.path.relpath(LIVE, REPO).replace('\\', '/'),
        'prior_state_source': os.path.relpath(PRIOR, REPO).replace('\\', '/'),
        'method': ('fetch fresh live replies for all 48 (greedy decoding, reproducible); '
                   'diff against 2026-08-24 replies; only changed replies re-adjudicated '
                   'against edge_probe_natural_048.jsonl\'s expected_behavior; unchanged '
                   'replies carry their prior verdict forward'),
        'adjudicator': 'Claude (Sonnet 5), against each row\'s own committed rubric',
        'n_replies_changed': len(moved) if False else sum(1 for r in rows if r['reply_changed']),
        'n_verdicts_changed': len(moved),
        'overall_before_2026_08_24': dict(before),
        'overall_after_2026_09_03': dict(after),
        'moved_rows': moved,
        'cause_breakdown_of_moved_rows': dict(causes),
        'headline': (
            'CORRECTED 2026-09-04. Zero of the 48 natural questions touch corporate tax or '
            'the Alternative Minimum Tax -- the corporate-tax ask-alignment rewrite '
            '(corporate_tax_rate / minimum_turnover_tax) has no natural-48 touchpoint and '
            'contributed nothing to any movement measured here (verified separately, live '
            'and correct, via the R16 canary run). That part of the original headline stands. '
            'The rest does not: the original claimed the 4 moved rows traced to "GROUNDING" '
            '(retrieval reaching a correct fact). Checked directly and found wrong: for '
            'nat_28/nat_44, the actual VAT-withholding rate facts rank 7th-16th, never in '
            'production\'s top-3 retrieval window -- both replies are UNGROUNDED, correct '
            'from weights despite irrelevant retrieved context. nat_30 was already correctly '
            'marked "unclear" in the original pass. nat_36\'s live reply is ALSO ungrounded '
            'today -- its real fix (efd_not_every_business\'s corrected, ask-aligned CONCISE '
            'text) is prepared and locally verified but NOT YET SHIPPED to production (staged '
            'in commit 951fb67, pending the next Kaggle regen); today\'s correct nat_36 answer '
            'is weights-answered, same as before. So: THREE of the four moved rows this '
            'cycle (nat_28, nat_30, nat_44) and the one regression (nat_37) are the SAME '
            'phenomenon -- retrieval-noise reshuffling between regens producing a different '
            'irrelevant context each time, with the model\'s weights landing on the right '
            'answer three times and the wrong answer once. This is retrieval INSTABILITY '
            'exposed, not grounding delivered. See PROGRESS.md\'s 2026-09-04 pilot '
            're-derivation for the full account.'
        ),
        'rows': rows,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(f"BEFORE (2026-08-24): {dict(before)}")
    print(f"AFTER  (2026-09-03): {dict(after)}")
    print(f"{len(moved)} verdict(s) moved: {moved}")
    print(f"cause breakdown: {dict(causes)}")
    print(f"\n[saved] {OUT}")


if __name__ == '__main__':
    main()
