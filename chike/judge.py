"""chike/judge.py — frontier LLM-as-judge scoring OVERLAY (eval-only).

Follow-up #3, work item 5 (integration). This module is the item-4 non-determinism
design made reusable, plus the item-5 confirmation-overlay aggregation:

  * item 4  — pinned provider (DeepInfra, seed=42, allow_fallbacks:false) + MAJORITY-OF-5
              voting (a tie -> `undetermined`). Pinning alone cut flips 4/14 -> 1/14 at 14
              examples but left 2 correct<->wrong flips at scale on the 39 census IDs;
              majority-of-5 is robust to both 5-1 and 4-2 splits (proof in PROGRESS.md).
  * item 5  — the judge is a CONSERVATIVE, ASYMMETRIC overlay on chike.scoring:
                - FILLS the reliable=False gap (regex explicitly abstained there),
                - FLAGS (never silently flips) disagreements on the reliable=True set,
              producing a third "judge-augmented" accuracy alongside raw + reliable-denom.

IMPORTANT — NOT production serving logic. This is a scorer overlay, exactly like
chike.scoring.scorer_reliability. It never runs on the modal_app.py serving path, so it is
EXEMPT from the modal_app.py<->eval.py dual-file-sync rule (that rule governs serving logic:
decompose / RAG / post-generation cleanup). The judge NEVER overrides a confident regex
verdict in the live GATE PASSED number; eval.py's pass/fail trigger is unchanged.

Leaf module: stdlib + `requests` only, no chike-internal imports, so it works both as a
normal import (Kaggle clone) and via fetch-and-exec.
"""
import json
import re
import time
from collections import Counter

# ── judge model + pinning (item-4 Option A) ──────────────────────────────────────
DEFAULT_MODEL = 'qwen/qwen3-32b'      # dense 32B, Qwen3 covers 119 languages incl. Swahili
DEFAULT_PROVIDER = 'DeepInfra'        # single backend provider — kills OpenRouter cross-provider routing
DEFAULT_SEED = 42
DEFAULT_N = 5                         # majority-of-5 (item-4: robust to 5-1 AND 4-2 splits)
PRICE_IN = 0.00000008                # USD/token (OpenRouter listing, prompt)
PRICE_OUT = 0.00000028               # USD/token (OpenRouter listing, completion)
VALID_VERDICTS = ('correct', 'wrong', 'undetermined')

JUDGE_SYS = (
    "You are a bilingual Kiswahili/English compliance-answer grader for Tanzanian tax, "
    "labour and business-registration questions. You are given a QUESTION, a REFERENCE "
    "answer known to be correct, and a GENERATED answer to grade. Decide whether the "
    "GENERATED answer is substantively correct RELATIVE TO THE REFERENCE: it must agree on "
    "the key fact, figure, polarity (yes/no) or refusal. Extra wording, code-switching or "
    "phrasing differences do NOT make it wrong. A directly contradicting figure, a flipped "
    "yes/no, or a confidently wrong claim IS wrong. If the generated answer is too vague or "
    "off-topic to tell, use undetermined. Judge meaning, not surface form. Answer in the "
    "language you like but keep the justification to ONE sentence."
)


def clean_for_judge(g):
    """The same ramble-strip the census/NLI harnesses use, for parity of the graded text."""
    g = g or ''
    for mk in ['\nuser', 'user_0', 'user ', '\n\n']:
        i = g.find(mk)
        if i > 40:
            g = g[:i]
    m = re.search(r'[Tt]hibitisha na[^)]*\)', g)
    if m:
        g = g[:m.end()]
    return g.strip()


def build_user_prompt(question, ref, gen):
    return (
        f"SWALI (question):\n{question}\n\n"
        f"JIBU SAHIHI LA RUFAA (reference correct answer):\n{ref}\n\n"
        f"JIBU LILILOTOLEWA (generated answer to grade):\n{gen}\n\n"
        'Return ONLY a JSON object, no other text:\n'
        '{"verdict": "correct" | "wrong" | "undetermined", "justification": "<one sentence>"}'
    )


