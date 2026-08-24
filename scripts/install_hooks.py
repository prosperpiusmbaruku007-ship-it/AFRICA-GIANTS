#!/usr/bin/env python3
"""Point git at the versioned hooks in .githooks/ so the pre-push gate is active.

Hooks in .git/hooks are not version-controlled, so a hook committed there protects nobody but
the machine it was written on. `core.hooksPath` makes the repo's own .githooks/ authoritative,
which means the gate travels with a clone.

Run once per clone:  python scripts/install_hooks.py
"""
import os
import subprocess
import sys


def main():
    repo = subprocess.run(['git', 'rev-parse', '--show-toplevel'],
                          capture_output=True, text=True, check=True).stdout.strip()
    hooks = os.path.join(repo, '.githooks')
    if not os.path.isdir(hooks):
        print(f'ERROR: {hooks} does not exist')
        return 1
    subprocess.run(['git', 'config', 'core.hooksPath', '.githooks'], cwd=repo, check=True)
    current = subprocess.run(['git', 'config', '--get', 'core.hooksPath'],
                             cwd=repo, capture_output=True, text=True).stdout.strip()
    print(f'core.hooksPath = {current}')
    hook = os.path.join(hooks, 'pre-push')
    print(f'pre-push present: {os.path.isfile(hook)}')
    print('The push gate is active. Bypass with CHIKE_SKIP_PREPUSH=1 only when the suite '
          'cannot run at all.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
