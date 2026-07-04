"""Shared, business-styled matplotlib helpers.

One consistent visual language across every notebook: muted palette,
no top/right spines, the truth always dashed black, the model in blue,
the "do nothing / naive" baseline in orange.
"""
from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np

# Palette
BLUE = "#2c7fb8"     # the model / our estimate
GREEN = "#238b45"    # oracle / true-good
ORANGE = "#d95f0e"   # naive / warning / cost line
GREY = "#999999"     # failure-mode / placebos
GOLD = "#e6ab02"

STYLE = {
    "figure.dpi": 130,
    "font.size": 9.5,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.alpha": 0.25,
    "axes.titlesize": 10.5,
    "axes.titleweight": "bold",
}


def use_style():
    plt.rcParams.update(STYLE)


# --------------------------------------------------------------------------
def recovery_scatter(ax, tau_true, estimates: dict, title="Does the method recover the truth?"):
    """45-degree recovery plot: estimated CATE vs true tau, for one or more
    labelled estimators. `estimates` maps label -> posterior-mean array."""
    from .metrics import pehe  # local import to avoid cycle at module load

    colors = {"S-learner": GREY, "T-learner": BLUE, "BCF": GREEN}
    for label, point in estimates.items():
        c = colors.get(label, BLUE)
        rmse = np.sqrt(np.mean((point - tau_true) ** 2))
        ax.scatter(tau_true, point, s=8, alpha=0.4, color=c, label=f"{label} (PEHE {rmse:.1f})")
    lim = [tau_true.min() - 3, tau_true.max() + 3]
    ax.plot(lim, lim, "k--", lw=1)
    ax.set_xlim(lim); ax.set_ylim(lim)
    ax.set_xlabel("true effect  Ï„(x)"); ax.set_ylabel("estimated CATE")
    ax.set_title(title); ax.legend(frameon=False, fontsize=8)


def calibration_by_decile(ax, by_decile_series, level=0.90, title="Is the uncertainty honest across the effect range?"):
    """Bar of interval coverage per true-effect decile vs the nominal line."""
    ax.bar(range(len(by_decile_series)), by_decile_series.values, color=BLUE, alpha=0.85)
    ax.axhline(level, color="k", ls="--", lw=1)
    ax.set_ylim(0, 1)
    ax.set_xlabel("decile of true effect (low â†’ high)")
    ax.set_ylabel(f"{int(level*100)}% CI coverage")
    ax.set_title(title)


def profit_plot(ax, frac, cum_profit, stop, oracle_profit=None, title=None):
    """Cumulative-profit curve with the optimal stopping point marked."""
    ax.plot(frac, cum_profit, color=BLUE, lw=2, label="model policy")
    if oracle_profit is not None:
        ax.plot(frac, oracle_profit, color=GREEN, ls="--", lw=1.2, label="oracle (knows truth)")
    ax.axhline(0, color="k", lw=0.6)
    ax.axvline(frac[stop], color=BLUE, lw=0.7, alpha=0.5)
    ax.plot(frac[stop], cum_profit[stop], "o", color=BLUE)
    ax.set_xlabel("fraction of base contacted")
    ax.set_ylabel("cumulative profit (â‚¬)")
    ax.set_title(title or f"Stop at {frac[stop]*100:.0f}% of base â†’ â‚¬{cum_profit[stop]:.0f} profit")
    ax.legend(frameon=False, fontsize=8)


def overlap_plot(ax, propensity, treated_mask, title="Overlap check: both groups everywhere?"):
    """Propensity histograms by arm — the positivity/overlap diagnostic."""
    ax.hist(propensity[treated_mask], bins=30, alpha=0.6, color=BLUE, label="treated", density=True)
    ax.hist(propensity[~treated_mask], bins=30, alpha=0.6, color=ORANGE, label="control", density=True)
    ax.set_xlabel("propensity  e(x) = P(treat | x)"); ax.set_ylabel("density")
    ax.set_title(title); ax.legend(frameon=False)


def placebo_spaghetti(ax, t, placebo_gaps, real_gap, launch, p_value, title=None):
    """Placebo-in-space plot: is the treated gap an outlier vs placebos?"""
    for g in placebo_gaps:
        ax.plot(t, g, color="#bbbbbb", lw=0.7, alpha=0.7)
    ax.plot(t, real_gap, color=GREEN, lw=2, label="treated unit")
    ax.axvline(launch, color=ORANGE, lw=1)
    ax.axhline(0, color="k", lw=0.6)
    ax.set_xlabel("period"); ax.set_ylabel("gap vs synthetic")
    ax.set_title(title or f"Placebo test: is the treated gap an outlier?  (p = {p_value:.3f})")
    ax.legend(frameon=False, fontsize=8)


def sc_counterfactual_plot(ax, t, observed, cf_samples, launch, title="Treated unit vs its synthetic control"):
    """Treated series vs synthetic counterfactual with credible band."""
    ax.plot(t, observed, color="#111111", lw=1.8, label="observed (treated)")
    ax.plot(t, cf_samples.mean(0), color=BLUE, lw=1.6, ls="--", label="synthetic counterfactual")
    ax.fill_between(t, np.quantile(cf_samples, 0.05, 0), np.quantile(cf_samples, 0.95, 0), color=BLUE, alpha=0.2)
    post = t >= launch
    ax.fill_between(t[post], observed[post], cf_samples.mean(0)[post], color=GREEN, alpha=0.25)
    ax.axvline(launch, color=ORANGE, lw=1)
    ax.set_xlabel("period"); ax.set_ylabel("outcome")
    ax.set_title(title); ax.legend(frameon=False, fontsize=8)


def sensitivity_plot(ax, strengths, estimates, true_ate, cost, tipping=None,
                     title="How much hidden confounding overturns the call?"):
    """Estimated ATE (adjusting for observed X only) as an unobserved
    confounder strengthens, with the true ATE and the cost/decision line."""
    ax.plot(strengths, estimates, color=BLUE, lw=2)
    ax.axhline(true_ate, color=GREEN, ls="--", label=f"true ATE â‚¬{true_ate:.1f}")
    ax.axhline(cost, color="k", ls=":", label=f"cost â‚¬{cost:.0f}")
    if tipping is not None and not np.isnan(tipping):
        ax.axvline(tipping, color=ORANGE, lw=1)
        ax.text(tipping, cost + 0.5, f" flips at s≈{tipping:.1f}", fontsize=8, color=ORANGE)
    ax.set_xlabel("strength of unobserved confounder")
    ax.set_ylabel("estimated ATE (adjusting for X only)")
    ax.set_title(title); ax.legend(frameon=False, fontsize=8)


def decision_hist(ax, total_samples, cost, true_total=None, title=None):
    """Posterior of total incremental value with the cost line — the
    go/no-go picture."""
    ax.hist(total_samples, bins=40, color=BLUE, alpha=0.85)
    ax.axvline(cost, color=ORANGE, lw=1.4)
    ax.text(cost, ax.get_ylim()[1] * 0.9, f" cost â‚¬{cost:.0f}", fontsize=8)
    if true_total is not None:
        ax.axvline(true_total, color="k", ls="--", lw=0.8)
        ax.text(true_total, ax.get_ylim()[1] * 0.75, " true", fontsize=8)
    p = (total_samples > cost).mean()
    ax.set_xlabel("total incremental value")
    ax.set_title(title or f"Rollout decision: P(value > cost) = {p:.2f}")
