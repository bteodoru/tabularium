# NP 112:2014 Presumed Bearing Pressure Tables Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement tabelele D.1–D.5 din NP 112:2014 Anexa D ca 6 module în `src/tabularium/np_112_2014/`, expunând presiunile convenționale (presumed bearing pressure) cu lookup + interpolare și result type comun.

**Architecture:** Shared `PresumedBearingPressureResult(LookupResult)` in `np_112_2014/__init__.py`. Enums extinse în `enums.py`. D.4 folosește două apeluri succesive `interpolate_linear` (existent) pe axele `e` și `I_C` — nu e nevoie de o funcție nouă. Fiecare tabel e un modul separat cu `_SOURCE`, `_TABLE`, și `get_presumed_bearing_pressure()`.

**Tech Stack:** Python 3.10+, stdlib `dataclasses`, `bisect`. Test runner: `pytest`.

---

## File Map

| Action | Path |
|---|---|
| Modify | `src/tabularium/enums.py` |
| Modify | `src/tabularium/np_112_2014/__init__.py` |
| Create | `src/tabularium/np_112_2014/presumed_bearing_pressure_rocks.py` |
| Create | `src/tabularium/np_112_2014/presumed_bearing_pressure_boulders.py` |
| Create | `src/tabularium/np_112_2014/presumed_bearing_pressure_gravels.py` |
| Create | `src/tabularium/np_112_2014/presumed_bearing_pressure_sands.py` |
| Create | `src/tabularium/np_112_2014/presumed_bearing_pressure_fines.py` |
| Create | `src/tabularium/np_112_2014/presumed_bearing_pressure_fills.py` |
| Modify | `src/tabularium/registry.py` |
| Modify | `CLAUDE.md` |
| Create | `tests/test_np_112_2014_presumed_bearing_pressure_rocks.py` |
| Create | `tests/test_np_112_2014_presumed_bearing_pressure_boulders.py` |
| Create | `tests/test_np_112_2014_presumed_bearing_pressure_gravels.py` |
| Create | `tests/test_np_112_2014_presumed_bearing_pressure_sands.py` |
| Create | `tests/test_np_112_2014_presumed_bearing_pressure_fines.py` |
| Create | `tests/test_np_112_2014_presumed_bearing_pressure_fills.py` |

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

## Task 2: `PresumedBearingPressureResult`

**Files:**
- Modify: `src/tabularium/np_112_2014/__init__.py`

- [ ] **Step 1: Add `PresumedBearingPressureResult` în `np_112_2014/__init__.py`**

Înlocuiește conținutul fișierului `src/tabularium/np_112_2014/__init__.py`:

```python
from __future__ import annotations

from dataclasses import dataclass

from ..models import LookupResult


@dataclass
class PresumedBearingPressureResult(LookupResult):
    p_conv: float | None = None
    p_conv_range: tuple[float, float] | None = None

    @property
    def is_resolved(self) -> bool:
        return self.p_conv is not None
```

- [ ] **Step 2: Verifică testele existente**

```
pytest tests/ -v
```

Expected: toate testele existente PASS (nicio modificare la NP 122).

- [ ] **Step 3: Commit**

```bash
git add src/tabularium/np_112_2014/__init__.py
git commit -m "feat(np112): add PresumedBearingPressureResult"
```

---

## Task 3: D.1 — `presumed_bearing_pressure_rocks.py`

**Files:**
- Create: `src/tabularium/np_112_2014/presumed_bearing_pressure_rocks.py`
- Create: `tests/test_np_112_2014_presumed_bearing_pressure_rocks.py`

- [ ] **Step 1: Write failing tests**

Creează `tests/test_np_112_2014_presumed_bearing_pressure_rocks.py`:

```python
import pytest
from tabularium.np_112_2014.presumed_bearing_pressure_rocks import (
    SoilCategory,
    PresumedBearingPressureResult,
    get_presumed_bearing_pressure,
)


def test_rocky_returns_range():
    r = get_presumed_bearing_pressure(SoilCategory.ROCKY)
    assert r.valid is True
    assert r.p_conv is None
    assert r.p_conv_range == (1000.0, 6000.0)
    assert r.is_resolved is False
    assert r.errors == []
    assert len(r.warnings) == 1


def test_semi_rocky_marl_returns_range():
    r = get_presumed_bearing_pressure(SoilCategory.SEMI_ROCKY_MARL)
    assert r.valid is True
    assert r.p_conv_range == (350.0, 1100.0)
    assert r.is_resolved is False


def test_semi_rocky_shale_returns_range():
    r = get_presumed_bearing_pressure(SoilCategory.SEMI_ROCKY_SHALE)
    assert r.valid is True
    assert r.p_conv_range == (600.0, 850.0)


def test_warning_present():
    r = get_presumed_bearing_pressure(SoilCategory.ROCKY)
    assert any("compactit" in w.lower() or "degradare" in w.lower() for w in r.warnings)


def test_source_metadata():
    r = get_presumed_bearing_pressure(SoilCategory.ROCKY)
    assert r.source is not None
    assert r.source.code == "NP 112:2014"
    assert r.source.table == "Tabelul D.1"


def test_result_type():
    r = get_presumed_bearing_pressure(SoilCategory.ROCKY)
    assert isinstance(r, PresumedBearingPressureResult)


def test_invalid_category():
    r = get_presumed_bearing_pressure("invalid")
    assert r.valid is False
    assert len(r.errors) == 1


def test_non_rocky_category_rejected():
    r = get_presumed_bearing_pressure(SoilCategory.FINE_SAND)
    assert r.valid is False
    assert len(r.errors) == 1
```

