# Ghi nhận setup thực tế

- PostgreSQL 16.16 và pgvector 0.8.7 được kiểm tra kết nối thành công.
- Cài torch==2.9.1+cpu vào `starter/.venv` gặp OSError [Errno 2] ở file
  `torch/include/ATen/native/transformers/cuda/mem_eff_attention/iterators/predicated_tile_access_iterator_residual_last.h`.
  Đường dẫn repo lồng nhau làm đường dẫn cài đặt vượt giới hạn Windows.
- Khắc phục: tạo `.venv` ở thư mục ngoài cùng workspace, dùng
  `..\..\.venv\Scripts\python.exe` khi đứng trong starter. Không dùng mock
  embeddings và không thay đổi cấu hình model dựa trên dev/test.
- Model dùng cho thí nghiệm đã đổi từ gợi ý E5 sang MiniLM trước retrieval;
  lý do, revision và tham số được ghi trong cấu hình và protocol đã chốt.
- Cache Hugging Face tại starter/.cache cũng gặp giới hạn đường dẫn khi
  ghi tokenizer_config.json. Đã chuyển cache sang .cache ở thư mục ngoài
  cùng workspace, giữ nguyên model revision, dữ liệu và tham số.
