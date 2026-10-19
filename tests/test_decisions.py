"""Tests for the decision engine: costs, RUL decisions, policies, fault tables."""
import numpy as np
import pytest

from src.costs import MaintenanceCosts
from src.fault_decisions import (
    INSPECT, MONITOR, OPERATE, REPLACE, action_cost, decide,
    expected_cost_of_missed_failure,
)
from src.policies import (
    simulate_fixed_interval, simulate_predictive, simulate_run_to_failure,
    summarize,
)
from src.rul_decisions import RULDecisionEngine


@pytest.fixture
def costs():
    return MaintenanceCosts(planned=1.0, unplanned_multiplier=5.0,
                            inspection=0.1, lead_time=1)


@pytest.fixture
def engine():
    # synthetic residuals ~ N(0, 10): model slightly noisy but unbiased
    rng = np.random.default_rng(0)
    return RULDecisionEngine(rng.normal(0, 10, 5000), MaintenanceCosts())


# --- costs ---
def test_unplanned_is_k_times_planned(costs):
    assert costs.unplanned == pytest.approx(5.0)


# --- RUL decision engine ---
def test_failure_probability_bounded_and_monotone(engine):
    ps = [engine.failure_probability(r, horizon=10) for r in [0, 30, 60, 120]]
    assert all(0.0 <= p <= 1.0 for p in ps)
    assert ps == sorted(ps, reverse=True)  # higher pred RUL -> lower risk


def test_intervene_fires_on_high_risk(engine):
    act, p = engine.should_intervene(pred_rul=5, horizon=10)
    assert act and p > 1 / 5  # decision rule: p * C_u > C_p


def test_wait_on_healthy(engine):
    act, p = engine.should_intervene(pred_rul=150, horizon=10)
    assert not act


def test_breakeven_threshold_sane(engine):
    t = engine.breakeven_threshold(horizon=10)
    assert 0 < t < 120


# --- policies ---
def test_run_to_failure_always_unplanned(costs):
    r = simulate_run_to_failure(true_life=200, costs=costs)
    assert r["cost"] == pytest.approx(costs.unplanned) and r["unplanned"] == 1


def test_fixed_interval_catches_long_life(costs):
    r = simulate_fixed_interval(true_life=200, interval=50, costs=costs)
    assert r["cost"] == pytest.approx(costs.planned)
    assert r["wasted_life"] == pytest.approx(150.0)


def test_fixed_interval_misses_short_life(costs):
    r = simulate_fixed_interval(true_life=30, interval=50, costs=costs)
    assert r["cost"] == pytest.approx(costs.unplanned)


def test_predictive_acts_in_time(costs):
    # perfect predictions: pred == true; threshold 20, lead 1
    true = np.arange(100, 0, -1, dtype=float)
    r = simulate_predictive(true, true, threshold=20, costs=costs)
    assert r["cost"] == pytest.approx(costs.planned)
    assert r["acted_at"] == 80  # first t with true[t] <= 20


def test_predictive_too_late_when_blind(costs):
    # predictions stuck at 125 (model sees nothing): never acts -> fails
    true = np.arange(100, 0, -1, dtype=float)
    pred = np.full_like(true, 125.0)
    r = simulate_predictive(true, pred, threshold=20, costs=costs)
    assert r["cost"] == pytest.approx(costs.unplanned)


def test_summarize_aggregates(costs):
    rs = [simulate_run_to_failure(200, costs) for _ in range(4)]
    s = summarize(rs)
    assert s["n_engines"] == 4 and s["unplanned_rate"] == 1.0
    assert s["cost_per_engine"] == pytest.approx(costs.unplanned)


# --- fault decisions ---
def test_decide_known_states():
    assert decide("cooler", "close to failure")[0] == REPLACE
    assert decide("pump", "no leakage")[0] == OPERATE
    assert decide("valve", "small lag")[0] == MONITOR
    assert decide("accumulator", "severely reduced")[0] == INSPECT


def test_decide_unknown_raises():
    with pytest.raises(KeyError):
        decide("cooler", "exploded")


def test_action_costs(costs):
    assert action_cost(OPERATE, costs) == 0.0
    assert action_cost(INSPECT, costs) == pytest.approx(0.1)
    assert action_cost(REPLACE, costs) == pytest.approx(1.0)
    assert expected_cost_of_missed_failure(0.2, costs) == pytest.approx(1.0)