- [ ] **Step 2: Run to verify fail**

```
pytest tests/test_np_112_2014_presumed_bearing_pressure_rocks.py -v
```

Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Implement modul**

Creează `src/tabularium/np_112_2014/presumed_bearing_pressure_rocks.py`:

```python
from __future__ import annotations

from ..enums import SoilCategory
from ..models import CodeSource
from . import PresumedBearingPressureResult

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


def get_presumed_bearing_pressure(soil_category: SoilCategory) -> PresumedBearingPressureResult:
    """
    Returnează intervalul presiunii convenționale de bază p̄_conv [kPa]
    pentru roci stâncoase și semi-stâncoase conform NP 112:2014, Tabelul D.1.
    """
    result = PresumedBearingPressureResult(source=_SOURCE)

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
pytest tests/test_np_112_2014_presumed_bearing_pressure_rocks.py -v
```

Expected: all PASS.

- [ ] **Step 5: Commit**

```bash
git add src/tabularium/np_112_2014/presumed_bearing_pressure_rocks.py tests/test_np_112_2014_presumed_bearing_pressure_rocks.py
git commit -m "feat(np112): add presumed_bearing_pressure_rocks (Tabelul D.1)"
```

---

## Task 4: D.2 — `presumed_bearing_pressure_boulders.py`

**Files:**
- Create: `src/tabularium/np_112_2014/presumed_bearing_pressure_boulders.py`
- Create: `tests/test_np_112_2014_presumed_bearing_pressure_boulders.py`

- [ ] **Step 1: Write failing tests**

Creează `tests/test_np_112_2014_presumed_bearing_pressure_boulders.py`:

```python
import pytest
from tabularium.np_112_2014.presumed_bearing_pressure_boulders import (
    SoilCategory,
    PresumedBearingPressureResult,
    get_presumed_bearing_pressure,
)


# ── BOULDER_GRAVEL_FILL — fixed value ─────────────────────────────────────────

def test_boulder_gravel_fill_fixed():
    r = get_presumed_bearing_pressure(SoilCategory.BOULDER_GRAVEL_FILL)
    assert r.valid is True
    assert r.p_conv == pytest.approx(750.0)
    assert r.p_conv_range is None
    assert r.is_resolved is True
    assert r.errors == []
    assert r.warnings == []


def test_boulder_gravel_fill_ignores_ic():
    r = get_presumed_bearing_pressure(SoilCategory.BOULDER_GRAVEL_FILL, consistency_index=0.7)
    assert r.valid is True
    assert r.p_conv == pytest.approx(750.0)


# ── BOULDER_CLAY_FILL — interpolable range ────────────────────────────────────

def test_boulder_clay_fill_no_ic_returns_range():
    r = get_presumed_bearing_pressure(SoilCategory.BOULDER_CLAY_FILL)
    assert r.valid is True
    assert r.p_conv is None
    assert r.p_conv_range == (350.0, 600.0)
    assert r.is_resolved is False
    assert len(r.warnings) == 1


def test_boulder_clay_fill_ic_min():
    r = get_presumed_bearing_pressure(SoilCategory.BOULDER_CLAY_FILL, consistency_index=0.5)
    assert r.valid is True
    assert r.p_conv == pytest.approx(350.0)
    assert r.interpolated is False


def test_boulder_clay_fill_ic_max():
    r = get_presumed_bearing_pressure(SoilCategory.BOULDER_CLAY_FILL, consistency_index=1.0)
    assert r.valid is True
    assert r.p_conv == pytest.approx(600.0)
    assert r.interpolated is False


def test_boulder_clay_fill_ic_interpolated():
    # IC=0.75 is midpoint of [0.5, 1.0] → 350 + 0.5*(600-350) = 475
    r = get_presumed_bearing_pressure(SoilCategory.BOULDER_CLAY_FILL, consistency_index=0.75)
    assert r.valid is True
    assert r.p_conv == pytest.approx(475.0)
    assert r.interpolated is True


def test_boulder_clay_fill_ic_below_range():
    r = get_presumed_bearing_pressure(SoilCategory.BOULDER_CLAY_FILL, consistency_index=0.3)
    assert r.valid is False
    assert len(r.errors) == 1


def test_boulder_clay_fill_ic_above_range():
    r = get_presumed_bearing_pressure(SoilCategory.BOULDER_CLAY_FILL, consistency_index=1.1)
    assert r.valid is False
    assert len(r.errors) == 1


def test_source_metadata():
    r = get_presumed_bearing_pressure(SoilCategory.BOULDER_GRAVEL_FILL)
    assert r.source.code == "NP 112:2014"
    assert r.source.table == "Tabelul D.2"


def test_result_type():
    r = get_presumed_bearing_pressure(SoilCategory.BOULDER_GRAVEL_FILL)
    assert isinstance(r, PresumedBearingPressureResult)


def test_invalid_category():
    r = get_presumed_bearing_pressure("invalid")
    assert r.valid is False
    assert len(r.errors) == 1


def test_non_boulder_category_rejected():
    r = get_presumed_bearing_pressure(SoilCategory.FINE_SAND)
    assert r.valid is False
    assert len(r.errors) == 1
```

