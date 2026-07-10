# Notebook reports (PDF)

One self-contained PDF per notebook — the **full narrative + plots + printed results**,
with code inputs and sampler-progress noise stripped out, so a non-technical reader can
follow the story end to end. Generated from the committed **FULL-mode** runs (full-quality
posteriors: 4 chains, 1500/1500 draws on the headline fits) — these are the reference figures.

| report | technique |
|--------|-----------|
| [00_foundations.pdf](00_foundations.pdf) | causal-inference vocabulary + estimator ladder |
| [01_uplift_targeting.pdf](01_uplift_targeting.pdf) | ⭐ Anchor A — customer-level uplift (BCF) |
| [02_segment_effects.pdf](02_segment_effects.pdf) | segment/moderation effects (pathmc) |
| [03_price_elasticity.pdf](03_price_elasticity.pdf) | hierarchical price elasticity |
| [04_funnel_mediation.pdf](04_funnel_mediation.pdf) | funnel mediation / path effects |
| [05_what_to_control_for.pdf](05_what_to_control_for.pdf) | DAGs, colliders, sensitivity |
| [06_incrementality_mmm.pdf](06_incrementality_mmm.pdf) | causal MMM (pymc-marketing) |
| [07_geo_lift_synthetic_control.pdf](07_geo_lift_synthetic_control.pdf) | ⭐ Anchor B — geo-lift synthetic control |
| [08_rollout_did.pdf](08_rollout_did.pdf) | difference-in-differences |
| [09_threshold_perk_rdd.pdf](09_threshold_perk_rdd.pdf) | regression discontinuity |
| [10_redesign_its.pdf](10_redesign_its.pdf) | interrupted time series |
| [11_endogenous_exposure_iv.pdf](11_endogenous_exposure_iv.pdf) | instrumental variables |

## Regenerate

```bash
make reports        # renders reports/*.pdf from the executed notebooks
```

Needs `xelatex` on the PATH (MacTeX/TeX Live). The generator (`scripts/make_reports.py`)
hides code cells, drops the MCMC progress noise, and sanitizes a few glyphs that the
default LaTeX fonts can't render (Greek letters in code spans, arrows, checkmarks) into
LaTeX-safe text — the real `$…$` math blocks are left untouched and typeset natively.
