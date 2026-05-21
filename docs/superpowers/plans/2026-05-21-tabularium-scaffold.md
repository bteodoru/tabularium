# tabularium Package Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the tabularium Python package with scaffold, shared infrastructure (`models.py`, `interpolation.py`), the NP 122 Tabelul A.6.2 lookup, and a registry skeleton.

**Architecture:** Pure Python package. A base `LookupResult` dataclass in `models.py` holds common fields (`valid`, `interpolated`, `source`, `warnings`, `errors`). A generic `interpolate_linear` utility in `interpolation.py` interpolates a single float value over a `dict[float, float]` knot map. Table modules (e.g. `np122/indicative_shear_strength.py`) subclass `LookupResult` with table-specific fields and implement a single public lookup function. A central `registry.py` indexes available tables by string key.

**Tech Stack:** Python 3.10+, stdlib only (`dataclasses`, `bisect`), pytest.

---

## File Map

| File | Responsibility |
|------|---------------|
| `pyproject.toml` | Build metadata, dev dependencies |
| `tabularium/__init__.py` | Package marker + version |
| `tabularium/models.py` | `CodeSource`, `LookupResult` base |
| `tabularium/interpolation.py` | `interpolate_linear`, `LinearResult` |
| `tabularium/registry.py` | `TableEntry`, `REGISTRY`, `list_tables`, `get_table` |
| `tabularium/np122/__init__.py` | Subpackage marker |
| `tabularium/np122/indicative_shear_strength.py` | Table data, `ShearStrengthResult`, `get_phi_c` |
| `tabularium/np112/__init__.py` | Subpackage marker (placeholder) |
| `tests/__init__.py` | Test package marker |
| `tests/test_models.py` | Smoke tests for dataclass instantiation |
| `tests/test_interpolation.py` | Full TDD for `interpolate_linear` |
| `tests/test_np122_indicative_shear_strength.py` | Full TDD for `get_phi_c` |
| `tests/test_registry.py` | TDD for registry lookup |

---

## Task 1: Package Scaffold

**Files:**
- Create: `pyproject.toml`
- Create: `tabularium/__init__.py`
- Create: `tabularium/np122/__init__.py`
- Create: `tabularium/np112/__init__.py`
- Create: `tests/__init__.py`

- [ ] **Step 1: Create `pyproject.toml`**

```toml
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.backends.legacy:build"

[project]
name = "tabularium"
version = "0.1.0"
description = "Romanian geotechnical normative table lookups"
requires-python = ">=3.10"
dependencies = []

[project.optional-dependencies]
dev = ["pytest>=7"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

- [ ] **Step 2: Create package markers**

`tabularium/__init__.py`:
```python
"""tabularium — Romanian geotechnical normative table lookups."""

__version__ = "0.1.0"
```

`tabularium/np122/__init__.py` — empty file.

`tabularium/np112/__init__.py` — empty file.

`tests/__init__.py` — empty file.

- [ ] **Step 3: Install in editable mode and verify import**

```bash
pip install -e ".[dev]"
python -c "import tabularium; print(tabularium.__version__)"
```
Expected output: `0.1.0`

- [ ] **Step 4: Commit**

```bash
git init
git add pyproject.toml tabularium/ tests/
git commit -m "chore: initial package scaffold"
```

---

## Task 2: `models.py`

**Files:**
- Create: `tabularium/models.py`
- Create: `tests/test_models.py`

- [ ] **Step 1: Write the failing test**

`tests/test_models.py`:
```python
from tabularium.models import CodeSource, LookupResult


def test_code_source_required_fields():
    src = CodeSource(code="NP 122:2010", table="Tabelul A.6.2")
    assert src.code == "NP 122:2010"
    assert src.table == "Tabelul A.6.2"
    assert src.section is None


def test_code_source_with_section():
    src = CodeSource(code="NP 122:2010", table="Tabelul A.6.2", section="A.6")
    assert src.section == "A.6"


def test_lookup_result_defaults():
    r = LookupResult()
    assert r.valid is False
    assert r.interpolated is False
    assert r.source is None
    assert r.warnings == []
    assert r.errors == []


def test_lookup_result_with_source():
    src = CodeSource(code="NP 122:2010", table="Tabelul A.6.2")
    r = LookupResult(valid=True, source=src)
    assert r.valid is True
    assert r.source.code == "NP 122:2010"


