"""Tests for flexible operation log parsing and bilingual UI labels."""

from __future__ import annotations

import io

import pandas as pd
import pytest

from core.ai_recommendations import get_detailed_recommendations
from core.i18n import bilingual, t
from core.operation_log import load_default_sample_path, parse_default_sample, parse_operation_log, removal_rate_pct
from core.operation_log_advisor import build_rule_based_recommendations
from core.operation_log_schema import detect_schema


def parse_operation_log_from_df(raw: pd.DataFrame, *, source_name: str = "test"):
    buf = io.BytesIO()
    raw.to_excel(buf, index=False, header=False)
    buf.seek(0)
    return parse_operation_log(buf, source_name=source_name)


EXCEL_FORMAT_FIXTURES: list[tuple[str, pd.DataFrame, list[str]]] = [
    (
        "english_two_row_header",
        pd.DataFrame(
            [
                ["Date", "Duration", "NH4 Influent conc", "Reactor(1) effluent", "Reactor(2) effluent"],
                ["", "days", "mg/L", "mg/L", "mg/L"],
                ["2026-01-01", 10, 100, 20, 18],
                ["2026-01-02", 11, 110, 25, 22],
            ]
        ),
        ["nh4_influent_mg_l", "reactor1_effluent_mg_l"],
    ),
    (
        "chinese_headers",
        pd.DataFrame(
            [
                ["日期", "天数", "进水氨氮浓度", "反应器1出水", "反应器2出水"],
                ["", "天", "mg/L", "mg/L", "mg/L"],
                ["2026-01-01", 100, 500, 50, 45],
                ["2026-01-02", 101, 520, 48, 42],
            ]
        ),
        ["duration_days", "nh4_influent_mg_l"],
    ),
    (
        "duration_only_no_date",
        pd.DataFrame(
            [
                ["Duration days", "NH4 influent mg/L", "R1 effluent", "Removal rate (1)"],
                [50, 400, 40, 90],
                [51, 410, 42, 89],
            ]
        ),
        ["duration_days", "nh4_influent_mg_l"],
    ),
    (
        "single_row_header",
        pd.DataFrame(
            [
                ["Date", "Duration", "NH4 influent conc mg/L", "Reactor 1 effluent", "TN influent"],
                ["2026-03-01", 200, 600, 55, 610],
                ["2026-03-02", 201, 590, 52, 600],
            ]
        ),
        ["nh4_influent_mg_l", "tn_influent_mg_l"],
    ),
    (
        "abbreviated_r1_r2",
        pd.DataFrame(
            [
                ["Duration", "NH4 influent", "R1 effluent", "R2 effluent", "Influent loading"],
                ["days", "mg/L", "mg/L", "mg/L", "g-N/L/d"],
                [1, 300, 30, 28, 0.5],
                [2, 310, 32, 29, 0.52],
            ]
        ),
        ["nh4_influent_mg_l", "reactor1_effluent_mg_l"],
    ),
    (
        "mixed_en_zh_tn",
        pd.DataFrame(
            [
                ["Date", "Duration", "NH4 influent", "Reactor(1)", "Reactor(2)", "TN influent", "TN effluent R1"],
                ["", "days", "conc", "conc", "conc", "conc", "conc"],
                ["2026-04-01", 10, 450, 45, 40, 460, 50],
            ]
        ),
        ["tn_influent_mg_l", "tn_effluent_r1_mg_l"],
    ),
]


def test_removal_rate_formula():
    assert removal_rate_pct(100.0, 30.0) == pytest.approx(70.0)
    assert removal_rate_pct(0.0, 10.0) is None


def test_bilingual_ui_strings():
    duration = t("oplog.duration")
    assert "Duration" in duration
    assert "运行时间" in duration
    assert bilingual("Load data", "加载数据") == "Load data (加载数据)"
    assert "KASLU LAB" in t("brand.title")
    assert "卡琉实验室" in t("brand.title")


@pytest.mark.parametrize("format_name,raw,expected_fields", EXCEL_FORMAT_FIXTURES)
def test_parse_various_excel_formats(format_name, raw, expected_fields):
    schema = detect_schema(raw)
    assert schema.is_usable, f"{format_name}: schema not usable"
    result = parse_operation_log_from_df(raw, source_name=format_name)
    assert result.summary.row_count >= 1
    for field in expected_fields:
        assert field in result.schema.detected_fields, f"{format_name}: missing {field}"


