# Design: NP 074:2022 — Clasificarea condițiilor de teren (Tabelele A.1–A.3)

## Scop

Implementarea unui clasificator parametric pentru condițiile de teren conform NP 074:2022,
Anexa A, Tabelele A.1–A.3. Returnează `TerrainCondition` (GOOD / MEDIUM / DIFFICULT),
tabelul și rândul din normativ, cu warnings pentru cazurile care implică excepții din
NP 125 / NP 126.

Consumatori: Opifer (via tool wrappers), viitoare module Geotilus.

---

## Structură fișiere

### Fișiere noi

```
src/tabularium/np_074_2022/
├── __init__.py
└── terrain_condition.py

src/tabularium/np_074_2022/registry.py

tests/
└── test_np_074_2022_terrain_condition.py
```

### Fișiere modificate

- `src/tabularium/enums.py` — 3 enums noi + `LOOSE` în `RelativeDensity`
- `src/tabularium/registry.py` — include registry-ul `np_074_2022`

---

## Date

### Enums noi în `enums.py`

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

`RelativeDensity` primește valoarea nouă: `LOOSE = ("loose", "Afânată")`.

### Input dataclass (în `terrain_condition.py`)

```python
@dataclass
class TerrainConditionInput:
    soil_group: SoilGroup

    # NON_COHESIVE
    relative_density: RelativeDensity | None = None

    # COHESIVE_FINE
    plasticity_class: PlasticityClass | None = None  # LOW / MEDIUM / HIGH
    void_ratio: float | None = None                  # e
    consistency_index: float | None = None           # IC

    # FILL
    fill_category: FillCategory | None = None
    organic_content_pct: float = 0.0                 # procente, default 0
    fill_age_years: float | None = None

    # General
    stratification_uniform_horizontal: bool = True

    # Flaguri opționale — Opifer le poate seta explicit
    collapsible: bool | None = None        # PSU — NP 125
    active: bool | None = None             # PUCM activitate ridicată — NP 126
    liquefiable: bool | None = None        # lichefiere seismică
    sliding_potential: bool | None = None  # teren în pantă cu potențial de alunecare
```

### Result dataclass (în `terrain_condition.py`)

```python
@dataclass
class TerrainConditionResult(LookupResult):
    condition: TerrainCondition | None = None
    matched_table: str | None = None   # "A.1", "A.2" sau "A.3"
    matched_row: int | None = None     # număr rând 1-based conform normativului
```

`LookupResult` furnizează: `valid`, `interpolated`, `source`, `warnings`, `errors`.
`interpolated` va fi întotdeauna `False` (tabelele A.1–A.3 nu au interpolare).

---

## Logica de clasificare

Funcție publică: `classify_terrain_condition(inp: TerrainConditionInput) -> TerrainConditionResult`

`_SOURCE = CodeSource(code="NP 074:2022", table="Tabelele A.1–A.3", section="Anexa A")`

### Pasul 1 — Override flags (evaluate primele, indiferent de soil_group)

| Flag | Valoare | Rezultat | Tabel | Rând |
|------|---------|----------|-------|------|
| `collapsible` | `True` | DIFFICULT | A.3 | 4 |
| `active` | `True` | DIFFICULT | A.3 | 5 |
| `liquefiable` | `True` | DIFFICULT | A.3 | 2 |
| `sliding_potential` | `True` | DIFFICULT | A.3 | 7 |

Dacă mai multe flaguri sunt `True` simultan, se returnează primul match în ordinea de mai sus
(toate duc la DIFFICULT — ordinea afectează doar `matched_row`).

### Pasul 2 — Clasificare per soil_group

#### ROCKY

- `stratification_uniform_horizontal=True` → **GOOD**, A.1 rând 6
- `stratification_uniform_horizontal=False` → eroare: `"Roci cu stratificație neuniformă nu sunt acoperite de tabelele A.1–A.3"`

#### NON_COHESIVE

