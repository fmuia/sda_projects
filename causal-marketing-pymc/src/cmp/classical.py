"""The Step-0 toolkit: classical (non-Bayesian) estimators, with honest inference.

Every notebook opens its estimation work with a **Step 0 · The classical read** — the
same estimand and the same identification strategy as the Bayesian section that follows,
estimated the simplest way that is still *correct*: a point estimate and an interval,
no likelihood, no priors, no sampler. The point is pedagogical scaffolding. The reader
meets the causal idea (what identifies the effect) before meeting the Bayesian machinery
(what a posterior is), instead of both at once.

Two rules this module exists to enforce:

1. **The standard error must be right.** An interval built on the wrong SE is worse than
   no interval: it is a confident lie. Panel/DiD estimates need cluster-robust SEs
   (Bertrand-Duflo-Mullainathan 2004: iid SEs on serially-correlated panels can be off
   by 5x+), time series need HAC, heteroskedastic cross-sections need HC1. So these
   wrappers make the covariance choice explicit and non-defaultable.
2. **A confidence interval is not a posterior.** Everything here returns a `Classical`
   result whose `.ci` is a *confidence* interval: a statement about the procedure (90% of
   intervals built this way cover the truth in repeated sampling), NOT a probability that
   the effect lies inside it. It cannot answer "what is P(lift > cost)?" — that question
   is native to a posterior, and answering it is the job of the Bayesian section. The
   `Classical.cannot_say()` helper prints that boundary, so the notebooks state it in one
   consistent voice rather than fudging it.

statsmodels does the covariance algebra (it is in both environments); this module keeps
the API small, the estimands explicit, and the interpretation honest.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

__all__ = [
    "Classical", "ols", "diff_in_means", "did_2x2", "event_study", "iv_2sls",
    "rd_local_linear", "segmented_its", "mediation_product", "bootstrap_ci",
    "no_pooling", "complete_pooling",
]


def _sm():
    """statsmodels, imported lazily so `import cmp` stays cheap and env-agnostic."""
    import statsmodels.api as sm
    return sm


@dataclass
class Classical:
    """A point estimate and a *confidence* interval — the classical answer, and its limits.

    `estimate` is the point estimate of `name` (the estimand); `se` its standard error
    under `cov` (the covariance assumption — always stated, never defaulted silently);
    `ci` the (1-alpha) confidence interval; `extra` holds method-specific diagnostics
    (first-stage F, bandwidth, n_clusters, ...).
    """
    name: str
    estimate: float
    se: float
    ci: tuple[float, float]
    alpha: float
    cov: str
    n: int
    extra: dict = field(default_factory=dict)

    @property
    def t(self) -> float:
        return self.estimate / self.se if self.se else np.nan

    @property
    def significant(self) -> bool:
        """Does the interval exclude zero? (A statement about the procedure, not a belief.)"""
        return (self.ci[0] > 0) or (self.ci[1] < 0)

    def __repr__(self) -> str:  # what the notebooks print
        lo, hi = self.ci
        pct = int(round((1 - self.alpha) * 100))
        return (f"{self.name}: {self.estimate:,.4g}  "
                f"[{pct}% CI {lo:,.4g}, {hi:,.4g}]  (SE {self.se:,.3g}, {self.cov}, n={self.n:,})")

    def line(self, unit: str = "") -> str:
        lo, hi = self.ci
        pct = int(round((1 - self.alpha) * 100))
        u = unit
        return (f"{self.estimate:,.2f}{u}  [{pct}% CI {lo:,.2f}{u}, {hi:,.2f}{u}]"
                f"  ·  SE {self.se:,.2f}  ·  {self.cov}")

    def cannot_say(self) -> str:
        """The one sentence every Step 0 must end on — said the same way every time."""
        pct = int(round((1 - self.alpha) * 100))
        return (
            f"What this {pct}% confidence interval does NOT say: that there is a {pct}% "
            f"probability the true effect lies inside it. It is a property of the "
            f"*procedure* — {pct}% of intervals built this way would cover the truth "
            f"across repeated samples. This interval either contains the truth or it "
            f"does not. To get a probability *about the effect itself* — the thing a "
            f"go/no-go rule like P(lift > cost) >= 0.9 actually needs — you need a "
            f"posterior. That is what the Bayesian section adds."
        )


def _ci(est, se, alpha, dof=None):
    from scipy import stats
    q = stats.t.ppf(1 - alpha / 2, dof) if dof else stats.norm.ppf(1 - alpha / 2)
    return (est - q * se, est + q * se)


def ols(df: pd.DataFrame, formula: str, target: str, *, cov: str = "HC1",
        cluster: str | None = None, maxlags: int | None = None,
        alpha: float = 0.10, name: str | None = None) -> Classical:
    """OLS with an explicit, honest covariance choice.

    cov: "HC1" (heteroskedasticity-robust, the cross-section default),
         "cluster" (needs `cluster=<column>` — use for panels: BDM),
         "HAC" (needs `maxlags` — use for time series),
         "nonrobust" (only when you can defend homoskedastic iid errors).
    `target` is the coefficient that *is* the causal estimand under the notebook's
    identification argument — naming it forces the analyst to say which one that is.
    """
    import statsmodels.formula.api as smf
    m = smf.ols(formula, data=df)
    if cov == "cluster":
        if cluster is None:
            raise ValueError("cov='cluster' requires cluster=<column name>")
        res = m.fit(cov_type="cluster", cov_kwds={"groups": df[cluster]})
        n_g = df[cluster].nunique()
        cov_label, extra = f"cluster-robust by {cluster} ({n_g} clusters)", {"n_clusters": n_g}
    elif cov == "HAC":
        if maxlags is None:
            raise ValueError("cov='HAC' requires maxlags=<int>")
        res = m.fit(cov_type="HAC", cov_kwds={"maxlags": maxlags})
        cov_label, extra = f"Newey-West HAC (maxlags={maxlags})", {"maxlags": maxlags}
    else:
        res = m.fit(cov_type=cov)
        cov_label, extra = ("HC1 heteroskedasticity-robust" if cov == "HC1" else cov), {}
    if target not in res.params.index:
        raise KeyError(f"{target!r} not in fitted coefficients: {list(res.params.index)}")
    est, se = float(res.params[target]), float(res.bse[target])
    extra["r2"] = float(res.rsquared)
    # A cluster-robust SE is only as good as the number of clusters, so the interval must be
    # built on t(G-1), not t(n-k). statsmodels knows this and exposes it as df_resid_inference;
    # passing res.df_resid instead made every clustered interval in the book ~9 % too narrow
    # (12 regions: t(11) = 1.796 against t(752) = 1.647). The point estimate is unaffected.
    dof = getattr(res, "df_resid_inference", res.df_resid)
    return Classical(name or target, est, se, _ci(est, se, alpha, dof),
                     alpha, cov_label, int(res.nobs), extra)


def diff_in_means(y, t, *, alpha: float = 0.10, name: str = "ATE (difference in means)") -> Classical:
    """The simplest estimator there is — valid under randomization, and nothing else.
    Welch SE (does not assume equal variances across arms)."""
    y, t = np.asarray(y, float), np.asarray(t).astype(bool)
    y1, y0 = y[t], y[~t]
    est = y1.mean() - y0.mean()
    se = np.sqrt(y1.var(ddof=1) / y1.size + y0.var(ddof=1) / y0.size)
    dof = se**4 / ((y1.var(ddof=1) / y1.size)**2 / (y1.size - 1)
                   + (y0.var(ddof=1) / y0.size)**2 / (y0.size - 1))
    return Classical(name, est, se, _ci(est, se, alpha, dof), alpha, "Welch (unequal variances)",
                     y.size, {"n_treated": int(y1.size), "n_control": int(y0.size)})


def did_2x2(df: pd.DataFrame, *, outcome: str, unit: str, time: str, treated: str,
            post: str, alpha: float = 0.10) -> Classical:
    """Canonical 2x2 difference-in-differences: y ~ treated + post + treated:post, with
    the interaction as the ATT. SEs clustered on `unit` — with serially-correlated panel
    outcomes, iid SEs are badly anti-conservative (Bertrand-Duflo-Mullainathan 2004)."""
    d = df.rename(columns={outcome: "_y", treated: "_g", post: "_p"})
    return ols(d, "_y ~ _g * _p", target="_g:_p", cov="cluster", cluster=unit,
               alpha=alpha, name="ATT (2x2 DiD, interaction term)")


def event_study(df: pd.DataFrame, *, outcome: str, unit: str, rel_time: str, treated: str,
                base: int = -1, alpha: float = 0.10) -> pd.DataFrame:
    """Two-way fixed-effects event study: leads and lags relative to `base` (normalised to
    0). Pre-period coefficients are the parallel-trends *evidence*; post-period ones are
    the dynamic ATT. Cluster-robust on `unit`. Returns a tidy frame (k, estimate, se, lo, hi)."""
    import statsmodels.formula.api as smf
    from scipy import stats
    d = df.copy()
    d["_k"] = d[rel_time].astype(int)
    d["_int"] = d[treated].astype(int)
    ks = sorted(k for k in d["_k"].unique() if k != base)
    # patsy chokes on "-" in a term name (it reads _d-4 as subtraction), so encode the
    # sign: m = minus (lead), p = plus (lag).
    col = {k: f"_d{'m' if k < 0 else 'p'}{abs(k)}" for k in ks}
    for k in ks:
        d[col[k]] = ((d["_k"] == k) & (d["_int"] == 1)).astype(int)
    terms = " + ".join(col[k] for k in ks)
    res = smf.ols(f"{outcome} ~ {terms} + C({unit}) + C(_k)", data=d).fit(
        cov_type="cluster", cov_kwds={"groups": d[unit]})
    # t(G-1), not the normal quantile: the event-study bands are read as parallel-trends
    # evidence, and a band that is too narrow manufactures a pre-trend violation that is not there.
    q = stats.t.ppf(1 - alpha / 2, getattr(res, "df_resid_inference", res.df_resid))
    rows = [{"k": base, "estimate": 0.0, "se": 0.0, "lo": 0.0, "hi": 0.0, "is_base": True}]
    for k in ks:
        e, s = float(res.params[col[k]]), float(res.bse[col[k]])
        rows.append({"k": k, "estimate": e, "se": s, "lo": e - q * s, "hi": e + q * s,
                     "is_base": False})
    return pd.DataFrame(rows).sort_values("k").reset_index(drop=True)


def iv_2sls(df: pd.DataFrame, *, outcome: str, endog: str, instrument: str,
            controls: list[str] | None = None, alpha: float = 0.10,
            cov: str = "HC1", cluster: str | None = None) -> Classical:
    """Two-stage least squares — the classical IV workhorse, with proper 2SLS standard
    errors and the first-stage F.

    The SE subtlety, stated in the direction the algebra actually gives (an earlier version
    of this docstring asserted the opposite and a notebook caught it by *computing* it):
    if you run 2SLS by hand — regress X on Z to get X_hat, then OLS y on X_hat — the point
    estimate is right but the reported SE is WRONG, and it is wrong by being TOO WIDE.
    The residual must be formed against the ORIGINAL X, not X_hat:

        y - X_hat b = (y - X b) + (X - X_hat) b = u_hat + v_hat b

    so SSR_naive = SSR_correct + b^2 * sum(v_hat^2) + cross >= SSR_correct whenever b != 0.
    The hand-rolled second stage therefore charges itself for first-stage prediction error
    that is not part of the structural noise, and reports a conservative (too-wide) interval.
    This function forms the residual against the original X, which is the 2SLS rule.

    Rule of thumb: first-stage F < 10 means a weak instrument — the 2SLS estimate is then
    biased back toward OLS and its interval should not be trusted (see `extra["weak"]`).
    """
    ctrl = controls or []
    X_cols = [endog] + ctrl
    Z_cols = [instrument] + ctrl
    y = df[outcome].to_numpy(float)
    X = np.column_stack([np.ones(len(df))] + [df[c].to_numpy(float) for c in X_cols])
    Z = np.column_stack([np.ones(len(df))] + [df[c].to_numpy(float) for c in Z_cols])
    # 2SLS: b = (X'P_Z X)^-1 X'P_Z y, with P_Z the projection onto Z
    ZtZ_inv = np.linalg.pinv(Z.T @ Z)
    Pz_X = Z @ (ZtZ_inv @ (Z.T @ X))
    A = np.linalg.pinv(Pz_X.T @ X)
    b = A @ (Pz_X.T @ y)
    resid = y - X @ b                      # residuals use the ORIGINAL X (the 2SLS rule)
    n, k = X.shape

    # This module's whole discipline is that an estimator may not default its covariance choice in
    # silence — and this function used to do exactly that, hard-coding homoskedastic 2SLS. The
    # sandwich is V = A * meat * A', with A = (X'P_Z X)^-1 and the meat built from P_Z X and the
    # 2SLS residuals. `cov` now has to be chosen, exactly as in `ols`.
    A = np.linalg.pinv(Pz_X.T @ X)
    dof = n - k
    if cov == "cluster":
        if cluster is None:
            raise ValueError("cov='cluster' requires cluster=<column name>")
        g = df[cluster].to_numpy()
        meat = np.zeros((k, k))
        for lvl in np.unique(g):
            m = g == lvl
            sg = Pz_X[m].T @ resid[m]                       # score summed within the cluster
            meat += np.outer(sg, sg)
        n_g = len(np.unique(g))
        # the small-sample correction statsmodels uses, and the dof that matters is G-1, not n-k
        meat *= (n_g / max(n_g - 1, 1)) * ((n - 1) / max(n - k, 1))
        V = A @ meat @ A.T
        dof = n_g - 1
        cov_label, extra = f"cluster-robust by {cluster} ({n_g} clusters)", {"n_clusters": n_g}
    elif cov == "nonrobust":
        s2 = (resid @ resid) / (n - k)
        V = s2 * np.linalg.pinv(Pz_X.T @ Pz_X)
        cov_label, extra = "2SLS (homoskedastic)", {}
    else:                                                   # HC1, the default
        meat = (Pz_X * (resid ** 2)[:, None]).T @ Pz_X
        meat *= n / max(n - k, 1)                           # HC1 finite-sample correction
        V = A @ meat @ A.T
        cov_label, extra = "2SLS, HC1 heteroskedasticity-robust", {}

    est, se = float(b[1]), float(np.sqrt(V[1, 1]))
    # first stage: endog ~ instrument + controls; F on the excluded instrument
    import statsmodels.api as sm
    fs = sm.OLS(df[endog].to_numpy(float), Z).fit()
    F = float(fs.tvalues[1] ** 2)          # single instrument: F = t^2
    extra.update({"first_stage_F": F, "weak": F < 10,
                  "first_stage_coef": float(fs.params[1])})
    return Classical("LATE (2SLS)", est, se, _ci(est, se, alpha, dof), alpha, cov_label, n, extra)


def rd_local_linear(df: pd.DataFrame, *, outcome: str, running: str, cutoff: float,
                    bandwidth: float, kernel: str = "triangular",
                    alpha: float = 0.10) -> Classical:
    """Sharp RD by local linear regression inside a bandwidth, fitted separately on each
    side (the standard specification: allowing different slopes left and right). The
    estimand is the jump at the cutoff — a LATE *at* the threshold, and nowhere else.
    Triangular kernel weights (down-weight far-from-cutoff points) by default."""
    d = df.copy()
    d["_c"] = d[running] - cutoff
    d = d[np.abs(d["_c"]) <= bandwidth].copy()
    d["_r"] = (d["_c"] >= 0).astype(int)
    if kernel == "triangular":
        d["_w"] = 1 - np.abs(d["_c"]) / bandwidth
    else:
        d["_w"] = 1.0
    import statsmodels.formula.api as smf
    res = smf.wls(f"{outcome} ~ _r * _c", data=d, weights=d["_w"]).fit(cov_type="HC1")
    est, se = float(res.params["_r"]), float(res.bse["_r"])
    return Classical(f"RD jump at {running}={cutoff:g}", est, se,
                     _ci(est, se, alpha, res.df_resid), alpha,
                     f"HC1, local linear, {kernel} kernel, h={bandwidth:g}", int(res.nobs),
                     {"bandwidth": bandwidth, "n_left": int((d["_r"] == 0).sum()),
                      "n_right": int((d["_r"] == 1).sum())})


def segmented_its(df: pd.DataFrame, *, outcome: str, time: str, intervention: float,
                  maxlags: int = 7, season: int | None = None,
                  alpha: float = 0.10) -> dict[str, Classical]:
    """Segmented (interrupted) time-series regression: a level shift AND a slope change at
    the intervention, with Newey-West HAC standard errors — daily/weekly series are
    autocorrelated, and iid SEs would make the effect look far more precise than it is.
    `season` adds a Fourier pair of that period. Returns {"level": ..., "slope": ...}."""
    d = df.copy()
    d["_t"] = d[time].astype(float)
    d["_post"] = (d["_t"] >= intervention).astype(int)
    d["_since"] = np.clip(d["_t"] - intervention, 0, None)
    terms = "_t + _post + _since"
    if season:
        d["_s1"] = np.sin(2 * np.pi * d["_t"] / season)
        d["_c1"] = np.cos(2 * np.pi * d["_t"] / season)
        terms += " + _s1 + _c1"
    out = {}
    for key, target, label in (("level", "_post", "Level shift at the intervention"),
                               ("slope", "_since", "Slope change after the intervention")):
        out[key] = ols(d, f"{outcome} ~ {terms}", target=target, cov="HAC",
                       maxlags=maxlags, alpha=alpha, name=label)
    return out


def mediation_product(df: pd.DataFrame, *, outcome: str, treatment: str, mediator: str,
                      controls: list[str] | None = None, n_boot: int = 2000,
                      alpha: float = 0.10, seed: int = 0) -> dict[str, Classical]:
    """Baron-Kenny / product-of-coefficients mediation, the classical decomposition:

        M ~ a*T + controls          (treatment -> mediator)
        Y ~ c*T + b*M + controls    (both -> outcome, holding the other fixed)
        indirect (NIE) = a*b,  direct (NDE) = c,  total = a*b + c

    The indirect effect is a *product* of two estimates, so its sampling distribution is
    not normal and the delta-method SE is only a first-order approximation — hence a
    nonparametric bootstrap interval, which is what the applied literature uses.
    NOTE the causal content is NOT in the algebra: a*b is the NIE only under sequential
    ignorability (no unmeasured mediator-outcome confounding), which no regression can
    check. Same estimand, same assumption, as the Bayesian section.
    """
    ctrl = controls or []
    cs = (" + " + " + ".join(ctrl)) if ctrl else ""
    import statsmodels.formula.api as smf

    def _fit(data):
        ma = smf.ols(f"{mediator} ~ {treatment}{cs}", data=data).fit()
        my = smf.ols(f"{outcome} ~ {treatment} + {mediator}{cs}", data=data).fit()
        a, b, c = ma.params[treatment], my.params[mediator], my.params[treatment]
        return a * b, c, a * b + c

    nie, nde, tot = _fit(df)
    rng = np.random.default_rng(seed)
    boots = np.array([_fit(df.iloc[rng.integers(0, len(df), len(df))]) for _ in range(n_boot)])
    lo, hi = np.percentile(boots, [100 * alpha / 2, 100 * (1 - alpha / 2)], axis=0)
    se = boots.std(axis=0, ddof=1)
    names = ("NIE (indirect, a*b)", "NDE (direct, c)", "Total effect")
    return {k: Classical(nm, float(e), float(s), (float(l), float(h)), alpha,
                         f"nonparametric bootstrap ({n_boot} resamples)", len(df))
            for k, nm, e, s, l, h in zip(("nie", "nde", "total"), names,
                                         (nie, nde, tot), se, lo, hi)}


def bootstrap_ci(data, stat, *, n_boot: int = 2000, alpha: float = 0.10, seed: int = 0,
                 name: str = "statistic") -> Classical:
    """Percentile bootstrap for any statistic — the classical escape hatch when no closed
    form exists. It is still a *confidence* interval: resampling the data approximates the
    sampling distribution of the estimator, not a distribution of belief over the
    parameter. It cannot be read as P(effect in range)."""
    arr = np.asarray(data)
    rng = np.random.default_rng(seed)
    est = float(stat(arr))
    boots = np.array([float(stat(arr[rng.integers(0, len(arr), len(arr))])) for _ in range(n_boot)])
    lo, hi = np.percentile(boots, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    return Classical(name, est, float(boots.std(ddof=1)), (float(lo), float(hi)), alpha,
                     f"percentile bootstrap ({n_boot} resamples)", len(arr))


def no_pooling(df: pd.DataFrame, *, formula: str, target: str, group: str,
               cov: str = "HC1", alpha: float = 0.10) -> pd.DataFrame:
    """Fit the model SEPARATELY in each group — the classical "no pooling" arm. Every group
    is estimated from its own data alone, so thin groups get wild, wide estimates: this is
    precisely the noise that Bayesian partial pooling shrinks. Returns a tidy frame."""
    rows = []
    for g, d in df.groupby(group):
        try:
            r = ols(d, formula, target=target, cov=cov, alpha=alpha)
            rows.append({group: g, "n": r.n, "estimate": r.estimate, "se": r.se,
                         "lo": r.ci[0], "hi": r.ci[1], "width": r.ci[1] - r.ci[0]})
        except Exception as e:  # a group too thin to identify the coefficient at all
            rows.append({group: g, "n": len(d), "estimate": np.nan, "se": np.nan,
                         "lo": np.nan, "hi": np.nan, "width": np.nan, "error": str(e)[:40]})
    return pd.DataFrame(rows)


def complete_pooling(df: pd.DataFrame, *, formula: str, target: str, cov: str = "HC1",
                     alpha: float = 0.10) -> Classical:
    """One estimate for everyone — the classical "complete pooling" arm. Maximally precise
    and maximally wrong if the groups genuinely differ: it assumes the effect is identical
    everywhere. The two classical arms (this and `no_pooling`) bracket the bias-variance
    trade-off that partial pooling interpolates between."""
    return ols(df, formula, target=target, cov=cov, alpha=alpha,
               name="Pooled effect (complete pooling)")
