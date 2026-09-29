import pandas as pd
import pytest

from core.early_warning import EarlyWarningConfig, normalize_columns, run_early_warning, template_dataframe
from core.self_control import ControllerSettings, PIController, recommend_rules


def _stable(n=20):
    return pd.DataFrame({"day": range(1, n + 1), "nh4_in": 200.0, "nh4_out": 20.0,
                         "no2_out": 2.0, "no3_out": 20.0 + 0.2 * (pd.Series(range(n)) % 3)})


def test_stable_data_is_normal():
    res = run_early_warning(_stable())
    assert res.status == "normal"
    assert res.data["no3_ratio"].iloc[-1] == pytest.approx(0.112, abs=0.01)


def test_nob_outbreak_raises_alarm():
    d = _stable(25)
    d.loc[d.index[-3:], "no3_out"] = [45.0, 60.0, 80.0]
    res = run_early_warning(d)
    assert res.status == "alarm"


def test_missing_columns_raise():
    with pytest.raises(ValueError):
        run_early_warning(pd.DataFrame({"day": [1, 2], "nh4_in": [1, 2]}))


def test_normalize_operation_log_names():
    raw = pd.DataFrame({"duration_days": [1], "nh4_influent_mg_l": [200], "reactor1_effluent_mg_l": [20],
                        "no3_effluent_mg_l": [22], "do_mg_l": [0.3]})
    out = normalize_columns(raw)
    assert {"day", "nh4_in", "nh4_out", "no3_out", "do"} <= set(out.columns)


def test_template_is_valid_input():
    res = run_early_warning(template_dataframe(), EarlyWarningConfig())
    assert res.status in ("normal", "watch", "warning", "alarm")


def test_rules_lower_do_on_nob():
    act = recommend_rules({"no3_ratio": 0.25, "no2_out": 1.0, "nh4_out": 10.0}, 0.4)
    assert act.do_setpoint < 0.4


def test_rules_raise_do_when_aob_limited():
    act = recommend_rules({"no3_ratio": 0.10, "no2_out": 1.0, "nh4_out": 80.0}, 0.2)
    assert act.do_setpoint > 0.2


def test_rules_respect_bounds():
    s = ControllerSettings()
    act = recommend_rules({"no3_ratio": 0.5, "no2_out": 1.0, "nh4_out": 1.0}, s.do_min, 1.0, s)
    assert act.do_setpoint >= s.do_min
    assert act.aeration_fraction < 1.0


def test_pi_direction():
    pi = PIController()
    assert pi.step({"no3_ratio": 0.11, "nh4_out": 40.0}, 0.3).do_setpoint > 0.3
