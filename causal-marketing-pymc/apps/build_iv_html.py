"""Generate a self-contained, Quarto-style HTML lecture for Chapter 13 (instrumental variables).

The output is ONE file, apps/iv_lecture.html, that opens in any browser with no server, no runtime,
and no external assets — the counterpart to course/Notebook1_Experiments.html.

It stays interactive without any live computation: every slider state is PRE-RENDERED to a matplotlib
PNG frame and embedded as a data URI, and a few lines of vanilla JS swap the image as you drag. So the
numbers are exactly the notebook's (rendered by the real numpy + fixed seed, and the bundled posterior
draws), never re-simulated in the browser.

Build:  .venv/bin/python apps/build_iv_html.py     (or `make html-iv`)
Data:   apps/iv_lecture_data.json (draws + nb11/nb11b scalars), from `make data-iv`.
"""
from __future__ import annotations

import base64
import io
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, FancyArrowPatch

HERE = Path(__file__).resolve().parent
OUT = HERE / "iv_lecture.html"

NAVY = "#1f3a5f"
BLUE, GREEN, ORANGE, GOLD, GREY = "#2c6fbb", "#2e8b57", "#d1622b", "#e0a520", "#8a8a8a"
plt.rcParams.update({
    "font.size": 12.5,
    "axes.titlesize": 14, "axes.titleweight": "bold", "axes.titlecolor": NAVY,
    "axes.labelsize": 12, "xtick.labelsize": 10.5, "ytick.labelsize": 10.5, "legend.fontsize": 10.5,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.alpha": 0.22, "figure.facecolor": "white",
})

D = json.loads((HERE / "iv_lecture_data.json").read_text())
BETA = np.array(D["beta_probit"])
BETA_G = np.array(D["beta_gauss"])
RHO = np.array(D["rho_probit"])
SIM, CRI = D["sim"], D["criteo"]
TRUE = float(D["true"])


# ----------------------------------------------------------------------------- model + figures

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


def uri(fig, dpi):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=dpi, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


def draw_dag(ax, nodes, edges, note=""):
    R = 0.085
    ax.set_xlim(-0.02, 1.02); ax.set_ylim(-0.08, 1.10); ax.axis("off"); ax.set_aspect("equal")
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
        ax.text(x, y, name, ha="center", va="center", color="white", fontweight="bold",
                fontsize=15, zorder=4)
    if note:
        ax.text(0.5, -0.04, note, ha="center", va="top", fontsize=10, color=NAVY,
                transform=ax.transAxes)


def fig_confound():
    fig, ax = plt.subplots(figsize=(5.0, 3.2))
    draw_dag(ax, {"U": (0.5, 0.95, GREY), "X": (0.16, 0.26, BLUE), "Y": (0.84, 0.26, GREEN)},
             [("U", "X", "ok"), ("U", "Y", "ok"), ("X", "Y", "ok")],
             "U = buying intent (unobserved).   X = exposure.   Y = sales.")
    ax.set_title("Why the dashboard lies")
    return uri(fig, 130)


def fig_instrument():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(9.6, 3.4))
    draw_dag(a1, {"U": (0.5, 0.95, GREY), "Z": (0.06, 0.26, GOLD), "X": (0.5, 0.26, BLUE),
                  "Y": (0.94, 0.26, GREEN)},
             [("Z", "X", "ok"), ("X", "Y", "ok"), ("U", "X", "ok"), ("U", "Y", "ok")],
             "Z reaches Y only through X.   No arrow U→Z, no arrow Z→Y.")
    a1.set_title("A valid instrument")
    a2.axis("off")
    a2.text(0.0, 1.0, "What makes Z an instrument", fontweight="bold", fontsize=12.5, color=NAVY)
    for i, (h, t) in enumerate([
        ("1.  Relevance", "Z actually moves exposure X.\nTestable — it is the first-stage F."),
        ("2.  As-good-as-random", "Z is unrelated to intent U.\nHolds by design when Z is a lottery."),
        ("3.  Exclusion", "Z affects sales Y only through X.\nUntestable — argued, never checked."),
    ]):
        y = 0.78 - i * 0.27
        a2.text(0.02, y, h, fontweight="bold", fontsize=11.5, color=BLUE)
        a2.text(0.05, y - 0.09, t, fontsize=10.5, color="0.25", va="top")
    return uri(fig, 130)


