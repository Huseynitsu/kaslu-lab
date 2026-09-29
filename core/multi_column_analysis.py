"""
Laboratory notebook analysis — Entrance (influent) vs Reactor (bulk/effluent).

"Distilled water" is treated as the REAGENT BLANK: it is not a sample point. Its absorbance
should be subtracted during photometry; here it is only checked for contamination.

Indicators depend on the reactor type:
  pn      — two-stage PN: NH4 removal, NO2 accumulation, effluent NO2/NH4 vs 1.32 (anammox feed)
  anammox — stage 2: feed NO2/NH4 (entrance), ΔNO2/ΔNH4 ≈ 1.32, ΔNO3/ΔNH4 ≈ 0.26 [1]
  pna     — one-stage PN/A: TIN removal, ΔNO3/ΔNH4 ≈ 0.11, effluent NO2
"""
from dataclasses import dataclass, field

import matplotlib.pyplot as plt
import pandas as pd

from core.constants import ANAMMOX_IDEAL_RATIO
from core.diagnostics import interpret_daily_reading
from core.lab_table import NOTEBOOK_PARAMETERS, PARAMETER_LABELS, SAMPLE_COLUMNS, extract_column

EFFICIENCY_PARAMS = ("nh4", "tin")
NH4_REMOVAL_WARNING_THRESHOLD = 30.0
NO2_NH4_DEVIATION_TOLERANCE = 0.25
BLANK_TOLERANCE_MG_L = 0.1
SAMPLE_POINTS = ("entrance", "reactor")


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
    indicators: dict = field(default_factory=dict)


def _safe_pct(numerator: float, denominator: float) -> float | None:
    if denominator == 0:
        return None
    return (numerator / denominator) * 100.0


def _no2_nh4_ratio(nh4: float, no2: float) -> float | None:
    if nh4 <= 0:
        return None
    return no2 / nh4


