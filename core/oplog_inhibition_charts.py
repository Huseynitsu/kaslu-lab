"""FA / FNA chart series for Reactor Operation Log (separate from generic line charts)."""

from __future__ import annotations

import pandas as pd

from core.chemistry import free_ammonia_as_molecule, free_nitrous_acid_mg_l
from core.operation_log_charts import series_label


def build_fa_chart_df(
    df: pd.DataFrame,
    *,
    x_col: str,
    x_label: str,
    ph: float,
    temperature_c: float,
) -> pd.DataFrame | None:
    src = next((c for c in ("reactor1_effluent_mg_l", "nh4_influent_mg_l") if c in df.columns and df[c].notna().any()), None)
    if src is None:
        return None
    out = df[[x_col]].copy()
    ph_s = df["ph"] if "ph" in df.columns else pd.Series(ph, index=df.index)
    t_s = df["temperature_c"] if "temperature_c" in df.columns else pd.Series(temperature_c, index=df.index)
    out["fa"] = [
        free_ammonia_as_molecule(v, p if pd.notna(p) else ph, t if pd.notna(t) else temperature_c) if pd.notna(v) else None
        for v, p, t in zip(df[src], ph_s, t_s)
    ]
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
    ph_s = df["ph"] if "ph" in df.columns else pd.Series(ph, index=df.index)
    t_s = df["temperature_c"] if "temperature_c" in df.columns else pd.Series(temperature_c, index=df.index)
    out["fna"] = [
        free_nitrous_acid_mg_l(v, p if pd.notna(p) else ph, t if pd.notna(t) else temperature_c) if pd.notna(v) else None
        for v, p, t in zip(df["no2_effluent_mg_l"], ph_s, t_s)
    ]
    out = out.set_index(x_col)[["fna"]]
    out.index.name = x_label
    out.columns = [series_label("fna")]
    return out
