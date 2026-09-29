"""Partial nitritation (AOB/NOB) step on the unit-consistent PN/A model (no anammox)."""

from __future__ import annotations

from core.pna_model import ReactorConfig, simulate


def pn_reactor_config(nh4, no2, no3, ph, temperature, do, x_aob, x_nob, srt,
                      *, days=1, influent_nh4=0.0, hrt_days=0.0) -> ReactorConfig:
    continuous = hrt_days and hrt_days > 0 and influent_nh4 > 0
    return ReactorConfig(
        nh4=nh4, no2=no2, no3=no3,
        nh4_in=influent_nh4 if continuous else 0.0, no2_in=0.0, no3_in=0.0,
        hrt_d=hrt_days if continuous else None,
        ph=ph, temperature=temperature, do=do,
        x_aob=max(x_aob, 1e-6), x_nob=max(x_nob, 1e-6), x_amx=1e-9,
        srt_floc=max(float(srt), 1e-3), srt_amx=1e9, days=days,
    )


def partial_nitritation_step(nh4, no2, no3, ph, temperature, do, x_aob, x_nob, srt,
                             influent_nh4: float = 0.0, hrt_days: float = 0.0):
    """
    Advance PN by one day. Returns (nh4, no2, no3, x_aob, x_nob, nar).
    NAR = NO2 / (NO2 + NO3) — nitrite accumulation ratio.
    """
    cfg = pn_reactor_config(nh4, no2, no3, ph, temperature, do, x_aob, x_nob, srt,
                            days=1, influent_nh4=influent_nh4, hrt_days=hrt_days)
    last = simulate(cfg).iloc[-1]
    denom = last["NO2"] + last["NO3"]
    nar = float(last["NO2"] / denom) if denom > 1e-9 else 0.0
    return (float(last["NH4"]), float(last["NO2"]), float(last["NO3"]),
            float(last["AOB"]), float(last["NOB"]), nar)
