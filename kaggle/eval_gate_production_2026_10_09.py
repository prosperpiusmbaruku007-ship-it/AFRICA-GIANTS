# -*- coding: utf-8 -*-
"""THE FULL GATE, AGAINST THE BUILD PRODUCTION IS ACTUALLY SERVING — 2026-10-09.

No full gate has run since `1476caa` (2026-08-08). Every Bar A figure quoted in the two months
since is that run's, and it was taken against a **217-fact index** while production now serves
**184**. So the current number is not merely old; it was measured on a different system.

This run replaces it. One arm, no v15 comparison (that question was settled at `5d0dcb7` and
v16 is what ships), 400 questions, through `chike.orchestrator` with the SINGLE-ARM retriever —
the production configuration, with D-FIDELITY-7 and D-FIDELITY-8 wired.

════════════════════════════════════════════════════════════════════════════════════════════
 1. IT SCORES BOTH DIRECTIONS, BECAUSE A GUARD MAKES A1 FALL WITHOUT MOVING A2
════════════════════════════════════════════════════════════════════════════════════════════
D-FIDELITY-7 and -8 replace a confident wrong answer with a non-answer. That is the safe
direction and it is a real win — and it is **invisible to a single accuracy figure**, because
the row still does not pass. Read as one number the whole exercise looks like nothing happened.

So the headline carries TWO numbers and a count, never a net:

    A1  WRONG-ANSWER RATE   in-corpus rows answered with a located, wrong value
    A2  RIGHT-ANSWER RATE   in-corpus rows the user can act on
    G   GUARD INTERVENTIONS a fidelity guard replaced or blanked the body

A falling A1 with a flat A2 is **CONTAINMENT**, not improvement, and the summary says that word
out loud when it happens. The two axes are kept ORTHOGONAL — outcome (right/wrong/no-answer) is
an exhaustive partition and is ASSERTED to be one; guard intervention is a separate count
cross-tabbed against it. That cross-tab is the part that matters: a compute body blanked by a
guard still renders the engine's working, so it can be a guard intervention AND a right answer,
while a fact body replaced by a guard can only ever be a no-answer.

════════════════════════════════════════════════════════════════════════════════════════════
 2. IT SCORES THE CHANGED ROWS UNDER BOTH KEYS, SO KEY CORRECTION IS NOT INSIDE THE MOVEMENT
════════════════════════════════════════════════════════════════════════════════════════════
A corrected gold moves the score with no model change. The old keys are read OUT OF GIT by
`eval/controls/derive_gold_key_corrections_2026_10_09.py` and committed as
`eval/results/gold_key_corrections_2026_10_09.json`, which this file LOADS — it does not
re-derive them, so the two cannot disagree (the dry-run lesson: a harness that re-implements
the real run's tables is not a harness of that run).

Measured, not assumed: of 24 rows of the 400 edited since the baseline, **22 cannot move a
score** (19 are `nssf.or.tz` -> `nssf.go.tz` in the gold prose) and exactly **2 narrow the key**
— `eval_355` and `eval_383`. Those two are scored under both keys and the delta is reported on
its own line.

⛔ THE ARM IS NARROWER THAN THE FOUR THINGS IT WAS ASKED TO COVER, AND EVERY GAP IS NAMED.
`KEY_CORRECTION_COVERAGE` (printed, and shipped inside the artifact) accounts for eval_383,
eval_355, eval_331, **ext_15**, **ext_56** and **the 41 sourced of 73** one at a time. Re-derived,
not taken from the request: `ext_15` is RE_RUN_REQUIRED and its key changed twice, but it lives in
a 78-row probe set that is NOT in these 400, was never scored at `1476caa`, and carries no
`correct_answer_sw`/`answer_type` — its gold is `expected_behavior` PROSE, which `score_question`
cannot score at all. `ext_56` carries **no `_scoring_key_correction` of any kind**; the 2026-09-23
adjudication records it as `verdict=WRONG, cause=MODEL`, so there is no old key to score against
and listing it would manufacture a key-correction term out of a model defect. The 41 came from a
`mode=REPORT_ONLY` backfill whose own header says "Changes no gold answer", so their delta is
exactly **zero by construction** — the live part of that file is its **4
`disagreements_reported_not_changed`**, which are candidate wrong keys still scoring rows today.

⚠️ AND ONE CHANGE IS INVISIBLE TO THE REGEX SCORER, WHICH IS WORSE THAN A MEASURED DELTA.
`eval_331`'s correction note says "VERDICT FLIPPED from No to Yes". `_yn_polarity` reads its OLD
gold as **yes** — the old gold stated the No as *"hulazimiki"* and `_YN_NEG` carries
`halazimiki` (3rd person) but not `hulazimiki` (2nd person), one vowel, so it fell through to
the AFFIRMATIVE DEFAULT. A model leading with "Ndiyo" passed eval_331 both before and after the
verdict flipped. The regex delta is zero by construction; only the judge can see it. Not
repaired here — widening `_YN_NEG` moves historical numbers and needs R17's treatment, not a
one-word patch riding along with a gate package.

════════════════════════════════════════════════════════════════════════════════════════════
 3. PRE-REGISTERED EXPECTATION — WRITTEN AND COMMITTED BEFORE THE RUN, SO IT CANNOT BE READ
    BACKWARDS
════════════════════════════════════════════════════════════════════════════════════════════
The baseline, re-derived from `eval/results/gate_phase_d_paired_1476caa.json`'s raw rows:

    in-corpus raw        314/384 = 81.8%     <- THE COMPARABLE HEADLINE
    in-corpus reliable   222/270 = 82.2%
    fact_path_190 raw    158/184 = 85.9%   reliable 111/130 = 85.4%
    staged_50            42/50   = 84.0%
    compute_type         84/102  = 82.4%
    adversarial_150      108/144 = 75.0%
    clarified            21
    index                217 facts

🔴 A CORRECTION TO MY OWN STOCK-TAKE, STATED HERE BECAUSE THE COMPARISON DEPENDS ON IT. On
2026-10-08 I reported the baseline blend as "330/400 = 82.5%". That figure includes the 16
`out_of_corpus` rows in BOTH numerator and denominator (all 16 passed), so it is an
in-corpus-plus-refusals number. The gate's own `_acc` excludes OOC by design and R7's Gate 1 is
an IN-CORPUS bar, so **81.8% is the like-for-like baseline** and 82.5% must not be compared
against this run's in-corpus figure. Both are reported below so the two can never be conflated
again.

WHAT I EXPECT, with each term's direction and size, and the honest width of the band:

  (a) KEY CORRECTION  -2 rows at most, i.e. **-0.52 pts**, and the direction is DOWN. Both
      corrected keys are stricter, and the row only moves if the model gives the old answer.
      This is a hard bound: the dual-score arm measures it exactly rather than estimating it.
  (b) CORRECTED FACTS  **+1.25 pts at most**, direction UP. 12 of the 400 rows (3.0%) touch a
      fact corrected after the baseline; 5 of those were failing at the baseline, so at most 5
      rows can flip, i.e. 5/384. Bound re-derived in
      `eval/controls/pilot_stocktake_2026_10_08.py`, not recalled.
  (c) THE TWO WIRED GUARDS  expected to move **A1 down and A2 not at all**. D-FIDELITY-7 was
      priced at 18 flags over 5,599 stored rows with **0 in gold**; D-FIDELITY-8 at 1 flag over
      13,632 rows, **0 in gold**. Neither can produce a right answer, so if A2 rises, that rise
      is NOT theirs and must be attributed elsewhere.
  (d) THE INDEX, 217 -> 184  **UNBOUNDED AND UNMEASURED, AND IT IS THE LARGEST TERM.** The drop
      is consolidation (221 -> 187 on 2026-08-26, "three consolidated families"), not deletion,
      plus four stale renderings corrected out of production. Consolidation is plausibly
      positive — the ask-aligned rewrites measured at rank 1 — but **nothing has measured its
      effect on these 400 questions**, and `nat_23` moving 45->46 from a single rewrite is the
      standing proof that index composition perturbs neighbours. If the result lands outside
      (a)+(b), this is the first place to look, and NOT a reason to doubt the run.

  SO THE PRE-REGISTERED POINT ESTIMATE IS  81.8% - 0.5 + 1.25 ~= **82.5% in-corpus raw**, with
  the honest statement that term (d) is larger than both the others and unsigned. I am NOT
  predicting Bar A clears 85%. The fact-path bucket sat at 85.9% raw / 85.4% reliable at the
  baseline — ON R7's line, not clear of it — and that bucket is where a first-time user's
  question lands, so it is the bucket to read first.

  🎯 THE ONE ROW TO WATCH: `eval_347`. D-FIDELITY-7 should now withhold its fabricated TZS
  11,000,000 EFD threshold. That is a **FAIL that is a WIN**, and it must appear as
  `outcome=NO_ANSWER, guard=D-FIDELITY-7`, not as a wrong answer. If it still asserts the
  figure, the guard is not reaching the fact path in production and that is the finding of the
  run.

  ⛔ IF THE RESULT LANDS BELOW THE PROJECTION, that is a result to bring back, not a reason to
  reopen a decision — the founder's standing instruction from 2026-08-08: decide against a real
  number, not a projected one.

════════════════════════════════════════════════════════════════════════════════════════════
 HOW TO RUN  (Kaggle notebook, GPU ON, Internet ON)
════════════════════════════════════════════════════════════════════════════════════════════
    import requests
    exec(requests.get('https://raw.githubusercontent.com/prosperpiusmbaruku007-ship-it/'
                      'AFRICA-GIANTS/main/kaggle/eval_gate_production_2026_10_09.py',
                      timeout=20).text)

    Secrets: AFRICA_GIANTS (HF token), OPENROUTER_API_KEY (judge overlay — MANDATORY)
    Runtime: ~400 generations ~= 50-75 min, plus ~15 min judge.

PER-ROW FLUSH AND RESUME. The artifact is written after EVERY row and the run resumes from it,
so a codec fault, a dropped TCP connection or a reclaimed Kaggle session costs one row and
never the run. Four separate incidents with no shared mechanism established that enumerating
mechanisms is the wrong defence; this is the structural one.
"""
import glob
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import time
from collections import Counter, defaultdict

