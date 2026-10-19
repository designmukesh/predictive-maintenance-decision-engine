"""Fault-state decision tables (hydraulic system, project #1 outputs).

Project #1 classifies each component's condition per operating cycle.
This module maps (component, predicted state, confidence) -> maintenance
action, with an expected-cost justification per rule.

Actions:
  OPERATE  - keep running, no action
  MONITOR  - keep running, flag for watchlist / next inspection
  INSPECT  - schedule inspection at next planned window (pay inspection cost)
  REPLACE  - schedule replacement before failure (pay planned cost)

The mapping encodes domain judgment: a "close to failure" cooler degrades
fast and hot (project #1: ~17C hotter) -> REPLACE; a "reduced efficiency"
cooler is stable -> INSPECT. Rules are explicit and auditable — the point
is a *decision policy you can argue about*, not a black box.
"""
from src.costs import MaintenanceCosts

OPERATE, MONITOR, INSPECT, REPLACE = "operate", "monitor", "inspect", "replace"

# (component, predicted_state) -> (action, rationale)
DECISION_TABLE = {
    # cooler: 3 states
    ("cooler", "close to failure"): (REPLACE,
        "Cooler near failure runs ~17C hotter (project #1); thermal runaway risk."),
    ("cooler", "reduced efficiency"): (INSPECT,
        "Degraded but stable; inspect at next window, watch trend."),
    ("cooler", "full efficiency"): (OPERATE, "Healthy."),
    # valve: 4 states
    ("valve", "close to failure"): (REPLACE,
        "Valve near total failure risks uncommanded motion / pressure loss."),
    ("valve", "severe lag"): (INSPECT,
        "Response degraded; inspect and trend before it worsens."),
    ("valve", "small lag"): (MONITOR, "Minor lag; watchlist, no action yet."),
    ("valve", "optimal switching"): (OPERATE, "Healthy."),
    # pump: 3 states
    ("pump", "severe leakage"): (REPLACE,
        "Severe internal leakage -> pressure collapse risk."),
    ("pump", "weak leakage"): (INSPECT,
        "Early leakage signature; inspect seals at next window."),
    ("pump", "no leakage"): (OPERATE, "Healthy."),
    # accumulator: 4 states
    ("accumulator", "close to failure"): (REPLACE,
        "Loss of pressure buffering -> system shock risk."),
    ("accumulator", "severely reduced"): (INSPECT,
        "Precharge likely low; inspect and recharge."),
    ("accumulator", "slightly reduced"): (MONITOR, "Mild; watchlist."),
    ("accumulator", "optimal pressure"): (OPERATE, "Healthy."),
}


def decide(component, predicted_state):
    """Return (action, rationale) for a component prediction."""
    key = (component, predicted_state)
    if key not in DECISION_TABLE:
        raise KeyError(f"unknown (component, state): {key}")
    return DECISION_TABLE[key]


def action_cost(action, costs: MaintenanceCosts):
    """Immediate cost of taking an action (expected-value framing)."""
    return {
        OPERATE: 0.0,
        MONITOR: 0.0,
        INSPECT: costs.inspection,
        REPLACE: costs.planned,
    }[action]


def expected_cost_of_missed_failure(prob_failure, costs: MaintenanceCosts):
    """What a wrong OPERATE/MONITOR costs in expectation: p * C_u."""
    return prob_failure * costs.unplanned
