"""Tests for cmp.cache — the load-or-run layer that keeps a live lecture off the sampler.

The one that matters is `test_changed_inputs_force_refit`. A cache that silently
serves a stale fit after the model or seed changed would let a notebook print
numbers its prose no longer describes — the single failure mode this repo has been
bitten by most.
"""
import numpy as np
import pytest

from cmp import cache


@pytest.fixture(autouse=True)
def _isolated_cache(tmp_path, monkeypatch):
    """Never touch the user's real ~/.cache/cmp during tests."""
    monkeypatch.setenv("CMP_CACHE_HOME", str(tmp_path))
    monkeypatch.delenv("CMP_REFIT", raising=False)
    yield


def test_runs_once_then_loads():
    calls = []

    def fit():
        calls.append(1)
        return {"answer": 42}

    a = cache.load_or_run("k", fit, inputs=dict(seed=1), verbose=False)
    b = cache.load_or_run("k", fit, inputs=dict(seed=1), verbose=False)

    assert a == b == {"answer": 42}
    assert len(calls) == 1, "second call must hit the cache, not refit"


def test_changed_inputs_force_refit():
    """Change anything the answer depends on -> cache MISS, not a stale hit."""
    calls = []

    def fit():
        calls.append(1)
        return len(calls)

    cache.load_or_run("k", fit, inputs=dict(seed=1), verbose=False)
    cache.load_or_run("k", fit, inputs=dict(seed=2), verbose=False)   # seed changed
    cache.load_or_run("k", fit, inputs=dict(seed=1, draws=500), verbose=False)  # profile changed

    assert len(calls) == 3, "each distinct input set must refit"


def test_ndarray_inputs_are_hashed_by_content():
    """A changed DGP (different data) must invalidate the cache."""
    calls = []

    def fit():
        calls.append(1)
        return 1

    x = np.arange(10.0)
    cache.load_or_run("k", fit, inputs=dict(data=x), verbose=False)
    cache.load_or_run("k", fit, inputs=dict(data=x.copy()), verbose=False)   # same content -> hit
    assert len(calls) == 1

    y = x.copy()
    y[3] += 1e-6                                                   # different content -> miss
    cache.load_or_run("k", fit, inputs=dict(data=y), verbose=False)
    assert len(calls) == 2


def test_refit_flag_forces_recompute():
    calls = []

    def fit():
        calls.append(1)
        return 1

    cache.load_or_run("k", fit, inputs=None, verbose=False)
    cache.load_or_run("k", fit, inputs=None, refit=True, verbose=False)
    assert len(calls) == 2


def test_corrupt_cache_refits_instead_of_raising():
    def fit():
        return {"ok": True}

    cache.load_or_run("k", fit, inputs=None, verbose=False)
    victim = next(cache.cache_dir().glob("k-*.pkl"))
    victim.write_bytes(b"not a pickle")

    assert cache.load_or_run("k", fit, inputs=None, verbose=False) == {"ok": True}


def test_clear_cache():
    cache.load_or_run("a", lambda: 1, inputs=None, verbose=False)
    cache.load_or_run("b", lambda: 2, inputs=None, verbose=False)
    assert len(cache.cache_info()) == 2
    assert cache.clear_cache("a") == 1
    assert len(cache.cache_info()) == 1
    assert cache.clear_cache() == 1


def test_unpicklable_result_fails_loudly_with_a_useful_message():
    """A silently-skipped cache write would leave the notebook re-sampling on every run —
    the exact failure the cache exists to prevent — and nobody would notice until it
    stalled in front of a lecture theatre. CausalPy's result objects really do hold a
    functools.partial and really did trip this."""
    import functools

    class Unpicklable:
        def __init__(self):
            self.fn = functools.partial(lambda x: x, 1)

        def __reduce__(self):
            raise AttributeError("'functools.partial' object has no attribute '__name__'")

    with pytest.raises(TypeError, match="not picklable"):
        cache.load_or_run("bad", Unpicklable, inputs=None, verbose=False)
