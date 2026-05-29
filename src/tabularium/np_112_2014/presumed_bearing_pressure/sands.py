from __future__ import annotations

from ...enums import MoistureCondition, RelativeDensity, Soil, SoilCategory
from ...models import CodeSource
from . import PresumedBearingPressureResult

_SOURCE = CodeSource(code="NP 112:2014", table="Tabelul D.3")

_SAND_CATEGORIES = {
    Soil.COARSE_SAND,
    Soil.MEDIUM_SAND,
    Soil.FINE_SAND,
    Soil.SILTY_SAND,
}

_SOIL_TYPES: dict[Soil, SoilCategory] = {
    Soil.COARSE_SAND: SoilCategory.NON_COHESIVE,
    Soil.MEDIUM_SAND: SoilCategory.NON_COHESIVE,
    Soil.FINE_SAND:   SoilCategory.NON_COHESIVE,
    Soil.SILTY_SAND:  SoilCategory.COHESIVE,
}

# Categorii fără diferențiere pe umiditate: orice MoistureCondition e acceptat
_MOISTURE_INDEPENDENT = {Soil.COARSE_SAND, Soil.MEDIUM_SAND}

# _TABLE[(Soil, MoistureCondition | None)][RelativeDensity] = p_conv
# None ca cheie de umiditate = indiferent de umiditate
_TABLE: dict[tuple[Soil, MoistureCondition | None], dict[RelativeDensity, float]] = {
    (Soil.COARSE_SAND, None): {
        RelativeDensity.DENSE:  700.0,
        RelativeDensity.MEDIUM: 600.0,
    },
    (Soil.MEDIUM_SAND, None): {
        RelativeDensity.DENSE:  600.0,
        RelativeDensity.MEDIUM: 500.0,
    },
    (Soil.FINE_SAND, MoistureCondition.DRY): {
        RelativeDensity.DENSE:  500.0,
        RelativeDensity.MEDIUM: 350.0,
    },
    (Soil.FINE_SAND, MoistureCondition.MOIST): {
        RelativeDensity.DENSE:  500.0,
        RelativeDensity.MEDIUM: 350.0,
    },
    (Soil.FINE_SAND, MoistureCondition.VERY_MOIST): {
        RelativeDensity.DENSE:  350.0,
        RelativeDensity.MEDIUM: 250.0,
    },
    (Soil.FINE_SAND, MoistureCondition.SATURATED): {
        RelativeDensity.DENSE:  350.0,
        RelativeDensity.MEDIUM: 250.0,
    },
    (Soil.SILTY_SAND, MoistureCondition.DRY): {
        RelativeDensity.DENSE:  350.0,
        RelativeDensity.MEDIUM: 300.0,
    },
    (Soil.SILTY_SAND, MoistureCondition.MOIST): {
        RelativeDensity.DENSE:  250.0,
        RelativeDensity.MEDIUM: 200.0,
    },
    (Soil.SILTY_SAND, MoistureCondition.VERY_MOIST): {
        RelativeDensity.DENSE:  200.0,
        RelativeDensity.MEDIUM: 150.0,
    },
    (Soil.SILTY_SAND, MoistureCondition.SATURATED): {
        RelativeDensity.DENSE:  200.0,
        RelativeDensity.MEDIUM: 150.0,
    },
}


def get_presumed_bearing_pressure(
    soil_category: Soil,
    relative_density: RelativeDensity,
    moisture_condition: MoistureCondition,
) -> PresumedBearingPressureResult:
    """
    Returnează p̄_conv [kPa] pentru nisipuri conform NP 112:2014, Tabelul D.3.

    Pentru COARSE_SAND și MEDIUM_SAND, moisture_condition este acceptat
    dar nu influențează valoarea (tabelul are un singur rând per categorie).
    """
    result = PresumedBearingPressureResult(source=_SOURCE)

    try:
        soil_category     = Soil(soil_category)
        relative_density  = RelativeDensity(relative_density)
        moisture_condition = MoistureCondition(moisture_condition)
    except ValueError as exc:
        result.errors.append(f"Valoare necunoscută: {exc}.")
        return result

    if soil_category not in _SAND_CATEGORIES:
        result.errors.append(
            f"Categoria {soil_category!r} nu aparține Tabelului D.3 (nisipuri). "
            "Folosiți modulul corespunzător categoriei de sol."
        )
        return result

    result.soil_type = _SOIL_TYPES[soil_category]

    key_moisture = None if soil_category in _MOISTURE_INDEPENDENT else moisture_condition
    row = _TABLE.get((soil_category, key_moisture))

    if row is None:
        result.errors.append(
            f"Combinație inexistentă în tabel: {soil_category!r} + {moisture_condition!r}."
        )
        return result

    result.p_conv = row[relative_density]
    result.valid = True
    return result
