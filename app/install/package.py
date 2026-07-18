from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

# A *scanned* archive: what an install would put on disk, before anything is
# actually copied. This is the intermediate the roadmap calls ``ModPackage`` —
# inspected but not yet installed — so the UI can preview it and the installer
# can act on it.


class BundleKind(Enum):
    """The two kinds of on-disk content this phase installs.

    Merges into game config (input.xml, user.settings, …) are a separate,
    later phase; a bundle here is a plain folder copy into the game tree.
    """

    MOD = "mod"
    DLC = "dlc"

    @property
    def install_subdir(self) -> str:
        """Folder under the game root this bundle is copied into."""
        return "Mods" if self is BundleKind.MOD else "DLC"

    @property
    def manifest_group(self) -> str:
        """Label used as the content-group key in the manifest, matching the
        existing schema (``"Mods/"`` / ``"DLC/"``)."""
        return "Mods/" if self is BundleKind.MOD else "DLC/"


@dataclass(frozen=True, slots=True)
class Bundle:
    """One deployable folder found in an archive, e.g. ``modFriendlyHUD``."""

    kind: BundleKind
    name: str
    source: Path  # directory inside the extracted tree to copy from


@dataclass(slots=True)
class ModPackage:
    """The result of scanning an extracted archive: which bundles it holds plus
    metadata guessed from the archive itself. Nothing here has touched the game."""

    archive_path: Path
    root: Path
    bundles: list[Bundle] = field(default_factory=list)
    suggested_name: str = ""
    suggested_version: str | None = None
    readme: str = ""

    @property
    def mods(self) -> list[Bundle]:
        return [b for b in self.bundles if b.kind is BundleKind.MOD]

    @property
    def dlcs(self) -> list[Bundle]:
        return [b for b in self.bundles if b.kind is BundleKind.DLC]

    @property
    def is_empty(self) -> bool:
        return not self.bundles

    def content_groups(self) -> dict[str, tuple[str, ...]]:
        """Group bundle names the way the manifest records installed content."""
        groups: dict[str, tuple[str, ...]] = {}
        mods = tuple(b.name for b in self.mods)
        dlcs = tuple(b.name for b in self.dlcs)
        if mods:
            groups[BundleKind.MOD.manifest_group] = mods
        if dlcs:
            groups[BundleKind.DLC.manifest_group] = dlcs
        return groups
