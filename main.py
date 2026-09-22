from core.simulation import simulate_30_days
from core.config import ExperimentConfig


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