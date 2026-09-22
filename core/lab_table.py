"""
Lab notebook table — fixed format matching paper log.

Each row (pH, NO3, NO2, NH4) has three measured values:
  Distilled water | Entrance water | Reactor

Multi-column analysis compares all sample points; kinetic simulation uses the Reactor column.
"""

import json
from dataclasses import dataclass, field

from core.constants import get_literature_default, get_literature_reference

SAMPLE_COLUMNS = {
    "distilled": "Distilled water",
    "entrance": "Entrance water",
    "reactor": "Reactor",
}

NOTEBOOK_PARAMETERS = ["ph", "no3", "no2", "nh4"]

PARAMETER_LABELS = {
    "ph": "pH",
    "no3": "NO3-N (mg/L)",
    "no2": "NO2-N (mg/L)",
    "nh4": "NH4-N (mg/L)",
}

DEFAULT_TABLE = {
    "ph": {"distilled": 7.0, "entrance": 7.5, "reactor": 7.8},
    "no3": {"distilled": 0.0, "entrance": 5.0, "reactor": 2.0},
    "no2": {"distilled": 0.0, "entrance": 0.0, "reactor": 30.0},
    "nh4": {"distilled": 0.0, "entrance": 100.0, "reactor": 50.0},
}

DEFAULT_SIM_COLUMN = "reactor"


@dataclass
class SimulationInputs:
    nh4: float
    no2: float
    no3: float
    ph: float
    temperature: float
    do: float
    srt: float
    biomass: float
    hco3: float
    sim_column: str
    operating_custom: dict = field(default_factory=dict)


def default_table() -> dict:
    return {p: dict(DEFAULT_TABLE[p]) for p in NOTEBOOK_PARAMETERS}


def extract_column(table: dict, column: str) -> dict:
    """All notebook parameters from one sample point."""
    return {p: float(table[p][column]) for p in NOTEBOOK_PARAMETERS}


def resolve_operating_param(stage: str, param: str, use_custom: bool, custom_value: float) -> tuple[float, str]:
    if use_custom:
        return float(custom_value), "User input"
    default = get_literature_default(stage, param)
    ref = get_literature_reference(stage, param)
    return default, ref


def build_simulation_inputs(
    table: dict,
    sim_column: str,
    stage: str,
    use_custom: dict,
    custom_values: dict,
) -> SimulationInputs:
    col_values = extract_column(table, sim_column)
    operating_custom = {}

    temperature, _ = resolve_operating_param(
        stage, "temperature", use_custom.get("temperature", False), custom_values.get("temperature", 35)
    )
    do, _ = resolve_operating_param(stage, "do", use_custom.get("do", False), custom_values.get("do", 0.8))
    srt, _ = resolve_operating_param(stage, "srt", use_custom.get("srt", False), custom_values.get("srt", 4))
    biomass, _ = resolve_operating_param(
        stage, "biomass", use_custom.get("biomass", False), custom_values.get("biomass", 200)
    )
    hco3, _ = resolve_operating_param(stage, "hco3", use_custom.get("hco3", False), custom_values.get("hco3", 120))

    for key in ["temperature", "do", "srt", "biomass", "hco3"]:
        operating_custom[key] = use_custom.get(key, False)

    return SimulationInputs(
        nh4=col_values["nh4"],
        no2=col_values["no2"],
        no3=col_values["no3"],
        ph=col_values["ph"],
        temperature=temperature,
        do=do,
        srt=srt,
        biomass=biomass,
        hco3=hco3 if stage == "anammox" else 0.0,
        sim_column=sim_column,
        operating_custom=operating_custom,
    )


def notebook_editor_column_config():
    """Streamlit data_editor columns — allow any lab-scale concentration/pH precision."""
    import streamlit as st

    value_col = st.column_config.NumberColumn(
        format="%.6g",
        step=1e-9,
        min_value=-1e9,
        max_value=1e9,
    )
    return {
        "Parameter": st.column_config.TextColumn(disabled=True),
        "param_key": None,
        "Distilled water": value_col,
        "Entrance water": value_col,
        "Reactor": value_col,
    }


def table_to_dataframe(table: dict):
    import pandas as pd

    rows = []
    for param in NOTEBOOK_PARAMETERS:
        rows.append({
            "Parameter": PARAMETER_LABELS[param],
            "param_key": param,
            "Distilled water": table[param]["distilled"],
            "Entrance water": table[param]["entrance"],
            "Reactor": table[param]["reactor"],
        })
    return pd.DataFrame(rows)


def dataframe_to_table(df) -> dict:
    table = default_table()
    for _, row in df.iterrows():
        key = row["param_key"]
        if key not in table:
            continue
        table[key]["distilled"] = float(row["Distilled water"])
        table[key]["entrance"] = float(row["Entrance water"])
        table[key]["reactor"] = float(row["Reactor"])
    return table


def table_to_json(table: dict) -> str:
    return json.dumps(table)


def table_from_json(raw: str | None) -> dict:
    if not raw:
        return default_table()
    try:
        data = json.loads(raw)
        table = default_table()
        for param in NOTEBOOK_PARAMETERS:
            for col in SAMPLE_COLUMNS:
                if param in data and col in data[param]:
                    table[param][col] = float(data[param][col])
        return table
    except (json.JSONDecodeError, TypeError, ValueError):
        return default_table()


def sim_column_from_json(raw: str | None) -> str:
    if not raw:
        return DEFAULT_SIM_COLUMN
    try:
        data = json.loads(raw)
        if isinstance(data, str):
            return data if data in SAMPLE_COLUMNS else DEFAULT_SIM_COLUMN
        if isinstance(data, dict) and "sim_column" in data:
            col = data["sim_column"]
            return col if col in SAMPLE_COLUMNS else DEFAULT_SIM_COLUMN
    except (json.JSONDecodeError, TypeError):
        pass
    return DEFAULT_SIM_COLUMN


def sim_column_to_json(column: str) -> str:
    return json.dumps({"sim_column": column})


def selected_columns_to_json(columns: list[str]) -> str:
    valid = [c for c in columns if c in SAMPLE_COLUMNS]
    return json.dumps({"selected_columns": valid or list(SAMPLE_COLUMNS.keys())})


def selected_columns_from_json(raw: str | None) -> list[str]:
    if not raw:
        return list(SAMPLE_COLUMNS.keys())
    try:
        data = json.loads(raw)
        if isinstance(data, dict):
            if "selected_columns" in data:
                cols = [c for c in data["selected_columns"] if c in SAMPLE_COLUMNS]
                return cols or list(SAMPLE_COLUMNS.keys())
            if "sim_column" in data:
                return list(SAMPLE_COLUMNS.keys())
    except (json.JSONDecodeError, TypeError):
        pass
    return list(SAMPLE_COLUMNS.keys())
