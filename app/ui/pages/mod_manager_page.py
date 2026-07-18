from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import QByteArray, QPointF, QRect, QSettings, Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QColor, QDragEnterEvent, QDropEvent
from PyQt6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from app.config import CheckLevel, load_config, validate_game_path
from app.apis.nexus_metadata import NexusLookupError, lookup_archive_metadata
from app.data import (
    UNCATEGORIZED_CATEGORY_NAME,
    palette_color_key,
    preferred_install_category_name,
    slugify,
)
from app.domain import Category, InstalledMod
from app.install import InstallError, install_archive
from app.manifest import Manifest, ManifestStore
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
        # Categories are mod-driven now; the "add empty group" affordance no
        # longer fits the model, so hide it rather than let it spawn a box that
        # would be pruned on the next reconcile.
        self.box_workspace.add_group_button.hide()

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
        """Keys that should have a box: Uncategorized plus every category a mod
        is currently filed under."""
        keys = {UNCATEGORIZED.key}
        keys.update(mod.category_key for mod in self.mod_model.mods)
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
        """Install each archive to disk and record it in the manifest.

        Synchronous for now — extraction/merge threading is a separate roadmap
        step. Game-config merges are deliberately not performed here yet, so a
        mod with config needs installs its files but leaves those merges pending.

        With no explicit ``category_key``, each archive is filed automatically
        from its verified Nexus metadata. Adult content always goes to the
        dedicated Adult Content category, ahead of Nexus's normal taxonomy.
        Passing a key remains available for callers that intentionally override
        automatic categorisation.
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
        for path in paths:
            resolved_category_key = category_key
            category_name: str | None = None
            if resolved_category_key is None:
                try:
                    metadata = lookup_archive_metadata(Path(path).name)
                except NexusLookupError as exc:
                    category_name = UNCATEGORIZED.name
                    warnings.append(
                        f"{Path(path).name}: Nexus metadata unavailable ({exc}); "
                        f"filed under {UNCATEGORIZED.name}"
                    )
                else:
                    category_name = preferred_install_category_name(
                        metadata.category_name,
                        contains_adult_content=metadata.contains_adult_content,
                    )

            try:
                result = install_archive(path, config.game_path, config.vault_path)
            except (InstallError, OSError) as exc:
                failures.append(f"{Path(path).name}: {exc}")
                continue
            if resolved_category_key is None:
                resolved_category_key = self._resolve_category_name(
                    category_name or UNCATEGORIZED.name
                )
            self._register_installed_mod(result.mod, resolved_category_key)
            installed.append(result.mod.name)

        self._report_install(installed, failures, warnings)

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
