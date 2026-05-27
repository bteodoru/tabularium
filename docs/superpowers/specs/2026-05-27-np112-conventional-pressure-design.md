# Design: NP 112:2014 Conventional Pressure Tables (Anexa D)

**Date:** 2026-05-27
**Normative:** NP 112:2014
**Scope:** Tabelele D.1–D.5 — presiuni convenționale de bază `p̄_conv` pentru terenuri de fundare

---

## 1. Overview

Implementarea a 6 module în `src/tabularium/np_112_2014/`, fiecare acoperind o categorie semantică de teren. Toate modulele returnează același tip de result (`ConventionalPressureResult`), definit o singură dată în `np_112_2014/__init__.py`.

Provocarea principală față de tabelele NP 122 existente: unele intrări returnează **intervale** (`p_conv_range`) în loc de valori scalare, cu două tipuri distincte de intervale:
- **Range de judecată** (D.1): normativul nu oferă formulă de interpolare, practicianul alege.
- **Range interpolabil** (D.2): normativul specifică explicit interpolarea după `I_C` între `I_C = 0.5` și `I_C = 1.0`.

---

## 2. Result Type

Definit în `src/tabularium/np_112_2014/__init__.py`, extinde `LookupResult` din `models.py`:

```python
@dataclass
class ConventionalPressureResult(LookupResult):
    p_conv: float | None = None
    p_conv_range: tuple[float, float] | None = None

    @property
    def is_resolved(self) -> bool:
        return self.p_conv is not None
```

`LookupResult` furnizează: `valid`, `interpolated`, `source: CodeSource`, `warnings: list[str]`, `errors: list[str]`.

---

## 3. Enums noi în `enums.py`

### Extindem `SoilCategory` (valori adăugate, cele existente neschimbate):

```python
# D.1 — roci
ROCKY              = "rocky"               # Roci stâncoase
SEMI_ROCKY_MARL    = "semi_rocky_marl"     # Marne, marne argiloase, argile marnoase compacte
SEMI_ROCKY_SHALE   = "semi_rocky_shale"    # Șisturi argiloase, argile șistoase, nisipuri cimentate

# D.2 — boulders
BOULDER_GRAVEL_FILL = "boulder_gravel_fill"  # Blocuri/bolovănișuri cu nisip și pietriș
BOULDER_CLAY_FILL   = "boulder_clay_fill"    # Blocuri cu pământuri argiloase (I_C ∈ [0.5, 1])

# D.2 — gravels
GRAVEL_CLEAN_CRYSTAL = "gravel_clean_crystal"  # Pietriș curat din roci cristaline
GRAVEL_WITH_SAND     = "gravel_with_sand"      # Pietriș cu nisip
GRAVEL_SEDIMENTARY   = "gravel_sedimentary"    # Pietriș din fragmente de roci sedimentare
GRAVEL_SILTY_SAND    = "gravel_silty_sand"     # Pietriș cu nisip argilos (I_C ∈ [0.5, 1])

# D.3 — sands (MEDIUM_SAND, FINE_SAND, SILTY_SAND deja existente)
COARSE_SAND          = "coarse_sand"           # Nisip mare
```

### Enums noi:

```python
class MoistureCondition(str, Enum):
    DRY        = "dry"         # uscat
    MOIST      = "moist"       # umed
    VERY_MOIST = "very_moist"  # foarte umed
    SATURATED  = "saturated"   # saturat

class PlasticityClass(str, Enum):
    LOW    = "low"    # I_P ≤ 10%
    MEDIUM = "medium" # 10% < I_P ≤ 20%
    HIGH   = "high"   # I_P > 20%

class FillType(str, Enum):
    CONTROLLED_COMPACTED = "controlled_compacted"  # umpluturi compactate controlate
    KNOWN_ORIGIN         = "known_origin"          # umpluturi de proveniență cunoscută

class FillSoilType(str, Enum):
    SANDY_SLAG = "sandy_slag"  # pământuri nisipoase și zguri (fără nisipuri prăfoase)
    SILTY_FINE = "silty_fine"  # nisipuri prăfoase, coezive, cenușe
```

---

## 4. Module și semnături

### `conventional_pressure_rocks.py` — Tabelul D.1

```python
def get_p_conv(soil_category: SoilCategory) -> ConventionalPressureResult
```

- Returnează întotdeauna `p_conv_range`, `p_conv=None`.
- Warning: "Valoarea se alege pe baza compactității și stării de degradare a rocii."
- Domeniu: `ROCKY`, `SEMI_ROCKY_MARL`, `SEMI_ROCKY_SHALE`.

