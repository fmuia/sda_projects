"""Generate apps/iv_slides_sh.html, the management-first rework of the Ch. 13 IV deck.

Same pipeline as build_iv_slides.py (tokens from the executed shards, DATA bundle at
/*__DATA__*/, vendored MathJax at /*__MATHJAX__*/), different template and output:

  Template: apps/iv_slides_sh_src.html   (editable source)
  Output:   apps/iv_slides_sh.html       (generated, self-contained)

Build:  .venv/bin/python apps/build_iv_slides_sh.py
"""
from __future__ import annotations

import build_iv_slides as base

base.SRC = base.HERE / "iv_slides_sh_src.html"
base.OUT = base.HERE / "iv_slides_sh.html"

if __name__ == "__main__":
    base.main()
