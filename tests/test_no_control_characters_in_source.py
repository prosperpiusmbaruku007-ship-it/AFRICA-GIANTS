# -*- coding: utf-8 -*-
"""R39, made permanent (founder's instruction 2026-11-17): NO .py FILE IN THE REPO MAY CONTAIN A CONTROL CHARACTER.

Why: a regex written through a generating script with a non-raw string turns `\\b` into a literal BACKSPACE (0x08). The pattern then matches nothing, the source LOOKS correct in every terminal, editor and diff, and
nothing downstream fails -- it happened twice in one session (PROGRESS 4at). Only the characters themselves can be searched for, so this test searches for them in EVERY Python file, not only files touched recently.

Allowed: TAB (0x09), LF (0x0a), CR (0x0d). Everything else below 0x20 fails, and so does DEL (0x7f). Populations: every tracked .py file (`git ls-files`), PLUS every .py file on disk outside the ignored directories,
so a new untracked file is checked before it is ever committed. The check is planted (a temp file carrying a real backspace must be reported) and its population is asserted non-trivial (R20: a scan that
finds nothing because it scanned nothing).
"""
import os
import re
import subprocess

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BAD = re.compile("[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
SKIP_DIRS = {".git", "scratch", "__pycache__", "node_modules", ".venv", "venv", ".mypy_cache", ".pytest_cache"}


def find_control_characters(path):
    """[(line_number, column, hex_code, context)] for every control character in the file; [] when clean."""
    out = []
    with open(path, encoding="utf-8", errors="replace", newline="") as f:
        for n, line in enumerate(f, 1):
            for m in BAD.finditer(line):
                out.append((n, m.start() + 1, hex(ord(m.group())), repr(line[max(0, m.start() - 25):m.start() + 12])))
    return out


def python_files():
    files = set()
    try:
        tracked = subprocess.run(["git", "ls-files", "-z", "--", "*.py"], cwd=REPO, capture_output=True, check=True).stdout.decode("utf-8", "replace").split("\0")
        files.update(os.path.join(REPO, t) for t in tracked if t)
    except (OSError, subprocess.CalledProcessError):
        pass
    for root, dirs, names in os.walk(REPO):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        files.update(os.path.join(root, n) for n in names if n.endswith(".py"))
    return sorted(f for f in files if os.path.isfile(f))


def test_no_python_file_contains_a_control_character():
    files = python_files()
    assert len(files) > 200, f"the scan found only {len(files)} .py files; a scan of nothing is not a pass"
    found = {os.path.relpath(f, REPO): hits for f in files if (hits := find_control_characters(f))}
    assert not found, "control characters in source (a `\\b` written as a literal backspace is invisible in every editor):\n" + "\n".join(
        f"  {p}:{h[0]}:{h[1]} {h[2]} {h[3]}" for p, hits in found.items() for h in hits[:5])


def test_PLANTED_a_real_backspace_in_a_regex_is_reported(tmp_path):
    bad = tmp_path / "planted.py"
    bad.write_text('import re\nPAT = re.compile("' + chr(8) + "wangapi" + chr(8) + '")\n', encoding="utf-8")
    hits = find_control_characters(str(bad))
    assert [h[2] for h in hits] == ["0x8", "0x8"] and hits[0][0] == 2, hits


def test_PLANTED_the_other_control_characters_and_DEL_are_reported_but_tab_lf_cr_are_not(tmp_path):
    ok = tmp_path / "ok.py"
    ok.write_bytes(b"x = 1\r\n\ty = 2\n")
    assert find_control_characters(str(ok)) == []
    for code in (0x00, 0x01, 0x07, 0x0b, 0x0c, 0x1b, 0x1f, 0x7f):
        p = tmp_path / f"c{code}.py"
        p.write_bytes(b"x = '" + bytes([code]) + b"'\n")
        assert [h[2] for h in find_control_characters(str(p))] == [hex(code)], code


def test_the_escaped_form_is_NOT_a_control_character(tmp_path):
    """the correct source -- a backslash followed by the letter b inside a raw string -- must pass, or the test would force the wrong fix"""
    good = tmp_path / "good.py"
    good.write_text('import re\nPAT = re.compile(r"' + chr(92) + "bwangapi" + chr(92) + 'b")\n', encoding="utf-8")
    assert find_control_characters(str(good)) == []


# ---- the JSON route: json.dump stores a backspace as the escape \b, so a RAW-text scan of a .json file cannot see it; the LOADED strings can ----------------------------------------------------------------
JSON_DATA = ("scripts/locked_facts.json", "kaggle/chike_config.json", "sources/whitelist.json", "chike-inference/rag_facts_text.json", "kaggle/rag_facts_text.json")


def _control_strings(obj, path=""):
    import json as _j  # noqa: F401
    if isinstance(obj, str):
        if BAD.search(obj):
            yield path, obj[:120]
    elif isinstance(obj, dict):
        for k, v in obj.items():
            yield from _control_strings(v, f"{path}/{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from _control_strings(v, f"{path}/{i}")


def test_no_loaded_json_string_contains_a_control_character_and_every_wrong_pattern_compiles_to_something():
    import json
    found = []
    for rel in JSON_DATA:
        with open(os.path.join(REPO, rel), encoding="utf-8") as f:
            found += [(rel, p, s) for p, s in _control_strings(json.load(f))]
    assert not found, "control characters in loaded JSON strings (the JSON escape for a backspace is \b):\n" + "\n".join(f"  {r}{p}: {s!r}" for r, p, s in found[:8])
    with open(os.path.join(REPO, "scripts/locked_facts.json"), encoding="utf-8") as f:
        facts = json.load(f)
    pats = [(k, w) for k, v in facts.items() if isinstance(v, dict) for w in (v.get("wrong_patterns") or [])]
    assert len(pats) > 100, f"only {len(pats)} wrong_patterns found; a scan of nothing is not a pass"
    for k, w in pats:
        re.compile(w)                                              # raises on a pattern that does not compile


def test_PLANTED_a_backspace_inside_a_json_string_is_reported_after_loading():
    import json
    # json.dumps writes the backspace as the two-character escape; json.loads gives the real character back -- exactly the shape that hid two corrupt wrong_patterns in locked_facts.json
    text = json.dumps({"wrong_patterns": ["a" + chr(8) + "wangapi" + chr(8)]})
    assert chr(8) not in text and chr(92) + "b" in text, "the escaped form is invisible to a raw-text scan"
    assert [p for p, _ in _control_strings(json.loads(text))] == ["/wrong_patterns/0"]