- [ ] **Step 2: Run to verify fail**

```
pytest tests/test_np_112_2014_presumed_bearing_pressure_boulders.py -v
```

Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Implement modul**

Creează `src/tabularium/np_112_2014/presumed_bearing_pressure_boulders.py`:

```python
from __future__ import annotations

from ..enums import SoilCategory
from ..interpolation import interpolate_linear
from ..models import CodeSource
from . import PresumedBearingPressureResult

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


def get_presumed_bearing_pressure(
    soil_category: SoilCategory,
    consistency_index: float | None = None,
) -> PresumedBearingPressureResult:
    """
    Returnează p̄_conv [kPa] pentru pământuri foarte grosiere
    conform NP 112:2014, Tabelul D.2.

    consistency_index (I_C) necesar doar pentru BOULDER_CLAY_FILL.
    """
    result = PresumedBearingPressureResult(source=_SOURCE)

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
pytest tests/test_np_112_2014_presumed_bearing_pressure_boulders.py -v
```

Expected: all PASS.

- [ ] **Step 5: Commit**

```bash
git add src/tabularium/np_112_2014/presumed_bearing_pressure_boulders.py tests/test_np_112_2014_presumed_bearing_pressure_boulders.py
git commit -m "feat(np112): add presumed_bearing_pressure_boulders (Tabelul D.2)"
```

---

## Task 5: D.2 — `presumed_bearing_pressure_gravels.py`

**Files:**
- Create: `src/tabularium/np_112_2014/presumed_bearing_pressure_gravels.py`
- Create: `tests/test_np_112_2014_presumed_bearing_pressure_gravels.py`

- [ ] **Step 1: Write failing tests**

Creează `tests/test_np_112_2014_presumed_bearing_pressure_gravels.py`:

```python
import pytest
from tabularium.np_112_2014.presumed_bearing_pressure_gravels import (
    SoilCategory,
    PresumedBearingPressureResult,
    get_presumed_bearing_pressure,
)


def test_gravel_clean_crystal():
    r = get_presumed_bearing_pressure(SoilCategory.GRAVEL_CLEAN_CRYSTAL)
    assert r.valid is True
    assert r.p_conv == pytest.approx(600.0)
    assert r.p_conv_range is None
    assert r.errors == []


def test_gravel_with_sand():
    r = get_presumed_bearing_pressure(SoilCategory.GRAVEL_WITH_SAND)
    assert r.valid is True
    assert r.p_conv == pytest.approx(550.0)


def test_gravel_sedimentary():
    r = get_presumed_bearing_pressure(SoilCategory.GRAVEL_SEDIMENTARY)
    assert r.valid is True
    assert r.p_conv == pytest.approx(350.0)


def test_gravel_silty_sand_no_ic_returns_range():
    r = get_presumed_bearing_pressure(SoilCategory.GRAVEL_SILTY_SAND)
    assert r.valid is True
    assert r.p_conv is None
    assert r.p_conv_range == (350.0, 500.0)
    assert len(r.warnings) == 1


def test_gravel_silty_sand_ic_min():
    r = get_presumed_bearing_pressure(SoilCategory.GRAVEL_SILTY_SAND, consistency_index=0.5)
    assert r.valid is True
    assert r.p_conv == pytest.approx(350.0)
    assert r.interpolated is False


def test_gravel_silty_sand_ic_max():
    r = get_presumed_bearing_pressure(SoilCategory.GRAVEL_SILTY_SAND, consistency_index=1.0)
    assert r.valid is True
    assert r.p_conv == pytest.approx(500.0)
    assert r.interpolated is False


def test_gravel_silty_sand_ic_interpolated():
    # IC=0.75 midpoint [0.5, 1.0] → 350 + 0.5*150 = 425
    r = get_presumed_bearing_pressure(SoilCategory.GRAVEL_SILTY_SAND, consistency_index=0.75)
    assert r.valid is True
    assert r.p_conv == pytest.approx(425.0)
    assert r.interpolated is True


def test_gravel_silty_sand_ic_out_of_range():
    r = get_presumed_bearing_pressure(SoilCategory.GRAVEL_SILTY_SAND, consistency_index=0.2)
    assert r.valid is False
    assert len(r.errors) == 1


def test_source_metadata():
    r = get_presumed_bearing_pressure(SoilCategory.GRAVEL_WITH_SAND)
    assert r.source.code == "NP 112:2014"
    assert r.source.table == "Tabelul D.2"


def test_invalid_category():
    r = get_presumed_bearing_pressure("invalid")
    assert r.valid is False
    assert len(r.errors) == 1


def test_non_gravel_category_rejected():
    r = get_presumed_bearing_pressure(SoilCategory.ROCKY)
    assert r.valid is False
    assert len(r.errors) == 1
```

- [ ] **Step 2: Run to verify fail**

```
pytest tests/test_np_112_2014_presumed_bearing_pressure_gravels.py -v
```

Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Implement modul**

Creează `src/tabularium/np_112_2014/presumed_bearing_pressure_gravels.py`:

