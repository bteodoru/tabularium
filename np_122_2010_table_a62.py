"""
np074_table_a62.py
==================
Tabelul A.6.2 – NP 122:2022
Valori caracteristice φ' (grade) și c' (kPa) pentru pământuri coezive.

Domeniu de validitate: S_r > 0.8 (Observația 1 din tabel).

Design notes
------------
- Interpolarea pe *e* este lineară, conform Observației 2 din tabel.
- Nu se interpolează pe I_C — normativul nu prevede acest lucru.
  Lookup-ul pe I_C este discret, pe rândul al cărui interval conține valoarea.
- Celulele goale din tabel reprezintă domenii invalide (nu zerouri).
  Extrapolarea în afara domeniului tabelat pentru un rând dat este interzisă.
- I_C > 1.0: în afara tabelului; se returnează rezultat cu avertisment explicit.
- I_C < 0.25: pământ plastic moale, complet în afara tabelului; eroare.
- Frontiere convenite: [0.75, ∞) → rândul "0.75-1.00"
                        [0.50, 0.75) → rândul "0.50-0.75"
                        [0.25, 0.50) → rândul "0.25-0.50"
"""

from __future__ import annotations

import bisect
from dataclasses import dataclass, field
from typing import Optional


# ── Datele tabelului ──────────────────────────────────────────────────────────
# _TABLE[ip_cat][ic_range][e] = (phi [grade], c [kPa])
#
# ip_cat   : "<10" | "10-20" | ">20"
# ic_range : "0.75-1.00" | "0.50-0.75" | "0.25-0.50"
# e        : valoare tabelată exactă (float)

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
        # Rândul "0.25-0.50" nu apare pentru IP < 10 în tabel.
    },
    "10-20": {
        "0.75-1.00": {
            0.45: (22, 30),
            0.55: (21, 24),
            0.65: (20, 20),
            0.75: (19, 16),
            0.85: (18, 14),
            0.95: (16, 12),
            # e = 1.05 lipsește pentru acest rând
        },
        "0.50-0.75": {
            0.45: (20, 25),
            0.55: (19, 22),
            0.65: (18, 18),
            0.75: (17, 15),
            0.85: (15, 12),
            0.95: (14, 10),
            # e = 1.05 lipsește pentru acest rând
        },
        "0.25-0.50": {
            # e = 0.45 și 0.55 lipsesc pentru acest rând
            0.65: (16, 16),
            0.75: (15, 13),
            0.85: (13, 10),
            0.95: (11,  9),
            1.05: (10,  7),
        },
    },
    ">20": {
        "0.75-1.00": {
            # e = 0.45 lipsește pentru acest rând
            0.55: (17, 53),
            0.65: (16, 44),
            0.75: (15, 35),
            0.85: (15, 31),
            0.95: (13, 27),
            1.05: (11, 24),
        },
        "0.50-0.75": {
            # e = 0.45 și 0.55 lipsesc pentru acest rând
            0.65: (15, 37),
            0.75: (14, 33),
            0.85: (13, 28),
            0.95: (11, 24),
            1.05: ( 9, 21),
        },
        "0.25-0.50": {
            # e = 0.45 și 0.55 lipsesc pentru acest rând
            0.65: (12, 29),
            0.75: (11, 27),
            0.85: (10, 23),
            0.95: ( 8, 21),
            1.05: ( 5, 19),
        },
    },
}

# Rânduri I_C disponibile per categorie I_P (pentru validare rapidă)
_IC_RANGES_AVAILABLE: dict[str, list[str]] = {
    cat: list(rows.keys()) for cat, rows in _TABLE.items()
}


# ── Tipuri de rezultat ────────────────────────────────────────────────────────

@dataclass
class ShearParamResult:
    """Rezultatul unui query pe Tabelul A.6.2."""

    phi: Optional[float] = None          # φ' [grade]
    c:   Optional[float] = None          # c' [kPa]
    valid: bool = False

    ip_category: Optional[str] = None   # "<10" | "10-20" | ">20"
    ic_range:    Optional[str] = None   # rândul I_C utilizat
    e_lower:     Optional[float] = None # e inferior pentru interpolare
    e_upper:     Optional[float] = None # e superior pentru interpolare
    interpolated_on_e: bool = False     # True dacă e ≠ valoare tabelată exactă

    warnings: list[str] = field(default_factory=list)
    errors:   list[str] = field(default_factory=list)


# ── Logică internă ────────────────────────────────────────────────────────────

