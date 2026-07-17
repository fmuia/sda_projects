"""A test run must not be able to damage the artifact it is testing.

`make test` executes all 14 notebooks with CMP_FAST=1. The mode stamp in the result shards
stops the book being typeset from FAST *numbers* — but `table()` and `figure()` used to write
into `book/build/` unconditionally, so a green FAST test run quietly replaced the 77 tables and
92 figure PDFs that the FULL prose is typeset around. The book would then build clean, and be
wrong. These guard that door: CMP_RESULTS_DIR must redirect the floats, not just the shards.
"""
import os
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import pytest

from cmp import report

BOOK_BUILD = Path(report.BUILD)


def _snapshot(d: Path) -> dict[str, float]:
    return {str(p): p.stat().st_mtime_ns for p in d.rglob("*") if p.is_file()}


@pytest.fixture
def redirected(tmp_path, monkeypatch):
    monkeypatch.setenv("CMP_RESULTS_DIR", str(tmp_path))
    return tmp_path


def test_table_respects_results_dir(redirected):
    before = _snapshot(BOOK_BUILD / "tables") if (BOOK_BUILD / "tables").exists() else {}
    report.table(pd.DataFrame({"a": [1], "b": [2]}), "nb00.isolation_probe",
                 caption="a table written during a test run")
    assert (redirected / "tables" / "nb00_isolation_probe.tex").exists(), \
        "table() did not write into CMP_RESULTS_DIR"
    after = _snapshot(BOOK_BUILD / "tables") if (BOOK_BUILD / "tables").exists() else {}
    assert after == before, "a test run wrote into book/build/tables — it can corrupt the book"


def test_figure_respects_results_dir(redirected):
    before = _snapshot(BOOK_BUILD / "figures") if (BOOK_BUILD / "figures").exists() else {}
    fig, ax = plt.subplots()
    ax.plot([0, 1], [0, 1])
    report.figure(fig, "nb00.isolation_probe", caption="a figure written during a test run")
    plt.close(fig)
    assert (redirected / "figures" / "nb00_isolation_probe.pdf").exists(), \
        "figure() did not write into CMP_RESULTS_DIR"
    after = _snapshot(BOOK_BUILD / "figures") if (BOOK_BUILD / "figures").exists() else {}
    assert after == before, "a test run wrote into book/build/figures — it can corrupt the book"


def test_legacy_results_json_is_refused_not_merged(tmp_path, monkeypatch):
    """The pre-shard single-file store used to be merged AFTER the shards, so it overrode every
    colliding key and carried no mode stamp. If one ever reappears, the book must refuse it."""
    shards, legacy = tmp_path / "results", tmp_path / "results.json"
    monkeypatch.setenv("CMP_RESULTS_DIR", str(shards))
    monkeypatch.setenv("CMP_FAST", "0")      # so the shard itself is not the thing flagged stale
    monkeypatch.setattr(report, "RESULTS", legacy)
    report.value("nb00.isolation_probe_scalar", 1.0)
    assert report.load()["nb00.isolation_probe_scalar"]["value"] == 1.0
    assert report.stale_shards() == [], "a clean FULL shard was flagged stale"

    legacy.write_text(
        '{"nb00.isolation_probe_scalar": {"value": 999.0, "text": "999", "unit": "", "note": ""}}')
    assert report.load()["nb00.isolation_probe_scalar"]["value"] == 1.0, \
        "a legacy results.json overrode a shard — the backdoor is open again"
    assert any("legacy" in s for s in report.stale_shards()), \
        "a legacy results.json is present and stale_shards() did not flag it"
