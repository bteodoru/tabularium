import pytest
from tabularium.enums import Soil, SoilCategory
from tabularium.np_112_2014.allowable_bearing_capacity import WorkingConditionFactorResult
from tabularium.np_112_2014.allowable_bearing_capacity.working_condition_factor import (
    get_working_condition_factor,
)


# ── Rândul 1: fără condiție secundară (mₗ = 2.0) ─────────────────────────────

def test_boulder_sand_fill():
    r = get_working_condition_factor(soil=Soil.BOULDER_SAND_FILL)
    assert r.valid is True
    assert r.ml == pytest.approx(2.0)
    assert r.errors == []

def test_medium_sand():
    r = get_working_condition_factor(soil=Soil.MEDIUM_SAND)
    assert r.valid is True
    assert r.ml == pytest.approx(2.0)

def test_coarse_sand():
    r = get_working_condition_factor(soil=Soil.COARSE_SAND)
    assert r.valid is True
    assert r.ml == pytest.approx(2.0)

def test_gravel():
    r = get_working_condition_factor(soil=Soil.GRAVEL)
    assert r.valid is True
    assert r.ml == pytest.approx(2.0)


# ── Nisipuri fine (Sᵣ) ────────────────────────────────────────────────────────

def test_fine_sand_sr_at_threshold():
    r = get_working_condition_factor(soil=Soil.FINE_SAND, saturation_ratio=0.8)
    assert r.valid is True
    assert r.ml == pytest.approx(1.7)

def test_fine_sand_sr_above_threshold():
    r = get_working_condition_factor(soil=Soil.FINE_SAND, saturation_ratio=0.81)
    assert r.valid is True
    assert r.ml == pytest.approx(1.6)

def test_fine_sand_missing_saturation_ratio():
    r = get_working_condition_factor(soil=Soil.FINE_SAND)
    assert r.valid is False
    assert len(r.errors) == 1


# ── Nisipuri prăfoase (Sᵣ) ───────────────────────────────────────────────────

def test_silty_sand_dry_moist():
    r = get_working_condition_factor(soil=Soil.SILTY_SAND, saturation_ratio=0.5)
    assert r.valid is True
    assert r.ml == pytest.approx(1.5)

def test_silty_sand_very_moist():
    r = get_working_condition_factor(soil=Soil.SILTY_SAND, saturation_ratio=0.9)
    assert r.valid is True
    assert r.ml == pytest.approx(1.3)

def test_silty_sand_missing_saturation_ratio():
    r = get_working_condition_factor(soil=Soil.SILTY_SAND)
    assert r.valid is False
    assert len(r.errors) == 1


# ── Bolovănișuri cu fill coeziv (Iᶜ) ─────────────────────────────────────────

def test_boulder_cohesive_fill_stiff():
    r = get_working_condition_factor(soil=Soil.BOULDER_COHESIVE_FILL, consistency_index=0.5)
    assert r.valid is True
    assert r.ml == pytest.approx(1.3)

def test_boulder_cohesive_fill_soft():
    r = get_working_condition_factor(soil=Soil.BOULDER_COHESIVE_FILL, consistency_index=0.49)
    assert r.valid is True
    assert r.ml == pytest.approx(1.1)

def test_boulder_cohesive_fill_missing_ic():
    r = get_working_condition_factor(soil=Soil.BOULDER_COHESIVE_FILL)
    assert r.valid is False
    assert len(r.errors) == 1


# ── Pietriș cu fill coeziv (Iᶜ) ──────────────────────────────────────────────

def test_gravel_cohesive_fill_stiff():
    r = get_working_condition_factor(soil=Soil.GRAVEL_COHESIVE_FILL, consistency_index=0.7)
    assert r.valid is True
    assert r.ml == pytest.approx(1.3)

def test_gravel_cohesive_fill_soft():
    r = get_working_condition_factor(soil=Soil.GRAVEL_COHESIVE_FILL, consistency_index=0.3)
    assert r.valid is True
    assert r.ml == pytest.approx(1.1)

def test_gravel_cohesive_fill_missing_ic():
    r = get_working_condition_factor(soil=Soil.GRAVEL_COHESIVE_FILL)
    assert r.valid is False
    assert len(r.errors) == 1


# ── Pământuri coezive generice via SoilCategory (Iᶜ) ─────────────────────────

def test_cohesive_category_stiff():
    r = get_working_condition_factor(soil_category=SoilCategory.COHESIVE, consistency_index=0.75)
    assert r.valid is True
    assert r.ml == pytest.approx(1.4)

def test_cohesive_category_ic_exactly_05():
    r = get_working_condition_factor(soil_category=SoilCategory.COHESIVE, consistency_index=0.5)
    assert r.valid is True
    assert r.ml == pytest.approx(1.4)

def test_cohesive_category_soft():
    r = get_working_condition_factor(soil_category=SoilCategory.COHESIVE, consistency_index=0.49)
    assert r.valid is True
    assert r.ml == pytest.approx(1.1)

def test_cohesive_category_missing_ic():
    r = get_working_condition_factor(soil_category=SoilCategory.COHESIVE)
    assert r.valid is False
    assert len(r.errors) == 1

def test_non_cohesive_category_rejected():
    r = get_working_condition_factor(soil_category=SoilCategory.NON_COHESIVE)
    assert r.valid is False
    assert len(r.errors) == 1


# ── Validare parametri ────────────────────────────────────────────────────────

def test_neither_soil_nor_category():
    r = get_working_condition_factor()
    assert r.valid is False
    assert len(r.errors) == 1

def test_both_soil_and_category():
    r = get_working_condition_factor(
        soil=Soil.GRAVEL,
        soil_category=SoilCategory.COHESIVE,
    )
    assert r.valid is False
    assert len(r.errors) == 1


# ── Categorii neacceptate de H.7 ─────────────────────────────────────────────

def test_gravel_clean_crystal_rejected():
    r = get_working_condition_factor(soil=Soil.GRAVEL_CLEAN_CRYSTAL)
    assert r.valid is False
    assert len(r.errors) == 1

def test_boulder_gravel_fill_rejected():
    r = get_working_condition_factor(soil=Soil.BOULDER_GRAVEL_FILL)
    assert r.valid is False
    assert len(r.errors) == 1

def test_invalid_string_rejected():
    r = get_working_condition_factor(soil="invalid")
    assert r.valid is False
    assert len(r.errors) == 1


# ── Metadata ──────────────────────────────────────────────────────────────────

def test_source_metadata_via_soil():
    r = get_working_condition_factor(soil=Soil.GRAVEL)
    assert r.source.code == "NP 112:2014"
    assert r.source.table == "Tabelul H.7"

def test_source_metadata_via_category():
    r = get_working_condition_factor(soil_category=SoilCategory.COHESIVE, consistency_index=0.6)
    assert r.source.code == "NP 112:2014"
    assert r.source.table == "Tabelul H.7"

def test_result_type():
    r = get_working_condition_factor(soil=Soil.GRAVEL)
    assert isinstance(r, WorkingConditionFactorResult)
