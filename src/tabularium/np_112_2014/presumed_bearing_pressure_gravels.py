from __future__ import annotations

from ..enums import SoilCategory, get_soil_type
from ..interpolation import interpolate_linear
from ..models import CodeSource
from . import PresumedBearingPressureResult

_SOURCE = CodeSource(code="NP 112:2014", table="Tabelul D.2")

_GRAVEL_CATEGORIES = {
    SoilCategory.GRAVEL_CLEAN_CRYSTAL,
    SoilCategory.GRAVEL_WITH_SAND,
    SoilCategory.GRAVEL_SEDIMENTARY,
    SoilCategory.GRAVEL_SILTY_SAND,
}

_FIXED: dict[SoilCategory, float] = {
    SoilCategory.GRAVEL_CLEAN_CRYSTAL: 600.0,
    SoilCategory.GRAVEL_WITH_SAND:     550.0,
    SoilCategory.GRAVEL_SEDIMENTARY:   350.0,
}

_INTERPOLABLE: dict[SoilCategory, dict[float, float]] = {
    SoilCategory.GRAVEL_SILTY_SAND: {0.5: 350.0, 1.0: 500.0},
}

_IC_RANGE_WARNING = "Furnizați consistency_index (I_C) pentru a rezolva valoarea exactă."


def get_presumed_bearing_pressure(
    soil_category: SoilCategory,
    consistency_index: float | None = None,
) -> PresumedBearingPressureResult:
    """
    Returnează p̄_conv [kPa] pentru pământuri grosiere (pietrișuri)
    conform NP 112:2014, Tabelul D.2.

    consistency_index (I_C) necesar doar pentru GRAVEL_SILTY_SAND.
    """
    result = PresumedBearingPressureResult(source=_SOURCE)

    try:
        soil_category = SoilCategory(soil_category)
    except ValueError:
        result.errors.append(f"Categorie de sol necunoscută: {soil_category!r}.")
        return result

    if soil_category not in _GRAVEL_CATEGORIES:
        result.errors.append(
            f"Categoria {soil_category!r} nu aparține Tabelului D.2 (gravels). "
            "Folosiți modulul corespunzător categoriei de sol."
        )
        return result

    result.soil_type = get_soil_type(soil_category)

    if soil_category in _FIXED:
        result.p_conv = _FIXED[soil_category]
        result.valid = True
        return result

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
