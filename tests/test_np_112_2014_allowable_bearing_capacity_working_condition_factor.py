import pytest
from tabularium.enums import Soil
from tabularium.np_112_2014.allowable_bearing_capacity import WorkingConditionFactorResult
from tabularium.np_112_2014.allowable_bearing_capacity.working_condition_factor import (
    get_working_condition_factor,
)


# ── Rândul 1: fără condiție secundară (m₁ = 2.0) ─────────────────────────────

def test_boulder_sand_fill():
    r = get_working_condition_factor(Soil.BOULDER_SAND_FILL)
    assert r.valid is True
    assert r.m1 == pytest.approx(2.0)
    assert r.errors == []

def test_medium_sand():
    r = get_working_condition_factor(Soil.MEDIUM_SAND)
    assert r.valid is True
    assert r.m1 == pytest.approx(2.0)

def test_coarse_sand():
    r = get_working_condition_factor(Soil.COARSE_SAND)
    assert r.valid is True
    assert r.m1 == pytest.approx(2.0)

def test_gravel():
    r = get_working_condition_factor(Soil.GRAVEL)
    assert r.valid is True
    assert r.m1 == pytest.approx(2.0)


# ── Nisipuri fine (Sᵣ) ────────────────────────────────────────────────────────

def test_fine_sand_sr_at_threshold():
    # Sᵣ = 0.8 → uscate/umede → m₁ = 1.7
    r = get_working_condition_factor(Soil.FINE_SAND, saturation_ratio=0.8)
    assert r.valid is True
    assert r.m1 == pytest.approx(1.7)

def test_fine_sand_sr_above_threshold():
    # Sᵣ > 0.8 → foarte umede/saturate → m₁ = 1.6
    r = get_working_condition_factor(Soil.FINE_SAND, saturation_ratio=0.81)
    assert r.valid is True
    assert r.m1 == pytest.approx(1.6)

def test_fine_sand_missing_saturation_ratio():
    r = get_working_condition_factor(Soil.FINE_SAND)
    assert r.valid is False
    assert len(r.errors) == 1


# ── Nisipuri prăfoase (Sᵣ) ───────────────────────────────────────────────────

def test_silty_sand_dry_moist():
    r = get_working_condition_factor(Soil.SILTY_SAND, saturation_ratio=0.5)
    assert r.valid is True
    assert r.m1 == pytest.approx(1.5)

def test_silty_sand_very_moist():
    r = get_working_condition_factor(Soil.SILTY_SAND, saturation_ratio=0.9)
    assert r.valid is True
    assert r.m1 == pytest.approx(1.3)

def test_silty_sand_missing_saturation_ratio():
    r = get_working_condition_factor(Soil.SILTY_SAND)
    assert r.valid is False
    assert len(r.errors) == 1


# ── Bolovănișuri cu fill coeziv (Iᶜ) ─────────────────────────────────────────

def test_boulder_cohesive_fill_stiff():
    # Iᶜ = 0.5 (exact la limită ≥ 0.5) → m₁ = 1.3
    r = get_working_condition_factor(Soil.BOULDER_COHESIVE_FILL, consistency_index=0.5)
    assert r.valid is True
    assert r.m1 == pytest.approx(1.3)

def test_boulder_cohesive_fill_soft():
    r = get_working_condition_factor(Soil.BOULDER_COHESIVE_FILL, consistency_index=0.49)
    assert r.valid is True
    assert r.m1 == pytest.approx(1.1)

def test_boulder_cohesive_fill_missing_ic():
    r = get_working_condition_factor(Soil.BOULDER_COHESIVE_FILL)
    assert r.valid is False
    assert len(r.errors) == 1


# ── Pietriș cu fill coeziv (Iᶜ) ──────────────────────────────────────────────

def test_gravel_cohesive_fill_stiff():
    r = get_working_condition_factor(Soil.GRAVEL_COHESIVE_FILL, consistency_index=0.7)
    assert r.valid is True
    assert r.m1 == pytest.approx(1.3)

def test_gravel_cohesive_fill_soft():
    r = get_working_condition_factor(Soil.GRAVEL_COHESIVE_FILL, consistency_index=0.3)
    assert r.valid is True
    assert r.m1 == pytest.approx(1.1)

def test_gravel_cohesive_fill_missing_ic():
    r = get_working_condition_factor(Soil.GRAVEL_COHESIVE_FILL)
    assert r.valid is False
    assert len(r.errors) == 1


# ── Pământuri coezive (Iᶜ) ────────────────────────────────────────────────────

def test_cohesive_soil_stiff():
    r = get_working_condition_factor(Soil.COHESIVE_SOIL, consistency_index=0.75)
    assert r.valid is True
    assert r.m1 == pytest.approx(1.4)

def test_cohesive_soil_ic_exactly_05():
    # Iᶜ = 0.5 → la limita ≥ 0.5 → m₁ = 1.4
    r = get_working_condition_factor(Soil.COHESIVE_SOIL, consistency_index=0.5)
    assert r.valid is True
    assert r.m1 == pytest.approx(1.4)

def test_cohesive_soil_soft():
    r = get_working_condition_factor(Soil.COHESIVE_SOIL, consistency_index=0.49)
    assert r.valid is True
    assert r.m1 == pytest.approx(1.1)

def test_cohesive_soil_missing_ic():
    r = get_working_condition_factor(Soil.COHESIVE_SOIL)
    assert r.valid is False
    assert len(r.errors) == 1


# ── Categorii neacceptate de H.7 ─────────────────────────────────────────────

def test_gravel_clean_crystal_rejected():
    r = get_working_condition_factor(Soil.GRAVEL_CLEAN_CRYSTAL)
    assert r.valid is False
    assert len(r.errors) == 1

def test_boulder_gravel_fill_rejected():
    r = get_working_condition_factor(Soil.BOULDER_GRAVEL_FILL)
    assert r.valid is False
    assert len(r.errors) == 1

def test_invalid_string_rejected():
    r = get_working_condition_factor("invalid")
    assert r.valid is False
    assert len(r.errors) == 1


# ── Metadata ──────────────────────────────────────────────────────────────────

def test_source_metadata():
    r = get_working_condition_factor(Soil.GRAVEL)
    assert r.source.code == "NP 112:2014"
    assert r.source.table == "Tabelul H.7"

def test_result_type():
    r = get_working_condition_factor(Soil.GRAVEL)
    assert isinstance(r, WorkingConditionFactorResult)
