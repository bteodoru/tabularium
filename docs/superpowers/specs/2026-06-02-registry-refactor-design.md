# Registry Refactor Design

**Date:** 2026-06-02  
**Status:** Approved

## Goal

Replace the flat `REGISTRY` dict in `tabularium/registry.py` with a composable `Registry` class. Each normative owns its local registry; a top-level assembly point merges them via `include()`. Normative logic modules are untouched.

## Chosen Approach

Option A — assembly in `tabularium/registry.py`.

## File Structure

```
src/tabularium/
├── core/
│   ├── __init__.py          (empty)
│   └── registry.py          ← Registry class + TableEntry dataclass
├── np_112_2014/
│   ├── registry.py          ← local Registry() + registrations  [NEW]
│   └── ...                  (unchanged)
├── np_122_2010/
│   ├── registry.py          ← local Registry() + registrations  [NEW]
│   └── ...                  (unchanged)
├── registry.py              ← REPLACED: global instance + include() calls
├── __init__.py              ← exposes `registry`
└── ...                      (unchanged)
```

Files untouched: all lookup modules, `enums.py`, `interpolation.py`, `models.py`, all individual module tests.

## `core/registry.py`

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
            raise KeyError(f"Tabel necunoscut: {name!r}. Disponibile: {list(self._entries)}")
        return self._entries[name]

    def all(self) -> dict[str, TableEntry]:
        return dict(self._entries)
```

No global instance in `core/`. Pure types only.

## Per-normative `registry.py`

Each file at `tabularium/np_XXX_YYYY/registry.py`:

```python
from tabularium.core.registry import Registry, TableEntry
from .<module> import <func>

registry = Registry()
registry.register("<content_name>", TableEntry(
    func=<func>,
    normative="NP XXX:YYYY",
    table_id="X.Y",
    description="...",
))
```

Keys in sub-registries have **no normative prefix** — the namespace comes from `include()`.

## `tabularium/registry.py` (assembly)

```python
from tabularium.core.registry import Registry, TableEntry  # re-exported for consumers
from tabularium.np_112_2014.registry import registry as _np112
from tabularium.np_122_2010.registry import registry as _np122

registry = Registry()
registry.include(_np112, namespace="np_112_2014")
registry.include(_np122, namespace="np_122_2010")
```

Final keys are identical to current ones (e.g. `"np_112_2014.presumed_bearing_pressure_sands"`), so external consumers see no change.

Adding a new normative = one new `np_XXX/registry.py` + one import + one `include()` in this file. Visible in git diff, no auto-discovery.

## `tabularium/__init__.py`

```python
from .registry import registry as registry
```

## Tests

`test_registry.py` is rewritten to use the new API:
- `registry.get(key)` instead of `get_table(key)`
- `registry.all()` instead of `REGISTRY`
- `entry.func` instead of `entry.lookup_fn`

All other test files (`test_np_112_*.py`, `test_np_122_*.py`, `test_models.py`, etc.) are unchanged — they test lookup functions directly without the registry.

## What Does NOT Change

- All lookup function signatures
- All `*Result` dataclasses
- All module-level tests
- `enums.py`, `interpolation.py`, `models.py`
- Import paths for lookup modules (e.g. `from tabularium.np_112_2014.presumed_bearing_pressure.sands import ...`)

## Invariants

- No auto-discovery (`importlib`, `pkgutil`, etc.) — all imports are explicit
- New normative requires a visible git diff in `tabularium/registry.py`
- `core/` contains only pure type definitions, no side effects on import
