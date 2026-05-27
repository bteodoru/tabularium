# NP 112:2014 Conventional Pressure Tables Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement tabelele D.1–D.5 din NP 112:2014 Anexa D ca 6 module în `src/tabularium/np_112_2014/`, cu lookup + interpolare și result type comun.

**Architecture:** Shared `ConventionalPressureResult(LookupResult)` in `np_112_2014/__init__.py`. Enums extinse în `enums.py`. `interpolate_bilinear` adăugat în `interpolation.py`. Fiecare tabel e un modul separat cu `_SOURCE`, `_TABLE`, și `get_p_conv()`.

**Tech Stack:** Python 3.10+, stdlib `dataclasses`, `bisect`. Test runner: `pytest`.

---

## File Map

| Action | Path |
|---|---|
| Modify | `src/tabularium/enums.py` |
| Modify | `src/tabularium/interpolation.py` |
| Modify | `src/tabularium/np_112_2014/__init__.py` |
| Create | `src/tabularium/np_112_2014/conventional_pressure_rocks.py` |
| Create | `src/tabularium/np_112_2014/conventional_pressure_boulders.py` |
| Create | `src/tabularium/np_112_2014/conventional_pressure_gravels.py` |
| Create | `src/tabularium/np_112_2014/conventional_pressure_sands.py` |
| Create | `src/tabularium/np_112_2014/conventional_pressure_fines.py` |
| Create | `src/tabularium/np_112_2014/conventional_pressure_fills.py` |
| Modify | `src/tabularium/registry.py` |
| Modify | `CLAUDE.md` |
| Modify | `tests/test_interpolation.py` |
| Create | `tests/test_np_112_2014_conventional_pressure_rocks.py` |
| Create | `tests/test_np_112_2014_conventional_pressure_boulders.py` |
| Create | `tests/test_np_112_2014_conventional_pressure_gravels.py` |
| Create | `tests/test_np_112_2014_conventional_pressure_sands.py` |
| Create | `tests/test_np_112_2014_conventional_pressure_fines.py` |
| Create | `tests/test_np_112_2014_conventional_pressure_fills.py` |

---

## Task 1: Enums

**Files:**
- Modify: `src/tabularium/enums.py`

- [ ] **Step 1: Extend `SoilCategory` and add new enums**

Replace the full contents of `src/tabularium/enums.py` with:

```python
from __future__ import annotations

from enum import Enum


class SoilCategory(str, Enum):
    # NP 122:2010 — existente
    GRAVEL_COARSE_SAND        = "gravel_coarse_sand"
    GRAVEL_COARSE_MEDIUM_SAND = "gravel_coarse_medium_sand"
    MEDIUM_SAND               = "medium_sand"
    FINE_SAND                 = "fine_sand"
    SILTY_SAND                = "silty_sand"

    # NP 112:2014 D.1 — roci
    ROCKY                     = "rocky"
    SEMI_ROCKY_MARL           = "semi_rocky_marl"
    SEMI_ROCKY_SHALE          = "semi_rocky_shale"

    # NP 112:2014 D.2 — boulders
    BOULDER_GRAVEL_FILL       = "boulder_gravel_fill"
    BOULDER_CLAY_FILL         = "boulder_clay_fill"

    # NP 112:2014 D.2 — gravels
    GRAVEL_CLEAN_CRYSTAL      = "gravel_clean_crystal"
    GRAVEL_WITH_SAND          = "gravel_with_sand"
    GRAVEL_SEDIMENTARY        = "gravel_sedimentary"
    GRAVEL_SILTY_SAND         = "gravel_silty_sand"

    # NP 112:2014 D.3 — sands
    COARSE_SAND               = "coarse_sand"


class RelativeDensity(str, Enum):
    MEDIUM = "medium"  # I_D = 35…65%
    DENSE  = "dense"   # I_D > 65%


class MoistureCondition(str, Enum):
    DRY        = "dry"
    MOIST      = "moist"
    VERY_MOIST = "very_moist"
    SATURATED  = "saturated"


class PlasticityClass(str, Enum):
    LOW    = "low"    # I_P ≤ 10%
    MEDIUM = "medium" # 10% < I_P ≤ 20%
    HIGH   = "high"   # I_P > 20%


class FillType(str, Enum):
    CONTROLLED_COMPACTED = "controlled_compacted"
    KNOWN_ORIGIN         = "known_origin"


class FillSoilType(str, Enum):
    SANDY_SLAG = "sandy_slag"  # pământuri nisipoase și zguri (fără nisipuri prăfoase)
    SILTY_FINE = "silty_fine"  # nisipuri prăfoase, coezive, cenușe
```

- [ ] **Step 2: Verify existing tests still pass**

```
pytest tests/ -v
```

Expected: all existing tests PASS (enum values for NP 122 unchanged).

- [ ] **Step 3: Commit**

```bash
git add src/tabularium/enums.py
git commit -m "feat(enums): add SoilCategory entries and new enums for NP 112:2014"
```

---

## Task 2: `ConventionalPressureResult` și `interpolate_bilinear`

**Files:**
- Modify: `src/tabularium/np_112_2014/__init__.py`
- Modify: `src/tabularium/interpolation.py`
- Modify: `tests/test_interpolation.py`

- [ ] **Step 1: Write failing tests pentru `interpolate_bilinear`**

Actualizează linia de import din vârful `tests/test_interpolation.py`:

```python
from tabularium.interpolation import BilinearResult, LinearResult, interpolate_bilinear, interpolate_linear
```

Adaugă la sfârșitul aceluiași fișier:

```python


# ── interpolate_bilinear ──────────────────────────────────────────────────────

def test_bilinear_exact_node():
    # grid[x][y] = value; exact match on both axes
    grid = {
        0.5: {0.5: 300.0, 0.75: 325.0},
        0.7: {0.5: 275.0, 0.75: 285.0},
    }
    r = interpolate_bilinear(grid, x=0.5, y=0.5)
    assert r.value == pytest.approx(300.0)
    assert r.interpolated is False
    assert r.warnings == []


def test_bilinear_interpolate_y_only():
    # x exact, y between knots: 0.5*(300+325)/2 not right — linear on y
    # y=0.625 is midpoint of [0.5, 0.75] → (300+325)/2 = 312.5
    grid = {
        0.5: {0.5: 300.0, 0.75: 325.0},
        0.7: {0.5: 275.0, 0.75: 285.0},
    }
    r = interpolate_bilinear(grid, x=0.5, y=0.625)
    assert r.value == pytest.approx(312.5)
    assert r.interpolated is True
    assert r.warnings == []


def test_bilinear_interpolate_x_only():
    # y exact, x between knots
    # x=0.6 is midpoint of [0.5, 0.7], y=0.5 exact
    # → (300+275)/2 = 287.5
    grid = {
        0.5: {0.5: 300.0, 0.75: 325.0},
        0.7: {0.5: 275.0, 0.75: 285.0},
    }
    r = interpolate_bilinear(grid, x=0.6, y=0.5)
    assert r.value == pytest.approx(287.5)
    assert r.interpolated is True


def test_bilinear_interpolate_both_axes():
    # x=0.6 (midpoint [0.5,0.7]), y=0.625 (midpoint [0.5,0.75])
    # At x=0.5, y=0.625 → 312.5
    # At x=0.7, y=0.625 → (275+285)/2 = 280.0
    # At x=0.6 → (312.5+280.0)/2 = 296.25
    grid = {
        0.5: {0.5: 300.0, 0.75: 325.0},
        0.7: {0.5: 275.0, 0.75: 285.0},
    }
    r = interpolate_bilinear(grid, x=0.6, y=0.625)
    assert r.value == pytest.approx(296.25)
    assert r.interpolated is True


def test_bilinear_x_below_range():
    grid = {
        0.5: {0.5: 300.0, 0.75: 325.0},
        0.7: {0.5: 275.0, 0.75: 285.0},
    }
    r = interpolate_bilinear(grid, x=0.3, y=0.6)
    assert r.value is None
    assert len(r.warnings) == 1
    assert "0.5" in r.warnings[0]


def test_bilinear_x_above_range():
    grid = {
        0.5: {0.5: 300.0, 0.75: 325.0},
        0.7: {0.5: 275.0, 0.75: 285.0},
    }
    r = interpolate_bilinear(grid, x=0.9, y=0.6)
    assert r.value is None
    assert len(r.warnings) == 1


def test_bilinear_y_below_range():
    grid = {
        0.5: {0.5: 300.0, 0.75: 325.0},
        0.7: {0.5: 275.0, 0.75: 285.0},
    }
    r = interpolate_bilinear(grid, x=0.6, y=0.3)
    assert r.value is None
    assert len(r.warnings) == 1


def test_bilinear_result_type():
    grid = {0.5: {0.5: 300.0, 0.75: 325.0}, 0.7: {0.5: 275.0, 0.75: 285.0}}
    r = interpolate_bilinear(grid, x=0.5, y=0.5)
    assert isinstance(r, BilinearResult)
```