import requests

REPO = 'prosperpiusmbaruku007-ship-it/AFRICA-GIANTS'
RAW = f'https://raw.githubusercontent.com/{REPO}/main'
DATASET_REPO = 'prospAprospA007/africa-giants-dataset'

# The index production serves. ASSERTED, not assumed — see gate_index_identity() below.
EXPECTED_FACT_COUNT = 184

# The commit the last full gate ran at, and its re-derived in-corpus headline. Both are read
# back out of the committed artifact at run time rather than trusted from this comment.
BASELINE_COMMIT = '1476caa'

# The same URL eval/controls/verify_fee_band_guard_live_2026_10_08.py uses, so the two cannot
# drift apart and point at different endpoints.
PRODUCTION_HEALTH = 'https://prosperpiusmbaruku007--chike-inference-health.modal.run'

print('=' * 90)
print('FULL GATE — production configuration, 184-fact index, D-FIDELITY-7 and -8 wired')
print('=' * 90)

# ── AUTH ─────────────────────────────────────────────────────────────────────────────────
try:
    import kaggle_secrets
    _sc = kaggle_secrets.UserSecretsClient()
    hf_token = _sc.get_secret('AFRICA_GIANTS')
except Exception as e:                                                   # noqa: BLE001
    raise RuntimeError('run on Kaggle with the AFRICA_GIANTS secret attached') from e
assert hf_token, 'AFRICA_GIANTS empty'
os.environ['HF_TOKEN'] = hf_token
print(f'[auth] AFRICA_GIANTS ({hf_token[:6]}...) OK')

# The judge is MANDATORY (2026-08-09) and the reason is specific, not procedural: at 1476caa
# eval_318 (tells a TZS 205,000,000 business it need not register for VAT against a 200M
# threshold) and eval_320 (SDL 28,000 on a ONE-employee payroll) BOTH scored pass=True. The
# regex scorer positively CREDITS the two worst defects of that cycle; only the judge calls
# either wrong. The instrument that can see the wrong-direction class must not be the one that
# can silently not run. Fail at second 0, not after the GPU pass.
try:
    OR_KEY = _sc.get_secret('OPENROUTER_API_KEY')
except Exception:                                                        # noqa: BLE001
    OR_KEY = os.environ.get('OPENROUTER_API_KEY', '')
JUDGE_OPT_OUT = os.environ.get('CHIKE_JUDGE', '1') == '0'
if not OR_KEY and not JUDGE_OPT_OUT:
    raise RuntimeError(
        'OPENROUTER_API_KEY missing — the judge overlay is MANDATORY for a gate run.\n'
        '  Attach it as a Kaggle secret named OPENROUTER_API_KEY (or set the env var).\n'
        '  Cost on the last full run: ~$0.20 for this many rows, against ~1h of GPU.\n'
        '  Explicit opt-out: CHIKE_JUDGE=0. The artifact is then stamped SKIPPED and its\n'
        '  headline is NOT trustworthy on its own — it cannot see the class above.')
RUN_JUDGE = bool(OR_KEY) and not JUDGE_OPT_OUT
print(f'[auth] judge overlay {"ON (mandatory)" if RUN_JUDGE else "EXPLICITLY DISABLED"}')

# ── CLONE, AND REFUSE A STALE ONE ────────────────────────────────────────────────────────
_CLONE = '/kaggle/working/AFRICA-GIANTS'
if not os.path.isdir(_CLONE):
    subprocess.run(['git', 'clone', '--depth', '1', f'https://github.com/{REPO}.git', _CLONE],
                   check=True)
else:
    subprocess.run(['git', '-C', _CLONE, 'fetch', '--depth', '1', 'origin', 'main'], check=True)
    subprocess.run(['git', '-C', _CLONE, 'reset', '--hard', 'origin/main'], check=True)
sys.path.insert(0, _CLONE)
_sha = subprocess.run(['git', '-C', _CLONE, 'rev-parse', '--short', 'HEAD'],
                      capture_output=True, text=True).stdout.strip()
try:
    _live = requests.get(f'https://api.github.com/repos/{REPO}/commits/main',
                         headers={'Cache-Control': 'no-cache'}, timeout=20).json()['sha'][:7]
except Exception:                                                        # noqa: BLE001
    _live = '?'
# A stale clone is FATAL here, not a warning. The whole point of this run is that it measures a
# specific build; measuring a different one silently is the stale-clone near-miss of 2026-08-26.
if _live not in ('?', '') and _live[:7] != _sha[:7]:
    raise RuntimeError(f'STALE CLONE: GitHub main is {_live}, clone is {_sha}. Re-run the cell.')
print(f'[clone] HEAD {_sha} (GitHub main {_live}) — fresh')

from chike import judge as chike_judge                                   # noqa: E402
from chike import clarification, fidelity, pipeline_v15                  # noqa: E402
from chike.model_abstraction import ModelBackend                         # noqa: E402
from chike.orchestrator import Orchestrator                              # noqa: E402
from chike.scoring import score_question, scorer_reliability             # noqa: E402

# ── THE POLARITY RULE — IMPORTED FROM THE CLONE, NEVER RE-IMPLEMENTED HERE ───────────────
# ⛔ A PRESENCE CHECK CANNOT JUDGE AN INDEX ROW. Rows 57, 63 and 159 DELIBERATELY carry their
# superseded value under a negation — row 57 reads "...hakuna kizingiti ... Na SI TZS
# 11,000,000." — so `'11,000,000' in row` is True of the row that PROTECTS the figure. This
# file shipped exactly that check at two sites and the offline test caught the first one; the
# cost would have been a FATAL pre-flight abort after the HF download, i.e. the GPU hour this
# package exists to protect.
#
# The rule is NOT re-written here. `sweep_superseded_values_in_built_index._asserted_spans` is
# the committed, hardened one, authored for THIS population (built index rows) rather than
# borrowed from another — the sixth R20 arrival point is a detector pointed at text its cues
# were never written for. It also already carries the four narrowings whose every failure
# DELETED findings, and a second copy of a cue list is the defect R39 names: a cue present in
# two rules has to be removed from two rules, and only a re-run finds the second.
_sws = importlib.util.spec_from_file_location(
    'superseded_sweep', os.path.join(_CLONE, 'eval', 'index_quality',
                                     'sweep_superseded_values_in_built_index.py'))
_SWEEP = importlib.util.module_from_spec(_sws)
_sws.loader.exec_module(_SWEEP)
# The instrument is exercised BEFORE it judges anything — nine planted specimens in both
# directions, including row 57's own sentence-final negated figure. An inert rule returns
# "nothing asserted" for every row, which is byte-identical to a clean index.
_SWEEP._self_test()
print('[polarity] mention-vs-assertion rule loaded from the clone, self-test PASSED')


def asserts_value(text, token):
    """True when `text` ASSERTS `token`, False when it only MENTIONS it under a negation."""
    return bool(_SWEEP._asserted_spans(text or '', token))

# ── CONFIG (R14) ─────────────────────────────────────────────────────────────────────────
_cb = str(int(time.time() * 1000))
CONFIG = requests.get(f'{RAW}/kaggle/chike_config.json?cb={_cb}',
                      headers={'Cache-Control': 'no-cache'}, timeout=20).json()
SYSTEM_PROMPT = CONFIG['system_prompt']
REFUSAL_PHRASES = CONFIG['refusal_phrases']
GEN = CONFIG['generation_params']
STOP = GEN['stop_strings']
ADAPTER = CONFIG.get('adapter_repo', 'prospAprospA007/africa-giants-adapter-v15')
print(f'[config] v={CONFIG.get("version")} adapter={ADAPTER} '
      f'rag_fact_count={CONFIG.get("rag_fact_count")}')


