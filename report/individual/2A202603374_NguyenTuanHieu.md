# Báo cáo Day 06 — Nguyễn Tuấn Hiếu

- MSSV: **2A202603374**.
- Lớp: L3A, suy ra từ tên repo do người học cung cấp; cần xác nhận nếu khác.
- Repo: https://github.com/tuanhieu1162004-hub/K5-L3A-DAY06-NguyenTuanHieu-2A202603374-DataIngestion

## Dữ liệu và pipeline

Corpus là Think Python 2e, Version 2.4.1, Allen B. Downey / Green Tea Press. PDF 244 trang; dùng PDF page 23–72, loại 38 và 72 chỉ có running header: **48 trang nội dung**. Giấy phép CC BY-NC 3.0; ghi nguồn, chỉ sử dụng phi thương mại. Không dùng HTML nên không áp ngưỡng 1.500 ký tự/trang. Manifest có SHA256, số trang vật lý, printed_page, số ký tự và provenance review.

Trích xuất layout bằng pypdf, chuẩn hóa NFC/line endings, giữ thụt lề code và dấu nối. Còn từ bị dính do font, running headers và công thức/hình không được biểu diễn đầy đủ. Không dùng OCR. Chi tiết kiểm tra nguồn và AI hỗ trợ tại `starter/results/input_review/`.

Embedding local CPU: `sentence-transformers/all-MiniLM-L6-v2`, revision `1110a243fdf4706b3f48f1d95db1a4f5529b4d41`, 384 chiều, normalized float vectors, giới hạn 256 token; kiểm tra token và báo lỗi thay vì âm thầm truncate. Query/document dùng plain text, không prefix E5. Đổi từ gợi ý E5 sang MiniLM trước retrieval vì dữ liệu/câu hỏi tiếng Anh; không dựa trên kết quả.

Vector store: PostgreSQL 16.16 (Debian 16.16-1.pgdg12+1), pgvector 0.8.7. Bảng day6_chunks lưu bền vững trong Docker volume, cosine **exact**, không tạo ANN index. Metadata có source, document_id, page, printed_page, chapter/chapter_title và offsets. chapter có giá trị từ ranh giới chương đã đối chiếu; giúp phân biệt phạm vi nhưng có thể loại bằng chứng hữu ích ngoài chương khi ngữ cảnh lọc quá hẹp.

## Cấu hình và benchmark

A: fixed 500 ký tự, overlap 50. B: gom đoạn tối đa 500, tách đoạn quá dài tại ranh giới câu/từ, overlap 0. C dùng nguyên chunk/vector của B, chỉ thêm chapter filter khi câu hỏi cung cấp. Câu không filter có retrieval giống B.

Đầu vào/model revision/mẫu coherence được chốt lúc **2026-11-13T19:34:57+07:00**. 20 câu có đáp án/evidence, 15 dev chương 1–4 và 5 test chương 5; 3 câu filter gồm q08/q11/q16. Gold thay thế được ghi trước retrieval. Chia theo chương giảm trùng nội dung nhưng kiến thức vẫn liên quan. Chỉ question được embedding, không đưa đáp án/gold source/page vào query hay filter.

Tiêu chí chọn đã chốt: dev Hit@3, rồi Hit@1, rồi search latency trung bình, cuối cùng mã strategy. Đã chọn **C** lúc 2026-11-13T20:23:14+07:00, trước khi chạy test. Chưa tinh chỉnh tham số theo test. Checksum và trace SHA được lưu để kiểm chứng thứ tự.

## Kết quả retrieval

Hit yêu cầu đúng nguồn/trang và đủ một gold evidence trong **một chunk**. Chỉ fold whitespace, chấp nhận alternative gold đã ghi. Tách evidence qua nhiều chunk vẫn là miss theo metric chính. Bằng chứng tương đương khác cần review riêng; exact matching có thể bỏ sót cách diễn đạt hợp lệ.

| Strategy | Split | Hit@1 | Evidence Hit@3 | Chunk count | Search trung bình (ms) |
|---|---|---|---|---|---|
| A | dev | 7/15 (46.7%) | 10/15 (66.7%) | 241 | 11.98 |
| B | dev | 12/15 (80.0%) | 12/15 (80.0%) | 271 | 10.65 |
| C | dev | 12/15 (80.0%) | 12/15 (80.0%) | 271 | 10.58 |
| A | test | 2/5 (40.0%) | 4/5 (80.0%) | 241 | 12.62 |
| B | test | 3/5 (60.0%) | 3/5 (60.0%) | 271 | 12.02 |
| C | test | 3/5 (60.0%) | 3/5 (60.0%) | 271 | 10.48 |