- [ ] **Step 2: Run tests to verify they fail**

```
pytest tests/test_interpolation.py -v -k "bilinear"
```

Expected: FAIL with `ImportError: cannot import name 'BilinearResult'`

- [ ] **Step 3: Implement `BilinearResult` și `interpolate_bilinear` în `interpolation.py`**

Adaugă după clasa `LinearResult` și `interpolate_linear` la sfârșitul fișierului `src/tabularium/interpolation.py`:

```python

@dataclass
class BilinearResult:
    value: float | None
    interpolated: bool
    warnings: list[str] = field(default_factory=list)


def interpolate_bilinear(
    grid: dict[float, dict[float, float]],
    x: float,
    y: float,
) -> BilinearResult:
    """
    Interpolare biliniară pe o grilă rectangulară grid[x][y] = value.
    Fără extrapolate pe nicio axă.
    """
    x_vals = sorted(grid)

    if x < x_vals[0] - 1e-9:
        return BilinearResult(
            value=None, interpolated=False,
            warnings=[
                f"x = {x} < x_min tabelat ({x_vals[0]}). "
                "Extrapolarea nu este permisă."
            ],
        )
    if x > x_vals[-1] + 1e-9:
        return BilinearResult(
            value=None, interpolated=False,
            warnings=[
                f"x = {x} > x_max tabelat ({x_vals[-1]}). "
                "Extrapolarea nu este permisă."
            ],
        )

    y_ref = sorted(grid[x_vals[0]])
    if y < y_ref[0] - 1e-9:
        return BilinearResult(
            value=None, interpolated=False,
            warnings=[
                f"y = {y} < y_min tabelat ({y_ref[0]}). "
                "Extrapolarea nu este permisă."
            ],
        )
    if y > y_ref[-1] + 1e-9:
        return BilinearResult(
            value=None, interpolated=False,
            warnings=[
                f"y = {y} > y_max tabelat ({y_ref[-1]}). "
                "Extrapolarea nu este permisă."
            ],
        )

    for xv in x_vals:
        if abs(x - xv) < 1e-9:
            lr = interpolate_linear(grid[xv], y)
            return BilinearResult(
                value=lr.value,
                interpolated=lr.interpolated,
                warnings=lr.warnings,
            )

    idx = bisect.bisect_left(x_vals, x)
    x0, x1 = x_vals[idx - 1], x_vals[idx]

    lr0 = interpolate_linear(grid[x0], y)
    lr1 = interpolate_linear(grid[x1], y)

    if lr0.value is None or lr1.value is None:
        return BilinearResult(
            value=None, interpolated=False,
            warnings=lr0.warnings + lr1.warnings,
        )

    t = (x - x0) / (x1 - x0)
    return BilinearResult(
        value=lr0.value + t * (lr1.value - lr0.value),
        interpolated=True,
    )
```

- [ ] **Step 4: Run bilinear tests**

```
pytest tests/test_interpolation.py -v
```

Expected: all tests PASS.

- [ ] **Step 5: Add `ConventionalPressureResult` în `np_112_2014/__init__.py`**

Înlocuiește conținutul fișierului `src/tabularium/np_112_2014/__init__.py`:

```python
from __future__ import annotations

from dataclasses import dataclass

from ..models import LookupResult


@dataclass
class ConventionalPressureResult(LookupResult):
    p_conv: float | None = None
    p_conv_range: tuple[float, float] | None = None

    @property
    def is_resolved(self) -> bool:
        return self.p_conv is not None
```

- [ ] **Step 6: Commit**

```bash
git add src/tabularium/interpolation.py src/tabularium/np_112_2014/__init__.py tests/test_interpolation.py
git commit -m "feat: add interpolate_bilinear and ConventionalPressureResult"
```

---

## Task 3: D.1 — `conventional_pressure_rocks.py`

**Files:**
- Create: `src/tabularium/np_112_2014/conventional_pressure_rocks.py`
- Create: `tests/test_np_112_2014_conventional_pressure_rocks.py`

- [ ] **Step 1: Write failing tests**

Creează `tests/test_np_112_2014_conventional_pressure_rocks.py`:

```python
import pytest
from tabularium.np_112_2014.conventional_pressure_rocks import (
    SoilCategory,
    ConventionalPressureResult,
    get_p_conv,
)


def test_rocky_returns_range():
    r = get_p_conv(SoilCategory.ROCKY)
    assert r.valid is True
    assert r.p_conv is None
    assert r.p_conv_range == (1000.0, 6000.0)
    assert r.is_resolved is False
    assert r.errors == []
    assert len(r.warnings) == 1


def test_semi_rocky_marl_returns_range():
    r = get_p_conv(SoilCategory.SEMI_ROCKY_MARL)
    assert r.valid is True
    assert r.p_conv_range == (350.0, 1100.0)
    assert r.is_resolved is False


def test_semi_rocky_shale_returns_range():
    r = get_p_conv(SoilCategory.SEMI_ROCKY_SHALE)
    assert r.valid is True
    assert r.p_conv_range == (600.0, 850.0)


def test_warning_present():
    r = get_p_conv(SoilCategory.ROCKY)
    assert any("compactit" in w.lower() or "degradare" in w.lower() for w in r.warnings)


def test_source_metadata():
    r = get_p_conv(SoilCategory.ROCKY)
    assert r.source is not None
    assert r.source.code == "NP 112:2014"
    assert r.source.table == "Tabelul D.1"


def test_result_type():
    r = get_p_conv(SoilCategory.ROCKY)
    assert isinstance(r, ConventionalPressureResult)


def test_invalid_category():
    r = get_p_conv("invalid")
    assert r.valid is False
    assert len(r.errors) == 1


def test_non_rocky_category_rejected():
    r = get_p_conv(SoilCategory.FINE_SAND)
    assert r.valid is False
    assert len(r.errors) == 1
```

- [ ] **Step 2: Run to verify fail**

```
pytest tests/test_np_112_2014_conventional_pressure_rocks.py -v
```

Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Implement modul**

Creează `src/tabularium/np_112_2014/conventional_pressure_rocks.py`:

