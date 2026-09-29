"""
Scientific constants for PN, anammox and one-stage PN/A.

Reference list (keep in sync with docs/SCIENCE.md)
[1] Strous, M., Heijnen, J.J., Kuenen, J.G., Jetten, M.S.M. (1998). The sequencing batch
    reactor as a powerful tool for the study of slowly growing anaerobic ammonium-oxidizing
    microorganisms. Appl. Microbiol. Biotechnol. 50, 589–596.
[2] Strous, M., Kuenen, J.G., Jetten, M.S.M. (1999). Key physiology of anaerobic ammonium
    oxidation. Appl. Environ. Microbiol. 65(7), 3248–3250.
[3] Hellinga, C., Schellen, A.A.J.C., Mulder, J.W., van Loosdrecht, M.C.M., Heijnen, J.J. (1998).
    The SHARON process. Water Sci. Technol. 37(9), 135–142.
[4] Anthonisen, A.C. et al. (1976). Inhibition of nitrification by ammonia and nitrous acid.
    J. Water Pollut. Control Fed. 48(5), 835–852.
[5] Standard Methods 23rd ed. (2017); China: HJ 535-2009 (NH4-N, Nessler), GB 7493-87
    (NO2-N), HJ/T 346-2007 (NO3-N, UV).
[6] Jubany, I., Lafuente, J., Baeza, J.A., Carrera, J. (2009). Total and stable washout of
    nitrite oxidizing bacteria from a nitrifying continuous activated sludge system using
    automatic control based on Oxygen Uptake Rate measurements. Water Res. 43(11), 2761–2772.
    (Previously mis-attributed to "Pollice et al."; that study used DO/OUR control at
    SRT ≈ 30 d — it does NOT support "SRT < 5 d".)
[7] Lotti, T., Kleerebezem, R., Lubello, C., van Loosdrecht, M.C.M. (2014). Physiological and
    kinetic characterization of a suspended cell anammox culture. Water Res. 60, 1–14.
[8] Hao, X., Heijnen, J.J., van Loosdrecht, M.C.M. (2002). Model-based evaluation of
    temperature and inflow variations on a partial nitrification–ANAMMOX biofilm process.
    Water Res. 36(19), 4839–4849.
"""

# ---------------------------------------------------------------------------
# Anammox stoichiometry (mol per mol NH4+ ; equal to mg N / mg N for N species)
# ---------------------------------------------------------------------------
STROUS_1998 = {
    "name": "Strous et al. (1998) [1]",
    "no2_per_nh4": 1.32,
    "no3_per_nh4": 0.26,
    "n2_per_nh4": 1.02,          # mol N2 -> 2.04 mol N
    "hco3_per_nh4": 0.066,
    "h_per_nh4": 0.13,
    "biomass_per_nh4": 0.066,    # mol CH2O0.5N0.15
    "biomass_mw": 24.1,          # g/mol CH2O0.5N0.15
    "biomass_n_frac": 0.15,
}

# Lotti et al. (2014) [7] — highly enriched suspended culture; widely used in newer work.
# Coefficients as reported in [7]; verify against the paper before citing numerically.
LOTTI_2014 = {
    "name": "Lotti et al. (2014) [7]",
    "no2_per_nh4": 1.146,
    "no3_per_nh4": 0.161,
    "n2_per_nh4": 0.986,
    "hco3_per_nh4": 0.071,
    "h_per_nh4": 0.057,
    "biomass_per_nh4": 0.071,    # mol CH1.74O0.31N0.20
    "biomass_mw": 21.5,
    "biomass_n_frac": 0.20,
}

STOICHIOMETRY_SETS = {"strous_1998": STROUS_1998, "lotti_2014": LOTTI_2014}
DEFAULT_STOICHIOMETRY = "strous_1998"

