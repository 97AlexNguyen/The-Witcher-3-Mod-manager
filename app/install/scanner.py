from __future__ import annotations

import os
import re
from collections.abc import Iterable
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
README_MAX_CHARS = 4000

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
    """Collect mod/dlc bundles from an extracted tree at *root*."""
    return [
        Bundle(kind, name, root.joinpath(*path))
        for kind, name, path in classify_dirs(_relative_dir_paths(root))
    ]


def _relative_dir_paths(root: Path) -> list[tuple[str, ...]]:
    """Every directory under *root*, as segment tuples relative to it."""
    paths: list[tuple[str, ...]] = []
    for dirpath, dirnames, _files in os.walk(root):
        rel = Path(dirpath).relative_to(root)
        base = () if rel == Path(".") else rel.parts
        for name in dirnames:
            paths.append((*base, name))
    return paths


def classify_dirs(
    dir_paths: Iterable[tuple[str, ...]],
) -> list[tuple[BundleKind, str, tuple[str, ...]]]:
    """Decide which directories are bundles, given every directory in a tree.

    Works purely on directory *paths* (segment tuples), so the same rules apply
    whether the tree lives on disk or is reconstructed from an archive's entry
    listing — the pre-install preview and the real install therefore always agree
    on what will be installed. Returns ``(kind, bundle_name, path)`` tuples, the
    path being the bundle directory's segments.

    Rule 1 (preferred): the immediate child dirs of any ``Mods``/``DLC`` container
    are bundles of that kind. A container nested inside another container is
    ignored, mirroring the disk walk which never descends into a container.

    Rule 2 (fallback, only when rule 1 finds nothing): a loose top-level dir whose
    name starts with ``mod``/``dlc`` is a bundle of that kind.
    """
    dirs = {tuple(path) for path in dir_paths if path}
    containers = {
        path: _CONTAINER_NAMES[path[-1].casefold()]
        for path in dirs
        if path[-1].casefold() in _CONTAINER_NAMES
    }

    found: list[tuple[BundleKind, str, tuple[str, ...]]] = []
    for container, kind in containers.items():
        if _has_container_ancestor(container, containers):
            continue
        for path in dirs:
            if len(path) == len(container) + 1 and path[:-1] == container:
                found.append((kind, path[-1], path))

    if not found:
        for path in dirs:
            if len(path) != 1:
                continue
            for prefixes, kind in _PREFIX_KINDS:
                if path[0].casefold().startswith(prefixes):
                    found.append((kind, path[0], path))
                    break

    return _dedupe(sorted(found, key=lambda item: item[2]))


def dir_paths_from_names(names: Iterable[str]) -> set[tuple[str, ...]]:
    """Reconstruct the set of directory paths implied by archive entry names.

    An entry like ``Mods/modX/content/blob.bundle`` implies the directories
    ``Mods``, ``Mods/modX`` and ``Mods/modX/content``. Explicit directory entries
    (trailing slash) are honoured too. Separators are normalised so archives that
    use backslashes are handled.
    """
    dirs: set[tuple[str, ...]] = set()
    for raw in names:
        normalised = raw.replace("\\", "/")
        segments = [segment for segment in normalised.strip("/").split("/") if segment]
        if not segments:
            continue
        # A file entry contributes only its parent dirs; a dir entry itself counts.
        depth = len(segments) if normalised.endswith("/") else len(segments) - 1
        for cut in range(1, depth + 1):
            dirs.add(tuple(segments[:cut]))
    return dirs


def readme_entry_name(names: Iterable[str]) -> str | None:
    """The archive entry for a top-level readme, matching the disk scan's rule of
    only looking at root-level files. ``None`` when the archive has no readme."""
    candidates: list[str] = []
    for raw in names:
        normalised = raw.replace("\\", "/")
        if normalised.endswith("/") or "/" in normalised.strip("/"):
            continue  # a directory, or not at the top level
        if normalised.strip("/").casefold() in _README_NAMES:
            candidates.append(raw)
    return sorted(candidates, key=str.casefold)[0] if candidates else None


def _has_container_ancestor(
    path: tuple[str, ...], containers: dict[tuple[str, ...], BundleKind]
) -> bool:
    return any(path[:cut] in containers for cut in range(1, len(path)))


def _dedupe(
    bundles: list[tuple[BundleKind, str, tuple[str, ...]]],
) -> list[tuple[BundleKind, str, tuple[str, ...]]]:
    seen: set[tuple[BundleKind, str]] = set()
    unique: list[tuple[BundleKind, str, tuple[str, ...]]] = []
    for kind, name, path in bundles:
        key = (kind, name.casefold())
        if key in seen:
            continue
        seen.add(key)
        unique.append((kind, name, path))
    return unique


def _find_readme(root: Path) -> str:
    for child in _files_in(root):
        if child.name.casefold() in _README_NAMES:
            try:
                text = child.read_text("utf-8", errors="replace")
            except OSError:
                return ""
            return text.strip()[:README_MAX_CHARS]
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