def test_lookup_result_warnings_not_shared():
    r1 = LookupResult()
    r2 = LookupResult()
    r1.warnings.append("w")
    assert r2.warnings == []
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_models.py -v
```
Expected: `ImportError` — `tabularium.models` not found.

- [ ] **Step 3: Implement `models.py`**

`tabularium/models.py`:
```python
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class CodeSource:
    code: str
    table: str
    section: str | None = None


@dataclass
class LookupResult:
    valid: bool = False
    interpolated: bool = False
    source: CodeSource | None = None
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_models.py -v
```
Expected: 5 PASSED.

- [ ] **Step 5: Commit**

```bash
git add tabularium/models.py tests/test_models.py
git commit -m "feat: add CodeSource and LookupResult base dataclasses"
```

---

## Task 3: `interpolation.py`

**Files:**
- Create: `tabularium/interpolation.py`
- Create: `tests/test_interpolation.py`

- [ ] **Step 1: Write failing tests**

`tests/test_interpolation.py`:
```python
import pytest
from tabularium.interpolation import LinearResult, interpolate_linear


def test_exact_match_first():
    knots = {0.45: 25.0, 0.55: 24.0, 0.65: 22.0}
    r = interpolate_linear(knots, 0.45)
    assert r.value == pytest.approx(25.0)
    assert r.interpolated is False
    assert r.x_lower == pytest.approx(0.45)
    assert r.x_upper == pytest.approx(0.45)
    assert r.warnings == []


def test_exact_match_middle():
    knots = {0.45: 25.0, 0.55: 24.0, 0.65: 22.0}
    r = interpolate_linear(knots, 0.55)
    assert r.value == pytest.approx(24.0)
    assert r.interpolated is False


def test_exact_match_last():
    knots = {0.45: 25.0, 0.55: 24.0, 0.65: 22.0}
    r = interpolate_linear(knots, 0.65)
    assert r.value == pytest.approx(22.0)
    assert r.interpolated is False


def test_interpolated_midpoint():
    # Between 0.55 (24.0) and 0.65 (22.0) → t=0.5 → 23.0
    knots = {0.45: 25.0, 0.55: 24.0, 0.65: 22.0}
    r = interpolate_linear(knots, 0.60)
    assert r.value == pytest.approx(23.0)
    assert r.interpolated is True
    assert r.x_lower == pytest.approx(0.55)
    assert r.x_upper == pytest.approx(0.65)
    assert r.warnings == []


def test_interpolated_one_quarter():
    # Between 0.45 (25.0) and 0.55 (24.0) → t=0.25 → 24.75
    knots = {0.45: 25.0, 0.55: 24.0, 0.65: 22.0}
    r = interpolate_linear(knots, 0.475)
    assert r.value == pytest.approx(24.75)
    assert r.interpolated is True
    assert r.x_lower == pytest.approx(0.45)
    assert r.x_upper == pytest.approx(0.55)


def test_below_range():
    knots = {0.55: 24.0, 0.65: 22.0}
    r = interpolate_linear(knots, 0.40)
    assert r.value is None
    assert r.interpolated is False
    assert r.x_lower is None
    assert r.x_upper is None
    assert len(r.warnings) == 1
    assert "x_min" in r.warnings[0] or "0.55" in r.warnings[0]


def test_above_range():
    knots = {0.55: 24.0, 0.65: 22.0}
    r = interpolate_linear(knots, 0.80)
    assert r.value is None
    assert len(r.warnings) == 1
    assert "x_max" in r.warnings[0] or "0.65" in r.warnings[0]


def test_single_knot_exact():
    knots = {0.55: 24.0}
    r = interpolate_linear(knots, 0.55)
    assert r.value == pytest.approx(24.0)
    assert r.interpolated is False


def test_single_knot_miss():
    knots = {0.55: 24.0}
    r = interpolate_linear(knots, 0.60)
    assert r.value is None
    assert len(r.warnings) == 1


def test_result_type():
    knots = {0.5: 10.0, 0.7: 8.0}
    r = interpolate_linear(knots, 0.6)
    assert isinstance(r, LinearResult)
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_interpolation.py -v
```
Expected: `ImportError` — `tabularium.interpolation` not found.

- [ ] **Step 3: Implement `interpolation.py`**

`tabularium/interpolation.py`:
```python
from __future__ import annotations