# ── THE INDEX CONTENT PROBES — MODULE-LEVEL SO THEY CAN BE RUN OFFLINE ───────────────────
# ⛔ THIS IS A FUNCTION RATHER THAN A BLOCK INSIDE `gate_index_identity` FOR ONE REASON: THE
# OFFLINE TEST MUST *RUN* IT, NOT GREP IT. A test asserting that the source contains the string
# `must_not_assert` is R20's vacuous check — it passes on a probe that is wired wrong, mis-keyed,
# or looking at the wrong row. Lifting it out lets tests/test_gate_production_package.py call it
# against the real committed index, which is the only thing that can catch what happened here:
#
#   `must_not_contain` on row 57 — the row that DENIES the fabrication ("EFD haina kizingiti cha
#   mauzo kwa mwaka ... Na SI TZS 11,000,000"). Containment is True of exactly that row, so this
#   FATAL pre-flight would have aborted the run — AFTER the HF download, on a correct index.
#   CLAUDE.md already records that rows 57, 63 and 159 deliberately carry their superseded value
#   under a negation and that "a presence check would fail the very rows it protects".
#
# Every probe keeps a POSITIVE limb, and that is not symmetry for its own sake: a negated-mention
# check passes trivially on a row that has lost the content altogether, so the positive limb is
# the only thing standing between this probe and vacuity.
#
# BOTH NOTATIONS ARE LISTED FOR EVERY CLAIM (R36). Swahili writes money in digits AND in words in
# the same file; a digit-keyed sweep found 3 rows where a claim-keyed one found 14. So
# 'milioni 11' is not redundant with '11,000,000'.
INDEX_CONTENT_PROBES = [
    {'row': 172, 'must_contain': ['70,000'],
     'must_not_assert': ['USD 25', 'dola 25'],
     'why': 'the BRELA foreign-company late-filing penalty. USD 25 is the superseded '
            '2026-06-30 figure; TZS 70,000 is the 2026-10-06 capture.'},
    # ⚠️ `haina`, not `hakuna`. The live row reads "EFD HAINA kizingiti cha mauzo kwa mwaka"; a
    # first draft of the offline test asserted `hakuna` and failed on the correct row. Here that
    # slip would have been FATAL after the HF download. The forms are LISTED rather than
    # assembled from optional morphemes (R37) and matched if ANY is present — each states the
    # same claim, so this is claim-keyed, not loosened.
    {'row': 57, 'must_contain_any': ['haina kizingiti', 'hakuna kizingiti', 'hakina kizingiti'],
     'must_not_assert': ['TZS 11,000,000', '11,000,000', 'milioni 11'],
     'why': 'the fabricated EFD turnover threshold. s.44(1) makes EFD the default for everyone; '
            'any assertion of a threshold here is the defect row 57 carried live for five and a '
            'half weeks. A negated MENTION is the correction working, not the defect.'},
]


def index_content_probes(facts, asserted_spans):
    """Run INDEX_CONTENT_PROBES against `facts`. Returns (fails, detail).

    `asserted_spans` is injected rather than reached for, so the caller decides which polarity
    rule is in force and the test exercises the same one the Kaggle run does.
    """
    fails, detail = [], {}
    for p in INDEX_CONTENT_PROBES:
        if p['row'] >= len(facts):
            fails.append(f'content probe row {p["row"]} is out of range ({len(facts)} rows)')
            continue
        text = facts[p['row']]
        text = text if isinstance(text, str) else json.dumps(text, ensure_ascii=False)
        for needle in p.get('must_contain', []):
            if needle.lower() not in text.lower():
                fails.append(f'row {p["row"]} does NOT contain {needle!r} — {p["why"]}')
        any_of = p.get('must_contain_any', [])
        if any_of and not any(n.lower() in text.lower() for n in any_of):
            fails.append(f'row {p["row"]} contains NONE of {any_of!r} — {p["why"]}')
        for needle in p.get('must_not_assert', []):
            spans = asserted_spans(text, needle)
            if spans:
                fails.append(f'row {p["row"]} ASSERTS {needle!r} (as {spans!r}, not under a '
                             f'negation) — {p["why"]}')
        detail[f'row_{p["row"]}'] = text[:200]
    return fails, detail


# ── PRE-FLIGHT GATES — every one FATAL, every one before the GPU is touched ──────────────
def gate_index_identity():
    """⛔ THE INDEX THIS RUN MEASURES MUST BE THE ONE PRODUCTION SERVES, AND THAT IS A CLAIM
    ABOUT BYTES, NOT ABOUT A ROW COUNT.

    Four checks, because each catches something the others cannot:
      1. the HF copy the gate downloads == the repo copies in BOTH kaggle/ and
         chike-inference/ (R15's dual-commit; a one-sided commit means the gate and production
         disagree and nothing says so)
      2. the row count == EXPECTED_FACT_COUNT, and == chike_config.json's rag_fact_count
      3. a CONTENT probe: row 172 must read TZS 70,000, not USD 25. A digest proves the files
         match each other; only a content probe proves they are the NEW build. This is the
         probe that carried the whole of the 2026-10-07 deploy evidence before /health existed.
      4. row 57 must NOT assert the fabricated TZS 11,000,000 EFD threshold.

    The previous harness PRINTED a mismatch here and carried on. A printed warning two hours
    into a GPU run is a check that cannot fail.
    """
    from huggingface_hub import hf_hub_download
    npy = hf_hub_download(repo_id=DATASET_REPO, filename='rag_embeddings.npy',
                          repo_type='dataset', token=hf_token)
    txt = hf_hub_download(repo_id=DATASET_REPO, filename='rag_facts_text.json',
                          repo_type='dataset', token=hf_token)

    def sha(p):
        return hashlib.sha256(open(p, 'rb').read()).hexdigest()

    fails, detail = [], {}
    for hf_path, rels in ((npy, ('kaggle/rag_embeddings.npy',
                                 'chike-inference/rag_embeddings.npy')),
                          (txt, ('kaggle/rag_facts_text.json',
                                 'chike-inference/rag_facts_text.json'))):
        h = sha(hf_path)
        detail[os.path.basename(hf_path)] = {'hf': h[:16]}
        for rel in rels:
            r = sha(os.path.join(_CLONE, rel))
            detail[os.path.basename(hf_path)][rel] = r[:16]
            if r != h:
                fails.append(f'{rel} sha256 {r[:16]} != HF {h[:16]} — R15 dual-commit is out '
                             f'of sync, so the gate and production are not reading the same '
                             f'index')
    facts = json.load(open(txt, encoding='utf-8'))
    detail['rows'] = len(facts)
    if len(facts) != EXPECTED_FACT_COUNT:
        fails.append(f'index has {len(facts)} rows, expected {EXPECTED_FACT_COUNT}')
    cfg_n = CONFIG.get('rag_fact_count')
    if cfg_n is not None and cfg_n != len(facts):
        fails.append(f'chike_config.json rag_fact_count={cfg_n} != index rows {len(facts)}')

    # CONTENT probes — a digest cannot tell a matched pair of STALE files from a matched pair of
    # fresh ones. R34: read the artifact, do not infer from metadata.
    pf, pd = index_content_probes(facts, _SWEEP._asserted_spans)
    fails.extend(pf)
    detail.update(pd)
    return fails, detail, npy, txt


def gate_guards_are_wired():
    """⛔ WATCH THE GUARDS BLOCK, RATHER THAN CHECKING THAT THEY EXIST (R26).

    "D-FIDELITY-7 and -8 are wired" is the premise of this whole run, and `grep` cannot
    establish it: two inert controls found on 2026-08-24 had nothing wrong with their logic —
    one was handed no files, the other lived in a module production never imports. So each
    guard is PLANTED with the exact body it exists to catch, and given a clean body it must
    pass. Offline, instant, before the GPU.

    The specimens are the real measured defects, verbatim from the live replies that motivated
    each guard, not paraphrases — a five-word paraphrase was enough to flip a correct body into
    a flagged one once.
    """
    checks = []

    # D-FIDELITY-7 — the fabricated EFD threshold, as served live on 2026-10-06 for eval_347.
    dirty7 = ('Kizingiti cha kuanza kutumia EFD ni mauzo ya TZS 11,000,000 kwa mwaka.')
    clean7 = ('EFD inahitajika kwa default kwa kila mfanyabiashara; hakuna kizingiti cha '
              'mauzo. Usajili wa VAT ni TZS 200,000,000 kwa mwaka.')
    checks.append(('D-FIDELITY-7 blocks the fabricated EFD threshold',
                   bool(fidelity.body_states_wrong_threshold(dirty7)), True))
    checks.append(('D-FIDELITY-7 passes a correct no-threshold body',
                   bool(fidelity.body_states_wrong_threshold(clean7)), False))

    # D-FIDELITY-8 — the live 290,000 answer for a TZS 2,000,000,000 share capital.
    q8 = ('Nina kampuni na mtaji wa hisa wa TZS 2,000,000,000. Ada ya kusajili BRELA ni '
          'ngapi?')
    dirty8 = 'Ada ya kusajili kampuni yako ni TZS 290,000.'
    clean8 = 'Ada ya kusajili kampuni yenye mtaji huo ni TZS 600,000.'
    checks.append(('D-FIDELITY-8 blocks the wrong share-capital band fee',
                   bool(fidelity.body_states_wrong_fee_band(q8, dirty8)), True))
    checks.append(('D-FIDELITY-8 passes the correct band fee',
                   bool(fidelity.body_states_wrong_fee_band(q8, clean8)), False))

    # And the REPLACEMENT COPY must exist and be non-trivial — a guard that replaces a body
    # with an empty string on the fact path ships silence, which is the one outcome worse than
    # the wrong answer it removed.
    copy8 = clarification.wrong_fee_band_withheld()
    checks.append(('D-FIDELITY-8 replacement copy is substantive',
                   len(copy8) > 200 and 'mtaji wa hisa' in copy8, True))
    copy7 = clarification.wrong_threshold_withheld('efd')
    checks.append(('D-FIDELITY-7 replacement copy is substantive', len(copy7) > 80, True))

    fails = [f'{name}: got {got!r}, expected {want!r}' for name, got, want in checks
             if got != want]
    return fails, [{'check': n, 'got': g, 'want': w} for n, g, w in checks]


