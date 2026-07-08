"""Uplift policy explorer (marimo).

Precompute the per-customer effect posterior ONCE, then let sliders re-derive
the euro decision instantly: discount cost `c`, the confidence bar `P(τ>c)`,
and the base size. Live profit curve, target set, and €-value-of-information.

Run:   marimo run apps/uplift_policy_explorer.py     (read-only app)
Edit:  marimo edit apps/uplift_policy_explorer.py    (notebook)
Uses the pymc>=6 core environment (.venv / cmp-core kernel).
"""
import marimo

app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import numpy as np
    import matplotlib.pyplot as plt
    from sklearn.linear_model import LogisticRegression
    from cmp import dgp, estimators as est, policy, plots
    plots.use_style()
    return LogisticRegression, dgp, est, mo, np, plots, plt, policy


@app.cell
def _(mo):
    mo.md(
        """
        # Uplift policy explorer

        The posterior over each customer's effect is fit **once**. The sliders below
        only re-derive the *decision* — so they respond instantly. Move them and watch
        who we'd target, how much we'd make, and what the remaining uncertainty is worth.
        """
    )
    return


@app.cell
def _(LogisticRegression, dgp, est, np):
    # ---- expensive step, runs ONCE (does not depend on any slider) ----
    _df = dgp.uplift_customers(n=1000, regime="observational", seed=7)
    _feat = _df.attrs["feature_cols"]
    X = _df[_feat].values
    T = _df["T"].values
    y = _df["y"].values
    tau = _df["tau"].values
    _phat = LogisticRegression(max_iter=1000).fit(X, T).predict_proba(X)[:, 1]
    cate = est.bcf(X, T, y, _phat, seed=60, draws=200, tune=200, chains=2, m=40)
    cate_point = cate.mean(0)
    return cate, cate_point, tau


@app.cell
def _(mo):
    c_slider = mo.ui.slider(2, 20, value=8, step=1, label="discount cost c (€)")
    conf_slider = mo.ui.slider(0.3, 0.95, value=0.8, step=0.05, label="confidence bar  P(τ>c) >")
    base_slider = mo.ui.slider(200, 1000, value=1000, step=100, label="mailable base size")
    mo.vstack([c_slider, conf_slider, base_slider])
    return base_slider, c_slider, conf_slider


@app.cell
def _(base_slider, c_slider, cate, cate_point, conf_slider, np, plots, plt, policy, tau):
    c = c_slider.value
    conf = conf_slider.value
    n = int(base_slider.value)

    # subset to the chosen base size (top-ranked mailable customers are the ones we score)
    idx = np.arange(n)
    cate_s = cate[:, idx]
    point_s = cate_point[idx]
    tau_s = tau[idx]

    mask, p_worth = policy.target_set(cate_s, c, confidence=conf)
    frac, cum, stop = policy.profit_curve(point_s, tau_s, c)
    _, oracle, _ = policy.profit_curve(tau_s, tau_s, c)
    voi = policy.value_of_information(cate_s, c)

    fig, ax = plt.subplots(1, 2, figsize=(11, 4))
    plots.profit_plot(ax[0], frac, cum, stop, oracle_profit=oracle)
    ax[1].scatter(point_s[~mask], p_worth[~mask], s=8, alpha=.4, color=plots.GREY, label="skip")
    ax[1].scatter(point_s[mask], p_worth[mask], s=8, alpha=.6, color=plots.GREEN, label="target")
    ax[1].axvline(c, color="k", ls=":"); ax[1].axhline(conf, color=plots.ORANGE, ls="--")
    ax[1].set_xlabel("estimated effect τ̂ (€)"); ax[1].set_ylabel("P(τ > c)")
    ax[1].set_title(f"Target {int(mask.sum())} of {n}  ·  confidence bar {conf:.2f}")
    ax[1].legend(frameon=False, fontsize=8)
    fig.tight_layout()
    return c, fig, mask, n, stop, cum, frac, voi


@app.cell
def _(c, cum, frac, mask, mo, n, stop, voi):
    mo.md(
        f"""
        ### Decision at cost €{c:.0f}

        | quantity | value |
        |---|---|
        | customers targeted | **{int(mask.sum())} / {n}** (top {frac[stop]:.0%} by rank) |
        | profit at optimal stop | **€{cum[stop]:,.0f}** |
        | value of information (total) | **€{voi['total']:,.0f}** |
        | …on the {voi['n_straddlers']} "straddlers" | **€{voi['voi_on_straddlers']:,.0f}** |

        The straddlers — whose interval crosses the cost line — are exactly the
        customers to put into an A/B test rather than mail blind.
        """
    )
    return


@app.cell
def _(fig):
    fig
    return


if __name__ == "__main__":
    app.run()
