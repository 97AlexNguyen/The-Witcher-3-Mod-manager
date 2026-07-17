from __future__ import annotations

from dataclasses import dataclass

FONT_HEADING = "Hanken Grotesk"
FONT_BODY = "Inter"
FONT_MONO = "Cascadia Mono"
FONT_HEADING_FALLBACK = "Segoe UI Semibold"
FONT_BODY_FALLBACK = "Segoe UI"

TYPO_HEADLINE_LG = (24, 600, 32, -0.01)
TYPO_HEADLINE_MD = (20, 600, 28, -0.01)
TYPO_HEADLINE_SM = (16, 600, 24, 0.00)
TYPO_BODY_LG = (15, 400, 22, 0.00)
TYPO_BODY_MD = (14, 400, 20, 0.00)
TYPO_BODY_SM = (13, 400, 18, 0.00)
TYPO_LABEL_MD = (12, 600, 16, 0.05)
TYPO_LABEL_SM = (11, 500, 14, 0.00)

SPACING_XS = 4
SPACING_SM = 8
SPACING_MD = 16
SPACING_LG = 24
SPACING_XL = 32

RADIUS_SM = 2
RADIUS_DEFAULT = 4
RADIUS_MD = 6
RADIUS_LG = 8
RADIUS_XL = 12
RADIUS_FULL = 9999

TABLE_ROW_HEIGHT = 72
MOD_THUMBNAIL_SIZE = 48
MOD_CARD_HEIGHT = 112
MOD_CARD_THUMBNAIL_WIDTH = 132
MOD_CARD_THUMBNAIL_HEIGHT = 88
CATEGORY_RAIL_WIDTH = 180
DETAIL_PANEL_WIDTH = 320

COLOR_SUCCESS = "#1e7d4a"
COLOR_WARNING = "#b45309"
COLOR_DANGER = "#ba1a1a"

CATEGORY_COLORS = {
    "neutral": "#737685",
    "blue": "#4f83ff",
    "violet": "#9b7cff",
    "teal": "#2aa198",
    "amber": "#d58a1f",
}

CATEGORY_KEY_COLORS = {
    "graphics": CATEGORY_COLORS["blue"],
    "gameplay": CATEGORY_COLORS["violet"],
    "interface": CATEGORY_COLORS["teal"],
    "uncategorized": CATEGORY_COLORS["amber"],
}


@dataclass(frozen=True, slots=True)
class ThemeColors:
    background: str
    surface: str
    surface_lowest: str
    surface_low: str
    surface_high: str
    on_surface: str
    on_surface_variant: str
    outline: str
    outline_variant: str
    primary: str
    on_primary: str
    primary_container: str
    primary_fixed: str
    inverse_surface: str
    inverse_on_surface: str


LIGHT = ThemeColors(
    background="#faf9ff",
    surface="#e9edff",
    surface_lowest="#ffffff",
    surface_low="#f1f3ff",
    surface_high="#e1e8ff",
    on_surface="#051a3e",
    on_surface_variant="#434654",
    outline="#737685",
    outline_variant="#c3c6d6",
    primary="#003d9b",
    on_primary="#ffffff",
    primary_container="#0052cc",
    primary_fixed="#dae2ff",
    inverse_surface="#1d3054",
    inverse_on_surface="#edf0ff",
)

DARK = ThemeColors(
    background="#0B121F",
    surface="#161C27",
    surface_lowest="#161C27",
    surface_low="#1E2738",
    surface_high="#252D3D",
    on_surface="#edf0ff",
    on_surface_variant="#9ca3b8",
    outline="#3d4560",
    outline_variant="#252D3D",
    primary="#b2c5ff",
    on_primary="#081a3a",
    primary_container="#0040a2",
    primary_fixed="#26395c",
    inverse_surface="#edf0ff",
    inverse_on_surface="#1d3054",
)
