from __future__ import annotations

import unittest
from dataclasses import replace

from PyQt6.QtCore import QItemSelectionModel, QMimeData, QPoint, QPointF, QSettings, Qt, QUrl
from PyQt6.QtGui import QDropEvent
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
        self.assertEqual(page.splitter.count(), 2)
        page.close()
        settings.clear()

    def test_result_count_reports_total_when_filtered(self) -> None:
        page, settings = self.make_page("result-total")
        page.filter_bar.search_input.setText("ghost")
        self.app.processEvents()
        self.assertEqual(page.result_label.text(), "1 of 5 shown")
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
        self.assertEqual(page.result_label.text(), "2 of 5 shown")
        page.close()
        settings.clear()

    def test_selection_drives_detail_panel(self) -> None:
        page, settings = self.make_page("detail-selection")
        index = page.proxy.index(0, 0)
        page.card_list.selectionModel().select(index, QItemSelectionModel.SelectionFlag.ClearAndSelect)
        self.app.processEvents()
        selected_mod = index.data(InstalledModRoles.MOD)
        self.assertIs(page.detail_panel.current_mod, selected_mod)
        self.assertEqual(page.detail_panel.name_label.text(), selected_mod.name)
        page.close()
        settings.clear()

    def test_detail_category_edit_updates_mock_model(self) -> None:
        page, settings = self.make_page("detail-edits")
        index = page.proxy.index(0, 0)
        page.card_list.selectionModel().select(index, QItemSelectionModel.SelectionFlag.ClearAndSelect)
        self.app.processEvents()
        mod = page.detail_panel.current_mod
        page.detail_panel.category_combo.setCurrentIndex(page.detail_panel.category_combo.findData("gameplay"))
        self.app.processEvents()
        self.assertEqual(mod.category_key, "gameplay")
        page.close()
        settings.clear()

    def test_detail_panel_exposes_no_mod_mutating_controls(self) -> None:
        page, settings = self.make_page("detail-lean")
        self.select_first(page)
        panel = page.detail_panel
        # Category is the only thing the panel may change; priority and enablement are
        # owned by game config and the card respectively.
        for gone in ("priority_spin", "enable_button", "state_label", "health_label"):
            self.assertFalse(hasattr(panel, gone), f"{gone} should be gone from the detail panel")
        for gone_signal in ("priority_changed", "enabled_changed"):
            self.assertFalse(hasattr(panel, gone_signal), f"{gone_signal} should be gone")
        self.assertTrue(hasattr(panel, "category_combo"))
        page.close()
        settings.clear()

    def test_priority_is_shown_read_only_in_the_meta_block(self) -> None:
        page, settings = self.make_page("priority-readonly")
        self.select_first(page)
        mod = page.detail_panel.current_mod
        self.assertEqual(page.detail_panel.priority_label.text(), f"Priority: {mod.priority}")

        page.mod_model.set_priority(mod, None)
        self.app.processEvents()
        self.assertEqual(page.detail_panel.priority_label.text(), "Priority: Unassigned")
        page.close()
        settings.clear()

    def test_multi_selection_shows_bulk_summary(self) -> None:
        page, settings = self.make_page("detail-multi")
        selection = page.card_list.selectionModel()
        selection.select(page.proxy.index(0, 0), QItemSelectionModel.SelectionFlag.ClearAndSelect)
        selection.select(page.proxy.index(1, 0), QItemSelectionModel.SelectionFlag.Select)
        self.app.processEvents()
        self.assertIsNone(page.detail_panel.current_mod)
        self.assertEqual(page.detail_panel.multi_title.text(), "2 MODS SELECTED")
        page.close()
        settings.clear()

    def test_detail_segment_switches_content_section(self) -> None:
        page, settings = self.make_page("detail-sections")
        page.card_list.selectionModel().select(
            page.proxy.index(1, 0),
            QItemSelectionModel.SelectionFlag.ClearAndSelect,
        )
        self.app.processEvents()
        page.detail_panel.segment_group.button(2).click()
        self.app.processEvents()
        self.assertEqual(page.detail_panel.section_stack.currentIndex(), 2)
        self.assertIn("Toggle HUD", page.detail_panel.section_labels[2].text())
        page.close()
        settings.clear()

    def select_first(self, page):
        index = page.proxy.index(0, 0)
        page.card_list.selectionModel().select(index, QItemSelectionModel.SelectionFlag.ClearAndSelect)
        page.card_list.setCurrentIndex(index)
        self.app.processEvents()
        return index

    def test_editing_a_mod_out_of_the_active_filter_keeps_it_visible(self) -> None:
        page, settings = self.make_page("edit-out-of-filter")
        page.filter_bar.category_combo.setCurrentIndex(page.filter_bar.category_combo.findData("gameplay"))
        self.app.processEvents()
        self.select_first(page)
        mod = page.detail_panel.current_mod
        page.detail_panel.category_combo.setCurrentIndex(page.detail_panel.category_combo.findData("graphics"))
        self.app.processEvents()

        self.assertEqual(mod.category_key, "graphics")
        # The row the user was editing must survive, keep its selection, and explain itself.
        self.assertIs(page.detail_panel.current_mod, mod)
        self.assertIn(mod, [page.proxy.index(r, 0).data(InstalledModRoles.MOD) for r in range(page.proxy.rowCount())])
        self.assertTrue(page.card_list.selectionModel().selectedIndexes())
        self.assertTrue(page.notice_label.isVisible())
        self.assertIn("no longer matches", page.notice_label.text())
        page.close()
        settings.clear()

    def pin_a_mod_out_of_filter(self, page):
        page.filter_bar.category_combo.setCurrentIndex(page.filter_bar.category_combo.findData("gameplay"))
        self.app.processEvents()
        self.select_first(page)
        mod = page.detail_panel.current_mod
        page.detail_panel.category_combo.setCurrentIndex(page.detail_panel.category_combo.findData("graphics"))
        self.app.processEvents()
        return mod

    def visible_mods(self, page):
        return [page.proxy.index(r, 0).data(InstalledModRoles.MOD) for r in range(page.proxy.rowCount())]

    def test_pin_is_dropped_when_a_different_filter_is_chosen(self) -> None:
        page, settings = self.make_page("pin-drop")
        mod = self.pin_a_mod_out_of_filter(page)
        page.filter_bar.category_combo.setCurrentIndex(page.filter_bar.category_combo.findData("interface"))
        self.app.processEvents()
        self.assertNotIn(mod, self.visible_mods(page))
        self.assertFalse(page.notice_label.isVisible())
        page.close()
        settings.clear()

    def test_pin_is_dropped_when_the_same_category_is_re_picked(self) -> None:
        page, settings = self.make_page("pin-repick")
        mod = self.pin_a_mod_out_of_filter(page)
        self.assertIn(mod, self.visible_mods(page))
        # Re-picking "Gameplay" emits activated but not currentIndexChanged.
        page.filter_bar.category_combo.activated.emit(page.filter_bar.category_combo.currentIndex())
        self.app.processEvents()
        self.assertNotIn(mod, self.visible_mods(page))
        self.assertFalse(page.notice_label.isVisible())
        page.close()
        settings.clear()

    def test_empty_library_and_filtered_empty_states_differ(self) -> None:
        page, settings = self.make_page("empty-states")
        page.filter_bar.search_input.setText("zzzz-no-such-mod")
        self.app.processEvents()
        self.assertIs(page.content_stack.currentWidget(), page.empty_filtered)

        page.filter_bar.search_input.clear()
        page.mod_model.beginResetModel()
        page.mod_model._mods.clear()
        page.mod_model.endResetModel()
        self.app.processEvents()
        self.assertIs(page.content_stack.currentWidget(), page.empty_library)
        page.close()
        settings.clear()

    def test_detail_panel_follows_external_model_changes(self) -> None:
        page, settings = self.make_page("panel-sync")
        self.select_first(page)
        mod = page.detail_panel.current_mod
        page.mod_model.set_priority(mod, 777)
        self.app.processEvents()
        self.assertEqual(page.detail_panel.priority_label.text(), "Priority: 777")

        page.mod_model.set_category(mod, "interface")
        self.app.processEvents()
        self.assertEqual(page.detail_panel.category_combo.currentData(), "interface")
        page.close()
        settings.clear()

    def test_keyboard_space_toggles_and_enter_focuses_details(self) -> None:
        page, settings = self.make_page("keyboard")
        index = self.select_first(page)
        page.card_list.setFocus()
        mod = index.data(InstalledModRoles.MOD)
        original = mod.enabled
        QTest.keyClick(page.card_list, Qt.Key.Key_Space)
        self.app.processEvents()
        self.assertEqual(mod.enabled, not original)

        page.detail_panel.show_selection([])
        QTest.keyClick(page.card_list, Qt.Key.Key_Return)
        self.app.processEvents()
        self.assertIs(page.detail_panel.current_mod, mod)
        page.close()
        settings.clear()

    def test_card_exposes_only_toggle_and_remove_actions(self) -> None:
        page, settings = self.make_page("card-actions")
        delegate = page.card_list.itemDelegate()
        card = page.card_list.visualRect(page.proxy.index(0, 0))
        self.assertEqual(len(delegate._action_rects(card)), 2)
        self.assertFalse(hasattr(delegate, "details_requested"))
        page.close()
        settings.clear()

    def test_detail_panel_can_be_collapsed_but_card_list_cannot(self) -> None:
        page, settings = self.make_page("collapsible")
        self.assertTrue(page.splitter.isCollapsible(1))
        self.assertFalse(page.splitter.isCollapsible(0))
        page.close()
        settings.clear()

    def test_keyboard_delete_surfaces_remove_feedback(self) -> None:
        page, settings = self.make_page("keyboard-delete")
        index = self.select_first(page)
        page.card_list.setFocus()
        mod = index.data(InstalledModRoles.MOD)
        QTest.keyClick(page.card_list, Qt.Key.Key_Delete)
        self.app.processEvents()
        self.assertTrue(page.notice_label.isVisible())
        self.assertIn(mod.name, page.notice_label.text())
        page.close()
        settings.clear()

    def test_dropping_archives_is_accepted_and_acknowledged(self) -> None:
        page, settings = self.make_page("drop")
        self.assertTrue(page.acceptDrops())
        received: list[list[str]] = []
        page.archives_dropped.connect(received.append)

        mime = QMimeData()
        mime.setUrls([QUrl.fromLocalFile("C:/tmp/cool_mod.zip"), QUrl.fromLocalFile("C:/tmp/other.7z")])
        event = QDropEvent(
            QPointF(20, 20),
            Qt.DropAction.CopyAction,
            mime,
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier,
        )
        page.dropEvent(event)
        self.app.processEvents()
        self.assertTrue(event.isAccepted())
        self.assertEqual(received, [["C:/tmp/cool_mod.zip", "C:/tmp/other.7z"]])
        self.assertTrue(page.notice_label.isVisible())
        page.close()
        settings.clear()

    def test_dropping_a_non_archive_is_rejected(self) -> None:
        page, settings = self.make_page("drop-reject")
        mime = QMimeData()
        mime.setUrls([QUrl.fromLocalFile("C:/tmp/notes.txt")])
        event = QDropEvent(
            QPointF(20, 20),
            Qt.DropAction.CopyAction,
            mime,
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier,
        )
        page.dropEvent(event)
        self.app.processEvents()
        self.assertFalse(event.isAccepted())
        self.assertFalse(page.notice_label.isVisible())
        page.close()
        settings.clear()


class ModelLookupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QApplication.instance() or QApplication([])

    def test_row_lookup_uses_object_identity_not_value_equality(self) -> None:
        mods = make_mock_mods()
        twin = replace(mods[0])
        model = InstalledModListModel([twin, *mods])
        # twin compares equal to mods[0]; the lookup must still find the real object.
        self.assertEqual(twin, mods[0])
        self.assertEqual(model.row_for(mods[0]), 1)
        self.assertEqual(model.row_for(twin), 0)

        model.set_priority(mods[0], 123)
        self.assertEqual(mods[0].priority, 123)
        self.assertNotEqual(twin.priority, 123)

    def test_row_lookup_reports_unknown_mods(self) -> None:
        mods = make_mock_mods()
        model = InstalledModListModel(mods[1:])
        self.assertEqual(model.row_for(mods[0]), -1)
        self.assertFalse(model.set_priority(mods[0], 5))
        self.assertFalse(model.set_category(mods[0], "graphics"))


if __name__ == "__main__":
    unittest.main()
