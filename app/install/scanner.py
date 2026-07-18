from __future__ import annotations

import os
import re
from pathlib import Path

from app.install.package import Bundle, BundleKind, ModPackage

# Turn an extracted archive tree into a :class:`ModPackage`. Real Witcher 3 mod
# archives are laid out inconsistently, so this handles the common shapes:
#
#   1. Wrapped:  <root>/Mods/modX/... , <root>/DLC/dlcX/...
#   2. Nested:   <root>/Some Name/Mods/modX/...   (extra folder from the zipper)
#   3. Loose:    <root>/modX/... , <root>/dlcX/... (no Mods/DLC wrapper at all)
#
# Shapes 1 and 2 are the same rule — find any folder named ``Mods``/``DLC`` and
# treat its immediate children as bundles. Only when none exists do we fall back
# to matching top-level folders by their ``mod``/``dlc`` name prefix.

# Folders whose *immediate children* are bundles of the mapped kind.
_CONTAINER_NAMES = {"mods": BundleKind.MOD, "dlc": BundleKind.DLC}

# Fallback: a loose top-level folder is classified by its name prefix.
_PREFIX_KINDS = ((("dlc",), BundleKind.DLC), (("mod",), BundleKind.MOD))

_README_NAMES = ("readme.txt", "readme.md", "read me.txt", "readme")
_README_MAX_CHARS = 4000

# Nexus download filenames look like ``Name-<modid>-<ver-with-dashes>-<stamp>``,
# e.g. ``Friendly HUD-201-13-6-1650000000``. Dots in the version are dashes.
_NEXUS_RE = re.compile(r"^(?P<name>.+?)-\d+-(?P<ver>\d[\d-]*?)-\d{6,}$")
# Generic fallback: a trailing dotted version like ``... v1.2.3`` or ``...-2.0``.
_TRAILING_VER_RE = re.compile(r"[ _-]v?(\d+(?:\.\d+)+)$", re.IGNORECASE)


def scan_package(root: Path | str, archive_path: Path | str) -> ModPackage:
    """Inspect an already-extracted tree at *root* and describe what it installs."""
    root_path = Path(root)
    archive = Path(archive_path)
    bundles = _find_bundles(root_path)
    name, version = parse_archive_name(archive.name)
    return ModPackage(
        archive_path=archive,
        root=root_path,
        bundles=bundles,
        suggested_name=name,
        suggested_version=version,
        readme=_find_readme(root_path),
    )


def _find_bundles(root: Path) -> list[Bundle]:
    """Collect mod/dlc bundles, preferring explicit Mods/DLC containers."""
    found: list[Bundle] = []
    for dirpath, dirnames, _files in os.walk(root):
        here = Path(dirpath)
        keep_descending: list[str] = []
        for name in dirnames:
            kind = _CONTAINER_NAMES.get(name.casefold())
            if kind is None:
                keep_descending.append(name)
                continue
            for child in _child_dirs(here / name):
                found.append(Bundle(kind, child.name, child))
        # Don't walk into a container we already harvested; still descend the rest
        # so a nested ``Some Name/Mods`` layout is reached.
        dirnames[:] = keep_descending

    if found:
        return _dedupe(found)

    # No Mods/DLC folder anywhere — classify loose top-level folders by prefix.
    for child in _child_dirs(root):
        for prefixes, kind in _PREFIX_KINDS:
            if child.name.casefold().startswith(prefixes):
                found.append(Bundle(kind, child.name, child))
                break
    return _dedupe(found)


def _child_dirs(parent: Path) -> list[Path]:
    try:
        return sorted((c for c in parent.iterdir() if c.is_dir()), key=lambda p: p.name)
    except OSError:
        return []


def _dedupe(bundles: list[Bundle]) -> list[Bundle]:
    seen: set[tuple[BundleKind, str]] = set()
    unique: list[Bundle] = []
    for bundle in bundles:
        key = (bundle.kind, bundle.name.casefold())
        if key in seen:
            continue
        seen.add(key)
        unique.append(bundle)
    return unique


def _find_readme(root: Path) -> str:
    for child in _files_in(root):
        if child.name.casefold() in _README_NAMES:
            try:
                text = child.read_text("utf-8", errors="replace")
            except OSError:
                return ""
            return text.strip()[:_README_MAX_CHARS]
    return ""


def _files_in(parent: Path) -> list[Path]:
    try:
        return sorted((c for c in parent.iterdir() if c.is_file()), key=lambda p: p.name)
    except OSError:
        return []


def parse_archive_name(filename: str) -> tuple[str, str | None]:
    """Best-effort (display name, version) from a download filename.

    Only a hint for now — the Nexus API is expected to overwrite both later
    (roadmap: "Version source"). Returns the cleaned stem and ``None`` version
    when nothing version-like is found.
    """
    stem = Path(filename).stem

    match = _NEXUS_RE.match(stem)
    if match:
        name = _clean_name(match.group("name"))
        version = match.group("ver").replace("-", ".")
        return name or stem, version or None

    trailing = _TRAILING_VER_RE.search(stem)
    if trailing:
        name = _clean_name(stem[: trailing.start()])
        return name or stem, trailing.group(1)

    return _clean_name(stem) or stem, None


def _clean_name(raw: str) -> str:
    return re.sub(r"[\s_-]+", " ", raw).strip()
