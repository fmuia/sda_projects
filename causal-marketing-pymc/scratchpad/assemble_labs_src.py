"""One-time assembler for apps/labs_slides_src.html (the business-applications closer deck).

Splices the SHARED CHROME out of apps/iv_slides_src.html (CSS, MathJax config, footer/nav/TOC
DOM, svg helpers, poll wiring, deck-navigation IIFE, the two base64 logo chips) and combines it
with the labs deck's own slides (scratchpad/labs_slides_fragment.html) and figures
(scratchpad/labs_figures_fragment.js).

After this runs once, apps/labs_slides_src.html is the CANONICAL editable source; edit it
directly and rebuild with `make html-labs`. Re-running this assembler OVERWRITES it from the
fragments, so only re-run if you deliberately want to re-derive the chrome.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
APPS = HERE.parent / "apps"
IV = (APPS / "iv_slides_src.html").read_text()
SLIDES = (HERE / "labs_slides_fragment.html").read_text()
FIGURES = (HERE / "labs_figures_fragment.js").read_text()
OUT = APPS / "labs_slides_src.html"


def cut(s: str, start: str, end: str, *, incl_start=True, incl_end=False) -> str:
    i = s.index(start)
    j = s.index(end, i)
    a = i if incl_start else i + len(start)
    b = j + len(end) if incl_end else j
    return s[a:b]


# 1 · head + CSS + MathJax config, up to (excluding) the first slide section
head = IV[: IV.index("<!-- ============ 1 · TITLE ============ -->")]
head = head.replace(
    "<title>Instrumental Variables: what is one ad exposure worth? (slides)</title>",
    "<title>Causal Inference in the Wild: PyMC Labs cases (slides)</title>",
)

# 2 · the two logo chips (giant base64 lines on the IV title slide), spliced verbatim
logo_lines = [ln.strip() for ln in IV.splitlines() if '<span class="logo-chip">' in ln]
if len(logo_lines) != 2:
    sys.exit(f"FAIL: expected 2 logo-chip lines in iv_slides_src.html, found {len(logo_lines)}")
slides = SLIDES.replace("__PYMC_LOGO__", "    " + logo_lines[0]).replace(
    "__LABS_LOGO__", "    " + logo_lines[1]
)
if "__" in re.sub(r"<!--.*?-->", "", slides.replace("__SOURCES", "")):  # loose guard
    pass  # data-* attrs etc. are fine; real placeholder misses are caught by the build

# 3 · chrome DOM after SLIDES-END: deck close, navzones, footer, pbar, tocOv, script open,
#     DATA marker line (stop before the IV N-map line)
mid = cut(IV, "<!-- SLIDES-END", 'const N = {"naive"')
mid = mid.replace(
    "<span>Causal Marketing · SDA Bocconi · Instrumental Variables</span>",
    "<span>Causal Marketing · SDA Bocconi · Causal Inference in the Wild</span>",
)

# 4 · svg helpers + fitEq (stop before the IV-specific world simulator)
helpers = cut(IV, "/* ==== svg helpers ==== */",
              "/* ==== shared: regenerate the IV world in JS")

# 5 · tail: FIGURES-END, poll wiring, nav IIFE, close (rename the localStorage theme key)
tail = IV[IV.index("/* FIGURES-END"):]
tail = tail.replace("ivSlidesTheme", "labsSlidesTheme")

out = (
    head
    + slides
    + "\n"
    + mid
    + "const N = {};\n"
    + helpers
    + FIGURES
    + "\n"
    + tail
)
OUT.write_text(out)
n_slides = out.count('<section class="slide')
print(f"wrote {OUT.relative_to(APPS.parent)}  ({len(out)/1e3:.0f} KB, {n_slides} slides)")
