"""Readable audit evidence for the student's own confirmation."""
from .run import RESULTS, lines, read
from .grading import load_reviews


def main() -> None:
    reviews = {(r["dimension"], r["case_id"]): r for r in load_reviews()}
    text = ["# Hồ sơ chấm coherence, grounding và metadata", "",
        "Bảng chấm chung ở **review_labels.csv**, gồm đủ 90 bản ghi có điểm/kết luận, lý do và phương pháp. "
        "Codex hỗ trợ chấm nội dung, công cụ đối chiếu metadata với nguồn; A-s01 dùng điểm 0 người học cung cấp. "
        "Nguồn gốc nhận xét được giữ để tái lập, không khẳng định tác giả đã tự chấm mọi mẫu.", "",
        "Nếu sửa đánh giá, cập nhật score và reason trong review_labels.csv, giữ nguyên ID/strategy và ghi đúng reviewer/method. "
        "Coherence: 0 không hiểu do cắt ý; 1 hiểu một phần; 2 tự hiểu và giữ trọn ý. "
        "Grounding: 0 không có evidence; 1 thiếu điều kiện/ngữ cảnh; 2 đủ bằng chứng để trả lời và truy nguồn.", "",
        "## Coherence — 10 vị trí giống nhau cho mỗi cấu hình", ""]
    for case in lines(RESULTS / "coherence_review_cases.jsonl"):
        case_id = case["strategy"] + "-" + case["sample_id"]
        review = reviews[("coherence", case_id)]
        chunk = case["chunk"]
        text += [f"### {review['case_id']} — PDF page {chunk['page']}", "",
            f"Chunk `{chunk['chunk_id']}`, offsets {chunk['metadata']['start_char']}–{chunk['metadata']['end_char']}. "
            f"Điểm: **{review['score']}/2**. {review['reason']} Người/công cụ chấm: {review['reviewer']}.", "", "```text", chunk["text"], "```", ""]
    text += ["## Grounding và metadata — 5 test mỗi cấu hình", "",
        "Đọc cả top-3, đánh giá độ đủ bằng chứng; có thể grounding đủ dù metric exact-quote miss. "
        "Metadata từng rank đã được đối chiếu với corpus_preview/PDF và lưu kết luận trong cùng bảng chấm.", ""]
    for case in lines(RESULTS / "grounding_review_cases.jsonl"):
        case_id = case["strategy"] + "-" + case["question_id"]
        review = reviews[("grounding", case_id)]
        text += [f"### {review['case_id']} — {case['question']}", "",
            f"Đáp án gold: {case['expected_answer']}", "",
            f"Grounding: **{review['score']}/2**. {review['reason']} Người/công cụ chấm: {review['reviewer']}.", "",
            f"Requested filter: `{case['requested_filter']}`; applied: `{case['applied_filter']}`.", ""]
        for hit in case["hits"]:
            meta_review = reviews[("metadata", f"{case['strategy']}-{case['question_id']}-r{hit['rank']}")]
            text += [f"**Rank {hit['rank']}** — PDF page {hit['page']}, chapter {hit['metadata']['chapter']}, "
                f"printed page {hit['metadata']['printed_page']}; ID `{hit['chunk_id']}`.",
                f"Nguồn: {hit['source']}", f"Metadata đủ/đúng: {bool(int(meta_review['score']))}.", "", "```text", hit["text"], "```", ""]
    (RESULTS / "AUDIT_REVIEW.md").write_text("\n".join(text), encoding="utf-8")
    print("Written results/AUDIT_REVIEW.md from 90 completed consolidated grades.")


if __name__ == "__main__":
    main()
