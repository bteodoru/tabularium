# Indicative Deformation Modulus Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement two lookup modules for NP 122:2010 — `indicative_deformation_modulus_non_cohesive` (Tabelul A.6.3) and `indicative_deformation_modulus_cohesive` (Tabelul A.6.4) — with tests and registry entries.

**Architecture:** Each module defines a `*Result(LookupResult)` dataclass, a hardcoded `_TABLE` dict, and a public `get_deformation_modulus()` function. Non-cohesive is a pure enum-keyed category lookup; cohesive mirrors `indicative_shear_strength` — categorical on IP/IC, linear interpolation on void ratio `e` via `interpolate_linear()`. Both are registered in `registry.py`.

**Tech Stack:** Python ≥ 3.10, dataclasses (stdlib), pytest, `tabularium.interpolation.interpolate_linear`, `tabularium.models.CodeSource` / `LookupResult`.

**Spec:** `docs/superpowers/specs/2026-05-21-indicative-deformation-modulus-design.md`

**Reference implementation:** `src/tabularium/np122/indicative_shear_strength.py` and its tests.

---

## File Map

| Action | Path | Responsibility |
|--------|------|---------------|
| Create | `src/tabularium/np122/indicative_deformation_modulus_non_cohesive.py` | Enums, table, lookup for A.6.3 |
| Create | `src/tabularium/np122/indicative_deformation_modulus_cohesive.py` | Table, IC/IP classification, interpolation for A.6.4 |
| Create | `tests/test_np122_indicative_deformation_modulus_non_cohesive.py` | Tests for A.6.3 |
| Create | `tests/test_np122_indicative_deformation_modulus_cohesive.py` | Tests for A.6.4 |
| Modify | `src/tabularium/registry.py` | Add two new `TableEntry` entries |
| Modify | `CLAUDE.md` | Update package structure section |

---

## Task 1: Non-cohesive module skeleton (A.6.3)

**Files:**
- Create: `src/tabularium/np122/indicative_deformation_modulus_non_cohesive.py`
- Create: `tests/test_np122_indicative_deformation_modulus_non_cohesive.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_np122_indicative_deformation_modulus_non_cohesive.py`:

```python
import pytest
from tabularium.np122.indicative_deformation_modulus_non_cohesive import (
    DeformationModulusNonCohesiveResult,
    RelativeDensity,
    SoilCategory,
    get_deformation_modulus,
)


def test_gravel_coarse_medium_sand_medium():
    r = get_deformation_modulus(SoilCategory.GRAVEL_COARSE_MEDIUM_SAND, RelativeDensity.MEDIUM)
    assert r.valid is True
    assert r.interpolated is False
    assert r.e_modulus == pytest.approx(30_000.0)
    assert r.errors == []
    assert r.warnings == []


def test_gravel_coarse_medium_sand_dense():
    r = get_deformation_modulus(SoilCategory.GRAVEL_COARSE_MEDIUM_SAND, RelativeDensity.DENSE)
    assert r.valid is True
    assert r.e_modulus == pytest.approx(40_000.0)


def test_fine_sand_medium():
    r = get_deformation_modulus(SoilCategory.FINE_SAND, RelativeDensity.MEDIUM)
    assert r.valid is True
    assert r.e_modulus == pytest.approx(25_000.0)


def test_fine_sand_dense():
    r = get_deformation_modulus(SoilCategory.FINE_SAND, RelativeDensity.DENSE)
    assert r.valid is True
    assert r.e_modulus == pytest.approx(35_000.0)


def test_silty_sand_medium():
    r = get_deformation_modulus(SoilCategory.SILTY_SAND, RelativeDensity.MEDIUM)
    assert r.valid is True
    assert r.e_modulus == pytest.approx(18_000.0)


def test_silty_sand_dense():
    r = get_deformation_modulus(SoilCategory.SILTY_SAND, RelativeDensity.DENSE)
    assert r.valid is True
    assert r.e_modulus == pytest.approx(30_000.0)


def test_source_metadata():
    r = get_deformation_modulus(SoilCategory.FINE_SAND, RelativeDensity.MEDIUM)
    assert r.source is not None
    assert r.source.code == "NP 122:2010"
    assert r.source.table == "Tabelul A.6.3"


def test_result_type():
    r = get_deformation_modulus(SoilCategory.SILTY_SAND, RelativeDensity.DENSE)
    assert isinstance(r, DeformationModulusNonCohesiveResult)
```

- [ ] **Step 2: Run test to confirm it fails**

```bash
pytest tests/test_np122_indicative_deformation_modulus_non_cohesive.py -v
```

Expected: `ModuleNotFoundError` or `ImportError` — module does not exist yet.

- [ ] **Step 3: Implement the module**

