from __future__ import annotations

import sys

from PyQt6.QtWidgets import QApplication

from app.ui.main_window import MainWindow
from app.ui.theme.manager import ThemeManager, load_fonts


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("Witcher 3 Mod Manager")
    app.setOrganizationName("W3MM")
    load_fonts()

    theme_manager = ThemeManager(app)
    theme_manager.apply_dark()
    #apply fusion theme
    app.setStyle("Fusion")


    window = MainWindow(theme_manager)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
