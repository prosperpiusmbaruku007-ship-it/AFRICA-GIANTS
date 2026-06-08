#!/usr/bin/env python3
"""
GIT-PUSH-GUARD — scan staged and/or modified files for API key patterns.
Usage:
  python scripts/scan_for_keys.py                 # Scan staged files only
  python scripts/scan_for_keys.py --all-modified  # Scan staged + unstaged
Exit: 0 = clean, 1 = key patterns found
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
    args = parser.parse_args()

    staged = get_staged_files()
    files_to_scan = list(staged)

    if args.all_modified:
        for f in get_modified_files():
            if f not in files_to_scan:
                files_to_scan.append(f)

    if not files_to_scan:
        print('No files to scan (no staged or modified files found).')
        sys.exit(0)

    label = "staged + modified" if args.all_modified else "staged"
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