def _classify_ip(IP: float) -> str:
    """Determină categoria I_P."""
    if IP < 10:
        return "<10"
    elif IP <= 20:
        return "10-20"
    else:
        return ">20"


def _select_ic_range(IC: float, ip_cat: str) -> tuple[Optional[str], list[str]]:
    """
    Selectează rândul I_C prin lookup discret.
    Returnează (ic_range_key | None, warnings).
    """
    warnings: list[str] = []

    # I_C > 1.0: supraconsolidat, în afara tabelului
    if IC > 1.0:
        warnings.append(
            f"I_C = {IC:.3f} > 1,00: pământ supraconsolidat, în afara domeniului "
            "acoperit de Tabelul A.6.2. Se utilizează rândul I_C ∈ [0,75 … 1,00] "
            "cu caracter conservativ (valorile φ' și c' pot fi supraevaluate)."
        )
        IC = 0.90  # plasat în mijlocul rândului superior

    # Determinare rând
    if IC >= 0.75:
        candidate = "0.75-1.00"
    elif IC >= 0.50:
        candidate = "0.50-0.75"
    elif IC >= 0.25:
        candidate = "0.25-0.50"
    else:
        # IC < 0.25: pământ moale plastic, complet în afara tabelului
        return None, warnings

    # Verifică că rândul există pentru categoria I_P dată
    if candidate not in _IC_RANGES_AVAILABLE[ip_cat]:
        return None, warnings

    return candidate, warnings


def _interpolate_on_e(
    row: dict[float, tuple[int, int]],
    e: float,
) -> tuple[Optional[float], Optional[float], Optional[float], Optional[float], bool, list[str]]:
    """
    Interpolează liniar φ' și c' pentru valoarea *e* în rândul dat.

    Returnează:
        (phi, c, e_lower, e_upper, interpolated, warnings)
    phi/c = None  →  e este în afara domeniului tabelat pentru acest rând.
    """
    warnings: list[str] = []
    e_vals = sorted(row.keys())

    # Potrivire exactă (cu toleranță numerică)
    for ev in e_vals:
        if abs(e - ev) < 1e-9:
            phi, c = row[ev]
            return float(phi), float(c), ev, ev, False, warnings

    idx = bisect.bisect_left(e_vals, e)

    # Extrapolarea este interzisă
    if idx == 0:
        warnings.append(
            f"e = {e:.3f} < e_min tabelat ({e_vals[0]:.2f}) pentru acest rând. "
            "Extrapolarea nu este permisă."
        )
        return None, None, None, None, False, warnings

    if idx == len(e_vals):
        warnings.append(
            f"e = {e:.3f} > e_max tabelat ({e_vals[-1]:.2f}) pentru acest rând. "
            "Extrapolarea nu este permisă."
        )
        return None, None, None, None, False, warnings

    # Interpolare liniară
    e0, e1 = e_vals[idx - 1], e_vals[idx]
    phi0, c0 = row[e0]
    phi1, c1 = row[e1]

    t = (e - e0) / (e1 - e0)
    phi = phi0 + t * (phi1 - phi0)
    c   = c0   + t * (c1   - c0)

    return phi, c, e0, e1, True, warnings


# ── Funcție publică ───────────────────────────────────────────────────────────

