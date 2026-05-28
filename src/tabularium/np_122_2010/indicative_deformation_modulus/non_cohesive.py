from __future__ import annotations

from dataclasses import dataclass

from ...enums import RelativeDensity, SoilCategory
from ...models import CodeSource, LookupResult

_SOURCE = CodeSource(code="NP 122:2010", table="Tabelul A.6.3")


@dataclass
class DeformationModulusNonCohesiveResult(LookupResult):
    e_modulus: float | None = None


# _TABLE[SoilCategory][RelativeDensity] = E (kPa)
_TABLE: dict[SoilCategory, dict[RelativeDensity, float]] = {
    SoilCategory.GRAVEL_COARSE_MEDIUM_SAND: {
        RelativeDensity.MEDIUM: 30_000.0,
        RelativeDensity.DENSE:  40_000.0,
    },
    SoilCategory.FINE_SAND: {
        RelativeDensity.MEDIUM: 25_000.0,
        RelativeDensity.DENSE:  35_000.0,
    },
    SoilCategory.SILTY_SAND: {
        RelativeDensity.MEDIUM: 18_000.0,
        RelativeDensity.DENSE:  30_000.0,
    },
}


def get_deformation_modulus(
    soil_category: SoilCategory,
    relative_density: RelativeDensity,
) -> DeformationModulusNonCohesiveResult:
    """
    Returnează modulul de deformație lineară E (kPa) pentru pământuri nisipoase
    conform NP 122:2010, Tabelul A.6.3.
    """
    result = DeformationModulusNonCohesiveResult(source=_SOURCE)

    try:
        soil_category = SoilCategory(soil_category)
        relative_density = RelativeDensity(relative_density)
    except ValueError:
        result.errors.append(
            f"Valori necunoscute: soil_category={soil_category!r}, "
            f"relative_density={relative_density!r}."
        )
        return result

    result.e_modulus = _TABLE[soil_category][relative_density]
    result.valid = True
    return result
