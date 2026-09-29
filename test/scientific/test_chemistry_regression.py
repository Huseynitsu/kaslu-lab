"""Regression tests for the FA/FNA bug (pKa of HNO2 was ≈7.7 instead of ≈3.3)."""

import pytest

from core.chemistry import (
    anthonisen_fna_closed_form,
    free_ammonia_as_molecule,
    free_nitrous_acid_as_molecule,
    free_nitrous_acid_mg_l,
    pka_nitrous_acid,
)


def test_pka_hno2_is_about_3_3():
    assert 3.2 < pka_nitrous_acid(30) < 3.4


def test_fna_is_tiny_at_neutral_ph():
    # 50 mg NO2-N/L at pH 7.5, 30 °C → ≈ 0.003 mg HNO2-N/L (not tens of mg/L)
    assert free_nitrous_acid_mg_l(50, 7.5, 30) < 0.01


def test_fna_matches_anthonisen():
    assert free_nitrous_acid_as_molecule(50, 7.5, 30) == pytest.approx(anthonisen_fna_closed_form(50, 7.5, 30), rel=0.03)


def test_fa_fraction_at_ph_925_is_half():
    # at pH = pKa (≈9.25 at 25 °C) half of TAN is NH3
    fa_n = free_ammonia_as_molecule(100, 9.2505, 25) * 14.0067 / 17.031
    assert fa_n == pytest.approx(50, rel=0.02)
