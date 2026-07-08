"""Confounding sensitivity explorer (marimo).

One slider: the strength of an *unobserved* confounder. Watch the estimated ATE
(adjusting for observed X only) drift as the hidden confounder strengthens, cross
the cost line, and flip the decision. The "how fragile is this conclusion?" story.

Run:   marimo run apps/confounding_sensitivity.py
Edit:  marimo edit apps/confounding_sensitivity.py
Uses the pymc>=6 core environment (.venv / cmp-core kernel). No sampling needed —
the estimator here is a fast covariate-adjusted OLS, so the slider is instant.
"""
import marimo

app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import numpy as np
    import matplotlib.pyplot as plt
    from cmp import dgp, plots
    plots.use_style()
    return dgp, mo, np, plots, plt


@app.cell
def _(mo):
    mo.md(
        """
        # Confounding sensitivity — how fragile is the conclusion?

        We assumed we measured every confounder. What if we didn't? Below, a hidden
        driver `U` moves *both* who gets the email and how much they spend. Slide its
        strength up and watch the ATE we'd estimate (adjusting for the **observed**
        features only) drift — and note the point where it crosses the cost line and
        would wrongly say *"email everyone pays."*
        """
    )
    return


@app.cell
def _(dgp, np):
    # ---- precompute the whole drift curve ONCE (fast OLS per strength) ----
    COST = 8.0
    strengths = np.linspace(0, 12, 49)

    def adjusted_ate(Xd, Td, yd):
        D = np.column_stack([np.ones(len(Td)), Td, Xd])
        beta, *_ = np.linalg.lstsq(D, yd, rcond=None)
        return beta[1]

    _base = dgp.uplift_customers(n=1000, regime="observational", confounder_strength=0.0, seed=7)
    true_ate = float(_base["tau"].mean())
    feat = _base.attrs["feature_cols"]

    drift = []
    for sv in strengths:
        d = dgp.uplift_customers(n=1000, regime="observational", confounder_strength=sv, seed=7)
        drift.append(adjusted_ate(d[feat].values, d["T"].values, d["y"].values))
    drift = np.array(drift)
    tip = float(strengths[np.argmax(drift > COST)]) if np.any(drift > COST) else float("nan")
    return COST, drift, strengths, tip, true_ate


@app.cell
def _(mo, strengths):
    s_slider = mo.ui.slider(
        float(strengths.min()), float(strengths.max()), value=0.0, step=0.25,
        label="unobserved confounder strength",
    )
    s_slider
    return (s_slider,)


@app.cell
def _(COST, drift, np, plots, plt, s_slider, strengths, tip, true_ate):
    s = s_slider.value
    est_here = float(np.interp(s, strengths, drift))
    flipped = est_here > COST

    fig, ax = plt.subplots(figsize=(8, 4.5))
    plots.sensitivity_plot(ax, strengths, drift, true_ate, COST, tipping=tip)
    ax.axvline(s, color="#333333", lw=1.4)
    ax.plot([s], [est_here], "o", color=("#d95f0e" if flipped else "#238b45"), ms=10, zorder=5)
    ax.set_title(
        f"At strength {s:.2f}:  estimated ATE €{est_here:.1f}  "
        + ("→ FLIPPED (would over-mail)" if flipped else "→ decision holds")
    )
    fig.tight_layout()
    return est_here, fig, flipped, s


@app.cell
def _(fig):
    fig      # display the drift plot (a cell's last expression is its marimo output)
    return


@app.cell
def _(COST, est_here, flipped, mo, s, tip, true_ate):
    verdict = (
        f"**Decision flipped.** A hidden confounder of strength {s:.2f} pushes the "
        f"estimate to €{est_here:.1f}, above the €{COST:.0f} cost — we'd wrongly mail "
        f"everyone. The true ATE is only €{true_ate:.1f}."
        if flipped else
        f"**Decision holds.** At strength {s:.2f} the estimate is €{est_here:.1f}, still "
        f"below the €{COST:.0f} cost. True ATE €{true_ate:.1f}."
    )
    mo.md(
        f"""
        {verdict}

        The **tipping point** is strength ≈ **{tip:.1f}**. Ask the domain expert:
        *is a hidden confounder that strong plausible here?* If yes, the result is
        fragile and needs an experiment; if no, it's robust. That judgement — not a
        p-value — is what makes the conclusion defensible.
        """
    )
    return


if __name__ == "__main__":
    app.run()
