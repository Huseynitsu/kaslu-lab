import pandas as pd

from core.dataset_builder import build_dataset
from core.ml_model import AnammoxMLModel
from core.hybrid_model import HybridModel

df = build_dataset(100)

ml_model = AnammoxMLModel()
ml_model.train(df)

hybrid = HybridModel(ml_model)

sample = df[[
    "NH4_init",
    "NO2_init",
    "pH",
    "Temperature",
    "DO",
    "SRT",
    "Biomass_init"
]].head(5)

result = hybrid.predict(sample)

print(result)