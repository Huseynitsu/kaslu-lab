import pandas as pd

from core.model_manager import load_model


def predict_anammox(

    nh4,
    no2,
    hco3,

    ph,
    temperature,
    do,

    srt,
    biomass

):

    model = load_model()

    if model is None:

        raise Exception(
            "No trained model found."
        )

    input_df = pd.DataFrame([{

        "NH4_init": nh4,
        "NO2_init": no2,

        "HCO3_init": hco3,

        "pH": ph,
        "Temperature": temperature,
        "DO": do,

        "SRT": srt,

        "Biomass_init": biomass

    }])

    result = model.predict(
        input_df
    )

    return {

        "mechanistic_no3":
            float(
                result[
                    "mechanistic_no3"
                ].iloc[0]
            ),

        "ml_no3":
            float(
                result[
                    "ml_no3"
                ][0]
            ),

        "prediction_gap":
            float(
                result[
                    "prediction_gap"
                ][0]
            ),

        "stability":
            int(
                result[
                    "stability"
                ][0]
            )

    }