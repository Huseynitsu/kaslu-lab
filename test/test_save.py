from core.database import save_experiment
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

save_experiment(
    config,
    final_nh4=0.5,
    final_no2=0.7,
    final_no3=12.3,
    final_biomass=900,
    stability=0.95
)

print("Experiment saved")