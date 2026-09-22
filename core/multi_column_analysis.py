"""
Multi-column lab notebook analysis — Distilled, Entrance, Reactor compared together.
"""

from dataclasses import dataclass, field

import matplotlib.pyplot as plt
import pandas as pd

from core.constants import ANAMMOX_IDEAL_RATIO
from core.lab_table import NOTEBOOK_PARAMETERS, PARAMETER_LABELS, SAMPLE_COLUMNS, extract_column

EFFICIENCY_PARAMS = ("nh4", "no3")
NH4_REMOVAL_WARNING_THRESHOLD = 30.0
NO3_INCREASE_TOLERANCE = 0.5
NO2_NH4_DEVIATION_TOLERANCE = 0.25


@dataclass
class Alert:
    level: str
    message: str


@dataclass
class MultiColumnAnalysisResult:
    values_df: pd.DataFrame
    differences_df: pd.DataFrame
    efficiency_df: pd.DataFrame
    ratio_df: pd.DataFrame
    alerts: list[Alert] = field(default_factory=list)
    selected_columns: list[str] = field(default_factory=list)


def _safe_pct(numerator: float, denominator: float) -> float | None:
    if denominator == 0:
        return None
    return (numerator / denominator) * 100.0


def _no2_nh4_ratio(nh4: float, no2: float) -> float | None:
    if nh4 <= 0:
        return None
    return no2 / nh4


def analyze_multi_column(
    table: dict,
    selected_columns: list[str] | None = None,
    stage: str = "pn",
) -> MultiColumnAnalysisResult:
    columns = selected_columns or list(SAMPLE_COLUMNS.keys())
    columns = [c for c in columns if c in SAMPLE_COLUMNS]

    column_data = {col: extract_column(table, col) for col in columns}

    value_rows = []
    for param in NOTEBOOK_PARAMETERS:
        row = {"Parameter": PARAMETER_LABELS[param], "param_key": param}
        for col in columns:
            row[SAMPLE_COLUMNS[col]] = column_data[col][param]
        value_rows.append(row)
    values_df = pd.DataFrame(value_rows)

    diff_rows = []
    pairs = [
        ("Entrance − Distilled", "entrance", "distilled"),
        ("Reactor − Entrance", "reactor", "entrance"),
        ("Reactor − Distilled", "reactor", "distilled"),
    ]
    for label, col_a, col_b in pairs:
        if col_a not in column_data or col_b not in column_data:
            continue
        for param in NOTEBOOK_PARAMETERS:
            diff_rows.append({
                "Comparison": label,
                "Parameter": PARAMETER_LABELS[param],
                "param_key": param,
                "Difference": column_data[col_a][param] - column_data[col_b][param],
            })
    differences_df = pd.DataFrame(diff_rows)

    efficiency_rows = []
    if "entrance" in column_data and "reactor" in column_data:
        ent = column_data["entrance"]
        react = column_data["reactor"]
        for param in EFFICIENCY_PARAMS:
            removal = ent[param] - react[param]
            pct = _safe_pct(removal, ent[param])
            efficiency_rows.append({
                "Parameter": PARAMETER_LABELS[param],
                "param_key": param,
                "Entrance (mg/L)": ent[param],
                "Reactor (mg/L)": react[param],
                "Removal (mg/L)": removal,
                "Efficiency (%)": pct,
            })
    efficiency_df = pd.DataFrame(efficiency_rows)

    ratio_rows = []
    for col in columns:
        if col not in column_data:
            continue
        data = column_data[col]
        ratio = _no2_nh4_ratio(data["nh4"], data["no2"])
        deviation = None if ratio is None else ratio - ANAMMOX_IDEAL_RATIO
        ratio_rows.append({
            "Sample point": SAMPLE_COLUMNS[col],
            "column_key": col,
            "NH4-N (mg/L)": data["nh4"],
            "NO2-N (mg/L)": data["no2"],
            "NO2/NH4 ratio": ratio,
            "Ideal ratio": ANAMMOX_IDEAL_RATIO,
            "Deviation from ideal": deviation,
        })
    ratio_df = pd.DataFrame(ratio_rows)

    alerts = build_alerts(column_data, efficiency_df, ratio_df, stage)

    return MultiColumnAnalysisResult(
        values_df=values_df,
        differences_df=differences_df,
        efficiency_df=efficiency_df,
        ratio_df=ratio_df,
        alerts=alerts,
        selected_columns=columns,
    )


