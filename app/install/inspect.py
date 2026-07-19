"""Cheap, read-only inspection of an archive — *without* extracting it to disk.

The pre-install review dialog needs to show what an archive would install (its
Mods/DLC folders) and its readme *before* the user commits. Fully extracting the
archive just to preview it — and then throwing that away if the user cancels — is
wasteful for a large mod. Instead this module reads the archive's entry listing
(a header read, not a decompression) to reconstruct the folder layout, and pulls
out only the small readme member.

Actual extraction still happens once, later, when the user confirms — see
:func:`app.install.installer.prepare_archive`. The bundle-detection rules are
shared with the disk scanner (:func:`app.install.scanner.classify_dirs`), so the
preview and the real install can never disagree about what gets installed.
"""

from __future__ import annotations

import tempfile
import zipfile
from dataclasses import dataclass, field
from pathlib import Path

from app.install.errors import (
    ArchiveError,
    RarToolMissingError,
    UnsupportedArchiveError,
)
from app.install.package import BundleKind
from app.install.scanner import (
    README_MAX_CHARS,
    classify_dirs,
    dir_paths_from_names,
    readme_entry_name,
)


@dataclass(slots=True)
class ArchivePreview:
    """What an archive *would* install, derived from its listing alone."""

    mod_names: list[str] = field(default_factory=list)
    dlc_names: list[str] = field(default_factory=list)
    readme: str = ""

    @property
    def is_empty(self) -> bool:
        return not self.mod_names and not self.dlc_names


def inspect_archive(archive_path: Path | str) -> ArchivePreview:
    """Describe *archive_path* without extracting its contents to disk.

    Raises the same errors as extraction for a corrupt, unreadable, or
    unsupported archive (:class:`ArchiveError`, :class:`UnsupportedArchiveError`,
    :class:`RarToolMissingError`) so a broken archive is caught at preview time
    rather than after the user clicks install.
    """
    archive = Path(archive_path)
    names = _list_names(archive)
    bundles = classify_dirs(dir_paths_from_names(names))
    preview = ArchivePreview(
        mod_names=[name for kind, name, _ in bundles if kind is BundleKind.MOD],
        dlc_names=[name for kind, name, _ in bundles if kind is BundleKind.DLC],
    )
    preview.readme = _read_readme(archive, names)
    return preview


def _list_names(archive: Path) -> list[str]:
    suffix = archive.suffix.lower()
    if suffix == ".zip":
        return _zip_names(archive)
    if suffix == ".7z":
        return _sevenzip_names(archive)
    if suffix == ".rar":
        return _rar_names(archive)
    raise UnsupportedArchiveError(
        f"Unsupported archive type '{archive.suffix}'. "
        "Supported formats are .zip, .7z, and .rar."
    )


def _zip_names(archive: Path) -> list[str]:
    try:
        with zipfile.ZipFile(archive) as zf:
            return zf.namelist()
    except (zipfile.BadZipFile, OSError) as exc:
        raise ArchiveError(f"Could not read the zip archive: {exc}") from exc


def _sevenzip_names(archive: Path) -> list[str]:
    import py7zr

    try:
        with py7zr.SevenZipFile(archive, mode="r") as zf:
            return list(zf.getnames())
    except (py7zr.exceptions.ArchiveError, OSError) as exc:
        raise ArchiveError(f"Could not read the 7z archive: {exc}") from exc


def _rar_names(archive: Path) -> list[str]:
    import rarfile

    # Listing reads RAR headers, which rarfile parses itself — it does not need
    # the external unrar tool (that is only required to decompress file data).
    try:
        with rarfile.RarFile(archive) as rf:
            return rf.namelist()
    except rarfile.RarCannotExec as exc:
        raise RarToolMissingError(
            "Extracting .rar archives needs 7-Zip or WinRAR installed. "
            "Please install one of them and try again."
        ) from exc
    except (rarfile.Error, OSError) as exc:
        raise ArchiveError(f"Could not read the rar archive: {exc}") from exc


def _read_readme(archive: Path, names: list[str]) -> str:
    """Read just the readme member, best-effort. Any failure (including a .rar
    that needs a tool the user hasn't installed) yields an empty readme rather
    than blocking the preview — the real install still surfaces such errors."""
    entry = readme_entry_name(names)
    if entry is None:
        return ""
    try:
        data = _read_member(archive, entry)
    except Exception:
        return ""
    if data is None:
        return ""
    return data.decode("utf-8", errors="replace").strip()[:README_MAX_CHARS]


def _read_member(archive: Path, entry: str) -> bytes | None:
    suffix = archive.suffix.lower()
    if suffix == ".zip":
        with zipfile.ZipFile(archive) as zf:
            return zf.read(entry)
    if suffix == ".rar":
        import rarfile

        with rarfile.RarFile(archive) as rf:
            return rf.read(entry)
    if suffix == ".7z":
        import py7zr

        # py7zr has no single-member in-memory read, so extract just this one
        # small file to a scratch dir and read it back.
        with tempfile.TemporaryDirectory(prefix="w3mm-readme-") as tmp:
            with py7zr.SevenZipFile(archive, mode="r") as zf:
                zf.extract(path=tmp, targets=[entry])
            member = Path(tmp) / entry.replace("\\", "/")
            return member.read_bytes() if member.is_file() else None
    return None
