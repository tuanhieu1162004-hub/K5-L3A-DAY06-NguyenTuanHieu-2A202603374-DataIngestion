# Kiểm tra đầu vào Think Python 2e

Người kiểm tra bổ sung: **Codex (AI)**, theo yêu cầu tự chạy và tự kiểm tra.
Thời điểm cụ thể được ghi trong manifest, từng câu hỏi và snapshot đi kèm.

## Corpus

- 25 trang đã có nhãn accepted được giữ nguyên. Lần này kiểm tra lại nguồn,
  text và metadata của chúng bằng chương trình; không ghi nhận đã xem ảnh
  hoặc thực hiện lại kiểm tra nội dung thủ công của con người trên 25 trang đó.
- 23 trang PDF 49–71 được AI đọc toàn bộ text và xem ảnh render từ PDF gốc.
  Mỗi trang có nội dung bài học, code, glossary hoặc bài tập hữu ích. Trang
  50 và 60 ngắn nhưng có yêu cầu bài tập thực sự, không chỉ có tài liệu tham khảo.
- Trang 38 và 72 đã được xem ảnh: chỉ có running header, tiếp tục bị loại.
- Tổng 48 trang accepted, đủ mức tối thiểu 30 trang của đề. Không áp ngưỡng
  1.500 ký tự cho trang PDF; ngưỡng đó thuộc quy tắc đơn vị nguồn không phân trang.
- Đã xem trang nhan đề/copyright, xác nhận Version 2.4.1 và CC BY-NC 3.0.
- SHA256 PDF khớp manifest; text lưu của cả 48 trang khớp phép trích xuất lại;
  số trang, chương và số ký tự khớp inventory. Chi tiết: `source_checks.json`.
- Ghi nhận theo từng trang: `corpus_review.csv`. Ảnh đối chiếu: `sheet_01.png`
  đến `sheet_07.png`, có nhãn số trang PDF.

## Kiểm tra đáp án và evidence

Các nhãn accepted trước đó của 20 câu được giữ nguyên. AI đọc lại câu hỏi,
đáp án và đoạn gold; đối chiếu sự hiện diện bằng pypdf và PyMuPDF độc lập.
Đây là kiểm tra đầu vào benchmark, **không phải nhãn grounding/coherence
thủ công của con người**, cũng không phải kết quả truy xuất.

| Câu | Cơ sở đáp án trong nguồn |
|---|---|
| q01 | Định nghĩa interpreter ở glossary và phần Running Python. |
| q02 | Đoạn ambiguity nêu ngôn ngữ hình thức được thiết kế gần như/hoàn toàn không mơ hồ. |
| q03 | Prompt báo interpreter sẵn sàng nhận code/input. |
| q04 | Phần arithmetic xác định ** là exponentiation; bổ sung ví dụ precedence ở trang 34. |
| q05 | Định nghĩa variable là tên tham chiếu một giá trị; bổ sung glossary trang 36. |
| q06 | class được xác định là keyword và keyword không được dùng làm tên biến. |
| q07 | Script mode tính expression nhưng không tự hiển thị; cần print. |
| q08 | String multiplication là repetition; toán hạng còn lại phải là integer. |
| q09 | int bỏ phần thập phân, không làm tròn về số nguyên gần nhất. |
| q10 | Body chỉ chạy khi gọi hàm; bổ sung giải thích flow ở trang 43. |
| q11 | Local variable chỉ tồn tại/dùng trong hàm; bổ sung glossary trang 48. |
| q12 | Fruitful có kết quả; void không có giá trị hữu ích/luôn trả None; bổ sung glossary trang 48. |
| q13 | Đối số được đánh giá trước khi gọi hàm. |
| q14 | Đoạn refactoring mô tả cải thiện interface và tái sử dụng; bổ sung glossary trang 58. |
| q15 | Docstring ở đầu hàm và mô tả interface; bổ sung glossary trang 59. |
| q16 | Glossary nêu floor division làm tròn xuống về âm vô cực; bổ sung định nghĩa round down ở trang 61. |
| q17 | Chained conditional chỉ chạy nhánh đúng đầu tiên và kết thúc statement. |
| q18 | Cần base case không gọi đệ quy và phải bảo đảm tới được base case. |
| q19 | input trả nội dung người dùng nhập dưới dạng string. |
| q20 | Dòng báo lỗi là nơi phát hiện; nguyên nhân có thể ở trước đó. |

Ba filter ở q08/q11/q16 được cung cấp trong câu hỏi và khớp chương của
gold. Không dùng gold page/source hay đáp án làm filter. Giữ nguyên 15 dev /
5 test. Bổ sung 8 gold thay thế trước khi có thí nghiệm retrieval; cả đoạn
gold chính và thay thế cần được chấp nhận khi chấm. Danh sách chưa bảo đảm
bao quát mọi cách diễn đạt bằng chứng tương đương, nên vẫn cần audit lỗi.

## Giới hạn và bước tiếp theo

- Text còn từ bị dính do đổi font, dấu nối cuối dòng và running headers.
  Không sửa normalization sau khi xem test mà bỏ qua việc chốt benchmark lại.
- Bảng, hình và công thức không được biểu diễn hoàn chỉnh bằng text.
- Test chỉ có 5 câu thuộc một chương, không đại diện mọi chủ đề.
- Cùng AI hỗ trợ viết và kiểm tra câu hỏi có nguy cơ thiên lệch.
- Chưa có thí nghiệm retrieval do agent chạy ở bước kiểm tra này. Chưa có
  nhãn coherence/grounding hoặc điểm Hit@1/Hit@3.
- `Ready for manual freeze: True` chỉ là đủ điều kiện chốt đầu vào; chưa tự
  biến thành một benchmark đã frozen. Ghi checksum/commit và tiêu chí chọn
  trước khi chạy A/B/C; dùng dev để điều chỉnh rồi mới đánh giá test.

Tái lập kiểm tra nguồn từ `starter/`:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-review.txt
.\.venv\Scripts\python.exe scripts/check_input_sources.py
.\.venv\Scripts\python.exe -m src.validate_benchmark
```

Nguồn sách: Allen B. Downey / Green Tea Press,
https://greenteapress.com/thinkpython2/thinkpython2.pdf, CC BY-NC 3.0.
Ảnh chỉ là các trang được render để đối chiếu; không thay đổi nội dung sách.