def gate_measures_what_is_serving():
    """Ask PRODUCTION what it is running, and compare `chike/` tree-for-tree.

    ⛔ THIS IS REPORTING, NOT A BLOCK, AND THE DISTINCTION IS DELIBERATE. The gate must still
    run if production is mid-deploy or /health is unreachable; what it must never do is CLAIM to
    measure the serving build without having asked. So the answer is recorded in the artifact
    either way, and the headline is stamped with it.

    The comparison is on the `chike/` SUBTREE, not on the commit SHA. A gate at a later commit
    that touched only docs, tests and eval data is measuring byte-identical answer-producing
    code; demanding SHA equality would force a pointless redeploy and would make the honest
    answer unavailable. Tree equality is the claim that actually matters.
    """
    out = {'health_url': PRODUCTION_HEALTH}
    try:
        h = requests.get(PRODUCTION_HEALTH, timeout=120).json()
    except Exception as e:                                               # noqa: BLE001
        out['error'] = str(e)[:200]
        out['verdict'] = ('COULD NOT ASK — /health unreachable. This run does NOT carry '
                          'evidence that it measures the serving build.')
        return out
    out['health'] = h
    served = (h.get('build') or '').strip()
    out['served_build'] = served
    out['gate_build'] = _sha
    if not served or served == 'dev':
        out['verdict'] = ('/health reports no build SHA, so the serving code cannot be '
                          'identified. NOT evidence.')
        return out
    gate_tree = subprocess.run(['git', '-C', _CLONE, 'rev-parse', f'{_sha}:chike'],
                               capture_output=True, text=True).stdout.strip()
    srv = subprocess.run(['git', '-C', _CLONE, 'rev-parse', f'{served}:chike'],
                         capture_output=True, text=True)
    served_tree = srv.stdout.strip() if srv.returncode == 0 else ''
    out['gate_chike_tree'] = gate_tree
    out['served_chike_tree'] = served_tree
    if not served_tree:
        out['verdict'] = (f'the served SHA {served} is not in this shallow clone, so the trees '
                          f'cannot be compared. Re-run with a full clone to settle it.')
    elif served_tree == gate_tree:
        out['verdict'] = (f'MEASURES THE SERVING CODE. chike/ at the gate commit ({_sha}) is '
                          f'byte-identical to chike/ at the serving commit ({served}); the '
                          f'commits differ only outside the answer-producing package.')
    else:
        diff = subprocess.run(['git', '-C', _CLONE, 'diff', '--stat', f'{served}..{_sha}',
                               '--', 'chike/'], capture_output=True, text=True).stdout
        out['chike_diff_stat'] = diff[-1500:]
        out['verdict'] = (f'⚠️ chike/ DIFFERS between the gate commit ({_sha}) and the serving '
                          f'commit ({served}). This run measures code production is NOT '
                          f'running. The diff is recorded above — read it before quoting any '
                          f'number as production behaviour.')
    return out


print('\n' + '-' * 90)
print('PRE-FLIGHT — all gates FATAL, all before the GPU is touched')
print('-' * 90)
idx_fails, idx_detail, _rag_npy, _rag_txt = gate_index_identity()
print(f'  index identity   : {"OK" if not idx_fails else "FAIL"}   rows={idx_detail["rows"]}')
print(f'    row 172: {idx_detail.get("row_172", "")[:110]}')
grd_fails, grd_detail = gate_guards_are_wired()
print(f'  guards planted   : {"OK" if not grd_fails else "FAIL"}   '
      f'{len(grd_detail)} checks, both directions')
for f in idx_fails + grd_fails:
    print(f'    ⛔ {f}')
if idx_fails or grd_fails:
    raise RuntimeError('PRE-FLIGHT FAILED — nothing was run. Fix the above; a gate measured '
                       'against the wrong index, or with a guard that does not fire, produces '
                       'a number that describes no system.')
serving = gate_measures_what_is_serving()
print(f'  serving identity : {serving["verdict"][:200]}')

# ── DATA: the 400, and the committed old-key table ───────────────────────────────────────
def _load(rel, n):
    rows = [json.loads(l) for l in open(os.path.join(_CLONE, rel), encoding='utf-8')
            if l.strip()]
    assert len(rows) == n, f'{rel}: expected {n}, got {len(rows)}'
    return rows


gate = _load('eval/accuracy_gate/eval_questions_001.jsonl', 200)
additions = _load('eval/accuracy_gate/eval_questions_002_additions.jsonl', 50)
additions3 = _load('eval/accuracy_gate/eval_questions_003.jsonl', 150)
for r in gate:
    r['_source'] = 'gate_001'
for r in additions:
    r['_source'] = 'additions_002'
for r in additions3:
    r['_source'] = 'additions_003'
ALL = gate + additions + additions3
BY_ID = {q['id']: q for q in ALL}
print(f'\n[data] {len(ALL)} questions (200 gate + 50 additions + 150 adversarial)')

# ⛔ THE OLD KEYS ARE LOADED FROM THE COMMITTED ARTIFACT, NOT RE-DERIVED HERE. Re-deriving them
# would create a second implementation of the same table, and the two could disagree without
# either being obviously wrong — the exact defect that let the 2026-10-07 dry run report SAFE
# while the real regen aborted. One owner: derive_gold_key_corrections_2026_10_09.py.
_kc_path = os.path.join(_CLONE, 'eval', 'results', 'gold_key_corrections_2026_10_09.json')
with open(_kc_path, encoding='utf-8') as fh:
    KEYCORR = json.load(fh)
DUAL_SCORE_IDS = list(KEYCORR['dual_score_these'])
OLD_KEYS = {f['id']: f['old'] for f in KEYCORR['findings_400']
            if f.get('scored_fields_changed') and 'old' in f}
assert DUAL_SCORE_IDS, ('the key-correction artifact lists NO rows to dual-score. Either no '
                        'gold changed — in which case say so explicitly rather than shipping '
                        'an arm that measures nothing — or the derivation broke.')
assert all(i in OLD_KEYS for i in DUAL_SCORE_IDS)
assert all(i in BY_ID for i in DUAL_SCORE_IDS), 'a dual-score id is not in the 400'
print(f'[keys] dual-scoring {len(DUAL_SCORE_IDS)} rows under both keys: {DUAL_SCORE_IDS}')
print(f'[keys] scorer-blind declared flips (regex delta is 0 by construction): '
      f'{KEYCORR["scorer_blind_verdict_flips"]["ids"]}')

# ── MODEL ────────────────────────────────────────────────────────────────────────────────
subprocess.run(['pip', 'install', '-q', '-U', 'bitsandbytes>=0.46.1'], check=True)
subprocess.run(['pip', 'install', '-q', '-U', 'sentence-transformers>=2.7.0'], check=True)
import torch                                                             # noqa: E402
from transformers import (AutoTokenizer, AutoModelForCausalLM,           # noqa: E402
                          BitsAndBytesConfig, StoppingCriteria, StoppingCriteriaList)

print(f'[model] loading {ADAPTER} (4-bit) ...', flush=True)
tokenizer = AutoTokenizer.from_pretrained(ADAPTER, token=hf_token, trust_remote_code=True)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token
_bnb = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type='nf4',
                          bnb_4bit_compute_dtype=torch.float16,
                          bnb_4bit_use_double_quant=True)
model = AutoModelForCausalLM.from_pretrained(ADAPTER, quantization_config=_bnb,
                                             device_map='auto', token=hf_token,
                                             trust_remote_code=True)
model.eval()
print('[model] loaded OK')


class _Stop(StoppingCriteria):
    def __init__(self, tok, stops):
        self.tok, self.stops = tok, stops

    def __call__(self, input_ids, scores, **kw):
        return any(s in self.tok.decode(input_ids[0], skip_special_tokens=True)[-100:]
                   for s in self.stops)


def _generate(prompt, params=None):
    """The Kaggle twin of modal_app.ChikeModel._generate — same StoppingCriteria, same
    gen_kwargs from config (R14), same slicing. Decoding is greedy, so a changed answer is a
    changed system and never sampling noise."""
    p = dict(GEN)
    if params:
        p.update(params)
    inp = tokenizer(prompt, return_tensors='pt').to(model.device)
    with torch.no_grad():
        out = model.generate(
            **inp,
            max_new_tokens=int(p.get('max_new_tokens', 350)),
            do_sample=bool(p.get('do_sample', False)),
            repetition_penalty=float(p.get('repetition_penalty', 1.1)),
            no_repeat_ngram_size=int(p.get('no_repeat_ngram_size', 0)),
            stopping_criteria=StoppingCriteriaList([_Stop(tokenizer, STOP)]),
            eos_token_id=tokenizer.eos_token_id, pad_token_id=tokenizer.pad_token_id)
    return tokenizer.decode(out[0][inp['input_ids'].shape[1]:],
                            skip_special_tokens=True).strip()


