from __future__ import annotations

import unittest

from app.nexus_metadata import (
    _build_metadata,
    extract_mod_id_candidates,
    find_matching_file,
)


class NexusMetadataMatchingTests(unittest.TestCase):
    def test_extracts_numeric_candidates_without_interpreting_versions(self) -> None:
        filename = "lambert_npc 12580 1 2026-07-18T06-40Z kQW7gSUuQ.zip"
        self.assertEqual(
            extract_mod_id_candidates(filename), (12580, 1, 2026, 7, 18, 6, 40)
        )

    def test_matches_the_entire_archive_name_case_insensitively(self) -> None:
        files = [
            {"file_name": "other 12580 1.zip"},
            {"file_name": "lambert_npc 12580 1 2026-07-18T06-40Z kQW7gSUuQ.zip"},
        ]
        matched = find_matching_file(
            "LAMBERT_NPC 12580 1 2026-07-18T06-40Z KQW7GSUUQ.ZIP", files
        )
        self.assertIs(matched, files[1])

    def test_accepts_an_extensionless_name_only_when_unique(self) -> None:
        files = [{"file_name": "lambert_npc 12580 1.zip"}]
        self.assertIs(
            find_matching_file("lambert_npc 12580 1", files), files[0]
        )

    def test_keeps_the_adult_content_flag_from_mod_metadata(self) -> None:
        metadata = _build_metadata(
            "example 12580.zip",
            12580,
            {"name": "Example", "contains_adult_content": True},
            {"file_id": 1, "file_name": "example 12580.zip"},
        )
        self.assertTrue(metadata.contains_adult_content)


if __name__ == "__main__":
    unittest.main()
