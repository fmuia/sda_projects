"""Chapter 13 as a room-ready lecture — instrumental variables.

A ~45-minute guest lecture, built as a SLIDE DECK: the body is one `mo.accordion` with
`multiple=False`, so opening a slide closes the last one — click down the deck as you present.
Each slide is self-contained: the concept is taught first (a boxed definition and the one-line
intuition), then worked on ONE running case (a retailer deciding how much to bid for a single ad
exposure), with its own interactive controls and figure.

Nothing here samples. The classical arm (OLS, first stage, reduced form, 2SLS/Wald, the first-stage
F, the weak-instrument sweep, the euro cap) is recomputed LIVE from the sliders in closed form. The
Bayesian arm is the REAL posterior from the notebook's PyMC/NUTS run, precomputed and bundled. So
the whole app is numpy / scipy / matplotlib only and runs in the browser.

Run:    marimo run  apps/iv_lecture.py      (clean lecture view — use this in the room)
Edit:   marimo edit apps/iv_lecture.py      (presenter / notebook view — shows the code)
Data:   apps/build_iv_lecture_data.py bundles the draws + the notebook's scalar results and embeds
        them here (the BLOB below), so the WASM export `make site` is fully self-contained.
"""
import marimo

app = marimo.App(width="medium")


# ============================== setup: data, palette, helpers ==============================

@app.cell
def _():
    import base64
    import json
    import zlib
    from pathlib import Path

    import marimo as mo
    import numpy as np
    import matplotlib.pyplot as plt
    from matplotlib.patches import Circle, FancyArrowPatch

    # A calm, lecture-deck palette. NAVY for titles; the accent colours carry meaning and are reused
    # on every figure: BLUE = treatment / 2SLS, GREEN = outcome / Bayes, ORANGE = the naive number,
    # GOLD = the instrument, GREY = the unobserved.
    NAVY = "#1f3a5f"
    BLUE, GREEN, ORANGE, GOLD, GREY = "#2c6fbb", "#2e8b57", "#d1622b", "#e0a520", "#8a8a8a"
    plt.rcParams.update({
        "figure.dpi": 140, "font.size": 13,
        "axes.titlesize": 15, "axes.titleweight": "bold", "axes.titlecolor": NAVY,
        "axes.labelsize": 12.5, "xtick.labelsize": 11, "ytick.labelsize": 11, "legend.fontsize": 11,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": True, "grid.alpha": 0.22,
    })

    # The bundle travels INSIDE this file (see the BLOB below), so the app is self-contained for the
    # WASM take-home. When run locally we prefer the JSON on disk if present (lets you rebuild draws
    # without regenerating the blob), and fall back to the embedded copy otherwise.
    def _load():
        for p in (Path(__file__).parent / "iv_lecture_data.json", Path("apps/iv_lecture_data.json")):
            try:
                if p.exists():
                    return json.loads(p.read_text())
            except Exception:
                pass
        return json.loads(zlib.decompress(base64.b64decode(BLOB)).decode())

    D = _load()
    beta_probit = np.array(D["beta_probit"])   # the SHIPPED posterior (binary-aware probit)
    beta_gauss = np.array(D["beta_gauss"])      # the misspecified joint-Gaussian starting point
    rho_probit = np.array(D["rho_probit"])      # endogeneity correlation, the one new object
    SIM = D["sim"]                              # simulated-market scalars (from nb11)
    CRI = D["criteo"]                           # real Criteo-market scalars (from nb11b)
    TRUE = float(D["true"])
    return (BLUE, CRI, Circle, FancyArrowPatch, GOLD, GREEN, GREY, NAVY, ORANGE, SIM, TRUE,
            beta_gauss, beta_probit, mo, np, plt, rho_probit)


@app.cell
def _(mo):
    # Typography to match a polished lecture deck: larger reading size, navy headings, calm spacing.
    # Injected as an inline <style> so it applies identically under `marimo run`, the HTML export,
    # and the WASM take-home. Targets marimo's markdown container (`.prose`).
    style = mo.Html("""
    <style>
      .prose, .prose p, .prose li { font-size: 1.16rem !important; line-height: 1.66 !important; }
      .prose h1 { font-size: 2.5rem !important; color: #1f3a5f !important; font-weight: 800 !important;
                  letter-spacing: -0.015em; margin-bottom: .1em; }
      .prose h2 { font-size: 1.95rem !important; color: #1f3a5f !important; font-weight: 800 !important; }
      .prose h3 { font-size: 1.55rem !important; color: #1f3a5f !important; font-weight: 700 !important; }
      .prose h4 { font-size: 1.24rem !important; color: #33475b !important; font-weight: 700 !important;
                  line-height: 1.4 !important; }
      .prose strong { color: #16273f; }
      /* accordion slide titles: large, calm, navy */
      details > summary, .marimo-accordion summary { font-size: 1.32rem !important;
                  font-weight: 700 !important; color: #1f3a5f !important; padding: .55rem 0 !important; }
      /* callout boxes: a touch larger */
      [data-kind], .callout { font-size: 1.12rem !important; }
    </style>
    """)
    style
    return


@app.cell
def _(mo):
    # ---- boxes: one visual vocabulary for the whole deck ----
    def _box(title, body, kind, icon):
        return mo.callout(mo.md(f"**{icon}&nbsp; {title}**\n\n{body}"), kind=kind)

    def define(term, body):
        return _box(f"Definition — {term}", body, "info", "▣")

    def idea(body):
        return _box("The idea in one line", body, "neutral", "◆")

    def takeaway(body):
        return _box("Manager's takeaway", body, "success", "€")

    def slip(body):
        return _box("Where teams slip", body, "warn", "▲")
    return define, idea, slip, takeaway


