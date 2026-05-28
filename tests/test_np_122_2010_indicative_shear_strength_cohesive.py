import pytest
from tabularium.np_122_2010.indicative_shear_strength.cohesive import ShearStrengthResult, get_phi_c


# ── Lookup exact ──────────────────────────────────────────────────────────────

def test_exact_lookup_ip_lt10_ic_0_75_1_00():
    # IP <10, IC 0.75-1.00, e=0.45 (exact)
    r = get_phi_c(ip=7.0, ic=0.80, e=0.45)
    assert r.valid is True
    assert r.phi == pytest.approx(25.0)
    assert r.c == pytest.approx(10.0)
    assert r.interpolated is False
    assert r.ip_category == "<10"
    assert r.ic_range == "0.75-1.00"
    assert r.e_lower == pytest.approx(0.45)
    assert r.e_upper == pytest.approx(0.45)
    assert r.warnings == []
    assert r.errors == []


def test_exact_lookup_ip_10_20_ic_0_25_0_50():
    # IP 10-20, IC 0.25-0.50, e=1.05 (exact, boundary)
    r = get_phi_c(ip=15.0, ic=0.30, e=1.05)
    assert r.valid is True
    assert r.phi == pytest.approx(10.0)
    assert r.c == pytest.approx(7.0)
    assert r.interpolated is False


def test_exact_lookup_ip_gt20_ic_0_75_1_00_e_at_1_05():
    # IP >20, IC 0.75-1.00, e=1.05 (exact, boundary)
    r = get_phi_c(ip=25.0, ic=0.80, e=1.05)
    assert r.valid is True
    assert r.phi == pytest.approx(11.0)
    assert r.c == pytest.approx(24.0)
    assert r.interpolated is False


# ── Lookup interpolat ─────────────────────────────────────────────────────────

def test_interpolated_lookup_midpoint():
    # IP 10-20, IC 0.50-0.75, e=0.60 (between 0.55→(19,22) and 0.65→(18,18))
    # t = (0.60-0.55)/(0.65-0.55) = 0.5
    # phi = 19 + 0.5*(18-19) = 18.5
    # c   = 22 + 0.5*(18-22) = 20.0
    r = get_phi_c(ip=15.0, ic=0.60, e=0.60)
    assert r.valid is True
    assert r.interpolated is True
    assert r.phi == pytest.approx(18.5)
    assert r.c == pytest.approx(20.0)
    assert r.e_lower == pytest.approx(0.55)
    assert r.e_upper == pytest.approx(0.65)
    assert r.warnings == []


def test_interpolated_lookup_ip_gt20():
    # IP >20, IC 0.50-0.75, e=0.70 (between 0.65→(15,37) and 0.75→(14,33))
    # t = (0.70-0.65)/(0.75-0.65) = 0.5
    # phi = 15 + 0.5*(14-15) = 14.5
    # c   = 37 + 0.5*(33-37) = 35.0
    r = get_phi_c(ip=25.0, ic=0.60, e=0.70)
    assert r.valid is True
    assert r.phi == pytest.approx(14.5)
    assert r.c == pytest.approx(35.0)


# ── Source ────────────────────────────────────────────────────────────────────

def test_source_metadata():
    r = get_phi_c(ip=15.0, ic=0.60, e=0.55)
    assert r.source is not None
    assert r.source.code == "NP 122:2010"
    assert r.source.table == "Tabelul A.6.2"


# ── Cazuri eroare ─────────────────────────────────────────────────────────────

def test_ic_below_025_returns_error():
    r = get_phi_c(ip=15.0, ic=0.10, e=0.65)
    assert r.valid is False
    assert len(r.errors) == 1


def test_ic_row_missing_for_ip_category():
    # IP <10 nu are rândul "0.25-0.50" → eroare
    r = get_phi_c(ip=7.0, ic=0.30, e=0.65)
    assert r.valid is False
    assert len(r.errors) == 1


def test_e_below_minimum_for_row():
    # IP 10-20, IC 0.25-0.50 — e_min = 0.65; e=0.45 < 0.65 → eroare
    r = get_phi_c(ip=15.0, ic=0.30, e=0.45)
    assert r.valid is False
    assert len(r.errors) == 1


def test_e_above_maximum_for_row():
    # IP <10, IC 0.75-1.00 — e_max = 0.65; e=0.80 > 0.65 → eroare
    r = get_phi_c(ip=7.0, ic=0.80, e=0.80)
    assert r.valid is False
    assert len(r.errors) == 1


# ── Cazuri warning (valid) ────────────────────────────────────────────────────

def test_ic_above_1_warning_and_valid():
    # IC > 1.0 → warning, se utilizează rândul 0.75-1.00
    r = get_phi_c(ip=15.0, ic=1.20, e=0.65)
    assert r.valid is True
    assert len(r.warnings) == 1
    assert "supraconsolidat" in r.warnings[0]
    assert r.ic_range == "0.75-1.00"


# ── Frontiere categorii I_P ───────────────────────────────────────────────────

def test_ip_boundary_exactly_10():
    # IP=10 → categorie "10-20"
    r = get_phi_c(ip=10.0, ic=0.80, e=0.45)
    assert r.ip_category == "10-20"
    assert r.valid is True
    assert r.phi == pytest.approx(22.0)
    assert r.c == pytest.approx(30.0)


def test_ip_boundary_exactly_20():
    # IP=20 → categorie "10-20"
    r = get_phi_c(ip=20.0, ic=0.80, e=0.45)
    assert r.ip_category == "10-20"
    assert r.valid is True


def test_ip_just_above_20():
    # IP=20.1 → categorie ">20"
    r = get_phi_c(ip=20.1, ic=0.80, e=0.55)
    assert r.ip_category == ">20"
    assert r.valid is True


# ── Tip rezultat ──────────────────────────────────────────────────────────────

def test_result_type():
    r = get_phi_c(ip=15.0, ic=0.60, e=0.55)
    assert isinstance(r, ShearStrengthResult)
