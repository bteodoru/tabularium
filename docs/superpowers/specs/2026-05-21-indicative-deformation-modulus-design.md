# Design: Indicative Deformation Modulus (NP 122:2010, Tabelele A.6.3 și A.6.4)

**Date:** 2026-05-21
**Normative:** NP 122:2010
**Tables:** A.6.3 (pământuri nisipoase), A.6.4 (pământuri coezive)

---

## Scope

Two new lookup modules under `src/tabularium/np122/`:

| Module | Table | Soil type |
|--------|-------|-----------|
| `indicative_deformation_modulus_non_cohesive.py` | A.6.3 | Pământuri nisipoase |
| `indicative_deformation_modulus_cohesive.py` | A.6.4 | Pământuri coezive |

Both expose a `get_deformation_modulus()` function and a `*Result(LookupResult)` dataclass. Both are registered in `registry.py`.

---

## Module 1: `indicative_deformation_modulus_non_cohesive` (A.6.3)

### Inputs

| Parameter | Type | Description |
|-----------|------|-------------|
| `soil_category` | `SoilCategory` | Soil type enum |
| `relative_density` | `RelativeDensity` | Compaction class enum |

### Enums (defined in the same module)

```python
class SoilCategory(str, Enum):
    GRAVEL_COARSE_MEDIUM_SAND = "gravel_coarse_medium_sand"  # Nisip cu pietriș și nisip mare și mijlociu
    FINE_SAND = "fine_sand"                                   # Nisip fin
    SILTY_SAND = "silty_sand"                                 # Nisip prăfos

class RelativeDensity(str, Enum):
    MEDIUM = "medium"  # Îndesare medie, I_D = 35…65%
    DENSE  = "dense"   # Îndesat și foarte îndesat, I_D > 65%
```

### Table data

| SoilCategory | MEDIUM (kPa) | DENSE (kPa) |
|---|---|---|
| GRAVEL_COARSE_MEDIUM_SAND | 30 000 | 40 000 |
| FINE_SAND | 25 000 | 35 000 |
| SILTY_SAND | 18 000 | 30 000 |

### Result dataclass

```python
@dataclass
class DeformationModulusNonCohesiveResult(LookupResult):
    e_modulus: float | None = None  # E in kPa
```

`interpolated` is always `False` (pure category lookup, no interpolation).

### Function signature

```python
def get_deformation_modulus(
    soil_category: SoilCategory,
    relative_density: RelativeDensity,
) -> DeformationModulusNonCohesiveResult:
```

### Error handling

Invalid enum values (e.g., unknown string passed as `str` subclass) → `valid=False` with an error message. No warnings expected for valid inputs.

### Source

```python
_SOURCE = CodeSource(code="NP 122:2010", table="Tabelul A.6.3")
```

---

## Module 2: `indicative_deformation_modulus_cohesive` (A.6.4)

### Inputs

| Parameter | Type | Description |
|-----------|------|-------------|
| `ip` | `float` | Indicele de plasticitate [%] |
| `ic` | `float` | Indicele de consistență [-] |
| `e` | `float` | Indicele porilor [-] |

### Table structure

Same nested structure as A.6.2 (`_TABLE[ip_cat][ic_range][e] = E_kPa`), but with a single `float` value per cell instead of a `(phi, c)` tuple.

```
_TABLE: dict[str, dict[str, dict[float, int]]]
```

#### IP `<10` — single IC range `"0.25-1.00"`

| e    | E (kPa) |
|------|---------|
| 0.45 | 32 000  |
| 0.55 | 24 000  |
| 0.65 | 16 000  |
| 0.75 | 10 000  |
| 0.85 |  7 000  |

#### IP `10-20` — IC range `"0.75-1.00"`

| e    | E (kPa) |
|------|---------|
| 0.45 | 34 000  |
| 0.55 | 27 000  |
| 0.65 | 22 000  |
| 0.75 | 17 000  |
| 0.85 | 14 000  |
| 0.95 | 11 000  |

#### IP `10-20` — IC range `"0.50-0.75"`

| e    | E (kPa) |
|------|---------|
| 0.45 | 32 000  |
| 0.55 | 25 000  |
| 0.65 | 19 000  |
| 0.75 | 14 000  |
| 0.85 | 11 000  |
| 0.95 |  8 000  |

#### IP `>20` — IC range `"0.75-1.00"`

