from __future__ import annotations

from ..enums import FillSoilType, FillType, SoilType
from ..interpolation import interpolate_linear
from ..models import CodeSource
from . import PresumedBearingPressureResult

_SOURCE = CodeSource(code="NP 112:2014", table="Tabelul D.5")

# _TABLE[FillType][FillSoilType][S_r] = p_conv
# Noduri tabelate: S_r = 0.5 și S_r = 0.8
_TABLE: dict[FillType, dict[FillSoilType, dict[float, float]]] = {
    FillType.CONTROLLED_COMPACTED: {
        FillSoilType.SANDY_SLAG: {0.5: 250.0, 0.8: 200.0},
        FillSoilType.SILTY_FINE: {0.5: 180.0, 0.8: 150.0},
    },
    FillType.KNOWN_ORIGIN: {
        FillSoilType.SANDY_SLAG: {0.5: 180.0, 0.8: 150.0},
        FillSoilType.SILTY_FINE: {0.5: 120.0, 0.8: 100.0},
    },
}

_FILL_SOIL_TYPE: dict[FillSoilType, SoilType] = {
    FillSoilType.SANDY_SLAG: SoilType.NON_COHESIVE,
    FillSoilType.SILTY_FINE: SoilType.COHESIVE,
}

_SR_MIN = 0.0
_SR_MAX = 1.0
_SR_NODE_LOW = 0.5
_SR_NODE_HIGH = 0.8


def get_presumed_bearing_pressure(
    fill_type: FillType,
    fill_soil_type: FillSoilType,
    saturation_degree: float,
) -> PresumedBearingPressureResult:
    """
    Returnează p̄_conv [kPa] pentru umpluturi conform NP 112:2014, Tabelul D.5.

    Interpolare liniară pe S_r ∈ [0.5, 0.8].
    S_r < 0.5 → valoarea nodului 0.5; S_r > 0.8 → valoarea nodului 0.8.
    S_r în afara [0, 1] → eroare.
    """
    result = PresumedBearingPressureResult(source=_SOURCE)

    try:
        fill_type = FillType(fill_type)
        fill_soil_type = FillSoilType(fill_soil_type)
    except ValueError as exc:
        result.errors.append(f"Valoare necunoscută: {exc}.")
        return result

    if saturation_degree < _SR_MIN or saturation_degree > _SR_MAX:
        result.errors.append(
            f"saturation_degree (S_r) = {saturation_degree} este în afara "
            f"domeniului fizic [{_SR_MIN}, {_SR_MAX}]."
        )
        return result

    result.soil_type = _FILL_SOIL_TYPE[fill_soil_type]

    knots = _TABLE[fill_type][fill_soil_type]

    # Clampare la nodurile tabelate pentru S_r în afara intervalului de interpolare
    if saturation_degree <= _SR_NODE_LOW:
        result.p_conv = knots[_SR_NODE_LOW]
        result.valid = True
        return result

    if saturation_degree >= _SR_NODE_HIGH:
        result.p_conv = knots[_SR_NODE_HIGH]
        result.valid = True
        return result

    lr = interpolate_linear(knots, saturation_degree)
    result.p_conv = lr.value
    result.interpolated = lr.interpolated
    result.valid = True
    return result
