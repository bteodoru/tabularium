# Design: working_condition_factor (Tabelul H.7, NP 112:2014)

## Scop

Adăugarea tabelului H.7 din NP 112:2014 — coeficientul condițiilor de lucru (m₁) — ca modul de lookup în pachetul `tabularium`, sub `np_112_2014/allowable_bearing_capacity/`.

Includem și un refactor de consistență semantică a enum-urilor, necesar înainte de adăugarea de valori noi.

---

## Pas 1 — Refactor enum names

### Problema

`SoilCategory` conține denumiri specifice de pământuri (CLAY, FINE_SAND, ...) iar `SoilType` conține categorii largi (COHESIVE, NON_COHESIVE) — semantica e inversată față de ce ar fi natural.

### Soluție

| Enum vechi | Enum nou | Rol |
|---|---|---|
| `SoilCategory` | `Soil` | Denumiri specifice de pământuri |
| `SoilType` | `SoilCategory` | Categorii largi (COHESIVE, NON_COHESIVE, ...) |

### Fișiere afectate (find & replace mecanic)

- `src/tabularium/enums.py`
- `src/tabularium/models.py` (dacă referă SoilType)
- Toate modulele din `np_112_2014/presumed_bearing_pressure/`
- Toate modulele din `np_122_2010/`
- Toate fișierele de test

### Verificare

Rulăm întreaga suită de teste după rename pentru a confirma că nimic nu s-a stricat înainte de a continua.

---

## Pas 2 — Modificări `enums.py` (valori noi + rename)

### Rename în `Soil` (fost `SoilCategory`)

| Vechi | Nou |
|---|---|
| `BOULDER_CLAY_FILL` | `BOULDER_COHESIVE_FILL` |

Fișiere afectate: `presumed_bearing_pressure/boulders.py`, testul aferent.

### Adăugări noi în `Soil`

```python
BOULDER_SAND_FILL    = "boulder_sand_fill"     # bolovănișuri cu fill de nisip (H.7 rând 1)
GRAVEL               = "gravel"                # pietriș generic (H.7 rând 1)
GRAVEL_COHESIVE_FILL = "gravel_cohesive_fill"  # pietriș cu fill coeziv (H.7 rânduri 4/6)
COHESIVE_SOIL        = "cohesive_soil"         # pământuri coezive generice (H.7 rânduri 5/7)
```

---

## Pas 3 — Implementare H.7

### Structura fișierelor

```
src/tabularium/np_112_2014/
└── allowable_bearing_capacity/
    ├── __init__.py                    # WorkingConditionFactorResult
    └── working_condition_factor.py    # Tabelul H.7 — m₁
tests/
└── test_np_112_2014_allowable_bearing_capacity_working_condition_factor.py
```

### Result model

```python
# allowable_bearing_capacity/__init__.py
from __future__ import annotations
from dataclasses import dataclass
from ...models import LookupResult

@dataclass
class WorkingConditionFactorResult(LookupResult):
    m1: float | None = None
```

### Semnătura funcției

```python
def get_working_condition_factor(
    soil_category: Soil,
    saturation_ratio: float | None = None,   # necesar pt FINE_SAND, SILTY_SAND
    consistency_index: float | None = None,  # necesar pt BOULDER_COHESIVE_FILL, GRAVEL_COHESIVE_FILL, COHESIVE_SOIL
) -> WorkingConditionFactorResult:
```

### Tabelul H.7 — mapare completă

Sursa: `CodeSource(code="NP 112:2014", table="Tabelul H.7")`

| Soil | Condiție | m₁ |
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
| `COHESIVE_SOIL` | Iᶜ ≥ 0.5 | 1.4 |
| `BOULDER_COHESIVE_FILL` | Iᶜ < 0.5 | 1.1 |
| `GRAVEL_COHESIVE_FILL` | Iᶜ < 0.5 | 1.1 |
| `COHESIVE_SOIL` | Iᶜ < 0.5 | 1.1 |

**Notă rândul 4 din H.7:** imaginea conține probabil o eroare tipografică — scrie „Iᶜ ≤ 0,5 → 1.3" dar contextul fizic (sol mai rigid = factor mai mare) indică Iᶜ ≥ 0.5. Implementăm Iᶜ ≥ 0.5.

Categoriile `GRAVEL_CLEAN_CRYSTAL`, `GRAVEL_WITH_SAND`, `GRAVEL_SEDIMENTARY`, `GRAVEL_SILTY_SAND`, `BOULDER_GRAVEL_FILL` **nu sunt acceptate** în H.7 — funcția returnează error.

### Validare

- `FINE_SAND` / `SILTY_SAND` fără `saturation_ratio` → error
- `BOULDER_COHESIVE_FILL` / `GRAVEL_COHESIVE_FILL` / `COHESIVE_SOIL` fără `consistency_index` → error
- `Soil` neacceptat de H.7 → error cu mesaj explicit
- Parametri irelevanți furnizați (ex: `saturation_ratio` dat pentru `COHESIVE_SOIL`) → ignorați silențios

---

## Pas 4 — Teste + Registry

### Registry

```python
"np_112_2014.working_condition_factor": TableEntry(
    normative="NP 112:2014",
    table_id="H.7",
    description="Coeficientul condițiilor de lucru m₁",
    lookup_fn=_np112_working_condition_factor,
),
```

### Teste

Fișier: `tests/test_np_112_2014_allowable_bearing_capacity_working_condition_factor.py`

- Lookup exact fiecare din cele 13 rânduri distincte
- `FINE_SAND` fără `saturation_ratio` → error
- `COHESIVE_SOIL` fără `consistency_index` → error
- `Soil` neacceptat (ex: `GRAVEL_CLEAN_CRYSTAL`) → error
- `BOULDER_SAND_FILL` → m₁ = 2.0 (fără parametri secundari)
- `BOULDER_COHESIVE_FILL` cu Iᶜ = 0.5 → m₁ = 1.3 (limita exactă ≥ 0.5)
- `COHESIVE_SOIL` cu Iᶜ = 0.49 → m₁ = 1.1 (< 0.5)
