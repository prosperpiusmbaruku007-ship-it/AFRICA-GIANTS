import json, os, subprocess, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
base = json.load(open(os.path.join(REPO, 'chike-whatsapp', 'deploy_tunables.json'), encoding='utf-8'))
S = os.path.join(REPO, 'scratch', 'pf')
os.makedirs(S, exist_ok=True)


def plant(name, mutate):
    d = dict(base)
    mutate(d)
    p = os.path.join(S, name + '.json')
    json.dump(d, open(p, 'w', encoding='utf-8'))
    return p


RUNS = [
    ('A_clean', [], {}),
    ('B_shell_changed_COHORT_SIZE_3', [], {'COHORT_SIZE': '3'}),
    ('C_file_missing_MAX_RENOTIFIES', ['--tunables-file', plant('missing', lambda d: d.pop('MAX_RENOTIFIES'))], {}),
    ('D_file_changed_RENOTIFY_600', ['--tunables-file', plant('changed', lambda d: d.update(RENOTIFY_AFTER_S='600'))], {}),
    ('E_same_with_override', ['--tunables-file', os.path.join(S, 'changed.json')], {'CHIKE_TUNABLES_OVERRIDE': 'plant: moving re-notify to 10 minutes'}),
    ('F_autosend_off_even_with_override', ['--tunables-file', plant('off', lambda d: d.update(AUTOSEND_ENGINE='0'))],
     {'CHIKE_TUNABLES_OVERRIDE': 'plant: turning auto-send off'}),
]
out = {}
for name, args, env in RUNS:
    e = dict(os.environ, PYTHONIOENCODING='utf-8', PYTHONUTF8='1', **env)
    for k in ('CHIKE_TUNABLES_OVERRIDE',):
        if k not in env:
            e.pop(k, None)
    p = subprocess.run([sys.executable, 'scripts/preflight_deploy.py', 'chike-whatsapp/modal_whatsapp.py'] + args, cwd=REPO,
                       capture_output=True, text=True, encoding='utf-8', errors='replace', env=e)
    out[name] = {'rc': p.returncode, 'out': p.stdout[-2600:]}
    json.dump(out, open(os.path.join(REPO, 'scratch', 'pf_plants.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(name, 'rc=', p.returncode, flush=True)
print('ALLDONE', flush=True)
