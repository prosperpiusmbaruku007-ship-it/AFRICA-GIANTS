# -*- coding: utf-8 -*-
"""Standing fetch helper, built 2026-09-02 per CLAUDE.md R30: a tool-bug workaround written only
as prose decays -- this project diagnosed WebFetch's tra.go.tz failure once (2026-08-16), never
turned it into a callable tool, and every session since kept re-recording the same domains as
"unreachable" instead of re-finding the fix. This is the fix, made callable.

WebFetch's "Parse Error: Invalid header value char" on many .go.tz domains is a bug in that one
tool's HTTP client, not a real block -- curl reaches tra.go.tz, brela.go.tz, osha.go.tz,
mof.go.tz, nssf.go.tz, wcf.go.tz, kazi.go.tz cleanly. tanzlii.org's HTML frontend is a GENUINE
Cloudflare Turnstile challenge (no tool bypasses it); media.tanzlii.org, a different subdomain
serving the same documents as direct PDFs, is NOT behind that challenge and usually works.
immigration.go.tz is a GENUINE client-rendered SPA shell (no server-side content at all,
regardless of tool). This helper does not paper over those two -- it fetches what curl can
fetch and reports plainly what it got, so a genuine block is never mistaken for a fixed one.

Usage:
    python scripts/fetch_primary_source.py <url> [output.pdf]
    python scripts/fetch_primary_source.py <url> --text-only   # print extracted text, PDF only

Exit code 0 with real content saved/printed; exit code 1 with the HTTP status and byte count
printed to stderr if the fetch did not produce usable content (never silently returns nothing).
"""
import subprocess
import sys
import os
import tempfile

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36'


def fetch(url, out_path, timeout=60):
    """curl -L with a real browser UA. Returns (status_code, byte_count, out_path)."""
    result = subprocess.run(
        ['curl', '-sL', '-A', UA, '-o', out_path, '--max-time', str(timeout),
         '-w', '%{http_code} %{size_download}', url],
        capture_output=True, text=True)
    parts = result.stdout.strip().split()
    status = int(parts[0]) if parts and parts[0].isdigit() else 0
    size = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 0
    return status, size


def extract_pdf_text(pdf_path):
    result = subprocess.run(['pdftotext', '-layout', pdf_path, '-'],
                             capture_output=True, text=True, encoding='utf-8', errors='replace')
    return result.stdout


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    url = sys.argv[1]
    text_only = '--text-only' in sys.argv
    out_path = None
    for a in sys.argv[2:]:
        if not a.startswith('--'):
            out_path = a
    if out_path is None:
        fd, out_path = tempfile.mkstemp(suffix='.download')
        os.close(fd)

    status, size = fetch(url, out_path)

    if status != 200 or size == 0:
        sys.stderr.write(f'FETCH FAILED: HTTP {status}, {size} bytes -- {url}\n')
        sys.stderr.write('Not treated as a tool bug automatically. If this is a .go.tz domain '
                          'other than tanzlii.org/immigration.go.tz, retry once before '
                          'concluding it is genuinely blocked (CLAUDE.md R30).\n')
        sys.exit(1)

    is_pdf = False
    with open(out_path, 'rb') as f:
        is_pdf = f.read(5) == b'%PDF-'

    if text_only:
        if not is_pdf:
            sys.stderr.write('--text-only requested but the response is not a PDF; printing raw bytes as text.\n')
            with open(out_path, encoding='utf-8', errors='replace') as f:
                print(f.read())
        else:
            print(extract_pdf_text(out_path))
    else:
        print(f'OK: HTTP {status}, {size} bytes, saved to {out_path} '
              f'({"PDF" if is_pdf else "non-PDF"})')


if __name__ == '__main__':
    main()
