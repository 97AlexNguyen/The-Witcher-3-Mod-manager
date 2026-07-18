from __future__ import annotations

import zipfile
from pathlib import Path

from app.install.errors import (
    ArchiveError,
    RarToolMissingError,
    UnsupportedArchiveError,
)

# Archive extraction. Formats and their backing libraries follow CLAUDE.md:
#   .zip -> stdlib zipfile
#   .7z  -> py7zr (pure Python)
#   .rar -> rarfile, which shells out to an external unrar/7-Zip/WinRAR binary.
#
# We extract the whole archive to a caller-owned directory and hand it back; the
# scanner then inspects the tree. Nothing here decides what is a mod — that is
# the scanner's job.

SUPPORTED_SUFFIXES = (".zip", ".7z", ".rar")


def extract_archive(archive_path: Path | str, dest_dir: Path | str) -> Path:
    """Extract *archive_path* into *dest_dir* and return *dest_dir*.

    Raises :class:`UnsupportedArchiveError` for unknown extensions,
    :class:`RarToolMissingError` when a .rar needs an external tool that is not
    installed, and :class:`ArchiveError` for corrupt or unreadable archives.
    """
    archive = Path(archive_path)
    dest = Path(dest_dir)
    dest.mkdir(parents=True, exist_ok=True)

    suffix = archive.suffix.lower()
    if suffix == ".zip":
        _extract_zip(archive, dest)
    elif suffix == ".7z":
        _extract_7z(archive, dest)
    elif suffix == ".rar":
        _extract_rar(archive, dest)
    else:
        raise UnsupportedArchiveError(
            f"Unsupported archive type '{archive.suffix}'. "
            "Supported formats are .zip, .7z, and .rar."
        )
    return dest


def _extract_zip(archive: Path, dest: Path) -> None:
    try:
        with zipfile.ZipFile(archive) as zf:
            zf.extractall(dest)
    except (zipfile.BadZipFile, OSError) as exc:
        raise ArchiveError(f"Could not read the zip archive: {exc}") from exc


def _extract_7z(archive: Path, dest: Path) -> None:
    import py7zr

    try:
        with py7zr.SevenZipFile(archive, mode="r") as zf:
            zf.extractall(path=dest)
    except (py7zr.exceptions.ArchiveError, OSError) as exc:
        raise ArchiveError(f"Could not read the 7z archive: {exc}") from exc


def _extract_rar(archive: Path, dest: Path) -> None:
    import rarfile

    try:
        with rarfile.RarFile(archive) as rf:
            rf.extractall(dest)
    except (rarfile.RarCannotExec, rarfile.RarExecError) as exc:
        # The library is present but the external unrar/7-Zip/WinRAR is not.
        raise RarToolMissingError(
            "Extracting .rar archives needs 7-Zip or WinRAR installed. "
            "Please install one of them and try again."
        ) from exc
    except (rarfile.Error, OSError) as exc:
        raise ArchiveError(f"Could not read the rar archive: {exc}") from exc
