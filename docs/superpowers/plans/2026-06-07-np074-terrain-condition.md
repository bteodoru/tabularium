# NP 074:2022 Terrain Condition Classifier — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement a parametric terrain condition classifier (Tables A.1–A.3, NP 074:2022) that returns GOOD/MEDIUM/DIFFICULT with matched table/row and contextual warnings for NP 125/NP 126 exceptions.

**Architecture:** One new module `np_074_2022/terrain_condition.py` with a single public function `classify_terrain_condition(inp: TerrainConditionInput) -> TerrainConditionResult`. Three new enums and one enum extension are added to the existing `enums.py`. A local registry wires into the global registry following the same pattern as `np_112_2014` and `np_122_2010`.

**Tech Stack:** Python 3.11+, stdlib `dataclasses`, `pytest`. No new dependencies.

---

## File Map

| Action | Path | Responsibility |
|--------|------|----------------|
| Modify | `src/tabularium/enums.py` | Add `TerrainCondition`, `SoilGroup`, `FillCategory`, `RelativeDensity.LOOSE` |
| Create | `src/tabularium/np_074_2022/__init__.py` | Package marker |
| Create | `src/tabularium/np_074_2022/terrain_condition.py` | `TerrainConditionInput`, `TerrainConditionResult`, `classify_terrain_condition` |
| Create | `src/tabularium/np_074_2022/registry.py` | Local registry entry |
| Modify | `src/tabularium/registry.py` | Include `np_074_2022` namespace |
| Create | `tests/test_np_074_2022_terrain_condition.py` | All tests |

---

## Task 1: Extend enums + module skeleton

**Files:**
- Modify: `src/tabularium/enums.py`
- Create: `src/tabularium/np_074_2022/__init__.py`
- Create: `src/tabularium/np_074_2022/terrain_condition.py`
- Create: `tests/test_np_074_2022_terrain_condition.py`

- [ ] **Step 1: Write the failing import test**

Create `tests/test_np_074_2022_terrain_condition.py`:

```python
from tabularium.np_074_2022.terrain_condition import (
    TerrainConditionInput,
    TerrainConditionResult,
    classify_terrain_condition,
)
from tabularium.enums import (
    FillCategory,
    RelativeDensity,
    SoilGroup,
    TerrainCondition,
)


def test_imports():
    assert TerrainCondition.GOOD
    assert TerrainCondition.MEDIUM
    assert TerrainCondition.DIFFICULT
    assert SoilGroup.ROCKY
    assert SoilGroup.NON_COHESIVE
    assert SoilGroup.COHESIVE_FINE
    assert SoilGroup.FILL
    assert FillCategory.CONTROLLED_COMPACTED
    assert FillCategory.KNOWN_ORIGIN_ORGANIZED
    assert FillCategory.UNCONTROLLED
    assert FillCategory.HOUSEHOLD
    assert RelativeDensity.LOOSE


def test_input_dataclass_instantiation():
    inp = TerrainConditionInput(soil_group=SoilGroup.ROCKY)
    assert inp.soil_group == SoilGroup.ROCKY
    assert inp.collapsible is None
    assert inp.active is None
    assert inp.liquefiable is None
    assert inp.sliding_potential is None
    assert inp.stratification_uniform_horizontal is True


def test_result_dataclass_defaults():
    r = TerrainConditionResult()
    assert r.valid is False
    assert r.condition is None
    assert r.matched_table is None
    assert r.matched_row is None
    assert r.interpolated is False
    assert r.warnings == []
    assert r.errors == []
```

- [ ] **Step 2: Run test to verify it fails**

```bash
python3 -m pytest tests/test_np_074_2022_terrain_condition.py -v
```

Expected: `ModuleNotFoundError` or `ImportError`

- [ ] **Step 3: Add enums to `src/tabularium/enums.py`**

Append after the last existing class (`SoilCategory`):

```python
class TerrainCondition(_LabeledEnum):
    GOOD      = ("good",      "Terenuri bune")
    MEDIUM    = ("medium",    "Terenuri medii")
    DIFFICULT = ("difficult", "Terenuri dificile")


class SoilGroup(_LabeledEnum):
    ROCKY         = ("rocky",         "Roci stâncoase și semistâncoase")
    NON_COHESIVE  = ("non_cohesive",  "Pământuri necoezive (nisipuri, pietrișuri, bolovănișuri)")
    COHESIVE_FINE = ("cohesive_fine", "Pământuri fine coezive")
    FILL          = ("fill",          "Umpluturi")


class FillCategory(_LabeledEnum):
    CONTROLLED_COMPACTED   = ("controlled_compacted",   "Umpluturi compactate controlat")
    KNOWN_ORIGIN_ORGANIZED = ("known_origin_organized", "Umpluturi de proveniență cunoscută, realizate organizat")
    UNCONTROLLED           = ("uncontrolled",           "Umpluturi executate necontrolat")
    HOUSEHOLD              = ("household",              "Umpluturi din resturi menajere")
```

Also add `LOOSE` to `RelativeDensity`:

```python
class RelativeDensity(_LabeledEnum):
    LOOSE  = ("loose",  "Afânată")    # ← add this line
    MEDIUM = ("medium", "Medie")
    DENSE  = ("dense",  "Densă")
```

- [ ] **Step 4: Create `src/tabularium/np_074_2022/__init__.py`**