@app.cell
def _(Circle, FancyArrowPatch, NAVY, np):
    # ---- one DAG drawer, reused for every causal diagram ----
    # nodes: {name: (x, y, facecolor)};  edges: list of (from, to, kind) where kind in
    # {"ok" (solid grey), "bad" (dashed red = an assumption being broken)}. A "bad" edge bows so it
    # visibly bypasses any node it would otherwise pass straight through (Z→Y arcing around X).
    def draw_dag(ax, nodes, edges, note=""):
        R = 0.085
        ax.set_xlim(-0.02, 1.02); ax.set_ylim(-0.06, 1.10); ax.axis("off"); ax.set_aspect("equal")
        for a, b, kind in edges:
            xa, ya, _ = nodes[a]; xb, yb, _ = nodes[b]
            dx, dy = xb - xa, yb - ya; L = float(np.hypot(dx, dy)); ux, uy = dx / L, dy / L
            p0 = (xa + ux * R, ya + uy * R); p1 = (xb - ux * R, yb - uy * R)
            col = "#c0392b" if kind == "bad" else "0.30"
            ls = (0, (4, 3)) if kind == "bad" else "-"
            cs = "arc3,rad=-0.45" if kind == "bad" else "arc3,rad=0"
            ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle="-|>", mutation_scale=17, lw=2.0,
                                         color=col, linestyle=ls, connectionstyle=cs, zorder=2))
        for name, (x, y, c) in nodes.items():
            ax.add_patch(Circle((x, y), R, fc=c, ec="black", lw=1.3, zorder=3, alpha=0.92))
            ax.text(x, y, name, ha="center", va="center", color="white",
                    fontweight="bold", fontsize=15, zorder=4)
        if note:
            ax.text(0.5, -0.03, note, ha="center", va="top", fontsize=10.5, color=NAVY,
                    transform=ax.transAxes)
    return (draw_dag,)


@app.cell
def _(np):
    # --- the IV world and its CLASSICAL estimators, inlined (mirrors cmp.dgp.iv_ad_exposure +
    # cmp.classical.iv_2sls). Closed form: two least-squares slopes and a division. Fixed seed so
    # the picture is stable per (gamma, kappa, n) — what moves is the mechanism, not the noise. ---
    def fit_iv(gamma=1.1, kappa=12.0, n=3000, seed=37, a0=0.3, lam=0.8, mu=50.0, beta=15.0, sigma=6.0):
        rng = np.random.default_rng(seed)
        U = rng.normal(0, 1, n)
        Z = rng.integers(0, 2, n).astype(float)
        X = (rng.uniform(size=n) < 1 / (1 + np.exp(-(a0 + gamma * Z + lam * U)))).astype(float)
        Y = mu + beta * X + kappa * U + rng.normal(0, sigma, n)

        def slope(x, y):
            Dm = np.column_stack([np.ones(len(x)), x])
            return np.linalg.lstsq(Dm, y, rcond=None)[0], Dm

        b_ols, _ = slope(X, Y)
        b_fs, Zd = slope(Z, X)
        b_rf, _ = slope(Z, Y)
        naive, pi, delta = float(b_ols[1]), float(b_fs[1]), float(b_rf[1])
        wald = delta / pi if pi != 0 else np.nan
        xhat = Zd @ b_fs
        var_pi = float(np.sum((X - xhat) ** 2)) / (n - 2) / float(np.sum((Z - Z.mean()) ** 2))
        F = float(pi ** 2 / var_pi) if var_pi > 0 else np.inf
        Xm = np.column_stack([np.ones(n), X]); Xh = np.column_stack([np.ones(n), xhat])
        b2 = np.linalg.solve(Xh.T @ Xm, Xh.T @ Y)
        resid = Y - Xm @ b2
        s2 = float(resid @ resid) / (n - 2)
        se = float(np.sqrt((s2 * np.linalg.inv(Xh.T @ Xh))[1, 1]))
        return dict(naive=naive, pi=pi, delta=delta, wald=float(b2[1]), F=F, se=se,
                    fs_lo=float(X[Z == 0].mean()), fs_hi=float(X[Z == 1].mean()))
    return (fit_iv,)


@app.cell
def _(mo):
    # The three live controls, declared once so any slide can read their .value.
    kappa = mo.ui.slider(0.0, 24.0, value=12.0, step=1.0,
                         label="Confounding $\\kappa$  (how hard intent also lifts sales, €)",
                         show_value=True)
    gamma = mo.ui.slider(0.05, 2.0, value=1.1, step=0.05,
                         label="Instrument strength $\\gamma$  (how hard the lottery moves exposure)",
                         show_value=True)
    cost = mo.ui.slider(4.0, 22.0, value=10.0, step=0.5, label="Cost per exposure $c$  (€)",
                        show_value=True)
    return cost, gamma, kappa


# ============================== slide builders ==============================
# Each returns one self-contained slide (an Html block placed inside the accordion).

@app.cell
def _(SIM, TRUE, idea, mo, takeaway):
    slide_decision = mo.vstack([
        mo.md(
            rf"""
            #### A retailer must set one number: the most it will pay for a single ad exposure.

            The demand-side platform's dashboard says users who **saw** an ad convert far more than
            users who did not, and it wants the bid cap raised. That number is honest arithmetic and
            the **wrong number to bid on** — the platform *chose* whom to expose, and it chose people
            already likely to buy. The exposed carry their own intent into the comparison.

            On this chapter's simulated market the dashboard prices an exposure at
            **€{SIM['naive']:.1f}**; the true worth is **€{TRUE:.0f}**. Bidding the dashboard number
            pays a **€{SIM['naive'] - TRUE:.0f} premium per exposure** for intent the retailer
            already owned.
            """
        ),
        idea(
            "To bid on a number, the number has to be **causal** — the sales an exposure *creates*, "
            "not the sales that would have happened anyway. Correlation from a targeting engine is "
            "the opposite of what a bid needs."
        ),
        takeaway(
            f"A €{SIM['naive'] - TRUE:.0f} error per exposure is not rounding. Across millions of "
            "exposures a quarter it is the whole media budget's worth of over-payment. This lecture "
            "is one method for getting the number right when you **cannot** randomize who sees the ad."
        ),
    ], gap=1)
    return (slide_decision,)


