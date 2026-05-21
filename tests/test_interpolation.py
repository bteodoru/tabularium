import pytest
from tabularium.interpolation import LinearResult, interpolate_linear


def test_exact_match_first():
    knots = {0.45: 25.0, 0.55: 24.0, 0.65: 22.0}
    r = interpolate_linear(knots, 0.45)
    assert r.value == pytest.approx(25.0)
    assert r.interpolated is False
    assert r.x_lower == pytest.approx(0.45)
    assert r.x_upper == pytest.approx(0.45)
    assert r.warnings == []


def test_exact_match_middle():
    knots = {0.45: 25.0, 0.55: 24.0, 0.65: 22.0}
    r = interpolate_linear(knots, 0.55)
    assert r.value == pytest.approx(24.0)
    assert r.interpolated is False


def test_exact_match_last():
    knots = {0.45: 25.0, 0.55: 24.0, 0.65: 22.0}
    r = interpolate_linear(knots, 0.65)
    assert r.value == pytest.approx(22.0)
    assert r.interpolated is False


def test_interpolated_midpoint():
    # Between 0.55 (24.0) and 0.65 (22.0) → t=0.5 → 23.0
    knots = {0.45: 25.0, 0.55: 24.0, 0.65: 22.0}
    r = interpolate_linear(knots, 0.60)
    assert r.value == pytest.approx(23.0)
    assert r.interpolated is True
    assert r.x_lower == pytest.approx(0.55)
    assert r.x_upper == pytest.approx(0.65)
    assert r.warnings == []


def test_interpolated_one_quarter():
    # Between 0.45 (25.0) and 0.55 (24.0) → t=0.25 → 24.75
    knots = {0.45: 25.0, 0.55: 24.0, 0.65: 22.0}
    r = interpolate_linear(knots, 0.475)
    assert r.value == pytest.approx(24.75)
    assert r.interpolated is True
    assert r.x_lower == pytest.approx(0.45)
    assert r.x_upper == pytest.approx(0.55)


def test_below_range():
    knots = {0.55: 24.0, 0.65: 22.0}
    r = interpolate_linear(knots, 0.40)
    assert r.value is None
    assert r.interpolated is False
    assert r.x_lower is None
    assert r.x_upper is None
    assert len(r.warnings) == 1
    assert "0.55" in r.warnings[0]


def test_above_range():
    knots = {0.55: 24.0, 0.65: 22.0}
    r = interpolate_linear(knots, 0.80)
    assert r.value is None
    assert len(r.warnings) == 1
    assert "0.65" in r.warnings[0]


def test_single_knot_exact():
    knots = {0.55: 24.0}
    r = interpolate_linear(knots, 0.55)
    assert r.value == pytest.approx(24.0)
    assert r.interpolated is False


def test_single_knot_miss():
    knots = {0.55: 24.0}
    r = interpolate_linear(knots, 0.60)
    assert r.value is None
    assert len(r.warnings) == 1


def test_result_type():
    knots = {0.5: 10.0, 0.7: 8.0}
    r = interpolate_linear(knots, 0.6)
    assert isinstance(r, LinearResult)
