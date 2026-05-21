import pytest
from tabularium.np122.indicative_deformation_modulus_non_cohesive import (
    DeformationModulusNonCohesiveResult,
    RelativeDensity,
    SoilCategory,
    get_deformation_modulus,
)


def test_gravel_coarse_medium_sand_medium():
    r = get_deformation_modulus(SoilCategory.GRAVEL_COARSE_MEDIUM_SAND, RelativeDensity.MEDIUM)
    assert r.valid is True
    assert r.interpolated is False
    assert r.e_modulus == pytest.approx(30_000.0)
    assert r.errors == []
    assert r.warnings == []


def test_gravel_coarse_medium_sand_dense():
    r = get_deformation_modulus(SoilCategory.GRAVEL_COARSE_MEDIUM_SAND, RelativeDensity.DENSE)
    assert r.valid is True
    assert r.e_modulus == pytest.approx(40_000.0)


def test_fine_sand_medium():
    r = get_deformation_modulus(SoilCategory.FINE_SAND, RelativeDensity.MEDIUM)
    assert r.valid is True
    assert r.e_modulus == pytest.approx(25_000.0)


def test_fine_sand_dense():
    r = get_deformation_modulus(SoilCategory.FINE_SAND, RelativeDensity.DENSE)
    assert r.valid is True
    assert r.e_modulus == pytest.approx(35_000.0)


def test_silty_sand_medium():
    r = get_deformation_modulus(SoilCategory.SILTY_SAND, RelativeDensity.MEDIUM)
    assert r.valid is True
    assert r.e_modulus == pytest.approx(18_000.0)


def test_silty_sand_dense():
    r = get_deformation_modulus(SoilCategory.SILTY_SAND, RelativeDensity.DENSE)
    assert r.valid is True
    assert r.e_modulus == pytest.approx(30_000.0)


def test_source_metadata():
    r = get_deformation_modulus(SoilCategory.FINE_SAND, RelativeDensity.MEDIUM)
    assert r.source is not None
    assert r.source.code == "NP 122:2010"
    assert r.source.table == "Tabelul A.6.3"


def test_result_type():
    r = get_deformation_modulus(SoilCategory.SILTY_SAND, RelativeDensity.DENSE)
    assert isinstance(r, DeformationModulusNonCohesiveResult)
