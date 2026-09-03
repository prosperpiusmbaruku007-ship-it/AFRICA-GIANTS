# -*- coding: utf-8 -*-
"""
Regenerate the RAG index with intfloat/multilingual-e5-base (768-dim) ON KAGGLE.

Why Kaggle: the e5-base weights (~1.1 GB) do not download on the local Tanzania
network (ISP block stalls the transfer ~737 MB in), so the 768-dim embeddings must
be produced where the network works. This is the R15 workaround process.

What it does:
  1. Resolve scripts/locked_facts.json + scripts/precompute_rag_embeddings.py — LOCAL
     files if this is a git checkout with both present (self-consistent, no network),
     GitHub raw fetch only otherwise (single source of truth in the no-checkout case).
  2. Build the fact texts via precompute.build_fact_texts() (importable, no side effects).
  3. Embed with e5-base (facts get the 'passage: ' prefix; queries get 'query: ').
  4. FULL VERIFICATION: every fact must self-retrieve at rank 1, AND all critical
     known-failure queries must hit their expected fact in the top-3.
  5. Save + upload rag_embeddings.npy + rag_facts_text.json to the HF DATASET repo
     ONLY if verification passes. modal_app.py bakes these from chike-inference/ and
     eval.py fetches them from the dataset repo — so both consumers get the same index.
     Both files land in ONE atomic Hub commit (create_commit, not two independent
     upload_file calls) — see the OPERATIONAL note near the upload section for why.

Run this in a Kaggle notebook cell, then paste the verification output back.

OPERATIONAL (2026-08-17): every Kaggle harness in this project (eval.py, the probe
scripts, this one) bootstraps by fetching from raw.githubusercontent.com / the GitHub
API, all unauthenticated, all sharing ONE per-IP rate budget (GitHub: ~60 req/hr
unauthenticated). A regen run on 2026-08-17 hit 429 twice in the SAME run — once on
the commit-SHA lookup, once on the locked_facts.json fetch two lines later — while
running from a fresh git clone where every file this script needed was already on
disk. The clone made the fetches redundant, not safer: a checkout plus N independent
re-fetches of files already in that checkout is its own drift risk (the fetch could
in principle land a DIFFERENT commit than the one just cloned), on top of burning
budget every other harness in this list draws from. This script now prefers the
checkout when one exists; the other scripts in kaggle/ still fetch unconditionally
and remain exposed to the same shared budget — not fixed here, logged so it isn't
rediscovered as a surprise mid-run again.
"""
import os
import subprocess
import sys
import json
import importlib.util

import numpy as np
import requests

# ── AUTH ────────────────────────────────────────────────────────────────────────
try:
    import kaggle_secrets
    hf_token = kaggle_secrets.UserSecretsClient().get_secret('AFRICA_GIANTS')
    print(f'[auth] HF token from Kaggle secret ({hf_token[:8]}...)')
except Exception as e:
    hf_token = os.environ.get('HF_TOKEN', '')
    print(f'[auth] fallback env HF_TOKEN: {hf_token[:8] if hf_token else "MISSING"}')
os.environ['HF_TOKEN'] = hf_token

DATASET_REPO = 'prospAprospA007/africa-giants-dataset'
GH_REPO = 'prosperpiusmbaruku007-ship-it/AFRICA-GIANTS'
RAW = f'https://raw.githubusercontent.com/{GH_REPO}/main'
SOURCE_FILES = ['scripts/locked_facts.json', 'scripts/precompute_rag_embeddings.py']

# ── EXPECTED_HEAD — the commit this package was packaged FOR ────────────────────
# Found 2026-08-26: this script printed 'GitHub main HEAD = <sha>' at startup and NOTHING
# read it. Three commits (the fee consolidation, mof.go.tz, and the guards/rank-gate this
# very check lives in) sat local-only, unpushed, while this notebook was being prepared to
# run on Kaggle -- a clean clone of origin/main would have resolved to 5c55470, BEFORE the
# consolidation existed, and this script would have happily rebuilt the OLD 221-row index,
# printed [OK] on every guard (nothing about the old index is wrong FOR the old index), and
# uploaded it -- a fully successful-looking run that shipped exactly nothing of what it was
# run for. The print statement recorded the fact; it did not stop anything.
#
# Set this to the short SHA of the commit that most recently changed what this script
# DEPENDS ON being present (FACT_GROUPS, the rank-regression gate, the five local-levy
# guards) whenever this file is intentionally repackaged. It is NOT the SHA of the commit
# that contains this line (that commit cannot know its own hash) -- it is the commit this
# packaging assumes as a floor. A clone at that commit OR ANY DESCENDANT of it is fine; a
# clone that does not contain it as an ancestor means the required commits were never
# pushed, and this script must refuse to run rather than quietly build the wrong index.
#
# BUMPED 2026-09-03 (second bump, same day): fc9b0c8's regen shipped and was re-
# adjudicated (nat_27/nat_36 KNOWN-FAIL re-check) -- found and fixed 3 more defects
# AFTER that run completed: electrical_test_fee_reduction_initial/_final's self-
# retrieval failure (merged into a FACT_GROUPS passage), and two typo'd/duplicate NSSF
# and GN487A fragments (contribution_rate_emplyees, penalty_fine_non_citizen) dropped
# as noise plus two genuine NSSF facts (maternity_cash_benefit_rate,
# unpaid_contribution_penalty_rate) given ask-aligned rewrites. None of this is in the
# index currently deployed (fc9b0c8-built) -- this floor exists so the NEXT regen
# cannot silently rebuild without them.
EXPECTED_HEAD = '951fb67'


