from dataclasses import dataclass, field

from core.constants import ANAMMOX_NO3_PER_NH4
from core.stoichiometry import check_anammox_feed


@dataclass
class DailyDiagnostics:
    stage: str
    status: str  # ok, warning, danger
    findings: list[str] = field(default_factory=list)
    actions: list[str] = field(default_factory=list)


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
    Interpret lab data using article section 3.3 decision table.
    stage: 'pn' (partial nitritation) or 'anammox'
    """
    findings = []
    actions = []
    status = "ok"

    d_nh4 = None
    d_no2 = None
    d_no3 = None

    if nh4_yesterday is not None:
        d_nh4 = nh4_today - nh4_yesterday
    if no2_yesterday is not None:
        d_no2 = no2_today - no2_yesterday
    if no3_yesterday is not None:
        d_no3 = no3_today - no3_yesterday

    if stage == "pn":
        if d_nh4 is not None and d_nh4 < -0.5:
            findings.append("NH₄ is decreasing — AOB activity detected (PN is working).")

        if d_no2 is not None and d_no2 > 0.5:
            findings.append("NO₂ is accumulating — PN stage is running with NOB under control.")

        if d_no3 is not None and d_no3 > 0.5:
            if d_nh4 is not None and d_nh4 >= -0.5:
                findings.append("NO₃ is rising alone — NOB may be active (harmful to Anammox).")
                actions.append("Lower DO to 0.8 mg/L, reduce SRT to 3–5 days, keep pH at 7.5–8.0.")
                status = "danger"
            else:
                findings.append("NO₃ is rising, but NH₄ is also decreasing — mixed NOB + AOB activity.")

        if d_no2 is not None and d_no2 < -0.5 and d_no3 is not None and d_no3 > 0.5:
            findings.append("NO₂ is decreasing while NO₃ rises — NOB is oxidizing nitrite to nitrate.")
            actions.append("Review NOB suppression parameters (Table 1).")
            status = "danger"

        feed = check_anammox_feed(nh4_today, no2_today, no3_today)
        if feed.ready_for_anammox:
            findings.append("Effluent is close to ready for transfer to the Anammox stage.")
        elif nh4_today > 0 and no2_today > 0:
            findings.append(f"Anammox ratio: NO₂/NH₄ = {feed.no2_nh4_ratio:.2f} (ideal 1.32).")

    else:  # anammox stage
        if d_nh4 is not None and d_nh4 < -0.5 and d_no2 is not None and d_no2 < -0.5:
            if d_no3 is not None and d_no3 > 0.3:
                findings.append(
                    "NH₄ and NO₂ are decreasing while NO₃ rises — Anammox is active "
                    "(intrinsic NO₃ production, Strous equation)."
                )
            else:
                findings.append("NH₄ and NO₂ are decreasing — Anammox reaction is proceeding.")

        if d_no3 is not None and d_no3 > 0.5:
            if d_nh4 is not None and d_nh4 >= -0.5 and (d_no2 is None or d_no2 >= -0.5):
                findings.append("NO₃ is rising without NH₄/NO₂ decrease — possible NOB interference.")
                actions.append("Keep DO below 0.2 mg/L in the Anammox reactor.")
                status = "danger"
            elif d_nh4 is not None and d_nh4 < -0.5:
                expected = abs(d_nh4) * ANAMMOX_NO3_PER_NH4
                if d_no3 <= expected * 1.5:
                    findings.append(
                        f"NO₃ increase is consistent with intrinsic Anammox (~{expected:.1f} mg/L expected)."
                    )

        if nh4_today > 10 and no2_today > 10:
            feed = check_anammox_feed(nh4_today, no2_today, no3_today)
            if not feed.ready_for_anammox:
                findings.append("Substrate ratio is not optimal — Anammox efficiency may be reduced.")
                status = "warning" if status == "ok" else status

    if not findings:
        findings.append("No significant day-to-day change detected.")

    if not actions and status == "ok":
        actions.append("Maintain current operating conditions.")

    return DailyDiagnostics(
        stage=stage,
        status=status,
        findings=findings,
        actions=actions,
    )