| `soil_category` | `p_conv_range` [kPa] |
|---|---|
| `ROCKY` | (1000, 6000) |
| `SEMI_ROCKY_MARL` | (350, 1100) |
| `SEMI_ROCKY_SHALE` | (600, 850) |

### `conventional_pressure_boulders.py` — Tabelul D.2 (pământuri foarte grosiere)

```python
def get_p_conv(
    soil_category: SoilCategory,
    consistency_index: float | None = None,
) -> ConventionalPressureResult
```

- `BOULDER_GRAVEL_FILL`: valoare fixă 750 kPa, `consistency_index` ignorat.
- `BOULDER_CLAY_FILL`: range interpolabil pe `I_C ∈ [0.5, 1.0]`.
  - Dacă `consistency_index` furnizat: `p_conv` scalar, `interpolated=True` dacă între noduri.
  - Dacă `consistency_index=None`: `p_conv_range=(350, 600)`, warning "Furnizați I_C pentru a rezolva valoarea".
  - `I_C` în afara `[0.5, 1.0]`: `errors`, `valid=False`.

### `conventional_pressure_gravels.py` — Tabelul D.2 (pământuri grosiere)

```python
def get_p_conv(
    soil_category: SoilCategory,
    consistency_index: float | None = None,
) -> ConventionalPressureResult
```

- `GRAVEL_CLEAN_CRYSTAL`: 600 kPa fix.
- `GRAVEL_WITH_SAND`: 550 kPa fix.
- `GRAVEL_SEDIMENTARY`: 350 kPa fix.
- `GRAVEL_SILTY_SAND`: range interpolabil pe `I_C ∈ [0.5, 1.0]`, același comportament ca `BOULDER_CLAY_FILL`.

### `conventional_pressure_sands.py` — Tabelul D.3

```python
def get_p_conv(
    soil_category: SoilCategory,
    relative_density: RelativeDensity,
    moisture_condition: MoistureCondition,
) -> ConventionalPressureResult
```

- Toate valorile fixe, fără interpolare.
- `moisture_condition` relevant doar pentru `FINE_SAND` și `SILTY_SAND`; pentru `COARSE_SAND` și `MEDIUM_SAND` orice `MoistureCondition` e acceptat — tabelul are un singur rând per categorie, deci moisture nu influențează valoarea.
- Rândul "uscat sau umed" din tabelul D.3 pentru `FINE_SAND` e reprezentat ca două rânduri distincte (`DRY` și `MOIST`) cu aceleași valori — evită aliasing în implementare.
- Combinație `(soil_category, moisture_condition)` inexistentă în tabel (e.g. `SILTY_SAND` + `DRY_OR_MOIST`) → `errors`, `valid=False`.

| `soil_category` | `moisture_condition` | `DENSE` | `MEDIUM` |
|---|---|---|---|
| `COARSE_SAND` | — | 700 | 600 |
| `MEDIUM_SAND` | — | 600 | 500 |
| `FINE_SAND` | `DRY` | 500 | 350 |
| `FINE_SAND` | `MOIST` | 500 | 350 |
| `FINE_SAND` | `VERY_MOIST` | 350 | 250 |
| `FINE_SAND` | `SATURATED` | 350 | 250 |
| `SILTY_SAND` | `DRY` | 350 | 300 |
| `SILTY_SAND` | `MOIST` | 250 | 200 |
| `SILTY_SAND` | `VERY_MOIST` | 200 | 150 |
| `SILTY_SAND` | `SATURATED` | 200 | 150 |

### `conventional_pressure_fines.py` — Tabelul D.4

```python
def get_p_conv(
    plasticity_class: PlasticityClass,
    void_ratio: float,        # e — indicele porilor
    consistency_index: float, # I_C
) -> ConventionalPressureResult
```

- Tabelul are **două sub-grile separate** per clasă de plasticitate: banda `[0.5, 0.75)` și banda `[0.75, 1.0]`. Nu există interpolare cross-bandă.
- Logica de lookup: (1) selectează banda după `I_C` (`I_C < 0.75` → banda inferioară, `I_C ≥ 0.75` → banda superioară); (2) aplică `interpolate_bilinear` pe sub-grila selectată cu `x = e`, `y = I_C`.
- `interpolate_bilinear` operează întotdeauna pe o singură sub-grilă rectangulară — nu traversează granița dintre benzi.
- Domenii valide `e` per clasă: LOW `e < 0.7`, MEDIUM `e < 1.0`, HIGH `e < 1.1`.
- `I_C < 0.5` sau `I_C > 1.0` sau `e` depășește limita → `errors`, `valid=False`.
- Nota 1 din normativ: se interpolează succesiv după `I_C` și `e`.

