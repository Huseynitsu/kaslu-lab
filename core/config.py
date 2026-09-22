from dataclasses import dataclass


@dataclass
class ExperimentConfig:
    nh4: float = 50.0
    no2: float = 66.0
    no3: float = 0.0
    hco3: float = 120.0
    ph: float = 7.8
    temperature: float = 35.0
    do: float = 0.8
    x_anammox: float = 800.0
    srt: float = 20.0
