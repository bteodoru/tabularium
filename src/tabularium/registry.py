from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from .models import LookupResult
from .np_122_2010.indicative_shear_strength_non_cohesive import get_phi as _np122_shear_non_cohesive
from .np_122_2010.indicative_shear_strength_cohesive import get_phi_c as _np122_shear_cohesive
from .np_122_2010.indicative_deformation_modulus_non_cohesive import (
    get_deformation_modulus as _np122_deformation_non_cohesive,
)
from .np_122_2010.indicative_deformation_modulus_cohesive import (
    get_deformation_modulus as _np122_deformation_cohesive,
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
}


def list_tables() -> list[str]:
    return list(REGISTRY)


def get_table(key: str) -> TableEntry:
    if key not in REGISTRY:
        raise KeyError(
            f"Tabel necunoscut: {key!r}. Disponibile: {list_tables()}"
        )
    return REGISTRY[key]
