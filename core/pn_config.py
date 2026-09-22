from dataclasses import dataclass


@dataclass
class PNConfig:

    # ==========================
    # INFLUENT NITROGEN
    # ==========================

    nh4: float = 100.0
    no2: float = 0.0
    no3: float = 0.0

    x_aob: float = 150.0
    x_nob: float = 50.0

    # ==========================
    # REACTOR CONDITIONS
    # ==========================

    ph: float = 7.8

    temperature: float = 35.0

    do: float = 0.8

    # ==========================
    # RETENTION
    # ==========================

    srt: float = 5.0

    influent_nh4: float = 0.0
    hrt_days: float = 0.0