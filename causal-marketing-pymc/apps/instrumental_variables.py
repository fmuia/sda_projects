"""Instrumental-variables explorer (marimo) — self-selection, the first-stage F, and the euro cap.

The companion to Chapter 13. An ad platform targets the users already likely to convert, so the
naive exposed-vs-unexposed gap is inflated by the buyers' own intent. A randomized encouragement
(a serving-priority lottery) instruments the exposure. Move the sliders and watch three things at
once: how far OLS drifts above the truth as confounding grows, how the first-stage F decides whether
the instrument can fix it, and where the defensible bid cap lands.

WASM-SAFE: imports only numpy / scipy / matplotlib (all present in Pyodide). It must NOT import
`cmp` — local packages cannot be installed in the browser. The IV world, the estimators and the
decision are all defined inline, and nothing is sampled: the estimator is closed-form (two
least-squares slopes and a division), so every slider is instant. The probability the effect clears
its cost is read off the 2SLS sampling distribution, which Bernstein-von Mises says the Bayesian
posterior matches at this sample size (Chapter 13, section 13.8).

Run:    marimo run apps/instrumental_variables.py       (read-only app)
Edit:   marimo edit apps/instrumental_variables.py       (notebook)
Ship:   marimo export html-wasm apps/instrumental_variables.py -o site/instrumental_variables --mode run
"""
import marimo

app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import numpy as np
    import matplotlib.pyplot as plt
    from scipy import stats

    # Repo visual language, inlined (cmp.plots is unavailable in the browser).
    BLUE, GREEN, ORANGE, GOLD, GREY = "#2c7fb8", "#238b45", "#d95f0e", "#e6a817", "#999999"
    plt.rcParams.update({
        "figure.dpi": 130, "font.size": 9.5,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": True, "grid.alpha": 0.25,
        "axes.titlesize": 10.5, "axes.titleweight": "bold",
    })
    TRUE = 15.0   # the planted per-exposure effect (euros); the grade every estimator is marked on
    return BLUE, GOLD, GREEN, GREY, ORANGE, TRUE, mo, np, plt, stats


@app.cell
def _(mo):
    mo.md(
        r"""
        # Ad exposure is self-selected: what an exposure is really worth

        The platform shows ads to the people most likely to buy, so the exposed would have converted
        more **with or without the ad**. The naive exposed-vs-unexposed gap credits the ad with that
        intent. A randomized **encouragement** $Z$ (a serving-priority lottery, not an ad) moves
        exposure without touching intent, and the effect is the ratio

        $$\hat\beta_{\text{IV}} \;=\; \frac{\text{what the lottery did to sales}}{\text{what the lottery did to exposure}} \;=\; \frac{\hat\delta}{\hat\pi}.$$

        Three sliders below. **Confounding** is how hard the platform chases intent (it inflates OLS).
        **Instrument strength** is how firmly the lottery moves exposure (it sets the first-stage $F$).
        **Cost** is what you would pay per exposure. Watch the naive number, the causal number, and
        the bid cap move.
        """
    )
    return


@app.cell
def _(mo):
    gamma = mo.ui.slider(0.05, 2.0, value=1.1, step=0.05,
                         label="Instrument strength $\\gamma$ (lottery $\\to$ exposure)")
    kappa = mo.ui.slider(0.0, 24.0, value=12.0, step=1.0,
                         label="Confounding $\\kappa$ (intent $\\to$ sales, €)")
    cost = mo.ui.slider(4.0, 22.0, value=10.0, step=0.5, label="Cost per exposure $c$ (€)")
    n = mo.ui.slider(1000, 20000, value=3000, step=500, label="Customers $n$")
    return cost, gamma, kappa, n


@app.cell
def _(cost, gamma, kappa, mo, n):
    mo.hstack([mo.vstack([gamma, kappa]), mo.vstack([cost, n])], justify="start", gap=2)
    return


