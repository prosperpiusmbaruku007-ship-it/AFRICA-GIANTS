# -*- coding: utf-8 -*-
"""Inbound-first onboarding: a wa.me link with pre-filled Swahili text, and a QR code PNG of it.

THE PHONE NUMBER IS NEVER IN THE REPO. Supply it at run time, locally:
    set CHIKE_WA_NUMBER=2557XXXXXXXX      (or: --number 2557XXXXXXXX)
    python scripts/make_onboarding_link.py
Output goes to scratch/onboarding/ (gitignored): link.txt and qr.png. The QR step needs `pip install segno`
(pure Python, no dependencies); without it the link is still written and the script says so.

The pre-filled text is "Habari Chike", and `build_link` REFUSES any text the handler would not classify as a GREETING:
a participant who taps the link and presses send is sending a greeting, which gets the disclosure and the welcome with no model
call. A pre-filled QUESTION would spend a GPU call and put a card in front of a reviewer for a message that asks nothing.
"""
import argparse
import os
import re
import sys
import urllib.parse

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "chike-whatsapp"))

PREFILLED_TEXT = "Habari Chike"
OUT_DIR = os.path.join(_ROOT, "scratch", "onboarding")


def normalise_number(raw):
    """International digits only (no '+', spaces or dashes), 9-15 digits. Anything else raises: a wrong number on a printed QR
    sends a participant's first message to a stranger."""
    digits = re.sub(r"[\s\-+()]", "", str(raw or ""))
    if not digits.isdigit() or not (9 <= len(digits) <= 15):
        raise ValueError("number must be international digits, 9-15 long (e.g. 2557XXXXXXXX)")
    return digits


def build_link(number, text=PREFILLED_TEXT):
    import handler_core as core
    if str(text).strip().lower() not in core.GREETINGS:
        raise ValueError(f"pre-filled text {text!r} is not a greeting: it would be handled as a QUESTION (GPU call + reviewer card)")
    return "https://wa.me/" + normalise_number(number) + "?text=" + urllib.parse.quote(text, safe="")


def write_outputs(link, out_dir=OUT_DIR):
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "link.txt"), "w", encoding="utf-8") as f:
        f.write(link + "\n")
    try:
        import segno
    except ImportError:
        return False
    segno.make(link, error="m").save(os.path.join(out_dir, "qr.png"), scale=12, border=4)
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--number", default=os.environ.get("CHIKE_WA_NUMBER"))
    ap.add_argument("--text", default=PREFILLED_TEXT)
    a = ap.parse_args()
    if not a.number:
        sys.exit("supply the number locally: --number 2557XXXXXXXX or CHIKE_WA_NUMBER (it is never stored in the repo)")
    link = build_link(a.number, a.text)
    qr = write_outputs(link)
    print("link written to scratch/onboarding/link.txt")
    print("qr.png written" if qr else "QR NOT written: run `pip install segno` and re-run")


if __name__ == "__main__":
    main()
