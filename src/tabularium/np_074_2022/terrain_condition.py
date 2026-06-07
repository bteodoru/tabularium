from __future__ import annotations

from dataclasses import dataclass

from ..enums import (
    FillCategory,
    PlasticityClass,
    RelativeDensity,
    SoilGroup,
    TerrainCondition,
)
from ..models import CodeSource, LookupResult

_SOURCE = CodeSource(code="NP 074:2022", table="Tabelele A.1–A.3", section="Anexa A")

_E_MAX: dict[PlasticityClass, float] = {
    PlasticityClass.LOW:    0.7,
    PlasticityClass.MEDIUM: 1.0,
    PlasticityClass.HIGH:   1.1,
}


@dataclass
class TerrainConditionInput:
    soil_group: SoilGroup

    # NON_COHESIVE
    relative_density: RelativeDensity | None = None

    # COHESIVE_FINE
    plasticity_class: PlasticityClass | None = None
    void_ratio: float | None = None
    consistency_index: float | None = None

    # FILL
    fill_category: FillCategory | None = None
    organic_content_pct: float = 0.0
    fill_age_years: float | None = None

    # General
    stratification_uniform_horizontal: bool = True

    # Optional override flags
    collapsible: bool | None = None
    active: bool | None = None
    liquefiable: bool | None = None
    sliding_potential: bool | None = None


@dataclass
class TerrainConditionResult(LookupResult):
    condition: TerrainCondition | None = None
    matched_table: str | None = None
    matched_row: int | None = None


def _make_result(
    condition: TerrainCondition,
    table: str,
    row: int,
    warnings: list[str] | None = None,
) -> TerrainConditionResult:
    r = TerrainConditionResult(source=_SOURCE)
    r.condition = condition
    r.matched_table = table
    r.matched_row = row
    r.valid = True
    if warnings:
        r.warnings.extend(warnings)
    return r


def _error(msg: str) -> TerrainConditionResult:
    r = TerrainConditionResult(source=_SOURCE)
    r.errors.append(msg)
    return r


def classify_terrain_condition(inp: TerrainConditionInput) -> TerrainConditionResult:
    if inp.collapsible is True:
        return _make_result(TerrainCondition.DIFFICULT, "A.3", 4)
    if inp.active is True:
        return _make_result(TerrainCondition.DIFFICULT, "A.3", 5)
    if inp.liquefiable is True:
        return _make_result(TerrainCondition.DIFFICULT, "A.3", 2)
    if inp.sliding_potential is True:
        return _make_result(TerrainCondition.DIFFICULT, "A.3", 7)

    try:
        soil_group = SoilGroup(inp.soil_group)
    except ValueError:
        return _error(f"Grup de sol necunoscut: {inp.soil_group!r}.")

    if soil_group == SoilGroup.ROCKY:
        return _classify_rocky(inp)
    if soil_group == SoilGroup.NON_COHESIVE:
        return _classify_non_cohesive(inp)
    if soil_group == SoilGroup.COHESIVE_FINE:
        return _classify_cohesive_fine(inp)
    return _classify_fill(inp)


def _classify_rocky(inp: TerrainConditionInput) -> TerrainConditionResult:
    raise NotImplementedError


def _classify_non_cohesive(inp: TerrainConditionInput) -> TerrainConditionResult:
    raise NotImplementedError


def _classify_cohesive_fine(inp: TerrainConditionInput) -> TerrainConditionResult:
    raise NotImplementedError


def _classify_fill(inp: TerrainConditionInput) -> TerrainConditionResult:
    raise NotImplementedError