def fig_compliers():
    r = fit_iv()
    always, compl, never = r["fs_lo"], r["fs_hi"] - r["fs_lo"], 1 - r["fs_hi"]
    fig, ax = plt.subplots(figsize=(9.0, 1.9))
    left = 0.0
    for w, c, lab in [(always, GREY, "always-takers"), (compl, GREEN, "compliers"),
                      (never, "#d3d3d3", "never-takers")]:
        ax.barh(0, w, left=left, color=c, edgecolor="white", height=0.6)
        ax.text(left + w / 2, 0, f"{lab}\n{100 * w:.0f}%", ha="center", va="center", fontsize=11.5,
                fontweight="bold", color="white" if c != "#d3d3d3" else "0.35")
        left += w
    ax.set_xlim(0, 1); ax.set_ylim(-0.5, 0.5); ax.axis("off")
    ax.set_title(f"The lottery moves only the compliers — {100 * compl:.0f}% of the base "
                 f"(= the first stage)")
    return uri(fig, 130)


def fig_classical(kappa):
    r = fit_iv(kappa=kappa)
    fig, ax = plt.subplots(figsize=(8.6, 3.0))
    lo = min(TRUE, r["wald"], r["naive"]) - 3; hi = max(TRUE, r["wald"], r["naive"]) + 3
    ax.axvspan(r["wald"] - 1.645 * r["se"], r["wald"] + 1.645 * r["se"], color=BLUE, alpha=0.15)
    ax.axvline(TRUE, color="black", ls="--", lw=1.6, label=f"truth €{TRUE:.0f}")
    ax.axvline(r["naive"], color=ORANGE, lw=2.6, label=f"naive OLS €{r['naive']:.1f}")
    ax.axvline(r["wald"], color=BLUE, lw=2.6, label=f"Wald = 2SLS €{r['wald']:.1f}")
    ax.annotate("", xy=(r["naive"], 0.5), xytext=(r["wald"], 0.5),
                arrowprops=dict(arrowstyle="<->", color=GREY, lw=1.3))
    ax.text((r["naive"] + r["wald"]) / 2, 0.6, f"self-selection €{r['naive'] - r['wald']:.1f}",
            ha="center", fontsize=10.5, color="0.3")
    ax.set_xlim(lo, hi); ax.set_ylim(0, 1); ax.set_yticks([])
    ax.set_xlabel("effect of one exposure on sales (€)")
    ax.set_title(f"OLS vs 2SLS   (first-stage F = {r['F']:,.0f})")
    ax.legend(loc="upper left")
    return uri(fig, 105), r


def fig_weak(gamma, kappa=12.0):
    gs = np.linspace(0.05, 1.6, 20)
    med, lo, hi, Fs = [], [], [], []
    for g in gs:
        ws = np.array([fit_iv(gamma=g, kappa=kappa, seed=200 + s)["wald"] for s in range(30)])
        med.append(np.median(ws)); lo.append(np.quantile(ws, .05)); hi.append(np.quantile(ws, .95))
        Fs.append(fit_iv(gamma=g, kappa=kappa)["F"])
    med, lo, hi, Fs = map(np.array, (med, lo, hi, Fs))
    naive_ref = fit_iv(kappa=kappa)["naive"]
    cur = fit_iv(gamma=gamma, kappa=kappa)
    fig, ax = plt.subplots(figsize=(8.6, 3.1))
    ax.fill_between(Fs, np.clip(lo, -40, 100), np.clip(hi, -40, 100), color=BLUE, alpha=0.18,
                    label="90% range across repeats")
    ax.plot(Fs, np.clip(med, -40, 100), color=BLUE, lw=2.4, label="median Wald")
    ax.axhline(TRUE, color="black", ls="--", lw=1.4, label=f"truth €{TRUE:.0f}")
    ax.axhline(naive_ref, color=ORANGE, lw=1.8, label=f"OLS ≈ €{naive_ref:.0f}")
    ax.axvline(10, color=GREY, ls=":", lw=1.8); ax.text(10, -36, " F = 10", fontsize=10, color="0.35")
    ax.axvline(cur["F"], color="#c0392b", lw=2.0, label=f"your γ (F = {cur['F']:,.0f})")
    ax.set_xscale("log"); ax.set_ylim(-42, 102)
    ax.set_xlabel("first-stage F (log scale)"); ax.set_ylabel("Wald estimate (€)")
    ax.set_title("Below F = 10 the estimator comes apart")
    ax.legend(loc="lower right")
    return uri(fig, 105), cur


