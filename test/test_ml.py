import sys
import os

PROJECT_ROOT = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        ".."
    )
)

sys.path.append(PROJECT_ROOT)

from core.dataset_builder import build_dataset
from core.ml_model import AnammoxMLModel

df = build_dataset(100)

model = AnammoxMLModel()

model.train(df)

sample = df.iloc[:5]

X = sample[[
    "NH4_init",
    "NO2_init",
    "pH",
    "Temperature",
    "DO",
    "SRT",
    "Biomass_init"
]]

pred_no3, pred_stability = model.predict(X)

print(pred_no3)
print(pred_stability)