ANAMMOX_NO2_PER_NH4 = STROUS_1998["no2_per_nh4"]
ANAMMOX_NO3_PER_NH4 = STROUS_1998["no3_per_nh4"]
ANAMMOX_HCO3_MOL_PER_NH4 = STROUS_1998["hco3_per_nh4"]
ANAMMOX_HCO3_MASS_PER_NH4 = ANAMMOX_HCO3_MOL_PER_NH4 * 61.0 / 14.0  # mg HCO3- / mg NH4-N
ANAMMOX_IDEAL_RATIO = ANAMMOX_NO2_PER_NH4  # NO2-N / NH4-N in anammox FEED (two-stage)

# Fraction of consumed N (NH4 + NO2) that ends as NO3: 0.26 / 2.32 = 11.2 %
# (bug fixed: previously divided by 1 + 1.32 + 0.26, counting the product as input)
ANAMMOX_INTRINSIC_NO3_FRACTION = ANAMMOX_NO3_PER_NH4 / (1.0 + ANAMMOX_NO2_PER_NH4)


def anammox_yield_vss_per_n(stoich: dict = STROUS_1998) -> float:
    """g VSS formed per g NH4-N consumed by anammox (from the catabolic equation)."""
    return stoich["biomass_per_nh4"] * stoich["biomass_mw"] / 14.0


# ---------------------------------------------------------------------------
# One-stage PN/A (CANON / DEMON / granular / MBBR) indicators
# ---------------------------------------------------------------------------
# Overall: AOB oxidise 1.32 NH4 -> NO2 for each 1 NH4 used by anammox.
# NH4 removed = 1 + 1.32 = 2.32 ; NO3 produced = 0.26  ->  ΔNO3/ΔNH4 = 0.112
def pna_no3_per_nh4_removed(stoich: dict = STROUS_1998) -> float:
    return stoich["no3_per_nh4"] / (1.0 + stoich["no2_per_nh4"])


def pna_max_tn_removal(stoich: dict = STROUS_1998) -> float:
    """Theoretical max TN removal of autotrophic PN/A (no denitrification): ~0.89 (Strous)."""
    return 1.0 - pna_no3_per_nh4_removed(stoich)


PNA_NO3_PER_NH4_REMOVED = pna_no3_per_nh4_removed()   # 0.112 (Strous); 0.075 (Lotti)
PNA_MAX_TN_REMOVAL = pna_max_tn_removal()             # 0.888
# Early-warning thresholds for ΔNO3/ΔNH4 (operator-tunable defaults, not literature constants)
PNA_NO3_RATIO_WARNING = 0.15
PNA_NO3_RATIO_ALARM = 0.20
# Bulk DO for one-stage PN/A: ~0.3 mg/L optimum at 20 °C in a biofilm model [8];
# full-scale granular / MBBR systems usually operate 0.1–0.5 mg/L or with intermittent aeration.
PNA_DO_MIN = 0.1
PNA_DO_MAX = 0.5
PNA_DO_OPTIMAL = (0.2, 0.4)
PNA_NO2_EFFLUENT_WARNING = 20.0   # mg N/L — anammox not keeping up with AOB
PNA_NO2_EFFLUENT_ALARM = 50.0     # mg N/L — anammox inhibition risk [2]
PNA_RESIDUAL_NH4_MIN = 5.0        # mg N/L — residual NH4 helps keep NOB out-competed

# ---------------------------------------------------------------------------
# Two-stage partial nitritation (PN) — suspended sludge, sidestream (SHARON-type)
# ---------------------------------------------------------------------------
PN_DO_MIN = 0.5
PN_DO_MAX = 1.0
PN_DO_OPTIMAL = (0.5, 1.0)

PN_TEMP_MIN = 30.0
PN_TEMP_MAX = 40.0
PN_TEMP_OPTIMAL = (30.0, 35.0)

PN_PH_MIN = 7.5
PN_PH_MAX = 8.5
PN_PH_OPTIMAL = (7.5, 8.0)

