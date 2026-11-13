"""Readable audit evidence for the student's own confirmation."""
from .run import RESULTS, lines, read


def main() -> None:
    reviews = read(RESULTS / "ai_reviews.json")
    text = ["# Hồ sơ chấm coherence, grounding và metadata", "",
        "Các điểm gợi ý dưới đây do **Codex (AI)** đọc mẫu và chấm theo rubric. "
        "Tác giả cần tự đọc, sửa nếu cần và điền các cột human_* trong ba CSV. "
        "Không thay toàn bộ ô trống bằng điểm AI khi chưa kiểm tra.", "",
        "- human_coherence_labels.csv: human_score 0/1/2, human_reason, human_reviewer.",
        "- human_grounding_labels.csv: human_score 0/1/2, human_reason, human_reviewer.",
        "- human_metadata_labels.csv: human_confirmed true/false về metadata đúng/đủ, human_reason, human_reviewer.",
        "", "Các file nằm cùng thư mục với hồ sơ này. Giữ ID/rank/strategy khi sửa. "
        "Coherence: 0 không hiểu do cắt ý; 1 hiểu một phần; 2 tự hiểu và giữ trọn ý. "
        "Grounding: 0 không có evidence; 1 thiếu điều kiện/ngữ cảnh; 2 đủ bằng chứng để trả lời và truy nguồn.", "",
        "## Coherence — 10 vị trí giống nhau cho mỗi cấu hình", ""]
    for case in lines(RESULTS / "coherence_review_cases.jsonl"):
        review = next(r for r in reviews["coherence"] if r["strategy"] == case["strategy"] and r["sample_id"] == case["sample_id"])
        chunk = case["chunk"]
        text += [f"### {review['case_id']} — PDF page {chunk['page']}", "",
            f"Chunk `{chunk['chunk_id']}`, offsets {chunk['metadata']['start_char']}–{chunk['metadata']['end_char']}. "
            f"Điểm AI: **{review['score']}/2**. {review['reason']}", "", "```text", chunk["text"], "```", ""]
    text += ["## Grounding và metadata — 5 test mỗi cấu hình", "",
        "Đọc cả top-3, đánh giá độ đủ bằng chứng; có thể grounding đủ dù metric exact-quote miss. "
        "Kiểm tra nguồn/trang/chương của từng rank với corpus_preview/PDF, ghi metadata đúng/đủ vào CSV.", ""]
    for case in lines(RESULTS / "grounding_review_cases.jsonl"):
        review = next(r for r in reviews["grounding"] if r["strategy"] == case["strategy"] and r["question_id"] == case["question_id"])
        text += [f"### {review['case_id']} — {case['question']}", "",
            f"Đáp án gold: {case['expected_answer']}", "",
            f"Grounding AI: **{review['score']}/2**. {review['reason']}", "",
            f"Requested filter: `{case['requested_filter']}`; applied: `{case['applied_filter']}`.", ""]
        for hit in case["hits"]:
            text += [f"**Rank {hit['rank']}** — PDF page {hit['page']}, chapter {hit['metadata']['chapter']}, "
                f"printed page {hit['metadata']['printed_page']}; ID `{hit['chunk_id']}`.",
                f"Nguồn: {hit['source']}", "", "```text", hit["text"], "```", ""]
    (RESULTS / "AUDIT_REVIEW.md").write_text("\n".join(text), encoding="utf-8")
    print("Written results/AUDIT_REVIEW.md; human labels remain unfilled.")


if __name__ == "__main__":
    main()
