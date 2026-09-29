from dataclasses import dataclass


@dataclass
class PNConfig:
    """Partial nitritation (two-stage, suspended sludge). ``hrt_days<=0`` → batch."""

    nh4: float = 100.0
    no2: float = 0.0
    no3: float = 0.0

    x_aob: float = 150.0
    x_nob: float = 50.0

    ph: float = 7.8
    temperature: float = 35.0
    do: float = 0.8

    srt: float = 2.0

    influent_nh4: float = 0.0
    hrt_days: float = 0.0
    days: int = 30
