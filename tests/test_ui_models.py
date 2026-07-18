from __future__ import annotations

import unittest
from dataclasses import replace

from PyQt6.QtCore import QEvent, QMimeData, QPoint, QPointF, QRect, QSettings, Qt, QUrl
from PyQt6.QtGui import QColor, QDropEvent, QFont, QFontMetrics, QMouseEvent
from PyQt6.QtTest import QTest
from PyQt6.QtWidgets import QApplication

from app.data import make_mock_categories, make_mock_mods
from app.ui.models import InstalledModListModel, InstalledModRoles
from app.ui.pages import ModManagerPage
from app.ui.widgets.mod_card import _wrap_elided


class ModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self) -> None:
        self.mods = make_mock_mods()
        self.model = InstalledModListModel(self.mods)

    def test_categories_are_single_assignment(self) -> None:
        keys = {category.key for category in make_mock_categories() if category.key != "all"}
        self.assertTrue(all(mod.category_key in keys for mod in self.mods))

    def test_toggle_updates_only_in_memory(self) -> None:
        index = self.model.index(0, 0)
        original = bool(index.data(InstalledModRoles.ENABLED))
        self.assertTrue(self.model.setData(index, not original, InstalledModRoles.ENABLED))
        self.assertEqual(bool(index.data(InstalledModRoles.ENABLED)), not original)

    def test_set_category_moves_mod(self) -> None:
        mod = self.mods[0]
        self.assertTrue(self.model.set_category(mod, "interface"))
        self.assertEqual(mod.category_key, "interface")


class ModelLookupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QApplication.instance() or QApplication([])

    def test_row_lookup_uses_object_identity_not_value_equality(self) -> None:
        mods = make_mock_mods()
        twin = replace(mods[0])
        model = InstalledModListModel([twin, *mods])
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


class ElisionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QApplication.instance() or QApplication([])

    def _metrics(self) -> QFontMetrics:
        font = QFont()
        font.setPointSize(14)
        return QFontMetrics(font)

    def test_long_name_never_overflows_the_box(self) -> None:
        fm = self._metrics()
        text = "Brothers in Arms - TW3 Bug Fix Collection Extended Deluxe Ultra Edition"
        wrapped = _wrap_elided(fm, text, 220, 2)
        lines = wrapped.split("\n")
        self.assertLessEqual(len(lines), 2)
        for line in lines:
            self.assertLessEqual(fm.horizontalAdvance(line), 220)
        self.assertTrue(wrapped.endswith("…"))

    def test_short_name_is_left_intact(self) -> None:
        fm = self._metrics()
        wrapped = _wrap_elided(fm, "Ghost Mode", 220, 2)
        self.assertEqual(wrapped, "Ghost Mode")

    def test_single_overlong_word_is_elided_not_clipped(self) -> None:
        fm = self._metrics()
        wrapped = _wrap_elided(fm, "Supercalifragilisticexpialidociousmodnamewithnospaces", 120, 2)
        for line in wrapped.split("\n"):
            self.assertLessEqual(fm.horizontalAdvance(line), 120)


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

    def tearDownPage(self, page: ModManagerPage, settings: QSettings) -> None:
        page.close()
        settings.clear()

    def test_canvas_has_one_box_per_real_category(self) -> None:
        page, settings = self.make_page("canvas")
        self.assertEqual(set(page.boxes), {"graphics", "gameplay", "interface", "uncategorized"})
        self.assertNotIn("all", page.boxes)
        self.assertEqual(page.splitter.count(), 2)
        self.tearDownPage(page, settings)

    def test_boxes_are_embedded_as_items_in_the_node_canvas(self) -> None:
        page, settings = self.make_page("freeform-workspace")
        self.assertIs(page.splitter.widget(0), page.box_workspace)
        self.assertIs(page.splitter.widget(1), page.detail_panel)
        self.assertEqual(page.box_workspace.box_count(), 4)
        self.assertTrue(all(box.graphicsProxyWidget() is not None for box in page.boxes.values()))
        self.tearDownPage(page, settings)

    def test_box_header_stats_reflect_the_model(self) -> None:
        page, settings = self.make_page("stats")
        self.assertIn("2 mods", page.boxes["gameplay"].stats_label.text())
        self.assertIn("1 mod", page.boxes["graphics"].stats_label.text())
        self.assertIn("1", page.boxes["uncategorized"].attention_label.text())
        self.assertIn("need attention", page.boxes["uncategorized"].attention_label.toolTip())
        self.tearDownPage(page, settings)

    def test_box_can_collapse_to_stats_only(self) -> None:
        page, settings = self.make_page("collapse")
        box = page.boxes["gameplay"]
        box.collapse_button.click()
        self.app.processEvents()
        self.assertTrue(box.is_collapsed)
        self.assertFalse(box.body.isVisible())
        self.assertTrue(box.stats_label.isVisible())
        box.collapse_button.click()
        self.app.processEvents()
        self.assertFalse(box.is_collapsed)
        self.assertTrue(box.body.isVisible())
        self.tearDownPage(page, settings)

    def test_one_box_can_move_and_resize_without_affecting_another(self) -> None:
        page, settings = self.make_page("independent-geometry")
        graphics = page.boxes["graphics"]
        gameplay_before = page.box_workspace.box_geometry("gameplay")
        page.box_workspace.set_box_geometry("graphics", QRect(72, 84, 680, 520))
        self.app.processEvents()
        self.assertEqual(page.box_workspace.box_geometry("graphics"), QRect(72, 84, 680, 520))
        self.assertEqual(page.box_workspace.box_geometry("gameplay"), gameplay_before)
        self.tearDownPage(page, settings)

    def test_canvas_zoom_is_bounded_and_changes_the_view_transform(self) -> None:
        page, settings = self.make_page("canvas-zoom")
        canvas = page.box_workspace
        canvas.set_zoom(1.0)
        canvas.zoom_by(canvas.ZOOM_STEP)
        self.app.processEvents()
        self.assertAlmostEqual(canvas.zoom_factor, canvas.ZOOM_STEP)
        self.assertAlmostEqual(canvas.transform().m11(), canvas.ZOOM_STEP)
        canvas.set_zoom(100.0)
        self.assertEqual(canvas.zoom_factor, canvas.MAX_ZOOM)
        canvas.set_zoom(0.01)
        self.assertEqual(canvas.zoom_factor, canvas.MIN_ZOOM)
        self.tearDownPage(page, settings)

    def test_arrange_boxes_creates_a_compact_non_overlapping_layout(self) -> None:
        page, settings = self.make_page("canvas-arrange")
        canvas = page.box_workspace
        original_sizes = {key: box.size() for key, box in page.boxes.items()}
        for key in page.boxes:
            canvas.set_box_geometry(key, QRect(100, 100, original_sizes[key].width(), original_sizes[key].height()))

        canvas.arrange_button.click()
        self.app.processEvents()
        geometries = [canvas.box_geometry(key) for key in page.boxes]
        for index, geometry in enumerate(geometries):
            self.assertEqual(geometry.size(), original_sizes[list(page.boxes)[index]])
            for other in geometries[index + 1:]:
                self.assertFalse(geometry.intersects(other))
        self.assertGreater(len({geometry.y() for geometry in geometries}), 1)
        self.tearDownPage(page, settings)

    def test_middle_mouse_drag_pans_the_canvas_camera(self) -> None:
        page, settings = self.make_page("canvas-pan")
        canvas = page.box_workspace
        before = canvas.camera_center()
        start = QPointF(240, 220)
        end = QPointF(320, 280)
        canvas.mousePressEvent(QMouseEvent(
            QEvent.Type.MouseButtonPress, start, start,
            Qt.MouseButton.MiddleButton, Qt.MouseButton.MiddleButton,
            Qt.KeyboardModifier.NoModifier,
        ))
        canvas.mouseMoveEvent(QMouseEvent(
            QEvent.Type.MouseMove, end, end,
            Qt.MouseButton.NoButton, Qt.MouseButton.MiddleButton,
            Qt.KeyboardModifier.NoModifier,
        ))
        canvas.mouseReleaseEvent(QMouseEvent(
            QEvent.Type.MouseButtonRelease, end, end,
            Qt.MouseButton.MiddleButton, Qt.MouseButton.NoButton,
            Qt.KeyboardModifier.NoModifier,
        ))
        self.app.processEvents()
        self.assertNotEqual(canvas.camera_center(), before)
        self.tearDownPage(page, settings)

    def test_drag_and_resize_handles_change_only_their_box_geometry(self) -> None:
        page, settings = self.make_page("mouse-geometry")
        box = page.boxes["graphics"]
        other_before = page.box_workspace.box_geometry("gameplay")

        canvas = page.box_workspace
        handle = box.drag_handle
        handle_center = handle.mapTo(box, handle.rect().center())
        start_scene = box.graphicsProxyWidget().mapToScene(QPointF(handle_center))
        start = QPointF(canvas.mapFromScene(start_scene))
        global_pos = QPointF(canvas.viewport().mapToGlobal(start.toPoint()))
        canvas.mousePressEvent(QMouseEvent(
            QEvent.Type.MouseButtonPress, start, global_pos,
            Qt.MouseButton.LeftButton, Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier,
        ))
        for delta in (QPointF(20, 16), QPointF(48, 36), QPointF(80, 60)):
            canvas.mouseMoveEvent(QMouseEvent(
                QEvent.Type.MouseMove, start + delta, global_pos + delta,
                Qt.MouseButton.NoButton, Qt.MouseButton.LeftButton,
                Qt.KeyboardModifier.NoModifier,
            ))
        canvas.mouseReleaseEvent(QMouseEvent(
            QEvent.Type.MouseButtonRelease, start + QPointF(80, 60), global_pos + QPointF(80, 60),
            Qt.MouseButton.LeftButton, Qt.MouseButton.NoButton,
            Qt.KeyboardModifier.NoModifier,
        ))
        self.assertEqual(page.box_workspace.box_geometry("graphics").topLeft(), QPointF(104, 84).toPoint())

        resize = box.resize_handle
        local = QPointF(resize.rect().center())
        global_pos = QPointF(resize.mapToGlobal(resize.rect().center()))
        before_size = box.size()
        resize.mousePressEvent(QMouseEvent(
            QEvent.Type.MouseButtonPress, local, global_pos,
            Qt.MouseButton.LeftButton, Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier,
        ))
        resize.mouseMoveEvent(QMouseEvent(
            QEvent.Type.MouseMove, local, global_pos + QPointF(120, 80),
            Qt.MouseButton.NoButton, Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier,
        ))
        resize.mouseReleaseEvent(QMouseEvent(
            QEvent.Type.MouseButtonRelease, local, global_pos + QPointF(120, 80),
            Qt.MouseButton.LeftButton, Qt.MouseButton.NoButton,
            Qt.KeyboardModifier.NoModifier,
        ))
        self.assertEqual(box.width(), before_size.width() + 120)
        self.assertEqual(box.height(), before_size.height() + 80)
        self.assertEqual(page.box_workspace.box_geometry("gameplay"), other_before)
        self.tearDownPage(page, settings)

    def test_boxes_show_their_cards_immediately(self) -> None:
        page, settings = self.make_page("cards")
        self.assertEqual(page.boxes["gameplay"].flow.count(), 2)
        self.assertEqual(page.boxes["graphics"].flow.count(), 1)
        self.tearDownPage(page, settings)

    def test_dropping_a_mod_recategorizes_and_updates_all_views(self) -> None:
        page, settings = self.make_page("drop-mod")
        page._on_mod_dropped("ghost-mode", "graphics")
        self.app.processEvents()

        self.assertEqual(page._mod_for_identity("ghost-mode").category_key, "graphics")
        self.assertEqual(page.boxes["gameplay"].flow.count(), 1)
        self.assertEqual(page.boxes["graphics"].flow.count(), 2)
        self.assertIn("1 mod", page.boxes["gameplay"].stats_label.text())
        self.assertIn("2 mods", page.boxes["graphics"].stats_label.text())
        self.assertFalse(page.notice_label.isVisible())
        self.tearDownPage(page, settings)

    def test_dragging_a_card_between_canvas_boxes_recategorizes_it(self) -> None:
        page, settings = self.make_page("canvas-card-drag")
        canvas = page.box_workspace
        canvas.frame_all()
        source_box = page.boxes["gameplay"]
        target_box = page.boxes["graphics"]
        source_card = next(
            source_box.flow.itemAt(index).widget()
            for index in range(source_box.flow.count())
            if source_box.flow.itemAt(index).widget().mod.identity == "ghost-mode"
        )

        start_local = source_card.mapTo(source_box, QPoint(18, 18))
        start_scene = source_box.graphicsProxyWidget().mapToScene(QPointF(start_local))
        start = QPointF(canvas.mapFromScene(start_scene))
        target_local = target_box.scroll.viewport().mapTo(
            target_box,
            target_box.scroll.viewport().rect().center(),
        )
        target_scene = target_box.graphicsProxyWidget().mapToScene(QPointF(target_local))
        end = QPointF(canvas.mapFromScene(target_scene))
        QTest.mousePress(
            canvas.viewport(),
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier,
            start.toPoint(),
        )
        QTest.mouseMove(canvas.viewport(), end.toPoint(), 20)
        self.assertIsNotNone(canvas._card_drag_item)
        self.assertEqual(target_box.property("dropActive"), "true")

        QTest.mouseRelease(
            canvas.viewport(),
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier,
            end.toPoint(),
        )
        self.app.processEvents()

        self.assertEqual(page._mod_for_identity("ghost-mode").category_key, "graphics")
        self.assertEqual(target_box.property("dropActive"), "false")
        self.assertIsNone(canvas._card_drag_item)
        self.tearDownPage(page, settings)

    def test_card_menu_is_a_native_popup_anchored_after_pan_and_zoom(self) -> None:
        page, settings = self.make_page("canvas-card-menu")
        canvas = page.box_workspace
        box = page.boxes["graphics"]
        proxy = box.graphicsProxyWidget()
        canvas.set_zoom(1.6)
        canvas.centerOn(proxy.sceneBoundingRect().center())
        self.app.processEvents()
        card = box.flow.itemAt(0).widget()
        button_local = card.menu_button.mapTo(box, card.menu_button.rect().center())
        button_scene = proxy.mapToScene(QPointF(button_local))
        button_viewport = canvas.mapFromScene(button_scene)

        QTest.mouseClick(
            canvas.viewport(),
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier,
            button_viewport,
        )
        self.app.processEvents()

        menu = card._open_menu
        self.assertIsNotNone(menu)
        self.assertTrue(menu.isVisible())
        self.assertIs(menu.parentWidget(), canvas)
        self.assertIsNone(menu.graphicsProxyWidget())
        self.assertEqual(menu.pos(), card._menu_popup_position(menu))
        self.assertIsNone(canvas._card_drag_source)
        menu.close()
        self.app.processEvents()
        self.tearDownPage(page, settings)

    def test_dropping_onto_the_same_box_is_a_noop(self) -> None:
        page, settings = self.make_page("drop-same")
        before = page.boxes["gameplay"].flow.count()
        page._on_mod_dropped("ghost-mode", "gameplay")
        self.app.processEvents()
        self.assertEqual(page.boxes["gameplay"].flow.count(), before)
        self.assertFalse(page.notice_label.isVisible())
        self.tearDownPage(page, settings)

    def test_toggling_a_card_updates_the_model_and_keeps_the_card(self) -> None:
        page, settings = self.make_page("toggle")
        box = page.boxes["graphics"]
        card = box.flow.itemAt(0).widget()
        mod = card.mod
        before = mod.enabled
        card.toggle.click()
        self.app.processEvents()

        self.assertNotEqual(mod.enabled, before)
        row = page.mod_model.row_for(mod)
        self.assertEqual(bool(page.mod_model.index(row, 0).data(InstalledModRoles.ENABLED)), mod.enabled)
        # An enable toggle refreshes only the header, so the same card object survives.
        self.assertIs(box.flow.itemAt(0).widget(), card)
        self.tearDownPage(page, settings)

    def test_search_filters_within_a_box(self) -> None:
        page, settings = self.make_page("search")
        box = page.boxes["gameplay"]
        box.search_input.setText("ghost")
        self.app.processEvents()
        self.assertEqual(box.flow.count(), 1)
        self.tearDownPage(page, settings)

    def test_single_click_selection_drives_the_detail_panel(self) -> None:
        page, settings = self.make_page("details")
        card = page.boxes["interface"].flow.itemAt(0).widget()
        box = page.boxes["interface"]
        card_local = card.mapTo(box, card.rect().center())
        scene_position = box.graphicsProxyWidget().mapToScene(QPointF(card_local))
        viewport_position = page.box_workspace.mapFromScene(scene_position)
        QTest.mouseClick(
            page.box_workspace.viewport(),
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier,
            viewport_position,
        )
        self.app.processEvents()
        self.assertIs(page.detail_panel.current_mod, card.mod)
        self.assertEqual(page.detail_panel.name_label.text(), card.mod.name)
        self.assertEqual(card.property("selected"), "true")
        self.tearDownPage(page, settings)

    def test_each_box_color_with_alpha_round_trips(self) -> None:
        page, settings = self.make_page("box-color")
        expected = QColor(32, 96, 160, 88)
        page.boxes["graphics"].set_custom_color(expected)
        page.save_state()
        page.close()

        page2 = ModManagerPage(settings)
        page2.show()
        self.app.processEvents()
        actual = page2.boxes["graphics"].custom_color
        self.assertIsNotNone(actual)
        self.assertEqual(actual.rgba(), expected.rgba())
        page2.close()
        settings.clear()

    def test_detail_category_combo_recategorizes_through_the_model(self) -> None:
        page, settings = self.make_page("detail-cat")
        card = page.boxes["interface"].flow.itemAt(0).widget()
        card.details_requested.emit(card.mod)
        self.app.processEvents()
        mod = page.detail_panel.current_mod
        combo = page.detail_panel.category_combo
        combo.setCurrentIndex(combo.findData("gameplay"))
        self.app.processEvents()
        self.assertEqual(mod.category_key, "gameplay")
        self.assertIn(str(len(page._mods_in("gameplay"))), page.boxes["gameplay"].stats_label.text())
        self.tearDownPage(page, settings)

    def test_remove_is_acknowledged_but_not_wired(self) -> None:
        page, settings = self.make_page("remove")
        before = page.mod_model.rowCount()
        page._request_remove(page.mod_model.mod_at(0))
        self.app.processEvents()
        self.assertEqual(page.mod_model.rowCount(), before)
        self.assertTrue(page.notice_label.isVisible())
        self.assertIn("later phase", page.notice_label.text())
        self.tearDownPage(page, settings)

    def test_splitter_state_round_trips_without_error(self) -> None:
        page, settings = self.make_page("persist")
        page.save_state()
        page.close()

        page2 = ModManagerPage(settings)
        page2.show()
        self.app.processEvents()
        self.assertEqual(set(page2.boxes), {"graphics", "gameplay", "interface", "uncategorized"})
        page2.close()
        settings.clear()

    def test_box_geometry_and_collapsed_state_round_trip(self) -> None:
        page, settings = self.make_page("box-state")
        expected_geometry = QRect(96, 128, 692, 508)
        page.box_workspace.set_box_geometry("graphics", expected_geometry)
        expected_center = QPointF(340, -180)
        page.box_workspace.restore_view(1.6, expected_center)
        page.boxes["graphics"].set_collapsed(True)
        page.save_state()
        page.close()

        page2 = ModManagerPage(settings)
        page2.show()
        self.app.processEvents()
        restored = page2.boxes["graphics"]
        self.assertEqual(page2.box_workspace.box_geometry("graphics").topLeft(), expected_geometry.topLeft())
        self.assertTrue(page2.boxes["graphics"].is_collapsed)
        self.assertFalse(page2.boxes["gameplay"].is_collapsed)
        self.assertAlmostEqual(page2.box_workspace.zoom_factor, 1.6)
        restored_center = page2.box_workspace.camera_center()
        self.assertLess(abs(restored_center.x() - expected_center.x()), 2.0)
        self.assertLess(abs(restored_center.y() - expected_center.y()), 2.0)
        restored.set_collapsed(False)
        self.app.processEvents()
        self.assertEqual(restored.size(), expected_geometry.size())
        page2.close()
        settings.clear()

    def test_detail_pane_is_collapsible_but_grid_is_not(self) -> None:
        page, settings = self.make_page("collapsible")
        self.assertTrue(page.splitter.isCollapsible(1))
        self.assertFalse(page.splitter.isCollapsible(0))
        self.tearDownPage(page, settings)

    def test_dropping_archives_is_accepted_and_acknowledged(self) -> None:
        page, settings = self.make_page("drop-archive")
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
        self.tearDownPage(page, settings)

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
        self.tearDownPage(page, settings)


if __name__ == "__main__":
    unittest.main()
