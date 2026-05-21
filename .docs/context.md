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
tabularium/
├── __init__.py
├── registry.py          # central index of all available tables
├── interpolation.py     # shared interpolation utilities (linear, bilinear)
├── models.py            # shared dataclasses (TableResult, LookupInput, etc.)
├── np122/
│   ├── __init__.py
│   └── shear_strength.py   # first table to implement (see below)
├── np112/
│   └── __init__.py
└── tests/
    ├── test_np122_shear_strength.py
    └── ...
```

## Design principles

- Pure Python, no external dependencies except `dataclasses` (stdlib)
- If interpolation needs numpy, that's acceptable but keep it optional/light
- All table data lives as Python data structures (dicts, dataclasses), not in any DB or file format
- Every public function must have type hints
- Every table module must have a corresponding test file with at minimum: exact lookup (no interpolation), interpolated lookup, out-of-range input handling
- `registry.py` should expose a unified interface to discover available tables across normatives
