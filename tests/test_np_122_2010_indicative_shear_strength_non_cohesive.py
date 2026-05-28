import pytest
from tabularium.np_122_2010.indicative_shear_strength.non_cohesive import (
    RelativeDensity,
    ShearStrengthNonCohesiveResult,
    SoilCategory,
    get_phi,
)


# ── Exact lookup ──────────────────────────────────────────────────────────────

def test_gravel_coarse_sand_medium():
    r = get_phi(SoilCategory.GRAVEL_COARSE_SAND, RelativeDensity.MEDIUM)
    assert r.valid is True
    assert r.interpolated is False
    assert r.phi == pytest.approx(33.0)
    assert r.errors == []
    assert r.warnings == []


def test_gravel_coarse_sand_dense():
    r = get_phi(SoilCategory.GRAVEL_COARSE_SAND, RelativeDensity.DENSE)
    assert r.valid is True
    assert r.phi == pytest.approx(36.0)


def test_medium_sand_medium():
    r = get_phi(SoilCategory.MEDIUM_SAND, RelativeDensity.MEDIUM)
    assert r.valid is True
    assert r.phi == pytest.approx(31.0)


def test_medium_sand_dense():
    r = get_phi(SoilCategory.MEDIUM_SAND, RelativeDensity.DENSE)
    assert r.valid is True
    assert r.phi == pytest.approx(33.0)


def test_fine_sand_medium():
    r = get_phi(SoilCategory.FINE_SAND, RelativeDensity.MEDIUM)
    assert r.valid is True
    assert r.phi == pytest.approx(27.0)


def test_fine_sand_dense():
    r = get_phi(SoilCategory.FINE_SAND, RelativeDensity.DENSE)
    assert r.valid is True
    assert r.phi == pytest.approx(30.0)


def test_silty_sand_medium():
    r = get_phi(SoilCategory.SILTY_SAND, RelativeDensity.MEDIUM)
    assert r.valid is True
    assert r.phi == pytest.approx(24.0)


def test_silty_sand_dense():
    r = get_phi(SoilCategory.SILTY_SAND, RelativeDensity.DENSE)
    assert r.valid is True
    assert r.phi == pytest.approx(28.0)


# ── Source metadata ───────────────────────────────────────────────────────────

def test_source_metadata():
    r = get_phi(SoilCategory.FINE_SAND, RelativeDensity.MEDIUM)
    assert r.source is not None
    assert r.source.code == "NP 122:2010"
    assert r.source.table == "Tabelul A.6.1"


def test_result_type():
    r = get_phi(SoilCategory.SILTY_SAND, RelativeDensity.DENSE)
    assert isinstance(r, ShearStrengthNonCohesiveResult)


# ── Error cases ───────────────────────────────────────────────────────────────

def test_invalid_soil_category():
    r = get_phi("invalid_category", RelativeDensity.MEDIUM)
    assert r.valid is False
    assert len(r.errors) == 1


def test_invalid_relative_density():
    r = get_phi(SoilCategory.FINE_SAND, "invalid_density")
    assert r.valid is False
    assert len(r.errors) == 1