```python
from __future__ import annotations

from ..enums import SoilCategory
from ..interpolation import interpolate_linear
from ..models import CodeSource
from . import PresumedBearingPressureResult

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


def get_presumed_bearing_pressure(
    soil_category: SoilCategory,
    consistency_index: float | None = None,
) -> PresumedBearingPressureResult:
    """
    Returnează p̄_conv [kPa] pentru pământuri grosiere (pietrișuri)
    conform NP 112:2014, Tabelul D.2.

    consistency_index (I_C) necesar doar pentru GRAVEL_SILTY_SAND.
    """
    result = PresumedBearingPressureResult(source=_SOURCE)

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
pytest tests/test_np_112_2014_presumed_bearing_pressure_gravels.py -v
```

Expected: all PASS.

- [ ] **Step 5: Commit**

```bash
git add src/tabularium/np_112_2014/presumed_bearing_pressure_gravels.py tests/test_np_112_2014_presumed_bearing_pressure_gravels.py
git commit -m "feat(np112): add presumed_bearing_pressure_gravels (Tabelul D.2)"
```

---

## Task 6: D.3 — `presumed_bearing_pressure_sands.py`

**Files:**
- Create: `src/tabularium/np_112_2014/presumed_bearing_pressure_sands.py`
- Create: `tests/test_np_112_2014_presumed_bearing_pressure_sands.py`

- [ ] **Step 1: Write failing tests**

Creează `tests/test_np_112_2014_presumed_bearing_pressure_sands.py`:

```python
import pytest
from tabularium.np_112_2014.presumed_bearing_pressure_sands import (
    SoilCategory,
    RelativeDensity,
    MoistureCondition,
    PresumedBearingPressureResult,
    get_presumed_bearing_pressure,
)


# ── Exact lookups ─────────────────────────────────────────────────────────────

def test_coarse_sand_dense():
    r = get_presumed_bearing_pressure(SoilCategory.COARSE_SAND, RelativeDensity.DENSE, MoistureCondition.DRY)
    assert r.valid is True
    assert r.p_conv == pytest.approx(700.0)
    assert r.errors == []
    assert r.warnings == []


def test_coarse_sand_medium():
    r = get_presumed_bearing_pressure(SoilCategory.COARSE_SAND, RelativeDensity.MEDIUM, MoistureCondition.SATURATED)
    assert r.valid is True
    assert r.p_conv == pytest.approx(600.0)


def test_medium_sand_dense():
    r = get_presumed_bearing_pressure(SoilCategory.MEDIUM_SAND, RelativeDensity.DENSE, MoistureCondition.MOIST)
    assert r.valid is True
    assert r.p_conv == pytest.approx(600.0)


def test_medium_sand_medium():
    r = get_presumed_bearing_pressure(SoilCategory.MEDIUM_SAND, RelativeDensity.MEDIUM, MoistureCondition.DRY)
    assert r.valid is True
    assert r.p_conv == pytest.approx(500.0)


def test_fine_sand_dry_dense():
    r = get_presumed_bearing_pressure(SoilCategory.FINE_SAND, RelativeDensity.DENSE, MoistureCondition.DRY)
    assert r.valid is True
    assert r.p_conv == pytest.approx(500.0)


def test_fine_sand_moist_medium():
    r = get_presumed_bearing_pressure(SoilCategory.FINE_SAND, RelativeDensity.MEDIUM, MoistureCondition.MOIST)
    assert r.valid is True
    assert r.p_conv == pytest.approx(350.0)


def test_fine_sand_very_moist_dense():
    r = get_presumed_bearing_pressure(SoilCategory.FINE_SAND, RelativeDensity.DENSE, MoistureCondition.VERY_MOIST)
    assert r.valid is True
    assert r.p_conv == pytest.approx(350.0)


def test_fine_sand_saturated_medium():
    r = get_presumed_bearing_pressure(SoilCategory.FINE_SAND, RelativeDensity.MEDIUM, MoistureCondition.SATURATED)
    assert r.valid is True
    assert r.p_conv == pytest.approx(250.0)


def test_silty_sand_dry_dense():
    r = get_presumed_bearing_pressure(SoilCategory.SILTY_SAND, RelativeDensity.DENSE, MoistureCondition.DRY)
    assert r.valid is True
    assert r.p_conv == pytest.approx(350.0)


def test_silty_sand_moist_medium():
    r = get_presumed_bearing_pressure(SoilCategory.SILTY_SAND, RelativeDensity.MEDIUM, MoistureCondition.MOIST)
    assert r.valid is True
    assert r.p_conv == pytest.approx(200.0)


def test_silty_sand_very_moist_dense():
    r = get_presumed_bearing_pressure(SoilCategory.SILTY_SAND, RelativeDensity.DENSE, MoistureCondition.VERY_MOIST)
    assert r.valid is True
    assert r.p_conv == pytest.approx(200.0)


def test_silty_sand_saturated_medium():
    r = get_presumed_bearing_pressure(SoilCategory.SILTY_SAND, RelativeDensity.MEDIUM, MoistureCondition.SATURATED)
    assert r.valid is True
    assert r.p_conv == pytest.approx(150.0)


# ── Source & type ─────────────────────────────────────────────────────────────

def test_source_metadata():
    r = get_presumed_bearing_pressure(SoilCategory.COARSE_SAND, RelativeDensity.DENSE, MoistureCondition.DRY)
    assert r.source.code == "NP 112:2014"
    assert r.source.table == "Tabelul D.3"


def test_result_type():
    r = get_presumed_bearing_pressure(SoilCategory.COARSE_SAND, RelativeDensity.DENSE, MoistureCondition.DRY)
    assert isinstance(r, PresumedBearingPressureResult)


# ── Error cases ───────────────────────────────────────────────────────────────

def test_invalid_category():
    r = get_presumed_bearing_pressure("invalid", RelativeDensity.DENSE, MoistureCondition.DRY)
    assert r.valid is False
    assert len(r.errors) == 1


def test_invalid_relative_density():
    r = get_presumed_bearing_pressure(SoilCategory.COARSE_SAND, "invalid", MoistureCondition.DRY)
    assert r.valid is False
    assert len(r.errors) == 1


def test_invalid_moisture_condition():
    r = get_presumed_bearing_pressure(SoilCategory.FINE_SAND, RelativeDensity.DENSE, "invalid")
    assert r.valid is False
    assert len(r.errors) == 1


def test_non_sand_category_rejected():
    r = get_presumed_bearing_pressure(SoilCategory.ROCKY, RelativeDensity.DENSE, MoistureCondition.DRY)
    assert r.valid is False
    assert len(r.errors) == 1
```

