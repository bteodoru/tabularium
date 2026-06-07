from __future__ import annotations

from tabularium.core.registry import Registry, TableEntry  # noqa: F401 — re-exported
from tabularium.np_074_2022.registry import registry as _np074
from tabularium.np_112_2014.registry import registry as _np112
from tabularium.np_122_2010.registry import registry as _np122

registry = Registry()
registry.include(_np074, namespace="np_074_2022")
registry.include(_np112, namespace="np_112_2014")
registry.include(_np122, namespace="np_122_2010")

__all__ = ["registry", "Registry", "TableEntry"]
