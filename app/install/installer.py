from __future__ import annotations

import shutil
import tempfile
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from app.data import slugify
from app.domain import InstalledMod, ModStatus
from app.install.errors import EmptyPackageError, GamePathError
from app.install.extract import extract_archive
from app.install.package import Bundle, ModPackage
from app.install.scanner import scan_package

# Put a scanned package on disk and describe the installed mod for the manifest.
#
# Scope for this phase (roadmap): copy ``Mods/`` and ``DLC/`` bundles into the
# game tree and vault the source archive. Merging into game config (input.xml,
# user.settings, …) is deliberately NOT done here — that is a later phase, and
# a mod with no config needs is fully installed by the copy alone.


@dataclass(slots=True)
class InstallResult:
    """What an install produced: the manifest record plus where files landed."""

    mod: InstalledMod
    installed_paths: list[Path]
    vaulted_archive: Path | None


def install_package(
    package: ModPackage,
    game_path: Path | str,
    vault_path: Path | str | None = None,
    *,
    installed_on: date | None = None,
) -> InstallResult:
    """Copy *package*'s bundles into the game and record an :class:`InstalledMod`.

    Raises :class:`GamePathError` if *game_path* is not a directory and
    :class:`EmptyPackageError` if the package has no bundles to install.
    """
    game = Path(game_path)
    if not game.is_dir():
        raise GamePathError(f"Game folder does not exist: {game}")
    if package.is_empty:
        raise EmptyPackageError(
            "The archive contains no Mods or DLC folders to install."
        )

    installed_paths = [_deploy_bundle(bundle, game) for bundle in package.bundles]
    vaulted = _vault_archive(package.archive_path, vault_path)

    mod = _record(package, vaulted, installed_on or date.today())
    return InstallResult(mod=mod, installed_paths=installed_paths, vaulted_archive=vaulted)


def install_archive(
    archive_path: Path | str,
    game_path: Path | str,
    vault_path: Path | str | None = None,
    *,
    installed_on: date | None = None,
) -> InstallResult:
    """Extract, scan, and install *archive_path* in one step.

    Extraction happens in a temporary directory that is removed once the bundles
    have been copied into the game.
    """
    archive = Path(archive_path)
    with tempfile.TemporaryDirectory(prefix="w3mm-extract-") as tmp:
        root = extract_archive(archive, Path(tmp))
        package = scan_package(root, archive)
        return install_package(
            package, game_path, vault_path, installed_on=installed_on
        )


def _deploy_bundle(bundle: Bundle, game: Path) -> Path:
    """Copy one bundle folder into ``<game>/Mods`` or ``<game>/DLC``.

    ``dirs_exist_ok`` lets a reinstall overwrite an existing bundle in place
    rather than failing on the second install.
    """
    dest = game / bundle.kind.install_subdir / bundle.name
    shutil.copytree(bundle.source, dest, dirs_exist_ok=True)
    return dest


def _vault_archive(archive: Path, vault_path: Path | str | None) -> Path | None:
    """Copy the source archive into the vault so the mod can be reinstalled."""
    if not vault_path:
        return None
    vault = Path(vault_path)
    vault.mkdir(parents=True, exist_ok=True)
    target = vault / archive.name
    shutil.copy2(archive, target)
    return target


def _record(package: ModPackage, vaulted: Path | None, when: date) -> InstalledMod:
    name = package.suggested_name or package.archive_path.stem
    bundle_count = len(package.bundles)
    return InstalledMod(
        identity=slugify(name),
        name=name,
        description=package.readme.splitlines()[0] if package.readme else "",
        version=package.suggested_version,
        priority=None,
        enabled=True,
        category_key="uncategorized",
        installed_on=when,
        content=package.content_groups(),
        readme=package.readme,
        status=ModStatus.OK,
        status_detail=(
            f"Installed {bundle_count} folder{'s' if bundle_count != 1 else ''} "
            "to disk (Mods/DLC)"
        ),
        vault_path=str(vaulted) if vaulted is not None else None,
    )
