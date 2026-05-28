import pytest
from tabularium.np_112_2014.presumed_bearing_pressure.fills import (
    FillType,
    FillSoilType,
    PresumedBearingPressureResult,
    get_presumed_bearing_pressure,
)


# ── Exact lookups la noduri (Sr ≤ 0.5 și Sr ≥ 0.8) ──────────────────────────────

def test_controlled_sandy_sr_low():
    r = get_presumed_bearing_pressure(FillType.CONTROLLED_COMPACTED, FillSoilType.SANDY_SLAG, saturation_degree=0.3)
    assert r.valid is True
    assert r.p_conv == pytest.approx(250.0)
    assert r.interpolated is False
    assert r.errors == []


def test_controlled_sandy_sr_high():
    r = get_presumed_bearing_pressure(FillType.CONTROLLED_COMPACTED, FillSoilType.SANDY_SLAG, saturation_degree=0.9)
    assert r.valid is True
    assert r.p_conv == pytest.approx(200.0)
    assert r.interpolated is False


def test_controlled_silty_sr_low():
    r = get_presumed_bearing_pressure(FillType.CONTROLLED_COMPACTED, FillSoilType.SILTY_FINE, saturation_degree=0.2)
    assert r.valid is True
    assert r.p_conv == pytest.approx(180.0)


def test_controlled_silty_sr_high():
    r = get_presumed_bearing_pressure(FillType.CONTROLLED_COMPACTED, FillSoilType.SILTY_FINE, saturation_degree=1.0)
    assert r.valid is True
    assert r.p_conv == pytest.approx(150.0)


def test_known_origin_sandy_sr_low():
    r = get_presumed_bearing_pressure(FillType.KNOWN_ORIGIN, FillSoilType.SANDY_SLAG, saturation_degree=0.0)
    assert r.valid is True
    assert r.p_conv == pytest.approx(180.0)


def test_known_origin_silty_sr_high():
    r = get_presumed_bearing_pressure(FillType.KNOWN_ORIGIN, FillSoilType.SILTY_FINE, saturation_degree=0.8)
    assert r.valid is True
    assert r.p_conv == pytest.approx(100.0)
    assert r.interpolated is False


# ── Interpolation ─────────────────────────────────────────────────────────────

def test_controlled_sandy_sr_midpoint():
    # Sr=0.65 midpoint [0.5, 0.8] → (250+200)/2 = 225
    r = get_presumed_bearing_pressure(FillType.CONTROLLED_COMPACTED, FillSoilType.SANDY_SLAG, saturation_degree=0.65)
    assert r.valid is True
    assert r.p_conv == pytest.approx(225.0)
    assert r.interpolated is True


def test_known_origin_silty_interpolated():
    # Sr=0.65 midpoint [0.5, 0.8] → (120+100)/2 = 110
    r = get_presumed_bearing_pressure(FillType.KNOWN_ORIGIN, FillSoilType.SILTY_FINE, saturation_degree=0.65)
    assert r.valid is True
    assert r.p_conv == pytest.approx(110.0)
    assert r.interpolated is True


def test_sr_at_lower_node():
    # Sr=0.5 exact node
    r = get_presumed_bearing_pressure(FillType.CONTROLLED_COMPACTED, FillSoilType.SANDY_SLAG, saturation_degree=0.5)
    assert r.valid is True
    assert r.p_conv == pytest.approx(250.0)
    assert r.interpolated is False


def test_sr_at_upper_node():
    # Sr=0.8 exact node
    r = get_presumed_bearing_pressure(FillType.CONTROLLED_COMPACTED, FillSoilType.SANDY_SLAG, saturation_degree=0.8)
    assert r.valid is True
    assert r.p_conv == pytest.approx(200.0)
    assert r.interpolated is False


# ── Out-of-range Sr ───────────────────────────────────────────────────────────

def test_sr_negative():
    r = get_presumed_bearing_pressure(FillType.CONTROLLED_COMPACTED, FillSoilType.SANDY_SLAG, saturation_degree=-0.1)
    assert r.valid is False
    assert len(r.errors) == 1


def test_sr_above_one():
    r = get_presumed_bearing_pressure(FillType.CONTROLLED_COMPACTED, FillSoilType.SANDY_SLAG, saturation_degree=1.1)
    assert r.valid is False
    assert len(r.errors) == 1


# ── Source & type ─────────────────────────────────────────────────────────────

def test_source_metadata():
    r = get_presumed_bearing_pressure(FillType.CONTROLLED_COMPACTED, FillSoilType.SANDY_SLAG, saturation_degree=0.3)
    assert r.source.code == "NP 112:2014"
    assert r.source.table == "Tabelul D.5"


def test_result_type():
    r = get_presumed_bearing_pressure(FillType.CONTROLLED_COMPACTED, FillSoilType.SANDY_SLAG, saturation_degree=0.3)
    assert isinstance(r, PresumedBearingPressureResult)


def test_invalid_fill_type():
    r = get_presumed_bearing_pressure("invalid", FillSoilType.SANDY_SLAG, saturation_degree=0.3)
    assert r.valid is False
    assert len(r.errors) == 1


def test_invalid_fill_soil_type():
    r = get_presumed_bearing_pressure(FillType.CONTROLLED_COMPACTED, "invalid", saturation_degree=0.3)
    assert r.valid is False
    assert len(r.errors) == 1
