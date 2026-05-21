from __future__ import annotations

from enum import Enum


class SoilCategory(str, Enum):
    GRAVEL_COARSE_SAND        = "gravel_coarse_sand"         # Nisip cu pietriș și nisip mare
    GRAVEL_COARSE_MEDIUM_SAND = "gravel_coarse_medium_sand"  # Nisip cu pietriș și nisip mare și mijlociu
    MEDIUM_SAND               = "medium_sand"                # Nisip mijlociu
    FINE_SAND                 = "fine_sand"                  # Nisip fin
    SILTY_SAND                = "silty_sand"                 # Nisip prăfos


class RelativeDensity(str, Enum):
    MEDIUM = "medium"  # I_D = 35…65%
    DENSE  = "dense"   # I_D > 65%
