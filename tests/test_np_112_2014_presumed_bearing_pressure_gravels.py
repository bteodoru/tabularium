import pytest
from tabularium.np_112_2014.presumed_bearing_pressure.gravels import (
    Soil,
    PresumedBearingPressureResult,
    get_presumed_bearing_pressure,
)


def test_gravel_clean_crystal():
    r = get_presumed_bearing_pressure(Soil.GRAVEL_CLEAN_CRYSTAL)
    assert r.valid is True
    assert r.p_conv == pytest.approx(600.0)
    assert r.p_conv_range is None
    assert r.errors == []


def test_gravel_with_sand():
    r = get_presumed_bearing_pressure(Soil.GRAVEL_WITH_SAND)
    assert r.valid is True
    assert r.p_conv == pytest.approx(550.0)


def test_gravel_sedimentary():
    r = get_presumed_bearing_pressure(Soil.GRAVEL_SEDIMENTARY)
    assert r.valid is True
    assert r.p_conv == pytest.approx(350.0)


def test_gravel_silty_sand_no_ic_returns_range():
    r = get_presumed_bearing_pressure(Soil.GRAVEL_SILTY_SAND)
    assert r.valid is True
    assert r.p_conv is None
    assert r.p_conv_range == (350.0, 500.0)
    assert len(r.warnings) == 1


def test_gravel_silty_sand_ic_min():
    r = get_presumed_bearing_pressure(Soil.GRAVEL_SILTY_SAND, consistency_index=0.5)
    assert r.valid is True
    assert r.p_conv == pytest.approx(350.0)
    assert r.interpolated is False


def test_gravel_silty_sand_ic_max():
    r = get_presumed_bearing_pressure(Soil.GRAVEL_SILTY_SAND, consistency_index=1.0)
    assert r.valid is True
    assert r.p_conv == pytest.approx(500.0)
    assert r.interpolated is False


def test_gravel_silty_sand_ic_interpolated():
    # IC=0.75 midpoint [0.5, 1.0] → 350 + 0.5*150 = 425
    r = get_presumed_bearing_pressure(Soil.GRAVEL_SILTY_SAND, consistency_index=0.75)
    assert r.valid is True
    assert r.p_conv == pytest.approx(425.0)
    assert r.interpolated is True


def test_gravel_silty_sand_ic_out_of_range():
    r = get_presumed_bearing_pressure(Soil.GRAVEL_SILTY_SAND, consistency_index=0.2)
    assert r.valid is False
    assert len(r.errors) == 1


def test_source_metadata():
    r = get_presumed_bearing_pressure(Soil.GRAVEL_WITH_SAND)
    assert r.source.code == "NP 112:2014"
    assert r.source.table == "Tabelul D.2"


def test_invalid_category():
    r = get_presumed_bearing_pressure("invalid")
    assert r.valid is False
    assert len(r.errors) == 1


def test_non_gravel_category_rejected():
    r = get_presumed_bearing_pressure(Soil.ROCKY)
    assert r.valid is False
    assert len(r.errors) == 1
