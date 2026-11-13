"""Regression checks for source coverage, leakage guards and evidence metrics."""
import json
import unittest
from pathlib import Path

from src.chunking import by_paragraph, fixed_size
from src.evaluation import evaluate_query, summarize
from src.models import DocumentPage
from src.run import check_frozen


class ChunkingTests(unittest.TestCase):
    def test_real_corpus_coverage_and_source_offsets(self):
        rows = Path("results/pages.jsonl").read_text(encoding="utf-8").splitlines()
        for row in rows:
            page = DocumentPage(**json.loads(row))
            for build in (lambda: fixed_size(page, 500, 50), lambda: by_paragraph(page, 500)):
                chunks = build()
                self.assertEqual(chunks, build())
                covered = set()
                for chunk in chunks:
                    start, end = chunk.metadata["start_char"], chunk.metadata["end_char"]
                    self.assertEqual(chunk.text, page.text[start:end])
                    self.assertLessEqual(len(chunk.text), 500)
                    self.assertEqual(chunk.metadata["chapter"], page.metadata["chapter"])
                    covered.update(range(start, end))
                self.assertTrue(all(i in covered for i, c in enumerate(page.text) if not c.isspace()))

    def test_invalid_overlap_cannot_hang(self):
        page = DocumentPage("d", "s", 1, "a" * 100)
        for overlap in (-1, 10, 11):
            with self.assertRaises(ValueError):
                fixed_size(page, 10, overlap)

    def test_oversized_unbroken_paragraph_and_unicode(self):
        page = DocumentPage("d", "s", 1, "đ" * 1100)
        chunks = by_paragraph(page, 500)
        self.assertEqual("".join(c.text for c in chunks), page.text)
        self.assertEqual([len(c.text) for c in chunks], [500, 500, 100])


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.q = {"id": "probe", "split": "dev", "question": "probe", "expected_answer": "probe",
            "gold_source_id": "d", "gold_page": 1, "evidence_quote": "full evidence",
            "gold_alternatives": [{"source_id": "d", "page": 2, "evidence_quote": "alternative proof"}]}

    def hit(self, page, text, document="d"):
        return {"document_id": document, "page": page, "text": text, "metadata": {},
                "chunk_id": "probe", "source": "s", "score": 0.9}

    def test_full_evidence_requires_source_page_and_single_chunk(self):
        for hits in ([self.hit(1, "full")], [self.hit(3, "full evidence")],
                     [self.hit(1, "full evidence", "other")],
                     [self.hit(1, "full"), self.hit(1, "evidence")]):
            self.assertFalse(evaluate_query(self.q, hits)["hit_at_3"])

    def test_alternative_and_whitespace(self):
        self.assertTrue(evaluate_query(self.q, [self.hit(2, "alternative\n proof")])["hit_at_1"])
        result = evaluate_query(self.q, [self.hit(1, "irrelevant"), self.hit(1, "full evidence")])
        self.assertFalse(result["hit_at_1"])
        self.assertTrue(result["hit_at_3"])

    def test_metrics_keep_split_denominators(self):
        a = evaluate_query(self.q, [self.hit(1, "full evidence")])
        b = evaluate_query({**self.q, "id": "test", "split": "test"}, [])
        rows = summarize([{**a, "strategy": "A", "search_seconds": .1},
                          {**b, "strategy": "A", "search_seconds": .1}])["rows"]
        self.assertEqual([(r["split"], r["hit3_n"], r["n"]) for r in rows], [("dev", 1, 1), ("test", 0, 1)])

    def test_frozen_inputs_still_match(self):
        self.assertFalse(check_frozen()["test_retrieval_seen"])


if __name__ == "__main__":
    unittest.main()
