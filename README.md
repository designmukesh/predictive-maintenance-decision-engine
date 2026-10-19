# Predictive Maintenance — Decision Engine

> **The missing layer between prediction and action.** Projects #1 and #2 answer
> *"what is the machine's condition?"* This project answers *"what should we do,
> and when?"* — turning RUL predictions and fault classifications into
> maintain / inspect / replace decisions under an explicit, assumption-labeled
> cost model.

## The idea in 60 seconds

A planner holding "RUL = 40 cycles" still has to decide: intervene now or wait?
This project derives the answer from economics instead of folklore:

- **Decision rule:** act when `P(failure) × C_unplanned > C_planned`, i.e. when
  failure risk exceeds `1/k` (k = unplanned ÷ planned cost ratio).
- **Honest uncertainty:** failure probability comes from 3,524 *observed*
  prediction errors (project #2's validation residuals) — no assumed Gaussian.
- **Backtested like a trading strategy:** three policies (run-to-failure,
  fixed-interval, predictive) run over 20 turbofan engines with out-of-sample
  predictions; every bill is exact because true failure cycles are known.

## Headline results (illustrative — costs are labeled assumptions, k=5)

| Policy | Cost / engine | Unplanned failures |
|---|---|---|
| Run-to-failure | 5.0 | 20/20 |
| Fixed-interval (N=25) | 1.0 | 0 |
| **Predictive (T\*=8)** | **1.0** | **0** |

The predictive policy matches the best fixed schedule on cost with **zero
unplanned failures and the least wasted healthy life** — and the ranking holds
for k ∈ {3, 5, 10}. Two findings complicated the story (both in the notebooks):
the cost curve is **L-shaped, not U-shaped** (wasted life isn't monetized), and
T\* doesn't move with k under this cost model — k prices timidity, not the optimum.

The hydraulic module maps project #1's fault states to actions via an auditable
decision table: 1,764 held-out predictions → action distribution, 0.295 expected
action cost per cycle, 1 missed severe state in 380.

## Repo map

```
src/                decision library: costs, RUL decision engine, policy simulators,
                    fault-state decision table, input bridges to projects #1/#2
tests/              14 pytest tests over the decision math
notebooks/
  01_decision_framing.ipynb   cost model → decision rule → empirical risk curves
  02_policy_backtest.ipynb    three-policy backtest, threshold & k sensitivity, autopsy
app/streamlit_app.py         interactive demo: move k and T, watch policies re-rank
docs/               methodology, business_case, limitations, data_dictionary,
                    interview_guide, learning_guide, project_story
reports/            policy_sweep.json, figures
```

## Reproduce

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest tests/ -q                       # 14 tests
jupyter notebook notebooks/            # 01 then 02 (02 retrains; ~3 min)
streamlit run app/streamlit_app.py
```

Inputs regenerate from projects #1 and #2 (`src/inputs.py`); no raw data is
committed. Set `P1`/`P2` paths in `src/inputs.py` if your checkout differs.

## Limitations (volunteer these first)

Costs are assumed; 20 engines is a small backtest; wasted life isn't monetized;
single failure mode (FD001); perfect-execution assumption. Full list in
`docs/limitations.md` — percentages are illustrative, the *method* is the deliverable.
