from __future__ import annotations

import zipfile
from pathlib import Path

from app.install.errors import (
    ArchiveError,
    RarToolMissingError,
    UnsupportedArchiveError,
)
from app.install.progress import InstallPhase, InstallProgress, ProgressCallback

# Archive extraction. Formats and their backing libraries follow CLAUDE.md:
#   .zip -> stdlib zipfile
#   .7z  -> py7zr (pure Python)
#   .rar -> rarfile, which shells out to an external unrar/7-Zip/WinRAR binary.
#
# We extract the whole archive to a caller-owned directory and hand it back; the
# scanner then inspects the tree. Nothing here decides what is a mod — that is
# the scanner's job.
#
# When a ``progress`` callback is given, extraction is driven member-by-member so
# byte-level progress can be reported; with no callback the fast library-native
# ``extractall`` is used and behaviour is exactly as before.

SUPPORTED_SUFFIXES = (".zip", ".7z", ".rar")


def extract_archive(
    archive_path: Path | str,
    dest_dir: Path | str,
    *,
    progress: ProgressCallback | None = None,
) -> Path:
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
        _extract_zip(archive, dest, progress)
    elif suffix == ".7z":
        _extract_7z(archive, dest, progress)
    elif suffix == ".rar":
        _extract_rar(archive, dest, progress)
    else:
        raise UnsupportedArchiveError(
            f"Unsupported archive type '{archive.suffix}'. "
            "Supported formats are .zip, .7z, and .rar."
        )
    return dest


def _emit(progress: ProgressCallback | None, done: int, total: int, detail: str) -> None:
    if progress is not None:
        progress(InstallProgress(InstallPhase.EXTRACT, done, total, detail))


def _extract_zip(archive: Path, dest: Path, progress: ProgressCallback | None) -> None:
    try:
        with zipfile.ZipFile(archive) as zf:
            if progress is None:
                zf.extractall(dest)
                return
            members = zf.infolist()
            total = sum(member.file_size for member in members)
            done = 0
            _emit(progress, 0, total, "")
            for member in members:
                zf.extract(member, dest)
                done += member.file_size
                _emit(progress, done, total, member.filename)
    except (zipfile.BadZipFile, OSError) as exc:
        raise ArchiveError(f"Could not read the zip archive: {exc}") from exc


def _extract_7z(archive: Path, dest: Path, progress: ProgressCallback | None) -> None:
    import py7zr

    try:
        if progress is None:
            with py7zr.SevenZipFile(archive, mode="r") as zf:
                zf.extractall(path=dest)
            return
        with py7zr.SevenZipFile(archive, mode="r") as zf:
            entries = [entry for entry in zf.list() if not entry.is_directory]
        sizes = {entry.filename: entry.uncompressed for entry in entries}
        total = sum(sizes.values())
        callback = _make_7z_callback(sizes, total, progress)
        with py7zr.SevenZipFile(archive, mode="r") as zf:
            zf.extractall(path=dest, callback=callback)
        # Guarantee the bar reaches 100% even if any per-file name didn't match.
        _emit(progress, total, total, "")
    except (py7zr.exceptions.ArchiveError, OSError) as exc:
        raise ArchiveError(f"Could not read the 7z archive: {exc}") from exc


def _make_7z_callback(sizes: dict[str, int], total: int, progress: ProgressCallback):
    """Build a py7zr ExtractCallback that reports cumulative *uncompressed* bytes.

    The byte counts py7zr passes to ``report_start`` are compressed sizes, so
    instead we look each finished file up in *sizes* (uncompressed, from the
    archive listing) and accumulate that. Defined here, not at module scope, so
    py7zr stays a lazy import."""
    from py7zr.callbacks import ExtractCallback

    class _Progress(ExtractCallback):
        def __init__(self) -> None:
            self._done = 0

        def report_start_preparation(self) -> None:
            _emit(progress, 0, total, "")

        def report_start(self, processing_file_path: str, processing_bytes) -> None:
            pass

        def report_update(self, decompressed_bytes) -> None:
            pass

        def report_end(self, processing_file_path: str, wrote_bytes) -> None:
            self._done += sizes.get(processing_file_path, 0)
            _emit(progress, self._done, total, processing_file_path)

        def report_postprocess(self) -> None:
            pass

        def report_warning(self, message: str) -> None:
            pass

    return _Progress()


def _extract_rar(archive: Path, dest: Path, progress: ProgressCallback | None) -> None:
    import rarfile

    try:
        # rarfile drives an external tool for one bulk extractall and offers no
        # per-file feedback, so progress here is reported as indeterminate
        # (total 0) — a busy indicator rather than a stuck percentage.
        _emit(progress, 0, 0, archive.name)
        with rarfile.RarFile(archive) as rf:
            rf.extractall(dest)
        _emit(progress, 0, 0, "")
    except rarfile.RarCannotExec as exc:
        # The library is present but the external unrar/7-Zip/WinRAR is not.
        raise RarToolMissingError(
            "Extracting .rar archives needs 7-Zip or WinRAR installed. "
            "Please install one of them and try again."
        ) from exc
    except (rarfile.Error, OSError) as exc:
        raise ArchiveError(f"Could not read the rar archive: {exc}") from exc
