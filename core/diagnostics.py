"""
Daily interpretation of NH4 / NO2 / NO3 readings.

Two ways to compare:
* "day-to-day" (today vs yesterday, same sampling point) — valid for BATCH / SBR cycles;
* "in-out" (influent vs effluent the same day) — the correct basis for CONTINUOUS reactors.

Stages: "pn" (two-stage partial nitritation), "anammox" (stage 2), "pna" (one-stage PN/A).
Quantitative rules use the Strous stoichiometry [1]:
  anammox stage : ΔNO3/ΔNH4 ≈ 0.26, ΔNO2/ΔNH4 ≈ 1.32
  one-stage PN/A: ΔNO3/ΔNH4 ≈ 0.11 (0.26 / 2.32)
"""

from dataclasses import dataclass, field

from core.constants import (
    ANAMMOX_NO2_PER_NH4,
    ANAMMOX_NO3_PER_NH4,
    PNA_NO2_EFFLUENT_ALARM,
    PNA_NO2_EFFLUENT_WARNING,
    PNA_NO3_PER_NH4_REMOVED,
    PNA_NO3_RATIO_ALARM,
    PNA_NO3_RATIO_WARNING,
    PNA_RESIDUAL_NH4_MIN,
)
from core.stoichiometry import check_anammox_feed

NOISE = 0.5  # mg N/L — changes smaller than this are treated as analytical noise


@dataclass
class DailyDiagnostics:
    stage: str
    status: str  # ok, warning, danger
    findings: list[str] = field(default_factory=list)
    actions: list[str] = field(default_factory=list)
    metrics: dict = field(default_factory=dict)


def _worse(a: str, b: str) -> str:
    order = {"ok": 0, "warning": 1, "danger": 2}
    return a if order[a] >= order[b] else b


