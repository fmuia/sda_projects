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
        "eNplnd2OZUdupV+lkFczgFAdEWT8aS4NzJVnYMD2lWEI1VK2VbCk0lSVZDeMfvcJ8luR5whuoDu7Ms/P3hEMcnFxkfu/Xr5+/u31"
        "5dva35dvXn55+dZKOf/n+09fvp5flvjln1+/fvju18+f/vzx/Opf6nxfx/ymrvdl9PFNHe+H9fNvf+9lnX/be9t7xb+t1f7NefmY"
        "dX9zPn+s6d/Ufd43WvzcVmv8vS4b8ffZxor3z/MB8bmlb4/vGWV5/N235/fN3ixe12fz/P7tNT6v7pWf22r8di+zeFcZLa/G40Pj"
        "yzbXFp9xXlXniu+YY+Z3rt5b/L2WXuPddl6Q99Ti53l7K3nNzUt+y/Q946f7yvfvkh/rhW/zZptLN27VVmXJVt7C+doRl+xr8bGj"
        "zfi32e7x92Kl5c8VS1XPUu78/H7WNL9nxZL7+Zy+4u82Y4nO986y4nt7ia04r9+xVPP9WnHb7SxZ/NvP3z1vc1j8fr/vtbVYjjXP"
        "0rd6Pr9z2xafM9/HIq33tTbW0i1/aTMvoubPs4/5IeffK/bzfFnn9758583ayH212XraUZ266JZr2apjL5vFql74nhp2ZGdnZ9qV"
        "bcub8bPaeTO5aD32Lu1i7dri3816z89Z5dxUOYs8F5ff2fNhucet9VzcOWdazt4lr6uOnte558jbd1t8T/P8fcf8isz2WHuuzmJ1"
        "3CyXcKTFnFUoNa/2vDt/rlbyanvLne6Dla515b/nLHlxq3OozuGZMuuaizcxyDp2jcXYO695dV9xUfcszZ6vct9pb73v/PfIo3SW"
        "0nou1eIU7LrzJO/SeFmu7NmxvOLZY//Opcb2+PnGljbW+sxl3t248ryjFm4il6vs2OZ21qXnellukx23UPOaxjHSNJ9S0p20VvLz"
        "2h75OauWjU1zza2ysG3VPDOljvz8XTzNcU3LlZpj8bm5T8cR6Ax077xuW15HyyU72zprbohN3FPb3jAXjniZM19nWvmzv2nuPc5M"
        "vr/nKm1slBXcuT3nwMo46tnnsMWz0BzEPEs9NiZvftm52bN9fKWNlZ7vWPhgKddmXzyXrmyW6ngrjntYethYLqkdN8TJ6IY76nvk"
        "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"
        "/fj67ucPnz/+/OndT6/ff/3t8+u7nz59+OHLuw+//PDuh49ffv3pw1+/vPv64+uX1//17uPXd7+8/v76+d3n33758i4+7v27f3x9"
        "fRdf9afvf/zw69fXz1/+9PH3919f//P9y1m1jz+/fPtfL798+Pj7uciYzzlDWTJXtMgfm3z5jw8//fDybQ4/OqH2/LWuUqLk9/Lx"
        "9+9ev3z949/msYQTH17+8t2Xrx/ibz3abU8OdVxViWcvrPO3j5/jbcS5eX651zzRM/ifl798+e6nTy/f9my9j1GhY8eXxYWcP/34"
        "8eXbObL1Ip5cHw+IP37g5T9ef/i3c/HR3t+PuZ93bc9ZMi/ff/j1XINFs3SUzkp45ojvL99/+vjLX376+Gte/QkW8WjKeRx8ZE8v"
        "P75++OHzp09nYf7bO+1s5+u5+JiEMVs5V7JPChdJycufP/z19ct3P79++IUP/cPfz1Wmad6/R/928LcnrO0elcpopow1saj+l5Nc"
        "RQ5RI0Zlm+VP+ccaTwnd0ZZ1cusVDZD5x1iW1FyUvU8kXqEzCinLy4fP+cZ4wtp83iD+FG9rJI5vf5p/O2vz+ePX109PVmErZ36P"
        "HTWVfNK6rMIyN/J46OWIhzXU/tj5gxhj0viBaSXaSkOzy85/9+v38ef3x5Ht+58clfHy4Zfvf/z0+VwUDxYKQ+vxsEiXGebNtBxe"
        "tw+qi2fBt2Cr+GPcjnlA1Bh9E/NCo0zGPeQ7LSZYz5jye6B2D/pHf4x3Oux6zAZpPj0KgH/Y0baTUz9bEg/57SHZ09/zosKjnQ1p"
        "MRhlBzWnP+qizq+Oow9k3YOZvZt9nFJUq1t0NZ5FCMN8bPYx+xGPoo7mphOhQjL1tNv1HKkTnNdooe4O+unY9C+/f/f7h59+O1tW"
        "I14cUNbPf+Nh4cdtnr/r2OlcJPip6yD8YzfBRp4//Pr59eePv/383f/77cPn4ylevt1nw2Nob48ud4vC1Mvrf/766cvxQl8erzpX"
        "E/95X86SfveX33766buf89ztGKZ1PvYvn84Gff/pd702Xpe/Ym3DjPYsYUmhbtjN/va3/w85qGlT"
    )
    # <<BLOB-END>>
    return (BLOB,)


if __name__ == "__main__":
    app.run()
