"""Grade-table integrity and the student's explicit zero rating."""
import copy
import unittest

from src.grading import load_reviews, validate_reviews


class GradingTests(unittest.TestCase):
    def setUp(self):
        self.rows = load_reviews()

    def test_zero_rating_is_retained_with_its_actual_origin(self):
        row = next(r for r in self.rows if r["case_id"] == "A-s01")
        self.assertEqual(int(row["score"]), 0)
        self.assertIn("Nguyễn Tuấn Hiếu", row["reviewer"])
        self.assertIn("Codex", row["reviewer"])
        self.assertEqual(len(self.rows), 90)

    def test_duplicate_or_missing_case_cannot_appear_complete(self):
        for invalid in (self.rows[:-1], [*self.rows, self.rows[0]]):
            with self.assertRaises(ValueError):
                validate_reviews(invalid)

    def test_missing_reason_or_wrong_strategy_is_rejected(self):
        for key, value in (("reason", ""), ("strategy", "B")):
            invalid = copy.deepcopy(self.rows)
            invalid[0][key] = value
            with self.assertRaises(ValueError):
                validate_reviews(invalid)


if __name__ == "__main__":
    unittest.main()