- [ ] **Step 2: Run to verify fail**

```
pytest tests/test_np_112_2014_presumed_bearing_pressure_sands.py -v
```

Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Implement modul**

Creează `src/tabularium/np_112_2014/presumed_bearing_pressure_sands.py`:

```python
from __future__ import annotations

from ..enums import MoistureCondition, RelativeDensity, SoilCategory
from ..models import CodeSource
from . import PresumedBearingPressureResult

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


def get_presumed_bearing_pressure(
    soil_category: SoilCategory,
    relative_density: RelativeDensity,
    moisture_condition: MoistureCondition,
) -> PresumedBearingPressureResult:
    """
    Returnează p̄_conv [kPa] pentru nisipuri conform NP 112:2014, Tabelul D.3.

    Pentru COARSE_SAND și MEDIUM_SAND, moisture_condition este acceptat
    dar nu influențează valoarea (tabelul are un singur rând per categorie).
    """
    result = PresumedBearingPressureResult(source=_SOURCE)

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
pytest tests/test_np_112_2014_presumed_bearing_pressure_sands.py -v
```

Expected: all PASS.

- [ ] **Step 5: Commit**

```bash
git add src/tabularium/np_112_2014/presumed_bearing_pressure_sands.py tests/test_np_112_2014_presumed_bearing_pressure_sands.py
git commit -m "feat(np112): add presumed_bearing_pressure_sands (Tabelul D.3)"
```

---

## Task 7: D.4 — `presumed_bearing_pressure_fines.py`

**Files:**
- Create: `src/tabularium/np_112_2014/presumed_bearing_pressure_fines.py`
- Create: `tests/test_np_112_2014_presumed_bearing_pressure_fines.py`

- [ ] **Step 1: Write failing tests**

Creează `tests/test_np_112_2014_presumed_bearing_pressure_fines.py`:

```python
import pytest
from tabularium.np_112_2014.presumed_bearing_pressure_fines import (
    PlasticityClass,
    PresumedBearingPressureResult,
    get_presumed_bearing_pressure,
)


# ── Exact node lookups ────────────────────────────────────────────────────────

def test_low_plasticity_exact_node_upper_band():
    # LOW, e=0.5, IC=0.75 → exact node in upper band → 325
    r = get_presumed_bearing_pressure(PlasticityClass.LOW, void_ratio=0.5, consistency_index=0.75)
    assert r.valid is True
    assert r.p_conv == pytest.approx(325.0)
    assert r.interpolated is False
    assert r.errors == []


def test_low_plasticity_exact_node_ic_1():
    # LOW, e=0.7, IC=1.0 → exact node → 300
    r = get_presumed_bearing_pressure(PlasticityClass.LOW, void_ratio=0.7, consistency_index=1.0)
    assert r.valid is True
    assert r.p_conv == pytest.approx(300.0)
    assert r.interpolated is False


def test_low_plasticity_exact_node_lower_band():
    # LOW, e=0.5, IC=0.5 → exact node in lower band → 300
    r = get_presumed_bearing_pressure(PlasticityClass.LOW, void_ratio=0.5, consistency_index=0.5)
    assert r.valid is True
    assert r.p_conv == pytest.approx(300.0)
    assert r.interpolated is False


def test_high_plasticity_exact_node():
    # HIGH, e=0.6, IC=1.0 → 525
    r = get_presumed_bearing_pressure(PlasticityClass.HIGH, void_ratio=0.6, consistency_index=1.0)
    assert r.valid is True
    assert r.p_conv == pytest.approx(525.0)


# ── Band boundary: IC=0.75 goes to upper band ─────────────────────────────────

def test_ic_0_75_uses_upper_band():
    # LOW, e=0.5, IC=0.75 → upper band, exact node → 325 (not lower band which also has 325 here)
    r = get_presumed_bearing_pressure(PlasticityClass.LOW, void_ratio=0.5, consistency_index=0.75)
    assert r.valid is True
    assert r.p_conv == pytest.approx(325.0)
    assert r.interpolated is False


# ── Bilinear interpolation ────────────────────────────────────────────────────

def test_low_plasticity_interpolate_e_only():
    # LOW, e=0.6 (midpoint [0.5,0.7]), IC=0.75 exact
    # upper band: e=0.5→325, e=0.7→285; at e=0.6 → (325+285)/2 = 305
    r = get_presumed_bearing_pressure(PlasticityClass.LOW, void_ratio=0.6, consistency_index=0.75)
    assert r.valid is True
    assert r.p_conv == pytest.approx(305.0)
    assert r.interpolated is True


def test_low_plasticity_interpolate_ic_only():
    # LOW, e=0.5 exact, IC=0.875 (midpoint [0.75,1.0])
    # upper band e=0.5: IC=0.75→325, IC=1.0→350; at IC=0.875 → (325+350)/2 = 337.5
    r = get_presumed_bearing_pressure(PlasticityClass.LOW, void_ratio=0.5, consistency_index=0.875)
    assert r.valid is True
    assert r.p_conv == pytest.approx(337.5)
    assert r.interpolated is True


def test_medium_plasticity_bilinear():
    # MEDIUM, upper band, e=0.6 (midpoint [0.5,0.7]), IC=0.875 (midpoint [0.75,1.0])
    # At e=0.5, IC=0.875 → (325+350)/2 = 337.5
    # At e=0.7, IC=0.875 → (285+300)/2 = 292.5
    # At e=0.6 → (337.5+292.5)/2 = 315.0
    r = get_presumed_bearing_pressure(PlasticityClass.MEDIUM, void_ratio=0.6, consistency_index=0.875)
    assert r.valid is True
    assert r.p_conv == pytest.approx(315.0)
    assert r.interpolated is True


# ── Out-of-range ──────────────────────────────────────────────────────────────

def test_ic_below_range():
    r = get_presumed_bearing_pressure(PlasticityClass.LOW, void_ratio=0.5, consistency_index=0.3)
    assert r.valid is False
    assert len(r.errors) == 1


def test_ic_above_range():
    r = get_presumed_bearing_pressure(PlasticityClass.LOW, void_ratio=0.5, consistency_index=1.1)
    assert r.valid is False
    assert len(r.errors) == 1


def test_e_above_limit_low():
    # LOW: e_max = 0.7
    r = get_presumed_bearing_pressure(PlasticityClass.LOW, void_ratio=0.8, consistency_index=0.8)
    assert r.valid is False
    assert len(r.errors) == 1


def test_e_below_minimum():
    r = get_presumed_bearing_pressure(PlasticityClass.LOW, void_ratio=0.3, consistency_index=0.8)
    assert r.valid is False
    assert len(r.errors) == 1


def test_e_at_limit_high():
    # HIGH: e_max = 1.1, e=1.1 is a data point → should be valid
    r = get_presumed_bearing_pressure(PlasticityClass.HIGH, void_ratio=1.1, consistency_index=1.0)
    assert r.valid is True
    assert r.p_conv == pytest.approx(300.0)


# ── Source & type ─────────────────────────────────────────────────────────────

def test_source_metadata():
    r = get_presumed_bearing_pressure(PlasticityClass.LOW, void_ratio=0.5, consistency_index=0.75)
    assert r.source.code == "NP 112:2014"
    assert r.source.table == "Tabelul D.4"


def test_result_type():
    r = get_presumed_bearing_pressure(PlasticityClass.LOW, void_ratio=0.5, consistency_index=0.75)
    assert isinstance(r, PresumedBearingPressureResult)


def test_invalid_plasticity_class():
    r = get_presumed_bearing_pressure("invalid", void_ratio=0.5, consistency_index=0.75)
    assert r.valid is False
    assert len(r.errors) == 1
```

- [ ] **Step 2: Run to verify fail**

```
pytest tests/test_np_112_2014_presumed_bearing_pressure_fines.py -v
```

Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Implement modul**

Creează `src/tabularium/np_112_2014/presumed_bearing_pressure_fines.py`:

```python
from __future__ import annotations

import bisect

from ..enums import PlasticityClass
from ..interpolation import interpolate_linear
from ..models import CodeSource
from . import PresumedBearingPressureResult

_SOURCE = CodeSource(code="NP 112:2014", table="Tabelul D.4")

# _SubGrid[e][I_C] = p_conv
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

    band = "upper" if consistency_index >= _IC_BAND_BOUNDARY else "lower"
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
    result.valid = True
    return result
```

- [ ] **Step 4: Run tests**

```
pytest tests/test_np_112_2014_presumed_bearing_pressure_fines.py -v
```

Expected: all PASS.

- [ ] **Step 5: Commit**

```bash
git add src/tabularium/np_112_2014/presumed_bearing_pressure_fines.py tests/test_np_112_2014_presumed_bearing_pressure_fines.py
git commit -m "feat(np112): add presumed_bearing_pressure_fines (Tabelul D.4)"
```

---

## Task 8: D.5 — `presumed_bearing_pressure_fills.py`

**Files:**
- Create: `src/tabularium/np_112_2014/presumed_bearing_pressure_fills.py`
- Create: `tests/test_np_112_2014_presumed_bearing_pressure_fills.py`

