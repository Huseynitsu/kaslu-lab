import numpy as np

from core.config import ExperimentConfig
from core.pn_config import PNConfig
from core.pn_simulation import simulate_pn_30_days
from core.pna_model import ReactorConfig, simulate
from core.simulation import simulate_30_days


def test_legacy_simulation_columns():
    df = simulate_30_days(ExperimentConfig())
    for c in ("Day", "NH4", "NO2", "NO3", "HCO3", "Biomass", "Activity", "Stability"):
        assert c in df.columns
    assert len(df) == 30
    assert df["Stability"].between(0, 1).all()


def test_anammox_batch_consumes_substrates_quickly():
    # unit bug regression: 800 mg VSS/L must remove the 50/66 feed within a day, not ~0.4 mg/L/d
    df = simulate_30_days(ExperimentConfig(do=0.0))
    assert df.iloc[0]["NH4"] < 5


def test_pn_simulation_runs_and_nar_defined():
    df = simulate_pn_30_days(PNConfig(nh4=100, influent_nh4=500, hrt_days=1.5, srt=1.5))
    assert df["NAR"].between(0, 1).all()
    assert df.iloc[-1]["NAR"] > 0.9


def test_vectorised_scenarios_match_single_runs():
    cfg = ReactorConfig(days=10, dt_min=15.0)
    runs = simulate(cfg, overrides={"do": np.array([0.2, 0.3])})
    single = simulate(ReactorConfig(days=10, dt_min=15.0, do=0.3))
    assert abs(runs[1].iloc[-1]["NH4"] - single.iloc[-1]["NH4"]) < 1e-9


def test_concentrations_never_negative():
    df = simulate(ReactorConfig(days=20, do=2.0, dt_min=15.0))
    assert (df[["NH4", "NO2", "NO3", "AOB", "NOB", "AMX"]] >= 0).all().all()