```python
from __future__ import annotations
```

- [ ] **Step 5: Create `src/tabularium/np_074_2022/terrain_condition.py` with dataclasses only**

```python
from __future__ import annotations

from dataclasses import dataclass

from ..enums import (
    FillCategory,
    PlasticityClass,
    RelativeDensity,
    SoilGroup,
    TerrainCondition,
)
from ..models import CodeSource, LookupResult

_SOURCE = CodeSource(code="NP 074:2022", table="Tabelele A.1–A.3", section="Anexa A")

_E_MAX: dict[PlasticityClass, float] = {
    PlasticityClass.LOW:    0.7,
    PlasticityClass.MEDIUM: 1.0,
    PlasticityClass.HIGH:   1.1,
}


@dataclass
class TerrainConditionInput:
    soil_group: SoilGroup

    # NON_COHESIVE
    relative_density: RelativeDensity | None = None

    # COHESIVE_FINE
    plasticity_class: PlasticityClass | None = None
    void_ratio: float | None = None
    consistency_index: float | None = None

    # FILL
    fill_category: FillCategory | None = None
    organic_content_pct: float = 0.0
    fill_age_years: float | None = None

    # General
    stratification_uniform_horizontal: bool = True

    # Optional override flags
    collapsible: bool | None = None
    active: bool | None = None
    liquefiable: bool | None = None
    sliding_potential: bool | None = None


@dataclass
class TerrainConditionResult(LookupResult):
    condition: TerrainCondition | None = None
    matched_table: str | None = None
    matched_row: int | None = None


def classify_terrain_condition(inp: TerrainConditionInput) -> TerrainConditionResult:
    raise NotImplementedError
```

- [ ] **Step 6: Run tests to verify they pass**

```bash
python3 -m pytest tests/test_np_074_2022_terrain_condition.py::test_imports tests/test_np_074_2022_terrain_condition.py::test_input_dataclass_instantiation tests/test_np_074_2022_terrain_condition.py::test_result_dataclass_defaults -v
```

Expected: 3 passed

- [ ] **Step 7: Commit**

```bash
git add src/tabularium/enums.py src/tabularium/np_074_2022/__init__.py src/tabularium/np_074_2022/terrain_condition.py tests/test_np_074_2022_terrain_condition.py
git commit -m "feat(np074): add enums, module skeleton for terrain condition classifier"
```

---

## Task 2: Override flags

**Files:**
- Modify: `tests/test_np_074_2022_terrain_condition.py` — add override flag tests
- Modify: `src/tabularium/np_074_2022/terrain_condition.py` — implement flags logic + helpers

- [ ] **Step 1: Add override flag tests to the test file**

Append to `tests/test_np_074_2022_terrain_condition.py`:

```python
from tabularium.enums import PlasticityClass


# ── Override flags ─────────────────────────────────────────────────────────────

def test_collapsible_true_returns_difficult_a3_row4():
    inp = TerrainConditionInput(
        soil_group=SoilGroup.COHESIVE_FINE,
        plasticity_class=PlasticityClass.LOW,
        void_ratio=0.6,
        consistency_index=0.80,
        collapsible=True,
    )
    r = classify_terrain_condition(inp)
    assert r.valid is True
    assert r.condition == TerrainCondition.DIFFICULT
    assert r.matched_table == "A.3"
    assert r.matched_row == 4


def test_active_true_returns_difficult_a3_row5():
    inp = TerrainConditionInput(
        soil_group=SoilGroup.COHESIVE_FINE,
        plasticity_class=PlasticityClass.HIGH,
        void_ratio=1.0,
        consistency_index=0.80,
        active=True,
    )
    r = classify_terrain_condition(inp)
    assert r.valid is True
    assert r.condition == TerrainCondition.DIFFICULT
    assert r.matched_table == "A.3"
    assert r.matched_row == 5


def test_liquefiable_true_returns_difficult_a3_row2():
    inp = TerrainConditionInput(
        soil_group=SoilGroup.NON_COHESIVE,
        relative_density=RelativeDensity.DENSE,
        liquefiable=True,
    )
    r = classify_terrain_condition(inp)
    assert r.valid is True
    assert r.condition == TerrainCondition.DIFFICULT
    assert r.matched_table == "A.3"
    assert r.matched_row == 2


def test_sliding_potential_true_returns_difficult_a3_row7():
    inp = TerrainConditionInput(
        soil_group=SoilGroup.ROCKY,
        sliding_potential=True,
    )
    r = classify_terrain_condition(inp)
    assert r.valid is True
    assert r.condition == TerrainCondition.DIFFICULT
    assert r.matched_table == "A.3"
    assert r.matched_row == 7


def test_collapsible_false_does_not_override():
    # collapsible=False → does not trigger override, falls through to normal logic
    inp = TerrainConditionInput(
        soil_group=SoilGroup.ROCKY,
        collapsible=False,
    )
    r = classify_terrain_condition(inp)
    assert r.condition == TerrainCondition.GOOD
    assert r.matched_table == "A.1"
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python3 -m pytest tests/test_np_074_2022_terrain_condition.py -k "override or collapsible or liquefiable or sliding or active_true" -v
```

Expected: `NotImplementedError`

- [ ] **Step 3: Implement helpers and override flags in `terrain_condition.py`**

Replace `classify_terrain_condition` and add helpers:

```python
def _make_result(
    condition: TerrainCondition,
    table: str,
    row: int,
    warnings: list[str] | None = None,
) -> TerrainConditionResult:
    r = TerrainConditionResult(source=_SOURCE)
    r.condition = condition
    r.matched_table = table
    r.matched_row = row
    r.valid = True
    if warnings:
        r.warnings.extend(warnings)
    return r


def _error(msg: str) -> TerrainConditionResult:
    r = TerrainConditionResult(source=_SOURCE)
    r.errors.append(msg)
    return r


def classify_terrain_condition(inp: TerrainConditionInput) -> TerrainConditionResult:
    if inp.collapsible is True:
        return _make_result(TerrainCondition.DIFFICULT, "A.3", 4)
    if inp.active is True:
        return _make_result(TerrainCondition.DIFFICULT, "A.3", 5)
    if inp.liquefiable is True:
        return _make_result(TerrainCondition.DIFFICULT, "A.3", 2)
    if inp.sliding_potential is True:
        return _make_result(TerrainCondition.DIFFICULT, "A.3", 7)

    try:
        soil_group = SoilGroup(inp.soil_group)
    except ValueError:
        return _error(f"Grup de sol necunoscut: {inp.soil_group!r}.")

    if soil_group == SoilGroup.ROCKY:
        return _classify_rocky(inp)
    if soil_group == SoilGroup.NON_COHESIVE:
        return _classify_non_cohesive(inp)
    if soil_group == SoilGroup.COHESIVE_FINE:
        return _classify_cohesive_fine(inp)
    return _classify_fill(inp)


def _classify_rocky(inp: TerrainConditionInput) -> TerrainConditionResult:
    raise NotImplementedError


def _classify_non_cohesive(inp: TerrainConditionInput) -> TerrainConditionResult:
    raise NotImplementedError


def _classify_cohesive_fine(inp: TerrainConditionInput) -> TerrainConditionResult:
    raise NotImplementedError


def _classify_fill(inp: TerrainConditionInput) -> TerrainConditionResult:
    raise NotImplementedError
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python3 -m pytest tests/test_np_074_2022_terrain_condition.py -k "test_collapsible or test_active_true or test_liquefiable or test_sliding or test_collapsible_false" -v
```

Expected: 5 passed

- [ ] **Step 5: Commit**

```bash
git add tests/test_np_074_2022_terrain_condition.py src/tabularium/np_074_2022/terrain_condition.py
git commit -m "feat(np074): implement override flags (collapsible, active, liquefiable, sliding_potential)"
```

---

## Task 3: ROCKY and NON_COHESIVE classification

**Files:**
- Modify: `tests/test_np_074_2022_terrain_condition.py`
- Modify: `src/tabularium/np_074_2022/terrain_condition.py`

- [ ] **Step 1: Add ROCKY and NON_COHESIVE tests**

Append to `tests/test_np_074_2022_terrain_condition.py`:

```python
# ── ROCKY ─────────────────────────────────────────────────────────────────────

def test_rocky_uniform_horizontal_returns_good_a1_row6():
    r = classify_terrain_condition(
        TerrainConditionInput(soil_group=SoilGroup.ROCKY)
    )
    assert r.valid is True
    assert r.condition == TerrainCondition.GOOD
    assert r.matched_table == "A.1"
    assert r.matched_row == 6
    assert r.errors == []


def test_rocky_non_uniform_returns_error():
    r = classify_terrain_condition(
        TerrainConditionInput(
            soil_group=SoilGroup.ROCKY,
            stratification_uniform_horizontal=False,
        )
    )
    assert r.valid is False
    assert len(r.errors) == 1


def test_rocky_source_metadata():
    r = classify_terrain_condition(
        TerrainConditionInput(soil_group=SoilGroup.ROCKY)
    )
    assert r.source.code == "NP 074:2022"
    assert r.source.table == "Tabelele A.1–A.3"


# ── NON_COHESIVE ──────────────────────────────────────────────────────────────

def test_non_cohesive_dense_uniform_returns_good_a1_row2():
    r = classify_terrain_condition(
        TerrainConditionInput(
            soil_group=SoilGroup.NON_COHESIVE,
            relative_density=RelativeDensity.DENSE,
        )
    )
    assert r.valid is True
    assert r.condition == TerrainCondition.GOOD
    assert r.matched_table == "A.1"
    assert r.matched_row == 2


def test_non_cohesive_medium_uniform_returns_medium_a2_row1():
    r = classify_terrain_condition(
        TerrainConditionInput(
            soil_group=SoilGroup.NON_COHESIVE,
            relative_density=RelativeDensity.MEDIUM,
        )
    )
    assert r.valid is True
    assert r.condition == TerrainCondition.MEDIUM
    assert r.matched_table == "A.2"
    assert r.matched_row == 1


def test_non_cohesive_loose_returns_difficult_a3_row1():
    r = classify_terrain_condition(
        TerrainConditionInput(
            soil_group=SoilGroup.NON_COHESIVE,
            relative_density=RelativeDensity.LOOSE,
        )
    )
    assert r.valid is True
    assert r.condition == TerrainCondition.DIFFICULT
    assert r.matched_table == "A.3"
    assert r.matched_row == 1


def test_non_cohesive_dense_non_uniform_returns_error():
    r = classify_terrain_condition(
        TerrainConditionInput(
            soil_group=SoilGroup.NON_COHESIVE,
            relative_density=RelativeDensity.DENSE,
            stratification_uniform_horizontal=False,
        )
    )
    assert r.valid is False
    assert len(r.errors) == 1


def test_non_cohesive_missing_density_returns_error():
    r = classify_terrain_condition(
        TerrainConditionInput(soil_group=SoilGroup.NON_COHESIVE)
    )
    assert r.valid is False
    assert len(r.errors) == 1


def test_non_cohesive_loose_ignores_stratification():
    # LOOSE → DIFFICULT regardless of stratification flag
    r = classify_terrain_condition(
        TerrainConditionInput(
            soil_group=SoilGroup.NON_COHESIVE,
            relative_density=RelativeDensity.LOOSE,
            stratification_uniform_horizontal=False,
        )
    )
    assert r.valid is True
    assert r.condition == TerrainCondition.DIFFICULT
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python3 -m pytest tests/test_np_074_2022_terrain_condition.py -k "rocky or non_cohesive" -v
```

