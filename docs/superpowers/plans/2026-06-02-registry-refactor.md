# Registry Refactor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the flat `REGISTRY` dict with a composable `Registry` class — each normative owns a local registry, a top-level assembly point merges them via `include()`.

**Architecture:** `tabularium/core/registry.py` defines pure types (`Registry`, `TableEntry`) with no global state. Each normative subfolder gets a `registry.py` that instantiates a local `Registry` and registers its functions. `tabularium/registry.py` (replaced) creates the global instance and calls `include()` for each normative.

**Tech Stack:** Pure Python stdlib (`dataclasses`, `collections.abc`). No new dependencies.

**Spec:** `docs/superpowers/specs/2026-06-02-registry-refactor-design.md`

---

## File Map

| Action | Path | Role |
|--------|------|------|
| Create | `src/tabularium/core/__init__.py` | Package marker (empty) |
| Create | `src/tabularium/core/registry.py` | `Registry` class + `TableEntry` dataclass |
| Create | `src/tabularium/np_112_2014/registry.py` | Local registry with all np112 registrations |
| Create | `src/tabularium/np_122_2010/registry.py` | Local registry with all np122 registrations |
| Replace | `src/tabularium/registry.py` | Global instance + `include()` assembly |
| Modify | `src/tabularium/__init__.py` | Expose `registry` |
| Create | `tests/test_core_registry.py` | Unit tests for `Registry` class |
| Replace | `tests/test_registry.py` | Integration tests for assembled global registry |

All lookup modules, enums, models, interpolation, and individual module tests are **untouched**.

---

## Task 1: Core registry types

**Files:**
- Create: `src/tabularium/core/__init__.py`
- Create: `src/tabularium/core/registry.py`
- Create: `tests/test_core_registry.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_core_registry.py`:

```python
import pytest
from tabularium.core.registry import Registry, TableEntry


def _entry(name: str = "t") -> TableEntry:
    return TableEntry(
        func=lambda: None,
        normative="NP 999:2099",
        table_id="X.1",
        description=f"Test {name}",
    )


def test_register_and_get():
    reg = Registry()
    e = _entry()
    reg.register("test", e)
    assert reg.get("test") is e


def test_get_unknown_raises_key_error():
    reg = Registry()
    with pytest.raises(KeyError, match="necunoscut"):
        reg.get("nonexistent")


def test_all_returns_shallow_copy():
    reg = Registry()
    e = _entry()
    reg.register("t", e)
    result = reg.all()
    assert result == {"t": e}
    result["extra"] = _entry("extra")
    assert "extra" not in reg.all()


def test_include_without_namespace():
    reg = Registry()
    other = Registry()
    e = _entry()
    other.register("foo", e)
    reg.include(other)
    assert reg.get("foo") is e


def test_include_with_namespace():
    reg = Registry()
    other = Registry()
    e = _entry()
    other.register("foo", e)
    reg.include(other, namespace="np_999_2099")
    assert reg.get("np_999_2099.foo") is e
    with pytest.raises(KeyError):
        reg.get("foo")


def test_include_does_not_mutate_source():
    reg = Registry()
    other = Registry()
    e = _entry()
    other.register("foo", e)
    reg.include(other, namespace="ns")
    assert reg.all() == {"ns.foo": e}
    assert other.all() == {"foo": e}


def test_table_entry_fields():
    fn = lambda: None
    e = TableEntry(func=fn, normative="NP 1:2000", table_id="A.1", description="x")
    assert e.func is fn
    assert e.normative == "NP 1:2000"
    assert e.table_id == "A.1"
    assert e.description == "x"
```

- [ ] **Step 2: Run tests to verify they fail**

```
pytest tests/test_core_registry.py -v
```

Expected: `ModuleNotFoundError: No module named 'tabularium.core'`

- [ ] **Step 3: Create the package marker**

Create `src/tabularium/core/__init__.py` — empty file.

