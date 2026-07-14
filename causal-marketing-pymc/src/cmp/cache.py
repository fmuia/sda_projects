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

    def norm(o):
        if isinstance(o, np.ndarray):
            return ("ndarray", o.shape, str(o.dtype),
                    hashlib.sha256(np.ascontiguousarray(o).tobytes()).hexdigest()[:16])
        if isinstance(o, dict):
            return {k: norm(v) for k, v in sorted(o.items())}
        if isinstance(o, (list, tuple)):
            return type(o).__name__, [norm(v) for v in o]
        return o

    return hashlib.sha256(repr(norm(inputs)).encode()).hexdigest()[:12]


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

    path = cache_dir() / f"{key}-{_fingerprint(inputs)}.pkl"

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
