"""
Self-control (supervisory aeration control) for one-stage PN/A.

The controller proposes a new bulk DO set-point (and, if DO is already at its floor, a shorter
aerobic fraction) from the latest daily indicators. It is a DECISION-SUPPORT tool: every action
must be confirmed by the operator. Two strategies are provided so they can be compared in the
thesis on the digital twin:

* ``rules`` — expert rules derived from PN/A literature (NOB ↔ high DO; NO2 build-up ↔ anammox
               limitation; high NH4 with low NO2/NO3 ↔ AOB limitation).
* ``pi``    — velocity-form PI law on two errors:
               e1 = NH4_out − NH4_setpoint   (ammonium-based aeration control, "ABAC")
               e2 = ΔNO3/ΔNH4 − 0.11         (nitrate-production feedback, NOB guard)
               ΔDO = Kp·Δe + Ki·e   (clipped).

Also provides ``closed_loop_test`` — runs the controller against the mechanistic model
(core.pna_model) as a digital twin, with measurement noise.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace

import numpy as np
import pandas as pd

from core.constants import (
    PNA_NO2_EFFLUENT_ALARM,
    PNA_NO2_EFFLUENT_WARNING,
    PNA_NO3_PER_NH4_REMOVED,
    PNA_NO3_RATIO_ALARM,
    PNA_NO3_RATIO_WARNING,
    PNA_RESIDUAL_NH4_MIN,
)
from core.pna_model import ReactorConfig, simulate


@dataclass
class ControllerSettings:
    do_min: float = 0.05
    do_max: float = 1.0
    do_step: float = 0.05
    aeration_fraction_min: float = 0.3
    nh4_setpoint: float = 5.0           # mg N/L residual NH4 target
    nh4_high: float = 40.0              # AOB-limited if above and NO2/NO3 low
    kp_nh4: float = 0.005               # (mg O2/L) per (mg N/L)
    ki_nh4: float = 0.002
    kp_ratio: float = 1.0               # (mg O2/L) per unit ratio
    ki_ratio: float = 0.5


@dataclass
class ControlAction:
    do_setpoint: float
    aeration_fraction: float
    change: str                 # increase | decrease | hold
    rationale: list[str] = field(default_factory=list)
    other_actions: list[str] = field(default_factory=list)
    needs_operator_confirmation: bool = True


def _clip(v, lo, hi):
    return float(min(max(v, lo), hi))


def recommend_rules(latest: dict, do_now: float, aeration_fraction: float = 1.0,
                    s: ControllerSettings | None = None) -> ControlAction:
    """latest: dict with no3_ratio, no2_out, nh4_out (NaN allowed)."""
    s = s or ControllerSettings()
    ratio = latest.get("no3_ratio")
    no2 = latest.get("no2_out") or 0.0
    nh4 = latest.get("nh4_out")
    why, other = [], []
    delta = 0.0
    af = aeration_fraction

    if no2 >= PNA_NO2_EFFLUENT_ALARM:
        delta = -2 * s.do_step
        why.append(f"Effluent NO2 {no2:.0f} ≥ {PNA_NO2_EFFLUENT_ALARM} mg N/L: nitritation outruns anammox → less oxygen.")
        other.append("Reduce nitrogen loading until NO2 < 20 mg N/L; check anammox activity and temperature.")
    elif ratio is not None and np.isfinite(ratio) and ratio >= PNA_NO3_RATIO_ALARM:
        delta = -2 * s.do_step
        why.append(f"ΔNO3/ΔNH4 {ratio:.3f} ≥ {PNA_NO3_RATIO_ALARM}: NOB proliferation → lower DO.")
        other.append("Increase floc wasting / hydrocyclone underflow to shorten NOB (floc) SRT; keep residual NH4.")
    elif ratio is not None and np.isfinite(ratio) and ratio >= PNA_NO3_RATIO_WARNING:
        delta = -s.do_step
        why.append(f"ΔNO3/ΔNH4 {ratio:.3f} ≥ {PNA_NO3_RATIO_WARNING}: early NOB activity → lower DO one step.")
    elif no2 >= PNA_NO2_EFFLUENT_WARNING:
        delta = -s.do_step
        why.append(f"Effluent NO2 {no2:.0f} mg N/L rising → lower DO one step.")
    elif nh4 is not None and np.isfinite(nh4) and nh4 >= s.nh4_high:
        delta = +s.do_step
        why.append(f"Residual NH4 {nh4:.0f} ≥ {s.nh4_high} mg N/L with low NO2/NO3 → AOB oxygen-limited, raise DO.")
    elif nh4 is not None and np.isfinite(nh4) and nh4 < PNA_RESIDUAL_NH4_MIN and ratio is not None and np.isfinite(ratio) \
            and ratio > PNA_NO3_PER_NH4_REMOVED * 1.2:
        delta = -s.do_step
        why.append("Residual NH4 very low while NO3 production rises → over-aeration, lower DO.")
    else:
        why.append("Indicators within target band → hold set-point.")

    new_do = do_now + delta
    if new_do < s.do_min and delta < 0:
        af = _clip(aeration_fraction - 0.1, s.aeration_fraction_min, 1.0)
        why.append(f"DO already at floor ({s.do_min}); shorten aerobic fraction to {af:.0%}.")
    new_do = _clip(new_do, s.do_min, s.do_max)
    change = "increase" if new_do > do_now + 1e-9 else "decrease" if new_do < do_now - 1e-9 or af < aeration_fraction else "hold"
    return ControlAction(new_do, af, change, why, other)


class PIController:
    """Velocity-form PI on NH4 residual (+) and ΔNO3/ΔNH4 (−)."""

    def __init__(self, s: ControllerSettings | None = None):
        self.s = s or ControllerSettings()
        self.prev_e = None

    def step(self, latest: dict, do_now: float) -> ControlAction:
        s = self.s
        nh4 = latest.get("nh4_out")
        ratio = latest.get("no3_ratio")
        e1 = (nh4 - s.nh4_setpoint) if nh4 is not None and np.isfinite(nh4) else 0.0
        e2 = (ratio - PNA_NO3_PER_NH4_REMOVED) if ratio is not None and np.isfinite(ratio) else 0.0
        e2 = max(e2, 0.0)  # only act on excess nitrate
        prev = self.prev_e or (e1, e2)
        d_do = (s.kp_nh4 * (e1 - prev[0]) + s.ki_nh4 * e1) - (s.kp_ratio * (e2 - prev[1]) + s.ki_ratio * e2)
        d_do = _clip(d_do, -2 * s.do_step, 2 * s.do_step)
        self.prev_e = (e1, e2)
        new_do = _clip(do_now + d_do, s.do_min, s.do_max)
        change = "increase" if new_do > do_now + 1e-9 else "decrease" if new_do < do_now - 1e-9 else "hold"
        why = [f"PI: e_NH4 = {e1:+.1f} mg N/L, e_NO3ratio = {e2:+.3f} → ΔDO = {new_do - do_now:+.3f} mg/L."]
        return ControlAction(new_do, 1.0, change, why)


# ---------------------------------------------------------------------------
# Digital twin
# ---------------------------------------------------------------------------
def _indicators_from_record(rec: dict, cfg: ReactorConfig, rng, noise: float) -> dict:
    def meas(v):
        return max(v * (1 + rng.normal(0, noise)), 0.0)
    nh4 = meas(rec["NH4"])
    no2 = meas(rec["NO2"])
    no3 = meas(rec["NO3"])
    removed = cfg.nh4_in - nh4
    ratio = (no3 - cfg.no3_in) / removed if removed > 1 else float("nan")
    return {"nh4_out": nh4, "no2_out": no2, "no3_out": no3, "no3_ratio": ratio}


def closed_loop_test(cfg: ReactorConfig, strategy: str = "rules", settings: ControllerSettings | None = None,
                     noise: float = 0.03, seed: int = 1) -> pd.DataFrame:
    """
    strategy: "fixed" (open loop), "rules" or "pi". Controller acts once per day on noisy
    daily measurements of the model's effluent.
    """
    rng = np.random.default_rng(seed)
    s = settings or ControllerSettings()
    state = {"do": cfg.do}
    pi = PIController(s)
    log = []

    def schedule(day, st):
        rec = st["records"][-1]
        ind = _indicators_from_record(rec, cfg, rng, noise)
        if strategy == "rules":
            act = recommend_rules(ind, state["do"], 1.0, s)
            state["do"] = act.do_setpoint
        elif strategy == "pi":
            act = pi.step(ind, state["do"])
            state["do"] = act.do_setpoint
        log.append({"Day": day, "DO_setpoint": state["do"], **ind})
        return state["do"]

    df = simulate(replace(cfg), do_schedule=schedule)
    return df


def synthetic_nob_outbreak(days: int = 70, onset_day: int = 30, do_base: float = 0.3, do_after: float = 0.65,
                           noise: float = 0.04, seed: int = 7) -> pd.DataFrame:
    """
    SYNTHETIC demo data (clearly labelled): stable PN/A, then an aeration fault raises DO from
    ``onset_day`` and NOB slowly take over. Used to demonstrate / test early-warning lead time.
    """
    rng = np.random.default_rng(seed)
    cfg = ReactorConfig(days=days, do=do_base, dt_min=10.0, x_nob=5.0)
    warm = replace(cfg, days=250, dt_min=15.0)
    ss = simulate(warm).iloc[-1]
    cfg = replace(cfg, nh4=ss["NH4"], no2=ss["NO2"], no3=ss["NO3"],
                  x_aob=ss["AOB"], x_nob=max(ss["NOB"], 5.0), x_amx=ss["AMX"])

    def schedule(day, st):
        if day < onset_day:
            return do_base
        ramp = min((day - onset_day) / 20.0, 1.0)
        return do_base + ramp * (do_after - do_base)

    sim = simulate(cfg, do_schedule=schedule)
    sim = sim[sim["Day"] >= 1]

    def n(v):
        return np.maximum(v * (1 + rng.normal(0, noise, len(v))), 0.0)

    return pd.DataFrame({
        "day": sim["Day"].round().astype(int).values,
        "nh4_in": n(np.full(len(sim), cfg.nh4_in)),
        "nh4_out": n(sim["NH4"].values),
        "no2_in": 0.0,
        "no2_out": n(sim["NO2"].values),
        "no3_in": 0.0,
        "no3_out": n(sim["NO3"].values),
        "do": sim["DO"].values,
        "ph": 7.6,
        "temperature": cfg.temperature,
        "hrt_h": 24.0 * cfg.hrt_d,
    })