@app.cell
def _(BLUE, GREEN, GREY, SIM, TRUE, define, draw_dag, idea, mo, plt):
    _fig, _ax = plt.subplots(figsize=(5.2, 3.4))
    draw_dag(
        _ax,
        nodes={"U": (0.5, 0.95, GREY), "X": (0.16, 0.26, BLUE), "Y": (0.84, 0.26, GREEN)},
        edges=[("U", "X", "ok"), ("U", "Y", "ok"), ("X", "Y", "ok")],
        note="U = buying intent (unobserved).   X = exposure.   Y = sales.",
    )
    _ax.set_title("Why the dashboard lies")
    _fig.tight_layout()
    slide_confound = mo.vstack([
        mo.md(
            rf"""
            #### The two groups were never comparable to begin with.

            Write $Y_i(1)$ for what customer $i$ would buy **if exposed** and $Y_i(0)$ if **not**.
            The effect on that customer is $Y_i(1) - Y_i(0)$; we only ever see one of the two. The
            number we want is the average of that difference over the people a bid can move.

            The dashboard instead reports $\E[Y \mid \text{{exposed}}] - \E[Y \mid \text{{not}}]$ —
            **different people**. Intent $U$ pushes a customer toward exposure *and* toward buying,
            so the exposed would have bought more even with no ad. That shared cause is the diagram's
            fork ($U \to X$ and $U \to Y$), and it is the €{SIM['naive'] - TRUE:.0f} gap.
            """
        ),
        define(
            "confounding (selection bias)",
            r"A variable that causes both the treatment and the outcome, so the raw gap blends the "
            r"real effect with the pre-existing difference between the groups. You cannot subtract "
            r"it out if you cannot see it — and intent is exactly what you cannot see.",
        ),
        _fig,
        idea("Any honest method has to manufacture a comparison the targeting engine did not rig."),
    ], gap=1)
    return (slide_confound,)


@app.cell
def _(BLUE, GOLD, GREEN, GREY, NAVY, define, draw_dag, mo, plt):
    _fig, (_a1, _a2) = plt.subplots(1, 2, figsize=(10.0, 3.5))
    draw_dag(
        _a1,
        nodes={"U": (0.5, 0.95, GREY), "Z": (0.06, 0.26, GOLD),
               "X": (0.5, 0.26, BLUE), "Y": (0.94, 0.26, GREEN)},
        edges=[("Z", "X", "ok"), ("X", "Y", "ok"), ("U", "X", "ok"), ("U", "Y", "ok")],
        note="Z reaches Y ONLY through X.   No arrow U→Z, no arrow Z→Y.",
    )
    _a1.set_title("A valid instrument")
    _a2.axis("off")
    _a2.text(0.0, 0.98, "What makes Z an instrument", fontweight="bold", fontsize=13, color=NAVY)
    for _i, (_h, _t) in enumerate([
        ("1.  Relevance", "Z actually moves exposure X.\nTestable — it is the first-stage F."),
        ("2.  As-good-as-random", "Z is unrelated to intent U.\nHolds by design when Z is a lottery."),
        ("3.  Exclusion", "Z affects sales Y only through X.\nUntestable — argued, never checked."),
    ]):
        _y = 0.76 - _i * 0.27
        _a2.text(0.02, _y, _h, fontweight="bold", fontsize=12, color=BLUE)
        _a2.text(0.05, _y - 0.085, _t, fontsize=11, color="0.25", va="top")
    _fig.tight_layout()
    slide_instrument = mo.vstack([
        mo.md(
            r"""
            #### An instrument imports a slice of randomness the firm did not run itself.

            We need a lever that moves exposure, that intent could not have caused, and that touches
            sales only by moving exposure. In the case it is a randomized **serving-priority
            lottery**: on a coin flip the platform bumps a user up the auction queue, raising the
            chance they see the ad. The coin is blind to who the user is, and the queue position can
            only touch sales by changing whether the ad was shown. Read the diagram by what is
            **missing**: no arrow into $Z$ (random), and no arrow from $Z$ to $Y$ except through $X$.
            """
        ),
        define(
            "instrument",
            "A variable $Z$ that (1) moves the treatment, (2) is assigned as-good-as-randomly, and "
            "(3) affects the outcome only through the treatment. Conditions 1–2 you defend with data "
            "and design; condition 3 you can only argue from how the world works.",
        ),
        _fig,
    ], gap=1)
    return (slide_instrument,)


@app.cell
def _(GREEN, GREY, define, fit_iv, mo, plt):
    _r = fit_iv()
    _always = _r["fs_lo"]; _compl = _r["fs_hi"] - _r["fs_lo"]; _never = 1 - _r["fs_hi"]
    _fig, _ax = plt.subplots(figsize=(9.2, 1.9))
    _left = 0.0
    for _w, _c, _lab in [(_always, GREY, "always-takers"), (_compl, GREEN, "compliers"),
                         (_never, "#d3d3d3", "never-takers")]:
        _ax.barh(0, _w, left=_left, color=_c, edgecolor="white", height=0.6)
        _ax.text(_left + _w / 2, 0, f"{_lab}\n{100 * _w:.0f}%", ha="center", va="center",
                 fontsize=12, fontweight="bold", color="white" if _c != "#d3d3d3" else "0.35")
        _left += _w
    _ax.set_xlim(0, 1); _ax.set_ylim(-0.5, 0.5); _ax.axis("off")
    _ax.set_title(f"The lottery moves only the compliers — {100 * _compl:.0f}% of the base "
                  f"(= the first stage)")
    _fig.tight_layout()
    slide_compliers = mo.vstack([
        mo.md(
            r"""
            #### IV answers a sharp question, not a vague one.

            Split the base by how people react to the nudge. **Always-takers** would see the ad
            regardless; **never-takers** never see it; **compliers** see it *only because* the lottery
            nudged them. We rule out **defiers** — the monotonicity assumption: the nudge never pushes
            anyone *away* from exposure.

            When the lottery flips, always- and never-takers do not budge, so they cancel. Only
            compliers move — so the instrument measures the effect **on compliers**. That is not a
            limitation to apologize for: the compliers are exactly the people a higher bid would newly
            expose. It is the right population for the decision.
            """
        ),
        define(
            "LATE (local average treatment effect)",
            "The average effect among compliers — the people whose treatment the instrument actually "
            "changed. The first-stage share IS the complier share, so a stronger instrument speaks "
            "for a larger slice of the base.",
        ),
        _fig,
    ], gap=1)
    return (slide_compliers,)


