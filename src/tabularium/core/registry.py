from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass


@dataclass
class TableEntry:
    func: Callable
    normative: str
    table_id: str
    description: str


class Registry:
    def __init__(self) -> None:
        self._entries: dict[str, TableEntry] = {}

    def register(self, name: str, entry: TableEntry) -> None:
        self._entries[name] = entry

    def include(self, other: Registry, namespace: str | None = None) -> None:
        for name, entry in other._entries.items():
            key = f"{namespace}.{name}" if namespace else name
            self._entries[key] = entry

    def get(self, name: str) -> TableEntry:
        if name not in self._entries:
            raise KeyError(
                f"Tabel necunoscut: {name!r}. Disponibile: {list(self._entries)}"
            )
        return self._entries[name]

    def all(self) -> dict[str, TableEntry]:
        return dict(self._entries)
