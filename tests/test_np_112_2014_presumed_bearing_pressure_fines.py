import pytest
from tabularium.np_112_2014.presumed_bearing_pressure_fines import (
    PlasticityClass,
    PresumedBearingPressureResult,
    get_presumed_bearing_pressure,
)


# ── Exact node lookups ────────────────────────────────────────────────────────

def test_low_plasticity_exact_node_upper_band():
    # LOW, e=0.5, IC=0.75 → exact node in upper band → 325
    r = get_presumed_bearing_pressure(PlasticityClass.LOW, void_ratio=0.5, consistency_index=0.75)
    assert r.valid is True
    assert r.p_conv == pytest.approx(325.0)
    assert r.interpolated is False
    assert r.errors == []


def test_low_plasticity_exact_node_ic_1():
    # LOW, e=0.7, IC=1.0 → exact node → 300
    r = get_presumed_bearing_pressure(PlasticityClass.LOW, void_ratio=0.7, consistency_index=1.0)
    assert r.valid is True
    assert r.p_conv == pytest.approx(300.0)
    assert r.interpolated is False


def test_low_plasticity_exact_node_lower_band():
    # LOW, e=0.5, IC=0.5 → exact node in lower band → 300
    r = get_presumed_bearing_pressure(PlasticityClass.LOW, void_ratio=0.5, consistency_index=0.5)
    assert r.valid is True
    assert r.p_conv == pytest.approx(300.0)
    assert r.interpolated is False


def test_high_plasticity_exact_node():
    # HIGH, e=0.6, IC=1.0 → 525
    r = get_presumed_bearing_pressure(PlasticityClass.HIGH, void_ratio=0.6, consistency_index=1.0)
    assert r.valid is True
    assert r.p_conv == pytest.approx(525.0)


# ── Band boundary: IC=0.75 goes to upper band ─────────────────────────────────

def test_ic_0_75_uses_upper_band():
    # LOW, e=0.5, IC=0.75 → upper band, exact node → 325
    r = get_presumed_bearing_pressure(PlasticityClass.LOW, void_ratio=0.5, consistency_index=0.75)
    assert r.valid is True
    assert r.p_conv == pytest.approx(325.0)
    assert r.interpolated is False


# ── Successive interpolation ──────────────────────────────────────────────────

def test_low_plasticity_interpolate_e_only():
    # LOW, e=0.6 (midpoint [0.5,0.7]), IC=0.75 exact
    # upper band: e=0.5→325, e=0.7→285; at e=0.6 → (325+285)/2 = 305
    r = get_presumed_bearing_pressure(PlasticityClass.LOW, void_ratio=0.6, consistency_index=0.75)
    assert r.valid is True
    assert r.p_conv == pytest.approx(305.0)
    assert r.interpolated is True


def test_low_plasticity_interpolate_ic_only():
    # LOW, e=0.5 exact, IC=0.875 (midpoint [0.75,1.0])
    # upper band e=0.5: IC=0.75→325, IC=1.0→350; at IC=0.875 → (325+350)/2 = 337.5
    r = get_presumed_bearing_pressure(PlasticityClass.LOW, void_ratio=0.5, consistency_index=0.875)
    assert r.valid is True
    assert r.p_conv == pytest.approx(337.5)
    assert r.interpolated is True


def test_medium_plasticity_bilinear():
    # MEDIUM, upper band, e=0.6 (midpoint [0.5,0.7]), IC=0.875 (midpoint [0.75,1.0])
    # At e=0.5, IC=0.875 → (325+350)/2 = 337.5
    # At e=0.7, IC=0.875 → (285+300)/2 = 292.5
    # At e=0.6 → (337.5+292.5)/2 = 315.0
    r = get_presumed_bearing_pressure(PlasticityClass.MEDIUM, void_ratio=0.6, consistency_index=0.875)
    assert r.valid is True
    assert r.p_conv == pytest.approx(315.0)
    assert r.interpolated is True


# ── Out-of-range ──────────────────────────────────────────────────────────────

def test_ic_below_range():
    r = get_presumed_bearing_pressure(PlasticityClass.LOW, void_ratio=0.5, consistency_index=0.3)
    assert r.valid is False
    assert len(r.errors) == 1


def test_ic_above_range():
    r = get_presumed_bearing_pressure(PlasticityClass.LOW, void_ratio=0.5, consistency_index=1.1)
    assert r.valid is False
    assert len(r.errors) == 1


def test_e_above_limit_low():
    # LOW: e_max = 0.7
    r = get_presumed_bearing_pressure(PlasticityClass.LOW, void_ratio=0.8, consistency_index=0.8)
    assert r.valid is False
    assert len(r.errors) == 1


def test_e_below_minimum():
    r = get_presumed_bearing_pressure(PlasticityClass.LOW, void_ratio=0.3, consistency_index=0.8)
    assert r.valid is False
    assert len(r.errors) == 1


def test_e_at_limit_high():
    # HIGH: e_max = 1.1, e=1.1 is a data point → should be valid
    r = get_presumed_bearing_pressure(PlasticityClass.HIGH, void_ratio=1.1, consistency_index=1.0)
    assert r.valid is True
    assert r.p_conv == pytest.approx(300.0)


# ── Source & type ─────────────────────────────────────────────────────────────

def test_source_metadata():
    r = get_presumed_bearing_pressure(PlasticityClass.LOW, void_ratio=0.5, consistency_index=0.75)
    assert r.source.code == "NP 112:2014"
    assert r.source.table == "Tabelul D.4"


def test_result_type():
    r = get_presumed_bearing_pressure(PlasticityClass.LOW, void_ratio=0.5, consistency_index=0.75)
    assert isinstance(r, PresumedBearingPressureResult)


def test_invalid_plasticity_class():
    r = get_presumed_bearing_pressure("invalid", void_ratio=0.5, consistency_index=0.75)
    assert r.valid is False
    assert len(r.errors) == 1
