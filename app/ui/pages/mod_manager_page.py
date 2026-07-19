from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import (
    QByteArray,
    QPointF,
    QRect,
    QSettings,
    Qt,
    QThreadPool,
    QTimer,
    pyqtSignal,
)
from PyQt6.QtGui import QColor, QCursor, QDragEnterEvent, QDropEvent
from PyQt6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMenu,
    QMessageBox,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from app.config import CheckLevel, load_config, validate_game_path
from app.apis.nexus_metadata import NexusLookupError, lookup_archive_metadata
from app.apis.nexus_thumbnail import cache_thumbnail
from app.data import (
    UNCATEGORIZED_CATEGORY_NAME,
    load_category_catalog,
    palette_color_key,
    preferred_install_category_name,
    slugify,
)
from app.domain import Category, InstalledMod
from app.install import (
    InstallError,
    UninstallError,
    inspect_archive,
    parse_archive_name,
    uninstall_mod,
)
from app.manifest import Manifest, ManifestStore
from app.ui.dialogs import (
    InstallDecision,
    InstallProgressDialog,
    InstallReviewDialog,
    InstallWorker,
)
from app.ui.models import InstalledModListModel, InstalledModRoles
from app.ui.services import ThumbnailProvider
from app.ui.theme.tokens import SPACING_LG, SPACING_MD, SPACING_SM
from app.ui.widgets import CategoryBox, ModBoxWorkspace, ModDetailPanel

# Categories are derived from the installed mods, not a fixed list. A category
# box exists exactly when at least one mod is filed under it — installing a mod
# creates the category selected from Nexus metadata, and moving the last mod
# out of a category removes it. "Uncategorized" is the one permanent home that
# always exists, even when empty, so a mod always has somewhere to land.
UNCATEGORIZED = Category(
    "uncategorized", UNCATEGORIZED_CATEGORY_NAME, "amber", built_in=True
)


