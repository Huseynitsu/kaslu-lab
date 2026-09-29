"""
Early-warning system for one-stage PN/A (thesis module).

Pipeline
--------
1. Process indicators from daily influent/effluent data
   (TIN removal, NLR/NRR, ΔNO3/ΔNH4, effluent NO2, residual NH4, FA/FNA).
2. Rule layer — literature-based thresholds (Strous stoichiometry: ΔNO3/ΔNH4 ≈ 0.11).
3. Statistical layer — EWMA control charts (univariate, direction-aware) and Hotelling T²
   (multivariate) against a baseline period of stable operation.
4. Forecast layer — local linear trend of ΔNO3/ΔNH4 and TIN removal → "days until alarm"
   (the early-warning lead time).

No external ML libraries are needed (runs on Streamlit Cloud as-is). The statistical layer is
the "AI" baseline to which more complex models (LSTM, autoencoder) can be compared in the thesis.

Input columns (canonical, mg N/L unless noted):
    day, nh4_in, nh4_out, no2_in, no2_out, no3_in, no3_out,
    optional: do, ph, temperature, hrt_h, tn_in, tn_out
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from core.chemistry import free_ammonia_as_molecule, free_nitrous_acid_as_molecule
from core.constants import (
    PNA_NO2_EFFLUENT_ALARM,
    PNA_NO2_EFFLUENT_WARNING,
    PNA_NO3_PER_NH4_REMOVED,
    PNA_NO3_RATIO_ALARM,
    PNA_NO3_RATIO_WARNING,
    PNA_RESIDUAL_NH4_MIN,
)

CANONICAL = ["day", "nh4_in", "nh4_out", "no2_in", "no2_out", "no3_in", "no3_out",
             "do", "ph", "temperature", "hrt_h", "tn_in", "tn_out"]
REQUIRED = ["nh4_in", "nh4_out", "no3_out"]

# indicator -> direction that is "bad" (+1 increase is bad, -1 decrease is bad)
MONITORED = {
    "no3_ratio": +1,
    "tin_removal_pct": -1,
    "no2_out": +1,
    "nh4_out": +1,
}
# Smallest meaningful standard deviation per indicator (analytical noise floor). Prevents
# control limits from becoming unrealistically tight when the baseline is very quiet.
MIN_SIGMA = {"no3_ratio": 0.01, "tin_removal_pct": 1.0, "no2_out": 0.5, "nh4_out": 0.5}

LEVELS = ["normal", "watch", "warning", "alarm"]


@dataclass
class EarlyWarningConfig:
    no3_ratio_target: float = PNA_NO3_PER_NH4_REMOVED
    no3_ratio_warning: float = PNA_NO3_RATIO_WARNING
    no3_ratio_alarm: float = PNA_NO3_RATIO_ALARM
    no2_warning: float = PNA_NO2_EFFLUENT_WARNING
    no2_alarm: float = PNA_NO2_EFFLUENT_ALARM
    residual_nh4_min: float = PNA_RESIDUAL_NH4_MIN
    tin_removal_warning: float = 60.0      # % — reactor-specific, set from your own baseline
    baseline_days: int = 14
    ewma_lambda: float = 0.3
    ewma_L: float = 3.0
    trend_window: int = 7
    forecast_horizon_days: int = 7
    default_ph: float = 7.5
    default_temperature: float = 30.0


@dataclass
class Signal:
    day: float
    level: str
    source: str   # rule | ewma | t2 | forecast
    indicator: str
    message: str


@dataclass
class EarlyWarningResult:
    data: pd.DataFrame
    signals: list[Signal]
    status: str
    risk_score: float
    reasons: list[str]
    forecast: dict = field(default_factory=dict)
    baseline: dict = field(default_factory=dict)


# ---------------------------------------------------------------------------
# 1. Indicators
# ---------------------------------------------------------------------------
def compute_indicators(df: pd.DataFrame, cfg: EarlyWarningConfig | None = None) -> pd.DataFrame:
    cfg = cfg or EarlyWarningConfig()
    d = df.copy()
    for c in CANONICAL:
        if c not in d.columns:
            d[c] = np.nan
    if d["day"].isna().all():
        d["day"] = np.arange(1, len(d) + 1, dtype=float)
    for c in ("no2_in", "no3_in"):
        d[c] = d[c].fillna(0.0)
    d["no2_out"] = d["no2_out"].fillna(0.0)
    d = d.sort_values("day").reset_index(drop=True)

    d["tin_in"] = d["nh4_in"] + d["no2_in"] + d["no3_in"]
    d["tin_out"] = d["nh4_out"] + d["no2_out"] + d["no3_out"]
    d["nh4_removed"] = d["nh4_in"] - d["nh4_out"]
    d["nh4_removal_pct"] = 100.0 * d["nh4_removed"] / d["nh4_in"].where(d["nh4_in"] > 0)
    d["tin_removal_pct"] = 100.0 * (d["tin_in"] - d["tin_out"]) / d["tin_in"].where(d["tin_in"] > 0)
    d["no3_produced"] = d["no3_out"] - d["no3_in"]
    d["no3_ratio"] = (d["no3_produced"] / d["nh4_removed"]).where(d["nh4_removed"] > 1.0)
    hrt_d = d["hrt_h"] / 24.0
    d["nlr"] = (d["tin_in"] / hrt_d / 1000.0).where(hrt_d > 0)                       # kg N/m3/d
    d["nrr"] = ((d["tin_in"] - d["tin_out"]) / hrt_d / 1000.0).where(hrt_d > 0)
    ph = d["ph"].fillna(cfg.default_ph)
    temp = d["temperature"].fillna(cfg.default_temperature)
    d["fa_nh3"] = [free_ammonia_as_molecule(n, p, t) for n, p, t in zip(d["nh4_out"].fillna(0), ph, temp)]
    d["fna_hno2"] = [free_nitrous_acid_as_molecule(n, p, t) for n, p, t in zip(d["no2_out"].fillna(0), ph, temp)]
    return d


# ---------------------------------------------------------------------------
# 2. Rule layer
# ---------------------------------------------------------------------------
def rule_signals(d: pd.DataFrame, cfg: EarlyWarningConfig) -> list[Signal]:
    out: list[Signal] = []
    for _, r in d.iterrows():
        day = float(r["day"])
        ratio = r["no3_ratio"]
        if pd.notna(ratio):
            if ratio >= cfg.no3_ratio_alarm:
                out.append(Signal(day, "alarm", "rule", "no3_ratio",
                                  f"ΔNO3/ΔNH4 = {ratio:.3f} ≥ {cfg.no3_ratio_alarm} — NOB proliferation."))
            elif ratio >= cfg.no3_ratio_warning:
                out.append(Signal(day, "warning", "rule", "no3_ratio",
                                  f"ΔNO3/ΔNH4 = {ratio:.3f} ≥ {cfg.no3_ratio_warning} — NOB activity rising."))
        no2 = r["no2_out"]
        if pd.notna(no2):
            if no2 >= cfg.no2_alarm:
                out.append(Signal(day, "alarm", "rule", "no2_out",
                                  f"Effluent NO2 = {no2:.1f} mg N/L — anammox inhibition risk."))
            elif no2 >= cfg.no2_warning:
                out.append(Signal(day, "warning", "rule", "no2_out",
                                  f"Effluent NO2 = {no2:.1f} mg N/L — nitritation exceeds anammox capacity."))
        nh4 = r["nh4_out"]
        if pd.notna(nh4) and nh4 < cfg.residual_nh4_min and pd.notna(ratio) and ratio > cfg.no3_ratio_target * 1.2:
            out.append(Signal(day, "watch", "rule", "nh4_out",
                              f"Residual NH4 {nh4:.1f} mg N/L with rising NO3 — over-aeration."))
        tin = r["tin_removal_pct"]
        if pd.notna(tin) and tin < cfg.tin_removal_warning:
            out.append(Signal(day, "warning", "rule", "tin_removal_pct",
                              f"TIN removal {tin:.0f}% < {cfg.tin_removal_warning:.0f}%."))
    return out


# ---------------------------------------------------------------------------
# 3. Statistical layer
# ---------------------------------------------------------------------------
def _robust_stats(x: pd.Series, floor: float = 0.0) -> tuple[float, float]:
    x = x.dropna()
    if len(x) < 3:
        return float("nan"), float("nan")
    med = float(x.median())
    mad = float((x - med).abs().median()) * 1.4826
    sd = float(x.std(ddof=1))
    sigma = mad if mad > 1e-9 else sd
    return med, max(sigma, floor, 1e-6)


def ewma_chart(x: pd.Series, mu: float, sigma: float, lam: float, L: float) -> pd.DataFrame:
    z = []
    prev = mu
    for v in x:
        cur = prev if pd.isna(v) else lam * v + (1 - lam) * prev
        z.append(cur)
        prev = cur
    z = np.asarray(z)
    k = np.arange(1, len(z) + 1)
    width = L * sigma * np.sqrt(lam / (2 - lam) * (1 - (1 - lam) ** (2 * k)))
    return pd.DataFrame({"ewma": z, "ucl": mu + width, "lcl": mu - width})


def _chi2_quantile(p: float, dof: int) -> float:
    """Wilson–Hilferty approximation of the chi-square quantile (no SciPy needed)."""
    # inverse standard normal via Acklam-like rational approximation (sufficient here)
    from statistics import NormalDist
    z = NormalDist().inv_cdf(p)
    return dof * (1 - 2 / (9 * dof) + z * math.sqrt(2 / (9 * dof))) ** 3


def statistical_signals(d: pd.DataFrame, cfg: EarlyWarningConfig) -> tuple[list[Signal], dict, pd.DataFrame]:
    out: list[Signal] = []
    n_base = min(cfg.baseline_days, max(len(d) // 2, 0))
    base = d.iloc[:n_base]
    baseline: dict = {"n": n_base}
    charts = pd.DataFrame({"day": d["day"]})
    if n_base < 5:
        baseline["note"] = "Baseline too short (<5 days) — statistical layer disabled."
        return out, baseline, charts

    for ind, bad_dir in MONITORED.items():
        mu, sigma = _robust_stats(base[ind], MIN_SIGMA.get(ind, 0.0))
        if not np.isfinite(mu):
            continue
        baseline[ind] = {"median": mu, "sigma": sigma}
        ch = ewma_chart(d[ind], mu, sigma, cfg.ewma_lambda, cfg.ewma_L)
        charts[f"{ind}_ewma"] = ch["ewma"].values
        charts[f"{ind}_ucl"] = ch["ucl"].values
        charts[f"{ind}_lcl"] = ch["lcl"].values
        for i in range(n_base, len(d)):
            z, u, l = ch.iloc[i]
            if (bad_dir > 0 and z > u) or (bad_dir < 0 and z < l):
                out.append(Signal(float(d["day"].iloc[i]), "watch", "ewma", ind,
                                  f"EWMA of {ind} left its control band (baseline {mu:.3g} ± {sigma:.2g})."))

    feats = [c for c in MONITORED if c in baseline]
    if len(feats) >= 2:
        X0 = base[feats].dropna()
        if len(X0) >= 5 * len(feats):
            mu = X0.mean().values
            floors = np.array([MIN_SIGMA.get(f, 0.0) ** 2 for f in feats])
            S = np.cov(X0.values, rowvar=False) + np.diag(floors)
            Sinv = np.linalg.pinv(S)
            thr = _chi2_quantile(0.99, len(feats))
            t2 = []
            for _, r in d[feats].iterrows():
                if r.isna().any():
                    t2.append(np.nan)
                    continue
                v = r.values - mu
                t2.append(float(v @ Sinv @ v))
            charts["t2"] = t2
            charts["t2_limit"] = thr
            baseline["t2_limit"] = thr
            for i in range(n_base, len(d)):
                if pd.notna(t2[i]) and t2[i] > thr:
                    out.append(Signal(float(d["day"].iloc[i]), "watch", "t2", "multivariate",
                                      f"Hotelling T² = {t2[i]:.1f} > {thr:.1f} — joint pattern differs from baseline."))
    return out, baseline, charts


# ---------------------------------------------------------------------------
# 4. Forecast layer
# ---------------------------------------------------------------------------
def linear_trend(days: pd.Series, values: pd.Series) -> tuple[float, float, float]:
    m = values.notna() & days.notna()
    x, y = days[m].values.astype(float), values[m].values.astype(float)
    if len(x) < 3 or np.ptp(x) == 0:
        return float("nan"), float("nan"), float("nan")
    slope, intercept = np.polyfit(x, y, 1)
    pred = slope * x + intercept
    ss_tot = ((y - y.mean()) ** 2).sum()
    r2 = 1 - ((y - pred) ** 2).sum() / ss_tot if ss_tot > 0 else 0.0
    return float(slope), float(intercept), float(r2)


def forecast_threshold_crossing(d: pd.DataFrame, cfg: EarlyWarningConfig) -> dict:
    tail = d.tail(cfg.trend_window)
    res: dict = {}
    slope, icpt, r2 = linear_trend(tail["day"], tail["no3_ratio"])
    last_day = float(d["day"].iloc[-1])
    if np.isfinite(slope):
        now = slope * last_day + icpt
        res["no3_ratio"] = {"slope_per_day": slope, "r2": r2, "fitted_now": now}
        if slope > 0 and now < cfg.no3_ratio_alarm:
            res["no3_ratio"]["days_to_alarm"] = (cfg.no3_ratio_alarm - now) / slope
        if slope > 0 and now < cfg.no3_ratio_warning:
            res["no3_ratio"]["days_to_warning"] = (cfg.no3_ratio_warning - now) / slope
    slope, icpt, r2 = linear_trend(tail["day"], tail["tin_removal_pct"])
    if np.isfinite(slope):
        now = slope * last_day + icpt
        res["tin_removal_pct"] = {"slope_per_day": slope, "r2": r2, "fitted_now": now}
        if slope < 0 and now > cfg.tin_removal_warning:
            res["tin_removal_pct"]["days_to_warning"] = (now - cfg.tin_removal_warning) / -slope
    return res


def forecast_signals(fc: dict, d: pd.DataFrame, cfg: EarlyWarningConfig) -> list[Signal]:
    out = []
    day = float(d["day"].iloc[-1])
    r = fc.get("no3_ratio", {})
    for key, lvl in (("days_to_alarm", "warning"), ("days_to_warning", "watch")):
        t = r.get(key)
        if t is not None and t <= cfg.forecast_horizon_days and r.get("r2", 0) >= 0.5:
            out.append(Signal(day, lvl, "forecast", "no3_ratio",
                              f"ΔNO3/ΔNH4 trend (+{r['slope_per_day']:.4f}/d, R²={r['r2']:.2f}) reaches "
                              f"{key.split('_')[-1]} threshold in ≈{t:.1f} d."))
            break
    t = fc.get("tin_removal_pct", {}).get("days_to_warning")
    if t is not None and t <= cfg.forecast_horizon_days and fc["tin_removal_pct"].get("r2", 0) >= 0.5:
        out.append(Signal(day, "watch", "forecast", "tin_removal_pct",
                          f"TIN removal declining — below {cfg.tin_removal_warning:.0f}% in ≈{t:.1f} d."))
    return out


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------
def run_early_warning(df: pd.DataFrame, cfg: EarlyWarningConfig | None = None) -> EarlyWarningResult:
    cfg = cfg or EarlyWarningConfig()
    missing = [c for c in REQUIRED if c not in df.columns or df[c].isna().all()]
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")
    d = compute_indicators(df, cfg)
    signals = rule_signals(d, cfg)
    stat, baseline, charts = statistical_signals(d, cfg)
    signals += stat
    fc = forecast_threshold_crossing(d, cfg)
    signals += forecast_signals(fc, d, cfg)
    d = d.merge(charts, on="day", how="left")

    last_day = float(d["day"].iloc[-1])
    current = [s for s in signals if s.day == last_day]
    status = "normal"
    for s in current:
        if LEVELS.index(s.level) > LEVELS.index(status):
            status = s.level
    # risk score: 0–100 from latest indicators
    last = d.iloc[-1]
    score = 0.0
    if pd.notna(last["no3_ratio"]):
        score += 50 * min(max((last["no3_ratio"] - cfg.no3_ratio_target) /
                              max(cfg.no3_ratio_alarm - cfg.no3_ratio_target, 1e-9), 0), 1)
    if pd.notna(last["no2_out"]):
        score += 30 * min(max(last["no2_out"] / cfg.no2_alarm, 0), 1)
    score += 20 * min(len([s for s in current if s.source in ("ewma", "t2", "forecast")]) / 3, 1)
    reasons = list(dict.fromkeys(s.message for s in current)) or ["All indicators within their normal range."]
    return EarlyWarningResult(d, signals, status, round(score, 1), reasons, fc, baseline)


def first_detection_day(result: EarlyWarningResult, min_level: str = "watch") -> float | None:
    days = [s.day for s in result.signals if LEVELS.index(s.level) >= LEVELS.index(min_level)]
    return min(days) if days else None


# ---------------------------------------------------------------------------
# Input helpers
# ---------------------------------------------------------------------------
def template_dataframe() -> pd.DataFrame:
    return pd.DataFrame({
        "day": [1, 2, 3],
        "nh4_in": [200.0, 200.0, 200.0], "nh4_out": [20.0, 22.0, 19.0],
        "no2_in": [0.0, 0.0, 0.0], "no2_out": [2.0, 2.5, 1.8],
        "no3_in": [0.0, 0.0, 0.0], "no3_out": [21.0, 20.0, 21.5],
        "do": [0.3, 0.3, 0.3], "ph": [7.6, 7.6, 7.5], "temperature": [30.0, 30.0, 30.0],
        "hrt_h": [24.0, 24.0, 24.0],
    })


ALIASES = {
    "day": ["day", "days", "duration_days", "time", "天数"],
    "nh4_in": ["nh4_in", "nh4_influent", "nh4_influent_mg_l", "influent_nh4", "进水氨氮"],
    "nh4_out": ["nh4_out", "nh4_effluent", "reactor1_effluent_mg_l", "effluent_nh4", "出水氨氮"],
    "no2_in": ["no2_in", "no2_influent", "no2_influent_mg_l"],
    "no2_out": ["no2_out", "no2_effluent", "no2_effluent_mg_l"],
    "no3_in": ["no3_in", "no3_influent", "no3_influent_mg_l"],
    "no3_out": ["no3_out", "no3_effluent", "no3_effluent_mg_l"],
    "do": ["do", "do_mg_l", "dissolved_oxygen"],
    "ph": ["ph"],
    "temperature": ["temperature", "temperature_c", "temp", "t"],
    "hrt_h": ["hrt_h", "hrt"],
    "tn_in": ["tn_in", "tn_influent_mg_l"],
    "tn_out": ["tn_out", "tn_effluent_r1_mg_l"],
}


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    lower = {str(c).strip().lower(): c for c in df.columns}
    out = pd.DataFrame(index=df.index)
    for canon, names in ALIASES.items():
        for n in names:
            if n.lower() in lower:
                out[canon] = pd.to_numeric(df[lower[n.lower()]], errors="coerce")
                break
    return out
