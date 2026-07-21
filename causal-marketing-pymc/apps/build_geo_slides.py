"""Generate the self-contained Chapter 9 (synthetic control) slide deck: apps/geo_lift_slides.html.

One offline file, the Ch. 9 counterpart to apps/iv_lecture.html — no server, no CDN, no runtime
computation of any published number. Three inputs, none hand-typed:

  1. TOKENS  — every scalar in the prose comes from the executed shards
               (book/build/results/nb07.json, nb07b.json). The template writes {{nb07.p_go}};
               an unknown or stale token is a BUILD ERROR, exactly like a missing book macro.
  2. DATA    — the series/draws bundle written by nb07's "lecture bundle" cell
               (apps/geo_lecture_data.json): panel series, weights, placebo paths, posterior
               draws, ACF. Injected verbatim at the /*__DATA__*/ marker for the live SVG charts.
  3. FIGS    — the book's own vector figures (book/build/figures/*.pdf), rasterised at build
               time and inlined as data URIs at <!--FIG:name--> markers. The heavy statistical
               results (coverage study, ACF, variance growth, real-data exam) are shown as the
               book shows them, not re-drawn by hand.

Math is real LaTeX: \\( .. \\) / \\[ .. \\] rendered by MathJax (tex-svg, vendored into
apps/vendor/ on first build, then inlined — the output needs no network and no fonts).

Build:  .venv/bin/python apps/build_geo_slides.py     (or `make html-geo`)
Template: apps/geo_slides_src.html  (the editable source; the .html output is generated).
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
import urllib.request
from base64 import b64encode
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
RESULTS = REPO / "book" / "build" / "results"
FIGDIR = REPO / "book" / "build" / "figures"
VENDOR = HERE / "vendor"
SRC = HERE / "geo_slides_src.html"
OUT = HERE / "geo_lift_slides.html"
BUNDLE = HERE / "geo_lecture_data.json"

MATHJAX_URL = "https://cdn.jsdelivr.net/npm/mathjax@3.2.2/es5/tex-svg.js"
FIG_DPI = 150


def load_tokens() -> dict[str, str]:
    """{{nb07.key}} -> the shard's formatted text (the same string the book macro carries)."""
    tokens: dict[str, str] = {}
    for shard in ("nb07.json", "nb07b.json"):
        d = json.loads((RESULTS / shard).read_text())
        meta = d.get("_meta", {})
        if meta.get("fast", False):
            sys.exit(f"FAIL: {shard} is a FAST-mode shard; re-execute the notebook with CMP_FAST=0.")
        for key, rec in d.items():
            if isinstance(rec, dict) and "text" in rec:
                tokens[key] = str(rec["text"])
    return tokens


def mathjax_js() -> str:
    VENDOR.mkdir(exist_ok=True)
    cached = VENDOR / "mathjax-tex-svg-3.2.2.js"
    if not cached.exists():
        print(f"vendoring MathJax -> {cached.relative_to(REPO)}")
        with urllib.request.urlopen(MATHJAX_URL, timeout=60) as r:
            cached.write_bytes(r.read())
    return cached.read_text()


def fig_data_uri(name: str) -> str:
    pdf = FIGDIR / f"{name}.pdf"
    if not pdf.exists():
        sys.exit(f"FAIL: template asks for figure '{name}' but {pdf} does not exist.")
    with tempfile.TemporaryDirectory() as td:
        stem = Path(td) / name
        subprocess.run(
            ["pdftoppm", "-png", "-r", str(FIG_DPI), "-singlefile", str(pdf), str(stem)],
            check=True,
        )
        png = stem.with_suffix(".png").read_bytes()
    return "data:image/png;base64," + b64encode(png).decode()


