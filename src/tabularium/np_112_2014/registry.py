from __future__ import annotations

from tabularium.core.registry import Registry, TableEntry
from .presumed_bearing_pressure.rocks import get_presumed_bearing_pressure as _rocks
from .presumed_bearing_pressure.boulders import get_presumed_bearing_pressure as _boulders
from .presumed_bearing_pressure.gravels import get_presumed_bearing_pressure as _gravels
from .presumed_bearing_pressure.sands import get_presumed_bearing_pressure as _sands
from .presumed_bearing_pressure.fines import get_presumed_bearing_pressure as _fines
from .presumed_bearing_pressure.fills import get_presumed_bearing_pressure as _fills
from .allowable_bearing_capacity.working_condition_factor import (
    get_working_condition_factor as _wcf,
)

registry = Registry()

registry.register("presumed_bearing_pressure_rocks", TableEntry(
    func=_rocks,
    normative="NP 112:2014",
    table_id="D.1",
    description="Presiuni convenționale p̄_conv [kPa] pentru roci stâncoase și semi-stâncoase",
))
registry.register("presumed_bearing_pressure_boulders", TableEntry(
    func=_boulders,
    normative="NP 112:2014",
    table_id="D.2",
    description="Presiuni convenționale p̄_conv [kPa] pentru pământuri foarte grosiere",
))
registry.register("presumed_bearing_pressure_gravels", TableEntry(
    func=_gravels,
    normative="NP 112:2014",
    table_id="D.2",
    description="Presiuni convenționale p̄_conv [kPa] pentru pământuri grosiere (pietrișuri)",
))
registry.register("presumed_bearing_pressure_sands", TableEntry(
    func=_sands,
    normative="NP 112:2014",
    table_id="D.3",
    description="Presiuni convenționale p̄_conv [kPa] pentru nisipuri",
))
registry.register("presumed_bearing_pressure_fines", TableEntry(
    func=_fines,
    normative="NP 112:2014",
    table_id="D.4",
    description="Presiuni convenționale p̄_conv [kPa] pentru pământuri fine coezive",
))
registry.register("presumed_bearing_pressure_fills", TableEntry(
    func=_fills,
    normative="NP 112:2014",
    table_id="D.5",
    description="Presiuni convenționale p̄_conv [kPa] pentru umpluturi",
))
registry.register("working_condition_factor", TableEntry(
    func=_wcf,
    normative="NP 112:2014",
    table_id="H.7",
    description="Coeficientul condițiilor de lucru mₗ",
))
