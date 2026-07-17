"""Execute every notebook headless in FAST mode and assert it runs clean.

Each notebook declares its own kernelspec (cmp-core for pymc>=6 notebooks,
cmp-legacy for the causalpy / pymc-marketing ones). nbclient launches that
kernel as a subprocess, so a single pytest process can drive both
environments — provided both kernels are registered (`make kernels`).

CMP_FAST=1 is forced so each notebook targets < ~2 min.

The run's `cmp.report` output is redirected to a throwaway directory (CMP_RESULTS_DIR). The
notebooks emit their book results as a side effect of executing, so without this a FAST test run
would overwrite `book/build/results/` — the FULL-mode shards the book is typeset from — and the
next `make book` would (correctly) refuse to build from them. A green test run must not damage the
artifact it is testing.
"""
import os
import tempfile
from pathlib import Path

import nbformat
import pytest
from nbclient import NotebookClient
from jupyter_client.kernelspec import KernelSpecManager

os.environ["CMP_FAST"] = "1"
os.environ.setdefault("CMP_RESULTS_DIR",
                      tempfile.mkdtemp(prefix="cmp-test-results-"))

NB_DIR = Path(__file__).resolve().parent.parent / "notebooks"
NOTEBOOKS = sorted(NB_DIR.glob("*.ipynb"))
AVAILABLE_KERNELS = set(KernelSpecManager().find_kernel_specs().keys())

# The environment split: which kernel each notebook MUST declare (README "Environment split").
CORE = {"00", "01", "02", "03", "04", "05", "07"}
LEGACY = {"06", "08", "09", "10", "11"}

# In CI both kernels are registered, so a skip means a real setup problem, not an
# intentional exemption. Set CMP_STRICT_KERNELS=1 there to turn skips into failures
# (a missing legacy kernel would otherwise silently pass 5 notebooks).
STRICT = os.environ.get("CMP_STRICT_KERNELS") == "1"


def _expected_kernel(nb_path):
    num = nb_path.name[:2]
    if num in CORE:
        return "cmp-core"
    if num in LEGACY:
        return "cmp-legacy"
    return None


@pytest.mark.parametrize("nb_path", NOTEBOOKS, ids=lambda p: p.name)
def test_notebook_kernelspec(nb_path):
    """Kernelspec-drift guard (needs no kernels — just reads metadata). A past
    incident had nbclient rewrite a notebook's kernelspec to python3/.venv,
    silently breaking `import cmp`; this fails loudly if a notebook no longer
    declares the kernel its environment split requires."""
    nb = nbformat.read(nb_path, as_version=4)
    declared = nb.metadata.get("kernelspec", {}).get("name")
    expected = _expected_kernel(nb_path)
    assert expected is not None, f"{nb_path.name}: not in the env-split map — add it to CORE/LEGACY"
    assert declared == expected, (
        f"{nb_path.name}: declares kernel '{declared}', expected '{expected}' — kernelspec drift"
    )


@pytest.mark.parametrize("nb_path", NOTEBOOKS, ids=lambda p: p.name)
def test_notebook_runs(nb_path):
    nb = nbformat.read(nb_path, as_version=4)
    kernel = nb.metadata.get("kernelspec", {}).get("name", "python3")
    if kernel not in AVAILABLE_KERNELS:
        msg = (
            f"kernel '{kernel}' not registered (run `make kernels`); "
            f"available: {sorted(AVAILABLE_KERNELS)}"
        )
        if STRICT:
            pytest.fail(msg + "  [CMP_STRICT_KERNELS=1 — skips are failures in CI]")
        pytest.skip(msg)
    # 600s per cell (not 300): on a cold ~/.cache/cmp, 07b/11b's first loader cell
    # does a one-time dataset download (11b: the 311 MB Criteo file + one full parse).
    # Warm-cache runs stay well under the old 300s budget.
    client = NotebookClient(nb, timeout=600, kernel_name=kernel)
    client.execute()  # raises CellExecutionError on any cell failure