def fig_bayes():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(10.0, 3.2))
    a1.hist(BETA_G, bins=45, color=ORANGE, alpha=0.55, density=True,
            label=f"joint-Gaussian (mean €{BETA_G.mean():.1f})")
    a1.hist(BETA, bins=45, color=BLUE, alpha=0.6, density=True,
            label=f"binary-aware probit (mean €{BETA.mean():.1f})")
    a1.axvline(TRUE, color="black", ls="--", lw=1.6, label=f"truth €{TRUE:.0f}")
    a1.set_xlabel("effect of one exposure on sales (€)"); a1.set_yticks([])
    a1.set_title("The posterior (shipped = probit)"); a1.legend(fontsize=9.5)
    a2.hist(RHO, bins=45, color=GREEN, alpha=0.7, density=True)
    a2.axvline(0, color=GREY, lw=1.4)
    a2.set_xlabel("endogeneity correlation ρ"); a2.set_yticks([])
    a2.set_title(f"ρ: the self-selection, named   (P(ρ > 0) = {(RHO > 0).mean():.2f})")
    return uri(fig, 125)


def fig_euro(cost):
    p_pays = float((BETA > cost).mean())
    cap = float(np.quantile(BETA, 0.10))
    coin = float(np.median(BETA))
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(10.0, 3.2))
    a1.hist(BETA - cost, bins=45, color=BLUE, alpha=0.8, density=True)
    a1.axvline(0, color=ORANGE, lw=2.0)
    a1.set_xlabel("net value per exposure (€)"); a1.set_yticks([])
    a1.set_title(f"At a €{cost:.1f} cost: P(pays) = {p_pays:.2f}")
    grid = np.linspace(BETA.min() - 1, BETA.max() + 1, 200)
    pc = np.array([(BETA > g).mean() for g in grid])
    a2.plot(grid, pc, color=BLUE, lw=2.4)
    a2.axhline(0.90, color="black", ls="--", lw=1.0)
    a2.axvline(cap, color=GREEN, ls=":", lw=1.8, label=f"cap €{cap:.1f} (P=0.9)")
    a2.axvline(coin, color=GOLD, ls=":", lw=1.8, label=f"coin flip €{coin:.1f}")
    a2.axvline(cost, color=ORANGE, lw=2.0, label=f"your cost €{cost:.1f}")
    a2.set_xlabel("assumed cost per exposure (€)"); a2.set_ylabel("P(exposure pays)")
    a2.set_ylim(0, 1.02); a2.set_title("The bid cap is a 90% probability bar"); a2.legend(fontsize=9.5)
    return uri(fig, 105), dict(p_pays=p_pays, cap=cap)


def fig_criteo():
    rows = [("naive (dashboard)", CRI["naive"], CRI["naive_lo"], CRI["naive_hi"], ORANGE),
            ("2SLS / Wald", CRI["wald"], CRI["wald_lo"], CRI["wald_hi"], BLUE),
            ("Bayesian", CRI["bayes_mean"], CRI["bayes_lo"], CRI["bayes_hi"], GREEN)]
    fig, ax = plt.subplots(figsize=(9.2, 2.8))
    for i, (lab, m, lo, hi, c) in enumerate(rows):
        y = len(rows) - 1 - i
        ax.plot([lo, hi], [y, y], color=c, lw=3.4, solid_capstyle="round")
        ax.plot(m, y, "o", color=c, ms=9)
        ax.text(m, y + 0.22, f"+{m:.1f} pp", ha="center", fontsize=10.5, fontweight="bold", color=c)
    ax.axvline(CRI["anchor"], color="black", ls="--", lw=1.5)
    ax.text(CRI["anchor"], -0.7, f"design anchor +{CRI['anchor']:.1f} pp  ({CRI['n_full_m']:.0f}M rows)",
            ha="center", va="top", fontsize=10, color="0.3")
    ax.set_yticks(range(len(rows))); ax.set_yticklabels([r[0] for r in rows][::-1])
    ax.set_ylim(-1.4, len(rows) - 0.3)
    ax.set_xlabel("incremental conversion lift (percentage points)")
    ax.set_title("Criteo uplift data: the dashboard inflates; both causal arms hit the anchor")
    return uri(fig, 125)


def fig_failure():
    fig, ax = plt.subplots(figsize=(5.0, 3.2))
    draw_dag(ax, {"U": (0.5, 0.95, GREY), "Z": (0.06, 0.26, GOLD), "X": (0.5, 0.26, BLUE),
                  "Y": (0.94, 0.26, GREEN)},
             [("Z", "X", "ok"), ("X", "Y", "ok"), ("U", "X", "ok"), ("U", "Y", "ok"),
              ("Z", "Y", "bad")],
             "The red arrow — a side-channel Z→Y — is what breaks exclusion.")
    ax.set_title("The failure no test can see")
    return uri(fig, 130)


