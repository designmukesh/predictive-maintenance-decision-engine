# Executive Summary — Predictive Maintenance Decision Engine

**Question.** Predictions don't maintain machines — decisions do. Given RUL
estimates and fault classifications from two validated ML systems, what is the
optimal maintenance policy, and what is it worth?

**Approach.** (1) An explicit cost model normalized to planned = 1.0, with the
unplanned/planned ratio k ∈ {3, 5, 10} as labeled scenarios. (2) A decision rule
derived from expected cost: intervene when failure risk exceeds 1/k, with risk
read off the observed residual distribution (3,524 validation errors — no assumed
Gaussian). (3) A backtest of three policies over 20 engines with out-of-sample
predictions: run-to-failure, fixed-interval, predictive. (4) An auditable
fault-state → action table for the hydraulic system, evaluated on 1,764 held-out
predictions.

**Findings.**
- Predictive (T\*=8) eliminates unplanned failures (0/20) at the same modeled
  cost as the best fixed schedule (1.0/engine vs 5.0 for run-to-failure).
- Policy ranking is robust across k ∈ {3, 5, 10}; savings vs run-to-failure range
  67–90% (illustrative — they inherit the assumed costs).
- The cost-vs-threshold curve is L-shaped with a flat bottom: threshold error is
  cheap; the binding tradeoff is wasted healthy life (mean 7.8 cycles at T\*).
- T\* is k-insensitive under this cost model (k prices timidity, not the optimum);
  the marginal rule p > 1/k remains k-sensitive. Monetizing wasted life is the
  documented extension that would unite the two.
- Hydraulic policy: expected action cost 0.295/cycle; 1 missed severe state in 380.

**Recommendation.** The method — not any single number — is the deliverable:
derive thresholds from your cost ratio, backtest policies on your history, and
monitor slip rate + wasted life as the policy's vital signs. Next step is a field
pilot with a holdout fleet, not a rollout.

**Caveats.** Assumed costs; n=20 engines; single failure mode; perfect execution
assumed; test-rig fault data. See docs/limitations.md.