Necesită `relative_density`. Dacă lipsește → eroare: `"relative_density este necesar pentru NON_COHESIVE"`.

| `relative_density` | `stratification_uniform_horizontal` | Rezultat | Tabel | Rând |
|--------------------|-------------------------------------|----------|-------|------|
| `DENSE` | `True` | GOOD | A.1 | 2 |
| `DENSE` | `False` | eroare* | — | — |
| `MEDIUM` | `True` | MEDIUM | A.2 | 1 |
| `MEDIUM` | `False` | eroare* | — | — |
| `LOOSE` | orice | DIFFICULT | A.3 | 1 |

*eroare: `"Pământuri necoezive dense/medii necesită stratificație uniformă și orizontală conform A.1/A.2"`

#### COHESIVE_FINE

Necesită `plasticity_class`, `void_ratio`, `consistency_index`. Dacă lipsește oricare → eroare.

Limite void_ratio per clasă de plasticitate:

| `plasticity_class` | `e_max` |
|--------------------|---------|
| `LOW` (IP<10%) | 0.7 |
| `MEDIUM` (IP 10–20%) | 1.0 |
| `HIGH` (IP>20%) | 1.1 |

Logică (în ordine):

```
1. IC < 0.5
   → DIFFICULT, A.3 rând 3

2. IC ∈ [0.5, 0.75)
   dacă e > e_max → eroare: "combinație e/IC în afara domeniului tabelelor A.1–A.3"
   altfel → MEDIUM (A.2: LOW→rând 2, MEDIUM→rând 3, HIGH→rând 4)
   + warning dacă active is None și plasticity_class în {MEDIUM, HIGH}:
     "Verificați activitatea conform NP 126 — dacă activitate mare/foarte mare → A.3 rând 5 (DIFFICULT)"

3. IC ≥ 0.75
   dacă e > e_max → eroare: "combinație e/IC în afara domeniului tabelelor A.1–A.3"
   altfel → GOOD (A.1: LOW→rând 3, MEDIUM→rând 4, HIGH→rând 5)
   + warning dacă collapsible is None:
     "Verificați sensibilitatea la umezire conform NP 125 — dacă PSU → A.3 rând 4 (DIFFICULT)"
   + warning dacă active is None și plasticity_class în {MEDIUM, HIGH}:
     "Verificați umflările/contracțiile conform NP 126 — dacă activitate mare/foarte mare → A.3 rând 5 (DIFFICULT)"
```

#### FILL

Necesită `fill_category`. Dacă lipsește → eroare.

| `fill_category` | Condiție suplimentară | Rezultat | Tabel | Rând | Note |
|-----------------|----------------------|----------|-------|------|------|
| `CONTROLLED_COMPACTED` | — | GOOD | A.1 | 7 | — |
| `HOUSEHOLD` | — | DIFFICULT | A.3 | 9 | — |
| `KNOWN_ORIGIN_ORGANIZED` | `organic_content_pct < 5` | MEDIUM | A.2 | 6 | — |
| `KNOWN_ORIGIN_ORGANIZED` | `organic_content_pct ≥ 5` | DIFFICULT | A.3 | 6 | — |
| `UNCONTROLLED` | `fill_age_years is None` | eroare | — | — | "fill_age_years necesar pentru UNCONTROLLED" |
| `UNCONTROLLED` | `fill_age_years < 10` | DIFFICULT | A.3 | 8 | — |
| `UNCONTROLLED` | `10 ≤ fill_age_years ≤ 12` | MEDIUM | A.2 | 6 | warning: "Vârstă la limita zonei gri 10–12 ani (A.2 rând 6 / A.3 rând 8)" |
| `UNCONTROLLED` | `fill_age_years > 12` | MEDIUM | A.2 | 6 | — |

---

## Gestionarea erorilor

- Orice eroare → `valid=False`, câmpul `errors` populat, `condition=None`
- Warnings → `valid=True`, rezultatul este returnat, `warnings` populat
- `interpolated` este întotdeauna `False`

