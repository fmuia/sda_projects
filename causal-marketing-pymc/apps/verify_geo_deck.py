"""Verify every numeric claim in the geo-lift slide deck against recomputation.

The deck (apps/geo_lift_slides.html) states numbers in three layers:
  - static prose (token-substituted from the nb07/nb07b shards at build time),
  - the N map (formatted strings injected from the shards, written into spans by JS),
  - live charts reading the baked DATA bundle.

This harness closes the loop: apps/geo_claims.yaml maps each displayed number to the
slide that states it (anchored by data-t, never by slide position), to an expression
recomputed from the baked DATA, and/or to the shard token it must equal. A future
change to DATA, the shards, or the prose fails loudly with the slide named.

Checks per claim (all optional except id+slides):
  text   : string that must appear on every listed slide (tag-stripped, ws-normalised)
  expr   : numpy expression over DATA keys; helpers rmse(a,b), pctl(x,q), skew(x)
  value  : expected numeric value of expr (and of the shard, if given)
  tol    : |expr - value| tolerance (default 0.5); tol_shard for the shard check
  shard  : token name whose shard *value* must match `value`
  min/max: bounds on expr instead of value (guards, e.g. skew > 0.5)
  defect : known-defect note -> reported as WARN, not FAIL (remediation phases burn
           these down; an empty defect list is the target state)

Also verified: every N-map key equals its shard text, and a per-slide visible-length
budget (warn-only until the Phase-4 trim, then hard).

Run: .venv/bin/python apps/verify_geo_deck.py   (exit 1 on any FAIL)
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
REPO = HERE.parent
DECK = HERE / "geo_lift_slides.html"
CLAIMS = HERE / "geo_claims.yaml"
RESULTS = REPO / "book" / "build" / "results"

CHAR_BUDGET = 2600          # visible chars per slide (fold-out bodies excluded)
CHAR_BUDGET_HARD = True


def load_deck():
    html = DECK.read_text()
    i = html.index("/*__DATA__*/")
    j = html.index("{", i)
    data, _ = json.JSONDecoder().raw_decode(html, j)
    nm = re.search(r"/\*__NUMS__\*/(\{.*?\})/\*__ENDNUMS__\*/", html, re.S)
    nmap = json.loads(nm.group(1)) if nm else {}
    body = html[: html.index("/* ==== baked data (injected) ==== */")]
    slides, slides_visible = {}, {}

    def strip_tags(chunk):
        txt = re.sub(r"<[^>]+>", " ", chunk)
        txt = htmllib.unescape(txt)
        return re.sub(r"[\s   ]+", " ", txt).strip()

    for chunk in re.split(r'(?=<section class="slide)', body)[1:]:
        t = re.search(r'data-t="([^"]*)"', chunk)
        key = htmllib.unescape(t.group(1)) if t else f"slide{len(slides)+1}"
        slides[key] = strip_tags(chunk)
        # what the audience sees before opening any fold: keep each <details>'s summary,
        # drop its body
        vis = re.sub(r"<details.*?<summary>(.*?)</summary>.*?</details>", r" \1 ", chunk, flags=re.S)
        slides_visible[key] = strip_tags(vis)
    return data, nmap, slides, slides_visible


def load_shards():
    out = {}
    for shard in ("nb07.json", "nb07b.json"):
        d = json.loads((RESULTS / shard).read_text())
        for k, rec in d.items():
            if isinstance(rec, dict):
                out[k] = rec
    return out


def skew(x):
    x = np.asarray(x, float)
    m = x - x.mean()
    return float((m**3).mean() / (m**2).mean() ** 1.5)


def make_env(data):
    env = {
        "np": np, "sum": np.sum, "mean": np.mean, "std": np.std, "abs": np.abs,
        "min": np.min, "max": np.max, "sort": np.sort, "diff": np.diff, "sqrt": np.sqrt,
        "all": np.all, "float": float, "len": len,
        "pctl": lambda x, q: float(np.percentile(np.asarray(x, float), q)),
        "rmse": lambda a, b: float(np.sqrt(np.mean((np.asarray(a, float) - np.asarray(b, float)) ** 2))),
        "skew": skew,
        "norm_q90": 1.2815515655446004,
        "norm_cdf": lambda z: 0.5 * (1 + __import__("math").erf(z / 2**0.5)),
    }
    for k, v in data.items():
        if isinstance(v, list):
            try:
                env[k] = np.asarray(v, dtype=float)
            except (TypeError, ValueError):
                env[k] = v
        else:
            env[k] = v
    return env


def norm(s):
    return re.sub(r"[\s   ]+", " ", s)


def main() -> int:
    data, nmap, slides, slides_visible = load_deck()
    shards = load_shards()
    env = make_env(data)
    claims = yaml.safe_load(CLAIMS.read_text())

    failures, warnings, npass = [], [], 0

    def report(claim_id, ok, msg, defect=None):
        nonlocal npass
        if ok:
            npass += 1
        elif defect:
            warnings.append((claim_id, f"KNOWN DEFECT ({defect}): {msg}"))
        else:
            failures.append((claim_id, msg))

    for c in claims:
        cid = c["id"]
        defect = c.get("defect")
        if defect:
            # the entry documents the CURRENT (convicted) state so the deck verifies
            # end-to-end; keep the conviction visible until the fixing phase lands
            warnings.append((cid, f"OPEN DEFECT: {defect}"))
        # -- text presence on every listed slide ------------------------------------
        texts = c.get("texts") or ([c["text"]] if c.get("text") else [])
        for t in texts:
            for st in c.get("slides", []):
                if st not in slides:
                    report(cid, False, f"slide anchor {st!r} not found in deck", defect)
                elif norm(t) not in slides[st]:
                    report(cid, False, f"text {t!r} missing on slide {st!r}", defect)
                else:
                    report(cid, True, "")
        # -- recomputation from DATA -------------------------------------------------
        if "expr" in c:
            try:
                v = float(eval(c["expr"], {"__builtins__": {}}, env))  # noqa: S307 - trusted repo file
            except Exception as e:  # noqa: BLE001
                report(cid, False, f"expr error: {e}", defect)
                v = None
            if v is not None:
                if "value" in c:
                    tol = c.get("tol", 0.5)
                    report(cid, abs(v - c["value"]) <= tol,
                           f"expr={v:.4g} vs displayed {c['value']} (tol {tol})", defect)
                if "min" in c:
                    report(cid, v >= c["min"], f"expr={v:.4g} below min {c['min']}", defect)
                if "max" in c:
                    report(cid, v <= c["max"], f"expr={v:.4g} above max {c['max']}", defect)
        # -- shard cross-check ---------------------------------------------------------
        if "shard" in c:
            rec = shards.get(c["shard"])
            if rec is None:
                report(cid, False, f"shard token {c['shard']!r} missing", defect)
            elif "value" in c and isinstance(rec.get("value"), (int, float)):
                tol = c.get("tol_shard", c.get("tol", 0.5))
                report(cid, abs(rec["value"] - c["value"]) <= tol,
                       f"shard {c['shard']}={rec['value']:.4g} vs displayed {c['value']} (tol {tol})", defect)
            elif "shard_text" in c:
                report(cid, rec.get("text") == c["shard_text"],
                       f"shard {c['shard']} text={rec.get('text')!r} != {c['shard_text']!r}", defect)

    # -- N map: every injected formatted number equals its shard text -----------------
    for k, v in nmap.items():
        rec = shards.get(f"nb07.{k}", shards.get(f"nb07b.{k}"))
        ok = rec is not None and str(rec.get("text")) == str(v)
        report(f"nmap:{k}", ok, f"N[{k}]={v!r} vs shard {rec.get('text') if rec else 'MISSING'!r}")

    # -- slide length budget -----------------------------------------------------------
    for st, txt in slides_visible.items():
        if len(txt) > CHAR_BUDGET:
            msg = f"slide {st!r}: {len(txt)} visible chars > budget {CHAR_BUDGET}"
            (failures if CHAR_BUDGET_HARD else warnings).append((f"length:{st}", msg))

    print(f"geo deck verification: {npass} checks passed, "
          f"{len(warnings)} warnings, {len(failures)} failures")
    for cid, msg in warnings:
        print(f"  WARN {cid:28s} {msg}")
    for cid, msg in failures:
        print(f"  FAIL {cid:28s} {msg}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
