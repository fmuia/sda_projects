"""Experiment design explorer (marimo) — power, MDE, sample size, and the cost of peeking.

The four quantities of a test (alpha, power, n, effect) are tied together: fix any
three and the fourth is pinned. Sliders let the room *feel* that coupling, which no
static table does.

WASM-SAFE: imports only numpy / scipy / matplotlib (all present in Pyodide). It must
NOT import `cmp` — local packages cannot be installed in the browser. Everything this
app needs is defined inline, so `marimo export html-wasm` produces a page that runs
with no Python, no install, no network.

Run:    marimo run apps/experiment_design.py       (read-only app)
Edit:   marimo edit apps/experiment_design.py      (notebook)
Ship:   marimo export html-wasm apps/experiment_design.py -o site/experiment_design --mode run
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
    BLUE, GREEN, ORANGE, GREY = "#2c7fb8", "#238b45", "#d95f0e", "#999999"
    plt.rcParams.update({
        "figure.dpi": 130, "font.size": 9.5,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": True, "grid.alpha": 0.25,
        "axes.titlesize": 10.5, "axes.titleweight": "bold",
    })
    return BLUE, GREEN, GREY, ORANGE, mo, np, plt, stats


@app.cell
def _(mo):
    mo.md(
        """
        # Designing the test *before* you run it

        Most failed experiments were doomed before the first user arrived: the test never had
        a real chance of seeing the effect that mattered. Four quantities are locked together —
        **significance α**, **power 1−β**, **sample size n**, and the **effect** you want to catch.
        Fix any three and the fourth is pinned.

        Move the sliders. Watch what your test can and cannot see.
        """
    )
    return


@app.cell
def _(mo):
    p0 = mo.ui.slider(0.01, 0.30, value=0.05, step=0.005, label="Baseline conversion $p_0$")
    lift = mo.ui.slider(0.001, 0.05, value=0.010, step=0.001, label="Lift you care about $\\Delta$ (abs.)")
    n_per_arm = mo.ui.slider(500, 100_000, value=20_000, step=500, label="Users **per arm** $n$")
    alpha = mo.ui.slider(0.01, 0.20, value=0.05, step=0.01, label="Significance $\\alpha$")
    return alpha, lift, n_per_arm, p0


@app.cell
def _(alpha, lift, mo, n_per_arm, p0):
    mo.hstack([mo.vstack([p0, lift]), mo.vstack([n_per_arm, alpha])], justify="start", gap=2)
    return


@app.cell
def _(np, stats):
    # --- the design math ---------------------------------------------------------------
    # Mirrors cmp.design exactly (this app must stay WASM-safe, so it cannot import cmp;
    # tests/test_design.py is the guard on the real thing, incl. a cross-check against R's
    # power.prop.test).
    #
    # `power_of` is the primitive; the other two are numeric inversions of it, so they
    # cannot disagree. Getting this wrong is easy and expensive: standardize by the POOLED
    # variance (what the null claims) but spread by the UNPOOLED one (what is actually true
    # when the arms convert at different rates). An earlier draft used the baseline variance
    # for both and overstated power by ~4 points — it would have printed "80% power" on a
    # test that really had 76%.
    from scipy.optimize import brentq

    def power_of(p0, delta, n, alpha=0.05):
        p1 = p0 + delta
        za = stats.norm.ppf(1 - alpha / 2)
        pbar = (p0 + p1) / 2
        se_null = np.sqrt(2 * pbar * (1 - pbar) / n)
        se_alt = np.sqrt((p0 * (1 - p0) + p1 * (1 - p1)) / n)
        crit = za * se_null
        return float(stats.norm.cdf((abs(delta) - crit) / se_alt)
                     + stats.norm.cdf((-abs(delta) - crit) / se_alt))

    def n_needed(p0, delta, alpha=0.05, power=0.80):
        """Users per arm needed to detect an absolute lift `delta`."""
        if delta <= 0:
            return float("inf")
        f = lambda n: power_of(p0, delta, n, alpha) - power
        if f(1e9) < 0:
            return float("inf")
        if f(2.0) > 0:
            return 2.0
        return float(brentq(f, 2.0, 1e9, xtol=1e-4))

    def mde(p0, n, alpha=0.05, power=0.80):
        """Smallest absolute lift detectable with `power` at `alpha`, given n per arm."""
        f = lambda d: power_of(p0, d, n, alpha) - power
        hi = 0.99 - p0
        if f(hi) < 0:
            return float("nan")
        return float(brentq(f, 1e-9, hi, xtol=1e-10))
    return mde, n_needed, power_of


@app.cell
def _(alpha, lift, mde, mo, n_needed, n_per_arm, p0, power_of):
    _p0, _d, _n, _a = p0.value, lift.value, n_per_arm.value, alpha.value
    _pow = power_of(_p0, _d, _n, _a)
    _mde80 = mde(_p0, _n, _a, 0.80)
    _need = n_needed(_p0, _d, _a, 0.80)

    _verdict = (
        f"✅ **Powered.** At n={_n:,}/arm this test has **{_pow:.0%} power** to see a "
        f"{_d*100:.2f} pp lift."
        if _pow >= 0.80 else
        f"⚠️ **Underpowered.** At n={_n:,}/arm this test has only **{_pow:.0%} power** to see a "
        f"{_d*100:.2f} pp lift. You need **{_need:,.0f} per arm** ({_need/_n:.1f}× more) to reach 80%."
    )

    mo.md(
        f"""
        | | |
        |---|---|
        | Power at your n and lift | **{_pow:.1%}** |
        | Smallest lift you can detect (80% power) | **{_mde80*100:.2f} pp** ({_mde80/_p0:.0%} relative) |
        | n per arm needed for your lift | **{_need:,.0f}** |
        | Total users needed (both arms) | **{2*_need:,.0f}** |

        {_verdict}
        """
    )
    return


@app.cell
def _(BLUE, GREEN, GREY, ORANGE, alpha, lift, n_needed, n_per_arm, np, p0, plt, power_of, stats):
    _p0, _d, _n, _a = p0.value, lift.value, n_per_arm.value, alpha.value

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.5, 3.9))

    # LEFT: the two bell curves — the picture *of* a test.
    _p1 = _p0 + _d
    _se = np.sqrt(_p0 * (1 - _p0) / _n + _p1 * (1 - _p1) / _n)
    _crit = stats.norm.ppf(1 - _a / 2) * _se

    _x = np.linspace(-4.2 * _se, _d + 4.2 * _se, 600)
    _null = stats.norm.pdf(_x, 0, _se)
    _alt = stats.norm.pdf(_x, _d, _se)
    ax1.plot(_x * 100, _null, color=GREY, lw=1.8, label="No effect (H₀)")
    ax1.plot(_x * 100, _alt, color=BLUE, lw=1.8, label=f"True lift = {_d*100:.2f} pp")
    _reject = _x >= _crit
    ax1.fill_between(_x[_reject] * 100, 0, _alt[_reject], color=BLUE, alpha=0.30,
                     label=f"Power = {power_of(_p0,_d,_n,_a):.0%}")
    ax1.fill_between(_x[_reject] * 100, 0, _null[_reject], color=ORANGE, alpha=0.55,
                     label=f"False positive = {_a:.0%}")
    ax1.axvline(_crit * 100, color="black", ls="--", lw=1.1)
    ax1.set_xlabel("estimated lift (pp)")
    ax1.set_yticks([])
    ax1.set_title("A test is two bell curves")
    ax1.legend(fontsize=7.2, loc="upper left", framealpha=0.9)

    # RIGHT: power vs n — where 80% is bought.
    _grid = np.linspace(500, max(6 * _n, 3 * n_needed(_p0, _d, _a, 0.80)), 300)
    _pw = [power_of(_p0, _d, g, _a) for g in _grid]
    ax2.plot(_grid / 1000, _pw, color=BLUE, lw=2)
    ax2.axhline(0.80, color=GREEN, ls="--", lw=1.2, label="80% power")
    ax2.axvline(_n / 1000, color=ORANGE, lw=1.6, label=f"your n = {_n:,}")
    _need = n_needed(_p0, _d, _a, 0.80)
    ax2.plot([_need / 1000], [0.80], "o", color=GREEN, ms=7,
             label=f"need {_need:,.0f}/arm")
    ax2.set_xlabel("users per arm (thousands)")
    ax2.set_ylabel("power")
    ax2.set_ylim(0, 1.02)
    ax2.set_title("Power is bought with sample size")
    ax2.legend(fontsize=7.2, loc="lower right", framealpha=0.9)

    fig.tight_layout()
    fig
    return


@app.cell
def _(mo):
    mo.md(
        """
        Two things the sliders make obvious, and neither is intuitive:

        1. **Halving the lift you want to catch roughly quadruples the users you need** — the
           sample scales with $1/\\Delta^2$. Chasing small effects is brutally expensive.
        2. **A low baseline rate is expensive too.** At $p_0=1\\%$ you need far more traffic
           than at $p_0=20\\%$ to see the same *relative* lift.

        > **The discipline:** decide the smallest lift worth shipping, read off the users and
        > weeks it takes, and **commit to that sample before launch**.

        ---

        ## The cost of peeking

        Everything above assumes the sample size is fixed in advance and the result is read
        **once**. Teams routinely violate this: they watch the p-value every morning and ship
        the moment it dips below 0.05. Each look is another chance for a *dead* test to wander
        under the line by luck — and those chances accumulate.

        Below, the redesign does **nothing**. The true effect is exactly zero. We simulate
        honest teams who look repeatedly and stop at the first "win".
        """
    )
    return


@app.cell
def _(mo):
    n_looks = mo.ui.slider(1, 20, value=10, step=1, label="Number of looks at the data")
    n_sims = mo.ui.slider(200, 4000, value=1500, step=100, label="Simulated experiments")
    return n_looks, n_sims


@app.cell
def _(mo, n_looks, n_sims):
    mo.hstack([n_looks, n_sims], justify="start", gap=2)
    return


@app.cell
def _(alpha, n_looks, n_per_arm, n_sims, np, p0, stats):
    # True effect is ZERO. Any "significant" result is a false positive, by construction.
    _rng = np.random.default_rng(7)
    _p0v, _n, _a, _L, _S = p0.value, int(n_per_arm.value), alpha.value, int(n_looks.value), int(n_sims.value)

    # Look at equally spaced interim points, ending at the planned n.
    _checkpoints = np.linspace(_n / _L, _n, _L).astype(int)
    _za = stats.norm.ppf(1 - _a / 2)

    # Simulate the *cumulative* conversions arm-by-arm, then test at each checkpoint.
    _increments = np.diff(np.concatenate([[0], _checkpoints]))
    _hit_peek = np.zeros(_S, dtype=bool)
    _hit_once = np.zeros(_S, dtype=bool)

    _cumA = np.zeros(_S)
    _cumB = np.zeros(_S)
    _cum_n = 0
    for _i, _inc in enumerate(_increments):
        _cumA += _rng.binomial(_inc, _p0v, size=_S)
        _cumB += _rng.binomial(_inc, _p0v, size=_S)   # same rate: no effect
        _cum_n += _inc
        _pA, _pB = _cumA / _cum_n, _cumB / _cum_n
        _se = np.sqrt(_pA * (1 - _pA) / _cum_n + _pB * (1 - _pB) / _cum_n)
        _se = np.where(_se == 0, np.inf, _se)
        _sig = np.abs((_pB - _pA) / _se) > _za
        _hit_peek |= _sig                      # a peeker stops at the FIRST significant look
        if _i == len(_increments) - 1:
            _hit_once = _sig                   # the disciplined team looks only at the end

    peek_rate = _hit_peek.mean()
    once_rate = _hit_once.mean()
    return once_rate, peek_rate


@app.cell
def _(BLUE, GREEN, ORANGE, alpha, mo, n_looks, once_rate, peek_rate, plt):
    _a = alpha.value
    _fig, _ax = plt.subplots(figsize=(6.4, 3.1))
    _bars = _ax.bar(
        ["Look once\n(disciplined)", f"Peek {int(n_looks.value)}×\n(stop at first win)"],
        [once_rate, peek_rate],
        color=[GREEN, ORANGE], width=0.55,
    )
    _ax.axhline(_a, color="black", ls="--", lw=1.2, label=f"intended false-positive rate = {_a:.0%}")
    for _b, _v in zip(_bars, [once_rate, peek_rate]):
        _ax.text(_b.get_x() + _b.get_width() / 2, _v + 0.006, f"{_v:.1%}",
                 ha="center", fontweight="bold", color=BLUE)
    _ax.set_ylabel("false-positive rate")
    _ax.set_title("The redesign does nothing. How often do we 'win' anyway?")
    _ax.legend(fontsize=8)
    _fig.tight_layout()

    mo.vstack([
        _fig,
        mo.md(
            f"""
            Peeking {int(n_looks.value)} times turns an intended **{_a:.0%}** error rate into
            **{peek_rate:.1%}**. Roughly **1 in {max(1, round(1/max(peek_rate, 1e-9)))}** "wins"
            from a peeking team is pure noise — on a treatment that does *literally nothing*.

            The fix is not to look less anxiously; it is to **fix the sample size and the
            analysis date in advance**, or, when live monitoring is genuinely needed, to use a
            sequential method (alpha-spending, always-valid confidence sequences) that budgets
            the looks up front.

            Changing the primary metric after seeing the data is the same error in a different
            coat: with enough metrics on the dashboard, one of them will cross 0.05 on its own.
            """
        ),
    ])
    return


@app.cell
def _(mo):
    mo.md(
        """
        ---
        ### What to walk out with

        - **Power is a design decision, not a diagnostic.** Compute it before launch; afterwards
          it only tells you why you saw nothing.
        - **The MDE is the honest headline.** "We can detect ≥ X pp" is a truthful description of
          a test's capability; "no significant effect" without an MDE is not.
        - **Peeking is not a small sin.** It multiplies your false-positive rate several-fold.
        - **Pre-register**: the metric, the sample, the analysis date, and the segments you will
          look at. Everything else is exploration, and must be labelled as such.
        """
    )
    return


if __name__ == "__main__":
    app.run()