Create `src/tabularium/np122/indicative_deformation_modulus_non_cohesive.py`:

```python
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from ..models import CodeSource, LookupResult

_SOURCE = CodeSource(code="NP 122:2010", table="Tabelul A.6.3")


class SoilCategory(str, Enum):
    GRAVEL_COARSE_MEDIUM_SAND = "gravel_coarse_medium_sand"
    FINE_SAND = "fine_sand"
    SILTY_SAND = "silty_sand"


class RelativeDensity(str, Enum):
    MEDIUM = "medium"  # I_D = 35…65%
    DENSE  = "dense"   # I_D > 65%


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
```

- [ ] **Step 4: Run tests to verify they all pass**

```bash
pytest tests/test_np122_indicative_deformation_modulus_non_cohesive.py -v
```

Expected: 8 tests PASSED.

- [ ] **Step 5: Commit**

```bash
git add src/tabularium/np122/indicative_deformation_modulus_non_cohesive.py \
        tests/test_np122_indicative_deformation_modulus_non_cohesive.py
git commit -m "feat(np122): add indicative_deformation_modulus_non_cohesive (A.6.3)"
```

---

## Task 2: Cohesive module skeleton (A.6.4)

**Files:**
- Create: `src/tabularium/np122/indicative_deformation_modulus_cohesive.py`
- Create: `tests/test_np122_indicative_deformation_modulus_cohesive.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_np122_indicative_deformation_modulus_cohesive.py`:

```python
import pytest
from tabularium.np122.indicative_deformation_modulus_cohesive import (
    DeformationModulusCohesiveResult,
    get_deformation_modulus,
)


# ── Exact lookup ──────────────────────────────────────────────────────────────

def test_exact_ip_lt10_e045():
    # IP <10, IC 0.25-1.00, e=0.45 (exact tabulated value)
    r = get_deformation_modulus(ip=7.0, ic=0.80, e=0.45)
    assert r.valid is True
    assert r.interpolated is False
    assert r.e_modulus == pytest.approx(32_000.0)
    assert r.ip_category == "<10"
    assert r.ic_range == "0.25-1.00"
    assert r.e_lower == pytest.approx(0.45)
    assert r.e_upper == pytest.approx(0.45)
    assert r.errors == []
    assert r.warnings == []


def test_exact_ip_10_20_ic_075_e055():
    # IP 10-20, IC 0.75-1.00, e=0.55 (exact)
    r = get_deformation_modulus(ip=15.0, ic=0.80, e=0.55)
    assert r.valid is True
    assert r.interpolated is False
    assert r.e_modulus == pytest.approx(27_000.0)
    assert r.ip_category == "10-20"
    assert r.ic_range == "0.75-1.00"


def test_exact_ip_10_20_ic_050_e075():
    # IP 10-20, IC 0.50-0.75, e=0.75 (exact)
    r = get_deformation_modulus(ip=15.0, ic=0.60, e=0.75)
    assert r.valid is True
    assert r.interpolated is False
    assert r.e_modulus == pytest.approx(14_000.0)
    assert r.ic_range == "0.50-0.75"


def test_exact_ip_gt20_ic_075_e105():
    # IP >20, IC 0.75-1.00, e=1.05 (exact, boundary)
    r = get_deformation_modulus(ip=25.0, ic=0.80, e=1.05)
    assert r.valid is True
    assert r.interpolated is False
    assert r.e_modulus == pytest.approx(12_000.0)
    assert r.ip_category == ">20"


def test_exact_ip_gt20_ic_050_e065():
    # IP >20, IC 0.50-0.75, e=0.65 (exact)
    r = get_deformation_modulus(ip=25.0, ic=0.60, e=0.65)
    assert r.valid is True
    assert r.interpolated is False
    assert r.e_modulus == pytest.approx(21_000.0)
    assert r.ic_range == "0.50-0.75"


# ── Interpolated lookup ───────────────────────────────────────────────────────

def test_interpolated_ip_lt10_midpoint():
    # IP <10, IC 0.25-1.00, e=0.50 (between 0.45→32000 and 0.55→24000)
    # t = (0.50-0.45)/(0.55-0.45) = 0.5
    # E = 32000 + 0.5*(24000-32000) = 28000
    r = get_deformation_modulus(ip=7.0, ic=0.80, e=0.50)
    assert r.valid is True
    assert r.interpolated is True
    assert r.e_modulus == pytest.approx(28_000.0)
    assert r.e_lower == pytest.approx(0.45)
    assert r.e_upper == pytest.approx(0.55)


def test_interpolated_ip_10_20_ic_075():
    # IP 10-20, IC 0.75-1.00, e=0.70 (between 0.65→22000 and 0.75→17000)
    # t = (0.70-0.65)/(0.75-0.65) = 0.5
    # E = 22000 + 0.5*(17000-22000) = 19500
    r = get_deformation_modulus(ip=15.0, ic=0.80, e=0.70)
    assert r.valid is True
    assert r.interpolated is True
    assert r.e_modulus == pytest.approx(19_500.0)


def test_interpolated_ip_gt20_ic_050():
    # IP >20, IC 0.50-0.75, e=0.70 (between 0.65→21000 and 0.75→18000)
    # t = (0.70-0.65)/(0.75-0.65) = 0.5
    # E = 21000 + 0.5*(18000-21000) = 19500
    r = get_deformation_modulus(ip=25.0, ic=0.60, e=0.70)
    assert r.valid is True
    assert r.interpolated is True
    assert r.e_modulus == pytest.approx(19_500.0)


# ── IP boundaries ─────────────────────────────────────────────────────────────

def test_ip_exactly_10():
    r = get_deformation_modulus(ip=10.0, ic=0.80, e=0.45)
    assert r.ip_category == "10-20"
    assert r.valid is True
    assert r.e_modulus == pytest.approx(34_000.0)


def test_ip_exactly_20():
    r = get_deformation_modulus(ip=20.0, ic=0.80, e=0.45)
    assert r.ip_category == "10-20"
    assert r.valid is True


def test_ip_just_above_20():
    r = get_deformation_modulus(ip=20.1, ic=0.80, e=0.55)
    assert r.ip_category == ">20"
    assert r.valid is True


# ── Out-of-range errors ───────────────────────────────────────────────────────

def test_ic_below_025_ip_lt10():
    r = get_deformation_modulus(ip=7.0, ic=0.20, e=0.65)
    assert r.valid is False
    assert len(r.errors) == 1


def test_ic_below_050_ip_10_20():
    r = get_deformation_modulus(ip=15.0, ic=0.40, e=0.65)
    assert r.valid is False
    assert len(r.errors) == 1


def test_ic_below_050_ip_gt20():
    r = get_deformation_modulus(ip=25.0, ic=0.40, e=0.65)
    assert r.valid is False
    assert len(r.errors) == 1


def test_e_below_minimum_for_row():
    # IP >20, IC 0.75-1.00: e_min = 0.55; e=0.45 → error
    r = get_deformation_modulus(ip=25.0, ic=0.80, e=0.45)
    assert r.valid is False
    assert len(r.errors) == 1


def test_e_above_maximum_for_row():
    # IP <10, IC 0.25-1.00: e_max = 0.85; e=0.95 → error
    r = get_deformation_modulus(ip=7.0, ic=0.80, e=0.95)
    assert r.valid is False
    assert len(r.errors) == 1


# ── IC > 1.0 warning ─────────────────────────────────────────────────────────

def test_ic_above_1_warning_ip_lt10():
    # IC > 1.0 for IP <10: warning, still valid, use "0.25-1.00"
    r = get_deformation_modulus(ip=7.0, ic=1.10, e=0.65)
    assert r.valid is True
    assert len(r.warnings) == 1
    assert r.ic_range == "0.25-1.00"


def test_ic_above_1_warning_ip_10_20():
    # IC > 1.0 for IP 10-20: warning, use "0.75-1.00" conservatively
    r = get_deformation_modulus(ip=15.0, ic=1.10, e=0.65)
    assert r.valid is True
    assert len(r.warnings) == 1
    assert r.ic_range == "0.75-1.00"


# ── Source metadata ───────────────────────────────────────────────────────────

def test_source_metadata():
    r = get_deformation_modulus(ip=15.0, ic=0.80, e=0.55)
    assert r.source is not None
    assert r.source.code == "NP 122:2010"
    assert r.source.table == "Tabelul A.6.4"


def test_result_type():
    r = get_deformation_modulus(ip=15.0, ic=0.80, e=0.55)
    assert isinstance(r, DeformationModulusCohesiveResult)
```

- [ ] **Step 2: Run test to confirm it fails**

```bash
pytest tests/test_np122_indicative_deformation_modulus_cohesive.py -v
```

Expected: `ModuleNotFoundError` — module does not exist yet.

- [ ] **Step 3: Implement the module**

Create `src/tabularium/np122/indicative_deformation_modulus_cohesive.py`:

```python
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
```

- [ ] **Step 4: Run tests to verify they all pass**

```bash
pytest tests/test_np122_indicative_deformation_modulus_cohesive.py -v
```

Expected: 20 tests PASSED.

- [ ] **Step 5: Commit**

```bash
git add src/tabularium/np122/indicative_deformation_modulus_cohesive.py \
        tests/test_np122_indicative_deformation_modulus_cohesive.py
git commit -m "feat(np122): add indicative_deformation_modulus_cohesive (A.6.4)"
```

