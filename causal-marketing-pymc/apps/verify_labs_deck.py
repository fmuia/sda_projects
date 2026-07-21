"""Verify every claim in the business-applications closer deck against its pinned source.

Adapted from apps/verify_geo_deck.py for a deck whose numbers come from PUBLIC BLOG POSTS
(pinned in apps/labs_deck_data.json with source URLs) instead of notebook shards. The
claims registry apps/labs_claims.yaml maps each displayed fact to the slide that states
it (anchored by data-t, never by position), to the data-file key that pins it, and,
for chart-baked numbers, to an expression over the injected DATA bundle.

Checks per claim (all optional except id + slides + source):
  text/texts : string(s) that must appear on every listed slide (tag-stripped, ws-normalised)
  expr       : numpy expression over DATA keys
  value/tol  : |expr - value| tolerance
  source     : labs_deck_data.json key that must exist and carry a source_url

Global checks (this deck automates two sweeps the other decks run by hand):
  - no unresolved {{token}} residue in the built deck
  - ZERO em-dashes outside the inlined MathJax blob (deck grammar rule)
  - no raw euro/dollar signs inside \\( \\) / \\[ \\] math
  - per-slide visible-length budget (CHAR_BUDGET, fold-out bodies excluded), hard
  - every data-file entry carries source_url + quote; retrieval date present in _meta

Run: .venv/bin/python apps/verify_labs_deck.py   (exit 1 on any FAIL)
"""
from __future__ import annotations

import html as htmllib
import json
import re
import sys
from pathlib import Path

import numpy as np
import yaml

HERE = Path(__file__).resolve().parent
DECK = HERE / "labs_slides.html"
CLAIMS = HERE / "labs_claims.yaml"
DATAFILE = HERE / "labs_deck_data.json"

CHAR_BUDGET = 2600          # visible chars per slide (fold-out bodies excluded)
CHAR_BUDGET_HARD = True


def load_deck(deck: Path = DECK):
    html = deck.read_text()
    i = html.index("/*__DATA__*/")
    j = html.index("{", i)
    data, _ = json.JSONDecoder().raw_decode(html, j)
    body = html[: html.index("/* ==== baked data (injected) ==== */")]
    slides, slides_visible = {}, {}

    def strip_tags(chunk):
        txt = re.sub(r"<[^>]+>", " ", chunk)
        txt = htmllib.unescape(txt)
        return re.sub(r"[\s  ]+", " ", txt).strip()

    for chunk in re.split(r'(?=<section class="slide)', body)[1:]:
        t = re.search(r'data-t="([^"]*)"', chunk)
        key = htmllib.unescape(t.group(1)) if t else f"slide{len(slides)+1}"
        slides[key] = strip_tags(chunk)
        vis = re.sub(r"<details.*?<summary>(.*?)</summary>.*?</details>", r" \1 ", chunk, flags=re.S)
        slides_visible[key] = strip_tags(vis)
    return html, data, slides, slides_visible


def sans_mathjax(html: str) -> str:
    """The full deck text with the inlined MathJax blob excised (it is one script tag)."""
    m = re.search(r'<script id="mathjax-inline">.*?</script>', html, re.S)
    return html if not m else html[: m.start()] + html[m.end():]


def make_env(data):
    env = {
        "np": np, "sum": np.sum, "mean": np.mean, "abs": np.abs,
        "min": np.min, "max": np.max, "float": float, "len": len,
    }
    for k, v in data.items():
        env[k] = v
    return env


def norm(s):
    return re.sub(r"[\s  ]+", " ", s)


def main(deck: Path = DECK) -> int:
    html, data, slides, slides_visible = load_deck(deck)
    pins = json.loads(DATAFILE.read_text())
    env = make_env(data)
    claims = yaml.safe_load(CLAIMS.read_text())

    failures, warnings, npass = [], [], 0

    def report(claim_id, ok, msg):
        nonlocal npass
        if ok:
            npass += 1
        else:
            failures.append((claim_id, msg))

    for c in claims:
        cid = c["id"]
        # -- provenance key must exist and carry a URL --------------------------------
        src = c.get("source")
        rec = pins.get(src) if src else None
        report(cid, rec is not None and bool(rec.get("source_url")),
               f"source key {src!r} missing from labs_deck_data.json or lacks source_url")
        # -- text presence on every listed slide --------------------------------------
        texts = c.get("texts") or ([c["text"]] if c.get("text") else [])
        for t in texts:
            for st in c.get("slides", []):
                if st not in slides:
                    report(cid, False, f"slide anchor {st!r} not found in deck")
                elif norm(t) not in slides[st]:
                    report(cid, False, f"text {t!r} missing on slide {st!r}")
                else:
                    report(cid, True, "")
        # -- recomputation from DATA ---------------------------------------------------
        if "expr" in c:
            try:
                v = float(eval(c["expr"], {"__builtins__": {}}, env))  # noqa: S307 - trusted repo file
            except Exception as e:  # noqa: BLE001
                report(cid, False, f"expr error: {e}")
                v = None
            if v is not None and "value" in c:
                tol = c.get("tol", 0.5)
                report(cid, abs(v - c["value"]) <= tol,
                       f"expr={v:.4g} vs displayed {c['value']} (tol {tol})")

    # -- data-file hygiene: every pin has url + quote; retrieval date stamped ----------
    for k, rec in pins.items():
        if k.startswith("_"):
            continue
        report(f"pin:{k}", bool(rec.get("source_url")) and bool(rec.get("quote")),
               "pin lacks source_url or quote")
    report("pin:_meta", bool(pins.get("_meta", {}).get("retrieved")),
           "labs_deck_data.json _meta.retrieved missing")

    # -- token residue ------------------------------------------------------------------
    residue = sorted(set(re.findall(r"\{\{[a-z0-9_.]+\}\}", html)))
    report("tokens:residue", not residue, f"unresolved tokens in built deck: {residue}")

    # -- em-dash sweep (deck grammar: zero outside the MathJax blob) --------------------
    dashes = sans_mathjax(html).count("—")
    report("sweep:emdash", dashes == 0, f"{dashes} em-dash(es) found outside MathJax")

    # -- raw currency inside math -------------------------------------------------------
    bad_math = [m.group(0)[:60] for m in
                re.finditer(r"\\[(\[](?:(?!\\[)\]]).)*?[€$].*?\\[)\]]", sans_mathjax(html), re.S)
                if "\\text{" not in m.group(0)]
    report("sweep:currency-in-math", not bad_math, f"raw currency inside math: {bad_math}")

    # -- slide length budget ------------------------------------------------------------
    for st, txt in slides_visible.items():
        if len(txt) > CHAR_BUDGET:
            msg = f"slide {st!r}: {len(txt)} visible chars > budget {CHAR_BUDGET}"
            (failures if CHAR_BUDGET_HARD else warnings).append((f"length:{st}", msg))

    print(f"labs deck verification: {npass} checks passed, "
          f"{len(warnings)} warnings, {len(failures)} failures")
    for cid, msg in warnings:
        print(f"  WARN {cid:28s} {msg}")
    for cid, msg in failures:
        print(f"  FAIL {cid:28s} {msg}")
    return 1 if failures else 0


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(description="Verify a labs-claims deck against apps/labs_claims.yaml.")
    ap.add_argument("--deck", type=Path, default=DECK, help="deck to verify (default: labs_slides.html)")
    a = ap.parse_args()
    sys.exit(main(a.deck.resolve()))
