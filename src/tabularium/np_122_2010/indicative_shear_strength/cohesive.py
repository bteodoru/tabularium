from __future__ import annotations

from dataclasses import dataclass

from ...interpolation import interpolate_linear
from ...models import CodeSource, LookupResult

_SOURCE = CodeSource(code="NP 122:2010", table="Tabelul A.6.2")


@dataclass
class ShearStrengthResult(LookupResult):
    phi: float | None = None
    c: float | None = None
    ip_category: str | None = None
    ic_range: str | None = None
    e_lower: float | None = None
    e_upper: float | None = None


# _TABLE[ip_cat][ic_range][e] = (phi [grade], c [kPa])
_TABLE: dict[str, dict[str, dict[float, tuple[int, int]]]] = {
    "<10": {
        "0.75-1.00": {
            0.45: (25, 10),
            0.55: (24,  7),
            0.65: (22,  5),
        },
        "0.50-0.75": {
            0.45: (23,  8),
            0.55: (22,  6),
            0.65: (20,  4),
            0.75: (17,  2),
        },
    },
    "10-20": {
        "0.75-1.00": {
            0.45: (22, 30),
            0.55: (21, 24),
            0.65: (20, 20),
            0.75: (19, 16),
            0.85: (18, 14),
            0.95: (16, 12),
        },
        "0.50-0.75": {
            0.45: (20, 25),
            0.55: (19, 22),
            0.65: (18, 18),
            0.75: (17, 15),
            0.85: (15, 12),
            0.95: (14, 10),
        },
        "0.25-0.50": {
            0.65: (16, 16),
            0.75: (15, 13),
            0.85: (13, 10),
            0.95: (11,  9),
            1.05: (10,  7),
        },
    },
    ">20": {
        "0.75-1.00": {
            0.55: (17, 53),
            0.65: (16, 44),
            0.75: (15, 35),
            0.85: (15, 31),
            0.95: (13, 27),
            1.05: (11, 24),
        },
        "0.50-0.75": {
            0.65: (15, 37),
            0.75: (14, 33),
            0.85: (13, 28),
            0.95: (11, 24),
            1.05: ( 9, 21),
        },
        "0.25-0.50": {
            0.65: (12, 29),
            0.75: (11, 27),
            0.85: (10, 23),
            0.95: ( 8, 21),
            1.05: ( 5, 19),
        },
    },
}

_IC_RANGES_AVAILABLE: dict[str, list[str]] = {
    cat: list(rows.keys()) for cat, rows in _TABLE.items()
}


def _classify_ip(ip: float) -> str:
    if ip < 10:
        return "<10"
    if ip <= 20:
        return "10-20"
    return ">20"


def _select_ic_range(ic: float, ip_cat: str) -> tuple[str | None, list[str]]:
    warnings: list[str] = []
    if ic > 1.0:
        warnings.append(
            f"I_C = {ic:.3f} > 1,00: pământ supraconsolidat, în afara domeniului "
            "acoperit de Tabelul A.6.2. Se utilizează rândul I_C ∈ [0,75 … 1,00] "
            "cu caracter conservativ."
        )
        ic = 0.90

    if ic >= 0.75:
        candidate = "0.75-1.00"
    elif ic >= 0.50:
        candidate = "0.50-0.75"
    elif ic >= 0.25:
        candidate = "0.25-0.50"
    else:
        return None, warnings

    if candidate not in _IC_RANGES_AVAILABLE[ip_cat]:
        return None, warnings

    return candidate, warnings


def get_phi_c(ip: float, ic: float, e: float) -> ShearStrengthResult:
    """
    Returnează valorile orientative ale parametrilor rezistenței la forfecare
    a pământurilor coezive, în condiții drenate  (φ', c') conform NP 122:2010,
    Tabelul A.6.2.

    Domeniu de validitate: S_r > 0.8.
    Interpolarea pe e este liniară. Nu se interpolează pe I_C.
    Extrapolarea în afara domeniului tabelat este interzisă.

    Parameters
    ----------
    ip : float  Indicele de plasticitate [%]
    ic : float  Indicele de consistență  [-]
    e  : float  Indicele porilor         [-]
    """
    result = ShearStrengthResult(source=_SOURCE)
    all_warnings: list[str] = []

    ip_cat = _classify_ip(ip)
    result.ip_category = ip_cat

    ic_range, ic_warnings = _select_ic_range(ic, ip_cat)
    all_warnings.extend(ic_warnings)

    if ic_range is None:
        result.errors.append(
            f"I_C = {ic:.3f} este în afara domeniului tabelat "
            f"pentru I_P = {ip:.1f}% (categorie: {ip_cat}). "
            "Tabelul A.6.2 nu acoperă I_C < 0,25."
        )
        result.warnings = all_warnings
        return result

    result.ic_range = ic_range
    row = _TABLE[ip_cat][ic_range]

    knots_phi = {ev: float(vc[0]) for ev, vc in row.items()}
    knots_c   = {ev: float(vc[1]) for ev, vc in row.items()}

    phi_res = interpolate_linear(knots_phi, e)
    c_res   = interpolate_linear(knots_c,   e)
    all_warnings.extend(phi_res.warnings)

    if phi_res.value is None:
        e_vals = sorted(row)
        result.errors.append(
            f"e = {e:.3f} este în afara domeniului tabelat pentru "
            f"I_P {ip_cat}, I_C {ic_range}. "
            f"Domeniu disponibil: e ∈ [{e_vals[0]:.2f} … {e_vals[-1]:.2f}]."
        )
        result.warnings = all_warnings
        return result

    result.phi = round(phi_res.value, 2)
    result.c   = round(c_res.value, 2)  # type: ignore[arg-type]
    result.valid = True
    result.interpolated = phi_res.interpolated
    result.e_lower = phi_res.x_lower
    result.e_upper = phi_res.x_upper
    result.warnings = all_warnings
    return result
