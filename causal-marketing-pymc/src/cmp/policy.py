"""Turn a posterior over effects into a euro decision.

The recurring move: an effect posterior is only useful once it becomes a
number a manager acts on — who to target, expected profit, how sure we are,
and what it's worth to reduce the remaining uncertainty.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


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


def policy_comparison(cate_samples: np.ndarray, tau_true: np.ndarray, cost: float,
                      confidence: float = 0.8, seed: int = 0):
    """Compare four targeting policies on realised profit (evaluated on the
    known truth), each with a posterior over profit induced by CATE
    uncertainty. Policies:

      - treat-all      : contact everyone
      - treat-none     : baseline (0)
      - random         : contact a random half
      - model (mean)   : contact where posterior-mean CATE > cost
      - model (conf.)  : contact where P(CATE>cost) > confidence (the honest rule)
      - oracle         : contact where the TRUE effect > cost (upper bound)

    Returns a DataFrame with mean profit, 90% CI, and fraction contacted."""
    n = len(tau_true)
    # Draw the random baseline from a stream *decoupled* from `seed`: a notebook
    # commonly passes the same integer it used to seed the DGP, and a scalar
    # default_rng(seed) would then replay the identical uniforms the DGP already
    # consumed (e.g. its first feature draw), turning "random 50%" into a feature
    # rule. Spawning off a SeedSequence gives an independent, still-reproducible
    # stream. See tests/test_package.py::test_random_baseline_is_independent.
    rng = np.random.default_rng(np.random.SeedSequence(seed).spawn(1)[0])
    gain = tau_true - cost  # realised per-customer profit if contacted

    def profit_of(mask_matrix):
        # mask_matrix: (S, n) boolean of who we'd contact under each posterior draw
        return (mask_matrix * gain[None, :]).sum(axis=1)

    p_worth = (cate_samples > cost).mean(axis=0)
    mean_cate = cate_samples.mean(axis=0)
    rand_mask = rng.random(n) < 0.5

    policies = {
        "treat-all": np.ones((1, n), bool),
        "random-50%": rand_mask[None, :],
        "model (mean>cost)": (mean_cate > cost)[None, :],
        "model (P>conf)": (p_worth > confidence)[None, :],
        "oracle": (tau_true > cost)[None, :],
    }
    rows = []
    for name, mask in policies.items():
        # profit is deterministic given the (fixed) mask and known truth,
        # but we expose the CATE-driven decision uncertainty for the model rules
        prof = profit_of(mask)
        rows.append({
            "policy": name,
            "profit": float(prof.mean()),
            "frac_contacted": float(mask.mean()),
        })
    df = pd.DataFrame(rows)
    df["profit_vs_all"] = df["profit"] - df.loc[df.policy == "treat-all", "profit"].values[0]
    return df


def voi_targeting_size(cate_samples: np.ndarray, cost: float, confidence: float = 0.8):
    """How many customers sit in the 'decision-flips' zone worth an A/B test:
    the straddlers whose 90% interval spans the cost line. Returns the count
    and their share, plus the per-customer VOI concentrated on them."""
    lo, hi = np.quantile(cate_samples, [0.05, 0.95], axis=0)
    straddle = (lo < cost) & (hi > cost)
    voi = value_of_information(cate_samples, cost)
    return {
        "n_straddlers": int(straddle.sum()),
        "share": float(straddle.mean()),
        "voi_on_straddlers": voi["voi_on_straddlers"],
        "voi_total": voi["total"],
    }


def break_even(effect_samples: np.ndarray, unit_value: float):
    """Cost at which the program breaks even under uncertainty: the effect
    level times unit value. Returns the break-even cost at the posterior
    mean and the 5th percentile (a conservative planning number)."""
    ev = effect_samples * unit_value
    return {
        "breakeven_cost_mean": float(ev.mean()),
        "breakeven_cost_p05": float(np.quantile(ev, 0.05)),
        "breakeven_cost_p95": float(np.quantile(ev, 0.95)),
    }


def go_no_go(total_effect_samples: np.ndarray, cost: float):
    """Program-evaluation decision (Anchor B style): given a posterior over
    the *total* incremental value and a fixed campaign cost, report
    P(value > cost), the expected **net value** (E[value] − cost, in the same
    units as value), the expected **ROI as a ratio** ((E[value] − cost) / cost,
    so break-even is 0), and the 90% credible interval on value.

    `expected_net_value` is a euro amount; `expected_roi` is a unitless return
    ratio — different quantities, both reported explicitly. (An earlier version
    mislabeled the net-value euro amount as 'expected_roi', which misreads as a
    huge percentage return.)"""
    p_beats = float((total_effect_samples > cost).mean())
    mean_value = float(total_effect_samples.mean())
    return {
        "P_value_gt_cost": p_beats,
        "expected_value": mean_value,
        "expected_net_value": mean_value - cost,                               # euros of net value
        "expected_roi": (mean_value - cost) / cost if cost else float("nan"),  # ratio; break-even = 0
        "value_lo": float(np.quantile(total_effect_samples, 0.05)),
        "value_hi": float(np.quantile(total_effect_samples, 0.95)),
        "cost": float(cost),
        "decision": "GO" if p_beats > 0.9 else ("NO-GO" if p_beats < 0.5 else "TEST FURTHER"),
    }
