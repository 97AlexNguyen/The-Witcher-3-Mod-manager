from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path

from app.domain import InstalledMod
from app.install.errors import GamePathError, UninstallError

# Only these manifest content groups represent plain copied folders. Game config
# groups will be handled by their format-specific unmerge flows in a later phase.
_CONTENT_ROOTS = {
    "Mods/": "Mods",
    "DLC/": "DLC",
}


@dataclass(frozen=True, slots=True)
class UninstallResult:
    """Summary of removing one mod's tracked copied content from the game."""

    removed_paths: tuple[Path, ...]
    missing_paths: tuple[Path, ...]
    shared_paths: tuple[Path, ...]


def uninstall_mod(
    mod: InstalledMod,
    game_path: Path | str,
    installed_mods: tuple[InstalledMod, ...] | list[InstalledMod] = (),
) -> UninstallResult:
    """Remove a mod's tracked ``Mods/`` and ``DLC/`` bundle folders.

    The vaulted source archive is intentionally retained for future reinstall.
    A bundle also claimed by another manifest record is left on disk so removing
    one mod cannot break another. Missing folders count as already removed.

    Raises :class:`UninstallError` for unsafe manifest entries or deletion
    failures. If deletion is partial, the caller should retain the manifest
    record so the operation can be retried.
    """
    game = Path(game_path)
    if not game.is_dir():
        raise GamePathError(f"Game folder does not exist: {game}")

    shared = _content_claims(installed_mods, excluding=mod)
    removed_paths: list[Path] = []
    missing_paths: list[Path] = []
    shared_paths: list[Path] = []
    failures: list[str] = []

    for group, names in mod.content.items():
        root_name = _CONTENT_ROOTS.get(group)
        if root_name is None:
            continue
        for name in names:
            try:
                target = _safe_bundle_path(game, root_name, name)
            except ValueError as exc:
                failures.append(str(exc))
                continue

            claim = (group.casefold(), name.casefold())
            if claim in shared:
                shared_paths.append(target)
                continue
            if not target.exists() and not target.is_symlink():
                missing_paths.append(target)
                continue
            try:
                if target.is_symlink() or target.is_file():
                    target.unlink()
                else:
                    shutil.rmtree(target)
            except OSError as exc:
                failures.append(f"{target}: {exc}")
            else:
                removed_paths.append(target)

    if failures:
        raise UninstallError(
            "Could not remove all tracked content: " + "; ".join(failures),
            removed_paths=tuple(str(path) for path in removed_paths),
            failed_paths=tuple(failures),
        )

    return UninstallResult(
        removed_paths=tuple(removed_paths),
        missing_paths=tuple(missing_paths),
        shared_paths=tuple(shared_paths),
    )


def _content_claims(
    mods: tuple[InstalledMod, ...] | list[InstalledMod],
    *,
    excluding: InstalledMod,
) -> set[tuple[str, str]]:
    claims: set[tuple[str, str]] = set()
    for candidate in mods:
        if candidate is excluding or candidate.identity == excluding.identity:
            continue
        for group, names in candidate.content.items():
            if group not in _CONTENT_ROOTS:
                continue
            claims.update((group.casefold(), name.casefold()) for name in names)
    return claims


def _safe_bundle_path(game: Path, root_name: str, name: str) -> Path:
    """Return a direct child of a content root, rejecting path traversal."""
    if (
        not isinstance(name, str)
        or not name
        or name in {".", ".."}
        or "/" in name
        or "\\" in name
        or Path(name).is_absolute()
    ):
        raise ValueError(f"Unsafe manifest content path: {name!r}")

    root = (game / root_name).resolve()
    target = root / name
    if target.parent.resolve() != root:
        raise ValueError(f"Unsafe manifest content path: {name!r}")
    return target