## Coherence, metadata và grounding

Phương pháp: Codex hỗ trợ đọc và chấm mẫu theo rubric; metadata được đối chiếu bằng công cụ với nguồn và offsets. A-s01 dùng điểm 0 người học trực tiếp cung cấp; nhận xét về ranh giới đoạn do Codex ghi. Người/công cụ và phương pháp của từng nhãn được lưu trong review_labels.csv, không khẳng định tác giả đã tự chấm mọi mẫu.

Coherence dùng cùng 10 vị trí nguồn đã chốt; khi nhiều chunk bao phủ, chọn chunk có start_char gần vị trí nhất từ phía trước. Grounding dùng cùng 5 test mỗi cấu hình, xét đủ bằng chứng trong cả top-3; không đo độ chính xác câu trả lời LLM.

| Strategy | Coherence /2 (10 mẫu) | Metadata đủ/đúng | Filter test tuân thủ | Grounding: số mức 0/1/2 | Grounding /2 |
|---|---|---|---|---|---|
| A | 0.90 | 15/15 | 1/1 | 0/0/5 | 2.00 |
| B | 1.60 | 15/15 | 1/1 | 0/0/5 | 2.00 |
| C | 1.60 | 15/15 | 1/1 | 0/0/5 | 2.00 |

Đã chấm **90/90 bản ghi**: 30 coherence, 15 grounding và 45 metadata. Mỗi bản ghi có điểm/kết luận, lý do và người/công cụ chấm trong review_labels.csv. Hồ sơ đọc từng mẫu ở AUDIT_REVIEW.md; các bảng trước khi gộp được giữ trong review_history/.

## Tài nguyên và tái lập

Model load/download lần ingest: 15.311s. Thời gian ingest bên dưới bao gồm encoding/cache, lưu DB và một lần nạp lại để kiểm tra; không bao gồm load/download model. Search gồm round trip SQL, không gồm query embedding. C dùng lại vector cache của B nên không so thời gian encode C như một lần cold start độc lập.

| Strategy | Ký tự/chunk: min/median/max | Tổng ký tự | Tokens (có special tokens) | Ingest + recheck (s) | Vector mới | Phí dịch vụ |
|---|---|---|---|---|---|---|
| A | 52/500/500 | 109160 | 24821 | 14.773 | 241 | 0 USD |
| B | 21/404/500 | 98903 | 22495 | 13.810 | 268 | 0 USD |
| C | 21/404/500 | 98903 | 22495 | 0.629 | 0 | 0 USD |

Phí dịch vụ 0 USD vì chạy local; không tính điện/mạng/hardware. Nạp lại không tăng chunk count; thử xóa stale snapshot có số bản ghi [2, 1, 0]. Backend được mở lại từ các process dev/test riêng nên có kiểm tra lưu bền vững. Phiên bản thư viện ở environment.txt, cấu hình ở strategies.json, cách chạy ở RUNBOOK.md. Lỗi đường dẫn Windows và cách khắc phục có trong setup_notes.md/pipeline_errors.log; không fallback mock.

## Phân tích và kết luận

A–B: chia theo đoạn nâng dev Hit@3 từ 10/15 lên 12/15 và Hit@1 từ 7/15 lên 12/15, nhưng số chunk tăng 241 lên 271. B ít tổng ký tự/token hơn nhờ không overlap. Theo 10 vị trí đã chốt, coherence tổng hợp là 0.90/2 cho A và 1.60/2 cho B/C. B vẫn cắt các đoạn dài và có chunk chỉ chứa running header.

B–C: Hit@1/Hit@3 không đổi trên cả hai split. Với dev q08, B trả các chương [2,1,2], C trả [2,2,2]; tuân thủ filter dev tăng từ 1/2 lên 2/2. Top-3 của cả 5 câu test giống nhau giữa B/C. Filter có ích để giữ phạm vi, nhưng không loại được chunk header cùng chương và chưa làm tăng retrieval accuracy trong mẫu này.

