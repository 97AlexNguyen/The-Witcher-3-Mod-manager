from __future__ import annotations

from PyQt6.QtCore import QPoint, QPointF, QRect, QSize, Qt, pyqtSignal
from PyQt6.QtGui import QFont, QMouseEvent, QResizeEvent
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QScrollArea,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from app.domain import Category, InstalledMod, ModStatus
from app.ui.services import ThumbnailProvider
from app.ui.theme.tokens import (
    CATEGORY_COLORS,
    CATEGORY_KEY_COLORS,
    BOX_COLLAPSED_HEIGHT,
    BOX_DEFAULT_HEIGHT,
    BOX_DEFAULT_WIDTH,
    BOX_MIN_HEIGHT,
    BOX_RESIZE_HANDLE_SIZE,
    GROUP_CARD_WIDTH,
    SPACING_MD,
    SPACING_SM,
    TYPO_HEADLINE_SM,
)
from app.ui.widgets.flow_layout import FlowLayout
from app.ui.widgets.mod_card import ModCard
from app.ui.widgets.mod_drop_target import ModDropTargetMixin

class BoxDragHandle(QToolButton):
    """Visual grab handle; the canvas owns pointer tracking for stable dragging."""

    def __init__(self, category_key: str, box: QWidget, parent=None) -> None:
        super().__init__(parent)
        self._box = box
        self.setObjectName("boxDragHandle")
        self.setText("⠿")
        self.setToolTip("Drag to move this box")
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        self.setFixedSize(28, 28)

class BoxResizeHandle(QToolButton):
    """Bottom-right grip that resizes only its owning box."""

    def __init__(self, box: QWidget, parent=None) -> None:
        super().__init__(parent)
        self._box = box
        self._press_scene: QPointF | None = None
        self._origin_size: QSize | None = None
        self.setObjectName("boxResizeHandle")
        self.setText("◢")
        self.setToolTip("Drag to resize this box")
        self.setCursor(Qt.CursorShape.SizeFDiagCursor)
        self.setFixedSize(BOX_RESIZE_HANDLE_SIZE, BOX_RESIZE_HANDLE_SIZE)

    def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton:
            self._press_scene = self._box.canvas_point_from_global(event.globalPosition().toPoint())
            self._origin_size = self._box.size()
            self._box.raise_on_canvas()
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if self._press_scene is None or self._origin_size is None:
            return
        current = self._box.canvas_point_from_global(event.globalPosition().toPoint())
        delta = current - self._press_scene
        width = max(self._box.minimumWidth(), self._origin_size.width() + delta.x())
        height = max(self._box.minimumHeight(), self._origin_size.height() + delta.y())
        self._box.resize(int(round(width / 4) * 4), int(round(height / 4) * 4))
        self._box.notify_geometry_changed()
        event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        self._press_scene = None
        self._origin_size = None
        self._box.notify_geometry_changed()
        event.accept()