def parse_verdict(msg):
    """Parse a judge reply into (verdict, justification). Identical fallback ladder to
    kaggle/judge_regression.py: prefer a strict {..."verdict"...} JSON object, then fall
    back to substring detection. Pure — unit-tested without the network."""
    verdict, just = 'undetermined', ''
    msg = msg or ''
    mm = re.search(r'\{[^{}]*"verdict"[^{}]*\}', msg, re.S)
    if mm:
        try:
            o = json.loads(mm.group(0))
            verdict = str(o.get('verdict', 'undetermined')).lower().strip()
            just = str(o.get('justification', ''))[:200]
        except Exception:
            pass
    if verdict not in VALID_VERDICTS:
        lm = msg.lower()
        verdict = ('wrong' if 'wrong' in lm else 'correct' if 'correct' in lm else 'undetermined')
    return verdict, just


def majority_vote(verdicts):
    """(item-4) Reduce N per-call verdicts to one. A STRICT plurality wins; any tie for the
    top spot -> 'undetermined' (an honest judge coin-flip must not silently pass/fail). With
    n=5 and two categories no tie is possible; a 3-way 2-2-1 splits to undetermined. Pure."""
    c = Counter(v for v in verdicts if v in VALID_VERDICTS)
    top = c.most_common()
    if not top:
        return 'undetermined', True, {}
    if len(top) > 1 and top[0][1] == top[1][1]:
        return 'undetermined', True, dict(c)     # tie -> undetermined
    return top[0][0], False, dict(c)


def judge_once(question, ref, gen, *, api_key, model=DEFAULT_MODEL, provider=DEFAULT_PROVIDER,
               seed=DEFAULT_SEED, timeout=120, retries=3, _requests=None):
    """One PINNED judge call. Returns a dict with verdict / justification / provider served /
    token usage / latency / err. `_requests` is injectable for testing."""
    requests = _requests
    if requests is None:
        import requests  # local import so the module loads without the dep present
    body = {'model': model, 'temperature': 0, 'max_tokens': 400,
            'reasoning': {'enabled': False}, 'seed': seed,
            'provider': {'order': [provider], 'allow_fallbacks': False},
            'messages': [{'role': 'system', 'content': JUDGE_SYS},
                         {'role': 'user', 'content': build_user_prompt(question, ref, gen)}]}
    t = time.time()
    verdict, just, prov, pin, pout, err = 'undetermined', '', '?', 0, 0, ''
    for attempt in range(retries):
        try:
            resp = requests.post('https://openrouter.ai/api/v1/chat/completions',
                                 headers={'Authorization': 'Bearer ' + api_key,
                                          'Content-Type': 'application/json'},
                                 json=body, timeout=timeout)
            j = resp.json()
            if 'choices' not in j:
                err = str(j.get('error', j))[:160]
                time.sleep(2 + attempt * 3); continue
            prov = j.get('provider', '?')
            u = j.get('usage', {}) or {}
            pin, pout = u.get('prompt_tokens', 0), u.get('completion_tokens', 0)
            verdict, just = parse_verdict(j['choices'][0]['message']['content'])
            err = ''
            break
        except Exception as e:
            err = f'{type(e).__name__}: {e}'[:160]
            time.sleep(2 + attempt * 3)
    return {'verdict': verdict, 'justification': just, 'provider': prov,
            'pin': pin, 'pout': pout, 'dt': round(time.time() - t, 2), 'err': err}


def judge_majority(question, ref, gen, *, api_key, n=DEFAULT_N, model=DEFAULT_MODEL,
                   provider=DEFAULT_PROVIDER, seed=DEFAULT_SEED, timeout=120, _requests=None):
    """(item-4) N pinned calls -> one majority verdict. Verifies the pin held (providers set)
    and keeps a majority-aligned justification. Returns the aggregate record."""
    calls = [judge_once(question, ref, gen, api_key=api_key, model=model, provider=provider,
                        seed=seed, timeout=timeout, _requests=_requests) for _ in range(n)]
    verdicts = [c['verdict'] for c in calls]
    verdict, tie, votes = majority_vote(verdicts)
    just = next((c['justification'] for c in calls if c['verdict'] == verdict), calls[0]['justification'])
    return {'verdict': verdict, 'tie': tie, 'votes': votes, 'n': n,
            'justification': just,
            'providers': sorted({c['provider'] for c in calls}),
            'pin': sum(c['pin'] for c in calls), 'pout': sum(c['pout'] for c in calls),
            'err_count': sum(1 for c in calls if c['err']),
            'per_call': verdicts}