def _assert_expected_head_present(local_head, live_sha):
    """Abort BEFORE any model load or embedding work if the resolved commit does not
    contain EXPECTED_HEAD as an ancestor (or equal it). Two paths, matching the two ways
    _live_sha above gets resolved -- local git checkout (no network) or GitHub API fetch
    (one extra lightweight call, only on the fallback path that already hits the network)."""
    if local_head:
        try:
            out = subprocess.run(
                ['git', 'merge-base', '--is-ancestor', EXPECTED_HEAD, 'HEAD'],
                capture_output=True, text=True, timeout=10)
        except Exception as e:
            print(f'[FATAL] could not verify HEAD ancestry locally ({e}) -- refusing to '
                  f'guess. Push and re-clone, or fix git availability.')
            sys.exit(1)
        if out.returncode != 0:
            print(f'[FATAL] checkout HEAD ({live_sha}) does NOT contain {EXPECTED_HEAD} as '
                  f'an ancestor. This script was packaged assuming {EXPECTED_HEAD} (fee '
                  f'consolidation + rank gate + local-levy guards) is already on the branch '
                  f'being built from. Push your local commits to origin/main and re-clone '
                  f'before running this notebook -- otherwise this run silently rebuilds '
                  f'the OLD index and reports success.')
            sys.exit(1)
    else:
        try:
            cmp_resp = requests.get(
                f'https://api.github.com/repos/{GH_REPO}/compare/{EXPECTED_HEAD}...{live_sha}',
                timeout=30)
            cmp_resp.raise_for_status()
            status = cmp_resp.json().get('status')
        except Exception as e:
            print(f'[FATAL] could not verify HEAD ancestry via GitHub compare API ({e}) -- '
                  f'refusing to guess.')
            sys.exit(1)
        if status not in ('identical', 'ahead'):
            print(f'[FATAL] GitHub main ({live_sha}) does not contain {EXPECTED_HEAD} as an '
                  f'ancestor (compare status={status!r}). The required commits (fee '
                  f'consolidation + rank gate + local-levy guards) are not on origin/main -- '
                  f'push them first. Otherwise this run silently rebuilds the OLD index and '
                  f'reports success.')
            sys.exit(1)
    print(f'[OK] HEAD ({live_sha}) contains the expected baseline {EXPECTED_HEAD}')

# ── RESOLVE SOURCE OF TRUTH: LOCAL CHECKOUT FIRST, RAW FETCH ONLY AS FALLBACK ────
# A git checkout with both files already present is authoritative and self-consistent
# by construction (they came from the SAME commit, on disk, no network needed). Only
# fall back to the raw-fetch path (cache-busted, since raw.githubusercontent.com sits
# behind a ~5-min CDN TTL and a stale copy would silently regenerate from old facts)
# when there is no usable checkout — e.g. a bare Kaggle kernel with no `git clone`.
# git rev-parse over the GitHub API for the SHA: it is the commit the ON-DISK files
# actually came from, not a fresh lookup that could in principle name a DIFFERENT,
# newer commit than the checkout if main moved between clone and run.
def _git_head():
    try:
        out = subprocess.run(['git', 'rev-parse', 'HEAD'], capture_output=True,
                              text=True, timeout=10)
        return out.stdout.strip()[:7] if out.returncode == 0 else None
    except Exception:
        return None


_local_head = _git_head() if all(os.path.exists(p) for p in SOURCE_FILES) else None

if _local_head:
    _live_sha = _local_head
    print(f'[local] git checkout HEAD = {_live_sha} -- using on-disk source files, '
          f'no GitHub fetch for {SOURCE_FILES}')
else:
    import time
    _cb = str(int(time.time() * 1000))
    _nocache = {'Cache-Control': 'no-cache', 'Pragma': 'no-cache'}

    _sha_resp = requests.get(
        'https://api.github.com/repos/prosperpiusmbaruku007-ship-it/AFRICA-GIANTS/commits/main',
        headers=_nocache, timeout=30)
    _sha_resp.raise_for_status()  # a 429 here must crash loud, not silently become '?'
    _live_sha = _sha_resp.json().get('sha', '?')[:7]
    print(f'[fetch] GitHub main HEAD = {_live_sha} (index will be built from THIS commit)')

    for name in SOURCE_FILES:
        r = requests.get(f'{RAW}/{name}?cb={_cb}', headers=_nocache, timeout=30)
        r.raise_for_status()
        os.makedirs(os.path.dirname(name), exist_ok=True)
        with open(name, 'w', encoding='utf-8') as f:
            f.write(r.text)
        print(f'[fetch] {name} ({len(r.content)} bytes)')

# The print above records the resolved commit; on its own it never stopped anything (this
# is the exact gap found 2026-08-26). This is the check that does.
_assert_expected_head_present(_local_head, _live_sha)

# Import build_fact_texts from the fetched module (module-level is side-effect free;
# embedding only runs under its own __main__, which we do NOT trigger by importing).
spec = importlib.util.spec_from_file_location('precompute', 'scripts/precompute_rag_embeddings.py')
precompute = importlib.util.module_from_spec(spec)
spec.loader.exec_module(precompute)

EMBED_MODEL    = precompute.EMBED_MODEL          # intfloat/multilingual-e5-base
PASSAGE_PREFIX = precompute.E5_PASSAGE_PREFIX     # 'passage: '
assert EMBED_MODEL == 'intfloat/multilingual-e5-base', f'unexpected embedder: {EMBED_MODEL}'

fact_texts_to_embed, fact_keys, dropped = precompute.build_fact_texts()
print(f'[rag] kept {len(fact_texts_to_embed)} facts, dropped {len(dropped)} noise')

# ── EMBED WITH E5-BASE ──────────────────────────────────────────────────────────
from sentence_transformers import SentenceTransformer
print(f'[rag] loading {EMBED_MODEL} ...')
model = SentenceTransformer(EMBED_MODEL)

# e5 asymmetric retrieval: facts embedded as passages. The saved rag_facts_text.json
# holds the PLAIN texts (that is what gets injected into the prompt); only the embedded
# copy is prefixed. Queries get the 'query: ' prefix at retrieval time.
prefixed = [PASSAGE_PREFIX + t for t in fact_texts_to_embed]
embeddings = np.array(model.encode(prefixed, show_progress_bar=True))
norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
embeddings_normalized = embeddings / (norms + 1e-10)
print(f'[rag] embeddings shape: {embeddings_normalized.shape}  (expect (N, 768) for e5-base)')
assert embeddings_normalized.shape[1] == 768, (
    f'DIMENSION ERROR: expected 768, got {embeddings_normalized.shape[1]} — wrong embedder?')

# ── FULL VERIFICATION — every fact in the index ─────────────────────────────────
print('\n' + '=' * 60)
print('FULL VERIFICATION — every fact in the index')
print('=' * 60)

