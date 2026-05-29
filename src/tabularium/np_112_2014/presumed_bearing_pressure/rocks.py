from __future__ import annotations

from ...enums import Soil
from ...models import CodeSource
from . import PresumedBearingPressureResult

_SOURCE = CodeSource(code="NP 112:2014", table="Tabelul D.1")

_ROCKY_CATEGORIES = {Soil.ROCKY, Soil.SEMI_ROCKY_MARL, Soil.SEMI_ROCKY_SHALE}

_TABLE: dict[Soil, tuple[float, float]] = {
    Soil.ROCKY:           (1000.0, 6000.0),
    Soil.SEMI_ROCKY_MARL: (350.0,  1100.0),
    Soil.SEMI_ROCKY_SHALE:(600.0,   850.0),
}

_WARNING = (
    "Valoarea se alege pe baza compactității și stării de degradare a rocii "
    "stâncoase sau semi-stâncoase. Nu variază cu adâncimea de fundare."
)


def get_presumed_bearing_pressure(soil_category: Soil) -> PresumedBearingPressureResult:
    """
    Returnează intervalul presiunii convenționale de bază p̄_conv [kPa]
    pentru roci stâncoase și semi-stâncoase conform NP 112:2014, Tabelul D.1.
    """
    result = PresumedBearingPressureResult(source=_SOURCE)

    try:
        soil_category = Soil(soil_category)
    except ValueError:
        result.errors.append(f"Categorie de sol necunoscută: {soil_category!r}.")
        return result

    if soil_category not in _ROCKY_CATEGORIES:
        result.errors.append(
            f"Categoria {soil_category!r} nu aparține Tabelului D.1 (roci). "
            "Folosiți modulul corespunzător categoriei de sol."
        )
        return result

    result.p_conv_range = _TABLE[soil_category]
    result.soil_type = None
    result.warnings.append(_WARNING)
    result.valid = True
    return result
