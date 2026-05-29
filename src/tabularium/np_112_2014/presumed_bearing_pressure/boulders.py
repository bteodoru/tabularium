from __future__ import annotations

from ...enums import Soil, SoilCategory
from ...interpolation import interpolate_linear
from ...models import CodeSource
from . import PresumedBearingPressureResult

_SOURCE = CodeSource(code="NP 112:2014", table="Tabelul D.2")

_BOULDER_CATEGORIES = {Soil.BOULDER_GRAVEL_FILL, Soil.BOULDER_CLAY_FILL}

_FIXED: dict[Soil, float] = {
    Soil.BOULDER_GRAVEL_FILL: 750.0,
}

# Noduri pentru interpolare pe I_C: {I_C: p_conv}
_INTERPOLABLE: dict[Soil, dict[float, float]] = {
    Soil.BOULDER_CLAY_FILL: {0.5: 350.0, 1.0: 600.0},
}

_IC_RANGE_WARNING = "Furnizați consistency_index (I_C) pentru a rezolva valoarea exactă."


def get_presumed_bearing_pressure(
    soil_category: Soil,
    consistency_index: float | None = None,
) -> PresumedBearingPressureResult:
    """
    Returnează p̄_conv [kPa] pentru pământuri foarte grosiere
    conform NP 112:2014, Tabelul D.2.

    consistency_index (I_C) necesar doar pentru BOULDER_CLAY_FILL.
    """
    result = PresumedBearingPressureResult(source=_SOURCE)

    try:
        soil_category = Soil(soil_category)
    except ValueError:
        result.errors.append(f"Categorie de sol necunoscută: {soil_category!r}.")
        return result

    if soil_category not in _BOULDER_CATEGORIES:
        result.errors.append(
            f"Categoria {soil_category!r} nu aparține Tabelului D.2 (boulders). "
            "Folosiți modulul corespunzător categoriei de sol."
        )
        return result

    result.soil_type = SoilCategory.NON_COHESIVE

    if soil_category in _FIXED:
        result.p_conv = _FIXED[soil_category]
        result.valid = True
        return result

    # Range interpolabil
    knots = _INTERPOLABLE[soil_category]
    ic_min, ic_max = min(knots), max(knots)

    if consistency_index is None:
        result.p_conv_range = (knots[ic_min], knots[ic_max])
        result.warnings.append(_IC_RANGE_WARNING)
        result.valid = True
        return result

    if consistency_index < ic_min or consistency_index > ic_max:
        result.errors.append(
            f"consistency_index = {consistency_index} este în afara domeniului "
            f"[{ic_min}, {ic_max}] pentru {soil_category!r}."
        )
        return result

    lr = interpolate_linear(knots, consistency_index)
    result.p_conv = lr.value
    result.interpolated = lr.interpolated
    result.valid = True
    return result
