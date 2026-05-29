from __future__ import annotations

from dataclasses import dataclass

from ...enums import RelativeDensity, Soil
from ...models import CodeSource, LookupResult

_SOURCE = CodeSource(code="NP 122:2010", table="Tabelul A.6.1")


@dataclass
class ShearStrengthNonCohesiveResult(LookupResult):
    phi: float | None = None  # unghi de frecare internă φ' [grade]


# _TABLE[Soil][RelativeDensity] = φ' (grade)
_TABLE: dict[Soil, dict[RelativeDensity, float]] = {
    Soil.GRAVEL_COARSE_SAND: {
        RelativeDensity.MEDIUM: 33.0,
        RelativeDensity.DENSE:  36.0,
    },
    Soil.MEDIUM_SAND: {
        RelativeDensity.MEDIUM: 31.0,
        RelativeDensity.DENSE:  33.0,
    },
    Soil.FINE_SAND: {
        RelativeDensity.MEDIUM: 27.0,
        RelativeDensity.DENSE:  30.0,
    },
    Soil.SILTY_SAND: {
        RelativeDensity.MEDIUM: 24.0,
        RelativeDensity.DENSE:  28.0,
    },
}


def get_phi(
    soil_category: Soil,
    relative_density: RelativeDensity,
) -> ShearStrengthNonCohesiveResult:
    """
    Returnează valoarea caracteristică a unghiului de frecare internă φ' (grade)
    pentru pământuri necoezive conform NP 122:2010, Tabelul A.6.1.

    Valabil pentru pământuri necoezive cu particule relativ rotunjite.
    Pentru particule colțuroase se pot accepta valori mai ridicate.
    """
    result = ShearStrengthNonCohesiveResult(source=_SOURCE)

    try:
        soil_category    = Soil(soil_category)
        relative_density = RelativeDensity(relative_density)
    except ValueError:
        result.errors.append(
            f"Valori necunoscute: soil_category={soil_category!r}, "
            f"relative_density={relative_density!r}."
        )
        return result

    result.phi   = _TABLE[soil_category][relative_density]
    result.valid = True
    return result
