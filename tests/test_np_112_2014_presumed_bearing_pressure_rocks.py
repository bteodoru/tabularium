import pytest
from tabularium.np_112_2014.presumed_bearing_pressure.rocks import (
    Soil,
    PresumedBearingPressureResult,
    get_presumed_bearing_pressure,
)


def test_rocky_returns_range():
    r = get_presumed_bearing_pressure(Soil.ROCKY)
    assert r.valid is True
    assert r.p_conv is None
    assert r.p_conv_range == (1000.0, 6000.0)
    assert r.is_resolved is False
    assert r.errors == []
    assert len(r.warnings) == 1


def test_semi_rocky_marl_returns_range():
    r = get_presumed_bearing_pressure(Soil.SEMI_ROCKY_MARL)
    assert r.valid is True
    assert r.p_conv_range == (350.0, 1100.0)
    assert r.is_resolved is False


def test_semi_rocky_shale_returns_range():
    r = get_presumed_bearing_pressure(Soil.SEMI_ROCKY_SHALE)
    assert r.valid is True
    assert r.p_conv_range == (600.0, 850.0)


def test_warning_present():
    r = get_presumed_bearing_pressure(Soil.ROCKY)
    assert any("compactit" in w.lower() or "degradare" in w.lower() for w in r.warnings)


def test_source_metadata():
    r = get_presumed_bearing_pressure(Soil.ROCKY)
    assert r.source is not None
    assert r.source.code == "NP 112:2014"
    assert r.source.table == "Tabelul D.1"


def test_result_type():
    r = get_presumed_bearing_pressure(Soil.ROCKY)
    assert isinstance(r, PresumedBearingPressureResult)


def test_invalid_category():
    r = get_presumed_bearing_pressure("invalid")
    assert r.valid is False
    assert len(r.errors) == 1


def test_non_rocky_category_rejected():
    r = get_presumed_bearing_pressure(Soil.FINE_SAND)
    assert r.valid is False
    assert len(r.errors) == 1
