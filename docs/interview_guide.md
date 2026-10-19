# Interview Guide — Predictive Maintenance Decision Engine

## The 90-second pitch
"Most predictive-maintenance pilots die when the model meets the planner: the
model says RUL is 40 cycles, and nobody knows what to *do*. I built the missing
layer — a decision engine that turns RUL predictions and fault classifications
into maintain/replace/inspect decisions under an explicit cost model. Backtested
on 20 turbofan engines with out-of-sample predictions, the predictive policy
eliminates unplanned failures at the same cost as the best fixed schedule, with
thresholds derived from economics — act when failure risk exceeds 1/k — not tuned
by hand."

## Questions you should be able to answer

**Q: Why not just pick the threshold by grid search on cost?**
A: I did sweep it — but the cost curve has a flat bottom, so the argmin is
ill-defined. The honest selection is lexicographic: minimize cost, then minimize
wasted healthy life. And the flat bottom is good news: threshold error is cheap.

**Q: Your T* doesn't move with k. Isn't that suspicious?**
A: It's correct for this cost model and I can prove it: once T is large enough
for zero failures, cost is 20×1.0 regardless of k — k only prices the left wall
(the cost of being too timid). The *marginal* rule (act when p > 1/k) IS
k-sensitive. If wasted life were monetized, T* would move with k too — that's a
stated extension.

**Q: Why empirical residuals instead of a Gaussian?**
A: Because the model's error distribution is what it is — asymmetric, heavier
near failure. Reading P(fail) off 3,524 observed errors is honest uncertainty;
assuming normality would understate late-error risk, which is exactly the
dangerous kind.

**Q: 20 engines is tiny. Why should I believe the savings?**
A: You shouldn't believe the percentages — they're illustrative. Believe the
ranking: predictive ≥ fixed-interval > run-to-failure holds across k ∈ {3,5,10}
and the mechanism is transparent. The next step is a field pilot, not a rollout.

**Q: Fixed-interval already gets 1.0 per engine. Why bother with ML?**
A: Fair — and I state it plainly in the business case. The ML buys precision,
not cost, here: zero unplanned failures with less wasted life, adapting per
engine instead of per calendar. On a heterogeneous fleet the gap widens.

**Q: How would you deploy this?**
A: Three pieces: (1) the policy service (predict → decide → work order),
(2) re-estimation of the residual distribution as field data arrives,
(3) monitoring the two vital signs — slip rate and wasted life — with an
automatic threshold review when either drifts.

## Questions to ask them
- "How do your planners set intervention thresholds today — calendar, hours, gut feel?"
- "Do you have a measured unplanned/planned cost ratio, or is k tribal knowledge?"
- "What happens to a model recommendation nobody acts on — is there a feedback loop?"
