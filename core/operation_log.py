"""
Parse and analyze PN/A reactor operation Excel logs (flexible column detection).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import BinaryIO

import pandas as pd

from core.i18n import t
from core.operation_log_schema import SchemaReport, detect_schema, extract_dataframe


@dataclass
class OperationLogSummary:
    row_count: int
    date_start: pd.Timestamp | None
    date_end: pd.Timestamp | None
    duration_min: float | None
    duration_max: float | None
    nh4_removal_r1_mean: float | None
    nh4_removal_r2_mean: float | None
    removal_formula_max_error_pct: float | None
    alerts: list[str] = field(default_factory=list)


@dataclass
class OperationLogResult:
    df: pd.DataFrame
    summary: OperationLogSummary
    schema: SchemaReport
    source_name: str


def removal_rate_pct(influent: float, effluent: float) -> float | None:
    if influent is None or influent <= 0 or effluent is None or pd.isna(effluent):
        return None
    return (influent - effluent) / influent * 100.0


def _read_raw(source: BinaryIO | str | Path) -> pd.DataFrame:
    return pd.read_excel(source, sheet_name=0, header=None)


def _x_axis_column(df: pd.DataFrame, schema: SchemaReport) -> str:
    if "duration_days" in schema.mapped_fields and df["duration_days"].notna().any():
        return "duration_days"
    if "date" in schema.mapped_fields and df["date"].notna().any():
        return "date"
    return "row_index"


def _enrich_computed_columns(df: pd.DataFrame, schema: SchemaReport) -> pd.DataFrame:
    out = df.copy()

    if "nh4_influent_mg_l" in schema.mapped_fields:
        inf = out["nh4_influent_mg_l"]
        if "reactor1_effluent_mg_l" in schema.mapped_fields:
            out["nh4_removal_r1_calc_pct"] = [
                removal_rate_pct(i, e) for i, e in zip(inf, out["reactor1_effluent_mg_l"])
            ]
            if "removal_rate_r1_pct" not in schema.mapped_fields:
                out["removal_rate_r1_pct"] = out["nh4_removal_r1_calc_pct"]
        if "reactor2_effluent_mg_l" in schema.mapped_fields:
            out["nh4_removal_r2_calc_pct"] = [
                removal_rate_pct(i, e) for i, e in zip(inf, out["reactor2_effluent_mg_l"])
            ]
            if "removal_rate_r2_pct" not in schema.mapped_fields:
                out["removal_rate_r2_pct"] = out["nh4_removal_r2_calc_pct"]

    if "tn_influent_mg_l" in schema.mapped_fields and "tn_effluent_r1_mg_l" in schema.mapped_fields:
        out["tn_removal_r1_calc_pct"] = [
            removal_rate_pct(i, e) for i, e in zip(out["tn_influent_mg_l"], out["tn_effluent_r1_mg_l"])
        ]
        if "tn_removal_r1_pct" not in schema.mapped_fields:
            out["tn_removal_r1_pct"] = out["tn_removal_r1_calc_pct"]

    if "x_axis" not in out.columns:
        x_col = _x_axis_column(out, schema)
        if x_col == "row_index" and "row_index" not in out.columns:
            out["row_index"] = range(len(out))
        out["x_axis"] = out[x_col]

    return out


def parse_operation_log(source: BinaryIO | str | Path, *, source_name: str = "upload") -> OperationLogResult:
    raw = _read_raw(source)
    if raw.empty or raw.shape[1] < 2:
        raise ValueError("File is empty or has too few columns.")

    schema = detect_schema(raw)
    if not schema.is_usable:
        hint = "; ".join(schema.warnings) or "Need at least date/duration and NH4 data."
        raise ValueError(f"Could not understand this Excel layout. {hint}")

    df = extract_dataframe(raw, schema)
    if df.empty:
        raise ValueError("No data rows found after parsing.")

    df = _enrich_computed_columns(df, schema)
    summary = _build_summary(df, schema)
    return OperationLogResult(df=df, summary=summary, schema=schema, source_name=source_name)


def _build_summary(df: pd.DataFrame, schema: SchemaReport) -> OperationLogSummary:
    alerts: list[str] = []

    if df.empty:
        return OperationLogSummary(
            row_count=0,
            date_start=None,
            date_end=None,
            duration_min=None,
            duration_max=None,
            nh4_removal_r1_mean=None,
            nh4_removal_r2_mean=None,
            removal_formula_max_error_pct=None,
            alerts=alerts or ["No data rows found after parsing."],
        )

    max_err = None
    if "nh4_removal_r1_calc_pct" in df.columns and "removal_rate_r1_pct" in schema.mapped_fields:
        err1 = (df["nh4_removal_r1_calc_pct"] - df["removal_rate_r1_pct"]).abs()
        parts = [err1]
        if "nh4_removal_r2_calc_pct" in df.columns and "removal_rate_r2_pct" in schema.mapped_fields:
            parts.append((df["nh4_removal_r2_calc_pct"] - df["removal_rate_r2_pct"]).abs())
        max_err = float(pd.concat(parts).max())
        if max_err > 0.05:
            alerts.append(t("oplog.alert.formula_mismatch", err=max_err))

    r1_mean = None
    r2_mean = None
    if df["removal_rate_r1_pct"].notna().any():
        r1_mean = float(df["removal_rate_r1_pct"].mean())
        if r1_mean < 70:
            alerts.append(t("oplog.alert.r1_mean_low", pct=r1_mean))
        latest_r1 = df["removal_rate_r1_pct"].iloc[-1]
        if pd.notna(latest_r1) and latest_r1 < 80:
            alerts.append(t("oplog.alert.r1_latest_low"))
    if df["removal_rate_r2_pct"].notna().any():
        r2_mean = float(df["removal_rate_r2_pct"].mean())

    if (
        "tn_influent_mg_l" in schema.mapped_fields
        and "nh4_influent_mg_l" in schema.mapped_fields
        and (df["tn_influent_mg_l"] - df["nh4_influent_mg_l"]).abs().gt(1).any()
    ):
        alerts.append(t("oplog.alert.tn_nh4_diff"))

    date_start = df["date"].min() if df["date"].notna().any() else None
    date_end = df["date"].max() if df["date"].notna().any() else None
    dur_min = float(df["duration_days"].min()) if df["duration_days"].notna().any() else None
    dur_max = float(df["duration_days"].max()) if df["duration_days"].notna().any() else None

    return OperationLogSummary(
        row_count=len(df),
        date_start=date_start,
        date_end=date_end,
        duration_min=dur_min,
        duration_max=dur_max,
        nh4_removal_r1_mean=r1_mean,
        nh4_removal_r2_mean=r2_mean,
        removal_formula_max_error_pct=max_err,
        alerts=alerts,
    )


def load_default_sample_path() -> Path | None:
    path = Path(r"c:\Users\Huseyn\Desktop\Copy of 侯赛因.xlsx")
    return path if path.is_file() else None


def parse_default_sample() -> OperationLogResult | None:
    path = load_default_sample_path()
    if path is None:
        return None
    return parse_operation_log(path, source_name=path.name)