- [ ] **Step 1: Write failing tests**

Creează `tests/test_np_112_2014_presumed_bearing_pressure_fills.py`:

```python
import pytest
from tabularium.np_112_2014.presumed_bearing_pressure_fills import (
    FillType,
    FillSoilType,
    PresumedBearingPressureResult,
    get_presumed_bearing_pressure,
)


# ── Exact lookups la noduri (Sr ≤ 0.5 și Sr ≥ 0.8) ──────────────────────────

def test_controlled_sandy_sr_low():
    r = get_presumed_bearing_pressure(FillType.CONTROLLED_COMPACTED, FillSoilType.SANDY_SLAG, saturation_degree=0.3)
    assert r.valid is True
    assert r.p_conv == pytest.approx(250.0)
    assert r.interpolated is False
    assert r.errors == []


def test_controlled_sandy_sr_high():
    r = get_presumed_bearing_pressure(FillType.CONTROLLED_COMPACTED, FillSoilType.SANDY_SLAG, saturation_degree=0.9)
    assert r.valid is True
    assert r.p_conv == pytest.approx(200.0)
    assert r.interpolated is False


def test_controlled_silty_sr_low():
    r = get_presumed_bearing_pressure(FillType.CONTROLLED_COMPACTED, FillSoilType.SILTY_FINE, saturation_degree=0.2)
    assert r.valid is True
    assert r.p_conv == pytest.approx(180.0)


def test_controlled_silty_sr_high():
    r = get_presumed_bearing_pressure(FillType.CONTROLLED_COMPACTED, FillSoilType.SILTY_FINE, saturation_degree=1.0)
    assert r.valid is True
    assert r.p_conv == pytest.approx(150.0)


def test_known_origin_sandy_sr_low():
    r = get_presumed_bearing_pressure(FillType.KNOWN_ORIGIN, FillSoilType.SANDY_SLAG, saturation_degree=0.0)
    assert r.valid is True
    assert r.p_conv == pytest.approx(180.0)


def test_known_origin_silty_sr_high():
    r = get_presumed_bearing_pressure(FillType.KNOWN_ORIGIN, FillSoilType.SILTY_FINE, saturation_degree=0.8)
    assert r.valid is True
    assert r.p_conv == pytest.approx(100.0)
    assert r.interpolated is False


# ── Interpolation ─────────────────────────────────────────────────────────────

def test_controlled_sandy_sr_midpoint():
    # Sr=0.65 midpoint [0.5, 0.8] → (250+200)/2 = 225
    r = get_presumed_bearing_pressure(FillType.CONTROLLED_COMPACTED, FillSoilType.SANDY_SLAG, saturation_degree=0.65)
    assert r.valid is True
    assert r.p_conv == pytest.approx(225.0)
    assert r.interpolated is True


def test_known_origin_silty_interpolated():
    # Sr=0.65 midpoint [0.5, 0.8] → (120+100)/2 = 110
    r = get_presumed_bearing_pressure(FillType.KNOWN_ORIGIN, FillSoilType.SILTY_FINE, saturation_degree=0.65)
    assert r.valid is True
    assert r.p_conv == pytest.approx(110.0)
    assert r.interpolated is True


def test_sr_at_lower_node():
    # Sr=0.5 exact node
    r = get_presumed_bearing_pressure(FillType.CONTROLLED_COMPACTED, FillSoilType.SANDY_SLAG, saturation_degree=0.5)
    assert r.valid is True
    assert r.p_conv == pytest.approx(250.0)
    assert r.interpolated is False


def test_sr_at_upper_node():
    # Sr=0.8 exact node
    r = get_presumed_bearing_pressure(FillType.CONTROLLED_COMPACTED, FillSoilType.SANDY_SLAG, saturation_degree=0.8)
    assert r.valid is True
    assert r.p_conv == pytest.approx(200.0)
    assert r.interpolated is False


# ── Out-of-range Sr ───────────────────────────────────────────────────────────

def test_sr_negative():
    r = get_presumed_bearing_pressure(FillType.CONTROLLED_COMPACTED, FillSoilType.SANDY_SLAG, saturation_degree=-0.1)
    assert r.valid is False
    assert len(r.errors) == 1


def test_sr_above_one():
    r = get_presumed_bearing_pressure(FillType.CONTROLLED_COMPACTED, FillSoilType.SANDY_SLAG, saturation_degree=1.1)
    assert r.valid is False
    assert len(r.errors) == 1


# ── Source & type ─────────────────────────────────────────────────────────────

def test_source_metadata():
    r = get_presumed_bearing_pressure(FillType.CONTROLLED_COMPACTED, FillSoilType.SANDY_SLAG, saturation_degree=0.3)
    assert r.source.code == "NP 112:2014"
    assert r.source.table == "Tabelul D.5"


def test_result_type():
    r = get_presumed_bearing_pressure(FillType.CONTROLLED_COMPACTED, FillSoilType.SANDY_SLAG, saturation_degree=0.3)
    assert isinstance(r, PresumedBearingPressureResult)


def test_invalid_fill_type():
    r = get_presumed_bearing_pressure("invalid", FillSoilType.SANDY_SLAG, saturation_degree=0.3)
    assert r.valid is False
    assert len(r.errors) == 1


def test_invalid_fill_soil_type():
    r = get_presumed_bearing_pressure(FillType.CONTROLLED_COMPACTED, "invalid", saturation_degree=0.3)
    assert r.valid is False
    assert len(r.errors) == 1
```

