import pytest
from tabularium.np_112_2014.presumed_bearing_pressure.boulders import (
    Soil,
    PresumedBearingPressureResult,
    get_presumed_bearing_pressure,
)


# ── BOULDER_GRAVEL_FILL — fixed value ─────────────────────────────────────────

def test_boulder_gravel_fill_fixed():
    r = get_presumed_bearing_pressure(Soil.BOULDER_GRAVEL_FILL)
    assert r.valid is True
    assert r.p_conv == pytest.approx(750.0)
    assert r.p_conv_range is None
    assert r.is_resolved is True
    assert r.errors == []
    assert r.warnings == []


def test_boulder_gravel_fill_ignores_ic():
    r = get_presumed_bearing_pressure(Soil.BOULDER_GRAVEL_FILL, consistency_index=0.7)
    assert r.valid is True
    assert r.p_conv == pytest.approx(750.0)


# ── BOULDER_COHESIVE_FILL — interpolable range ────────────────────────────────────

def test_boulder_clay_fill_no_ic_returns_range():
    r = get_presumed_bearing_pressure(Soil.BOULDER_COHESIVE_FILL)
    assert r.valid is True
    assert r.p_conv is None
    assert r.p_conv_range == (350.0, 600.0)
    assert r.is_resolved is False
    assert len(r.warnings) == 1


def test_boulder_clay_fill_ic_min():
    r = get_presumed_bearing_pressure(Soil.BOULDER_COHESIVE_FILL, consistency_index=0.5)
    assert r.valid is True
    assert r.p_conv == pytest.approx(350.0)
    assert r.interpolated is False


def test_boulder_clay_fill_ic_max():
    r = get_presumed_bearing_pressure(Soil.BOULDER_COHESIVE_FILL, consistency_index=1.0)
    assert r.valid is True
    assert r.p_conv == pytest.approx(600.0)
    assert r.interpolated is False


def test_boulder_clay_fill_ic_interpolated():
    # IC=0.75 is midpoint of [0.5, 1.0] → 350 + 0.5*(600-350) = 475
    r = get_presumed_bearing_pressure(Soil.BOULDER_COHESIVE_FILL, consistency_index=0.75)
    assert r.valid is True
    assert r.p_conv == pytest.approx(475.0)
    assert r.interpolated is True


def test_boulder_clay_fill_ic_below_range():
    r = get_presumed_bearing_pressure(Soil.BOULDER_COHESIVE_FILL, consistency_index=0.3)
    assert r.valid is False
    assert len(r.errors) == 1


def test_boulder_clay_fill_ic_above_range():
    r = get_presumed_bearing_pressure(Soil.BOULDER_COHESIVE_FILL, consistency_index=1.1)
    assert r.valid is False
    assert len(r.errors) == 1


def test_source_metadata():
    r = get_presumed_bearing_pressure(Soil.BOULDER_GRAVEL_FILL)
    assert r.source.code == "NP 112:2014"
    assert r.source.table == "Tabelul D.2"


def test_result_type():
    r = get_presumed_bearing_pressure(Soil.BOULDER_GRAVEL_FILL)
    assert isinstance(r, PresumedBearingPressureResult)


def test_invalid_category():
    r = get_presumed_bearing_pressure("invalid")
    assert r.valid is False
    assert len(r.errors) == 1


def test_non_boulder_category_rejected():
    r = get_presumed_bearing_pressure(Soil.FINE_SAND)
    assert r.valid is False
    assert len(r.errors) == 1
