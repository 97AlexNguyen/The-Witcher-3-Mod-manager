from app.install.errors import (
    ArchiveError,
    EmptyPackageError,
    GamePathError,
    InstallError,
    RarToolMissingError,
    UninstallError,
    UnsupportedArchiveError,
)
from app.install.extract import SUPPORTED_SUFFIXES, extract_archive
from app.install.inspect import ArchivePreview, inspect_archive
from app.install.installer import (
    InstallResult,
    install_archive,
    install_package,
    prepare_archive,
)
from app.install.package import Bundle, BundleKind, ModPackage
from app.install.progress import InstallPhase, InstallProgress, ProgressCallback
from app.install.scanner import parse_archive_name, scan_package
from app.install.uninstaller import UninstallResult, uninstall_mod

__all__ = [
    "ArchiveError",
    "ArchivePreview",
    "Bundle",
    "BundleKind",
    "EmptyPackageError",
    "GamePathError",
    "InstallError",
    "InstallPhase",
    "InstallProgress",
    "InstallResult",
    "ModPackage",
    "ProgressCallback",
    "RarToolMissingError",
    "SUPPORTED_SUFFIXES",
    "UnsupportedArchiveError",
    "UninstallError",
    "UninstallResult",
    "extract_archive",
    "inspect_archive",
    "install_archive",
    "install_package",
    "prepare_archive",
    "parse_archive_name",
    "scan_package",
    "uninstall_mod",
]