- [ ] **Step 2: Run to verify fail**

```
pytest tests/test_np_112_2014_presumed_bearing_pressure_fills.py -v
```

Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Implement modul**

Creează `src/tabularium/np_112_2014/presumed_bearing_pressure_fills.py`:

```python
from __future__ import annotations

from ..enums import FillSoilType, FillType
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

_SR_MIN = 0.0
_SR_MAX = 1.0
_SR_NODE_LOW  = 0.5
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
pytest tests/test_np_112_2014_presumed_bearing_pressure_fills.py -v
```

Expected: all PASS.

- [ ] **Step 5: Commit**

```bash
git add src/tabularium/np_112_2014/presumed_bearing_pressure_fills.py tests/test_np_112_2014_presumed_bearing_pressure_fills.py
git commit -m "feat(np112): add presumed_bearing_pressure_fills (Tabelul D.5)"
```

---

## Task 9: Registry + CLAUDE.md

**Files:**
- Modify: `src/tabularium/registry.py`
- Modify: `CLAUDE.md`

- [ ] **Step 1: Adaugă intrările în registry**

În `src/tabularium/registry.py`, adaugă importurile după cele existente:

```python
from .np_112_2014.presumed_bearing_pressure_rocks import get_presumed_bearing_pressure as _np112_rocks
from .np_112_2014.presumed_bearing_pressure_boulders import get_presumed_bearing_pressure as _np112_boulders
from .np_112_2014.presumed_bearing_pressure_gravels import get_presumed_bearing_pressure as _np112_gravels
from .np_112_2014.presumed_bearing_pressure_sands import get_presumed_bearing_pressure as _np112_sands
from .np_112_2014.presumed_bearing_pressure_fines import get_presumed_bearing_pressure as _np112_fines
from .np_112_2014.presumed_bearing_pressure_fills import get_presumed_bearing_pressure as _np112_fills
```

Adaugă în dicționarul `REGISTRY`:

```python
    "np_112_2014.presumed_bearing_pressure_rocks": TableEntry(
        normative="NP 112:2014",
        table_id="D.1",
        description="Presiuni convenționale p̄_conv [kPa] pentru roci stâncoase și semi-stâncoase",
        lookup_fn=_np112_rocks,
    ),
    "np_112_2014.presumed_bearing_pressure_boulders": TableEntry(
        normative="NP 112:2014",
        table_id="D.2",
        description="Presiuni convenționale p̄_conv [kPa] pentru pământuri foarte grosiere",
        lookup_fn=_np112_boulders,
    ),
    "np_112_2014.presumed_bearing_pressure_gravels": TableEntry(
        normative="NP 112:2014",
        table_id="D.2",
        description="Presiuni convenționale p̄_conv [kPa] pentru pământuri grosiere (pietrișuri)",
        lookup_fn=_np112_gravels,
    ),
    "np_112_2014.presumed_bearing_pressure_sands": TableEntry(
        normative="NP 112:2014",
        table_id="D.3",
        description="Presiuni convenționale p̄_conv [kPa] pentru nisipuri",
        lookup_fn=_np112_sands,
    ),
    "np_112_2014.presumed_bearing_pressure_fines": TableEntry(
        normative="NP 112:2014",
        table_id="D.4",
        description="Presiuni convenționale p̄_conv [kPa] pentru pământuri fine coezive",
        lookup_fn=_np112_fines,
    ),
    "np_112_2014.presumed_bearing_pressure_fills": TableEntry(
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
│   ├── __init__.py                          # PresumedBearingPressureResult
│   ├── presumed_bearing_pressure_rocks.py       # Tabelul D.1 — roci stâncoase și semi-stâncoase
│   ├── presumed_bearing_pressure_boulders.py    # Tabelul D.2 — pământuri foarte grosiere
│   ├── presumed_bearing_pressure_gravels.py     # Tabelul D.2 — pământuri grosiere (pietrișuri)
│   ├── presumed_bearing_pressure_sands.py       # Tabelul D.3 — nisipuri
│   ├── presumed_bearing_pressure_fines.py       # Tabelul D.4 — pământuri fine coezive
│   └── presumed_bearing_pressure_fills.py       # Tabelul D.5 — umpluturi
```

Actualizează și secțiunea `tests/`:

```
├── test_np_112_2014_presumed_bearing_pressure_rocks.py
├── test_np_112_2014_presumed_bearing_pressure_boulders.py
├── test_np_112_2014_presumed_bearing_pressure_gravels.py
├── test_np_112_2014_presumed_bearing_pressure_sands.py
├── test_np_112_2014_presumed_bearing_pressure_fines.py
└── test_np_112_2014_presumed_bearing_pressure_fills.py
```

- [ ] **Step 4: Rulează toate testele**

```
pytest tests/ -v
```

Expected: toate PASS.

- [ ] **Step 5: Commit final**

```bash
git add src/tabularium/registry.py CLAUDE.md
git commit -m "feat(registry): register NP 112:2014 presumed bearing pressure tables D.1–D.5"
```