@app.cell
def _(BLUE, GREY, ORANGE, TRUE, define, fit_iv, kappa, mo, plt):
    _r = fit_iv(kappa=kappa.value)
    _fig, _ax = plt.subplots(figsize=(9.4, 3.2))
    _lo = min(TRUE, _r["wald"], _r["naive"]) - 3; _hi = max(TRUE, _r["wald"], _r["naive"]) + 3
    _ax.axvspan(_r["wald"] - 1.645 * _r["se"], _r["wald"] + 1.645 * _r["se"], color=BLUE, alpha=0.15)
    _ax.axvline(TRUE, color="black", ls="--", lw=1.6, label=f"truth €{TRUE:.0f}")
    _ax.axvline(_r["naive"], color=ORANGE, lw=2.6, label=f"naive OLS €{_r['naive']:.1f}")
    _ax.axvline(_r["wald"], color=BLUE, lw=2.6, label=f"Wald = 2SLS €{_r['wald']:.1f}")
    _ax.annotate("", xy=(_r["naive"], 0.5), xytext=(_r["wald"], 0.5),
                 arrowprops=dict(arrowstyle="<->", color=GREY, lw=1.3))
    _ax.text((_r["naive"] + _r["wald"]) / 2, 0.6, f"self-selection €{_r['naive'] - _r['wald']:.1f}",
             ha="center", fontsize=11, color="0.3")
    _ax.set_xlim(_lo, _hi); _ax.set_ylim(0, 1); _ax.set_yticks([])
    _ax.set_xlabel("effect of one exposure on sales (€)")
    _ax.set_title(f"OLS vs 2SLS   (first-stage F = {_r['F']:,.0f})")
    _ax.legend(loc="upper left")
    _fig.tight_layout()
    slide_classical = mo.vstack([
        mo.md(
            r"""
            #### Three ordinary regressions and one division — no sampler.

            $$\underbrace{\pi=\E[X\mid Z{=}1]-\E[X\mid Z{=}0]}_{\text{first stage: nudge}\to\text{exposure}}
            \quad
            \underbrace{\delta=\E[Y\mid Z{=}1]-\E[Y\mid Z{=}0]}_{\text{reduced form: nudge}\to\text{sales}}
            \quad
            \hat\beta_{\text{IV}}=\frac{\delta}{\pi}.$$

            The nudge lifted sales by $\delta$ only because it lifted exposure by $\pi$; dividing
            strips out everything else. **Drag $\kappa$** below: as the platform chases intent
            harder, naive OLS climbs away from the truth while 2SLS stays put. The distance between
            the lines is the self-selection the instrument removes.
            """
        ),
        define(
            "2SLS / the Wald ratio",
            r"With one binary instrument and no controls, two-stage least squares equals $\delta/\pi$ "
            r"(reduced form over first stage). The first-stage $F$ measures how strongly $Z$ moves "
            r"$X$; the rule of thumb wants $F \gtrsim 10$.",
        ),
        kappa,
        _fig,
    ], gap=1)
    return (slide_classical,)


@app.cell
def _(BLUE, GREY, ORANGE, TRUE, fit_iv, gamma, kappa, mo, np, plt, slip):
    _gs = np.linspace(0.05, 1.6, 20)
    _med, _lo, _hi, _Fs = [], [], [], []
    for _g in _gs:
        _ws = np.array([fit_iv(gamma=_g, kappa=kappa.value, seed=200 + _s)["wald"] for _s in range(30)])
        _med.append(np.median(_ws)); _lo.append(np.quantile(_ws, .05)); _hi.append(np.quantile(_ws, .95))
        _Fs.append(fit_iv(gamma=_g, kappa=kappa.value)["F"])
    _med, _lo, _hi, _Fs = map(np.array, (_med, _lo, _hi, _Fs))
    _naive_ref = fit_iv(kappa=kappa.value)["naive"]
    _cur_F = fit_iv(gamma=gamma.value, kappa=kappa.value)["F"]
    _fig, _ax = plt.subplots(figsize=(9.4, 3.3))
    _ax.fill_between(_Fs, np.clip(_lo, -40, 100), np.clip(_hi, -40, 100), color=BLUE, alpha=0.18,
                     label="90% range across repeats")
    _ax.plot(_Fs, np.clip(_med, -40, 100), color=BLUE, lw=2.4, label="median Wald")
    _ax.axhline(TRUE, color="black", ls="--", lw=1.4, label=f"truth €{TRUE:.0f}")
    _ax.axhline(_naive_ref, color=ORANGE, lw=1.8, label=f"OLS ≈ €{_naive_ref:.0f}")
    _ax.axvline(10, color=GREY, ls=":", lw=1.8); _ax.text(10, -36, " F = 10", fontsize=11, color="0.35")
    _ax.axvline(_cur_F, color=GREY, lw=1.2, alpha=0.6)
    _ax.set_xscale("log"); _ax.set_ylim(-42, 102)
    _ax.set_xlabel("first-stage F (log scale)"); _ax.set_ylabel("Wald estimate (€)")
    _ax.set_title("Below F = 10 the estimator comes apart")
    _ax.legend(loc="lower right")
    _fig.tight_layout()
    slide_weak = mo.vstack([
        mo.md(
            r"""
            #### A weak instrument is worse than none.

            The whole method divides by the first stage $\pi$. If the instrument barely moves
            exposure, that denominator is near zero and the ratio goes wild. **Drag $\gamma$** toward
            zero and watch $F$ fall through 10. Two things happen at once: the interval balloons
            (expected), and the point estimate drifts back **up toward OLS** (not expected) — a
            near-zero denominator reintroduces exactly the bias the instrument was meant to remove.
            Your current $\gamma$ is the faint vertical line.
            """
        ),
        slip(
            r"A weak instrument can be wrong by multiples of the true effect while still wearing the "
            r"costume of a causal number. Always report the first-stage $F$. When it is small, walk "
            r"away — or report an **Anderson–Rubin** confidence set, valid at any strength "
            r"(worked in Chapter 13's appendix).",
        ),
        gamma,
        _fig,
    ], gap=1)
    return (slide_weak,)


