# TerrainTableEntry + get_table_entries — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Expune toate cele 22 de rânduri din Tabelele A.1–A.3 (NP 074:2022) ca tuple de `TerrainTableEntry` frozen dataclasse-uri, filtrabile după `TerrainCondition`.

**Architecture:** `TerrainTableEntry` se adaugă în `terrain_condition.py` alături de clasificatorul existent — aceeași responsabilitate (normativul A.1–A.3), aceeași sursă. `_TABLE_ENTRIES` este un tuple module-level imutabil; `get_table_entries` filtrează și returnează. Funcțiile `_classify_*` existente rămân nemodificate.

**Tech Stack:** Python 3.11+, stdlib `dataclasses` (`frozen=True`).

---

## File Map

| Acțiune | Cale | Responsabilitate |
|---------|------|-----------------|
| Modify | `src/tabularium/np_074_2022/terrain_condition.py` | Adaugă `TerrainTableEntry`, `_TABLE_ENTRIES`, `get_table_entries` |
| Modify | `tests/test_np_074_2022_terrain_condition.py` | Secțiune nouă `# ── get_table_entries` |

---

## Task 1: TerrainTableEntry dataclass + stub

**Files:**
- Modify: `src/tabularium/np_074_2022/terrain_condition.py`
- Modify: `tests/test_np_074_2022_terrain_condition.py`

- [ ] **Step 1: Adaugă testul de import și structura dataclass**

Append în `tests/test_np_074_2022_terrain_condition.py`:

```python
# ── get_table_entries ─────────────────────────────────────────────────────────

from tabularium.np_074_2022.terrain_condition import (
    TerrainTableEntry,
    get_table_entries,
)


def test_terrain_table_entry_is_frozen():
    from dataclasses import FrozenInstanceError
    entry = TerrainTableEntry(
        nr_crt=1,
        table_ref="A.1",
        condition=TerrainCondition.GOOD,
        description="Test",
    )
    try:
        entry.nr_crt = 99  # type: ignore[misc]
        assert False, "Should have raised FrozenInstanceError"
    except FrozenInstanceError:
        pass


def test_terrain_table_entry_defaults():
    entry = TerrainTableEntry(
        nr_crt=1,
        table_ref="A.1",
        condition=TerrainCondition.GOOD,
        description="Test",
    )
    assert entry.soil_types == ()
    assert entry.soil_group is None
    assert entry.relative_density is None
    assert entry.plasticity_class is None
    assert entry.ic_min is None
    assert entry.ic_max is None
    assert entry.e_max is None
    assert entry.fill_category is None
    assert entry.organic_content_max is None
    assert entry.organic_content_min is None
    assert entry.fill_age_min_years is None
    assert entry.fill_age_max_years is None
    assert entry.requires_uniform_stratification is True
    assert entry.normative_references == ()


def test_get_table_entries_returns_tuple():
    result = get_table_entries()
    assert isinstance(result, tuple)
```

- [ ] **Step 2: Run to verify it fails**

```bash
python3 -m pytest tests/test_np_074_2022_terrain_condition.py -k "terrain_table_entry or get_table_entries_returns_tuple" -v
```

Expected: `ImportError` — `TerrainTableEntry` and `get_table_entries` not defined

- [ ] **Step 3: Adaugă `TerrainTableEntry` și stub `get_table_entries` în `terrain_condition.py`**

Append după definiția `TerrainConditionResult` (după linia cu `matched_row`), înainte de `_make_result`:

```python
@dataclass(frozen=True)
class TerrainTableEntry:
    nr_crt: int
    table_ref: str
    condition: TerrainCondition
    description: str
    soil_types: tuple[str, ...] = ()
    soil_group: SoilGroup | None = None
    relative_density: RelativeDensity | None = None
    plasticity_class: PlasticityClass | None = None
    ic_min: float | None = None
    ic_max: float | None = None
    e_max: float | None = None
    fill_category: FillCategory | None = None
    organic_content_max: float | None = None
    organic_content_min: float | None = None
    fill_age_min_years: float | None = None
    fill_age_max_years: float | None = None
    requires_uniform_stratification: bool = True
    normative_references: tuple[str, ...] = ()


def get_table_entries(
    condition: TerrainCondition | None = None,
) -> tuple[TerrainTableEntry, ...]:
    """Returnează rândurile din Tabelele A.1–A.3, opțional filtrate după condiție."""
    raise NotImplementedError
```

