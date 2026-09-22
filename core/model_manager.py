import os
import joblib


# =====================================
# PROJECT ROOT
# =====================================

PROJECT_ROOT = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        ".."
    )
)

MODEL_DIR = os.path.join(
    PROJECT_ROOT,
    "models"
)

MODEL_PATH = os.path.join(
    MODEL_DIR,
    "hybrid_model.pkl"
)


# =====================================
# SAVE MODEL
# =====================================

def save_model(model):

    os.makedirs(
        MODEL_DIR,
        exist_ok=True
    )

    joblib.dump(
        model,
        MODEL_PATH
    )

    print(
        f"Model saved → {MODEL_PATH}"
    )


# =====================================
# LOAD MODEL
# =====================================

def load_model():

    if not os.path.exists(
        MODEL_PATH
    ):

        print(
            "No trained model found."
        )

        return None

    try:

        model = joblib.load(
            MODEL_PATH
        )

        return model

    except Exception as e:

        print(
            f"Model loading failed: {e}"
        )

        return None


# =====================================
# INFO
# =====================================

def model_exists():

    return os.path.exists(
        MODEL_PATH
    )