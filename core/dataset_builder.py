import random
import pandas as pd

from core.config import ExperimentConfig
from core.simulation import simulate_30_days


def generate_random_config():

    return ExperimentConfig(

        # PN effluent

        nh4=random.uniform(
            20,
            120
        ),

        no2=random.uniform(
            25,
            160
        ),

        # alkalinity

        hco3=random.uniform(
            80,
            300
        ),

        # reactor conditions

        ph=random.uniform(
            7.0,
            8.5
        ),

        temperature=random.uniform(
            25,
            40
        ),

        do=random.uniform(
            0.0,
            0.5
        ),

        # biomass

        x_anammox=random.uniform(
            500,
            5000
        ),

        # UASB sludge retention

        srt=random.uniform(
            20,
            100
        )
    )


def build_dataset(
    n_samples=1000
):

    dataset_rows = []

    for i in range(n_samples):

        config = generate_random_config()

        df = simulate_30_days(
            config
        )

        final_row = df.iloc[-1]

        dataset_rows.append({

            # =====================
            # INPUTS
            # =====================

            "NH4_init":
                config.nh4,

            "NO2_init":
                config.no2,

            "HCO3_init":
                config.hco3,

            "pH":
                config.ph,

            "Temperature":
                config.temperature,

            "DO":
                config.do,

            "Biomass_init":
                config.x_anammox,

            "SRT":
                config.srt,

            # =====================
            # OUTPUTS
            # =====================

            "NH4_final":
                final_row["NH4"],

            "NO2_final":
                final_row["NO2"],

            "NO3_final":
                final_row["NO3"],

            "HCO3_final":
                final_row["HCO3"],

            "Biomass_final":
                final_row["Biomass"],

            "Stability":
                final_row["Stability"]
        })

        print(
            f"Sample {i + 1}/{n_samples}"
        )

    return pd.DataFrame(
        dataset_rows
    )


def save_dataset(
    df,
    filename="anammox_dataset.csv"
):

    df.to_csv(
        filename,
        index=False
    )

    print(
        f"Dataset saved -> {filename}"
    )