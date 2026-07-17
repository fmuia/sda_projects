"""Fit once, load forever — so a live lecture never waits on a sampler.

Every expensive fit in this cookbook goes through `load_or_run`. The first call
samples and writes the result to disk; every call after that loads it in
milliseconds. Nothing is re-sampled in front of an audience.

    from cmp.cache import load_or_run

    sc = load_or_run(
        "07_sc_ar1",                                  # cache key
        lambda: est.synthetic_control_ar1(target, donors, pre, post, **est.FULL),
        inputs=dict(seed=3, model="ar1", **est.FULL),  # anything that changes the answer
    )

Why the `inputs` dict matters
-----------------------------
The key alone is not enough. If you change the seed, the sampler profile, or the
DGP and keep the key, a stale cache would silently serve you the *old* answer and
the notebook's prose would describe numbers that no longer exist. So `inputs` is
hashed into the filename: change any of it and you get a cache miss and a fresh
fit, which is the safe failure. This is the guardrail against the one bug that
actually matters here — prose that no longer matches the output.

Where it writes
---------------
`~/.cache/cmp/fits` by default — deliberately NOT the repo, which lives in
Dropbox (a few hundred MB of InferenceData would sync forever). Override with
`CMP_CACHE_HOME`. Set `CMP_REFIT=1` to force every fit to recompute (use this
when you change a model and want the whole cookbook rebuilt).

Before a lecture, run `make warm` to populate the cache from a cold machine.
"""
from __future__ import annotations

import hashlib
import os
import pickle
import time
from pathlib import Path
from typing import Any, Callable

__all__ = ["cache_dir", "load_or_run", "cache_info", "clear_cache"]


def cache_dir() -> Path:
    """Where fits are cached. `CMP_CACHE_HOME` overrides; defaults to ~/.cache/cmp."""
    root = os.environ.get("CMP_CACHE_HOME")
    base = Path(root).expanduser() if root else Path.home() / ".cache" / "cmp"
    d = base / "fits"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _fingerprint(inputs: Any) -> str:
    """Stable short hash of whatever the caller says the fit depends on.

    `repr` is good enough (and stable) for the scalars/dicts/tuples we pass; numpy
    arrays are hashed by their bytes so a changed DGP changes the key.
    """
    import numpy as np

    try:
        import pandas as pd
    except ImportError:                                    # pandas is a hard dep, but be safe
        pd = None

    def norm(o):
        if isinstance(o, np.ndarray):
            return ("ndarray", o.shape, str(o.dtype),
                    hashlib.sha256(np.ascontiguousarray(o).tobytes()).hexdigest()[:16])
        # A DataFrame/Series used to fall through to `repr(o)` — and pandas TRUNCATES its repr
        # (head/tail with an ellipsis). Two different frames with the same head, tail and shape
        # therefore produced the SAME cache key and silently shared a fit.
        if pd is not None and isinstance(o, (pd.DataFrame, pd.Series)):
            h = hashlib.sha256(
                pd.util.hash_pandas_object(o, index=True).values.tobytes()).hexdigest()[:16]
            cols = tuple(map(str, getattr(o, "columns", [])))
            return ("pandas", type(o).__name__, o.shape, cols, h)
        if isinstance(o, dict):
            return {k: norm(v) for k, v in sorted(o.items())}
        if isinstance(o, (list, tuple)):
            return type(o).__name__, [norm(v) for v in o]
        return o

    return hashlib.sha256(repr(norm(inputs)).encode()).hexdigest()[:12]


def _code_fingerprint(fn: Callable) -> str:
    """Hash the SOURCE of `fn` and of every `cmp.*` function it (transitively) calls.

    THE BUG THIS FIXES. The cache key used to be `key` + a hash of the caller-declared `inputs`
    only. It contained nothing about the MODEL. So changing a prior, a likelihood, an estimator or
    a DGP generator — while the declared inputs stayed the same — made `load_or_run` return the
    OLD posterior, silently. Every diagnostic downstream then graded a model that no longer existed,
    and it looked completely clean. This is the single most dangerous failure mode in the repo,
    because a stale fit is indistinguishable from a fresh one.

    Rather than hash every module (which would invalidate the whole cache on any edit), walk the
    names `fn` actually references, resolve them against `fn`'s globals, and hash the source of the
    ones that live in `cmp`. Recurse, so `est.synthetic_control_ar1` -> its helpers are covered too.
    """
    import inspect

    seen: set[str] = set()
    chunks: list[str] = []

    def walk(f, depth=0):
        if depth > 4:
            return
        qual = getattr(f, "__module__", "") + "." + getattr(f, "__qualname__", "")
        if qual in seen:
            return
        seen.add(qual)
        try:
            chunks.append(inspect.getsource(f))
        except (OSError, TypeError):
            # No source available (a C builtin, or a lambda typed at a REPL). That is NOT a reason
            # to stop: the caller's lambda is usually a one-line shim, and the code we actually need
            # to fingerprint is the cmp.* model it calls. Keep walking.
            pass

        g = getattr(f, "__globals__", {}) or {}
        names = set(getattr(getattr(f, "__code__", None), "co_names", ()) or ())
        # free variables too: a lambda closing over a locally-defined model function
        for cell, name in zip(getattr(f, "__closure__", None) or (),
                              getattr(getattr(f, "__code__", None), "co_freevars", ()) or ()):
            try:
                obj = cell.cell_contents
            except ValueError:
                continue
            if callable(obj) and getattr(obj, "__module__", "").startswith("cmp"):
                walk(obj, depth + 1)

        for name in names:
            obj = g.get(name)
            if obj is None:
                continue
            mod = getattr(obj, "__module__", "") or getattr(obj, "__name__", "")
            # a cmp function referenced directly
            if callable(obj) and str(getattr(obj, "__module__", "")).startswith("cmp"):
                walk(obj, depth + 1)
            # a cmp MODULE referenced as `est.foo` / `dgp.bar`: co_names carries both `est` and
            # `foo`, so resolve every other name against the module.
            elif inspect.ismodule(obj) and str(getattr(obj, "__name__", "")).startswith("cmp"):
                for attr in names:
                    sub = getattr(obj, attr, None)
                    if callable(sub) and str(getattr(sub, "__module__", "")).startswith("cmp"):
                        walk(sub, depth + 1)

    walk(fn)
    return hashlib.sha256("".join(chunks).encode()).hexdigest()[:12]