def fig_equation():
    fig = plt.figure(figsize=(9.2, 0.95)); fig.patch.set_alpha(0)
    fig.text(0.5, 0.5,
             r"$\pi=E[X\mid Z{=}1]-E[X\mid Z{=}0]"
             r"\qquad \delta=E[Y\mid Z{=}1]-E[Y\mid Z{=}0]"
             r"\qquad \hat\beta_{IV}=\dfrac{\delta}{\pi}$",
             ha="center", va="center", fontsize=17, color="#16273f")
    return uri(fig, 150)


# ----------------------------------------------------------------------------- assemble figures
print("rendering figures ...")
CAP = float(np.quantile(BETA, 0.10))
COIN = float(np.median(BETA))
FIGS = {
    "confound": fig_confound(), "instrument": fig_instrument(), "compliers": fig_compliers(),
    "bayes": fig_bayes(), "criteo": fig_criteo(), "failure": fig_failure(), "eq": fig_equation(),
}

KVALS = list(range(0, 25, 2))                       # kappa 0..24 step 2
K_FRAMES, K_LAB = [], []
for k in KVALS:
    u, r = fig_classical(float(k))
    K_FRAMES.append(u); K_LAB.append(f"κ = {k} €  ·  OLS €{r['naive']:.1f} vs 2SLS €{r['wald']:.1f}")
K_DEFAULT = KVALS.index(12)

GVALS = [round(g, 2) for g in np.linspace(0.1, 2.0, 20)]
G_FRAMES, G_LAB = [], []
for g in GVALS:
    u, r = fig_weak(g)
    G_LAB.append(f"γ = {g:.2f}  ·  F ≈ {r['F']:,.0f}"); G_FRAMES.append(u)
G_DEFAULT = min(range(len(GVALS)), key=lambda i: abs(GVALS[i] - 1.1))

CVALS = list(range(4, 23))                          # cost 4..22
C_FRAMES, C_LAB = [], []
for c in CVALS:
    u, r = fig_euro(float(c))
    C_LAB.append(f"cost = €{c}  ·  P(pays) = {r['p_pays']:.2f}  ·  cap €{r['cap']:.1f}")
    C_FRAMES.append(u)
C_DEFAULT = CVALS.index(10)
print(f"  {len(K_FRAMES)+len(G_FRAMES)+len(C_FRAMES)} interactive frames + {len(FIGS)} static")


# ----------------------------------------------------------------------------- HTML
def callout(kind, icon, title, body):
    return (f'<div class="callout {kind}"><div class="ct">{icon}&nbsp; {title}</div>'
            f'<div class="cb">{body}</div></div>')


def figure(src, cap):
    return f'<figure><img src="{src}" alt="{cap}"><figcaption>{cap}</figcaption></figure>'


def interactive(sid, label, frames, labels, default):
    arr = "[" + ",".join(f'"{f}"' for f in frames) + "]"
    labs = "[" + ",".join(json.dumps(x) for x in labels) + "]"
    return f"""
    <div class="interactive">
      <div class="slider-row">
        <label for="{sid}">{label}</label>
        <input type="range" id="{sid}" min="0" max="{len(frames) - 1}" step="1" value="{default}">
        <output id="{sid}o"></output>
      </div>
      <figure><img id="{sid}i" alt="interactive figure"></figure>
    </div>
    <script>window.__WIRE__.push(["{sid}", {arr}, {labs}, {default}]);</script>
    """


