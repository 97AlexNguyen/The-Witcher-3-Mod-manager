"""Nexus metadata lookup for an archive downloaded from nexusmods.com.

An archive filename is an opaque identifier, not a version format to decode.
This module uses its numeric fragments only to locate possible mod pages, then
requires an exact filename match against Nexus's per-file API response before
returning any metadata.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import re

import requests

from app.config.credentials import get_nexus_api_key
from app.config.nexus_api import DEFAULT_TIMEOUT, _APP_HEADERS
from app.data.category_catalog import nexus_category_name

GAME_DOMAIN = "witcher3"
MOD_URL_TEMPLATE = "https://api.nexusmods.com/v1/games/{game}/mods/{mod_id}.json"
FILES_URL_TEMPLATE = "https://api.nexusmods.com/v1/games/{game}/mods/{mod_id}/files.json"
MOD_PAGE_TEMPLATE = "https://www.nexusmods.com/{game}/mods/{mod_id}"
_NUMBER_RE = re.compile(r"(?<!\d)(\d{1,10})(?!\d)")
_ARCHIVE_SUFFIXES = (".zip", ".rar", ".7z")


class NexusLookupError(RuntimeError):
    """Base error for a Nexus archive metadata lookup."""


class NexusApiKeyMissingError(NexusLookupError):
    """Raised when no saved API key is available for a lookup."""


class NexusArchiveNotFoundError(NexusLookupError):
    """Raised when the filename cannot be verified against Nexus API data."""


@dataclass(frozen=True, slots=True)
class NexusArchiveMetadata:
    """Verified Nexus data for one concrete downloadable archive.

    ``mod_id`` identifies a Nexus mod page; ``file_id`` identifies the exact
    archive selected by the user. Store both in the manifest.
    """

    archive_filename: str
    nexus_mod_id: int
    nexus_file_id: int
    mod_name: str
    file_name: str
    version: str | None
    short_description: str
    thumbnail_url: str | None
    contains_adult_content: bool
    category_id: int | None
    category_name: str | None
    file_category: str | None
    is_primary_file: bool
    author: str | None
    mod_page_url: str
    file_uploaded_time: str | None
    file_uploaded_timestamp: int | None
    file_size_kb: int | None
    file_size_bytes: int | None
    content_preview_url: str | None
    virus_scan_url: str | None

    def to_dict(self) -> dict:
        """Return JSON-ready data suitable for a manifest entry."""
        return asdict(self)


def lookup_archive_metadata(
    archive_filename: str | Path,
    *,
    api_key: str | None = None,
    timeout: float = DEFAULT_TIMEOUT,
) -> NexusArchiveMetadata:
    """Return verified metadata for a Nexus-downloaded archive.

    The lookup succeeds only when a returned ``files[].file_name`` matches the
    input filename (case-insensitively). A filename without its archive suffix
    is accepted only when that stem identifies one file uniquely.
    """
    filename = Path(archive_filename).name.strip()
    if not filename:
        raise NexusArchiveNotFoundError("Enter an archive filename.")

    key = (api_key or get_nexus_api_key() or "").strip()
    if not key:
        raise NexusApiKeyMissingError("No Nexus API key is saved.")

    candidate_ids = extract_mod_id_candidates(filename)
    if not candidate_ids:
        raise NexusArchiveNotFoundError(
            f"Could not find a numeric Nexus mod ID candidate in '{filename}'."
        )

    for mod_id in candidate_ids:
        files_response = _get_json(
            FILES_URL_TEMPLATE.format(game=GAME_DOMAIN, mod_id=mod_id),
            api_key=key,
            timeout=timeout,
            allow_not_found=True,
        )
        if files_response is None:
            continue
        matched_file = find_matching_file(filename, files_response.get("files"))
        if matched_file is None:
            continue

        mod_response = _get_json(
            MOD_URL_TEMPLATE.format(game=GAME_DOMAIN, mod_id=mod_id),
            api_key=key,
            timeout=timeout,
        )
        return _build_metadata(filename, mod_id, mod_response, matched_file)

    raise NexusArchiveNotFoundError(
        "Nexus did not return a file whose name matches "
        f"'{filename}'. The archive may have been renamed or removed."
    )


def extract_mod_id_candidates(filename: str | Path) -> tuple[int, ...]:
    """Return possible IDs from the filename, in left-to-right order.

    These are candidates only; :func:`lookup_archive_metadata` verifies one by
    matching the full filename returned by Nexus. This deliberately does not
    interpret any number as a version.
    """
    name = Path(filename).name
    candidates: list[int] = []
    for raw in _NUMBER_RE.findall(name):
        value = int(raw)
        if value > 0 and value not in candidates:
            candidates.append(value)
    return tuple(candidates)


def find_matching_file(archive_filename: str, files: object) -> dict | None:
    """Find an exact API file-name match, allowing a uniquely matched stem."""
    if not isinstance(files, list):
        return None
    wanted = Path(archive_filename).name.casefold()
    records = [entry for entry in files if isinstance(entry, dict)]
    exact = [entry for entry in records if _file_name(entry).casefold() == wanted]
    if len(exact) == 1:
        return exact[0]

    if _has_archive_suffix(wanted):
        return None
    stem_matches = [
        entry for entry in records if _archive_stem(_file_name(entry)).casefold() == wanted
    ]
    return stem_matches[0] if len(stem_matches) == 1 else None


def _get_json(
    url: str,
    *,
    api_key: str,
    timeout: float,
    allow_not_found: bool = False,
) -> dict | None:
    try:
        response = requests.get(
            url,
            headers={"apikey": api_key, "Accept": "application/json", **_APP_HEADERS},
            timeout=timeout,
        )
    except requests.RequestException as error:
        raise NexusLookupError(f"Could not call Nexus API: {error}") from error
    if allow_not_found and response.status_code == 404:
        return None
    try:
        response.raise_for_status()
    except requests.HTTPError as error:
        raise NexusLookupError(f"Nexus returned HTTP {response.status_code}.") from error
    try:
        data = response.json()
    except ValueError as error:
        raise NexusLookupError("Nexus returned a response that was not JSON.") from error
    if not isinstance(data, dict):
        raise NexusLookupError("Nexus returned an unexpected JSON response.")
    return data


def _build_metadata(
    archive_filename: str,
    mod_id: int,
    mod: dict,
    file: dict,
) -> NexusArchiveMetadata:
    category_id = _optional_int(mod.get("category_id"))
    return NexusArchiveMetadata(
        archive_filename=archive_filename,
        nexus_mod_id=mod_id,
        nexus_file_id=_required_int(file.get("file_id"), "file_id"),
        mod_name=_string(mod.get("name")) or f"Nexus mod {mod_id}",
        file_name=_string(file.get("name")) or _file_name(file),
        version=_string(file.get("version")) or _string(file.get("mod_version")),
        short_description=_string(mod.get("summary")) or "",
        thumbnail_url=_string(mod.get("picture_url")),
        contains_adult_content=bool(mod.get("contains_adult_content", False)),
        category_id=category_id,
        category_name=nexus_category_name(category_id),
        file_category=_string(file.get("category_name")),
        is_primary_file=bool(file.get("is_primary", False)),
        author=_string(mod.get("uploaded_by")) or _string(mod.get("author")),
        mod_page_url=MOD_PAGE_TEMPLATE.format(game=GAME_DOMAIN, mod_id=mod_id),
        file_uploaded_time=_string(file.get("uploaded_time")),
        file_uploaded_timestamp=_optional_int(file.get("uploaded_timestamp")),
        file_size_kb=_optional_int(file.get("size_kb")),
        file_size_bytes=_optional_int(file.get("size_in_bytes")),
        content_preview_url=_string(file.get("content_preview_link")),
        virus_scan_url=_string(file.get("external_virus_scan_url")),
    )


def _file_name(file: dict) -> str:
    return _string(file.get("file_name")) or ""


def _archive_stem(filename: str) -> str:
    lowered = filename.casefold()
    for suffix in _ARCHIVE_SUFFIXES:
        if lowered.endswith(suffix):
            return filename[: -len(suffix)]
    return filename


def _has_archive_suffix(filename: str) -> bool:
    return filename.casefold().endswith(_ARCHIVE_SUFFIXES)


def _string(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    value = value.strip()
    return value or None


def _optional_int(value: object) -> int | None:
    return value if isinstance(value, int) and not isinstance(value, bool) else None


def _required_int(value: object, field_name: str) -> int:
    result = _optional_int(value)
    if result is None:
        raise NexusLookupError(f"Nexus file response has no valid {field_name}.")
    return result