class ModManagerPage(QWidget):
    archives_dropped = pyqtSignal(list)

    ARCHIVE_SUFFIXES = (".zip", ".7z", ".rar")
    NOTICE_TIMEOUT_MS = 6000
    MANIFEST_SAVE_DEBOUNCE_MS = 300

    def __init__(
        self,
        settings: QSettings,
        theme_manager=None,
        parent=None,
        *,
        manifest_path=None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("pageSurface")
        self.setAcceptDrops(True)
        self._settings = settings
        self._theme_manager = theme_manager
        self._dark_theme = bool(theme_manager.is_dark) if theme_manager is not None else True

        # The manifest is the source of truth for installed mods. Take the write
        # lock (a second instance stays read-only), then load — a fresh install
        # starts empty (only the permanent Uncategorized box).
        self._store = ManifestStore(manifest_path)
        self._store.acquire()
        self._readonly_warned = False
        manifest = self._store.load(seed=self._seed_manifest)
        self.mod_model = InstalledModListModel(list(manifest.mods), self)
        self.thumbnails = ThumbnailProvider()

        # Metadata (name/colour) for every category that currently has a box.
        # Rebuilt from the manifest and kept pruned to the active set.
        self._registry: dict[str, Category] = self._build_registry(manifest.categories)
        # Keys of user-created categories, which keep their box even when empty
        # (until the user removes them). Seeded from the manifest so hand-made
        # empty categories survive a restart.
        self._pinned_keys: set[str] = {
            category.key
            for category in manifest.categories
            if category.user_created and category.key != UNCATEGORIZED.key
        }
        # Live lists the boxes and detail panel hold by reference; kept in sync
        # with the active category set so their "move to" menus stay current.
        self._categories: list[Category] = []
        self._box_categories: list[Category] = []

        self._manifest_save_timer = QTimer(self)
        self._manifest_save_timer.setSingleShot(True)
        self._manifest_save_timer.setInterval(self.MANIFEST_SAVE_DEBOUNCE_MS)
        self._manifest_save_timer.timeout.connect(self._persist_manifest)

        self.boxes: dict[str, CategoryBox] = {}

        self._notice_timer = QTimer(self)
        self._notice_timer.setSingleShot(True)
        self._notice_timer.setInterval(self.NOTICE_TIMEOUT_MS)
        self._notice_timer.timeout.connect(self._hide_notice)

        self._build_ui()
        self._connect()
        self._reconcile_boxes(rebuild_body=True)
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
        # Categories are usually mod-driven, but the user may also create one by
        # hand (the "+ Group" control or the canvas right-click menu). A hand-made
        # category is pinned so its empty box survives the next reconcile.

        self.detail_panel = ModDetailPanel(self._box_categories)
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
        self.box_workspace.create_category_requested.connect(self._prompt_create_category)
        self.box_workspace.context_menu_requested.connect(self._show_canvas_menu)
        self.detail_panel.category_changed.connect(self._set_mod_category)
        self.mod_model.dataChanged.connect(self._on_model_data_changed)
        self.mod_model.rowsInserted.connect(self._on_membership_changed)
        self.mod_model.rowsRemoved.connect(self._on_membership_changed)
        self.mod_model.modelReset.connect(self._on_membership_changed)
        # Any change to mod state (toggle, recategorize, priority) persists to the
        # manifest, debounced so a burst of edits coalesces into one atomic write.
        self.mod_model.dataChanged.connect(self._schedule_manifest_save)
        self.mod_model.rowsInserted.connect(self._schedule_manifest_save)
        self.mod_model.rowsRemoved.connect(self._schedule_manifest_save)
        self.mod_model.modelReset.connect(self._schedule_manifest_save)
        if self._theme_manager is not None:
            self._theme_manager.theme_changed.connect(self._on_theme_changed)

    def _restore_state(self) -> None:
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

    # -- category registry ------------------------------------------------- #

    def _build_registry(self, categories: list[Category]) -> dict[str, Category]:
        """Seed category metadata from the manifest, always including the
        permanent Uncategorized home. ``all`` is a filter concept, not a box."""
        registry: dict[str, Category] = {UNCATEGORIZED.key: UNCATEGORIZED}
        for category in categories:
            if category.key == "all" or category.key == UNCATEGORIZED.key:
                continue
            registry[category.key] = category
        return registry

    def _category_for(self, key: str) -> Category:
        """Return category metadata for ``key``, synthesising it if a mod refers
        to a category the registry has not seen (e.g. hand-edited manifest)."""
        category = self._registry.get(key)
        if category is None:
            name = key.replace("-", " ").replace("_", " ").strip().title() or key
            category = Category(key, name, palette_color_key(len(self._registry)))
            self._registry[key] = category
        return category

    def _active_category_keys(self) -> set[str]:
        """Keys that should have a box: Uncategorized, every category a mod is
        currently filed under, and every user-created (pinned) category, which
        stays even while empty."""
        keys = {UNCATEGORIZED.key}
        keys.update(mod.category_key for mod in self.mod_model.mods)
        keys.update(self._pinned_keys)
        return keys

    def _ordered_active_categories(self) -> list[Category]:
        """Active categories with Uncategorized first, then the rest by name."""
        active = self._active_category_keys()
        others = sorted(
            (self._category_for(key) for key in active if key != UNCATEGORIZED.key),
            key=lambda c: c.name.casefold(),
        )
        return [self._category_for(UNCATEGORIZED.key), *others]

    def _sync_category_lists(self) -> None:
        """Point the shared category lists at the active set and prune metadata
        for categories that no longer have a box."""
        active = self._ordered_active_categories()
        active_keys = {category.key for category in active}
        # Mutate in place: boxes and the detail panel hold these by reference.
        self._box_categories[:] = active
        self._categories[:] = active
        self.detail_panel.set_categories(active)
        for key in list(self._registry):
            if key != UNCATEGORIZED.key and key not in active_keys:
                del self._registry[key]

    def _reconcile_boxes(self, rebuild_body: bool = True) -> None:
        """Add boxes for newly-populated categories and drop boxes whose last
        mod has left (Uncategorized is never dropped)."""
        active_keys = self._active_category_keys()
        for key in list(self.boxes):
            if key not in active_keys:
                self.boxes.pop(key, None)
                self.box_workspace.remove_box(key)
        self._sync_category_lists()
        for category in self._ordered_active_categories():
            if category.key not in self.boxes:
                self._install_box(category)
        self._refresh_boxes(rebuild_body=rebuild_body)

    # -- user-created categories ------------------------------------------ #

    def _show_canvas_menu(self, global_pos, scene_pos) -> None:
        """Right-click menu for the canvas. Over a box it offers to remove that
        category (when empty); anywhere it offers to create a new one."""
        menu = QMenu(self)
        key = self.box_workspace.box_key_at(scene_pos)
        if key is not None:
            category = self._registry.get(key)
            name = category.name if category is not None else key
            remove_action = menu.addAction(f"Remove “{name}”")
            if category is not None and category.built_in:
                remove_action.setEnabled(False)
                remove_action.setToolTip("The Uncategorized box is permanent.")
            elif self._mods_in(key):
                remove_action.setEnabled(False)
                remove_action.setToolTip("Move this box's mods out before removing it.")
            else:
                remove_action.triggered.connect(lambda _=False, k=key: self._remove_category(k))
            menu.addSeparator()
        menu.addMenu(self._build_create_category_menu("New category"))
        menu.setToolTipsVisible(True)
        menu.exec(global_pos)

    def _available_catalog_categories(self) -> list[Category]:
        """Catalog categories that don't yet have a box, sorted by name.

        Each category maps to at most one box, so once a category is active
        (has a box) it drops out of the "new category" menu. Uncategorized is
        the permanent home and is never offered here."""
        active = self._active_category_keys()
        return sorted(
            (
                category
                for category in load_category_catalog()
                if category.key != UNCATEGORIZED.key and category.key not in active
            ),
            key=lambda c: c.name.casefold(),
        )

    def _build_create_category_menu(self, title: str = "New category") -> QMenu:
        """A menu listing every catalog category that doesn't yet have a box.

        Each entry creates that category directly on click. When all categories
        are already placed the menu holds a single disabled hint."""
        menu = QMenu(title, self)
        available = self._available_catalog_categories()
        if not available:
            empty = menu.addAction("All categories already have a box")
            empty.setEnabled(False)
            return menu
        for category in available:
            action = menu.addAction(category.name)
            action.triggered.connect(
                lambda _=False, c=category: self._create_category(c)
            )
        return menu

    def _prompt_create_category(self) -> None:
        menu = self._build_create_category_menu()
        menu.exec(QCursor.pos())

    def _create_category(self, template: Category) -> None:
        """Create a user-made category from the catalog and place its (empty)
        box on the canvas."""
        if template.key in self._registry or template.key in self._active_category_keys():
            self._show_notice(f"A category named '{template.name}' already exists.")
            return
        self._registry[template.key] = Category(
            template.key, template.name, template.color_key, user_created=True
        )
        self._pinned_keys.add(template.key)
        self._reconcile_boxes(rebuild_body=True)  # creates the box (free placement)
        self._schedule_manifest_save()
        self._show_notice(f"Created category '{template.name}'.")

    def _remove_category(self, key: str) -> None:
        """Remove an empty user-created category and its box."""
        if key == UNCATEGORIZED.key:
            return
        category = self._registry.get(key)
        if category is not None and category.built_in:
            return
        if self._mods_in(key):
            self._show_notice("Move this box's mods out before removing it.")
            return
        self._pinned_keys.discard(key)
        self._registry.pop(key, None)
        self._settings.remove(f"mod_manager/box_geometry/{key}")
        self._settings.remove(f"mod_manager/box_color/{key}")
        self._reconcile_boxes(rebuild_body=True)  # box no longer active -> removed
        self._schedule_manifest_save()

    # -- manifest persistence --------------------------------------------- #

    def _seed_manifest(self) -> Manifest:
        """A fresh install starts empty: no mods, only the permanent
        Uncategorized category."""
        return Manifest(mods=[], categories=[UNCATEGORIZED])

    def _current_manifest(self) -> Manifest:
        return Manifest(
            mods=list(self.mod_model.mods),
            categories=self._ordered_active_categories(),
        )

    def _schedule_manifest_save(self, *_args) -> None:
        self._manifest_save_timer.start()

    def _persist_manifest(self) -> None:
        if self._store.save(self._current_manifest()):
            return
        # Another instance holds the write lock; say so once, not on every edit.
        if not self._readonly_warned:
            self._readonly_warned = True
            self._show_notice(
                "Another instance is running — changes to your mod list won't be saved."
            )

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
        self.mod_model.set_category(mod, category_key)  # emits dataChanged -> reconcile

    def _on_mod_enabled(self, mod: InstalledMod) -> None:
        row = self.mod_model.row_for(mod)
        if row < 0:
            return
        index = self.mod_model.index(row, 0)
        self.mod_model.setData(index, mod.enabled, InstalledModRoles.ENABLED)

    def _request_remove(self, mod: InstalledMod) -> None:
        if not self._store.can_write:
            self._show_notice(
                "Another instance is running — removals are disabled in read-only mode."
            )
            return

        config = load_config()
        game_check = validate_game_path(config.game_path)
        if config.game_path is None or game_check.level is CheckLevel.ERROR:
            self._show_notice(
                "Set a valid game folder in Settings before removing mods."
            )
            return

        dialog = QMessageBox(self)
        dialog.setIcon(QMessageBox.Icon.Warning)
        dialog.setWindowTitle("Remove mod")
        dialog.setText(f"Remove '{mod.name}' from the game?")
        dialog.setInformativeText(
            "Its tracked Mods/DLC folders will be deleted. "
            "The vaulted source archive will be kept for reinstall."
        )
        dialog.setStandardButtons(
            QMessageBox.StandardButton.Cancel | QMessageBox.StandardButton.Yes
        )
        dialog.setDefaultButton(QMessageBox.StandardButton.Cancel)
        remove_button = dialog.button(QMessageBox.StandardButton.Yes)
        remove_button.setText("Remove mod")
        remove_button.setProperty("class", "danger")
        remove_button.style().unpolish(remove_button)
        remove_button.style().polish(remove_button)
        if dialog.exec() != QMessageBox.StandardButton.Yes:
            return

        try:
            result = uninstall_mod(mod, config.game_path, self.mod_model.mods)
        except (UninstallError, OSError) as exc:
            self._show_notice(
                f"Could not fully remove '{mod.name}': {exc}. "
                "Its manifest record was kept so you can retry."
            )
            return

        if self.detail_panel.current_mod is mod:
            self.detail_panel.show_selection([])
        if not self.mod_model.remove_mod(mod):
            self._show_notice(
                f"Removed '{mod.name}' from disk, but its manifest record was not found."
            )
            return

        # Disk removal and manifest removal form one user action. Persist now so
        # a quick app exit cannot resurrect the removed card from stale data.
        self._manifest_save_timer.stop()
        self._persist_manifest()

        detail = "Vault archive kept."
        if result.shared_paths:
            count = len(result.shared_paths)
            detail += f" Kept {count} folder{'s' if count != 1 else ''} shared with other mods."
        self._show_notice(f"Removed '{mod.name}'. {detail}")

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
        # A recategorize may have emptied a box or filled a new one, so reconcile;
        # an enable-only change refreshes headers so the clicked card survives.
        if membership_changed:
            self._reconcile_boxes(rebuild_body=True)
        else:
            self._refresh_boxes(rebuild_body=False)
        # Keep the detail panel in step with whichever mod it is showing.
        mod = self.detail_panel.current_mod
        if mod is not None:
            for row in range(top_left.row(), bottom_right.row() + 1):
                if self.mod_model.mod_at(row) is mod:
                    self.detail_panel.show_selection([mod])
                    break

    def _on_membership_changed(self, *_args) -> None:
        self._reconcile_boxes(rebuild_body=True)

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
        self.install_archives(paths)

    # -- install ----------------------------------------------------------- #

    def prompt_install(self) -> None:
        """Open a file picker and install the chosen archives (header button)."""
        filter_str = "Mod archives (*.zip *.7z *.rar)"
        paths, _ = QFileDialog.getOpenFileNames(
            self, "Select mod archives", "", filter_str
        )
        if paths:
            self.install_archives(paths)

    def install_archives(self, paths: list[str], category_key: str | None = None) -> None:
        """Review each archive in a pre-install dialog, then install on confirm.

        Rather than installing silently, each archive is first *inspected* (its
        entry listing read, without extracting to disk) so the user can see an
        overview (Nexus data, cover art), what the install will put on disk, and
        edit how it is filed (name, category, enabled). Only when they confirm is
        the archive actually extracted and installed — a cancelled archive is
        never unpacked. ``category_key`` only seeds the dialog's default category;
        the user's choice in the dialog wins.

        Synchronous for now — extraction/merge threading is a separate roadmap
        step. Game-config merges are deliberately not performed here yet, so a
        mod with config needs installs its files but leaves those merges pending.
        """
        if not self._store.can_write:
            self._show_notice(
                "Another instance is running — installs are disabled in read-only mode."
            )
            return

        config = load_config()
        game_check = validate_game_path(config.game_path)
        if config.game_path is None or game_check.level is CheckLevel.ERROR:
            self._show_notice(
                "Set a valid game folder in Settings before installing mods."
            )
            return

        installed: list[str] = []
        failures: list[str] = []
        warnings: list[str] = []
        for index, path in enumerate(paths):
            cancelled = self._review_and_install(
                path, config, category_key, index, len(paths),
                installed, failures, warnings,
            )
            if cancelled:
                break

        self._report_install(installed, failures, warnings)

    def _review_and_install(
        self,
        path: str,
        config,
        category_key: str | None,
        index: int,
        total: int,
        installed: list[str],
        failures: list[str],
        warnings: list[str],
    ) -> bool:
        """Prepare, review, and (on confirm) install one archive.

        Returns ``True`` when the user chose *Cancel all*, signalling the caller
        to abandon the rest of the batch. Inspection/extraction failures are
        recorded in ``failures`` and swallowed so one bad archive doesn't sink the
        others.
        """
        name = Path(path).name
        metadata = self._lookup_metadata(name)
        # Read the archive listing only (no extraction to disk yet) to preview it.
        try:
            preview = inspect_archive(path)
        except (InstallError, OSError) as exc:
            failures.append(f"{name}: {exc}")
            return False

        # Fetch the Nexus cover once: it is the dialog preview now and the mod's
        # card image after install. A failed download leaves None, which the
        # placeholder cover handles.
        thumbnail = cache_thumbnail(metadata.to_dict()) if metadata else None
        dialog = InstallReviewDialog(
            preview=preview,
            metadata=metadata,
            archive_path=Path(path),
            thumbnail_path=thumbnail,
            category_options=self._category_name_options(),
            suggested_category=self._suggested_category_name(metadata, category_key),
            default_name=self._default_mod_name(metadata, path),
            index=index,
            total=total,
            parent=self,
        )
        dialog.exec()
        decision = dialog.decision()
        if decision is InstallDecision.CANCEL_ALL:
            return True
        if decision is not InstallDecision.INSTALL:
            return False  # skipped: nothing was extracted, move to the next

        choices = dialog.choices()
        # Only now, on the user's confirmation, is the archive actually unpacked —
        # and it runs on a worker thread behind a progress dialog so a multi-GB
        # mod doesn't freeze the UI.
        result, error = self._run_install_worker(path, config, metadata, choices)
        if error is not None:
            failures.append(f"{name}: {error}")
            return False
        if result is None:
            failures.append(f"{name}: install did not complete.")
            return False

        result.mod.enabled = choices.enabled
        if thumbnail:
            result.mod.thumbnail_path = thumbnail
        resolved_key = self._resolve_category_name(
            choices.category_name or UNCATEGORIZED.name
        )
        self._register_installed_mod(result.mod, resolved_key)
        installed.append(result.mod.name)
        return False

    def _run_install_worker(self, path, config, metadata, choices):
        """Run the confirmed install on a worker thread behind a modal progress
        dialog. Returns ``(InstallResult | None, Exception | None)`` once done.

        ``dialog.exec()`` spins a nested event loop that keeps the UI painting and
        the progress bar updating while the worker runs; the finished/failed
        handlers stash the outcome and end the loop."""
        worker = InstallWorker(
            archive_path=path,
            game_path=config.game_path,
            vault_path=config.vault_path,
            nexus_metadata=metadata.to_dict() if metadata else None,
            name_override=choices.name,
        )
        dialog = InstallProgressDialog(choices.name or Path(path).stem, parent=self)
        outcome: dict[str, object] = {"result": None, "error": None}

        def done(result=None, error=None) -> None:
            outcome["result"] = result
            outcome["error"] = error
            dialog.finish(result, error)

        worker.signals.progress.connect(dialog.update_progress)
        worker.signals.finished.connect(lambda result: done(result=result))
        worker.signals.failed.connect(lambda error: done(error=error))
        # Hold a reference so the signals object isn't collected mid-flight.
        self._install_worker = worker
        QThreadPool.globalInstance().start(worker)
        dialog.exec()
        self._install_worker = None
        return outcome["result"], outcome["error"]

    @staticmethod
    def _lookup_metadata(filename: str):
        """Best-effort Nexus lookup; the dialog explains an absent match, so a
        failed lookup is not an error here — it just yields no metadata."""
        try:
            return lookup_archive_metadata(filename)
        except NexusLookupError:
            return None

    def _suggested_category_name(self, metadata, category_key: str | None) -> str:
        """The category the dialog defaults to: a caller-pinned one, else the one
        derived from Nexus metadata, else Uncategorized."""
        if category_key is not None:
            pinned = self._registry.get(category_key)
            if pinned is not None:
                return pinned.name
        if metadata is not None:
            return preferred_install_category_name(
                metadata.category_name,
                contains_adult_content=metadata.contains_adult_content,
            )
        return UNCATEGORIZED.name

    def _category_name_options(self) -> list[str]:
        """Category names offered in the dialog dropdown: the active ones plus the
        full catalog, so the user can file into an existing box or a known kind."""
        names = {UNCATEGORIZED.name}
        names.update(category.name for category in self._registry.values())
        names.update(category.name for category in load_category_catalog())
        return sorted(names, key=str.casefold)

    @staticmethod
    def _default_mod_name(metadata, path: str) -> str:
        if metadata is not None and metadata.mod_name:
            return metadata.mod_name
        guessed, _version = parse_archive_name(Path(path).name)
        return guessed or Path(path).stem

    def _resolve_category_name(self, name: str) -> str:
        """Map a category name to a key, creating a new category if needed."""
        for category in self._registry.values():
            if category.name.casefold() == name.casefold():
                return category.key
        key = self._unique_key(slugify(name))
        self._registry[key] = Category(key, name, palette_color_key(len(self._registry)))
        return key

    def _register_installed_mod(self, mod: InstalledMod, category_key: str) -> None:
        """Give the mod a unique identity, file it under ``category_key``, and add
        it to the model (which triggers a reconcile so its box appears)."""
        mod.identity = self._unique_identity(mod.identity)
        mod.category_key = category_key
        self._category_for(category_key)  # ensure metadata exists
        self.mod_model.add_mod(mod)  # emits rowsInserted -> reconcile + manifest save

    def _unique_identity(self, base: str) -> str:
        identity = base or "mod"
        suffix = 2
        while self.mod_model.has_identity(identity):
            identity = f"{base}-{suffix}"
            suffix += 1
        return identity

    def _unique_key(self, base: str) -> str:
        key = base or "category"
        suffix = 2
        while key in self._registry:
            key = f"{base}-{suffix}"
            suffix += 1
        return key

    def _report_install(
        self,
        installed: list[str],
        failures: list[str],
        warnings: list[str] | None = None,
    ) -> None:
        parts: list[str] = []
        if installed:
            parts.append(
                f"Installed {len(installed)} mod{'s' if len(installed) != 1 else ''}: "
                + ", ".join(installed)
            )
        if failures:
            parts.append("Failed: " + "; ".join(failures))
        if warnings:
            parts.append("Warnings: " + "; ".join(warnings))
        if not parts:
            parts.append("No mods were installed.")
        self._show_notice("  ·  ".join(parts))

    # -- persistence ------------------------------------------------------- #

    def save_state(self) -> None:
        # Flush any pending debounced manifest write before we lose the timer,
        # then hand back the inter-process lock for the next instance.
        if self._manifest_save_timer.isActive():
            self._manifest_save_timer.stop()
            self._persist_manifest()
        self._store.release()

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
