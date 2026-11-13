"""Export attributed review evidence without fabricating human assessments."""
import csv
from .run import RESULTS, check_frozen, lines, now, read, save
from .validate_benchmark import canonical


def write_csv(path, rows):
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    check_frozen()
    reviews = read(RESULTS / "ai_reviews.json")
    rows = []
    for kind in ("coherence", "grounding"):
        for review in reviews[kind]:
            rows.append({"dimension": kind, "case_id": review["case_id"],
                "strategy": review["strategy"], "score_or_correct": review["score"],
                "reason": review["reason"], "reviewer": review["reviewer"],
                "reviewer_type": "AI", "human_confirmed": False})
    for case in lines(RESULTS / "metadata_review_cases.jsonl"):
        rows.append({"dimension": "metadata", "case_id": f"{case['strategy']}-{case['question_id']}-r{case['rank']}",
            "strategy": case["strategy"], "score_or_correct": case["automated_metadata_correct"],
            "reason": "Source/page/chapter/printed_page and exact text offsets checked against frozen source pages.",
            "reviewer": "Source verification script", "reviewer_type": "automated_source_check", "human_confirmed": False})
    assert len(rows) == 90
    history = RESULTS / "review_history"
    target = history if history.exists() else RESULTS
    write_csv(target / "attributed_review_labels.csv", rows)
    # Preserve the user's explicit score. A rationale was not supplied, so do not
    # fabricate it or count this as a completed human rubric review.
    human_path = target / "human_coherence_labels.csv"
    with human_path.open(encoding="utf-8-sig", newline="") as handle:
        human = list(csv.DictReader(handle))
    for row in human:
        if row["case_id"] == "A-s01":
            if row["human_score"] not in ("", "0"):
                raise ValueError("A-s01 differs from explicit user score; preserve and reconcile before overwriting")
            row["human_score"] = "0"
            row["human_reviewer"] = "Nguyễn Tuấn Hiếu"
    write_csv(human_path, human)
    save(RESULTS / "user_review_provenance.json", {"recorded_at": now(),
        "case_id": "A-s01", "human_score": 0, "human_reviewer": "Nguyễn Tuấn Hiếu",
        "source": "User explicitly answered 0 when asked to grade A-s01 in this conversation",
        "human_reason": None, "note": "Rationale not supplied. Other ratings remain attributed to AI/scripts, not the student."})

    supplemental = []
    cases = lines(RESULTS / "traces_test.jsonl")
    for strategy in ("B", "C"):
        case = next(c for c in cases if c["strategy"] == strategy and c["question_id"] == "q17")
        hit = case["hits"][0]
        assert hit["page"] == 64 and hit["document_id"] == "think-python-2e"
        proof = "Even if more than one condition is true, only the first true branch runs."
        assert canonical(proof) in canonical(hit["text"])
        supplemental.append({"strategy": strategy, "question_id": "q17", "rank": 1,
            "chunk_id": hit["chunk_id"], "page": 64, "reviewer": "Codex (AI)",
            "equivalent_evidence_supported": True, "human_confirmed": False,
            "reason": "The same source/page explicitly gives the first-true-branch rule and statement termination. The missing introductory gold sentence is unnecessary to answer.",
            "timing": "Post-hoc supplementary review only; not used for selection; frozen gold and primary metrics unchanged."})
    write_csv(RESULTS / "supplemental_evidence_reviews.csv", supplemental)
    metrics = []
    for strategy in "ABC":
        selected = [c for c in cases if c["strategy"] == strategy]
        extra = {r["question_id"] for r in supplemental if r["strategy"] == strategy}
        metrics.append({"strategy": strategy, "n": len(selected),
            "primary_hit3_n": sum(c["hit_at_3"] for c in selected),
            "ai_equivalence_hit3_n": sum(c["hit_at_3"] or c["question_id"] in extra for c in selected)})
    save(RESULTS / "supplemental_evidence_metrics.json", {"reviewed_at": now(), "rows": metrics,
        "reviewer": "Codex (AI)", "used_for_selection": False, "human_confirmed": False,
        "note": "Supplementary AI adjudication of q17 only. Not a replacement for the original metric or a new test experiment."})
    print("Exported 90 attributed labels and q17 supplemental evidence review; saved user A-s01=0 without inventing a reason.")


if __name__ == "__main__":
    main()
