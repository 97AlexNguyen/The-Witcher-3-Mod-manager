from __future__ import annotations

from PyQt6.QtCore import QByteArray, QSettings, Qt
from PyQt6.QtGui import QCloseEvent
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QMainWindow, QPushButton, QVBoxLayout, QWidget

from app.ui.pages import ModManagerPage
from app.ui.theme import ThemeManager
from app.ui.theme.tokens import SPACING_LG, SPACING_MD, SPACING_SM


class MainWindow(QMainWindow):
    def __init__(self, theme_manager: ThemeManager) -> None:
        super().__init__()
        self._theme_manager = theme_manager
        self._settings = QSettings()
        self.setWindowTitle("Witcher 3 Mod Manager")
        self.setMinimumSize(1100, 680)
        self.resize(1440, 860)
        self._build_ui()
        self._restore_geometry()

    def _build_ui(self) -> None:
        root = QWidget()
        root.setObjectName("appRoot")
        layout = QVBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QFrame()
        header.setObjectName("appHeader")
        header.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        header.setFixedHeight(88)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(SPACING_LG, 0, SPACING_LG, 0)
        header_layout.setSpacing(SPACING_MD)

        brand_mark = QLabel("W3")
        brand_mark.setObjectName("brandMark")
        brand_mark.setFixedSize(44, 44)
        brand_mark.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(brand_mark)

        brand_text = QVBoxLayout()
        brand_text.setSpacing(0)
        title = QLabel("WITCHER 3 MOD MANAGER")
        title.setProperty("class", "headline-md")
        subtitle = QLabel("Local mod library and load-order workspace")
        subtitle.setProperty("class", "muted")
        brand_text.addWidget(title)
        brand_text.addWidget(subtitle)
        header_layout.addLayout(brand_text)
        header_layout.addStretch()

        install_button = QPushButton("+  INSTALL MOD")
        install_button.setProperty("class", "primary")
        install_button.setToolTip("The install flow will be connected in a later phase")
        header_layout.addWidget(install_button)
        self.theme_button = QPushButton("LIGHT MODE" if self._theme_manager.is_dark else "DARK MODE")
        self.theme_button.setProperty("class", "ghost")
        self.theme_button.clicked.connect(self._theme_manager.toggle)
        self._theme_manager.theme_changed.connect(self._theme_changed)
        header_layout.addWidget(self.theme_button)
        settings_button = QPushButton("SETTINGS")
        settings_button.setToolTip("Settings navigation will be connected when the app shell grows")
        header_layout.addWidget(settings_button)
        layout.addWidget(header)

        self.mod_manager_page = ModManagerPage(self._settings)
        layout.addWidget(self.mod_manager_page, 1)
        self.setCentralWidget(root)
        self._theme_changed(self._theme_manager.is_dark)

    def _theme_changed(self, dark: bool) -> None:
        self.theme_button.setText("LIGHT MODE" if dark else "DARK MODE")
        self.mod_manager_page.card_list.setProperty("darkTheme", dark)
        self.mod_manager_page.card_list.viewport().update()

    def _restore_geometry(self) -> None:
        geometry = self._settings.value("window/geometry")
        if isinstance(geometry, QByteArray):
            self.restoreGeometry(geometry)

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        self.mod_manager_page.save_state()
        self._settings.setValue("window/geometry", self.saveGeometry())
        self._settings.sync()
        super().closeEvent(event)