```python
from __future__ import annotations

from ..enums import SoilCategory
from ..models import CodeSource
from . import ConventionalPressureResult

_SOURCE = CodeSource(code="NP 112:2014", table="Tabelul D.1")

_ROCKY_CATEGORIES = {SoilCategory.ROCKY, SoilCategory.SEMI_ROCKY_MARL, SoilCategory.SEMI_ROCKY_SHALE}

_TABLE: dict[SoilCategory, tuple[float, float]] = {
    SoilCategory.ROCKY:           (1000.0, 6000.0),
    SoilCategory.SEMI_ROCKY_MARL: (350.0,  1100.0),
    SoilCategory.SEMI_ROCKY_SHALE:(600.0,   850.0),
}

_WARNING = (
    "Valoarea se alege pe baza compactității și stării de degradare a rocii "
    "stâncoase sau semi-stâncoase. Nu variază cu adâncimea de fundare."
)


def get_p_conv(soil_category: SoilCategory) -> ConventionalPressureResult:
    """
    Returnează intervalul presiunii convenționale de bază p̄_conv [kPa]
    pentru roci stâncoase și semi-stâncoase conform NP 112:2014, Tabelul D.1.
    """
    result = ConventionalPressureResult(source=_SOURCE)

    try:
        soil_category = SoilCategory(soil_category)
    except ValueError:
        result.errors.append(f"Categorie de sol necunoscută: {soil_category!r}.")
        return result

    if soil_category not in _ROCKY_CATEGORIES:
        result.errors.append(
            f"Categoria {soil_category!r} nu aparține Tabelului D.1 (roci). "
            "Folosiți modulul corespunzător categoriei de sol."
        )
        return result

    result.p_conv_range = _TABLE[soil_category]
    result.warnings.append(_WARNING)
    result.valid = True
    return result
```

- [ ] **Step 4: Run tests**

```
pytest tests/test_np_112_2014_conventional_pressure_rocks.py -v
```

Expected: all PASS.

- [ ] **Step 5: Commit**

```bash
git add src/tabularium/np_112_2014/conventional_pressure_rocks.py tests/test_np_112_2014_conventional_pressure_rocks.py
git commit -m "feat(np112): add conventional_pressure_rocks (Tabelul D.1)"
```

---

## Task 4: D.2 — `conventional_pressure_boulders.py`

**Files:**
- Create: `src/tabularium/np_112_2014/conventional_pressure_boulders.py`
- Create: `tests/test_np_112_2014_conventional_pressure_boulders.py`

- [ ] **Step 1: Write failing tests**

Creează `tests/test_np_112_2014_conventional_pressure_boulders.py`:

```python
import pytest
from tabularium.np_112_2014.conventional_pressure_boulders import (
    SoilCategory,
    ConventionalPressureResult,
    get_p_conv,
)


# ── BOULDER_GRAVEL_FILL — fixed value ─────────────────────────────────────────

def test_boulder_gravel_fill_fixed():
    r = get_p_conv(SoilCategory.BOULDER_GRAVEL_FILL)
    assert r.valid is True
    assert r.p_conv == pytest.approx(750.0)
    assert r.p_conv_range is None
    assert r.is_resolved is True
    assert r.errors == []
    assert r.warnings == []


def test_boulder_gravel_fill_ignores_ic():
    r = get_p_conv(SoilCategory.BOULDER_GRAVEL_FILL, consistency_index=0.7)
    assert r.valid is True
    assert r.p_conv == pytest.approx(750.0)


# ── BOULDER_CLAY_FILL — interpolable range ────────────────────────────────────

def test_boulder_clay_fill_no_ic_returns_range():
    r = get_p_conv(SoilCategory.BOULDER_CLAY_FILL)
    assert r.valid is True
    assert r.p_conv is None
    assert r.p_conv_range == (350.0, 600.0)
    assert r.is_resolved is False
    assert len(r.warnings) == 1


def test_boulder_clay_fill_ic_min():
    r = get_p_conv(SoilCategory.BOULDER_CLAY_FILL, consistency_index=0.5)
    assert r.valid is True
    assert r.p_conv == pytest.approx(350.0)
    assert r.interpolated is False


def test_boulder_clay_fill_ic_max():
    r = get_p_conv(SoilCategory.BOULDER_CLAY_FILL, consistency_index=1.0)
    assert r.valid is True
    assert r.p_conv == pytest.approx(600.0)
    assert r.interpolated is False


def test_boulder_clay_fill_ic_interpolated():
    # IC=0.75 is midpoint of [0.5, 1.0] → 350 + 0.5*(600-350) = 475
    r = get_p_conv(SoilCategory.BOULDER_CLAY_FILL, consistency_index=0.75)
    assert r.valid is True
    assert r.p_conv == pytest.approx(475.0)
    assert r.interpolated is True


def test_boulder_clay_fill_ic_below_range():
    r = get_p_conv(SoilCategory.BOULDER_CLAY_FILL, consistency_index=0.3)
    assert r.valid is False
    assert len(r.errors) == 1


def test_boulder_clay_fill_ic_above_range():
    r = get_p_conv(SoilCategory.BOULDER_CLAY_FILL, consistency_index=1.1)
    assert r.valid is False
    assert len(r.errors) == 1


def test_source_metadata():
    r = get_p_conv(SoilCategory.BOULDER_GRAVEL_FILL)
    assert r.source.code == "NP 112:2014"
    assert r.source.table == "Tabelul D.2"


def test_result_type():
    r = get_p_conv(SoilCategory.BOULDER_GRAVEL_FILL)
    assert isinstance(r, ConventionalPressureResult)


def test_invalid_category():
    r = get_p_conv("invalid")
    assert r.valid is False
    assert len(r.errors) == 1


def test_non_boulder_category_rejected():
    r = get_p_conv(SoilCategory.FINE_SAND)
    assert r.valid is False
    assert len(r.errors) == 1
```

- [ ] **Step 2: Run to verify fail**

```
pytest tests/test_np_112_2014_conventional_pressure_boulders.py -v
```

Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Implement modul**

Creează `src/tabularium/np_112_2014/conventional_pressure_boulders.py`:

```python
from __future__ import annotations

from ..enums import SoilCategory
from ..interpolation import interpolate_linear
from ..models import CodeSource
from . import ConventionalPressureResult

_SOURCE = CodeSource(code="NP 112:2014", table="Tabelul D.2")

_BOULDER_CATEGORIES = {SoilCategory.BOULDER_GRAVEL_FILL, SoilCategory.BOULDER_CLAY_FILL}

_FIXED: dict[SoilCategory, float] = {
    SoilCategory.BOULDER_GRAVEL_FILL: 750.0,
}

# Noduri pentru interpolare pe I_C: {I_C: p_conv}
_INTERPOLABLE: dict[SoilCategory, dict[float, float]] = {
    SoilCategory.BOULDER_CLAY_FILL: {0.5: 350.0, 1.0: 600.0},
}

_IC_RANGE_WARNING = "Furnizați consistency_index (I_C) pentru a rezolva valoarea exactă."


def get_p_conv(
    soil_category: SoilCategory,
    consistency_index: float | None = None,
) -> ConventionalPressureResult:
    """
    Returnează p̄_conv [kPa] pentru pământuri foarte grosiere
    conform NP 112:2014, Tabelul D.2.

    consistency_index (I_C) necesar doar pentru BOULDER_CLAY_FILL.
    """
    result = ConventionalPressureResult(source=_SOURCE)

    try:
        soil_category = SoilCategory(soil_category)
    except ValueError:
        result.errors.append(f"Categorie de sol necunoscută: {soil_category!r}.")
        return result

    if soil_category not in _BOULDER_CATEGORIES:
        result.errors.append(
            f"Categoria {soil_category!r} nu aparține Tabelului D.2 (boulders). "
            "Folosiți modulul corespunzător categoriei de sol."
        )
        return result

    if soil_category in _FIXED:
        result.p_conv = _FIXED[soil_category]
        result.valid = True
        return result

    # Range interpolabil
    knots = _INTERPOLABLE[soil_category]
    ic_min, ic_max = min(knots), max(knots)

    if consistency_index is None:
        result.p_conv_range = (knots[ic_min], knots[ic_max])
        result.warnings.append(_IC_RANGE_WARNING)
        result.valid = True
        return result

    if consistency_index < ic_min or consistency_index > ic_max:
        result.errors.append(
            f"consistency_index = {consistency_index} este în afara domeniului "
            f"[{ic_min}, {ic_max}] pentru {soil_category!r}."
        )
        return result

    lr = interpolate_linear(knots, consistency_index)
    result.p_conv = lr.value
    result.interpolated = lr.interpolated
    result.valid = True
    return result
```

