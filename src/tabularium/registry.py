from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from .models import LookupResult
from .np122.indicative_shear_strength import get_phi_c as _np122_shear


@dataclass
class TableEntry:
    normative: str
    table_id: str
    description: str
    lookup_fn: Callable[..., LookupResult]


REGISTRY: dict[str, TableEntry] = {
    "np122.indicative_shear_strength": TableEntry(
        normative="NP 122:2010",
        table_id="A.6.2",
        description="Valori orientative φ', c' pentru pământuri coezive (S_r > 0,8)",
        lookup_fn=_np122_shear,
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
