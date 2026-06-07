from tabularium.np_074_2022.terrain_condition import (
    TerrainConditionInput,
    TerrainConditionResult,
    classify_terrain_condition,
)
from tabularium.enums import (
    FillCategory,
    PlasticityClass,
    RelativeDensity,
    SoilGroup,
    TerrainCondition,
)


def test_imports():
    assert TerrainCondition.GOOD
    assert TerrainCondition.MEDIUM
    assert TerrainCondition.DIFFICULT
    assert SoilGroup.ROCKY
    assert SoilGroup.NON_COHESIVE
    assert SoilGroup.COHESIVE_FINE
    assert SoilGroup.FILL
    assert FillCategory.CONTROLLED_COMPACTED
    assert FillCategory.KNOWN_ORIGIN_ORGANIZED
    assert FillCategory.UNCONTROLLED
    assert FillCategory.HOUSEHOLD
    assert RelativeDensity.LOOSE


def test_input_dataclass_instantiation():
    inp = TerrainConditionInput(soil_group=SoilGroup.ROCKY)
    assert inp.soil_group == SoilGroup.ROCKY
    assert inp.collapsible is None
    assert inp.active is None
    assert inp.liquefiable is None
    assert inp.sliding_potential is None
    assert inp.stratification_uniform_horizontal is True


def test_result_dataclass_defaults():
    r = TerrainConditionResult()
    assert r.valid is False
    assert r.condition is None
    assert r.matched_table is None
    assert r.matched_row is None
    assert r.interpolated is False
    assert r.warnings == []
    assert r.errors == []


# ── Override flags ─────────────────────────────────────────────────────────────


def test_collapsible_true_returns_difficult_a3_row4():
    inp = TerrainConditionInput(
        soil_group=SoilGroup.COHESIVE_FINE,
        plasticity_class=PlasticityClass.LOW,
        void_ratio=0.6,
        consistency_index=0.80,
        collapsible=True,
    )
    r = classify_terrain_condition(inp)
    assert r.valid is True
    assert r.condition == TerrainCondition.DIFFICULT
    assert r.matched_table == "A.3"
    assert r.matched_row == 4


def test_active_true_returns_difficult_a3_row5():
    inp = TerrainConditionInput(
        soil_group=SoilGroup.COHESIVE_FINE,
        plasticity_class=PlasticityClass.HIGH,
        void_ratio=1.0,
        consistency_index=0.80,
        active=True,
    )
    r = classify_terrain_condition(inp)
    assert r.valid is True
    assert r.condition == TerrainCondition.DIFFICULT
    assert r.matched_table == "A.3"
    assert r.matched_row == 5


def test_liquefiable_true_returns_difficult_a3_row2():
    inp = TerrainConditionInput(
        soil_group=SoilGroup.NON_COHESIVE,
        relative_density=RelativeDensity.DENSE,
        liquefiable=True,
    )
    r = classify_terrain_condition(inp)
    assert r.valid is True
    assert r.condition == TerrainCondition.DIFFICULT
    assert r.matched_table == "A.3"
    assert r.matched_row == 2


def test_sliding_potential_true_returns_difficult_a3_row7():
    inp = TerrainConditionInput(
        soil_group=SoilGroup.ROCKY,
        sliding_potential=True,
    )
    r = classify_terrain_condition(inp)
    assert r.valid is True
    assert r.condition == TerrainCondition.DIFFICULT
    assert r.matched_table == "A.3"
    assert r.matched_row == 7


def test_collapsible_false_does_not_override():
    # collapsible=False → does not trigger override, falls through to normal logic
    inp = TerrainConditionInput(
        soil_group=SoilGroup.ROCKY,
        collapsible=False,
    )
    r = classify_terrain_condition(inp)
    assert r.condition == TerrainCondition.GOOD
    assert r.matched_table == "A.1"


# ── ROCKY ─────────────────────────────────────────────────────────────────────

def test_rocky_uniform_horizontal_returns_good_a1_row6():
    r = classify_terrain_condition(
        TerrainConditionInput(soil_group=SoilGroup.ROCKY)
    )
    assert r.valid is True
    assert r.condition == TerrainCondition.GOOD
    assert r.matched_table == "A.1"
    assert r.matched_row == 6
    assert r.errors == []