def _tin(d: dict) -> float:
    return d["nh4"] + d["no2"] + d["no3"]


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
    if "entrance" in column_data and "reactor" in column_data:
        for param in NOTEBOOK_PARAMETERS:
            diff_rows.append({
                "Comparison": "Reactor − Entrance",
                "Parameter": PARAMETER_LABELS[param],
                "param_key": param,
                "Difference": column_data["reactor"][param] - column_data["entrance"][param],
            })
    differences_df = pd.DataFrame(diff_rows)

    efficiency_rows = []
    indicators: dict = {}
    if "entrance" in column_data and "reactor" in column_data:
        ent, react = column_data["entrance"], column_data["reactor"]
        for key, label, e_val, r_val in (
            ("nh4", PARAMETER_LABELS["nh4"], ent["nh4"], react["nh4"]),
            ("tin", "TIN = NH4+NO2+NO3 (mg N/L)", _tin(ent), _tin(react)),
        ):
            removal = e_val - r_val
            efficiency_rows.append({
                "Parameter": label,
                "param_key": key,
                "Entrance (mg/L)": e_val,
                "Reactor (mg/L)": r_val,
                "Removal (mg/L)": removal,
                "Efficiency (%)": _safe_pct(removal, e_val),
            })
        d_nh4 = ent["nh4"] - react["nh4"]
        indicators["NH4 removed (mg N/L)"] = d_nh4
        indicators["NO2 change (mg N/L)"] = react["no2"] - ent["no2"]
        indicators["NO3 produced (mg N/L)"] = react["no3"] - ent["no3"]
        if d_nh4 > 0.5:
            indicators["ΔNO3/ΔNH4"] = (react["no3"] - ent["no3"]) / d_nh4
            indicators["ΔNO2/ΔNH4 (consumed)"] = (ent["no2"] - react["no2"]) / d_nh4
    efficiency_df = pd.DataFrame(efficiency_rows)

    ratio_rows = []
    ratio_points = {"pn": ["reactor"], "anammox": ["entrance"]}.get(stage, [])
    for col in ratio_points:
        if col not in column_data:
            continue
        data = column_data[col]
        ratio = _no2_nh4_ratio(data["nh4"], data["no2"])
        ratio_rows.append({
            "Sample point": SAMPLE_COLUMNS[col],
            "column_key": col,
            "NH4-N (mg/L)": data["nh4"],
            "NO2-N (mg/L)": data["no2"],
            "NO2/NH4 ratio": ratio,
            "Ideal ratio": ANAMMOX_IDEAL_RATIO,
            "Deviation from ideal": None if ratio is None else ratio - ANAMMOX_IDEAL_RATIO,
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
        indicators=indicators,
    )


def build_alerts(
    column_data: dict,
    efficiency_df: pd.DataFrame,
    ratio_df: pd.DataFrame,
    stage: str,
) -> list[Alert]:
    alerts: list[Alert] = []

    if "distilled" in column_data:
        blank = column_data["distilled"]
        dirty = [PARAMETER_LABELS[p] for p in ("nh4", "no2", "no3") if blank[p] > BLANK_TOLERANCE_MG_L]
        if dirty:
            alerts.append(Alert("warning", "Reagent blank (distilled water) shows N above %.1f mg/L for %s — "
                                "check water/reagents; subtract blank absorbance." % (BLANK_TOLERANCE_MG_L, ", ".join(dirty))))

    if "entrance" in column_data and "reactor" in column_data:
        ent, react = column_data["entrance"], column_data["reactor"]
        if not efficiency_df.empty:
            nh4_row = efficiency_df[efficiency_df["param_key"] == "nh4"]
            eff = None if nh4_row.empty else nh4_row.iloc[0]["Efficiency (%)"]
            if eff is not None and eff < NH4_REMOVAL_WARNING_THRESHOLD:
                alerts.append(Alert("warning", "NH4 removal efficiency is %.1f%% (below %.0f%%)." % (eff, NH4_REMOVAL_WARNING_THRESHOLD)))
            elif eff is not None:
                alerts.append(Alert("ok", "NH4 removal efficiency is %.1f%%." % eff))
            tin_row = efficiency_df[efficiency_df["param_key"] == "tin"]
            if stage in ("pna", "anammox") and not tin_row.empty and tin_row.iloc[0]["Efficiency (%)"] is not None:
                alerts.append(Alert("ok", "TIN removal efficiency is %.1f%% (autotrophic max ≈ 89%%)." % tin_row.iloc[0]["Efficiency (%)"]))

        diag = interpret_daily_reading(
            react["nh4"], react["no2"], react["no3"],
            ent["nh4"], ent["no2"], ent["no3"], stage=stage,
        )
        level = {"ok": "ok", "warning": "warning", "danger": "danger"}[diag.status]
        for f in diag.findings:
            alerts.append(Alert(level if level != "ok" else "ok", f))
        for a in diag.actions:
            if a != "Maintain current operating conditions.":
                alerts.append(Alert("warning", "Action: " + a))

    for _, row in ratio_df.iterrows():
        ratio = row["NO2/NH4 ratio"]
        if ratio is None or pd.isna(ratio):
            continue
        deviation = abs(ratio - ANAMMOX_IDEAL_RATIO)
        what = "PN effluent" if stage == "pn" else "Anammox feed"
        if deviation > NO2_NH4_DEVIATION_TOLERANCE:
            alerts.append(Alert("warning", "%s NO2/NH4 = %.2f (target 1.32 [1], deviation %.2f)." % (what, ratio, deviation)))
        else:
            alerts.append(Alert("ok", "%s NO2/NH4 = %.2f — close to 1.32." % (what, ratio)))

    if not alerts:
        alerts.append(Alert("ok", "No critical deviations detected."))
    return alerts


def plot_comparison_bars(result: MultiColumnAnalysisResult) -> plt.Figure:
    from core.ui.theme import apply_matplotlib_theme

    apply_matplotlib_theme()
    df = result.values_df.set_index("Parameter")
    plot_cols = [c for c in df.columns if c in (SAMPLE_COLUMNS["entrance"], SAMPLE_COLUMNS["reactor"])]
    fig, ax = plt.subplots(figsize=(10, 5))
    df[plot_cols].plot(kind="bar", ax=ax, rot=0)
    ax.set_ylabel("Concentration / pH")
    ax.set_title("Entrance vs Reactor")
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
    ax.bar(["NH4", "TIN"][: len(plot_df)], plot_df["Efficiency (%)"].astype(float), color=["#2ecc71", "#3498db"][: len(plot_df)])
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
    if ratio_df.empty:
        return None
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