all_pass = True
failures = []

for i, fact_text in enumerate(fact_texts_to_embed):
    # Use the fact itself as a self-query to confirm it retrieves itself at rank 1.
    # This confirms the embedding is not degenerate/broken for this fact.
    self_query = f'query: {fact_text[:100]}'
    q_emb = model.encode([self_query])[0]
    q_norm = q_emb / (np.linalg.norm(q_emb) + 1e-10)
    scores = np.dot(embeddings_normalized, q_norm)
    top_idx = int(np.argmax(scores))

    if top_idx == i:
        continue  # fact retrieves itself correctly — good
    else:
        failures.append({
            'index': i,
            'fact': fact_text[:100],
            'retrieved_instead': fact_texts_to_embed[top_idx][:100],
            'score': float(scores[top_idx]),
        })

print(f'Total facts checked: {len(fact_texts_to_embed)}')
print(f'Self-retrieval failures: {len(failures)}')

if failures:
    print('\nFacts that do NOT retrieve themselves as top match (may indicate embedding issues):')
    for f in failures[:20]:
        print(f'  [{f["index"]}] {f["fact"]}')
        print(f'      retrieved instead: {f["retrieved_instead"]} (score {f["score"]:.3f})')

# Also run the critical known-failure queries as a secondary check.
critical_queries = [
    # ── ANCHORS MIGRATED TO UNIQUE SUBSTRINGS, 2026-08-22 (R10 change, approved) ──
    # Every anchor below was verified to occur in EXACTLY ONE index fact, and that is
    # re-asserted at runtime by the GUARD ANCHOR UNIQUENESS block. The previous anchors were
    # ambiguous -- '3.5' matched 6 facts, '22,000' 6, '5,000,000' 6, '18%' 6 -- so a guard
    # could pass on a neighbouring fact and report success for one it never retrieved. That is
    # not hypothetical: the 'SDL rate' guard was satisfied by THREE different facts at once
    # (88, 212, 5), and nothing said which. See eval/results/regen_guard_audit.json.
    #
    # THREE DEAD ANCHORS were also found and removed -- 'elfu 22', '28 julai' and
    # 'efd threshold tzs 11m' matched ZERO facts, so they had never contributed anything and
    # would never have fired. A dead anchor is invisible while a live sibling carries the
    # guard; both of these sat behind an ambiguous one that always passed.
    ('GN487A penalty', 'query: Faini kwa raia wa kigeni anayevunja GN487A ni kiasi gani hasa?', ['Faini kwa mgeni']),
    ('SDL rate', 'query: SDL rate Tanzania ni asilimia ngapi?', ['asilimia tatu na nusu']),
    ('NSSF employer', 'query: Mwajiri analipa asilimia ngapi NSSF kila mwezi?', ['asilimia 10']),
    ('BRELA annual return', 'query: Ada ya annual return BRELA ni shilingi ngapi?', ['kila mwaka ni TZS 22,000']),
    ('VAT withholding services', 'query: VAT withholding kwenye huduma ni asilimia ngapi?', ['services is 6']),
    ('Zero-rated input VAT', 'query: Naweza kudai input VAT kwenye bidhaa zilizo zero-rated?', ['input vat']),
    ('GN487A effective date', 'query: GN487A ilianza kutekelezwa tarehe gani?', ['came into effect on 28 July']),
    ('GN487A full name', 'query: Jina kamili la GN487A ni nini?', ['gn487a full legal name']),
    ('Facilitator penalty', 'query: Adhabu ya raia wa Tanzania anayemsaidia mgeni ni nini?', ['milioni tano']),
    ('Phone repair activity', 'query: Mgeni anaweza kutengeneza simu?', ['phone', 'simu', 'activity 3']),
    # lv_01/fp_01 narrow faithfulness fix: the license-lending fact must WIN for the
    # kukopesha+leseni trigger (its distinctive tokens), while NOT displacing
    # 'Phone repair activity' above — the two guards together bracket the over-match fix.
    ('License lending facilitation', 'query: Raia anayekopesha leseni yake kwa mgeni anaadhibiwa?', ['kukopesha']),
    # Marriage-exemption Swahili grounding (eval_175): the previously English-only
    # gn487a_marriage_no_exemption fact must now WIN its own Swahili query. kuoa/kuolewa
    # are distinctive to this fact (no other fact uses them), so this is unambiguous.
    ('GN487A marriage no exemption', 'query: Ninaoa Mtanzania, naweza kufanya biashara ya rejareja?', ['kuoa', 'kuolewa']),
    ('PAYE 800K band', 'query: PAYE kwa mshahara wa TZS 800,000 ni kiasi gani?', ['78,000']),
    ('SDL 12-employee calculation', 'query: Kwa wafanyakazi 12 wenye mshahara TZS 600,000, SDL jumla ni kiasi gani?', ['252,000']),
    ('NSSF 12-employee calculation', 'query: Kwa wafanyakazi 12 wenye mshahara TZS 600,000, NSSF jumla ni kiasi gani?', ['1,440,000']),
    # Number-selection regression guard: the compound query where the model kept
    # defaulting to the per-employee 120,000 instead of the 12-employee total.
    # Retrieved fact must carry the scaled total AND the explicit 'SI TZS 120,000'
    # contrast (verified separately below) — the contrastive-correction pattern.
    ('NSSF compound (120k selection bug)', 'query: Kampuni ina wafanyakazi 12 wenye mshahara TZS 600,000 kila mmoja. NSSF jumla ya kampuni ni kiasi gani?', ['1,440,000']),
    # EFD-threshold Swahili grounding (eval_347): the concise efd_threshold_tzs_11m fact must
    # WIN its own query — previously the 200M-magnitude vat_registration fact hijacked it.
    ('EFD threshold', 'query: Kizingiti cha kuanza kutumia EFD ni mauzo ya TZS 200,000,000, sivyo?', ['milioni kumi na moja']),
    # Anti-displacement guard (bracket): the new concise EFD fact mentions 200M/kusajili-VAT,
    # which could displace the real VAT-registration fact from a genuine VAT-reg query — the
    # exact failure mode the GN487A concise facts hit. This must still return the 200M VAT-reg
    # fact. If it FAILS, narrow the EFD fact's 200M contrast (GN487A narrowing precedent).
    # NOTE 2026-08-22: this guard PASSES, and the displacement it was written to catch is
    # nonetheless HAPPENING -- [57] (the EFD fact, which mentions 200M as a contrast) is at
    # RANK 1 for this VAT-registration query, above [145], the fact actually asked for. The
    # old '200,000,000' anchor matched all three of [15], [57], [145], so the guard could not
    # see that its own feared displacement had occurred. Anchored to [145] now. It still
    # passes (rank 2), but a future slip to rank 4 will now be caught.
    ('VAT registration threshold (displacement guard)', 'query: Kizingiti cha kusajili VAT ni mauzo ya kiasi gani kwa mwaka?', ['200,000,000 kwa miezi 12']),
    # ── FACT-ACCURACY 2026-07-27: the three VERBATIM edge questions must each retrieve ──
    # These are the EXACT questions from the 20-edge probe that produced the fabrications
    # (not lexically-easy paraphrases — an earlier draft used paraphrases too close to the
    # fact wording, which passed here but still missed on the real phrasing; see PROGRESS
    # §FACT-ACCURACY). Expected keywords are distinctive to each corrected fact.
    # Q13 BRELA striking-off: model fabricated a "must finish its term first" bar.
    ('BRELA striking-off (Q13 verbatim)', 'query: Kampuni yangu imesajiliwa miaka sita iliyopita, naweza kuifuta sasa?', ['defunct', 'mahakama kuu', 'sura 212']),
    # Q14 OSHA/WCF: model answered wrong agency + invented a 2-employee WCF threshold.
    # ACCEPTED AMBIGUITY, 2026-08-22 — deliberately NOT migrated to a unique anchor.
    # Its three anchors each match two facts, [68] and [69], and BOTH state the thing the
    # guard exists to protect (OSHA registers all workplaces; WCF starts from the first
    # employee). Either one is a correct answer to this question, so passing on "the other"
    # fact is not a false pass. Pinning it to [69] alone would make the guard fail spuriously
    # if [68] were retrieved instead — a worse outcome than the ambiguity.
    # The lesson generalises: ambiguity is a fault when the alternative fact would be a WRONG
    # answer, not merely when more than one fact matches.
    ('OSHA/WCF small-count (Q14 verbatim)', 'query: Nina wafanyakazi wawili tu dukani, bado nasajiliwa mahali fulani?', ['osha husajili', 'wcf huanza', 'mfanyakazi wa kwanza']),
    # Q16 EFD: model said every shop needs an EFD regardless of sales.
    # anchor UPDATED 2026-09-03: the old anchors ('si kila biashara', 'risiti za mkono')
    # were phrases from the STALE, fabricated turnover-threshold text this row used to
    # carry (see efd_not_every_business's rewrite note in precompute_rag_embeddings.py --
    # same defect nat_36's guard was re-adjudicated for, found and fixed in the same
    # pass). Both anchors are now DEAD by design: the corrected text deliberately no
    # longer says "si kila biashara" or offers "risiti za mkono" as a turnover-based
    # option. Re-anchored to the corrected text's own unique phrase; re-verified this
    # guard's query still resolves to the same row at rank 1 on the full prospective
    # 183-row dry-run re-embed.
    ('EFD not-every-business (Q16 verbatim)', 'query: Duka langu dogo halifikishi mauzo makubwa kila siku, bado nahitaji mashine ya risiti?', ['HAKUNA kizingiti cha mauzo']),
    # ── C4 REACHABILITY CYCLE, 2026-08-17 ── one positive guard for the row that
    # actually cleared top-3 after two rounds of wording (GN605A_sector_count, nat_43,
    # rank 127->1); four negative/displacement guards for nat_26/27/34/36, whose pools
    # sit downstream of the sdl_rate_2025/sdl_employee_threshold/brela_annual_return_fee
    # deletions and the annual_return_filing_fee/late_filing_penalty_monthly_fee/GN605A
    # rewrites.
    #
    # ⚠️ CORRECTED 2026-08-22. This block used to claim nat_27's guard "is what caught the
    # vat_withholding_goods/services displacement ... if anyone re-attempts it, this guard is
    # what will catch the regression again." BOTH HALVES WERE FALSE and the claim cost real
    # wins. Measured (eval/index_quality/reopen_nat44_nat28.py): the rewrite moves nat_27's
    # fact by ONE rank (15 -> 16), on a row whose fact is not retrieved either way -- there was
    # no regression to catch. And the guard could not have caught one: it tested `'18%' in
    # fact_text`, which SIX index facts satisfy, including [64] vat_withholding_formula_correct
    # -- the very fact the rewrite touches. It reported the standard-rate fact as retrieved
    # while matching the withholding fact. See eval/results/regen_guard_audit.json.
    #
    # nat_37 and nat_38 were ORIGINALLY going to be guarded here too, per the founder's
    # list of six. Local dry-run verification (scratch/local_regen_verify.py) found both
    # ALREADY FAIL against the currently deployed index -- confirmed independent of any
    # change in this cycle by testing them against kaggle/rag_facts_text.json as-is,
    # before any of this session's edits. They are not protected by anything today,
    # C4 or otherwise; wiring a guard for an already-failing row would only block this
    # cycle's real wins from deploying. Named as their own item in PROGRESS instead of
    # silently guarded here.
    #
    # ⚠️ REWRITTEN 2026-08-22 (R10 change, approved). These five previously used PARAPHRASED
    # query text and AMBIGUOUS keywords, and both faults were live:
    #   * Phrasing: they differed from their eval rows by capitalisation and a '?'. That is not
    #     cosmetic -- for nat_36 the guard phrasing puts its fact at rank 2 and the verbatim
    #     eval text puts it at rank 17. A guard that only passes on a phrasing no user sends
    #     certifies nothing.
    #   * Keywords: '18%' matches 6 facts, '11,000,000' matches 3, '95,000' matches 3,
    #     '100,000,000' matches 4. A guard could pass on a neighbour and report success.
    # Now: VERBATIM text from eval/accuracy_gate/edge_probe_natural_048.jsonl, and anchors
    # verified to occur in exactly ONE index fact (asserted at runtime below, so this cannot
    # rot silently when facts are edited).
    ('GN605A sector count (nat_43 verbatim, the row that clears)', 'query: mimi ni mkulima nina vibarua je kima cha chini kinatofautiana kwa sekta', ['hakina kiwango kimoja']),
    ('VAT six-month threshold (nat_26 displacement guard)', 'query: nimefungua duka miezi sita iliyopita nimeuza jumla milioni 60 hadi sasa je nimefika kiwango cha vat', ['100,000,000 kwa miezi 6']),
    # anchor UPDATED 2026-09-03: vat_standard_rate got its first CONCISE entry (it had
    # none before -- default English "key: value" fallback, which never appeared in
    # top-3 across three regens, fc9b0c8/76e64ed/b002b96 -- see PROGRESS.md). New text is
    # Swahili-first and ask-aligned to this exact question; anchor changed from the old
    # English 'NEVER 14%' to 'SIYO 14%' to match (an English anchor would defeat the
    # point of a Swahili-first rewrite). Measured locally at RANK 1 (was rank 12) against
    # the currently-deployed index, and PASSES on the full prospective 183-row dry-run
    # re-embed before this file was repackaged. Removed from KNOWN_FAILING below.
    ('VAT standard rate (nat_27 displacement guard)', 'query: vat ya asilimia ngapi naiweka kwenye bei ya bidhaa zangu', ['SIYO 14%']),
    # anchor UPDATED 2026-08-26 (fee consolidation): 'company registration fee 1' matched
    # ZERO facts once the ladder's 14 rows were absorbed into company_registration_ladder --
    # the exact dead-anchor failure mode this uniqueness check exists to catch, found by
    # eval/index_quality/verify_regen_guards_post_consolidation.py before this ever reached
    # Kaggle. The old row (company_registration_fee_1: 95,000 TZS) is now inside the group
    # passage; anchored to a phrase from that passage instead, verified unique among the
    # prospective 187 rows.
    #
    # anchor UPDATED AGAIN 2026-08-26 (nat_34 RETRIEVAL regression, not a text/anchor
    # problem): text-uniqueness passed on Kaggle run #1 and the guard still FAILED --
    # the passage ranked 4th, one place outside top-3, because consolidation let an
    # untouched neighbour (business_name_maintenance_fee) climb into the vacated
    # competing slot (eval/results/nat34_regression_diagnosis.json). Fixed at the source
    # by RE-LEADING the group passage with nat_34's own vocabulary -- "kusajili kampuni",
    # "gharama ya kuanzia", "kuhifadhi jina" -- instead of the regulatory share-capital
    # frame (R15's topic-alignment lever, the same one that moved nat_36 17->1 and
    # nat_28 79->10; see precompute_rag_embeddings.py FACT_GROUPS['company_registration_
    # ladder']). Anchor updated to the new lead phrase; re-verified unique AND in top-3
    # against the prospective index by verify_regen_guard_retrievability.py before this
    # file was repackaged.
    ('Company registration fee (nat_34 displacement guard)', 'query: nataka kusajili kampuni gharama ya kuanzia ni ngapi na kuhifadhi jina', ['gharama ya kuanzia ni TZS 95,000']),
    # anchor UPDATED 2026-09-03, and the fix is NOT the anchor -- efd_not_every_business's
    # CONCISE text was found STALE: it still stated the TZS 11,000,000 turnover-threshold
    # framing that was found fabricated on 2026-08-29 and corrected in locked_facts.json,
    # but the CONCISE rendering here was never updated to match (a sync gap, not a
    # phrasing gap). Old anchor 'milioni kumi na moja' was never IN this row's text at
    # all (it lives in efd_threshold_tzs_11m's separate row) and would have kept failing
    # even under a correctness-only fix -- confirmed directly: a correctness-only rewrite
    # (dropping the 11M figure without ask-aligning) fell OUT of top-3 entirely (rank 6).
    # The ask-aligned rewrite recovers both correctness AND rank -- measured locally at
    # RANK 1 (from not-in-top-3) against the currently-deployed index, non-displacing on
    # nat_26/nat_38/the original Q16 target, and PASSES the full prospective 183-row
    # dry-run re-embed. Removed from KNOWN_FAILING below -- this is a genuine close, not
    # a guard-anchor patch over an unfixed retrieval gap.
    ('EFD threshold, VAT-unregistered (nat_36 displacement guard)', 'query: mauzo yangu ya mwaka ni milioni 15 na sijasajili vat je nahitaji mashine ya risiti', ['HAKUNA kizingiti cha mauzo']),
    # NEW GUARD 2026-09-03, for the NEW fact efd_receipt_per_transaction_no_minimum,
    # closing nat_37's live regression (readjudicate_changed_48_r15_2026_09_03.py):
    # no locked fact anywhere stated the per-transaction (as opposed to per-business/
    # turnover) EFD rule, so retrieval returned zero relevant content for this question
    # in both the pre- and post-R15 index (confirmed: eval/results/grounding_48.json's
    # own 2026-08-22 measurement already found NO_OVERLAP here), and the model fabricated
    # a TZS 500 minimum-transaction exemption from weights alone. Measured locally at
    # RANK 2 (in top-3) against the currently-deployed index plus this one new row, and
    # PASSES the full prospective 183-row dry-run re-embed.
    ('EFD receipt required per-transaction, no minimum (nat_37 gap-closing guard)', 'query: mteja amenunua kwa shilingi 2000 tu nampa risiti ya mashine au inaruhusiwa kuandika kwa mkono', ['KWA KILA muamala']),
    # ── FEE-CONSOLIDATION BATCH, 2026-08-26 -- the five council-fee/market-dues/business-
    # licence facts reclassified from GAP to ANSWERED (add_local_levy_facts.py, PROGRESS.md
    # 'THE THREE UNANSWERABLE DOMAINS'). Pinned pending_r15 in check_facts_index_sync.py
    # until THIS regen runs. Anchors verified unique against build_fact_texts()'s prospective
    # 187-row output before this file was packaged (all five resolve to exactly one row each,
    # since none is in CONCISE_BILINGUAL_FACTS -- default key:value rendering, EXACT-key-
    # matchable once the row exists, which is why no PINNED entry survives past this regen).
    ('Council service levy is a ceiling (new fact)', 'query: Halmashauri wananitoza ushuru wa huduma asilimia 0.3 ya mauzo yangu, ni sahihi?', ['KIKOMO cha asilimia 0.3']),
    ('Council service levy non-corporate conflict (new fact)', 'query: Mimi ni mfanyabiashara mmoja mmoja, ninatakiwa kulipa ushuru wa huduma wa halmashauri?', ['non-corporate']),
    ('Market dues no national amount (new fact)', 'query: Ushuru wa genge langu sokoni ni shilingi ngapi?', ['Sheria ya Masoko (Cap 106)']),
    ('Market dues exemptions (new fact)', 'query: Ninauza maandazi sokoni, ninatakiwa kulipa ushuru wa soko?', ['maandazi na samaki wa kukaanga']),
    ('Business licence fee national schedule, local collection (new fact)', 'query: Leseni ya biashara yangu inagharimu kiasi gani, na nani hutoa?', ['Ada imepangwa KITAIFA']),
    # ── CORPORATE/PARTNERSHIP TAX SOURCE PASS, 2026-09-01 ──────────────────────────
    # corporate_tax_rate and minimum_turnover_tax moved into CONCISE_BILINGUAL_FACTS this
    # session (ask-aligned from the first draft, not retrofitted -- see the comments beside
    # each entry in scripts/precompute_rag_embeddings.py). Anchors verified unique against
    # build_fact_texts()'s prospective 188-row output before this file was packaged.
    ('Corporate tax rate (ask-aligned)', 'query: Kodi ya kampuni Tanzania ni asilimia ngapi?', ['kampuni za kawaida']),
    ('AMT loss-making corporation (ask-aligned)', 'query: Kampuni yangu ina hasara miaka mitatu mfululizo, nalipa kodi gani?', ['hasara miaka mitatu mfululizo']),
]

