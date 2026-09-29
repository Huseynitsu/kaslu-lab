"""
Scientific validation — checks of the code against INDEPENDENT literature benchmarks.

Two kinds of checks (reported separately, do not confuse them):
  * verification — the code implements the equations correctly (closed forms, mass balance);
  * literature benchmarks — model behaviour agrees with published facts (qualitative/semi-quantitative).
Neither replaces calibration/validation with YOUR reactor data (see docs/SCIENCE.md, §Validation plan).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field, replace

from core.chemistry import (
    anthonisen_fa_closed_form,
    anthonisen_fna_closed_form,
    free_ammonia_as_molecule,
    free_nitrous_acid_as_molecule,
    pka_ammonia,
    pka_nitrous_acid,
)
from core.constants import (
    ANAMMOX_INTRINSIC_NO3_FRACTION,
    LOTTI_2014,
    PNA_MAX_TN_REMOVAL,
    PNA_NO3_PER_NH4_REMOVED,
    STROUS_1998,
)
from core.dilution import calculate_dilution, fit_calibration
from core.early_warning import first_detection_day, run_early_warning
from core.lab_table import default_table
from core.multi_column_analysis import analyze_multi_column
from core.pna_model import KineticParameters, ReactorConfig, simulate
from core.stoichiometry import check_anammox_feed


@dataclass
class ValidationCheck:
    name: str
    passed: bool
    expected: str
    actual: str
    reference: str = ""
    severity: str = "critical"  # critical | warning | info
    kind: str = "verification"  # verification | benchmark


@dataclass
class ScientificReport:
    domain: str
    checks: list[ValidationCheck] = field(default_factory=list)

    @property
    def passed_count(self) -> int:
        return sum(1 for c in self.checks if c.passed)

    @property
    def total(self) -> int:
        return len(self.checks)

    @property
    def score_pct(self) -> float:
        return 100.0 if not self.checks else 100.0 * self.passed_count / self.total

    @property
    def all_critical_passed(self) -> bool:
        return all(c.passed for c in self.checks if c.severity == "critical")


def _check(name, passed, expected, actual, reference="", severity="critical", kind="verification"):
    return ValidationCheck(name, bool(passed), expected, actual, reference, severity, kind)


def _rel(a, b):
    return abs(a - b) / max(abs(b), 1e-12)


# ---------------------------------------------------------------------------
def validate_chemistry() -> ScientificReport:
    r = ScientificReport("FA / FNA chemistry")
    r.checks.append(_check("pKa NH4+/NH3 at 25 °C ≈ 9.25", abs(pka_ammonia(25) - 9.25) < 0.02,
                           "9.25 ± 0.02", f"{pka_ammonia(25):.3f}", "Emerson et al. 1975"))
    r.checks.append(_check("pKa HNO2 at 25 °C ≈ 3.35", abs(pka_nitrous_acid(25) - 3.35) < 0.05,
                           "3.35 ± 0.05", f"{pka_nitrous_acid(25):.3f}", "Anthonisen et al. 1976"))
    for nh4, ph, t in ((50, 7.5, 30), (200, 8.0, 35), (20, 7.0, 20)):
        a, b = free_ammonia_as_molecule(nh4, ph, t), anthonisen_fa_closed_form(nh4, ph, t)
        r.checks.append(_check(f"FA({nh4} mg N/L, pH {ph}, {t} °C) = Anthonisen", _rel(a, b) < 0.03,
                               f"{b:.4f} mg NH3/L", f"{a:.4f}", "[4]"))
    for no2, ph, t in ((50, 7.5, 30), (200, 7.0, 25), (5, 8.0, 35)):
        a, b = free_nitrous_acid_as_molecule(no2, ph, t), anthonisen_fna_closed_form(no2, ph, t)
        r.checks.append(_check(f"FNA({no2} mg N/L, pH {ph}, {t} °C) = Anthonisen", _rel(a, b) < 0.03,
                               f"{b:.5f} mg HNO2/L", f"{a:.5f}", "[4]"))
    return r


def validate_stoichiometry() -> ScientificReport:
    r = ScientificReport("Anammox stoichiometry")
    for S in (STROUS_1998, LOTTI_2014):
        n_in = 1 + S["no2_per_nh4"]
        n_out = 2 * S["n2_per_nh4"] + S["no3_per_nh4"] + S["biomass_per_nh4"] * S["biomass_n_frac"]
        r.checks.append(_check(f"N balance closes — {S['name']}", _rel(n_out, n_in) < 0.01,
                               f"{n_in:.3f}", f"{n_out:.3f}", S["name"]))
    r.checks.append(_check("Intrinsic NO3 ≈ 11 % of consumed N (0.26/2.32)",
                           abs(ANAMMOX_INTRINSIC_NO3_FRACTION - 0.112) < 0.002, "0.112",
                           f"{ANAMMOX_INTRINSIC_NO3_FRACTION:.3f}", "[1]"))
    r.checks.append(_check("One-stage PN/A ΔNO3/ΔNH4 ≈ 0.11", abs(PNA_NO3_PER_NH4_REMOVED - 0.112) < 0.002,
                           "0.112", f"{PNA_NO3_PER_NH4_REMOVED:.3f}", "[1]"))
    r.checks.append(_check("Max autotrophic TIN removal ≈ 89 %", abs(PNA_MAX_TN_REMOVAL - 0.888) < 0.003,
                           "0.888", f"{PNA_MAX_TN_REMOVAL:.3f}", "[1]"))
    ideal = check_anammox_feed(50.0, 66.0, 0.0, 120.0)
    low = check_anammox_feed(50.0, 30.0, 0.0, 120.0)
    r.checks.append(_check("Feed 50/66 ready; 50/30 not ready", ideal.ready_for_anammox and not low.ready_for_anammox,
                           "True / False", f"{ideal.ready_for_anammox} / {low.ready_for_anammox}", "[1]"))
    return r


def validate_anammox_kinetics() -> ScientificReport:
    r = ScientificReport("Anammox kinetics (model)")
    p = KineticParameters()
    td = math.log(2) / p.mu_amx
    r.checks.append(_check("Doubling time 7–14 d", 7 <= td <= 14, "7–14 d", f"{td:.1f} d",
                           "[1] Strous 1998 (~11 d)", kind="benchmark"))
    cfg = ReactorConfig(nh4=50, no2=66, no3=0, hrt_d=None, do=0.0, x_aob=1e-6, x_nob=1e-6, x_amx=800,
                        srt_floc=1e9, srt_amx=1e9, temperature=30, ph=7.8, days=1, dt_min=1.0)
    df = simulate(cfg, record_every_d=1 / 24)
    h1 = df.iloc[1]
    rate = (50 - h1["NH4"]) * 24 / 800  # g N / g VSS / d, first hour
    r.checks.append(_check("Specific NH4 uptake 0.1–1.5 g N/g VSS/d", 0.1 <= rate <= 1.5,
                           "0.1–1.5", f"{rate:.2f}", "[1][7] literature range", kind="benchmark"))
    last = df.iloc[-1]
    d_nh4, d_no2, d_no3 = 50 - last["NH4"], 66 - last["NO2"], last["NO3"]
    r.checks.append(_check("ΔNO2/ΔNH4 = 1.32", abs(d_no2 / d_nh4 - 1.32) < 0.02, "1.32",
                           f"{d_no2 / d_nh4:.3f}", "[1]"))
    r.checks.append(_check("ΔNO3/ΔNH4 = 0.26", abs(d_no3 / d_nh4 - 0.26) < 0.02, "0.26",
                           f"{d_no3 / d_nh4:.3f}", "[1]"))
    n_end = last["NH4"] + last["NO2"] + last["NO3"] + last["N2_cum"]
    r.checks.append(_check("N conserved in batch (±2 %)", _rel(n_end, 116.0) < 0.02 + 0.0099 * d_nh4 / 116,
                           "116 mg N/L", f"{n_end:.2f}", "mass balance"))
    low = simulate(replace(cfg, do=0.05)).iloc[-1]
    high = simulate(replace(cfg, do=1.0, days=1)).iloc[-1]
    r.checks.append(_check("O2 inhibits anammox (DO 1.0 < DO 0.05)", (50 - high["NH4"]) < (50 - low["NH4"]),
                           "less NH4 removed at DO 1.0", f"{50 - high['NH4']:.1f} vs {50 - low['NH4']:.1f}",
                           "[2]", kind="benchmark"))
    return r


def validate_pn_sharon() -> ScientificReport:
    r = ScientificReport("Partial nitritation (SHARON principle)")
    base = ReactorConfig(nh4=500, nh4_in=1000, hrt_d=1.25, srt_floc=1.25, x_amx=1e-9, x_aob=300, x_nob=100,
                         do=1.0, ph=7.5, days=90, dt_min=15.0)
    hot = simulate(replace(base, temperature=35)).iloc[-1]
    cold = simulate(replace(base, temperature=20)).iloc[-1]
    r.checks.append(_check("35 °C, SRT=HRT=1.25 d: NOB washed out (NAR > 0.95)", hot["NAR"] > 0.95,
                           "> 0.95", f"{hot['NAR']:.3f}", "[3] Hellinga 1998", kind="benchmark"))
    r.checks.append(_check("35 °C: NH4 oxidised (> 80 %)", hot["NH4_removal_pct"] > 80, "> 80 %",
                           f"{hot['NH4_removal_pct']:.1f} %", "[3]", kind="benchmark"))
    r.checks.append(_check("20 °C: SHARON fails (AOB washout, NH4 removal < 20 %)", cold["NH4_removal_pct"] < 20,
                           "< 20 %", f"{cold['NH4_removal_pct']:.1f} %", "[3]", kind="benchmark"))
    return r


def validate_pna() -> ScientificReport:
    r = ScientificReport("One-stage PN/A (model)")
    cfg = ReactorConfig(days=150, dt_min=15.0)
    low = simulate(replace(cfg, do=0.3)).iloc[-1]
    high = simulate(replace(cfg, do=1.0)).iloc[-1]
    r.checks.append(_check("DO 0.3: TIN removal 80–89 %", 80 <= low["TIN_removal_pct"] <= 89.5, "80–89 %",
                           f"{low['TIN_removal_pct']:.1f} %", "[1][8]", kind="benchmark"))
    r.checks.append(_check("DO 0.3: ΔNO3/ΔNH4 ≈ 0.11", abs(low["dNO3_dNH4"] - 0.112) < 0.02, "0.11 ± 0.02",
                           f"{low['dNO3_dNH4']:.3f}", "[1]", kind="benchmark"))
    r.checks.append(_check("DO 1.0: NOB/NO2 build-up lowers TIN removal", high["TIN_removal_pct"] < low["TIN_removal_pct"] - 20,
                           "≥ 20 points lower", f"{high['TIN_removal_pct']:.1f} %", "[8] Hao et al. 2002", kind="benchmark"))
    r.checks.append(_check("DO 1.0: ΔNO3/ΔNH4 rises above 0.2", high["dNO3_dNH4"] > 0.2, "> 0.2",
                           f"{high['dNO3_dNH4']:.3f}", "[8]", kind="benchmark"))
    return r


def validate_lab_tools() -> ScientificReport:
    r = ScientificReport("Lab tools (photometry, notebook)")
    cal = fit_calibration([0, 0.2, 0.4, 0.8, 1.2, 1.6], [0.0, 0.06, 0.12, 0.24, 0.36, 0.48])
    r.checks.append(_check("Calibration slope 0.30, R² ≈ 1", abs(cal.slope - 0.3) < 1e-6 and cal.r2 > 0.9999,
                           "0.300", f"{cal.slope:.4f}", "linear regression"))
    d = calculate_dilution(0.45, 0.30, dilution_factor=50)
    r.checks.append(_check("A=0.45, k=0.30, 50× → 75 mg N/L", abs(d.true_concentration_mg_l - 75.0) < 1e-6,
                           "75.0", f"{d.true_concentration_mg_l:.2f}", "C = A/k × DF"))
    hi = calculate_dilution(1.6, 0.30)
    r.checks.append(_check("A=1.6 flagged out of range", not hi.in_linear_range, "False", str(hi.in_linear_range), "[5]"))
    res = analyze_multi_column(default_table(), stage="pna")
    eff = res.efficiency_df.set_index("param_key")["Efficiency (%)"]
    r.checks.append(_check("NH4 removal (100→50) = 50 %", abs(eff["nh4"] - 50.0) < 1e-9, "50", f"{eff['nh4']}"))
    r.checks.append(_check("TIN removal (105→82) = 21.9 %", abs(eff["tin"] - 100 * 23 / 105) < 1e-9,
                           f"{100 * 23 / 105:.1f}", f"{eff['tin']:.1f}"))
    return r


def validate_early_warning() -> ScientificReport:
    from core.self_control import synthetic_nob_outbreak

    r = ScientificReport("Early warning (synthetic outbreak)")
    data = synthetic_nob_outbreak()
    res = run_early_warning(data)
    pre = [s for s in res.signals if s.day < 30]
    first = first_detection_day(res, "watch")
    alarm = first_detection_day(res, "alarm")
    r.checks.append(_check("No false alarms before the fault (day < 30)", len(pre) == 0, "0 signals",
                           f"{len(pre)} signals", "specificity", kind="benchmark"))
    r.checks.append(_check("Fault detected before the first alarm", first is not None and alarm is not None and first < alarm,
                           "watch day < alarm day", f"{first} / {alarm}", "lead time", kind="benchmark"))
    return r


def run_full_scientific_audit() -> list[ScientificReport]:
    return [
        validate_chemistry(),
        validate_stoichiometry(),
        validate_anammox_kinetics(),
        validate_pn_sharon(),
        validate_pna(),
        validate_lab_tools(),
        validate_early_warning(),
    ]


def format_audit_summary(reports: list[ScientificReport]) -> str:
    lines = ["Scientific validation audit", "=" * 40]
    for rep in reports:
        lines.append(f"\n{rep.domain}: {rep.passed_count}/{rep.total} ({rep.score_pct:.0f}%)")
        for check in rep.checks:
            mark = "PASS" if check.passed else "FAIL"
            lines.append(f"  [{mark}] ({check.kind}) {check.name}")
            if not check.passed:
                lines.append(f"         expected: {check.expected}")
                lines.append(f"         actual:   {check.actual}")
                if check.reference:
                    lines.append(f"         ref:      {check.reference}")
    total_pass = sum(r.passed_count for r in reports)
    total = sum(r.total for r in reports)
    lines.append(f"\nOverall: {total_pass}/{total} checks passed ({100 * total_pass / max(total, 1):.0f}%)")
    lines.append("NOTE: passing these checks does not validate the model for YOUR reactor — calibrate with lab data.")
    return "\n".join(lines)
