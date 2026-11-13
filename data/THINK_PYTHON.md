# Corpus Think Python 2e: buoc doc va kiem tra

Nguon: https://greenteapress.com/thinkpython2/thinkpython2.pdf

Ban hien tai: 2nd Edition, Version 2.4.1. Giay phep: CC BY-NC 3.0
Unported. Ghi nguon Allen B. Downey / Green Tea Press va cac thay doi;
su dung phi thuong mai.

## Tai lap

Chay tu `starter/`:

```powershell
.\.venv\Scripts\python.exe -m src.prepare_corpus --download
```

Lenh chi tai PDF khi file chua ton tai. No tao `results/pages.jsonl`,
`results/corpus_preview.txt`, `results/ingestion_errors.jsonl` va manifest.
Neu `data/manifest.json` o goc repo da ton tai, manifest moi duoc ghi vao
`data/manifest.generated.json`, de bao toan cac nhan kiem tra thu cong.

## Pham vi

| Chapter | PDF pages (1-based) | Printed pages |
|---|---|---|
| 1 | 23-30 | 1-8 |
| 2 | 31-38 | 9-16 |
| 3 | 39-50 | 17-28 |
| 4 | 51-60 | 29-38 |
| 5 | 61-72 | 39-50 |

Hai trang PDF 38 va 72 chi co running header nen bi loai. Con 48 trang
co van ban; day chua phai ket luan da kiem tra thu cong 48 trang hop le.

## Viec hoc vien can lam truoc benchmark

1. Mo PDF va doi chieu cac trang da trich xuat voi `corpus_preview.txt`.
2. Kiem tra nguon, trang PDF, trang in, chuong, thu tu van ban va code.
3. Phat hien cac trang chi co hinh/bang, van ban loi hoac khong huu ich.
   Neu loai them trang, can cap nhat danh sach corpus va ghi ly do; khong
   chi sua so dem. Dam bao van con it nhat 30 trang noi dung hop le.
4. Trong manifest, doi `content_review_status` cua cac trang duoc chap nhan
   thanh `accepted` sau khi da kiem tra; dien `verified_content_page_count`
   bang so trang thuc te da xac minh. Trang thai hien tai xem manifest;
   cac review bo sung boi AI duoc ghi ro trong `review_provenance` va
   `starter/results/input_review/REVIEW.md`.
5. Viet it nhat 20 cau hoi co dap an va evidence tu van ban da chuan hoa.
   Goi y: 15 dev tu chuong 1-4, 5 test tu chuong 5; ghi han che ve kien
   thuc lien quan giua cac chuong. It nhat 2 cau dev va 1 cau test co filter
   `chapter` duoc cung cap truoc retrieval. Chot benchmark truoc khi thu.

## Han che da quan sat

- Mot so tu bi dinh khi PDF doi kieu chu; khong tu chen khoang trang bang
  quy tac doan mo. Doi chieu evidence voi ca PDF va text da chuan hoa.
- Dau gach noi o cuoi dong duoc giu de tranh sua nham toan tu/code.
- Running headers/footers tren cac trang co noi dung van duoc giu.
- OCR chua duoc su dung. Co chu trich xuat duoc khong tu chung minh
  chat luong van ban hay tinh hop le cua trang.

Buoc nay chua tao embedding, chunk, chi so retrieval hay nhan grounding.
