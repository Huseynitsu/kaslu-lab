"""
Acid–base chemistry for free ammonia (FA) and free nitrous acid (FNA).

References
----------
[4]  Anthonisen, A.C., Loehr, R.C., Prakasam, T.B.S., Srinath, E.G. (1976).
     Inhibition of nitrification by ammonia and nitrous acid.
     J. Water Pollut. Control Fed. 48(5), 835–852.
     FA  (mg NH3/L)  = 17/14 · TAN-N · 10^pH / (exp(6344/(273+T)) + 10^pH)
     FNA (mg HNO2/L) = 46/14 · NO2-N / (exp(-2300/(273+T)) · 10^pH)
[E]  Emerson, K. et al. (1975). Aqueous ammonia equilibrium calculations.
     J. Fish. Res. Board Can. 32, 2379–2383.  pKa = 0.09018 + 2729.92 / T(K)

Units
-----
All inputs are mg N/L (TAN-N, NO2-N). Functions ending in ``_mg_l`` return
mg N/L (NH3-N or HNO2-N). Functions ending in ``_as_molecule`` return mg NH3/L
or mg HNO2/L, which is the basis Anthonisen used for his inhibition thresholds.

NOTE (bug fixed 2026-09): the previous version used pKa(HNO2) = 0.29 + 2200/T,
i.e. ≈ 7.7 at 25 °C. The real pKa of nitrous acid is ≈ 3.3, so FNA was
over-estimated by ~2–3 orders of magnitude.
"""

from __future__ import annotations

import math

KELVIN = 273.15
MW_N = 14.0067
MW_NH3 = 17.031
MW_HNO2 = 47.013


def pka_ammonia(temperature_c: float = 25.0) -> float:
    """pKa of NH4+/NH3 (Emerson et al., 1975). ≈9.25 at 25 °C."""
    return 0.09018 + 2729.92 / (temperature_c + KELVIN)


def pka_nitrous_acid(temperature_c: float = 25.0) -> float:
    """
    pKa of HNO2/NO2- from Anthonisen's Ka = exp(-2300 / (273 + T)).

    pKa = 2300 / ((273 + T) · ln 10)  → ≈3.35 at 25 °C, ≈3.30 at 30 °C.
    """
    return 2300.0 / ((temperature_c + 273.0) * math.log(10.0))


def free_ammonia_mg_l(nh4_n_mg_l: float, ph: float, temperature_c: float = 25.0) -> float:
    """Free ammonia as mg NH3-N/L from total ammonium-N (TAN-N)."""
    if nh4_n_mg_l is None or nh4_n_mg_l <= 0:
        return 0.0
    pka = pka_ammonia(temperature_c)
    return nh4_n_mg_l / (1.0 + 10.0 ** (pka - ph))


def free_nitrous_acid_mg_l(no2_n_mg_l: float, ph: float, temperature_c: float = 25.0) -> float:
    """
    Free nitrous acid as mg HNO2-N/L from total nitrite-N.

        FNA = NO2-N / (1 + 10^(pH − pKa)),   pKa = pka_nitrous_acid(T)
    """
    if no2_n_mg_l is None or no2_n_mg_l <= 0:
        return 0.0
    pka = pka_nitrous_acid(temperature_c)
    return no2_n_mg_l / (1.0 + 10.0 ** (ph - pka))


def free_ammonia_as_molecule(nh4_n_mg_l: float, ph: float, temperature_c: float = 25.0) -> float:
    """Free ammonia as mg NH3/L (Anthonisen basis)."""
    return free_ammonia_mg_l(nh4_n_mg_l, ph, temperature_c) * MW_NH3 / MW_N


def free_nitrous_acid_as_molecule(no2_n_mg_l: float, ph: float, temperature_c: float = 25.0) -> float:
    """Free nitrous acid as mg HNO2/L (Anthonisen basis)."""
    return free_nitrous_acid_mg_l(no2_n_mg_l, ph, temperature_c) * MW_HNO2 / MW_N


def anthonisen_fa_closed_form(nh4_n_mg_l: float, ph: float, temperature_c: float) -> float:
    """Anthonisen (1976) closed form, mg NH3/L — used for validation."""
    tenph = 10.0 ** ph
    return (17.0 / 14.0) * nh4_n_mg_l * tenph / (math.exp(6344.0 / (273.0 + temperature_c)) + tenph)


def anthonisen_fna_closed_form(no2_n_mg_l: float, ph: float, temperature_c: float) -> float:
    """Anthonisen (1976) closed form, mg HNO2/L — used for validation."""
    ka = math.exp(-2300.0 / (273.0 + temperature_c))
    return (46.0 / 14.0) * no2_n_mg_l / (ka * 10.0 ** ph)


# Anthonisen (1976) inhibition ranges, expressed as the molecule (mg NH3/L, mg HNO2/L)
FA_NOB_INHIBITION_ONSET = (0.1, 1.0)   # mg NH3/L — Nitrobacter inhibited
FA_AOB_INHIBITION_ONSET = (10.0, 150.0)  # mg NH3/L — Nitrosomonas inhibited
FNA_NITRIFIER_INHIBITION_ONSET = (0.2, 2.8)  # mg HNO2/L — both groups


def classify_fa(fa_nh3_mg_l: float) -> str:
    """Qualitative FA zone per Anthonisen (1976) — input is mg NH3/L."""
    if fa_nh3_mg_l < FA_NOB_INHIBITION_ONSET[0]:
        return "no_inhibition"
    if fa_nh3_mg_l < FA_AOB_INHIBITION_ONSET[0]:
        return "nob_inhibition"  # selective NOB suppression window
    return "aob_inhibition"


def classify_fna(fna_hno2_mg_l: float) -> str:
    """Qualitative FNA zone per Anthonisen (1976) — input is mg HNO2/L."""
    if fna_hno2_mg_l < FNA_NITRIFIER_INHIBITION_ONSET[0]:
        return "no_inhibition"
    return "nitrifier_inhibition"
