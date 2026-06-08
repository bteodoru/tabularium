from __future__ import annotations

from dataclasses import dataclass

from ..enums import (
    FillCategory,
    PlasticityClass,
    RelativeDensity,
    SoilGroup,
    TerrainCondition,
)
from ..models import CodeSource, LookupResult

_SOURCE = CodeSource(code="NP 074:2022", table="Tabelele A.1–A.3", section="Anexa A")

_E_MAX: dict[PlasticityClass, float] = {
    PlasticityClass.LOW:    0.7,
    PlasticityClass.MEDIUM: 1.0,
    PlasticityClass.HIGH:   1.1,
}


@dataclass
class TerrainConditionInput:
    soil_group: SoilGroup

    # NON_COHESIVE
    relative_density: RelativeDensity | None = None

    # COHESIVE_FINE
    plasticity_class: PlasticityClass | None = None
    void_ratio: float | None = None
    consistency_index: float | None = None

    # FILL
    fill_category: FillCategory | None = None
    organic_content_pct: float = 0.0
    fill_age_years: float | None = None

    # General
    stratification_uniform_horizontal: bool = True

    # Optional override flags
    collapsible: bool | None = None
    active: bool | None = None
    liquefiable: bool | None = None
    sliding_potential: bool | None = None


@dataclass
class TerrainConditionResult(LookupResult):
    condition: TerrainCondition | None = None
    matched_table: str | None = None
    matched_row: int | None = None


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


def _make_result(
    condition: TerrainCondition,
    table: str,
    row: int,
    warnings: list[str] | None = None,
) -> TerrainConditionResult:
    r = TerrainConditionResult(source=_SOURCE)
    r.condition = condition
    r.matched_table = table
    r.matched_row = row
    r.valid = True
    if warnings:
        r.warnings.extend(warnings)
    return r


def _error(msg: str) -> TerrainConditionResult:
    r = TerrainConditionResult(source=_SOURCE)
    r.errors.append(msg)
    return r


def classify_terrain_condition(inp: TerrainConditionInput) -> TerrainConditionResult:
    if inp.collapsible is True:
        return _make_result(TerrainCondition.DIFFICULT, "A.3", 4)
    if inp.active is True:
        return _make_result(TerrainCondition.DIFFICULT, "A.3", 5)
    if inp.liquefiable is True:
        return _make_result(TerrainCondition.DIFFICULT, "A.3", 2)
    if inp.sliding_potential is True:
        return _make_result(TerrainCondition.DIFFICULT, "A.3", 7)

    try:
        soil_group = SoilGroup(inp.soil_group)
    except ValueError:
        return _error(f"Grup de sol necunoscut: {inp.soil_group!r}.")

    if soil_group == SoilGroup.ROCKY:
        return _classify_rocky(inp)
    if soil_group == SoilGroup.NON_COHESIVE:
        return _classify_non_cohesive(inp)
    if soil_group == SoilGroup.COHESIVE_FINE:
        return _classify_cohesive_fine(inp)
    return _classify_fill(inp)


def _classify_rocky(inp: TerrainConditionInput) -> TerrainConditionResult:
    if not inp.stratification_uniform_horizontal:
        return _error(
            "Roci cu stratificație neuniformă nu sunt acoperite de tabelele A.1–A.3."
        )
    return _make_result(TerrainCondition.GOOD, "A.1", 6)


def _classify_non_cohesive(inp: TerrainConditionInput) -> TerrainConditionResult:
    if inp.relative_density is None:
        return _error("relative_density este necesar pentru NON_COHESIVE.")

    try:
        density = RelativeDensity(inp.relative_density)
    except ValueError:
        return _error(f"Densitate relativă necunoscută: {inp.relative_density!r}.")

    if density == RelativeDensity.LOOSE:
        return _make_result(TerrainCondition.DIFFICULT, "A.3", 1)

    if not inp.stratification_uniform_horizontal:
        return _error(
            "Pământuri necoezive dense/medii necesită stratificație uniformă și orizontală conform A.1/A.2."
        )

    if density == RelativeDensity.DENSE:
        return _make_result(TerrainCondition.GOOD, "A.1", 2)
    return _make_result(TerrainCondition.MEDIUM, "A.2", 1)