def interpret_daily_reading(
    nh4_today: float,
    no2_today: float,
    no3_today: float,
    nh4_yesterday: float | None = None,
    no2_yesterday: float | None = None,
    no3_yesterday: float | None = None,
    stage: str = "pn",
) -> DailyDiagnostics:
    """
    "yesterday" values may equally be the INFLUENT values of the same day (in-out mode):
    the arithmetic is identical — Δ = reference − current for consumption.
    """
    findings: list[str] = []
    actions: list[str] = []
    status = "ok"
    metrics: dict = {}

    d_nh4 = None if nh4_yesterday is None else nh4_today - nh4_yesterday
    d_no2 = None if no2_yesterday is None else no2_today - no2_yesterday
    d_no3 = None if no3_yesterday is None else no3_today - no3_yesterday
    nh4_removed = None if d_nh4 is None else -d_nh4

    if stage == "pn":
        if d_nh4 is not None and d_nh4 < -NOISE:
            findings.append("NH₄ decreased — AOB are oxidising ammonium.")
        if d_no2 is not None and d_no2 > NOISE:
            findings.append("NO₂ accumulates — nitritation is working.")
        if d_no3 is not None and d_no3 > NOISE and nh4_removed and nh4_removed > NOISE:
            nar_prod = (d_no2 or 0) / max((d_no2 or 0) + d_no3, 1e-9)
            metrics["NO2 share of oxidised N"] = nar_prod
            if nar_prod < 0.8:
                findings.append(f"Only {nar_prod:.0%} of oxidised N stays as NO₂ — NOB are active.")
                actions.append("Lower DO, keep T ≥ 30 °C with short SRT, or raise FA (pH) to suppress NOB.")
                status = "danger"
            else:
                findings.append(f"{nar_prod:.0%} of oxidised N remains as NO₂ — NOB largely suppressed.")
        elif d_no3 is not None and d_no3 > NOISE:
            findings.append("NO₃ rises without NH₄ removal — NOB oxidising existing NO₂.")
            actions.append("Review NOB suppression (DO, SRT, FA/FNA).")
            status = "danger"
        feed = check_anammox_feed(nh4_today, no2_today, no3_today)
        metrics["NO2/NH4"] = feed.no2_nh4_ratio
        if feed.ready_for_anammox:
            findings.append("Effluent NO₂/NH₄ is close to 1.32 — suitable anammox feed.")
        elif nh4_today > 0 or no2_today > 0:
            findings.append(f"Effluent NO₂/NH₄ = {feed.no2_nh4_ratio:.2f} (anammox feed target 1.32).")

    elif stage == "anammox":
        if nh4_removed is not None and nh4_removed > NOISE:
            if d_no2 is not None:
                r_no2 = -d_no2 / nh4_removed
                metrics["ΔNO2/ΔNH4"] = r_no2
                findings.append(f"ΔNO₂/ΔNH₄ = {r_no2:.2f} (anammox ≈ {ANAMMOX_NO2_PER_NH4}).")
                if r_no2 < 0.9:
                    findings.append("Less NO₂ consumed than anammox needs — NH₄ removal by another route (AOB?) or data error.")
                    status = _worse(status, "warning")
                elif r_no2 > 1.8:
                    findings.append("More NO₂ consumed than anammox needs — denitrification or NOB may be consuming NO₂.")
                    status = _worse(status, "warning")
            if d_no3 is not None:
                r_no3 = d_no3 / nh4_removed
                metrics["ΔNO3/ΔNH4"] = r_no3
                findings.append(f"ΔNO₃/ΔNH₄ = {r_no3:.2f} (anammox ≈ {ANAMMOX_NO3_PER_NH4}).")
                if r_no3 > ANAMMOX_NO3_PER_NH4 * 1.5:
                    findings.append("NO₃ production exceeds the anammox stoichiometry — NOB activity likely.")
                    actions.append("Keep DO < 0.2 mg/L in the anammox reactor; check for air leaks.")
                    status = "danger"
                elif r_no3 < ANAMMOX_NO3_PER_NH4 * 0.5:
                    findings.append("NO₃ production lower than stoichiometry — possible heterotrophic denitrification (COD present).")
        elif d_no3 is not None and d_no3 > NOISE:
            findings.append("NO₃ rises without NH₄ removal — possible NOB interference.")
            actions.append("Keep DO below 0.2 mg/L in the anammox reactor.")
            status = "danger"
        if no2_today > PNA_NO2_EFFLUENT_ALARM:
            findings.append(f"NO₂ = {no2_today:.0f} mg N/L — risk of nitrite inhibition of anammox.")
            actions.append("Reduce nitrite load (NLR) until activity recovers.")
            status = _worse(status, "warning")

    else:  # one-stage PN/A
        if nh4_removed is not None and nh4_removed > NOISE and d_no3 is not None:
            r = d_no3 / nh4_removed
            metrics["ΔNO3/ΔNH4"] = r
            findings.append(f"ΔNO₃/ΔNH₄ = {r:.3f} (theory ≈ {PNA_NO3_PER_NH4_REMOVED:.2f}).")
            if r >= PNA_NO3_RATIO_ALARM:
                findings.append("NOB proliferation — nitrate production far above anammox stoichiometry.")
                actions.append("Lower DO set-point / shorten aerobic phase; keep residual NH₄; consider washing out flocs (NOB).")
                status = "danger"
            elif r >= PNA_NO3_RATIO_WARNING:
                findings.append("Early sign of NOB activity.")
                actions.append("Reduce DO set-point by ~0.05–0.1 mg/L and re-check in 1–2 days.")
                status = _worse(status, "warning")
            elif r < 0.05:
                findings.append("Very low NO₃ production — heterotrophic denitrification may contribute (check COD).")
        if no2_today >= PNA_NO2_EFFLUENT_ALARM:
            findings.append(f"Effluent NO₂ = {no2_today:.0f} mg N/L — anammox cannot keep up (inhibition risk).")
            actions.append("Reduce aeration (less nitritation) and check anammox activity/temperature.")
            status = "danger"
        elif no2_today >= PNA_NO2_EFFLUENT_WARNING:
            findings.append(f"Effluent NO₂ = {no2_today:.0f} mg N/L — nitritation exceeds anammox capacity.")
            actions.append("Slightly reduce aeration or load.")
            status = _worse(status, "warning")
        if nh4_today < PNA_RESIDUAL_NH4_MIN:
            findings.append("Residual NH₄ is very low — over-aeration favours NOB.")
            status = _worse(status, "warning")

    if not findings:
        findings.append("No significant change detected (Δ < 0.5 mg N/L).")
    if not actions and status == "ok":
        actions.append("Maintain current operating conditions.")

    return DailyDiagnostics(stage=stage, status=status, findings=findings,
                            actions=list(dict.fromkeys(actions)), metrics=metrics)
