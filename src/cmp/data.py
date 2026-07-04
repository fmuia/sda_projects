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
HILLSTROM_URL = "https://raw.githubusercontent.com/dmitrykazhdan/uplift-modelling-datasets/master/Hillstrom.csv"
_HILLSTROM_ALT = "http://www.minethatdata.com/Kevin_Hillstrom_MineThatData_E-MailAnalytics_DataMiningChallenge_2008.03.20.csv"


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


# --------------------------------------------------------------------------
# LaLonde / NSW (classic observational-vs-experimental benchmark; §5)
# --------------------------------------------------------------------------
LALONDE_NSW_URL = "https://users.nber.org/~rdehejia/data/nsw_dw.dta"
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