# ── KNOWN-FAILING GUARDS (2026-08-22) ────────────────────────────────────────────
# A guard here is a KNOWN, TRACKED retrieval defect: it is reported every run as
# [KNOWN-FAIL] and does NOT block the regen. It is not a passing guard and not an absent one.
#
# Removing a name from this set is how a defect gets CLOSED. Adding one requires a PROGRESS
# entry naming why. A name here that starts PASSING is itself reported as a defect
# ([STALE-KNOWN-FAIL]) and DOES block -- otherwise this set becomes the place guards go to be
# forgotten, which is the failure mode it exists to prevent.
KNOWN_FAILING = {
    # BOTH prior members of this set closed 2026-09-03 -- see the anchor-update comments
    # beside each guard's tuple above (vat_standard_rate / efd_not_every_business), and
    # readjudicate_changed_48_r15_2026_09_03.py for the live-answer evidence that
    # motivated closing nat_36's the right way (a content fix, not a guard patch). Both
    # verified PASS on the full prospective 183-row dry-run re-embed before this file was
    # repackaged -- if either comes back [STALE-KNOWN-FAIL] on the real Kaggle run, that
    # means the dry-run (CPU, local sentence-transformers) and the Kaggle run (same model,
    # same code path) disagree, which would itself be worth investigating rather than
    # re-adding the name reflexively.
}

