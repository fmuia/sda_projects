"""Verify the unified session deck (apps/unified_slides.html) end to end.

Two registries, one deck:
  - apps/geo_claims.yaml   via verify_geo_deck  (--allow-missing-slides semantics: claims
    anchored to full-deck slides absent from the short arc are skipped, exactly as for
    apps/geo_lift_sh.html);
  - apps/labs_claims.yaml  via verify_labs_deck (also carries the deck-wide sweeps: token
    residue, ZERO em-dashes outside MathJax, no raw currency inside math, per-slide
    visible-length budget, pin hygiene).

Run: .venv/bin/python apps/verify_unified_deck.py   (exit 1 on any FAIL)
"""
from __future__ import annotations

import sys
from pathlib import Path

import verify_geo_deck as vg
import verify_labs_deck as vl

HERE = Path(__file__).resolve().parent
DECK = HERE / "unified_slides.html"


def main() -> int:
    if not DECK.exists():
        sys.exit(f"FAIL: {DECK} missing — run apps/build_unified_slides.py first.")
    print("== geo claims (short-arc subset) " + "=" * 46)
    rc_geo = vg.main(deck=DECK, allow_missing_slides=True)
    print("== labs claims + deck-wide sweeps " + "=" * 45)
    rc_labs = vl.main(deck=DECK)
    return 1 if (rc_geo or rc_labs) else 0


if __name__ == "__main__":
    sys.exit(main())
