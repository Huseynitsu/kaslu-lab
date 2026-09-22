import pandas as pd

from core.ml_model import AnammoxMLModel

from core.anammox_model import (
    mechanistic_prediction
)


class HybridModel:

    def __init__(
        self,
        ml_model: AnammoxMLModel
    ):

        self.ml_model = ml_model

    def predict(
        self,
        input_df: pd.DataFrame
    ):

        # ==================================
        # MECHANISTIC PREDICTION
        # ==================================

        mechanistic_no3 = input_df.apply(

            lambda row:

            mechanistic_prediction(

                row["NH4_init"],
                row["NO2_init"]

            ),

            axis=1

        )

        # ==================================
        # MACHINE LEARNING PREDICTION
        # ==================================

        ml_no3, stability = (
            self.ml_model.predict(
                input_df
            )
        )

        # ==================================
        # DIFFERENCE ANALYSIS
        # ==================================

        prediction_gap = (
            ml_no3 -
            mechanistic_no3.values
        )

        # ==================================
        # RETURN
        # ==================================

        return {

            "mechanistic_no3":
                mechanistic_no3,

            "ml_no3":
                ml_no3,

            "prediction_gap":
                prediction_gap,

            "stability":
                stability

        }