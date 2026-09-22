"""FA / FNA chart series for Reactor Operation Log (separate from generic line charts)."""

from __future__ import annotations

import pandas as pd

from core.chemistry import free_ammonia_mg_l, free_nitrous_acid_mg_l
from core.operation_log_charts import series_label


def build_fa_chart_df(
    df: pd.DataFrame,
    *,
    x_col: str,
    x_label: str,
    ph: float,
    temperature_c: float,
) -> pd.DataFrame | None:
    if "nh4_influent_mg_l" not in df.columns:
        return None
    out = df[[x_col]].copy()
    out["fa"] = df["nh4_influent_mg_l"].apply(
        lambda v: free_ammonia_mg_l(v, ph, temperature_c) if pd.notna(v) else None
    )
    out = out.set_index(x_col)[["fa"]]
    out.index.name = x_label
    out.columns = [series_label("fa")]
    return out


def build_fna_chart_df(
    df: pd.DataFrame,
    *,
    x_col: str,
    x_label: str,
    ph: float,
    temperature_c: float,
) -> pd.DataFrame | None:
    if "no2_effluent_mg_l" not in df.columns or not df["no2_effluent_mg_l"].notna().any():
        return None
    out = df[[x_col]].copy()
    out["fna"] = df["no2_effluent_mg_l"].apply(
        lambda v: free_nitrous_acid_mg_l(v, ph, temperature_c) if pd.notna(v) else None
    )
    out = out.set_index(x_col)[["fna"]]
    out.index.name = x_label
    out.columns = [series_label("fna")]
    return out