- [ ] **Step 4: Run to verify tests pass**

```bash
python3 -m pytest tests/test_np_074_2022_terrain_condition.py -k "terrain_table_entry or get_table_entries_returns_tuple" -v
```

Expected: `test_terrain_table_entry_is_frozen` PASS, `test_terrain_table_entry_defaults` PASS, `test_get_table_entries_returns_tuple` FAIL cu `NotImplementedError`

- [ ] **Step 5: Commit**

```bash
git add src/tabularium/np_074_2022/terrain_condition.py tests/test_np_074_2022_terrain_condition.py
git commit -m "feat(np074): add TerrainTableEntry dataclass and get_table_entries stub"
```

---

## Task 2: _TABLE_ENTRIES + implementare completă

**Files:**
- Modify: `src/tabularium/np_074_2022/terrain_condition.py`
- Modify: `tests/test_np_074_2022_terrain_condition.py`

- [ ] **Step 1: Adaugă testele de date**

Append în `tests/test_np_074_2022_terrain_condition.py`:

```python
def test_get_table_entries_total_count():
    assert len(get_table_entries()) == 22


def test_get_table_entries_filter_good():
    entries = get_table_entries(TerrainCondition.GOOD)
    assert len(entries) == 7
    assert all(e.condition == TerrainCondition.GOOD for e in entries)


def test_get_table_entries_filter_medium():
    entries = get_table_entries(TerrainCondition.MEDIUM)
    assert len(entries) == 6
    assert all(e.condition == TerrainCondition.MEDIUM for e in entries)


def test_get_table_entries_filter_difficult():
    entries = get_table_entries(TerrainCondition.DIFFICULT)
    assert len(entries) == 9
    assert all(e.condition == TerrainCondition.DIFFICULT for e in entries)


def test_get_table_entries_order():
    entries = get_table_entries()
    refs = [(e.table_ref, e.nr_crt) for e in entries]
    expected = (
        [("A.1", i) for i in range(1, 8)]
        + [("A.2", i) for i in range(1, 7)]
        + [("A.3", i) for i in range(1, 10)]
    )
    assert refs == expected


def test_get_table_entries_returns_tuple_not_list():
    assert isinstance(get_table_entries(), tuple)
    assert isinstance(get_table_entries(TerrainCondition.GOOD), tuple)


def test_a1_row3_spot_check():
    entry = get_table_entries(TerrainCondition.GOOD)[2]  # index 2 = nr_crt 3
    assert entry.nr_crt == 3
    assert entry.table_ref == "A.1"
    assert entry.soil_group == SoilGroup.COHESIVE_FINE
    assert entry.plasticity_class == PlasticityClass.LOW
    assert entry.ic_min == 0.75
    assert entry.ic_max is None
    assert entry.e_max == 0.7
    assert entry.requires_uniform_stratification is True
    assert entry.normative_references == ("NP 125",)
    assert "Nisipuri argiloase" in entry.soil_types


def test_a2_row6_spot_check():
    entry = get_table_entries(TerrainCondition.MEDIUM)[5]  # index 5 = nr_crt 6
    assert entry.nr_crt == 6
    assert entry.table_ref == "A.2"
    assert entry.fill_category == FillCategory.KNOWN_ORIGIN_ORGANIZED
    assert entry.organic_content_max == 5.0
    assert entry.fill_age_min_years == 10.0
    assert entry.requires_uniform_stratification is False


def test_a3_row2_spot_check():
    entry = get_table_entries(TerrainCondition.DIFFICULT)[1]  # index 1 = nr_crt 2
    assert entry.nr_crt == 2
    assert entry.table_ref == "A.3"
    assert entry.soil_group == SoilGroup.NON_COHESIVE
    assert entry.relative_density is None
    assert entry.requires_uniform_stratification is False
    assert entry.normative_references == ()


def test_a1_row7_no_uniform_stratification():
    entry = get_table_entries(TerrainCondition.GOOD)[6]  # index 6 = nr_crt 7
    assert entry.fill_category == FillCategory.CONTROLLED_COMPACTED
    assert entry.requires_uniform_stratification is False


def test_a3_row3_ic_max():
    entry = get_table_entries(TerrainCondition.DIFFICULT)[2]  # nr_crt 3
    assert entry.ic_max == 0.5
    assert entry.ic_min is None
```

- [ ] **Step 2: Run to verify they fail**