def get_phi_c(IP: float, IC: float, e: float) -> ShearParamResult:
    """
    Returnează valorile caracteristice orientative pentru parametrii rezistenței 
    la forfecare, φ' și c', conform NP 122:2022 (Tabelul A.6.2).

    Parametri
    ---------
    IP : float  – Indicele de plasticitate [%]
    IC : float  – Indicele de consistență  [-]
    e  : float  – Indicele porilor         [-]

    Returns
    -------
    ShearParamResult
        .phi      – unghiul de frecare efectiv φ' [grade] sau None
        .c        – coeziunea efectivă c'          [kPa]  sau None
        .valid    – True dacă valorile au putut fi determinate
        .interpolated_on_e – True dacă s-a interpolat pe e
        .e_lower, .e_upper – capetele intervalului de interpolare
        .ip_category, .ic_range – clasificările utilizate
        .warnings – avertismente (result.valid poate fi True)
        .errors   – motive pentru care result.valid = False
    """
    result = ShearParamResult()
    all_warnings: list[str] = []

    # ── 1. Clasificare I_P ────────────────────────────────────────────────────
    ip_cat = _classify_ip(IP)
    result.ip_category = ip_cat

    # ── 2. Selectare rând I_C ─────────────────────────────────────────────────
    ic_range, ic_warnings = _select_ic_range(IC, ip_cat)
    all_warnings.extend(ic_warnings)

    if ic_range is None:
        result.errors.append(
            f"I_C = {IC:.3f} este în afara domeniului tabelat "
            f"pentru I_P = {IP:.1f}% (categorie: {ip_cat}). "
            "Tabelul A.6.2 nu acoperă I_C < 0,25."
        )
        result.warnings = all_warnings
        return result

    result.ic_range = ic_range
    row = _TABLE[ip_cat][ic_range]

    # ── 3. Interpolare pe e ───────────────────────────────────────────────────
    phi, c, e_lower, e_upper, interpolated, e_warnings = _interpolate_on_e(row, e)
    all_warnings.extend(e_warnings)

    if phi is None:
        e_vals = sorted(row.keys())
        result.errors.append(
            f"e = {e:.3f} este în afara domeniului tabelat pentru "
            f"I_P {ip_cat}, I_C {ic_range}. "
            f"Domeniu disponibil: e ∈ [{e_vals[0]:.2f} … {e_vals[-1]:.2f}]."
        )
        result.warnings = all_warnings
        return result

    # ── 4. Rezultat valid ─────────────────────────────────────────────────────
    result.phi = round(phi, 2)
    result.c   = round(c,   2)
    result.valid = True
    result.e_lower = e_lower
    result.e_upper = e_upper
    result.interpolated_on_e = interpolated
    result.warnings = all_warnings

    return result


# ── Wrapper pentru tool MCP ───────────────────────────────────────────────────

def tool_get_shear_params_coeziv(
    IP: float,
    IC: float,
    e: float,
) -> dict:
    """
    Tool Opifer – Tabelul A.6.2, NP 074:2022.

    Returnează valorile caracteristice ale parametrilor de rezistență la forfecare
    (φ', c') pentru pământuri coezive cu S_r > 0,8.

    Args:
        IP: Indicele de plasticitate [%]  – ex. 18.5
        IC: Indicele de consistență  [-]  – ex. 0.72
        e:  Indicele porilor         [-]  – ex. 0.81

    Returns:
        dict cu câmpurile:
            phi            – φ' [grade] sau null
            c              – c' [kPa] sau null
            valid          – bool
            interpolated_on_e – bool
            e_lower        – e inferior utilizat la interpolare
            e_upper        – e superior utilizat la interpolare
            ip_category    – categoria I_P utilizată
            ic_range       – rândul I_C utilizat
            warnings       – listă de avertismente (non-fatale)
            errors         – listă de erori (valid = False)
            source         – referința normativă
    """
    result = get_phi_c(IP=IP, IC=IC, e=e)
    return {
        "phi":               result.phi,
        "c":                 result.c,
        "valid":             result.valid,
        "interpolated_on_e": result.interpolated_on_e,
        "e_lower":           result.e_lower,
        "e_upper":           result.e_upper,
        "ip_category":       result.ip_category,
        "ic_range":          result.ic_range,
        "warnings":          result.warnings,
        "errors":            result.errors,
        "source":            "NP 074:2022, Tabelul A.6.2",
    }


# ── Smoke tests ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import json

    cases = [
        # (IP,   IC,    e,     descriere)
        (18.5, 0.72, 0.81,  "IP 10-20, IC 0.50-0.75, e interpolat"),
        (7.0,  0.80, 0.55,  "IP <10,   IC 0.75-1.00, e exact"),
        (25.0, 0.60, 0.70,  "IP >20,   IC 0.50-0.75, e interpolat"),
        (15.0, 0.30, 0.90,  "IP 10-20, IC 0.25-0.50, e interpolat"),
        (15.0, 1.20, 0.65,  "IC > 1.0  → warning supraconsolidat"),
        (10.0, 0.10, 0.65,  "IC < 0.25 → eroare domeniu"),
        (18.0, 0.60, 0.40,  "e < e_min pentru rândul dat → eroare"),
        (25.0, 0.80, 1.05,  "IP >20,   IC 0.75-1.00, e exact la limită"),
    ]

    for IP, IC, e, desc in cases:
        r = tool_get_shear_params_coeziv(IP=IP, IC=IC, e=e)
        print(f"\n{'─'*60}")
        print(f"[{desc}]  IP={IP}, IC={IC}, e={e}")
        print(json.dumps(r, ensure_ascii=False, indent=2))