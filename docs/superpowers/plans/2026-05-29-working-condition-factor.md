# Working Condition Factor (H.7) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add Tabelul H.7 (coeficientul condițiilor de lucru m₁) from NP 112:2014 as a lookup module, preceded by a semantic rename of the two core enums for codebase consistency.

**Architecture:** Four sequential tasks — (1) mechanical enum rename across codebase, (2) enum value changes (rename + additions), (3) TDD implementation of the H.7 module under a new `allowable_bearing_capacity` sub-package, (4) registry + docs update. Each task ends with a green test suite and a commit.

**Tech Stack:** Python 3, dataclasses (stdlib), pytest

---

## File Map

**Modified:**
- `src/tabularium/enums.py` — rename classes, rename one value, add 4 new values
- `src/tabularium/np_112_2014/presumed_bearing_pressure/boulders.py` — update enum references
- `src/tabularium/np_112_2014/presumed_bearing_pressure/gravels.py` — update enum imports
- `src/tabularium/np_112_2014/presumed_bearing_pressure/fills.py` — update enum imports
- `src/tabularium/np_112_2014/presumed_bearing_pressure/rocks.py` — update enum imports
- `src/tabularium/np_112_2014/presumed_bearing_pressure/sands.py` — update enum imports
- `src/tabularium/np_112_2014/presumed_bearing_pressure/__init__.py` — update enum imports
- `src/tabularium/np_122_2010/indicative_shear_strength/non_cohesive.py` — update enum imports
- `src/tabularium/np_122_2010/indicative_deformation_modulus/non_cohesive.py` — update enum imports
- `src/tabularium/registry.py` — add new entry + import
- `tests/test_np_112_2014_presumed_bearing_pressure_boulders.py` — update enum name references
- All other test files that import `SoilCategory` or `SoilType`
- `CLAUDE.md` — add new module to package structure

**Created:**
- `src/tabularium/np_112_2014/allowable_bearing_capacity/__init__.py`
- `src/tabularium/np_112_2014/allowable_bearing_capacity/working_condition_factor.py`
- `tests/test_np_112_2014_allowable_bearing_capacity_working_condition_factor.py`

---

## Task 1: Rename SoilCategory → Soil and SoilType → SoilCategory

The existing names are semantically inverted: `SoilCategory` holds specific soil names (CLAY, FINE_SAND…) and `SoilType` holds broad categories (COHESIVE, NON_COHESIVE). We fix this before adding new values so every new line uses correct names from day one.

**Files:** All 18 files listed in the file map above (mechanical find & replace).

- [ ] **Step 1: Rename both classes in enums.py**

Open `src/tabularium/enums.py` and apply these two changes:

```python
# line 6 — change:
class SoilCategory(str, Enum):
# to:
class Soil(str, Enum):

# line 61 — change:
class SoilType(str, Enum):
# to:
class SoilCategory(str, Enum):
```

- [ ] **Step 2: Replace all usages of `SoilCategory` → `Soil` across source and tests**

Run from the repo root (inside `tabularium/`):

```bash
find src tests -name "*.py" ! -path "*/__pycache__/*" | \
  xargs perl -pi -e 's/\bSoilCategory\b/Soil/g'
```

- [ ] **Step 3: Replace all usages of `SoilType` → `SoilCategory` across source and tests**

`FillSoilType` must NOT be renamed — the negative lookbehind protects it:

```bash
find src tests -name "*.py" ! -path "*/__pycache__/*" | \
  xargs perl -pi -e 's/(?<![A-Za-z])SoilType\b/SoilCategory/g'
```

- [ ] **Step 4: Verify no stale references remain**

```bash
grep -rn "SoilCategory\|SoilType" src tests --include="*.py" | grep -v __pycache__ | grep -v "FillSoilType" | grep -v "class Soil\b" | grep -v "class SoilCategory"
```

Expected output: empty (no lines printed).

- [ ] **Step 5: Run the full test suite**

```bash
python3 -m pytest tests/ -q
```

Expected: `164 passed`

- [ ] **Step 6: Commit**