def test_rocky_non_uniform_returns_error():
    r = classify_terrain_condition(
        TerrainConditionInput(
            soil_group=SoilGroup.ROCKY,
            stratification_uniform_horizontal=False,
        )
    )
    assert r.valid is False
    assert len(r.errors) == 1


def test_rocky_source_metadata():
    r = classify_terrain_condition(
        TerrainConditionInput(soil_group=SoilGroup.ROCKY)
    )
    assert r.source.code == "NP 074:2022"
    assert r.source.table == "Tabelele A.1–A.3"


# ── NON_COHESIVE ──────────────────────────────────────────────────────────────

def test_non_cohesive_dense_uniform_returns_good_a1_row2():
    r = classify_terrain_condition(
        TerrainConditionInput(
            soil_group=SoilGroup.NON_COHESIVE,
            relative_density=RelativeDensity.DENSE,
        )
    )
    assert r.valid is True
    assert r.condition == TerrainCondition.GOOD
    assert r.matched_table == "A.1"
    assert r.matched_row == 2


def test_non_cohesive_medium_uniform_returns_medium_a2_row1():
    r = classify_terrain_condition(
        TerrainConditionInput(
            soil_group=SoilGroup.NON_COHESIVE,
            relative_density=RelativeDensity.MEDIUM,
        )
    )
    assert r.valid is True
    assert r.condition == TerrainCondition.MEDIUM
    assert r.matched_table == "A.2"
    assert r.matched_row == 1


def test_non_cohesive_loose_returns_difficult_a3_row1():
    r = classify_terrain_condition(
        TerrainConditionInput(
            soil_group=SoilGroup.NON_COHESIVE,
            relative_density=RelativeDensity.LOOSE,
        )
    )
    assert r.valid is True
    assert r.condition == TerrainCondition.DIFFICULT
    assert r.matched_table == "A.3"
    assert r.matched_row == 1


def test_non_cohesive_dense_non_uniform_returns_error():
    r = classify_terrain_condition(
        TerrainConditionInput(
            soil_group=SoilGroup.NON_COHESIVE,
            relative_density=RelativeDensity.DENSE,
            stratification_uniform_horizontal=False,
        )
    )
    assert r.valid is False
    assert len(r.errors) == 1


def test_non_cohesive_missing_density_returns_error():
    r = classify_terrain_condition(
        TerrainConditionInput(soil_group=SoilGroup.NON_COHESIVE)
    )
    assert r.valid is False
    assert len(r.errors) == 1


def test_non_cohesive_loose_ignores_stratification():
    # LOOSE → DIFFICULT regardless of stratification flag
    r = classify_terrain_condition(
        TerrainConditionInput(
            soil_group=SoilGroup.NON_COHESIVE,
            relative_density=RelativeDensity.LOOSE,
            stratification_uniform_horizontal=False,
        )
    )
    assert r.valid is True
    assert r.condition == TerrainCondition.DIFFICULT


# ── COHESIVE_FINE ─────────────────────────────────────────────────────────────

# IC < 0.5 → DIFFICULT A.3 row 3

def test_cohesive_fine_ic_below_0_5_returns_difficult_a3_row3():
    r = classify_terrain_condition(
        TerrainConditionInput(
            soil_group=SoilGroup.COHESIVE_FINE,
            plasticity_class=PlasticityClass.MEDIUM,
            void_ratio=0.8,
            consistency_index=0.4,
        )
    )
    assert r.valid is True
    assert r.condition == TerrainCondition.DIFFICULT
    assert r.matched_table == "A.3"
    assert r.matched_row == 3


def test_cohesive_fine_ic_exactly_0_5_is_medium():
    # IC=0.5 is the boundary — belongs to [0.5, 0.75) band → MEDIUM
    r = classify_terrain_condition(
        TerrainConditionInput(
            soil_group=SoilGroup.COHESIVE_FINE,
            plasticity_class=PlasticityClass.LOW,
            void_ratio=0.6,
            consistency_index=0.5,
        )
    )
    assert r.valid is True
    assert r.condition == TerrainCondition.MEDIUM


# IC ∈ [0.5, 0.75) → MEDIUM A.2 rows 2/3/4

