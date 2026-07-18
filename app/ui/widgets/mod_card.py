from __future__ import annotations

from PyQt6.QtCore import QMimeData, QPoint, QPointF, QRect, QSize, Qt, pyqtSignal
from PyQt6.QtGui import QDrag, QFont, QFontMetrics, QMouseEvent, QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMenu,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from app.domain import Category, InstalledMod, ModStatus
from app.ui.services import ThumbnailProvider
from app.ui.theme.tokens import (
    CATEGORY_COLORS,
    CATEGORY_KEY_COLORS,
    COLOR_DANGER,
    COLOR_SUCCESS,
    COLOR_WARNING,
    GROUP_CARD_HEIGHT,
    GROUP_CARD_THUMBNAIL,
    GROUP_CARD_WIDTH,
    RADIUS_DEFAULT,
    SPACING_SM,
    SPACING_XS,
    TYPO_BODY_MD,
)

# Carries the dragged mod's identity between boxes. Identity, not a Python object
# reference, because a QMimeData payload crosses the drag/drop boundary as bytes.
MIME_MOD_IDENTITY = "application/x-w3mm-mod-identity"

_STATUS_META: dict[ModStatus, tuple[str, str]] = {
    ModStatus.OK: ("Healthy", COLOR_SUCCESS),
    ModStatus.INCOMPLETE: ("Needs attention", COLOR_WARNING),
    ModStatus.VAULT_MISSING: ("Vault missing", COLOR_WARNING),
    ModStatus.ERROR: ("Error", COLOR_DANGER),
}

_NAME_LINES = 2


def _wrap_elided(metrics: QFontMetrics, text: str, width: int, max_lines: int) -> str:
    """Wrap ``text`` into at most ``max_lines`` lines of ``width`` px, ellipsising overflow.

    Guarantees the result fits the given box: never clipped mid-glyph, never taller
    than ``max_lines``. Overflow is marked with an ellipsis and the full text lives
    in the card's tool tip, so nothing is silently lost.
    """
    words = text.split()
    lines: list[str] = []
    current = ""
    index = 0
    while index < len(words) and len(lines) < max_lines:
        word = words[index]
        trial = word if not current else f"{current} {word}"
        if not current or metrics.horizontalAdvance(trial) <= width:
            current = trial
            index += 1
        else:
            lines.append(current)
            current = ""
    if current and len(lines) < max_lines:
        lines.append(current)
        current = ""
    has_leftover = index < len(words) or bool(current)
    if has_leftover and lines:
        lines[-1] = metrics.elidedText(lines[-1] + "…", Qt.TextElideMode.ElideRight, width)
    # A single over-long word is force-accepted above; elide any line that still overflows.
    lines = [
        line if metrics.horizontalAdvance(line) <= width
        else metrics.elidedText(line, Qt.TextElideMode.ElideRight, width)
        for line in lines
    ]
    return "\n".join(lines)


