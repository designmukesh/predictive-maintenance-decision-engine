# Data Dictionary — Project #3 inputs

This project trains no new models on new data. Its inputs are the **outputs**
of projects #1 and #2, regenerated on demand by `src/inputs.py`.

## RUL backtest inputs (from project #2)

| Field | Meaning |
|---|---|
| `engines[u]["true"]` | True RUL per cycle for validation engine u (piecewise-linear, capped at 125) |
| `engines[u]["pred"]` | Out-of-sample predicted RUL per cycle (HGB trained on the other 80 engines) |
| `engines[u]["life"]` | True total cycles (failure cycle) |
| `residuals` | `pred − true` on 3,524 validation windows; the empirical error distribution |

Source: NASA C-MAPSS FD001 (Saxena & Goebel, 2008), via project #2's pipeline.
20 validation engines; seed 42 split.

## Hydraulic fault inputs (from project #1)

| Field | Meaning |
|---|---|
| `component` | cooler / valve / pump / accumulator |
| `true_state` | Human-readable fault label (e.g. "close to failure", "weak leakage") |
| `pred_state` | RandomForest prediction on held-out cycle |
| `confidence` | Max predicted-class probability |

1,764 rows = 441 held-out cycles × 4 components. Source: UCI hydraulic rig
dataset (Helwig et al., 2018), via project #1's feature pipeline (187 features).

## Cost parameters (assumed, not observed)

| Parameter | Baseline | Meaning |
|---|---|---|
| `planned` | 1.0 | Cost of a planned intervention (numeraire) |
| `unplanned_multiplier` (k) | 5.0 | Unplanned failure costs k× planned |
| `inspection` | 0.1 | Cost of an inspection |
| `lead_time` | 1 cycle | Delay between decision and action |
