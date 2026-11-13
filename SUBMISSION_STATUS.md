# Trạng thái bài làm

Đã hoàn thiện và chạy thực tế phần kỹ thuật:

- Corpus 48 trang, manifest/quyền sử dụng và kiểm tra nguồn.
- 20 câu đã chốt, 15 dev / 5 test, 3 câu filter.
- Embedding model thật, revision cố định, pgvector lưu bền vững và filter SQL.
- A/B/C chạy đủ, nạp lại không trùng và xóa stale chunks đã kiểm chứng.
- Chọn C trên dev trước test; có checksum, trace, latency và chi phí local.
- 7 regression tests đạt; 60 trace / 180 top-3 và metadata 45/45 đã kiểm tra.
- Báo cáo, experiment log, phiên bản môi trường và ví dụ lỗi đã lưu.
- Lệnh tái lập --reproduce đã chạy thật; số hit khớp, kết quả gốc không đổi.
- Đã xuất 90 nhãn có attribution, nhận xét q17 bổ sung và ghi điểm A-s01=0
  theo câu trả lời thực tế của người học. Không tạo thêm nhãn dưới tên tác giả.

Các phần còn cần tác giả thực hiện trước khi coi là bài nộp hoàn tất:

1. Đọc `starter/results/AUDIT_REVIEW.md`, điền ba CSV `human_*_labels.csv`
   sau khi tự kiểm tra. Hiện có 30 mẫu coherence, 15 grounding và 45 bản ghi
   metadata chờ xác nhận; nhãn AI không được giả thành nhãn của tác giả.
2. Chạy `-m src.reporting` để cập nhật bảng điểm tác giả và đọc lại báo cáo.
3. Xác nhận lớp L3A nếu tên repo chưa phản ánh lớp thực tế.
4. Commit snapshot thật được ghi trong STUDENT.md và artifacts/source_commit.json
   khi tạo xong. Trạng thái đẩy repo kiểm chứng bằng lịch sử GitHub và
   artifacts/publish_receipt.json trong bản local/ZIP nếu có. Việc nộp link
   qua kênh lớp chưa được xác nhận; không suy ra từ việc có repo online.

Xem `RUNBOOK.md` để chạy các lệnh. ZIP được tạo bằng
`starter/scripts/package_submission.py`; loại .env, môi trường ảo và cache.
Bản ZIP là hồ sơ để xem xét/xác nhận, chưa thay cho việc nộp bài qua kênh lớp.
