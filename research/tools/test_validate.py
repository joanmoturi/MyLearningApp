"""Focused negative checks for research integrity, using isolated temporary fixtures."""

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from validate import DATA_FILES, ROOT, validate


class ResearchIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="engineering-academy-validation-")
        self.root = Path(self.directory.name)
        (self.root / "schemas").mkdir()
        shutil.copy2(ROOT / "schemas" / "package.schema.json", self.root / "schemas" / "package.schema.json")
        for name in DATA_FILES:
            shutil.copy2(ROOT / name, self.root / name)

    def tearDown(self):
        self.directory.cleanup()

    def change(self, name, mutation):
        path = self.root / name
        data = json.loads(path.read_text(encoding="utf-8"))
        mutation(data)
        path.write_text(json.dumps(data), encoding="utf-8")

    def test_unresolved_video_reference_is_rejected(self):
        self.change("CURRICULUM_14_DAYS.json", lambda d: d["curricula"][0]["lessons"][0].update(recommended_youtube_resource_id="resource-does-not-exist"))
        report = validate(self.root)
        self.assertEqual(report["status"], "failed")
        self.assertTrue(any("Unresolved" in error for error in report["errors"]))

    def test_hidden_extra_time_and_forward_prerequisite_are_rejected(self):
        def mutate(data):
            lessons = data["curricula"][0]["lessons"]
            lessons[0]["time_budget_minutes"]["implementation"] += 30
            lessons[0]["prerequisites"]["lesson_ids"] = [lessons[2]["id"]]
        self.change("CURRICULUM_30_DAYS.json", mutate)
        report = validate(self.root)
        self.assertEqual(report["status"], "failed")
        self.assertTrue(any("Time sum mismatch" in error for error in report["errors"]))
        self.assertTrue(any("Out-of-order lesson prerequisite" in error for error in report["errors"]))

    def test_invented_frequency_and_unsupported_feedback_score_are_rejected(self):
        self.change("JOB_MARKET_SKILLS_MATRIX.json", lambda d: d["skills"][0].update(sample_mention_count=999))
        self.change("RESOURCE_CATALOG.json", lambda d: d["resources"][0]["score_breakdown"].update(community_feedback=10))
        report = validate(self.root)
        self.assertEqual(report["status"], "failed")
        self.assertTrue(any("Frequency mismatch" in error for error in report["errors"]))
        self.assertTrue(any("Unsupported community score" in error for error in report["errors"]))


if __name__ == "__main__":
    unittest.main()