### `conventional_pressure_fills.py` — Tabelul D.5

```python
def get_p_conv(
    fill_type: FillType,
    fill_soil_type: FillSoilType,
    saturation_degree: float,  # S_r ∈ [0, 1]
) -> ConventionalPressureResult
```

- Valorile tabelate la `S_r ≤ 0.5` și `S_r ≥ 0.8`.
- `S_r ∈ [0.5, 0.8]`: interpolare liniară cu `interpolate_linear`.
- `S_r < 0` sau `S_r > 1`: `errors`, `valid=False`.
- `S_r ≤ 0.5`: valoarea de la nodul `0.5` (fără interpolare, consistent cu "no extrapolation").
- `S_r ≥ 0.8`: valoarea de la nodul `0.8`.

---

## 5. Interpolation

### `interpolate_bilinear` (nou în `interpolation.py`)

Interpolare biliniară pe o grilă rectangulară definită de două axe discrete:

```python
def interpolate_bilinear(
    grid: dict[float, dict[float, float]],  # grid[x][y] = value
    x: float,
    y: float,
) -> BilinearResult
```

Folosit în D.4 cu `x = e`, `y = I_C`. Fără extrapolation pe nicio axă.

### `interpolate_linear` (existent)

Folosit în D.2 (interpolare pe `I_C`) și D.5 (interpolare pe `S_r`).

---

## 6. Error / Range behavior

| Situație | `p_conv` | `p_conv_range` | `valid` | note |
|---|---|---|---|---|
| Valoare fixă | scalar | `None` | `True` | — |
| Range judecată (D.1) | `None` | `(min, max)` | `True` | warning cu instrucțiune |
| Range interpolabil, param furnizat | scalar | `None` | `True` | `interpolated=True` dacă între noduri |
| Range interpolabil, param lipsă | `None` | `(min, max)` | `True` | warning "Furnizați I_C" |
| Input necunoscut / out-of-range | `None` | `None` | `False` | `errors` populat |

---

## 7. Registry

6 intrări noi în `registry.py`:

```python
"np_112_2014.conventional_pressure_rocks":    TableEntry(normative="NP 112:2014", table_id="D.1", ...)
"np_112_2014.conventional_pressure_boulders": TableEntry(normative="NP 112:2014", table_id="D.2", ...)
"np_112_2014.conventional_pressure_gravels":  TableEntry(normative="NP 112:2014", table_id="D.2", ...)
"np_112_2014.conventional_pressure_sands":    TableEntry(normative="NP 112:2014", table_id="D.3", ...)
"np_112_2014.conventional_pressure_fines":    TableEntry(normative="NP 112:2014", table_id="D.4", ...)
"np_112_2014.conventional_pressure_fills":    TableEntry(normative="NP 112:2014", table_id="D.5", ...)
```

---

## 8. Teste

Un fișier de test per modul + extindere `test_interpolation.py` pentru `interpolate_bilinear`:

| Fișier test | Acoperire minimă |
|---|---|
| `test_np_112_2014_conventional_pressure_rocks.py` | lookup exact per categorie, `is_resolved=False`, warning prezent |
| `test_np_112_2014_conventional_pressure_boulders.py` | valoare fixă, range nerezolvat, interpolare pe I_C, I_C out-of-range |
| `test_np_112_2014_conventional_pressure_gravels.py` | valori fixe, range nerezolvat, interpolare pe I_C |
| `test_np_112_2014_conventional_pressure_sands.py` | lookup exact per combinație, combinație invalidă |
| `test_np_112_2014_conventional_pressure_fines.py` | lookup exact pe nod, interpolare biliniară, e out-of-range, I_C out-of-range |
| `test_np_112_2014_conventional_pressure_fills.py` | lookup exact la S_r ≤ 0.5, la S_r ≥ 0.8, interpolare, S_r invalid |
| `test_interpolation.py` (extins) | `interpolate_bilinear`: exact pe nod, interpolare pe o axă, interpolare biliniară, out-of-range |

---

## 9. CLAUDE.md update

Secțiunea "Package structure" din CLAUDE.md se actualizează cu cele 6 module noi după implementare.
