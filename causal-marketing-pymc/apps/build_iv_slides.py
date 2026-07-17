"""Generate the self-contained Chapter 13 (instrumental variables) slide deck: apps/iv_slides.html.

One offline file, the Ch. 13 counterpart to apps/geo_lift_slides.html. Clone of the geo build:
three inputs, none hand-typed.

  1. TOKENS  — every scalar in the prose comes from the executed shards
               (book/build/results/nb11.json, nb11b.json). The template writes {{nb11.iv_est}};
               an unknown or stale token is a BUILD ERROR, exactly like a missing book macro.
  2. DATA    — the bundle written to book/build/lecture_iv_data.json by bake_bundle() below:
               the real NUTS posterior draws (subsampled), every numeric shard scalar, and the
               DGP parameters the live JS simulator regenerates from. Injected at /*__DATA__*/.
  3. MATHJAX — the vendored tex-svg build (apps/vendor/), inlined at /*__MATHJAX__*/.

Build:  .venv/bin/python apps/build_iv_slides.py     (or `make html-iv-slides`)
Template: apps/iv_slides_src.html  (the editable source; the .html output is generated).
"""
from __future__ import annotations

import json
import re
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
RESULTS = REPO / "book" / "build" / "results"
VENDOR = HERE / "vendor"
SRC = HERE / "iv_slides_src.html"
OUT = HERE / "iv_slides.html"
DRAWS = HERE / "iv_lecture_data.json"          # real NUTS draws, already bundled earlier
BUNDLE = REPO / "book" / "build" / "lecture_iv_data.json"

MATHJAX_URL = "https://cdn.jsdelivr.net/npm/mathjax@3.2.2/es5/tex-svg.js"
# The IV data-generating world (mirrors cmp.dgp.iv_ad_exposure / the notebook), so the live JS
# simulator regenerates the exact world the graded numbers came from.
# seed chosen (scan over mulberry32 seeds) so the live JS draw at the default (kappa=12, gamma=1.1)
# reproduces the notebook's headline numbers: naive 23.7, 2SLS 16.5, F 156, first stage 56->77.
DGP = {"a0": 0.3, "gamma": 1.1, "kappa": 12.0, "lam": 0.8, "mu": 50.0, "beta": 15.0,
       "sigma": 6.0, "n": 3000, "seed": 264275, "T0": None}


def load_tokens() -> dict[str, str]:
    """{{nb11.key}} / {{nb11b.key}} -> the shard's formatted text (the book macro's string)."""
    tokens: dict[str, str] = {}
    for shard in ("nb11.json", "nb11b.json"):
        d = json.loads((RESULTS / shard).read_text())
        if d.get("_meta", {}).get("fast", False):
            sys.exit(f"FAIL: {shard} is a FAST-mode shard; re-execute the notebook with CMP_FAST=0.")
        for key, rec in d.items():
            if isinstance(rec, dict) and "text" in rec:
                tokens[key] = str(rec["text"])
    return tokens


def scalars(shard: str) -> dict[str, float]:
    d = json.loads((RESULTS / shard).read_text())
    prefix = shard.split(".")[0] + "."
    return {k[len(prefix):]: rec["value"] for k, rec in d.items()
            if isinstance(rec, dict) and isinstance(rec.get("value"), (int, float))}


def bake_bundle() -> dict:
    """Real NUTS draws (subsampled to ~1200, rounded) + every shard scalar + the DGP params."""
    d = json.loads(DRAWS.read_text())

    def sub(arr, n=1200, dp=2):
        a = list(arr)
        step = max(1, len(a) // n)
        return [round(float(v), dp) for v in a[::step][:n]]

    bundle = {
        "beta_probit": sub(d["beta_probit"]),
        "beta_gauss": sub(d["beta_gauss"]),
        "rho_probit": sub(d["rho_probit"]),
        "true": float(d["true"]),
        "dgp": DGP,
        "scalars": scalars("nb11.json"),
        "scalars_b": scalars("nb11b.json"),
    }
    BUNDLE.write_text(json.dumps(bundle, separators=(",", ":")))
    return bundle


def mathjax_js() -> str:
    VENDOR.mkdir(exist_ok=True)
    cached = VENDOR / "mathjax-tex-svg-3.2.2.js"
    if not cached.exists():
        print(f"vendoring MathJax -> {cached.relative_to(REPO)}")
        with urllib.request.urlopen(MATHJAX_URL, timeout=60) as r:
            cached.write_bytes(r.read())
    return cached.read_text()


def main() -> None:
    if not SRC.exists():
        sys.exit(f"FAIL: {SRC} missing.")
    html = SRC.read_text()
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
    bundle = bake_bundle()
    marker = re.compile(r"/\*__DATA__\*/\{.*?\};", re.S)
    if not marker.search(html):
        sys.exit("FAIL: template has no /*__DATA__*/{...}; marker.")
    html = marker.sub("/*__DATA__*/" + json.dumps(bundle, separators=(",", ":")) + ";", html, count=1)

    # 3 · MathJax ------------------------------------------------------------------------
    if "/*__MATHJAX__*/" not in html:
        sys.exit("FAIL: template has no /*__MATHJAX__*/ marker.")
    html = html.replace("/*__MATHJAX__*/", mathjax_js(), 1)

    OUT.write_text(html)
    size = OUT.stat().st_size / 1e6
    print(f"wrote {OUT.relative_to(REPO)}  ({size:.1f} MB, {len(used)} shard tokens, "
          f"{len(bundle['beta_probit'])} draws, MathJax inlined)")


if __name__ == "__main__":
    main()