# Anchor uniqueness is a PRECONDITION, not an assumption: if a fact edit makes an anchor match
# two rows, the guard silently regains the exact fault this change removed. Checked here, on
# the texts actually being embedded, before any guard runs.
print('\n' + '=' * 60)
print('GUARD ANCHOR UNIQUENESS')
print('=' * 60)
# Guards whose ambiguity has been ADJUDICATED AS BENIGN: every fact their anchors match is a
# correct answer to the guard's question, so passing on "the other one" is not a false pass.
# A name here needs the reasoning written at the guard itself, not just this set.
ACCEPTED_AMBIGUOUS = {
    # anchors match [68] and [69]; both carry OSHA-registers-all-workplaces and
    # WCF-from-first-employee. Pinning to one would fail spuriously on the other.
    'OSHA/WCF small-count (Q14 verbatim)',
}

_anchor_pass = True
_dead, _ambiguous = [], []
for _name, _query, _expected in critical_queries:
    for _kw in _expected:
        _hits = [i for i, t in enumerate(fact_texts_to_embed) if _kw.lower() in t.lower()]
        if not _hits:
            # An anchor matching nothing can never fire. Three of these were found on
            # 2026-08-22 ('elfu 22', '28 julai', 'efd threshold tzs 11m'), each hidden
            # behind a live sibling anchor that always passed.
            _dead.append((_name, _kw))
            _anchor_pass = False
        elif len(_hits) > 1 and _name not in ACCEPTED_AMBIGUOUS:
            _ambiguous.append((_name, _kw, _hits))
            _anchor_pass = False

