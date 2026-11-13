# Protocol đã chốt trước retrieval

Thời điểm và checksum: `benchmark/frozen.json`.

- Corpus: 48 trang của Think Python 2e; giữ normalization đã review.
- Benchmark: 15 dev / 5 test; 3 câu có chapter filter, gồm 1 test.
- Model: sentence-transformers/all-MiniLM-L6-v2, revision được pin trong
  strategies.json. Đổi từ gợi ý E5 sang MiniLM trước retrieval vì dữ liệu
  và query đều tiếng Anh, model nhỏ phù hợp CPU. Không dùng kết quả để chọn model.
- Plain text cho query và document, không thêm prefix của E5. Chuẩn hóa vector,
  cosine, exact pgvector cho cả ba cấu hình; top_k=3.
- A: 500 ký tự, overlap 50. B: theo đoạn, giới hạn 500, overlap 0. C dùng
  chính chunk/vector của B, chỉ thêm filter chapter do câu hỏi cung cấp.
- Giả thuyết: A có thể cắt mất điều kiện; B có thể giữ ý tốt hơn nhưng đoạn
  dài vẫn bị tách; C có thể giảm nhiễu ở câu có filter nhưng không cải thiện
  câu không filter. Đây là giả thuyết, không phải kết quả.
- Chọn cấu hình theo dev: Hit@3, rồi Hit@1, rồi thời gian search trung bình
  thấp hơn, cuối cùng mã cấu hình theo alphabet. Thời gian là một lần đo nhỏ,
  có cache và nhiễu; không suy rộng về hiệu năng backend.
- Lưu selection.json trước khi chạy test. Không chỉnh cấu hình bằng test.
- Coherence: 10 vị trí đã cố định trong coherence_positions.json. Khi có
  nhiều chunk chứa vị trí, chọn chunk bắt đầu gần vị trí nhất từ phía trước.
- Metric chính cần đủ evidence trong MỘT chunk đúng nguồn/trang; không gộp
  nhiều chunk để biến một miss thành hit. Chấp nhận gold thay thế đã ghi.
- Grounding, coherence và metadata có bảng review riêng. Nhãn do AI hỗ trợ
  chấm phải ghi rõ người chấm và không tự gọi là xác nhận thủ công của tác giả.

Nguồn model: https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2
Nguồn backend: https://github.com/pgvector/pgvector
