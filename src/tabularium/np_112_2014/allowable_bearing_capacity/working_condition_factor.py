from __future__ import annotations

from ...enums import Soil, SoilCategory
from ...models import CodeSource
from . import WorkingConditionFactorResult, WorkingConditionTableEntry, WorkingConditionTableResult

_SOURCE = CodeSource(code="NP 112:2014", table="Tabelul H.7")

_SR_THRESHOLD = 0.8   # Sᵣ ≤ 0.8 → uscat/umed; Sᵣ > 0.8 → foarte umed/saturat
_IC_THRESHOLD = 0.5   # Iᶜ ≥ 0.5 → consistent; Iᶜ < 0.5 → moale

# Categorii fără condiție secundară: ml fix
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

# ml pentru SoilCategory.COHESIVE (pământuri coezive generice): (m1_consistent, m1_moale)
_COHESIVE_CATEGORY_M1: tuple[float, float] = (1.4, 1.1)


def get_working_condition_factor(
    soil: Soil | None = None,
    soil_category: SoilCategory | None = None,
    saturation_ratio: float | None = None,
    consistency_index: float | None = None,
) -> WorkingConditionFactorResult:
    """
    Returnează coeficientul condițiilor de lucru ml
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
                f"consistency_index (Iᶜ) este necesar pentru '{soil_category.label}'."
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
        result.errors.append(f"Categorie de sol necunoscută: '{soil}'.")
        return result

    if soil in _NO_CONDITION:
        result.m1 = _NO_CONDITION[soil]
        result.valid = True
        return result

    if soil in _SATURATION:
        if saturation_ratio is None:
            result.errors.append(
                f"saturation_ratio (Sᵣ) este necesar pentru '{soil.label}'."
            )
            return result
        m1_dry, m1_wet = _SATURATION[soil]
        result.m1 = m1_dry if saturation_ratio <= _SR_THRESHOLD else m1_wet
        result.valid = True
        return result

    if soil in _CONSISTENCY:
        if consistency_index is None:
            result.errors.append(
                f"consistency_index (Iᶜ) este necesar pentru '{soil.label}'."
            )
            return result
        m1_stiff, m1_soft = _CONSISTENCY[soil]
        result.m1 = m1_stiff if consistency_index >= _IC_THRESHOLD else m1_soft
        result.valid = True
        return result

    result.errors.append(
        f"Categoria '{soil.label}' nu este acoperită de Tabelul H.7. "
        "Verificați că folosiți categoria corectă pentru acest tabel."
    )
    return result


def get_ml_table() -> WorkingConditionTableResult:
    """Returnează Tabelul H.7 complet din NP 112:2014."""
    entries = [
        WorkingConditionTableEntry(soil_label=Soil.BOULDER_SAND_FILL.label,    m1=2.0),
        WorkingConditionTableEntry(soil_label=Soil.GRAVEL.label,               m1=2.0),
        WorkingConditionTableEntry(soil_label=Soil.COARSE_SAND.label,          m1=2.0),
        WorkingConditionTableEntry(soil_label=Soil.MEDIUM_SAND.label,          m1=2.0),
        WorkingConditionTableEntry(
            soil_label=Soil.FINE_SAND.label,
            m1_uscat_umed=1.7, m1_saturat=1.6, conditie="Sr",
        ),
        WorkingConditionTableEntry(
            soil_label=Soil.SILTY_SAND.label,
            m1_uscat_umed=1.5, m1_saturat=1.3, conditie="Sr",
        ),
        WorkingConditionTableEntry(
            soil_label=Soil.BOULDER_COHESIVE_FILL.label,
            m1_consistent=1.3, m1_moale=1.1, conditie="Ic",
        ),
        WorkingConditionTableEntry(
            soil_label=Soil.GRAVEL_COHESIVE_FILL.label,
            m1_consistent=1.3, m1_moale=1.1, conditie="Ic",
        ),
        WorkingConditionTableEntry(
            soil_label=SoilCategory.COHESIVE.label,
            m1_consistent=1.4, m1_moale=1.1, conditie="Ic",
        ),
    ]
    return WorkingConditionTableResult(entries=entries, source=_SOURCE)