for _name, _kw in _dead:
    print(f'[DEAD-ANCHOR] {_name}: anchor {_kw!r} matches ZERO facts -- it can never fire')
for _name, _kw, _hits in _ambiguous:
    print(f'[AMBIGUOUS] {_name}: anchor {_kw!r} matches {len(_hits)} facts {_hits[:8]}')
if _anchor_pass:
    print(f'[OK] every anchor across {len(critical_queries)} guards resolves to exactly one '
          f'fact ({len(ACCEPTED_AMBIGUOUS)} adjudicated-benign exception(s))')
else:
    print('[WARN] the anchors above CANNOT do the job they claim -- a dead anchor never')
    print('       fires, and an ambiguous one can pass on a fact it does not mean.')
    print('       See eval/results/regen_guard_audit.json and PROGRESS.md 2026-08-22.')

print('\n' + '=' * 60)
print('CRITICAL KNOWN-FAILURE QUERIES')
print('=' * 60)

critical_pass = True
_known_fail_seen = set()
for name, query, expected in critical_queries:
    q_emb = model.encode([query])[0]
    q_norm = q_emb / (np.linalg.norm(q_emb) + 1e-10)
    scores = np.dot(embeddings_normalized, q_norm)
    top3_idx = np.argsort(scores)[-3:][::-1]

    found = False
    for idx in top3_idx:
        if any(kw.lower() in fact_texts_to_embed[idx].lower() for kw in expected):
            found = True
            break

    if not found and name in KNOWN_FAILING:
        # Tracked defect: visible every run, does not block the regen.
        _known_fail_seen.add(name)
        print(f'[KNOWN-FAIL] {name}')
        for r, idx in enumerate(top3_idx, 1):
            print(f'        top{r}: {fact_texts_to_embed[idx][:90]}')
    elif found and name in KNOWN_FAILING:
        # The defect was fixed and nobody removed it from the set. That is a real problem:
        # a stale entry means a genuine future regression on this row would be swallowed as
        # "known". Block until the set is updated.
        _known_fail_seen.add(name)
        critical_pass = False
        print(f'[STALE-KNOWN-FAIL] {name} now PASSES -- remove it from KNOWN_FAILING')
    else:
        status = 'PASS' if found else 'FAIL'
        print(f'[{status}] {name}')
        if not found:
            critical_pass = False
            # show what WAS retrieved so a fail is diagnosable, not just a red X
            for r, idx in enumerate(top3_idx, 1):
                print(f'        top{r}: {fact_texts_to_embed[idx][:90]}')