class _Backend(ModelBackend):
    def __init__(self):
        # The attribute Orchestrator._backend_tokenizer() looks for, so build_chat_prompt
        # routes through apply_chat_template — byte-identical to production's prompt format.
        # Without it the orchestrator silently falls back to a naive-concat shape the model was
        # never trained on, and the whole run mis-measures.
        self.tokenizer = tokenizer

    def generate(self, prompt, params=None):
        return _generate(prompt, params)


single_arm = pipeline_v15.V15Retriever(emb_path=_rag_npy, texts_path=_rag_txt,
                                       expected_fact_count=EXPECTED_FACT_COUNT)
print(f'[rag] preflight OK — {single_arm.preflight() if hasattr(single_arm, "preflight") else EXPECTED_FACT_COUNT} facts')
orch = Orchestrator(backend=_Backend(), retriever=single_arm.retrieve_facts,
                    system_prompt=SYSTEM_PROMPT)


# ── GUARD CLASSIFICATION — structural, then cross-checked against the generators ─────────
# ⛔ HOW A GUARD INTERVENTION IS IDENTIFIED, AND WHY IT IS NOT A PROSE MATCH.
#
# `_validate_and_clean` returns EARLY on a pre-existing clarification (`if
# sub.needs_clarification: return sub`), so a never-guess clarification keeps `raw_text == ""`
# — the model was never called. Every GUARD branch, by contrast, sets `raw_text=sub.text`: the
# model DID answer and the guard replaced what it said. That is a structural discriminator
# already present in the shipped code, not a pattern invented for this harness.
#
#   fact-path guard REPLACEMENT : needs_clarification AND raw_text != ""
#   compute-path guard BLANKING : computation is not None AND text == "" AND raw_text != ""
#
# The copy is then matched against `chike.clarification`'s OWN GENERATORS to name WHICH guard
# fired. Matching against the generator is not the same thing as hand-writing the Swahili: if
# the copy changes, the generator changes with it. The two signals are reported SEPARATELY, and
# a structural hit with no copy match is recorded as `guard=UNNAMED` rather than dropped — a
# classifier that silently discards what it cannot name is R39's deleting direction.
_GUARD_COPY = {}
try:
    _GUARD_COPY[clarification.wrong_fee_band_withheld()] = 'D-FIDELITY-8'
except Exception:                                                        # noqa: BLE001
    pass
for _subj in ('efd', 'vat', 'sdl', 'nssf', 'wcf', 'paye', 'tin', 'leseni', ''):
    try:
        _GUARD_COPY.setdefault(clarification.wrong_threshold_withheld(_subj), 'D-FIDELITY-7')
    except Exception:                                                    # noqa: BLE001
        pass
for _n in range(0, 61):
    try:
        _GUARD_COPY.setdefault(clarification.headcount_contradiction(_n), 'GUARD-A-headcount')
    except Exception:                                                    # noqa: BLE001
        pass
assert len(_GUARD_COPY) >= 3, ('the guard-copy table was built from the generators and came '
                               'out nearly empty, so every guard would be reported UNNAMED. '
                               'A classifier that cannot name anything is inert.')
print(f'[guards] copy table built from the generators: {len(_GUARD_COPY)} strings, '
      f'{sorted(set(_GUARD_COPY.values()))}')


def classify_guards(reply):
    """Return (n_interventions, [names]) for one Reply, walking its sub-answers."""
    hits = []
    for sa in getattr(reply, 'sub_answers', ()) or ():
        replaced = bool(sa.needs_clarification) and bool(sa.raw_text)
        blanked = (sa.computation is not None and not (sa.text or '').strip()
                   and bool(sa.raw_text))
        if not (replaced or blanked):
            continue
        name = _GUARD_COPY.get((sa.text or '').strip())
        if name is None:
            name = 'COMPUTE-BLANKED' if blanked else 'UNNAMED'
        hits.append({'guard': name, 'mode': 'blanked' if blanked else 'replaced',
                     'pre_guard_body': (sa.raw_text or '')[:400],
                     'post_guard_text': (sa.text or '')[:400]})
    return hits


# ── PER-ROW FLUSH AND RESUME ───────────────────────────────────────────────────────────
ARTIFACT_NAME = f'gate_production_{_sha}.json'
ARTIFACT_PATH = f'/kaggle/working/{ARTIFACT_NAME}'
_rows_done = []
if os.path.exists(ARTIFACT_PATH):
    try:
        with open(ARTIFACT_PATH, encoding='utf-8') as fh:
            _prev = json.load(fh)
        if _prev.get('clone_head') == _sha:
            _rows_done = _prev.get('rows', [])
            print(f'[resume] {len(_rows_done)} rows already measured at this commit — '
                  f'continuing, not restarting')
    except Exception as e:                                               # noqa: BLE001
        print(f'[resume] existing artifact unusable ({str(e)[:100]}) — starting fresh')


def _flush(rows, **extra):
    payload = {
        'mode': 'full_gate_production_config',
        'clone_head': _sha, 'github_head': _live,
        'utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'adapter': ADAPTER, 'config_version': CONFIG.get('version'),
        'index_facts': EXPECTED_FACT_COUNT, 'index_identity': idx_detail,
        'guard_preflight': grd_detail,
        'serving_identity': serving,
        'baseline_commit': BASELINE_COMMIT,
        'key_corrections': {'dual_scored': DUAL_SCORE_IDS,
                            'scorer_blind_flips': KEYCORR['scorer_blind_verdict_flips'],
                            'source': 'eval/results/gold_key_corrections_2026_10_09.json'},
        'judge_overlay_status': ('pending' if RUN_JUDGE else
                                 'SKIPPED (CHIKE_JUDGE=0) — headline NOT trustworthy alone'),
        'n_questions': len(ALL), 'rows_measured': len(rows), 'rows': rows,
    }
    payload.update(extra)
    tmp = ARTIFACT_PATH + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)
    os.replace(tmp, ARTIFACT_PATH)       # atomic: a crash mid-write cannot corrupt the artifact
    return payload


def _publish(payload, complete=False):
    payload['complete'] = complete
    with open(ARTIFACT_PATH, 'w', encoding='utf-8') as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)
    local = hashlib.sha256(open(ARTIFACT_PATH, 'rb').read()).hexdigest()
    from huggingface_hub import HfApi, hf_hub_download as _dl
    for attempt in range(1, 4):
        try:
            HfApi().upload_file(path_or_fileobj=ARTIFACT_PATH, path_in_repo=ARTIFACT_NAME,
                                repo_id=DATASET_REPO, repo_type='dataset', token=hf_token)
            back = _dl(repo_id=DATASET_REPO, filename=ARTIFACT_NAME, repo_type='dataset',
                       token=hf_token, force_download=True)
            if hashlib.sha256(open(back, 'rb').read()).hexdigest() == local:
                print(f'[publish] OK  {DATASET_REPO}/{ARTIFACT_NAME}  sha256={local[:16]}  '
                      f'complete={complete}', flush=True)
                return True
            print('[publish] VERIFY MISMATCH — retrying', flush=True)
        except Exception as e:                                           # noqa: BLE001
            print(f'[publish] attempt {attempt}/3 failed: {str(e)[:180]}', flush=True)
            time.sleep(10 * attempt)
    print('\n' + '!' * 90)
    print(f'!! HF PUBLISH FAILED. The artifact IS at {ARTIFACT_PATH} — DOWNLOAD IT MANUALLY.')
    print('!' * 90 + '\n', flush=True)
    return False


# ── ROUTE TAGGING ────────────────────────────────────────────────────────────────────────
for q in ALL:
    try:
        q['_compute'] = bool(orch.classify(q['question_sw'])) and any(
            orch.route(p).kind == 'compute' for p in orch.decompose(q['question_sw']))
    except Exception:                                                    # noqa: BLE001
        q['_compute'] = False
print(f'[route] {sum(q["_compute"] for q in ALL)}/{len(ALL)} routed to compute')


# ── THE RUN ──────────────────────────────────────────────────────────────────────────────
def _score_both_keys(q, gen, clarified):
    """Score under the CURRENT key always, and additionally under the BASELINE key when this
    row's gold changed. `old_pass` is None for every unchanged row, so the key-correction delta
    is computed over exactly the rows whose key moved and over nothing else."""
    if clarified:
        new_pass = False
    else:
        try:
            new_pass = bool(score_question(q, gen, REFUSAL_PHRASES))
        except Exception:                                                # noqa: BLE001
            new_pass = False
    old_pass = None
    if q['id'] in OLD_KEYS:
        oq = dict(q)
        oq.update(OLD_KEYS[q['id']])          # answer_type + the two gold fields, as at baseline
        old_pass = False if clarified else bool(score_question(oq, gen, REFUSAL_PHRASES))
    return new_pass, old_pass