SECTIONS = [
    ("s1", "The decision", f"""
      <p class="lead">A retailer must set one number: the most it will pay for a single ad exposure.</p>
      <p>The demand-side platform's dashboard says users who <b>saw</b> an ad convert far more than
      users who did not, and it wants the bid cap raised. That number is honest arithmetic and the
      <b>wrong number to bid on</b>: the platform <i>chose</i> whom to expose, and it chose people
      already likely to buy. The exposed carry their own intent into the comparison.</p>
      <p>On this chapter's simulated market the dashboard prices an exposure at
      <b>€{SIM['naive']:.1f}</b>; the true worth is <b>€{TRUE:.0f}</b>. Bidding the dashboard number
      pays a <b>€{SIM['naive'] - TRUE:.0f} premium per exposure</b> for intent the retailer already
      owned.</p>
      {callout("idea", "◆", "The idea in one line",
               "To bid on a number, the number has to be <b>causal</b> — the sales an exposure "
               "<i>creates</i>, not the sales that would have happened anyway. Correlation from a "
               "targeting engine is the opposite of what a bid needs.")}
      {callout("takeaway", "€", "Manager's takeaway",
               f"A €{SIM['naive'] - TRUE:.0f} error per exposure is not rounding. Across millions of "
               "exposures a quarter it is the whole media budget's worth of over-payment. This "
               "lecture is one method for getting the number right when you <b>cannot</b> randomize "
               "who sees the ad.")}
    """),
    ("s2", "Why the dashboard lies", f"""
      <p class="lead">The two groups were never comparable to begin with.</p>
      <p>Write <i>Y<sub>i</sub></i>(1) for what customer <i>i</i> would buy <b>if exposed</b> and
      <i>Y<sub>i</sub></i>(0) if <b>not</b>. The effect on that customer is the difference; we only
      ever see one of the two. The number we want is the average of that difference over the people a
      bid can move.</p>
      <p>The dashboard instead reports E[Y | exposed] − E[Y | not] — <b>different people</b>. Intent
      <i>U</i> pushes a customer toward exposure <i>and</i> toward buying, so the exposed would have
      bought more even with no ad. That shared cause is the diagram's fork (U → X and U → Y), and it
      is the €{SIM['naive'] - TRUE:.0f} gap.</p>
      {callout("define", "▣", "Definition — confounding (selection bias)",
               "A variable that causes both the treatment and the outcome, so the raw gap blends the "
               "real effect with the pre-existing difference between the groups. You cannot subtract "
               "it out if you cannot see it — and intent is exactly what you cannot see.")}
      {figure(FIGS['confound'], "The unobserved fork: intent U causes both exposure X and sales Y.")}
      {callout("idea", "◆", "The idea in one line",
               "Any honest method has to manufacture a comparison the targeting engine did not rig.")}
    """),
    ("s3", "The instrument", f"""
      <p class="lead">An instrument imports a slice of randomness the firm did not run itself.</p>
      <p>We need a lever that moves exposure, that intent could not have caused, and that touches
      sales only by moving exposure. In the case it is a randomized <b>serving-priority lottery</b>:
      on a coin flip the platform bumps a user up the auction queue, raising the chance they see the
      ad. The coin is blind to who the user is, and the queue position can only touch sales by
      changing whether the ad was shown. Read the diagram by what is <b>missing</b>: no arrow into Z
      (random), and no arrow from Z to Y except through X.</p>
      {callout("define", "▣", "Definition — instrument",
               "A variable Z that (1) moves the treatment, (2) is assigned as-good-as-randomly, and "
               "(3) affects the outcome only through the treatment. Conditions 1–2 you defend with "
               "data and design; condition 3 you can only argue from how the world works.")}
      {figure(FIGS['instrument'], "A valid instrument, and its three conditions.")}
    """),
    ("s4", "Compliers — who the answer is about", f"""
      <p class="lead">IV answers a sharp question, not a vague one.</p>
      <p>Split the base by how people react to the nudge. <b>Always-takers</b> would see the ad
      regardless; <b>never-takers</b> never see it; <b>compliers</b> see it <i>only because</i> the
      lottery nudged them. We rule out <b>defiers</b> — the monotonicity assumption: the nudge never
      pushes anyone <i>away</i> from exposure.</p>
      <p>When the lottery flips, always- and never-takers do not budge, so they cancel. Only compliers
      move — so the instrument measures the effect <b>on compliers</b>. That is not a limitation to
      apologize for: the compliers are exactly the people a higher bid would newly expose. It is the
      right population for the decision.</p>
      {callout("define", "▣", "Definition — LATE (local average treatment effect)",
               "The average effect among compliers — the people whose treatment the instrument "
               "actually changed. The first-stage share IS the complier share, so a stronger "
               "instrument speaks for a larger slice of the base.")}
      {figure(FIGS['compliers'], "The base splits into three groups; the instrument speaks only for "
              "the compliers.")}
    """),
    ("s5", "The classical estimate — 2SLS = Wald", f"""
      <p class="lead">Three ordinary regressions and one division — no sampler.</p>
      {figure(FIGS['eq'], "First stage, reduced form, and their ratio.")}
      <p>The nudge lifted sales by δ only because it lifted exposure by π; dividing strips out
      everything else. <b>Drag the confounding slider</b>: as the platform chases intent harder,
      naive OLS climbs away from the truth while 2SLS stays put. The distance between the lines is the
      self-selection the instrument removes.</p>
      {callout("define", "▣", "Definition — 2SLS / the Wald ratio",
               "With one binary instrument and no controls, two-stage least squares equals δ/π "
               "(reduced form over first stage). The first-stage F measures how strongly Z moves X; "
               "the rule of thumb wants F ≳ 10.")}
      {interactive("k", "Confounding κ (how hard intent also lifts sales, €)", K_FRAMES, K_LAB, K_DEFAULT)}
    """),
    ("s6", "What can go wrong — weak instruments", f"""
      <p class="lead">A weak instrument is worse than none.</p>
      <p>The whole method divides by the first stage π. If the instrument barely moves exposure, that
      denominator is near zero and the ratio goes wild. <b>Drag the strength slider</b> toward zero
      and watch F fall through 10. Two things happen at once: the interval balloons (expected), and
      the point estimate drifts back <b>up toward OLS</b> (not expected) — a near-zero denominator
      reintroduces exactly the bias the instrument was meant to remove.</p>
      {interactive("g", "Instrument strength γ (how hard the lottery moves exposure)", G_FRAMES, G_LAB, G_DEFAULT)}
      {callout("slip", "▲", "Where teams slip",
               "A weak instrument can be wrong by multiples of the true effect while still wearing "
               "the costume of a causal number. Always report the first-stage F. When it is small, "
               "walk away — or report an <b>Anderson–Rubin</b> confidence set, valid at any strength "
               "(worked in Chapter 13's appendix).")}
    """),
    ("s7", "What Bayes adds", f"""
      <p class="lead">Same answer, now carrying a probability — plus the endogeneity, named.</p>
      <p>Same instrument, same four assumptions, same LATE. The Bayesian model changes only how
      uncertainty is reported, and it estimates one thing 2SLS cannot: the endogeneity ρ, the
      correlation between the intent that drives exposure and the intent that drives sales. A credibly
      <b>positive ρ</b> ({SIM['rho']:+.2f}) is the self-selection made visible.</p>
      <p>At n = 3000 the posterior mean (€{BETA.mean():.1f}) and 2SLS (€{SIM['iv_est']:.1f}) agree to a
      rounding error — <b>Bernstein–von Mises</b>: with enough data the posterior collapses onto the
      classical estimate, which is why its shape is a tidy bell.</p>
      {callout("define", "▣", "Definition — posterior distribution",
               "The full range of effect values consistent with the data and model, each weighted by "
               "plausibility. A confidence interval is a statement about the procedure over many "
               "hypothetical datasets; a posterior is a statement about <i>this</i> effect — so it "
               "can say P(effect &gt; c).")}
      {figure(FIGS['bayes'], "The real NUTS posterior (loaded, not sampled here): the probit lands on "
              "the truth; ρ names the self-selection.")}
    """),
    ("s8", "The decision, in euros", f"""
      <p class="lead">The decision is a probability, not a confidence bar.</p>
      <p>The rule: <b>bid up to c as long as P(β &gt; c) ≥ 0.90</b>. That cap is simply the posterior's
      10th percentile — €{CAP:.1f} here. <b>Drag the cost</b> and read both numbers off the real
      draws: the probability the exposure pays at that price, and the highest cap you can defend with
      90% confidence. Calibrating on the dashboard's €{SIM['naive']:.1f} instead sanctions paying about
      <b>€{SIM['naive'] - BETA.mean():.0f} too much</b> per exposure.</p>
      {interactive("c", "Cost per exposure c (€)", C_FRAMES, C_LAB, C_DEFAULT)}
      {callout("takeaway", "€", "Manager's takeaway",
               f"Bid cap €{CAP:.1f} (90% rule), break-even ≈ €{COIN:.1f} (coin-flip), headroom "
               f"€{SIM['headroom']:.1f} over the €10 cost. The dashboard's €{SIM['naive']:.1f} would "
               "have burned the headroom and then some. This is the one thing the classical arm "
               "structurally cannot hand a manager: a probability attached to the euro.")}
    """),
    ("s9", "On real data — Criteo", f"""
      <p class="lead">The same method on {CRI['n_full_m']:.0f} million rows of real ad-experiment data.</p>
      <p>Criteo's public uplift dataset. The randomized treatment flag is the instrument for who was
      actually exposed — a first stage of only <b>{CRI['first_pct']:.1f}%</b> (compliers are a thin
      slice), but an enormously strong one: <b>F ≈ {CRI['f_stat']:,.0f}</b>. The dashboard gap is
      <b>+{CRI['naive']:.1f} pp</b>. 2SLS lands at <b>+{CRI['wald']:.1f} pp</b>, the Bayesian fit at
      <b>+{CRI['bayes_mean']:.1f} pp</b> — and both sit on the <b>+{CRI['anchor']:.1f} pp</b> design
      anchor computed on all {CRI['n_full_m']:.0f}M rows. The wedge between the dashboard and the
      causal answer is the self-selection, now measured rather than assumed.</p>
      {callout("define", "▣", "Definition — external anchor",
               "A trustworthy estimate from far more data or a cleaner design, used as the referee. "
               "Here the full-sample randomized difference plays truth, so we can grade the "
               "subsample's IV honestly instead of just admiring its confidence interval.")}
      {figure(FIGS['criteo'], "Real Criteo data: the dashboard inflates; both causal arms hit the "
              "13.98M-row anchor.")}
      {callout("takeaway", "€", "Manager's takeaway",
               f"At €{CRI['cost']:.2f} per exposure and €{CRI['conv_value']:.2f} per incremental "
               f"visit, the defensible cap is €{CRI['cap']:.2f}. Bidding the dashboard number across "
               f"{CRI['exposures_quarter']:,.0f} exposures a quarter would overpay about "
               f"<b>€{CRI['premium_quarter']:,.0f} every quarter</b>.")}
    """),
    ("s10", "Failure modes, scope, and recap", f"""
      <p class="lead">Two failures you can catch; one you cannot.</p>
      <ul>
        <li><b>Weak instrument</b> — a small first-stage F. Catchable: look at the F (§6).</li>
        <li><b>Exclusion violation</b> — the red arrow below. If the lottery moved sales through
        <i>any</i> other path, the estimate is biased and <b>no diagnostic will flag it</b>. Defend by
        design: pick an instrument so content-free that a side-channel is implausible, then price how
        big one would have to be to flip the decision.</li>
        <li><b>Scope</b> — IV speaks for <b>compliers</b>, not the whole base. It licenses a bid on
        <i>incremental</i> exposure — exactly what a bid buys — and does not transfer to a different
        instrument or market.</li>
      </ul>
      {figure(FIGS['failure'], "The exclusion restriction is the one assumption no test can check.")}
      {callout("slip", "▲", "Where teams slip",
               "The seductive mistake is to trust a tight confidence interval. A weak or invalid "
               "instrument can be precisely wrong. Precision is not validity — the assumptions are, "
               "and two of them live outside the data.")}
      {callout("takeaway", "€", "Manager's takeaway",
               "One number, gotten right: what an exposure is worth to the people a bid can move. "
               "Instrument → first-stage F → 2SLS → posterior → P(β &gt; c) → a bid cap you can "
               "defend in the room. That is the whole method.")}
    """),
]

