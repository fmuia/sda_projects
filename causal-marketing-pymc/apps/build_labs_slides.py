"""Generate the self-contained business-applications closer deck: apps/labs_slides.html.

The third deck (after geo_lift_slides.html and iv_slides.html): five real PyMC Labs
engagements linked back to the two lecture chapters. Same build discipline as the other
two decks, with one deliberate substitution: this deck's numbers come from PUBLIC BLOG
POSTS, not notebook shards, so its source of truth is apps/labs_deck_data.json, where
every entry pins a number/quote to its source_url and retrieval date.

  1. TOKENS  — every scalar/quote in the prose comes from labs_deck_data.json; the
               template writes {{labs.key}}; an unknown token is a BUILD ERROR,
               exactly like a missing book macro. (No nb* shards: book/build/ need
               not exist to build this deck.)
  2. DATA    — a small bundle injected at /*__DATA__*/: the ROAS truth values (from
               the data file, for the S6 chart) and a deterministic schematic series
               for the S4 counterfactual sketch (formula-generated here, labelled
               "schematic" on the slide; it is a drawing, not client data).
  3. MATHJAX — the vendored tex-svg build (apps/vendor/), inlined at /*__MATHJAX__*/.
  4. SOURCES — the backup Sources slide's table rows are generated from the data
               file at <!--SOURCES_ROWS-->, so provenance can never go stale.

Build:  .venv/bin/python apps/build_labs_slides.py     (or `make html-labs`)
Template: apps/labs_slides_src.html  (the editable source; the .html output is generated).
Verify: .venv/bin/python apps/verify_labs_deck.py  (claims registry: apps/labs_claims.yaml)
"""
from __future__ import annotations

import json
import math
import re
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
VENDOR = HERE / "vendor"
SRC = HERE / "labs_slides_src.html"
OUT = HERE / "labs_slides.html"
DATAFILE = HERE / "labs_deck_data.json"

MATHJAX_URL = "https://cdn.jsdelivr.net/npm/mathjax@3.2.2/es5/tex-svg.js"


def load_pins() -> dict[str, dict]:
    d = json.loads(DATAFILE.read_text())
    return {k: v for k, v in d.items() if not k.startswith("_")}


def counter_series() -> dict:
    """Deterministic schematic for the S4 counterfactual sketch (a drawing, not data).

    24 monthly points, launch at t=16: a smooth trending base with mild seasonality
    (the counterfactual), plus a saturating lift after the launch (the actual). No RNG,
    so the deck is byte-stable across builds.
    """
    n, launch = 24, 16
    cf, actual = [], []
    for i in range(n):
        base = 100.0 + 0.7 * i + 6.0 * math.sin(i / 2.2)
        lift = 14.0 * (1 - math.exp(-(i - launch) / 2.5)) if i >= launch else 0.0
        cf.append(round(base, 1))
        actual.append(round(base + lift, 1))
    return {"cf": cf, "actual": actual, "launch": launch}


def bake_bundle(pins: dict[str, dict]) -> dict:
    return {
        "roas": {"x1": pins["labs.roas_x1"]["value"], "x2": pins["labs.roas_x2"]["value"]},
        "counter": counter_series(),
    }


def sources_rows(pins: dict[str, dict]) -> str:
    """One table row per unique source URL on the backup Sources slide."""
    by_url: dict[str, list[str]] = {}
    for key, rec in pins.items():
        by_url.setdefault(rec["source_url"], []).append(key.removeprefix("labs."))
    rows = []
    for url in sorted(by_url, key=lambda u: (u.split("/")[2], u)):
        slug = url.rstrip("/").split("/")[-1]
        host = url.split("/")[2].removeprefix("www.")
        facts = ", ".join(sorted(by_url[url]))
        rows.append(
            f"        <tr><td>{host} · {slug}</td>"
            f'<td style="text-align:left">{facts}</td></tr>'
        )
    return "\n".join(rows)


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
    pins = load_pins()
    tokens = {k: str(v["text"]) for k, v in pins.items()}

    # 1 · scalar/quote tokens --------------------------------------------------------
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
        sys.exit("FAIL: unknown tokens (not in labs_deck_data.json): "
                 + ", ".join(sorted(set(missing))))

    # 2 · the data bundle ------------------------------------------------------------
    bundle = bake_bundle(pins)
    marker = re.compile(r"/\*__DATA__\*/\{.*?\};", re.S)
    if not marker.search(html):
        sys.exit("FAIL: template has no /*__DATA__*/{...}; marker.")
    html = marker.sub("/*__DATA__*/" + json.dumps(bundle, separators=(",", ":")) + ";",
                      html, count=1)

    # 3 · the Sources slide ----------------------------------------------------------
    if "<!--SOURCES_ROWS-->" not in html:
        sys.exit("FAIL: template has no <!--SOURCES_ROWS--> marker.")
    html = html.replace("<!--SOURCES_ROWS-->", sources_rows(pins), 1)

    # 4 · MathJax --------------------------------------------------------------------
    if "/*__MATHJAX__*/" not in html:
        sys.exit("FAIL: template has no /*__MATHJAX__*/ marker.")
    html = html.replace("/*__MATHJAX__*/", mathjax_js(), 1)

    OUT.write_text(html)
    unused = sorted(set(tokens) - used)
    size = OUT.stat().st_size / 1e6
    print(f"wrote {OUT.relative_to(REPO)}  ({size:.1f} MB, {len(used)} pinned tokens, "
          f"MathJax inlined)")
    if unused:
        print(f"note: {len(unused)} pinned but unused keys (fine; kept for claims/provenance): "
              + ", ".join(unused))


if __name__ == "__main__":
    main()
