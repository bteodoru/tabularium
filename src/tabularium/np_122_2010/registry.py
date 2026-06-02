from __future__ import annotations

from tabularium.core.registry import Registry, TableEntry
from .indicative_shear_strength.non_cohesive import get_phi as _shear_non_cohesive
from .indicative_shear_strength.cohesive import get_phi_c as _shear_cohesive
from .indicative_deformation_modulus.non_cohesive import (
    get_deformation_modulus as _deformation_non_cohesive,
)
from .indicative_deformation_modulus.cohesive import (
    get_deformation_modulus as _deformation_cohesive,
)

registry = Registry()

registry.register("indicative_shear_strength_non_cohesive", TableEntry(
    func=_shear_non_cohesive,
    normative="NP 122:2010",
    table_id="A.6.1",
    description="Valori caracteristice φ' (grade) pentru pământuri necoezive",
))
registry.register("indicative_shear_strength_cohesive", TableEntry(
    func=_shear_cohesive,
    normative="NP 122:2010",
    table_id="A.6.2",
    description="Valori orientative φ', c' pentru pământuri coezive (S_r > 0,8)",
))
registry.register("indicative_deformation_modulus_non_cohesive", TableEntry(
    func=_deformation_non_cohesive,
    normative="NP 122:2010",
    table_id="A.6.3",
    description="Valori caracteristice E (kPa) pentru pământuri nisipoase",
))
registry.register("indicative_deformation_modulus_cohesive", TableEntry(
    func=_deformation_cohesive,
    normative="NP 122:2010",
    table_id="A.6.4",
    description="Valori caracteristice E (kPa) pentru pământuri coezive",
))
