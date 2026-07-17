from __future__ import annotations

import unittest

from PyQt6.QtCore import QPoint, QSettings, Qt
from PyQt6.QtTest import QTest
from PyQt6.QtWidgets import QApplication

from app.data import make_mock_categories, make_mock_mods
from app.ui.models import InstalledModListModel, InstalledModRoles, ModListFilterProxy, SortMode
from app.ui.pages import ModManagerPage
from app.ui.theme.tokens import SPACING_MD


class UiModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self) -> None:
        self.mods = make_mock_mods()
        self.source = InstalledModListModel(self.mods)
        self.proxy = ModListFilterProxy()
        self.proxy.setSourceModel(self.source)

    def test_category_and_search_filters_are_combined(self) -> None:
        self.proxy.set_category("gameplay")
        self.proxy.set_search_text("ghost")
        self.assertEqual(self.proxy.rowCount(), 1)
        self.assertEqual(self.proxy.index(0, 0).data(InstalledModRoles.MOD).identity, "ghost-mode")

    def test_search_includes_mod_description(self) -> None:
        self.proxy.set_search_text("blade oil")
        self.assertEqual(self.proxy.rowCount(), 1)
        self.assertEqual(self.proxy.index(0, 0).data(InstalledModRoles.MOD).identity, "auto-apply-oils")

    def test_sort_modes_use_domain_values(self) -> None:
        self.proxy.set_sort_mode(SortMode.PRIORITY, Qt.SortOrder.DescendingOrder)
        priorities = [
            self.proxy.index(row, 0).data(InstalledModRoles.MOD).priority
            for row in range(self.proxy.rowCount())
        ]
        self.assertEqual(priorities[:3], [20, 10, 5])
        self.assertEqual(priorities[-1], None)

    def test_categories_are_single_assignment(self) -> None:
        categories = {category.key for category in make_mock_categories() if category.key != "all"}
        self.assertTrue(all(mod.category_key in categories for mod in self.mods))

    def test_mock_toggle_updates_only_in_memory(self) -> None:
        index = self.source.index(0, 0)
        original = bool(index.data(InstalledModRoles.ENABLED))
        self.assertTrue(self.source.setData(index, not original, InstalledModRoles.ENABLED))
        self.assertEqual(bool(index.data(InstalledModRoles.ENABLED)), not original)


class ModManagerPageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QApplication.instance() or QApplication([])

    def make_page(self, name: str) -> tuple[ModManagerPage, QSettings]:
        settings = QSettings(QSettings.Format.IniFormat, QSettings.Scope.UserScope, "W3MM-Test", name)
        settings.clear()
        page = ModManagerPage(settings)
        page.resize(1200, 760)
        page.show()
        self.app.processEvents()
        return page, settings

    def test_dashboard_card_layout_can_be_constructed(self) -> None:
        page, settings = self.make_page("cards")
        self.assertEqual(page.mod_model.rowCount(), 5)
        self.assertEqual(page.proxy.rowCount(), 5)
        self.assertEqual(page.card_list.model(), page.proxy)
        self.assertEqual(page.result_label.text(), "5 shown")
        page.close()
        settings.clear()

    def test_card_delegate_toggle_action_handles_mouse_click(self) -> None:
        page, settings = self.make_page("toggle-card")
        index = page.proxy.index(0, 0)
        original = bool(index.data(InstalledModRoles.ENABLED))
        item_rect = page.card_list.visualRect(index)
        click_pos = QPoint(item_rect.right() - SPACING_MD - 66, item_rect.top() + SPACING_MD + 16)
        QTest.mouseClick(page.card_list.viewport(), Qt.MouseButton.LeftButton, pos=click_pos)
        self.app.processEvents()
        self.assertEqual(bool(index.data(InstalledModRoles.ENABLED)), not original)
        page.close()
        settings.clear()

    def test_result_count_follows_active_filter(self) -> None:
        page, settings = self.make_page("result-count")
        page.filter_bar.category_combo.setCurrentIndex(page.filter_bar.category_combo.findData("gameplay"))
        self.app.processEvents()
        self.assertEqual(page.result_label.text(), "2 shown")
        page.close()
        settings.clear()


if __name__ == "__main__":
    unittest.main()