print(f'\n[run] {len(ALL) - len(_rows_done)} of {len(ALL)} questions through the production '
      f'orchestrator ...', flush=True)
done_ids = {r['id'] for r in _rows_done}
rows, t0 = list(_rows_done), time.time()
for i, q in enumerate(ALL):
    if q['id'] in done_ids:
        continue
    gen = raw = ''
    clarified = False
    guards = []
    err = None
    try:
        reply = orch.answer(q['question_sw'])
        gen, raw = reply.text, reply.raw_text
        clarified = bool(reply.needs_clarification)
        guards = classify_guards(reply)
        refused = bool(getattr(reply, 'refused', False))
    except Exception as e:                                               # noqa: BLE001
        # A per-row error is RECORDED, never fatal. A run that aborts on row 180 loses 180 rows
        # of GPU; a run that records the error loses one row and says which.
        err, gen, refused = f'{type(e).__name__}: {e}'[:300], '', False
    new_pass, old_pass = _score_both_keys(q, gen, clarified)
    try:
        reliable, why = scorer_reliability(q, gen)
    except Exception:                                                    # noqa: BLE001
        reliable, why = True, ''
    rows.append({
        'id': q['id'], 'source': q['_source'], 'subdomain': q.get('subdomain', ''),
        'answer_type': q.get('answer_type', ''), 'compute': q['_compute'],
        'question_sw': q['question_sw'],
        'correct_answer_sw': q.get('correct_answer_sw', ''),
        'generated': gen, 'raw_generated': raw,
        'clarified': clarified, 'refused': refused,
        'guard_interventions': guards,
        'pass': new_pass, 'pass_under_baseline_key': old_pass,
        'reliable': reliable, 'reliable_reason': why,
        'error': err,
        'target': q.get('_target', ''), 'why_hard': q.get('_why_hard', ''),
    })
    _flush(rows)                                     # EVERY row, not every 25
    if len(rows) % 25 == 0:
        print(f'  [{len(rows)}/{len(ALL)}] {time.time() - t0:.0f}s', flush=True)
payload = _flush(rows)
_publish(payload)
assert len(rows) == len(ALL), f'{len(rows)} rows measured, expected {len(ALL)}'


# ── SCORING: TWO AXES, AND THE PARTITION IS ASSERTED ────────────────────────────────────
def outcome(r):
    """⛔ AXIS 1 — EXHAUSTIVE AND MUTUALLY EXCLUSIVE. Asserted below, because a classification
    whose buckets do not sum to its denominator is reporting something other than what it
    claims, and nothing else in the run would say so."""
    if r['error']:
        return 'ERROR'
    if r['clarified']:
        return 'NO_ANSWER'
    return 'RIGHT' if r['pass'] else 'WRONG'


def bars(rows_):
    """A1 / A2 / guard count over one population, with the population NAMED (R22)."""
    inc = [r for r in rows_ if r['subdomain'] != 'out_of_corpus']
    c = Counter(outcome(r) for r in inc)
    n = len(inc)
    guard_rows = [r for r in inc if r['guard_interventions']]
    assert c['RIGHT'] + c['WRONG'] + c['NO_ANSWER'] + c['ERROR'] == n, (
        f'the outcome partition does not sum to the denominator: {dict(c)} vs n={n}')
    return {
        'n_in_corpus': n,
        'A2_right': c['RIGHT'], 'A2_rate': (c['RIGHT'] / n if n else 0.0),
        'A1_wrong': c['WRONG'], 'A1_rate': (c['WRONG'] / n if n else 0.0),
        'no_answer': c['NO_ANSWER'], 'no_answer_rate': (c['NO_ANSWER'] / n if n else 0.0),
        'errors': c['ERROR'],
        'guard_rows': len(guard_rows),
        'guard_by_name': dict(Counter(g['guard'] for r in guard_rows
                                      for g in r['guard_interventions'])),
        # ⛔ THE CROSS-TAB IS THE POINT. A compute body blanked by a guard still renders the
        # engine's working, so it can be RIGHT; a fact body replaced by a guard can only be
        # NO_ANSWER. Netting them would hide exactly the distinction this run exists to show.
        'guard_x_outcome': dict(Counter(outcome(r) for r in guard_rows)),
    }


def reliable_only(rows_):
    return [r for r in rows_ if r['reliable']]


BUCKETS = {
    'ALL_400': rows,
    'fact_path_190': [r for r in rows if r['source'] == 'gate_001' and not r['compute']],
    'staged_50': [r for r in rows if r['source'] == 'additions_002'],
    'compute_type': [r for r in rows if r['compute']],
    'adversarial_150': [r for r in rows if r['source'] == 'additions_003'],
}

# The baseline, read back out of the committed artifact — never from a comment or a write-up.
_bl_path = os.path.join(_CLONE, 'eval', 'results',
                        f'gate_phase_d_paired_{BASELINE_COMMIT}.json')
with open(_bl_path, encoding='utf-8') as fh:
    _bl = json.load(fh)
_bl_rows = _bl['v16_results']
_bl_inc = [r for r in _bl_rows if r['subdomain'] != 'out_of_corpus']
BASELINE = {
    'commit': BASELINE_COMMIT, 'utc': _bl.get('utc'), 'index_facts': _bl.get('index_facts'),
    'in_corpus_n': len(_bl_inc),
    'in_corpus_pass': sum(r['pass'] for r in _bl_inc),
    'in_corpus_raw': sum(r['pass'] for r in _bl_inc) / len(_bl_inc),
    'clarified': sum(r['clarified'] for r in _bl_inc),
    '_the_82_5_figure': ('330/400 = 82.5% was reported on 2026-10-08 as the baseline blend. It '
                         'includes the 16 out_of_corpus rows in BOTH numerator and denominator '
                         '(all 16 passed). The gate excludes OOC by design and R7 Gate 1 is an '
                         'IN-CORPUS bar, so the like-for-like baseline is '
                         f'{sum(r["pass"] for r in _bl_inc)}/{len(_bl_inc)} = '
                         f'{sum(r["pass"] for r in _bl_inc) / len(_bl_inc):.1%}.'),
    '_baseline_had_no_guards': ('D-FIDELITY-7 was NOT_WIRED and D-FIDELITY-8 did not exist at '
                                'this commit, so the baseline has NO guard interventions and '
                                'its A1 therefore includes every wrong answer the two guards '
                                'now catch. That is precisely the term the A1/A2 split exists '
                                'to expose.'),
}

print('\n' + '=' * 90)
print(f'BAR A — TWO NUMBERS AND A COUNT. NEVER A NET.   (gate {_sha}, '
      f'{EXPECTED_FACT_COUNT}-fact index)')
print('=' * 90)
BARS = {}
for name, bucket in BUCKETS.items():
    BARS[name] = {'raw': bars(bucket), 'reliable': bars(reliable_only(bucket))}
    b, l = BARS[name]['raw'], BARS[name]['reliable']
    print(f'\n{name}: n={len(bucket)}')
    print(f'   A2 RIGHT  {b["A2_right"]:3d}/{b["n_in_corpus"]:3d} = {b["A2_rate"]:6.1%}   '
          f'(reliable {l["A2_right"]}/{l["n_in_corpus"]} = {l["A2_rate"]:.1%})')
    print(f'   A1 WRONG  {b["A1_wrong"]:3d}/{b["n_in_corpus"]:3d} = {b["A1_rate"]:6.1%}   '
          f'(reliable {l["A1_wrong"]}/{l["n_in_corpus"]} = {l["A1_rate"]:.1%})')
    print(f'   NO ANSWER {b["no_answer"]:3d}/{b["n_in_corpus"]:3d} = '
          f'{b["no_answer_rate"]:6.1%}   errors={b["errors"]}')
    print(f'   GUARDS    {b["guard_rows"]} rows  {b["guard_by_name"]}  '
          f'x outcome {b["guard_x_outcome"]}')

_a = BARS['ALL_400']['raw']
print('\n' + '-' * 90)
print('AGAINST THE BASELINE — like for like, in-corpus, OOC excluded from both')
print('-' * 90)
print(f'  baseline {BASELINE["commit"]} ({BASELINE["utc"]}, {BASELINE["index_facts"]} facts): '
      f'{BASELINE["in_corpus_pass"]}/{BASELINE["in_corpus_n"]} = '
      f'{BASELINE["in_corpus_raw"]:.1%}')
print(f'  this run {_sha} ({EXPECTED_FACT_COUNT} facts):                 '
      f'{_a["A2_right"]}/{_a["n_in_corpus"]} = {_a["A2_rate"]:.1%}')
_a2_delta = (_a['A2_rate'] - BASELINE['in_corpus_raw']) * 100
# Baseline A1 = everything not passing and not clarified, computed the same way as this run's.
_bl_clar = sum(r['clarified'] for r in _bl_inc)
_bl_wrong = len(_bl_inc) - sum(r['pass'] for r in _bl_inc) - _bl_clar
_a1_delta = (_a['A1_rate'] - _bl_wrong / len(_bl_inc)) * 100
print(f'  A2 (right-answer rate) delta: {_a2_delta:+.1f} pts')
print(f'  A1 (wrong-answer rate) delta: {_a1_delta:+.1f} pts  '
      f'(baseline A1 = {_bl_wrong}/{len(_bl_inc)} = {_bl_wrong / len(_bl_inc):.1%})')

