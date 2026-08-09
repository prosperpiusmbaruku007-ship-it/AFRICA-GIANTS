# -*- coding: utf-8 -*-
"""CONTAINER-PATH-1 regression guards.

The defect: two loaders read a REPO-RELATIVE kaggle/chike_config.json and fail SOFT — one to
"" and one to {}. The Modal image mounts only chike/ and bakes the config elsewhere, so inside
the container those paths do not resolve. Defaulting from them would have served an empty
system prompt and a 39-phrase OOC list (instead of 107, dropping the whole SAFETY-1 audit),
silently, with every offline instrument still green.

These tests simulate the container by making the config unreadable, and assert the code now
FAILS LOUD instead of degrading. They are the construction that replaces "safe because the
caller happens to be explicit".
"""
import pytest

from chike import classification, prompting
from chike.model_abstraction import ModelBackend
from chike.orchestrator import Orchestrator


class _Silent(ModelBackend):
    def generate(self, prompt, params=None):
        return ''


@pytest.fixture
def config_unreadable(monkeypatch):
    """Simulate the Modal container: the repo-relative config path does not resolve."""
    monkeypatch.setattr(prompting, '_CONFIG_PATH', '/nonexistent/kaggle/chike_config.json')
    monkeypatch.setattr(classification, '_LOCAL_CONFIG_PATH',
                        '/nonexistent/kaggle/chike_config.json')


# --- system prompt -------------------------------------------------------------------

def test_load_system_prompt_raises_when_the_config_cannot_be_read(config_unreadable):
    """Was: returned "" -> Chike with no persona and no R11 scope boundaries, silently."""
    with pytest.raises(RuntimeError, match='system_prompt unavailable'):
        prompting.load_system_prompt()


def test_load_system_prompt_soft_mode_still_available_for_deliberate_callers(config_unreadable):
    assert prompting.load_system_prompt(required=False) == ''


def test_load_system_prompt_raises_on_a_present_but_empty_prompt(monkeypatch, tmp_path):
    p = tmp_path / 'chike_config.json'
    p.write_text('{"system_prompt": "   "}', encoding='utf-8')
    monkeypatch.setattr(prompting, '_CONFIG_PATH', str(p))
    with pytest.raises(RuntimeError, match='system_prompt is empty'):
        prompting.load_system_prompt()


def test_build_chat_prompt_inherits_the_strictness(config_unreadable):
    """build_chat_prompt defaults system_prompt from the loader, so it must fail loud too."""
    with pytest.raises(RuntimeError, match='system_prompt unavailable'):
        prompting.build_chat_prompt('Kiwango cha SDL ni ngapi?', facts=[])


def test_explicit_system_prompt_is_unaffected_by_an_unreadable_config(config_unreadable):
    """The production shape: pass it explicitly and the missing file is irrelevant."""
    out = prompting.build_chat_prompt('Kiwango cha SDL ni ngapi?', facts=[],
                                      system_prompt='Jina lako ni Chike.')
    assert 'Jina lako ni Chike.' in out


# --- orchestrator phrase lists -------------------------------------------------------

def test_orchestrator_refuses_to_default_phrase_lists_from_an_unreadable_config(
        config_unreadable):
    """THE defect. Was: 107 -> 39 OOC phrases, silently, reopening SAFETY-1."""
    with pytest.raises(RuntimeError, match='cannot default ooc_phrases'):
        Orchestrator(_Silent(), retriever=lambda q: [])


def test_orchestrator_accepts_explicit_phrase_lists_with_an_unreadable_config(
        config_unreadable):
    """The production shape — modal_app passes resolve_phrases(CONFIG) from the BAKED file."""
    orch = Orchestrator(_Silent(), retriever=lambda q: [],
                        ooc_phrases=['capital gains'], in_scope_phrases=['sdl'],
                        system_prompt='Jina lako ni Chike.')
    assert orch.ooc_phrases == ('capital gains',)


def test_a_partial_override_still_raises(config_unreadable):
    """Passing only one list still needs the config for the other — must not half-default."""
    with pytest.raises(RuntimeError, match='cannot default ooc_phrases'):
        Orchestrator(_Silent(), retriever=lambda q: [], ooc_phrases=['capital gains'])


def test_the_real_config_still_yields_the_full_list():
    """Guards the guard: with the repo config readable, defaulting must still give 107."""
    cfg = classification.load_local_config()
    assert cfg, 'repo config should be readable in the test environment'
    ooc, _ = classification.resolve_phrases(cfg)
    hardcoded, _ = classification.resolve_phrases({})
    assert len(ooc) > len(hardcoded), 'config-only phrases must exist for this guard to matter'
    assert len(ooc) == 107, f'expected the SAFETY-1 list of 107, got {len(ooc)}'


# --- credential hygiene ----------------------------------------------------------------

def test_local_adapter_scrubs_the_token_from_a_failed_call(monkeypatch):
    """A 401 must not print the credential.

    requests' HTTPError embeds the full URL, and the token rides in the query string — so
    raise_for_status() leaks it into pytest output and terminal scrollback. Observed live on
    2026-08-09: the post-rotation 401s printed the real token into the suite's failure report.
    """
    import requests

    from chike.model_abstraction import LocalAdapter

    secret = 'SUPER-SECRET-TOKEN-VALUE'

    class _Resp:
        status_code = 401

        def raise_for_status(self):
            raise requests.exceptions.HTTPError(
                f'401 Client Error: Unauthorized for url: https://x/?token={secret}')

        def json(self):
            return {}

    monkeypatch.setattr(requests, 'post', lambda *a, **k: _Resp())
    adapter = LocalAdapter(endpoint_url='https://x', token=secret)
    with pytest.raises(RuntimeError) as ei:
        adapter.generate('swali')
    rendered = str(ei.value) + repr(getattr(ei.value, '__cause__', ''))
    assert secret not in rendered, 'the token leaked into the raised error'
    assert '<TOKEN>' in rendered
