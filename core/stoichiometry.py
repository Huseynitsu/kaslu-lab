from dataclasses import dataclass

from core.constants import (
    ANAMMOX_HCO3_MASS_PER_NH4,
    ANAMMOX_IDEAL_RATIO,
    ANAMMOX_INTRINSIC_NO3_FRACTION,
    ANAMMOX_NO2_PER_NH4,
    ANAMMOX_NO3_PER_NH4,
)


@dataclass
class StoichiometryResult:
    nh4_mg_l: float
    no2_mg_l: float
    no3_mg_l: float
    hco3_mg_l: float | None
    no2_nh4_ratio: float
    ideal_ratio: float
    ratio_deviation_pct: float
    ready_for_anammox: bool
    limiting_substrate: str
    expected_no3_from_anammox: float
    expected_no2_consumed: float
    expected_hco3_consumed: float
    messages: list[str]


def check_anammox_feed(
    nh4_mg_l: float,
    no2_mg_l: float,
    no3_mg_l: float = 0.0,
    hco3_mg_l: float | None = None,
    ratio_tolerance_pct: float = 15.0,
) -> StoichiometryResult:
    """
    Check if PN effluent meets Strous stoichiometry for anammox feed.
    """
    messages = []

    if nh4_mg_l <= 0 and no2_mg_l <= 0:
        return StoichiometryResult(
            nh4_mg_l=nh4_mg_l,
            no2_mg_l=no2_mg_l,
            no3_mg_l=no3_mg_l,
            hco3_mg_l=hco3_mg_l,
            no2_nh4_ratio=0.0,
            ideal_ratio=ANAMMOX_IDEAL_RATIO,
            ratio_deviation_pct=100.0,
            ready_for_anammox=False,
            limiting_substrate="none",
            expected_no3_from_anammox=0.0,
            expected_no2_consumed=0.0,
            expected_hco3_consumed=0.0,
            messages=["NH₄ and NO₂ concentrations are zero."],
        )

    ratio = no2_mg_l / max(nh4_mg_l, 1e-9)
    deviation_pct = abs(ratio - ANAMMOX_IDEAL_RATIO) / ANAMMOX_IDEAL_RATIO * 100.0

    nh4_limited = nh4_mg_l
    no2_limited = no2_mg_l / ANAMMOX_NO2_PER_NH4
    hco3_limited = float("inf")
    if hco3_mg_l is not None:
        hco3_limited = hco3_mg_l / ANAMMOX_HCO3_MASS_PER_NH4

    reactive_nh4 = min(nh4_limited, no2_limited, hco3_limited)

    if reactive_nh4 == nh4_limited and reactive_nh4 < no2_limited:
        limiting = "NH4"
        messages.append("Limiting substrate: NH₄ — excess NO₂ is available.")
    elif reactive_nh4 == no2_limited and reactive_nh4 < nh4_limited:
        limiting = "NO2"
        messages.append("Limiting substrate: NO₂ — strengthen the PN stage.")
    elif hco3_mg_l is not None and reactive_nh4 == hco3_limited:
        limiting = "HCO3"
        messages.append("Limiting substrate: HCO₃⁻ — add alkalinity.")
    else:
        limiting = "balanced"
        messages.append("Substrate balance is good.")

    expected_no3 = reactive_nh4 * ANAMMOX_NO3_PER_NH4
    expected_no2_used = reactive_nh4 * ANAMMOX_NO2_PER_NH4
    expected_hco3_used = reactive_nh4 * ANAMMOX_HCO3_MASS_PER_NH4

    ready = deviation_pct <= ratio_tolerance_pct and nh4_mg_l > 0 and no2_mg_l > 0

    if deviation_pct > ratio_tolerance_pct:
        if ratio < ANAMMOX_IDEAL_RATIO:
            messages.append(
                f"NO₂/NH₄ ratio ({ratio:.2f}) is below ideal {ANAMMOX_IDEAL_RATIO:.2f} — "
                "more nitrite is needed (strengthen PN)."
            )
        else:
            messages.append(
                f"NO₂/NH₄ ratio ({ratio:.2f}) is above ideal {ANAMMOX_IDEAL_RATIO:.2f} — "
                "ammonium is low or nitrite is excessive."
            )
    else:
        messages.append(
            f"Ratio is close to ideal ({ratio:.2f} ≈ {ANAMMOX_IDEAL_RATIO:.2f})."
        )

    if no3_mg_l > expected_no3 * 2 and nh4_mg_l > 5:
        messages.append(
            "NO₃ may exceed intrinsic Anammox levels — check for NOB activity."
        )

    return StoichiometryResult(
        nh4_mg_l=nh4_mg_l,
        no2_mg_l=no2_mg_l,
        no3_mg_l=no3_mg_l,
        hco3_mg_l=hco3_mg_l,
        no2_nh4_ratio=ratio,
        ideal_ratio=ANAMMOX_IDEAL_RATIO,
        ratio_deviation_pct=deviation_pct,
        ready_for_anammox=ready,
        limiting_substrate=limiting,
        expected_no3_from_anammox=expected_no3,
        expected_no2_consumed=expected_no2_used,
        expected_hco3_consumed=expected_hco3_used,
        messages=messages,
    )


def intrinsic_no3_note() -> str:
    pct = ANAMMOX_INTRINSIC_NO3_FRACTION * 100
    return (
        f"Anammox intrinsically converts ~{pct:.0f}% of input nitrogen to NO₃⁻ "
        f"(Strous: {ANAMMOX_NO3_PER_NH4} mol NO₃ / mol NH₄)."
    )
