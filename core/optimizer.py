from core.config import ExperimentConfig
from core.simulation import simulate_30_days


def optimize_parameters(
    nh4,
    no2,
    biomass,
    hco3=120
):

    best_score = -999999

    best_result = None

    ph_values = [

        7.0,
        7.2,
        7.4,
        7.6,
        7.8,
        8.0

    ]

    temp_values = [

        25,
        28,
        30,
        32,
        35,
        38,
        40

    ]

    do_values = [

        0.1,
        0.2,
        0.3,
        0.5,
        0.8

    ]

    srt_values = [

        15,
        20,
        25,
        30,
        35

    ]

    for ph in ph_values:

        for temp in temp_values:

            for do in do_values:

                for srt in srt_values:

                    config = ExperimentConfig(

                        nh4=nh4,
                        no2=no2,
                        hco3=hco3,

                        ph=ph,
                        temperature=temp,
                        do=do,

                        x_anammox=biomass,

                        srt=srt
                    )

                    df = simulate_30_days(
                        config
                    )

                    final = df.iloc[-1]

                    # ==========================
                    # PERFORMANCE
                    # ==========================

                    nh4_removal = (

                        (
                            nh4 -
                            final["NH4"]
                        )
                        /
                        max(nh4, 1)

                    )

                    no2_removal = (

                        (
                            no2 -
                            final["NO2"]
                        )
                        /
                        max(no2, 1)

                    )

                    stability = (
                        final["Stability"]
                    )

                    no3_penalty = (

                        final["NO3"]
                        /
                        max(nh4, 1)

                    )

                    # ==========================
                    # OBJECTIVE FUNCTION
                    # ==========================

                    score = (

                        nh4_removal * 0.40 +

                        no2_removal * 0.30 +

                        stability * 0.25 -

                        no3_penalty * 0.05

                    )

                    if score > best_score:

                        best_score = score

                        best_result = {

                            "Score":
                                round(score, 4),

                            "pH":
                                ph,

                            "Temperature":
                                temp,

                            "DO":
                                do,

                            "SRT":
                                srt,

                            "NH4 Removal":
                                round(
                                    nh4_removal,
                                    4
                                ),

                            "NO2 Removal":
                                round(
                                    no2_removal,
                                    4
                                ),

                            "Final NH4":
                                round(
                                    final["NH4"],
                                    4
                                ),

                            "Final NO2":
                                round(
                                    final["NO2"],
                                    4
                                ),

                            "Final NO3":
                                round(
                                    final["NO3"],
                                    4
                                ),

                            "Final Biomass":
                                round(
                                    final["Biomass"],
                                    4
                                ),

                            "Stability":
                                round(
                                    stability,
                                    4
                                )
                        }

    return best_result