# Learning Guide — Predictive Maintenance Decision Engine

## What you'll learn
1. Why predictions ≠ decisions, and what the missing layer contains.
2. How to derive an intervention threshold from economics (p > 1/k).
3. How to turn observed model errors into honest failure probabilities.
4. How to backtest maintenance policies like trading strategies.
5. Why the cost curve came out L-shaped — and what that teaches about cost models.

## Path through the repo (2–3 hours)
1. **README.md** (10 min) — the one-page story.
2. **Notebook 01** (45 min) — run it. Pause at the risk curves: for each horizon,
   ask yourself *why* the curve is steep where it is. Change k in the worked
   example and watch the act-cycle move.
3. **`src/`** (30 min) — read `costs.py`, then `rul_decisions.py`, then
   `policies.py`. They're small; every line earns its place. Run the tests:
   `pytest tests/ -q`.
4. **Notebook 02** (60 min) — the backtest. Before looking at results, predict:
   which policy wins? Is the cost curve U- or L-shaped? Then read the
   interpretation cells — they disagree with the first draft, on purpose.
5. **Streamlit app** (20 min) — `streamlit run app/streamlit_app.py`. Move the k
   slider and T slider; find a combination where the predictive policy *loses*
   to fixed-interval. (Hint: try very small T.)
6. **docs/limitations.md** (10 min) — memorize the top three; volunteer them
   before anyone asks.

## Exercises
1. **Monetize wasted life.** Add a `wasted_cost_per_cycle` parameter to
   `MaintenanceCosts`, charge it in `simulate_predictive`, and re-run the sweep.
   Does the curve become U-shaped? Does T* move with k now?
2. **Break the policy.** Construct a residual distribution (e.g. biased late
   errors) under which T*=8 suffers slips. What does that tell you about
   monitoring?
3. **Write the work order.** Pick one engine's intervention point and draft the
   actual maintenance work order a planner would issue — notice what the model
   *doesn't* tell you (spares, crew, slot).

## Key terms
- **k (cost ratio):** unplanned ÷ planned intervention cost. The only cost number
  the decision needs.
- **Lexicographic selection:** minimize cost first, then wasted life — for flat-bottomed optima.
- **Slip:** a failure that beats the policy inside the lead time.
- **Empirical residual CDF:** the observed error distribution, used as the
  uncertainty model.
- **Vital signs:** slip rate + wasted life — the two numbers to monitor live.
