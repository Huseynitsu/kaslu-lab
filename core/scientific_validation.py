"""
Scientific validation helpers for Anammox research models.

References:
  [1][2] Strous et al. — Anammox stoichiometry and kinetics
  [3] Hellinga et al. — PN operational ranges
  [4] Anthonisen et al. — FA/FNA inhibition
  [6] Pollice et al. — NOB washout (SRT < 5 d)
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace

from core.anammox_model import full_anammox_model, mechanistic_prediction
from core.config import ExperimentConfig
from core.constants import (
    ANAMMOX_IDEAL_RATIO,
    ANAMMOX_NO2_PER_NH4,
    ANAMMOX_NO3_PER_NH4,
    ANAMMOX_DO_MAX,
)
from core.lab_table import default_table
from core.multi_column_analysis import analyze_multi_column
from core.pn_config import PNConfig
from core.pn_model import partial_nitritation_step
from core.pn_simulation import simulate_pn_30_days
from core.simulation import simulate_30_days
from core.stoichiometry import check_anammox_feed


@dataclass
class ValidationCheck:
    name: str
    passed: bool
    expected: str
    actual: str
    reference: str = ""
    severity: str = "critical"  # critical | warning | info


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
        if not self.checks:
            return 100.0
        return 100.0 * self.passed_count / self.total

    @property
    def all_critical_passed(self) -> bool:
        return all(c.passed for c in self.checks if c.severity == "critical")


def _check(name, passed, expected, actual, reference="", severity="critical") -> ValidationCheck:
    return ValidationCheck(name, passed, expected, actual, reference, severity)


def validate_strous_constants() -> ScientificReport:
    report = ScientificReport("Strous stoichiometry constants")
    report.checks.append(_check(
        "NO2/NH4 stoichiometric ratio",
        ANAMMOX_NO2_PER_NH4 == 1.32,
        "1.32",
        str(ANAMMOX_NO2_PER_NH4),
        "[1][2] Strous",
    ))
    report.checks.append(_check(
        "Intrinsic NO3/NH4 ratio",
        abs(ANAMMOX_NO3_PER_NH4 - 0.26) < 1e-9,
        "0.26",
        str(ANAMMOX_NO3_PER_NH4),
        "[1][2] Strous",
    ))
    report.checks.append(_check(
        "Ideal feed ratio equals NO2/NH4 coeff",
        ANAMMOX_IDEAL_RATIO == ANAMMOX_NO2_PER_NH4,
        "equal",
        f"{ANAMMOX_IDEAL_RATIO} vs {ANAMMOX_NO2_PER_NH4}",
        "[1][2] Strous",
    ))
    return report


def validate_stoichiometry_feed() -> ScientificReport:
    report = ScientificReport("Anammox feed stoichiometry")

    ideal = check_anammox_feed(50.0, 66.0, 0.0, 120.0, ratio_tolerance_pct=15.0)
    report.checks.append(_check(
        "Ideal PN effluent (50/66) ready for Anammox",
        ideal.ready_for_anammox,
        "ready=True",
        f"ready={ideal.ready_for_anammox}, ratio={ideal.no2_nh4_ratio:.2f}",
        "[1][2] NO2/NH4 = 1.32",
    ))

    low_no2 = check_anammox_feed(50.0, 30.0, 0.0, 120.0)
    report.checks.append(_check(
        "Low NO2 feed not ready",
        not low_no2.ready_for_anammox,
        "ready=False",
        f"ready={low_no2.ready_for_anammox}, ratio={low_no2.no2_nh4_ratio:.2f}",
        "[1][2] ratio < 1.32",
    ))

    mech_no3 = mechanistic_prediction(50.0, 66.0)
    reactive = min(50.0, 66.0 / ANAMMOX_NO2_PER_NH4)
    expected = reactive * ANAMMOX_NO3_PER_NH4
    report.checks.append(_check(
        "Mechanistic NO3 prediction",
        abs(mech_no3 - expected) < 1e-9,
        f"{expected:.4f} mg/L",
        f"{mech_no3:.4f} mg/L",
        "[1][2] intrinsic NO3",
    ))

    report.checks.append(_check(
        "Expected NO3 from feed check",
        abs(ideal.expected_no3_from_anammox - expected) < 1e-6,
        f"{expected:.4f}",
        f"{ideal.expected_no3_from_anammox:.4f}",
        "check_anammox_feed vs mechanistic_prediction",
    ))
    return report


def validate_anammox_single_step(
    nh4: float = 50.0,
    no2: float = 66.0,
    do: float = 0.1,
) -> ScientificReport:
    report = ScientificReport("Anammox single-step kinetics")

    nh4_f, no2_f, no3_f, _, _, activity = full_anammox_model(
        nh4, no2, 0.0, 200.0, 7.8, 35.0, do, 800.0, 30.0,
    )

    dnh4 = nh4 - nh4_f
    dno2 = no2 - no2_f
    dno3 = no3_f

    if dnh4 > 1e-6:
        ratio_no2 = dno2 / dnh4
        ratio_no3 = dno3 / dnh4
        report.checks.append(_check(
            "Single-step NO2/NH4 removal ratio",
            abs(ratio_no2 - ANAMMOX_NO2_PER_NH4) < 0.05,
            f"{ANAMMOX_NO2_PER_NH4:.2f}",
            f"{ratio_no2:.3f}",
            "[1][2] Strous stoichiometry",
        ))
        report.checks.append(_check(
            "Single-step NO3/NH4 production ratio",
            abs(ratio_no3 - ANAMMOX_NO3_PER_NH4) < 0.05,
            f"{ANAMMOX_NO3_PER_NH4:.2f}",
            f"{ratio_no3:.3f}",
            "[1][2] intrinsic NO3",
        ))
    else:
        report.checks.append(_check(
            "NH4 consumed in one step",
            False,
            "> 0",
            f"{dnh4:.6f}",
            severity="warning",
        ))

    report.checks.append(_check(
        "NH4 decreases",
        nh4_f <= nh4,
        f"final <= {nh4}",
        f"{nh4_f:.3f}",
        "[1][2] Anammox uptake",
    ))
    report.checks.append(_check(
        "NO2 decreases",
        no2_f <= no2,
        f"final <= {no2}",
        f"{no2_f:.3f}",
        "[1][2] Anammox uptake",
    ))
    report.checks.append(_check(
        "NO3 non-decreasing",
        no3_f >= 0.0,
        ">= 0",
        f"{no3_f:.3f}",
        "[1][2] intrinsic NO3 production",
    ))

    _, _, _, _, _, act_high_do = full_anammox_model(
        nh4, no2, 0.0, 200.0, 7.8, 35.0, 1.0, 800.0, 30.0,
    )
    report.checks.append(_check(
        "Oxygen inhibition (DO=0.1 vs DO=1.0)",
        activity > act_high_do,
        "activity(low DO) > activity(high DO)",
        f"{activity:.3f} vs {act_high_do:.3f}",
        f"[1][2] DO < {ANAMMOX_DO_MAX} mg/L",
    ))
    return report


def validate_anammox_30day_simulation(
    config: ExperimentConfig | None = None,
) -> ScientificReport:
    report = ScientificReport("Anammox 30-day simulation")

    cfg = config or ExperimentConfig(
        nh4=50.0,
        no2=66.0,
        no3=0.0,
        hco3=200.0,
        ph=7.8,
        temperature=35.0,
        do=0.1,
        x_anammox=800.0,
        srt=30.0,
    )

    df = simulate_30_days(cfg)
    initial = df.iloc[0]
    final = df.iloc[-1]

    nh4_removed = cfg.nh4 - final["NH4"]
    no2_removed = cfg.no2 - final["NO2"]
    no3_gain = final["NO3"] - cfg.no3

    report.checks.append(_check(
        "30-day NH4 removal positive",
        nh4_removed > 0.5,
        "> 0.5 mg/L",
        f"{nh4_removed:.2f} mg/L",
        "[1][2] Anammox activity",
        severity="warning",
    ))
    report.checks.append(_check(
        "30-day NO2 removal positive",
        no2_removed > 0.5,
        "> 0.5 mg/L",
        f"{no2_removed:.2f} mg/L",
        "[1][2] Anammox activity",
        severity="warning",
    ))
    report.checks.append(_check(
        "Monotonic NH4 trend (overall)",
        final["NH4"] < initial["NH4"],
        "day30 NH4 < day1 NH4",
        f"{final['NH4']:.2f} < {initial['NH4']:.2f}",
        "[1][2]",
    ))
    report.checks.append(_check(
        "Monotonic NO2 trend (overall)",
        final["NO2"] < initial["NO2"],
        "day30 NO2 < day1 NO2",
        f"{final['NO2']:.2f} < {initial['NO2']:.2f}",
        "[1][2]",
    ))

    if nh4_removed > 0.5:
        intrinsic_ratio = no3_gain / nh4_removed
        report.checks.append(_check(
            "30-day intrinsic NO3/NH4 removed",
            abs(intrinsic_ratio - ANAMMOX_NO3_PER_NH4) < 0.02,
            f"{ANAMMOX_NO3_PER_NH4:.2f}",
            f"{intrinsic_ratio:.3f}",
            "[1][2] Strous 0.26 mol/mol",
        ))

    high_do_cfg = replace(cfg, do=1.0)
    df_high = simulate_30_days(high_do_cfg)
    removal_low_do = cfg.nh4 - final["NH4"]
    removal_high_do = high_do_cfg.nh4 - df_high.iloc[-1]["NH4"]
    report.checks.append(_check(
        "Low DO removes more NH4 than high DO",
        removal_low_do >= removal_high_do,
        "removal(DO=0.1) >= removal(DO=1.0)",
        f"{removal_low_do:.2f} vs {removal_high_do:.2f}",
        "[1][2] oxygen inhibition",
    ))
    return report


def validate_pn_single_step() -> ScientificReport:
    report = ScientificReport("PN single-step kinetics")

    nh4_i, no2_i, no3_i = 100.0, 0.0, 0.0
    nh4_f, no2_f, no3_f, _, _, nar = partial_nitritation_step(
        nh4=nh4_i,
        no2=no2_i,
        no3=no3_i,
        ph=7.8,
        temperature=35.0,
        do=0.8,
        x_aob=200.0,
        x_nob=20.0,
        srt=4.0,
    )

    report.checks.append(_check(
        "AOB oxidizes NH4 to NO2 (NH4 down)",
        nh4_f < nh4_i,
        f"NH4 {nh4_i} -> lower",
        f"{nh4_f:.3f}",
        "[3] partial nitritation",
    ))
    report.checks.append(_check(
        "NO2 accumulates from AOB",
        no2_f > no2_i,
        f"NO2 {no2_i} -> higher",
        f"{no2_f:.3f}",
        "[3] partial nitritation",
    ))
    report.checks.append(_check(
        "NOB suppressed - low NO3",
        no3_f < 0.5,
        "NO3 < 0.5 mg/L",
        f"{no3_f:.4f}",
        "[6] NOB washout SRT < 5 d",
    ))
    report.checks.append(_check(
        "High NAR (NO2/(NO2+NO3))",
        nar > 0.9,
        "> 0.9",
        f"{nar:.3f}",
        "[3][6] PN selectivity",
    ))
    return report


def validate_pn_30day_batch() -> ScientificReport:
    report = ScientificReport("PN 30-day batch simulation")

    cfg = PNConfig(
        nh4=100.0,
        no2=0.0,
        no3=0.0,
        ph=7.8,
        temperature=35.0,
        do=0.8,
        srt=4.0,
        x_aob=200.0,
        x_nob=20.0,
    )
    df = simulate_pn_30_days(cfg)
    final = df.iloc[-1]

    report.checks.append(_check(
        "Batch NH4 decreases over 30 d",
        final["NH4"] < cfg.nh4,
        f"< {cfg.nh4}",
        f"{final['NH4']:.2f}",
        "[3] PN",
        severity="warning",
    ))
    report.checks.append(_check(
        "Batch NO2 increases over 30 d",
        final["NO2"] > 0.5,
        "> 0.5 mg/L",
        f"{final['NO2']:.2f}",
        "[3] PN",
        severity="warning",
    ))
    report.checks.append(_check(
        "Batch NO3 stays low (NOB out)",
        final["NO3"] < 1.0,
        "< 1.0 mg/L",
        f"{final['NO3']:.4f}",
        "[6] NOB suppression",
    ))
    report.checks.append(_check(
        "Final NAR high",
        final["NAR"] > 0.95,
        "> 0.95",
        f"{final['NAR']:.3f}",
        "[3][6] nitrite accumulation",
    ))

    report.checks.append(_check(
        "PN kinetic calibration note",
        (cfg.nh4 - final["NH4"]) >= 1.0,
        ">= 1 mg/L NH4 removed in 30 d (calibration target)",
        f"{cfg.nh4 - final['NH4']:.2f} mg/L removed",
        "Lab calibration recommended",
        severity="info",
    ))
    return report


def validate_multi_column_analysis() -> ScientificReport:
    report = ScientificReport("Multi-column lab analysis")

    table = default_table()
    result = analyze_multi_column(table, stage="pn")

    nh4_eff = result.efficiency_df[result.efficiency_df["param_key"] == "nh4"].iloc[0]
    expected_eff = (100.0 - 50.0) / 100.0 * 100.0

    report.checks.append(_check(
        "NH4 removal efficiency formula",
        abs(nh4_eff["Efficiency (%)"] - expected_eff) < 1e-6,
        f"{expected_eff}%",
        f"{nh4_eff['Efficiency (%)']}%",
        "Entrance to Reactor mass balance",
    ))

    reactor_ratio = result.ratio_df[result.ratio_df["column_key"] == "reactor"].iloc[0]["NO2/NH4 ratio"]
    expected_ratio = 30.0 / 50.0
    report.checks.append(_check(
        "Reactor NO2/NH4 ratio",
        abs(reactor_ratio - expected_ratio) < 1e-6,
        f"{expected_ratio:.2f}",
        f"{reactor_ratio:.2f}",
        "[1][2] performance index",
    ))

    ent_dist = result.differences_df[
        (result.differences_df["param_key"] == "nh4")
        & (result.differences_df["Comparison"] == "Entrance − Distilled")
    ].iloc[0]["Difference"]
    report.checks.append(_check(
        "Entrance minus Distilled NH4 difference",
        ent_dist == 100.0,
        "100.0",
        f"{ent_dist}",
        "Lab notebook arithmetic",
    ))
    return report


def run_full_scientific_audit() -> list[ScientificReport]:
    return [
        validate_strous_constants(),
        validate_stoichiometry_feed(),
        validate_anammox_single_step(),
        validate_anammox_30day_simulation(),
        validate_pn_single_step(),
        validate_pn_30day_batch(),
        validate_multi_column_analysis(),
    ]


def format_audit_summary(reports: list[ScientificReport]) -> str:
    lines = ["Scientific validation audit", "=" * 40]
    for rep in reports:
        lines.append(f"\n{rep.domain}: {rep.passed_count}/{rep.total} ({rep.score_pct:.0f}%)")
        for check in rep.checks:
            mark = "PASS" if check.passed else "FAIL"
            lines.append(f"  [{mark}] {check.name}")
            if not check.passed:
                lines.append(f"         expected: {check.expected}")
                lines.append(f"         actual:   {check.actual}")
                if check.reference:
                    lines.append(f"         ref:      {check.reference}")
    total_pass = sum(r.passed_count for r in reports)
    total = sum(r.total for r in reports)
    lines.append(f"\nOverall: {total_pass}/{total} checks passed ({100*total_pass/total:.0f}%)")
    return "\n".join(lines)