@app.cell
def _(BLUE, GREEN, GREY, ORANGE, SIM, TRUE, beta_gauss, beta_probit, define, mo, plt, rho_probit):
    # REAL posterior draws (precomputed by PyMC in notebooks/11; loaded, never sampled).
    _fig, (_a1, _a2) = plt.subplots(1, 2, figsize=(10.4, 3.3))
    _a1.hist(beta_gauss, bins=45, color=ORANGE, alpha=0.55, density=True,
             label=f"joint-Gaussian (mean €{beta_gauss.mean():.1f})")
    _a1.hist(beta_probit, bins=45, color=BLUE, alpha=0.6, density=True,
             label=f"binary-aware probit (mean €{beta_probit.mean():.1f})")
    _a1.axvline(TRUE, color="black", ls="--", lw=1.6, label=f"truth €{TRUE:.0f}")
    _a1.set_xlabel("effect of one exposure on sales (€)"); _a1.set_yticks([])
    _a1.set_title("The posterior (shipped = probit)"); _a1.legend(fontsize=10)
    _a2.hist(rho_probit, bins=45, color=GREEN, alpha=0.7, density=True)
    _a2.axvline(0, color=GREY, lw=1.4)
    _a2.set_xlabel("endogeneity correlation $\\rho$"); _a2.set_yticks([])
    _a2.set_title(f"ρ: the self-selection, named   (P(ρ > 0) = {(rho_probit > 0).mean():.2f})")
    _fig.tight_layout()
    slide_bayes = mo.vstack([
        mo.md(
            rf"""
            #### Same answer, now carrying a probability — plus the endogeneity, named.

            Same instrument, same four assumptions, same LATE. The Bayesian model changes only how
            uncertainty is reported, and it estimates one thing 2SLS cannot: the endogeneity $\rho$,
            the correlation between the intent that drives exposure and the intent that drives sales.
            A credibly **positive $\rho$** ({SIM['rho']:+.2f}) is the self-selection made visible.

            At $n=3000$ the posterior mean (€{beta_probit.mean():.1f}) and 2SLS (€{SIM['iv_est']:.1f})
            agree to a rounding error — **Bernstein–von Mises**: with enough data the posterior
            collapses onto the classical estimate, which is why its shape is a tidy bell.
            """
        ),
        define(
            "posterior distribution",
            "The full range of effect values consistent with the data and model, each weighted by "
            "plausibility. A confidence interval is a statement about the procedure over many "
            "hypothetical datasets; a posterior is a statement about *this* effect — so it can say "
            "P(effect > c).",
        ),
        mo.callout(
            mo.md("**Note.** The earlier sliders do **not** move these histograms. This is the real "
                  "NUTS output, computed once and bundled — you cannot re-fit a Bayesian model live "
                  "in a browser. The sliders drive the *classical* arm, which is closed-form."),
            kind="neutral",
        ),
        _fig,
    ], gap=1)
    return (slide_bayes,)


@app.cell
def _(BLUE, GREEN, ORANGE, SIM, beta_probit, cost, mo, np, plt, takeaway):
    _c = cost.value
    _p_pays = float((beta_probit > _c).mean())
    _cap = float(np.quantile(beta_probit, 0.10))
    _coin = float(np.median(beta_probit))
    _fig, (_a1, _a2) = plt.subplots(1, 2, figsize=(10.4, 3.3))
    _a1.hist(beta_probit - _c, bins=45, color=BLUE, alpha=0.8, density=True)
    _a1.axvline(0, color=ORANGE, lw=2.0)
    _a1.set_xlabel("net value per exposure (€)"); _a1.set_yticks([])
    _a1.set_title(f"At a €{_c:.1f} cost: P(pays) = {_p_pays:.2f}")
    _grid = np.linspace(beta_probit.min() - 1, beta_probit.max() + 1, 200)
    _pc = np.array([(beta_probit > g).mean() for g in _grid])
    _a2.plot(_grid, _pc, color=BLUE, lw=2.4)
    _a2.axhline(0.90, color="black", ls="--", lw=1.0)
    _a2.axvline(_cap, color=GREEN, ls=":", lw=1.8, label=f"cap €{_cap:.1f} (P=0.9)")
    _a2.axvline(_coin, color="#e0a520", ls=":", lw=1.8, label=f"coin flip €{_coin:.1f}")
    _a2.axvline(_c, color=ORANGE, lw=2.0, label=f"your cost €{_c:.1f}")
    _a2.set_xlabel("assumed cost per exposure (€)"); _a2.set_ylabel("P(exposure pays)")
    _a2.set_ylim(0, 1.02); _a2.set_title("The bid cap is a 90% probability bar"); _a2.legend(fontsize=10)
    _fig.tight_layout()
    slide_euro = mo.vstack([
        mo.md(
            rf"""
            #### The decision is a probability, not a confidence bar.

            The rule: **bid up to $c$ as long as $P(\beta > c) \ge 0.90$.** That cap is simply the
            posterior's 10th percentile — €{SIM['cap']:.1f} here. **Drag the cost** and read both
            numbers off the real draws: the probability the exposure pays at that price, and the
            highest cap you can defend with 90% confidence. Calibrating on the dashboard's
            €{SIM['naive']:.1f} instead sanctions paying about
            **€{SIM['naive'] - beta_probit.mean():.0f} too much** per exposure.
            """
        ),
        takeaway(
            f"Bid cap €{SIM['cap']:.1f} (90% rule), break-even ≈ €{SIM['coinflip']:.1f} (coin-flip), "
            f"headroom €{SIM['headroom']:.1f} over the €10 cost. The dashboard's €{SIM['naive']:.1f} "
            "would have burned the headroom and then some. This is the one thing the classical arm "
            "structurally cannot hand a manager: a probability attached to the euro."
        ),
        cost,
        _fig,
    ], gap=1)
    return (slide_euro,)


