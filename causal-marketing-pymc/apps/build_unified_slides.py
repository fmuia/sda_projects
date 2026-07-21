"""Generate the UNIFIED SDA session deck: apps/unified_slides.html.

Part 1 ("Causal Inference in the Wild": real PyMC Labs engagements, the business hook)
spliced in FRONT of the short classical geo deck (synthetic control, Acts I-IV), closing
with the labs synthesis slides. One file, one chrome (the geo deck's, a strict superset),
one DATA bundle. The narrative this deck implements: apps/geo_lift_lecture_emphasis.md;
the spoken script: apps/geo_lift_lecture_speech.md.

Inputs, none hand-typed:
  tokens : {{nb07*.*}} from the executed notebook shards (build_geo_slides.load_tokens)
           PLUS {{labs.*}} from apps/labs_deck_data.json (blog-pinned facts with source
           URLs; build_labs_slides.load_pins). The two prefixes are disjoint (asserted).
  DATA   : the geo bundle (build_geo_slides.build_bundle) merged with the labs chart keys
           (the deterministic counterfactual schematic + the pinned ROAS pair). The key
           sets are disjoint (asserted), so the labs figure code reads the same DATA
           global as the geo figures.
  SOURCES: the labs Sources backup table rows at <!--SOURCES_ROWS-->.
  MATHJAX: the vendored tex-svg build, inlined once at /*__MATHJAX__*/.

Build:  .venv/bin/python apps/build_unified_slides.py     (or `make html-unified`)
Template: apps/unified_slides_src.html (canonical; edit it, then rebuild).
Verify: .venv/bin/python apps/verify_unified_deck.py  (geo claims subset + labs claims)
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import build_geo_slides as bg
import build_labs_slides as bl

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
SRC = HERE / "unified_slides_src.html"
OUT = HERE / "unified_slides.html"


def main() -> None:
    if not SRC.exists():
        sys.exit(f"FAIL: {SRC} missing.")
    html = SRC.read_text()

    # 1 · scalar/quote tokens from BOTH sources ------------------------------------------
    pins = bl.load_pins()
    tokens = bg.load_tokens()
    labs_tokens = {k: str(v["text"]) for k, v in pins.items()}
    dup = set(tokens) & set(labs_tokens)
    if dup:
        sys.exit("FAIL: token collision between shards and labs pins: " + ", ".join(sorted(dup)))
    tokens |= labs_tokens

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
        sys.exit("FAIL: unknown tokens (neither shards nor labs pins): "
                 + ", ".join(sorted(set(missing))))

    # 2 · ONE data bundle (geo + labs chart keys), 2b · the N map ------------------------
    bundle = bg.build_bundle()
    labs_bundle = bl.bake_bundle(pins)
    overlap = set(bundle) & set(labs_bundle)
    if overlap:
        sys.exit("FAIL: DATA key overlap between geo and labs bundles: " + ", ".join(sorted(overlap)))
    bundle.update(labs_bundle)
    html = bg.inject_data(html, bundle)
    html = bg.inject_nums(html, tokens)

    # 3 · the labs Sources backup slide --------------------------------------------------
    if "<!--SOURCES_ROWS-->" not in html:
        sys.exit("FAIL: template has no <!--SOURCES_ROWS--> marker.")
    html = html.replace("<!--SOURCES_ROWS-->", bl.sources_rows(pins), 1)

    # 4 · MathJax ------------------------------------------------------------------------
    if "/*__MATHJAX__*/" not in html:
        sys.exit("FAIL: template has no /*__MATHJAX__*/ marker.")
    html = html.replace("/*__MATHJAX__*/", bg.mathjax_js(), 1)

    OUT.write_text(html)
    size = OUT.stat().st_size / 1e6
    n_slides = html.count('<section class="slide')
    print(f"wrote {OUT.relative_to(REPO)}  ({size:.1f} MB, {n_slides} slides, "
          f"{len(used)} tokens, MathJax inlined)")


if __name__ == "__main__":
    main()
