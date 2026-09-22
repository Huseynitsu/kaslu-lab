import pandas as pd

from core.anammox_model import full_anammox_model
from core.config import ExperimentConfig


def simulate_30_days(config: ExperimentConfig) -> pd.DataFrame:
    nh4 = config.nh4
    no2 = config.no2
    no3 = config.no3
    hco3 = config.hco3

    ph = config.ph
    temperature = config.temperature
    do = config.do

    x_anammox = config.x_anammox
    srt = config.srt

    days = []
    nh4_history = []
    no2_history = []
    no3_history = []
    hco3_history = []
    biomass_history = []
    activity_history = []
    stability_history = []

    for day in range(1, 31):
        nh4_before = nh4
        no2_before = no2

        (
            nh4,
            no2,
            no3,
            hco3,
            x_anammox,
            activity,
        ) = full_anammox_model(
            nh4,
            no2,
            no3,
            hco3,
            ph,
            temperature,
            do,
            x_anammox,
            srt,
        )

        ratio = no2_before / max(nh4_before, 1e-6)
        ratio_factor = 1 - abs(ratio - 1.32) / 1.32
        ratio_factor = max(0.0, min(ratio_factor, 1.0))

        biomass_factor = min(1.0, x_anammox / 1000.0)

        stability = activity * ratio_factor * biomass_factor
        stability = max(0.0, min(stability, 1.0))

        days.append(day)
        nh4_history.append(nh4)
        no2_history.append(no2)
        no3_history.append(no3)
        hco3_history.append(hco3)
        biomass_history.append(x_anammox)
        activity_history.append(activity)
        stability_history.append(stability)

    return pd.DataFrame({
        "Day": days,
        "NH4": nh4_history,
        "NO2": no2_history,
        "NO3": no3_history,
        "HCO3": hco3_history,
        "Biomass": biomass_history,
        "Activity": activity_history,
        "Stability": stability_history,
    })
