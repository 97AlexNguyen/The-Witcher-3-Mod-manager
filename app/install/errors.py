from __future__ import annotations

# Failures that can happen while turning a downloaded archive into an installed,
# manifest-tracked mod. They are deliberately fine-grained so the UI can show a
# specific, actionable message (e.g. "install 7-Zip") instead of a generic error.


class InstallError(Exception):
    """Base class for every failure in the install flow."""


class ArchiveError(InstallError):
    """The archive could not be read or extracted."""


class UnsupportedArchiveError(ArchiveError):
    """The file is not one of the supported archive formats (.zip/.7z/.rar)."""


class RarToolMissingError(ArchiveError):
    """A .rar archive was given but no external unrar/7-Zip/WinRAR is available.

    RAR's compression is proprietary and has no pure-Python implementation, so
    ``rarfile`` shells out to an external binary. When it is missing we surface a
    clear instruction rather than silently failing — see CLAUDE.md.
    """


class EmptyPackageError(InstallError):
    """The archive contained no ``Mods/`` or ``DLC/`` bundles to install."""


class GamePathError(InstallError):
    """The configured game path is missing or does not look like an install."""


class UninstallError(InstallError):
    """One or more tracked content folders could not be removed.

    ``removed_paths`` lets callers explain that the uninstall was partial while
    keeping the manifest record available for a safe retry.
    """

    def __init__(
        self,
        message: str,
        *,
        removed_paths: tuple[str, ...] = (),
        failed_paths: tuple[str, ...] = (),
    ) -> None:
        super().__init__(message)
        self.removed_paths = removed_paths
        self.failed_paths = failed_paths