import bisect
from dataclasses import dataclass, field


@dataclass
class LinearResult:
    value: float | None
    x_lower: float | None
    x_upper: float | None
    interpolated: bool
    warnings: list[str] = field(default_factory=list)


def interpolate_linear(knots: dict[float, float], x: float) -> LinearResult:
    """
    Interpolează liniar valoarea y pentru x dat, fără extrapolate.

    knots: mapare {x_tabelat: y_tabelat}
    Returnează LinearResult cu value=None și un warning dacă x este în afara domeniului.
    """
    x_vals = sorted(knots)

    for xv in x_vals:
        if abs(x - xv) < 1e-9:
            return LinearResult(
                value=float(knots[xv]),
                x_lower=xv,
                x_upper=xv,
                interpolated=False,
            )

    idx = bisect.bisect_left(x_vals, x)

    if idx == 0:
        return LinearResult(
            value=None,
            x_lower=None,
            x_upper=None,
            interpolated=False,
            warnings=[
                f"x = {x} < x_min tabelat ({x_vals[0]}) pentru acest rând. "
                "Extrapolarea nu este permisă."
            ],
        )

    if idx == len(x_vals):
        return LinearResult(
            value=None,
            x_lower=None,
            x_upper=None,
            interpolated=False,
            warnings=[
                f"x = {x} > x_max tabelat ({x_vals[-1]}) pentru acest rând. "
                "Extrapolarea nu este permisă."
            ],
        )

    x0, x1 = x_vals[idx - 1], x_vals[idx]
    t = (x - x0) / (x1 - x0)
    return LinearResult(
        value=knots[x0] + t * (knots[x1] - knots[x0]),
        x_lower=x0,
        x_upper=x1,
        interpolated=True,
    )
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_interpolation.py -v
```
Expected: 10 PASSED.

- [ ] **Step 5: Commit**

```bash
git add tabularium/interpolation.py tests/test_interpolation.py
git commit -m "feat: add generic linear interpolation utility"
```

> **Notă — `bilinear`:** `context.md` menționează și interpolarea biliniară, necesară pentru tabele 2D. Nu se implementează acum (nu există tabel 2D disponibil). Se adaugă când apare primul tabel cu doi parametri continui.

---

## Task 4: `np122/indicative_shear_strength.py`

**Files:**
- Create: `tabularium/np122/indicative_shear_strength.py`
- Create: `tests/test_np122_indicative_shear_strength.py`

- [ ] **Step 1: Write failing tests**

`tests/test_np122_indicative_shear_strength.py`:
```python
import pytest
from tabularium.np122.indicative_shear_strength import ShearStrengthResult, get_phi_c


# ── Lookup exact ──────────────────────────────────────────────────────────────

def test_exact_lookup_ip_lt10_ic_0_75_1_00():
    # IP <10, IC 0.75-1.00, e=0.45 (exact)
    r = get_phi_c(ip=7.0, ic=0.80, e=0.45)
    assert r.valid is True
    assert r.phi == pytest.approx(25.0)
    assert r.c == pytest.approx(10.0)
    assert r.interpolated is False
    assert r.ip_category == "<10"
    assert r.ic_range == "0.75-1.00"
    assert r.e_lower == pytest.approx(0.45)
    assert r.e_upper == pytest.approx(0.45)
    assert r.warnings == []
    assert r.errors == []


def test_exact_lookup_ip_10_20_ic_0_25_0_50():
    # IP 10-20, IC 0.25-0.50, e=1.05 (exact, boundary)
    r = get_phi_c(ip=15.0, ic=0.30, e=1.05)
    assert r.valid is True
    assert r.phi == pytest.approx(10.0)
    assert r.c == pytest.approx(7.0)
    assert r.interpolated is False


def test_exact_lookup_ip_gt20_ic_0_75_1_00_e_at_1_05():
    # IP >20, IC 0.75-1.00, e=1.05 (exact, boundary)
    r = get_phi_c(ip=25.0, ic=0.80, e=1.05)
    assert r.valid is True
    assert r.phi == pytest.approx(11.0)
    assert r.c == pytest.approx(24.0)
    assert r.interpolated is False


