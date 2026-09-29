import pandas as pd

from core.pn_config import PNConfig
from core.pn_model import pn_reactor_config
from core.pna_model import simulate


def simulate_pn_30_days(config: PNConfig) -> pd.DataFrame:
    """PN reactor simulation (batch, or CSTR when hrt_days > 0 and influent_nh4 > 0)."""
    cfg = pn_reactor_config(
        config.nh4, config.no2, config.no3, config.ph, config.temperature, config.do,
        config.x_aob, config.x_nob, config.srt,
        days=getattr(config, "days", 30),
        influent_nh4=config.influent_nh4, hrt_days=config.hrt_days,
    )
    df = simulate(cfg)
    df = df[df["Day"] >= 1].reset_index(drop=True)
    df["Day"] = df["Day"].round().astype(int)
    df["NAR"] = df["NAR"].fillna(0.0)
    return df[["Day", "NH4", "NO2", "NO3", "AOB", "NOB", "NAR", "FA", "FNA", "NH4_removal_pct"]]
