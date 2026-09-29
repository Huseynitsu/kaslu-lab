"""Chart helpers for Reactor Operation Log — human-readable labels only."""

from __future__ import annotations

import pandas as pd

from core.i18n import bilingual, t
from core.operation_log_schema import SchemaReport

CHART_SERIES_LABELS = {
    "nh4_influent_mg_l": ("NH₄ influent", "NH₄ 进水"),
    "reactor1_effluent_mg_l": ("Reactor (1) effluent", "反应器 (1) 出水"),
    "reactor2_effluent_mg_l": ("Reactor (2) effluent", "反应器 (2) 出水"),
    "removal_rate_r1_pct": ("Removal R1 (%)", "R1 去除率 (%)"),
    "removal_rate_r2_pct": ("Removal R2 (%)", "R2 去除率 (%)"),
    "tn_influent_mg_l": ("TN influent", "TN 进水"),
    "tn_effluent_r1_mg_l": ("TN effluent R1", "TN 出水 R1"),
    "tn_effluent_r2_mg_l": ("TN effluent R2", "TN 出水 R2"),
    "loading_influent_g_n_l_d": ("Influent loading", "进水负荷"),
    "anr_r1_g_n_l_d": ("ANR R1", "R1 ANR"),
    "anr_r2_g_n_l_d": ("ANR R2", "R2 ANR"),
    "fa": ("FA (mg NH₃/L)", "FA（mg NH₃/L）"),
    "fna": ("FNA (mg HNO₂-N/L)", "FNA（mg HNO₂-N/L）"),
}

TABLE_COLUMN_LABELS = {
    "date": ("Date", "日期"),
    "duration_days": ("Duration (days)", "运行时间（天）"),
    "nh4_influent_mg_l": ("NH₄ influent", "NH₄ 进水"),
    "reactor1_effluent_mg_l": ("R1 effluent", "R1 出水"),
    "reactor2_effluent_mg_l": ("R2 effluent", "R2 出水"),
    "removal_rate_r1_pct": ("Removal R1 (%)", "R1 去除率 (%)"),
    "removal_rate_r2_pct": ("Removal R2 (%)", "R2 去除率 (%)"),
    "tn_influent_mg_l": ("TN influent", "TN 进水"),
    "tn_effluent_r1_mg_l": ("TN effluent R1", "TN 出水 R1"),
    "anr_r1_g_n_l_d": ("ANR R1", "R1 ANR"),
    "loading_influent_g_n_l_d": ("Influent load", "进水负荷"),
}


def series_label(field: str) -> str:
    pair = CHART_SERIES_LABELS.get(field)
    if pair:
        return bilingual(pair[0], pair[1])
    return field.replace("_", " ").title()


def table_label(field: str) -> str:
    pair = TABLE_COLUMN_LABELS.get(field)
    if pair:
        return bilingual(pair[0], pair[1])
    return field.replace("_", " ").title()


def resolve_x_axis(df: pd.DataFrame, schema: SchemaReport) -> tuple[str, str]:
    if "duration_days" in schema.mapped_fields and df["duration_days"].notna().any():
        return "duration_days", t("oplog.duration")
    if "date" in schema.mapped_fields and df["date"].notna().any():
        return "date", t("oplog.date_range")
    if "duration_days" in df.columns and df["duration_days"].notna().any():
        return "duration_days", t("oplog.duration")
    return "duration_days" if "duration_days" in df.columns else df.columns[0], t("oplog.duration")


def build_line_chart_df(df: pd.DataFrame, schema: SchemaReport, columns: list[str]) -> pd.DataFrame:
    x_col, x_label = resolve_x_axis(df, schema)
    available = [c for c in columns if c in df.columns]
    out = df[available].copy()
    out.index = df[x_col]
    out.index.name = x_label
    out.columns = [series_label(c) for c in available]
    return out


def build_display_table(df: pd.DataFrame) -> pd.DataFrame:
    skip = {"x_axis", "row_index"}
    skip_suffix = "_calc_pct"
    cols = [c for c in df.columns if c not in skip and not c.endswith(skip_suffix)]
    cols = cols[:14]
    view = df[cols].copy()
    view.columns = [table_label(c) for c in cols]
    return view


def escape_markdown(text: str) -> str:
    """Prevent underscores and asterisks from breaking Streamlit markdown alerts."""
    return text.replace("\\", "\\\\").replace("_", "\\_").replace("*", "\\*")