def test_cohesive_fine_low_medium_band_a2_row2():
    r = classify_terrain_condition(
        TerrainConditionInput(
            soil_group=SoilGroup.COHESIVE_FINE,
            plasticity_class=PlasticityClass.LOW,
            void_ratio=0.6,
            consistency_index=0.60,
        )
    )
    assert r.valid is True
    assert r.condition == TerrainCondition.MEDIUM
    assert r.matched_table == "A.2"
    assert r.matched_row == 2


def test_cohesive_fine_medium_medium_band_a2_row3():
    r = classify_terrain_condition(
        TerrainConditionInput(
            soil_group=SoilGroup.COHESIVE_FINE,
            plasticity_class=PlasticityClass.MEDIUM,
            void_ratio=0.8,
            consistency_index=0.60,
        )
    )
    assert r.valid is True
    assert r.condition == TerrainCondition.MEDIUM
    assert r.matched_table == "A.2"
    assert r.matched_row == 3


def test_cohesive_fine_high_medium_band_a2_row4():
    r = classify_terrain_condition(
        TerrainConditionInput(
            soil_group=SoilGroup.COHESIVE_FINE,
            plasticity_class=PlasticityClass.HIGH,
            void_ratio=1.0,
            consistency_index=0.60,
        )
    )
    assert r.valid is True
    assert r.condition == TerrainCondition.MEDIUM
    assert r.matched_table == "A.2"
    assert r.matched_row == 4


# IC ≥ 0.75 → GOOD A.1 rows 3/4/5

def test_cohesive_fine_low_good_band_a1_row3():
    r = classify_terrain_condition(
        TerrainConditionInput(
            soil_group=SoilGroup.COHESIVE_FINE,
            plasticity_class=PlasticityClass.LOW,
            void_ratio=0.6,
            consistency_index=0.80,
            collapsible=False,
        )
    )
    assert r.valid is True
    assert r.condition == TerrainCondition.GOOD
    assert r.matched_table == "A.1"
    assert r.matched_row == 3
    assert r.errors == []


def test_cohesive_fine_medium_good_band_a1_row4():
    r = classify_terrain_condition(
        TerrainConditionInput(
            soil_group=SoilGroup.COHESIVE_FINE,
            plasticity_class=PlasticityClass.MEDIUM,
            void_ratio=0.8,
            consistency_index=0.80,
            collapsible=False,
            active=False,
        )
    )
    assert r.valid is True
    assert r.condition == TerrainCondition.GOOD
    assert r.matched_table == "A.1"
    assert r.matched_row == 4
    assert r.warnings == []


def test_cohesive_fine_high_good_band_a1_row5():
    r = classify_terrain_condition(
        TerrainConditionInput(
            soil_group=SoilGroup.COHESIVE_FINE,
            plasticity_class=PlasticityClass.HIGH,
            void_ratio=1.0,
            consistency_index=0.80,
            collapsible=False,
            active=False,
        )
    )
    assert r.valid is True
    assert r.condition == TerrainCondition.GOOD
    assert r.matched_table == "A.1"
    assert r.matched_row == 5
    assert r.warnings == []


# Warnings for NP 125 / NP 126

def test_cohesive_fine_good_band_collapsible_none_emits_np125_warning():
    r = classify_terrain_condition(
        TerrainConditionInput(
            soil_group=SoilGroup.COHESIVE_FINE,
            plasticity_class=PlasticityClass.LOW,
            void_ratio=0.6,
            consistency_index=0.80,
            collapsible=None,
        )
    )
    assert r.valid is True
    assert r.condition == TerrainCondition.GOOD
    assert any("NP 125" in w for w in r.warnings)


def test_cohesive_fine_medium_good_band_active_none_emits_np126_warning():
    r = classify_terrain_condition(
        TerrainConditionInput(
            soil_group=SoilGroup.COHESIVE_FINE,
            plasticity_class=PlasticityClass.MEDIUM,
            void_ratio=0.8,
            consistency_index=0.80,
            collapsible=False,
            active=None,
        )
    )
    assert r.valid is True
    assert any("NP 126" in w for w in r.warnings)


def test_cohesive_fine_low_good_band_active_none_no_np126_warning():
    # LOW plasticity — NP 126 warning does NOT apply
    r = classify_terrain_condition(
        TerrainConditionInput(
            soil_group=SoilGroup.COHESIVE_FINE,
            plasticity_class=PlasticityClass.LOW,
            void_ratio=0.6,
            consistency_index=0.80,
            collapsible=False,
            active=None,
        )
    )
    assert r.valid is True
    assert not any("NP 126" in w for w in r.warnings)


