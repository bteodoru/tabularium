from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from .models import LookupResult
from .np_122_2010.indicative_shear_strength.non_cohesive import get_phi as _np122_shear_non_cohesive
from .np_122_2010.indicative_shear_strength.cohesive import get_phi_c as _np122_shear_cohesive
from .np_122_2010.indicative_deformation_modulus.non_cohesive import (
    get_deformation_modulus as _np122_deformation_non_cohesive,
)
from .np_122_2010.indicative_deformation_modulus.cohesive import (
    get_deformation_modulus as _np122_deformation_cohesive,
)
from .np_112_2014.presumed_bearing_pressure.rocks import get_presumed_bearing_pressure as _np112_rocks
from .np_112_2014.presumed_bearing_pressure.boulders import get_presumed_bearing_pressure as _np112_boulders
from .np_112_2014.presumed_bearing_pressure.gravels import get_presumed_bearing_pressure as _np112_gravels
from .np_112_2014.presumed_bearing_pressure.sands import get_presumed_bearing_pressure as _np112_sands
from .np_112_2014.presumed_bearing_pressure.fines import get_presumed_bearing_pressure as _np112_fines
from .np_112_2014.presumed_bearing_pressure.fills import get_presumed_bearing_pressure as _np112_fills
from .np_112_2014.allowable_bearing_capacity.working_condition_factor import (
    get_working_condition_factor as _np112_working_condition_factor,
)


@dataclass
class TableEntry:
    normative: str
    table_id: str
    description: str
    lookup_fn: Callable[..., LookupResult]


REGISTRY: dict[str, TableEntry] = {
    "np_122_2010.indicative_shear_strength_non_cohesive": TableEntry(
        normative="NP 122:2010",
        table_id="A.6.1",
        description="Valori caracteristice φ' (grade) pentru pământuri necoezive",
        lookup_fn=_np122_shear_non_cohesive,
    ),
    "np_122_2010.indicative_shear_strength_cohesive": TableEntry(
        normative="NP 122:2010",
        table_id="A.6.2",
        description="Valori orientative φ', c' pentru pământuri coezive (S_r > 0,8)",
        lookup_fn=_np122_shear_cohesive,
    ),
    "np_122_2010.indicative_deformation_modulus_non_cohesive": TableEntry(
        normative="NP 122:2010",
        table_id="A.6.3",
        description="Valori caracteristice E (kPa) pentru pământuri nisipoase",
        lookup_fn=_np122_deformation_non_cohesive,
    ),
    "np_122_2010.indicative_deformation_modulus_cohesive": TableEntry(
        normative="NP 122:2010",
        table_id="A.6.4",
        description="Valori caracteristice E (kPa) pentru pământuri coezive",
        lookup_fn=_np122_deformation_cohesive,
    ),
    "np_112_2014.presumed_bearing_pressure_rocks": TableEntry(
        normative="NP 112:2014",
        table_id="D.1",
        description="Presiuni convenționale p̄_conv [kPa] pentru roci stâncoase și semi-stâncoase",
        lookup_fn=_np112_rocks,
    ),
    "np_112_2014.presumed_bearing_pressure_boulders": TableEntry(
        normative="NP 112:2014",
        table_id="D.2",
        description="Presiuni convenționale p̄_conv [kPa] pentru pământuri foarte grosiere",
        lookup_fn=_np112_boulders,
    ),
    "np_112_2014.presumed_bearing_pressure_gravels": TableEntry(
        normative="NP 112:2014",
        table_id="D.2",
        description="Presiuni convenționale p̄_conv [kPa] pentru pământuri grosiere (pietrișuri)",
        lookup_fn=_np112_gravels,
    ),
    "np_112_2014.presumed_bearing_pressure_sands": TableEntry(
        normative="NP 112:2014",
        table_id="D.3",
        description="Presiuni convenționale p̄_conv [kPa] pentru nisipuri",
        lookup_fn=_np112_sands,
    ),
    "np_112_2014.presumed_bearing_pressure_fines": TableEntry(
        normative="NP 112:2014",
        table_id="D.4",
        description="Presiuni convenționale p̄_conv [kPa] pentru pământuri fine coezive",
        lookup_fn=_np112_fines,
    ),
    "np_112_2014.presumed_bearing_pressure_fills": TableEntry(
        normative="NP 112:2014",
        table_id="D.5",
        description="Presiuni convenționale p̄_conv [kPa] pentru umpluturi",
        lookup_fn=_np112_fills,
    ),
    "np_112_2014.working_condition_factor": TableEntry(
        normative="NP 112:2014",
        table_id="H.7",
        description="Coeficientul condițiilor de lucru mₗ",
        lookup_fn=_np112_working_condition_factor,
    ),
}


def list_tables() -> list[str]:
    return list(REGISTRY)


def get_table(key: str) -> TableEntry:
    if key not in REGISTRY:
        raise KeyError(
            f"Tabel necunoscut: {key!r}. Disponibile: {list_tables()}"
        )
    return REGISTRY[key]