Expected: `NotImplementedError` for all

- [ ] **Step 3: Implement `_classify_rocky` and `_classify_non_cohesive`**

Replace the two stub functions in `terrain_condition.py`:

```python
def _classify_rocky(inp: TerrainConditionInput) -> TerrainConditionResult:
    if not inp.stratification_uniform_horizontal:
        return _error(
            "Roci cu stratificație neuniformă nu sunt acoperite de tabelele A.1–A.3."
        )
    return _make_result(TerrainCondition.GOOD, "A.1", 6)


def _classify_non_cohesive(inp: TerrainConditionInput) -> TerrainConditionResult:
    if inp.relative_density is None:
        return _error("relative_density este necesar pentru NON_COHESIVE.")

    try:
        density = RelativeDensity(inp.relative_density)
    except ValueError:
        return _error(f"Densitate relativă necunoscută: {inp.relative_density!r}.")

    if density == RelativeDensity.LOOSE:
        return _make_result(TerrainCondition.DIFFICULT, "A.3", 1)

    if not inp.stratification_uniform_horizontal:
        return _error(
            "Pământuri necoezive dense/medii necesită stratificație uniformă și orizontală conform A.1/A.2."
        )

    if density == RelativeDensity.DENSE:
        return _make_result(TerrainCondition.GOOD, "A.1", 2)
    return _make_result(TerrainCondition.MEDIUM, "A.2", 1)
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python3 -m pytest tests/test_np_074_2022_terrain_condition.py -k "rocky or non_cohesive" -v
```

Expected: 9 passed

- [ ] **Step 5: Run full suite to catch regressions**

```bash
python3 -m pytest tests/ -q
```

Expected: all passed

- [ ] **Step 6: Commit**

```bash
git add tests/test_np_074_2022_terrain_condition.py src/tabularium/np_074_2022/terrain_condition.py
git commit -m "feat(np074): implement ROCKY and NON_COHESIVE terrain classification"
```

---

## Task 4: COHESIVE_FINE classification

**Files:**
- Modify: `tests/test_np_074_2022_terrain_condition.py`
- Modify: `src/tabularium/np_074_2022/terrain_condition.py`

- [ ] **Step 1: Add COHESIVE_FINE tests**

Append to `tests/test_np_074_2022_terrain_condition.py`:

```python
# ── COHESIVE_FINE ─────────────────────────────────────────────────────────────

# IC < 0.5 → DIFFICULT A.3 row 3

def test_cohesive_fine_ic_below_0_5_returns_difficult_a3_row3():
    r = classify_terrain_condition(
        TerrainConditionInput(
            soil_group=SoilGroup.COHESIVE_FINE,
            plasticity_class=PlasticityClass.MEDIUM,
            void_ratio=0.8,
            consistency_index=0.4,
        )
    )
    assert r.valid is True
    assert r.condition == TerrainCondition.DIFFICULT
    assert r.matched_table == "A.3"
    assert r.matched_row == 3


def test_cohesive_fine_ic_exactly_0_5_is_medium():
    # IC=0.5 is the boundary — belongs to [0.5, 0.75) band → MEDIUM
    r = classify_terrain_condition(
        TerrainConditionInput(
            soil_group=SoilGroup.COHESIVE_FINE,
            plasticity_class=PlasticityClass.LOW,
            void_ratio=0.6,
            consistency_index=0.5,
        )
    )
    assert r.valid is True
    assert r.condition == TerrainCondition.MEDIUM


# IC ∈ [0.5, 0.75) → MEDIUM A.2 rows 2/3/4

def test_cohesive_fine_low_medium_band_a2_row2():
    r = classify_terrain_condition(
        TerrainConditionInput(
            soil_group=SoilGroup.COHESIVE_FINE,
            plasticity_class=PlasticityClass.LOW,
            void_ratio=0.6,
            consistency_index=0.60,
        )
    )
    assert r.valid is True
    assert r.condition == TerrainCondition.MEDIUM
    assert r.matched_table == "A.2"
    assert r.matched_row == 2


def test_cohesive_fine_medium_medium_band_a2_row3():
    r = classify_terrain_condition(
        TerrainConditionInput(
            soil_group=SoilGroup.COHESIVE_FINE,
            plasticity_class=PlasticityClass.MEDIUM,
            void_ratio=0.8,
            consistency_index=0.60,
        )
    )
    assert r.valid is True
    assert r.condition == TerrainCondition.MEDIUM
    assert r.matched_table == "A.2"
    assert r.matched_row == 3


def test_cohesive_fine_high_medium_band_a2_row4():
    r = classify_terrain_condition(
        TerrainConditionInput(
            soil_group=SoilGroup.COHESIVE_FINE,
            plasticity_class=PlasticityClass.HIGH,
            void_ratio=1.0,
            consistency_index=0.60,
        )
    )
    assert r.valid is True
    assert r.condition == TerrainCondition.MEDIUM
    assert r.matched_table == "A.2"
    assert r.matched_row == 4


# IC ≥ 0.75 → GOOD A.1 rows 3/4/5

def test_cohesive_fine_low_good_band_a1_row3():
    r = classify_terrain_condition(
        TerrainConditionInput(
            soil_group=SoilGroup.COHESIVE_FINE,
            plasticity_class=PlasticityClass.LOW,
            void_ratio=0.6,
            consistency_index=0.80,
            collapsible=False,
        )
    )
    assert r.valid is True
    assert r.condition == TerrainCondition.GOOD
    assert r.matched_table == "A.1"
    assert r.matched_row == 3
    assert r.errors == []


def test_cohesive_fine_medium_good_band_a1_row4():
    r = classify_terrain_condition(
        TerrainConditionInput(
            soil_group=SoilGroup.COHESIVE_FINE,
            plasticity_class=PlasticityClass.MEDIUM,
            void_ratio=0.8,
            consistency_index=0.80,
            collapsible=False,
            active=False,
        )
    )
    assert r.valid is True
    assert r.condition == TerrainCondition.GOOD
    assert r.matched_table == "A.1"
    assert r.matched_row == 4
    assert r.warnings == []


def test_cohesive_fine_high_good_band_a1_row5():
    r = classify_terrain_condition(
        TerrainConditionInput(
            soil_group=SoilGroup.COHESIVE_FINE,
            plasticity_class=PlasticityClass.HIGH,
            void_ratio=1.0,
            consistency_index=0.80,
            collapsible=False,
            active=False,
        )
    )
    assert r.valid is True
    assert r.condition == TerrainCondition.GOOD
    assert r.matched_table == "A.1"
    assert r.matched_row == 5
    assert r.warnings == []


# Warnings for NP 125 / NP 126

def test_cohesive_fine_good_band_collapsible_none_emits_np125_warning():
    r = classify_terrain_condition(
        TerrainConditionInput(
            soil_group=SoilGroup.COHESIVE_FINE,
            plasticity_class=PlasticityClass.LOW,
            void_ratio=0.6,
            consistency_index=0.80,
            collapsible=None,
        )
    )
    assert r.valid is True
    assert r.condition == TerrainCondition.GOOD
    assert any("NP 125" in w for w in r.warnings)


def test_cohesive_fine_medium_good_band_active_none_emits_np126_warning():
    r = classify_terrain_condition(
        TerrainConditionInput(
            soil_group=SoilGroup.COHESIVE_FINE,
            plasticity_class=PlasticityClass.MEDIUM,
            void_ratio=0.8,
            consistency_index=0.80,
            collapsible=False,
            active=None,
        )
    )
    assert r.valid is True
    assert any("NP 126" in w for w in r.warnings)


def test_cohesive_fine_low_good_band_active_none_no_np126_warning():
    # LOW plasticity — NP 126 warning does NOT apply
    r = classify_terrain_condition(
        TerrainConditionInput(
            soil_group=SoilGroup.COHESIVE_FINE,
            plasticity_class=PlasticityClass.LOW,
            void_ratio=0.6,
            consistency_index=0.80,
            collapsible=False,
            active=None,
        )
    )
    assert r.valid is True
    assert not any("NP 126" in w for w in r.warnings)


def test_cohesive_fine_active_false_no_np126_warning():
    # active=False → not active, no warning
    r = classify_terrain_condition(
        TerrainConditionInput(
            soil_group=SoilGroup.COHESIVE_FINE,
            plasticity_class=PlasticityClass.HIGH,
            void_ratio=1.0,
            consistency_index=0.60,
            active=False,
        )
    )
    assert r.valid is True
    assert r.condition == TerrainCondition.MEDIUM
    assert not any("NP 126" in w for w in r.warnings)


def test_cohesive_fine_medium_band_medium_plasticity_active_none_emits_np126_warning():
    r = classify_terrain_condition(
        TerrainConditionInput(
            soil_group=SoilGroup.COHESIVE_FINE,
            plasticity_class=PlasticityClass.MEDIUM,
            void_ratio=0.8,
            consistency_index=0.60,
            active=None,
        )
    )
    assert r.valid is True
    assert r.condition == TerrainCondition.MEDIUM
    assert any("NP 126" in w for w in r.warnings)


def test_cohesive_fine_medium_band_low_plasticity_active_none_no_np126_warning():
    r = classify_terrain_condition(
        TerrainConditionInput(
            soil_group=SoilGroup.COHESIVE_FINE,
            plasticity_class=PlasticityClass.LOW,
            void_ratio=0.6,
            consistency_index=0.60,
            active=None,
        )
    )
    assert r.valid is True
    assert not any("NP 126" in w for w in r.warnings)


# Out-of-range e

def test_cohesive_fine_e_exceeds_max_for_low_plasticity_returns_error():
    # LOW: e_max = 0.7
    r = classify_terrain_condition(
        TerrainConditionInput(
            soil_group=SoilGroup.COHESIVE_FINE,
            plasticity_class=PlasticityClass.LOW,
            void_ratio=1.5,
            consistency_index=0.80,
        )
    )
    assert r.valid is False
    assert len(r.errors) == 1


def test_cohesive_fine_e_at_max_is_valid():
    # HIGH: e_max=1.1, e=1.1 → valid
    r = classify_terrain_condition(
        TerrainConditionInput(
            soil_group=SoilGroup.COHESIVE_FINE,
            plasticity_class=PlasticityClass.HIGH,
            void_ratio=1.1,
            consistency_index=0.80,
            collapsible=False,
            active=False,
        )
    )
    assert r.valid is True
    assert r.condition == TerrainCondition.GOOD


# Missing required fields

def test_cohesive_fine_missing_plasticity_class_returns_error():
    r = classify_terrain_condition(
        TerrainConditionInput(
            soil_group=SoilGroup.COHESIVE_FINE,
            void_ratio=0.6,
            consistency_index=0.80,
        )
    )
    assert r.valid is False
    assert len(r.errors) == 1


def test_cohesive_fine_missing_consistency_index_returns_error():
    r = classify_terrain_condition(
        TerrainConditionInput(
            soil_group=SoilGroup.COHESIVE_FINE,
            plasticity_class=PlasticityClass.LOW,
            void_ratio=0.6,
        )
    )
    assert r.valid is False
    assert len(r.errors) == 1


def test_cohesive_fine_missing_void_ratio_returns_error():
    r = classify_terrain_condition(
        TerrainConditionInput(
            soil_group=SoilGroup.COHESIVE_FINE,
            plasticity_class=PlasticityClass.LOW,
            consistency_index=0.80,
        )
    )
    assert r.valid is False
    assert len(r.errors) == 1
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python3 -m pytest tests/test_np_074_2022_terrain_condition.py -k "cohesive_fine" -v
```

