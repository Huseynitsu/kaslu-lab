"""Per-chart analytics — human-readable text for operation log recommendations."""

from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

from core.i18n import bilingual
from core.operation_log import OperationLogResult

FIELD_LABELS = {
    "nh4_influent_mg_l": ("NH₄ influent", "NH₄ 进水"),
    "reactor1_effluent_mg_l": ("Reactor (1) effluent", "反应器 (1) 出水"),
    "reactor2_effluent_mg_l": ("Reactor (2) effluent", "反应器 (2) 出水"),
    "tn_influent_mg_l": ("TN influent", "TN 进水"),
    "tn_effluent_r1_mg_l": ("TN effluent R1", "TN 出水 R1"),
    "tn_effluent_r2_mg_l": ("TN effluent R2", "TN 出水 R2"),
    "loading_influent_g_n_l_d": ("Influent loading", "进水负荷"),
    "anr_r1_g_n_l_d": ("ANR Reactor 1", "R1 ANR"),
    "anr_r2_g_n_l_d": ("ANR Reactor 2", "R2 ANR"),
}


@dataclass
class MetricHighlight:
    label: str
    value: str
    caption: str


@dataclass
class SectionAdvice:
    section_id: str
    title: str
    summary: str
    highlights: list[MetricHighlight] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)

    @property
    def analysis(self) -> str:
        """Backward compatibility for AI prompt builder."""
        parts = [self.summary]
        for h in self.highlights:
            parts.append(f"{h.label}: {h.value} ({h.caption})")
        return " ".join(parts)


def _L(en: str, zh: str) -> str:
    return bilingual(en, zh)


def _label(field: str) -> str:
    pair = FIELD_LABELS.get(field, (field.replace("_", " ").title(), field))
    return bilingual(pair[0], pair[1])


def _trend_code(series: pd.Series) -> str:
    s = series.dropna()
    if len(s) < 2:
        return "unknown"
    delta = float(s.iloc[-1] - s.iloc[0])
    if abs(delta) < 0.05 * max(abs(float(s.mean())), 1.0):
        return "stable"
    return "up" if delta > 0 else "down"


def _trend_en(code: str) -> str:
    return {
        "up": "increasing",
        "down": "decreasing",
        "stable": "stable",
        "unknown": "n/a",
    }.get(code, code)


def _trend_zh(code: str) -> str:
    return {
        "up": "上升",
        "down": "下降",
        "stable": "稳定",
        "unknown": "无",
    }.get(code, code)


def _trend_word(code: str) -> str:
    return _L(_trend_en(code), _trend_zh(code))


def _trend_arrow(code: str) -> str:
    return {"up": "↑", "down": "↓", "stable": "→", "unknown": "—"}.get(code, "—")


def _stats(series: pd.Series) -> dict | None:
    s = series.dropna()
    if s.empty:
        return None
    code = _trend_code(s)
    return {
        "min": float(s.min()),
        "max": float(s.max()),
        "mean": float(s.mean()),
        "latest": float(s.iloc[-1]),
        "trend_code": code,
        "trend": _trend_word(code),
        "arrow": _trend_arrow(code),
    }


def _stat_caption(st: dict, *, decimals: int = 1, unit_suffix: str = "") -> str:
    d = decimals
    suf = unit_suffix
    return _L(
        f"avg {st['mean']:.{d}f}{suf} · range {st['min']:.{d}f}–{st['max']:.{d}f}{suf} · {st['arrow']} {_trend_en(st['trend_code'])}",
        f"平均 {st['mean']:.{d}f}{suf} · 范围 {st['min']:.{d}f}–{st['max']:.{d}f}{suf} · {st['arrow']} {_trend_zh(st['trend_code'])}",
    )


def _metric(field: str, st: dict, *, unit: str = "mg/L", decimals: int = 1) -> MetricHighlight:
    fmt = f"{{:.{decimals}f}}"
    return MetricHighlight(
        label=_label(field),
        value=f"{fmt.format(st['latest'])} {unit}",
        caption=_stat_caption(st, decimals=decimals),
    )


