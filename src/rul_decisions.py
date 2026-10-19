"""Turbofan RUL decision engine — the heart of project #3.

The question is not "what is the RUL?" (project #2 answered that) but
"given a predicted RUL with known error, when should we intervene?"

Decision rule from expected cost. Let:
  p = P(true RUL < horizon | predicted RUL)   # failure risk before next chance
  C_p = cost of planned intervention
  C_u = cost of unplanned failure  (= k * C_p)

Act now if expected cost of waiting exceeds cost of acting:
    p * C_u > C_p    <=>    p > 1 / k

The risk p comes from the *empirical residual distribution* observed on
validation engines in project #2 — honest uncertainty, not an assumed
Gaussian. If residuals r = predicted - true, then
    P(true < H | pred) = P(r > pred - H) = 1 - CDF_resid(pred - H).
"""
import numpy as np

from src.costs import MaintenanceCosts


class RULDecisionEngine:
    """Turns RUL predictions + observed error into intervene/wait decisions."""

    def __init__(self, residuals, costs: MaintenanceCosts = None):
        """residuals: array of (predicted - true) from validation engines."""
        self.residuals = np.asarray(residuals, dtype=float)
        self.costs = costs or MaintenanceCosts()
        # sorted residuals for empirical CDF lookups
        self._sorted = np.sort(self.residuals)

    def failure_probability(self, pred_rul, horizon):
        """P(true RUL < horizon | predicted RUL = pred_rul).

        = P(residual > pred_rul - horizon), read off the empirical CDF.
        """
        thresh = pred_rul - horizon
        # fraction of observed residuals strictly greater than thresh
        return float(np.mean(self._sorted > thresh))

    def should_intervene(self, pred_rul, horizon=1):
        """Act now if p(fail within horizon) * C_u > C_p."""
        p = self.failure_probability(pred_rul, horizon)
        return bool(p * self.costs.unplanned > self.costs.planned), p

    def breakeven_threshold(self, horizon=1, grid=None):
        """Predicted-RUL threshold where the decision flips (for reporting).

        Returns the largest pred_rul at which should_intervene is True.
        """
        grid = np.arange(0, 200, 0.5) if grid is None else np.asarray(grid)
        decisions = [self.should_intervene(r, horizon)[0] for r in grid]
        below = grid[decisions]
        return float(below.max()) if len(below) else 0.0

    def expected_cost_of_waiting(self, pred_rul, horizon=1):
        """p * C_u — the expected cost if we do nothing for `horizon` cycles."""
        return self.failure_probability(pred_rul, horizon) * self.costs.unplanned
