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
    # True when the user created this category by hand. Such a category keeps its
    # box on the canvas even with no mods filed under it (until the user removes
    # it), unlike a mod-derived category which vanishes when its last mod leaves.
    user_created: bool = False


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
    # Archive size in bytes, taken from the Nexus file record at install time.
    size_bytes: int | None = None
    # The Nexus metadata JSON exactly as parsed when this mod was installed. It
    # is a point-in-time snapshot — the mod page may change or vanish upstream —
    # so it is cached here rather than re-fetched. None when the archive was not
    # matched to a Nexus file (e.g. no API key, or a hand-built archive).
    nexus_metadata: dict | None = None
