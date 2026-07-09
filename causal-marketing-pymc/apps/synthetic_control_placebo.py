"""Synthetic-control placebo explorer (marimo).

Pick which market is "treated" and when the campaign launches; watch the synthetic
fit, the placebo-in-space spaghetti, and the permutation p-value update live. Uses
the fast SLSQP simplex fitter so every selection is near-instant (the Bayesian
version with full uncertainty lives in notebook 07).

Run:   marimo run apps/synthetic_control_placebo.py
Edit:  marimo edit apps/synthetic_control_placebo.py
Uses the pymc>=6 core environment (.venv / cmp-core kernel).
"""
import marimo

app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import numpy as np
    import matplotlib.pyplot as plt
    from cmp import dgp, estimators as est, plots
    plots.use_style()
    return dgp, est, mo, np, plots, plt


@app.cell
def _(mo):
    mo.md(
        """
        # Synthetic control — placebo inference explorer

        Choose the treated market and the launch week. The app rebuilds the synthetic
        counterfactual from the other markets, then runs the **placebo-in-space** test:
        pretend each other market was treated and see whether the real market's gap is
        an outlier. The permutation p-value updates as you move the controls.

        > Note: only market **dma_00** actually carries a planted +12% campaign effect.
        > Pick any other market and you should see a *non-significant* p — the test's
        > specificity in action.
        """
    )
    return


@app.cell
def _(dgp):
    # panel is fixed; only dma_00 has a real effect
    sales_df, true_effect, default_launch, treated_label = dgp.geo_panel(
        n_weeks=60, launch_week=40, n_dmas=30, lift_pct=0.12, seed=3)
    sales = sales_df.values.T
    labels = list(sales_df.columns)
    return labels, sales, sales_df


@app.cell
def _(labels, mo):
    market = mo.ui.dropdown(options=labels, value=labels[0], label="treated market")
    launch = mo.ui.slider(20, 50, value=40, step=2, label="launch week")
    mo.hstack([market, launch])
    return launch, market


@app.cell
def _(est, labels, launch, market, np, plots, plt, sales):
    treated_idx = labels.index(market.value)
    L = int(launch.value)
    W = sales.shape[1]
    pre, post = slice(0, L), slice(L, W)
    t = np.arange(W)

    donors = np.delete(sales, treated_idx, axis=0)
    y_tr = sales[treated_idx]
    gap, w = est.sc_effect_slsqp(y_tr, donors, pre, post)
    cf = y_tr - gap
    pre_rmse = float(np.sqrt(np.mean(gap[pre] ** 2)))

    placebo_gaps, real_gap, p_space = est.placebo_in_space(
        sales, treated_idx, pre, post, pre_rmse, rmse_multiple=3.0)

    fig, ax = plt.subplots(1, 2, figsize=(12, 4))
    ax[0].plot(t, y_tr, color="#111", lw=1.8, label="observed")
    ax[0].plot(t, cf, color=plots.BLUE, lw=1.6, ls="--", label="synthetic")
    ax[0].fill_between(t[post], y_tr[post], cf[post], color=plots.GREEN, alpha=0.25)
    ax[0].axvline(L, color=plots.ORANGE, lw=1)
    ax[0].set_title(f"{market.value}: fit vs synthetic (pre-RMSE {pre_rmse:.2f})")
    ax[0].set_xlabel("week"); ax[0].set_ylabel("sales (€000)"); ax[0].legend(frameon=False, fontsize=8)
    plots.placebo_spaghetti(ax[1], t, placebo_gaps, real_gap, L, p_space)
    fig.tight_layout()
    n_placebo = len(placebo_gaps)   # donors surviving the pre-RMSE filter (p-value denominator)
    return L, fig, p_space, pre_rmse, n_placebo


@app.cell
def _(fig):
    fig      # display the fit + placebo-spaghetti plot (last expression = marimo output)
    return


@app.cell
def _(L, market, mo, n_placebo, p_space, pre_rmse):
    sig = "**significant**" if p_space <= 0.1 else "**not significant**"
    floor = 1.0 / (n_placebo + 1)
    mo.md(
        f"""
        ### {market.value}, launch week {L}

        - pre-period fit RMSE: **{pre_rmse:.2f}** (smaller = more trustworthy synthetic)
        - placebo permutation **p = {p_space:.3f}** → {sig} at the 0.1 level
          (rank of the treated gap among **{n_placebo}** donors that passed the 3× pre-RMSE
          filter, +1 for the treated unit; the smallest attainable p is 1/({n_placebo}+1) ≈ **{floor:.3f}**)

        If you picked a market with no real campaign, a low p here would be a *false
        positive* — which is why the placebo test, not the gap alone, is the evidence.
        """
    )
    return


if __name__ == "__main__":
    app.run()