CSS = """
:root { --navy:#1f3a5f; --ink:#24303f; --rule:#e5e9f0; }
* { box-sizing: border-box; }
body { margin:0; color:var(--ink); background:#fff; font-size:18px; line-height:1.66;
  font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
  -webkit-font-smoothing:antialiased; }
a { color:#2c6fbb; text-decoration:none; } a:hover { text-decoration:underline; }
.wrap { max-width:1160px; margin:0 auto; display:flex; gap:2.4rem; padding:0 1.4rem; }
.toc { width:238px; flex:none; position:sticky; top:0; align-self:flex-start; height:100vh;
  overflow:auto; padding:2.2rem 0; font-size:.92rem; }
.toc .toc-title { text-transform:uppercase; letter-spacing:.06em; font-size:.72rem; color:#8a95a4;
  font-weight:700; margin-bottom:.6rem; }
.toc ol { list-style:none; margin:0; padding:0; border-left:2px solid var(--rule); }
.toc li a { display:block; padding:.28rem 0 .28rem .9rem; color:#48566a; border-left:2px solid transparent;
  margin-left:-2px; }
.toc li a:hover, .toc li a.active { color:var(--navy); border-left-color:var(--navy); text-decoration:none; }
main { flex:1; min-width:0; max-width:820px; padding:2.2rem 0 6rem; }
.titleblock { border-bottom:1px solid var(--rule); padding-bottom:1.6rem; margin-bottom:1.2rem; }
h1 { color:var(--navy); font-size:2.7rem; font-weight:800; letter-spacing:-.02em; line-height:1.1;
  margin:.2rem 0 .3rem; }
.subtitle { font-size:1.28rem; color:#4a5a70; margin:0 0 1.3rem; font-weight:400; }
.meta { display:grid; grid-template-columns:auto 1fr; gap:.25rem 1.2rem; font-size:.95rem; color:#48566a; }
.meta b { color:var(--navy); font-weight:700; }
h2 { color:var(--navy); font-size:1.85rem; font-weight:800; margin:2.6rem 0 .8rem; scroll-margin-top:1rem; }
h2 .num { color:#b7c2d2; font-weight:800; margin-right:.5rem; }
.lead { font-size:1.2rem; color:var(--navy); font-weight:600; margin:.4rem 0 1rem; }
p, li { font-size:1.06rem; }
figure { margin:1.6rem 0; text-align:center; }
figure img { max-width:100%; height:auto; border-radius:4px; }
figcaption { font-size:.9rem; color:#6b7688; margin-top:.5rem; font-style:italic; }
.callout { border-radius:7px; padding:.9rem 1.15rem; margin:1.5rem 0; border-left:5px solid; }
.callout .ct { font-weight:700; margin-bottom:.35rem; }
.callout .cb { font-size:1.0rem; }
.callout.define { border-color:#2c6fbb; background:#eef4fb; }
.callout.define .ct { color:#1f5fa8; }
.callout.idea { border-color:#8a8a8a; background:#f4f5f7; }
.callout.idea .ct { color:#5b6472; }
.callout.takeaway { border-color:#2e8b57; background:#eef7f1; }
.callout.takeaway .ct { color:#1f6f43; }
.callout.slip { border-color:#d1622b; background:#fdf1ea; }
.callout.slip .ct { color:#b84e1c; }
.interactive { border:1px solid var(--rule); border-radius:8px; padding:1rem 1.15rem; margin:1.5rem 0;
  background:#fbfcfd; }
.slider-row { display:flex; align-items:center; gap:1rem; flex-wrap:wrap; margin-bottom:.6rem; }
.slider-row label { font-weight:600; color:var(--navy); font-size:1rem; }
.slider-row input[type=range] { flex:1; min-width:180px; accent-color:#2c6fbb; height:22px; }
.slider-row output { font-variant-numeric:tabular-nums; color:#b84e1c; font-weight:700; font-size:.98rem;
  min-width:230px; text-align:right; }
.interactive figure { margin:.3rem 0 0; }
@media (max-width:840px) { .toc { display:none; } .wrap { padding:0 1rem; } h1 { font-size:2.1rem; } }
"""

