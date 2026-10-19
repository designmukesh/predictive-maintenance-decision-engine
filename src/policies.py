"""Policy backtest simulators.

Each policy is run per engine over its full run-to-failure trajectory
(true failure cycle known). Costs are accumulated per engine-life:

- run_to_failure: operate until true failure -> pay unplanned.
- fixed_interval(N): intervene every N operating cycles -> pay planned each
  time; if the engine would fail before the next intervention, pay unplanned.
- predictive(engine, threshold T): each cycle, read the (out-of-sample)
  predicted RUL; when pred <= T, schedule intervention after `lead_time`
  cycles. If true failure lands inside the lead time -> unplanned (too late);
  else planned. Wasted healthy life = true remaining at intervention.

All predictions used here must be out-of-sample (project #2 validation
engines) — otherwise the backtest is circular.
"""
import numpy as np

from src.costs import MaintenanceCosts


def simulate_run_to_failure(true_life, costs: MaintenanceCosts):
    """Operate until failure. One cost, no decisions."""
    return {
        "cost": costs.unplanned,
        "unplanned": 1,
        "interventions": 0,
        "wasted_life": 0.0,
    }


def simulate_fixed_interval(true_life, interval, costs: MaintenanceCosts):
    """Intervene every `interval` cycles of operation."""
    t, cost, n_int = 0, 0.0, 0
    while True:
        nxt = t + interval
        if true_life <= nxt:
            # fails before the next scheduled intervention
            cost += costs.unplanned
            return {"cost": cost, "unplanned": 1, "interventions": n_int,
                    "wasted_life": 0.0}
        t = nxt
        cost += costs.planned
        n_int += 1
        return {"cost": cost, "unplanned": 0, "interventions": n_int,
                "wasted_life": float(true_life - t)}


def simulate_predictive(true_ruls, pred_ruls, threshold, costs: MaintenanceCosts):
    """Act when predicted RUL <= threshold; action lands after lead_time.

    true_ruls / pred_ruls: arrays aligned per cycle (out-of-sample preds).
    true_ruls[t] = true remaining cycles at cycle t.
    """
    true_ruls = np.asarray(true_ruls, dtype=float)
    pred_ruls = np.asarray(pred_ruls, dtype=float)
    L = costs.lead_time
    for t in range(len(true_ruls)):
        if pred_ruls[t] <= threshold:
            act_at = t + L
            if true_ruls[t] <= L:
                # fails during the lead time: too late
                return {"cost": costs.unplanned, "unplanned": 1,
                        "interventions": 0, "wasted_life": 0.0,
                        "acted_at": t}
            return {"cost": costs.planned, "unplanned": 0,
                    "interventions": 1, "wasted_life": float(true_ruls[t] - L),
                    "acted_at": t}
    # never triggered -> runs to failure
    return {"cost": costs.unplanned, "unplanned": 1, "interventions": 0,
            "wasted_life": 0.0, "acted_at": None}


def summarize(results):
    """Aggregate a list of per-engine result dicts."""
    n = len(results)
    return {
        "n_engines": n,
        "total_cost": float(sum(r["cost"] for r in results)),
        "cost_per_engine": float(sum(r["cost"] for r in results) / n),
        "unplanned_failures": int(sum(r["unplanned"] for r in results)),
        "unplanned_rate": float(sum(r["unplanned"] for r in results) / n),
        "interventions": int(sum(r["interventions"] for r in results)),
        "mean_wasted_life": float(np.mean([r["wasted_life"] for r in results])),
    }
