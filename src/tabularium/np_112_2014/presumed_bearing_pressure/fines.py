from __future__ import annotations

import bisect

from ...enums import PlasticityClass, SoilCategory
from ...interpolation import interpolate_linear
from ...models import CodeSource
from . import PresumedBearingPressureResult

_SOURCE = CodeSource(code="NP 112:2014", table="Tabelul D.4")

# _SubGrid[e][I_C] = p_conv
_SubGrid = dict[float, dict[float, float]]

# _TABLE[PlasticityClass]["medium_to_firm" | "stiff_to_hard"][e][I_C] = p_conv
# "medium_to_firm": I_C ∈ [0.5, 0.75)   "stiff_to_hard": I_C ∈ [0.75, 1.0]
_TABLE: dict[PlasticityClass, dict[str, _SubGrid]] = {
    PlasticityClass.LOW: {
        "medium_to_firm": {
            0.5: {0.50: 300.0, 0.75: 325.0},
            0.7: {0.50: 275.0, 0.75: 285.0},
        },
        "stiff_to_hard": {
            0.5: {0.75: 325.0, 1.00: 350.0},
            0.7: {0.75: 285.0, 1.00: 300.0},
        },
    },
    PlasticityClass.MEDIUM: {
        "medium_to_firm": {
            0.5: {0.50: 300.0, 0.75: 325.0},
            0.7: {0.50: 275.0, 0.75: 285.0},
            1.0: {0.50: 200.0, 0.75: 225.0},
        },
        "stiff_to_hard": {
            0.5: {0.75: 325.0, 1.00: 350.0},
            0.7: {0.75: 285.0, 1.00: 300.0},
            1.0: {0.75: 225.0, 1.00: 250.0},
        },
    },
    PlasticityClass.HIGH: {
        "medium_to_firm": {
            0.5: {0.50: 550.0, 0.75: 600.0},
            0.6: {0.50: 450.0, 0.75: 485.0},
            0.8: {0.50: 300.0, 0.75: 325.0},
            1.1: {0.50: 225.0, 0.75: 260.0},
        },
        "stiff_to_hard": {
            0.5: {0.75: 600.0, 1.00: 650.0},
            0.6: {0.75: 485.0, 1.00: 525.0},
            0.8: {0.75: 325.0, 1.00: 350.0},
            1.1: {0.75: 260.0, 1.00: 300.0},
        },
    },
}

_E_MIN = 0.5
_E_MAX: dict[PlasticityClass, float] = {
    PlasticityClass.LOW:    0.7,
    PlasticityClass.MEDIUM: 1.0,
    PlasticityClass.HIGH:   1.1,
}
_IC_MIN = 0.5
_IC_MAX = 1.0
_IC_BAND_BOUNDARY = 0.75


def _interpolate_successive(grid: _SubGrid, e: float, ic: float) -> tuple[float | None, bool]:
    """Interpolare succesivă: întâi pe I_C la fiecare nod e, apoi pe e."""
    e_vals = sorted(grid)

    # Exact match pe e → interpolare liniară pe I_C
    for ev in e_vals:
        if abs(e - ev) < 1e-9:
            lr = interpolate_linear(grid[ev], ic)
            return lr.value, lr.interpolated

    # Bracket pe e
    idx = bisect.bisect_left(e_vals, e)
    e0, e1 = e_vals[idx - 1], e_vals[idx]

    lr0 = interpolate_linear(grid[e0], ic)
    lr1 = interpolate_linear(grid[e1], ic)

    if lr0.value is None or lr1.value is None:
        return None, False

    t = (e - e0) / (e1 - e0)
    return lr0.value + t * (lr1.value - lr0.value), True


def get_presumed_bearing_pressure(
    plasticity_class: PlasticityClass,
    void_ratio: float,
    consistency_index: float,
) -> PresumedBearingPressureResult:
    """
    Returnează p̄_conv [kPa] pentru pământuri fine coezive
    conform NP 112:2014, Tabelul D.4.

    Interpolare succesivă pe I_C și e în interiorul benzii selectate.
    Nu se interpolează cross-bandă (limita benzii: I_C = 0.75).
    """
    result = PresumedBearingPressureResult(source=_SOURCE)

    try:
        plasticity_class = PlasticityClass(plasticity_class)
    except ValueError:
        result.errors.append(f"Clasă de plasticitate necunoscută: {plasticity_class!r}.")
        return result

    e_max = _E_MAX[plasticity_class]

    if void_ratio < _E_MIN or void_ratio > e_max:
        result.errors.append(
            f"void_ratio (e) = {void_ratio} este în afara domeniului "
            f"[{_E_MIN}, {e_max}] pentru plasticitate {plasticity_class!r}."
        )
        return result

    if consistency_index < _IC_MIN or consistency_index > _IC_MAX:
        result.errors.append(
            f"consistency_index (I_C) = {consistency_index} este în afara "
            f"domeniului [{_IC_MIN}, {_IC_MAX}]."
        )
        return result

    band = "stiff_to_hard" if consistency_index >= _IC_BAND_BOUNDARY else "medium_to_firm"
    grid = _TABLE[plasticity_class][band]

    value, interpolated = _interpolate_successive(grid, e=void_ratio, ic=consistency_index)

    if value is None:
        result.errors.append(
            f"Combinație (e={void_ratio}, I_C={consistency_index}) nu poate fi interpolată "
            f"în banda {band!r} pentru plasticitate {plasticity_class!r}."
        )
        return result

    result.p_conv = value
    result.interpolated = interpolated
    result.soil_type = SoilCategory.COHESIVE
    result.valid = True
    return result
