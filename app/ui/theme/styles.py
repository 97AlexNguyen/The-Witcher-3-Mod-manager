from __future__ import annotations

from app.ui.theme.tokens import (
    FONT_BODY,
    FONT_BODY_FALLBACK,
    FONT_HEADING,
    FONT_HEADING_FALLBACK,
    FONT_MONO,
    RADIUS_DEFAULT,
    RADIUS_LG,
    RADIUS_SM,
    SPACING_MD,
    SPACING_SM,
    SPACING_XS,
    TYPO_BODY_MD,
    TYPO_BODY_SM,
    TYPO_HEADLINE_MD,
    TYPO_HEADLINE_SM,
    TYPO_LABEL_MD,
    TYPO_LABEL_SM,
    DARK,
    LIGHT,
    ThemeColors,
    COLOR_DANGER,
)


def build_stylesheet(
    c: ThemeColors,
    body_font: str = FONT_BODY_FALLBACK,
    heading_font: str = FONT_HEADING_FALLBACK,
) -> str:
    return f"""
* {{ font-family: '{body_font}'; font-size: {TYPO_BODY_MD[0]}px; color: {c.on_surface}; outline: none; }}
QMainWindow, QWidget#appRoot {{ background: {c.background}; }}
QWidget#pageSurface {{ background: {c.background}; }}
QFrame#appHeader {{ background: {c.surface_lowest}; border-bottom: 1px solid {c.outline_variant}; }}
QLabel#brandMark {{ background: {c.primary_fixed}; color: {c.primary}; border: 1px solid {c.outline_variant}; border-radius: 22px; font-weight: 700; }}
QFrame#filterBar {{ background: {c.surface_lowest}; border: 1px solid {c.outline_variant}; border-radius: {RADIUS_LG}px; }}
QFrame#detailPanel {{ background: {c.surface_lowest}; border: 1px solid {c.outline_variant}; border-radius: {RADIUS_LG}px; }}
QFrame#detailMeta, QWidget#detailSection {{ background: {c.surface_low}; border: 1px solid {c.outline_variant}; border-radius: {RADIUS_DEFAULT}px; }}
QLabel#detailEmptyIcon {{ color: {c.primary}; font-size: 32px; }}
QFrame#filterBar QLineEdit, QFrame#filterBar QComboBox {{ min-height: 40px; border-radius: {RADIUS_DEFAULT}px; }}
QFrame#filterBar QPushButton {{ min-height: 40px; }}
QLabel[class="headline-md"] {{ font-family: '{heading_font}'; font-size: {TYPO_HEADLINE_MD[0]}px; font-weight: {TYPO_HEADLINE_MD[1]}; }}
QLabel[class="headline-sm"] {{ font-family: '{heading_font}'; font-size: {TYPO_HEADLINE_SM[0]}px; font-weight: {TYPO_HEADLINE_SM[1]}; }}
QLabel[class="label-md"] {{ font-size: {TYPO_LABEL_MD[0]}px; font-weight: {TYPO_LABEL_MD[1]}; letter-spacing: 0.05em; color: {c.on_surface_variant}; }}
QLabel[class="muted"] {{ color: {c.on_surface_variant}; }}
QLabel[class="mono"] {{ font-family: '{FONT_MONO}'; }}
QPushButton {{ min-height: 34px; padding: 0 {SPACING_MD}px; border: 1px solid {c.outline_variant}; border-radius: {RADIUS_DEFAULT}px; background: {c.surface_lowest}; font-size: {TYPO_LABEL_MD[0]}px; font-weight: {TYPO_LABEL_MD[1]}; }}
QPushButton:hover {{ background: {c.surface_low}; border-color: {c.outline}; }}
QPushButton:pressed {{ background: {c.surface_high}; }}
QPushButton:focus {{ border: 2px solid {c.primary}; }}
QPushButton:disabled {{ color: {c.outline}; background: {c.surface_low}; }}
QPushButton[class="primary"] {{ color: {c.on_primary}; background: {c.primary_container}; border-color: {c.primary_container}; }}
QPushButton[class="primary"]:hover {{ background: {c.primary}; border-color: {c.primary}; }}
QPushButton[class="danger"] {{ color: {COLOR_DANGER}; border-color: {COLOR_DANGER}; background: {c.surface_lowest}; }}
QPushButton[class="danger"]:hover {{ background: {c.surface_low}; }}
QPushButton[class="ghost"] {{ min-width: 34px; padding: 0 {SPACING_SM}px; background: transparent; border-color: transparent; color: {c.on_surface_variant}; }}
QPushButton[class="ghost"]:hover {{ background: {c.surface_low}; color: {c.on_surface}; }}
QPushButton[class="detailSegment"] {{ min-height: 28px; padding: 0 {SPACING_XS}px; background: transparent; border-color: transparent; color: {c.on_surface_variant}; font-size: {TYPO_LABEL_SM[0]}px; }}
QPushButton[class="detailSegment"]:hover {{ background: {c.surface_low}; color: {c.on_surface}; }}
QPushButton[class="detailSegment"]:checked {{ background: {c.primary_fixed}; color: {c.primary}; }}
QLineEdit, QComboBox, QSpinBox {{ min-height: 34px; padding: 0 {SPACING_SM}px; background: {c.surface_lowest}; border: 1px solid {c.outline_variant}; border-radius: {RADIUS_SM}px; selection-background-color: {c.primary_fixed}; }}
QLineEdit:hover, QComboBox:hover, QSpinBox:hover {{ border-color: {c.outline}; }}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus {{ border: 2px solid {c.primary}; }}
QComboBox::drop-down {{ width: 24px; border: none; }}
QComboBox QAbstractItemView {{ background: {c.surface_lowest}; border: 1px solid {c.outline_variant}; selection-background-color: {c.primary_fixed}; selection-color: {c.on_surface}; }}
QListView#modCardList {{ background: transparent; border: none; padding: 0; }}
QListView#modCardList::item {{ background: transparent; border: none; }}
QListView#modCardList::item:selected {{ background: transparent; }}
QWidget#emptyState {{ background: {c.surface_lowest}; border: 1px solid {c.outline_variant}; border-radius: {RADIUS_LG}px; }}
QLabel#noticeBar {{ padding: {SPACING_SM}px {SPACING_MD}px; background: {c.primary_fixed}; color: {c.primary}; border: 1px solid {c.primary}; border-radius: {RADIUS_DEFAULT}px; font-size: {TYPO_BODY_SM[0]}px; }}
QScrollArea#detailScroll {{ background: transparent; border: none; }}
QScrollArea#detailScroll QWidget#qt_scrollarea_viewport {{ background: transparent; }}
QScrollBar:vertical {{ width: 6px; background: transparent; }}
QScrollBar::handle:vertical {{ min-height: 24px; background: {c.outline_variant}; border-radius: 3px; }}
QScrollBar::handle:vertical:hover {{ background: {c.outline}; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
QSplitter#modWorkspaceSplitter::handle {{ background: {c.outline_variant}; width: 1px; }}
QToolTip {{ padding: {SPACING_XS}px {SPACING_SM}px; background: {c.inverse_surface}; color: {c.inverse_on_surface}; border: none; border-radius: {RADIUS_SM}px; font-size: {TYPO_LABEL_SM[0]}px; }}
"""


LIGHT_QSS = build_stylesheet(LIGHT)
DARK_QSS = build_stylesheet(DARK)