def _classify_cohesive_fine(inp: TerrainConditionInput) -> TerrainConditionResult:
    if inp.plasticity_class is None:
        return _error("plasticity_class este necesar pentru COHESIVE_FINE.")
    if inp.void_ratio is None:
        return _error("void_ratio este necesar pentru COHESIVE_FINE.")
    if inp.consistency_index is None:
        return _error("consistency_index este necesar pentru COHESIVE_FINE.")

    try:
        pc = PlasticityClass(inp.plasticity_class)
    except ValueError:
        return _error(f"Clasă de plasticitate necunoscută: {inp.plasticity_class!r}.")

    ic = inp.consistency_index
    e = inp.void_ratio
    e_max = _E_MAX[pc]

    if ic < 0.5:
        return _make_result(TerrainCondition.DIFFICULT, "A.3", 3)

    if ic < 0.75:
        if e > e_max:
            return _error(
                f"Combinație e={e}, IC={ic} în afara domeniului tabelelor A.1–A.3 "
                f"pentru plasticitate {pc!r} (e_max={e_max})."
            )
        row = {PlasticityClass.LOW: 2, PlasticityClass.MEDIUM: 3, PlasticityClass.HIGH: 4}[pc]
        warnings: list[str] = []
        if inp.active is None and pc in (PlasticityClass.MEDIUM, PlasticityClass.HIGH):
            warnings.append(
                "Verificați activitatea conform NP 126 — "
                "dacă activitate mare/foarte mare → A.3 rând 5 (DIFFICULT)."
            )
        return _make_result(TerrainCondition.MEDIUM, "A.2", row, warnings)

    # ic >= 0.75
    if e > e_max:
        return _error(
            f"Combinație e={e}, IC={ic} în afara domeniului tabelelor A.1–A.3 "
            f"pentru plasticitate {pc!r} (e_max={e_max})."
        )
    row = {PlasticityClass.LOW: 3, PlasticityClass.MEDIUM: 4, PlasticityClass.HIGH: 5}[pc]
    warnings = []
    if inp.collapsible is None:
        warnings.append(
            "Verificați sensibilitatea la umezire conform NP 125 — "
            "dacă PSU → A.3 rând 4 (DIFFICULT)."
        )
    if inp.active is None and pc in (PlasticityClass.MEDIUM, PlasticityClass.HIGH):
        warnings.append(
            "Verificați umflările/contracțiile conform NP 126 — "
            "dacă activitate mare/foarte mare → A.3 rând 5 (DIFFICULT)."
        )
    return _make_result(TerrainCondition.GOOD, "A.1", row, warnings)


def _classify_fill(inp: TerrainConditionInput) -> TerrainConditionResult:
    if inp.fill_category is None:
        return _error("fill_category este necesar pentru FILL.")

    try:
        fc = FillCategory(inp.fill_category)
    except ValueError:
        return _error(f"Categorie umpluturi necunoscută: {inp.fill_category!r}.")

    if fc == FillCategory.CONTROLLED_COMPACTED:
        return _make_result(TerrainCondition.GOOD, "A.1", 7)

    if fc == FillCategory.HOUSEHOLD:
        return _make_result(TerrainCondition.DIFFICULT, "A.3", 9)

    if fc == FillCategory.KNOWN_ORIGIN_ORGANIZED:
        if inp.organic_content_pct >= 5.0:
            return _make_result(TerrainCondition.DIFFICULT, "A.3", 6)
        return _make_result(TerrainCondition.MEDIUM, "A.2", 6)

    # UNCONTROLLED
    if inp.fill_age_years is None:
        return _error("fill_age_years este necesar pentru UNCONTROLLED.")
    if inp.fill_age_years < 10:
        return _make_result(TerrainCondition.DIFFICULT, "A.3", 8)
    warnings: list[str] = []
    if inp.fill_age_years <= 12:
        warnings.append(
            "Vârstă la limita zonei gri 10–12 ani (A.2 rând 6 / A.3 rând 8) — verificați cu normativul."
        )
    return _make_result(TerrainCondition.MEDIUM, "A.2", 6, warnings)
