"""Scientific analysis for a single saved experiment."""

from dataclasses import dataclass, field

import pandas as pd

from core.constants import ANAMMOX_DO_MAX, PN_DO_MAX, PN_DO_MIN
from core.diagnostics import interpret_daily_reading
from core.lab_table import table_from_json, selected_columns_from_json, SAMPLE_COLUMNS
from core.pn_control import assess_pn_operation
from core.stoichiometry import check_anammox_feed, intrinsic_no3_note


@dataclass
class ExperimentAnalysis:
    experiment_id: int
    stage: str
    status: str
    summary: str
    findings: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    metrics: dict = field(default_factory=dict)


def analyze_experiment(row: pd.Series, timeseries: pd.DataFrame | None = None) -> ExperimentAnalysis:
    stage = str(row.get("stage", "anammox") or "anammox")
    exp_id = int(row["id"])

    nh4 = float(row["nh4"])
    no2 = float(row["no2"])
    no3_init = float(row.get("initial_no3", 0) or 0)
    ph = float(row["ph"])
    temp = float(row.get("temperature", 35))
    do = float(row["do"])
    srt = float(row["srt"])

    final_nh4 = float(row["final_nh4"])
    final_no2 = float(row["final_no2"])
    final_no3 = float(row["final_no3"])
    stability = float(row["stability"])

    findings = []
    recommendations = []
    status = "ok"

    lab_table = table_from_json(row.get("lab_table_json"))
    selected = selected_columns_from_json(row.get("sim_sources_json"))

    findings.append(
        "Experiment #%d (%s): multi-column analysis (%s); reactor NH4=%.1f, NO2=%.1f, NO3=%.1f, pH=%.2f"
        % (
            exp_id,
            stage.upper(),
            ", ".join(SAMPLE_COLUMNS.get(c, c) for c in selected),
            nh4,
            no2,
            no3_init,
            ph,
        )
    )

    if stage == "pn":
        assessment = assess_pn_operation(do, temp, ph, srt, nh4, no2)
        findings.extend([c.message for c in assessment.checks if c.status != "ok"])
        recommendations.extend(assessment.recommendations)
        status = assessment.overall_status

        if final_no3 > no3_init + 1.0 and (final_nh4 >= nh4 - 0.5):
            findings.append("Final NO₃ rose without strong NH₄ removal — check NOB activity.")
            status = "danger" if status == "ok" else status

        feed = check_anammox_feed(final_nh4, final_no2, final_no3)
        if feed.ready_for_anammox:
            findings.append(f"Effluent ratio NO₂/NH₄ = {feed.no2_nh4_ratio:.2f} — ready for Anammox stage.")
        else:
            findings.append(f"Effluent ratio NO₂/NH₄ = {feed.no2_nh4_ratio:.2f} (target 1.32).")

        summary = f"PN experiment — NOB risk: {assessment.nob_risk}, NAR/stability: {stability:.2f}"

    else:
        if do > ANAMMOX_DO_MAX:
            findings.append(f"DO ({do:.2f} mg/L) is high for Anammox — oxygen inhibits the process.")
            recommendations.append(f"Keep DO below {ANAMMOX_DO_MAX} mg/L.")
            status = "warning" if status == "ok" else status

        feed = check_anammox_feed(nh4, no2, no3_init, float(row.get("hco3", 120) or 120))
        findings.extend(feed.messages)

        nh4_removed = nh4 - final_nh4
        no2_removed = no2 - final_no2
        no3_gain = final_no3 - no3_init

        if nh4_removed > 0.5 and no2_removed > 0.5:
            expected_no3 = nh4_removed * 0.26
            if no3_gain <= expected_no3 * 1.5:
                findings.append(
                    f"NH₄ and NO₂ decreased; NO₃ gain ({no3_gain:.1f} mg/L) matches intrinsic Anammox (~{expected_no3:.1f})."
                )
            else:
                findings.append("NO₃ increase exceeds intrinsic Anammox level — possible NOB interference.")
                status = "danger"

        findings.append(intrinsic_no3_note())
        summary = f"Anammox experiment — stability index: {stability:.2f}"

        if stability < 0.5:
            recommendations.append("Improve NH₄:NO₂ ratio (1:1.32), biomass, or reduce DO.")
            status = "warning" if status == "ok" else status

    if timeseries is not None and len(timeseries) >= 2:
        first = timeseries.iloc[0]
        last = timeseries.iloc[-1]
        diag = interpret_daily_reading(
            nh4_today=float(last["nh4"]),
            no2_today=float(last["no2"]),
            no3_today=float(last["no3"]),
            nh4_yesterday=float(first["nh4"]),
            no2_yesterday=float(first["no2"]),
            no3_yesterday=float(first["no3"]),
            stage=stage,
        )
        findings.extend(diag.findings)
        recommendations.extend(diag.actions)
        if diag.status == "danger":
            status = "danger"
        elif diag.status == "warning" and status == "ok":
            status = "warning"

    if not recommendations:
        recommendations.append("Maintain current operating conditions for this experiment.")

    return ExperimentAnalysis(
        experiment_id=exp_id,
        stage=stage,
        status=status,
        summary=summary,
        findings=findings,
        recommendations=list(dict.fromkeys(recommendations)),
        metrics={
            "initial_nh4": nh4,
            "initial_no2": no2,
            "initial_no3": no3_init,
            "final_nh4": final_nh4,
            "final_no2": final_no2,
            "final_no3": final_no3,
            "stability": stability,
            "lab_table": lab_table,
        },
    )
