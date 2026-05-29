from __future__ import annotations

from dataclasses import dataclass, field

from ...models import CodeSource, LookupResult


@dataclass
class WorkingConditionFactorResult(LookupResult):
    ml: float | None = None


@dataclass
class WorkingConditionTableEntry:
    """Un rând din Tabelul H.7 NP 112:2014."""
    soil_label: str
    ml: float | None = None
    ml_uscat_umed: float | None = None
    ml_saturat: float | None = None
    ml_consistent: float | None = None
    ml_moale: float | None = None
    conditie: str | None = None

    def to_dict(self) -> dict:
        from dataclasses import asdict
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class WorkingConditionTableResult:
    entries: list[WorkingConditionTableEntry] = field(default_factory=list)
    source: CodeSource | None = None