class CategoryBox(ModDropTargetMixin, QFrame):
    """One independent, collapsible and draggable category box."""

    mod_dropped = pyqtSignal(str, str)
    mod_enabled = pyqtSignal(object)
    mod_moved = pyqtSignal(object, str)
    mod_removed = pyqtSignal(object)
    mod_details = pyqtSignal(object)
    collapsed_changed = pyqtSignal(str, bool)
    geometry_changed = pyqtSignal(str, QRect)

    def __init__(
        self,
        category: Category,
        categories: list[Category],
        thumbnails: ThumbnailProvider,
        dark_theme: bool,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.category = category
        self._categories = categories
        self._thumbnails = thumbnails
        self._dark_theme = dark_theme
        self._target_category_key = category.key
        self._accent = CATEGORY_KEY_COLORS.get(category.key, CATEGORY_COLORS["neutral"])
        self._mods: list[InstalledMod] = []
        self._search = ""
        self._collapsed = False
        self._expanded_size = QSize(BOX_DEFAULT_WIDTH, BOX_DEFAULT_HEIGHT)

        self.setObjectName("categoryBox")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setAcceptDrops(True)
        self.setProperty("dropActive", "false")
        self.setProperty("collapsed", "false")
        self.setMinimumSize(GROUP_CARD_WIDTH + 2 * SPACING_MD, BOX_MIN_HEIGHT)
        self.resize(self._expanded_size)

        root = QVBoxLayout(self)
        root.setContentsMargins(SPACING_MD, SPACING_SM, SPACING_MD, SPACING_MD)
        root.setSpacing(SPACING_SM)

        header = QHBoxLayout()
        header.setSpacing(SPACING_SM)
        self.drag_handle = BoxDragHandle(category.key, self, self)
        header.addWidget(self.drag_handle)

        dot = QLabel()
        dot.setFixedSize(12, 12)
        dot.setStyleSheet(f"background: {self._accent}; border-radius: 6px;")
        header.addWidget(dot, 0, Qt.AlignmentFlag.AlignVCenter)

        name_font = QFont()
        name_font.setPointSize(TYPO_HEADLINE_SM[0])
        name_font.setWeight(QFont.Weight.DemiBold)
        name = QLabel(category.name)
        name.setFont(name_font)
        header.addWidget(name)

        self.stats_label = QLabel()
        self.stats_label.setObjectName("boxStats")
        header.addWidget(self.stats_label)

        self.attention_label = QLabel("")
        self.attention_label.setObjectName("boxTileAttention")
        header.addWidget(self.attention_label)
        header.addStretch()

        self.collapse_button = QToolButton()
        self.collapse_button.setObjectName("boxCollapseButton")
        self.collapse_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.collapse_button.setFixedSize(28, 28)
        self.collapse_button.clicked.connect(lambda: self.set_collapsed(not self._collapsed))
        header.addWidget(self.collapse_button)
        root.addLayout(header)

        self.body = QWidget()
        body_layout = QVBoxLayout(self.body)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(SPACING_SM)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search…")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.textChanged.connect(self._on_search)
        body_layout.addWidget(self.search_input)

        self.scroll = QScrollArea()
        self.scroll.setObjectName("boxScroll")
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        host = QWidget()
        self.flow = FlowLayout(host, margin=0, spacing=SPACING_SM + 2)
        self.scroll.setWidget(host)
        body_layout.addWidget(self.scroll, 1)

        self.empty_label = QLabel("This box is empty. Drag a mod here to move it in.")
        self.empty_label.setProperty("class", "muted")
        self.empty_label.setWordWrap(True)
        self.empty_label.hide()
        body_layout.addWidget(self.empty_label)
        root.addWidget(self.body)

        self.resize_handle = BoxResizeHandle(self, self)
        self.resize_handle.raise_()

        self.set_collapsed(False, emit_signal=False)

    def sizeHint(self) -> QSize:  # noqa: N802
        return QSize(BOX_DEFAULT_WIDTH, BOX_COLLAPSED_HEIGHT if self._collapsed else BOX_DEFAULT_HEIGHT)

    @property
    def is_collapsed(self) -> bool:
        return self._collapsed

    def persistent_geometry(self) -> QRect:
        """Return the expanded geometry even while the box is collapsed."""
        size = self._expanded_size if self._collapsed else self.size()
        return QRect(self.canvas_position().toPoint(), size)

    def canvas_position(self) -> QPointF:
        proxy = self.graphicsProxyWidget()
        return proxy.pos() if proxy is not None else QPointF(self.pos())

    def move_on_canvas(self, position: QPointF) -> None:
        proxy = self.graphicsProxyWidget()
        if proxy is not None:
            proxy.setPos(position)
        else:
            self.move(position.toPoint())

    def canvas_point_from_global(self, point: QPoint) -> QPointF:
        proxy = self.graphicsProxyWidget()
        if proxy is not None and proxy.scene() is not None and proxy.scene().views():
            view = proxy.scene().views()[0]
            viewport_point = view.viewport().mapFromGlobal(point)
            return view.mapToScene(viewport_point)
        return QPointF(point)

    def raise_on_canvas(self) -> None:
        proxy = self.graphicsProxyWidget()
        if proxy is None or proxy.scene() is None:
            self.raise_()
            return
        highest = max((item.zValue() for item in proxy.scene().items()), default=0.0)
        proxy.setZValue(highest + 1.0)

    def set_collapsed(self, collapsed: bool, emit_signal: bool = True) -> None:
        changed = collapsed != self._collapsed
        if collapsed and not self._collapsed:
            self._expanded_size = self.size()
        self._collapsed = collapsed
        self.body.setVisible(not collapsed)
        self.resize_handle.setVisible(not collapsed)
        self.collapse_button.setText("▸" if collapsed else "▾")
        self.collapse_button.setToolTip("Expand box" if collapsed else "Collapse box")
        self.setProperty("collapsed", "true" if collapsed else "false")
        self.style().unpolish(self)
        self.style().polish(self)
        if collapsed:
            self.setMinimumHeight(BOX_COLLAPSED_HEIGHT)
            self.resize(self.width(), BOX_COLLAPSED_HEIGHT)
        elif changed:
            self.setMinimumHeight(BOX_MIN_HEIGHT)
            self.resize(self._expanded_size.expandedTo(self.minimumSize()))
        self.notify_geometry_changed()
        if changed and emit_signal:
            self.collapsed_changed.emit(self.category.key, collapsed)

    def notify_geometry_changed(self) -> None:
        self.geometry_changed.emit(self.category.key, self.persistent_geometry())

    def resizeEvent(self, event: QResizeEvent) -> None:  # noqa: N802
        super().resizeEvent(event)
        self.resize_handle.move(
            self.width() - BOX_RESIZE_HANDLE_SIZE,
            self.height() - BOX_RESIZE_HANDLE_SIZE,
        )
        self.resize_handle.raise_()

    def set_dark_theme(self, dark: bool) -> None:
        if dark == self._dark_theme:
            return
        self._dark_theme = dark
        self._render_cards()

    def _set_drop_active(self, active: bool) -> None:
        self.setProperty("dropActive", "true" if active else "false")
        self.style().unpolish(self)
        self.style().polish(self)

    def set_mods(self, mods: list[InstalledMod], rebuild_body: bool = True) -> None:
        self._mods = mods
        self._update_header()
        if rebuild_body:
            self._render_cards()

    def _update_header(self) -> None:
        total = len(self._mods)
        enabled = sum(1 for mod in self._mods if mod.enabled)
        attention = sum(1 for mod in self._mods if mod.status is not ModStatus.OK)
        noun = "mod" if total == 1 else "mods"
        self.stats_label.setText(f"{enabled} on / {total} {noun}")
        self.attention_label.setText(f"⚠ {attention}" if attention else "")
        if attention:
            self.attention_label.setToolTip(f"{attention} need attention")

    def _on_search(self, text: str) -> None:
        self._search = text.strip().casefold()
        self._render_cards()

    def _matches(self, mod: InstalledMod) -> bool:
        return not self._search or self._search in f"{mod.name} {mod.description}".casefold()

    def _clear_cards(self) -> None:
        while self.flow.count():
            item = self.flow.takeAt(0)
            widget = item.widget()
            if widget is not None:
                if isinstance(widget, ModCard):
                    widget.close_actions_menu()
                widget.setParent(None)
                widget.deleteLater()

    def _render_cards(self) -> None:
        self._clear_cards()
        shown = [mod for mod in self._mods if self._matches(mod)]
        self.empty_label.setVisible(not shown)
        for mod in shown:
            card = ModCard(mod, self._categories, self._thumbnails, self._dark_theme)
            card.enabled_toggled.connect(self._on_card_enabled)
            card.move_requested.connect(self.mod_moved)
            card.remove_requested.connect(self.mod_removed)
            card.details_requested.connect(self.mod_details)
            self.flow.addWidget(card)

    def _on_card_enabled(self, mod: InstalledMod) -> None:
        self._update_header()
        self.mod_enabled.emit(mod)
