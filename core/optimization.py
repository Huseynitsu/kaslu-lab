from core.config import ExperimentConfig
from core.simulation import simulate_30_days


def optimize_reactor():

    best_score = -999999

    best_result = None

    for ph in [

        7.0,
        7.2,
        7.4,
        7.6,
        7.8,
        8.0

    ]:

        for temperature in [

            25,
            28,
            30,
            32,
            35,
            38,
            40

        ]:

            for do in [

                0.1,
                0.2,
                0.3,
                0.5,
                0.8

            ]:

                for biomass in [

                    300,
                    500,
                    800,
                    1200,
                    1500

                ]:

                    for srt in [

                        15,
                        20,
                        25,
                        30,
                        35

                    ]:

                        config = ExperimentConfig(

                            nh4=50,
                            no2=66,
                            hco3=120,

                            ph=ph,
                            temperature=temperature,
                            do=do,

                            x_anammox=biomass,

                            srt=srt
                        )

                        df = simulate_30_days(
                            config
                        )

                        final = df.iloc[-1]

                        # ==================================
                        # PERFORMANCE INDICATORS
                        # ==================================

                        nh4_removal = (

                            (
                                config.nh4 -
                                final["NH4"]
                            )
                            /
                            config.nh4

                        )

                        no2_removal = (

                            (
                                config.no2 -
                                final["NO2"]
                            )
                            /
                            config.no2

                        )

                        stability = (
                            final["Stability"]
                        )

                        no3_penalty = (

                            final["NO3"]
                            /
                            max(
                                config.nh4,
                                1
                            )

                        )

                        # ==================================
                        # OBJECTIVE FUNCTION
                        # ==================================

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
                                    round(
                                        score,
                                        4
                                    ),

                                "pH":
                                    ph,

                                "Temperature":
                                    temperature,

                                "DO":
                                    do,

                                "Biomass":
                                    biomass,

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