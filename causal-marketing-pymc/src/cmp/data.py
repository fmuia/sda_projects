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


# --------------------------------------------------------------------------
# Local cache for the larger real datasets (§7b, §11b)
# --------------------------------------------------------------------------
# The Criteo file is 311 MB and the Google geo CSVs are re-read on every
# notebook run, so unlike the tiny loaders above these cache to disk. The
# cache lives OUTSIDE the repo (which may sit in a synced folder — a 311 MB
# blob in Dropbox would churn forever): ~/.cache/cmp, overridable via
# CMP_DATA_HOME.

def _cache_dir() -> "Path":
    from pathlib import Path
    import os
    d = Path(os.environ.get("CMP_DATA_HOME", Path.home() / ".cache" / "cmp"))
    d.mkdir(parents=True, exist_ok=True)
    return d


def _fetch(url: str, dest_name: str, label: str) -> "Path":
    """Download url into the cache once; later calls hit the cached file."""
    from urllib.request import urlretrieve
    dest = _cache_dir() / dest_name
    if not dest.exists():
        print(f"[cmp.data] downloading {label} -> {dest} (one-time)")
        tmp = dest.with_suffix(dest.suffix + ".part")
        urlretrieve(url, tmp)
        tmp.rename(dest)
    return dest


# --------------------------------------------------------------------------
# Google `matched_markets` geo experiment (geo lift / synthetic control; §7b)
# --------------------------------------------------------------------------
# Pinned commit so the notebook is reproducible even if the repo moves.
GOOGLE_MM_SHA = "5e3cd957d9e3945b0446c94763f2f88b21f03ca5"
GOOGLE_MM_BASE = (
    "https://raw.githubusercontent.com/google/matched_markets/"
    f"{GOOGLE_MM_SHA}/matched_markets/csv/"
)


def load_google_geo() -> pd.DataFrame:
    """Google's example geo experiment (`salesandcost.csv` + `geoassignment.csv`
    from google/matched_markets): 100 US geos, daily sales in dollars,
    2015-01-05 → 2015-04-07. Geos were randomized into two groups; group 2
    (50 geos) received an ad campaign — $50,000 of spend, recorded in the
    `cost` column — during 2015-02-16 → 2015-03-15, group 1 stayed dark.
    This is the worked example behind Google's Time-Based-Regression geo
    methodology (Kerman, Wang & Vaver 2017).

    Returns a long dataframe: date, geo, sales, cost, group (1=control,
    2=treatment). 75 of 9,300 geo-days are missing at source (small geos,
    almost all pre-period) — left as-is here; the notebook interpolates and
    discloses.

    Licence: Apache 2.0 (google/matched_markets). We fetch a pinned commit,
    never vendor.
    """
    sales = pd.read_csv(
        _fetch(GOOGLE_MM_BASE + "salesandcost.csv", "google_geo_salesandcost.csv",
               "Google geo experiment sales/cost (~230 KB)"),
        parse_dates=["date"])
    assign = pd.read_csv(
        _fetch(GOOGLE_MM_BASE + "geoassignment.csv", "google_geo_geoassignment.csv",
               "Google geo experiment assignment (~1 KB)"))
    assign = assign.rename(columns={"geo.group": "group"})
    return sales.merge(assign, on="geo", validate="many_to_one")


# --------------------------------------------------------------------------
# Criteo uplift v2.1 (endogenous ad exposure / IV; §11b)
# --------------------------------------------------------------------------
CRITEO_URL = ("https://criteostorage.blob.core.windows.net/"
              "criteo-research-datasets/criteo-uplift-v2.1.csv.gz")


