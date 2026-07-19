"""Download and cache the mod thumbnail referenced by Nexus metadata.

The Nexus mod JSON carries a ``picture_url`` (surfaced as ``thumbnail_url`` on
:class:`~app.apis.nexus_metadata.NexusArchiveMetadata`). That URL points at a
Nexus CDN image which can change or disappear when the mod page is updated, so
this module fetches it once at install time and stores a local copy the app can
use as the card/preview image without re-hitting the network.

The cache lives beside the manifest in the app data directory. A failed or
missing download is never fatal: callers get ``None`` and fall back to the
generated placeholder cover.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import requests

from app.config.nexus_api import DEFAULT_TIMEOUT, _APP_HEADERS
from app.config.store import app_data_dir

THUMBNAIL_DIR_NAME = "thumbnails"
# Extensions Nexus serves cover images as; anything else falls back to ``.img``.
_KNOWN_SUFFIXES = (".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp")
_MAX_BYTES = 12 * 1024 * 1024  # cover art is small; guard against a runaway body


def thumbnail_cache_dir() -> Path:
    return app_data_dir() / THUMBNAIL_DIR_NAME


def cache_thumbnail(
    metadata: dict | None,
    *,
    timeout: float = DEFAULT_TIMEOUT,
) -> str | None:
    """Download the thumbnail named in *metadata* and return its cached path.

    Returns ``None`` — never raises — when there is no URL, the download fails,
    or the response is not usable. The filename is derived from the Nexus mod id
    (or the URL) so a reinstall of the same mod reuses the existing file.
    """
    url = _thumbnail_url(metadata)
    if not url:
        return None

    target = _cache_path(metadata, url)
    if target.is_file() and target.stat().st_size > 0:
        return str(target)

    try:
        response = requests.get(
            url,
            headers={"Accept": "image/*", **_APP_HEADERS},
            timeout=timeout,
            stream=True,
        )
        response.raise_for_status()
        body = _read_capped(response)
    except (requests.RequestException, OSError):
        return None
    if not body:
        return None

    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        tmp = target.with_suffix(target.suffix + ".part")
        tmp.write_bytes(body)
        tmp.replace(target)
    except OSError:
        return None
    return str(target)


def _thumbnail_url(metadata: dict | None) -> str | None:
    if not isinstance(metadata, dict):
        return None
    url = metadata.get("thumbnail_url")
    if isinstance(url, str) and url.strip().lower().startswith(("http://", "https://")):
        return url.strip()
    return None


def _cache_path(metadata: dict, url: str) -> Path:
    mod_id = metadata.get("nexus_mod_id")
    if isinstance(mod_id, int) and not isinstance(mod_id, bool):
        stem = f"mod_{mod_id}"
    else:
        stem = hashlib.sha1(url.encode("utf-8")).hexdigest()[:16]
    return thumbnail_cache_dir() / f"{stem}{_suffix_for(url)}"


def _suffix_for(url: str) -> str:
    suffix = Path(url.split("?", 1)[0].split("#", 1)[0]).suffix.lower()
    return suffix if suffix in _KNOWN_SUFFIXES else ".img"


def _read_capped(response: requests.Response) -> bytes | None:
    chunks: list[bytes] = []
    total = 0
    for chunk in response.iter_content(chunk_size=64 * 1024):
        if not chunk:
            continue
        total += len(chunk)
        if total > _MAX_BYTES:
            return None
        chunks.append(chunk)
    return b"".join(chunks)