# ── Lookup interpolat ─────────────────────────────────────────────────────────

def test_interpolated_lookup_midpoint():
    # IP 10-20, IC 0.50-0.75, e=0.60 (between 0.55→(19,22) and 0.65→(18,18))
    # t = (0.60-0.55)/(0.65-0.55) = 0.5
    # phi = 19 + 0.5*(18-19) = 18.5
    # c   = 22 + 0.5*(18-22) = 20.0
    r = get_phi_c(ip=15.0, ic=0.60, e=0.60)
    assert r.valid is True
    assert r.interpolated is True
    assert r.phi == pytest.approx(18.5)
    assert r.c == pytest.approx(20.0)
    assert r.e_lower == pytest.approx(0.55)
    assert r.e_upper == pytest.approx(0.65)
    assert r.warnings == []


def test_interpolated_lookup_ip_gt20():
    # IP >20, IC 0.50-0.75, e=0.70 (between 0.65→(15,37) and 0.75→(14,33))
    # t = (0.70-0.65)/(0.75-0.65) = 0.5
    # phi = 15 + 0.5*(14-15) = 14.5
    # c   = 37 + 0.5*(33-37) = 35.0
    r = get_phi_c(ip=25.0, ic=0.60, e=0.70)
    assert r.valid is True
    assert r.phi == pytest.approx(14.5)
    assert r.c == pytest.approx(35.0)


# ── Source ────────────────────────────────────────────────────────────────────

def test_source_metadata():
    r = get_phi_c(ip=15.0, ic=0.60, e=0.55)
    assert r.source is not None
    assert r.source.code == "NP 122:2010"
    assert r.source.table == "Tabelul A.6.2"


# ── Cazuri eroare ─────────────────────────────────────────────────────────────

def test_ic_below_025_returns_error():
    r = get_phi_c(ip=15.0, ic=0.10, e=0.65)
    assert r.valid is False
    assert len(r.errors) == 1
    assert "0,25" in r.errors[0] or "< 0" in r.errors[0]


def test_ic_row_missing_for_ip_category():
    # IP <10 nu are rândul "0.25-0.50" → eroare
    r = get_phi_c(ip=7.0, ic=0.30, e=0.65)
    assert r.valid is False
    assert len(r.errors) == 1


def test_e_below_minimum_for_row():
    # IP 10-20, IC 0.25-0.50 — e_min = 0.65; e=0.45 < 0.65 → eroare
    r = get_phi_c(ip=15.0, ic=0.30, e=0.45)
    assert r.valid is False
    assert len(r.errors) == 1


def test_e_above_maximum_for_row():
    # IP <10, IC 0.75-1.00 — e_max = 0.65; e=0.80 > 0.65 → eroare
    r = get_phi_c(ip=7.0, ic=0.80, e=0.80)
    assert r.valid is False
    assert len(r.errors) == 1


# ── Cazuri warning (valid) ────────────────────────────────────────────────────

def test_ic_above_1_warning_and_valid():
    # IC > 1.0 → warning, se utilizează rândul 0.75-1.00
    r = get_phi_c(ip=15.0, ic=1.20, e=0.65)
    assert r.valid is True
    assert len(r.warnings) == 1
    assert "supraconsolidat" in r.warnings[0]
    assert r.ic_range == "0.75-1.00"


# ── Frontiere categorii I_P ───────────────────────────────────────────────────

def test_ip_boundary_exactly_10():
    # IP=10 → categorie "10-20"
    r = get_phi_c(ip=10.0, ic=0.80, e=0.45)
    assert r.ip_category == "10-20"
    assert r.valid is True
    assert r.phi == pytest.approx(22.0)
    assert r.c == pytest.approx(30.0)


def test_ip_boundary_exactly_20():
    # IP=20 → categorie "10-20"
    r = get_phi_c(ip=20.0, ic=0.80, e=0.45)
    assert r.ip_category == "10-20"
    assert r.valid is True


def test_ip_just_above_20():
    # IP=20.1 → categorie ">20"
    r = get_phi_c(ip=20.1, ic=0.80, e=0.55)
    assert r.ip_category == ">20"
    assert r.valid is True


# ── Tip rezultat ──────────────────────────────────────────────────────────────

