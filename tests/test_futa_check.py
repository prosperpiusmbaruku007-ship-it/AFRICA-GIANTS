# -*- coding: utf-8 -*-
"""scripts/futa_check.py: the read-only, salt-free residue check for the throwaway-number FUTA test. Pure part tested; the I/O part only reads."""
import importlib.util
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_spec = importlib.util.spec_from_file_location("futa_check", os.path.join(_ROOT, "scripts", "futa_check.py"))
fc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(fc)


def test_it_counts_the_numbers_records_and_everyone_elses_separately():
    rows = [{"sender_tail": "1234"}, {"sender_tail": "1234"}, {"sender_tail": "9999"}]
    items = [{"sender_tail": "1234"}, {"sender_tail": "9999"}]
    s = fc.summarize("1234", rows, items, {"review": ["1234", "9999"], "transcript": ["9999"]}, 3, [])
    assert s["transcripts_mine"] == 2 and s["review_mine"] == 1 and s["archive_review_mine"] == 1 and s["archive_transcript_mine"] == 0
    assert s["residue_total"] == 4 and s["others_total"] == 1 + 1 + 1 + 1 and s["tombstones"] == 3


def test_a_clean_state_reports_zero_residue_and_the_others_unchanged():
    before = fc.summarize("1234", [{"sender_tail": "1234"}, {"sender_tail": "9999"}], [{"sender_tail": "1234"}], {"review": ["1234"], "transcript": []}, 0, [])
    after = fc.summarize("1234", [{"sender_tail": "9999"}], [], {"review": [], "transcript": []}, 9, [])
    assert before["residue_total"] == 3 and after["residue_total"] == 0, "positive control: the check sees it before and not after"
    assert before["others_total"] == after["others_total"] == 1, "everyone else is untouched"


def test_a_different_number_with_the_same_tail_would_show_up_which_is_why_it_is_a_second_opinion():
    s = fc.summarize("1234", [{"sender_tail": "1234"}], [], {"review": [], "transcript": []}, 0, [])
    assert s["residue_total"] == 1, "a tail match is a prompt to look, not proof; the in-Modal hash scan is the authority"


def test_it_reports_the_latest_logged_deletion_without_any_hash_or_number():
    logs = [{"ts": 1, "verified": False, "residue_stores": ["transcripts"], "archive_removed_dirs": 0, "counts": {"transcripts": 0}},
            {"ts": 2, "verified": True, "residue_stores": [], "archive_removed_dirs": 2, "counts": {"transcripts": 2}}]
    s = fc.summarize("1234", [], [], {"review": [], "transcript": []}, 0, logs)
    assert s["last_deletion"]["verified"] is True and s["last_deletion"]["residue_stores"] == []
    text = fc.render(s)
    assert "verified=True" in text and "1234" not in text, "the number's tail is not echoed in the output"


def test_it_refuses_a_missing_or_malformed_tail_and_never_reads_anything(capsys):
    assert fc.main([]) == 2 and fc.main(["--last4", "12"]) == 2 and fc.main(["--last4", "abcd"]) == 2
    assert "give --last4" in capsys.readouterr().out


def test_the_script_has_no_write_path():
    import ast
    tree = ast.parse(open(os.path.join(_ROOT, "scripts", "futa_check.py"), encoding="utf-8").read())
    names = {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)} | {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
    assert not (names & {"pop", "put", "update", "clear", "delete", "remove", "write", "batch_upload", "from_name_create"}), names & {"pop", "put", "update", "clear", "delete", "remove", "write"}
    assert "create_if_missing" not in open(os.path.join(_ROOT, "scripts", "futa_check.py"), encoding="utf-8").read().split('"""', 2)[2]


# ── --baseline: totals before the test, no digits (2026-11-27) ───────────────────────────────────────────────────
def test_the_baseline_needs_no_digits_and_prints_the_totals_the_later_check_compares_against():
    rows = [{"sender_tail": "1111"}, {"sender_tail": "2222"}]
    items = [{"sender_tail": "1111"}]
    s = fc.summarize(None, rows, items, {"review": ["1111", "2222"], "transcript": ["2222"]}, 4, [])
    out = fc.render_baseline(s)
    assert "TOTAL RECORDS (everyone): 6" in out and "tombstones 4" in out
    assert s["residue_total"] == 0, "with no number there is nothing to be a residue"
    assert "1111" not in out and "2222" not in out, "no tail appears in the baseline output"


def test_the_second_check_compares_against_the_baseline_exactly_when_only_the_new_number_was_added():
    base = fc.summarize(None, [{"sender_tail": "1111"}], [], {"review": [], "transcript": []}, 0, [])
    total = 1
    after_seed = fc.summarize("5555", [{"sender_tail": "1111"}, {"sender_tail": "5555"}, {"sender_tail": "5555"}], [{"sender_tail": "5555"}],
                              {"review": [], "transcript": []}, 0, [])
    assert after_seed["others_total"] == total and base["transcripts_total"] == total, "everyone else equals the baseline total after the number's own records are removed"
    changed = fc.summarize("5555", [{"sender_tail": "1111"}, {"sender_tail": "9999"}], [], {"review": [], "transcript": []}, 0, [])
    assert changed["others_total"] != total, "plant: if someone ELSE's record appeared or vanished, the comparison catches it"


def test_baseline_mode_runs_end_to_end_against_fake_stores_and_prints_no_tail(monkeypatch, capsys):
    import types

    class _D:
        def __init__(self, items):
            self._i = items

        def items(self):
            return list(self._i)

    stores = {"chike-transcripts-kv": [("a", {"sender_tail": "1111"}), ("b", {"sender_tail": "2222"})], "chike-review-queue-kv": [("r", {"sender_tail": "1111"})],
              "chike-archive-state-kv": []}

    class _Vol:
        @staticmethod
        def listdir(path):
            raise RuntimeError("not present")
    fake = types.SimpleNamespace(Dict=types.SimpleNamespace(from_name=lambda n: _D(stores[n])), Volume=types.SimpleNamespace(from_name=lambda n: _Vol))
    monkeypatch.setitem(sys.modules, "modal", fake)
    assert fc.main(["--baseline"]) == 0
    out = capsys.readouterr().out
    assert "TOTAL RECORDS (everyone): 3" in out and "1111" not in out and "2222" not in out


def test_without_baseline_or_a_valid_tail_nothing_runs(capsys):
    assert fc.main([]) == 2 and "--baseline" in capsys.readouterr().out
