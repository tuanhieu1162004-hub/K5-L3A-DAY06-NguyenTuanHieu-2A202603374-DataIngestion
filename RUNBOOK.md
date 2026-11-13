# Chạy bài Think Python — Nguyễn Tuấn Hiếu

MSSV: 2A202603374. Repo bài nộp được người học cung cấp:
https://github.com/tuanhieu1162004-hub/K5-L3A-DAY06-NguyenTuanHieu-2A202603374-DataIngestion

## Môi trường Windows

Repo nằm trong hai thư mục trùng tên. Môi trường `starter/.venv` cũ gặp lỗi
Windows giới hạn đường dẫn khi cài PyTorch. Môi trường chạy đầy đủ được tạo
ở **thư mục ngoài cùng của workspace**. Tất cả lệnh dưới chạy từ `starter/`:

```powershell
# Nếu tạo lại môi trường từ đầu:
python -m venv ..\..\.venv
..\..\.venv\Scripts\python.exe -m pip install torch==2.9.1 --index-url https://download.pytorch.org/whl/cpu
..\..\.venv\Scripts\python.exe -m pip install -r requirements.txt

# Chỉ tạo .env nếu chưa có; file này không được đưa lên Git:
if (!(Test-Path .env)) { Copy-Item .env.example .env }
docker compose -p day6_student_starter up -d --wait
..\..\.venv\Scripts\python.exe scripts/check_setup.py
```

Model tải lần đầu cần mạng và dung lượng ổ đĩa. Văn bản sách được embedding
tại máy, không gửi sang dịch vụ embedding trả phí. Model/cache trong
`.cache/` ở thư mục ngoài cùng workspace không nằm trong repo bài nộp;
không đưa cache hoặc môi trường ảo vào bài nộp.

## Dữ liệu và benchmark

- PDF: `starter/data/thinkpython2.pdf`, từ nguồn Green Tea Press chính thức.
- Manifest: `data/manifest.json` ở gốc repo; 48 trang chương 1–5, loại PDF
  page 38/72 chỉ có header. Giữ số trang PDF gốc và printed_page.
- Giấy phép nội dung: CC BY-NC 3.0; ghi nguồn Allen B. Downey / Green Tea
  Press và các bước trích xuất/chia chunk; chỉ sử dụng phi thương mại.
- `benchmark/questions.jsonl`: 20 câu, 15 dev / 5 test, 3 filter chapter.
- `artifacts/strategies.json`: model revision và ba cấu hình.
- `benchmark/frozen.json`: checksum đầu vào chốt trước retrieval.
- `benchmark/coherence_positions.json`: 10 vị trí mẫu chốt trước khi chấm.

`.gitattributes` giữ nguyên byte/line endings để SHA256 không đổi khi clone
trên Windows/Linux. Không tự format hoặc đổi xuống dòng các file đã frozen.