class ModCard(QFrame):
    """One mod inside an open box. Fixed size, draggable to another box.

    Every card is exactly the same size regardless of its mod's name length,
    version presence, or status — the grid inside a box must read as an even
    rack of identical slots, not a ragged list.
    """

    enabled_toggled = pyqtSignal(object)          # -> InstalledMod
    move_requested = pyqtSignal(object, str)      # -> InstalledMod, target category key
    remove_requested = pyqtSignal(object)         # -> InstalledMod
    details_requested = pyqtSignal(object)        # -> InstalledMod

    def __init__(
        self,
        mod: InstalledMod,
        categories: list[Category],
        thumbnails: ThumbnailProvider,
        dark_theme: bool,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.mod = mod
        self._categories = categories
        self._press_pos = None
        self._open_menu: QMenu | None = None
        accent = CATEGORY_KEY_COLORS.get(mod.category_key, CATEGORY_COLORS["neutral"])

        self.setObjectName("modCard")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setFixedSize(GROUP_CARD_WIDTH, GROUP_CARD_HEIGHT)
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        self.setProperty("modEnabled", "true" if mod.enabled else "false")
        self.setToolTip(f"{mod.name}\n\nDrag onto another box to recategorize · double-click for details")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(SPACING_SM + SPACING_XS, SPACING_SM, SPACING_SM + SPACING_XS, SPACING_SM)
        outer.setSpacing(SPACING_SM)

        top = QHBoxLayout()
        top.setSpacing(SPACING_SM)
        thumb = QLabel()
        thumb.setFixedSize(GROUP_CARD_THUMBNAIL, GROUP_CARD_THUMBNAIL)
        pixmap = thumbnails.pixmap(mod, accent, QSize(GROUP_CARD_THUMBNAIL, GROUP_CARD_THUMBNAIL), dark_theme)
        thumb.setPixmap(self._rounded(pixmap, RADIUS_DEFAULT))
        top.addWidget(thumb, 0, Qt.AlignmentFlag.AlignTop)

        name_font = QFont()
        name_font.setPointSize(TYPO_BODY_MD[0])
        name_font.setWeight(QFont.Weight.DemiBold)
        metrics = QFontMetrics(name_font)
        name_width = GROUP_CARD_WIDTH - 2 * (SPACING_SM + SPACING_XS) - GROUP_CARD_THUMBNAIL - SPACING_SM
        self.name_label = QLabel(_wrap_elided(metrics, mod.name, name_width, _NAME_LINES))
        self.name_label.setObjectName("modCardName")
        self.name_label.setFont(name_font)
        self.name_label.setFixedHeight(metrics.lineSpacing() * _NAME_LINES)
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.name_label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        top.addWidget(self.name_label, 1)
        outer.addLayout(top)

        bottom = QHBoxLayout()
        bottom.setSpacing(SPACING_SM)
        self.toggle = QToolButton()
        self.toggle.setObjectName("modToggle")
        self.toggle.setCheckable(True)
        self.toggle.setChecked(mod.enabled)
        self.toggle.setFixedSize(46, 22)
        self.toggle.setCursor(Qt.CursorShape.PointingHandCursor)
        self.toggle.setText("ON" if mod.enabled else "OFF")
        self.toggle.clicked.connect(self._on_toggle)
        bottom.addWidget(self.toggle)
        bottom.addStretch()

        version = QLabel(f"v{mod.version}" if mod.version else "no version")
        version.setProperty("class", "muted")
        bottom.addWidget(version)

        label, color = _STATUS_META[mod.status]
        status = QLabel(label)
        status.setStyleSheet(f"color: {color}; font-weight: 600;")
        status.setToolTip(mod.status_detail)
        bottom.addWidget(status)

        self.menu_button = QToolButton()
        self.menu_button.setObjectName("cardMenuButton")
        self.menu_button.setText("⋮")
        self.menu_button.setToolTip("More actions")
        self.menu_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.menu_button.clicked.connect(self._show_menu)
        bottom.addWidget(self.menu_button)
        outer.addLayout(bottom)

    @staticmethod
    def _rounded(pixmap: QPixmap, radius: int) -> QPixmap:
        from PyQt6.QtCore import QRectF
        from PyQt6.QtGui import QPainter, QPainterPath

        rounded = QPixmap(pixmap.size())
        rounded.fill(Qt.GlobalColor.transparent)
        painter = QPainter(rounded)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(QRectF(rounded.rect()), radius, radius)
        painter.setClipPath(path)
        painter.drawPixmap(0, 0, pixmap)
        painter.end()
        return rounded

    def _build_menu(self, parent: QWidget | None = None) -> QMenu:
        menu = QMenu(parent or self)
        move = menu.addMenu("Move to box")
        for category in self._categories:
            if category.key == self.mod.category_key:
                continue
            action = move.addAction(category.name)
            action.triggered.connect(lambda _checked, key=category.key: self.move_requested.emit(self.mod, key))
        details = menu.addAction("View details")
        details.triggered.connect(lambda: self.details_requested.emit(self.mod))
        menu.addSeparator()
        remove = menu.addAction("Remove mod")
        remove.triggered.connect(lambda: self.remove_requested.emit(self.mod))
        return menu

    def _show_menu(self) -> None:
        """Show actions as a native popup anchored to the transformed canvas button."""
        if self._open_menu is not None:
            self._open_menu.close()
            self._open_menu.deleteLater()
        view = self._embedded_view()
        menu = self._build_menu(view or self)
        menu.ensurePolished()
        menu.aboutToHide.connect(menu.deleteLater)
        menu.destroyed.connect(lambda _object=None, closing=menu: self._on_menu_destroyed(closing))
        self._open_menu = menu
        menu.popup(self._menu_popup_position(menu))

    def _on_menu_destroyed(self, menu: QMenu) -> None:
        if self._open_menu is menu:
            self._open_menu = None

    def close_actions_menu(self) -> None:
        if self._open_menu is not None:
            self._open_menu.close()

    def _embedded_proxy(self):
        widget: QWidget | None = self
        while widget is not None:
            proxy = widget.graphicsProxyWidget()
            if proxy is not None:
                return proxy
            widget = widget.parentWidget()
        return None

    def _embedded_view(self):
        proxy = self._embedded_proxy()
        if proxy is not None and proxy.scene() is not None and proxy.scene().views():
            return proxy.scene().views()[0]
        return None

    def _menu_button_global_rect(self) -> QRect:
        proxy = self._embedded_proxy()
        view = self._embedded_view()
        embedded = proxy.widget() if proxy is not None else None
        if proxy is None or view is None or embedded is None:
            top_left = self.menu_button.mapToGlobal(QPoint())
            return QRect(top_left, self.menu_button.size())

        local_top_left = self.menu_button.mapTo(embedded, QPoint())
        local_bottom_right = self.menu_button.mapTo(embedded, self.menu_button.rect().bottomRight())
        scene_top_left = proxy.mapToScene(QPointF(local_top_left))
        scene_bottom_right = proxy.mapToScene(QPointF(local_bottom_right))
        global_top_left = view.viewport().mapToGlobal(view.mapFromScene(scene_top_left))
        global_bottom_right = view.viewport().mapToGlobal(view.mapFromScene(scene_bottom_right))
        return QRect(global_top_left, global_bottom_right).normalized()

    def _menu_popup_position(self, menu: QMenu) -> QPoint:
        button = self._menu_button_global_rect()
        menu_size = menu.sizeHint()
        screen = QApplication.screenAt(button.center()) or QApplication.primaryScreen()
        if screen is None:
            return button.bottomLeft()
        available = screen.availableGeometry()
        x = button.right() - menu_size.width() + 1
        below = button.bottom() + SPACING_XS + 1
        above = button.top() - SPACING_XS - menu_size.height()
        y = below if below + menu_size.height() <= available.bottom() + 1 else above
        x = max(available.left(), min(x, available.right() - menu_size.width() + 1))
        y = max(available.top(), min(y, available.bottom() - menu_size.height() + 1))
        return QPoint(x, y)

    def _on_toggle(self) -> None:
        enabled = self.toggle.isChecked()
        # The card, its box, and the list model all reference this same InstalledMod
        # object; update it here so every view is consistent before anyone reads it.
        # The page still routes the change through the model so its listeners fire.
        self.mod.enabled = enabled
        self.toggle.setText("ON" if enabled else "OFF")
        self.setProperty("modEnabled", "true" if enabled else "false")
        self.style().unpolish(self)
        self.style().polish(self)
        self.enabled_toggled.emit(self.mod)

    # -- drag source + double-click ---------------------------------------- #

    def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton:
            self._press_pos = event.position().toPoint()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if not (event.buttons() & Qt.MouseButton.LeftButton) or self._press_pos is None:
            return
        moved = (event.position().toPoint() - self._press_pos).manhattanLength()
        if moved < QApplication.startDragDistance():
            return
        # The graphics workspace owns in-canvas card dragging. Native QDrag from
        # inside a QGraphicsProxyWidget is unreliable once the view is transformed.
        if self._embedded_view() is not None:
            event.ignore()
            return
        self._press_pos = None
        drag = QDrag(self)
        mime = QMimeData()
        mime.setData(MIME_MOD_IDENTITY, self.mod.identity.encode("utf-8"))
        drag.setMimeData(mime)
        pixmap = self.grab()
        drag.setPixmap(pixmap)
        drag.setHotSpot(event.position().toPoint())
        drag.exec(Qt.DropAction.MoveAction)

    def cancel_pending_drag(self) -> None:
        self._press_pos = None

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton:
            self._press_pos = None
            self.details_requested.emit(self.mod)
            event.accept()
            return
        super().mouseDoubleClickEvent(event)
