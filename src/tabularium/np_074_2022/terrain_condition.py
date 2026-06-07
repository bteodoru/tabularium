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


def classify_terrain_condition(inp: TerrainConditionInput) -> TerrainConditionResult:
    raise NotImplementedError
