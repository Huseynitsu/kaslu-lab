import sys
import os

PROJECT_ROOT = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        ".."
    )
)

sys.path.append(PROJECT_ROOT)

from core.prediction_service import (
    predict_reactor
)

result = predict_reactor(
    nh4=50,
    no2=66,
    ph=7.8,
    temperature=35,
    do=0.8,
    biomass=800,
    srt=20
)

print(result)