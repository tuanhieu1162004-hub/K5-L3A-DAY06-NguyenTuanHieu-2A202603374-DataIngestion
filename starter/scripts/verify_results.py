"""Verify persisted results and experimental controls without rerunning test."""
import hashlib
import json
import math
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

STARTER = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(STARTER))
from src.evaluation import summarize
from src.run import CONFIG, FREEZE, RESULTS, check_frozen, lines, now, read, save, sha, store


def main() -> None:
    frozen = check_frozen()
    dev, test = lines(RESULTS / "traces_dev.jsonl"), lines(RESULTS / "traces_test.jsonl")
    assert Counter(t["strategy"] for t in dev) == {"A": 15, "B": 15, "C": 15}
    assert Counter(t["strategy"] for t in test) == {"A": 5, "B": 5, "C": 5}
    assert len({(t["strategy"], t["question_id"]) for t in dev + test}) == 60
    selection = read(RESULTS / "selection.json")
    assert selection["dev_trace_sha256"] == sha(RESULTS / "traces_dev.jsonl")
    assert selection["frozen_sha256"] == sha(FREEZE) and not selection["test_retrieval_seen"]
    assert datetime.fromisoformat(frozen["frozen_at"]) <= min(datetime.fromisoformat(t["evaluated_at"]) for t in dev)
    assert max(datetime.fromisoformat(t["evaluated_at"]) for t in dev) <= datetime.fromisoformat(selection["selected_at"])
    assert datetime.fromisoformat(selection["selected_at"]) < min(datetime.fromisoformat(t["evaluated_at"]) for t in test)
    for split, traces in (("dev", dev), ("test", test)):
        assert summarize(traces)["rows"] == read(RESULTS / f"metrics_{split}.json")["rows"]
    for trace in dev + test:
        assert len(trace["hits"]) == 3
        assert [hit["rank"] for hit in trace["hits"]] == [1, 2, 3]
        assert len({hit["chunk_id"] for hit in trace["hits"]}) == 3
        assert all(math.isfinite(h["score"]) and -1.00001 <= h["score"] <= 1.00001 for h in trace["hits"])
        assert all(trace["hits"][i]["score"] >= trace["hits"][i + 1]["score"] for i in range(2))
        if trace["strategy"] == "C" and trace["requested_filter"]:
            assert trace["applied_filter"] == trace["requested_filter"] and trace["requested_filter_compliant"]
        elif trace["strategy"] != "C":
            assert trace["applied_filter"] is None
    assert lines(RESULTS / "chunks_B.jsonl") == lines(RESULTS / "chunks_C.jsonl")
    controls = 0
    for trace in dev + test:
        if trace["strategy"] == "B" and trace["requested_filter"] is None:
            paired = next(t for t in dev + test if t["strategy"] == "C" and t["question_id"] == trace["question_id"])
            assert [(h["chunk_id"], h["score"]) for h in trace["hits"]] == [(h["chunk_id"], h["score"]) for h in paired["hits"]]
            controls += 1
    meta = lines(RESULTS / "metadata_review_cases.jsonl")
    assert len(meta) == 45 and all(row["automated_metadata_correct"] for row in meta)
    ai = read(RESULTS / "ai_reviews.json")
    assert len(ai["coherence"]) == 30 and len(ai["grounding"]) == 15
    assert all(r["reviewer"] == "Codex (AI)" and r["score"] in (0, 1, 2) and not r["human_confirmed"] for kind in ("coherence", "grounding") for r in ai[kind])
    from src.grading import load_reviews, validate_reviews
    grades = load_reviews()
    validate_reviews(grades)
    assert len(grades) == 90
    stats = read(RESULTS / "ingestion_stats.json")
    backend = store(stats["dimensions"])
    try:
        persisted = {s: backend.count(s) for s in "ABC"}
        assert persisted == {s: stats["strategies"][s]["chunk_count"] for s in "ABC"}
        assert backend.count("__verification__") == 0
        with backend.connection.cursor() as cursor:
            cursor.execute("SELECT strategy,count(*) AS n,min(vector_dims(embedding)) AS dimensions FROM day6_chunks GROUP BY strategy")
            assert all(row["dimensions"] == 384 for row in cursor.fetchall())
            cursor.execute("SELECT indexdef FROM pg_indexes WHERE tablename='day6_chunks'")
            indexes = [row["indexdef"] for row in cursor.fetchall()]
            assert not any("hnsw" in text.lower() or "ivfflat" in text.lower() for text in indexes)
        backend.connection.commit()
        for filters in ({"gold_page": 1}, {"chapter": "2 OR 1=1"}):
            try:
                backend.search("A", [1.0] * 384, filters=filters)
            except ValueError:
                pass
            else:
                raise AssertionError("Invalid filter accepted")
    finally:
        backend.close()
    save(RESULTS / "verification.json", {"verified_at": now(), "passed": True,
        "dev_traces": len(dev), "test_traces": len(test), "top3_records": 180,
        "metadata_source_checks": len(meta), "nonfiltered_B_C_controls": controls,
        "graded_records_checked": len(grades), "grading_reviewer_method_recorded": True,
        "persistent_database_counts": persisted, "stale_removal_counts": stats["stale_removal_check_counts"],
        "exact_search_indexes": indexes, "selection_before_test_verified": True,
        "input_freeze_valid": True, "invalid_filter_rejection_verified": True,
        "code_snapshot_timing": "Recorded after execution. An isolated reproduction CLI was added after the primary run; frozen model/data/parameters and primary result files remain unchanged.",
        "code_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (STARTER / "src").glob("*.py")}})
    print(f"PASS: 60 query traces / 180 top-3 records; persistent DB {persisted}; {controls} B/C controls; dev selection before test; metadata 45/45.")


if __name__ == "__main__":
    main()