- [ ] **Step 4: Implement `core/registry.py`**

Create `src/tabularium/core/registry.py`:

```python
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass


@dataclass
class TableEntry:
    func: Callable
    normative: str
    table_id: str
    description: str


class Registry:
    def __init__(self) -> None:
        self._entries: dict[str, TableEntry] = {}

    def register(self, name: str, entry: TableEntry) -> None:
        self._entries[name] = entry

    def include(self, other: Registry, namespace: str | None = None) -> None:
        for name, entry in other._entries.items():
            key = f"{namespace}.{name}" if namespace else name
            self._entries[key] = entry

    def get(self, name: str) -> TableEntry:
        if name not in self._entries:
            raise KeyError(
                f"Tabel necunoscut: {name!r}. Disponibile: {list(self._entries)}"
            )
        return self._entries[name]

    def all(self) -> dict[str, TableEntry]:
        return dict(self._entries)
```

- [ ] **Step 5: Run tests to verify they pass**

```
pytest tests/test_core_registry.py -v
```

Expected: all 7 tests PASS.

- [ ] **Step 6: Commit**

```bash
git add src/tabularium/core/__init__.py src/tabularium/core/registry.py tests/test_core_registry.py
git commit -m "feat(core): add Registry class and TableEntry dataclass"
```

---

## Task 2: NP 112:2014 local registry

**Files:**
- Create: `src/tabularium/np_112_2014/registry.py`

No new tests — the assembled global registry (Task 4) will exercise this indirectly.

- [ ] **Step 1: Create `src/tabularium/np_112_2014/registry.py`**

```python
from __future__ import annotations

from tabularium.core.registry import Registry, TableEntry
from .presumed_bearing_pressure.rocks import get_presumed_bearing_pressure as _rocks
from .presumed_bearing_pressure.boulders import get_presumed_bearing_pressure as _boulders
from .presumed_bearing_pressure.gravels import get_presumed_bearing_pressure as _gravels
from .presumed_bearing_pressure.sands import get_presumed_bearing_pressure as _sands
from .presumed_bearing_pressure.fines import get_presumed_bearing_pressure as _fines
from .presumed_bearing_pressure.fills import get_presumed_bearing_pressure as _fills
from .allowable_bearing_capacity.working_condition_factor import (
    get_working_condition_factor as _wcf,
)

registry = Registry()

registry.register("presumed_bearing_pressure_rocks", TableEntry(
    func=_rocks,
    normative="NP 112:2014",
    table_id="D.1",
    description="Presiuni convenționale p̄_conv [kPa] pentru roci stâncoase și semi-stâncoase",
))
registry.register("presumed_bearing_pressure_boulders", TableEntry(
    func=_boulders,
    normative="NP 112:2014",
    table_id="D.2",
    description="Presiuni convenționale p̄_conv [kPa] pentru pământuri foarte grosiere",
))
registry.register("presumed_bearing_pressure_gravels", TableEntry(
    func=_gravels,
    normative="NP 112:2014",
    table_id="D.2",
    description="Presiuni convenționale p̄_conv [kPa] pentru pământuri grosiere (pietrișuri)",
))
registry.register("presumed_bearing_pressure_sands", TableEntry(
    func=_sands,
    normative="NP 112:2014",
    table_id="D.3",
    description="Presiuni convenționale p̄_conv [kPa] pentru nisipuri",
))
registry.register("presumed_bearing_pressure_fines", TableEntry(
    func=_fines,
    normative="NP 112:2014",
    table_id="D.4",
    description="Presiuni convenționale p̄_conv [kPa] pentru pământuri fine coezive",
))
registry.register("presumed_bearing_pressure_fills", TableEntry(
    func=_fills,
    normative="NP 112:2014",
    table_id="D.5",
    description="Presiuni convenționale p̄_conv [kPa] pentru umpluturi",
))
registry.register("working_condition_factor", TableEntry(
    func=_wcf,
    normative="NP 112:2014",
    table_id="H.7",
    description="Coeficientul condițiilor de lucru mₗ",
))
```

