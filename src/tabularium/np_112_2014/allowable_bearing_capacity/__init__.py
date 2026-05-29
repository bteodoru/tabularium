from __future__ import annotations

from dataclasses import dataclass

from ...models import LookupResult


@dataclass
class WorkingConditionFactorResult(LookupResult):
    m1: float | None = None