def build_section_analyses(
    result: OperationLogResult,
    *,
    fa_ph: float = 7.5,
    fa_temp: float = 35.0,
) -> list[SectionAdvice]:
    df = result.df
    schema = result.schema
    summary = result.summary
    sections: list[SectionAdvice] = []

    nh4_cols = [c for c in ("nh4_influent_mg_l", "reactor1_effluent_mg_l", "reactor2_effluent_mg_l") if c in schema.detected_fields]
    if nh4_cols:
        highlights = []
        recs = []
        inf_st = r1_st = r2_st = None
        if "nh4_influent_mg_l" in nh4_cols:
            inf_st = _stats(df["nh4_influent_mg_l"])
            if inf_st:
                highlights.append(_metric("nh4_influent_mg_l", inf_st))
        if "reactor1_effluent_mg_l" in nh4_cols:
            r1_st = _stats(df["reactor1_effluent_mg_l"])
            if r1_st:
                highlights.append(_metric("reactor1_effluent_mg_l", r1_st))
        if "reactor2_effluent_mg_l" in nh4_cols:
            r2_st = _stats(df["reactor2_effluent_mg_l"])
            if r2_st:
                highlights.append(_metric("reactor2_effluent_mg_l", r2_st))

        summary_text = _L(
            "This chart tracks ammonium across influent and both reactor effluents over reactor operating time.",
            "本图反映进水与两个反应器出水的氨氮浓度随运行时间的变化。",
        )
        if inf_st and r1_st:
            if r1_st["trend_code"] == "up":
                summary_text += " " + _L(
                    f"Influent NH₄ is {_trend_en(inf_st['trend_code'])} while Reactor (1) effluent is {_trend_en(r1_st['trend_code'])} — "
                    f"latest removal gap is {inf_st['latest'] - r1_st['latest']:.0f} mg/L (historical avg gap ~{inf_st['mean'] - r1_st['mean']:.0f} mg/L).",
                    f"进水 NH₄ {_trend_zh(inf_st['trend_code'])}，反应器 (1) 出水 {_trend_zh(r1_st['trend_code'])} — "
                    f"最新去除差值 {inf_st['latest'] - r1_st['latest']:.0f} mg/L（历史平均差值约 {inf_st['mean'] - r1_st['mean']:.0f} mg/L）。",
                )
                recs.append(
                    _L(
                        "Reactor (1) effluent NH₄ is rising — check DO, pH, temperature, biomass, and influent loading.",
                        "反应器 (1) 出水 NH₄ 上升 — 请检查 DO、pH、温度、生物量及进水负荷。",
                    )
                )
            else:
                summary_text += " " + _L(
                    "Effluent NH₄ trend is acceptable relative to influent.",
                    "相对进水而言，出水 NH₄ 趋势可接受。",
                )
                recs.append(
                    _L(
                        "Continue daily NH₄ logging for influent and both reactors.",
                        "请继续每日记录进水与两个反应器的 NH₄。",
                    )
                )
        sections.append(
            SectionAdvice(section_id="nh4", title=_L("NH₄ vs duration", "NH₄ 与运行时间"), summary=summary_text, highlights=highlights, recommendations=recs)
        )

    rem_cols = [c for c in ("removal_rate_r1_pct", "removal_rate_r2_pct") if c in df.columns and df[c].notna().any()]
    if rem_cols:
        highlights = []
        recs = []
        parts = []
        for col in rem_cols:
            st = _stats(df[col])
            if not st:
                continue
            if "r1" in col:
                label = _L("Reactor (1) removal", "反应器 (1) 去除率")
                name_en, name_zh = "Reactor (1)", "反应器 (1)"
            else:
                label = _L("Reactor (2) removal", "反应器 (2) 去除率")
                name_en, name_zh = "Reactor (2)", "反应器 (2)"
            highlights.append(
                MetricHighlight(
                    label=label,
                    value=f"{st['latest']:.1f} %",
                    caption=_stat_caption(st, decimals=1, unit_suffix="%"),
                )
            )
            parts.append(_L(f"{name_en}: {st['latest']:.1f}%", f"{name_zh}：{st['latest']:.1f}%"))
            if st["latest"] < 80:
                recs.append(
                    _L(
                        f"{name_en} latest removal is below 80% — review HRT, loading, and biomass health.",
                        f"{name_zh} 最新去除率低于 80% — 请检查 HRT、负荷和生物量状态。",
                    )
                )
        summary_text = _L(
            f"NH₄ removal efficiency over the log period. Latest values: {', '.join(parts)}.",
            f"日志期间的 NH₄ 去除效率。最新值：{', '.join(parts)}。",
        )
        if summary.removal_formula_max_error_pct is not None and summary.removal_formula_max_error_pct <= 0.01:
            summary_text += " " + _L(
                "Calculated removal matches the Excel formula (Influent − Effluent) / Influent.",
                "计算去除率与 Excel 公式 (进水−出水)/进水 一致。",
            )
        if not recs:
            recs.append(_L("Removal performance is within an acceptable range.", "去除性能处于可接受范围。"))
        sections.append(
            SectionAdvice(section_id="removal", title=_L("Removal rate", "去除率"), summary=summary_text, highlights=highlights, recommendations=recs)
        )

    tn_cols = [c for c in ("tn_influent_mg_l", "tn_effluent_r1_mg_l", "tn_effluent_r2_mg_l") if c in schema.detected_fields]
    if tn_cols:
        highlights = []
        recs = []
        for col in tn_cols:
            st = _stats(df[col])
            if st:
                highlights.append(_metric(col, st))
        summary_text = _L(
            "Total nitrogen (TN) includes all N forms — not only ammonium.",
            "总氮 (TN) 包含所有氮形态，不仅限于氨氮。",
        )
        if "tn_influent_mg_l" in schema.detected_fields and "nh4_influent_mg_l" in schema.detected_fields:
            diff = (df["tn_influent_mg_l"] - df["nh4_influent_mg_l"]).dropna()
            if not diff.empty:
                summary_text += " " + _L(
                    f"On average, TN influent exceeds NH₄ influent by {diff.mean():.0f} mg/L — nitrite/nitrate or organic N is present.",
                    f"平均而言 TN 进水比 NH₄ 进水高 {diff.mean():.0f} mg/L — 存在亚硝酸/硝酸或有机氮。",
                )
                recs.append(
                    _L(
                        "Add NO₂ and NO₃ measurements to explain the TN − NH₄ difference.",
                        "请补充 NO₂ 和 NO₃ 测量，以解释 TN 与 NH₄ 的差值。",
                    )
                )
        if "tn_removal_r1_pct" in df.columns and df["tn_removal_r1_pct"].notna().any():
            tr = _stats(df["tn_removal_r1_pct"])
            if tr:
                highlights.append(
                    MetricHighlight(
                        label=_L("TN removal R1", "R1 TN 去除率"),
                        value=f"{tr['latest']:.1f} %",
                        caption=_L(f"avg {tr['mean']:.1f}%", f"平均 {tr['mean']:.1f}%"),
                    )
                )
        if not recs:
            recs.append(_L("TN trends follow NH₄ removal — no major imbalance detected.", "TN 趋势与 NH₄ 去除一致 — 未发现明显失衡。"))
        sections.append(
            SectionAdvice(section_id="tn", title=_L("Total nitrogen (TN)", "总氮 TN"), summary=summary_text, highlights=highlights, recommendations=recs)
        )

    ops_cols = [c for c in ("anr_r1_g_n_l_d", "anr_r2_g_n_l_d", "loading_influent_g_n_l_d") if c in schema.detected_fields]
    if ops_cols:
        highlights = []
        recs = []
        for col in ops_cols:
            st = _stats(df[col])
            if st:
                highlights.append(_metric(col, st, unit="g-N/L/d", decimals=3))
        summary_parts = []
        if "hrt" in schema.detected_fields and df["hrt"].notna().any():
            hrt = float(df["hrt"].dropna().iloc[0])
            summary_parts.append(_L(f"HRT is logged as {hrt:.0f} h.", f"记录 HRT 为 {hrt:.0f} 小时。"))
        if "loading_influent_g_n_l_d" in ops_cols:
            ld = _stats(df["loading_influent_g_n_l_d"])
            if ld:
                summary_parts.append(
                    _L(
                        f"Influent nitrogen loading is {_trend_en(ld['trend_code'])} (latest {ld['latest']:.3f} g-N/L/d).",
                        f"进水氮负荷呈 {_trend_zh(ld['trend_code'])} 趋势（最新 {ld['latest']:.3f} g-N/L/d）。",
                    )
                )
        if "anr_r1_g_n_l_d" in ops_cols:
            anr = _stats(df["anr_r1_g_n_l_d"])
            if anr and anr["trend_code"] == "down":
                recs.append(
                    _L(
                        "ANR for Reactor (1) is declining — check biomass retention and activity.",
                        "反应器 (1) ANR 下降 — 请检查生物量滞留与活性。",
                    )
                )
        if not recs:
            recs.append(_L("Operating load and ANR are consistent with the logged HRT.", "运行负荷与 ANR 和记录的 HRT 一致。"))
        sections.append(
            SectionAdvice(
                section_id="ops",
                title=_L("ANR & loading", "ANR 与负荷"),
                summary=" ".join(summary_parts) or _L("Operating indicators from the lab log.", "来自实验日志的运行指标。"),
                highlights=highlights,
                recommendations=recs,
            )
        )

    if "reactor1_effluent_mg_l" in schema.detected_fields and "reactor2_effluent_mg_l" in schema.detected_fields:
        r1 = _stats(df["reactor1_effluent_mg_l"])
        r2 = _stats(df["reactor2_effluent_mg_l"])
        highlights = []
        recs = []
        summary_text = ""
        if r1 and r2:
            highlights = [
                MetricHighlight(_L("Latest R1 effluent", "R1 最新出水"), f"{r1['latest']:.1f} mg/L", _L(f"avg {r1['mean']:.1f}", f"平均 {r1['mean']:.1f}")),
                MetricHighlight(_L("Latest R2 effluent", "R2 最新出水"), f"{r2['latest']:.1f} mg/L", _L(f"avg {r2['mean']:.1f}", f"平均 {r2['mean']:.1f}")),
            ]
            summary_text = _L(
                f"Latest NH₄ effluent: Reactor (1) {r1['latest']:.1f} mg/L vs Reactor (2) {r2['latest']:.1f} mg/L.",
                f"最新 NH₄ 出水：反应器 (1) {r1['latest']:.1f} mg/L，反应器 (2) {r2['latest']:.1f} mg/L。",
            )
            if r2["latest"] > r1["latest"] * 1.1:
                recs.append(
                    _L(
                        "Reactor (2) shows higher NH₄ effluent — compare biomass age, mixing, and startup history.",
                        "反应器 (2) NH₄ 出水更高 — 请比较生物量龄、混合及启动历史。",
                    )
                )
            elif r1["latest"] > r2["latest"] * 1.1:
                recs.append(
                    _L(
                        "Reactor (1) shows higher NH₄ effluent — use Reactor (2) operation as reference if stable.",
                        "反应器 (1) NH₄ 出水更高 — 若 R2 稳定，可参考其运行方式。",
                    )
                )
            else:
                recs.append(_L("Both reactors perform similarly — parallel operation is balanced.", "两反应器性能接近 — 并行运行较均衡。"))
        sections.append(
            SectionAdvice(section_id="compare", title=_L("Reactor 1 vs 2", "反应器 1 vs 2"), summary=summary_text, highlights=highlights, recommendations=recs)
        )

    if "nh4_influent_mg_l" in schema.detected_fields:
        from core.chemistry import free_ammonia_mg_l

        fa_series = df["nh4_influent_mg_l"].apply(
            lambda v: free_ammonia_mg_l(v, fa_ph, fa_temp) if pd.notna(v) else None
        )
        fa = _stats(fa_series)
        highlights: list = []
        recs: list = []
        summary_text = _L(
            f"Free ammonia (FA, NH₃-N) from influent NH₄: FA = NH₄ / (1 + 10^(pKa − pH)), "
            f"pH {fa_ph}, {fa_temp} °C (sidebar).",
            f"由进水 NH₄ 估算游离氨 FA（NH₃-N）：FA = NH₄ / (1 + 10^(pKa − pH))，"
            f"侧边栏 pH {fa_ph}、{fa_temp} °C。",
        )
        if fa:
            highlights.append(
                MetricHighlight(
                    label=_L("FA (estimated)", "FA（估算）"),
                    value=f"{fa['latest']:.3f} mg/L",
                    caption=_stat_caption(fa, decimals=3),
                )
            )
            if fa["latest"] >= 1.0:
                summary_text += " " + _L(
                    "FA is high enough to inhibit NOB more than AOB during partial nitritation.",
                    "FA 足够高，在部分亚硝化阶段可更强烈抑制 NOB。",
                )
                recs.append(_L("Verify pH control strategy with measured pH in the Excel log.", "请在 Excel 中加入实测 pH 并验证 pH 控制策略。"))
            else:
                recs.append(_L("Consider raising pH if NOB activity is observed.", "若观察到 NOB 活性，可考虑提高 pH。"))
            recs.append(_L("Add measured pH and temperature columns for accurate FA.", "请添加实测 pH 和温度列以获得准确 FA。"))
            sections.append(
                SectionAdvice(
                    section_id="fa",
                    title=_L("Free ammonia (FA)", "游离氨 (FA)"),
                    summary=summary_text,
                    highlights=highlights,
                    recommendations=recs,
                )
            )

    if "no2_effluent_mg_l" in schema.detected_fields and df["no2_effluent_mg_l"].notna().any():
        from core.chemistry import free_nitrous_acid_mg_l

        fna_series = df["no2_effluent_mg_l"].apply(
            lambda v: free_nitrous_acid_mg_l(v, fa_ph, fa_temp) if pd.notna(v) else None
        )
        fna = _stats(fna_series)
        highlights = []
        recs = []
        summary_text = _L(
            f"Free nitrous acid (FNA, HNO₂-N) from NO₂ effluent: FNA = NO₂ / (1 + 10^(pH − pKa)), "
            f"pH {fa_ph}, {fa_temp} °C (sidebar).",
            f"由 NO₂ 出水估算游离亚硝酸 FNA（HNO₂-N）：FNA = NO₂ / (1 + 10^(pH − pKa))，"
            f"侧边栏 pH {fa_ph}、{fa_temp} °C。",
        )
        if fna:
            highlights.append(
                MetricHighlight(
                    label=_L("FNA (estimated)", "FNA（估算）"),
                    value=f"{fna['latest']:.4f} mg/L",
                    caption=_stat_caption(fna, decimals=4),
                )
            )
            if fna["latest"] >= 0.02:
                summary_text += " " + _L(
                    "FNA may inhibit AOB at this level — review pH and nitrite control.",
                    "当前 FNA 可能抑制 AOB — 请检查 pH 与亚硝酸盐控制。",
                )
                recs.append(_L("Lower pH or nitrite if AOB activity drops.", "若 AOB 活性下降，请考虑降低 pH 或 NO₂。"))
            elif fna["latest"] >= 0.001:
                recs.append(
                    _L(
                        "Monitor FNA if NO₂ accumulates during partial nitritation.",
                        "若 NO₂ 在部分亚硝化中积累，请持续监控 FNA。",
                    )
                )
            else:
                recs.append(_L("FNA is low — typical for stable AOB activity at this pH.", "FNA 较低 — 在此 pH 下 AOB 通常较稳定。"))
            recs.append(_L("Add measured pH and temperature columns for accurate FNA.", "请添加实测 pH 和温度列以获得准确 FNA。"))
            sections.append(
                SectionAdvice(
                    section_id="fna",
                    title=_L("Free nitrous acid (FNA)", "游离亚硝酸 (FNA)"),
                    summary=summary_text,
                    highlights=highlights,
                    recommendations=recs,
                )
            )

    return sections
