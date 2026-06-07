You are helping develop `tabularium`, a standalone Python package for Romanian geotechnical normative table lookups.

## Context

This package is part of the Geotilus ecosystem — a Django-based geotechnical SaaS platform for Romanian practitioners. The ecosystem already includes two similar standalone packages as precedent:

- `soil_classification` — soil classification logic (STAS 1243, SR EN ISO 14688, NP 074)
- `characteristic_values` — statistical engine for characteristic value calculation per NP 122:2010

`tabularium` follows the same pattern: pure Python, no Django dependencies, independently testable, versioned independently.

## Purpose

Romanian geotechnical codes (NP 122, NP 112 etc.) contain numerous tables with numerical values used in geotechnical calculations — shear strength parameters, bearing capacity factors, compressibility indices, etc. `tabularium` stores these tables as structured Python data and exposes lookup + interpolation logic.

## Consumers

- **Opifer** (AI assistant built on Anthropic API) — calls `tabularium` functions through thin tool wrappers
- **Aestimatio** (Geotilus module for characteristic values) — may consume the same data
- Future Geotilus calculation modules

## Package structure

```
src/tabularium/
├── __init__.py
├── registry.py          # central index of all available tables
├── interpolation.py     # shared interpolation utilities (linear)
├── models.py            # shared dataclasses (CodeSource, LookupResult)
├── np_074_2022/
│   ├── __init__.py
│   ├── registry.py
│   └── terrain_condition.py                         # Tabelele A.1–A.3 — clasificarea condițiilor de teren
├── np_112_2014/
│   ├── __init__.py
│   ├── registry.py
│   ├── presumed_bearing_pressure/
│   │   ├── __init__.py                              # PresumedBearingPressureResult
│   │   ├── rocks.py                                 # Tabelul D.1 — roci stâncoase și semi-stâncoase
│   │   ├── boulders.py                              # Tabelul D.2 — pământuri foarte grosiere
│   │   ├── gravels.py                               # Tabelul D.2 — pământuri grosiere (pietrișuri)
│   │   ├── sands.py                                 # Tabelul D.3 — nisipuri
│   │   ├── fines.py                                 # Tabelul D.4 — pământuri fine coezive
│   │   └── fills.py                                 # Tabelul D.5 — umpluturi
│   └── allowable_bearing_capacity/
│       ├── __init__.py                              # WorkingConditionFactorResult
│       └── working_condition_factor.py              # Tabelul H.7 — coeficientul condițiilor de lucru m₁
├── np_122_2010/
│   ├── __init__.py
│   ├── registry.py
│   ├── indicative_shear_strength/
│   │   ├── __init__.py
│   │   ├── non_cohesive.py                          # Tabelul A.6.1 — φ' pentru pământuri necoezive
│   │   └── cohesive.py                              # Tabelul A.6.2 — φ', c' pentru pământuri coezive
│   └── indicative_deformation_modulus/
│       ├── __init__.py
│       ├── non_cohesive.py                          # Tabelul A.6.3 — E pentru pământuri nisipoase
│       └── cohesive.py                              # Tabelul A.6.4 — E pentru pământuri coezive
tests/
├── test_models.py
├── test_interpolation.py
├── test_registry.py
├── test_np_074_2022_terrain_condition.py
├── test_np_112_2014_presumed_bearing_pressure_rocks.py
├── test_np_112_2014_presumed_bearing_pressure_boulders.py
├── test_np_112_2014_presumed_bearing_pressure_gravels.py
├── test_np_112_2014_presumed_bearing_pressure_sands.py
├── test_np_112_2014_presumed_bearing_pressure_fines.py
├── test_np_112_2014_presumed_bearing_pressure_fills.py
├── test_np_112_2014_allowable_bearing_capacity_working_condition_factor.py
├── test_np_122_2010_indicative_shear_strength_non_cohesive.py
├── test_np_122_2010_indicative_shear_strength_cohesive.py
├── test_np_122_2010_indicative_deformation_modulus_non_cohesive.py
└── test_np_122_2010_indicative_deformation_modulus_cohesive.py
```

## Design principles

- Pure Python, no external dependencies except `dataclasses` (stdlib)
- If interpolation needs numpy, that's acceptable but keep it optional/light
- All table data lives as Python data structures (dicts, dataclasses), not in any DB or file format
- Every public function must have type hints
- Every table module must have a corresponding test file with at minimum: exact lookup (no interpolation), interpolated lookup, out-of-range input handling
- `registry.py` exposes a unified interface to discover available tables across normatives
- Opifer tool wrappers live in Opifer, not in tabularium — tabularium exposes only lookup functions and result models

## Result model pattern

Each table module defines a `*Result` dataclass that extends `LookupResult` (from `models.py`) with table-specific fields. `LookupResult` provides the common infrastructure: `valid`, `interpolated`, `source` (a structured `CodeSource`), `warnings`, `errors`.

## Naming conventions

- Table modules named by content, not by normative indicator: `indicative_shear_strength.py` not `A_6_2.py`
- Normative indicator goes in the module docstring and in the registry entry
- Normative folder names include edition year: `np_122_2010/`, `np_112_2014/` — format `np_<number>_<year>`
- Registry keys: `"np_122_2010.indicative_shear_strength"` (normative prefix + content name)

## Adăugare tabel nou

1. Creează `src/tabularium/<np_XXX_YYYY>/<content_name>.py`
   - Definește `*Result(LookupResult)` cu câmpurile specifice tabelului
   - Implementează funcția publică de lookup cu type hints complete
   - Hardcodează `_SOURCE = CodeSource(code=..., table=...)`
   - Folosește `interpolate_linear` din `interpolation.py` pentru interpolare pe axe continue
2. Creează `tests/test_<np_XXX_YYYY>_<content_name>.py`
   - Acoperă: lookup exact, lookup interpolat, out-of-range, frontiere de categorie
3. Adaugă intrarea în `src/tabularium/registry.py` → `REGISTRY`
4. Actualizează secțiunea "Package structure" din acest fișier
