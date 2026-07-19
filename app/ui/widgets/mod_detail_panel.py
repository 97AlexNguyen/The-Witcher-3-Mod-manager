from __future__ import annotations

from functools import partial

from PyQt6.QtCore import QSignalBlocker, Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QButtonGroup,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from app.domain import Category, InstalledMod
from app.ui.theme.tokens import SPACING_MD, SPACING_SM, SPACING_XS


class ModDetailPanel(QFrame):
    category_changed = pyqtSignal(object, str)

    SECTIONS = ("Content", "Game settings", "Keys", "Readme")

    def __init__(self, categories: list[Category], parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("detailPanel")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setMinimumWidth(320)
        self._categories = [category for category in categories if category.key != "all"]
        self._mod: InstalledMod | None = None
        self._build_ui()
        self.show_selection([])

    @property
    def current_mod(self) -> InstalledMod | None:
        return self._mod

    def set_categories(self, categories: list[Category]) -> None:
        """Refresh the category dropdown when the active category set changes
        (categories are created/removed as mods are installed and moved)."""
        self._categories = [category for category in categories if category.key != "all"]
        self._populate_categories()
        if self._mod is not None:
            self._sync_category_combo(self._mod)

    def _populate_categories(self) -> None:
        with QSignalBlocker(self.category_combo):
            self.category_combo.clear()
            for category in self._categories:
                self.category_combo.addItem(category.name, category.key)

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(SPACING_MD, SPACING_MD, SPACING_MD, SPACING_MD)
        root.setSpacing(SPACING_MD)
        heading = QLabel("MOD DETAILS")
        heading.setProperty("class", "label-md")
        root.addWidget(heading)

        self.mode_stack = QStackedWidget()
        self.empty_page = self._build_empty_page()
        self.detail_page = self._build_detail_page()
        self.multi_page = self._build_multi_page()
        self.mode_stack.addWidget(self.empty_page)
        self.mode_stack.addWidget(self.detail_page)
        self.mode_stack.addWidget(self.multi_page)
        root.addWidget(self.mode_stack, 1)

    def _build_empty_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.addStretch()
        icon = QLabel("◇")
        icon.setObjectName("detailEmptyIcon")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon)
        title = QLabel("Select a mod")
        title.setProperty("class", "headline-sm")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        text = QLabel("Choose a card to inspect its manifest, game settings, keys, and readme.")
        text.setProperty("class", "muted")
        text.setWordWrap(True)
        text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(text)
        layout.addStretch()
        return page

    def _build_detail_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_MD)

        self.name_label = QLabel()
        self.name_label.setProperty("class", "headline-sm")
        self.name_label.setWordWrap(True)
        layout.addWidget(self.name_label)
        self.description_label = QLabel()
        self.description_label.setProperty("class", "muted")
        self.description_label.setWordWrap(True)
        layout.addWidget(self.description_label)

        meta = QFrame()
        meta.setObjectName("detailMeta")
        meta_layout = QVBoxLayout(meta)
        meta_layout.setContentsMargins(SPACING_SM, SPACING_SM, SPACING_SM, SPACING_SM)
        meta_layout.setSpacing(SPACING_XS)
        self.version_label = QLabel()
        self.installed_label = QLabel()
        self.size_label = QLabel()
        self.priority_label = QLabel()
        self.vault_label = QLabel()
        self.vault_label.setWordWrap(True)
        for label in (
            self.version_label,
            self.installed_label,
            self.size_label,
            self.priority_label,
            self.vault_label,
        ):
            label.setProperty("class", "muted")
            meta_layout.addWidget(label)
        layout.addWidget(meta)

        layout.addWidget(self._field_label("CATEGORY"))
        self.category_combo = QComboBox()
        self._populate_categories()
        self.category_combo.currentIndexChanged.connect(self._category_edited)
        layout.addWidget(self.category_combo)

        segments = QHBoxLayout()
        segments.setSpacing(SPACING_XS)
        self.segment_group = QButtonGroup(self)
        self.segment_group.setExclusive(True)
        for index, section in enumerate(self.SECTIONS):
            button = QPushButton(section.upper())
            button.setProperty("class", "detailSegment")
            button.setCheckable(True)
            button.clicked.connect(partial(self._select_section, index))
            self.segment_group.addButton(button, index)
            segments.addWidget(button, 1)
            if index == 0:
                button.setChecked(True)
        layout.addLayout(segments)

        self.section_stack = QStackedWidget()
        self.section_labels: list[QLabel] = []
        for _section in self.SECTIONS:
            scroll = QScrollArea()
            scroll.setObjectName("detailScroll")
            scroll.setWidgetResizable(True)
            scroll.setFrameShape(QFrame.Shape.NoFrame)
            content = QWidget()
            content.setObjectName("detailSection")
            content_layout = QVBoxLayout(content)
            content_layout.setContentsMargins(SPACING_SM, SPACING_SM, SPACING_SM, SPACING_SM)
            label = QLabel()
            label.setWordWrap(True)
            label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
            label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            content_layout.addWidget(label)
            content_layout.addStretch()
            scroll.setWidget(content)
            self.section_labels.append(label)
            self.section_stack.addWidget(scroll)
        layout.addWidget(self.section_stack, 1)
        return page

    def _build_multi_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.addStretch()
        self.multi_title = QLabel()
        self.multi_title.setProperty("class", "headline-sm")
        self.multi_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.multi_title)
        message = QLabel("Bulk actions affect only the current selection.")
        message.setProperty("class", "muted")
        message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(message)
        layout.addSpacing(SPACING_MD)
        enable = QPushButton("ENABLE SELECTED")
        disable = QPushButton("DISABLE SELECTED")
        category = QPushButton("ASSIGN CATEGORY")
        for button in (enable, disable, category):
            button.setEnabled(False)
            button.setToolTip("Bulk mutation logic will be connected in a later phase")
            layout.addWidget(button)
        layout.addStretch()
        return page

    @staticmethod
    def _field_label(text: str) -> QLabel:
        label = QLabel(text)
        label.setProperty("class", "label-md")
        return label

    def show_selection(self, mods: list[InstalledMod]) -> None:
        if not mods:
            self._mod = None
            self.mode_stack.setCurrentWidget(self.empty_page)
            return
        if len(mods) > 1:
            self._mod = None
            self.multi_title.setText(f"{len(mods)} MODS SELECTED")
            self.mode_stack.setCurrentWidget(self.multi_page)
            return

        mod = mods[0]
        self._mod = mod
        self.name_label.setText(mod.name)
        self.description_label.setText(mod.description)
        self.version_label.setText(f"Version: {mod.version or '?'}")
        self.installed_label.setText(f"Installed: {mod.installed_on.isoformat()}")
        self.size_label.setText(f"Size: {self._format_size(mod.size_bytes)}")
        self.priority_label.setText(
            f"Priority: {'Unassigned' if mod.priority is None else mod.priority}"
        )
        self.vault_label.setText(f"Vault: {mod.vault_path or 'Source archive unavailable'}")
        self._sync_category_combo(mod)
        self.section_labels[0].setText(self._format_groups(mod.content, "This mod writes no tracked content."))
        self.section_labels[1].setText(self._format_groups(mod.settings, "This mod adds no game settings."))
        self.section_labels[2].setText(self._format_groups(mod.keys, "This mod adds no key bindings."))
        self.section_labels[3].setText(mod.readme or "No readme was included in the source archive.")
        self.mode_stack.setCurrentWidget(self.detail_page)

    def _sync_category_combo(self, mod: InstalledMod) -> None:
        with QSignalBlocker(self.category_combo):
            index = self.category_combo.findData(mod.category_key)
            self.category_combo.setCurrentIndex(max(0, index))

    @staticmethod
    def _format_size(size_bytes: int | None) -> str:
        if not isinstance(size_bytes, int) or size_bytes < 0:
            return "Unknown"
        size = float(size_bytes)
        for unit in ("B", "KB", "MB", "GB"):
            if size < 1024 or unit == "GB":
                precision = 0 if unit == "B" else 1
                return f"{size:.{precision}f} {unit}"
            size /= 1024
        return f"{size:.1f} GB"

    @staticmethod
    def _format_groups(groups: dict[str, tuple[str, ...]], empty_message: str) -> str:
        if not groups:
            return empty_message
        lines: list[str] = []
        for heading, values in groups.items():
            lines.append(heading.upper())
            lines.extend(f"  • {value}" for value in values)
            lines.append("")
        return "\n".join(lines).rstrip()

    def _select_section(self, index: int) -> None:
        self.section_stack.setCurrentIndex(index)

    def _category_edited(self, index: int) -> None:
        if self._mod is not None and index >= 0:
            self.category_changed.emit(self._mod, self.category_combo.itemData(index))
