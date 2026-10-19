# Limitations — read before quoting any number

## 1. The costs are assumed, not observed
Every saving percentage inherits the cost model. k = 5 is a labeled assumption;
real k varies by asset, site, and contract. The robust claim is the *ranking*
(predictive ≥ fixed-interval > run-to-failure across k ∈ {3, 5, 10}), not any
single percentage.

## 2. Wasted healthy life is not monetized
The cost model charges for interventions and failures but not for discarded
remaining life. That's why the cost-vs-threshold curve is L-shaped (flat bottom)
rather than U-shaped, and why T* doesn't move with k. Monetizing lost production
per cycle is the natural extension — and would make the optimum k-sensitive.

## 3. Twenty engines is a small backtest
The turbofan backtest runs on 20 validation engines. Zero unplanned failures at
T*=8 is encouraging, not a guarantee — a larger fleet sample would widen the
confidence band. Treat percentages as illustrative.

## 4. Single failure mode, single operating condition
FD001 has one fault mode and one operating condition. Real fleets have competing
failure modes and varying duty cycles; the decision engine would need a
competing-risks extension.

## 5. The simulator assumes perfect execution
Interventions are assumed to happen exactly after the lead time, restore the
asset to as-good-as-new, and never introduce infant-mortality risk. Real
maintenance has execution noise.

## 6. Fault policy evaluated on test-rig data
The hydraulic decisions inherit project #1's caveat: test-rig cycles, not field
data. The decision table's rationales are domain judgment, reviewable in
`src/fault_decisions.py` — argue with them; that's the point.

## 7. No concept drift handling in the backtest
The empirical residual distribution is treated as stationary. In production it
must be re-estimated continuously — the monitoring design (docs) watches slip
rate and wasted life as the policy's vital signs.

## What we'd do with more time
Monetize wasted life; competing-risks RUL; execution-noise simulation;
calibration of predicted probabilities for the fault policy; a field pilot
design with a holdout fleet for a randomized policy comparison.