# ⛔ THE CONTAINMENT VERDICT, SPELLED OUT SO THE HEADLINE CANNOT BE MISREAD.
if _a1_delta < -0.5 and _a2_delta <= 0.5:
    READ = ('CONTAINMENT, NOT IMPROVEMENT. The wrong-answer rate fell and the right-answer '
            'rate did not rise. Confident wrong answers were converted into non-answers — the '
            'safe direction, and a real win on A1 — but the user is still owed those answers. '
            'Do NOT report this as an accuracy gain.')
elif _a2_delta > 0.5 and _a1_delta < -0.5:
    READ = ('BOTH BARS MOVED. A1 fell and A2 rose, so this is not containment alone — part of '
            'the A1 fall was converted into correct answers. Attribute the A2 rise to content '
            'or retrieval, NEVER to the guards: a guard cannot produce a right answer.')
elif _a2_delta > 0.5:
    READ = ('A2 ROSE WITH A1 ROUGHLY FLAT. The gain is content/retrieval-side; the guards did '
            'not contribute to it and should not be credited.')
elif _a2_delta < -0.5:
    READ = ('A2 FELL. Check the key-correction arm and the index change (217 -> 184) before '
            'concluding the system regressed — both are terms in this comparison and term (d) '
            'of the pre-registration is unsigned.')
else:
    READ = 'BOTH BARS ESSENTIALLY FLAT within half a point.'
print(f'\n  >>> HOW TO READ THIS: {READ}')

# ── KEY-CORRECTION ARM ───────────────────────────────────────────────────────────────────
print('\n' + '=' * 90)
print('KEY-CORRECTION ARM — the same generations, scored under the baseline keys')
print('=' * 90)
kc_rows = []
for r in rows:
    if r['pass_under_baseline_key'] is None:
        continue
    if r['pass_under_baseline_key'] != r['pass']:
        kc_rows.append(r)
    print(f"  {r['id']:10s} under baseline key={r['pass_under_baseline_key']!s:5s}  "
          f"under corrected key={r['pass']!s:5s}  "
          f"{'<-- MOVED BY THE KEY' if r['pass_under_baseline_key'] != r['pass'] else ''}")
_kc_delta = sum((1 if r['pass'] else 0) - (1 if r['pass_under_baseline_key'] else 0)
                for r in rows if r['pass_under_baseline_key'] is not None)
_kc_pts = _kc_delta / _a['n_in_corpus'] * 100 if _a['n_in_corpus'] else 0.0
print(f'\n  rows whose verdict the KEY alone moved: {len(kc_rows)} '
      f'{[r["id"] for r in kc_rows]}')
print(f'  net effect of key correction on A2: {_kc_delta:+d} rows = {_kc_pts:+.2f} pts')
print(f'  so MOVEMENT ATTRIBUTABLE TO THE SYSTEM = {_a2_delta:+.1f} - ({_kc_pts:+.2f}) = '
      f'{_a2_delta - _kc_pts:+.1f} pts')
print(f'\n  ⚠️ and {KEYCORR["scorer_blind_verdict_flips"]["ids"]} declared a verdict flip the '
      f'regex scorer CANNOT see, so its key-correction effect is 0 by construction and only '
      f'the judge can price it.')

# ── COVERAGE LEDGER: WHAT THE ARM DOES *NOT* REACH, NAMED ROW BY ROW ─────────────────────
# ⛔ THIS ARM IS NARROWER THAN THE FOUR THINGS IT WAS ASKED TO COVER, AND THE REASON IS
# DIFFERENT IN EVERY CASE. An arm that silently covers two of four reports a cleaner result
# than it earned — the same defect as a census that omits what it could not test. Each item
# was re-derived from the artifact, not from the request or from a write-up.
KEY_CORRECTION_COVERAGE = [
    {'item': 'eval_383', 'in_the_400': True, 'dual_scored': True,
     'why': 'TZS 300,000 -> 500,000, a genuine narrowing of a row in gate_001. AND THE '
            'CORRECTION WAS HALF-APPLIED UNTIL TODAY: score_question UNIONS the SW and EN '
            'numeric keys, so correct_answer_en left at 300,000 made the "corrected" key '
            'accept BOTH figures — the opposite of a correction, and it could never have '
            'shown a delta. R36 in the gold layer: the fix fired one field short of the '
            'bytes that are read.'},
    {'item': 'eval_355', 'in_the_400': True, 'dual_scored': True,
     'why': 'the second and only other row of the 400 whose key actually narrows. Not named '
            'in the request; included because the derivation found it.'},
    {'item': 'eval_331', 'in_the_400': True, 'dual_scored': False,
     'why': 'declared verdict flip (No -> Yes) that _yn_polarity cannot read — `hulazimiki` '
            'is absent from _YN_NEG, so it fell through to the affirmative default. Its '
            'regex delta is 0 BY CONSTRUCTION, which is worse than a measured delta because '
            'it looks like no change. Only the judge can price it.'},
    {'item': 'ext_15', 'in_the_400': False, 'dual_scored': False,
     'why': 'RE_RUN_REQUIRED, and its key changed TWICE (citation 2026-10-05, figure USD 25 '
            '-> TZS 70,000 on 2026-10-06). But it lives in '
            'eval/accuracy_gate/edge_probe_extended_078_DRAFT.jsonl, which is NOT part of '
            'these 400 and was never scored at 1476caa — so there is no baseline verdict to '
            'take a delta against. It also carries no `correct_answer_sw`/`answer_type`: its '
            'gold is `expected_behavior` PROSE, which score_question cannot score at all. '
            'Re-running it is an ADJUDICATION job (as on 2026-09-23), not a regex gate arm, '
            'and bolting a differently-shaped corpus onto this headline would corrupt it. '
            'OWED, and owed separately — its own note refuses desk re-labelling.'},
    {'item': 'ext_56', 'in_the_400': False, 'dual_scored': False,
     'why': '⚠️ NOT A KEY-CORRECTION ROW. It carries no `_scoring_key_correction` of any '
            'kind; the 2026-09-23 adjudication records it as verdict=WRONG, cause=MODEL '
            '("confirms the false premise" — 110M over six months DOES exceed the 100M/'
            '6-month threshold). Nothing about its gold changed, so there is no old key and '
            'nothing to dual-score. Listing it as a corrected row would have manufactured a '
            'key-correction term out of a model defect.'},
    {'item': 'the 41 sourced of 73 uncited gold answers', 'in_the_400': None,
     'dual_scored': False,
     'why': 'gold_provenance_backfill_pass1.json is mode=REPORT_ONLY and says so in its own '
            'header: "Changes no gold answer." It ATTACHED a source-register key to 41 rows '
            'and left 32 pending (41 + 32 = 73, re-derived). A provenance attachment moves '
            'no score, so the key-correction delta from all 41 is exactly ZERO — not small, '
            'zero, by construction. ⛔ THE LIVE PART IS ELSEWHERE IN THAT FILE: 4 '
            '`disagreements_reported_not_changed`. Those are gold answers that disagree with '
            'a primary source and were deliberately NOT edited, so they are candidate wrong '
            'keys still scoring rows today — and a wrong key is booked as a model failure '
            'forever, because the adjudication reads the key.'},
]
print('\n  ' + '-' * 86)
print('  COVERAGE LEDGER — what this arm reaches, and what it does not')
print('  ' + '-' * 86)
for c in KEY_CORRECTION_COVERAGE:
    print(f"  {'[DUAL-SCORED]' if c['dual_scored'] else '[NOT REACHED]'} {c['item']}")
    print(f"      {c['why']}")
print(f"\n  SO: {sum(1 for c in KEY_CORRECTION_COVERAGE if c['dual_scored'])} of "
      f"{len(KEY_CORRECTION_COVERAGE)} items are inside the measured delta. The other "
      f"{sum(1 for c in KEY_CORRECTION_COVERAGE if not c['dual_scored'])} are each zero or "
      f"unmeasurable FOR A STATED REASON, and two of them (ext_15's re-run, the 4 reported "
      f"disagreements) are work this run does not do.")

