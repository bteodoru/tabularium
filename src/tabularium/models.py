from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class CodeSource:
    code: str
    table: str
    section: str | None = None


@dataclass
class LookupResult:
    valid: bool = False
    interpolated: bool = False
    source: CodeSource | None = None
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