@app.cell
def _(BLUE, CRI, GREEN, ORANGE, define, mo, plt, takeaway):
    # Real Criteo market — scalars bundled from nb11b (never retyped). Outcome is conversion lift in
    # percentage points; the 13.98M-row design anchor is the referee (no planted truth).
    _rows = [
        ("naive (dashboard)", CRI["naive"], CRI["naive_lo"], CRI["naive_hi"], ORANGE),
        ("2SLS / Wald", CRI["wald"], CRI["wald_lo"], CRI["wald_hi"], BLUE),
        ("Bayesian", CRI["bayes_mean"], CRI["bayes_lo"], CRI["bayes_hi"], GREEN),
    ]
    _fig, _ax = plt.subplots(figsize=(9.6, 2.9))
    for _i, (_lab, _m, _lo, _hi, _c) in enumerate(_rows):
        _y = len(_rows) - 1 - _i
        _ax.plot([_lo, _hi], [_y, _y], color=_c, lw=3.4, solid_capstyle="round")
        _ax.plot(_m, _y, "o", color=_c, ms=9)
        _ax.text(_m, _y + 0.22, f"+{_m:.1f} pp", ha="center", fontsize=11, fontweight="bold", color=_c)
    _ax.axvline(CRI["anchor"], color="black", ls="--", lw=1.5)
    _ax.text(CRI["anchor"], -0.7, f"design anchor +{CRI['anchor']:.1f} pp  ({CRI['n_full_m']:.0f}M rows)",
             ha="center", va="top", fontsize=10.5, color="0.3")
    _ax.set_yticks(range(len(_rows))); _ax.set_yticklabels([r[0] for r in _rows][::-1])
    _ax.set_ylim(-1.4, len(_rows) - 0.3)
    _ax.set_xlabel("incremental conversion lift (percentage points)")
    _ax.set_title("Criteo uplift data: the dashboard inflates; both causal arms hit the anchor")
    _fig.tight_layout()
    slide_real = mo.vstack([
        mo.md(
            rf"""
            #### The same method on {CRI['n_full_m']:.0f} million rows of real ad-experiment data.

            Criteo's public uplift dataset. The randomized treatment flag is the instrument for who
            was actually exposed — a first stage of only **{CRI['first_pct']:.1f}%** (compliers are a
            thin slice), but an enormously strong one: **F ≈ {CRI['f_stat']:,.0f}**.

            The dashboard gap is **+{CRI['naive']:.1f} pp**. 2SLS lands at **+{CRI['wald']:.1f} pp**,
            the Bayesian fit at **+{CRI['bayes_mean']:.1f} pp** — and both sit on the
            **+{CRI['anchor']:.1f} pp** design anchor computed on all {CRI['n_full_m']:.0f}M rows. The
            wedge between the dashboard and the causal answer is the self-selection, now measured
            rather than assumed.
            """
        ),
        define(
            "external anchor",
            "A trustworthy estimate from far more data or a cleaner design, used as the referee. Here "
            "the full-sample randomized difference plays truth, so we can grade the subsample's IV "
            "honestly instead of just admiring its confidence interval.",
        ),
        _fig,
        takeaway(
            f"At €{CRI['cost']:.2f} per exposure and €{CRI['conv_value']:.2f} per incremental visit, "
            f"the defensible cap is €{CRI['cap']:.2f}. Bidding the dashboard number across "
            f"{CRI['exposures_quarter']:,.0f} exposures a quarter would overpay about "
            f"**€{CRI['premium_quarter']:,.0f} every quarter**."
        ),
    ], gap=1)
    return (slide_real,)


@app.cell
def _(BLUE, GREEN, GOLD, GREY, draw_dag, mo, plt, slip, takeaway):
    _fig, _ax = plt.subplots(figsize=(5.2, 3.4))
    draw_dag(
        _ax,
        nodes={"U": (0.5, 0.95, GREY), "Z": (0.06, 0.26, GOLD),
               "X": (0.5, 0.26, BLUE), "Y": (0.94, 0.26, GREEN)},
        edges=[("Z", "X", "ok"), ("X", "Y", "ok"), ("U", "X", "ok"), ("U", "Y", "ok"),
               ("Z", "Y", "bad")],
        note="The red arrow — a side-channel Z→Y — is what breaks exclusion.",
    )
    _ax.set_title("The failure no test can see")
    _fig.tight_layout()
    slide_wrong = mo.vstack([
        mo.md(
            r"""
            #### Two failures you can catch; one you cannot.

            - **Weak instrument** — a small first-stage $F$. Catchable: look at the $F$ (the slider
              two slides back).
            - **Exclusion violation** — the red arrow. If the lottery moved sales through *any* other
              path, the estimate is biased and **no diagnostic will flag it**. Defend by design: pick
              an instrument so content-free that a side-channel is implausible, then price how big one
              would have to be to flip the decision.
            - **Scope** — IV speaks for **compliers**, not the whole base. It licenses a bid on
              *incremental* exposure — exactly what a bid buys — and does not transfer to a different
              instrument or market.
            """
        ),
        slip(
            "The seductive mistake is to trust a tight confidence interval. A weak or invalid "
            "instrument can be precisely wrong. Precision is not validity — the assumptions are, and "
            "two of them live outside the data."
        ),
        takeaway(
            "One number, gotten right: what an exposure is worth to the people a bid can move. "
            "Instrument → first-stage F → 2SLS → posterior → P(β > c) → a bid cap you can defend in "
            "the room. That is the whole method."
        ),
        _fig,
    ], gap=1)
    return (slide_wrong,)


