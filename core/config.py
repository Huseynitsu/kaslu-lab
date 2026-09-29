from dataclasses import dataclass


@dataclass
class ExperimentConfig:
    """Anammox-stage (or PN/A) experiment. ``hrt_d=None`` → batch; otherwise continuous."""

    nh4: float = 50.0
    no2: float = 66.0
    no3: float = 0.0
    hco3: float = 120.0
    ph: float = 7.8
    temperature: float = 35.0
    do: float = 0.05
    x_anammox: float = 800.0
    srt: float = 30.0
    # continuous operation (optional)
    hrt_d: float | None = None
    nh4_in: float | None = None
    no2_in: float | None = None
    no3_in: float = 0.0
