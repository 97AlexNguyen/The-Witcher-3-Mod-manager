from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path

# The Witcher 3 ships the game executable under bin. The classic build uses
# bin/x64; the next-gen build adds bin/x64_dx12. Either proves this is a real
# install root rather than an arbitrary folder the user browsed to by mistake.
_GAME_EXE_RELATIVE = (
    Path("bin") / "x64" / "witcher3.exe",
    Path("bin") / "x64_dx12" / "witcher3.exe",
)


class CheckLevel(Enum):
    OK = auto()
    WARNING = auto()
    ERROR = auto()
    UNKNOWN = auto()


@dataclass(frozen=True, slots=True)
class CheckResult:
    level: CheckLevel
    message: str

    @property
    def ok(self) -> bool:
        return self.level is CheckLevel.OK


def validate_game_path(path: str | None) -> CheckResult:
    """Check whether *path* looks like a real Witcher 3 install root."""
    if not path or not path.strip():
        return CheckResult(CheckLevel.UNKNOWN, "No game folder set yet.")
    root = Path(path.strip())
    if not root.is_dir():
        return CheckResult(CheckLevel.ERROR, "Folder does not exist.")
    if any((root / rel).is_file() for rel in _GAME_EXE_RELATIVE):
        return CheckResult(CheckLevel.OK, "Witcher 3 install detected.")
    return CheckResult(
        CheckLevel.WARNING,
        "witcher3.exe not found under bin\\x64 — is this the game root?",
    )


def validate_vault_path(path: str | None) -> CheckResult:
    """Check the mod-archive storage (vault) folder used for reinstall."""
    if not path or not path.strip():
        return CheckResult(CheckLevel.UNKNOWN, "No storage folder set yet.")
    root = Path(path.strip())
    if not root.is_dir():
        return CheckResult(
            CheckLevel.WARNING, "Folder does not exist yet — it will be created."
        )
    return CheckResult(CheckLevel.OK, "Storage folder ready.")
