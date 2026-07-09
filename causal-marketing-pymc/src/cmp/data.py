"""Optional loaders for canonical public datasets.

Simulated data (cmp.dgp) is the default everywhere so the whole repo runs
offline and reproducibly. These loaders let a notebook toggle simulated ->
real. We deliberately do NOT vendor the data — each loader fetches from a
public URL and documents the licence. Network access is required only when
you call one of these.
"""
from __future__ import annotations

import pandas as pd

# --------------------------------------------------------------------------
# Hillstrom / MineThatData email campaign (uplift; §1, §2)
# --------------------------------------------------------------------------
# NB: plain http — the minethatdata.com host does not serve this file over TLS.
# The data is a public teaching CSV (no credentials, integrity not security-
# critical); pass your own https mirror as `url=` if your environment blocks http.
HILLSTROM_URL = "http://www.minethatdata.com/Kevin_Hillstrom_MineThatData_E-MailAnalytics_DataMiningChallenge_2008.03.20.csv"


def load_hillstrom(url: str = HILLSTROM_URL) -> pd.DataFrame:
    """Kevin Hillstrom's MineThatData email challenge: 64k customers
    randomly assigned to Mens email / Womens email / no email, with
    downstream visit, conversion and spend.

    A genuine randomized experiment, so it is the natural real-data swap-in
    for the uplift notebooks (unconfoundedness by design). Treatment column
    `segment`; outcomes `visit`, `conversion`, `spend`.

    Licence: released publicly by Kevin Hillstrom / MineThatData for the
    2008 email analytics challenge, free to use for research and teaching.
    Original: minethatdata.com. We fetch, never vendor.
    """
    df = pd.read_csv(url)
    df.columns = [c.strip().lower() for c in df.columns]
    return df


def hillstrom_binary_treatment(df: pd.DataFrame, treat_segment: str = "Womens E-Mail") -> pd.DataFrame:
    """Reduce the 3-arm Hillstrom data to a binary treatment: the chosen
    email segment vs 'No E-Mail'. Adds columns T (1/0) and keeps `spend`,
    `conversion`, `visit` plus the pre-treatment covariates."""
    seg = "segment"
    keep = df[df[seg].isin([treat_segment, "No E-Mail"])].copy()
    keep["T"] = (keep[seg] == treat_segment).astype(float)
    return keep


def hillstrom_uplift(treat_segment: str = "Womens E-Mail", outcome: str = "spend"):
    """One-liner real-data swap for the uplift notebooks. Fetches Hillstrom,
    reduces to a binary email/no-email treatment, numerically encodes the
    pre-treatment covariates, and returns everything the uplift pipeline
    needs — EXCEPT a ground-truth effect, because on real data the individual
    treatment effect is unobservable (that is the whole point of the field).

    Returns dict with X (n, p) float array, T (n,) 0/1, y (n,) outcome,
    feature_names, and a note. Because the assignment was randomized, the ATE
    is trustworthy without adjustment; there is simply no per-customer truth
    to validate a CATE against — use `load_ihdp` for that.
    """
    df = hillstrom_binary_treatment(load_hillstrom(), treat_segment=treat_segment)
    # pre-treatment covariates only (never post-treatment: visit/conversion are outcomes)
    feats = ["recency", "history", "mens", "womens", "newbie"]
    X = df[feats].astype(float).values
    return {
        "X": X, "T": df["T"].values.astype(float), "y": df[outcome].values.astype(float),
        "feature_names": feats, "n": len(df),
        "note": ("Real randomized email experiment (Hillstrom/MineThatData, 2008). "
                 "Randomized, so the ATE is unbiased without adjustment; no ground-truth "
                 "per-customer effect exists to validate CATE recovery."),
    }


# --------------------------------------------------------------------------
# LaLonde / NSW (classic observational-vs-experimental benchmark; §5)
# --------------------------------------------------------------------------
# The *randomized* NSW experimental file (Dehejia–Wahba .dta) lives at
# https://users.nber.org/~rdehejia/data/nsw_dw.dta — deliberately NOT loaded
# here (the notebooks use the observational CSV below). Kept as a note rather
# than a dead constant, so nothing implies an experimental-benchmark loader that
# doesn't exist; wire one up if you want the full experimental-vs-observational
# comparison.
LALONDE_CSV_URL = "https://raw.githubusercontent.com/robjellis/lalonde/master/lalonde_data.csv"


def load_lalonde(url: str = LALONDE_CSV_URL) -> pd.DataFrame:
    """The LaLonde / Dehejia-Wahba NSW job-training dataset — the canonical
    testbed for whether covariate adjustment on observational controls can
    recover an experimental benchmark (~$1,800 earnings effect). Treatment
    `treat`; outcome `re78` (1978 earnings); covariates age, education,
    race, marital status, prior earnings re74/re75.

    Licence: public, from Dehejia & Wahba / LaLonde; widely redistributed
    for teaching (e.g. R's MatchIt). We fetch, never vendor.
    """
    df = pd.read_csv(url)
    df.columns = [c.strip().lower() for c in df.columns]
    return df


# --------------------------------------------------------------------------
# IHDP (heterogeneous-effect benchmark; §1)
# --------------------------------------------------------------------------
IHDP_URL = "https://raw.githubusercontent.com/AMLab-Amsterdam/CEVAE/master/datasets/IHDP/csv/ihdp_npci_1.csv"


def load_ihdp(url: str = IHDP_URL) -> pd.DataFrame:
    """Infant Health and Development Program semi-synthetic benchmark: real
    covariates with simulated outcomes, so the *true* individual effect is
    known — the standard CATE/PEHE benchmark. Columns: treatment, y_factual,
    y_cfactual, mu0, mu1, then 25 covariates x1..x25.

    Licence: the semi-synthetic IHDP setup (Hill 2011) is distributed
    openly for causal-ML benchmarking. We fetch, never vendor.
    """
    cols = ["treatment", "y_factual", "y_cfactual", "mu0", "mu1"] + [f"x{i}" for i in range(1, 26)]
    df = pd.read_csv(url, header=None)
    df.columns = cols
    return df