# Summary, so the tracked-defect count is visible rather than buried in the log.
print(f'\n{len(KNOWN_FAILING)} known-failing guard(s) tracked: {sorted(KNOWN_FAILING)}')
_orphans = KNOWN_FAILING - _known_fail_seen
if _orphans:
    # A name in the set that matches no guard at all -- renamed or deleted guard. Same
    # forgetting failure as a stale pass, so it blocks too.
    critical_pass = False
    print(f'[ORPHAN-KNOWN-FAIL] not found among the guards: {sorted(_orphans)}')

# ── CONTRAST-LANGUAGE GUARD — NSSF 120k number-selection regression ──────────────
# The compound query must retrieve a fact that carries BOTH the correct scaled total
# (1,440,000) AND the explicit contrastive correction (SI TZS 120,000) in the SAME
# fact text. This directly counters the exact wrong number the model kept defaulting
# to; if a future fact edit drops the contrast, this fails loudly.
print('\n' + '=' * 60)
print('CONTRAST-LANGUAGE GUARD — NSSF 120k selection')
print('=' * 60)
_guard_q = 'query: Kampuni ina wafanyakazi 12 wenye mshahara TZS 600,000 kila mmoja. NSSF jumla ya kampuni ni kiasi gani?'
_q = model.encode([_guard_q])[0]
_q = _q / (np.linalg.norm(_q) + 1e-10)
_scores = np.dot(embeddings_normalized, _q)
_top3 = np.argsort(_scores)[-3:][::-1]
contrast_pass = any(
    ('1,440,000' in fact_texts_to_embed[i])
    and any(c in fact_texts_to_embed[i].lower() for c in ('si tzs 120,000', 'si 120,000'))
    for i in _top3
)
print(f'[{"PASS" if contrast_pass else "FAIL"}] retrieved fact carries 1,440,000 AND "SI TZS 120,000" contrast')
if not contrast_pass:
    for r, idx in enumerate(_top3, 1):
        print(f'        top{r}: {fact_texts_to_embed[idx][:110]}')

# ── DISAMBIGUATION GUARD — eval_380 non-citizen penalty AMOUNT ───────────────────
# The non-citizen-penalty-AMOUNT query must retrieve the 10M non-citizen fact in top-3
# AND must NOT contain the license-lending facilitation fact in top-3. The 10M fact was
# never outranked (it is rank 0); the regression was CONTEXT COMPOSITION — the narrowed
# 5M license-lending fact intruding at rank 2 put a second 5M figure in context and the
# model answered 5M instead of 10M. A plain 'is 10M present' check would have passed
# even while broken, so this is a two-part guard: 10M present AND license-lending fact
# ('kukopesha' — a token unique to that fact, absent from the 10M/generic-facilitator
# facts) absent. If a future edit lets the license-lending fact drift back into this
# query's top-3, this fails loudly.
print('\n' + '=' * 60)
print('DISAMBIGUATION GUARD — eval_380 non-citizen penalty amount')
print('=' * 60)
_dq = 'query: Faini ya chini kabisa anayotozwa asiye raia kwa kukiuka GN 487A ni TZS ngapi hasa?'
_dqe = model.encode([_dq])[0]
_dqe = _dqe / (np.linalg.norm(_dqe) + 1e-10)
_dscores = np.dot(embeddings_normalized, _dqe)
_dtop3 = np.argsort(_dscores)[-3:][::-1]
_has_10m = any(
    ('10,000,000' in fact_texts_to_embed[i] or 'milioni kumi' in fact_texts_to_embed[i].lower())
    for i in _dtop3)
_has_license = any('kukopesha' in fact_texts_to_embed[i].lower() for i in _dtop3)
disambig_pass = _has_10m and not _has_license
print(f'[{"PASS" if disambig_pass else "FAIL"}] 10M non-citizen fact in top-3 '
      f'(present={_has_10m}) AND license-lending fact absent (present={_has_license})')
if not disambig_pass:
    for r, idx in enumerate(_dtop3, 1):
        print(f'        top{r}: {fact_texts_to_embed[idx][:110]}')

