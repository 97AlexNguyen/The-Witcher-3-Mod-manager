from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Callable

import fasteners

from app.config.store import app_data_dir
from app.domain import Category, InstalledMod, ModStatus

# The *manifest*: this app's own record of which mods are installed, their
# category, priority, and what each one wrote where. See CLAUDE.md terminology.
#
# It is ours alone — machine-written and machine-read, never hand-edited, and
# never the game's *game config*. JSON by choice (UTF-8 by spec, no type
# coercion), living beside config.json in %LOCALAPPDATA%.
#
# This format is brand new to this rewrite; there is deliberately no import of
# any legacy installed.xml. The schema carries a top-level ``version`` so future
# changes can migrate rather than guess.

MANIFEST_FILE_NAME = "manifest.json"
MANIFEST_LOCK_NAME = "manifest.lock"
MANIFEST_VERSION = 1


def manifest_path() -> Path:
    return app_data_dir() / MANIFEST_FILE_NAME


def manifest_lock_path(target: Path | None = None) -> Path:
    base = target or manifest_path()
    return base.parent / MANIFEST_LOCK_NAME


@dataclass(slots=True)
class Manifest:
    """In-memory form of the manifest file: installed mods plus the category
    definitions they are filed under."""

    mods: list[InstalledMod] = field(default_factory=list)
    categories: list[Category] = field(default_factory=list)
    version: int = MANIFEST_VERSION

    def to_dict(self) -> dict:
        return {
            "version": self.version,
            "categories": [_category_to_dict(c) for c in self.categories],
            "mods": [_mod_to_dict(m) for m in self.mods],
        }

    @classmethod
    def from_dict(cls, raw: dict) -> "Manifest":
        categories = [
            c
            for c in (_category_from_dict(e) for e in _as_list(raw.get("categories")))
            if c is not None
        ]
        mods = [
            m
            for m in (_mod_from_dict(e) for e in _as_list(raw.get("mods")))
            if m is not None
        ]
        return cls(
            mods=mods,
            categories=categories,
            version=_as_int(raw.get("version"), MANIFEST_VERSION),
        )


# -- serialization ------------------------------------------------------- #


def _category_to_dict(category: Category) -> dict:
    return {
        "key": category.key,
        "name": category.name,
        "color_key": category.color_key,
        "built_in": category.built_in,
    }


def _category_from_dict(raw) -> Category | None:
    if not isinstance(raw, dict):
        return None
    key = raw.get("key")
    if not isinstance(key, str) or not key:
        return None
    return Category(
        key=key,
        name=raw.get("name") if isinstance(raw.get("name"), str) else key,
        color_key=raw.get("color_key") if isinstance(raw.get("color_key"), str) else "neutral",
        built_in=bool(raw.get("built_in", False)),
    )


def _mod_to_dict(mod: InstalledMod) -> dict:
    return {
        "identity": mod.identity,
        "name": mod.name,
        "description": mod.description,
        "version": mod.version,
        "priority": mod.priority,
        "enabled": mod.enabled,
        "category": mod.category_key,
        "installed_on": mod.installed_on.isoformat(),
        "content": _groups_to_dict(mod.content),
        "settings": _groups_to_dict(mod.settings),
        "keys": _groups_to_dict(mod.keys),
        "readme": mod.readme,
        "status": mod.status.name,
        "status_detail": mod.status_detail,
        "vault": mod.vault_path,
        "thumbnail": mod.thumbnail_path,
    }


def _mod_from_dict(raw) -> InstalledMod | None:
    if not isinstance(raw, dict):
        return None
    identity = raw.get("identity")
    name = raw.get("name")
    if not isinstance(identity, str) or not identity:
        return None
    if not isinstance(name, str) or not name:
        return None
    return InstalledMod(
        identity=identity,
        name=name,
        description=raw.get("description") if isinstance(raw.get("description"), str) else "",
        version=raw.get("version") if isinstance(raw.get("version"), str) else None,
        priority=_as_opt_int(raw.get("priority")),
        enabled=bool(raw.get("enabled", False)),
        category_key=raw.get("category") if isinstance(raw.get("category"), str) else "uncategorized",
        installed_on=_parse_date(raw.get("installed_on")),
        content=_groups_from_dict(raw.get("content")),
        settings=_groups_from_dict(raw.get("settings")),
        keys=_groups_from_dict(raw.get("keys")),
        readme=raw.get("readme") if isinstance(raw.get("readme"), str) else "",
        status=_parse_status(raw.get("status")),
        status_detail=raw.get("status_detail") if isinstance(raw.get("status_detail"), str) else "",
        vault_path=raw.get("vault") if isinstance(raw.get("vault"), str) else None,
        thumbnail_path=raw.get("thumbnail") if isinstance(raw.get("thumbnail"), str) else None,
    )


def _groups_to_dict(groups: dict[str, tuple[str, ...]]) -> dict[str, list[str]]:
    return {str(k): list(v) for k, v in groups.items()}


