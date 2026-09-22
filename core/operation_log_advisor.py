"""Rule-based operation log recommendations (works without external API)."""

from __future__ import annotations

from core.i18n import bilingual
from core.operation_log import OperationLogResult


def _L(en: str, zh: str) -> str:
    return bilingual(en, zh)


def build_rule_based_recommendations(result: OperationLogResult) -> list[str]:
    df = result.df
    schema = result.schema
    summary = result.summary
    recs: list[str] = []

    if df.empty:
        return [_L("No data to analyze.", "没有可分析的数据。")]

    recs.append(
        _L(
            f"Parsed {summary.row_count} records from '{result.source_name}'. "
            f"Detected {len(schema.detected_fields)} column(s) automatically.",
            f"已从 '{result.source_name}' 解析 {summary.row_count} 条记录，"
            f"自动识别 {len(schema.detected_fields)} 列。",
        )
    )

    if summary.nh4_removal_r1_mean is not None:
        if summary.nh4_removal_r1_mean >= 85:
            recs.append(
                _L(
                    f"Reactor(1) mean NH₄ removal is strong ({summary.nh4_removal_r1_mean:.1f}%). Maintain current operation.",
                    f"反应器(1)平均 NH₄ 去除率良好（{summary.nh4_removal_r1_mean:.1f}%）。请保持当前运行条件。",
                )
            )
        elif summary.nh4_removal_r1_mean >= 70:
            recs.append(
                _L(
                    f"Reactor(1) mean removal is moderate ({summary.nh4_removal_r1_mean:.1f}%). "
                    "Check DO, pH, temperature and biomass activity.",
                    f"反应器(1)平均去除率中等（{summary.nh4_removal_r1_mean:.1f}%）。"
                    "请检查 DO、pH、温度和生物量活性。",
                )
            )
        else:
            recs.append(
                _L(
                    f"Reactor(1) mean removal is low ({summary.nh4_removal_r1_mean:.1f}%). "
                    "Priority: verify influent load, HRT, and possible inhibition.",
                    f"反应器(1)平均去除率偏低（{summary.nh4_removal_r1_mean:.1f}%）。"
                    "优先检查进水负荷、HRT 及可能的抑制因素。",
                )
            )

    if "reactor1_effluent_mg_l" in schema.mapped_fields and "reactor2_effluent_mg_l" in schema.mapped_fields:
        last = df.iloc[-1]
        r1 = last.get("reactor1_effluent_mg_l")
        r2 = last.get("reactor2_effluent_mg_l")
        if pd_notna(r1) and pd_notna(r2):
            if r2 > r1 * 1.1:
                recs.append(
                    _L(
                        "Latest Reactor(2) effluent is higher than Reactor(1) — compare biomass, mixing, or startup stage.",
                        "最新数据中反应器(2)出水高于反应器(1) — 请比较生物量、混合或启动阶段。",
                    )
                )
            elif r1 > r2 * 1.1:
                recs.append(
                    _L(
                        "Reactor(1) performs better than Reactor(2) on latest NH₄ effluent — use R1 as reference operation.",
                        "最新 NH₄ 出水上反应器(1)优于反应器(2) — 可参考 R1 的运行方式。",
                    )
                )

    if "tn_influent_mg_l" in schema.mapped_fields and "nh4_influent_mg_l" in schema.mapped_fields:
        recs.append(
            _L(
                "TN influent is higher than NH₄ alone — monitor nitrite/nitrate fractions when those columns are added.",
                "TN 进水高于 NH₄ — 添加亚硝酸/硝酸列后请监测各氮形态比例。",
            )
        )

    missing_ops = []
    if "ph" not in schema.mapped_fields:
        missing_ops.append(_L("pH", "pH"))
    if "temperature_c" not in schema.mapped_fields:
        missing_ops.append(_L("temperature", "温度"))
    if "do_mg_l" not in schema.mapped_fields:
        missing_ops.append(_L("DO", "DO"))
    if missing_ops:
        recs.append(
            _L(
                f"Add columns for {', '.join(missing_ops)} to enable FA/FNA and full self-control checks.",
                f"建议添加 {', '.join(missing_ops)} 列，以启用 FA/FNA 和完整自控检查。",
            )
        )

    if "no2_effluent_mg_l" not in schema.mapped_fields:
        recs.append(
            _L(
                "NO₂ data is not in this log — add NO₂ effluent for Anammox balance and FNA monitoring.",
                "日志中尚无 NO₂ 数据 — 请添加 NO₂ 出水列以进行 Anammox 平衡和 FNA 监控。",
            )
        )

    for alert in summary.alerts:
        if alert not in recs:
            recs.append(alert)

    if len(recs) == 1:
        recs.append(_L("Operation looks stable. Continue daily logging in Excel.", "运行较稳定。请继续在 Excel 中每日记录。"))

    return recs


def pd_notna(value) -> bool:
    try:
        import pandas as pd
        return pd.notna(value)
    except Exception:
        return value is not None
