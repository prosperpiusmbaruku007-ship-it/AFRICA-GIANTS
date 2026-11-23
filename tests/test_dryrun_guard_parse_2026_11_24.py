"""The dry run's guard-table parser must read each critical query's keyword list EXACTLY as the regen does (a real Python list, any keyword passes).

Why this exists (2026-11-24): five dated dry runs split the list text on "','" (no space), so `['kuoa', 'kuolewa']` became ONE keyword that no row can contain, and exactly the four multi-keyword guards (phone repair, GN487A marriage,
BRELA striking-off, OSHA/WCF small-count) were reported as 'pre-existing failures that fail on the deployed index too'. Kaggle ran the real lists: all 91 PASS. A harness that re-parses what the real run executes is a model of the run (R24)."""
import ast
import importlib.util
import os
import re

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FOUR = ("Phone repair activity", "GN487A marriage no exemption", "BRELA striking-off (Q13 verbatim)", "OSHA/WCF small-count (Q14 verbatim)")


def _mod():
    spec = importlib.util.spec_from_file_location("_dry", os.path.join(_ROOT, "eval", "index_quality", "dryrun_regen_2026_11_24.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _src():
    return open(os.path.join(_ROOT, "kaggle", "regenerate_rag_e5.py"), encoding="utf-8").read()


def test_parser_equals_the_real_python_lists_for_every_guard():
    got = _mod().parse_committed_guards(_src())
    assert len(got) >= 91, len(got)                                      # a parser that finds nothing must fail, not pass vacuously (R20)
    raw = re.findall(r"\(\s*'([^']+)'\s*,\s*'(query: [^']+)'\s*,\s*\[([^\]]*)\]\s*\)", _src())
    assert [(n, q) for n, q, _ in got] == [(n, q) for n, q, _ in raw]
    for (n, q, kws), (_, _, text) in zip(got, raw):
        assert kws == list(ast.literal_eval("[" + text + "]")), n


def test_the_four_multi_keyword_guards_keep_all_their_keywords():
    by = {n: kws for n, _, kws in _mod().parse_committed_guards(_src())}
    for name in FOUR:
        assert len(by[name]) >= 2 and all("'" not in k for k in by[name]), (name, by[name])


def test_plant_the_old_naive_split_mis_parses_exactly_those_four():
    """POSITIVE CONTROL: the removed parser really was wrong, and wrong for these four and no others."""
    raw = re.findall(r"\(\s*'([^']+)'\s*,\s*'(query: [^']+)'\s*,\s*\[([^\]]*)\]\s*\)", _src())
    wrong = [n for n, _, text in raw if text.strip() and ast.literal_eval("[" + text + "]") != [a.strip().strip("'\"") for a in text.split("','")]]
    assert sorted(wrong) == sorted(FOUR), wrong