# ── item-5 CONFIRMATION-OVERLAY aggregation (pure; no network) ────────────────────
# Rows are the eval_orchestrator_combined.py result dicts. Required keys:
#   id, subdomain, pass (regex bool), reliable (bool), clarified (bool)
# plus 'judge' (the majority verdict string) attached by the judge pass.

def _incorpus(rows):
    return [r for r in rows if r.get('subdomain') != 'out_of_corpus']


def judge_gradeable(rows):
    """The rows the judge should grade: in-corpus, not a deliberate clarification. A
    clarification is a never-guess by design — grading it against a factual gold would
    penalise correct refusal behaviour (the census excluded its 30 clarified rows for the
    same reason). Refusals (out_of_corpus) live on the separate refusal gate."""
    return [r for r in _incorpus(rows) if not r.get('clarified')]


def build_confirmation_report(rows):
    """Turn judged rows into the three side-by-side numbers + the disagreement queue.

    The judge NEVER flips a confident regex verdict here:
      * reliable=True  -> judge is CONFIRMATION only. Disagreements are queued
        (false_pass = regex PASS + judge WRONG; false_fail = regex FAIL + judge CORRECT),
        NOT applied to any number.
      * reliable=False -> judge FILLS the gap the regex scorer abstained on:
        correct->pass, wrong->fail, undetermined-> still excluded (+ a conservative
        undet=fail floor is also reported to bracket the true accuracy).
    Every row here has been through judge_gradeable(), so clarifications are already out.
    """
    inc = _incorpus(rows)
    rel = [r for r in inc if r.get('reliable')]
    gap = [r for r in inc if not r.get('reliable') and not r.get('clarified')]

    raw_pass, raw_tot = sum(bool(r['pass']) for r in inc), len(inc)
    rel_pass, rel_tot = sum(bool(r['pass']) for r in rel), len(rel)

    gc = [r for r in gap if r.get('judge') == 'correct']
    gw = [r for r in gap if r.get('judge') == 'wrong']
    gu = [r for r in gap if r.get('judge') not in ('correct', 'wrong')]   # undetermined/None

    aug_pass = rel_pass + len(gc)
    aug_tot = rel_tot + len(gc) + len(gw)                 # undetermined excluded
    aug_tot_floor = rel_tot + len(gap)                    # conservative: undet counts as fail

    # disagreement queue on the confident (reliable=True) set — flags, never auto-applied
    false_pass = [r['id'] for r in rel if r['pass'] and r.get('judge') == 'wrong']
    false_fail = [r['id'] for r in rel if not r['pass'] and r.get('judge') == 'correct']

    def acc(p, t):
        return (p / t) if t else 0.0

    return {
        'raw':             {'pass': raw_pass, 'total': raw_tot, 'acc': acc(raw_pass, raw_tot)},
        'reliable_denom':  {'pass': rel_pass, 'total': rel_tot, 'acc': acc(rel_pass, rel_tot)},
        'judge_augmented': {'pass': aug_pass, 'total': aug_tot, 'acc': acc(aug_pass, aug_tot),
                            'floor_undet_fail': {'pass': aug_pass, 'total': aug_tot_floor,
                                                 'acc': acc(aug_pass, aug_tot_floor)}},
        'gap_fill': {'gap_n': len(gap), 'judge_correct': len(gc), 'judge_wrong': len(gw),
                     'judge_undetermined': len(gu),
                     'correct_ids': [r['id'] for r in gc], 'wrong_ids': [r['id'] for r in gw],
                     'undetermined_ids': [r['id'] for r in gu]},
        'disagreement_queue': {'false_pass_candidates': sorted(false_pass),
                               'false_fail_candidates': sorted(false_fail),
                               'note': 'CANDIDATES to adjudicate (work item 2), NOT corrections. '
                                       'The judge is not ground truth; it never auto-flips a '
                                       'reliable=True regex verdict.'},
    }
