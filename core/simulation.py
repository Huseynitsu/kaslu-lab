"""Anammox-stage 30-day simulation (batch or continuous) on the PN/A model."""

import numpy as np
import pandas as pd

from core.anammox_model import anammox_reactor_config, environmental_activity
from core.config import ExperimentConfig
from core.constants import ANAMMOX_HCO3_MASS_PER_NH4, PNA_MAX_TN_REMOVAL
from core.pna_model import simulate


def simulate_30_days(config: ExperimentConfig, days: int = 30) -> pd.DataFrame:
    """
    Columns kept for backward compatibility: Day, NH4, NO2, NO3, HCO3, Biomass, Activity, Stability.

    ``Stability`` is now an explicit *performance index* = TIN removal / theoretical maximum
    (0.888 for Strous stoichiometry), clipped to 0–1. It is NOT a measured stability.
    """
    cfg = anammox_reactor_config(
        config.nh4, config.no2, config.no3, config.ph, config.temperature, config.do,
        config.x_anammox, config.srt, days=days,
        hrt_d=config.hrt_d, nh4_in=config.nh4_in, no2_in=config.no2_in, no3_in=config.no3_in,
    )
    df = simulate(cfg)
    df = df[df["Day"] >= 1].reset_index(drop=True)
    activity = environmental_activity(config.ph, config.temperature, config.do)
    if config.hrt_d:
        nh4_used = (cfg.nh4_in - df["NH4"]).clip(lower=0)
        hco3 = np.maximum(config.hco3 - nh4_used * ANAMMOX_HCO3_MASS_PER_NH4, 0.0)
    else:
        hco3 = np.maximum(config.hco3 - (config.nh4 - df["NH4"]).clip(lower=0) * ANAMMOX_HCO3_MASS_PER_NH4, 0.0)
    perf = (df["TIN_removal_pct"] / 100.0 / PNA_MAX_TN_REMOVAL).clip(0, 1)
    out = pd.DataFrame({
        "Day": df["Day"].round().astype(int),
        "NH4": df["NH4"], "NO2": df["NO2"], "NO3": df["NO3"],
        "HCO3": hco3, "Biomass": df["AMX"],
        "Activity": activity, "Stability": perf,
        "TIN_removal_pct": df["TIN_removal_pct"], "dNO3_dNH4": df["dNO3_dNH4"],
    })
    return out
