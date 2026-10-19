# Business Case — why a decision layer, not just a model

## The problem it solves
Most industrial-AI pilots die at the same point: *"the model works, but nobody
acts on it."* The missing piece is rarely accuracy — it's the absence of a
**decision policy**: who acts, on what signal, at what threshold, at what cost.
This project is that missing piece, built on two real prediction systems.

## What the backtest shows (illustrative numbers, labeled assumptions)
On 20 validation turbofan engines at baseline economics (k=5):

- **Run-to-failure:** 5.0 per engine, 20/20 unplanned failures.
- **Best fixed-interval (N=25):** 1.0 per engine — planned beats reactive even
  without any ML, a fact worth stating plainly.
- **Predictive (T*=8):** 1.0 per engine, **0 unplanned failures**, least wasted
  healthy life of any zero-failure option.

The predictive policy's edge over fixed-interval isn't cost here — it's
**precision**: same spend, fewer surprises, and it adapts per engine instead of
per calendar.

## The product argument
1. **Thresholds from economics, not folklore.** "Act at RUL < 30" becomes
   "act when failure risk exceeds 1/k" — a number a planner can defend.
2. **Robust to the least certain input.** Policy ranking holds for k ∈ {3, 5, 10};
   the flat-bottomed cost curve means threshold error is cheap.
3. **Auditable automation.** The fault-state table is code-reviewed policy, not a
   black box — a reliability engineer can argue with every rule.
4. **Monitoring built in.** Slip rate (failures that beat the policy) and wasted
   life are the policy's vital signs; both are tracked, not hoped for.

## Honest boundaries (for the exec who asks "so what?")
- Percentages are illustrative — they inherit assumed costs and 20 engines.
- The framework generalizes; the numbers don't transfer to your fleet.
- The next step is a field pilot with a holdout fleet, not a rollout.

## One-slide version
> We turned two ML models into maintenance decisions. Backtested on 20 engines,
> the predictive policy eliminates unplanned failures at the same cost as the
> best fixed schedule — with thresholds derived from your cost ratio, not tuned
> by hand. The method is the deliverable; your costs plug straight in.
