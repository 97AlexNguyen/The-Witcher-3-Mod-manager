#!/usr/bin/env python
"""
category_mapper.py
------------------
Utility module that fetches the category list for a given Nexus Mods game,
caches it to *mapping/category_mapping.yaml*, and refreshes at most once per
24 hours.

Key features
============
* Finds API key in environment variable **NEXUS_API_KEY** or fallback file
  *api/api_key.txt* (same folder as this module).
* Writes YAML in the format:

    Category_Mapping:
      "1": "Animations"
      "2": "Armour"
      ...

* Automatically creates the *mapping/* directory if missing.
* Public call‑site: ``get_category_map(game_domain="witcher3")`` returns a
  ``dict[int,str]`` ready for lookup.
* CLI mode: ``python category_mapper.py --game skyrimspecialedition`` dumps the
  map to stdout.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import os
import pathlib
import typing as _t

try:
    import yaml  # type: ignore
except ImportError as _e:  # pragma: no cover – emit clear hint
    raise RuntimeError(
        "PyYAML is required: pip install pyyaml"
    ) from _e

import requests

# ---------------------------------------------------------------------------
# Constants & paths
# ---------------------------------------------------------------------------
DEFAULT_GAME = "witcher3"
CACHE_EXPIRY = _dt.timedelta(days=1)

# <root>/mapping/category_mapping.yaml
ROOT_DIR = pathlib.Path(__file__).resolve().parents[1]
MAPPING_DIR = ROOT_DIR / "mapping"
YAML_PATH = MAPPING_DIR / "category_mapping.yaml"

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _get_api_key() -> str:
    """Return Nexus Mods API key from env or *api/api_key.txt*.

    Raises
    ------
    RuntimeError
        If key cannot be found.
    """
    key = os.getenv("NEXUS_API_KEY")
    if key:
        return key.strip()

    key_file = pathlib.Path(__file__).parent / "api_key.txt"
    if key_file.exists():
        return key_file.read_text(encoding="utf-8").strip()

    raise RuntimeError(
        "Nexus Mods API key not found. Set NEXUS_API_KEY or create api/api_key.txt"
    )


def _fetch_remote_categories(game: str) -> dict[int, str]:
    """Fetch fresh category map from Nexus Mods API."""
    url = f"https://api.nexusmods.com/v1/games/{game}.json"
    headers = {"apikey": _get_api_key(), "Accept": "application/json"}
    resp = requests.get(url, headers=headers, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    return {c["category_id"]: c["name"] for c in data["categories"]}


def _load_cached_map() -> dict[int, str] | None:
    """Return cached map if file is fresh (< CACHE_EXPIRY)."""
    if YAML_PATH.exists():
        mtime = _dt.datetime.fromtimestamp(YAML_PATH.stat().st_mtime)
        if _dt.datetime.now() - mtime < CACHE_EXPIRY:
            doc = yaml.safe_load(YAML_PATH.read_text(encoding="utf-8")) or {}
            return {int(k): v for k, v in doc.get("Category_Mapping", {}).items()}
    return None


def _save_map(mapping: dict[int, str]) -> None:
    """Serialize mapping to YAML file (creates *mapping* dir if needed)."""
    MAPPING_DIR.mkdir(exist_ok=True)
    data = {"Category_Mapping": {str(k): v for k, v in mapping.items()}}
    YAML_PATH.write_text(yaml.dump(data, allow_unicode=True, sort_keys=True), encoding="utf-8")


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_category_map(game: str = DEFAULT_GAME) -> dict[int, str]:
    """Return category map, refreshing cache if stale."""
    cached = _load_cached_map()
    if cached:
        return cached

    fresh = _fetch_remote_categories(game)
    _save_map(fresh)
    return fresh


# ---------------------------------------------------------------------------
# CLI helper
# ---------------------------------------------------------------------------

def _cli():
    parser = argparse.ArgumentParser(description="Fetch Nexus Mods category mapping")
    parser.add_argument("--game", default=DEFAULT_GAME, help="Nexus domain name (e.g. witcher3)")
    args = parser.parse_args()

    mapping = get_category_map(args.game)
    import pprint

    pprint.pp(mapping)


if __name__ == "__main__":  # pragma: no cover
    _cli()
