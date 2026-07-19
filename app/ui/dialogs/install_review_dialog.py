"""Pre-install review dialog.

Instead of installing a dropped archive silently, the mod manager first extracts
and scans it, then shows this modal so the user can see *what the archive is*
(Nexus overview, cover art), *what installing it will do* (which Mods/DLC folders
land on disk), and tweak *how* it is filed (display name, category, enabled) —
before anything touches the game tree.

The dialog is purely presentational: it never installs. It reports the user's
decision (install / skip / cancel-all) plus their choices, and the page acts on
that using the already-extracted package.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path

from PyQt6.QtCore import QRect, QSize, Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from app.install.inspect import ArchivePreview
from app.apis.nexus_metadata import NexusArchiveMetadata
from app.ui.theme.tokens import (
    RADIUS_MD,
    SPACING_LG,
    SPACING_MD,
    SPACING_SM,
    SPACING_XS,
)

_PREVIEW_W = 200
_PREVIEW_H = 112  # 16:9-ish, matching the landscape Nexus cover art


class InstallDecision(Enum):
    """What the user chose to do with the reviewed archive."""

    INSTALL = auto()
    SKIP = auto()  # don't install this one, move on to the next archive
    CANCEL_ALL = auto()  # abandon the whole install batch


@dataclass(frozen=True, slots=True)
class InstallChoices:
    """The user's edits, applied by the page when it installs the package."""

    name: str
    category_name: str
    enabled: bool


