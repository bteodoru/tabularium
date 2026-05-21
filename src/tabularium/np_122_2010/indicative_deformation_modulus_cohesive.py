from __future__ import annotations

from dataclasses import dataclass

from ..interpolation import interpolate_linear
from ..models import CodeSource, LookupResult

_SOURCE = CodeSource(code="NP 122:2010", table="Tabelul A.6.4")


@dataclass
class DeformationModulusCohesiveResult(LookupResult):
    e_modulus: float | None = None
    ip_category: str | None = None
    ic_range: str | None = None
    e_lower: float | None = None
    e_upper: float | None = None


# _TABLE[ip_cat][ic_range][e] = E (kPa)
_TABLE: dict[str, dict[str, dict[float, int]]] = {
    "<10": {
        "0.25-1.00": {
            0.45: 32_000,
            0.55: 24_000,
            0.65: 16_000,
            0.75: 10_000,
            0.85:  7_000,
        },
    },
    "10-20": {
        "0.75-1.00": {
            0.45: 34_000,
            0.55: 27_000,
            0.65: 22_000,
            0.75: 17_000,
            0.85: 14_000,
            0.95: 11_000,
        },
        "0.50-0.75": {
            0.45: 32_000,
            0.55: 25_000,
            0.65: 19_000,
            0.75: 14_000,
            0.85: 11_000,
            0.95:  8_000,
        },
    },
    ">20": {
        "0.75-1.00": {
            0.55: 28_000,
            0.65: 24_000,
            0.75: 21_000,
            0.85: 18_000,
            0.95: 15_000,
            1.05: 12_000,
        },
        "0.50-0.75": {
            0.65: 21_000,
            0.75: 18_000,
            0.85: 15_000,
            0.95: 12_000,
            1.05:  9_000,
        },
    },
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
            "acoperit de Tabelul A.6.4. Se utilizează rândul disponibil cu caracter "
            "conservativ."
        )

    if ip_cat == "<10":
        if ic < 0.25:
            return None, warnings
        return "0.25-1.00", warnings

    # IP 10-20 or >20
    if ic > 1.0 or ic >= 0.75:
        return "0.75-1.00", warnings
    if ic >= 0.50:
        return "0.50-0.75", warnings
    return None, warnings


def get_deformation_modulus(ip: float, ic: float, e: float) -> DeformationModulusCohesiveResult:
    """
    Returnează modulul de deformație lineară E (kPa) pentru pământuri coezive
    conform NP 122:2010, Tabelul A.6.4.

    Interpolarea pe e este liniară. Nu se interpolează pe I_C sau I_P.
    Extrapolarea în afara domeniului tabelat este interzisă.

    Parameters
    ----------
    ip : float  Indicele de plasticitate [%]
    ic : float  Indicele de consistență  [-]
    e  : float  Indicele porilor         [-]
    """
    result = DeformationModulusCohesiveResult(source=_SOURCE)
    all_warnings: list[str] = []

    ip_cat = _classify_ip(ip)
    result.ip_category = ip_cat

    ic_range, ic_warnings = _select_ic_range(ic, ip_cat)
    all_warnings.extend(ic_warnings)

    if ic_range is None:
        limit = "0,25" if ip_cat == "<10" else "0,50"
        result.errors.append(
            f"I_C = {ic:.3f} este în afara domeniului tabelat "
            f"pentru I_P = {ip:.1f}% (categorie: {ip_cat}). "
            f"Tabelul A.6.4 nu acoperă I_C < {limit}."
        )
        result.warnings = all_warnings
        return result

    result.ic_range = ic_range
    row = _TABLE[ip_cat][ic_range]
    knots = {ev: float(v) for ev, v in row.items()}

    e_res = interpolate_linear(knots, e)
    all_warnings.extend(e_res.warnings)

    if e_res.value is None:
        e_vals = sorted(row)
        result.errors.append(
            f"e = {e:.3f} este în afara domeniului tabelat pentru "
            f"I_P {ip_cat}, I_C {ic_range}. "
            f"Domeniu disponibil: e ∈ [{e_vals[0]:.2f} … {e_vals[-1]:.2f}]."
        )
        result.warnings = all_warnings
        return result

    result.e_modulus = round(e_res.value, 2)
    result.valid = True
    result.interpolated = e_res.interpolated
    result.e_lower = e_res.x_lower
    result.e_upper = e_res.x_upper
    result.warnings = all_warnings
    return result
