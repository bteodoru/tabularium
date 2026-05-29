from __future__ import annotations

from dataclasses import dataclass

from ...enums import SoilCategory
from ...models import LookupResult


@dataclass
class PresumedBearingPressureResult(LookupResult):
    p_conv: float | None = None
    p_conv_range: tuple[float, float] | None = None
    soil_type: SoilCategory | None = None

    @property
    def is_resolved(self) -> bool:
        return self.p_conv is not None
