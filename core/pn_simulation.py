import pandas as pd

from core.pn_model import partial_nitritation_step
from core.pn_config import PNConfig


def simulate_pn_30_days(
    config: PNConfig
):

    nh4 = config.nh4
    no2 = config.no2
    no3 = config.no3

    x_aob = config.x_aob
    x_nob = config.x_nob

    days = []

    nh4_history = []
    no2_history = []
    no3_history = []

    aob_history = []
    nob_history = []

    nar_history = []

    for day in range(1, 31):

        (
            nh4,
            no2,
            no3,
            x_aob,
            x_nob,
            nar
        ) = partial_nitritation_step(

            nh4=nh4,
            no2=no2,
            no3=no3,

            ph=config.ph,
            temperature=config.temperature,
            do=config.do,

            x_aob=x_aob,
            x_nob=x_nob,

            srt=config.srt,
            influent_nh4=config.influent_nh4 if config.hrt_days <= 0 else 0.0,
        )

        if config.hrt_days > 0 and config.influent_nh4 > 0:
            tau = config.hrt_days
            nh4 = nh4 + (config.influent_nh4 - nh4) / tau
            no2 = no2 * (1.0 - 1.0 / tau)
            no3 = no3 * (1.0 - 1.0 / tau)

        days.append(day)

        nh4_history.append(nh4)
        no2_history.append(no2)
        no3_history.append(no3)

        aob_history.append(x_aob)
        nob_history.append(x_nob)

        nar_history.append(nar)

    return pd.DataFrame({

        "Day": days,

        "NH4": nh4_history,
        "NO2": no2_history,
        "NO3": no3_history,

        "AOB": aob_history,
        "NOB": nob_history,

        "NAR": nar_history
    })