```bash
python3 -m pytest tests/test_np_074_2022_terrain_condition.py -k "get_table_entries or spot_check or row3_ic_max or row7_no" -v
```

Expected: `NotImplementedError` pentru toate testele noi

- [ ] **Step 3: Adaugă `_TABLE_ENTRIES` și implementează `get_table_entries`**

În `terrain_condition.py`, adaugă `_TABLE_ENTRIES` înainte de `get_table_entries` (înlocuiește stub-ul cu implementarea completă):

```python
_TABLE_ENTRIES: tuple[TerrainTableEntry, ...] = (
    # ── Tabelul A.1 — Condiții de terenuri bune ───────────────────────────────
    TerrainTableEntry(
        nr_crt=1,
        table_ref="A.1",
        condition=TerrainCondition.GOOD,
        description=(
            "Blocuri, bolovănișuri și pietrișuri, conținând mai puțin de 40% nisip "
            "și mai puțin de 30% argilă, în condițiile unei stratificații practic "
            "uniforme și orizontale (având înclinarea mai mică de 10%)"
        ),
        soil_types=("Blocuri", "Bolovănișuri", "Pietrișuri"),
        soil_group=SoilGroup.NON_COHESIVE,
        requires_uniform_stratification=True,
    ),
    TerrainTableEntry(
        nr_crt=2,
        table_ref="A.1",
        condition=TerrainCondition.GOOD,
        description=(
            "Pământuri nisipoase, inclusiv nisipuri prăfoase, îndesate, în condițiile "
            "unei stratificații practic uniforme și orizontale"
        ),
        soil_types=("Nisipuri", "Nisipuri prăfoase"),
        soil_group=SoilGroup.NON_COHESIVE,
        relative_density=RelativeDensity.DENSE,
        requires_uniform_stratification=True,
    ),
    TerrainTableEntry(
        nr_crt=3,
        table_ref="A.1",
        condition=TerrainCondition.GOOD,
        description=(
            "Pământuri fine cu IP<10%: nisipuri argiloase, prafuri nisipoase și prafuri, "
            "având e<0.7 și IC≥0.75, în condițiile unei stratificații practic uniforme "
            "și orizontale"
        ),
        soil_types=("Nisipuri argiloase", "Prafuri nisipoase", "Prafuri"),
        soil_group=SoilGroup.COHESIVE_FINE,
        plasticity_class=PlasticityClass.LOW,
        ic_min=0.75,
        e_max=0.7,
        requires_uniform_stratification=True,
        normative_references=("NP 125",),
    ),
    TerrainTableEntry(
        nr_crt=4,
        table_ref="A.1",
        condition=TerrainCondition.GOOD,
        description=(
            "Pământuri fine cu 10%<IP<20%: nisipuri argiloase, prafuri nisipoase-argiloase, "
            "având e<1.0 și IC≥0.75, în condițiile unei stratificații practic uniforme "
            "și orizontale"
        ),
        soil_types=("Nisipuri argiloase", "Prafuri nisipoase-argiloase"),
        soil_group=SoilGroup.COHESIVE_FINE,
        plasticity_class=PlasticityClass.MEDIUM,
        ic_min=0.75,
        e_max=1.0,
        requires_uniform_stratification=True,
        normative_references=("NP 125", "NP 126"),
    ),
    TerrainTableEntry(
        nr_crt=5,
        table_ref="A.1",
        condition=TerrainCondition.GOOD,
        description=(
            "Pământuri fine cu IP>20%: argile nisipoase, argile prăfoase și argile, "
            "având e<1.1 și IC≥0.75, în condițiile unei stratificații practic uniforme "
            "și orizontale"
        ),
        soil_types=("Argile nisipoase", "Argile prăfoase", "Argile"),
        soil_group=SoilGroup.COHESIVE_FINE,
        plasticity_class=PlasticityClass.HIGH,
        ic_min=0.75,
        e_max=1.1,
        requires_uniform_stratification=True,
        normative_references=("NP 125", "NP 126"),
    ),
    TerrainTableEntry(
        nr_crt=6,
        table_ref="A.1",
        condition=TerrainCondition.GOOD,
        description=(
            "Roci stâncoase și semistâncoase în condițiile unei stratificații practic "
            "uniforme și orizontale"
        ),
        soil_types=("Roci stâncoase", "Roci semistâncoase"),
        soil_group=SoilGroup.ROCKY,
        requires_uniform_stratification=True,
    ),
    TerrainTableEntry(
        nr_crt=7,
        table_ref="A.1",
        condition=TerrainCondition.GOOD,
        description=(
            "Umpluturi compactate realizate conform unor documentații de execuție "
            "(caiete de sarcini) controlate calitativ de unități autorizate"
        ),
        soil_group=SoilGroup.FILL,
        fill_category=FillCategory.CONTROLLED_COMPACTED,
        requires_uniform_stratification=False,
    ),
    # ── Tabelul A.2 — Condiții de terenuri medii ──────────────────────────────
    TerrainTableEntry(
        nr_crt=1,
        table_ref="A.2",
        condition=TerrainCondition.MEDIUM,
        description=(
            "Pământuri nisipoase, inclusiv nisipuri prăfoase, de îndesare medie, "
            "în condițiile unei stratificații practic uniforme și orizontale "
            "(având înclinarea mai mică de 10%)"
        ),
        soil_types=("Nisipuri", "Nisipuri prăfoase"),
        soil_group=SoilGroup.NON_COHESIVE,
        relative_density=RelativeDensity.MEDIUM,
        requires_uniform_stratification=True,
    ),
    TerrainTableEntry(
        nr_crt=2,
        table_ref="A.2",
        condition=TerrainCondition.MEDIUM,
        description=(
            "Pământuri fine cu IP<10%: nisipuri argiloase, prafuri nisipoase și prafuri, "
            "având e<0.7 și 0.5<IC<0.75, în condițiile unei stratificații practic "
            "uniforme și orizontale"
        ),
        soil_types=("Nisipuri argiloase", "Prafuri nisipoase", "Prafuri"),
        soil_group=SoilGroup.COHESIVE_FINE,
        plasticity_class=PlasticityClass.LOW,
        ic_min=0.5,
        ic_max=0.75,
        e_max=0.7,
        requires_uniform_stratification=True,
    ),
    TerrainTableEntry(
        nr_crt=3,
        table_ref="A.2",
        condition=TerrainCondition.MEDIUM,
        description=(
            "Pământuri fine cu 10%<IP<20%: nisipuri argiloase, prafuri nisipoase-argiloase, "
            "având e<1.0 și 0.5<IC<0.75, în condițiile unei stratificații practic "
            "uniforme și orizontale"
        ),
        soil_types=("Nisipuri argiloase", "Prafuri nisipoase-argiloase"),
        soil_group=SoilGroup.COHESIVE_FINE,
        plasticity_class=PlasticityClass.MEDIUM,
        ic_min=0.5,
        ic_max=0.75,
        e_max=1.0,
        requires_uniform_stratification=True,
    ),
    TerrainTableEntry(
        nr_crt=4,
        table_ref="A.2",
        condition=TerrainCondition.MEDIUM,
        description=(
            "Pământuri fine cu IP>20%: argile nisipoase, argile prăfoase și argile, "
            "având e<1.1 și 0.5<IC<0.75, în condițiile unei stratificații practic "
            "uniforme și orizontale"
        ),
        soil_types=("Argile nisipoase", "Argile prăfoase", "Argile"),
        soil_group=SoilGroup.COHESIVE_FINE,
        plasticity_class=PlasticityClass.HIGH,
        ic_min=0.5,
        ic_max=0.75,
        e_max=1.1,
        requires_uniform_stratification=True,
    ),
    TerrainTableEntry(
        nr_crt=5,
        table_ref="A.2",
        condition=TerrainCondition.MEDIUM,
        description=(
            "Pământuri argiloase puțin active sau cu activitate medie, "
            "definite conform normativului NP 126"
        ),
        soil_types=("Pământuri argiloase",),
        soil_group=SoilGroup.COHESIVE_FINE,
        requires_uniform_stratification=False,
        normative_references=("NP 126",),
    ),
    TerrainTableEntry(
        nr_crt=6,
        table_ref="A.2",
        condition=TerrainCondition.MEDIUM,
        description=(
            "Umpluturi de proveniență cunoscută realizate organizat și conținând "
            "materii organice sub 5% sau umpluturi necompactate inițial, "
            "cu o vechime mai mare de 10-12 ani"
        ),
        soil_group=SoilGroup.FILL,
        fill_category=FillCategory.KNOWN_ORIGIN_ORGANIZED,
        organic_content_max=5.0,
        fill_age_min_years=10.0,
        requires_uniform_stratification=False,
    ),
    # ── Tabelul A.3 — Condiții de terenuri dificile ───────────────────────────
    TerrainTableEntry(
        nr_crt=1,
        table_ref="A.3",
        condition=TerrainCondition.DIFFICULT,
        description="Pământuri nisipoase, inclusiv nisipuri prăfoase, în stare afânată",
        soil_types=("Nisipuri", "Nisipuri prăfoase"),
        soil_group=SoilGroup.NON_COHESIVE,
        relative_density=RelativeDensity.LOOSE,
        requires_uniform_stratification=False,
    ),
    TerrainTableEntry(
        nr_crt=2,
        table_ref="A.3",
        condition=TerrainCondition.DIFFICULT,
        description=(
            "Pământuri nisipoase saturate susceptibile de lichefiere "
            "sub acțiuni seismice"
        ),
        soil_types=("Nisipuri", "Nisipuri prăfoase"),
        soil_group=SoilGroup.NON_COHESIVE,
        requires_uniform_stratification=False,
    ),
    TerrainTableEntry(
        nr_crt=3,
        table_ref="A.3",
        condition=TerrainCondition.DIFFICULT,
        description="Pământuri fine având IC<0.5",
        soil_group=SoilGroup.COHESIVE_FINE,
        ic_max=0.5,
        requires_uniform_stratification=False,
    ),
    TerrainTableEntry(
        nr_crt=4,
        table_ref="A.3",
        condition=TerrainCondition.DIFFICULT,
        description=(
            "Pământuri sensibile la umezire, definite conform normativului NP 125"
        ),
        soil_group=SoilGroup.COHESIVE_FINE,
        requires_uniform_stratification=False,
        normative_references=("NP 125",),
    ),
    TerrainTableEntry(
        nr_crt=5,
        table_ref="A.3",
        condition=TerrainCondition.DIFFICULT,
        description=(
            "Pământuri cu umflări și contracții mari, cu activitate mare și foarte mare, "
            "definite conform normativului NP 126"
        ),
        soil_group=SoilGroup.COHESIVE_FINE,
        requires_uniform_stratification=False,
        normative_references=("NP 126",),
    ),
    TerrainTableEntry(
        nr_crt=6,
        table_ref="A.3",
        condition=TerrainCondition.DIFFICULT,
        description="Pământuri cu conținut ridicat de materii organice (peste 5%)",
        organic_content_min=5.0,
        requires_uniform_stratification=False,
    ),
    TerrainTableEntry(
        nr_crt=7,
        table_ref="A.3",
        condition=TerrainCondition.DIFFICULT,
        description="Terenuri în pantă cu potențial de alunecare",
        requires_uniform_stratification=False,
    ),
    TerrainTableEntry(
        nr_crt=8,
        table_ref="A.3",
        condition=TerrainCondition.DIFFICULT,
        description=(
            "Umpluturi din pământ executate necontrolat cu o vechime sub 10 ani"
        ),
        soil_group=SoilGroup.FILL,
        fill_category=FillCategory.UNCONTROLLED,
        fill_age_max_years=10.0,
        requires_uniform_stratification=False,
    ),
    TerrainTableEntry(
        nr_crt=9,
        table_ref="A.3",
        condition=TerrainCondition.DIFFICULT,
        description="Umpluturi din resturi menajere, indiferent de vechime",
        soil_group=SoilGroup.FILL,
        fill_category=FillCategory.HOUSEHOLD,
        requires_uniform_stratification=False,
    ),
)


def get_table_entries(
    condition: TerrainCondition | None = None,
) -> tuple[TerrainTableEntry, ...]:
    """Returnează rândurile din Tabelele A.1–A.3, opțional filtrate după condiție."""
    if condition is None:
        return _TABLE_ENTRIES
    return tuple(e for e in _TABLE_ENTRIES if e.condition == condition)
```

- [ ] **Step 4: Run to verify tests pass**

```bash
python3 -m pytest tests/test_np_074_2022_terrain_condition.py -k "get_table_entries or spot_check or row3_ic_max or row7_no" -v
```

Expected: toate trec

- [ ] **Step 5: Run full suite**

```bash
python3 -m pytest tests/ -q
```

Expected: toate trec (255 + teste noi)

- [ ] **Step 6: Commit**

```bash
git add src/tabularium/np_074_2022/terrain_condition.py tests/test_np_074_2022_terrain_condition.py
git commit -m "feat(np074): implement _TABLE_ENTRIES and get_table_entries for A.1–A.3"
```
