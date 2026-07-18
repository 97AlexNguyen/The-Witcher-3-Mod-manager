from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path

# App preferences layer.
#
# This is neither the *manifest* (the app's record of installed mods) nor the
# game's *game config* (engine-owned xml/ini). It is a third thing: the app's
# own preferences — where the game lives, where mod archives are vaulted, and
# which Nexus account to use. See CLAUDE.md / AGENTS.md terminology.
#
# The Nexus API key is deliberately NOT stored here. Secrets go to the OS
# credential store via app.config.credentials; config.json holds only paths.

APP_DIR_NAME = "The Witcher 3 Mod Manager"
CONFIG_FILE_NAME = "config.json"
CONFIG_VERSION = 1


def app_data_dir() -> Path:
    """Return the app's per-user data directory, creating nothing.

    On Windows this is ``%LOCALAPPDATA%\\The Witcher 3 Mod Manager`` — the same
    directory the manifest lives in, so config sits beside it and backs up with it.
    """
    base = os.environ.get("LOCALAPPDATA")
    root = Path(base) if base else Path.home() / "AppData" / "Local"
    return root / APP_DIR_NAME


def config_path() -> Path:
    return app_data_dir() / CONFIG_FILE_NAME


@dataclass(slots=True)
class AppConfig:
    """User-chosen paths. Machine-written, machine-read; no hand editing expected."""

    game_path: str | None = None
    vault_path: str | None = None
    version: int = CONFIG_VERSION

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, raw: dict) -> "AppConfig":
        # Tolerate unknown / missing keys so a newer file opened by an older
        # build (or vice versa) degrades to defaults instead of crashing.
        return cls(
            game_path=_clean(raw.get("game_path")),
            vault_path=_clean(raw.get("vault_path")),
            version=int(raw.get("version", CONFIG_VERSION) or CONFIG_VERSION),
        )


def _clean(value) -> str | None:
    if not isinstance(value, str):
        return None
    value = value.strip()
    return value or None


def load_config(path: Path | None = None) -> AppConfig:
    """Load config.json, returning defaults if it is missing or unreadable.

    A corrupt or partially written file must never take the app down — the user
    can always re-enter paths, so we fall back to defaults rather than raising.
    """
    target = path or config_path()
    try:
        raw = json.loads(target.read_text("utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError, UnicodeDecodeError):
        return AppConfig()
    if not isinstance(raw, dict):
        return AppConfig()
    return AppConfig.from_dict(raw)


def save_config(config: AppConfig, path: Path | None = None) -> None:
    """Persist config atomically: write ``.new``, rotate old to ``.old``, rename.

    Mirrors the manifest's atomic-write contract: a power cut mid-write must
    leave either the previous config or the new one intact, never a truncated file.
    """
    target = path or config_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    new_path = target.with_suffix(target.suffix + ".new")
    old_path = target.with_suffix(target.suffix + ".old")

    payload = json.dumps(config.to_dict(), indent=2, ensure_ascii=False)
    new_path.write_text(payload, "utf-8")

    if target.exists():
        old_path.unlink(missing_ok=True)
        os.replace(target, old_path)
    os.replace(new_path, target)