- [ ] **Step 2: Smoke-check the import**

```
python -c "from tabularium.np_112_2014.registry import registry; print(list(registry.all()))"
```

Expected output (order may vary):
```
['presumed_bearing_pressure_rocks', 'presumed_bearing_pressure_boulders', 'presumed_bearing_pressure_gravels', 'presumed_bearing_pressure_sands', 'presumed_bearing_pressure_fines', 'presumed_bearing_pressure_fills', 'working_condition_factor']
```

- [ ] **Step 3: Commit**

```bash
git add src/tabularium/np_112_2014/registry.py
git commit -m "feat(np112): add local registry with all NP 112:2014 table registrations"
```

---

## Task 3: NP 122:2010 local registry

**Files:**
- Create: `src/tabularium/np_122_2010/registry.py`

- [ ] **Step 1: Create `src/tabularium/np_122_2010/registry.py`**

```python
from __future__ import annotations

from tabularium.core.registry import Registry, TableEntry
from .indicative_shear_strength.non_cohesive import get_phi as _shear_non_cohesive
from .indicative_shear_strength.cohesive import get_phi_c as _shear_cohesive
from .indicative_deformation_modulus.non_cohesive import (
    get_deformation_modulus as _deformation_non_cohesive,
)
from .indicative_deformation_modulus.cohesive import (
    get_deformation_modulus as _deformation_cohesive,
)

registry = Registry()

registry.register("indicative_shear_strength_non_cohesive", TableEntry(
    func=_shear_non_cohesive,
    normative="NP 122:2010",
    table_id="A.6.1",
    description="Valori caracteristice φ' (grade) pentru pământuri necoezive",
))
registry.register("indicative_shear_strength_cohesive", TableEntry(
    func=_shear_cohesive,
    normative="NP 122:2010",
    table_id="A.6.2",
    description="Valori orientative φ', c' pentru pământuri coezive (S_r > 0,8)",
))
registry.register("indicative_deformation_modulus_non_cohesive", TableEntry(
    func=_deformation_non_cohesive,
    normative="NP 122:2010",
    table_id="A.6.3",
    description="Valori caracteristice E (kPa) pentru pământuri nisipoase",
))
registry.register("indicative_deformation_modulus_cohesive", TableEntry(
    func=_deformation_cohesive,
    normative="NP 122:2010",
    table_id="A.6.4",
    description="Valori caracteristice E (kPa) pentru pământuri coezive",
))
```

- [ ] **Step 2: Smoke-check the import**

```
python -c "from tabularium.np_122_2010.registry import registry; print(list(registry.all()))"
```

Expected:
```
['indicative_shear_strength_non_cohesive', 'indicative_shear_strength_cohesive', 'indicative_deformation_modulus_non_cohesive', 'indicative_deformation_modulus_cohesive']
```

- [ ] **Step 3: Commit**

```bash
git add src/tabularium/np_122_2010/registry.py
git commit -m "feat(np122): add local registry with all NP 122:2010 table registrations"
```

---

## Task 4: Assembly — replace `tabularium/registry.py` and rewrite `test_registry.py`

**Files:**
- Replace: `src/tabularium/registry.py`
- Modify: `src/tabularium/__init__.py`
- Replace: `tests/test_registry.py`

- [ ] **Step 1: Write the failing integration tests**

Replace `tests/test_registry.py` entirely:

```python
import pytest
from tabularium.registry import registry
from tabularium.core.registry import TableEntry
from tabularium.enums import RelativeDensity, Soil


def test_registry_contains_all_expected_keys():
    keys = set(registry.all())
    expected = {
        "np_122_2010.indicative_shear_strength_non_cohesive",
        "np_122_2010.indicative_shear_strength_cohesive",
        "np_122_2010.indicative_deformation_modulus_non_cohesive",
        "np_122_2010.indicative_deformation_modulus_cohesive",
        "np_112_2014.presumed_bearing_pressure_rocks",
        "np_112_2014.presumed_bearing_pressure_boulders",
        "np_112_2014.presumed_bearing_pressure_gravels",
        "np_112_2014.presumed_bearing_pressure_sands",
        "np_112_2014.presumed_bearing_pressure_fines",
        "np_112_2014.presumed_bearing_pressure_fills",
        "np_112_2014.working_condition_factor",
    }
    assert expected.issubset(keys)


def test_get_returns_table_entry():
    entry = registry.get("np_122_2010.indicative_shear_strength_cohesive")
    assert isinstance(entry, TableEntry)
    assert entry.normative == "NP 122:2010"
    assert entry.table_id == "A.6.2"
    assert callable(entry.func)


def test_get_unknown_key_raises():
    with pytest.raises(KeyError, match="necunoscut"):
        registry.get("np999.nonexistent")


def test_func_is_callable_and_returns_valid_result():
    entry = registry.get("np_122_2010.indicative_shear_strength_cohesive")
    result = entry.func(ip=15.0, ic=0.60, e=0.55)
    assert result.valid is True


def test_all_returns_dict_of_table_entries():
    all_tables = registry.all()
    assert isinstance(all_tables, dict)
    assert all(isinstance(v, TableEntry) for v in all_tables.values())


def test_np122_deformation_non_cohesive_entry():
    entry = registry.get("np_122_2010.indicative_deformation_modulus_non_cohesive")
    assert entry.normative == "NP 122:2010"
    assert entry.table_id == "A.6.3"
    result = entry.func(Soil.FINE_SAND, RelativeDensity.MEDIUM)
    assert result.valid is True


def test_np122_deformation_cohesive_entry():
    entry = registry.get("np_122_2010.indicative_deformation_modulus_cohesive")
    assert entry.normative == "NP 122:2010"
    assert entry.table_id == "A.6.4"
    result = entry.func(ip=15.0, ic=0.80, e=0.55)
    assert result.valid is True


def test_np112_sands_entry_metadata():
    entry = registry.get("np_112_2014.presumed_bearing_pressure_sands")
    assert entry.normative == "NP 112:2014"
    assert entry.table_id == "D.3"
    assert callable(entry.func)
```

- [ ] **Step 2: Run tests to verify they fail**

```
pytest tests/test_registry.py -v
```

Expected: `ImportError` or `AttributeError` — `registry` is not yet the new object.

- [ ] **Step 3: Replace `src/tabularium/registry.py`**

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

- [ ] **Step 4: Expose `registry` in `src/tabularium/__init__.py`**

Add one line to the existing file:

```python
"""tabularium — Romanian geotechnical normative table lookups."""

__version__ = "0.1.0"

from .registry import registry as registry  # noqa: F401
```

- [ ] **Step 5: Run the new registry tests**

```
pytest tests/test_registry.py -v
```

Expected: all 8 tests PASS.

- [ ] **Step 6: Run the full test suite to confirm no regressions**

```
pytest --tb=short
```

Expected: all tests pass. The individual module tests (`test_np_112_*`, `test_np_122_*`, `test_models.py`, `test_interpolation.py`) are unaffected.

- [ ] **Step 7: Commit**

```bash
git add src/tabularium/registry.py src/tabularium/__init__.py tests/test_registry.py
git commit -m "feat: wire up composable registry — global assembly via Registry.include()"
```

---

## Done

After Task 4 all tests pass and the refactor is complete. The public API is unchanged for external consumers: lookup function import paths are identical, and final registry keys (e.g. `"np_112_2014.presumed_bearing_pressure_sands"`) are preserved.

To add a future normative (`np_XXX_YYYY`):
1. Create `src/tabularium/np_XXX_YYYY/registry.py` with a local `Registry()` and registrations.
2. Add two lines to `src/tabularium/registry.py`: one import + one `registry.include(...)`.