Expected: `NotImplementedError` for all

- [ ] **Step 3: Implement `_classify_cohesive_fine`**

Replace the stub in `terrain_condition.py`:

```python
def _classify_cohesive_fine(inp: TerrainConditionInput) -> TerrainConditionResult:
    if inp.plasticity_class is None:
        return _error("plasticity_class este necesar pentru COHESIVE_FINE.")
    if inp.void_ratio is None:
        return _error("void_ratio este necesar pentru COHESIVE_FINE.")
    if inp.consistency_index is None:
        return _error("consistency_index este necesar pentru COHESIVE_FINE.")

    try:
        pc = PlasticityClass(inp.plasticity_class)
    except ValueError:
        return _error(f"Clasă de plasticitate necunoscută: {inp.plasticity_class!r}.")

    ic = inp.consistency_index
    e = inp.void_ratio
    e_max = _E_MAX[pc]

    if ic < 0.5:
        return _make_result(TerrainCondition.DIFFICULT, "A.3", 3)

    if ic < 0.75:
        if e > e_max:
            return _error(
                f"Combinație e={e}, IC={ic} în afara domeniului tabelelor A.1–A.3 "
                f"pentru plasticitate {pc!r} (e_max={e_max})."
            )
        row = {PlasticityClass.LOW: 2, PlasticityClass.MEDIUM: 3, PlasticityClass.HIGH: 4}[pc]
        warnings: list[str] = []
        if inp.active is None and pc in (PlasticityClass.MEDIUM, PlasticityClass.HIGH):
            warnings.append(
                "Verificați activitatea conform NP 126 — "
                "dacă activitate mare/foarte mare → A.3 rând 5 (DIFFICULT)."
            )
        return _make_result(TerrainCondition.MEDIUM, "A.2", row, warnings)

    # ic >= 0.75
    if e > e_max:
        return _error(
            f"Combinație e={e}, IC={ic} în afara domeniului tabelelor A.1–A.3 "
            f"pentru plasticitate {pc!r} (e_max={e_max})."
        )
    row = {PlasticityClass.LOW: 3, PlasticityClass.MEDIUM: 4, PlasticityClass.HIGH: 5}[pc]
    warnings = []
    if inp.collapsible is None:
        warnings.append(
            "Verificați sensibilitatea la umezire conform NP 125 — "
            "dacă PSU → A.3 rând 4 (DIFFICULT)."
        )
    if inp.active is None and pc in (PlasticityClass.MEDIUM, PlasticityClass.HIGH):
        warnings.append(
            "Verificați umflările/contracțiile conform NP 126 — "
            "dacă activitate mare/foarte mare → A.3 rând 5 (DIFFICULT)."
        )
    return _make_result(TerrainCondition.GOOD, "A.1", row, warnings)
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python3 -m pytest tests/test_np_074_2022_terrain_condition.py -k "cohesive_fine" -v
```

Expected: all passed

- [ ] **Step 5: Run full suite to catch regressions**

```bash
python3 -m pytest tests/ -q
```

Expected: all passed

- [ ] **Step 6: Commit**

```bash
git add tests/test_np_074_2022_terrain_condition.py src/tabularium/np_074_2022/terrain_condition.py
git commit -m "feat(np074): implement COHESIVE_FINE terrain classification with NP 125/126 warnings"
```

