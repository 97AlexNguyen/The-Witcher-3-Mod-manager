from __future__ import annotations

from PyQt6.QtCore import QObject, QRunnable, Qt, QThreadPool, pyqtSignal
from PyQt6.QtWidgets import (
    QDialog,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.config import (
    AppConfig,
    CheckLevel,
    CheckResult,
    check_nexus_api_key,
    get_nexus_api_key,
    load_config,
    save_config,
    set_nexus_api_key,
    validate_game_path,
    validate_vault_path,
)
from app.ui.theme.tokens import SPACING_LG, SPACING_MD, SPACING_SM, SPACING_XS

_STATUS_CLASS = {
    CheckLevel.OK: "status-ok",
    CheckLevel.WARNING: "status-warn",
    CheckLevel.ERROR: "status-error",
    CheckLevel.UNKNOWN: "status-muted",
}


class _ApiCheckSignals(QObject):
    done = pyqtSignal(object)  # emits a CheckResult


class _ApiCheckWorker(QRunnable):
    """Runs the blocking Nexus validation off the UI thread."""

    def __init__(self, key: str) -> None:
        super().__init__()
        self._key = key
        self.signals = _ApiCheckSignals()

    def run(self) -> None:  # noqa: D401 - QRunnable entry point
        self.signals.done.emit(check_nexus_api_key(self._key))


class SettingsDialog(QDialog):
    """Modal editor for the app's own preferences: game path, mod vault, Nexus key.

    On accept it writes ``config.json`` (paths) and pushes the API key to the OS
    credential store. The key never touches the config file — see app.config.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("settingsDialog")
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.setMinimumWidth(560)

        self._config = load_config()
        self._build_ui()
        self._load_values()

    # -- construction ------------------------------------------------------ #

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING_LG, SPACING_LG, SPACING_LG, SPACING_LG)
        layout.setSpacing(SPACING_MD)

        heading = QLabel("SETTINGS")
        heading.setProperty("class", "headline-md")
        layout.addWidget(heading)

        layout.addWidget(
            self._path_section(
                "GAME FOLDER",
                "Your Witcher 3 install root — the folder containing bin\\x64.",
                path=True,
                field_attr="_game_edit",
                status_attr="_game_status",
                placeholder="e.g. C:\\Program Files (x86)\\Steam\\...\\The Witcher 3",
            )
        )
        layout.addWidget(
            self._path_section(
                "MOD STORAGE",
                "Where installed mod archives are vaulted so a mod can be reinstalled.",
                path=True,
                field_attr="_vault_edit",
                status_attr="_vault_status",
                placeholder="e.g. D:\\W3Mods\\vault",
            )
        )
        layout.addWidget(self._api_section())

        button_row = QHBoxLayout()
        button_row.setSpacing(SPACING_SM)
        button_row.addStretch()
        cancel = QPushButton("CANCEL")
        cancel.setProperty("class", "ghost")
        cancel.clicked.connect(self.reject)
        button_row.addWidget(cancel)
        save = QPushButton("SAVE")
        save.setProperty("class", "primary")
        save.setDefault(True)
        save.clicked.connect(self._on_save)
        button_row.addWidget(save)
        layout.addLayout(button_row)

    def _path_section(
        self,
        title: str,
        description: str,
        *,
        path: bool,
        field_attr: str,
        status_attr: str,
        placeholder: str,
    ) -> QFrame:
        frame, body = self._section_frame(title, description)

        row = QHBoxLayout()
        row.setSpacing(SPACING_SM)
        edit = QLineEdit()
        edit.setPlaceholderText(placeholder)
        edit.textChanged.connect(self._revalidate_paths)
        setattr(self, field_attr, edit)
        row.addWidget(edit, 1)
        if path:
            browse = QPushButton("BROWSE…")
            browse.clicked.connect(lambda: self._browse_into(edit))
            row.addWidget(browse)
        body.addLayout(row)

        status = QLabel("")
        status.setProperty("class", "status-muted")
        status.setWordWrap(True)
        setattr(self, status_attr, status)
        body.addWidget(status)
        return frame

    def _api_section(self) -> QFrame:
        frame, body = self._section_frame(
            "NEXUS ACCOUNT",
            "Personal API key from nexusmods.com. Stored securely in Windows "
            "Credential Manager, never in the config file. Not used yet.",
        )

        row = QHBoxLayout()
        row.setSpacing(SPACING_SM)
        self._api_edit = QLineEdit()
        self._api_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self._api_edit.setPlaceholderText("Paste your Nexus API key")
        row.addWidget(self._api_edit, 1)

        self._reveal_button = QPushButton("SHOW")
        self._reveal_button.setProperty("class", "ghost")
        self._reveal_button.setCheckable(True)
        self._reveal_button.toggled.connect(self._toggle_reveal)
        row.addWidget(self._reveal_button)

        self._check_button = QPushButton("CHECK API")
        self._check_button.clicked.connect(self._on_check_api)
        row.addWidget(self._check_button)
        body.addLayout(row)

        self._api_status = QLabel("")
        self._api_status.setProperty("class", "status-muted")
        self._api_status.setWordWrap(True)
        body.addWidget(self._api_status)
        return frame

    def _section_frame(self, title: str, description: str) -> tuple[QFrame, QVBoxLayout]:
        frame = QFrame()
        frame.setObjectName("settingsSection")
        frame.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        body = QVBoxLayout(frame)
        body.setContentsMargins(SPACING_MD, SPACING_MD, SPACING_MD, SPACING_MD)
        body.setSpacing(SPACING_XS)

        label = QLabel(title)
        label.setProperty("class", "label-md")
        body.addWidget(label)
        desc = QLabel(description)
        desc.setProperty("class", "muted")
        desc.setWordWrap(True)
        body.addWidget(desc)
        body.addSpacing(SPACING_XS)
        return frame, body

    # -- values ------------------------------------------------------------ #

    def _load_values(self) -> None:
        self._game_edit.setText(self._config.game_path or "")
        self._vault_edit.setText(self._config.vault_path or "")
        self._api_edit.setText(get_nexus_api_key() or "")
        self._revalidate_paths()
        self._api_status.setText("")

    def _revalidate_paths(self) -> None:
        self._apply_status(self._game_status, validate_game_path(self._game_edit.text()))
        self._apply_status(self._vault_status, validate_vault_path(self._vault_edit.text()))

    # -- actions ----------------------------------------------------------- #

    def _browse_into(self, edit: QLineEdit) -> None:
        start = edit.text().strip() or ""
        chosen = QFileDialog.getExistingDirectory(self, "Select folder", start)
        if chosen:
            edit.setText(chosen)

    def _toggle_reveal(self, revealed: bool) -> None:
        self._api_edit.setEchoMode(
            QLineEdit.EchoMode.Normal if revealed else QLineEdit.EchoMode.Password
        )
        self._reveal_button.setText("HIDE" if revealed else "SHOW")

    def _on_check_api(self) -> None:
        key = self._api_edit.text().strip()
        if not key:
            self._apply_status(self._api_status, check_nexus_api_key(key))
            return
        self._check_button.setEnabled(False)
        self._apply_status(
            self._api_status, CheckResult(CheckLevel.UNKNOWN, "Checking with Nexus…")
        )
        # Keep a reference so the worker's signals object is not garbage-collected
        # mid-flight; the network call runs on the global thread pool.
        self._api_worker = _ApiCheckWorker(key)
        self._api_worker.signals.done.connect(self._on_api_checked)
        QThreadPool.globalInstance().start(self._api_worker)

    def _on_api_checked(self, result: CheckResult) -> None:
        self._apply_status(self._api_status, result)
        self._check_button.setEnabled(True)
        self._api_worker = None

    def _on_save(self) -> None:
        self._config.game_path = self._game_edit.text().strip() or None
        self._config.vault_path = self._vault_edit.text().strip() or None
        save_config(self._config)
        set_nexus_api_key(self._api_edit.text())
        self.accept()

    def config(self) -> AppConfig:
        """The config as saved (valid only after the dialog is accepted)."""
        return self._config

    # -- helpers ----------------------------------------------------------- #

    def _apply_status(self, label: QLabel, result: CheckResult) -> None:
        label.setText(result.message)
        label.setProperty("class", _STATUS_CLASS[result.level])
        style = label.style()
        style.unpolish(label)
        style.polish(label)
