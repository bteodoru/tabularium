from __future__ import annotations

from enum import Enum


class SoilCategory(str, Enum):
    # NP 122:2010 — existente
    GRAVEL_COARSE_SAND        = "gravel_coarse_sand"
    GRAVEL_COARSE_MEDIUM_SAND = "gravel_coarse_medium_sand"
    MEDIUM_SAND               = "medium_sand"
    FINE_SAND                 = "fine_sand"
    SILTY_SAND                = "silty_sand"

    # NP 112:2014 D.1 — roci
    ROCKY                     = "rocky"
    SEMI_ROCKY_MARL           = "semi_rocky_marl"
    SEMI_ROCKY_SHALE          = "semi_rocky_shale"

    # NP 112:2014 D.2 — boulders
    BOULDER_GRAVEL_FILL       = "boulder_gravel_fill"
    BOULDER_CLAY_FILL         = "boulder_clay_fill"

    # NP 112:2014 D.2 — gravels
    GRAVEL_CLEAN_CRYSTAL      = "gravel_clean_crystal"
    GRAVEL_WITH_SAND          = "gravel_with_sand"
    GRAVEL_SEDIMENTARY        = "gravel_sedimentary"
    GRAVEL_SILTY_SAND         = "gravel_silty_sand"

    # NP 112:2014 D.3 — sands
    COARSE_SAND               = "coarse_sand"


class RelativeDensity(str, Enum):
    MEDIUM = "medium"  # I_D = 35…65%
    DENSE  = "dense"   # I_D > 65%


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


class SoilType(str, Enum):
    COHESIVE     = "cohesive"
    NON_COHESIVE = "non_cohesive"


# None pentru roci — corecțiile din metoda prescriptivă nu se aplică pe baza acestei axe
_SOIL_TYPE: dict[SoilCategory, SoilType | None] = {
    # NP 122:2010
    SoilCategory.GRAVEL_COARSE_SAND:        SoilType.NON_COHESIVE,
    SoilCategory.GRAVEL_COARSE_MEDIUM_SAND: SoilType.NON_COHESIVE,
    SoilCategory.MEDIUM_SAND:               SoilType.NON_COHESIVE,
    SoilCategory.FINE_SAND:                 SoilType.NON_COHESIVE,
    SoilCategory.SILTY_SAND:                SoilType.NON_COHESIVE,
    # NP 112:2014 D.1 — roci
    SoilCategory.ROCKY:                     None,
    SoilCategory.SEMI_ROCKY_MARL:           None,
    SoilCategory.SEMI_ROCKY_SHALE:          None,
    # NP 112:2014 D.2 — boulders
    SoilCategory.BOULDER_GRAVEL_FILL:       SoilType.NON_COHESIVE,
    SoilCategory.BOULDER_CLAY_FILL:         SoilType.COHESIVE,
    # NP 112:2014 D.2 — gravels
    SoilCategory.GRAVEL_CLEAN_CRYSTAL:      SoilType.NON_COHESIVE,
    SoilCategory.GRAVEL_WITH_SAND:          SoilType.NON_COHESIVE,
    SoilCategory.GRAVEL_SEDIMENTARY:        SoilType.NON_COHESIVE,
    SoilCategory.GRAVEL_SILTY_SAND:         SoilType.NON_COHESIVE,
    # NP 112:2014 D.3 — sands
    SoilCategory.COARSE_SAND:               SoilType.NON_COHESIVE,
}


def get_soil_type(category: SoilCategory) -> SoilType | None:
    """Returnează tipul de sol (cohesiv/necohesiv) sau None pentru roci."""
    return _SOIL_TYPE[SoilCategory(category)]
