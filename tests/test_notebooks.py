"""Execute every notebook headless in FAST mode and assert it runs clean.

Each notebook declares its own kernelspec (cmp-core for pymc>=6 notebooks,
cmp-legacy for the causalpy / pymc-marketing ones). nbclient launches that
kernel as a subprocess, so a single pytest process can drive both
environments — provided both kernels are registered (`make kernels`).

CMP_FAST=1 is forced so each notebook targets < ~2 min.
"""
import os
from pathlib import Path

import nbformat
import pytest
from nbclient import NotebookClient
from jupyter_client.kernelspec import KernelSpecManager

os.environ["CMP_FAST"] = "1"

NB_DIR = Path(__file__).resolve().parent.parent / "notebooks"
NOTEBOOKS = sorted(NB_DIR.glob("*.ipynb"))
AVAILABLE_KERNELS = set(KernelSpecManager().find_kernel_specs().keys())


@pytest.mark.parametrize("nb_path", NOTEBOOKS, ids=lambda p: p.name)
def test_notebook_runs(nb_path):
    nb = nbformat.read(nb_path, as_version=4)
    kernel = nb.metadata.get("kernelspec", {}).get("name", "python3")
    if kernel not in AVAILABLE_KERNELS:
        pytest.skip(
            f"kernel '{kernel}' not registered (run `make kernels`); "
            f"available: {sorted(AVAILABLE_KERNELS)}"
        )
    client = NotebookClient(nb, timeout=300, kernel_name=kernel)
    client.execute()  # raises CellExecutionError on any cell failure
