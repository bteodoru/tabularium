# Design: working_condition_factor (Tabelul H.7, NP 112:2014)

## Scop

Adăugarea tabelului H.7 din NP 112:2014 — coeficientul condițiilor de lucru (m₁) — ca modul de lookup în pachetul `tabularium`, sub `np_112_2014/allowable_bearing_capacity/`.

## Modificări `enums.py`

### Rename (breaking change)

| Vechi | Nou |
|-------|-----|
| `BOULDER_CLAY_FILL` | `BOULDER_COHESIVE_FILL` |

Fișiere afectate: `presumed_bearing_pressure/boulders.py`, `tests/test_np_112_2014_presumed_bearing_pressure_boulders.py`.

### Adăugări noi în `SoilCategory`

```python
BOULDER_SAND_FILL    = "boulder_sand_fill"     # bolovănișuri cu fill de nisip (H.7 rând 1)
GRAVEL               = "gravel"                # pietriș generic (H.7 rând 1)
GRAVEL_COHESIVE_FILL = "gravel_cohesive_fill"  # pietriș cu fill coeziv (H.7 rânduri 4/6)
CLAY                 = "clay"                  # argilă (H.7 rânduri 5/7)
SILT                 = "silt"                  # praf (H.7 rânduri 5/7)
```

## Structura fișierelor

```
src/tabularium/np_112_2014/
└── allowable_bearing_capacity/
    ├── __init__.py                    # WorkingConditionFactorResult
    └── working_condition_factor.py    # Tabelul H.7 — m₁
tests/
└── test_np_112_2014_allowable_bearing_capacity_working_condition_factor.py
```

## Result model

```python
# allowable_bearing_capacity/__init__.py
from __future__ import annotations
from dataclasses import dataclass
from ...models import LookupResult

@dataclass
class WorkingConditionFactorResult(LookupResult):
    m1: float | None = None
```

## Semnătura funcției

```python
def get_working_condition_factor(
    soil_category: SoilCategory,
    saturation_ratio: float | None = None,   # necesar pt FINE_SAND, SILTY_SAND
    consistency_index: float | None = None,  # necesar pt BOULDER_COHESIVE_FILL, GRAVEL_COHESIVE_FILL, CLAY, SILT
) -> WorkingConditionFactorResult:
```

## Tabelul H.7 — mapare completă

Sursa: `CodeSource(code="NP 112:2014", table="Tabelul H.7")`

| SoilCategory | Condiție | m₁ |
|---|---|---|
| `BOULDER_SAND_FILL` | — | 2.0 |
| `MEDIUM_SAND` | — | 2.0 |
| `COARSE_SAND` | — | 2.0 |
| `GRAVEL` | — | 2.0 |
| `FINE_SAND` | Sᵣ ≤ 0.8 | 1.7 |
| `FINE_SAND` | Sᵣ > 0.8 | 1.6 |
| `SILTY_SAND` | Sᵣ ≤ 0.8 | 1.5 |
| `SILTY_SAND` | Sᵣ > 0.8 | 1.3 |
| `BOULDER_COHESIVE_FILL` | Iᶜ ≥ 0.5 | 1.3 |
| `GRAVEL_COHESIVE_FILL` | Iᶜ ≥ 0.5 | 1.3 |
| `CLAY` | Iᶜ ≥ 0.5 | 1.4 |
| `SILT` | Iᶜ ≥ 0.5 | 1.4 |
| `BOULDER_COHESIVE_FILL` | Iᶜ < 0.5 | 1.1 |
| `GRAVEL_COHESIVE_FILL` | Iᶜ < 0.5 | 1.1 |
| `CLAY` | Iᶜ < 0.5 | 1.1 |
| `SILT` | Iᶜ < 0.5 | 1.1 |

**Notă rândul 4 din H.7:** imaginea conține probabil o eroare tipografică — scrie „Iᶜ ≤ 0,5 → 1.3" dar contextul fizic (sol mai rigid = factor mai mare) indică Iᶜ ≥ 0.5. Implementăm Iᶜ ≥ 0.5.

Categoriile `GRAVEL_CLEAN_CRYSTAL`, `GRAVEL_WITH_SAND`, `GRAVEL_SEDIMENTARY`, `GRAVEL_SILTY_SAND`, `BOULDER_GRAVEL_FILL` **nu sunt acceptate** în H.7 — funcția returnează error.

## Validare

- `FINE_SAND` / `SILTY_SAND` fără `saturation_ratio` → error
- `BOULDER_COHESIVE_FILL` / `GRAVEL_COHESIVE_FILL` / `CLAY` / `SILT` fără `consistency_index` → error
- `SoilCategory` neacceptat de H.7 → error cu mesaj explicit
- Parametri irelevanți furnizați (ex: `saturation_ratio` dat pentru `CLAY`) → ignorați silențios

## Registry

```python
"np_112_2014.working_condition_factor": TableEntry(
    normative="NP 112:2014",
    table_id="H.7",
    description="Coeficientul condițiilor de lucru m₁",
    lookup_fn=_np112_working_condition_factor,
),
```

## Teste

Fișier: `tests/test_np_112_2014_allowable_bearing_capacity_working_condition_factor.py`

- Lookup exact fiecare din cele 16 rânduri
- `FINE_SAND` fără `saturation_ratio` → error
- `CLAY` fără `consistency_index` → error
- `SoilCategory` neacceptat (ex: `GRAVEL_CLEAN_CRYSTAL`) → error
- `BOULDER_SAND_FILL` → m₁ = 2.0 (fără parametri secundari)
- `BOULDER_COHESIVE_FILL` cu Iᶜ = 0.5 → m₁ = 1.3 (limita exactă ≥ 0.5)
- `CLAY` cu Iᶜ = 0.49 → m₁ = 1.1 (< 0.5)