- [ ] **Step 4: Run tests**

```
pytest tests/test_np_112_2014_conventional_pressure_boulders.py -v
```

Expected: all PASS.

- [ ] **Step 5: Commit**

```bash
git add src/tabularium/np_112_2014/conventional_pressure_boulders.py tests/test_np_112_2014_conventional_pressure_boulders.py
git commit -m "feat(np112): add conventional_pressure_boulders (Tabelul D.2)"
```

---

## Task 5: D.2 — `conventional_pressure_gravels.py`

**Files:**
- Create: `src/tabularium/np_112_2014/conventional_pressure_gravels.py`
- Create: `tests/test_np_112_2014_conventional_pressure_gravels.py`

- [ ] **Step 1: Write failing tests**

Creează `tests/test_np_112_2014_conventional_pressure_gravels.py`:

```python
import pytest
from tabularium.np_112_2014.conventional_pressure_gravels import (
    SoilCategory,
    ConventionalPressureResult,
    get_p_conv,
)


def test_gravel_clean_crystal():
    r = get_p_conv(SoilCategory.GRAVEL_CLEAN_CRYSTAL)
    assert r.valid is True
    assert r.p_conv == pytest.approx(600.0)
    assert r.p_conv_range is None
    assert r.errors == []


def test_gravel_with_sand():
    r = get_p_conv(SoilCategory.GRAVEL_WITH_SAND)
    assert r.valid is True
    assert r.p_conv == pytest.approx(550.0)


def test_gravel_sedimentary():
    r = get_p_conv(SoilCategory.GRAVEL_SEDIMENTARY)
    assert r.valid is True
    assert r.p_conv == pytest.approx(350.0)


def test_gravel_silty_sand_no_ic_returns_range():
    r = get_p_conv(SoilCategory.GRAVEL_SILTY_SAND)
    assert r.valid is True
    assert r.p_conv is None
    assert r.p_conv_range == (350.0, 500.0)
    assert len(r.warnings) == 1


def test_gravel_silty_sand_ic_min():
    r = get_p_conv(SoilCategory.GRAVEL_SILTY_SAND, consistency_index=0.5)
    assert r.valid is True
    assert r.p_conv == pytest.approx(350.0)
    assert r.interpolated is False


def test_gravel_silty_sand_ic_max():
    r = get_p_conv(SoilCategory.GRAVEL_SILTY_SAND, consistency_index=1.0)
    assert r.valid is True
    assert r.p_conv == pytest.approx(500.0)
    assert r.interpolated is False


def test_gravel_silty_sand_ic_interpolated():
    # IC=0.75 midpoint [0.5, 1.0] → 350 + 0.5*150 = 425
    r = get_p_conv(SoilCategory.GRAVEL_SILTY_SAND, consistency_index=0.75)
    assert r.valid is True
    assert r.p_conv == pytest.approx(425.0)
    assert r.interpolated is True


def test_gravel_silty_sand_ic_out_of_range():
    r = get_p_conv(SoilCategory.GRAVEL_SILTY_SAND, consistency_index=0.2)
    assert r.valid is False
    assert len(r.errors) == 1


def test_source_metadata():
    r = get_p_conv(SoilCategory.GRAVEL_WITH_SAND)
    assert r.source.code == "NP 112:2014"
    assert r.source.table == "Tabelul D.2"


def test_invalid_category():
    r = get_p_conv("invalid")
    assert r.valid is False
    assert len(r.errors) == 1


def test_non_gravel_category_rejected():
    r = get_p_conv(SoilCategory.ROCKY)
    assert r.valid is False
    assert len(r.errors) == 1
```

- [ ] **Step 2: Run to verify fail**

```
pytest tests/test_np_112_2014_conventional_pressure_gravels.py -v
```

Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Implement modul**

Creează `src/tabularium/np_112_2014/conventional_pressure_gravels.py`:

```python
from __future__ import annotations

from ..enums import SoilCategory
from ..interpolation import interpolate_linear
from ..models import CodeSource
from . import ConventionalPressureResult

_SOURCE = CodeSource(code="NP 112:2014", table="Tabelul D.2")

_GRAVEL_CATEGORIES = {
    SoilCategory.GRAVEL_CLEAN_CRYSTAL,
    SoilCategory.GRAVEL_WITH_SAND,
    SoilCategory.GRAVEL_SEDIMENTARY,
    SoilCategory.GRAVEL_SILTY_SAND,
}

_FIXED: dict[SoilCategory, float] = {
    SoilCategory.GRAVEL_CLEAN_CRYSTAL: 600.0,
    SoilCategory.GRAVEL_WITH_SAND:     550.0,
    SoilCategory.GRAVEL_SEDIMENTARY:   350.0,
}

_INTERPOLABLE: dict[SoilCategory, dict[float, float]] = {
    SoilCategory.GRAVEL_SILTY_SAND: {0.5: 350.0, 1.0: 500.0},
}

_IC_RANGE_WARNING = "Furnizați consistency_index (I_C) pentru a rezolva valoarea exactă."


def get_p_conv(
    soil_category: SoilCategory,
    consistency_index: float | None = None,
) -> ConventionalPressureResult:
    """
    Returnează p̄_conv [kPa] pentru pământuri grosiere (pietrișuri)
    conform NP 112:2014, Tabelul D.2.

    consistency_index (I_C) necesar doar pentru GRAVEL_SILTY_SAND.
    """
    result = ConventionalPressureResult(source=_SOURCE)

    try:
        soil_category = SoilCategory(soil_category)
    except ValueError:
        result.errors.append(f"Categorie de sol necunoscută: {soil_category!r}.")
        return result

    if soil_category not in _GRAVEL_CATEGORIES:
        result.errors.append(
            f"Categoria {soil_category!r} nu aparține Tabelului D.2 (gravels). "
            "Folosiți modulul corespunzător categoriei de sol."
        )
        return result

    if soil_category in _FIXED:
        result.p_conv = _FIXED[soil_category]
        result.valid = True
        return result

    knots = _INTERPOLABLE[soil_category]
    ic_min, ic_max = min(knots), max(knots)

    if consistency_index is None:
        result.p_conv_range = (knots[ic_min], knots[ic_max])
        result.warnings.append(_IC_RANGE_WARNING)
        result.valid = True
        return result

    if consistency_index < ic_min or consistency_index > ic_max:
        result.errors.append(
            f"consistency_index = {consistency_index} este în afara domeniului "
            f"[{ic_min}, {ic_max}] pentru {soil_category!r}."
        )
        return result

    lr = interpolate_linear(knots, consistency_index)
    result.p_conv = lr.value
    result.interpolated = lr.interpolated
    result.valid = True
    return result
```

- [ ] **Step 4: Run tests**

```
pytest tests/test_np_112_2014_conventional_pressure_gravels.py -v
```

Expected: all PASS.

- [ ] **Step 5: Commit**

```bash
git add src/tabularium/np_112_2014/conventional_pressure_gravels.py tests/test_np_112_2014_conventional_pressure_gravels.py
git commit -m "feat(np112): add conventional_pressure_gravels (Tabelul D.2)"
```

