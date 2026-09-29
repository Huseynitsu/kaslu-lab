"""
Operating-window assessment for NOB suppression.

mode="pn"  : two-stage, suspended partial nitritation (SHARON-type) [3][4]
mode="pna" : one-stage PN/A (granules / biofilm) [8]

The checks are qualitative screening rules from the literature, not a model prediction.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from core.chemistry import (
    FA_AOB_INHIBITION_ONSET,
    FA_NOB_INHIBITION_ONSET,
    FNA_NITRIFIER_INHIBITION_ONSET,
    free_ammonia_as_molecule,
    free_nitrous_acid_as_molecule,
)
from core.constants import (
    ANAMMOX_SRT_MIN,
    PN_DO_MAX,
    PN_DO_MIN,
    PN_PH_MAX,
    PN_PH_MIN,
    PN_SRT_MAX,
    PN_TEMP_MAX,
    PN_TEMP_MIN,
    PNA_DO_MAX,
    PNA_DO_MIN,
    PNA_RESIDUAL_NH4_MIN,
)


@dataclass
class ParameterCheck:
    name: str
    value: float
    unit: str
    status: str  # ok | warning | danger
    message: str
    optimal_range: str
    reference: str = ""


@dataclass
class PNAssessment:
    mode: str
    nob_risk: str            # low | medium | high
    aob_favorability: str    # low | medium | high
    overall_status: str      # ok | warning | danger
    checks: list[ParameterCheck] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    fa_nh3_mg_l: float = 0.0
    fna_hno2_mg_l: float = 0.0


def _range_check(name, value, unit, lo, hi, ref, low_msg, high_msg, ok_msg="Within range."):
    if value < lo:
        return ParameterCheck(name, value, unit, "warning", low_msg, f"{lo}–{hi} {unit}", ref)
    if value > hi:
        return ParameterCheck(name, value, unit, "warning", high_msg, f"{lo}–{hi} {unit}", ref)
    return ParameterCheck(name, value, unit, "ok", ok_msg, f"{lo}–{hi} {unit}", ref)


def assess_pn_operation(
    do_mg_l: float,
    temperature_c: float,
    ph: float,
    srt_days: float,
    nh4_mg_l: float,
    no2_mg_l: float,
    mode: str = "pn",
) -> PNAssessment:
    checks: list[ParameterCheck] = []
    recs: list[str] = []
    risk_points = 0

    fa = free_ammonia_as_molecule(nh4_mg_l, ph, temperature_c)
    fna = free_nitrous_acid_as_molecule(no2_mg_l, ph, temperature_c)

    if mode == "pna":
        c = _range_check("DO (bulk)", do_mg_l, "mg/L", PNA_DO_MIN, PNA_DO_MAX, "[8] Hao et al. 2002",
                         "DO very low — AOB may limit NH4 conversion.",
                         "DO too high for one-stage PN/A — NOB growth and anammox O2 inhibition.")
        if c.status != "ok" and do_mg_l > PNA_DO_MAX:
            risk_points += 2
            recs.append(f"Lower DO toward {PNA_DO_MIN}–{PNA_DO_MAX} mg/L or use intermittent aeration.")
        checks.append(c)
        if srt_days < ANAMMOX_SRT_MIN:
            checks.append(ParameterCheck("SRT (anammox)", srt_days, "d", "danger",
                                         "Too short — anammox (doubling ≈ 11 d) will wash out.",
                                         f"≥ {ANAMMOX_SRT_MIN} d for anammox", "[1] Strous 1998"))
            recs.append("Retain anammox biomass (granules/carriers); shorten only the floc SRT to wash out NOB.")
            risk_points += 1
        else:
            checks.append(ParameterCheck("SRT (anammox)", srt_days, "d", "ok",
                                         "Long enough for anammox retention.", f"≥ {ANAMMOX_SRT_MIN} d", "[1]"))
        if nh4_mg_l < PNA_RESIDUAL_NH4_MIN:
            checks.append(ParameterCheck("Residual NH4", nh4_mg_l, "mg N/L", "warning",
                                         "Very low residual NH4 — over-aeration risk, NOB favoured.",
                                         f"≥ {PNA_RESIDUAL_NH4_MIN} mg N/L", "Operational practice"))
            risk_points += 1
            recs.append("Keep a small residual NH4 (reduce aeration or increase load).")
        t_rng = (25.0, 35.0)
        checks.append(_range_check("Temperature", temperature_c, "°C", *t_rng, "[8]",
                                   "Low T slows anammox and AOB; NOB relatively favoured.",
                                   "High T — check anammox stability above 35–37 °C."))
        checks.append(_range_check("pH", ph, "", 7.0, 8.2, "[2]",
                                   "Low pH — alkalinity limitation, FNA risk.",
                                   "High pH — FA may inhibit anammox/AOB."))
    else:
        c = _range_check("DO", do_mg_l, "mg/L", PN_DO_MIN, PN_DO_MAX, "[3][6]",
                         "DO low — AOB rate limited.",
                         "DO high — NOB (higher K_O) are no longer disadvantaged.")
        if do_mg_l > PN_DO_MAX:
            risk_points += 1
            recs.append(f"Reduce DO to {PN_DO_MIN}–{PN_DO_MAX} mg/L.")
        checks.append(c)
        c = _range_check("Temperature", temperature_c, "°C", PN_TEMP_MIN, PN_TEMP_MAX, "[3] SHARON",
                         "Below ~25–30 °C AOB lose their growth-rate advantage over NOB.",
                         "Above 40 °C nitrifier activity declines.")
        if temperature_c < PN_TEMP_MIN:
            risk_points += 1
            recs.append("At low temperature, SRT-based NOB washout is unreliable — rely on DO/FA/FNA control.")
        checks.append(c)
        checks.append(_range_check("pH", ph, "", PN_PH_MIN, PN_PH_MAX, "[4]",
                                   "Low pH lowers FA (less NOB inhibition) but raises FNA.",
                                   "High pH raises FA — may also inhibit AOB."))
        if srt_days > PN_SRT_MAX:
            checks.append(ParameterCheck("SRT", srt_days, "d", "warning",
                                         "Long SRT allows NOB to stay in suspended PN.",
                                         f"≈1–{PN_SRT_MAX:.0f} d (SHARON: SRT = HRT ≈ 1–1.5 d)", "[3]"))
            risk_points += 1
            recs.append("Shorten SRT (at ≥30 °C) to wash out NOB.")
        else:
            checks.append(ParameterCheck("SRT", srt_days, "d", "ok", "Short SRT supports NOB washout at high T.",
                                         f"≈1–{PN_SRT_MAX:.0f} d", "[3]"))

    fa_zone_ok = FA_NOB_INHIBITION_ONSET[0] <= fa < FA_AOB_INHIBITION_ONSET[0]
    checks.append(ParameterCheck(
        "Free ammonia (FA)", fa, "mg NH3/L",
        "ok" if fa_zone_ok else "warning",
        "FA in the NOB-selective window." if fa_zone_ok else (
            "FA below NOB inhibition onset — no FA selection." if fa < FA_NOB_INHIBITION_ONSET[0]
            else "FA above AOB inhibition onset."),
        f"{FA_NOB_INHIBITION_ONSET[0]}–{FA_AOB_INHIBITION_ONSET[0]} mg NH3/L (selective)", "[4] Anthonisen"))
    if fa < FA_NOB_INHIBITION_ONSET[0] and mode == "pn":
        risk_points += 1
    fna_ok = fna < FNA_NITRIFIER_INHIBITION_ONSET[0]
    checks.append(ParameterCheck(
        "Free nitrous acid (FNA)", fna, "mg HNO2/L",
        "ok" if fna_ok else "warning",
        "FNA below nitrifier inhibition onset." if fna_ok else "FNA may inhibit nitrifiers (NOB first).",
        f"< {FNA_NITRIFIER_INHIBITION_ONSET[0]} mg HNO2/L", "[4] Anthonisen"))

    nob_risk = "low" if risk_points == 0 else "medium" if risk_points <= 2 else "high"
    aob_fav = {"low": "high", "medium": "medium", "high": "low"}[nob_risk]
    overall = "ok" if nob_risk == "low" else "warning" if nob_risk == "medium" else "danger"
    if any(c.status == "danger" for c in checks):
        overall = "danger"
    if not recs:
        recs.append("Operating window is consistent with NOB suppression; confirm with NO3 trend (ΔNO3/ΔNH4).")
    return PNAssessment(mode, nob_risk, aob_fav, overall, checks, list(dict.fromkeys(recs)), fa, fna)
