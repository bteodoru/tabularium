from __future__ import annotations

from dataclasses import dataclass, field

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


@dataclass
class PConvTableCategory:
    """O categorie de teren din Tabelele D.2–D.3 NP 112:2014."""
    soil_category: str
    soil_label: str
    required_params: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        d: dict = {"soil_category": self.soil_category, "soil_label": self.soil_label}
        if self.required_params:
            d["required_params"] = self.required_params
        return d


@dataclass
class PConvTableFamily:
    """O familie de pământuri din Tabelele D.2–D.4 NP 112:2014."""
    soil_family: str
    table: str
    categories: list[PConvTableCategory] = field(default_factory=list)
    note: str | None = None
    required_params: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        d: dict = {"soil_family": self.soil_family, "table": self.table}
        if self.categories:
            d["categories"] = [c.to_dict() for c in self.categories]
        if self.note:
            d["note"] = self.note
        if self.required_params:
            d["required_params"] = self.required_params
        return d


@dataclass
class PConvTableResult:
    """Tabelele D.2–D.4 complete din NP 112:2014."""
    families: list[PConvTableFamily] = field(default_factory=list)
    note: str = ""

    def to_dict(self) -> dict:
        return {
            "families": [f.to_dict() for f in self.families],
            "note": self.note,
        }