---

## Task 6: D.3 — `conventional_pressure_sands.py`

**Files:**
- Create: `src/tabularium/np_112_2014/conventional_pressure_sands.py`
- Create: `tests/test_np_112_2014_conventional_pressure_sands.py`

- [ ] **Step 1: Write failing tests**

Creează `tests/test_np_112_2014_conventional_pressure_sands.py`:

```python
import pytest
from tabularium.np_112_2014.conventional_pressure_sands import (
    SoilCategory,
    RelativeDensity,
    MoistureCondition,
    ConventionalPressureResult,
    get_p_conv,
)


# ── Exact lookups ─────────────────────────────────────────────────────────────

def test_coarse_sand_dense():
    r = get_p_conv(SoilCategory.COARSE_SAND, RelativeDensity.DENSE, MoistureCondition.DRY)
    assert r.valid is True
    assert r.p_conv == pytest.approx(700.0)
    assert r.errors == []
    assert r.warnings == []


def test_coarse_sand_medium():
    r = get_p_conv(SoilCategory.COARSE_SAND, RelativeDensity.MEDIUM, MoistureCondition.SATURATED)
    assert r.valid is True
    assert r.p_conv == pytest.approx(600.0)


def test_medium_sand_dense():
    r = get_p_conv(SoilCategory.MEDIUM_SAND, RelativeDensity.DENSE, MoistureCondition.MOIST)
    assert r.valid is True
    assert r.p_conv == pytest.approx(600.0)


def test_medium_sand_medium():
    r = get_p_conv(SoilCategory.MEDIUM_SAND, RelativeDensity.MEDIUM, MoistureCondition.DRY)
    assert r.valid is True
    assert r.p_conv == pytest.approx(500.0)


def test_fine_sand_dry_dense():
    r = get_p_conv(SoilCategory.FINE_SAND, RelativeDensity.DENSE, MoistureCondition.DRY)
    assert r.valid is True
    assert r.p_conv == pytest.approx(500.0)


def test_fine_sand_moist_medium():
    r = get_p_conv(SoilCategory.FINE_SAND, RelativeDensity.MEDIUM, MoistureCondition.MOIST)
    assert r.valid is True
    assert r.p_conv == pytest.approx(350.0)


def test_fine_sand_very_moist_dense():
    r = get_p_conv(SoilCategory.FINE_SAND, RelativeDensity.DENSE, MoistureCondition.VERY_MOIST)
    assert r.valid is True
    assert r.p_conv == pytest.approx(350.0)


def test_fine_sand_saturated_medium():
    r = get_p_conv(SoilCategory.FINE_SAND, RelativeDensity.MEDIUM, MoistureCondition.SATURATED)
    assert r.valid is True
    assert r.p_conv == pytest.approx(250.0)


def test_silty_sand_dry_dense():
    r = get_p_conv(SoilCategory.SILTY_SAND, RelativeDensity.DENSE, MoistureCondition.DRY)
    assert r.valid is True
    assert r.p_conv == pytest.approx(350.0)


def test_silty_sand_moist_medium():
    r = get_p_conv(SoilCategory.SILTY_SAND, RelativeDensity.MEDIUM, MoistureCondition.MOIST)
    assert r.valid is True
    assert r.p_conv == pytest.approx(200.0)


def test_silty_sand_very_moist_dense():
    r = get_p_conv(SoilCategory.SILTY_SAND, RelativeDensity.DENSE, MoistureCondition.VERY_MOIST)
    assert r.valid is True
    assert r.p_conv == pytest.approx(200.0)


def test_silty_sand_saturated_medium():
    r = get_p_conv(SoilCategory.SILTY_SAND, RelativeDensity.MEDIUM, MoistureCondition.SATURATED)
    assert r.valid is True
    assert r.p_conv == pytest.approx(150.0)


# ── Source & type ─────────────────────────────────────────────────────────────

def test_source_metadata():
    r = get_p_conv(SoilCategory.COARSE_SAND, RelativeDensity.DENSE, MoistureCondition.DRY)
    assert r.source.code == "NP 112:2014"
    assert r.source.table == "Tabelul D.3"


def test_result_type():
    r = get_p_conv(SoilCategory.COARSE_SAND, RelativeDensity.DENSE, MoistureCondition.DRY)
    assert isinstance(r, ConventionalPressureResult)


# ── Error cases ───────────────────────────────────────────────────────────────

def test_invalid_category():
    r = get_p_conv("invalid", RelativeDensity.DENSE, MoistureCondition.DRY)
    assert r.valid is False
    assert len(r.errors) == 1


def test_invalid_relative_density():
    r = get_p_conv(SoilCategory.COARSE_SAND, "invalid", MoistureCondition.DRY)
    assert r.valid is False
    assert len(r.errors) == 1


def test_invalid_moisture_condition():
    r = get_p_conv(SoilCategory.FINE_SAND, RelativeDensity.DENSE, "invalid")
    assert r.valid is False
    assert len(r.errors) == 1


def test_non_sand_category_rejected():
    r = get_p_conv(SoilCategory.ROCKY, RelativeDensity.DENSE, MoistureCondition.DRY)
    assert r.valid is False
    assert len(r.errors) == 1
```

- [ ] **Step 2: Run to verify fail**

```
pytest tests/test_np_112_2014_conventional_pressure_sands.py -v
```

Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Implement modul**

Creează `src/tabularium/np_112_2014/conventional_pressure_sands.py`:

```python
from __future__ import annotations

from ..enums import MoistureCondition, RelativeDensity, SoilCategory
from ..models import CodeSource
from . import ConventionalPressureResult

_SOURCE = CodeSource(code="NP 112:2014", table="Tabelul D.3")

_SAND_CATEGORIES = {
    SoilCategory.COARSE_SAND,
    SoilCategory.MEDIUM_SAND,
    SoilCategory.FINE_SAND,
    SoilCategory.SILTY_SAND,
}

# Categorii fără diferențiere pe umiditate: orice MoistureCondition e acceptat
_MOISTURE_INDEPENDENT = {SoilCategory.COARSE_SAND, SoilCategory.MEDIUM_SAND}

# _TABLE[(SoilCategory, MoistureCondition | None)][RelativeDensity] = p_conv
# None ca cheie de umiditate = indiferent de umiditate
_TABLE: dict[tuple[SoilCategory, MoistureCondition | None], dict[RelativeDensity, float]] = {
    (SoilCategory.COARSE_SAND, None): {
        RelativeDensity.DENSE:  700.0,
        RelativeDensity.MEDIUM: 600.0,
    },
    (SoilCategory.MEDIUM_SAND, None): {
        RelativeDensity.DENSE:  600.0,
        RelativeDensity.MEDIUM: 500.0,
    },
    (SoilCategory.FINE_SAND, MoistureCondition.DRY): {
        RelativeDensity.DENSE:  500.0,
        RelativeDensity.MEDIUM: 350.0,
    },
    (SoilCategory.FINE_SAND, MoistureCondition.MOIST): {
        RelativeDensity.DENSE:  500.0,
        RelativeDensity.MEDIUM: 350.0,
    },
    (SoilCategory.FINE_SAND, MoistureCondition.VERY_MOIST): {
        RelativeDensity.DENSE:  350.0,
        RelativeDensity.MEDIUM: 250.0,
    },
    (SoilCategory.FINE_SAND, MoistureCondition.SATURATED): {
        RelativeDensity.DENSE:  350.0,
        RelativeDensity.MEDIUM: 250.0,
    },
    (SoilCategory.SILTY_SAND, MoistureCondition.DRY): {
        RelativeDensity.DENSE:  350.0,
        RelativeDensity.MEDIUM: 300.0,
    },
    (SoilCategory.SILTY_SAND, MoistureCondition.MOIST): {
        RelativeDensity.DENSE:  250.0,
        RelativeDensity.MEDIUM: 200.0,
    },
    (SoilCategory.SILTY_SAND, MoistureCondition.VERY_MOIST): {
        RelativeDensity.DENSE:  200.0,
        RelativeDensity.MEDIUM: 150.0,
    },
    (SoilCategory.SILTY_SAND, MoistureCondition.SATURATED): {
        RelativeDensity.DENSE:  200.0,
        RelativeDensity.MEDIUM: 150.0,
    },
}


def get_p_conv(
    soil_category: SoilCategory,
    relative_density: RelativeDensity,
    moisture_condition: MoistureCondition,
) -> ConventionalPressureResult:
    """
    Returnează p̄_conv [kPa] pentru nisipuri conform NP 112:2014, Tabelul D.3.

    Pentru COARSE_SAND și MEDIUM_SAND, moisture_condition este acceptat
    dar nu influențează valoarea (tabelul are un singur rând per categorie).
    """
    result = ConventionalPressureResult(source=_SOURCE)

    try:
        soil_category     = SoilCategory(soil_category)
        relative_density  = RelativeDensity(relative_density)
        moisture_condition = MoistureCondition(moisture_condition)
    except ValueError as exc:
        result.errors.append(f"Valoare necunoscută: {exc}.")
        return result

    if soil_category not in _SAND_CATEGORIES:
        result.errors.append(
            f"Categoria {soil_category!r} nu aparține Tabelului D.3 (nisipuri). "
            "Folosiți modulul corespunzător categoriei de sol."
        )
        return result

    key_moisture = None if soil_category in _MOISTURE_INDEPENDENT else moisture_condition
    row = _TABLE.get((soil_category, key_moisture))

    if row is None:
        result.errors.append(
            f"Combinație inexistentă în tabel: {soil_category!r} + {moisture_condition!r}."
        )
        return result

    result.p_conv = row[relative_density]
    result.valid = True
    return result
```

