from __future__ import annotations

from dataclasses import dataclass, field

from ...models import CodeSource, LookupResult


@dataclass
class WorkingConditionFactorResult(LookupResult):
    m1: float | None = None


@dataclass
class WorkingConditionTableEntry:
    """Un rând din Tabelul H.7 NP 112:2014."""
    soil_label: str
    m1: float | None = None
    m1_uscat_umed: float | None = None
    m1_saturat: float | None = None
    m1_consistent: float | None = None
    m1_moale: float | None = None
    conditie: str | None = None

    def to_dict(self) -> dict:
        from dataclasses import asdict
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class WorkingConditionTableResult:
    entries: list[WorkingConditionTableEntry] = field(default_factory=list)
    source: CodeSource | None = None