# ============================== the deck ==============================

@app.cell
def _(mo):
    header = mo.md(
        """
        # What is one ad exposure worth?
        #### Instrumental variables — pricing incremental exposure you cannot randomize

        &nbsp;

        | | |
        |---|---|
        | **Course** | *Causal Inference & XAI for Business* · SDA Bocconi |
        | **Chapter** | 13 · Endogenous exposure and instrumental variables |
        | **How to use** | Open one slide at a time. Sliders are live; the posterior is real, precomputed NUTS output. |
        """
    )
    header
    return


@app.cell
def _(define):
    case = define(
        "The running case",
        "A retailer buys display ads through a demand-side platform and must set a **bid cap** — the "
        "most it will pay for one ad **exposure**. The platform's dashboard shows exposed users "
        "converting far more, and wants the cap raised. We follow this one decision from the wrong "
        "number to a bid cap the growth team can defend.",
    )
    case
    return


@app.cell
def _(mo, slide_bayes, slide_classical, slide_compliers, slide_confound, slide_decision,
      slide_euro, slide_instrument, slide_real, slide_weak, slide_wrong):
    # The deck. multiple=False → opening a slide collapses the previous one, so it advances like a
    # slide deck. lazy=True → each slide's content renders when you open it.
    mo.accordion(
        {
            "**1 — The decision** · what is one exposure worth?": slide_decision,
            "**2 — Why the dashboard lies** · confounding and potential outcomes": slide_confound,
            "**3 — The instrument** · a lottery, and its three conditions": slide_instrument,
            "**4 — Compliers** · who the answer is about (LATE)": slide_compliers,
            "**5 — The classical estimate** · 2SLS = Wald  ·  ▸ slider": slide_classical,
            "**6 — What can go wrong** · weak instruments  ·  ▸ slider": slide_weak,
            "**7 — What Bayes adds** · the posterior, and ρ": slide_bayes,
            "**8 — The decision, in euros** · P(β > c), the cap  ·  ▸ slider": slide_euro,
            "**9 — On real data** · Criteo, 14 million rows": slide_real,
            "**10 — Failure modes, scope, and recap**": slide_wrong,
        },
        multiple=False,
        lazy=True,
    )
    return