| e    | E (kPa) |
|------|---------|
| 0.55 | 28 000  |
| 0.65 | 24 000  |
| 0.75 | 21 000  |
| 0.85 | 18 000  |
| 0.95 | 15 000  |
| 1.05 | 12 000  |

#### IP `>20` — IC range `"0.50-0.75"`

| e    | E (kPa) |
|------|---------|
| 0.65 | 21 000  |
| 0.75 | 18 000  |
| 0.85 | 15 000  |
| 0.95 | 12 000  |
| 1.05 |  9 000  |

### IP classification

```
ip < 10   → "<10"
ip ≤ 20   → "10-20"
ip > 20   → ">20"
```

### IC range selection

**IP `<10`:**
- IC ≥ 0.25 → `"0.25-1.00"` (only one range exists for this IP category)
- IC > 1.0 → warning (supraconsolidat, în afara domeniului), still use `"0.25-1.00"`
- IC < 0.25 → error, `valid=False`

**IP `10-20` and `>20`:**
- IC ≥ 0.75 → `"0.75-1.00"`
- 0.50 ≤ IC < 0.75 → `"0.50-0.75"`
- IC < 0.50 → error, `valid=False`
- IC > 1.0 → warning (supraconsolidat), select `"0.75-1.00"` conservatively

### Interpolation

Linear interpolation on `e` via `interpolate_linear()` from `tabularium.interpolation`. No extrapolation — `e` outside the tabulated range for the selected row → error, `valid=False`.

No interpolation on `ip` or `ic` (categorical axes).

### Result dataclass

```python
@dataclass
class DeformationModulusCohesiveResult(LookupResult):
    e_modulus: float | None = None   # E in kPa
    ip_category: str | None = None
    ic_range: str | None = None
    e_lower: float | None = None
    e_upper: float | None = None
```

### Function signature

```python
def get_deformation_modulus(ip: float, ic: float, e: float) -> DeformationModulusCohesiveResult:
```

### Source

```python
_SOURCE = CodeSource(code="NP 122:2010", table="Tabelul A.6.4")
```

---

## Registry entries

```python
"np122.indicative_deformation_modulus_non_cohesive": TableEntry(
    normative="NP 122:2010",
    table_id="A.6.3",
    description="Valori caracteristice E (kPa) pentru pământuri nisipoase",
    lookup_fn=...,
),
"np122.indicative_deformation_modulus_cohesive": TableEntry(
    normative="NP 122:2010",
    table_id="A.6.4",
    description="Valori caracteristice E (kPa) pentru pământuri coezive",
    lookup_fn=...,
),
```

Note: `registry.py` cannot accept the non-cohesive `get_deformation_modulus` directly (it takes enum args, not floats). The `lookup_fn` signature in `TableEntry` is `Callable[..., LookupResult]` — this is fine, but Opifer tool wrappers must handle enum conversion before calling.

---

## Test files

### `test_np122_indicative_deformation_modulus_non_cohesive.py`

- Exact lookup for all 6 combinations
- `valid=True`, `interpolated=False`, correct `e_modulus`
- `source.code == "NP 122:2010"`, `source.table == "Tabelul A.6.3"`

### `test_np122_indicative_deformation_modulus_cohesive.py`

- Exact lookup (no interpolation) — at least one per IP category
- Interpolated lookup — midpoint on `e` axis, verify computed value
- `e` below minimum for row → `valid=False`, error
- `e` above maximum for row → `valid=False`, error
- IC < 0.25 (IP<10) → error
- IC < 0.50 (IP 10-20 or >20) → error
- IC > 1.0 → warning + `valid=True`
- IP boundary: `ip=10` → `"10-20"`, `ip=20` → `"10-20"`, `ip=20.1` → `">20"`
- `source.code == "NP 122:2010"`, `source.table == "Tabelul A.6.4"`

---

## Files to create/modify

| Action | Path |
|--------|------|
| Create | `src/tabularium/np122/indicative_deformation_modulus_non_cohesive.py` |
| Create | `src/tabularium/np122/indicative_deformation_modulus_cohesive.py` |
| Create | `tests/test_np122_indicative_deformation_modulus_non_cohesive.py` |
| Create | `tests/test_np122_indicative_deformation_modulus_cohesive.py` |
| Modify | `src/tabularium/registry.py` |
| Modify | `CLAUDE.md` (package structure section) |