def test_cohesive_fine_active_false_no_np126_warning():
    # active=False → not active, no warning
    r = classify_terrain_condition(
        TerrainConditionInput(
            soil_group=SoilGroup.COHESIVE_FINE,
            plasticity_class=PlasticityClass.HIGH,
            void_ratio=1.0,
            consistency_index=0.60,
            active=False,
        )
    )
    assert r.valid is True
    assert r.condition == TerrainCondition.MEDIUM
    assert not any("NP 126" in w for w in r.warnings)


def test_cohesive_fine_medium_band_medium_plasticity_active_none_emits_np126_warning():
    r = classify_terrain_condition(
        TerrainConditionInput(
            soil_group=SoilGroup.COHESIVE_FINE,
            plasticity_class=PlasticityClass.MEDIUM,
            void_ratio=0.8,
            consistency_index=0.60,
            active=None,
        )
    )
    assert r.valid is True
    assert r.condition == TerrainCondition.MEDIUM
    assert any("NP 126" in w for w in r.warnings)


def test_cohesive_fine_medium_band_low_plasticity_active_none_no_np126_warning():
    r = classify_terrain_condition(
        TerrainConditionInput(
            soil_group=SoilGroup.COHESIVE_FINE,
            plasticity_class=PlasticityClass.LOW,
            void_ratio=0.6,
            consistency_index=0.60,
            active=None,
        )
    )
    assert r.valid is True
    assert not any("NP 126" in w for w in r.warnings)


# Out-of-range e

def test_cohesive_fine_e_exceeds_max_for_low_plasticity_returns_error():
    # LOW: e_max = 0.7
    r = classify_terrain_condition(
        TerrainConditionInput(
            soil_group=SoilGroup.COHESIVE_FINE,
            plasticity_class=PlasticityClass.LOW,
            void_ratio=1.5,
            consistency_index=0.80,
        )
    )
    assert r.valid is False
    assert len(r.errors) == 1


def test_cohesive_fine_e_at_max_is_valid():
    # HIGH: e_max=1.1, e=1.1 → valid
    r = classify_terrain_condition(
        TerrainConditionInput(
            soil_group=SoilGroup.COHESIVE_FINE,
            plasticity_class=PlasticityClass.HIGH,
            void_ratio=1.1,
            consistency_index=0.80,
            collapsible=False,
            active=False,
        )
    )
    assert r.valid is True
    assert r.condition == TerrainCondition.GOOD


# Missing required fields

def test_cohesive_fine_missing_plasticity_class_returns_error():
    r = classify_terrain_condition(
        TerrainConditionInput(
            soil_group=SoilGroup.COHESIVE_FINE,
            void_ratio=0.6,
            consistency_index=0.80,
        )
    )
    assert r.valid is False
    assert len(r.errors) == 1


def test_cohesive_fine_missing_consistency_index_returns_error():
    r = classify_terrain_condition(
        TerrainConditionInput(
            soil_group=SoilGroup.COHESIVE_FINE,
            plasticity_class=PlasticityClass.LOW,
            void_ratio=0.6,
        )
    )
    assert r.valid is False
    assert len(r.errors) == 1


def test_cohesive_fine_missing_void_ratio_returns_error():
    r = classify_terrain_condition(
        TerrainConditionInput(
            soil_group=SoilGroup.COHESIVE_FINE,
            plasticity_class=PlasticityClass.LOW,
            consistency_index=0.80,
        )
    )
    assert r.valid is False
    assert len(r.errors) == 1


# ── FILL ──────────────────────────────────────────────────────────────────────


def test_fill_controlled_compacted_returns_good_a1_row7():
    r = classify_terrain_condition(
        TerrainConditionInput(
            soil_group=SoilGroup.FILL,
            fill_category=FillCategory.CONTROLLED_COMPACTED,
        )
    )
    assert r.valid is True
    assert r.condition == TerrainCondition.GOOD
    assert r.matched_table == "A.1"
    assert r.matched_row == 7


def test_fill_household_returns_difficult_a3_row9():
    r = classify_terrain_condition(
        TerrainConditionInput(
            soil_group=SoilGroup.FILL,
            fill_category=FillCategory.HOUSEHOLD,
        )
    )
    assert r.valid is True
    assert r.condition == TerrainCondition.DIFFICULT
    assert r.matched_table == "A.3"
    assert r.matched_row == 9