def naive_grid() -> dict:
    """Precompute the "four estimators, one truth" figure over the deck's two dials.

    The slide-14 figure lets the audience sweep the loading spread s and the macro-shock sd
    sigma_eta. Rather than re-simulate a *toy* world in the browser (a different seed and solver
    from the case, which made the figure jump discontinuously the instant a dial left the case
    dials), we grade the REAL DGP here: for every (s, sigma_eta) cell we draw the seed-5 panel
    from cmp.dgp.geo_panel — the identical generator behind the whole chapter — and score the four
    estimators the notebook scores (before/after, treated-avg control, DiD, and the classical
    SLSQP synthetic control, cmp.estimators), against the planted truth. At the case dials
    (s=0.4, sigma_eta=1.2) the cell reproduces nb07's published numbers exactly (SC is the
    classical refit, ~0.1 off the shipped AR(1) bar), and neighbouring cells are now continuous
    with it. Deterministic, no notebook re-execution, nothing hand-typed.
    """
    import numpy as np
    from cmp import dgp, estimators as est

    S = [round(0.1 * i, 1) for i in range(9)]     # loading spread 0.0 .. 0.8  (slider value/10)
    SD = [round(0.3 * i, 1) for i in range(11)]   # macro-shock sd 0.0 .. 3.0  (slider value/10)
    cells = []
    for s in S:
        row = []
        for sd in SD:
            df, eff, launch, lab = dgp.geo_panel(seed=5, load_spread=s, macro_sd=sd)
            sales = df.values.T
            ti = list(df.columns).index(lab)
            y = sales[ti]
            donors = np.delete(sales, ti, axis=0)
            W = sales.shape[1]
            pre, post = slice(0, launch), slice(launch, W)
            dpost, dpre = donors[:, post].mean(0), donors[:, pre].mean(0)
            ba = float(y[post].mean() - y[pre].mean())
            tc = float((y[post] - dpost).mean())
            did = float(tc - (y[pre] - dpre).mean())
            gap, _ = est.sc_effect_slsqp(y, donors, pre, post)
            sc = float(gap[post].mean())
            truth = float(eff[post].mean())
            row.append([round(v, 2) for v in (ba, tc, did, sc, truth)])
        cells.append(row)
    return {"s": S, "sd": SD, "cells": cells,
            "labels": ["before / after", "treated − avg control",
                       "diff-in-differences", "synthetic control"]}


