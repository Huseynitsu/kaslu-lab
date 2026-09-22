import sys
import os

PROJECT_ROOT = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        ".."
    )
)

sys.path.append(PROJECT_ROOT)

from core.optimizer import (
    optimize_parameters
)

result = optimize_parameters(
    nh4=50,
    no2=66,
    biomass=800
)

print(result)