---

## Registry

`src/tabularium/np_074_2022/registry.py`:
```python
registry = Registry()
registry.register("terrain_condition", TableEntry(
    name="Clasificarea condițiilor de teren",
    code="NP 074:2022",
    table="Tabelele A.1–A.3",
    section="Anexa A",
    lookup_fn=classify_terrain_condition,
))
```

`src/tabularium/registry.py` include: `registry.include(_np074, namespace="np_074_2022")`.

---

## Testare

Fișier: `tests/test_np_074_2022_terrain_condition.py`

### Lookup exact — câte un test per rând normativ

- A.1 rând 2: NON_COHESIVE, DENSE, uniform → GOOD
- A.1 rând 3: COHESIVE_FINE, LOW, e=0.6, IC=0.80 → GOOD
- A.1 rând 4: COHESIVE_FINE, MEDIUM, e=0.8, IC=0.80 → GOOD (+ warnings NP 125/126 dacă flags=None)
- A.1 rând 5: COHESIVE_FINE, HIGH, e=1.0, IC=0.80 → GOOD
- A.1 rând 6: ROCKY, uniform → GOOD
- A.1 rând 7: FILL, CONTROLLED_COMPACTED → GOOD
- A.2 rând 1: NON_COHESIVE, MEDIUM, uniform → MEDIUM
- A.2 rând 2: COHESIVE_FINE, LOW, e=0.6, IC=0.60 → MEDIUM
- A.2 rând 3: COHESIVE_FINE, MEDIUM, e=0.8, IC=0.60 → MEDIUM
- A.2 rând 4: COHESIVE_FINE, HIGH, e=1.0, IC=0.60 → MEDIUM
- A.2 rând 5: COHESIVE_FINE, HIGH, e=1.0, IC=0.60, `active=False` → MEDIUM, fără warning NP 126
- A.2 rând 6: FILL, KNOWN_ORIGIN_ORGANIZED, organic=3% → MEDIUM
- A.2 rând 6: FILL, UNCONTROLLED, age=15 → MEDIUM
- A.3 rând 1: NON_COHESIVE, LOOSE → DIFFICULT
- A.3 rând 3: COHESIVE_FINE, any, IC=0.4 → DIFFICULT
- A.3 rând 6: FILL, KNOWN_ORIGIN_ORGANIZED, organic=6% → DIFFICULT
- A.3 rând 8: FILL, UNCONTROLLED, age=5 → DIFFICULT
- A.3 rând 9: FILL, HOUSEHOLD → DIFFICULT

### Override flags

- `collapsible=True` pe input care altfel → GOOD → DIFFICULT, A.3 rând 4
- `active=True` pe input care altfel → GOOD → DIFFICULT, A.3 rând 5
- `liquefiable=True` pe NON_COHESIVE DENSE → DIFFICULT, A.3 rând 2
- `sliding_potential=True` pe ROCKY → DIFFICULT, A.3 rând 7

### Warnings NP 125 / NP 126

- COHESIVE_FINE, IC≥0.75, `collapsible=None` → `valid=True`, `warnings` non-empty (NP 125)
- COHESIVE_FINE, MEDIUM, IC≥0.75, `active=None` → warnings non-empty (NP 126)
- COHESIVE_FINE, LOW, IC≥0.75, `active=None` → fără warning NP 126 (LOW nu necesită)
- FILL UNCONTROLLED, age=11 → MEDIUM + warning zonă gri

### Erori

- NON_COHESIVE fără `relative_density` → `valid=False`
- COHESIVE_FINE cu IC=0.80, e=1.5, LOW → `valid=False` (e depășit)
- FILL UNCONTROLLED fără `fill_age_years` → `valid=False`
- ROCKY cu `stratification_uniform_horizontal=False` → `valid=False`
- COHESIVE_FINE fără `consistency_index` → `valid=False`