C được chọn trước test do hòa dev hits với B và search trung bình 10,5848 ms so với 10,6482 ms của B. Chênh lệch khoảng 0,0634 ms rất nhỏ và chịu ảnh hưởng thứ tự/cache; không coi đây là bằng chứng C nhanh hơn nói chung.

Test Hit@3 của A là 4/5, cao hơn B/C 3/5; vẫn giữ C theo lựa chọn dev. AI đọc thấy top-3 đủ trả lời cả 5 test, dù có strict miss. q18 cần suy luận ngắn từ định nghĩa thay vì lấy được nguyên lời khuyên trực tiếp; tác giả nên đặc biệt xem lại nhãn này. Không sửa gold đã chốt hoặc thay số primary metric bằng nhãn AI sau khi xem test. Bằng chứng tương đương được tác giả xác nhận có thể được báo riêng như đánh giá bổ sung.

Hai ví dụ lỗi/giới hạn từ trace thật:

- **B/C / q17**, nguồn PDF page 64: Strict Evidence Hit@3 misses because the full frozen quote begins with Each condition is checked in order, outside the retrieved chunk. Top-1 still states the needed first-true-branch rule, so the AI grounding score is 2. Treat this as a strict metric limitation; author must confirm any equivalent-evidence supplement.
- **B/C / q18**, nguồn PDF page 66, 64, 69 (direct gold: 67): The direct recommendation on page 67 is absent, and rank 2 is just a running header from page 64. The glossary on page 69 permits inferring both checks; AI grounding is 2 with this caveat, while strict Hit@3 stays a miss. A chapter filter cannot fix within-chapter chunk noise.

Giữ lựa chọn **C** theo dev. Kết quả test chỉ mô tả 5 câu thuộc corpus này, không chứng minh một chiến lược tốt nhất tổng quát. AI cùng hỗ trợ soạn/chấm có thiên lệch; cỡ mẫu nhỏ, text PDF lỗi, metric chuỗi và latency một lần đo là các giới hạn chính. Cải tiến tiếp theo: review độc lập để kiểm tra độ nhất quán nhãn; cải thiện text PDF trên một thí nghiệm mới; tăng test theo nhiều chương; đánh giá hợp bằng chứng/hybrid như metric/thí nghiệm bổ sung, giữ metric chính.

## AI, artifact và trạng thái nộp

Codex hỗ trợ code, kiểm tra nguồn, soạn benchmark, chạy và phân tích. AI review đọc text theo rubric, có lý do từng mẫu, không phải LLM judge bên ngoài hay nhãn do tác giả xác nhận. Người học cần hiểu/giải thích code; phương pháp và nguồn gốc nhãn được công bố theo RULES.md. Trạng thái push được xác minh riêng bằng lịch sử GitHub và artifacts/publish_receipt.json trong bản local/ZIP nếu có; không suy ra đã nộp bài cho lớp từ việc có link repo. Commit snapshot được ghi trong STUDENT.md và artifacts/source_commit.json nếu đã tạo.

Artifacts: frozen.json, strategies.json, experiment_log.csv; pages/chunks; ingestion_stats.json; traces_dev/test.jsonl; metrics_dev/test.json, metrics.csv; selection.json; coherence/grounding/metadata_review_cases.jsonl; review_labels.csv; grading_manifest.json; review_history/; audit_summary.json; unit_tests.log; environment.txt; input_review/.

## Đánh giá bằng chứng tương đương bổ sung

Sau khi giữ nguyên kết quả gốc, Codex (AI) xác nhận top-1 của B/C-q17 trên đúng PDF page 64 đã đủ quy tắc cần trả lời. Đây là đánh giá bổ sung sau thí nghiệm, không dùng chọn cấu hình, không sửa gold đã chốt và chưa phải xác nhận của tác giả.

| Strategy | Hit@3 gốc | Hit@3 có thêm q17 do AI xác nhận |
|---|---|---|
| A | 4/5 | 4/5 |
| B | 3/5 | 4/5 |
| C | 3/5 | 4/5 |

Chi tiết từng đoạn: supplemental_evidence_reviews.csv. Giữ nguyên lựa chọn C theo dev và mọi số liệu primary ở trên.

## Kiểm chứng tái lập

Đã chạy `--stage all --reproduce`; số hit dev/test khớp bản gốc: True. Bảo toàn file gốc: True. Kết quả mới ở starter/results/reproductions/. Đây là tái lập trên test đã biết, không phải holdout mới; cache và thời gian có thể khác.