```bash
git add src/tabularium/enums.py \
  src/tabularium/np_112_2014/presumed_bearing_pressure/__init__.py \
  src/tabularium/np_112_2014/presumed_bearing_pressure/boulders.py \
  src/tabularium/np_112_2014/presumed_bearing_pressure/fills.py \
  src/tabularium/np_112_2014/presumed_bearing_pressure/fines.py \
  src/tabularium/np_112_2014/presumed_bearing_pressure/gravels.py \
  src/tabularium/np_112_2014/presumed_bearing_pressure/rocks.py \
  src/tabularium/np_112_2014/presumed_bearing_pressure/sands.py \
  src/tabularium/np_122_2010/indicative_shear_strength/non_cohesive.py \
  src/tabularium/np_122_2010/indicative_deformation_modulus/non_cohesive.py \
  tests/
git commit -m "refactor(enums): rename SoilCategory→Soil, SoilType→SoilCategory"
```

---

## Task 2: Rename BOULDER_CLAY_FILL → BOULDER_COHESIVE_FILL and add new Soil values

**Files:**
- Modify: `src/tabularium/enums.py`
- Modify: `src/tabularium/np_112_2014/presumed_bearing_pressure/boulders.py`
- Modify: `tests/test_np_112_2014_presumed_bearing_pressure_boulders.py`

- [ ] **Step 1: Rename BOULDER_CLAY_FILL everywhere**

```bash
find src tests -name "*.py" ! -path "*/__pycache__/*" | \
  xargs perl -pi -e 's/\bBOULDER_CLAY_FILL\b/BOULDER_COHESIVE_FILL/g'
```

- [ ] **Step 2: Add new Soil values in enums.py**

Open `src/tabularium/enums.py`. After the existing `GRAVEL_SILTY_SAND` line (currently inside the `Soil` class after Task 1), add:

```python
    # NP 112:2014 H.7 — working condition factor
    BOULDER_SAND_FILL    = "boulder_sand_fill"
    GRAVEL               = "gravel"
    GRAVEL_COHESIVE_FILL = "gravel_cohesive_fill"
    COHESIVE_SOIL        = "cohesive_soil"
```

- [ ] **Step 3: Run the full test suite**

```bash
python3 -m pytest tests/ -q
```

Expected: `164 passed`

- [ ] **Step 4: Commit**

```bash
git add src/tabularium/enums.py \
  src/tabularium/np_112_2014/presumed_bearing_pressure/boulders.py \
  tests/test_np_112_2014_presumed_bearing_pressure_boulders.py
git commit -m "refactor(enums): rename BOULDER_CLAY_FILL→BOULDER_COHESIVE_FILL, add H.7 soil values"
```

---

## Task 3: Create allowable_bearing_capacity package + result model

**Files:**
- Create: `src/tabularium/np_112_2014/allowable_bearing_capacity/__init__.py`

- [ ] **Step 1: Create the package file**

```python
# src/tabularium/np_112_2014/allowable_bearing_capacity/__init__.py
from __future__ import annotations

from dataclasses import dataclass

from ...models import LookupResult


@dataclass
class WorkingConditionFactorResult(LookupResult):
    m1: float | None = None
```

- [ ] **Step 2: Verify import works**

```bash
python3 -c "from tabularium.np_112_2014.allowable_bearing_capacity import WorkingConditionFactorResult; print('OK')"
```

Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add src/tabularium/np_112_2014/allowable_bearing_capacity/__init__.py
git commit -m "feat(np112): add allowable_bearing_capacity package with WorkingConditionFactorResult"
```

---

## Task 4: TDD — implement working_condition_factor.py

**Files:**
- Create: `tests/test_np_112_2014_allowable_bearing_capacity_working_condition_factor.py`
- Create: `src/tabularium/np_112_2014/allowable_bearing_capacity/working_condition_factor.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_np_112_2014_allowable_bearing_capacity_working_condition_factor.py`:

```python
import pytest
from tabularium.enums import Soil
from tabularium.np_112_2014.allowable_bearing_capacity import WorkingConditionFactorResult
from tabularium.np_112_2014.allowable_bearing_capacity.working_condition_factor import (
    get_working_condition_factor,
)


