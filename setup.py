'''Witcher 3 Mod Manager cx_Freeze setup script'''
# pylint: disable=wildcard-import,unused-wildcard-import

from cx_Freeze import Executable, setup

from src.globals.constants import *

# UPDATED: Include all necessary folders and files
FILES = [
    "res/",           # Resources (icons, etc.)
    "translations/",  # Language files
    "tools/",         # 7zip tools
    "mapping/",       # ✅ Category mapping files - NEEDED for categories
    "api/",           # ✅ API scripts and config - NEEDED for Nexus integration
    "logs/",          # ✅ Log directory (may be empty but structure needed)
    ("res/qt.conf", "qt.conf"),  # Qt configuration
    "LICENSE"
]

SHORTCUT_TABLE = [
    (
        "DesktopShortcut",        # Shortcut
        "DesktopFolder",          # Directory_
        TITLE,                    # Name
        "TARGETDIR",              # Component_
        "[TARGETDIR]TheWitcher3ModManager.exe",   # Target
        None,                     # Arguments
        None,                     # Description
        None,                     # Hotkey
        None,                     # Icon
        None,                     # IconIndex
        None,                     # ShowCmd
        'TARGETDIR'               # WkDir
    ),
]

MSI_DATA = {"Shortcut": SHORTCUT_TABLE}
BDIST_MSI_OPTIONS = {'data': MSI_DATA}

setup(
    name=TITLE,
    version=VERSION,
    url=URL_WEB,  # Fixed: should be URL_WEB not URL_GIT_CLONE
    license='Open-source',
    options={
        "build_exe": {
            "include_files": FILES,
            "excludes": ["distutils", "patool"],
            "optimize": 2,
            "zip_include_packages": ["src"],
            "include_msvcr": True
        },
        "bdist_msi": BDIST_MSI_OPTIONS
    },
    author=AUTHORS[1],
    author_email=AUTHORS_MAIL[1],
    description=TITLE,
    executables=[Executable(
        "main.py",
        target_name="TheWitcher3ModManager.exe",
        icon='res/w3a.ico',
        base="Win32GUI"
    )]
)