- [ ] **Step 4: Run tests**

```
pytest tests/test_np_112_2014_conventional_pressure_sands.py -v
```

Expected: all PASS.

- [ ] **Step 5: Commit**

```bash
git add src/tabularium/np_112_2014/conventional_pressure_sands.py tests/test_np_112_2014_conventional_pressure_sands.py
git commit -m "feat(np112): add conventional_pressure_sands (Tabelul D.3)"
```

---

## Task 7: D.4 — `conventional_pressure_fines.py`

**Files:**
- Create: `src/tabularium/np_112_2014/conventional_pressure_fines.py`
- Create: `tests/test_np_112_2014_conventional_pressure_fines.py`

- [ ] **Step 1: Write failing tests**

Creează `tests/test_np_112_2014_conventional_pressure_fines.py`:

```python
import pytest
from tabularium.np_112_2014.conventional_pressure_fines import (
    PlasticityClass,
    ConventionalPressureResult,
    get_p_conv,
)


# ── Exact node lookups ────────────────────────────────────────────────────────

def test_low_plasticity_exact_node_upper_band():
    # LOW, e=0.5, IC=0.75 → exact node in upper band → 325
    r = get_p_conv(PlasticityClass.LOW, void_ratio=0.5, consistency_index=0.75)
    assert r.valid is True
    assert r.p_conv == pytest.approx(325.0)
    assert r.interpolated is False
    assert r.errors == []


def test_low_plasticity_exact_node_ic_1():
    # LOW, e=0.7, IC=1.0 → exact node → 300
    r = get_p_conv(PlasticityClass.LOW, void_ratio=0.7, consistency_index=1.0)
    assert r.valid is True
    assert r.p_conv == pytest.approx(300.0)
    assert r.interpolated is False


def test_low_plasticity_exact_node_lower_band():
    # LOW, e=0.5, IC=0.5 → exact node in lower band → 300
    r = get_p_conv(PlasticityClass.LOW, void_ratio=0.5, consistency_index=0.5)
    assert r.valid is True
    assert r.p_conv == pytest.approx(300.0)
    assert r.interpolated is False


def test_high_plasticity_exact_node():
    # HIGH, e=0.6, IC=1.0 → 525
    r = get_p_conv(PlasticityClass.HIGH, void_ratio=0.6, consistency_index=1.0)
    assert r.valid is True
    assert r.p_conv == pytest.approx(525.0)


# ── Band boundary: IC=0.75 goes to upper band ─────────────────────────────────

def test_ic_0_75_uses_upper_band():
    # LOW, e=0.5, IC=0.75 → upper band, exact node → 325 (not lower band which also has 325 here)
    r = get_p_conv(PlasticityClass.LOW, void_ratio=0.5, consistency_index=0.75)
    assert r.valid is True
    assert r.p_conv == pytest.approx(325.0)
    assert r.interpolated is False


# ── Bilinear interpolation ────────────────────────────────────────────────────

def test_low_plasticity_interpolate_e_only():
    # LOW, e=0.6 (midpoint [0.5,0.7]), IC=0.75 exact
    # upper band: e=0.5→325, e=0.7→285; at e=0.6 → (325+285)/2 = 305
    r = get_p_conv(PlasticityClass.LOW, void_ratio=0.6, consistency_index=0.75)
    assert r.valid is True
    assert r.p_conv == pytest.approx(305.0)
    assert r.interpolated is True


def test_low_plasticity_interpolate_ic_only():
    # LOW, e=0.5 exact, IC=0.875 (midpoint [0.75,1.0])
    # upper band e=0.5: IC=0.75→325, IC=1.0→350; at IC=0.875 → (325+350)/2 = 337.5
    r = get_p_conv(PlasticityClass.LOW, void_ratio=0.5, consistency_index=0.875)
    assert r.valid is True
    assert r.p_conv == pytest.approx(337.5)
    assert r.interpolated is True


def test_medium_plasticity_bilinear():
    # MEDIUM, upper band, e=0.6 (midpoint [0.5,0.7]), IC=0.875 (midpoint [0.75,1.0])
    # At e=0.5, IC=0.875 → (325+350)/2 = 337.5
    # At e=0.7, IC=0.875 → (285+300)/2 = 292.5
    # At e=0.6 → (337.5+292.5)/2 = 315.0
    r = get_p_conv(PlasticityClass.MEDIUM, void_ratio=0.6, consistency_index=0.875)
    assert r.valid is True
    assert r.p_conv == pytest.approx(315.0)
    assert r.interpolated is True


# ── Out-of-range ──────────────────────────────────────────────────────────────

def test_ic_below_range():
    r = get_p_conv(PlasticityClass.LOW, void_ratio=0.5, consistency_index=0.3)
    assert r.valid is False
    assert len(r.errors) == 1


def test_ic_above_range():
    r = get_p_conv(PlasticityClass.LOW, void_ratio=0.5, consistency_index=1.1)
    assert r.valid is False
    assert len(r.errors) == 1


def test_e_above_limit_low():
    # LOW: e_max = 0.7
    r = get_p_conv(PlasticityClass.LOW, void_ratio=0.8, consistency_index=0.8)
    assert r.valid is False
    assert len(r.errors) == 1


def test_e_below_minimum():
    r = get_p_conv(PlasticityClass.LOW, void_ratio=0.3, consistency_index=0.8)
    assert r.valid is False
    assert len(r.errors) == 1


def test_e_at_limit_high():
    # HIGH: e_max = 1.1, e=1.1 is a data point → should be valid
    r = get_p_conv(PlasticityClass.HIGH, void_ratio=1.1, consistency_index=1.0)
    assert r.valid is True
    assert r.p_conv == pytest.approx(300.0)


# ── Source & type ─────────────────────────────────────────────────────────────

def test_source_metadata():
    r = get_p_conv(PlasticityClass.LOW, void_ratio=0.5, consistency_index=0.75)
    assert r.source.code == "NP 112:2014"
    assert r.source.table == "Tabelul D.4"


def test_result_type():
    r = get_p_conv(PlasticityClass.LOW, void_ratio=0.5, consistency_index=0.75)
    assert isinstance(r, ConventionalPressureResult)


def test_invalid_plasticity_class():
    r = get_p_conv("invalid", void_ratio=0.5, consistency_index=0.75)
    assert r.valid is False
    assert len(r.errors) == 1
```

