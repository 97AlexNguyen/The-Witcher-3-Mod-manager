from __future__ import annotations

import os
import shutil
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from app.data import slugify
from app.domain import InstalledMod, ModStatus
from app.install.errors import EmptyPackageError, GamePathError
from app.install.extract import extract_archive
from app.install.package import Bundle, ModPackage
from app.install.progress import InstallPhase, InstallProgress, ProgressCallback
from app.install.scanner import scan_package

# Copy into the vault (a possibly multi-GB archive) in chunks this big, so the
# copy can report byte progress instead of blocking in one opaque call.
_VAULT_CHUNK = 4 * 1024 * 1024

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
    nexus_metadata: dict | None = None,
    name_override: str | None = None,
    progress: ProgressCallback | None = None,
) -> InstallResult:
    """Copy *package*'s bundles into the game and record an :class:`InstalledMod`.

    ``nexus_metadata`` is the parsed Nexus file/mod JSON as it stood at install
    time; it is cached verbatim on the manifest record and used to enrich the
    mod's description, version, and archive size.

    ``name_override`` lets the caller (typically the review dialog) pin a
    user-chosen display name; when set it wins over the Nexus/guessed name.

    ``progress``, when given, receives :class:`InstallProgress` updates as the
    bundles are copied and the archive is vaulted, for a UI progress bar.

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

    installed_paths = _deploy_bundles(package.bundles, game, progress)
    vaulted = _vault_archive(package.archive_path, vault_path, progress)

    mod = _record(
        package, vaulted, installed_on or date.today(), nexus_metadata, name_override
    )
    return InstallResult(mod=mod, installed_paths=installed_paths, vaulted_archive=vaulted)


@contextmanager
def prepare_archive(
    archive_path: Path | str, *, progress: ProgressCallback | None = None
) -> Iterator[ModPackage]:
    """Extract and scan *archive_path*, yielding a :class:`ModPackage` to inspect.

    The archive is extracted into a temporary directory that stays alive for the
    duration of the ``with`` block, so the caller can preview the package *and*
    hand it to :func:`install_package` before the tree is removed. On leaving the
    block the temporary directory is always deleted.

    This is the two-step counterpart to :func:`install_archive`: it stops just
    short of touching the game, which is what the pre-install review dialog needs.
    """
    tmp = tempfile.mkdtemp(prefix="w3mm-extract-")
    try:
        root = extract_archive(Path(archive_path), Path(tmp), progress=progress)
        yield scan_package(root, archive_path)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def install_archive(
    archive_path: Path | str,
    game_path: Path | str,
    vault_path: Path | str | None = None,
    *,
    installed_on: date | None = None,
    nexus_metadata: dict | None = None,
    progress: ProgressCallback | None = None,
) -> InstallResult:
    """Extract, scan, and install *archive_path* in one step.

    Extraction happens in a temporary directory that is removed once the bundles
    have been copied into the game. ``progress`` is forwarded to both extraction
    and installation.
    """
    with prepare_archive(archive_path, progress=progress) as package:
        return install_package(
            package,
            game_path,
            vault_path,
            installed_on=installed_on,
            nexus_metadata=nexus_metadata,
            progress=progress,
        )


def _deploy_bundles(
    bundles: list[Bundle], game: Path, progress: ProgressCallback | None
) -> list[Path]:
    """Copy every bundle into the game tree, reporting byte progress if asked.

    With no callback this is a plain ``copytree`` per bundle (the original fast
    path). With one, ``copytree``'s per-file copy hook is used to accumulate
    copied bytes across all bundles so a single DEPLOY bar spans the whole set."""
    if progress is None:
        return [_deploy_bundle(bundle, game) for bundle in bundles]

    total = sum(_tree_size(bundle.source) for bundle in bundles)
    done = 0
    current = ""
    progress(InstallProgress(InstallPhase.DEPLOY, 0, total, ""))

    def copy_file(src, dst):
        nonlocal done
        shutil.copy2(src, dst)
        try:
            done += os.path.getsize(src)
        except OSError:
            pass
        progress(
            InstallProgress(InstallPhase.DEPLOY, done, total, f"{current}/{Path(src).name}")
        )

    installed: list[Path] = []
    for bundle in bundles:
        current = bundle.name
        dest = game / bundle.kind.install_subdir / bundle.name
        shutil.copytree(bundle.source, dest, dirs_exist_ok=True, copy_function=copy_file)
        installed.append(dest)
    return installed


def _deploy_bundle(bundle: Bundle, game: Path) -> Path:
    """Copy one bundle folder into ``<game>/Mods`` or ``<game>/DLC``.

    ``dirs_exist_ok`` lets a reinstall overwrite an existing bundle in place
    rather than failing on the second install.
    """
    dest = game / bundle.kind.install_subdir / bundle.name
    shutil.copytree(bundle.source, dest, dirs_exist_ok=True)
    return dest


def _tree_size(root: Path) -> int:
    total = 0
    for dirpath, _dirnames, filenames in os.walk(root):
        for name in filenames:
            try:
                total += os.path.getsize(os.path.join(dirpath, name))
            except OSError:
                pass
    return total


def _vault_archive(
    archive: Path, vault_path: Path | str | None, progress: ProgressCallback | None = None
) -> Path | None:
    """Copy the source archive into the vault so the mod can be reinstalled."""
    if not vault_path:
        return None
    vault = Path(vault_path)
    vault.mkdir(parents=True, exist_ok=True)
    target = vault / archive.name
    if progress is None:
        shutil.copy2(archive, target)
        return target
    _copy_with_progress(archive, target, progress)
    shutil.copystat(archive, target)
    return target


def _copy_with_progress(src: Path, dst: Path, progress: ProgressCallback) -> None:
    """Copy *src* to *dst* in chunks, reporting VAULT byte progress as it goes."""
    total = src.stat().st_size
    done = 0
    progress(InstallProgress(InstallPhase.VAULT, 0, total, src.name))
    with open(src, "rb") as source, open(dst, "wb") as sink:
        while True:
            chunk = source.read(_VAULT_CHUNK)
            if not chunk:
                break
            sink.write(chunk)
            done += len(chunk)
            progress(InstallProgress(InstallPhase.VAULT, done, total, src.name))


def _record(
    package: ModPackage,
    vaulted: Path | None,
    when: date,
    nexus_metadata: dict | None = None,
    name_override: str | None = None,
) -> InstalledMod:
    override = (name_override or "").strip()
    name = override or package.suggested_name or package.archive_path.stem
    bundle_count = len(package.bundles)
    meta = nexus_metadata or {}
    # Prefer the Nexus summary and version over what we could guess from the
    # archive; fall back to the readme's first line when Nexus is unavailable.
    description = _string(meta.get("short_description")) or (
        package.readme.splitlines()[0] if package.readme else ""
    )
    version = _string(meta.get("version")) or package.suggested_version
    size_bytes = meta.get("file_size_bytes")
    if not isinstance(size_bytes, int) or isinstance(size_bytes, bool):
        size_bytes = None
    return InstalledMod(
        identity=slugify(name),
        name=name,
        description=description,
        version=version,
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
        size_bytes=size_bytes,
        nexus_metadata=nexus_metadata or None,
    )


def _string(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    value = value.strip()
    return value or None
