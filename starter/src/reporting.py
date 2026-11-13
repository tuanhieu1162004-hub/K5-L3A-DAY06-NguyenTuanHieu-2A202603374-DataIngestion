"""Build submission artifacts from measured results and attributed AI reviews."""
import csv
import json
from collections import Counter
from pathlib import Path

from .run import CONFIG, FREEZE, REPO, RESULTS, check_frozen, lines, read, save


def csv_file(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    check_frozen()
    config, frozen = read(CONFIG), read(FREEZE)
    stats = read(RESULTS / "ingestion_stats.json")
    dev = read(RESULTS / "metrics_dev.json")["rows"]
    test = read(RESULTS / "metrics_test.json")["rows"]
    selection = read(RESULTS / "selection.json")
    reviews = read(RESULTS / "ai_reviews.json")
    metadata = lines(RESULTS / "metadata_review_cases.jsonl")
    traces = lines(RESULTS / "traces_test.jsonl")
    metric_rows = [{**row, "chunk_count": stats["strategies"][row["strategy"]]["chunk_count"]} for row in dev + test]
    csv_file(RESULTS / "metrics.csv", metric_rows)
    manual_pending = 0
    human_ratings_recorded = 0
    human_scores = {s: {"coherence": [], "grounding": [], "metadata": []} for s in "ABC"}
    audit_summary = []
    for kind in ("coherence", "grounding"):
        target = RESULTS / f"human_{kind}_labels.csv"
        if not target.exists():
            csv_file(target, [{"case_id": item["case_id"], "strategy": item["strategy"],
                "source_id": item["sample_id"] if kind == "coherence" else item["question_id"],
                "ai_score": item["score"], "ai_reason": item["reason"],
                "human_score": "", "human_reason": "", "human_reviewer": ""} for item in reviews[kind]])
        with target.open(encoding="utf-8-sig", newline="") as handle:
            for row in csv.DictReader(handle):
                human_ratings_recorded += row["human_score"] in ("0", "1", "2") and bool(row["human_reviewer"].strip())
                complete = row["human_score"] in ("0", "1", "2") and row["human_reviewer"].strip() and row["human_reason"].strip()
                manual_pending += not complete
                if complete:
                    human_scores[row["strategy"]][kind].append(int(row["human_score"]))
    target = RESULTS / "human_metadata_labels.csv"
    if not target.exists():
        csv_file(target, [{"strategy": m["strategy"], "question_id": m["question_id"],
            "rank": m["rank"], "chunk_id": m["chunk_id"], "page": m["page"],
            "automated_correct": m["automated_metadata_correct"], "human_confirmed": "",
            "human_reason": "", "human_reviewer": ""} for m in metadata])
    with target.open(encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            value = row["human_confirmed"].strip().lower()
            complete = value in ("true", "false", "1", "0") and row["human_reviewer"].strip() and row["human_reason"].strip()
            manual_pending += not complete
            if complete:
                human_scores[row["strategy"]]["metadata"].append(value in ("true", "1"))
    for strategy in "ABC":
        coherence = [r for r in reviews["coherence"] if r["strategy"] == strategy]
        grounding = [r for r in reviews["grounding"] if r["strategy"] == strategy]
        checked_meta = [r for r in metadata if r["strategy"] == strategy]
        row = next(r for r in test if r["strategy"] == strategy)
        distribution = Counter(r["score"] for r in grounding)
        audit_summary.append({"strategy": strategy,
            "coherence_ai_mean": sum(r["score"] for r in coherence) / len(coherence),
            "coherence_samples": len(coherence),
            "grounding_ai_mean": sum(r["score"] for r in grounding) / len(grounding),
            "grounding_ai_distribution": {str(k): distribution[k] for k in (0, 1, 2)},
            "metadata_automated_correct_n": sum(r["automated_metadata_correct"] for r in checked_meta),
            "metadata_checked_n": len(checked_meta),
            "requested_filter_compliant_n": row["requested_filter_compliant_n"],
            "filter_questions_n": row["filter_questions"]})
    save(RESULTS / "audit_summary.json", {"rows": audit_summary, "reviewer": "Codex (AI)",
        "human_confirmation_pending_records": manual_pending,
        "human_ratings_recorded": human_ratings_recorded,
        "human_confirmed_scores": human_scores,
        "note": "AI reading-based scores and automated metadata checks, not author-confirmed human labels."})

    log_rows = []
    for strategy in "ABC":
        setting = config["strategies"][strategy]
        d, t = next(r for r in dev if r["strategy"] == strategy), next(r for r in test if r["strategy"] == strategy)
        log_rows.append({"strategy": strategy, "chunking": setting["chunking"], "chunk_size": setting["size"],
            "overlap": setting["overlap"], "metadata": "document_id/source/page/printed_page/chapter/chapter_title/offsets",
            "filter": "chapter when supplied" if setting["filter"] else "none", "vectorizer": config["model"],
            "hypothesis": {"A": "Fixed windows may cut evidence", "B": "Paragraph units may improve coherence but can fragment long paragraphs", "C": "Chapter filtering may reduce off-topic hits; no change for unfiltered questions"}[strategy],
            "dev_hit1": f"{d['hit1_n']}/{d['n']}", "dev_hit3": f"{d['hit3_n']}/{d['n']}",
            "test_hit1": f"{t['hit1_n']}/{t['n']}", "test_hit3": f"{t['hit3_n']}/{t['n']}",
            "notes": f"Protocol frozen {frozen['frozen_at']}; exact cosine; local service cost 0 USD"})
    csv_file(REPO / "artifacts/experiment_log.csv", log_rows)

    report = ["# Báo cáo Day 06 — Nguyễn Tuấn Hiếu", "", "- MSSV: **2A202603374**.",
        "- Lớp: L3A, suy ra từ tên repo do người học cung cấp; cần xác nhận nếu khác.",
        "- Repo: https://github.com/tuanhieu1162004-hub/K5-L3A-DAY06-NguyenTuanHieu-2A202603374-DataIngestion", "",
        "## Dữ liệu và pipeline", "",
        "Corpus là Think Python 2e, Version 2.4.1, Allen B. Downey / Green Tea Press. "
        "PDF 244 trang; dùng PDF page 23–72, loại 38 và 72 chỉ có running header: **48 trang nội dung**. "
        "Giấy phép CC BY-NC 3.0; ghi nguồn, chỉ sử dụng phi thương mại. "
        "Không dùng HTML nên không áp ngưỡng 1.500 ký tự/trang. Manifest có SHA256, số trang vật lý, printed_page, số ký tự và provenance review.", "",
        "Trích xuất layout bằng pypdf, chuẩn hóa NFC/line endings, giữ thụt lề code và dấu nối. "
        "Còn từ bị dính do font, running headers và công thức/hình không được biểu diễn đầy đủ. "
        "Không dùng OCR. Chi tiết kiểm tra nguồn và AI hỗ trợ tại `starter/results/input_review/`.", "",
        f"Embedding local CPU: `{config['model']}`, revision `{config['model_revision']}`, "
        f"{stats['dimensions']} chiều, normalized float vectors, giới hạn {stats['model_max_tokens']} token; "
        "kiểm tra token và báo lỗi thay vì âm thầm truncate. Query/document dùng plain text, không prefix E5. "
        "Đổi từ gợi ý E5 sang MiniLM trước retrieval vì dữ liệu/câu hỏi tiếng Anh; không dựa trên kết quả.", "",
        f"Vector store: PostgreSQL {stats['versions']['postgres']}, pgvector {stats['versions']['pgvector']}. "
        "Bảng day6_chunks lưu bền vững trong Docker volume, cosine **exact**, không tạo ANN index. "
        "Metadata có source, document_id, page, printed_page, chapter/chapter_title và offsets. "
        "chapter có giá trị từ ranh giới chương đã đối chiếu; giúp phân biệt phạm vi nhưng có thể loại bằng chứng hữu ích ngoài chương khi ngữ cảnh lọc quá hẹp.", "",
        "## Cấu hình và benchmark", "",
        "A: fixed 500 ký tự, overlap 50. B: gom đoạn tối đa 500, tách đoạn quá dài tại ranh giới câu/từ, overlap 0. "
        "C dùng nguyên chunk/vector của B, chỉ thêm chapter filter khi câu hỏi cung cấp. Câu không filter có retrieval giống B.", "",
        f"Đầu vào/model revision/mẫu coherence được chốt lúc **{frozen['frozen_at']}**. "
        "20 câu có đáp án/evidence, 15 dev chương 1–4 và 5 test chương 5; 3 câu filter gồm q08/q11/q16. "
        "Gold thay thế được ghi trước retrieval. Chia theo chương giảm trùng nội dung nhưng kiến thức vẫn liên quan. "
        "Chỉ question được embedding, không đưa đáp án/gold source/page vào query hay filter.", "",
        "Tiêu chí chọn đã chốt: dev Hit@3, rồi Hit@1, rồi search latency trung bình, cuối cùng mã strategy. "
        f"Đã chọn **{selection['strategy']}** lúc {selection['selected_at']}, trước khi chạy test. "
        "Chưa tinh chỉnh tham số theo test. Checksum và trace SHA được lưu để kiểm chứng thứ tự.", "",
        "## Kết quả retrieval", "",
        "Hit yêu cầu đúng nguồn/trang và đủ một gold evidence trong **một chunk**. "
        "Chỉ fold whitespace, chấp nhận alternative gold đã ghi. Tách evidence qua nhiều chunk vẫn là miss theo metric chính. "
        "Bằng chứng tương đương khác cần review riêng; exact matching có thể bỏ sót cách diễn đạt hợp lệ.", "",
        "| Strategy | Split | Hit@1 | Evidence Hit@3 | Chunk count | Search trung bình (ms) |", "|---|---|---|---|---|---|"]
    for r in metric_rows:
        report.append(f"| {r['strategy']} | {r['split']} | {r['hit1_n']}/{r['n']} ({r['hit1']:.1%}) | {r['hit3_n']}/{r['n']} ({r['hit3']:.1%}) | {r['chunk_count']} | {r['mean_search_seconds']*1000:.2f} |")
    report += ["", "## Coherence, metadata và grounding", "",
        "**Điểm coherence/grounding dưới đây do Codex (AI) đọc và chấm từng mẫu theo rubric 0–2. "
        "Metadata được đối chiếu tự động với nguồn và offsets. Đây chưa phải xác nhận chấm thủ công của tác giả.**", "",
        "Coherence dùng cùng 10 vị trí nguồn đã chốt; khi nhiều chunk bao phủ, chọn chunk có start_char gần vị trí nhất từ phía trước. "
        "Grounding dùng cùng 5 test mỗi cấu hình, xét đủ bằng chứng trong cả top-3; không đo độ chính xác câu trả lời LLM.", "",
        "| Strategy | Coherence AI /2 (10 mẫu) | Metadata auto đủ/đúng | Filter test tuân thủ | Grounding AI: số mức 0/1/2 | Grounding AI /2 |",
        "|---|---|---|---|---|---|"]
    for r in audit_summary:
        dist = r["grounding_ai_distribution"]
        filter_rate = f"{r['requested_filter_compliant_n']}/{r['filter_questions_n']}" if r['filter_questions_n'] else "N/A"
        report.append(f"| {r['strategy']} | {r['coherence_ai_mean']:.2f} | {r['metadata_automated_correct_n']}/{r['metadata_checked_n']} | {filter_rate} | {dist['0']}/{dist['1']}/{dist['2']} | {r['grounding_ai_mean']:.2f} |")
    report += ["", "Kết quả tác giả xác nhận, tính riêng từ CSV có điểm/lý do/người chấm hợp lệ:", "",
        "| Strategy | Coherence tác giả /2 | Grounding tác giả /2 | Metadata tác giả đủ/đúng |",
        "|---|---|---|---|"]
    for strategy, values in human_scores.items():
        cells = []
        for kind in ("coherence", "grounding"):
            scores = values[kind]
            cells.append(f"{sum(scores)/len(scores):.2f} (n={len(scores)})" if scores else "Chưa chấm")
        meta_scores = values["metadata"]
        cells.append(f"{sum(meta_scores)}/{len(meta_scores)}" if meta_scores else "Chưa chấm")
        report.append(f"| {strategy} | {' | '.join(cells)} |")
    report += ["", f"Còn **{manual_pending} bản ghi chờ tác giả xác nhận/chấm** trong `human_*_labels.csv`. "
        "Không tự gán AI thành người chấm. Toàn bộ text mẫu, ID, nguồn, nhận xét AI và cột tác giả để trống có trong các file audit.", "",
        f"Đã ghi nhận {human_ratings_recorded} điểm do người học trực tiếp cung cấp. "
        "A-s01 được người học chọn 0; lý do chưa được cung cấp nên chưa tính là một bản ghi chấm hoàn tất. "
        "Toàn bộ 90 nhãn AI/kiểm tra metadata có tên người/công cụ chấm ở attributed_review_labels.csv.", "",
        "## Tài nguyên và tái lập", "",
        f"Model load/download lần ingest: {stats['model_load_seconds']:.3f}s. "
        "Thời gian ingest bên dưới bao gồm encoding/cache, lưu DB và một lần nạp lại để kiểm tra; không bao gồm load/download model. "
        "Search gồm round trip SQL, không gồm query embedding. C dùng lại vector cache của B nên không so thời gian encode C như một lần cold start độc lập.", "",
        "| Strategy | Ký tự/chunk: min/median/max | Tổng ký tự | Tokens (có special tokens) | Ingest + recheck (s) | Vector mới | Phí dịch vụ |",
        "|---|---|---|---|---|---|---|"]
    for name, r in stats["strategies"].items():
        report.append(f"| {name} | {r['length_min']}/{r['length_median']}/{r['length_max']} | {r['total_characters']} | {r['embedding']['total_tokens']} | {r['ingest_seconds_including_repeat_check']:.3f} | {r['embedding']['new_embeddings']} | 0 USD |")
    report += ["", "Phí dịch vụ 0 USD vì chạy local; không tính điện/mạng/hardware. "
        f"Nạp lại không tăng chunk count; thử xóa stale snapshot có số bản ghi {stats['stale_removal_check_counts']}. "
        "Backend được mở lại từ các process dev/test riêng nên có kiểm tra lưu bền vững. "
        "Phiên bản thư viện ở environment.txt, cấu hình ở strategies.json, cách chạy ở RUNBOOK.md. "
        "Lỗi đường dẫn Windows và cách khắc phục có trong setup_notes.md/pipeline_errors.log; không fallback mock.", "",
        "## Phân tích và kết luận", "",
        "A–B: chia theo đoạn nâng dev Hit@3 từ 10/15 lên 12/15 và Hit@1 từ 7/15 lên 12/15, "
        "nhưng số chunk tăng 241 lên 271. B ít tổng ký tự/token hơn nhờ không overlap. "
        "Theo 10 vị trí đã chốt, coherence do AI chấm là 1,00/2 cho A và 1,60/2 cho B/C. "
        "B vẫn cắt các đoạn dài và có chunk chỉ chứa running header.", "",
        "B–C: Hit@1/Hit@3 không đổi trên cả hai split. Với dev q08, B trả các chương [2,1,2], "
        "C trả [2,2,2]; tuân thủ filter dev tăng từ 1/2 lên 2/2. "
        "Top-3 của cả 5 câu test giống nhau giữa B/C. Filter có ích để giữ phạm vi, nhưng không loại "
        "được chunk header cùng chương và chưa làm tăng retrieval accuracy trong mẫu này.", "",
        "C được chọn trước test do hòa dev hits với B và search trung bình 10,5848 ms so với "
        "10,6482 ms của B. Chênh lệch khoảng 0,0634 ms rất nhỏ và chịu ảnh hưởng thứ tự/cache; "
        "không coi đây là bằng chứng C nhanh hơn nói chung.", "",
        "Test Hit@3 của A là 4/5, cao hơn B/C 3/5; vẫn giữ C theo lựa chọn dev. "
        "AI đọc thấy top-3 đủ trả lời cả 5 test, dù có strict miss. q18 cần suy luận ngắn từ định nghĩa "
        "thay vì lấy được nguyên lời khuyên trực tiếp; tác giả nên đặc biệt xem lại nhãn này. "
        "Không sửa gold đã chốt hoặc thay số primary metric bằng nhãn AI sau khi xem test. "
        "Bằng chứng tương đương được tác giả xác nhận có thể được báo riêng như đánh giá bổ sung.", "",
        "Hai ví dụ lỗi/giới hạn từ trace thật:", ""]
    for example in reviews["failure_examples"]:
        report.append(f"- **{example['strategy']} / {example['question_id']}**, nguồn PDF page {example['pages']}: {example['reason']}")
    report += ["", f"Giữ lựa chọn **{selection['strategy']}** theo dev. "
        "Kết quả test chỉ mô tả 5 câu thuộc corpus này, không chứng minh một chiến lược tốt nhất tổng quát. "
        "AI cùng hỗ trợ soạn/chấm có thiên lệch; cỡ mẫu nhỏ, text PDF lỗi, metric chuỗi và latency một lần đo là các giới hạn chính. "
        "Cải tiến tiếp theo: tác giả xác nhận nhãn; cải thiện text PDF trên một thí nghiệm mới; tăng test theo nhiều chương; "
        "đánh giá hợp bằng chứng/hybrid như metric/thí nghiệm bổ sung, giữ metric chính.", "",
        "## AI, artifact và trạng thái nộp", "",
        "Codex hỗ trợ code, kiểm tra nguồn, soạn benchmark, chạy và phân tích. "
        "AI review đọc text theo rubric, có lý do từng mẫu, không phải LLM judge bên ngoài hay nhãn do tác giả xác nhận. "
        "Người học cần hiểu/giải thích code và chấm/xác nhận nhãn thủ công theo RULES.md. "
        "Trạng thái push được xác minh riêng bằng lịch sử GitHub và artifacts/publish_receipt.json trong bản local/ZIP nếu có; "
        "không suy ra đã nộp bài cho lớp từ việc có link repo. Commit snapshot được ghi trong STUDENT.md và artifacts/source_commit.json nếu đã tạo.", "",
        "Artifacts: frozen.json, strategies.json, experiment_log.csv; pages/chunks; ingestion_stats.json; "
        "traces_dev/test.jsonl; metrics_dev/test.json, metrics.csv; selection.json; "
        "coherence/grounding/metadata_review_cases.jsonl; ai_reviews.json; human_*_labels.csv; "
        "audit_summary.json; unit_tests.log; environment.txt; input_review/.", ""]
    supplemental_path = RESULTS / "supplemental_evidence_metrics.json"
    if supplemental_path.exists():
        supplementary = read(supplemental_path)
        report += ["## Đánh giá bằng chứng tương đương bổ sung", "",
            "Sau khi giữ nguyên kết quả gốc, Codex (AI) xác nhận top-1 của B/C-q17 trên đúng PDF page 64 "
            "đã đủ quy tắc cần trả lời. Đây là đánh giá bổ sung sau thí nghiệm, không dùng chọn cấu hình, "
            "không sửa gold đã chốt và chưa phải xác nhận của tác giả.", "",
            "| Strategy | Hit@3 gốc | Hit@3 có thêm q17 do AI xác nhận |", "|---|---|---|"]
        for r in supplementary["rows"]:
            report.append(f"| {r['strategy']} | {r['primary_hit3_n']}/{r['n']} | {r['ai_equivalence_hit3_n']}/{r['n']} |")
        report += ["", "Chi tiết từng đoạn: supplemental_evidence_reviews.csv. Giữ nguyên lựa chọn C theo dev và mọi số liệu primary ở trên.", ""]
    reproductions = sorted((RESULTS / "reproductions").glob("*/reproduction_comparison.json")) if (RESULTS / "reproductions").exists() else []
    if reproductions:
        reproduced = read(reproductions[-1])
        report += ["## Kiểm chứng tái lập", "",
            f"Đã chạy `--stage all --reproduce`; số hit dev/test khớp bản gốc: {all(r['metric_counts_match'] for r in reproduced['comparisons'])}. "
            f"Bảo toàn file gốc: {reproduced['primary_results_preserved']}. "
            "Kết quả mới ở starter/results/reproductions/. Đây là tái lập trên test đã biết, không phải holdout mới; cache và thời gian có thể khác.", ""]
    target = REPO / "report/individual/2A202603374_NguyenTuanHieu.md"
    target.write_text("\n".join(report), encoding="utf-8")
    print(f"Report written: {target.name}; author audit records pending: {manual_pending}")


if __name__ == "__main__":
    main()