def load_criteo_uplift(n_per_arm: int = 100_000, seed: int = 11) -> pd.DataFrame:
    """Criteo uplift v2.1 (Diemert et al. 2018): 13.98M users from real ad
    incrementality tests. Columns: f0..f11 (anonymized user features),
    `treatment` (randomized: user targetable by the campaign), `exposure`
    (user actually saw an ad — self-selected via the auction/browsing),
    `visit` and `conversion` (outcomes). Exposure is one-sided: control
    users are never exposed.

    Because the full file is 311 MB and clustered by treatment (the head is
    all treated rows — a head-read is NOT a valid sample), this loader
    downloads it once, does one full pass, and caches a seeded subsample of
    `n_per_arm` treated + `n_per_arm` control rows, shuffled. Sampling on the
    randomized `treatment` alone cannot bias IV quantities (both E[Y|Z] and
    E[D|Z] are conditional on Z), and balancing the 85/15 arms roughly
    doubles precision per row. Later calls with the same (n_per_arm, seed)
    read the cached subsample directly.

    Licence: released by Criteo AI Lab for research use
    (https://ailab.criteo.com/criteo-uplift-prediction-dataset/); cite
    Diemert, Betlei, Renaudin & Amini (2018), "A Large Scale Benchmark for
    Uplift Modeling". We fetch and cache locally, never vendor.
    """
    import numpy as np
    sample_path = _cache_dir() / f"criteo-uplift-v2.1-sample-{n_per_arm}-seed{seed}.csv.gz"
    if sample_path.exists():
        return pd.read_csv(sample_path, dtype=np.float32)
    raw = _fetch(CRITEO_URL, "criteo-uplift-v2.1.csv.gz", "Criteo uplift v2.1 (311 MB)")
    print("[cmp.data] parsing the full 13.98M-row file to draw a balanced sample (~1 min)")
    chunks = [c for c in pd.read_csv(raw, chunksize=2_000_000, dtype=np.float32)]
    df = pd.concat(chunks, ignore_index=True)
    rng = np.random.default_rng(seed)
    idx_t = rng.choice(np.flatnonzero(df["treatment"].values == 1), n_per_arm, replace=False)
    idx_c = rng.choice(np.flatnonzero(df["treatment"].values == 0), n_per_arm, replace=False)
    sub = (df.iloc[np.concatenate([idx_t, idx_c])]
             .sample(frac=1, random_state=seed)      # shuffle so row order carries no arm signal
             .reset_index(drop=True))
    sub.to_csv(sample_path, index=False)
    return sub


def criteo_full_anchor() -> dict:
    """Design-based anchor from the FULL 13.98M-row Criteo file: the ITT,
    first stage, and Wald LATE on `visit` and `conversion`, computed exactly
    (no model, no subsample). At n=13.98M these are essentially free of
    sampling noise, so the notebook uses them as the closest real data gets
    to a 'planted truth' when grading the subsample estimates. Cached as a
    tiny JSON next to the raw file."""
    import json
    import numpy as np
    cache = _cache_dir() / "criteo-uplift-v2.1-anchor.json"
    if cache.exists():
        return json.loads(cache.read_text())
    raw = _fetch(CRITEO_URL, "criteo-uplift-v2.1.csv.gz", "Criteo uplift v2.1 (311 MB)")
    print("[cmp.data] one full pass over 13.98M rows for the design-based anchor (~1 min)")
    cols = ["treatment", "exposure", "visit", "conversion"]
    df = pd.concat([c for c in pd.read_csv(raw, usecols=cols, chunksize=4_000_000, dtype="int8")],
                   ignore_index=True)
    z = df["treatment"].values.astype(bool)
    d = df["exposure"].values.astype(float)
    dexp = d.astype(bool)                     # actually-exposed mask, for the as-treated (naive) gap
    first = float(d[z].mean() - d[~z].mean())
    out = {"n": int(len(df)), "first_stage": first,
           "p_exposed_treated": float(d[z].mean()), "p_exposed_control": float(d[~z].mean())}
    for y_col in ("visit", "conversion"):
        y = df[y_col].values.astype(float)
        itt = float(y[z].mean() - y[~z].mean())
        # naive = the as-treated exposed-vs-unexposed gap (what an attribution dashboard reports),
        # computed on the same full-file pass so the self-selection bias is grade-able, not hard-coded.
        naive = float(y[dexp].mean() - y[~dexp].mean())
        out[y_col] = {"base_control": float(y[~z].mean()), "itt": itt, "wald_late": itt / first,
                      "naive": naive}
    cache.write_text(json.dumps(out, indent=2))
    return out