JS = """
window.__WIRE__ = window.__WIRE__ || [];
window.addEventListener('DOMContentLoaded', function () {
  window.__WIRE__.forEach(function (w) {
    var id = w[0], frames = w[1], labels = w[2], def = w[3];
    var s = document.getElementById(id), img = document.getElementById(id + 'i'),
        out = document.getElementById(id + 'o');
    function upd() { var i = +s.value; img.src = frames[i]; out.textContent = labels[i]; }
    s.addEventListener('input', upd); s.value = def; upd();
  });
  // scroll-spy for the TOC
  var links = [].slice.call(document.querySelectorAll('.toc a'));
  var secs = links.map(function (a) { return document.querySelector(a.getAttribute('href')); });
  function spy() {
    var y = window.scrollY + 120, idx = 0;
    secs.forEach(function (sec, i) { if (sec && sec.offsetTop <= y) idx = i; });
    links.forEach(function (a, i) { a.classList.toggle('active', i === idx); });
  }
  window.addEventListener('scroll', spy); spy();
});
"""

toc = "\n".join(f'<li><a href="#{sid}">{i + 1} · {title}</a></li>'
                for i, (sid, title, _) in enumerate(SECTIONS))
body = "\n".join(f'<section><h2 id="{sid}"><span class="num">{i + 1}</span>{title}</h2>{html}</section>'
                 for i, (sid, title, html) in enumerate(SECTIONS))

