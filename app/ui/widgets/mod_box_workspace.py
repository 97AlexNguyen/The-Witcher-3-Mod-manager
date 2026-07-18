from __future__ import annotations

import math

from PyQt6.QtCore import QLineF, QPoint, QPointF, QRect, QRectF, QSize, Qt, pyqtSignal
from PyQt6.QtGui import (
    QColor,
    QContextMenuEvent,
    QKeyEvent,
    QMouseEvent,
    QPainter,
    QPen,
    QResizeEvent,
    QWheelEvent,
)
from PyQt6.QtWidgets import (
    QAbstractButton,
    QApplication,
    QFrame,
    QGraphicsPixmapItem,
    QGraphicsProxyWidget,
    QGraphicsScene,
    QGraphicsView,
    QHBoxLayout,
    QLabel,
    QToolButton,
)

from app.ui.theme.tokens import (
    BOX_DEFAULT_WIDTH,
    DARK,
    LIGHT,
    SPACING_LG,
    SPACING_MD,
    SPACING_SM,
    SPACING_XL,
)
from app.ui.widgets.mod_category_box import CategoryBox
from app.ui.widgets.mod_card import ModCard


class ModBoxWorkspace(QGraphicsView):
    """Houdini-style node canvas for independently movable category boxes."""

    # Emitted on a canvas right-click: (global pos, scene pos). The page owns the
    # menu because it knows which category sits under the cursor and whether it
    # can be removed.
    context_menu_requested = pyqtSignal(QPoint, QPointF)
    # Emitted by the "+ Group" control. The page prompts for a name and creates
    # the category; placement is handled here so it never overlaps a box.
    create_category_requested = pyqtSignal()

    SCENE_HALF_EXTENT = 10000
    MIN_ZOOM = 0.35
    MAX_ZOOM = 2.50
    ZOOM_STEP = 1.15
    GRID_MINOR = 20
    GRID_MAJOR = 100

    def __init__(self, dark_theme: bool = True, parent=None) -> None:
        scene = QGraphicsScene(parent)
        super().__init__(scene, parent)
        self.setObjectName("boxWorkspace")
        self._boxes: dict[str, CategoryBox] = {}
        self._proxies: dict[str, QGraphicsProxyWidget] = {}
        self._dark_theme = dark_theme
        self._zoom = 1.0
        self._panning = False
        self._space_pressed = False
        self._pan_start = QPoint()
        self._dragged_box_key: str | None = None
        self._box_drag_start = QPointF()
        self._box_drag_origin = QPointF()
        self._card_drag_source: ModCard | None = None
        self._card_drag_press = QPointF()
        self._card_drag_hot_spot = QPointF()
        self._card_drag_item: QGraphicsPixmapItem | None = None
        self._card_drop_target: CategoryBox | None = None

        extent = self.SCENE_HALF_EXTENT
        self.scene().setSceneRect(-extent, -extent, extent * 2, extent * 2)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.BoundingRectViewportUpdate)
        self.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setMouseTracking(True)

        self._build_controls()
        self.set_dark_theme(dark_theme)

    def _build_controls(self) -> None:
        self.controls = QFrame(self)
        self.controls.setObjectName("canvasControls")
        row = QHBoxLayout(self.controls)
        row.setContentsMargins(SPACING_SM, SPACING_SM, SPACING_SM, SPACING_SM)
        row.setSpacing(SPACING_SM)

        pan_hint = QLabel("MMB / Space+drag: Pan")
        pan_hint.setObjectName("canvasHint")
        row.addWidget(pan_hint)

        self.zoom_out_button = self._control_button("−", "Zoom out", lambda: self.zoom_by(1 / self.ZOOM_STEP))
        row.addWidget(self.zoom_out_button)
        self.zoom_label = QLabel("100%")
        self.zoom_label.setObjectName("canvasZoomLabel")
        self.zoom_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.zoom_label.setFixedWidth(52)
        row.addWidget(self.zoom_label)
        self.zoom_in_button = self._control_button("+", "Zoom in", lambda: self.zoom_by(self.ZOOM_STEP))
        row.addWidget(self.zoom_in_button)
        self.fit_button = self._control_button("Fit", "Frame all boxes", self.frame_all)
        self.fit_button.setFixedWidth(44)
        row.addWidget(self.fit_button)
        self.arrange_button = self._control_button(
            "Arrange", "Automatically arrange boxes in a compact grid", self.arrange_boxes
        )
        self.arrange_button.setFixedWidth(68)
        row.addWidget(self.arrange_button)
        self.add_group_button = self._control_button(
            "+ Group", "Create a new category box", self.create_category_requested.emit
        )
        self.add_group_button.setFixedWidth(72)
        row.addWidget(self.add_group_button)
        self.controls.adjustSize()
        self.controls.raise_()

    def _control_button(self, text: str, tooltip: str, callback) -> QToolButton:
        button = QToolButton(self.controls)
        button.setObjectName("canvasControlButton")
        button.setText(text)
        button.setToolTip(tooltip)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setFixedSize(32, 32)
        button.clicked.connect(callback)
        return button

    def add_box(self, box: CategoryBox, position: QPointF | None = None) -> None:
        # Compute placement before registering the box so it is measured against
        # the *existing* boxes only and never against itself.
        if position is None:
            position = self.free_position_for(box.size())
        self._boxes[box.category.key] = box
        proxy = self.scene().addWidget(box)
        self._proxies[box.category.key] = proxy
        proxy.setPos(position)
        box.geometry_changed.connect(self._on_box_geometry_changed)

    def free_position_for(self, size: QSize, gap: int = SPACING_LG) -> QPointF:
        """Find a spot for a new box that sits near the existing cluster without
        overlapping any of them.

        Auto-created categories (installing a mod under a new category) must land
        somewhere visible and clear of boxes the user has arranged by hand. We
        scan a grid anchored to the top-left of the current cluster, filling the
        first free slot; empty rows below the cluster guarantee a spot exists.
        """
        occupied = [
            QRectF(self.box_geometry(key))
            for key in self._boxes
            if self.box_geometry(key).isValid()
        ]
        width = float(size.width())
        height = float(size.height())

        def snap(point: QPointF) -> QPointF:
            return QPointF(round(point.x() / 4) * 4, round(point.y() / 4) * 4)

        if not occupied:
            return snap(QPointF(SPACING_LG, SPACING_LG))

        def is_free(candidate: QRectF) -> bool:
            padded = candidate.adjusted(-gap / 2, -gap / 2, gap / 2, gap / 2)
            return not any(padded.intersects(rect) for rect in occupied)

        union = occupied[0]
        for rect in occupied[1:]:
            union = union.united(rect)
        step_x = width + gap
        step_y = height + gap
        columns = max(1, int((union.width() + gap) // step_x) + 1)
        for row in range(200):
            for column in range(columns + 1):
                candidate = QRectF(
                    union.left() + column * step_x,
                    union.top() + row * step_y,
                    width,
                    height,
                )
                if is_free(candidate):
                    return snap(candidate.topLeft())
        return snap(QPointF(union.right() + gap, union.top()))

    def remove_box(self, category_key: str) -> None:
        """Remove a box from the canvas (its category no longer has any mods)."""
        proxy = self._proxies.pop(category_key, None)
        box = self._boxes.pop(category_key, None)
        if proxy is not None:
            self.scene().removeItem(proxy)
            proxy.deleteLater()
        if box is not None:
            box.deleteLater()
        self.scene().update()

    def box_count(self) -> int:
        return len(self._boxes)

    def box_geometry(self, category_key: str) -> QRect:
        box = self._boxes.get(category_key)
        proxy = self._proxies.get(category_key)
        if box is None or proxy is None:
            return QRect()
        return QRect(proxy.pos().toPoint(), box.size())

    def set_box_geometry(self, category_key: str, geometry: QRect) -> None:
        box = self._boxes.get(category_key)
        proxy = self._proxies.get(category_key)
        if box is None or proxy is None or not geometry.isValid():
            return
        proxy.setPos(QPointF(geometry.topLeft()))
        box.resize(
            max(box.minimumWidth(), geometry.width()),
            max(box.minimumHeight(), geometry.height()),
        )

    def _on_box_geometry_changed(self, _category_key: str, _geometry: QRect) -> None:
        self.scene().update()

    def refresh_extent(self) -> None:
        self.scene().update()

    def set_dark_theme(self, dark: bool) -> None:
        self._dark_theme = dark
        colors = DARK if dark else LIGHT
        self.setBackgroundBrush(QColor(colors.background))
        self.viewport().update()

    # -- camera ---------------------------------------------------------- #

    @property
    def zoom_factor(self) -> float:
        return self._zoom

    def camera_center(self) -> QPointF:
        return self.mapToScene(self.viewport().rect().center())

    def restore_view(self, zoom: float, center: QPointF) -> None:
        self.set_zoom(zoom)
        self.centerOn(center)

    def set_zoom(self, zoom: float) -> None:
        zoom = max(self.MIN_ZOOM, min(self.MAX_ZOOM, float(zoom)))
        center = self.camera_center()
        self.resetTransform()
        self.scale(zoom, zoom)
        self._zoom = zoom
        self.centerOn(center)
        self._update_zoom_label()

    def zoom_by(self, factor: float) -> None:
        target = max(self.MIN_ZOOM, min(self.MAX_ZOOM, self._zoom * factor))
        applied = target / self._zoom
        if abs(applied - 1.0) < 0.0001:
            return
        self.scale(applied, applied)
        self._zoom = target
        self._update_zoom_label()

    def reset_view(self) -> None:
        self.resetTransform()
        self._zoom = 1.0
        bounds = self.scene().itemsBoundingRect()
        self.centerOn(bounds.center() if not bounds.isEmpty() else QPointF())
        self._update_zoom_label()

    def frame_all(self) -> None:
        bounds = self.scene().itemsBoundingRect()
        if bounds.isEmpty():
            self.reset_view()
            return
        bounds = bounds.adjusted(-SPACING_LG, -SPACING_LG, SPACING_LG, SPACING_LG)
        self.fitInView(bounds, Qt.AspectRatioMode.KeepAspectRatio)
        fitted = self.transform().m11()
        if fitted > self.MAX_ZOOM:
            self.resetTransform()
            self.scale(self.MAX_ZOOM, self.MAX_ZOOM)
            fitted = self.MAX_ZOOM
        elif fitted < self.MIN_ZOOM:
            self.resetTransform()
            self.scale(self.MIN_ZOOM, self.MIN_ZOOM)
            fitted = self.MIN_ZOOM
        self._zoom = fitted
        self.centerOn(bounds.center())
        self._update_zoom_label()

    def arrange_boxes(self) -> None:
        """Pack boxes into non-overlapping rows near the current camera position."""
        if not self._boxes:
            return

        target_width = max(
            BOX_DEFAULT_WIDTH * 2 + SPACING_MD + 2 * SPACING_LG,
            self.viewport().width(),
        )
        center = self.camera_center()
        start_x = round((center.x() - target_width / 2) / 4) * 4
        start_y = round((center.y() - self.viewport().height() / 2) / 4) * 4
        right_edge = start_x + target_width
        x = start_x
        y = start_y
        row_height = 0

        for key, box in self._boxes.items():
            proxy = self._proxies[key]
            width = box.width()
            height = box.height()
            if x > start_x and x + width > right_edge:
                x = start_x
                y += row_height + SPACING_MD
                row_height = 0
            proxy.setPos(QPointF(x, y))
            box.notify_geometry_changed()
            x += width + SPACING_MD
            row_height = max(row_height, height)

        self.frame_all()

    def _update_zoom_label(self) -> None:
        self.zoom_label.setText(f"{round(self._zoom * 100):d}%")

    # -- input ----------------------------------------------------------- #

    def wheelEvent(self, event: QWheelEvent) -> None:  # noqa: N802
        delta = event.angleDelta().y()
        if delta == 0:
            super().wheelEvent(event)
            return
        self.zoom_by(self.ZOOM_STEP if delta > 0 else 1 / self.ZOOM_STEP)
        event.accept()

    def contextMenuEvent(self, event: QContextMenuEvent) -> None:  # noqa: N802
        scene_position = self.mapToScene(event.pos())
        self.context_menu_requested.emit(event.globalPos(), scene_position)
        event.accept()

    def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        if event.key() == Qt.Key.Key_Escape and self._card_drag_source is not None:
            self._cancel_card_drag()
            event.accept()
            return
        if event.key() == Qt.Key.Key_Space and not event.isAutoRepeat():
            self._space_pressed = True
            self.viewport().setCursor(Qt.CursorShape.OpenHandCursor)
            event.accept()
            return
        super().keyPressEvent(event)

    def keyReleaseEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        if event.key() == Qt.Key.Key_Space and not event.isAutoRepeat():
            self._space_pressed = False
            if not self._panning:
                self.viewport().unsetCursor()
            event.accept()
            return
        super().keyReleaseEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        wants_pan = event.button() == Qt.MouseButton.MiddleButton or (
            event.button() == Qt.MouseButton.LeftButton and self._space_pressed
        )
        if wants_pan:
            self._panning = True
            self._pan_start = event.position().toPoint()
            self.viewport().setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
            return
        if event.button() == Qt.MouseButton.LeftButton:
            scene_position = self.mapToScene(event.position().toPoint())
            dragged = self._box_at_header(scene_position)
            if dragged is not None:
                key, box = dragged
                self._dragged_box_key = key
                self._box_drag_start = scene_position
                self._box_drag_origin = self._proxies[key].pos()
                box.raise_on_canvas()
                box.set_dragging(True)
                event.accept()
                return
            card = self._card_at_drag_point(scene_position)
            if card is not None:
                self._card_drag_source = card
                self._card_drag_press = event.position()
                proxy = self._proxies.get(card.mod.category_key)
                embedded = proxy.widget() if proxy is not None else None
                if embedded is not None:
                    local = proxy.mapFromScene(scene_position).toPoint()
                    self._card_drag_hot_spot = QPointF(card.mapFrom(embedded, local))
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if self._dragged_box_key is not None:
            key = self._dragged_box_key
            box = self._boxes[key]
            current = self.mapToScene(event.position().toPoint())
            self._proxies[key].setPos(self._box_drag_origin + current - self._box_drag_start)
            box.notify_geometry_changed()
            event.accept()
            return
        if self._panning:
            current = event.position().toPoint()
            delta = current - self._pan_start
            self._pan_start = current
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
            event.accept()
            return
        if self._card_drag_source is not None:
            if not (event.buttons() & Qt.MouseButton.LeftButton):
                self._cancel_card_drag()
                super().mouseMoveEvent(event)
                return
            distance = (event.position() - self._card_drag_press).manhattanLength()
            if self._card_drag_item is None and distance >= QApplication.startDragDistance():
                self._begin_card_drag(event.position().toPoint())
            if self._card_drag_item is not None:
                self._move_card_drag(event.position().toPoint())
                event.accept()
                return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if self._dragged_box_key is not None and event.button() == Qt.MouseButton.LeftButton:
            box = self._boxes[self._dragged_box_key]
            self._dragged_box_key = None
            box.set_dragging(False)
            box.notify_geometry_changed()
            event.accept()
            return
        if self._panning and event.button() in (Qt.MouseButton.MiddleButton, Qt.MouseButton.LeftButton):
            self._panning = False
            self.viewport().setCursor(
                Qt.CursorShape.OpenHandCursor if self._space_pressed else Qt.CursorShape.ArrowCursor
            )
            event.accept()
            return
        if self._card_drag_source is not None and event.button() == Qt.MouseButton.LeftButton:
            if self._card_drag_item is not None:
                target = self._card_drop_target
                identity = self._card_drag_source.mod.identity
                self._cancel_card_drag()
                if target is not None:
                    target.mod_dropped.emit(identity, target.category.key)
                event.accept()
                return
            source = self._card_drag_source
            self._card_drag_source = None
            source.cancel_pending_drag()
            source.selection_requested.emit(source.mod)
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def _begin_card_drag(self, viewport_position: QPoint) -> None:
        card = self._card_drag_source
        if card is None:
            return
        card.cancel_pending_drag()
        drag_item = self.scene().addPixmap(card.grab())
        drag_item.setOpacity(0.72)
        drag_item.setZValue(max((item.zValue() for item in self.scene().items()), default=0.0) + 1.0)
        self._card_drag_item = drag_item
        card.setCursor(Qt.CursorShape.ClosedHandCursor)
        self._move_card_drag(viewport_position)

    def _move_card_drag(self, viewport_position: QPoint) -> None:
        if self._card_drag_item is None or self._card_drag_source is None:
            return
        self._auto_pan_for_card_drag(viewport_position)
        scene_position = self.mapToScene(viewport_position)
        self._card_drag_item.setPos(scene_position - self._card_drag_hot_spot)
        target = self._box_at_scene_position(scene_position)
        if target is not None and target.category.key == self._card_drag_source.mod.category_key:
            target = None
        self._set_card_drop_target(target)
        self.viewport().setCursor(
            Qt.CursorShape.DragMoveCursor if target is not None else Qt.CursorShape.ForbiddenCursor
        )

    def _auto_pan_for_card_drag(self, position: QPoint) -> None:
        """Keep destinations reachable when a card is dragged near a viewport edge."""
        edge = SPACING_XL
        step = SPACING_MD
        horizontal = -step if position.x() < edge else step if position.x() > self.viewport().width() - edge else 0
        vertical = -step if position.y() < edge else step if position.y() > self.viewport().height() - edge else 0
        if horizontal:
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() + horizontal)
        if vertical:
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() + vertical)

    def _set_card_drop_target(self, target: CategoryBox | None) -> None:
        if target is self._card_drop_target:
            return
        if self._card_drop_target is not None:
            self._card_drop_target._set_drop_active(False)
        self._card_drop_target = target
        if target is not None:
            target._set_drop_active(True)

    def _cancel_card_drag(self) -> None:
        source = self._card_drag_source
        self._set_card_drop_target(None)
        if self._card_drag_item is not None:
            self.scene().removeItem(self._card_drag_item)
            self._card_drag_item = None
        self._card_drag_source = None
        if source is not None:
            source.cancel_pending_drag()
            source.setCursor(Qt.CursorShape.OpenHandCursor)
        self.viewport().setCursor(
            Qt.CursorShape.OpenHandCursor if self._space_pressed else Qt.CursorShape.ArrowCursor
        )

    def _card_at_drag_point(self, scene_position: QPointF) -> ModCard | None:
        """Find a card while leaving its toggle and overflow button clickable."""
        for key, box in self._boxes_front_to_back():
            proxy = self._proxies[key]
            local = proxy.mapFromScene(scene_position).toPoint()
            if not box.rect().contains(local):
                continue
            widget = box.childAt(local)
            while widget is not None and widget is not box:
                if isinstance(widget, QAbstractButton):
                    return None
                if isinstance(widget, ModCard):
                    return widget
                widget = widget.parentWidget()
        return None

    def _box_at_scene_position(self, scene_position: QPointF) -> CategoryBox | None:
        for key, box in self._boxes_front_to_back():
            if box.rect().contains(self._proxies[key].mapFromScene(scene_position).toPoint()):
                return box
        return None

    def box_key_at(self, scene_position: QPointF) -> str | None:
        """Return the key of the front-most box under a scene point, if any."""
        for key, box in self._boxes_front_to_back():
            if box.rect().contains(self._proxies[key].mapFromScene(scene_position).toPoint()):
                return key
        return None

    def _boxes_front_to_back(self) -> list[tuple[str, CategoryBox]]:
        boxes_back_to_front = tuple(self._boxes.items())
        ordered = sorted(
            enumerate(boxes_back_to_front),
            key=lambda entry: (self._proxies[entry[1][0]].zValue(), entry[0]),
            reverse=True,
        )
        return [box_entry for _index, box_entry in ordered]

    def _box_at_header(self, scene_position: QPointF) -> tuple[str, CategoryBox] | None:
        """Return the box whose header drag zone contains a scene position."""
        for key, box in self._boxes_front_to_back():
            proxy = self._proxies[key]
            if box.point_in_drag_zone(proxy.mapFromScene(scene_position).toPoint()):
                return key, box
        return None

    # -- presentation ---------------------------------------------------- #

    def resizeEvent(self, event: QResizeEvent) -> None:  # noqa: N802
        super().resizeEvent(event)
        self.controls.adjustSize()
        self.controls.move(
            SPACING_MD,
            self.height() - self.controls.height() - SPACING_MD,
        )
        self.controls.raise_()

    def drawBackground(self, painter: QPainter, rect: QRectF) -> None:  # noqa: N802
        super().drawBackground(painter, rect)
        colors = DARK if self._dark_theme else LIGHT
        minor_color = QColor(colors.outline_variant)
        minor_color.setAlpha(90 if self._dark_theme else 70)
        major_color = QColor(colors.outline)
        major_color.setAlpha(110 if self._dark_theme else 80)

        self._draw_grid(painter, rect, self.GRID_MINOR, QPen(minor_color, 0))
        self._draw_grid(painter, rect, self.GRID_MAJOR, QPen(major_color, 0))

    @staticmethod
    def _draw_grid(painter: QPainter, rect: QRectF, step: int, pen: QPen) -> None:
        left = math.floor(rect.left() / step) * step
        top = math.floor(rect.top() / step) * step
        lines: list[QLineF] = []
        x = left
        while x <= rect.right():
            lines.append(QLineF(x, rect.top(), x, rect.bottom()))
            x += step
        y = top
        while y <= rect.bottom():
            lines.append(QLineF(rect.left(), y, rect.right(), y))
            y += step
        painter.setPen(pen)
        painter.drawLines(lines)
