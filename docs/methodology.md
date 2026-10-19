# Methodology — Predictive Maintenance Decision Engine

## 1. What this project is (and isn't)

Projects #1 and #2 answer *"what is the machine's condition?"* — fault classifications
and remaining-useful-life estimates. This project answers the question a maintenance
planner actually asks: *"what should we do, and when?"*

It is a **decision layer**, not a new ML model. It consumes:

- **RUL predictions** — out-of-sample predictions from project #2's HistGradientBoosting
  model (trained on 80 turbofan engines, decided on the other 20), plus the 3,524
  observed validation residuals as an empirical error distribution.
- **Fault-state predictions** — RandomForest classifiers retrained on project #1's
  hydraulic data (80/20 split, seed 42), evaluated on the held-out 441 cycles.

## 2. The cost model

All costs are normalized to `planned_intervention = 1.0`. The decision-relevant
parameter is `k = unplanned / planned` (industry rule of thumb: 3–10×). Three
labeled scenarios are carried through: k = 3 (conservative), 5 (baseline), 10 (severe).
Every monetary figure is an **assumed parameter**, stated as such — the framework is
real, the numbers are illustrative.

## 3. The decision rule (RUL)

Act when expected cost of waiting exceeds cost of acting:

```
p(true RUL < horizon | predicted RUL) × C_u > C_p   ⟺   p > 1/k
```

The failure probability `p` is read off the **empirical residual CDF** from project #2's
validation engines — observed errors, not an assumed Gaussian. If the residual
distribution shifts in the field, these curves are the first thing to re-estimate.

## 4. Policy backtest

Three policies are simulated per engine over full run-to-failure trajectories
(true failure cycle known, so every bill is exact):

| Policy | Rule | Cost per engine-life |
|---|---|---|
| Run-to-failure | operate until break | k |
| Fixed-interval (N) | replace every N cycles | 1.0 per intervention; k if failure lands between |
| Predictive (T) | act when pred RUL ≤ T; action lands after lead time | 1.0 if in time; k if failure lands in lead time |

Threshold T is swept 0–60; the selection rule is lexicographic: minimize cost,
then minimize wasted healthy life.

## 5. Fault-state policy (hydraulic)

An explicit, auditable decision table maps `(component, predicted state) → action`
(operate / monitor / inspect / replace), each rule carrying a stated rationale
(e.g. a cooler "close to failure" runs ~17 °C hotter per project #1 — replace,
don't debate). Evaluated on 1,764 held-out predictions by action distribution,
expected action cost per cycle, and count of missed severe states.

## 6. What "validation" means here

- Predictions are out-of-sample w.r.t. the decision backtest in both modules.
- The 20-engine backtest is small — percentages are illustrative, rankings are the claim.
- Sensitivity is run over k ∈ {3, 5, 10}; the policy ranking never flips.
- 14 pytest tests cover the decision math (costs, thresholds, policy accounting).