---

## Task 3: Registry entries

**Files:**
- Modify: `src/tabularium/registry.py`

- [ ] **Step 1: Write failing tests for registry**

`tests/test_registry.py` already exists with shear-strength tests. **Append** the following tests to it (do not overwrite):

```python
from tabularium.np122.indicative_deformation_modulus_non_cohesive import (
    RelativeDensity,
    SoilCategory,
)


def test_registry_has_non_cohesive_deformation_modulus():
    assert "np122.indicative_deformation_modulus_non_cohesive" in REGISTRY


def test_registry_has_cohesive_deformation_modulus():
    assert "np122.indicative_deformation_modulus_cohesive" in REGISTRY


def test_registry_non_cohesive_entry_metadata():
    entry = get_table("np122.indicative_deformation_modulus_non_cohesive")
    assert entry.normative == "NP 122:2010"
    assert entry.table_id == "A.6.3"
    assert callable(entry.lookup_fn)


def test_registry_cohesive_entry_metadata():
    entry = get_table("np122.indicative_deformation_modulus_cohesive")
    assert entry.normative == "NP 122:2010"
    assert entry.table_id == "A.6.4"
    assert callable(entry.lookup_fn)


def test_registry_cohesive_lookup_fn_works():
    # Cohesive lookup_fn accepts (ip, ic, e) keyword args
    entry = get_table("np122.indicative_deformation_modulus_cohesive")
    r = entry.lookup_fn(ip=15.0, ic=0.80, e=0.55)
    assert r.valid is True


def test_registry_non_cohesive_lookup_fn_works():
    # Non-cohesive lookup_fn requires SoilCategory and RelativeDensity enum args
    entry = get_table("np122.indicative_deformation_modulus_non_cohesive")
    r = entry.lookup_fn(SoilCategory.FINE_SAND, RelativeDensity.MEDIUM)
    assert r.valid is True
```

Note: the `REGISTRY` and `get_table` imports are already at the top of `test_registry.py`. Only the new `SoilCategory` / `RelativeDensity` import and the six new test functions need to be appended.

- [ ] **Step 2: Run test to confirm it fails**

```bash
pytest tests/test_registry.py::test_registry_has_non_cohesive_deformation_modulus \
       tests/test_registry.py::test_registry_has_cohesive_deformation_modulus -v
```

Expected: FAILED — keys not present yet.

- [ ] **Step 3: Add entries to registry**

Open `src/tabularium/registry.py`. Add the two new imports and entries:

```python
from .np122.indicative_deformation_modulus_non_cohesive import (
    get_deformation_modulus as _np122_deformation_non_cohesive,
)
from .np122.indicative_deformation_modulus_cohesive import (
    get_deformation_modulus as _np122_deformation_cohesive,
)
```

Then add to `REGISTRY`:

```python
    "np122.indicative_deformation_modulus_non_cohesive": TableEntry(
        normative="NP 122:2010",
        table_id="A.6.3",
        description="Valori caracteristice E (kPa) pentru pământuri nisipoase",
        lookup_fn=_np122_deformation_non_cohesive,
    ),
    "np122.indicative_deformation_modulus_cohesive": TableEntry(
        normative="NP 122:2010",
        table_id="A.6.4",
        description="Valori caracteristice E (kPa) pentru pământuri coezive",
        lookup_fn=_np122_deformation_cohesive,
    ),
```

- [ ] **Step 4: Run all registry tests**

```bash
pytest tests/test_registry.py -v
```

Expected: all PASSED (including any pre-existing registry tests).

- [ ] **Step 5: Run full test suite to check for regressions**

```bash
pytest -v
```

Expected: all PASSED.

- [ ] **Step 6: Commit**

```bash
git add src/tabularium/registry.py tests/test_registry.py
git commit -m "feat(registry): register indicative deformation modulus tables (A.6.3, A.6.4)"
```

---

## Task 4: CLAUDE.md update

**Files:**
- Modify: `CLAUDE.md`

- [ ] **Step 1: Update package structure section**

In `CLAUDE.md`, find the package structure block and add the two new files under `np122/`:

```
├── np122/
│   ├── __init__.py
│   ├── indicative_shear_strength.py
│   ├── indicative_deformation_modulus_non_cohesive.py
│   └── indicative_deformation_modulus_cohesive.py
```

Also update the tests listing:

```
tests/
├── test_models.py
├── test_interpolation.py
├── test_np122_indicative_shear_strength.py
├── test_np122_indicative_deformation_modulus_non_cohesive.py
├── test_np122_indicative_deformation_modulus_cohesive.py
└── test_registry.py
```

- [ ] **Step 2: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: update package structure in CLAUDE.md"
```
