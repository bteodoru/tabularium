from __future__ import annotations

from tabularium.core.registry import Registry, TableEntry
from .terrain_condition import classify_terrain_condition as _classify

registry = Registry()

registry.register("terrain_condition", TableEntry(
    func=_classify,
    normative="NP 074:2022",
    table_id="A.1–A.3",
    description="Clasificarea condițiilor de teren (Tabelele A.1–A.3, Anexa A)",
))
