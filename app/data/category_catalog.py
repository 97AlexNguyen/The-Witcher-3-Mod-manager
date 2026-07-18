from __future__ import annotations

import json
import re
from importlib import resources

from app.domain import Category

# Nexus does not ship colors with its taxonomy, so assign one deterministically
# from the app palette. Keying off the stable category_id means a category keeps
# the same accent across launches; users can still override any box's color.
PALETTE = ("blue", "violet", "teal", "amber")

_CATALOG_RESOURCE = "nexus_categories.json"
ADULT_CONTENT_CATEGORY_NAME = "Adult Content"
UNCATEGORIZED_CATEGORY_NAME = "Uncategorized"

# Synthetic home for mods that carry no category. It is not part of the Nexus
# taxonomy, so it is appended rather than read from the bundle.
_UNCATEGORIZED = Category(
    "uncategorized", UNCATEGORIZED_CATEGORY_NAME, "amber", built_in=True
)


def slugify(name: str) -> str:
    """Turn a human category name into a stable, lowercase key."""
    slug = re.sub(r"[^a-z0-9]+", "-", name.casefold()).strip("-")
    return slug or "category"


def palette_color_key(index: int) -> str:
    """Pick a palette color for the given slot, cycling deterministically."""
    return PALETTE[index % len(PALETTE)]


def load_category_catalog() -> list[Category]:
    """Return the available Nexus categories as app boxes (the *catalog*).

    This is reference data bundled with the app: the set of categories a mod may
    belong to. It intentionally does not decide which boxes are shown on the
    canvas or where they sit — that layout is manifest state owned elsewhere.
    """
    raw = json.loads(
        resources.files("app.data").joinpath(_CATALOG_RESOURCE).read_text("utf-8")
    )
    categories: list[Category] = []
    seen: set[str] = set()
    for entry in raw["categories"]:
        if not entry.get("parent_category"):
            continue  # skip the taxonomy root
        key = slugify(entry["name"])
        if key in seen:
            continue
        seen.add(key)
        categories.append(Category(key, entry["name"], palette_color_key(int(entry["category_id"]))))
    categories.append(_UNCATEGORIZED)
    return categories


def nexus_category_name(category_id: int | None) -> str | None:
    """Return Nexus's display name for a Witcher 3 mod category ID."""
    if category_id is None:
        return None
    raw = json.loads(
        resources.files("app.data").joinpath(_CATALOG_RESOURCE).read_text("utf-8")
    )
    for entry in raw.get("categories", []):
        if entry.get("category_id") == category_id:
            name = entry.get("name")
            return name if isinstance(name, str) else None
    return None


def preferred_install_category_name(
    nexus_category: str | None,
    *,
    contains_adult_content: bool,
) -> str:
    """Choose the app category for verified Nexus metadata.

    Adult content deliberately overrides Nexus's normal taxonomy so users can
    find, disable, or move all such mods as one group. Missing Nexus taxonomy
    data falls back to the permanent Uncategorized category.
    """
    if contains_adult_content:
        return ADULT_CONTENT_CATEGORY_NAME
    if isinstance(nexus_category, str) and nexus_category.strip():
        return nexus_category.strip()
    return UNCATEGORIZED_CATEGORY_NAME
