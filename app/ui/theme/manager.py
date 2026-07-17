from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QFont, QFontDatabase
from PyQt6.QtWidgets import QApplication

from app.ui.theme.styles import build_stylesheet
from app.ui.theme.tokens import (
    DARK,
    FONT_BODY,
    FONT_BODY_FALLBACK,
    FONT_HEADING,
    FONT_HEADING_FALLBACK,
    LIGHT,
)


def load_fonts() -> None:
    fonts_dir = Path(__file__).resolve().parents[3] / "assets" / "fonts"
    if fonts_dir.exists():
        for path in (*fonts_dir.glob("*.ttf"), *fonts_dir.glob("*.otf")):
            QFontDatabase.addApplicationFont(str(path))
    available = set(QFontDatabase.families())
    family = FONT_BODY if FONT_BODY in available else FONT_BODY_FALLBACK
    QApplication.setFont(QFont(family, 10))


class ThemeManager(QObject):
    theme_changed = pyqtSignal(bool)

    def __init__(self, app: QApplication) -> None:
        super().__init__()
        self._app = app
        self._dark = False
        available = set(QFontDatabase.families())
        body_font = FONT_BODY if FONT_BODY in available else FONT_BODY_FALLBACK
        heading_font = FONT_HEADING if FONT_HEADING in available else FONT_HEADING_FALLBACK
        self._light_qss = build_stylesheet(LIGHT, body_font, heading_font)
        self._dark_qss = build_stylesheet(DARK, body_font, heading_font)

    @property
    def is_dark(self) -> bool:
        return self._dark

    def apply_light(self) -> None:
        self._dark = False
        self._app.setStyleSheet(self._light_qss)
        self.theme_changed.emit(False)

    def apply_dark(self) -> None:
        self._dark = True
        self._app.setStyleSheet(self._dark_qss)
        self.theme_changed.emit(True)

    def toggle(self) -> None:
        self.apply_light() if self._dark else self.apply_dark()
