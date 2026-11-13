# Benchmark - Think Python 2e

Trang thai: **da frozen truoc retrieval; da chay dev -> select -> test cho A/B/C**.

Checksum: `benchmark/frozen.json`. Quyet dinh tren dev: `starter/results/selection.json`.
Ket qua: `starter/results/metrics_dev.json`, `metrics_test.json` va trace JSONL.
Nhom nhan AI va nhan tac gia duoc tach ro trong bao cao; tac gia chua xac nhan
bang cham thu cong. Khong chinh lai test hoac tham so theo cac ket qua nay.

Nhat ky review va nguon goc nhan: `starter/results/input_review/REVIEW.md`.
AI da doi chieu PDF/text va dap an; day khong phai cham thu cong coherence
hay grounding. Cac nhan danh gia retrieval ve sau phai ghi dung nguoi cham.

`questions.jsonl` gom 20 cau do AI ho tro soan tu corpus da trich xuat:
15 dev tu chuong 1-4 va 5 test tu chuong 5. Chuong 5 van lien quan kien
thuc voi cac chuong truoc; cach chia nay khong bao dam doc lap hoan toan.

Ba cau filter: q08 (chapter=2), q11 (chapter=3), q16 (test, chapter=5).
Pham vi chuong duoc neu trong cau hoi truoc retrieval. Khong tao filter
tu gold source, gold page hoac dap an. A/B bo qua filter; C chi dung filter
khi truong nay co mat. Khong them dap an vao embedding cua query.

## Quy trinh kiem tra khi thay doi dau vao

1. Hoan tat review corpus trong `data/manifest.json`.
2. Doi chieu tung cau voi PDF va `starter/results/corpus_preview.txt`:
   cau hoi ro rang, dap an dung, evidence du dieu kien va dung trang.
3. Evidence giu cac tu bi dinh va dau gach noi cua ban extract; day khong
   phai loi JSON. Khong sua quote cho dep neu text corpus chua duoc sua
   tuong ung. Neu doi normalization, chuan bi lai corpus va kiem tra lai.
4. Tim cac nguon/trang khac cung ho tro dap an, them `gold_alternatives`
   voi `source_id`, `page`, `evidence_quote` khi can. Hai cau q01 va q03
   da co vi du alternative gold. Nguoi cham can chap nhan bang chung
   tuong duong hop le, khong chi dung mot chuoi hoac mot trang.
5. Chi doi `review_status` tu `pending` thanh `accepted` sau khi thuc su
   kiem tra cau do. Day la nhan review benchmark, khong phai nhan hit,
   coherence hay grounding.

Tu thu muc `starter/`, chay:

```powershell
.\.venv\Scripts\python.exe -m src.validate_benchmark
```

Lenh kiem tra schema, split, filter va quote trong corpus. Bao cao luu tai
`starter/results/benchmark_validation.json`. Chuoi khop khong tu chung
minh dap an dung hay evidence du; van can review noi dung.

## Chot truoc khi retrieval

- Chot tap cau hoi/gold/split sau review, luu commit hoac checksum.
- Ghi tieu chi chon truoc khi xem ket qua: uu tien dev Hit@3, sau do
  dev Hit@1, sau do thoi gian truy xuat neu bang nhau.
- Chi dung dev de sua code, debug truy xuat va chinh tham so. Test gold
  duoc doc de soan/xac minh truoc thi nghiem; khong xem ket qua retrieval
  tren test de tinh chinh.
- Co dinh A/B/C va lua chon tren dev roi moi chay test cho ca ba.
- Khong doi tap test sau khi thay ket qua ma van goi do la holdout doc lap.

## Dinh dang

Moi dong la mot JSON object. Cac truong `review_status` va `type` la bo
sung; cac truong question, answer, gold va split theo BENCHMARK.md.
Ket qua kiem tra va nguon goc nhan duoc ghi trong input_review. Buoc nay
chua co diem retrieval hay nhan cham thu cong coherence/grounding.
