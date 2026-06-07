from tabularium.np_074_2022.terrain_condition import (
    TerrainConditionInput,
    TerrainConditionResult,
    classify_terrain_condition,
)
from tabularium.enums import (
    FillCategory,
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
