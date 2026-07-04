"""Turn a posterior over effects into a euro decision.

The recurring move: an effect posterior is only useful once it becomes a
number a manager acts on — who to target, expected profit, how sure we are,
and what it's worth to reduce the remaining uncertainty.
"""
from __future__ import annotations

import numpy as np


def profit_curve(rank_score: np.ndarray, tau_true: np.ndarray, cost: float):
    """Cumulative profit as we contact customers in descending order of
    `rank_score` (the model's CATE point estimate), realised on the true
    effect. Returns (fraction_contacted, cumulative_profit, stop_index).

    Each contacted customer yields tau_true - cost; the optimal stopping
    point is where cumulative profit peaks."""
    order = np.argsort(-rank_score)
    cum_profit = np.cumsum(tau_true[order] - cost)
    frac = np.arange(1, len(tau_true) + 1) / len(tau_true)
    stop = int(np.argmax(cum_profit))
    return frac, cum_profit, stop


def target_set(cate_samples: np.ndarray, cost: float, confidence: float = 0.8):
    """The honest targeting rule: contact where P(tau > cost | data) exceeds
    `confidence`, not merely where the posterior mean beats cost. Returns a
    boolean mask over units."""
    p_worth = (cate_samples > cost).mean(axis=0)
    return p_worth > confidence, p_worth


def cost_sweep(cate_point: np.ndarray, tau_true: np.ndarray, costs):
    """How the optimal policy (peak profit and fraction contacted) moves as
    the per-contact cost assumption changes. Returns dict of arrays."""
    order = np.argsort(-cate_point)
    tau_ordered = tau_true[order]
    n = len(tau_true)
    opt_profit, opt_frac = [], []
    for c in costs:
        cum = np.cumsum(tau_ordered - c)
        k = int(np.argmax(cum))
        opt_profit.append(float(cum[k]))
        opt_frac.append((k + 1) / n)
    return {"costs": np.asarray(costs), "opt_profit": np.array(opt_profit), "opt_frac": np.array(opt_frac)}


def confidence_sweep(cate_samples: np.ndarray, tau_true: np.ndarray, cost: float, thresholds):
    """Realised profit (on the truth) from targeting where P(tau>cost)
    exceeds each confidence threshold. Shows the cost of insisting on more
    certainty."""
    p_worth = (cate_samples > cost).mean(axis=0)
    profits = []
    n_targeted = []
    for t in thresholds:
        mask = p_worth > t
        profits.append(float((tau_true[mask] - cost).sum()))
        n_targeted.append(int(mask.sum()))
    return {"thresholds": np.asarray(thresholds), "profit": np.array(profits), "n_targeted": np.array(n_targeted)}


def value_of_information(cate_samples: np.ndarray, cost: float):
    """Per-customer expected option value of *resolving* the uncertainty in
    the CATE before deciding, in euros.

    With uncertainty, the best you can do per customer is act on the mean:
    max(E[tau] - cost, 0). If you could first learn tau exactly, you'd earn
    E[max(tau - cost, 0)] (act only when it actually pays). The gap is the
    value of that information — it is concentrated on the "straddlers" whose
    interval spans the cost line, where the decision could still flip.

    Returns dict: per_customer (array), total (float), straddlers (mask),
    voi_on_straddlers (float)."""
    mean_cate = cate_samples.mean(axis=0)
    ev_perfect = np.maximum(cate_samples - cost, 0).mean(axis=0)  # E[max(tau-c,0)]
    ev_act_on_mean = np.maximum(mean_cate - cost, 0)
    per_customer = ev_perfect - ev_act_on_mean
    lo, hi = np.quantile(cate_samples, [0.05, 0.95], axis=0)
    straddlers = (lo < cost) & (hi > cost)
    return {
        "per_customer": per_customer,
        "total": float(per_customer.sum()),
        "straddlers": straddlers,
        "n_straddlers": int(straddlers.sum()),
        "voi_on_straddlers": float(per_customer[straddlers].sum()),
    }


def go_no_go(total_effect_samples: np.ndarray, cost: float):
    """Program-evaluation decision (Anchor B style): given a posterior over
    the *total* incremental value and a fixed campaign cost, report
    P(value > cost), expected ROI, and the credible interval."""
    p_beats = float((total_effect_samples > cost).mean())
    roi = total_effect_samples - cost
    return {
        "P_value_gt_cost": p_beats,
        "expected_value": float(total_effect_samples.mean()),
        "expected_roi": float(roi.mean()),
        "value_lo": float(np.quantile(total_effect_samples, 0.05)),
        "value_hi": float(np.quantile(total_effect_samples, 0.95)),
        "cost": float(cost),
        "decision": "GO" if p_beats > 0.9 else ("NO-GO" if p_beats < 0.5 else "TEST FURTHER"),
    }
