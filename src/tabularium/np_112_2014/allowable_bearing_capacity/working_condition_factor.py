from __future__ import annotations

from ...enums import Soil, SoilCategory
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

# Categorii condiționate de Iᶜ prin Soil specific
_CONSISTENCY: dict[Soil, tuple[float, float]] = {
    Soil.BOULDER_COHESIVE_FILL: (1.3, 1.1),
    Soil.GRAVEL_COHESIVE_FILL:  (1.3, 1.1),
}

# m₁ pentru SoilCategory.COHESIVE (pământuri coezive generice): (m1_consistent, m1_moale)
_COHESIVE_CATEGORY_M1: tuple[float, float] = (1.4, 1.1)


def get_working_condition_factor(
    soil: Soil | None = None,
    soil_category: SoilCategory | None = None,
    saturation_ratio: float | None = None,
    consistency_index: float | None = None,
) -> WorkingConditionFactorResult:
    """
    Returnează coeficientul condițiilor de lucru m₁
    conform NP 112:2014, Tabelul H.7.

    Furnizați fie `soil` (denumire specifică), fie `soil_category=SoilCategory.COHESIVE`
    pentru pământuri coezive generice (rândurile 5/7 din tabel).
    """
    result = WorkingConditionFactorResult(source=_SOURCE)

    if soil is None and soil_category is None:
        result.errors.append("Furnizați fie `soil`, fie `soil_category`.")
        return result

    if soil is not None and soil_category is not None:
        result.errors.append("Furnizați doar unul din `soil` sau `soil_category`, nu ambele.")
        return result

    # --- Lookup via SoilCategory ---
    if soil_category is not None:
        try:
            soil_category = SoilCategory(soil_category)
        except ValueError:
            result.errors.append(f"SoilCategory necunoscută: {soil_category!r}.")
            return result

        if soil_category != SoilCategory.COHESIVE:
            result.errors.append(
                f"SoilCategory {soil_category!r} nu este acoperită de Tabelul H.7. "
                "Folosiți SoilCategory.COHESIVE pentru pământuri coezive generice."
            )
            return result

        if consistency_index is None:
            result.errors.append(
                "consistency_index (Iᶜ) este necesar pentru SoilCategory.COHESIVE."
            )
            return result

        m1_stiff, m1_soft = _COHESIVE_CATEGORY_M1
        result.m1 = m1_stiff if consistency_index >= _IC_THRESHOLD else m1_soft
        result.valid = True
        return result

    # --- Lookup via Soil ---
    try:
        soil = Soil(soil)
    except ValueError:
        result.errors.append(f"Categorie de sol necunoscută: {soil!r}.")
        return result

    if soil in _NO_CONDITION:
        result.m1 = _NO_CONDITION[soil]
        result.valid = True
        return result

    if soil in _SATURATION:
        if saturation_ratio is None:
            result.errors.append(
                f"saturation_ratio (Sᵣ) este necesar pentru {soil!r}."
            )
            return result
        m1_dry, m1_wet = _SATURATION[soil]
        result.m1 = m1_dry if saturation_ratio <= _SR_THRESHOLD else m1_wet
        result.valid = True
        return result

    if soil in _CONSISTENCY:
        if consistency_index is None:
            result.errors.append(
                f"consistency_index (Iᶜ) este necesar pentru {soil!r}."
            )
            return result
        m1_stiff, m1_soft = _CONSISTENCY[soil]
        result.m1 = m1_stiff if consistency_index >= _IC_THRESHOLD else m1_soft
        result.valid = True
        return result

    result.errors.append(
        f"Categoria {soil!r} nu este acoperită de Tabelul H.7. "
        "Verificați că folosiți categoria corectă pentru acest tabel."
    )
    return result
