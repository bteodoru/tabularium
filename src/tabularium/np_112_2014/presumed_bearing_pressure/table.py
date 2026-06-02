from __future__ import annotations

from ...enums import PlasticityClass, Soil
from . import PConvTableCategory, PConvTableFamily, PConvTableResult


def get_p_conv_table() -> PConvTableResult:
    """Returnează Tabelele D.2–D.4 complete din NP 112:2014 cu labels în română."""
    boulders_gravels = PConvTableFamily(
        soil_family="boulders_gravels",
        table="NP 112:2014, Tabelul D.2",
        categories=[
            PConvTableCategory(
                soil_category=Soil.BOULDER_GRAVEL_FILL.value,
                soil_label=Soil.BOULDER_GRAVEL_FILL.label,
            ),
            PConvTableCategory(
                soil_category=Soil.BOULDER_COHESIVE_FILL.value,
                soil_label=Soil.BOULDER_COHESIVE_FILL.label,
                required_params=["consistency_index"],
            ),
            PConvTableCategory(
                soil_category=Soil.GRAVEL_CLEAN_CRYSTAL.value,
                soil_label=Soil.GRAVEL_CLEAN_CRYSTAL.label,
            ),
            PConvTableCategory(
                soil_category=Soil.GRAVEL_WITH_SAND.value,
                soil_label=Soil.GRAVEL_WITH_SAND.label,
            ),
            PConvTableCategory(
                soil_category=Soil.GRAVEL_SEDIMENTARY.value,
                soil_label=Soil.GRAVEL_SEDIMENTARY.label,
            ),
            PConvTableCategory(
                soil_category=Soil.GRAVEL_CLAYEY_SAND.value,
                soil_label=Soil.GRAVEL_CLAYEY_SAND.label,
                required_params=["consistency_index"],
            ),
        ],
    )

    sands = PConvTableFamily(
        soil_family="sands",
        table="NP 112:2014, Tabelul D.3",
        categories=[
            PConvTableCategory(
                soil_category=Soil.COARSE_SAND.value,
                soil_label=Soil.COARSE_SAND.label,
                required_params=["relative_density"],
            ),
            PConvTableCategory(
                soil_category=Soil.MEDIUM_SAND.value,
                soil_label=Soil.MEDIUM_SAND.label,
                required_params=["relative_density"],
            ),
            PConvTableCategory(
                soil_category=Soil.FINE_SAND.value,
                soil_label=Soil.FINE_SAND.label,
                required_params=["relative_density", "moisture_condition"],
            ),
            PConvTableCategory(
                soil_category=Soil.SILTY_SAND.value,
                soil_label=Soil.SILTY_SAND.label,
                required_params=["relative_density", "moisture_condition"],
            ),
        ],
    )

    fines = PConvTableFamily(
        soil_family="fines",
        table="NP 112:2014, Tabelul D.4",
        note=(
            "Pământuri fine coezive — fără categorii fixe. "
            "Valoarea se interpolează din tabel pe baza clasei de plasticitate, "
            "indicelui porilor și indicelui de consistență."
        ),
        required_params=["plasticity_class", "void_ratio", "consistency_index"],
    )

    return PConvTableResult(
        families=[boulders_gravels, sands, fines],
        note=(
            "Rocile (Tabelul D.1) nu sunt incluse — returnează întotdeauna un interval, "
            "incompatibil cu metoda prescriptivă care necesită o valoare scalară."
        ),
    )
