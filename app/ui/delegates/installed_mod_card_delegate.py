from __future__ import annotations

from PyQt6.QtCore import QEvent, QRect, QRectF, QSize, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QMouseEvent, QPainter, QPainterPath, QPalette, QPen
from PyQt6.QtWidgets import QStyle, QStyledItemDelegate, QStyleOptionViewItem, QToolTip

from app.domain import ModStatus
from app.ui.models import InstalledModRoles
from app.ui.services import ThumbnailProvider
from app.ui.theme.tokens import (
    CATEGORY_KEY_COLORS,
    COLOR_DANGER,
    COLOR_SUCCESS,
    COLOR_WARNING,
    DARK,
    LIGHT,
    MOD_CARD_HEIGHT,
    MOD_CARD_THUMBNAIL_HEIGHT,
    MOD_CARD_THUMBNAIL_WIDTH,
    RADIUS_DEFAULT,
    RADIUS_LG,
    SPACING_MD,
    SPACING_SM,
    SPACING_XS,
    TYPO_BODY_MD,
    TYPO_BODY_SM,
    TYPO_HEADLINE_SM,
    TYPO_LABEL_SM,
)


class InstalledModCardDelegate(QStyledItemDelegate):
    remove_requested = pyqtSignal(object)

    ACTION_WIDTH = 112
    ACTION_HEIGHT = 28

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._thumbnails = ThumbnailProvider()

    def sizeHint(self, option, index) -> QSize:  # noqa: N802
        return QSize(max(720, option.rect.width()), MOD_CARD_HEIGHT)

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index) -> None:
        mod = index.data(InstalledModRoles.MOD)
        if mod is None:
            return

        explicit_theme = option.widget.property("darkTheme") if option.widget else None
        dark_theme = (
            bool(explicit_theme)
            if explicit_theme is not None
            else option.palette.color(QPalette.ColorRole.Window).lightness() < 128
        )
        theme = DARK if dark_theme else LIGHT
        selected = bool(option.state & QStyle.StateFlag.State_Selected)
        hovered = bool(option.state & QStyle.StateFlag.State_MouseOver)
        card = option.rect.adjusted(0, SPACING_XS, 0, -SPACING_XS)
        accent = index.data(InstalledModRoles.CATEGORY_COLOR)

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QPen(QColor(theme.primary if selected else theme.outline_variant), 1))
        painter.setBrush(QColor(theme.primary_fixed if selected else theme.surface_high if hovered else theme.surface_lowest))
        painter.drawRoundedRect(card, RADIUS_LG, RADIUS_LG)

        thumbnail_rect = QRect(
            card.left() + SPACING_SM,
            card.top() + SPACING_SM,
            MOD_CARD_THUMBNAIL_WIDTH,
            MOD_CARD_THUMBNAIL_HEIGHT,
        )
        thumbnail = self._thumbnails.pixmap(
            mod,
            accent,
            QSize(MOD_CARD_THUMBNAIL_WIDTH, MOD_CARD_THUMBNAIL_HEIGHT),
            dark_theme,
        )
        thumbnail_path = QPainterPath()
        thumbnail_path.addRoundedRect(QRectF(thumbnail_rect), RADIUS_DEFAULT, RADIUS_DEFAULT)
        painter.setClipPath(thumbnail_path)
        painter.setOpacity(1.0 if mod.enabled else 0.48)
        painter.drawPixmap(thumbnail_rect, thumbnail)
        painter.setClipping(False)
        painter.setOpacity(1.0)
        painter.setPen(QPen(QColor(theme.outline_variant), 1))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(thumbnail_rect, RADIUS_DEFAULT, RADIUS_DEFAULT)
        self._paint_status_badge(painter, thumbnail_rect, mod.enabled, theme)

        action_rects = self._action_rects(card)
        content_left = thumbnail_rect.right() + 12
        content_right = action_rects[0].left() - 12
        content_width = max(80, content_right - content_left)
        title_color = QColor(theme.on_surface if mod.enabled else theme.on_surface_variant)
        muted_color = QColor(theme.on_surface_variant)

        title_font = painter.font()
        title_font.setPointSize(TYPO_BODY_MD[0])
        title_font.setWeight(QFont.Weight.DemiBold)
        painter.setFont(title_font)
        painter.setPen(title_color)
        title = painter.fontMetrics().elidedText(mod.name, Qt.TextElideMode.ElideRight, content_width)
        painter.drawText(
            QRect(content_left, card.top() + SPACING_SM, content_width, 20),
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            title,
        )

        body_font = painter.font()
        body_font.setPointSize(TYPO_BODY_SM[0])
        body_font.setWeight(QFont.Weight.Normal)
        painter.setFont(body_font)
        painter.setPen(muted_color)
        description = painter.fontMetrics().elidedText(mod.description, Qt.TextElideMode.ElideRight, content_width)
        painter.drawText(
            QRect(content_left, card.top() + 30, content_width, 18),
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            description,
        )

        priority = "Unassigned" if mod.priority is None else str(mod.priority)
        metadata = f"v{mod.version or '?'}   ·   Priority {priority}   ·   Installed {mod.installed_on.isoformat()}"
        painter.drawText(
            QRect(content_left, card.top() + 52, content_width, 16),
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            metadata,
        )
        self._paint_tag(painter, QRect(content_left, card.top() + 76, 104, 20), mod.category_key, accent, theme)
        self._paint_health(painter, content_left + 112, card.top() + 76, mod.status, theme)

        self._paint_action(painter, action_rects[0], "DISABLE" if mod.enabled else "ENABLE", theme)
        self._paint_action(painter, action_rects[1], "REMOVE", theme, danger=True)
        painter.restore()

    def editorEvent(self, event, model, option, index) -> bool:  # noqa: N802
        if event.type() != QEvent.Type.MouseButtonRelease or not isinstance(event, QMouseEvent):
            return False
        if event.button() != Qt.MouseButton.LeftButton:
            return False
        card = option.rect.adjusted(0, SPACING_XS, 0, -SPACING_XS)
        toggle_rect, remove_rect = self._action_rects(card)
        point = event.position().toPoint()
        if toggle_rect.contains(point):
            return model.setData(index, not bool(index.data(InstalledModRoles.ENABLED)), InstalledModRoles.ENABLED)
        if remove_rect.contains(point):
            mod = index.data(InstalledModRoles.MOD)
            if mod is not None:
                self.remove_requested.emit(mod)
            return True
        return False

    def helpEvent(self, event, view, option, index) -> bool:  # noqa: N802
        if event.type() != QEvent.Type.ToolTip:
            return super().helpEvent(event, view, option, index)
        mod = index.data(InstalledModRoles.MOD)
        if mod is None:
            return super().helpEvent(event, view, option, index)
        card = option.rect.adjusted(0, SPACING_XS, 0, -SPACING_XS)
        toggle_rect, remove_rect = self._action_rects(card)
        tips = (
            (toggle_rect, f"{'Disable' if mod.enabled else 'Enable'} {mod.name}  (Space)"),
            (remove_rect, f"Remove {mod.name}  (Delete)"),
        )
        for rect, text in tips:
            if rect.contains(event.pos()):
                QToolTip.showText(event.globalPos(), text, view)
                return True
        return super().helpEvent(event, view, option, index)

    def _action_rects(self, card: QRect) -> tuple[QRect, QRect]:
        left = card.right() - SPACING_SM - self.ACTION_WIDTH
        block = self.ACTION_HEIGHT * 2 + SPACING_XS
        top = card.top() + (card.height() - block) // 2
        first = QRect(left, top, self.ACTION_WIDTH, self.ACTION_HEIGHT)
        second = first.translated(0, self.ACTION_HEIGHT + SPACING_XS)
        return first, second

    @staticmethod
    def _paint_status_badge(painter: QPainter, thumbnail: QRect, enabled: bool, theme) -> None:
        text = "ENABLED" if enabled else "DISABLED"
        width = 68 if enabled else 72
        rect = QRect(thumbnail.left() + SPACING_XS, thumbnail.top() + SPACING_XS, width, 20)
        painter.setPen(QPen(QColor(COLOR_SUCCESS if enabled else theme.on_surface_variant), 1))
        painter.setBrush(QColor(theme.surface_lowest))
        painter.drawRoundedRect(rect, 10, 10)
        font = painter.font()
        font.setPointSize(TYPO_LABEL_SM[0])
        font.setWeight(QFont.Weight.DemiBold)
        painter.setFont(font)
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, text)

    @staticmethod
    def _paint_tag(painter: QPainter, rect: QRect, category_key: str, accent: str, theme) -> None:
        label = category_key.replace("_", " ").title()
        painter.setPen(QPen(QColor(accent), 1))
        painter.setBrush(QColor(theme.surface_low))
        painter.drawRoundedRect(rect, 10, 10)
        font = painter.font()
        font.setPointSize(TYPO_LABEL_SM[0])
        painter.setFont(font)
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, label)

    @staticmethod
    def _paint_health(painter: QPainter, left: int, top: int, status: ModStatus, theme) -> None:
        labels = {
            ModStatus.OK: ("HEALTHY", COLOR_SUCCESS),
            ModStatus.INCOMPLETE: ("NEEDS ATTENTION", COLOR_WARNING),
            ModStatus.VAULT_MISSING: ("VAULT MISSING", theme.on_surface_variant),
            ModStatus.ERROR: ("ERROR", COLOR_DANGER),
        }
        text, color = labels[status]
        width = max(72, len(text) * 7 + 20)
        rect = QRect(left, top, width, 24)
        painter.setPen(QColor(color))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawText(rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, text)

    @staticmethod
    def _paint_action(painter: QPainter, rect: QRect, text: str, theme, danger: bool = False) -> None:
        color = QColor(COLOR_DANGER if danger else theme.on_surface)
        border = QColor(COLOR_DANGER if danger else theme.outline_variant)
        painter.setPen(QPen(border, 1))
        painter.setBrush(QColor(theme.surface_low))
        painter.drawRoundedRect(rect, RADIUS_DEFAULT, RADIUS_DEFAULT)
        font = painter.font()
        font.setPointSize(TYPO_LABEL_SM[0])
        font.setWeight(QFont.Weight.DemiBold)
        painter.setFont(font)
        painter.setPen(color)
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, text)
