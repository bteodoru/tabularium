# Design: NP 074:2022 — TerrainTableEntry + get_table_entries

## Scop

Expunerea datelor descriptive și evaluabile din Tabelele A.1–A.3 (NP 074:2022) ca structuri Python
imutabile. Consumatorii (Opifer, UI) pot afișa tabelul normativ, filtra după condiție, și accesa
criteriile numerice per rând fără să parseze text.

---

## Fișiere

### Noi / modificate

| Acțiune | Cale | Responsabilitate |
|---------|------|-----------------|
| Modify | `src/tabularium/np_074_2022/terrain_condition.py` | Adaugă `TerrainTableEntry`, `_TABLE_ENTRIES`, `get_table_entries` |
| Modify | `tests/test_np_074_2022_terrain_condition.py` | Teste pentru `get_table_entries` |

---

## Date

### `TerrainTableEntry` dataclass

```python
@dataclass(frozen=True)
class TerrainTableEntry:
    nr_crt: int
    table_ref: str                              # "A.1", "A.2", "A.3"
    condition: TerrainCondition
    description: str                            # text normativ pentru afișare

    # Tipuri de pământ menționate explicit în rând
    soil_types: tuple[str, ...] = ()            # ex. ("Blocuri", "Bolovănișuri", "Pietrișuri")

    # Criterii evaluabile — None = nu se aplică rândului
    soil_group: SoilGroup | None = None
    relative_density: RelativeDensity | None = None
    plasticity_class: PlasticityClass | None = None  # înlocuiește ip_min/ip_max
    ic_min: float | None = None
    ic_max: float | None = None                 # exclusiv (IC < ic_max pentru banda A.2)
    e_max: float | None = None
    fill_category: FillCategory | None = None
    organic_content_max: float | None = None    # procente; A.2r6 < 5%
    organic_content_min: float | None = None    # procente; A.3r6 > 5%
    fill_age_min_years: float | None = None     # A.2r6: > 10–12 ani
    fill_age_max_years: float | None = None     # A.3r8: < 10 ani
    requires_uniform_stratification: bool = True
    normative_references: tuple[str, ...] = ()  # ex. ("NP 125",), ("NP 126",)
```

### Funcție publică

```python
def get_table_entries(
    condition: TerrainCondition | None = None,
) -> tuple[TerrainTableEntry, ...]:
    """Returnează rândurile din Tabelele A.1–A.3, opțional filtrate după condiție."""
```

---

## Date complete — `_TABLE_ENTRIES`

Toate cele 22 de rânduri hardcodate ca `tuple[TerrainTableEntry, ...]`.

### Tabelul A.1 — Condiții de terenuri bune (7 rânduri)

| nr_crt | description (rezumat) | soil_types | soil_group | relative_density | plasticity_class | ic_min | e_max | fill_category | req_unif_strat | normative_ref |
|--------|----------------------|------------|------------|-----------------|-----------------|--------|-------|---------------|----------------|---------------|
| 1 | Blocuri, bolovănișuri și pietrișuri, <40% nisip, <30% argilă | ("Blocuri", "Bolovănișuri", "Pietrișuri") | NON_COHESIVE | — | — | — | — | — | True | () |
| 2 | Pământuri nisipoase îndesate | ("Nisipuri", "Nisipuri prăfoase") | NON_COHESIVE | DENSE | — | — | — | — | True | () |
| 3 | Pământuri fine IP<10%: e<0.7, IC≥0.75 | ("Nisipuri argiloase", "Prafuri nisipoase", "Prafuri") | COHESIVE_FINE | — | LOW | 0.75 | 0.7 | — | True | ("NP 125",) |
| 4 | Pământuri fine 10%<IP<20%: e<1.0, IC≥0.75 | ("Nisipuri argiloase", "Prafuri nisipoase-argiloase") | COHESIVE_FINE | — | MEDIUM | 0.75 | 1.0 | — | True | ("NP 125", "NP 126") |
| 5 | Pământuri fine IP>20%: e<1.1, IC≥0.75 | ("Argile nisipoase", "Argile prăfoase", "Argile") | COHESIVE_FINE | — | HIGH | 0.75 | 1.1 | — | True | ("NP 125", "NP 126") |
| 6 | Roci stâncoase și semistâncoase | ("Roci stâncoase", "Roci semistâncoase") | ROCKY | — | — | — | — | — | True | () |
| 7 | Umpluturi compactate controlat | () | FILL | — | — | — | — | CONTROLLED_COMPACTED | False | () |

### Tabelul A.2 — Condiții de terenuri medii (6 rânduri)