---

## Task 5: FILL classification

**Files:**
- Modify: `tests/test_np_074_2022_terrain_condition.py`
- Modify: `src/tabularium/np_074_2022/terrain_condition.py`

- [ ] **Step 1: Add FILL tests**

Append to `tests/test_np_074_2022_terrain_condition.py`:

```python
# ── FILL ──────────────────────────────────────────────────────────────────────

def test_fill_controlled_compacted_returns_good_a1_row7():
    r = classify_terrain_condition(
        TerrainConditionInput(
            soil_group=SoilGroup.FILL,
            fill_category=FillCategory.CONTROLLED_COMPACTED,
        )
    )
    assert r.valid is True
    assert r.condition == TerrainCondition.GOOD
    assert r.matched_table == "A.1"
    assert r.matched_row == 7


def test_fill_household_returns_difficult_a3_row9():
    r = classify_terrain_condition(
        TerrainConditionInput(
            soil_group=SoilGroup.FILL,
            fill_category=FillCategory.HOUSEHOLD,
        )
    )
    assert r.valid is True
    assert r.condition == TerrainCondition.DIFFICULT
    assert r.matched_table == "A.3"
    assert r.matched_row == 9


def test_fill_known_origin_low_organic_returns_medium_a2_row6():
    r = classify_terrain_condition(
        TerrainConditionInput(
            soil_group=SoilGroup.FILL,
            fill_category=FillCategory.KNOWN_ORIGIN_ORGANIZED,
            organic_content_pct=3.0,
        )
    )
    assert r.valid is True
    assert r.condition == TerrainCondition.MEDIUM
    assert r.matched_table == "A.2"
    assert r.matched_row == 6


def test_fill_known_origin_high_organic_returns_difficult_a3_row6():
    r = classify_terrain_condition(
        TerrainConditionInput(
            soil_group=SoilGroup.FILL,
            fill_category=FillCategory.KNOWN_ORIGIN_ORGANIZED,
            organic_content_pct=6.0,
        )
    )
    assert r.valid is True
    assert r.condition == TerrainCondition.DIFFICULT
    assert r.matched_table == "A.3"
    assert r.matched_row == 6


def test_fill_known_origin_exactly_5_pct_organic_returns_difficult():
    # boundary: >= 5% → DIFFICULT
    r = classify_terrain_condition(
        TerrainConditionInput(
            soil_group=SoilGroup.FILL,
            fill_category=FillCategory.KNOWN_ORIGIN_ORGANIZED,
            organic_content_pct=5.0,
        )
    )
    assert r.valid is True
    assert r.condition == TerrainCondition.DIFFICULT


def test_fill_uncontrolled_old_returns_medium_a2_row6():
    r = classify_terrain_condition(
        TerrainConditionInput(
            soil_group=SoilGroup.FILL,
            fill_category=FillCategory.UNCONTROLLED,
            fill_age_years=15.0,
        )
    )
    assert r.valid is True
    assert r.condition == TerrainCondition.MEDIUM
    assert r.matched_table == "A.2"
    assert r.matched_row == 6
    assert r.warnings == []


def test_fill_uncontrolled_young_returns_difficult_a3_row8():
    r = classify_terrain_condition(
        TerrainConditionInput(
            soil_group=SoilGroup.FILL,
            fill_category=FillCategory.UNCONTROLLED,
            fill_age_years=5.0,
        )
    )
    assert r.valid is True
    assert r.condition == TerrainCondition.DIFFICULT
    assert r.matched_table == "A.3"
    assert r.matched_row == 8


def test_fill_uncontrolled_exactly_10_years_returns_medium():
    # boundary: < 10 → DIFFICULT, so 10 → MEDIUM (in grey zone [10,12])
    r = classify_terrain_condition(
        TerrainConditionInput(
            soil_group=SoilGroup.FILL,
            fill_category=FillCategory.UNCONTROLLED,
            fill_age_years=10.0,
        )
    )
    assert r.valid is True
    assert r.condition == TerrainCondition.MEDIUM
    assert len(r.warnings) == 1


def test_fill_uncontrolled_grey_zone_emits_warning():
    r = classify_terrain_condition(
        TerrainConditionInput(
            soil_group=SoilGroup.FILL,
            fill_category=FillCategory.UNCONTROLLED,
            fill_age_years=11.0,
        )
    )
    assert r.valid is True
    assert r.condition == TerrainCondition.MEDIUM
    assert len(r.warnings) == 1
    assert "10" in r.warnings[0] and "12" in r.warnings[0]


def test_fill_uncontrolled_missing_age_returns_error():
    r = classify_terrain_condition(
        TerrainConditionInput(
            soil_group=SoilGroup.FILL,
            fill_category=FillCategory.UNCONTROLLED,
        )
    )
    assert r.valid is False
    assert len(r.errors) == 1


def test_fill_missing_category_returns_error():
    r = classify_terrain_condition(
        TerrainConditionInput(soil_group=SoilGroup.FILL)
    )
    assert r.valid is False
    assert len(r.errors) == 1
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python3 -m pytest tests/test_np_074_2022_terrain_condition.py -k "fill" -v
```

Expected: `NotImplementedError` for all

- [ ] **Step 3: Implement `_classify_fill`**

Replace the stub in `terrain_condition.py`:

```python
def _classify_fill(inp: TerrainConditionInput) -> TerrainConditionResult:
    if inp.fill_category is None:
        return _error("fill_category este necesar pentru FILL.")

    try:
        fc = FillCategory(inp.fill_category)
    except ValueError:
        return _error(f"Categorie umpluturi necunoscută: {inp.fill_category!r}.")

    if fc == FillCategory.CONTROLLED_COMPACTED:
        return _make_result(TerrainCondition.GOOD, "A.1", 7)

    if fc == FillCategory.HOUSEHOLD:
        return _make_result(TerrainCondition.DIFFICULT, "A.3", 9)

    if fc == FillCategory.KNOWN_ORIGIN_ORGANIZED:
        if inp.organic_content_pct >= 5.0:
            return _make_result(TerrainCondition.DIFFICULT, "A.3", 6)
        return _make_result(TerrainCondition.MEDIUM, "A.2", 6)

    # UNCONTROLLED
    if inp.fill_age_years is None:
        return _error("fill_age_years este necesar pentru UNCONTROLLED.")
    if inp.fill_age_years < 10:
        return _make_result(TerrainCondition.DIFFICULT, "A.3", 8)
    warnings: list[str] = []
    if inp.fill_age_years <= 12:
        warnings.append(
            "Vârstă la limita zonei gri 10–12 ani (A.2 rând 6 / A.3 rând 8) — verificați cu normativul."
        )
    return _make_result(TerrainCondition.MEDIUM, "A.2", 6, warnings)
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python3 -m pytest tests/test_np_074_2022_terrain_condition.py -k "fill" -v
```

Expected: all passed

- [ ] **Step 5: Run full suite**

```bash
python3 -m pytest tests/ -q
```

Expected: all passed

- [ ] **Step 6: Commit**

```bash
git add tests/test_np_074_2022_terrain_condition.py src/tabularium/np_074_2022/terrain_condition.py
git commit -m "feat(np074): implement FILL terrain classification"
```

---

## Task 6: Registry integration

**Files:**
- Create: `src/tabularium/np_074_2022/registry.py`
- Modify: `src/tabularium/registry.py`
- Modify: `tests/test_np_074_2022_terrain_condition.py` — add registry smoke test
- Modify: `CLAUDE.md` — update Package structure section

- [ ] **Step 1: Add registry smoke test**

Append to `tests/test_np_074_2022_terrain_condition.py`:

```python
# ── Registry ──────────────────────────────────────────────────────────────────

def test_registered_in_global_registry():
    from tabularium.registry import registry
    entry = registry.get("np_074_2022.terrain_condition")
    assert entry is not None
    assert callable(entry.func)
    assert entry.normative == "NP 074:2022"
```

- [ ] **Step 2: Run test to verify it fails**

```bash
python3 -m pytest tests/test_np_074_2022_terrain_condition.py::test_registered_in_global_registry -v
```

Expected: `KeyError` — tabel necunoscut

- [ ] **Step 3: Create `src/tabularium/np_074_2022/registry.py`**

```python
from __future__ import annotations

from tabularium.core.registry import Registry, TableEntry
from .terrain_condition import classify_terrain_condition as _classify

registry = Registry()

registry.register("terrain_condition", TableEntry(
    func=_classify,
    normative="NP 074:2022",
    table_id="A.1–A.3",
    description="Clasificarea condițiilor de teren (Tabelele A.1–A.3, Anexa A)",
))
```

- [ ] **Step 4: Update `src/tabularium/registry.py`**

Current content:
```python
from __future__ import annotations

from tabularium.core.registry import Registry, TableEntry  # noqa: F401 — re-exported
from tabularium.np_112_2014.registry import registry as _np112
from tabularium.np_122_2010.registry import registry as _np122

registry = Registry()
registry.include(_np112, namespace="np_112_2014")
registry.include(_np122, namespace="np_122_2010")

__all__ = ["registry", "Registry", "TableEntry"]
```

New content:
```python
from __future__ import annotations

from tabularium.core.registry import Registry, TableEntry  # noqa: F401 — re-exported
from tabularium.np_074_2022.registry import registry as _np074
from tabularium.np_112_2014.registry import registry as _np112
from tabularium.np_122_2010.registry import registry as _np122

registry = Registry()
registry.include(_np074, namespace="np_074_2022")
registry.include(_np112, namespace="np_112_2014")
registry.include(_np122, namespace="np_122_2010")

__all__ = ["registry", "Registry", "TableEntry"]
```

- [ ] **Step 5: Run registry test to verify it passes**

```bash
python3 -m pytest tests/test_np_074_2022_terrain_condition.py::test_registered_in_global_registry -v
```

Expected: PASS

- [ ] **Step 6: Run full suite**

```bash
python3 -m pytest tests/ -q
```

Expected: all passed

- [ ] **Step 7: Update CLAUDE.md Package structure section**

In `CLAUDE.md`, add to the package structure under `src/tabularium/`:

```
├── np_074_2022/
│   ├── __init__.py
│   ├── registry.py
│   └── terrain_condition.py                         # Tabelele A.1–A.3 — clasificarea condițiilor de teren
```

- [ ] **Step 8: Commit**

```bash
git add src/tabularium/np_074_2022/registry.py src/tabularium/registry.py tests/test_np_074_2022_terrain_condition.py CLAUDE.md
git commit -m "feat(np074): wire terrain condition classifier into global registry"
```
