# -*- coding: utf-8 -*-
"""R16 VERIFICATION: point production at a BAD INDEX and confirm it refuses to serve.

WHY A SCRIPT AND NOT A FEW COMMANDS. This deliberately breaks production, which means the
restore must not depend on me remembering to run it. Everything after the bad deploy is inside
`try/finally`: the config is restored and redeployed even if the probe raises, the network drops,
or the run is interrupted. R16's own worst incident was a window where production was DEAD because
a replacing deploy failed — so the replacing deploy is the finally-block, not a later step.

WHAT IS BEING VERIFIED, precisely. `chike-inference` now loads its RAG index through
`chike.retrieval.Retriever(..., expected_fact_count=CONFIG['rag_fact_count']).preflight()`, which
raises on three defects: missing files, `n_embeddings != n_texts`, and a count that does not match
the deploy's expectation. Before 2026-08-24 the container printed a warning, set `fact_texts = []`
and answered every compliance question with **no facts at all**.

The limb forced here is the COUNT limb: set `rag_fact_count` to a value the baked index does not
have. That exercises the same code path as the other two — preflight -> RetrievalIndexError ->
re-raise inside `@modal.enter()` — and it is the only limb that can be forced without rebuilding
the image around a corrupt file. **Stated rather than glossed: the missing-file and shape limbs are
covered by tests/test_modal_index_contract.py, not by this live run.**

THE PASS CONDITION IS A FAILURE. A request must come back as an ERROR. If it comes back 200 with a
fluent Swahili answer, the contract is still not protecting production and the whole point of
wiring it was missed — a factless answer is exactly the outcome the contract exists to prevent, and
it is indistinguishable from a good one to a user.

R16 step 3 (the negative case) is the restore arm: after putting the count back, a normal question
must answer correctly again. A change that only proves the new behaviour can be silently
over-broad.

R18: committed before it runs.
Artifact: eval/results/index_contract_live_verification.json
"""
import json
import os
import subprocess
import sys
import time
import urllib.parse
import urllib.request

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
CONFIG = os.path.join(REPO, 'kaggle', 'chike_config.json')
OUT = os.path.join(REPO, 'eval', 'results', 'index_contract_live_verification.json')
ENDPOINT = 'https://prosperpiusmbaruku007--chike-inference-web-endpoint.modal.run'
PROBE = 'SDL ni asilimia ngapi kwa kampuni yenye wafanyakazi 12?'
BAD_COUNT = 999          # the baked index has 187 rows (R15 regen #2, 2026-08-26)

ENV = dict(os.environ, PYTHONIOENCODING='utf-8', PYTHONUTF8='1')
LOG = []


def say(msg):
    print(msg, flush=True)
    LOG.append(msg)


def token():
    p = os.path.expanduser('~/.chike_modal_token.txt')
    return (os.environ.get('CHIKE_MODAL_TOKEN')
            or (open(p, encoding='utf-8').read().strip() if os.path.exists(p) else ''))


def redeploy(label):
    """R16: warm containers serve OLD code, so stop first. PYTHONIOENCODING is not optional —
    a cp1252 console once aborted a deploy on the CLI's own check-mark glyph and left BOTH app
    records stopped."""
    say(f'[{label}] modal app stop chike-inference --yes')
    subprocess.run([sys.executable, '-m', 'modal', 'app', 'stop', 'chike-inference', '--yes'],
                   env=ENV, capture_output=True, text=True, timeout=300)
    say(f'[{label}] modal deploy')
    p = subprocess.run([sys.executable, '-m', 'modal', 'deploy',
                        os.path.join(REPO, 'chike-inference', 'modal_app.py')],
                       env=ENV, capture_output=True, text=True, timeout=900,
                       encoding='utf-8', errors='replace')
    ok = p.returncode == 0
    say(f'[{label}] deploy rc={p.returncode}')
    if not ok:
        say((p.stdout or '')[-800:] + (p.stderr or '')[-800:])
    return ok


def probe():
    url = f'{ENDPOINT}?token={urllib.parse.quote(token())}'
    req = urllib.request.Request(url, data=json.dumps({'message': PROBE}).encode(),
                                 headers={'Content-Type': 'application/json'})
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=900) as r:
            body = r.read().decode('utf-8', 'replace')
            return {'outcome': 'HTTP_200', 'status': r.status, 'body': body[:900],
                    'elapsed_s': round(time.time() - t0, 1)}
    except Exception as exc:
        return {'outcome': 'ERROR', 'status': None,
                'body': f'{type(exc).__name__}: {str(exc)[:600]}',
                'elapsed_s': round(time.time() - t0, 1)}


def set_count(n):
    with open(CONFIG, encoding='utf-8') as f:
        cfg = json.load(f)
    was = cfg.get('rag_fact_count')
    cfg['rag_fact_count'] = n
    with open(CONFIG, 'w', encoding='utf-8') as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)
        f.write('\n')
    say(f'[config] rag_fact_count {was} -> {n}')
    return was


def flush(blob):
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(blob, f, ensure_ascii=False, indent=2)


def main():
    with open(CONFIG, encoding='utf-8') as f:
        good = json.load(f)['rag_fact_count']
    assert isinstance(good, int) and good > 0, 'config has no usable rag_fact_count to restore'

    blob = {'verified': '2026-08-24',
            'harness': 'eval/controls/verify_index_contract_live.py',
            'target': 'chike-inference (production)',
            'limb_forced': 'expected_fact_count mismatch',
            'limbs_not_forced_here': ['missing index files', 'n_embeddings != n_texts'],
            'good_count': good, 'bad_count': BAD_COUNT,
            'arms': {}, 'log': LOG}
    flush(blob)

    try:
        # ---- ARM 1: BAD INDEX EXPECTATION. Production must REFUSE TO SERVE. ------------------
        set_count(BAD_COUNT)
        deployed = redeploy('BAD')
        blob['arms']['bad'] = {'deploy_ok': deployed}
        flush(blob)
        if deployed:
            say('[BAD] probing — a 200 with a fluent answer here means the contract is NOT '
                'protecting production')
            r = probe()
            blob['arms']['bad']['probe'] = r
            blob['arms']['bad']['verdict'] = (
                'REFUSED (correct)' if r['outcome'] == 'ERROR'
                else 'SERVED ANYWAY — CONTRACT NOT PROTECTING PRODUCTION')
            say(f"[BAD] {r['outcome']} in {r['elapsed_s']}s :: {r['body'][:200]}")
            flush(blob)
    finally:
        # ---- ALWAYS: restore, redeploy, and prove it answers again (R16 negative case) -------
        set_count(good)
        restored = redeploy('RESTORE')
        blob.setdefault('arms', {})['restore'] = {'deploy_ok': restored}
        flush(blob)
        if restored:
            r = probe()
            blob['arms']['restore']['probe'] = r
            blob['arms']['restore']['verdict'] = (
                'ANSWERS AGAIN (correct)' if r['outcome'] == 'HTTP_200'
                else 'STILL DOWN AFTER RESTORE — INVESTIGATE NOW')
            say(f"[RESTORE] {r['outcome']} in {r['elapsed_s']}s :: {r['body'][:200]}")
        with open(CONFIG, encoding='utf-8') as f:
            blob['config_rag_fact_count_after'] = json.load(f)['rag_fact_count']
        blob['status'] = 'COMPLETE'
        flush(blob)
        say(f'[saved] {OUT}')


if __name__ == '__main__':
    main()
