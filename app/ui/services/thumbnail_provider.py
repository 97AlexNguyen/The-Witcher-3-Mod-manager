from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import QRect, QSize, Qt
from PyQt6.QtGui import QColor, QFont, QLinearGradient, QPainter, QPixmap

from app.domain import InstalledMod
from app.ui.theme.tokens import DARK, LIGHT, ThemeColors


class ThumbnailProvider:
    """Loads real thumbnails when present and creates cached mock covers otherwise."""

    def __init__(self) -> None:
        self._cache: dict[tuple[str, str, int, int, bool], QPixmap] = {}

    def pixmap(
        self,
        mod: InstalledMod,
        accent: str,
        size: int | QSize,
        dark_theme: bool,
    ) -> QPixmap:
        target = QSize(size, size) if isinstance(size, int) else size
        cache_key = (mod.thumbnail_path or mod.identity, accent, target.width(), target.height(), dark_theme)
        if cache_key not in self._cache:
            self._cache[cache_key] = self._build(mod, accent, target, dark_theme)
        return self._cache[cache_key]

    def _build(self, mod: InstalledMod, accent: str, size: QSize, dark_theme: bool) -> QPixmap:
        if mod.thumbnail_path and Path(mod.thumbnail_path).is_file():
            source = QPixmap(mod.thumbnail_path)
            if not source.isNull():
                return self._cover_crop(source, size)
        return self._placeholder(mod, accent, size, DARK if dark_theme else LIGHT)

    @staticmethod
    def _cover_crop(source: QPixmap, size: QSize) -> QPixmap:
        scaled = source.scaled(
            size.width(),
            size.height(),
            Qt.AspectRatioMode.KeepAspectRatioByExpanding,
            Qt.TransformationMode.SmoothTransformation,
        )
        left = max(0, (scaled.width() - size.width()) // 2)
        top = max(0, (scaled.height() - size.height()) // 2)
        return scaled.copy(QRect(left, top, size.width(), size.height()))

    @staticmethod
    def _placeholder(mod: InstalledMod, accent: str, size: QSize, theme: ThemeColors) -> QPixmap:
        width, height = size.width(), size.height()
        pixmap = QPixmap(width, height)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        gradient = QLinearGradient(0, 0, width, height)
        gradient.setColorAt(0.0, QColor(accent).lighter(116))
        gradient.setColorAt(1.0, QColor(theme.surface_high))
        painter.fillRect(pixmap.rect(), gradient)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(accent))
        painter.drawEllipse(width // 2, -height // 3, width, width)

        initials = "".join(word[0] for word in mod.name.split() if word and word[0].isalnum())[:2].upper()
        font = QFont()
        font.setPixelSize(16)
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(QColor(theme.on_surface))
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, initials or "MOD")
        painter.end()
        return pixmap