def build_alerts(
    column_data: dict,
    efficiency_df: pd.DataFrame,
    ratio_df: pd.DataFrame,
    stage: str,
) -> list[Alert]:
    alerts: list[Alert] = []

    if "entrance" in column_data and "reactor" in column_data:
        ent = column_data["entrance"]
        react = column_data["reactor"]

        nh4_row = efficiency_df[efficiency_df["param_key"] == "nh4"]
        if not nh4_row.empty:
            eff = nh4_row.iloc[0]["Efficiency (%)"]
            if eff is not None and eff < NH4_REMOVAL_WARNING_THRESHOLD:
                alerts.append(Alert(
                    "warning",
                    "NH4 removal efficiency is %.1f%% (below %.0f%% threshold)."
                    % (eff, NH4_REMOVAL_WARNING_THRESHOLD),
                ))
            elif eff is not None and eff >= NH4_REMOVAL_WARNING_THRESHOLD:
                alerts.append(Alert(
                    "ok",
                    "NH4 removal efficiency is %.1f%%." % eff,
                ))

        no3_increase = react["no3"] - ent["no3"]
        if no3_increase > NO3_INCREASE_TOLERANCE:
            alerts.append(Alert(
                "warning",
                "NO3 increased from entrance to reactor (+%.2f mg/L) — possible NOB activity [6]."
                % no3_increase,
            ))

        no2_build = react["no2"] - ent["no2"]
        if stage == "pn" and no2_build < 5.0 and ent["nh4"] > 10:
            alerts.append(Alert(
                "warning",
                "Limited NO2 accumulation in reactor — PN may be incomplete [3].",
            ))

    for _, row in ratio_df.iterrows():
        ratio = row["NO2/NH4 ratio"]
        if ratio is None:
            continue
        deviation = abs(ratio - ANAMMOX_IDEAL_RATIO)
        point = row["Sample point"]
        if deviation > NO2_NH4_DEVIATION_TOLERANCE:
            alerts.append(Alert(
                "warning",
                "%s: NO2/NH4 = %.2f (ideal 1.32, deviation %.2f) [1][2]."
                % (point, ratio, deviation),
            ))
        elif row["column_key"] == "reactor" and stage in ("pn", "anammox"):
            alerts.append(Alert(
                "ok",
                "%s: NO2/NH4 = %.2f — close to Anammox feed target 1.32." % (point, ratio),
            ))

    if not alerts:
        alerts.append(Alert("ok", "No critical deviations detected for selected sample points."))

    return alerts


def plot_comparison_bars(result: MultiColumnAnalysisResult) -> plt.Figure:
    from core.ui.theme import apply_matplotlib_theme

    apply_matplotlib_theme()
    df = result.values_df.set_index("Parameter")
    plot_cols = [c for c in df.columns if c in SAMPLE_COLUMNS.values()]
    fig, ax = plt.subplots(figsize=(10, 5))
    df[plot_cols].plot(kind="bar", ax=ax, rot=0)
    ax.set_ylabel("Concentration / pH")
    ax.set_title("Distilled vs Entrance vs Reactor")
    ax.legend(title="Sample point")
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    return fig


def plot_efficiency_bars(efficiency_df: pd.DataFrame) -> plt.Figure | None:
    from core.ui.theme import apply_matplotlib_theme

    apply_matplotlib_theme()
    if efficiency_df.empty:
        return None
    plot_df = efficiency_df.dropna(subset=["Efficiency (%)"])
    if plot_df.empty:
        return None
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(plot_df["Parameter"], plot_df["Efficiency (%)"], color=["#2ecc71", "#3498db"])
    ax.axhline(NH4_REMOVAL_WARNING_THRESHOLD, color="orange", linestyle="--", label="NH4 warning threshold")
    ax.set_ylabel("Removal efficiency (%)")
    ax.set_title("Entrance → Reactor removal efficiency")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    return fig


def plot_ratio_comparison(ratio_df: pd.DataFrame) -> plt.Figure | None:
    from core.ui.theme import apply_matplotlib_theme

    apply_matplotlib_theme()
    plot_df = ratio_df.dropna(subset=["NO2/NH4 ratio"])
    if plot_df.empty:
        return None
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(plot_df["Sample point"], plot_df["NO2/NH4 ratio"], color="#9b59b6")
    ax.axhline(ANAMMOX_IDEAL_RATIO, color="red", linestyle="--", linewidth=2, label="Ideal 1.32 [1]")
    ax.set_ylabel("NO2/NH4 ratio")
    ax.set_title("NO2/NH4 ratio vs Anammox ideal")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    return fig