@app.cell
def _(np):
    # --- the IV world and its estimators, inlined (mirrors cmp.dgp.iv_ad_exposure +
    # cmp.classical.iv_2sls; WASM-safe, closed-form, no sampler). Held at a fixed seed so the
    # picture is stable per (gamma, kappa, n): what moves is the mechanism, not the noise. ---
    def _sigmoid(z):
        return 1.0 / (1.0 + np.exp(-z))

    def fit_iv(gamma, kappa, n, seed=37, a0=0.3, lam=0.8, mu=50.0, beta=15.0, sigma=6.0):
        rng = np.random.default_rng(seed)
        U = rng.normal(0, 1, n)                       # unobserved intent (the confounder)
        Z = rng.integers(0, 2, n).astype(float)       # randomized encouragement (the instrument)
        X = (rng.uniform(size=n) < _sigmoid(a0 + gamma * Z + lam * U)).astype(float)
        Y = mu + beta * X + kappa * U + rng.normal(0, sigma, n)

        def slope(x, y):                               # OLS slope of y on x, with intercept
            D = np.column_stack([np.ones(len(x)), x])
            b = np.linalg.lstsq(D, y, rcond=None)[0]
            return b, D

        b_ols, _ = slope(X, Y); naive = float(b_ols[1])
        b_fs, Zd = slope(Z, X); pi = float(b_fs[1])
        b_rf, _ = slope(Z, Y); delta = float(b_rf[1])
        wald = delta / pi if pi != 0 else np.nan

        # first-stage F for a single instrument: the squared t of the Z coefficient
        xhat = Zd @ b_fs
        rss_fs = float(np.sum((X - xhat) ** 2))
        var_pi = rss_fs / (n - 2) / float(np.sum((Z - Z.mean()) ** 2))
        F = float(pi ** 2 / var_pi) if var_pi > 0 else np.inf

        # proper 2SLS standard error (residuals vs the REAL X, projected design vs Xhat)
        Xm = np.column_stack([np.ones(n), X]); Xh = np.column_stack([np.ones(n), xhat])
        b2 = np.linalg.solve(Xh.T @ Xm, Xh.T @ Y)      # == [b0, wald]
        resid = Y - Xm @ b2
        s2 = float(resid @ resid) / (n - 2)
        cov2 = s2 * np.linalg.inv(Xh.T @ Xh)
        se = float(np.sqrt(cov2[1, 1]))
        return dict(naive=naive, pi=pi, delta=delta, wald=float(b2[1]), F=F, se=se,
                    fs_lo=float(X[Z == 0].mean()), fs_hi=float(X[Z == 1].mean()))
    return (fit_iv,)


@app.cell
def _(TRUE, cost, fit_iv, gamma, kappa, mo, n, stats):
    _r = fit_iv(gamma.value, kappa.value, int(n.value))
    _c = cost.value
    # decision on the 2SLS sampling distribution (= the posterior, by Bernstein-von Mises):
    _p_pays = float(1 - stats.norm.cdf((_c - _r["wald"]) / _r["se"]))
    _cap = float(_r["wald"] + stats.norm.ppf(0.10) * _r["se"])     # 90%-probability bid cap
    _strong = _r["F"] >= 10

    _fverdict = (
        f"✅ **Strong instrument** ($F = {_r['F']:,.0f}$, well past 10). The $1/F$ rule prices the "
        f"residual OLS-bias leakage into 2SLS at about **€{abs(_r['naive']-TRUE)/max(_r['F'],1e-9):.2f}** "
        f"per exposure: negligible."
        if _strong else
        f"⚠️ **Weak instrument** ($F = {_r['F']:.1f} < 10$). The Wald denominator is near zero, so the "
        f"ratio inherits OLS's bias **and** an enormous variance. A weak instrument is worse than "
        f"none: the estimate below is wearing the costume of a causal number. Do not bid on it."
    )
    _dverdict = (
        f"✅ **BUY** to the complier margin: $P(\\beta > c) = {_p_pays:.2f} \\ge 0.90$."
        if _p_pays >= 0.90 else
        (f"🟡 **TEST FURTHER**: $P(\\beta > c) = {_p_pays:.2f}$ (between 0.5 and 0.9)."
         if _p_pays >= 0.5 else
         f"⛔ **NO-GO**: $P(\\beta > c) = {_p_pays:.2f} < 0.5$.")
    )

    mo.md(
        f"""
        | quantity | value |
        |---|---|
        | Naive OLS (the dashboard number) | **€{_r['naive']:.1f}** / exposure |
        | Wald ratio = 2SLS (the causal number) | **€{_r['wald']:.1f}** &nbsp;(±€{1.645*_r['se']:.1f}, 90%) |
        | Planted truth | €{TRUE:.0f} |
        | Self-selection wedge (naive − causal) | **€{_r['naive']-_r['wald']:.1f}** / exposure |
        | First stage: exposure rate {100*_r['fs_lo']:.0f}% → {100*_r['fs_hi']:.0f}% | complier share ≈ **{100*_r['pi']:.0f}%** |
        | First-stage $F$ | **{_r['F']:,.0f}** |
        | $P(\\text{{effect}} > c)$ at €{_c:.1f} | **{_p_pays:.2f}** |
        | Defensible bid cap (90% bar) | **€{_cap:.1f}** / exposure |

        {_fverdict}

        {_dverdict}
        """
    )
    return


