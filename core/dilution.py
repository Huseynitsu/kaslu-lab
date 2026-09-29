"""
Spectrophotometric calibration and dilution helpers [5].

Calibration: A = k · C + b  (A absorbance, C mg N/L in the measured solution)
Sample concentration = (A_sample − A_blank − b) / k × dilution factor
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from core.constants import (
    ABSORBANCE_LINEAR_MAX,
    ABSORBANCE_LINEAR_MIN,
    CALIBRATION_MIN_POINTS,
    CALIBRATION_MIN_R2,
)

STANDARD_FACTORS = (1, 2, 5, 10, 20, 25, 50, 100, 200, 500, 1000)


@dataclass
class DilutionResult:
    absorbance: float
    measured_concentration_mg_l: float
    dilution_factor: float
    true_concentration_mg_l: float
    in_linear_range: bool
    recommendation: str


@dataclass
class CalibrationResult:
    slope: float        # absorbance per mg/L
    intercept: float
    r2: float
    n_points: int
    acceptable: bool
    messages: list[str]


def fit_calibration(concentrations, absorbances) -> CalibrationResult:
    c = np.asarray(concentrations, dtype=float)
    a = np.asarray(absorbances, dtype=float)
    mask = np.isfinite(c) & np.isfinite(a)
    c, a = c[mask], a[mask]
    msgs = []
    if len(c) < 2 or np.ptp(c) == 0:
        return CalibrationResult(float("nan"), float("nan"), float("nan"), len(c), False,
                                 ["Need at least two distinct standards."])
    k, b = np.polyfit(c, a, 1)
    pred = k * c + b
    ss_res = float(((a - pred) ** 2).sum())
    ss_tot = float(((a - a.mean()) ** 2).sum())
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan")
    ok = True
    if len(c) < CALIBRATION_MIN_POINTS:
        ok = False
        msgs.append(f"Use ≥ {CALIBRATION_MIN_POINTS} standards (incl. zero); {len(c)} given.")
    if not (r2 >= CALIBRATION_MIN_R2):
        ok = False
        msgs.append(f"R² = {r2:.4f} < {CALIBRATION_MIN_R2} — repeat the standard curve.")
    if k <= 0:
        ok = False
        msgs.append("Slope must be positive.")
    if ok:
        msgs.append("Calibration acceptable.")
    return CalibrationResult(float(k), float(b), float(r2), len(c), ok, msgs)


def suggest_dilution_factor(absorbance: float, target: float = 0.5) -> float:
    """
    Dilution factor to apply BEFORE re-measuring an out-of-range (too dark) sample so that
    the new absorbance lands near ``target``. Rounded up to a practical factor.
    """
    if absorbance is None or absorbance <= ABSORBANCE_LINEAR_MAX:
        return 1.0
    needed = absorbance / target
    for f in STANDARD_FACTORS:
        if f >= needed:
            return float(f)
    return float(math.ceil(needed))


def calculate_dilution(
    absorbance: float,
    slope: float,
    dilution_factor: float = 1.0,
    intercept: float = 0.0,
    blank_absorbance: float = 0.0,
    slope_is_conc_per_abs: bool = False,
) -> DilutionResult:
    """
    ``absorbance`` must be measured on the (already diluted) solution.
    ``slope`` is k in A = k·C + b (absorbance per mg/L). For backward compatibility,
    ``slope_is_conc_per_abs=True`` accepts the old "mg/L per A" convention.
    """
    a_net = absorbance - blank_absorbance
    if slope_is_conc_per_abs:
        measured = (a_net - intercept) * slope
    else:
        measured = (a_net - intercept) / slope if slope else float("nan")
    measured = max(measured, 0.0)
    true_c = measured * dilution_factor
    in_range = ABSORBANCE_LINEAR_MIN <= absorbance <= ABSORBANCE_LINEAR_MAX
    if absorbance > ABSORBANCE_LINEAR_MAX:
        f = suggest_dilution_factor(absorbance)
        rec = (f"A = {absorbance:.3f} is above the linear range ({ABSORBANCE_LINEAR_MIN}–{ABSORBANCE_LINEAR_MAX}). "
               f"Dilute a further {f:.0f}× and re-measure; do not report this value.")
    elif absorbance < ABSORBANCE_LINEAR_MIN:
        rec = ("A is below the optimal range — use a smaller dilution factor or a longer cuvette "
               "(result is less precise).")
    else:
        rec = "Absorbance within the linear range."
    return DilutionResult(absorbance, measured, dilution_factor, true_c, in_range, rec)
