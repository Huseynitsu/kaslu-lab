"""
Scientific constants from Strous et al. (1998) and partial nitritation literature.
"""

# Strous full anammox stoichiometry (mol ratios on N basis unless noted)
ANAMMOX_NO2_PER_NH4 = 1.32
ANAMMOX_NO3_PER_NH4 = 0.26
ANAMMOX_HCO3_MOL_PER_NH4 = 0.066
ANAMMOX_HCO3_MASS_PER_NH4 = ANAMMOX_HCO3_MOL_PER_NH4 * 61.0 / 14.0  # mg HCO3- / mg NH4-N
ANAMMOX_IDEAL_RATIO = ANAMMOX_NO2_PER_NH4  # NO2-N / NH4-N
ANAMMOX_INTRINSIC_NO3_FRACTION = 0.26 / (1.0 + 1.32 + 0.26)  # ~10% of input N

# Partial nitritation operational ranges (Table 1, article)
PN_DO_MIN = 0.5
PN_DO_MAX = 1.0
PN_DO_OPTIMAL = (0.8, 1.0)

PN_TEMP_MIN = 30.0
PN_TEMP_MAX = 40.0
PN_TEMP_OPTIMAL = (30.0, 35.0)

PN_PH_MIN = 7.5
PN_PH_MAX = 8.5
PN_PH_OPTIMAL = (7.5, 8.0)

PN_SRT_MAX = 5.0
PN_SRT_OPTIMAL = (3.0, 5.0)

PN_FA_INHIBITORY_MIN = 1.0  # mg/L NH3-N
PN_FA_INHIBITORY_MAX = 10.0

# Anammox reactor (stage 2)
ANAMMOX_DO_MAX = 0.2
ANAMMOX_PH_MIN = 7.0
ANAMMOX_PH_MAX = 8.5
ANAMMOX_TEMP_MIN = 25.0
ANAMMOX_TEMP_MAX = 40.0
ANAMMOX_TEMP_OPTIMAL = (30.0, 37.0)
ANAMMOX_SRT_MIN = 15.0

# Spectrophotometry (Standard Methods) [5]
ABSORBANCE_LINEAR_MIN = 0.2
ABSORBANCE_LINEAR_MAX = 0.8
ABSORBANCE_TOO_HIGH = 1.0

# Literature defaults when optional operating inputs are not provided
# PN: Hellinga et al. [3], Anthonisen [4], Pollice [6]
# Anammox: Strous et al. [1][2]
LITERATURE_DEFAULTS = {
    "pn": {
        "temperature": 35.0,
        "temperature_ref": "[3] SHARON / PN optimum 30–35 °C",
        "do": 0.8,
        "do_ref": "[3] PN selective aeration 0.5–1.0 mg/L",
        "srt": 4.0,
        "srt_ref": "[6] NOB washout SRT < 5 days",
        "biomass": 200.0,
        "biomass_ref": "Typical lab-scale AOB enrichment (model default)",
        "hco3": 0.0,
        "hco3_ref": "Not used in PN stage",
    },
    "anammox": {
        "temperature": 35.0,
        "temperature_ref": "[1][2] Mesophilic Anammox ~30–37 °C",
        "do": 0.2,
        "do_ref": "[1][2] Anammox inhibited by oxygen (< 0.2 mg/L)",
        "srt": 30.0,
        "srt_ref": "UASB long biomass retention (typical lab reactor)",
        "biomass": 800.0,
        "biomass_ref": "[1] Enriched Anammox biomass (model default)",
        "hco3": 120.0,
        "hco3_ref": "[1] Strous stoichiometry inorganic carbon",
    },
}


def get_literature_default(stage: str, param: str) -> float:
    return float(LITERATURE_DEFAULTS[stage][param])


def get_literature_reference(stage: str, param: str) -> str:
    return LITERATURE_DEFAULTS[stage].get(param + "_ref", "")
