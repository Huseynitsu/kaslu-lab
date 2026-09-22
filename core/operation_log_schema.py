"""Detect columns in lab operation Excel files (flexible headers, EN/ZH)."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

import pandas as pd

# Canonical internal field names used across the app.
ALL_CANONICAL_FIELDS = [
    "date",
    "duration_days",
    "nh4_influent_abs",
    "nh4_influent_mg_l",
    "reactor1_abs",
    "reactor1_effluent_mg_l",
    "reactor2_abs",
    "reactor2_effluent_mg_l",
    "removal_rate_r1_pct",
    "removal_rate_r2_pct",
    "hrt",
    "loading_influent_g_n_l_d",
    "loading_r1_g_n_l_d",
    "loading_r2_g_n_l_d",
    "anr_r1_g_n_l_d",
    "anr_r2_g_n_l_d",
    "tn_influent_mg_l",
    "tn_effluent_r1_mg_l",
    "tn_effluent_r2_mg_l",
    "tn_removal_r1_pct",
    "tn_removal_r2_pct",
    "ph",
    "temperature_c",
    "do_mg_l",
    "no2_effluent_mg_l",
    "no3_effluent_mg_l",
]

# (field, patterns, priority) — higher priority wins on conflict.
FIELD_RULES: list[tuple[str, list[str], int]] = [
    ("date", [r"\bdate\b", r"日期"], 100),
    ("duration_days", [r"duration", r"\bdays\b", r"天数", r"时间", r"日"], 95),
    ("nh4_influent_abs", [r"nh4.*influent.*(abs|吸光)", r"influent.*nh4.*(abs|吸光)", r"进水.*氨.*吸光"], 80),
    (
        "nh4_influent_mg_l",
        [r"nh4.*influent.*(conc|浓度|mg)", r"influent.*nh4", r"nh4.*influent", r"进水.*氨", r"氨氮.*进水"],
        75,
    ),
    ("reactor1_abs", [r"reactor\s*\(?1\)?.*(abs|吸光)", r"reactor.*1.*吸光"], 70),
    (
        "reactor1_effluent_mg_l",
        [
            r"r1\s*eff",
            r"reactor\s*\(?1\)?.*(conc|浓度|eff|出水)",
            r"reactor\s*\(?1\)?",
            r"反应器\s*1",
            r"1号",
        ],
        65,
    ),
    ("reactor2_abs", [r"reactor\s*\(?2\)?.*(abs|吸光)", r"^2\s*吸光", r"reactor.*2.*吸光"], 70),
    (
        "reactor2_effluent_mg_l",
        [
            r"r2\s*eff",
            r"reactor\s*\(?2\)?.*(conc|浓度|eff)",
            r"^2\s*浓度",
            r"反应器\s*2",
            r"2号",
            r"\b2\b.*浓度",
        ],
        65,
    ),
    ("removal_rate_r1_pct", [r"removal.*1", r"去除率.*1", r"removal rate\s*\(?1"], 60),
    ("removal_rate_r2_pct", [r"removal.*2", r"去除率.*2", r"removal rate\s*\(?2", r"^2\.0"], 55),
    ("hrt", [r"\bhrt\b", r"水力停留", r"停留时间"], 50),
    ("loading_influent_g_n_l_d", [r"进水负荷", r"influent.*load", r"load.*influent", r"g-n/l/d"], 50),
    ("loading_r1_g_n_l_d", [r"reactor.*1.*负荷", r"实际处理负荷.*1"], 45),
    ("loading_r2_g_n_l_d", [r"reactor.*2.*负荷", r"实际处理负荷.*2"], 45),
    ("anr_r1_g_n_l_d", [r"anr.*1", r"anr.*（1", r"anr.*1"], 45),
    ("anr_r2_g_n_l_d", [r"anr.*2", r"anr.*（2", r"anr.*2"], 45),
    ("tn_influent_mg_l", [r"tn.*influent", r"总氮.*进水", r"tn concentration.*influent"], 55),
    ("tn_effluent_r1_mg_l", [r"tn.*effluent.*1", r"effluent\s*\(?1\)?", r"tn.*出水.*1"], 50),
    ("tn_effluent_r2_mg_l", [r"tn.*effluent.*2", r"^\(2\)", r"tn.*2"], 48),
    ("tn_removal_r1_pct", [r"tn removal.*1", r"tn.*去除.*1", r"effiency.*1", r"efficiency.*1"], 45),
    ("tn_removal_r2_pct", [r"tn removal.*2", r"tn.*去除.*2", r"effiency.*2", r"^\(2\).*removal"], 43),
    ("ph", [r"\bph\b", r"酸碱度"], 40),
    ("temperature_c", [r"temp", r"temperature", r"温度", r"℃"], 40),
    ("do_mg_l", [r"\bdo\b", r"dissolved oxygen", r"溶解氧"], 40),
    ("no2_effluent_mg_l", [r"no2", r"亚硝", r"nitrite"], 40),
    ("no3_effluent_mg_l", [r"no3", r"硝", r"nitrate"], 40),
]

# Standard 22-column template positions (fallback when headers are sparse).
POSITION_FALLBACK: dict[int, str] = {
    0: "date",
    1: "duration_days",
    2: "nh4_influent_abs",
    3: "nh4_influent_mg_l",
    4: "reactor1_abs",
    5: "reactor1_effluent_mg_l",
    6: "reactor2_abs",
    7: "reactor2_effluent_mg_l",
    8: "removal_rate_r1_pct",
    9: "removal_rate_r2_pct",
    10: "hrt",
    11: "loading_influent_g_n_l_d",
    12: "loading_r1_g_n_l_d",
    13: "loading_r2_g_n_l_d",
    14: "anr_r1_g_n_l_d",
    15: "anr_r2_g_n_l_d",
    17: "tn_influent_mg_l",
    18: "tn_effluent_r1_mg_l",
    19: "tn_effluent_r2_mg_l",
    20: "tn_removal_r1_pct",
    21: "tn_removal_r2_pct",
}


@dataclass
class SchemaReport:
    header_rows: list[int]
    data_start_row: int
    column_labels: list[str]
    mapped_fields: dict[str, int]
    detected_fields: list[str]
    missing_fields: list[str]
    warnings: list[str] = field(default_factory=list)

    @property
    def is_usable(self) -> bool:
        has_time = "date" in self.mapped_fields or "duration_days" in self.mapped_fields
        has_nh4 = "nh4_influent_mg_l" in self.mapped_fields or "reactor1_effluent_mg_l" in self.mapped_fields
        return has_time and has_nh4


def _normalize_label(text: str) -> str:
    return re.sub(r"\s+", " ", str(text).strip().lower())


def _combine_header(raw: pd.DataFrame, col_idx: int, header_rows: list[int]) -> str:
    parts: list[str] = []
    for row_idx in header_rows:
        if row_idx >= len(raw):
            continue
        val = raw.iloc[row_idx, col_idx]
        if pd.notna(val) and str(val).strip():
            parts.append(str(val).strip())
    return _normalize_label(" ".join(parts))


def _score_field(label: str, patterns: list[str]) -> float:
    if not label:
        return 0.0
    score = 0.0
    for pattern in patterns:
        if re.search(pattern, label, re.IGNORECASE):
            score += 10.0
            if label == pattern.strip("^$"):
                score += 5.0
    if "abs" in label or "吸光" in label:
        if "mg" in label or "浓度" in label or "conc" in label:
            score -= 5.0
    if ("conc" in label or "浓度" in label or "mg" in label) and "abs" not in label and "吸光" not in label:
        score += 2.0
    return score


def _guess_header_layout(raw: pd.DataFrame) -> tuple[list[int], int]:
    """Return header row indices and first data row index."""
    if len(raw) < 2:
        return [0], 1

    row2_first = raw.iloc[2, 0] if len(raw) > 2 else None
    if _looks_like_date(row2_first):
        return [0, 1], 2

    row1_first = raw.iloc[1, 0]
    if _looks_like_date(row1_first):
        return [0], 1

    row0_first = raw.iloc[0, 0]
    if _looks_like_date(row0_first):
        return [], 0

    return [0, 1], 2


def _looks_like_date(value) -> bool:
    if pd.isna(value):
        return False
    try:
        pd.to_datetime(value)
        return True
    except (TypeError, ValueError):
        return False


def detect_schema(raw: pd.DataFrame) -> SchemaReport:
    header_rows, data_start = _guess_header_layout(raw)
    n_cols = raw.shape[1]
    labels = [_combine_header(raw, c, header_rows) if header_rows else _normalize_label(raw.iloc[0, c]) for c in range(n_cols)]

    candidates: list[tuple[float, int, str, int]] = []
    for col_idx, label in enumerate(labels):
        for field, patterns, priority in FIELD_RULES:
            score = _score_field(label, patterns)
            if score > 0:
                candidates.append((score + priority * 0.1, col_idx, field, priority))

    candidates.sort(key=lambda x: (-x[0], -x[3], x[1]))

    mapped: dict[str, int] = {}
    used_cols: set[int] = set()

    for _score, col_idx, field, _priority in candidates:
        if field in mapped or col_idx in used_cols:
            continue
        if field.endswith("_mg_l") and "abs" in labels[col_idx] and "conc" not in labels[col_idx] and "浓度" not in labels[col_idx]:
            continue
        if field.endswith("_abs") and ("浓度" in labels[col_idx] or "conc" in labels[col_idx]):
            continue
        mapped[field] = col_idx
        used_cols.add(col_idx)

    warnings: list[str] = []
    if len(mapped) < 4 and n_cols >= 10:
        for col_idx, field in POSITION_FALLBACK.items():
            if col_idx >= n_cols or field in mapped:
                continue
            if col_idx in used_cols:
                continue
            label = labels[col_idx]
            if field == "date" and label and not re.search(r"\bdate\b|日期", label, re.I):
                continue
            if field.endswith("_abs") and label and re.search(r"eff|出水|effluent", label, re.I):
                continue
            mapped[field] = col_idx
            used_cols.add(col_idx)
            warnings.append(f"Used column position fallback for '{field}' (column {col_idx}).")

    detected = sorted(mapped.keys())
    optional_missing = [f for f in ALL_CANONICAL_FIELDS if f not in mapped]

    if "nh4_influent_mg_l" not in mapped and "reactor1_effluent_mg_l" not in mapped:
        warnings.append("No NH4 concentration column detected — check headers or upload the operation log template.")

    if "date" not in mapped and "duration_days" not in mapped:
        warnings.append("No date or duration column — charts may use row index.")

    return SchemaReport(
        header_rows=header_rows,
        data_start_row=data_start,
        column_labels=labels,
        mapped_fields=mapped,
        detected_fields=detected,
        missing_fields=optional_missing,
        warnings=warnings,
    )


def extract_dataframe(raw: pd.DataFrame, schema: SchemaReport) -> pd.DataFrame:
    data = raw.iloc[schema.data_start_row :].copy()
    rows: dict[str, list] = {field: [] for field in ALL_CANONICAL_FIELDS}

    for field in ALL_CANONICAL_FIELDS:
        if field in schema.mapped_fields:
            col_idx = schema.mapped_fields[field]
            rows[field] = data.iloc[:, col_idx].tolist()
        else:
            rows[field] = [None] * len(data)

    df = pd.DataFrame(rows)
    df = df.dropna(how="all").reset_index(drop=True)

    if "date" in schema.mapped_fields:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
    else:
        df["date"] = pd.NaT

    numeric_fields = [f for f in ALL_CANONICAL_FIELDS if f not in ("date",)]
    for col in numeric_fields:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    if schema.mapped_fields.get("date"):
        df = df[df["date"].notna() | df["duration_days"].notna()]
    elif schema.mapped_fields.get("duration_days"):
        df = df[df["duration_days"].notna()]
    else:
        df = df.dropna(how="all")

    if "duration_days" in schema.mapped_fields and df["duration_days"].notna().any():
        df = df.sort_values("duration_days", na_position="last").reset_index(drop=True)
    elif df["date"].notna().any():
        df = df.sort_values("date", na_position="last").reset_index(drop=True)
    else:
        df["row_index"] = range(len(df))

    return df
