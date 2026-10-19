"""Cost model for maintenance decisions.

All costs are normalized to planned_intervention = 1.0. Every monetary figure
in this project is an *assumed parameter*, not an observed fact — the framework
is real, the numbers are illustrative. The point of the normalization is that
only *ratios* matter for the decision: specifically k = unplanned / planned.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class MaintenanceCosts:
    """Unit-cost model for one asset.

    planned: cost of a planned intervention (shop visit, scheduled replacement).
        Normalized to 1.0 — the numeraire.
    unplanned_multiplier (k): unplanned failure costs k x planned. Industry
        rule of thumb: k ~ 3-10x (emergency labor, spare premium, downtime,
        secondary damage, schedule disruption).
    inspection: cost of an inspection / boroscope (fraction of planned).
    lead_time: cycles between deciding to intervene and the intervention
        happening (spare lead, slot availability). During lead time the asset
        keeps operating and can still fail.
    """

    planned: float = 1.0
    unplanned_multiplier: float = 5.0
    inspection: float = 0.1
    lead_time: int = 1

    @property
    def unplanned(self) -> float:
        return self.planned * self.unplanned_multiplier

    def describe(self) -> str:
        return (
            f"planned={self.planned}, unplanned={self.unplanned} "
            f"(k={self.unplanned_multiplier}), inspection={self.inspection}, "
            f"lead_time={self.lead_time}"
        )


# Illustrative scenario presets (labeled assumptions, not observations)
SCENARIOS = {
    "conservative": MaintenanceCosts(unplanned_multiplier=3.0, inspection=0.15),
    "baseline": MaintenanceCosts(unplanned_multiplier=5.0, inspection=0.10),
    "severe": MaintenanceCosts(unplanned_multiplier=10.0, inspection=0.05),
}
