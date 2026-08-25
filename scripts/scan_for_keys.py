#!/usr/bin/env python3
"""
GIT-PUSH-GUARD — scan staged and/or modified files for API key patterns.
Usage:
  python scripts/scan_for_keys.py                 # Scan staged files only
  python scripts/scan_for_keys.py --all-modified  # Scan staged + unstaged
  python scripts/scan_for_keys.py --range A..B    # Scan files changed in a commit range
  python scripts/scan_for_keys.py --all-tracked   # Scan every tracked file
  python scripts/scan_for_keys.py --files a b c   # Scan named paths (used by the tests)
Exit: 0 = clean, 1 = key patterns found

⚠️ THE DEFAULT MODE SEES NOTHING AT PUSH TIME, AND THAT IS WHY --range EXISTS (2026-08-24).
The pre-push hook called this script with NO ARGUMENT. At push time nothing is staged, so
`git diff --cached` returns empty, so the scan printed "No files to scan" and exited 0 —
**every time, on every push, regardless of what was being pushed.** The push gate's secret
check could not fail. `tests/test_push_gate.py` asserted the hook *mentions* this script and
branches on its status, both of which were true; neither says the check can fail.

That is R20 ("a mechanical pass may not insert a check that cannot fail") arriving inside the
gate built to enforce that family of discipline, and it is the reason `tests/test_push_gate.py`
now runs this script against a crafted fake key and asserts exit 1 — watch the check fail before
trusting it.
"""
import subprocess, re, sys, os, argparse

KEY_PATTERNS = [
    (r'sk-or-[A-Za-z0-9_-]{20,}', 'OpenRouter key'),
    (r'gsk_[A-Za-z0-9]{20,}', 'Groq key'),
    (r'sk-ant-[A-Za-z0-9_-]{20,}', 'Anthropic key'),
    (r'sk-proj-[A-Za-z0-9_-]{20,}', 'OpenAI key'),
    (r'hf_[A-Za-z0-9]{20,}', 'HuggingFace token'),
    (r'AQ\.[A-Za-z0-9_-]{20,}', 'Gemini key'),
    (r'github_pat_[A-Za-z0-9_]{20,}', 'GitHub token'),
    (r'ghp_[A-Za-z0-9]{20,}', 'GitHub token'),
    (r'csk-[A-Za-z0-9]{20,}', 'Cerebras key'),
]

# Only skip lines that are clearly placeholders or comments.
# NOTE: os.environ.get is intentionally NOT here — a line with
# os.environ.get("KEY", "sk-or-v1-realkey") still has a real key.
SAFE_LINE_PATTERNS = [
    r'YOUR_KEY_HERE',
    r'your-key-here',
    r'sk-ant-your',
    r'sk-or-your',
    r'gsk_your',
    r'hf_your',
    r'#\s*(example|Example|your key|placeholder)',
    r'sk-or-v1-\.\.\.',
    # A REDACTION PLACEHOLDER: a token body that is ENTIRELY x's. Found 2026-08-25 by running
    # --all-tracked, which is the fallback the pre-push hook takes when git gives it no range —
    # i.e. THE FIRST PUSH OF A NEW BRANCH. `handover.md:695` records a HuggingFace secret as
    # `hf_xxxxxxxxxxxxxxxxxxxxxxxxx`, so that push would have been blocked by a redaction.
    # R26's five-state vocabulary calls this OVERBROAD, and it is the half of R26 that yesterday's
    # fix skipped: the control was planted into (it MUST block) but never given a clean case (it
    # MUST pass).
    #
    # Deliberately the NARROWEST form that closes it (R17 step 4): the body after the prefix must
    # be x's and NOTHING else. A real key is mixed-case with digits, so `hf_xAbC...` still blocks.
    r'(?:hf_|sk-ant-|sk-or-v1-|gsk_|AIza)[xX]{8,}(?![A-Za-z0-9])',
]


def get_staged_files():
    result = subprocess.run(
        ['git', 'diff', '--cached', '--name-only'],
        capture_output=True, text=True
    )
    return [f.strip() for f in result.stdout.strip().split('\n') if f.strip()]


def get_modified_files():
    result = subprocess.run(
        ['git', 'diff', '--name-only'],
        capture_output=True, text=True
    )
    return [f.strip() for f in result.stdout.strip().split('\n') if f.strip()]


def get_range_files(rev_range):
    """Files touched by the commits in `rev_range` (e.g. 'origin/main..HEAD').

    This is what the pre-push hook needs: at push time nothing is staged, so the range is the
    only description of what is actually leaving the machine.
    """
    result = subprocess.run(
        ['git', 'diff', '--name-only', rev_range],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f'git diff --name-only {rev_range} failed: {result.stderr.strip()}')
        sys.exit(2)
    return [f.strip() for f in result.stdout.strip().split('\n') if f.strip()]


def get_tracked_files():
    result = subprocess.run(['git', 'ls-files'], capture_output=True, text=True)
    return [f.strip() for f in result.stdout.strip().split('\n') if f.strip()]


def is_safe_line(line):
    """Return True only if line is clearly a placeholder or comment."""
    for pat in SAFE_LINE_PATTERNS:
        if re.search(pat, line):
            return True
    return False


def scan_file(filepath):
    flags = []
    if not os.path.exists(filepath):
        return flags
    try:
        with open(filepath, encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f, 1):
                if is_safe_line(line):
                    continue
                for pattern, key_type in KEY_PATTERNS:
                    if re.search(pattern, line):
                        flags.append({
                            'file': filepath,
                            'line': line_num,
                            'type': key_type,
                            'content': line.strip()[:80]
                        })
    except Exception:
        pass
    return flags


def main():
    parser = argparse.ArgumentParser(
        description="Scan for embedded API keys before committing"
    )
    parser.add_argument('--all-modified', action='store_true',
                        help='Also scan unstaged modified files')
    parser.add_argument('--range', dest='rev_range',
                        help='Scan files changed in a commit range, e.g. origin/main..HEAD. '
                             'This is the pre-push mode — nothing is staged at push time.')
    parser.add_argument('--all-tracked', action='store_true',
                        help='Scan every tracked file (fallback when no range is derivable)')
    parser.add_argument('--files', nargs='+', help='Scan these paths and nothing else')
    args = parser.parse_args()

    if args.files:
        files_to_scan, label = list(args.files), 'named'
    elif args.all_tracked:
        files_to_scan, label = get_tracked_files(), 'tracked'
    elif args.rev_range:
        files_to_scan, label = get_range_files(args.rev_range), f'changed in {args.rev_range}'
    else:
        files_to_scan = list(get_staged_files())
        label = 'staged'
        if args.all_modified:
            label = 'staged + modified'
            for f in get_modified_files():
                if f not in files_to_scan:
                    files_to_scan.append(f)

    if not files_to_scan:
        print(f'No files to scan ({label}).')
        sys.exit(0)

    print(f'Scanning {len(files_to_scan)} {label} file(s)...')
    all_flags = []

    for filepath in files_to_scan:
        flags = scan_file(filepath)
        all_flags.extend(flags)

    if all_flags:
        print(f'\nBLOCKED — {len(all_flags)} API key pattern(s) found:')
        for f in all_flags:
            print(f"  {f['file']}:{f['line']} [{f['type']}]")
            print(f"  {f['content']}")
        print('\nRemove keys before committing.')
        print('Use os.environ.get("KEY_NAME", "") instead.')
        sys.exit(1)
    else:
        print(f'CLEAN — no API keys detected in {len(files_to_scan)} file(s).')
        sys.exit(0)


if __name__ == '__main__':
    main()