# ── Rândul 1: fără condiție secundară (m₁ = 2.0) ─────────────────────────────

def test_boulder_sand_fill():
    r = get_working_condition_factor(Soil.BOULDER_SAND_FILL)
    assert r.valid is True
    assert r.m1 == pytest.approx(2.0)
    assert r.errors == []

def test_medium_sand():
    r = get_working_condition_factor(Soil.MEDIUM_SAND)
    assert r.valid is True
    assert r.m1 == pytest.approx(2.0)

def test_coarse_sand():
    r = get_working_condition_factor(Soil.COARSE_SAND)
    assert r.valid is True
    assert r.m1 == pytest.approx(2.0)

def test_gravel():
    r = get_working_condition_factor(Soil.GRAVEL)
    assert r.valid is True
    assert r.m1 == pytest.approx(2.0)


# ── Nisipuri fine (Sᵣ) ────────────────────────────────────────────────────────

def test_fine_sand_sr_at_threshold():
    # Sᵣ = 0.8 → uscate/umede → m₁ = 1.7
    r = get_working_condition_factor(Soil.FINE_SAND, saturation_ratio=0.8)
    assert r.valid is True
    assert r.m1 == pytest.approx(1.7)

def test_fine_sand_sr_above_threshold():
    # Sᵣ > 0.8 → foarte umede/saturate → m₁ = 1.6
    r = get_working_condition_factor(Soil.FINE_SAND, saturation_ratio=0.81)
    assert r.valid is True
    assert r.m1 == pytest.approx(1.6)

def test_fine_sand_missing_saturation_ratio():
    r = get_working_condition_factor(Soil.FINE_SAND)
    assert r.valid is False
    assert len(r.errors) == 1


# ── Nisipuri prăfoase (Sᵣ) ───────────────────────────────────────────────────

def test_silty_sand_dry_moist():
    r = get_working_condition_factor(Soil.SILTY_SAND, saturation_ratio=0.5)
    assert r.valid is True
    assert r.m1 == pytest.approx(1.5)

def test_silty_sand_very_moist():
    r = get_working_condition_factor(Soil.SILTY_SAND, saturation_ratio=0.9)
    assert r.valid is True
    assert r.m1 == pytest.approx(1.3)

def test_silty_sand_missing_saturation_ratio():
    r = get_working_condition_factor(Soil.SILTY_SAND)
    assert r.valid is False
    assert len(r.errors) == 1


# ── Bolovănișuri cu fill coeziv (Iᶜ) ─────────────────────────────────────────

def test_boulder_cohesive_fill_stiff():
    # Iᶜ = 0.5 (exact la limită ≥ 0.5) → m₁ = 1.3
    r = get_working_condition_factor(Soil.BOULDER_COHESIVE_FILL, consistency_index=0.5)
    assert r.valid is True
    assert r.m1 == pytest.approx(1.3)

def test_boulder_cohesive_fill_soft():
    r = get_working_condition_factor(Soil.BOULDER_COHESIVE_FILL, consistency_index=0.49)
    assert r.valid is True
    assert r.m1 == pytest.approx(1.1)

def test_boulder_cohesive_fill_missing_ic():
    r = get_working_condition_factor(Soil.BOULDER_COHESIVE_FILL)
    assert r.valid is False
    assert len(r.errors) == 1


# ── Pietriș cu fill coeziv (Iᶜ) ──────────────────────────────────────────────

def test_gravel_cohesive_fill_stiff():
    r = get_working_condition_factor(Soil.GRAVEL_COHESIVE_FILL, consistency_index=0.7)
    assert r.valid is True
    assert r.m1 == pytest.approx(1.3)

def test_gravel_cohesive_fill_soft():
    r = get_working_condition_factor(Soil.GRAVEL_COHESIVE_FILL, consistency_index=0.3)
    assert r.valid is True
    assert r.m1 == pytest.approx(1.1)

def test_gravel_cohesive_fill_missing_ic():
    r = get_working_condition_factor(Soil.GRAVEL_COHESIVE_FILL)
    assert r.valid is False
    assert len(r.errors) == 1


