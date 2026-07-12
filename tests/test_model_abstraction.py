"""Tests for chike.model_abstraction — the ModelBackend interface and its backends.

Confirms the design principle that makes the pipeline testable: every backend is
substitutable for FakeBackend, which runs with no network and no GPU.
"""
import pytest

from chike.model_abstraction import (
    ModelBackend,
    FakeBackend,
    LocalAdapter,
    FrontierAPI,
)


# --- FakeBackend: scripted replies -----------------------------------------

def test_fake_returns_scripted_reply_when_provided():
    fake = FakeBackend(scripted_reply="SDL = TZS 236,250")
    assert fake.generate("compute sdl") == "SDL = TZS 236,250"
    assert fake.generate("anything at all") == "SDL = TZS 236,250"  # same every call


def test_fake_consumes_reply_queue_in_order_then_falls_back():
    fake = FakeBackend(scripted_reply="DEFAULT", replies=["first", "second"])
    assert fake.generate("a") == "first"
    assert fake.generate("b") == "second"
    assert fake.generate("c") == "DEFAULT"  # queue exhausted -> scripted fallback


# --- FakeBackend: echo mode -------------------------------------------------

def test_fake_echoes_truncated_prompt_when_no_script_set():
    fake = FakeBackend(echo_limit=10)
    long_prompt = "0123456789ABCDEFGHIJ"
    assert fake.generate(long_prompt) == "0123456789"  # truncated to echo_limit


def test_fake_echo_returns_whole_prompt_when_under_limit():
    fake = FakeBackend(echo_limit=200)
    assert fake.generate("short prompt") == "short prompt"


# --- FakeBackend: call recording -------------------------------------------

def test_fake_records_all_calls_with_prompt_and_params():
    fake = FakeBackend(scripted_reply="ok")
    fake.generate("first", params={"max_new_tokens": 350})
    fake.generate("second")

    assert fake.call_count == 2
    assert fake.calls[0] == {"prompt": "first", "params": {"max_new_tokens": 350}}
    assert fake.calls[1] == {"prompt": "second", "params": None}
    assert fake.last_prompt == "second"


def test_fake_reset_clears_recorded_calls():
    fake = FakeBackend(scripted_reply="ok")
    fake.generate("x")
    fake.reset()
    assert fake.call_count == 0


# --- ABC interface enforcement ---------------------------------------------

def test_backends_are_modelbackend_subclasses():
    assert issubclass(FakeBackend, ModelBackend)
    assert issubclass(LocalAdapter, ModelBackend)
    assert issubclass(FrontierAPI, ModelBackend)


def test_concrete_backends_are_instantiable():
    # Construction must not touch network or GPU — these must simply succeed.
    assert isinstance(LocalAdapter(config={"generation_params": {}, "repos": {}}), ModelBackend)
    assert isinstance(FrontierAPI(), ModelBackend)
    assert isinstance(FakeBackend(), ModelBackend)


def test_abc_rejects_subclass_that_does_not_implement_generate():
    class IncompleteBackend(ModelBackend):
        pass  # no generate() override

    with pytest.raises(TypeError):
        IncompleteBackend()


def test_frontier_stub_raises_until_wired():
    # The stub is instantiable (interface satisfied) but must fail loudly, not
    # silently fabricate, if generate() is actually called before it is wired.
    with pytest.raises(NotImplementedError):
        FrontierAPI().generate("compute paye on 800000")