@app.cell
def _(BLUE, GOLD, GREEN, GREY, ORANGE, TRUE, cost, fit_iv, gamma, kappa, n, np, plt, stats):
    _r = fit_iv(gamma.value, kappa.value, int(n.value))
    _c = cost.value
    fig, (axL, axR) = plt.subplots(1, 2, figsize=(10.6, 3.9))

    # LEFT: OLS vs 2SLS vs truth, on one number line — the wedge is the horizontal gap.
    _lo = min(TRUE, _r["wald"], _r["naive"]) - 3
    _hi = max(TRUE, _r["wald"], _r["naive"]) + 3
    axL.axvspan(_r["wald"] - 1.645 * _r["se"], _r["wald"] + 1.645 * _r["se"],
                color=BLUE, alpha=0.15, label="2SLS 90% interval")
    axL.axvline(TRUE, color="black", ls="--", lw=1.3, label=f"truth €{TRUE:.0f}")
    axL.axvline(_r["naive"], color=ORANGE, lw=2.2, label=f"naive OLS €{_r['naive']:.1f}")
    axL.axvline(_r["wald"], color=BLUE, lw=2.2, label=f"Wald / 2SLS €{_r['wald']:.1f}")
    axL.axvline(_c, color=GREY, lw=1.4, ls=":", label=f"cost €{_c:.1f}")
    axL.annotate("", xy=(_r["naive"], 0.5), xytext=(_r["wald"], 0.5),
                 arrowprops=dict(arrowstyle="<->", color=GREY, lw=1.2))
    axL.text((_r["naive"] + _r["wald"]) / 2, 0.56, f"wedge €{_r['naive']-_r['wald']:.1f}",
             ha="center", fontsize=8, color="0.3")
    axL.set_xlim(_lo, _hi); axL.set_ylim(0, 1); axL.set_yticks([])
    axL.set_xlabel("effect of an exposure on sales (€)")
    axL.set_title("Self-selection, and the slice IV removes")
    axL.legend(fontsize=7.2, loc="upper left", framealpha=0.9)

    # RIGHT: P(effect > c) as the cost sweeps — the cap is where it crosses 0.90.
    _grid = np.linspace(_lo, _hi, 300)
    _p = 1 - stats.norm.cdf((_grid - _r["wald"]) / _r["se"])
    _cap = _r["wald"] + stats.norm.ppf(0.10) * _r["se"]
    _coin = _r["wald"]
    axR.plot(_grid, _p, color=BLUE, lw=2)
    axR.axhline(0.90, color="black", ls="--", lw=0.9)
    axR.axvline(_cap, color=GREEN, ls=":", lw=1.4, label=f"cap €{_cap:.1f} (P=0.9)")
    axR.axvline(_coin, color=GOLD, ls=":", lw=1.4, label=f"coin flip €{_coin:.1f}")
    axR.axvline(_c, color=ORANGE, lw=1.6, label=f"your cost €{_c:.1f}")
    axR.set_xlim(_lo, _hi); axR.set_ylim(0, 1.02)
    axR.set_xlabel("assumed cost per exposure (€)")
    axR.set_ylabel("P(exposure pays)")
    axR.set_title("The bid cap is a 90% probability bar")
    axR.legend(fontsize=7.2, loc="lower left", framealpha=0.9)

    fig.tight_layout()
    fig
    return