# ── THE ROW TO WATCH ─────────────────────────────────────────────────────────────────────
print('\n' + '-' * 90)
print('THE PRE-REGISTERED ROW TO WATCH — eval_347')
print('-' * 90)
_e347 = next((r for r in rows if r['id'] == 'eval_347'), None)
if _e347:
    _g = [g['guard'] for g in _e347['guard_interventions']]
    print(f'  outcome={outcome(_e347)}  guards={_g}  pass={_e347["pass"]}')
    print(f'  reply: {_e347["generated"][:300]}')
    if _e347['raw_generated'] and _e347['guard_interventions']:
        print(f'  PRE-GUARD body: {_e347["guard_interventions"][0]["pre_guard_body"][:300]}')
    if 'D-FIDELITY-7' in _g:
        print('  >>> AS PRE-REGISTERED: the guard withheld the fabricated threshold. This is a '
              'FAIL THAT IS A WIN — A1 moved, A2 did not, and the answer is still owed.')
    # ⛔ POLARITY HERE TOO, AND IT MATTERS MORE THAN IN THE PRE-FLIGHT. The CORRECT answer to
    # this question contains the figure: row 57 serves "...hakuna kizingiti ... Na SI TZS
    # 11,000,000", so a model that repeats its own index row faithfully would have been
    # declared THE FINDING OF THE RUN. That is R34's shape — a confident wrong verdict from a
    # pattern, in the one line of output most likely to be quoted — and a false accusation is
    # the expensive direction, because only a false positive generates an edit, and the edit
    # would land in a guard that works.
    elif any(asserts_value(_e347['generated'], t)
             for t in ('TZS 11,000,000', '11,000,000', 'milioni 11')):
        print('  >>> ⛔ THE FINDING OF THE RUN: the fabricated threshold is STILL SERVED, '
              'ASSERTED and not under a negation. D-FIDELITY-7 is not reaching the fact path '
              'in this configuration.')
    elif any(_SWEEP._mentioned(_e347['generated'], t)
             for t in ('TZS 11,000,000', '11,000,000', 'milioni 11')):
        print('  >>> the figure appears but ONLY UNDER A NEGATION — the reply is denying the '
              'fabrication, which is what row 57 now says. Read it before calling it either '
              'way: this is the shape of a CORRECT answer, not of the defect.')
    else:
        print('  >>> neither: no guard fired and the fabrication is absent. Read the reply '
              'before concluding anything — the row may have been answered correctly.')

# ── JUDGE OVERLAY ────────────────────────────────────────────────────────────────────────
judge_overlay = None
if RUN_JUDGE:
    from concurrent.futures import ThreadPoolExecutor
    gradeable = chike_judge.judge_gradeable(rows)
    print('\n' + '=' * 90)
    print(f'JUDGE OVERLAY — majority-of-{chike_judge.DEFAULT_N}, pinned '
          f'{chike_judge.DEFAULT_PROVIDER}, grading {len(gradeable)} rows')
    print('=' * 90)
    _tj = time.time()

    def _one(r):
        return r['id'], chike_judge.judge_majority(
            r['question_sw'], r.get('correct_answer_sw', ''),
            chike_judge.clean_for_judge(r['generated']), api_key=OR_KEY)

    jrows, n = {}, 0
    with ThreadPoolExecutor(max_workers=8) as ex:
        for qid, v in ex.map(_one, gradeable):
            jrows[qid] = v
            n += 1
            if n % 50 == 0:
                print(f'   ...{n}/{len(gradeable)} ({time.time() - _tj:.0f}s)', flush=True)
    for r in rows:
        r['judge'] = jrows[r['id']]['verdict'] if r['id'] in jrows else None
    rep = chike_judge.build_confirmation_report(rows)
    cost = (sum(v['pin'] for v in jrows.values()) * chike_judge.PRICE_IN
            + sum(v['pout'] for v in jrows.values()) * chike_judge.PRICE_OUT)
    judge_overlay = {
        'report': rep, 'graded': len(gradeable),
        'providers': sorted({p for v in jrows.values() for p in v['providers']}),
        'usd': round(cost, 4), 'api_errors': sum(v['err_count'] for v in jrows.values()),
        'per_id': {k: {'verdict': v['verdict'], 'votes': v['votes'], 'tie': v['tie']}
                   for k, v in jrows.items()},
        'caveat': ('report-alongside only: the judge fills the reliable=False gap and FLAGS '
                   'disagreements on the reliable=True set, but never flips a confident regex '
                   'verdict and does not drive GATE PASSED.'),
    }
    print(f'  raw {rep["raw"]["acc"]:.1%} | reliable-denom {rep["reliable_denom"]["acc"]:.1%} '
          f'| JUDGE-AUGMENTED {rep["judge_augmented"]["acc"]:.1%}')
    dq = rep['disagreement_queue']
    print(f'  disagreement queue: {len(dq["false_pass_candidates"])} false-pass, '
          f'{len(dq["false_fail_candidates"])} false-fail (candidates, NOT applied)')
    print(f'  ~USD {cost:.4f}  wall {time.time() - _tj:.0f}s')
    # ⛔ THE JUDGE IS THE ONLY INSTRUMENT THAT CAN PRICE THE SCORER-BLIND ROWS. Report them
    # explicitly rather than leaving them inside an aggregate.
    for qid in KEYCORR['scorer_blind_verdict_flips']['ids']:
        jv = jrows.get(qid, {}).get('verdict')
        print(f'  scorer-blind row {qid}: judge says {jv!r} (the regex scorer cannot see this '
              f'row\'s verdict flip at all)')
else:
    print('\n[judge] SKIPPED — the headline below is NOT trustworthy on its own.')

# ── R7 ───────────────────────────────────────────────────────────────────────────────────
IN_THR = CONFIG['gate_thresholds']['in_corpus']
_fp = BARS['fact_path_190']['raw']
print('\n' + '=' * 90)
print(f'R7 GATE 1 — in-corpus accuracy, threshold {IN_THR:.0%}')
print('=' * 90)
print(f'  ALL_400 in-corpus A2        {_a["A2_rate"]:.1%}  '
      f'-> {"PASS" if _a["A2_rate"] > IN_THR else "BELOW"}')
print(f'  fact_path_190 A2 (raw)      {_fp["A2_rate"]:.1%}  '
      f'-> {"PASS" if _fp["A2_rate"] > IN_THR else "BELOW"}')
print(f'  fact_path_190 A2 (reliable) {BARS["fact_path_190"]["reliable"]["A2_rate"]:.1%}')
print('  NOTE: Gate 2 (refusal, >70%) is NOT measured by this run. R7 requires BOTH gates '
      'simultaneously, so no part of this output is a Gate-2 result and none of it should be '
      'quoted as pilot readiness on its own.')

summary = {
    'gate_commit': _sha, 'github_head': _live, 'index_facts': EXPECTED_FACT_COUNT,
    'adapter': ADAPTER, 'config_version': CONFIG.get('version'),
    'serving_identity': serving,
    'baseline': BASELINE,
    'bars': BARS,
    'deltas_vs_baseline': {
        'A2_pts': round(_a2_delta, 2), 'A1_pts': round(_a1_delta, 2),
        'key_correction_rows': _kc_delta, 'key_correction_pts': round(_kc_pts, 2),
        'A2_attributable_to_system_pts': round(_a2_delta - _kc_pts, 2),
        'how_to_read': READ,
        '_never_net_A1_and_A2': ('A falling A1 with a flat A2 is containment. A guard stops a '
                                 'wrong answer; it cannot produce a right one. Reporting one '
                                 'blended figure makes both the win and the debt invisible.'),
    },
    'key_correction_detail': [{'id': r['id'], 'baseline_key': r['pass_under_baseline_key'],
                               'corrected_key': r['pass']}
                              for r in rows if r['pass_under_baseline_key'] is not None],
    'scorer_blind_flips': KEYCORR['scorer_blind_verdict_flips'],
    # The ledger ships INSIDE the artifact, not only in the console. A caveat quoted away from
    # its number stops travelling with it; same reason ab_retriever_full.py carries
    # `why_each_population` in its own payload.
    'key_correction_coverage': KEY_CORRECTION_COVERAGE,
    'guard_rows': [{'id': r['id'], 'outcome': outcome(r),
                    'guards': [g['guard'] for g in r['guard_interventions']],
                    'pre_guard_body': r['guard_interventions'][0]['pre_guard_body']}
                   for r in rows if r['guard_interventions']],
    'errors': [{'id': r['id'], 'error': r['error']} for r in rows if r['error']],
    'r7_gate_1': {'threshold': IN_THR,
                  'all_400_in_corpus_A2': _a['A2_rate'],
                  'fact_path_190_A2': _fp['A2_rate'],
                  'gate_2_measured': False,
                  'note': 'R7 needs BOTH gates. Gate 2 is not in this run.'},
    'judge_overlay': judge_overlay,
    'judge_overlay_status': ('ran' if RUN_JUDGE else 'SKIPPED — headline not trustworthy alone'),
    'pre_registration': {
        '_recorded': 'committed in this file and in '
                     'eval/results/gate_preregistration_2026_10_09.json BEFORE the run',
        'point_estimate_in_corpus_raw': 0.825,
        'terms': {'key_correction_pts': -0.52, 'corrected_facts_pts': +1.25,
                  'guards': 'A1 down, A2 unchanged',
                  'index_217_to_184': 'UNBOUNDED AND UNSIGNED — the largest term'},
        'row_to_watch': 'eval_347',
    },
}
_publish(_flush(rows, summary=summary, judge_overlay=judge_overlay), complete=True)

print('\n\n' + '#' * 90)
print('### FULL GATE SUMMARY — PASTE EVERYTHING BETWEEN THE # LINES ###')
print('#' * 90)
print(json.dumps(summary, ensure_ascii=False, indent=1))
print('#' * 90)
print('### END SUMMARY ###')
print('#' * 90)
print(f'\n[done] HF: {DATASET_REPO}/{ARTIFACT_NAME}  (fetch THIS, not the paste)')
print('GATE_PRODUCTION_DONE')