HTML = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>What is one ad exposure worth? — Instrumental Variables</title>
<style>{CSS}</style>
<script>window.__WIRE__ = [];</script>
</head>
<body>
<div class="wrap">
  <nav class="toc"><div class="toc-title">On this page</div><ol>{toc}</ol></nav>
  <main>
    <header class="titleblock">
      <h1>What is one ad exposure worth?</h1>
      <p class="subtitle">Instrumental variables — pricing incremental exposure you cannot randomize</p>
      <div class="meta">
        <b>Course</b><span><i>Causal Inference &amp; XAI for Business</i> · SDA Bocconi</span>
        <b>Chapter</b><span>13 · Endogenous exposure and instrumental variables</span>
        <b>How to use</b><span>Read top to bottom. The three sliders are live; the posterior is real, precomputed NUTS output.</span>
      </div>
    </header>
    {callout("define", "▣", "The running case",
             "A retailer buys display ads through a demand-side platform and must set a <b>bid cap</b> "
             "— the most it will pay for one ad <b>exposure</b>. The platform's dashboard shows "
             "exposed users converting far more, and wants the cap raised. We follow this one decision "
             "from the wrong number to a bid cap the growth team can defend.")}
    {body}
    <footer style="margin-top:3rem;border-top:1px solid var(--rule);padding-top:1rem;color:#8a95a4;font-size:.85rem">
      Self-contained companion to Chapter 13. Figures and numbers generated from the executed notebook
      (<code>notebooks/11</code>); the sliders swap pre-rendered frames, so nothing computes in the browser.
    </footer>
  </main>
</div>
<script>{JS}</script>
</body>
</html>"""

OUT.write_text(HTML)
print(f"wrote {OUT}  ({OUT.stat().st_size / 1e6:.1f} MB)")