@app.cell
def _():
    # <<BLOB-START>>
    BLOB = (
        "eNplnd2OZUdupV+lkFczgFAdEWT8ae5mgLnyDAzYvjIMoVrKtgotqdRVJdkNo999gvxW5DmNMdBKV+b52TuCQS4uLnL/18vXz7+9"
        "vnxb+/vyzcsvL99aKef/+f7Tl6/nlyV++cfXrx+++/Xzpz9+PL/61zrf1zG/qet9GX18U8f7Yf382997Weff9t72XvFva7V/c14+"
        "Zt3fnM8fa/o3dZ/3jRY/t9Uaf6/LRvx9trHi/fN8QHxu6dvje0ZZHn/37fl9szeL1/XZPL9/e43Pq3vl57Yav93LLN5VRsur8fjQ"
        "+LLNtcVnnFfVueI75pj5nav3Fn+vpdd4t50X5D21+Hne3kpec/OS3zJ9z/jpvvL9u+THeuHbvNnm0o1btVVZspW3cL52xCX7Wnzs"
        "aDP+bbZ7/L1YaflzxVLVs5Q7P7+fNc3vWbHkfj6nr/i7zVii872zrPjeXmIrzut3LNV8v1bcdjtLFv/283fP2xwWv9/ve20tlmPN"
        "s/Stns/v3LbF58z3sUjrfa2NtXTLX9rMi6j58+xjfsj594r9PF/W+b0v33mzNnJfbbaedlSnLrrlWrbq2MtmsaoXvqeGHdnZ2Zl2"
        "ZdvyZvysdt5MLlqPvUu7WLu2+Hez3vNzVjk3Vc4iz8Xld/Z8WO5xaz0Xd86ZlrN3yeuqo+d17jny9t0W39M8f98xvyKzPdaeq7NY"
        "HTfLJRxpMWcVSs2rPe/On6uVvNrecqf7YKVrXfnvOUte3OocqnN4psy65uJNDLKOXWMx9s5rXt1XXNQ9S7Pnq9x32lvvO/898iid"
        "pbSeS7U4BbvuPMm7NF6WK3t2LK949ti/c6mxPX6+saWNtT5zmXc3rjzvqIWbyOUqO7a5nXXpuV6W22THLdS8pnGMNM2nlHQnrZX8"
        "vLZHfs6qZWPTXHOrLGxbNc9MqSM/fxdPc1zTcqXmWHxu7tNxBDoD3Tuv25bX0XLJzrbOmhtiE/fUtjfMhSNe5szXmVb+7G+ae48z"
        "k+/vuUobG2UFd27PObAyjnr2OWzxLDQHMc9Sj43Jm192bvZsH19pY6XnOxY+WMq12RfPpSubpTreiuMelh42lktqxw1xMrrhjvoe"
        "uXTWBl5s71yqcfxJ7PNZirT0Vlj6OVoukZfWMdKRtrw6PvYsWS7JXp4e3Hq4t3MXdWAKRZ5ieLqZNicntLJkaYXnoHp87bEYl2+O"
        "uHB8szWWprHuPS3cqqWr6i0XcocDjwU9n82t44RWC095rMxKnpfji/JDR+u5dG1X+bLGMT2bez5mGI5z18IKFxakDy6t1/z0sQd+"
        "NsNDXExNm9p95+t72vxZkDLS3/saeRXunOKVIStsajdtGFdv6a7r9PSgLW61nuUlGK3tjhnUtEyTJZ842Tm2FVcxc9cqm8d5Oivh"
        "lt9pxncfP5X34N7yW9oKt3jcZPF0t91muu2e7v14/xMsYonmnrm5a8a9HU/UK9HBp8nX5L0u2aqOx+T0ll7StEctuXJt4XQ99++s"
        "8H7zpul5crd3BEj827xxmkN7oIhiR+WE9EUgC2cT5lHZqOaV09lnutNdWKPj6/Nm2gQfjK44bx0fUyoHaaQtes97Occuvax5WTK2"
        "PIdnSfLWrVhGumIrjWu6VXz9wnPgUH23XOnEU+dTDWNZbeXLSllpLCdusUS757eN2LC4t9Uwh5pfflARXy4rsbI6sbvnPnUrwLa8"
        "+PMTEOVEAK+eIG1U73hRzkUdNb32AQ5Yy8ofRQZ/fK7hNIecoBNwNof3QMEGbjJhwnDOTU40judOz2T58XETJSNO+sHEBjuN79yb"
        "40cXx76uwU0BSXre7Ln5Hp7qYMLV024OlMy1POfWCFqFoLAJYudQ6EitXKTaa3qyPTseaxF8ihHFD/YEG2zWvlcwzTCCyag9PfDU"
        "InsFw/iqQIex5cvYi9Vl7Wz5sRctywDXpdmfmLXY09Z7OoaDC/O2ywIytUHMWumvwqIwqSHENiYx9thxB6qNSbBy5/LAqecUYrjx"
        "voMDR+f4HR/QMU0zbAxHZRuHf5YP/7czJE85plZw3edM5+6fEN3kNjHBPvJnSSdw0PkoE+fQwUAgiJEH5ACx9MLhlM9pbGcVSsvV"
        "qxMvXffEAQLGW+LEjIJ5Wptxxr3VBn6suZhz6oB0bn7KxmcjPJXMFY6DtJmbMIrPWJyu/KYMbOf4KqJxQriweTb3pCkAljyI4Q1G"
        "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"
        "PiIa9ZnccMdV+3smDfEkOxoamepA4zTDDmos8V9mfkY0+Wcrt54ukh2YDK3gwQ3Zd61HojHsgvbdWIwfP3/85c+5BhTROZEwHMBB"
        "UsQMVKAIYhe/WPV8yNcvP51NDttq5x+ff/v6Y/6rfPPy4fPP/zOW+T9fvl1nPbVy2Qb7t7998/LLp6+vL9++/OPn1+8//fzrb19f"
        "f3j3x7++i9/+8dOnP3/5Q63vPnx997//5R/+4d1/+8e//p//9Yf/+y///E/fvPv+w/c/vv7w39+/++cfX9/9/OHzx58/vfvp9fuv"
        "v31+fffTpw8/fHn34Zcf3v3w8cuvP33465d3X398/fL6P959/Prul9ffXz+/+/zbL1/exce9f/dPr6/v4qv+8P2PH379+vr5yx8+"
        "/v7+6+t/vn85S/Px57j0Xz58/P1cZIxKnSHymSumFZw9f/mPDz/9cG4m5lAd1HP+WlcpUX19+fj7d69fvv793+Y5lCdUv/zpuy9f"
        "P8TfenQ+n3T2RI0Sj8FY528fP8fbgBzz/HKveYBMUHEvf/ry3U+fXr7tOQUhpraOHV8WF3L+9OPHl2/nyC6YGgRSzA07X/Yfrz/8"
        "+7n4mLTQj+c579qeY31evv/w67kGi771qGKWCJIBtV6+//Txlz/99PHXvPoTt+MpofPE2khkX358/fDD50+fzsL8f++0s52v5+Jj"
        "KMls5VzJPtl05Icvf/zw19cv3/38+uEXPvTv/n6uMr3E/Xu00geVfhDG7lE0jr7WWBMLIUY5eW6kczXgQna8/pR/rPHA1h0dcrON"
        "Fb2o+cdYlpS/lL0PKFoh+QpV0THMfGM87G4+bxB/irc1cvi3P81jr99//vj19dOTVdjK8etjR3krH3ovq7BMUz2ePzriuRm1P3b+"
        "gPcY+n4Qc4kO35BPs/Pf/fp9/Pm4hGiK4f9yasnLh1++//HT53NRPOMpDK3HcztdZpg303KO4D4AewdADuKQP8btmEe2EFOIYnRr"
        "VCy5h3ynxTDxGQOXT9bTg4nTH+OdTqEjxrQ0nx612L/b0bazvHG2JJ633EM9qb/nRUVwORvSYkbNDpZUf9RFnV+dmBtJTg+S/G72"
        "iQ8hHGjRYHoWIQzzsdnH7Ec8FTz6zA5YCPXa024fL31i7VqjhdA+mMBj07/8/t3vH3767WxZjdB98HE//4vnth+Pff6uY6dzkTi0"
        "rpNsHbsJYvj84dfPrz9//O3n7/7y24fPx1O8fLvPhsf85B4DByxqhC+v//nrpy/HC315vOpcTfxfOMNfvvvTbz/99N3Pee52zDU7"
        "H/unT2eDvv/0u14br8tfsbZhRnuWsKQQmuxmf/vb/wMF/MC1"
    )
    # <<BLOB-END>>
    return (BLOB,)


if __name__ == "__main__":
    app.run()
