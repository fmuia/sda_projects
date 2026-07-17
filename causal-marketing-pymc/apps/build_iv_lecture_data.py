"""Assemble the IV lecture's data bundle and embed it, self-contained, into apps/iv_lecture.py.

The lecture must run two ways:
  - `marimo run apps/iv_lecture.py`  (local, in the room) — reads the JSON on disk;
  - `marimo export html-wasm`        (the student take-home) — has NO filesystem, so the
    data must travel INSIDE the .py.

So this script does three things, all from numbers the notebooks already produced (never retyped):
  1. keeps the real posterior draws that notebooks/11's "lecture bundle" cell wrote to
     apps/iv_lecture_data.json (beta_probit / beta_gauss / rho_probit, plus the per-seed means);
  2. merges in the *scalar* results — the simulated market from book/build/results/nb11.json and
     the real Criteo market from nb11b.json — so the euro figures and the real-data section cite
     sourced values, not hand-typed ones;
  3. writes the merged bundle back to iv_lecture_data.json AND embeds a zlib+base64 copy between
     the # <<BLOB-START>> / # <<BLOB-END>> markers in iv_lecture.py, so the WASM export is
     fully self-contained (zlib and base64 are stdlib, available in Pyodide).

Run from the repo root:  .venv/bin/python apps/build_iv_lecture_data.py
"""
from __future__ import annotations
import base64
import json
import zlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
DRAWS = HERE / "iv_lecture_data.json"
APP = HERE / "iv_lecture.py"
RESULTS = REPO / "book" / "build" / "results"


def _vals(shard: str, keys: dict[str, str]) -> dict[str, float]:
    """Pull {out_name: numeric value} for the requested macro keys from a results shard."""
    d = json.loads((RESULTS / shard).read_text())
    out: dict[str, float] = {}
    for src, dst in keys.items():
        rec = d[f"{shard.split('.')[0]}.{src}"]
        out[dst] = float(rec["value"])
    return out


def main() -> None:
    bundle = json.loads(DRAWS.read_text())

    # --- the simulated market (nb11): the numbers the euro sections read off ---
    bundle["sim"] = _vals("nb11.json", {
        "naive": "naive", "wald": "wald", "iv_est": "iv_est", "f_stat": "f_stat",
        "first": "first", "fs_lo": "fs_lo", "fs_hi": "fs_hi", "wedge": "wedge",
        "cap": "cap", "coinflip": "coinflip", "headroom": "headroom", "net": "net",
        "bayes_mean": "bayes_mean", "gauss_mean": "gauss_mean",
        "rho": "rho", "rho_lo": "rho_lo", "rho_hi": "rho_hi",
        "ar_lo": "ar_lo", "ar_hi": "ar_hi",
    })

    # --- the real Criteo market (nb11b): the real-data section ---
    bundle["criteo"] = _vals("nb11b.json", {
        "naive": "naive", "wald": "wald", "f_stat": "f_stat", "first_pct": "first_pct",
        "anchor_wald": "anchor",
        "wald_lo": "wald_lo", "wald_hi": "wald_hi", "naive_lo": "naive_lo", "naive_hi": "naive_hi",
        "bayes_mean": "bayes_mean", "bayes_lo": "bayes_lo", "bayes_hi": "bayes_hi",
        "rho": "rho", "rho_lo": "rho_lo", "rho_hi": "rho_hi",
        "conv_value": "conv_value", "cost": "cost", "cap": "cap",
        "premium_quarter": "premium_quarter", "exposures_quarter": "exposures_quarter",
        "n_full_m": "n_full_m", "fold_cover": "fold_cover", "fold_mean": "fold_mean",
    })

    # 1) rewrite the on-disk bundle (used by the local `marimo run`)
    DRAWS.write_text(json.dumps(bundle, separators=(",", ":")))

    # 2) embed a compressed copy into the app so the WASM export is self-contained
    raw = json.dumps(bundle, separators=(",", ":")).encode()
    blob = base64.b64encode(zlib.compress(raw, 9)).decode()
    # The assignment lives inside a `def _():` cell, so every line is indented 4 spaces; the string
    # is chunked to 100 chars/line so the .py stays readable and diff-able.
    chunks = [blob[i:i + 100] for i in range(0, len(blob), 100)]
    body = "\n".join(["    BLOB = ("] + [f'        "{c}"' for c in chunks] + ["    )"])

    src = APP.read_text()
    start, end = "# <<BLOB-START>>", "# <<BLOB-END>>"
    pre = src[:src.index(start)]                     # ends with the marker's 4-space indent
    post = src[src.index(end) + len(end):]           # begins right after the end marker text
    src = pre + start + "\n" + body + "\n    " + end + post
    APP.write_text(src)

    kb_json = DRAWS.stat().st_size / 1024
    print(f"bundle: {len(bundle['beta_probit'])} probit + {len(bundle['beta_gauss'])} gauss draws, "
          f"sim+criteo scalars merged")
    print(f"  iv_lecture_data.json  {kb_json:5.1f} KB (local run)")
    print(f"  embedded blob         {len(blob) / 1024:5.1f} KB (WASM-safe, in iv_lecture.py)")


if __name__ == "__main__":
    main()