def load_or_run(
    key: str,
    fn: Callable[[], Any],
    *,
    inputs: Any = None,
    refit: bool | None = None,
    verbose: bool = True,
) -> Any:
    """Return the cached result for `key`+`inputs`, else run `fn()` and cache it.

    Parameters
    ----------
    key : short human-readable name, e.g. "07_sc_ar1". Becomes part of the filename.
    fn : zero-argument callable that does the expensive work.
    inputs : anything that changes the answer (seed, sampler profile, data hash).
        Hashed into the filename, so a change forces a refit instead of serving a
        stale result. Passing None means "this fit depends on nothing" — almost
        never true; pass the real inputs.
    refit : force recomputation. Defaults to the CMP_REFIT env var.

    Returns whatever `fn` returned. Anything picklable works, including ArviZ
    InferenceData and dicts of numpy arrays.
    """
    if refit is None:
        refit = os.environ.get("CMP_REFIT", "").lower() in {"1", "true", "yes"}

    # The key is (name, declared inputs, MODEL CODE). The third component is the one that was
    # missing: without it, editing a prior or a likelihood served the old posterior back, silently.
    inputs_fp = _fingerprint(inputs)
    path = cache_dir() / f"{key}-{inputs_fp}-{_code_fingerprint(fn)}.pkl"

    # ---- one-time migration ------------------------------------------------------------------
    # Adding the code fingerprint renamed every cache file, so ~17 GB of perfectly good fits stopped
    # being found. Recomputing all of them is hours of sampling, and for SOME of them it is provably
    # unnecessary: if neither the model code nor the data has changed, the old fit is still exactly
    # right. `CMP_CACHE_ADOPT=<key>[,<key>...]` adopts the old, un-fingerprinted file for those keys
    # ONLY — a deliberate, per-key, auditable act. It is not a general escape hatch: without it a
    # missing fingerprint means a refit, which is the safe default and the whole point of the fix.
    if not refit and not path.exists():
        adopt = {k.strip() for k in os.environ.get("CMP_CACHE_ADOPT", "").split(",") if k.strip()}
        if key in adopt:
            legacy = cache_dir() / f"{key}-{inputs_fp}.pkl"
            if legacy.exists():
                print(f"[cache] ADOPTING the pre-fingerprint fit for '{key}'. You are asserting that "
                      f"neither its model code nor its data has changed. Renaming, not copying, so "
                      f"this happens exactly once.")
                legacy.replace(path)

    if path.exists() and not refit:
        try:
            with path.open("rb") as fh:
                payload = pickle.load(fh)
            if verbose:
                age = (time.time() - path.stat().st_mtime) / 3600
                print(f"[cache] loaded '{key}' ({payload['seconds']:.0f}s fit, "
                      f"cached {age:.1f}h ago) — nothing re-sampled.")
            return payload["result"]
        except Exception as exc:                       # corrupt / stale pickle
            print(f"[cache] '{key}' unreadable ({exc.__class__.__name__}); refitting.")

    if verbose:
        print(f"[cache] MISS '{key}' — fitting (this is the slow path)...")
    t0 = time.time()
    result = fn()
    seconds = time.time() - t0

    tmp = path.with_suffix(".tmp")                     # atomic: never leave a half-written cache
    try:
        with tmp.open("wb") as fh:
            pickle.dump({"result": result, "seconds": seconds, "key": key,
                         "inputs": repr(inputs)}, fh, protocol=pickle.HIGHEST_PROTOCOL)
        tmp.replace(path)
    except (TypeError, AttributeError, pickle.PicklingError) as exc:
        tmp.unlink(missing_ok=True)
        # Loud, not silent. A caught-and-ignored failure here would leave the notebook
        # re-sampling on every run — exactly the thing the cache exists to prevent — and
        # nobody would notice until it stalled in front of a lecture theatre.
        # Known offender: CausalPy's result objects hold a functools.partial and cannot be
        # pickled. Cache `result.idata` (an ArviZ InferenceData, which pickles fine) rather
        # than the wrapper.
        raise TypeError(
            f"load_or_run('{key}'): the fit completed in {seconds:.0f}s but its result is not "
            f"picklable ({type(exc).__name__}: {exc}). Cache a plain-data view of it instead — "
            f"e.g. `.idata`, or a dict of numpy arrays — not the library's wrapper object."
        ) from exc
    if verbose:
        print(f"[cache] stored '{key}' after {seconds:.0f}s -> {path.name}")
    return result


def cache_info() -> list[dict]:
    """List what is cached (key, size, age) — used by `make warm` to report."""
    out = []
    for p in sorted(cache_dir().glob("*.pkl")):
        out.append({
            "file": p.name,
            "mb": round(p.stat().st_size / 1e6, 1),
            "hours_old": round((time.time() - p.stat().st_mtime) / 3600, 1),
        })
    return out


def clear_cache(key: str | None = None) -> int:
    """Delete cached fits (all, or just those for `key`). Returns the count removed."""
    pattern = f"{key}-*.pkl" if key else "*.pkl"
    n = 0
    for p in cache_dir().glob(pattern):
        p.unlink()
        n += 1
    return n
