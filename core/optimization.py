"""
Model-based operating-point search for one-stage PN/A (uncalibrated model!).

Objective: maximise the nitrogen removal RATE (NRR) subject to TIN removal ≥ target,
effluent NO2 < limit and ΔNO3/ΔNH4 < limit; ties → lowest DO (aeration energy).
Evaluated over the last 10 days of the horizon (vectorised grid search over DO × HRT).
"""

from __future__ import annotations

from dataclasses import replace

import numpy as np
import pandas as pd

from core.constants import PNA_NO2_EFFLUENT_WARNING, PNA_NO3_RATIO_WARNING
from core.pna_model import ReactorConfig, simulate


def evaluate_grid(base: ReactorConfig, do_values, hrt_values_d, days: int = 60) -> pd.DataFrame:
    dd, hh = np.meshgrid(np.asarray(do_values, float), np.asarray(hrt_values_d, float))
    dd, hh = dd.ravel(), hh.ravel()
    runs = simulate(replace(base, days=days, dt_min=15.0), overrides={"do": dd, "hrt_d": hh}, record_every_d=5.0)
    rows = []
    for do, hrt, df in zip(dd, hh, runs):
        tail = df[df["Day"] >= days - 10]
        rows.append({
            "DO (mg/L)": do,
            "HRT (h)": hrt * 24.0,
            "NLR (kg N/m3/d)": float(tail["NLR"].mean()),
            "TIN removal (%)": float(tail["TIN_removal_pct"].mean()),
            "NRR (kg N/m3/d)": float(tail["NRR"].mean()),
            "ΔNO3/ΔNH4": float(tail["dNO3_dNH4"].mean()),
            "Effluent NO2 (mg N/L)": float(tail["NO2"].max()),
        })
    return pd.DataFrame(rows)


def optimize_reactor(base: ReactorConfig | None = None, do_values=None, hrt_values_h=None, days: int = 60,
                     no2_limit: float = PNA_NO2_EFFLUENT_WARNING, ratio_limit: float = PNA_NO3_RATIO_WARNING,
                     min_tin_removal: float = 80.0) -> dict:
    base = base or ReactorConfig()
    do_values = do_values if do_values is not None else [0.1, 0.2, 0.3, 0.4, 0.5, 0.7, 1.0]
    hrt_values_h = hrt_values_h if hrt_values_h is not None else [8, 12, 24, 36, 48]
    grid = evaluate_grid(base, do_values, np.asarray(hrt_values_h, float) / 24.0, days)
    feasible = grid[(grid["Effluent NO2 (mg N/L)"] < no2_limit) & (grid["ΔNO3/ΔNH4"] < ratio_limit)
                    & (grid["TIN removal (%)"] >= min_tin_removal)]
    if feasible.empty:
        best = grid.sort_values("TIN removal (%)", ascending=False).iloc[0]
    else:
        best = feasible.assign(_nrr=feasible["NRR (kg N/m3/d)"].round(3)).sort_values(
            ["_nrr", "DO (mg/L)"], ascending=[False, True]).iloc[0].drop("_nrr")
    return {"best": best.to_dict(), "feasible": not feasible.empty, "grid": grid}
