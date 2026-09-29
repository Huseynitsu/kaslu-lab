"""
Anammox-stage helpers (backward-compatible API) built on the unit-consistent PN/A model.

Bug fixed (2026-09): the previous version multiplied a specific rate (g N/g VSS/d) by biomass
in g/L but subtracted the result from concentrations in mg/L, so anammox conversion was
~1000× too slow (800 mg VSS/L removed only ~0.4 mg NH4-N/L per day).
"""

from __future__ import annotations



from core.constants import ANAMMOX_HCO3_MASS_PER_NH4, ANAMMOX_NO2_PER_NH4, ANAMMOX_NO3_PER_NH4
from core.pna_model import KineticParameters, ReactorConfig, growth_rates, simulate


def mechanistic_prediction(nh4, no2):
    """Expected intrinsic NO3 production (mg N/L) if the limiting substrate is fully used [1]."""
    nh4_available = min(nh4, no2 / ANAMMOX_NO2_PER_NH4)
    return max(nh4_available, 0.0) * ANAMMOX_NO3_PER_NH4


def environmental_activity(ph: float, temperature: float, do: float, params: KineticParameters | None = None) -> float:
    """Relative anammox activity (0–1) from T, pH and DO only (substrate-saturated)."""
    p = params or KineticParameters()
    _, _, mu_x = growth_rates(1e6, p.k_no2_amx * 20, do, ph, temperature, p)
    _, _, mu_ref = growth_rates(1e6, p.k_no2_amx * 20, 0.0, p.ph_opt_amx, 35.0, p)
    return float(min(max(float(mu_x) / float(mu_ref), 0.0), 1.0))


def anammox_reactor_config(nh4, no2, no3, ph, temperature, do, x_anammox, srt, *, days=1,
                           hrt_d=None, nh4_in=None, no2_in=None, no3_in=0.0) -> ReactorConfig:
    return ReactorConfig(
        nh4=nh4, no2=no2, no3=no3,
        nh4_in=nh4_in if nh4_in is not None else nh4,
        no2_in=no2_in if no2_in is not None else no2,
        no3_in=no3_in,
        hrt_d=hrt_d, ph=ph, temperature=temperature, do=do,
        x_aob=1e-6, x_nob=1e-6, x_amx=x_anammox,
        srt_floc=1e9, srt_amx=max(float(srt), 1e-3), days=days,
    )


def full_anammox_model(nh4, no2, no3, hco3, ph, temperature, do, x_anammox, srt):
    """
    Advance an anammox BATCH by one day.
    Returns (nh4, no2, no3, hco3, biomass, activity) — same signature as before.
    """
    cfg = anammox_reactor_config(nh4, no2, no3, ph, temperature, do, x_anammox, srt, days=1)
    last = simulate(cfg).iloc[-1]
    nh4_used = max(nh4 - last["NH4"], 0.0)
    hco3_new = max(hco3 - nh4_used * ANAMMOX_HCO3_MASS_PER_NH4, 0.0)
    return (
        float(last["NH4"]), float(last["NO2"]), float(last["NO3"]), float(hco3_new),
        float(last["AMX"]), environmental_activity(ph, temperature, do),
    )
