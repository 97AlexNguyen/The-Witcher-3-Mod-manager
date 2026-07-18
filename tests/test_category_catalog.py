from __future__ import annotations

import unittest

from app.data import load_category_catalog
from app.ui.theme.tokens import CATEGORY_COLORS


class CategoryCatalogTest(unittest.TestCase):
    def setUp(self) -> None:
        self.catalog = load_category_catalog()

    def test_skips_taxonomy_root(self) -> None:
        names = {category.name for category in self.catalog}
        self.assertNotIn("The Witcher 3", names)

    def test_includes_expected_categories(self) -> None:
        names = {category.name for category in self.catalog}
        self.assertIn("Visuals and Graphics", names)
        self.assertIn("Bug Fixes", names)
        self.assertIn("Quests and Adventures", names)

    def test_appends_uncategorized_home(self) -> None:
        uncategorized = [c for c in self.catalog if c.key == "uncategorized"]
        self.assertEqual(len(uncategorized), 1)
        self.assertTrue(uncategorized[0].built_in)
        self.assertIs(self.catalog[-1], uncategorized[0])

    def test_keys_are_unique_slugs(self) -> None:
        keys = [category.key for category in self.catalog]
        self.assertEqual(len(keys), len(set(keys)))
        graphics = next(c for c in self.catalog if c.name == "Visuals and Graphics")
        self.assertEqual(graphics.key, "visuals-and-graphics")

    def test_colors_are_from_the_palette_and_deterministic(self) -> None:
        for category in self.catalog:
            self.assertIn(category.color_key, CATEGORY_COLORS)
        self.assertEqual(
            [c.color_key for c in self.catalog],
            [c.color_key for c in load_category_catalog()],
        )


if __name__ == "__main__":
    unittest.main()
