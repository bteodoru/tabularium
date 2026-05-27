from __future__ import annotations

from ..enums import SoilCategory
from ..models import CodeSource
from . import PresumedBearingPressureResult

_SOURCE = CodeSource(code="NP 112:2014", table="Tabelul D.1")

_ROCKY_CATEGORIES = {SoilCategory.ROCKY, SoilCategory.SEMI_ROCKY_MARL, SoilCategory.SEMI_ROCKY_SHALE}

_TABLE: dict[SoilCategory, tuple[float, float]] = {
    SoilCategory.ROCKY:           (1000.0, 6000.0),
    SoilCategory.SEMI_ROCKY_MARL: (350.0,  1100.0),
    SoilCategory.SEMI_ROCKY_SHALE:(600.0,   850.0),
}

_WARNING = (
    "Valoarea se alege pe baza compactității și stării de degradare a rocii "
    "stâncoase sau semi-stâncoase. Nu variază cu adâncimea de fundare."
)


def get_presumed_bearing_pressure(soil_category: SoilCategory) -> PresumedBearingPressureResult:
    """
    Returnează intervalul presiunii convenționale de bază p̄_conv [kPa]
    pentru roci stâncoase și semi-stâncoase conform NP 112:2014, Tabelul D.1.
    """
    result = PresumedBearingPressureResult(source=_SOURCE)

    try:
        soil_category = SoilCategory(soil_category)
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
    result.warnings.append(_WARNING)
    result.valid = True
    return result
