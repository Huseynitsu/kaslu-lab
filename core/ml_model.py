import pandas as pd

from sklearn.model_selection import train_test_split

from sklearn.ensemble import (
    RandomForestRegressor,
    RandomForestClassifier
)

from sklearn.metrics import (
    mean_squared_error,
    accuracy_score,
    r2_score
)


class AnammoxMLModel:

    def __init__(self):

        self.no3_model = RandomForestRegressor(
            n_estimators=300,
            max_depth=12,
            random_state=42
        )

        self.stability_model = RandomForestClassifier(
            n_estimators=300,
            max_depth=10,
            random_state=42
        )

    def train(self, df: pd.DataFrame):

        # ==================================
        # FEATURES
        # ==================================

        X = df[[

            "NH4_init",
            "NO2_init",
            "NO3_init",

            "HCO3_init",

            "pH",
            "Temperature",
            "DO",

            "SRT",

            "Biomass_init"

        ]]

        # ==================================
        # TARGETS
        # ==================================

        y_no3 = df["NO3_final"]

        y_stability = (
            df["Stability"] >= 0.70
        ).astype(int)

        # ==================================
        # SPLIT
        # ==================================

        (
            X_train,
            X_test,
            y_no3_train,
            y_no3_test
        ) = train_test_split(
            X,
            y_no3,
            test_size=0.20,
            random_state=42
        )

        (
            _,
            _,
            y_stab_train,
            y_stab_test
        ) = train_test_split(
            X,
            y_stability,
            test_size=0.20,
            random_state=42
        )

        # ==================================
        # TRAIN
        # ==================================

        self.no3_model.fit(
            X_train,
            y_no3_train
        )

        self.stability_model.fit(
            X_train,
            y_stab_train
        )

        # ==================================
        # EVALUATION
        # ==================================

        no3_pred = self.no3_model.predict(
            X_test
        )

        stab_pred = self.stability_model.predict(
            X_test
        )

        mse = mean_squared_error(
            y_no3_test,
            no3_pred
        )

        r2 = r2_score(
            y_no3_test,
            no3_pred
        )

        acc = accuracy_score(
            y_stab_test,
            stab_pred
        )

        print("\n======================")
        print("MODEL RESULTS")
        print("======================")

        print(
            "NO3 MSE:",
            round(mse, 4)
        )

        print(
            "NO3 R2:",
            round(r2, 4)
        )

        print(
            "Stability Accuracy:",
            round(acc, 4)
        )

    def predict(
        self,
        input_data: pd.DataFrame
    ):

        no3 = self.no3_model.predict(
            input_data
        )

        stability = self.stability_model.predict(
            input_data
        )

        return (
            no3,
            stability
        )