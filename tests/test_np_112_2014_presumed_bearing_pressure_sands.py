import pytest
from tabularium.np_112_2014.presumed_bearing_pressure.sands import (
    Soil,
    RelativeDensity,
    MoistureCondition,
    PresumedBearingPressureResult,
    get_presumed_bearing_pressure,
)


# ── Exact lookups ─────────────────────────────────────────────────────────────

def test_coarse_sand_dense():
    r = get_presumed_bearing_pressure(Soil.COARSE_SAND, RelativeDensity.DENSE, MoistureCondition.DRY)
    assert r.valid is True
    assert r.p_conv == pytest.approx(700.0)
    assert r.errors == []
    assert r.warnings == []


def test_coarse_sand_medium():
    r = get_presumed_bearing_pressure(Soil.COARSE_SAND, RelativeDensity.MEDIUM, MoistureCondition.SATURATED)
    assert r.valid is True
    assert r.p_conv == pytest.approx(600.0)


def test_medium_sand_dense():
    r = get_presumed_bearing_pressure(Soil.MEDIUM_SAND, RelativeDensity.DENSE, MoistureCondition.MOIST)
    assert r.valid is True
    assert r.p_conv == pytest.approx(600.0)


def test_medium_sand_medium():
    r = get_presumed_bearing_pressure(Soil.MEDIUM_SAND, RelativeDensity.MEDIUM, MoistureCondition.DRY)
    assert r.valid is True
    assert r.p_conv == pytest.approx(500.0)


def test_fine_sand_dry_dense():
    r = get_presumed_bearing_pressure(Soil.FINE_SAND, RelativeDensity.DENSE, MoistureCondition.DRY)
    assert r.valid is True
    assert r.p_conv == pytest.approx(500.0)


def test_fine_sand_moist_medium():
    r = get_presumed_bearing_pressure(Soil.FINE_SAND, RelativeDensity.MEDIUM, MoistureCondition.MOIST)
    assert r.valid is True
    assert r.p_conv == pytest.approx(350.0)


def test_fine_sand_very_moist_dense():
    r = get_presumed_bearing_pressure(Soil.FINE_SAND, RelativeDensity.DENSE, MoistureCondition.VERY_MOIST)
    assert r.valid is True
    assert r.p_conv == pytest.approx(350.0)


def test_fine_sand_saturated_medium():
    r = get_presumed_bearing_pressure(Soil.FINE_SAND, RelativeDensity.MEDIUM, MoistureCondition.SATURATED)
    assert r.valid is True
    assert r.p_conv == pytest.approx(250.0)


def test_silty_sand_dry_dense():
    r = get_presumed_bearing_pressure(Soil.SILTY_SAND, RelativeDensity.DENSE, MoistureCondition.DRY)
    assert r.valid is True
    assert r.p_conv == pytest.approx(350.0)


def test_silty_sand_moist_medium():
    r = get_presumed_bearing_pressure(Soil.SILTY_SAND, RelativeDensity.MEDIUM, MoistureCondition.MOIST)
    assert r.valid is True
    assert r.p_conv == pytest.approx(200.0)


def test_silty_sand_very_moist_dense():
    r = get_presumed_bearing_pressure(Soil.SILTY_SAND, RelativeDensity.DENSE, MoistureCondition.VERY_MOIST)
    assert r.valid is True
    assert r.p_conv == pytest.approx(200.0)


def test_silty_sand_saturated_medium():
    r = get_presumed_bearing_pressure(Soil.SILTY_SAND, RelativeDensity.MEDIUM, MoistureCondition.SATURATED)
    assert r.valid is True
    assert r.p_conv == pytest.approx(150.0)


# ── Source & type ─────────────────────────────────────────────────────────────

def test_source_metadata():
    r = get_presumed_bearing_pressure(Soil.COARSE_SAND, RelativeDensity.DENSE, MoistureCondition.DRY)
    assert r.source.code == "NP 112:2014"
    assert r.source.table == "Tabelul D.3"


def test_result_type():
    r = get_presumed_bearing_pressure(Soil.COARSE_SAND, RelativeDensity.DENSE, MoistureCondition.DRY)
    assert isinstance(r, PresumedBearingPressureResult)


# ── Error cases ───────────────────────────────────────────────────────────────

def test_invalid_category():
    r = get_presumed_bearing_pressure("invalid", RelativeDensity.DENSE, MoistureCondition.DRY)
    assert r.valid is False
    assert len(r.errors) == 1


def test_invalid_relative_density():
    r = get_presumed_bearing_pressure(Soil.COARSE_SAND, "invalid", MoistureCondition.DRY)
    assert r.valid is False
    assert len(r.errors) == 1


def test_invalid_moisture_condition():
    r = get_presumed_bearing_pressure(Soil.FINE_SAND, RelativeDensity.DENSE, "invalid")
    assert r.valid is False
    assert len(r.errors) == 1


def test_non_sand_category_rejected():
    r = get_presumed_bearing_pressure(Soil.ROCKY, RelativeDensity.DENSE, MoistureCondition.DRY)
    assert r.valid is False
    assert len(r.errors) == 1