def test_result_type():
    r = get_phi_c(ip=15.0, ic=0.60, e=0.55)
    assert isinstance(r, ShearStrengthResult)
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_np122_indicative_shear_strength.py -v
```
Expected: `ImportError` — module not found.

- [ ] **Step 3: Implement `np122/indicative_shear_strength.py`**

`tabularium/np122/indicative_shear_strength.py`:
```python
from __future__ import annotations

from dataclasses import dataclass

from ..interpolation import interpolate_linear
from ..models import CodeSource, LookupResult

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
    Returnează valorile orientative ale parametrilor de rezistență la forfecare
    (φ', c') conform NP 122:2010, Tabelul A.6.2.

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
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_np122_indicative_shear_strength.py -v
```
Expected: 15 PASSED.

- [ ] **Step 5: Commit**

```bash
git add tabularium/np122/indicative_shear_strength.py tests/test_np122_indicative_shear_strength.py
git commit -m "feat: add NP 122 Tabelul A.6.2 indicative shear strength lookup"
```

---

## Task 5: `registry.py`

**Files:**
- Create: `tabularium/registry.py`
- Create: `tests/test_registry.py`

- [ ] **Step 1: Write failing tests**

`tests/test_registry.py`:
```python
import pytest
from tabularium.registry import TableEntry, get_table, list_tables


def test_list_tables_contains_shear_strength():
    tables = list_tables()
    assert "np122.indicative_shear_strength" in tables


def test_list_tables_returns_list_of_strings():
    tables = list_tables()
    assert isinstance(tables, list)
    assert all(isinstance(k, str) for k in tables)


def test_get_table_returns_entry():
    entry = get_table("np122.indicative_shear_strength")
    assert isinstance(entry, TableEntry)
    assert entry.normative == "NP 122:2010"
    assert entry.table_id == "A.6.2"
    assert callable(entry.lookup_fn)


def test_get_table_lookup_fn_works():
    entry = get_table("np122.indicative_shear_strength")
    r = entry.lookup_fn(ip=15.0, ic=0.60, e=0.55)
    assert r.valid is True


def test_get_table_unknown_key_raises():
    with pytest.raises(KeyError, match="necunoscut"):
        get_table("np999.nonexistent")
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_registry.py -v
```
Expected: `ImportError` — `tabularium.registry` not found.

- [ ] **Step 3: Implement `registry.py`**

`tabularium/registry.py`:
```python
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from .models import LookupResult
from .np122.indicative_shear_strength import get_phi_c as _np122_shear


@dataclass
class TableEntry:
    normative: str
    table_id: str
    description: str
    lookup_fn: Callable[..., LookupResult]


REGISTRY: dict[str, TableEntry] = {
    "np122.indicative_shear_strength": TableEntry(
        normative="NP 122:2010",
        table_id="A.6.2",
        description="Valori orientative φ', c' pentru pământuri coezive (S_r > 0,8)",
        lookup_fn=_np122_shear,
    ),
}


def list_tables() -> list[str]:
    return list(REGISTRY)


def get_table(key: str) -> TableEntry:
    if key not in REGISTRY:
        raise KeyError(
            f"Tabel necunoscut: {key!r}. Disponibile: {list_tables()}"
        )
    return REGISTRY[key]
```

- [ ] **Step 4: Run full test suite**

```bash
pytest -v
```
Expected: all tests PASSED (models + interpolation + shear strength + registry).

- [ ] **Step 5: Commit**

```bash
git add tabularium/registry.py tests/test_registry.py
git commit -m "feat: add registry skeleton with np122 shear strength entry"
```

---

## Final Verification

- [ ] **Run full suite one last time**

```bash
pytest -v --tb=short
```
Expected output: all tests PASSED, zero warnings.

- [ ] **Verify package imports cleanly**

```bash
python -c "
from tabularium.models import CodeSource, LookupResult
from tabularium.interpolation import interpolate_linear
from tabularium.np122.indicative_shear_strength import get_phi_c
from tabularium.registry import list_tables, get_table
print('tables:', list_tables())
r = get_phi_c(ip=15.0, ic=0.60, e=0.60)
print('phi:', r.phi, 'c:', r.c, 'valid:', r.valid)
"
```
Expected:
```
tables: ['np122.indicative_shear_strength']
phi: 18.5 c: 20.0 valid: True
```
