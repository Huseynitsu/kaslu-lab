"""
Mechanistic model for partial nitritation (PN), anammox and one-stage PN/A.

Three functional groups compete for substrate and oxygen:
    AOB : NH4+ + 1.5 O2 -> NO2-          (ammonia-oxidizing bacteria)
    NOB : NO2- + 0.5 O2 -> NO3-          (nitrite-oxidizing bacteria)
    AMX : NH4+ + 1.32 NO2- -> N2 + 0.26 NO3- + biomass   (anammox, Strous [1])

Structure follows Hao et al. (2002) [8]: Monod kinetics with oxygen switching functions and
Arrhenius temperature correction; FA/FNA inhibition of AOB/NOB follows Anthonisen [4]
(non-competitive form). Anammox stoichiometry comes from Strous et al. (1998) [1]
(or Lotti et al. 2014 [7], selectable).

Reactor: completely mixed (CSTR / SBR-average) with
    * liquid exchange  (S_in − S) / HRT          (HRT = inf → batch)
    * group-specific biomass retention  X / SRT_g (floc AOB/NOB vs. granule/biofilm AMX)
    * bulk DO prescribed by the (assumed ideal) aeration controller; optional intermittent
      aeration (fraction of time on).

IMPORTANT LIMITATIONS (state these in the thesis):
    * Not spatially resolved: oxygen gradients in granules/biofilm are lumped into an
      *apparent* anammox oxygen constant ``ko_amx`` (intrinsic ≈ 0.01 mg/L [8]).
    * No pH / alkalinity dynamics, no heterotrophs/COD, no N2O.
    * All parameters are literature defaults and MUST be calibrated with your reactor data
      before quantitative use.

Units: solutes mg N/L, biomass mg VSS/L, time d, rates mg/L/d.
Numerics: positivity-preserving Patankar–Euler scheme with fixed step (vectorised over
scenarios so Monte-Carlo / sensitivity runs are cheap).
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace

import numpy as np
import pandas as pd

from core.chemistry import pka_ammonia, pka_nitrous_acid
from core.constants import STOICHIOMETRY_SETS, anammox_yield_vss_per_n

R_GAS = 8.314e-3  # kJ/mol/K
T_REF_C = 30.0
COD_PER_VSS = 1.42


@dataclass
class KineticParameters:
    """Default parameters at 30 °C. Sources: [8] Hao et al. 2002; [1] Strous 1998; [4] Anthonisen."""

    # maximum specific growth rates (1/d) at 30 °C
    mu_aob: float = 2.05        # [8]
    mu_nob: float = 1.45        # [8]
    mu_amx: float = 0.065       # [1] doubling ≈ 11 d (Lotti 2014 [7] reports 0.21 d-1)
    # decay (1/d)
    b_aob: float = 0.13         # [8]
    b_nob: float = 0.06         # [8]
    b_amx: float = 0.003        # [8]
    # yields (g VSS / g N)
    y_aob: float = 0.150 / COD_PER_VSS   # [8] 0.150 g COD/g N
    y_nob: float = 0.041 / COD_PER_VSS   # [8] 0.041 g COD/g N
    # affinity constants (mg/L)
    k_nh4_aob: float = 2.4      # [8]
    k_o_aob: float = 0.3        # [8]
    k_no2_nob: float = 5.5      # [8]
    k_o_nob: float = 1.1        # [8]
    k_nh4_amx: float = 0.07     # [8]
    k_no2_amx: float = 0.05     # [8] (Lotti [7]: 0.035)
    ko_amx: float = 0.2         # APPARENT O2 inhibition constant for granules/biofilm (intrinsic 0.01 [8])
    ki_no2_amx: float = 100.0   # [2] nitrite inhibition of anammox (Haldane), mg N/L
    # FA / FNA inhibition (non-competitive), mg N/L as NH3-N / HNO2-N
    ki_fa_aob: float = 8.0      # ≈10 mg NH3/L onset [4]
    ki_fa_nob: float = 0.5      # 0.1–1.0 mg NH3/L onset [4]
    ki_fna_aob: float = 0.2     # [4] / Vadivelu et al. 2006
    ki_fna_nob: float = 0.06    # 0.22 mg HNO2/L ≈ 0.067 mg HNO2-N/L onset [4]
    # Arrhenius activation energies (kJ/mol) [8]
    ea_aob: float = 68.0
    ea_nob: float = 44.0
    ea_amx: float = 70.0
    # empirical anammox pH window [2] (range 6.7–8.3, optimum ≈ 8)
    ph_opt_amx: float = 8.0
    ph_width_amx: float = 0.6
    # biomass nitrogen content (g N / g VSS) for AOB/NOB growth
    i_n_bm: float = 0.12
    stoichiometry: str = "strous_1998"

    @property
    def stoich(self) -> dict:
        return STOICHIOMETRY_SETS[self.stoichiometry]

    @property
    def y_amx(self) -> float:
        return anammox_yield_vss_per_n(self.stoich)


@dataclass
class ReactorConfig:
    """Operating conditions. Set ``hrt_d=None`` (or <=0) for batch operation."""

    # initial concentrations (mg N/L)
    nh4: float = 50.0
    no2: float = 0.0
    no3: float = 0.0
    # influent (continuous mode)
    nh4_in: float = 200.0
    no2_in: float = 0.0
    no3_in: float = 0.0
    hrt_d: float | None = 1.0
    # environment
    ph: float = 7.8
    temperature: float = 30.0
    do: float = 0.3
    aeration_fraction: float = 1.0      # 1 = continuous aeration; <1 = intermittent (time-averaged cycle)
    aeration_cycle_min: float = 60.0
    # biomass (mg VSS/L)
    x_aob: float = 300.0
    x_nob: float = 50.0
    x_amx: float = 1500.0
    # retention (d) — use large values for granules/biofilm carriers
    srt_floc: float = 10.0              # AOB/NOB (flocs)
    srt_amx: float = 60.0               # anammox (granules/biofilm)
    days: int = 30
    dt_min: float = 5.0
    params: KineticParameters = field(default_factory=KineticParameters)


def _arrhenius(ea: float, temperature_c) -> np.ndarray:
    t = np.asarray(temperature_c, dtype=float) + 273.15
    return np.exp(ea / R_GAS * (1.0 / (T_REF_C + 273.15) - 1.0 / t))


def _monod(s, k):
    s = np.maximum(s, 0.0)
    return s / (k + s)


def _inhib(i, k):
    return k / (k + np.maximum(i, 0.0))


def fa_n(nh4, ph, temperature):
    pka = pka_ammonia(temperature)
    return np.maximum(nh4, 0.0) / (1.0 + 10.0 ** (pka - ph))


def fna_n(no2, ph, temperature):
    pka = pka_nitrous_acid(temperature)
    return np.maximum(no2, 0.0) / (1.0 + 10.0 ** (ph - pka))


def growth_rates(nh4, no2, do, ph, temperature, p: KineticParameters):
    """Specific growth rates (1/d) of AOB, NOB, AMX — vectorised."""
    fa = fa_n(nh4, ph, temperature)
    fna = fna_n(no2, ph, temperature)
    mu_a = (
        p.mu_aob * _arrhenius(p.ea_aob, temperature)
        * _monod(nh4, p.k_nh4_aob) * _monod(do, p.k_o_aob)
        * _inhib(fa, p.ki_fa_aob) * _inhib(fna, p.ki_fna_aob)
    )
    mu_n = (
        p.mu_nob * _arrhenius(p.ea_nob, temperature)
        * _monod(no2, p.k_no2_nob) * _monod(do, p.k_o_nob)
        * _inhib(fa, p.ki_fa_nob) * _inhib(fna, p.ki_fna_nob)
    )
    ph_amx = np.exp(-((np.asarray(ph, dtype=float) - p.ph_opt_amx) ** 2) / (2 * p.ph_width_amx ** 2))
    no2p = np.maximum(no2, 0.0)
    haldane_no2 = no2p / (p.k_no2_amx + no2p + no2p ** 2 / p.ki_no2_amx)
    mu_x = (
        p.mu_amx * _arrhenius(p.ea_amx, temperature)
        * _monod(nh4, p.k_nh4_amx) * haldane_no2
        * _inhib(do, p.ko_amx) * ph_amx
    )
    return mu_a, mu_n, mu_x


def _as_array(value, n):
    arr = np.asarray(value, dtype=float)
    if arr.ndim == 0:
        arr = np.full(n, float(arr))
    return arr


def simulate(
    cfg: ReactorConfig,
    *,
    n: int | None = None,
    overrides: dict | None = None,
    do_schedule=None,
    record_every_d: float = 1.0,
) -> pd.DataFrame | list[pd.DataFrame]:
    """
    Integrate the model.

    ``overrides``: dict of ReactorConfig field -> array of length n (vectorised scenarios).
    ``do_schedule``: optional callable(day:int, state:dict) -> DO setpoint, applied daily
                     (used for closed-loop self-control tests; single scenario only).
    Returns a DataFrame (single scenario) or a list of DataFrames (n scenarios).
    """
    overrides = overrides or {}
    if n is None:
        n = max([len(np.atleast_1d(v)) for v in overrides.values()] or [1])
    p = cfg.params
    st = cfg.params.stoich
    y_x = p.y_amx
    g = {name: _as_array(overrides.get(name, getattr(cfg, name)), n) for name in (
        "nh4", "no2", "no3", "nh4_in", "no2_in", "no3_in", "ph", "temperature", "do",
        "aeration_fraction", "x_aob", "x_nob", "x_amx", "srt_floc", "srt_amx",
    )}
    hrt_raw = overrides.get("hrt_d", cfg.hrt_d)
    if hrt_raw is None:
        hrt = np.full(n, np.inf)
    else:
        hrt = _as_array(hrt_raw, n)
        hrt = np.where(hrt <= 0, np.inf, hrt)
    dil = np.where(np.isfinite(hrt), 1.0 / np.where(np.isfinite(hrt), hrt, 1.0), 0.0)
    w_floc = 1.0 / np.maximum(g["srt_floc"], 1e-6)
    w_amx = 1.0 / np.maximum(g["srt_amx"], 1e-6)

    S_nh4, S_no2, S_no3 = g["nh4"].copy(), g["no2"].copy(), g["no3"].copy()
    Xa, Xn, Xx = g["x_aob"].copy(), g["x_nob"].copy(), g["x_amx"].copy()
    n2_cum = np.zeros(n)
    rem_nh4_cum = np.zeros(n)
    prod_no3_cum = np.zeros(n)

    dt = cfg.dt_min / 1440.0
    steps_per_day = int(round(1.0 / dt))
    dt = 1.0 / steps_per_day
    cycle_d = max(cfg.aeration_cycle_min, cfg.dt_min) / 1440.0
    do_set = g["do"].copy()

    records = [[] for _ in range(n)]

    def snapshot(day):
        fa = fa_n(S_nh4, g["ph"], g["temperature"])
        fna = fna_n(S_no2, g["ph"], g["temperature"])
        for i in range(n):
            records[i].append({
                "Day": day,
                "NH4": S_nh4[i], "NO2": S_no2[i], "NO3": S_no3[i],
                "AOB": Xa[i], "NOB": Xn[i], "AMX": Xx[i],
                "DO": do_set[i], "FA": fa[i], "FNA": fna[i],
                "N2_cum": n2_cum[i], "_rem_nh4": rem_nh4_cum[i], "_prod_no3": prod_no3_cum[i],
            })

    snapshot(0)
    total_steps = int(cfg.days) * steps_per_day
    for k in range(total_steps):
        t = k * dt
        if do_schedule is not None and k % steps_per_day == 0 and k > 0:
            day = k // steps_per_day
            state = {"NH4": float(S_nh4[0]), "NO2": float(S_no2[0]), "NO3": float(S_no3[0]),
                     "records": records[0]}
            do_set[:] = float(do_schedule(day, state))
        phase = (t % cycle_d) / cycle_d
        aer_on = phase < g["aeration_fraction"]
        do_now = np.where(aer_on, do_set, 0.0)

        mu_a, mu_n, mu_x = growth_rates(S_nh4, S_no2, do_now, g["ph"], g["temperature"], p)
        r_a = mu_a * Xa        # mg VSS/L/d
        r_n = mu_n * Xn
        r_x = mu_x * Xx
        # nitrogen conversions (mg N/L/d)
        aob_nh4 = r_a / p.y_aob          # NH4 -> NO2 (catabolic)
        aob_n_bm = p.i_n_bm * r_a        # N into AOB biomass
        nob_no2 = r_n / p.y_nob
        nob_n_bm = p.i_n_bm * r_n
        amx_nh4 = r_x / y_x
        amx_no2 = st["no2_per_nh4"] * amx_nh4
        amx_no3 = st["no3_per_nh4"] * amx_nh4
        amx_n2 = 2.0 * st["n2_per_nh4"] * amx_nh4

        # Positivity-preserving (Patankar-type) update, solved sequentially NH4 -> NO2 -> NO3.
        # Destruction terms are scaled by S_new/S; productions use the realised upstream flux.
        D_nh4 = aob_nh4 + aob_n_bm + amx_nh4 + nob_n_bm
        S_nh4_new = (S_nh4 + dt * dil * g["nh4_in"]) / (1.0 + dt * (dil + D_nh4 / np.maximum(S_nh4, 1e-9)))
        lim_nh4 = np.where(S_nh4 > 1e-9, S_nh4_new / np.maximum(S_nh4, 1e-9), 0.0)
        lim_nh4 = np.minimum(lim_nh4, 1.0)
        D_no2 = nob_no2 + amx_no2
        P_no2 = aob_nh4 * lim_nh4
        S_no2_new = (S_no2 + dt * (dil * g["no2_in"] + P_no2)) / (1.0 + dt * (dil + D_no2 / np.maximum(S_no2, 1e-9)))
        lim_no2 = np.where(S_no2 > 1e-9, np.minimum(S_no2_new / np.maximum(S_no2, 1e-9), 1.0), 0.0)
        lim_n = lim_no2
        lim_x = np.minimum(lim_nh4, lim_no2)
        P_no3 = nob_no2 * lim_n + amx_no3 * lim_x
        S_no3_new = (S_no3 + dt * (dil * g["no3_in"] + P_no3)) / (1.0 + dt * dil)

        rem_nh4_cum += dt * D_nh4 * lim_nh4
        prod_no3_cum += dt * P_no3
        n2_cum += dt * amx_n2 * lim_x

        Xa = Xa + dt * (r_a * lim_nh4 - (p.b_aob * _arrhenius(p.ea_aob, g["temperature"]) + w_floc) * Xa)
        Xn = Xn + dt * (r_n * lim_n - (p.b_nob * _arrhenius(p.ea_nob, g["temperature"]) + w_floc) * Xn)
        Xx = Xx + dt * (r_x * lim_x - (p.b_amx * _arrhenius(p.ea_amx, g["temperature"]) + w_amx) * Xx)
        Xa, Xn, Xx = (np.maximum(v, 1e-6) for v in (Xa, Xn, Xx))
        S_nh4, S_no2, S_no3 = S_nh4_new, S_no2_new, S_no3_new

        if (k + 1) % int(round(record_every_d * steps_per_day)) == 0:
            snapshot((k + 1) * dt)

    out = []
    for i in range(n):
        df = pd.DataFrame(records[i])
        df = add_indicators(df, nh4_in=g["nh4_in"][i], no2_in=g["no2_in"][i],
                            no3_in=g["no3_in"][i], hrt_d=hrt[i])
        out.append(df)
    return out[0] if n == 1 and not overrides else out


def add_indicators(df: pd.DataFrame, *, nh4_in: float, no2_in: float, no3_in: float, hrt_d: float) -> pd.DataFrame:
    """Performance indicators used throughout the app (continuous or batch)."""
    df = df.copy()
    df["TIN"] = df["NH4"] + df["NO2"] + df["NO3"]
    continuous = np.isfinite(hrt_d)
    if continuous:
        tin_in = nh4_in + no2_in + no3_in
        df["NH4_removal_pct"] = 100.0 * (nh4_in - df["NH4"]) / max(nh4_in, 1e-9)
        df["TIN_removal_pct"] = 100.0 * (tin_in - df["TIN"]) / max(tin_in, 1e-9)
        df["NLR"] = tin_in / hrt_d / 1000.0                         # kg N/m3/d
        df["NRR"] = (tin_in - df["TIN"]) / hrt_d / 1000.0           # kg N/m3/d
        d_nh4 = nh4_in - df["NH4"]
        d_no3 = df["NO3"] - no3_in
    else:
        tin0 = float(df["TIN"].iloc[0])
        nh40 = float(df["NH4"].iloc[0])
        df["NH4_removal_pct"] = 100.0 * (nh40 - df["NH4"]) / max(nh40, 1e-9)
        df["TIN_removal_pct"] = 100.0 * (tin0 - df["TIN"]) / max(tin0, 1e-9)
        df["NLR"] = np.nan
        df["NRR"] = np.nan
        d_nh4 = nh40 - df["NH4"]
        d_no3 = df["NO3"] - float(df["NO3"].iloc[0])
    df["dNO3_dNH4"] = np.where(d_nh4 > 0.5, d_no3 / np.maximum(d_nh4, 1e-9), np.nan)
    denom = df["NO2"] + df["NO3"]
    df["NAR"] = np.where(denom > 1e-6, df["NO2"] / np.maximum(denom, 1e-9), np.nan)
    df = df.drop(columns=[c for c in df.columns if c.startswith("_")])
    return df


def steady_state(cfg: ReactorConfig, days: int = 200) -> pd.Series:
    """Run long enough to approach steady state and return the last row."""
    return simulate(replace(cfg, days=days, dt_min=10.0), record_every_d=5.0).iloc[-1]