@app.cell
def _(mo):
    mo.md(
        r"""
        ---
        ### The weak-instrument trap, in one slider

        Slide **instrument strength $\gamma$** toward zero and watch the first-stage $F$ fall through
        10. Two things happen at once, and only one is obvious. The 2SLS interval balloons (obvious).
        And the point estimate drifts back **up toward the biased OLS number** (not obvious), because a
        near-zero denominator $\hat\pi$ makes the ratio unstable. That is why *a weak instrument is
        worse than none*: OLS is wrong by a known amount with a tight interval; a weak IV can be wrong
        by multiples of the effect while still looking like a causal estimate.

        Below, $F$ is swept by $\gamma$ with everything else at your current settings, so you can see
        exactly where the estimator comes apart.
        """
    )
    return


@app.cell
def _(BLUE, GREY, ORANGE, TRUE, fit_iv, kappa, n, np, plt):
    # Sweep the instrument strength; median Wald and its spread across fresh draws at each gamma.
    _gs = np.linspace(0.05, 1.6, 22)
    _med, _lo, _hi, _Fs = [], [], [], []
    for _g in _gs:
        _ws = []
        for _sd in range(40):
            _rr = fit_iv(_g, kappa.value, int(n.value), seed=200 + _sd)
            _ws.append(_rr["wald"])
        _ws = np.array(_ws)
        _med.append(np.median(_ws)); _lo.append(np.quantile(_ws, 0.05)); _hi.append(np.quantile(_ws, 0.95))
        _Fs.append(fit_iv(_g, kappa.value, int(n.value))["F"])
    _med, _lo, _hi, _Fs = map(np.array, (_med, _lo, _hi, _Fs))

    _naive_ref = fit_iv(1.1, kappa.value, int(n.value))["naive"]
    fig2, ax = plt.subplots(figsize=(7.2, 3.6))
    ax.fill_between(_Fs, np.clip(_lo, -40, 100), np.clip(_hi, -40, 100), color=BLUE, alpha=0.18,
                    label="90% range across draws")
    ax.plot(_Fs, np.clip(_med, -40, 100), color=BLUE, lw=2, label="median Wald")
    ax.axhline(TRUE, color="black", ls="--", lw=1.2, label=f"truth €{TRUE:.0f}")
    ax.axhline(_naive_ref, color=ORANGE, lw=1.5, label=f"OLS ≈ €{_naive_ref:.0f}")
    ax.axvline(10, color=GREY, ls=":", lw=1.6)
    ax.set_xscale("log"); ax.set_ylim(-42, 102)
    ax.text(10, -36, " F = 10", fontsize=8, color="0.35")
    ax.set_xlabel("first-stage F (log scale)")
    ax.set_ylabel("Wald estimate (€)")
    ax.set_title("Below F = 10 the estimator comes apart")
    ax.legend(fontsize=7.4, loc="lower right", framealpha=0.9)
    fig2.tight_layout()
    fig2
    return


@app.cell
def _(mo):
    mo.md(
        r"""
        ---
        ### What to walk out with

        - **The dashboard number is real arithmetic and the wrong number.** Precision is not accuracy:
          the naive gap has the tightest interval and misses the truth, because it credits the ad with
          the buyer's own intent.
        - **An instrument does not adjust for the confounder; it sidesteps it.** IV reads the effect off
          only the slice of exposure the lottery drove, which intent could not have caused.
        - **Check the $F$ before believing any IV number.** Above 10 it certifies; below 10 it warns.
          A weak instrument is worse than none.
        - **The decision is a probability, not a confidence bar.** The bid cap is the posterior 10th
          percentile: the most you can pay while $P(\text{effect} > \text{cost}) \ge 0.90$.
        - **IV speaks for compliers.** It prices *incremental* exposure, which is exactly what a bid buys.
        """
    )
    return


if __name__ == "__main__":
    app.run()
