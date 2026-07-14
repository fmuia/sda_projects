"""cmp — shared package for the causal-marketing-pymc cookbook.

Notebooks import from here to stay thin: simulators (dgp), estimators,
evaluation metrics, decision/policy helpers, shared plot styling, and
optional real-data loaders.

Live-lecture rule: every expensive fit goes through `cmp.cache.load_or_run`, so
a notebook shown in front of an audience loads its posteriors from disk instead
of re-sampling. `make warm` populates the cache; `CMP_REFIT=1` forces a rebuild.
"""

__version__ = "0.1.0"

from cmp.cache import load_or_run  # re-exported: the one import every notebook needs

__all__ = ["load_or_run"]
