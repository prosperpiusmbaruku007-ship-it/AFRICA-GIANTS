# -*- coding: utf-8 -*-
"""R26 for the live harnesses' artifact writes (founder's decision 2026-11-17): the artifact is written ATOMICALLY (temp file + os.replace), so a reader -- a test, a person, the analyser -- sees the OLD complete file or the NEW
complete file, never a prefix. PLANTED: a non-atomic writer (open "w" + write) is shown to expose a prefix, so the check cannot pass vacuously."""
import glob
import json
import os
import re
import sys
import threading

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "eval", "controls"))
import atomic_artifact  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_roundtrip_and_no_temp_file_left(tmp_path):
    p = tmp_path / "a.json"
    atomic_artifact.write_json(str(p), {"rows": [{"id": "x", "reply": "Hapana — si kweli"}]})
    assert json.loads(p.read_text(encoding="utf-8")) == {"rows": [{"id": "x", "reply": "Hapana — si kweli"}]}
    assert [f.name for f in tmp_path.iterdir()] == ["a.json"]


def test_a_failed_serialisation_never_touches_the_existing_artifact(tmp_path):
    p = tmp_path / "a.json"
    atomic_artifact.write_json(str(p), {"v": 1})
    with pytest.raises(TypeError):
        atomic_artifact.write_json(str(p), {"v": object()})
    assert json.loads(p.read_text(encoding="utf-8")) == {"v": 1}
    assert [f.name for f in tmp_path.iterdir()] == ["a.json"]


def test_at_the_moment_of_replacement_the_destination_is_still_the_complete_old_file_and_the_temp_is_the_complete_new_one(tmp_path, monkeypatch):
    p = tmp_path / "a.json"
    atomic_artifact.write_json(str(p), {"gen": "OLD", "pad": "x" * 100_000})
    seen = {}
    real = os.replace

    def spy(src, dst):
        seen["dst_before"] = json.loads(open(dst, encoding="utf-8").read())["gen"]
        seen["tmp"] = json.loads(open(src, encoding="utf-8").read())["gen"]
        return real(src, dst)
    monkeypatch.setattr(atomic_artifact.os, "replace", spy)
    atomic_artifact.write_json(str(p), {"gen": "NEW", "pad": "y" * 100_000})
    assert seen == {"dst_before": "OLD", "tmp": "NEW"}
    assert json.loads(p.read_text(encoding="utf-8"))["gen"] == "NEW"


def test_PLANTED_a_non_atomic_writer_exposes_a_prefix(tmp_path):
    """the positive control: `open(path, "w")` truncates first, so a reader in the middle sees an unparseable prefix"""
    p = tmp_path / "a.json"
    text = json.dumps({"rows": ["z" * 1000] * 50})
    f = open(p, "w", encoding="utf-8")
    f.write(text[: len(text) // 2])
    f.flush()
    with pytest.raises(json.JSONDecodeError):
        json.loads(p.read_text(encoding="utf-8"))
    f.close()


def test_a_reader_never_sees_a_prefix_under_concurrent_writes(tmp_path):
    p = tmp_path / "a.json"
    atomic_artifact.write_json(str(p), {"gen": 0, "pad": "p" * 50_000})
    stop, errors, reads = threading.Event(), [], [0]

    def reader():
        while not stop.is_set():
            try:
                json.loads(open(p, encoding="utf-8").read())
                reads[0] += 1
            except json.JSONDecodeError as e:
                errors.append(repr(e)[:80])
            except (PermissionError, FileNotFoundError):
                pass                                   # Windows may refuse the OPEN during the swap: that is not a prefix
    t = threading.Thread(target=reader)
    t.start()
    for i in range(1, 80):
        atomic_artifact.write_json(str(p), {"gen": i, "pad": ("q" if i % 2 else "r") * (50_000 + i)})
    stop.set()
    t.join()
    assert errors == [] and reads[0] > 0, (errors[:3], reads)


HARNESSES = sorted(glob.glob(os.path.join(REPO, "eval", "controls", "verify_*_2026_11_17.py")) + [os.path.join(REPO, "eval", "controls", "score_proposed_gold_tails_2026_11_17.py")])


def _code(path):
    return "\n".join(ln.split("#", 1)[0] for ln in open(path, encoding="utf-8").read().splitlines())


@pytest.mark.parametrize("path", HARNESSES, ids=[os.path.basename(h) for h in HARNESSES])
def test_every_live_harness_of_2026_11_17_writes_its_artifact_atomically(path):
    code = _code(path)
    assert "atomic_artifact.write_json(" in code, path
    assert not re.search(r"open\(OUT,\s*[\"']w", code), "a direct open(OUT, 'w') truncates the artifact before the new text exists"


def test_the_population_is_not_empty_R20():
    assert len(HARNESSES) >= 9