def _groups_from_dict(raw) -> dict[str, tuple[str, ...]]:
    if not isinstance(raw, dict):
        return {}
    result: dict[str, tuple[str, ...]] = {}
    for key, value in raw.items():
        if not isinstance(key, str) or not isinstance(value, list):
            continue
        result[key] = tuple(str(item) for item in value)
    return result


def _parse_status(raw) -> ModStatus:
    if isinstance(raw, str):
        try:
            return ModStatus[raw]
        except KeyError:
            pass
    return ModStatus.OK


def _parse_date(raw) -> date:
    if isinstance(raw, str):
        try:
            return date.fromisoformat(raw)
        except ValueError:
            pass
    return date.min


def _as_list(raw) -> list:
    return raw if isinstance(raw, list) else []


def _as_int(raw, default: int) -> int:
    try:
        return int(raw)
    except (TypeError, ValueError):
        return default


def _as_opt_int(raw) -> int | None:
    if raw is None or isinstance(raw, bool):
        return None if raw is None else int(raw)
    try:
        return int(raw)
    except (TypeError, ValueError):
        return None


# -- load / save --------------------------------------------------------- #


def load_manifest(path: Path | None = None) -> Manifest:
    """Load the manifest, returning an empty one if it is missing or unreadable.

    A corrupt or partially written manifest must never take the app down. The
    atomic write below guarantees a reader sees either the previous file or the
    new one intact, so falling back to empty only happens on real corruption.
    """
    target = path or manifest_path()
    try:
        raw = json.loads(target.read_text("utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError, UnicodeDecodeError):
        return Manifest()
    if not isinstance(raw, dict):
        return Manifest()
    return Manifest.from_dict(raw)


def save_manifest(manifest: Manifest, path: Path | None = None) -> None:
    """Persist atomically: write ``.new``, rotate old to ``.old``, then rename.

    Mirrors config.json's contract: a power cut mid-write must leave either the
    previous manifest or the new one intact, never a truncated file.
    """
    target = path or manifest_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    new_path = target.with_suffix(target.suffix + ".new")
    old_path = target.with_suffix(target.suffix + ".old")

    payload = json.dumps(manifest.to_dict(), indent=2, ensure_ascii=False)
    new_path.write_text(payload, "utf-8")

    if target.exists():
        old_path.unlink(missing_ok=True)
        os.replace(target, old_path)
    os.replace(new_path, target)


class ManifestStore:
    """Owns the manifest file and the inter-process lock guarding writes.

    Two app instances must not write the manifest concurrently. Reading is
    always safe (atomic writes mean a reader never sees a torn file), so
    :meth:`load` works with or without the lock; :meth:`save` requires it.
    """

    def __init__(self, path: Path | None = None, *, ignore_lock: bool = False) -> None:
        self._path = path or manifest_path()
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = None if ignore_lock else fasteners.InterProcessLock(str(manifest_lock_path(self._path)))
        self._locked = ignore_lock

    @property
    def path(self) -> Path:
        return self._path

    @property
    def can_write(self) -> bool:
        return self._locked

    def acquire(self) -> bool:
        """Try to take the write lock without blocking. Returns whether we hold it."""
        if self._locked:
            return True
        if self._lock is not None:
            if self._lock.acquire(blocking=False):
                self._locked = True
            else:
                # A failed non-blocking acquire still leaves the lock file open;
                # a read-only instance must not keep that OS handle dangling.
                self._close_handle()
        return self._locked

    def release(self) -> None:
        if self._lock is not None and self._locked:
            self._lock.release()
        # ignore_lock stores keep _locked True; never claim to hold what we don't
        self._locked = self._lock is None and self._locked
        self._close_handle()

    def _close_handle(self) -> None:
        """Close fasteners' underlying lock-file descriptor if it is still open,
        so the lock file can be removed on Windows (open handles block unlink)."""
        lock = self._lock
        if lock is not None and getattr(lock, "lockfile", None) is not None:
            try:
                lock._do_close()
            except Exception:
                pass

    def load(self, seed: Callable[[], Manifest] | None = None) -> Manifest:
        """Load the manifest. If no file exists yet and a ``seed`` factory is
        given, build one from it and persist it once (when we hold the lock)."""
        if self._path.exists():
            return load_manifest(self._path)
        if seed is None:
            return Manifest()
        manifest = seed()
        if self.can_write:
            save_manifest(manifest, self._path)
        return manifest

    def save(self, manifest: Manifest) -> bool:
        """Persist the manifest if we hold the write lock. Returns whether it
        was written; callers can surface a read-only notice on ``False``."""
        if not self.can_write:
            return False
        save_manifest(manifest, self._path)
        return True

    def __enter__(self) -> "ManifestStore":
        self.acquire()
        return self

    def __exit__(self, *_exc) -> None:
        self.release()