# SHARON [3]: chemostat without retention, SRT = HRT ≈ 1–1.5 d at 30–40 °C.
# "SRT < 5 d" is a general rule for suspended PN at elevated T; it must NOT be applied
# to one-stage PN/A where anammox (doubling ≈ 11 d [1]) needs long retention.
PN_SRT_MAX = 5.0
PN_SRT_OPTIMAL = (1.0, 3.0)

# Anthonisen [4] (mg NH3/L, mg HNO2/L — molecule basis)
PN_FA_INHIBITORY_MIN = 0.1   # NOB inhibition onset
PN_FA_INHIBITORY_MAX = 10.0  # AOB inhibition onset
PN_FNA_INHIBITORY_MIN = 0.2

# ---------------------------------------------------------------------------
# Anammox reactor (stage 2) / anammox biomass
# ---------------------------------------------------------------------------
ANAMMOX_DO_MAX = 0.2   # bulk DO; intrinsic K_O is far lower (~0.01 mg/L) [2][8]
ANAMMOX_PH_MIN = 6.7   # physiological range 6.7–8.3 [2]
ANAMMOX_PH_MAX = 8.3
ANAMMOX_TEMP_MIN = 20.0
ANAMMOX_TEMP_MAX = 43.0
ANAMMOX_TEMP_OPTIMAL = (30.0, 37.0)
ANAMMOX_SRT_MIN = 20.0   # ≥ 2–3 × doubling time (≈11 d [1])
ANAMMOX_NO2_INHIBITION = 100.0  # mg N/L — reported inhibition above ~100 mg NO2-N/L [2]

# ---------------------------------------------------------------------------
# Spectrophotometry [5]
# ---------------------------------------------------------------------------
ABSORBANCE_LINEAR_MIN = 0.2   # common lab practice for best photometric precision
ABSORBANCE_LINEAR_MAX = 0.8
ABSORBANCE_TOO_HIGH = 1.0
CALIBRATION_MIN_POINTS = 5
CALIBRATION_MIN_R2 = 0.999

# Literature defaults when optional operating inputs are not provided
LITERATURE_DEFAULTS = {
    "pn": {
        "temperature": 35.0,
        "temperature_ref": "[3] SHARON PN 30–40 °C",
        "do": 0.8,
        "do_ref": "Two-stage PN, low DO 0.5–1.0 mg/L",
        "srt": 2.0,
        "srt_ref": "[3] SHARON: SRT = HRT ≈ 1–1.5 d",
        "biomass": 200.0,
        "biomass_ref": "Model default AOB (mg VSS/L) — calibrate",
        "hco3": 0.0,
        "hco3_ref": "Not used in PN stage",
    },
    "anammox": {
        "temperature": 35.0,
        "temperature_ref": "[1][2] Mesophilic anammox ~30–37 °C",
        "do": 0.05,
        "do_ref": "[2] Anammox reversibly inhibited by O2",
        "srt": 30.0,
        "srt_ref": "[1] Long retention (doubling ≈ 11 d)",
        "biomass": 800.0,
        "biomass_ref": "Model default anammox (mg VSS/L) — calibrate",
        "hco3": 120.0,
        "hco3_ref": "[1] Inorganic carbon source",
    },
    "pna": {
        "temperature": 30.0,
        "temperature_ref": "[8] PN/A mesophilic",
        "do": 0.3,
        "do_ref": "[8] ~0.3 mg/L bulk DO optimum (biofilm model, 20 °C)",
        "srt": 40.0,
        "srt_ref": "Granule/biofilm retention for anammox",
        "biomass": 1500.0,
        "biomass_ref": "Model default anammox granules (mg VSS/L) — calibrate",
        "hco3": 0.0,
        "hco3_ref": "Alkalinity not modelled",
    },
}


def get_literature_default(stage: str, param: str) -> float:
    return float(LITERATURE_DEFAULTS[stage][param])


def get_literature_reference(stage: str, param: str) -> str:
    return LITERATURE_DEFAULTS[stage].get(param + "_ref", "")
