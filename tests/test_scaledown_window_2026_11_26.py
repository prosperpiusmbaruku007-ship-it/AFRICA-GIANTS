"""scaledown_window 300 -> 600 s (founder, 2026-11-26) and NO always-warm. Parses the deployed file's decorator, not a grep for a number (R26)."""
import ast
import os

_SRC = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "chike-inference", "modal_app.py"), encoding="utf-8").read()


def _cls_kwargs():
    for n in ast.walk(ast.parse(_SRC)):
        if isinstance(n, ast.ClassDef) and n.name == "ChikeModel":
            for d in n.decorator_list:
                if isinstance(d, ast.Call) and getattr(d.func, "attr", "") == "cls":
                    return {k.arg: k.value for k in d.keywords}
    raise AssertionError("ChikeModel's @app.cls decorator not found")


def test_the_gpu_class_scales_down_after_600_seconds():
    kw = _cls_kwargs()
    assert isinstance(kw["scaledown_window"], ast.Constant) and kw["scaledown_window"].value == 600


def test_no_always_warm_is_ever_configured_on_the_gpu_class():
    assert not {"min_containers", "keep_warm", "buffer_containers"} & set(_cls_kwargs()), "always-warm is ruled out (cost: $425-$575/month)"
