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
