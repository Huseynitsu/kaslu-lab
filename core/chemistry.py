import math


def pka_ammonia(temperature_c: float = 25.0) -> float:
    """Temperature-adjusted pKa for NH4+/NH3 equilibrium."""
    return 0.09018 + 2729.92 / (temperature_c + 273.0)


def pka_nitrous_acid(temperature_c: float = 25.0) -> float:
    """Temperature-adjusted pKa for HNO2/NO2- equilibrium."""
    return 0.29 + 2200.0 / (temperature_c + 273.0)


def free_ammonia_mg_l(nh4_n_mg_l: float, ph: float, temperature_c: float = 25.0) -> float:
    """
    Free ammonia (FA) as NH3-N in mg/L.
    Anthonisen et al. (1976) framework.
    """
    if nh4_n_mg_l <= 0:
        return 0.0
    pka = pka_ammonia(temperature_c)
    return nh4_n_mg_l / (1.0 + 10.0 ** (pka - ph))


def free_nitrous_acid_mg_l(no2_n_mg_l: float, ph: float, temperature_c: float = 25.0) -> float:
    """
    Free nitrous acid (FNA) as HNO2-N in mg/L (Anthonisen et al., 1976).

    Given total nitrite-N concentration S_NO2 (mg/L as N), pH, and temperature:

        FNA = S_NO2 / (1 + 10^(pH - pKa_HNO2))

    where pKa_HNO2 is from ``pka_nitrous_acid(temperature_c)``.
    """
    if no2_n_mg_l <= 0:
        return 0.0
    pka = pka_nitrous_acid(temperature_c)
    return no2_n_mg_l / (1.0 + 10.0 ** (ph - pka))
