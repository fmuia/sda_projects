# Book — open items (carry these to the final review pass)

## Cross-chapter dependency — CLOSED (2026-07-14 final pass)
Ch.2 §2.8 + takeaway 7 now cite Ch.10's DiD width result via `\nbEightBayesOverCluster` and
`\nbEightPooledOverScatter` (point_vs_posterior.tex:461–463, 558–560); `nb08.json` emits both.
The "misspecification goes both ways" claim is fully evidenced.

## Corrections measurement forced on MY briefs (do not reintroduce)
- **ITS cumulative impact is NOT "€1.824M vs €1.825M"** — that is C_T in *proportion-days*. In
  euros it is **€583,564 classical vs €583,852 Bayesian** (gap €288, width ratio 0.96x). The
  finding stands; my units were wrong and I repeated them to the user.
- **The €168,031 phantom in nb05 comes from the OMITTED CONFOUNDER**, not the collider. The
  collider's damage is the *decision flip*: the kitchen sink lands at €4.97, under the €5
  break-even, killing a profitable campaign. (Better lesson than the one I briefed.)
- **nb02 has no Bayesian hierarchical model.** Partial pooling there is the classical
  empirical-Bayes / James-Stein estimator; the Bayesian arm is an interaction model. Chapter
  retitled "Segment effects: pooling and shrinkage".
- **nb00 has no M-bias demo.** Ch.1 presents M-bias structurally, no numbers, and points at Ch.7.
- **HAC lag rule-of-thumb gives 4, not 7** for n=180. Ch.12 defends lag 7 as one weekly cycle (the
  more conservative choice) and shows the SE is insensitive across lags 4/7/14/21.
- **nb02 stale pointer**: its prose promises the hierarchical version "in nb03", but nb03 is price
  elasticity. Left alone as out of scope — fix in a later pass.

## The one honest exception to the iron rule
Ch.1's **LaLonde $1,800 experimental benchmark is CITED, not computed**. Emitted as a macro with
`note="published experimental benchmark; cited, not estimated here"` and flagged as such in the
chapter. This is correct — but it is the only number in the book that is not ours, and it should
stay flagged.

## Infra fixed already (do not re-report)
- results sharded per notebook (was a read-modify-write race)
- `_build_lock()` in build.py (aux/macros.tex race under concurrent agents) + aux self-heal retry
- `report.table(..., math_headers=True)` (headers were escaped into `\$\textbackslash varphi\$`)
- `macro_name()` now REJECTS digits in the key tail (`nb10.cl_r2` -> `\nbTenClR2` is illegal LaTeX
  and killed the whole book build with an error pointing nowhere near the cause)
- build.py CHAPTERS carries all 13; a chapter whose .tex is absent is skipped, not fatal
