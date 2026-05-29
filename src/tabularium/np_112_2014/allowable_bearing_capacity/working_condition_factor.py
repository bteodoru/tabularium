from __future__ import annotations

from ...enums import Soil
from ...models import CodeSource
from . import WorkingConditionFactorResult

_SOURCE = CodeSource(code="NP 112:2014", table="Tabelul H.7")

_SR_THRESHOLD = 0.8   # Sᵣ ≤ 0.8 → uscat/umed; Sᵣ > 0.8 → foarte umed/saturat
_IC_THRESHOLD = 0.5   # Iᶜ ≥ 0.5 → consistent; Iᶜ < 0.5 → moale

# Categorii fără condiție secundară: m₁ fix
_NO_CONDITION: dict[Soil, float] = {
    Soil.BOULDER_SAND_FILL: 2.0,
    Soil.MEDIUM_SAND:       2.0,
    Soil.COARSE_SAND:       2.0,
    Soil.GRAVEL:            2.0,
}

# Categorii condiționate de Sᵣ: (m1_uscat_umed, m1_foarte_umed_saturat)
_SATURATION: dict[Soil, tuple[float, float]] = {
    Soil.FINE_SAND:  (1.7, 1.6),
    Soil.SILTY_SAND: (1.5, 1.3),
}

# Categorii condiționate de Iᶜ: (m1_consistent, m1_moale)
_CONSISTENCY: dict[Soil, tuple[float, float]] = {
    Soil.BOULDER_COHESIVE_FILL: (1.3, 1.1),
    Soil.GRAVEL_COHESIVE_FILL:  (1.3, 1.1),
    Soil.COHESIVE_SOIL:         (1.4, 1.1),
}


def get_working_condition_factor(
    soil_category: Soil,
    saturation_ratio: float | None = None,
    consistency_index: float | None = None,
) -> WorkingConditionFactorResult:
    """
    Returnează coeficientul condițiilor de lucru m₁
    conform NP 112:2014, Tabelul H.7.
    """
    result = WorkingConditionFactorResult(source=_SOURCE)

    try:
        soil_category = Soil(soil_category)
    except ValueError:
        result.errors.append(f"Categorie de sol necunoscută: {soil_category!r}.")
        return result

    if soil_category in _NO_CONDITION:
        result.m1 = _NO_CONDITION[soil_category]
        result.valid = True
        return result

    if soil_category in _SATURATION:
        if saturation_ratio is None:
            result.errors.append(
                f"saturation_ratio (Sᵣ) este necesar pentru {soil_category!r}."
            )
            return result
        m1_dry, m1_wet = _SATURATION[soil_category]
        result.m1 = m1_dry if saturation_ratio <= _SR_THRESHOLD else m1_wet
        result.valid = True
        return result

    if soil_category in _CONSISTENCY:
        if consistency_index is None:
            result.errors.append(
                f"consistency_index (Iᶜ) este necesar pentru {soil_category!r}."
            )
            return result
        m1_stiff, m1_soft = _CONSISTENCY[soil_category]
        result.m1 = m1_stiff if consistency_index >= _IC_THRESHOLD else m1_soft
        result.valid = True
        return result

    result.errors.append(
        f"Categoria {soil_category!r} nu este acoperită de Tabelul H.7. "
        "Verificați că folosiți categoria corectă pentru acest tabel."
    )
    return result