# ── Pământuri coezive (Iᶜ) ────────────────────────────────────────────────────

def test_cohesive_soil_stiff():
    r = get_working_condition_factor(Soil.COHESIVE_SOIL, consistency_index=0.75)
    assert r.valid is True
    assert r.m1 == pytest.approx(1.4)

def test_cohesive_soil_ic_exactly_05():
    # Iᶜ = 0.5 → la limita ≥ 0.5 → m₁ = 1.4
    r = get_working_condition_factor(Soil.COHESIVE_SOIL, consistency_index=0.5)
    assert r.valid is True
    assert r.m1 == pytest.approx(1.4)

def test_cohesive_soil_soft():
    r = get_working_condition_factor(Soil.COHESIVE_SOIL, consistency_index=0.49)
    assert r.valid is True
    assert r.m1 == pytest.approx(1.1)

def test_cohesive_soil_missing_ic():
    r = get_working_condition_factor(Soil.COHESIVE_SOIL)
    assert r.valid is False
    assert len(r.errors) == 1


# ── Categorii neacceptate de H.7 ─────────────────────────────────────────────

def test_gravel_clean_crystal_rejected():
    r = get_working_condition_factor(Soil.GRAVEL_CLEAN_CRYSTAL)
    assert r.valid is False
    assert len(r.errors) == 1

def test_boulder_gravel_fill_rejected():
    r = get_working_condition_factor(Soil.BOULDER_GRAVEL_FILL)
    assert r.valid is False
    assert len(r.errors) == 1

def test_invalid_string_rejected():
    r = get_working_condition_factor("invalid")
    assert r.valid is False
    assert len(r.errors) == 1


# ── Metadata ──────────────────────────────────────────────────────────────────

def test_source_metadata():
    r = get_working_condition_factor(Soil.GRAVEL)
    assert r.source.code == "NP 112:2014"
    assert r.source.table == "Tabelul H.7"

def test_result_type():
    r = get_working_condition_factor(Soil.GRAVEL)
    assert isinstance(r, WorkingConditionFactorResult)
```

- [ ] **Step 2: Run tests to confirm they fail (module not yet implemented)**

```bash
python3 -m pytest tests/test_np_112_2014_allowable_bearing_capacity_working_condition_factor.py -v
```

Expected: `ImportError` or `ModuleNotFoundError` — the module doesn't exist yet.

- [ ] **Step 3: Implement working_condition_factor.py**

Create `src/tabularium/np_112_2014/allowable_bearing_capacity/working_condition_factor.py`:

```python
from __future__ import annotations

from ...enums import Soil
from ...models import CodeSource
from . import WorkingConditionFactorResult

_SOURCE = CodeSource(code="NP 112:2014", table="Tabelul H.7")

_SR_THRESHOLD = 0.8   # Sᵣ ≤ 0.8 → uscat/umed; Sᵣ > 0.8 → foarte umed/saturat
_IC_THRESHOLD = 0.5   # Iᶜ ≥ 0.5 → consistent; Iᶜ < 0.5 → moale

# Categorii fără condiție secundară: m₁ fix
_NO_CONDITION: dict[Soil, float] = {
    Soil.BOULDER_SAND_FILL: 2.0,
    Soil.MEDIUM_SAND:       2.0,
    Soil.COARSE_SAND:       2.0,
    Soil.GRAVEL:            2.0,
}

# Categorii condiționate de Sᵣ: (m1_uscat_umed, m1_foarte_umed_saturat)
_SATURATION: dict[Soil, tuple[float, float]] = {
    Soil.FINE_SAND:  (1.7, 1.6),
    Soil.SILTY_SAND: (1.5, 1.3),
}

# Categorii condiționate de Iᶜ: (m1_consistent, m1_moale)
_CONSISTENCY: dict[Soil, tuple[float, float]] = {
    Soil.BOULDER_COHESIVE_FILL: (1.3, 1.1),
    Soil.GRAVEL_COHESIVE_FILL:  (1.3, 1.1),
    Soil.COHESIVE_SOIL:         (1.4, 1.1),
}