```powershell
..\..\.venv\Scripts\python.exe -m src.validate_benchmark
..\..\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Nếu cần chuẩn bị lại PDF, dùng `-m src.prepare_corpus --download`. Lệnh tạo
manifest.generated.json khi manifest chính đã tồn tại. Không ghi đè manifest
đã review/frozen bằng bản generated. Nếu thực sự đổi corpus/normalization,
cần một thí nghiệm mới, chốt lại benchmark trước khi nhìn kết quả test mới.

## Chạy pipeline

Trên một bản bài chưa có kết quả:

```powershell
..\..\.venv\Scripts\python.exe -m src.run --stage all
```

Hoặc chạy lần lượt để học từng phần:

```powershell
..\..\.venv\Scripts\python.exe -m src.run --stage freeze
..\..\.venv\Scripts\python.exe -m src.run --stage ingest
..\..\.venv\Scripts\python.exe -m src.run --stage dev
..\..\.venv\Scripts\python.exe -m src.run --stage select
..\..\.venv\Scripts\python.exe -m src.run --stage test
..\..\.venv\Scripts\python.exe -m src.run --stage audit-export
```

Khi có kết quả test sẵn, `all` xác minh checksum và giữ kết quả. Để chạy lại
ngay từ repo đã có artifact mà không chuyển/xóa file, dùng:

```powershell
..\..\.venv\Scripts\python.exe -m src.run --stage all --reproduce
```

Kết quả mới nằm trong `starter/results/reproductions/<run_id>/`. Chương trình
so sánh số hit với bản gốc và xác minh các trace/selection gốc không đổi.
Cache model/vector có thể được dùng lại, vì vậy thời gian không phải cold start.
Đây là tái lập trên bộ test đã biết, không phải holdout mới. Tiêu chí thời gian
có thể chọn B thay C khi hai cấu hình hòa điểm; lựa chọn gốc vẫn được giữ.

## Mã nguồn để giải thích bài

1. `src/ingestion.py`: trích xuất PDF, NFC, giữ thụt lề và source/page.
2. `src/chunking.py`: A fixed 500/50; B theo đoạn tối đa 500, giữ offsets.
3. `src/embeddings.py`: MiniLM local, kiểm tra token, normalize vector và cache.
4. `src/store.py`: bảng day6_chunks, thay snapshot nguyên tử theo strategy,
   cosine exact và filter chapter trong SQL có tham số.
5. `src/evaluation.py`: nguồn/trang + đầy đủ evidence trong một chunk,
   chấp nhận documented alternative gold; Hit@1 và Evidence Hit@3.
6. `src/run.py`: freeze, ingest, dev, select, test và xuất mẫu audit.

Model MiniLM dùng plain text cho cả query/document, không có prefix E5.
B và C dùng cùng chunk/vector; chỉ C áp dụng filter khi câu hỏi có filter.
Nạp lại một strategy thay toàn bộ snapshot trong transaction, không ảnh hưởng
strategy khác; chunk cũ/tài liệu bị loại cũng được xóa khỏi snapshot đó.

## Kết quả và giới hạn

```powershell
# Kiểm tra kết quả đã lưu, không chạy lại test:
..\..\.venv\Scripts\python.exe scripts/verify_results.py
# Tạo lại bảng/báo cáo từ số liệu và nhãn AI đã lưu:
..\..\.venv\Scripts\python.exe -m src.reporting
..\..\.venv\Scripts\python.exe -m src.review_sheet
```

Mở `starter/results/AUDIT_REVIEW.md` để xem text và nguồn của từng mẫu.
Điền ba `human_*_labels.csv` sau khi tự đối chiếu; không gán nhãn AI thành
nhãn của tác giả. Báo cáo hiện trình bày điểm AI và trạng thái chờ xác nhận.

Đã có `attributed_review_labels.csv` gồm 90 nhãn với người/công cụ chấm rõ
ràng. `supplemental_evidence_reviews.csv` và bảng supplementary metrics giải
thích B/C-q17; đây là review AI sau thí nghiệm, không thay primary metric.
Điểm A-s01=0 do người học thực sự cung cấp được ghi riêng cùng provenance;
không tự tạo lý do hoặc các điểm khác dưới tên người học.

Xem `starter/results/` và báo cáo cá nhân trong `report/individual/`.
Trace có cả ID/text/score/metadata, requested/applied filter và gold.
Không suy luận nhãn coherence/grounding từ Hit@3. Nhãn do AI hỗ trợ review
được ghi rõ; cột xác nhận/chấm của tác giả cần được điền trung thực.

Pipeline không tạo chatbot hoặc câu trả lời LLM. Grounding đo độ đủ bằng
chứng truy xuất. Test chỉ 5 câu trong một chương; thời gian đo chịu ảnh hưởng
cache, thứ tự query và máy local. Phí dịch vụ 0 USD không bao gồm điện/mạng.

Nguồn: [Think Python](https://greenteapress.com/wp/think-python-2e/),
[MiniLM model card](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2),
[pgvector](https://github.com/pgvector/pgvector).