# ── RANK-REGRESSION GATE — the fee consolidation (nat_05/nat_23/nat_33) ──────────
# eval/results/feegroup_curation.json measured OFFLINE (2026-08-25, the deployed 221-row
# index vs. a locally-reconstructed 182-row consolidated arm) that the SDL-rate and BRELA
# annual-return-fee anchors move: nat_23 86->45, nat_33 48->23, nat_05 24->8. That measurement
# is the entire justification for shipping this consolidation -- and it has never been checked
# against a REAL regenerated index, only a local scoring harness reconstructing what a regen
# would produce. This is the first time it is.
#
# Verbatim question text and anchor-identification needles below are copied EXACTLY from
# eval/index_quality/measure_feegroup_curation.py's NAT48/ANCHORS (R24: a paraphrase is not
# the same check). Anchor uniqueness against the prospective 187-row index was confirmed
# offline before this file was packaged
# (eval/results/regen_guard_anchors_post_consolidation.json) -- re-asserted here at runtime
# too, since that is exactly the kind of thing a future fact edit could silently break.
#
# Tolerance: +5 ranks around the measured target. e5-base inference has no dropout, so
# local and Kaggle runs of the identical model are expected to reproduce near-identically;
# the tolerance absorbs float/BLAS-order noise, not a real regression. The baseline check
# (new rank must clearly beat the PRE-consolidation rank, not just be "close to" the target)
# is the second half of the gate for exactly that reason -- a number close to the target for
# the wrong reason is not evidence.
print('\n' + '=' * 60)
print('RANK-REGRESSION GATE — fee consolidation (nat_05/nat_23/nat_33)')
print('=' * 60)
RANK_GATE_CASES = [
    # (name, verbatim question, anchor needle, pre-consolidation rank, measured post rank)
    ('nat_23 (SDL rate)',
     'query: nina wafanyakazi 12 mishahara jumla milioni 5.5 nitalipa ngapi kwenye ile ya '
     'mafunzo na ile ya uzeeni',
     'kiwango cha mafunzo ni asilimia tatu na nusu', 86, 45),
    ('nat_33 (BRELA annual return fee)',
     'query: sijapeleka ritani ya kampuni yangu miezi saba sasa nitalipa faini kiasi gani na '
     'ada yenyewe ni ngapi',
     'ada ya kuwasilisha ritani (annual return) ya kampuni kila mwaka ni TZS 22,000', 48, 23),
    ('nat_05 (SDL rate)',
     'query: nimenunua mashine za kiwanda za milioni 50 na nina wafanyakazi 12 hiyo ya '
     'mafunzo nitalipa asilimia tatu na nusu ya nini',
     'kiwango cha mafunzo ni asilimia tatu na nusu', 24, 8),
]
RANK_TOLERANCE = 5
rank_gate_pass = True
for name, q, needle, pre_rank, measured_rank in RANK_GATE_CASES:
    hits = [i for i, t in enumerate(fact_texts_to_embed) if needle in t]
    if len(hits) != 1:
        rank_gate_pass = False
        print(f'[FAIL] {name}: anchor {needle!r} matches {len(hits)} facts (expected exactly '
              f'1) -- cannot locate the fact whose rank this gate is supposed to check')
        continue
    anchor_idx = hits[0]
    qv = model.encode([q])[0]
    qv = qv / (np.linalg.norm(qv) + 1e-10)
    sims = np.dot(embeddings_normalized, qv)
    order = np.argsort(-sims)
    observed_rank = int(np.where(order == anchor_idx)[0][0]) + 1
    within_tolerance = observed_rank <= measured_rank + RANK_TOLERANCE
    beats_baseline = observed_rank < pre_rank
    ok = within_tolerance and beats_baseline
    rank_gate_pass = rank_gate_pass and ok
    print(f'[{"PASS" if ok else "FAIL"}] {name}: pre-consolidation {pre_rank} -> measured '
          f'{measured_rank} (offline) -> observed {observed_rank} (this build, tolerance '
          f'+{RANK_TOLERANCE})')
    if not ok:
        for r, idx in enumerate(order[:5], 1):
            print(f'        top{r}: {fact_texts_to_embed[int(idx)][:90]}')
if rank_gate_pass:
    print(f'[OK] all {len(RANK_GATE_CASES)} consolidation anchors reproduce the offline-'
          f'measured movement within tolerance')

print()
# allow <10% self-retrieval noise (near-duplicate facts can surface a sibling at rank 1)
overall_pass = (critical_pass and contrast_pass and disambig_pass and rank_gate_pass
                and _anchor_pass
                and len(failures) < len(fact_texts_to_embed) * 0.1)
if overall_pass:
    print(f'VERIFICATION PASSED — {len(fact_texts_to_embed) - len(failures)}/{len(fact_texts_to_embed)} '
          f'facts self-retrieve correctly, all critical queries pass')
    print('Saving and uploading...')
else:
    print('VERIFICATION FAILED — review failures before saving')
    print(f'  critical_pass={critical_pass} | contrast_pass={contrast_pass} | '
          f'disambig_pass={disambig_pass} | rank_gate_pass={rank_gate_pass} | '
          f'anchor_pass={_anchor_pass} | self_retrieval_failures={len(failures)} '
          f'(tolerance={int(len(fact_texts_to_embed) * 0.1)})')
    sys.exit(1)   # do NOT upload a broken index

# ── SAVE + UPLOAD TO HF DATASET REPO ────────────────────────────────────────────
np.save('rag_embeddings.npy', embeddings_normalized)
with open('rag_facts_text.json', 'w', encoding='utf-8') as f:
    json.dump(fact_texts_to_embed, f, ensure_ascii=False, indent=2)
print(f'[save] rag_embeddings.npy {embeddings_normalized.shape} + '
      f'rag_facts_text.json ({len(fact_texts_to_embed)} facts)')

# ATOMIC upload (2026-08-17): these two files must correspond row-for-row (embedding
# i must describe fact_text i) -- they were two independent api.upload_file() calls,
# so a failure between them (rate limit, network drop) landed embeddings from THIS
# build alongside facts_text from the PREVIOUS one, or vice versa, with nothing
# anywhere checking the two are still paired. Every downstream consumer (modal_app.py,
# eval.py) loads both and trusts the row alignment; a mismatch is silent -- wrong or
# index-shifted retrieval, no exception. create_commit() with both files as one Hub
# commit means either both land or neither does.
from huggingface_hub import HfApi, CommitOperationAdd
api = HfApi()
api.create_commit(
    repo_id=DATASET_REPO,
    repo_type='dataset',
    operations=[
        CommitOperationAdd(path_in_repo='rag_embeddings.npy', path_or_fileobj='rag_embeddings.npy'),
        CommitOperationAdd(path_in_repo='rag_facts_text.json', path_or_fileobj='rag_facts_text.json'),
    ],
    commit_message=f'e5-base RAG index ({embeddings_normalized.shape[0]}x{embeddings_normalized.shape[1]}), '
                    f'built from {_live_sha}',
    token=hf_token,
)
print(f'[upload] rag_embeddings.npy + rag_facts_text.json -> {DATASET_REPO} (one commit)')

print('\n[done] e5 RAG index regenerated, verified, and uploaded.')
print(f'[done] FINAL SHAPE: {embeddings_normalized.shape}  |  facts: {len(fact_texts_to_embed)}')
