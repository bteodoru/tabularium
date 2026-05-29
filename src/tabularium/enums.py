from __future__ import annotations

from enum import Enum


class Soil(str, Enum):
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
    BOULDER_COHESIVE_FILL         = "boulder_clay_fill"

    # NP 112:2014 D.2 — gravels
    GRAVEL_CLEAN_CRYSTAL      = "gravel_clean_crystal"
    GRAVEL_WITH_SAND          = "gravel_with_sand"
    GRAVEL_SEDIMENTARY        = "gravel_sedimentary"
    GRAVEL_SILTY_SAND         = "gravel_silty_sand"

    # NP 112:2014 H.7 — working condition factor
    BOULDER_SAND_FILL         = "boulder_sand_fill"
    GRAVEL                    = "gravel"
    GRAVEL_COHESIVE_FILL      = "gravel_cohesive_fill"
    COHESIVE_SOIL             = "cohesive_soil"

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


class SoilCategory(str, Enum):
    COHESIVE     = "cohesive"
    NON_COHESIVE = "non_cohesive"