def main(src: Path = SRC, out: Path = OUT) -> None:
    html = src.read_text()
    tokens = load_tokens()

    # 1 · scalar tokens ------------------------------------------------------------------
    used, missing = set(), []
    def sub_token(m: re.Match) -> str:
        key = m.group(1).strip()
        if key not in tokens:
            missing.append(key)
            return m.group(0)
        used.add(key)
        return tokens[key]
    html = re.sub(r"\{\{([a-z0-9_.]+)\}\}", sub_token, html)
    if missing:
        sys.exit("FAIL: unknown tokens (not in the shards): " + ", ".join(sorted(set(missing))))

    # 2 · the data bundle ----------------------------------------------------------------
    if not BUNDLE.exists():
        sys.exit(f"FAIL: {BUNDLE} missing — re-execute nb07 (its lecture-bundle cell writes it).")
    bundle_meta = json.loads(BUNDLE.read_text())
    if bundle_meta.get("_fast", False):
        sys.exit("FAIL: the lecture bundle was written by a FAST run; re-execute nb07 FULL.")
    # merge every numeric shard scalar so the live charts read DATA.scalars.*, never literals
    for shard, dest in (("nb07.json", "scalars"), ("nb07b.json", "scalars_b")):
        d = json.loads((RESULTS / shard).read_text())
        prefix = shard.split(".")[0] + "."
        bundle_meta[dest] = {
            k[len(prefix):]: rec["value"]
            for k, rec in d.items()
            if isinstance(rec, dict) and isinstance(rec.get("value"), (int, float))
        }
    # aliases the deck's chart code reads, derived (not retyped) from the bundle/shards:
    # the top-12 classical weights in the same descending order the bundle's donor_*_top use
    # (argsort of -w_cl, exactly the notebook's selection rule), the measured ACF under its
    # historical name, and the classical total for the chart annotations.
    order = sorted(range(len(bundle_meta["w_cl_all"])),
                   key=lambda i: -bundle_meta["w_cl_all"][i])[:len(bundle_meta["donor_labels_top"])]
    bundle_meta["w_cl_top"] = [bundle_meta["w_cl_all"][i] for i in order]
    bundle_meta["w_ar1_top"] = [bundle_meta["w_ar1_all"][i] for i in order]
    bundle_meta["rho_meas"] = bundle_meta["acf"]["measured"]
    bundle_meta["real_tot"] = bundle_meta["scalars"]["cl_total"]

    # the real-data bundle (nb07b's lecture cell): the Act VI chart series
    bundle_b_path = HERE / "geo_lecture_data_b.json"
    if bundle_b_path.exists():
        bundle_b = json.loads(bundle_b_path.read_text())
        if bundle_b.pop("_fast", False):
            sys.exit("FAIL: geo_lecture_data_b.json was written by a FAST run; re-execute nb07b FULL.")
        bundle_meta.update(bundle_b)

    # INTERIM: keys the deck's live charts need but the nb07 lecture-bundle cell does not yet
    # emit, frozen at the deck's last consistent state (see the file's _note). Merged LAST, so
    # anything listed here silently wins over the bundle — hence the loud print. Phase 2 of the
    # slide remediation moves these into nb07/nb07b and deletes the file.
    extras_path = HERE / "geo_lecture_extras.json"
    if extras_path.exists():
        extras = {k: v for k, v in json.loads(extras_path.read_text()).items()
                  if not k.startswith("_")}
        overridden = sorted(k for k in extras if k in bundle_meta)
        added = sorted(k for k in extras if k not in bundle_meta)
        bundle_meta.update(extras)
        print(f"extras: +{len(added)} keys, OVERRIDING {len(overridden)}: {', '.join(overridden)}")

    # the slide-14 "four estimators, one truth" grid: the real DGP swept across the two dials,
    # so the live figure reads a precomputed cell instead of re-simulating a toy world.
    bundle_meta["naive_grid"] = naive_grid()
    print(f"naive grid: {len(bundle_meta['naive_grid']['s'])}×"
          f"{len(bundle_meta['naive_grid']['sd'])} cells from cmp.dgp.geo_panel")

    if "/*__DATA__*/" not in html:
        sys.exit("FAIL: template has no /*__DATA__*/ marker.")
    j = html.index("{", html.index("/*__DATA__*/"))
    _, end = json.JSONDecoder().raw_decode(html, j)
    html = html[:j] + json.dumps(bundle_meta, separators=(",", ":")) + html[end:]

    # 2b · the N map: formatted number strings the deck's JS writes into prose spans.
    # The template's /*__NUMS__*/{...}/*__ENDNUMS__*/ map supplies the KEYS; every value is
    # re-derived from the shards (nb07.<key>), so a number can no more go stale here than in
    # the {{token}} prose layer. A key missing from the shards is a build error.
    nm = re.search(r"/\*__NUMS__\*/(\{.*?\})/\*__ENDNUMS__\*/", html, re.S)
    if nm:
        n_keys = list(json.loads(nm.group(1)))
        missing_n = [k for k in n_keys if f"nb07.{k}" not in tokens and f"nb07b.{k}" not in tokens]
        if missing_n:
            sys.exit("FAIL: N-map keys not in the shards: " + ", ".join(missing_n))
        nmap = {k: tokens.get(f"nb07.{k}", tokens.get(f"nb07b.{k}")) for k in n_keys}
        html = html[:nm.start(1)] + json.dumps(nmap, separators=(",", ":")) + html[nm.end(1):]
        print(f"N map: {len(nmap)} formatted numbers injected from shards")

    # 3 · book figures -------------------------------------------------------------------
    fig_names = sorted(set(re.findall(r"<!--FIG:([a-z0-9_]+)-->", html)))
    for name in fig_names:
        print(f"embedding figure {name}")
        html = html.replace(f"<!--FIG:{name}-->", fig_data_uri(name))

    # 4 · MathJax ------------------------------------------------------------------------
    if "/*__MATHJAX__*/" not in html:
        sys.exit("FAIL: template has no /*__MATHJAX__*/ marker.")
    html = html.replace("/*__MATHJAX__*/", mathjax_js(), 1)

    out.write_text(html)
    size = out.stat().st_size / 1e6
    print(f"wrote {out.relative_to(REPO)}  ({size:.1f} MB, {len(used)} shard tokens, "
          f"{len(fig_names)} book figures, MathJax inlined)")


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(description="Build a geo-lift slide deck from a source template.")
    ap.add_argument("--src", type=Path, default=SRC, help="source template (default: geo_slides_src.html)")
    ap.add_argument("--out", type=Path, default=OUT, help="output deck (default: geo_lift_slides.html)")
    args = ap.parse_args()
    main(args.src.resolve(), args.out.resolve())
