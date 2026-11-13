"""One complete grading table, retaining the origin of each assessment."""
import csv
import hashlib
import shutil
from collections import Counter

from .run import RESULTS, lines, now, read, save


def archive_previous_tables() -> None:
    history = RESULTS / "review_history"
    history.mkdir(exist_ok=True)
    for name in ("human_coherence_labels.csv", "human_grounding_labels.csv",
                 "human_metadata_labels.csv", "attributed_review_labels.csv"):
        source, destination = RESULTS / name, history / name
        assert source.resolve().is_relative_to(RESULTS.resolve())
        assert destination.resolve().is_relative_to(RESULTS.resolve())
        if source.exists():
            if destination.exists():
                if source.read_bytes() != destination.read_bytes():
                    raise ValueError(f"Different historical table already exists: {name}")
                source.unlink()
            else:
                shutil.move(str(source), str(destination))


def validate_reviews(rows: list[dict]) -> None:
    expected = {(kind, case["case_id"]) for kind in ("coherence", "grounding")
                for case in read(RESULTS / "ai_reviews.json")[kind]}
    expected |= {("metadata", f"{case['strategy']}-{case['question_id']}-r{case['rank']}")
                 for case in lines(RESULTS / "metadata_review_cases.jsonl")}
    keys = [(r["dimension"], r["case_id"]) for r in rows]
    if len(keys) != len(set(keys)) or set(keys) != expected:
        raise ValueError("Grading rows must cover all 90 unique source cases exactly once")
    for row in rows:
        score = int(row["score"])
        allowed = (0, 1) if row["dimension"] == "metadata" else (0, 1, 2)
        if score not in allowed or row["strategy"] not in ("A", "B", "C") or not row["case_id"].startswith(row["strategy"] + "-"):
            raise ValueError("Invalid rubric score or strategy")
        if not all(row[k].strip() for k in ("reason", "reviewer", "method")):
            raise ValueError("Every grade requires a reason, reviewer and method")


def load_reviews() -> list[dict]:
    target = RESULTS / "review_labels.csv"
    if target.exists():
        with target.open(encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))
        validate_reviews(rows)
        return rows
    archive_previous_tables()
    prior = read(RESULTS / "ai_reviews.json")
    rows = []
    for kind in ("coherence", "grounding"):
        for case in prior[kind]:
            rows.append({"dimension": kind, "case_id": case["case_id"], "strategy": case["strategy"],
                "score": case["score"], "reason": case["reason"], "reviewer": case["reviewer"],
                "method": "Reading-based rubric assessment of the recorded source chunk/top-3",
                "reference": case.get("chunk_id", case.get("question_id", ""))})
    for case in lines(RESULTS / "metadata_review_cases.jsonl"):
        rows.append({"dimension": "metadata", "case_id": f"{case['strategy']}-{case['question_id']}-r{case['rank']}",
            "strategy": case["strategy"], "score": int(case["automated_metadata_correct"]),
            "reason": "Source, PDF page, chapter, printed_page and exact source offsets agree with the frozen corpus.",
            "reviewer": "Source verification script", "method": "Programmatic source and metadata cross-check",
            "reference": case["chunk_id"]})
    provenance = read(RESULTS / "user_review_provenance.json")
    for row in rows:
        if row["case_id"] == provenance["case_id"] and row["dimension"] == "coherence":
            row["score"] = provenance["human_score"]
            row["reason"] = ("The student explicitly chose 0. Observed boundaries: the chunk starts at the end of a previous sentence "
                             "and ends mid-word. These observations are supplied by Codex; the student did not supply a separate rationale.")
            row["reviewer"] = "Nguyễn Tuấn Hiếu (score); Codex (boundary observations)"
            row["method"] = "Explicit user rating; supporting source-boundary observations recorded separately"
    validate_reviews(rows)
    with target.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    save(RESULTS / "grading_manifest.json", {"completed_at": now(), "graded_records": len(rows),
        "dimension_counts": dict(Counter(r["dimension"] for r in rows)), "grading_complete": True,
        "method": "One consolidated table: Codex reading-based rubric grades, source-check script metadata grades, and the student's explicit A-s01=0 rating. Reviewer/method are retained in each row.",
        "author_independent_manual_review_confirmed": False,
        "note": "Complete assessments are not a claim that the student personally graded every record. Historical tables remain in review_history/.",
        "csv_sha256": hashlib.sha256(target.read_bytes()).hexdigest()})
    return rows


def summarize_reviews(rows: list[dict], test_metrics: list[dict]) -> list[dict]:
    validate_reviews(rows)
    summary = []
    for strategy in "ABC":
        coherence = [int(r["score"]) for r in rows if r["dimension"] == "coherence" and r["strategy"] == strategy]
        grounding = [int(r["score"]) for r in rows if r["dimension"] == "grounding" and r["strategy"] == strategy]
        metadata = [int(r["score"]) for r in rows if r["dimension"] == "metadata" and r["strategy"] == strategy]
        counts = Counter(grounding)
        metric = next(r for r in test_metrics if r["strategy"] == strategy)
        summary.append({"strategy": strategy, "coherence_mean": sum(coherence) / len(coherence),
            "coherence_samples": len(coherence), "grounding_mean": sum(grounding) / len(grounding),
            "grounding_distribution": {str(k): counts[k] for k in (0, 1, 2)},
            "metadata_correct_n": sum(metadata), "metadata_checked_n": len(metadata),
            "requested_filter_compliant_n": metric["requested_filter_compliant_n"],
            "filter_questions_n": metric["filter_questions"]})
    return summary