- [ ] **Step 2: Run to verify fail**

```
pytest tests/test_np_112_2014_conventional_pressure_fines.py -v
```

Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Implement modul**

Creează `src/tabularium/np_112_2014/conventional_pressure_fines.py`:

```python
from __future__ import annotations

from ..enums import PlasticityClass
from ..interpolation import interpolate_bilinear
from ..models import CodeSource
from . import ConventionalPressureResult

_SOURCE = CodeSource(code="NP 112:2014", table="Tabelul D.4")

# grid[e][I_C] = p_conv
_SubGrid = dict[float, dict[float, float]]

# _TABLE[PlasticityClass]["lower" | "upper"][e][I_C] = p_conv
# "lower": I_C ∈ [0.5, 0.75)   "upper": I_C ∈ [0.75, 1.0]
_TABLE: dict[PlasticityClass, dict[str, _SubGrid]] = {
    PlasticityClass.LOW: {
        "lower": {
            0.5: {0.50: 300.0, 0.75: 325.0},
            0.7: {0.50: 275.0, 0.75: 285.0},
        },
        "upper": {
            0.5: {0.75: 325.0, 1.00: 350.0},
            0.7: {0.75: 285.0, 1.00: 300.0},
        },
    },
    PlasticityClass.MEDIUM: {
        "lower": {
            0.5: {0.50: 300.0, 0.75: 325.0},
            0.7: {0.50: 275.0, 0.75: 285.0},
            1.0: {0.50: 200.0, 0.75: 225.0},
        },
        "upper": {
            0.5: {0.75: 325.0, 1.00: 350.0},
            0.7: {0.75: 285.0, 1.00: 300.0},
            1.0: {0.75: 225.0, 1.00: 250.0},
        },
    },
    PlasticityClass.HIGH: {
        "lower": {
            0.5: {0.50: 550.0, 0.75: 600.0},
            0.6: {0.50: 450.0, 0.75: 485.0},
            0.8: {0.50: 300.0, 0.75: 325.0},
            1.1: {0.50: 225.0, 0.75: 260.0},
        },
        "upper": {
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


def get_p_conv(
    plasticity_class: PlasticityClass,
    void_ratio: float,
    consistency_index: float,
) -> ConventionalPressureResult:
    """
    Returnează p̄_conv [kPa] pentru pământuri fine coezive
    conform NP 112:2014, Tabelul D.4.

    Interpolare biliniară pe (void_ratio = e, consistency_index = I_C)
    în interiorul benzii de I_C selectate. Nu se interpolează cross-bandă.
    """
    result = ConventionalPressureResult(source=_SOURCE)

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

    band = "upper" if consistency_index >= _IC_BAND_BOUNDARY else "lower"
    grid = _TABLE[plasticity_class][band]

    br = interpolate_bilinear(grid, x=void_ratio, y=consistency_index)

    if br.value is None:
        result.errors.extend(br.warnings)
        return result

    result.p_conv = br.value
    result.interpolated = br.interpolated
    result.valid = True
    return result
```

- [ ] **Step 4: Run tests**

```
pytest tests/test_np_112_2014_conventional_pressure_fines.py -v
```

Expected: all PASS.

- [ ] **Step 5: Commit**

```bash
git add src/tabularium/np_112_2014/conventional_pressure_fines.py tests/test_np_112_2014_conventional_pressure_fines.py
git commit -m "feat(np112): add conventional_pressure_fines (Tabelul D.4)"
```

---

## Task 8: D.5 — `conventional_pressure_fills.py`

**Files:**
- Create: `src/tabularium/np_112_2014/conventional_pressure_fills.py`
- Create: `tests/test_np_112_2014_conventional_pressure_fills.py`

- [ ] **Step 1: Write failing tests**

Creează `tests/test_np_112_2014_conventional_pressure_fills.py`:

```python
import pytest
from tabularium.np_112_2014.conventional_pressure_fills import (
    FillType,
    FillSoilType,
    ConventionalPressureResult,
    get_p_conv,
)


# ── Exact lookups la noduri (Sr ≤ 0.5 și Sr ≥ 0.8) ──────────────────────────

def test_controlled_sandy_sr_low():
    r = get_p_conv(FillType.CONTROLLED_COMPACTED, FillSoilType.SANDY_SLAG, saturation_degree=0.3)
    assert r.valid is True
    assert r.p_conv == pytest.approx(250.0)
    assert r.interpolated is False
    assert r.errors == []


def test_controlled_sandy_sr_high():
    r = get_p_conv(FillType.CONTROLLED_COMPACTED, FillSoilType.SANDY_SLAG, saturation_degree=0.9)
    assert r.valid is True
    assert r.p_conv == pytest.approx(200.0)
    assert r.interpolated is False


def test_controlled_silty_sr_low():
    r = get_p_conv(FillType.CONTROLLED_COMPACTED, FillSoilType.SILTY_FINE, saturation_degree=0.2)
    assert r.valid is True
    assert r.p_conv == pytest.approx(180.0)


def test_controlled_silty_sr_high():
    r = get_p_conv(FillType.CONTROLLED_COMPACTED, FillSoilType.SILTY_FINE, saturation_degree=1.0)
    assert r.valid is True
    assert r.p_conv == pytest.approx(150.0)


def test_known_origin_sandy_sr_low():
    r = get_p_conv(FillType.KNOWN_ORIGIN, FillSoilType.SANDY_SLAG, saturation_degree=0.0)
    assert r.valid is True
    assert r.p_conv == pytest.approx(180.0)


def test_known_origin_silty_sr_high():
    r = get_p_conv(FillType.KNOWN_ORIGIN, FillSoilType.SILTY_FINE, saturation_degree=0.8)
    assert r.valid is True
    assert r.p_conv == pytest.approx(100.0)
    assert r.interpolated is False


# ── Interpolation ─────────────────────────────────────────────────────────────

def test_controlled_sandy_sr_midpoint():
    # Sr=0.65 midpoint [0.5, 0.8] → (250+200)/2 = 225
    r = get_p_conv(FillType.CONTROLLED_COMPACTED, FillSoilType.SANDY_SLAG, saturation_degree=0.65)
    assert r.valid is True
    assert r.p_conv == pytest.approx(225.0)
    assert r.interpolated is True


def test_known_origin_silty_interpolated():
    # Sr=0.65 midpoint [0.5, 0.8] → (120+100)/2 = 110
    r = get_p_conv(FillType.KNOWN_ORIGIN, FillSoilType.SILTY_FINE, saturation_degree=0.65)
    assert r.valid is True
    assert r.p_conv == pytest.approx(110.0)
    assert r.interpolated is True


def test_sr_at_lower_node():
    # Sr=0.5 exact node
    r = get_p_conv(FillType.CONTROLLED_COMPACTED, FillSoilType.SANDY_SLAG, saturation_degree=0.5)
    assert r.valid is True
    assert r.p_conv == pytest.approx(250.0)
    assert r.interpolated is False


def test_sr_at_upper_node():
    # Sr=0.8 exact node
    r = get_p_conv(FillType.CONTROLLED_COMPACTED, FillSoilType.SANDY_SLAG, saturation_degree=0.8)
    assert r.valid is True
    assert r.p_conv == pytest.approx(200.0)
    assert r.interpolated is False


# ── Out-of-range Sr ───────────────────────────────────────────────────────────

def test_sr_negative():
    r = get_p_conv(FillType.CONTROLLED_COMPACTED, FillSoilType.SANDY_SLAG, saturation_degree=-0.1)
    assert r.valid is False
    assert len(r.errors) == 1


def test_sr_above_one():
    r = get_p_conv(FillType.CONTROLLED_COMPACTED, FillSoilType.SANDY_SLAG, saturation_degree=1.1)
    assert r.valid is False
    assert len(r.errors) == 1


# ── Source & type ─────────────────────────────────────────────────────────────

def test_source_metadata():
    r = get_p_conv(FillType.CONTROLLED_COMPACTED, FillSoilType.SANDY_SLAG, saturation_degree=0.3)
    assert r.source.code == "NP 112:2014"
    assert r.source.table == "Tabelul D.5"


def test_result_type():
    r = get_p_conv(FillType.CONTROLLED_COMPACTED, FillSoilType.SANDY_SLAG, saturation_degree=0.3)
    assert isinstance(r, ConventionalPressureResult)


def test_invalid_fill_type():
    r = get_p_conv("invalid", FillSoilType.SANDY_SLAG, saturation_degree=0.3)
    assert r.valid is False
    assert len(r.errors) == 1


def test_invalid_fill_soil_type():
    r = get_p_conv(FillType.CONTROLLED_COMPACTED, "invalid", saturation_degree=0.3)
    assert r.valid is False
    assert len(r.errors) == 1
```

