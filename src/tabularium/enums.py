from __future__ import annotations

from enum import Enum


class _LabeledEnum(str, Enum):
    def __new__(cls, value: str, label: str):
        obj = str.__new__(cls, value)
        obj._value_ = value
        obj.label = label
        return obj


class Soil(_LabeledEnum):
    # NP 122:2010 
    SAND_WITH_GRAVEL          = ("sand_with_gravel",          "Nisip cu pietriș")
    COARSE_SAND               = ("coarse_sand",               "Nisip mare")
    MEDIUM_SAND               = ("medium_sand",               "Nisip mijlociu")
    FINE_SAND                 = ("fine_sand",                 "Nisip fin")
    SILTY_SAND                = ("silty_sand",                "Nisip prăfos")

    # NP 112:2014 D.1 — roci
    ROCKY                     = ("rocky",                     "Rocă stâncoasă")
    SEMI_ROCKY_MARL           = ("semi_rocky_marl",           "Rocă semi-stâncoasă (marnă, marnă argiloasă, argilă marnoasă compactă)")
    SEMI_ROCKY_SHALE          = ("semi_rocky_shale",          "Rocă semi-stâncoasă (șist argilos, argila șistoasă, nisipuri cimentate)")

    # NP 112:2014 D.2 — boulders
    BOULDER_GRAVEL_FILL       = ("boulder_gravel_fill",       "Bolovăniș cu interspațiile umplute cu pietriș")
    BOULDER_COHESIVE_FILL     = ("boulder_cohesive_fill",     "Bolovăniș cu interspațiile umplute cu pământuri coezive")

    # NP 112:2014 D.2 — gravels
    GRAVEL_CLEAN_CRYSTAL      = ("gravel_clean_crystal",      "Pietriș curat cristalin")
    GRAVEL_WITH_SAND          = ("gravel_with_sand",          "Pietriș cu nisip")
    GRAVEL_SEDIMENTARY        = ("gravel_sedimentary",        "Pietriș din fragmente de roci sedimentare")
    GRAVEL_CLAYEY_SAND         = ("gravel_clayey_sand",       "Pietriș cu nisip argilos")

    # NP 112:2014 H.7 — working condition factor
    BOULDER_SAND_FILL         = ("boulder_sand_fill",         "Bolovăniș cu interspațiile umplute cu nisip")
    GRAVEL                    = ("gravel",                    "Pietriș")
    GRAVEL_COHESIVE_FILL      = ("gravel_cohesive_fill",      "Pietriș cu interspațiile umplute cu pământuri coezive")




class RelativeDensity(_LabeledEnum):
    MEDIUM = ("medium", "Medie")   # I_D = 35…65%
    DENSE  = ("dense",  "Densă")   # I_D > 65%


class MoistureCondition(_LabeledEnum):
    DRY        = ("dry",        "Uscat")
    MOIST      = ("moist",      "Umed")
    VERY_MOIST = ("very_moist", "Foarte umed")
    SATURATED  = ("saturated",  "Saturat")


class PlasticityClass(_LabeledEnum):
    LOW    = ("low",    "Plasticitate scăzută")   # I_P ≤ 10%
    MEDIUM = ("medium", "Plasticitate medie")      # 10% < I_P ≤ 20%
    HIGH   = ("high",   "Plasticitate ridicată")   # I_P > 20%


class FillType(_LabeledEnum):
    CONTROLLED_COMPACTED = ("controlled_compacted", "Umpluturi compactate controlat")
    KNOWN_ORIGIN         = ("known_origin",         "Umpluturi de proveniență cunoscută")


class FillSoilType(_LabeledEnum):
    SANDY_SLAG = ("sandy_slag", "Pământuri nisipoase și zguri")
    SILTY_FINE = ("silty_fine", "Nisipuri prăfoase, coezive, cenușe")


class SoilCategory(_LabeledEnum):
    COHESIVE     = ("cohesive",     "Coeziv")
    NON_COHESIVE = ("non_cohesive", "Necoeziv")