| nr_crt | description (rezumat) | soil_types | soil_group | relative_density | plasticity_class | ic_min | ic_max | e_max | fill_category | organic_max | fill_age_min | req_unif_strat | normative_ref |
|--------|----------------------|------------|------------|-----------------|-----------------|--------|--------|-------|---------------|-------------|--------------|----------------|---------------|
| 1 | Pământuri nisipoase de îndesare medie | ("Nisipuri", "Nisipuri prăfoase") | NON_COHESIVE | MEDIUM | — | — | — | — | — | — | — | True | () |
| 2 | Pământuri fine IP<10%: e<0.7, 0.5<IC<0.75 | ("Nisipuri argiloase", "Prafuri nisipoase", "Prafuri") | COHESIVE_FINE | — | LOW | 0.5 | 0.75 | 0.7 | — | — | — | True | () |
| 3 | Pământuri fine 10%<IP<20%: e<1.0, 0.5<IC<0.75 | ("Nisipuri argiloase", "Prafuri nisipoase-argiloase") | COHESIVE_FINE | — | MEDIUM | 0.5 | 0.75 | 1.0 | — | — | — | True | () |
| 4 | Pământuri fine IP>20%: e<1.1, 0.5<IC<0.75 | ("Argile nisipoase", "Argile prăfoase", "Argile") | COHESIVE_FINE | — | HIGH | 0.5 | 0.75 | 1.1 | — | — | — | True | () |
| 5 | Pământuri argiloase puțin/mediu active | ("Pământuri argiloase") | COHESIVE_FINE | — | — | — | — | — | — | — | — | False | ("NP 126",) |
| 6 | Umpluturi proveniență cunoscută <5% org. sau necompactate >10-12 ani | () | FILL | — | — | — | — | — | KNOWN_ORIGIN_ORGANIZED | 5.0 | 10.0 | False | () |

### Tabelul A.3 — Condiții de terenuri dificile (9 rânduri)

| nr_crt | description (rezumat) | soil_types | soil_group | relative_density | plasticity_class | ic_max | fill_category | organic_min | fill_age_max | req_unif_strat | normative_ref |
|--------|----------------------|------------|------------|-----------------|-----------------|--------|---------------|-------------|--------------|----------------|---------------|
| 1 | Pământuri nisipoase afânate | ("Nisipuri", "Nisipuri prăfoase") | NON_COHESIVE | LOOSE | — | — | — | — | — | False | () |
| 2 | Pământuri nisipoase saturate susceptibile de lichefiere | ("Nisipuri", "Nisipuri prăfoase") | NON_COHESIVE | — | — | — | — | — | — | False | () |
| 3 | Pământuri fine cu IC<0.5 | () | COHESIVE_FINE | — | — | 0.5 | — | — | — | False | () |
| 4 | Pământuri sensibile la umezire | () | COHESIVE_FINE | — | — | — | — | — | — | False | ("NP 125",) |
| 5 | Pământuri cu umflări și contracții mari, activitate mare/foarte mare | () | COHESIVE_FINE | — | — | — | — | — | — | False | ("NP 126",) |
| 6 | Pământuri cu conținut ridicat de materii organice (>5%) | () | — | — | — | — | — | 5.0 | — | False | () |
| 7 | Terenuri în pantă cu potențial de alunecare | () | — | — | — | — | — | — | — | False | () |
| 8 | Umpluturi din pământ necontrolate, vechime <10 ani | () | FILL | — | — | — | UNCONTROLLED | — | 10.0 | False | () |
| 9 | Umpluturi din resturi menajere, indiferent de vechime | () | FILL | — | — | — | HOUSEHOLD | — | — | False | () |

**Notă A.3:** `requires_uniform_stratification=False` pentru toate rândurile A.3 — aceste condiții sunt dificile indiferent de stratificație.

---

## Logica funcției

```python
def get_table_entries(
    condition: TerrainCondition | None = None,
) -> tuple[TerrainTableEntry, ...]:
    if condition is None:
        return _TABLE_ENTRIES
    return tuple(e for e in _TABLE_ENTRIES if e.condition == condition)
```

---

## Gestionarea erorilor

Funcția nu returnează erori — datele sunt hardcodate și imutabile. Niciun input invalid posibil
(condition este fie None fie un `TerrainCondition` valid).

---

## Testare

Fișier: `tests/test_np_074_2022_terrain_condition.py` — secțiune nouă `# ── get_table_entries`.

### Acoperire minimă

- Fără filtru → returnează toate 22 de intrări
- Filtru GOOD → 7 intrări, toate cu `condition == TerrainCondition.GOOD`
- Filtru MEDIUM → 6 intrări
- Filtru DIFFICULT → 9 intrări
- Ordine: A.1r1...A.1r7, A.2r1...A.2r6, A.3r1...A.3r9
- Spot check câmpuri A.1r3: `soil_group=COHESIVE_FINE`, `plasticity_class=LOW`, `ic_min=0.75`, `e_max=0.7`, `normative_references=("NP 125",)`
- Spot check câmpuri A.2r6: `fill_category=KNOWN_ORIGIN_ORGANIZED`, `organic_content_max=5.0`, `fill_age_min_years=10.0`
- Spot check A.3r2: `soil_group=NON_COHESIVE`, `relative_density=None`, `requires_uniform_stratification=False`
- Rezultat imutabil: modificarea unui câmp ridică `FrozenInstanceError`
- `get_table_entries(TerrainCondition.GOOD)` returnează `tuple`, nu `list`