@pytest.mark.parametrize("format_name,raw,expected_fields", EXCEL_FORMAT_FIXTURES)
def test_chart_and_advice_for_formats(format_name, raw, expected_fields):
    result = parse_operation_log_from_df(raw, source_name=format_name)
    from core.operation_log_charts import build_line_chart_df, resolve_x_axis

    x_col, x_label = resolve_x_axis(result.df, result.schema)
    assert x_col != "x_axis"
    assert "x_axis" not in x_label.lower()

    cols = [c for c in expected_fields if c in result.df.columns and c != "duration_days"]
    if cols:
        chart_df = build_line_chart_df(result.df, result.schema, cols[:2])
        assert chart_df.index.name != "x_axis"
        assert "x_axis" not in str(chart_df.columns)

    _used, sections, err = get_detailed_recommendations("rule_based", result)
    assert sections
    assert err is None


@pytest.mark.skipif(load_default_sample_path() is None, reason="Sample Excel not on Desktop")
def test_parse_default_sample():
    result = parse_default_sample()
    assert result is not None
    assert result.schema.is_usable
    assert result.summary.row_count >= 50
    assert "nh4_influent_mg_l" in result.schema.detected_fields
    assert result.summary.removal_formula_max_error_pct is not None
    assert result.summary.removal_formula_max_error_pct < 0.01


@pytest.mark.skipif(load_default_sample_path() is None, reason="Sample Excel not on Desktop")
def test_chart_labels_not_internal():
    from core.operation_log_charts import build_line_chart_df, resolve_x_axis

    result = parse_default_sample()
    assert result is not None
    x_col, x_label = resolve_x_axis(result.df, result.schema)
    assert x_col != "x_axis"
    assert "x_axis" not in x_label.lower()

    chart_df = build_line_chart_df(
        result.df,
        result.schema,
        ["nh4_influent_mg_l", "reactor1_effluent_mg_l"],
    )
    assert chart_df.index.name != "x_axis"
    assert "x_axis" not in str(chart_df.columns)
    assert "_" not in "".join(chart_df.columns)


@pytest.mark.skipif(load_default_sample_path() is None, reason="Sample Excel not on Desktop")
def test_rule_based_recommendations():
    result = parse_default_sample()
    assert result is not None
    items = build_rule_based_recommendations(result)
    assert len(items) >= 2


def test_partial_schema_minimal():
    raw = pd.DataFrame(
        [
            ["Date", "Duration", "NH4 Influent conc", "R1 eff"],
            ["", "days", "mg/L", "mg/L"],
            ["2026-01-01", 10, 100, 20],
            ["2026-01-02", 11, 110, 25],
        ]
    )
    schema = detect_schema(raw)
    assert schema.is_usable
    parse_operation_log_from_df(raw)


def test_builtin_ai_provider():
    raw = pd.DataFrame(
        [
            ["Date", "Duration", "NH4 influent", "Reactor(1)"],
            ["", "", "conc", "conc"],
            ["2026-01-01", 100, 500, 50],
        ]
    )
    result = parse_operation_log_from_df(raw)
    _used, sections, err = get_detailed_recommendations("rule_based", result)
    assert sections
    assert err is None


def test_advice_content_has_no_html_tags():
    raw = pd.DataFrame(
        [
            ["Date", "Duration", "NH4 influent", "Reactor(1)", "Reactor(2)"],
            ["", "days", "mg/L", "mg/L", "mg/L"],
            ["2026-01-01", 10, 500, 50, 45],
            ["2026-01-02", 11, 520, 48, 42],
        ]
    )
    result = parse_operation_log_from_df(raw)
    _used, sections, err = get_detailed_recommendations("rule_based", result)
    assert sections and err is None
    for sec in sections:
        assert "<div" not in sec.summary
        assert "<p" not in sec.summary
        for h in sec.highlights:
            assert "<" not in h.label
            assert "<" not in h.value
            assert "<" not in h.caption
        for rec in sec.recommendations:
            assert "<div" not in rec
