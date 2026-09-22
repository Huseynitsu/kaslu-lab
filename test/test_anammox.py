import sys
import os

PROJECT_ROOT = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        ".."
    )
)

sys.path.append(PROJECT_ROOT)

from core.database import get_dashboard_stats

print("SUCCESS")
print(get_dashboard_stats())

from core.config import ExperimentConfig
from core.simulation import simulate_30_days

config = ExperimentConfig(
    nh4=50,
    no2=66,
    ph=7.8,
    temperature=35,
    do=0.8,
    x_anammox=800,
    srt=20
)

df = simulate_30_days(config)

print(df.head())
print(df.tail())