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