def test_fill_known_origin_low_organic_returns_medium_a2_row6():
    r = classify_terrain_condition(
        TerrainConditionInput(
            soil_group=SoilGroup.FILL,
            fill_category=FillCategory.KNOWN_ORIGIN_ORGANIZED,
            organic_content_pct=3.0,
        )
    )
    assert r.valid is True
    assert r.condition == TerrainCondition.MEDIUM
    assert r.matched_table == "A.2"
    assert r.matched_row == 6


def test_fill_known_origin_high_organic_returns_difficult_a3_row6():
    r = classify_terrain_condition(
        TerrainConditionInput(
            soil_group=SoilGroup.FILL,
            fill_category=FillCategory.KNOWN_ORIGIN_ORGANIZED,
            organic_content_pct=6.0,
        )
    )
    assert r.valid is True
    assert r.condition == TerrainCondition.DIFFICULT
    assert r.matched_table == "A.3"
    assert r.matched_row == 6


def test_fill_known_origin_exactly_5_pct_organic_returns_difficult():
    # boundary: >= 5% → DIFFICULT
    r = classify_terrain_condition(
        TerrainConditionInput(
            soil_group=SoilGroup.FILL,
            fill_category=FillCategory.KNOWN_ORIGIN_ORGANIZED,
            organic_content_pct=5.0,
        )
    )
    assert r.valid is True
    assert r.condition == TerrainCondition.DIFFICULT


def test_fill_uncontrolled_old_returns_medium_a2_row6():
    r = classify_terrain_condition(
        TerrainConditionInput(
            soil_group=SoilGroup.FILL,
            fill_category=FillCategory.UNCONTROLLED,
            fill_age_years=15.0,
        )
    )
    assert r.valid is True
    assert r.condition == TerrainCondition.MEDIUM
    assert r.matched_table == "A.2"
    assert r.matched_row == 6
    assert r.warnings == []


def test_fill_uncontrolled_young_returns_difficult_a3_row8():
    r = classify_terrain_condition(
        TerrainConditionInput(
            soil_group=SoilGroup.FILL,
            fill_category=FillCategory.UNCONTROLLED,
            fill_age_years=5.0,
        )
    )
    assert r.valid is True
    assert r.condition == TerrainCondition.DIFFICULT
    assert r.matched_table == "A.3"
    assert r.matched_row == 8


def test_fill_uncontrolled_exactly_10_years_returns_medium():
    # boundary: < 10 → DIFFICULT, so 10 → MEDIUM (in grey zone [10,12])
    r = classify_terrain_condition(
        TerrainConditionInput(
            soil_group=SoilGroup.FILL,
            fill_category=FillCategory.UNCONTROLLED,
            fill_age_years=10.0,
        )
    )
    assert r.valid is True
    assert r.condition == TerrainCondition.MEDIUM
    assert len(r.warnings) == 1


def test_fill_uncontrolled_grey_zone_emits_warning():
    r = classify_terrain_condition(
        TerrainConditionInput(
            soil_group=SoilGroup.FILL,
            fill_category=FillCategory.UNCONTROLLED,
            fill_age_years=11.0,
        )
    )
    assert r.valid is True
    assert r.condition == TerrainCondition.MEDIUM
    assert len(r.warnings) == 1
    assert "10" in r.warnings[0] and "12" in r.warnings[0]


def test_fill_uncontrolled_missing_age_returns_error():
    r = classify_terrain_condition(
        TerrainConditionInput(
            soil_group=SoilGroup.FILL,
            fill_category=FillCategory.UNCONTROLLED,
        )
    )
    assert r.valid is False
    assert len(r.errors) == 1


def test_fill_missing_category_returns_error():
    r = classify_terrain_condition(
        TerrainConditionInput(soil_group=SoilGroup.FILL)
    )
    assert r.valid is False
    assert len(r.errors) == 1


# ── Registry ──────────────────────────────────────────────────────────────────

def test_registered_in_global_registry():
    from tabularium.registry import registry
    entry = registry.get("np_074_2022.terrain_condition")
    assert entry is not None
    assert callable(entry.func)
    assert entry.normative == "NP 074:2022"
