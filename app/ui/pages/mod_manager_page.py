from __future__ import annotations

import json

from PyQt6.QtCore import QByteArray, QPoint, QPointF, QRect, QSettings, Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QColor, QDragEnterEvent, QDropEvent
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QMenu,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from app.data import (
    load_category_catalog,
    make_mock_categories,
    make_mock_mods,
    palette_color_key,
    slugify,
)
from app.domain import Category, InstalledMod
from app.ui.models import InstalledModListModel, InstalledModRoles
from app.ui.services import ThumbnailProvider
from app.ui.theme.tokens import SPACING_LG, SPACING_MD, SPACING_SM
from app.ui.widgets import CategoryBox, ModBoxWorkspace, ModDetailPanel


class ModManagerPage(QWidget):
    archives_dropped = pyqtSignal(list)

    ARCHIVE_SUFFIXES = (".zip", ".7z", ".rar")
    NOTICE_TIMEOUT_MS = 6000
    def __init__(self, settings: QSettings, theme_manager=None, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("pageSurface")
        self.setAcceptDrops(True)
        self._settings = settings
        self._theme_manager = theme_manager
        self._dark_theme = bool(theme_manager.is_dark) if theme_manager is not None else True

        self._categories = make_mock_categories()
        # "all" is a filter concept from the old flat list; a box grid groups by real
        # categories, so every mod lands in exactly one box.
        self._box_categories = [c for c in self._categories if c.key != "all"]
        # Full Nexus taxonomy the user can spawn boxes from; layout (which boxes
        # exist) stays separate from this catalog of available categories.
        self._catalog = load_category_catalog()
        # Boxes created at runtime (from the catalog or custom) that must be
        # recreated on the next launch — the startup mock set does not cover them.
        self._extra_categories: list[Category] = []
        self.mod_model = InstalledModListModel(make_mock_mods(), self)
        self.thumbnails = ThumbnailProvider()

        self.boxes: dict[str, CategoryBox] = {}

        self._notice_timer = QTimer(self)
        self._notice_timer.setSingleShot(True)
        self._notice_timer.setInterval(self.NOTICE_TIMEOUT_MS)
        self._notice_timer.timeout.connect(self._hide_notice)

        self._build_ui()
        self._connect()
        self._refresh_boxes(rebuild_body=True)
        self._restore_state()

    # -- construction ------------------------------------------------------ #

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING_LG, SPACING_MD, SPACING_LG, SPACING_LG)
        layout.setSpacing(SPACING_MD)

        heading = QHBoxLayout()
        heading.setSpacing(SPACING_SM)
        title = QLabel("MOD BOXES")
        title.setProperty("class", "headline-sm")
        heading.addWidget(title)
        subtitle = QLabel("Wheel: zoom · MMB/Space+drag: pan · ⠿ move box · ◢ resize box")
        subtitle.setProperty("class", "muted")
        heading.addWidget(subtitle)
        heading.addStretch()
        drop_hint = QLabel("Drop .zip, .7z, or .rar files here to install")
        drop_hint.setProperty("class", "muted")
        heading.addWidget(drop_hint)
        layout.addLayout(heading)

        self.notice_label = QLabel()
        self.notice_label.setObjectName("noticeBar")
        self.notice_label.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.notice_label.setWordWrap(True)
        self.notice_label.hide()
        layout.addWidget(self.notice_label)

        self.box_workspace = ModBoxWorkspace(self._dark_theme)
        for category in list(self._box_categories):
            self._install_box(category)

        self.detail_panel = ModDetailPanel(self._categories)
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setObjectName("modWorkspaceSplitter")
        self.splitter.setChildrenCollapsible(False)
        self.splitter.setHandleWidth(1)
        self.splitter.addWidget(self.box_workspace)
        self.splitter.addWidget(self.detail_panel)
        self.splitter.setCollapsible(0, False)
        self.splitter.setCollapsible(1, True)
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 0)
        self.splitter.setSizes([1000, 340])
        layout.addWidget(self.splitter, 1)

    def _install_box(self, category: Category, position: QPointF | None = None) -> CategoryBox:
        """Create, wire, and place a box for ``category`` on the canvas."""
        box = CategoryBox(category, self._box_categories, self.thumbnails, self._dark_theme)
        box.mod_dropped.connect(self._on_mod_dropped)
        box.mod_enabled.connect(self._on_mod_enabled)
        box.mod_moved.connect(self._set_mod_category)
        box.mod_removed.connect(self._request_remove)
        box.mod_details.connect(self._show_details)
        box.mod_selected.connect(self._show_details)
        box.collapsed_changed.connect(self._on_box_collapsed)
        self.boxes[category.key] = box
        self.box_workspace.add_box(box, position)
        box.set_mods(self._mods_in(category.key), rebuild_body=True)
        return box

    def _connect(self) -> None:
        self.box_workspace.context_menu_requested.connect(self._show_canvas_menu)
        self.detail_panel.category_changed.connect(self._set_mod_category)
        self.mod_model.dataChanged.connect(self._on_model_data_changed)
        self.mod_model.rowsInserted.connect(self._on_membership_changed)
        self.mod_model.rowsRemoved.connect(self._on_membership_changed)
        self.mod_model.modelReset.connect(self._on_membership_changed)
        if self._theme_manager is not None:
            self._theme_manager.theme_changed.connect(self._on_theme_changed)

    def _restore_state(self) -> None:
        self._restore_custom_boxes()

        state = self._settings.value("mod_manager/detail_splitter")
        if isinstance(state, QByteArray):
            self.splitter.restoreState(state)

        for key in self.boxes:
            geometry = self._settings.value(f"mod_manager/box_geometry/{key}")
            if isinstance(geometry, QRect):
                self.box_workspace.set_box_geometry(key, geometry)
            color_value = self._settings.value(f"mod_manager/box_color/{key}")
            if isinstance(color_value, str):
                color = QColor(color_value)
                if color.isValid():
                    self.boxes[key].set_custom_color(color)

        collapsed = self._settings.value("mod_manager/collapsed_boxes", [])
        if isinstance(collapsed, str):
            collapsed = [collapsed]
        if isinstance(collapsed, list):
            collapsed_keys = set(collapsed)
            for key, box in self.boxes.items():
                box.set_collapsed(key in collapsed_keys, emit_signal=False)

        center = self._settings.value("mod_manager/canvas_center")
        try:
            zoom = float(self._settings.value("mod_manager/canvas_zoom", 1.0))
        except (TypeError, ValueError):
            zoom = 1.0
        if isinstance(center, QPointF):
            self.box_workspace.restore_view(zoom, center)
        else:
            QTimer.singleShot(0, self.box_workspace.reset_view)

    def _restore_custom_boxes(self) -> None:
        """Recreate boxes the user added in a previous session."""
        raw = self._settings.value("mod_manager/custom_boxes")
        if not isinstance(raw, str):
            return
        try:
            payload = json.loads(raw)
        except (TypeError, ValueError):
            return
        if not isinstance(payload, list):
            return
        for entry in payload:
            if not isinstance(entry, dict):
                continue
            key = entry.get("key")
            if not isinstance(key, str) or key in self.boxes:
                continue
            name = entry.get("name") if isinstance(entry.get("name"), str) else key
            color_key = entry.get("color_key") if isinstance(entry.get("color_key"), str) else "neutral"
            category = Category(key, name, color_key)
            self._register_category(category)
            self._install_box(category)

    def _persist_custom_boxes(self) -> None:
        payload = [
            {"key": c.key, "name": c.name, "color_key": c.color_key}
            for c in self._extra_categories
        ]
        self._settings.setValue("mod_manager/custom_boxes", json.dumps(payload))

    # -- group creation ---------------------------------------------------- #

    def _show_canvas_menu(self, global_pos: QPoint, scene_pos: QPointF) -> None:
        """Offer catalog categories (not yet placed) and a custom group option."""
        menu = QMenu(self)
        available = [c for c in self._catalog if c.key not in self.boxes]
        if available:
            add_menu = menu.addMenu("Add group")
            for category in available:
                action = add_menu.addAction(category.name)
                action.triggered.connect(
                    lambda _checked=False, c=category, p=scene_pos: self._add_group(c, p)
                )
        custom_action = menu.addAction("Custom group…")
        custom_action.triggered.connect(
            lambda _checked=False, p=scene_pos: self._create_custom_group(p)
        )
        menu.exec(global_pos)

    def _add_group(self, category: Category, position: QPointF) -> None:
        if category.key in self.boxes:
            return
        self._register_category(category)
        self._install_box(category, position)
        # Rebuild bodies so every card's "move to" menu learns the new target.
        self._refresh_boxes(rebuild_body=True)
        self._persist_custom_boxes()

    def _create_custom_group(self, position: QPointF) -> None:
        name, ok = QInputDialog.getText(self, "New group", "Group name:")
        if not ok:
            return
        name = name.strip()
        if not name:
            return
        key = self._unique_key(slugify(name))
        category = Category(key, name, palette_color_key(len(self.boxes)))
        self._register_category(category)
        self._install_box(category, position)
        self._refresh_boxes(rebuild_body=True)
        self._persist_custom_boxes()

    def _register_category(self, category: Category) -> None:
        """Track a runtime category so cards, dropdowns, and restore see it."""
        self._extra_categories.append(category)
        self._box_categories.append(category)
        self._categories.append(category)

    def _unique_key(self, base: str) -> str:
        key = base
        suffix = 2
        while key in self.boxes:
            key = f"{base}-{suffix}"
            suffix += 1
        return key

    # -- data helpers ------------------------------------------------------ #

    def _mods_in(self, category_key: str) -> list[InstalledMod]:
        return [mod for mod in self.mod_model.mods if mod.category_key == category_key]

    def _mod_for_identity(self, identity: str) -> InstalledMod | None:
        for mod in self.mod_model.mods:
            if mod.identity == identity:
                return mod
        return None

    def _refresh_boxes(self, rebuild_body: bool) -> None:
        for key, box in self.boxes.items():
            box.set_mods(self._mods_in(key), rebuild_body=rebuild_body)

    # -- mod mutations ----------------------------------------------------- #

    def _on_mod_dropped(self, identity: str, target_key: str) -> None:
        mod = self._mod_for_identity(identity)
        if mod is not None:
            self._set_mod_category(mod, target_key)

    def _set_mod_category(self, mod: InstalledMod, category_key: str) -> None:
        if mod.category_key == category_key:
            return
        self.mod_model.set_category(mod, category_key)  # emits dataChanged -> refresh

    def _on_mod_enabled(self, mod: InstalledMod) -> None:
        row = self.mod_model.row_for(mod)
        if row < 0:
            return
        index = self.mod_model.index(row, 0)
        self.mod_model.setData(index, mod.enabled, InstalledModRoles.ENABLED)

    def _request_remove(self, mod: InstalledMod) -> None:
        # Removal un-merges a mod from game config; that flow is not wired yet.
        self._show_notice(f"Removing '{mod.name}' will be connected in a later phase.")

    def _show_details(self, mod: InstalledMod) -> None:
        for box in self.boxes.values():
            box.set_selected_mod(mod.identity)
        self.detail_panel.show_selection([mod])
        # Make sure the detail pane is visible if the user had collapsed it.
        sizes = self.splitter.sizes()
        if len(sizes) == 2 and sizes[1] == 0:
            total = sum(sizes) or 1000
            self.splitter.setSizes([int(total * 0.72), int(total * 0.28)])

    # -- model reactions --------------------------------------------------- #

    def _on_model_data_changed(self, top_left, bottom_right, roles=None) -> None:
        roles = roles or []
        membership_changed = (not roles) or (InstalledModRoles.CATEGORY_COLOR in roles)
        # On an enable-only change, refresh headers only so the clicked card survives.
        self._refresh_boxes(rebuild_body=membership_changed)
        # Keep the detail panel in step with whichever mod it is showing.
        mod = self.detail_panel.current_mod
        if mod is not None:
            for row in range(top_left.row(), bottom_right.row() + 1):
                if self.mod_model.mod_at(row) is mod:
                    self.detail_panel.show_selection([mod])
                    break

    def _on_membership_changed(self, *_args) -> None:
        self._refresh_boxes(rebuild_body=True)

    def _on_theme_changed(self, dark: bool) -> None:
        self._dark_theme = dark
        self.box_workspace.set_dark_theme(dark)
        for box in self.boxes.values():
            box.set_dark_theme(dark)

    def _on_box_collapsed(self, _category_key: str, _collapsed: bool) -> None:
        self.box_workspace.refresh_extent()

    # -- notice bar -------------------------------------------------------- #

    def _show_notice(self, text: str) -> None:
        self.notice_label.setText(text)
        self.notice_label.show()
        self._notice_timer.start()

    def _hide_notice(self) -> None:
        self._notice_timer.stop()
        self.notice_label.hide()

    # -- archive drop ------------------------------------------------------ #

    def _archive_paths(self, event) -> list[str]:
        mime = event.mimeData()
        if not mime.hasUrls():
            return []
        return [
            url.toLocalFile()
            for url in mime.urls()
            if url.isLocalFile() and url.toLocalFile().lower().endswith(self.ARCHIVE_SUFFIXES)
        ]

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:  # noqa: N802
        if self._archive_paths(event):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event) -> None:  # noqa: N802
        if self._archive_paths(event):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent) -> None:  # noqa: N802
        paths = self._archive_paths(event)
        if not paths:
            event.ignore()
            return
        event.acceptProposedAction()
        self.archives_dropped.emit(paths)
        count = len(paths)
        self._show_notice(
            f"{count} archive{'s' if count != 1 else ''} received. "
            "The install flow will be connected in a later phase."
        )

    # -- persistence ------------------------------------------------------- #

    def save_state(self) -> None:
        self._persist_custom_boxes()
        self._settings.setValue("mod_manager/detail_splitter", self.splitter.saveState())
        self._settings.setValue("mod_manager/canvas_zoom", self.box_workspace.zoom_factor)
        self._settings.setValue("mod_manager/canvas_center", self.box_workspace.camera_center())
        for key, box in self.boxes.items():
            self._settings.setValue(f"mod_manager/box_geometry/{key}", box.persistent_geometry())
            color = box.custom_color
            if color is not None:
                self._settings.setValue(
                    f"mod_manager/box_color/{key}",
                    color.name(QColor.NameFormat.HexArgb),
                )
        self._settings.setValue(
            "mod_manager/collapsed_boxes",
            [key for key, box in self.boxes.items() if box.is_collapsed],
        )
