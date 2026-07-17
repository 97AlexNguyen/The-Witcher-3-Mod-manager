from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import Enum, auto


class ModStatus(Enum):
    OK = auto()
    INCOMPLETE = auto()
    VAULT_MISSING = auto()
    ERROR = auto()


@dataclass(frozen=True, slots=True)
class Category:
    key: str
    name: str
    color_key: str
    built_in: bool = False


@dataclass(slots=True)
class InstalledMod:
    identity: str
    name: str
    description: str
    version: str | None
    priority: int | None
    enabled: bool
    category_key: str
    installed_on: date
    content: dict[str, tuple[str, ...]] = field(default_factory=dict)
    settings: dict[str, tuple[str, ...]] = field(default_factory=dict)
    keys: dict[str, tuple[str, ...]] = field(default_factory=dict)
    readme: str = ""
    status: ModStatus = ModStatus.OK
    status_detail: str = "Installed cleanly"
    vault_path: str | None = None
    thumbnail_path: str | None = None
