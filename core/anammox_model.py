import math

from core.constants import ANAMMOX_HCO3_MASS_PER_NH4, ANAMMOX_NO2_PER_NH4, ANAMMOX_NO3_PER_NH4


def mechanistic_prediction(nh4, no2):
    """Expected intrinsic NO3 production from Strous stoichiometry."""
    nh4_available = min(nh4, no2 / ANAMMOX_NO2_PER_NH4)
    return nh4_available * ANAMMOX_NO3_PER_NH4


def full_anammox_model(
    nh4,
    no2,
    no3,
    hco3,
    ph,
    temperature,
    do,
    x_anammox,
    srt,
):
    DT = 1.0

    MU_MAX = 0.08
    K_NH4 = 0.5
    K_NO2 = 0.5
    KI_DO = 0.2

    Y = 0.11
    DECAY = 0.002

    ph_factor = math.exp(-((ph - 7.8) ** 2) / (2 * (0.4 ** 2)))

    temp_factor = math.exp(-((temperature - 35) ** 2) / (2 * (5 ** 2)))

    do_factor = KI_DO / (KI_DO + do)

    activity = max(0.0, min(ph_factor * temp_factor * do_factor, 1.0))

    monod_nh4 = nh4 / (K_NH4 + nh4)
    monod_no2 = no2 / (K_NO2 + no2)

    biomass_g = x_anammox / 1000.0

    # Specific uptake based on Strous kinetics [1][2]
    q_nh4 = (MU_MAX / Y) * monod_nh4 * monod_no2 * activity
    nh4_consumed = q_nh4 * biomass_g * DT

    max_nh4_possible = min(
        nh4,
        no2 / ANAMMOX_NO2_PER_NH4,
        hco3 / ANAMMOX_HCO3_MASS_PER_NH4,
    )

    nh4_consumed = min(nh4_consumed, max_nh4_possible)

    biomass_growth = Y * nh4_consumed

    no2_consumed = nh4_consumed * ANAMMOX_NO2_PER_NH4
    no3_produced = nh4_consumed * ANAMMOX_NO3_PER_NH4
    hco3_consumed = nh4_consumed * ANAMMOX_HCO3_MASS_PER_NH4

    nh4_new = max(nh4 - nh4_consumed, 0)
    no2_new = max(no2 - no2_consumed, 0)
    no3_new = no3 + no3_produced
    hco3_new = max(hco3 - hco3_consumed, 0)

    biomass_decay = DECAY * x_anammox
    x_new = x_anammox + biomass_growth - biomass_decay

    if srt < 15:
        x_new *= srt / 15

    x_new = max(x_new, 10)

    return nh4_new, no2_new, no3_new, hco3_new, x_new, activity
