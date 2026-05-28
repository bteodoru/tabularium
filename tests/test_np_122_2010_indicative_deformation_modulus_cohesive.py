import pytest
from tabularium.np_122_2010.indicative_deformation_modulus.cohesive import (
    DeformationModulusCohesiveResult,
    get_deformation_modulus,
)


# ── Exact lookup ──────────────────────────────────────────────────────────────

def test_exact_ip_lt10_e045():
    # IP <10, IC 0.25-1.00, e=0.45 (exact tabulated value)
    r = get_deformation_modulus(ip=7.0, ic=0.80, e=0.45)
    assert r.valid is True
    assert r.interpolated is False
    assert r.e_modulus == pytest.approx(32_000.0)
    assert r.ip_category == "<10"
    assert r.ic_range == "0.25-1.00"
    assert r.e_lower == pytest.approx(0.45)
    assert r.e_upper == pytest.approx(0.45)
    assert r.errors == []
    assert r.warnings == []


def test_exact_ip_10_20_ic_075_e055():
    # IP 10-20, IC 0.75-1.00, e=0.55 (exact)
    r = get_deformation_modulus(ip=15.0, ic=0.80, e=0.55)
    assert r.valid is True
    assert r.interpolated is False
    assert r.e_modulus == pytest.approx(27_000.0)
    assert r.ip_category == "10-20"
    assert r.ic_range == "0.75-1.00"


def test_exact_ip_10_20_ic_050_e075():
    # IP 10-20, IC 0.50-0.75, e=0.75 (exact)
    r = get_deformation_modulus(ip=15.0, ic=0.60, e=0.75)
    assert r.valid is True
    assert r.interpolated is False
    assert r.e_modulus == pytest.approx(14_000.0)
    assert r.ic_range == "0.50-0.75"


def test_exact_ip_gt20_ic_075_e105():
    # IP >20, IC 0.75-1.00, e=1.05 (exact, boundary)
    r = get_deformation_modulus(ip=25.0, ic=0.80, e=1.05)
    assert r.valid is True
    assert r.interpolated is False
    assert r.e_modulus == pytest.approx(12_000.0)
    assert r.ip_category == ">20"


def test_exact_ip_gt20_ic_050_e065():
    # IP >20, IC 0.50-0.75, e=0.65 (exact)
    r = get_deformation_modulus(ip=25.0, ic=0.60, e=0.65)
    assert r.valid is True
    assert r.interpolated is False
    assert r.e_modulus == pytest.approx(21_000.0)
    assert r.ic_range == "0.50-0.75"


# ── Interpolated lookup ───────────────────────────────────────────────────────

def test_interpolated_ip_lt10_midpoint():
    # IP <10, IC 0.25-1.00, e=0.50 (between 0.45→32000 and 0.55→24000)
    # t = (0.50-0.45)/(0.55-0.45) = 0.5
    # E = 32000 + 0.5*(24000-32000) = 28000
    r = get_deformation_modulus(ip=7.0, ic=0.80, e=0.50)
    assert r.valid is True
    assert r.interpolated is True
    assert r.e_modulus == pytest.approx(28_000.0)
    assert r.e_lower == pytest.approx(0.45)
    assert r.e_upper == pytest.approx(0.55)


def test_interpolated_ip_10_20_ic_075():
    # IP 10-20, IC 0.75-1.00, e=0.70 (between 0.65→22000 and 0.75→17000)
    # t = (0.70-0.65)/(0.75-0.65) = 0.5
    # E = 22000 + 0.5*(17000-22000) = 19500
    r = get_deformation_modulus(ip=15.0, ic=0.80, e=0.70)
    assert r.valid is True
    assert r.interpolated is True
    assert r.e_modulus == pytest.approx(19_500.0)


def test_interpolated_ip_gt20_ic_050():
    # IP >20, IC 0.50-0.75, e=0.70 (between 0.65→21000 and 0.75→18000)
    # t = (0.70-0.65)/(0.75-0.65) = 0.5
    # E = 21000 + 0.5*(18000-21000) = 19500
    r = get_deformation_modulus(ip=25.0, ic=0.60, e=0.70)
    assert r.valid is True
    assert r.interpolated is True
    assert r.e_modulus == pytest.approx(19_500.0)


# ── IP boundaries ─────────────────────────────────────────────────────────────

def test_ip_exactly_10():
    r = get_deformation_modulus(ip=10.0, ic=0.80, e=0.45)
    assert r.ip_category == "10-20"
    assert r.valid is True
    assert r.e_modulus == pytest.approx(34_000.0)


def test_ip_exactly_20():
    r = get_deformation_modulus(ip=20.0, ic=0.80, e=0.45)
    assert r.ip_category == "10-20"
    assert r.valid is True


def test_ip_just_above_20():
    r = get_deformation_modulus(ip=20.1, ic=0.80, e=0.55)
    assert r.ip_category == ">20"
    assert r.valid is True


# ── Out-of-range errors ───────────────────────────────────────────────────────

def test_ic_below_025_ip_lt10():
    r = get_deformation_modulus(ip=7.0, ic=0.20, e=0.65)
    assert r.valid is False
    assert len(r.errors) == 1


def test_ic_below_050_ip_10_20():
    r = get_deformation_modulus(ip=15.0, ic=0.40, e=0.65)
    assert r.valid is False
    assert len(r.errors) == 1


def test_ic_below_050_ip_gt20():
    r = get_deformation_modulus(ip=25.0, ic=0.40, e=0.65)
    assert r.valid is False
    assert len(r.errors) == 1


def test_e_below_minimum_for_row():
    # IP >20, IC 0.75-1.00: e_min = 0.55; e=0.45 → error
    r = get_deformation_modulus(ip=25.0, ic=0.80, e=0.45)
    assert r.valid is False
    assert len(r.errors) == 1


def test_e_above_maximum_for_row():
    # IP <10, IC 0.25-1.00: e_max = 0.85; e=0.95 → error
    r = get_deformation_modulus(ip=7.0, ic=0.80, e=0.95)
    assert r.valid is False
    assert len(r.errors) == 1


# ── IC > 1.0 warning ─────────────────────────────────────────────────────────

def test_ic_above_1_warning_ip_lt10():
    # IC > 1.0 for IP <10: warning, still valid, use "0.25-1.00"
    r = get_deformation_modulus(ip=7.0, ic=1.10, e=0.65)
    assert r.valid is True
    assert len(r.warnings) == 1
    assert r.ic_range == "0.25-1.00"


def test_ic_above_1_warning_ip_10_20():
    # IC > 1.0 for IP 10-20: warning, use "0.75-1.00" conservatively
    r = get_deformation_modulus(ip=15.0, ic=1.10, e=0.65)
    assert r.valid is True
    assert len(r.warnings) == 1
    assert r.ic_range == "0.75-1.00"


# ── Source metadata ───────────────────────────────────────────────────────────

def test_source_metadata():
    r = get_deformation_modulus(ip=15.0, ic=0.80, e=0.55)
    assert r.source is not None
    assert r.source.code == "NP 122:2010"
    assert r.source.table == "Tabelul A.6.4"


def test_result_type():
    r = get_deformation_modulus(ip=15.0, ic=0.80, e=0.55)
    assert isinstance(r, DeformationModulusCohesiveResult)