- [ ] **Step 2: Run to verify fail**

```
pytest tests/test_np_112_2014_conventional_pressure_fills.py -v
```

Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Implement modul**

Creează `src/tabularium/np_112_2014/conventional_pressure_fills.py`:

```python
from __future__ import annotations

from ..enums import FillSoilType, FillType
from ..interpolation import interpolate_linear
from ..models import CodeSource
from . import ConventionalPressureResult

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

_SR_MIN = 0.0
_SR_MAX = 1.0
_SR_NODE_LOW  = 0.5
_SR_NODE_HIGH = 0.8


def get_p_conv(
    fill_type: FillType,
    fill_soil_type: FillSoilType,
    saturation_degree: float,
) -> ConventionalPressureResult:
    """
    Returnează p̄_conv [kPa] pentru umpluturi conform NP 112:2014, Tabelul D.5.

    Interpolare liniară pe S_r ∈ [0.5, 0.8].
    S_r < 0.5 → valoarea nodului 0.5; S_r > 0.8 → valoarea nodului 0.8.
    S_r în afara [0, 1] → eroare.
    """
    result = ConventionalPressureResult(source=_SOURCE)

    try:
        fill_type      = FillType(fill_type)
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
```

- [ ] **Step 4: Run tests**

```
pytest tests/test_np_112_2014_conventional_pressure_fills.py -v
```

Expected: all PASS.

- [ ] **Step 5: Commit**

```bash
git add src/tabularium/np_112_2014/conventional_pressure_fills.py tests/test_np_112_2014_conventional_pressure_fills.py
git commit -m "feat(np112): add conventional_pressure_fills (Tabelul D.5)"
```

---

## Task 9: Registry + CLAUDE.md

**Files:**
- Modify: `src/tabularium/registry.py`
- Modify: `CLAUDE.md`

- [ ] **Step 1: Adaugă intrările în registry**

În `src/tabularium/registry.py`, adaugă importurile după cele existente:

```python
from .np_112_2014.conventional_pressure_rocks import get_p_conv as _np112_rocks
from .np_112_2014.conventional_pressure_boulders import get_p_conv as _np112_boulders
from .np_112_2014.conventional_pressure_gravels import get_p_conv as _np112_gravels
from .np_112_2014.conventional_pressure_sands import get_p_conv as _np112_sands
from .np_112_2014.conventional_pressure_fines import get_p_conv as _np112_fines
from .np_112_2014.conventional_pressure_fills import get_p_conv as _np112_fills
```

Adaugă în dicționarul `REGISTRY`:

```python
    "np_112_2014.conventional_pressure_rocks": TableEntry(
        normative="NP 112:2014",
        table_id="D.1",
        description="Presiuni convenționale p̄_conv [kPa] pentru roci stâncoase și semi-stâncoase",
        lookup_fn=_np112_rocks,
    ),
    "np_112_2014.conventional_pressure_boulders": TableEntry(
        normative="NP 112:2014",
        table_id="D.2",
        description="Presiuni convenționale p̄_conv [kPa] pentru pământuri foarte grosiere",
        lookup_fn=_np112_boulders,
    ),
    "np_112_2014.conventional_pressure_gravels": TableEntry(
        normative="NP 112:2014",
        table_id="D.2",
        description="Presiuni convenționale p̄_conv [kPa] pentru pământuri grosiere (pietrișuri)",
        lookup_fn=_np112_gravels,
    ),
    "np_112_2014.conventional_pressure_sands": TableEntry(
        normative="NP 112:2014",
        table_id="D.3",
        description="Presiuni convenționale p̄_conv [kPa] pentru nisipuri",
        lookup_fn=_np112_sands,
    ),
    "np_112_2014.conventional_pressure_fines": TableEntry(
        normative="NP 112:2014",
        table_id="D.4",
        description="Presiuni convenționale p̄_conv [kPa] pentru pământuri fine coezive",
        lookup_fn=_np112_fines,
    ),
    "np_112_2014.conventional_pressure_fills": TableEntry(
        normative="NP 112:2014",
        table_id="D.5",
        description="Presiuni convenționale p̄_conv [kPa] pentru umpluturi",
        lookup_fn=_np112_fills,
    ),
```

- [ ] **Step 2: Verifică registry**

```
pytest tests/test_registry.py -v
```

Expected: PASS (testele existente nu se schimbă).

- [ ] **Step 3: Actualizează CLAUDE.md**

În secțiunea "Package structure" din `CLAUDE.md`, înlocuiește blocul `np_112_2014/` cu:

```
├── np_112_2014/
│   ├── __init__.py                          # ConventionalPressureResult
│   ├── conventional_pressure_rocks.py       # Tabelul D.1 — roci stâncoase și semi-stâncoase
│   ├── conventional_pressure_boulders.py    # Tabelul D.2 — pământuri foarte grosiere
│   ├── conventional_pressure_gravels.py     # Tabelul D.2 — pământuri grosiere (pietrișuri)
│   ├── conventional_pressure_sands.py       # Tabelul D.3 — nisipuri
│   ├── conventional_pressure_fines.py       # Tabelul D.4 — pământuri fine coezive
│   └── conventional_pressure_fills.py       # Tabelul D.5 — umpluturi
```

Actualizează și secțiunea `tests/`:

```
├── test_np_112_2014_conventional_pressure_rocks.py
├── test_np_112_2014_conventional_pressure_boulders.py
├── test_np_112_2014_conventional_pressure_gravels.py
├── test_np_112_2014_conventional_pressure_sands.py
├── test_np_112_2014_conventional_pressure_fines.py
└── test_np_112_2014_conventional_pressure_fills.py
```

- [ ] **Step 4: Rulează toate testele**

```
pytest tests/ -v
```

Expected: toate PASS.

- [ ] **Step 5: Commit final**

```bash
git add src/tabularium/registry.py CLAUDE.md
git commit -m "feat(registry): register NP 112:2014 conventional pressure tables D.1–D.5"
```