class InstallReviewDialog(QDialog):
    """Modal shown once per archive before it is installed.

    Read the decision with :meth:`decision` and the user's edits with
    :meth:`choices` after ``exec()`` returns.
    """

    def __init__(
        self,
        *,
        preview: ArchivePreview,
        metadata: NexusArchiveMetadata | None,
        archive_path: Path,
        thumbnail_path: str | None,
        category_options: list[str],
        suggested_category: str,
        default_name: str,
        index: int = 0,
        total: int = 1,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._preview = preview
        self._metadata = metadata
        self._archive_path = archive_path
        self._thumbnail_path = thumbnail_path
        self._total = total
        self._decision = InstallDecision.SKIP

        self.setObjectName("installReviewDialog")
        self.setWindowTitle("Review install")
        self.setModal(True)
        self.setMinimumWidth(620)
        self.setMinimumHeight(560)

        self._build_ui(default_name, category_options, suggested_category, index, total)

    # -- public API -------------------------------------------------------- #

    def decision(self) -> InstallDecision:
        return self._decision

    def choices(self) -> InstallChoices:
        return InstallChoices(
            name=self._name_edit.text().strip() or self._archive_path.stem,
            category_name=self._category_combo.currentText().strip(),
            enabled=self._enabled_check.isChecked(),
        )

    # -- construction ------------------------------------------------------ #

    def _build_ui(
        self,
        default_name: str,
        category_options: list[str],
        suggested_category: str,
        index: int,
        total: int,
    ) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING_LG, SPACING_LG, SPACING_LG, SPACING_LG)
        layout.setSpacing(SPACING_MD)

        layout.addLayout(self._header(default_name, index, total))

        scroll = QScrollArea()
        scroll.setObjectName("reviewScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        body = QWidget()
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(0, 0, SPACING_SM, 0)
        body_layout.setSpacing(SPACING_MD)
        body_layout.addWidget(self._overview_section())
        body_layout.addWidget(self._plan_section())
        readme = self._readme_section()
        if readme is not None:
            body_layout.addWidget(readme)
        body_layout.addWidget(self._choices_section(default_name, category_options, suggested_category))
        body_layout.addStretch()
        scroll.setWidget(body)
        layout.addWidget(scroll, 1)

        layout.addLayout(self._button_row(total))

    def _header(self, default_name: str, index: int, total: int) -> QVBoxLayout:
        header = QVBoxLayout()
        header.setSpacing(SPACING_XS)
        title = QLabel(default_name or self._archive_path.stem)
        title.setProperty("class", "headline-md")
        title.setWordWrap(True)
        header.addWidget(title)
        subtitle = QLabel(self._archive_path.name)
        subtitle.setProperty("class", "muted")
        subtitle.setWordWrap(True)
        header.addWidget(subtitle)
        if total > 1:
            counter = QLabel(f"Reviewing file {index + 1} of {total}")
            counter.setProperty("class", "label-md")
            header.addWidget(counter)
        return header

    def _overview_section(self) -> QFrame:
        frame, body = self._section("OVERVIEW")
        row = QHBoxLayout()
        row.setSpacing(SPACING_MD)

        preview = QLabel()
        preview.setObjectName("reviewPreview")
        preview.setFixedSize(_PREVIEW_W, _PREVIEW_H)
        preview.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pixmap = self._preview_pixmap()
        if pixmap is not None:
            preview.setPixmap(pixmap)
        else:
            preview.setText("No preview")
            preview.setProperty("class", "muted")
        row.addWidget(preview, 0, Qt.AlignmentFlag.AlignTop)

        facts = QVBoxLayout()
        facts.setSpacing(SPACING_XS)
        for line in self._overview_facts():
            label = QLabel(line)
            label.setProperty("class", "muted")
            label.setWordWrap(True)
            label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            facts.addWidget(label)
        if self._metadata is not None and self._metadata.contains_adult_content:
            warn = QLabel("⚠ Flagged as adult content on Nexus.")
            warn.setProperty("class", "status-warn")
            warn.setWordWrap(True)
            facts.addWidget(warn)
        if self._metadata is not None:
            link = QLabel(
                f'<a href="{self._metadata.mod_page_url}">Open the Nexus mod page ↗</a>'
            )
            link.setProperty("class", "muted")
            link.setOpenExternalLinks(True)
            link.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
            facts.addWidget(link)
        facts.addStretch()
        row.addLayout(facts, 1)
        body.addLayout(row)

        summary = self._metadata.short_description if self._metadata else ""
        if summary:
            desc = QLabel(summary)
            desc.setWordWrap(True)
            desc.setProperty("class", "muted")
            body.addSpacing(SPACING_XS)
            body.addWidget(desc)
        return frame

    def _plan_section(self) -> QFrame:
        frame, body = self._section("INSTALL PLAN")
        mods = self._preview.mod_names
        dlcs = self._preview.dlc_names

        if self._preview.is_empty:
            warn = QLabel(
                "No Mods or DLC folders were found in this archive, so there is "
                "nothing to install. It may be a texture-only pack or laid out in "
                "a way the scanner does not recognise."
            )
            warn.setProperty("class", "status-error")
            warn.setWordWrap(True)
            body.addWidget(warn)
            return frame

        intro = QLabel("Installing this mod will:")
        intro.setProperty("class", "muted")
        body.addWidget(intro)
        if mods:
            body.addWidget(self._plan_line(f"Copy {_count(mods, 'folder')} into Mods\\", mods))
        if dlcs:
            body.addWidget(self._plan_line(f"Copy {_count(dlcs, 'folder')} into DLC\\", dlcs))
        body.addWidget(
            self._plan_line("Keep the source archive in your vault for reinstalling.", [])
        )
        return frame

    def _plan_line(self, heading: str, names: list[str]) -> QWidget:
        wrap = QWidget()
        col = QVBoxLayout(wrap)
        col.setContentsMargins(0, 0, 0, 0)
        col.setSpacing(1)
        head = QLabel(f"•  {heading}")
        head.setWordWrap(True)
        col.addWidget(head)
        for name in names:
            item = QLabel(f"      – {name}")
            item.setProperty("class", "mono")
            item.setWordWrap(True)
            col.addWidget(item)
        return wrap

    def _readme_section(self) -> QFrame | None:
        readme = (self._preview.readme or "").strip()
        if not readme:
            return None
        frame, body = self._section("README")
        scroll = QScrollArea()
        scroll.setObjectName("reviewReadmeScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setMaximumHeight(160)
        text = QLabel(readme)
        text.setWordWrap(True)
        text.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        text.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        text.setContentsMargins(0, 0, SPACING_SM, 0)
        scroll.setWidget(text)
        body.addWidget(scroll)
        return frame

    def _choices_section(
        self,
        default_name: str,
        category_options: list[str],
        suggested_category: str,
    ) -> QFrame:
        frame, body = self._section("HOW TO FILE IT")

        body.addWidget(self._field_label("DISPLAY NAME"))
        self._name_edit = QLineEdit(default_name)
        self._name_edit.setPlaceholderText(self._archive_path.stem)
        body.addWidget(self._name_edit)

        body.addWidget(self._field_label("CATEGORY"))
        self._category_combo = QComboBox()
        self._category_combo.setEditable(True)
        seen: set[str] = set()
        for name in [suggested_category, *category_options]:
            key = name.casefold()
            if name and key not in seen:
                seen.add(key)
                self._category_combo.addItem(name)
        if suggested_category:
            self._category_combo.setCurrentText(suggested_category)
        body.addWidget(self._category_combo)
        hint = QLabel("Suggested from Nexus metadata — type to file it elsewhere.")
        hint.setProperty("class", "muted")
        hint.setWordWrap(True)
        body.addWidget(hint)

        body.addSpacing(SPACING_XS)
        self._enabled_check = QCheckBox("Enable this mod after installing")
        self._enabled_check.setChecked(True)
        body.addWidget(self._enabled_check)
        return frame

    def _button_row(self, total: int) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(SPACING_SM)
        if total > 1:
            cancel_all = QPushButton("CANCEL ALL")
            cancel_all.setProperty("class", "ghost")
            cancel_all.clicked.connect(self._on_cancel_all)
            row.addWidget(cancel_all)
        row.addStretch()

        skip = QPushButton("SKIP" if total > 1 else "CANCEL")
        skip.setProperty("class", "ghost")
        skip.clicked.connect(self._on_skip)
        row.addWidget(skip)

        install = QPushButton("INSTALL")
        install.setProperty("class", "primary")
        install.setDefault(True)
        install.setEnabled(not self._preview.is_empty)
        if self._preview.is_empty:
            install.setToolTip("There is nothing in this archive to install.")
        install.clicked.connect(self._on_install)
        row.addWidget(install)
        return row

    # -- decisions --------------------------------------------------------- #

    def _on_install(self) -> None:
        self._decision = InstallDecision.INSTALL
        self.accept()

    def _on_skip(self) -> None:
        self._decision = InstallDecision.SKIP
        self.reject()

    def _on_cancel_all(self) -> None:
        self._decision = InstallDecision.CANCEL_ALL
        self.reject()

    # -- helpers ----------------------------------------------------------- #

    def _section(self, title: str) -> tuple[QFrame, QVBoxLayout]:
        frame = QFrame()
        frame.setObjectName("settingsSection")
        frame.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        body = QVBoxLayout(frame)
        body.setContentsMargins(SPACING_MD, SPACING_MD, SPACING_MD, SPACING_MD)
        body.setSpacing(SPACING_XS)
        label = QLabel(title)
        label.setProperty("class", "label-md")
        body.addWidget(label)
        return frame, body

    @staticmethod
    def _field_label(text: str) -> QLabel:
        label = QLabel(text)
        label.setProperty("class", "label-md")
        return label

    def _overview_facts(self) -> list[str]:
        facts = [
            f"File: {self._archive_path.name}",
            f"Size: {self._format_size(self._archive_size())}",
        ]
        meta = self._metadata
        if meta is None:
            facts.append(
                "Not matched to a Nexus mod (no API key, offline, or a renamed "
                "or hand-built archive). It will still install."
            )
            return facts
        facts.append(f"Nexus mod: {meta.mod_name}")
        if meta.author:
            facts.append(f"Author: {meta.author}")
        if meta.version:
            facts.append(f"Version: {meta.version}")
        if meta.category_name:
            facts.append(f"Nexus category: {meta.category_name}")
        if meta.file_uploaded_time:
            facts.append(f"Uploaded: {meta.file_uploaded_time}")
        return facts

    def _archive_size(self) -> int | None:
        if self._metadata is not None and isinstance(self._metadata.file_size_bytes, int):
            return self._metadata.file_size_bytes
        try:
            return self._archive_path.stat().st_size
        except OSError:
            return None

    def _preview_pixmap(self) -> QPixmap | None:
        if not self._thumbnail_path or not Path(self._thumbnail_path).is_file():
            return None
        source = QPixmap(self._thumbnail_path)
        if source.isNull():
            return None
        size = QSize(_PREVIEW_W, _PREVIEW_H)
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


def _count(items: list[str], noun: str) -> str:
    count = len(items)
    return f"{count} {noun}{'s' if count != 1 else ''}"