def get_working_condition_factor(
    soil_category: Soil,
    saturation_ratio: float | None = None,
    consistency_index: float | None = None,
) -> WorkingConditionFactorResult:
    """
    Returnează coeficientul condițiilor de lucru m₁
    conform NP 112:2014, Tabelul H.7.
    """
    result = WorkingConditionFactorResult(source=_SOURCE)

    try:
        soil_category = Soil(soil_category)
    except ValueError:
        result.errors.append(f"Categorie de sol necunoscută: {soil_category!r}.")
        return result

    if soil_category in _NO_CONDITION:
        result.m1 = _NO_CONDITION[soil_category]
        result.valid = True
        return result

    if soil_category in _SATURATION:
        if saturation_ratio is None:
            result.errors.append(
                f"saturation_ratio (Sᵣ) este necesar pentru {soil_category!r}."
            )
            return result
        m1_dry, m1_wet = _SATURATION[soil_category]
        result.m1 = m1_dry if saturation_ratio <= _SR_THRESHOLD else m1_wet
        result.valid = True
        return result

    if soil_category in _CONSISTENCY:
        if consistency_index is None:
            result.errors.append(
                f"consistency_index (Iᶜ) este necesar pentru {soil_category!r}."
            )
            return result
        m1_stiff, m1_soft = _CONSISTENCY[soil_category]
        result.m1 = m1_stiff if consistency_index >= _IC_THRESHOLD else m1_soft
        result.valid = True
        return result

    result.errors.append(
        f"Categoria {soil_category!r} nu este acoperită de Tabelul H.7. "
        "Verificați că folosiți categoria corectă pentru acest tabel."
    )
    return result
```

- [ ] **Step 4: Run the new tests**

```bash
python3 -m pytest tests/test_np_112_2014_allowable_bearing_capacity_working_condition_factor.py -v
```

Expected: all tests pass.

- [ ] **Step 5: Run the full suite**

```bash
python3 -m pytest tests/ -q
```

Expected: `189 passed` (164 existing + 25 new).

- [ ] **Step 6: Commit**

```bash
git add src/tabularium/np_112_2014/allowable_bearing_capacity/working_condition_factor.py \
  tests/test_np_112_2014_allowable_bearing_capacity_working_condition_factor.py
git commit -m "feat(np112): implement working_condition_factor — Tabelul H.7 (m₁)"
```

---

## Task 5: Registry + CLAUDE.md

**Files:**
- Modify: `src/tabularium/registry.py`
- Modify: `CLAUDE.md`

- [ ] **Step 1: Add import and registry entry in registry.py**

At the top of `src/tabularium/registry.py`, add after the last existing import:

```python
from .np_112_2014.allowable_bearing_capacity.working_condition_factor import (
    get_working_condition_factor as _np112_working_condition_factor,
)
```

At the end of the `REGISTRY` dict, add:

```python
    "np_112_2014.working_condition_factor": TableEntry(
        normative="NP 112:2014",
        table_id="H.7",
        description="Coeficientul condițiilor de lucru m₁",
        lookup_fn=_np112_working_condition_factor,
    ),
```

- [ ] **Step 2: Update package structure in CLAUDE.md**

In the `## Package structure` section of `CLAUDE.md`, add the new subfolder under `np_112_2014/`:

```
├── np_112_2014/
│   ├── __init__.py
│   ├── presumed_bearing_pressure/
│   │   └── ... (existing files)
│   └── allowable_bearing_capacity/
│       ├── __init__.py                                  # WorkingConditionFactorResult
│       └── working_condition_factor.py                  # Tabelul H.7 — coeficientul condițiilor de lucru m₁
```

And add to the `tests/` section:

```
│   └── test_np_112_2014_allowable_bearing_capacity_working_condition_factor.py
```

- [ ] **Step 3: Run the full suite**

```bash
python3 -m pytest tests/ -q
```

Expected: `189 passed`

- [ ] **Step 4: Commit**

```bash
git add src/tabularium/registry.py CLAUDE.md
git commit -m "feat(registry): register np_112_2014.working_condition_factor (Tabelul H.7)"
```
