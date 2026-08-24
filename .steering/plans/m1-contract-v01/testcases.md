---
plan: m1-contract-v01
milestone: M1
status: draft
covers: [TEL-01, TEL-07]
adr: [0001]
requirements:
  - docs/protocol-notes.md#3
  - docs/product/06-spec-management.md
---

# m1-contract-v01 · testcases — LÀM SAO BIẾT XONG

> Đây là **thiết kế test**, không phải danh sách ID. Danh sách ID là
> `docs/product/05-test-catalog.md` — nguồn sự thật duy nhất, đừng chép lại.
> Mỗi mục dưới đây là một ID trong `covers:` của spec.md.

## <TEST-ID> · [tầng] · <mô tả ngắn từ catalog>

- **Tiền đề:** <trạng thái ban đầu, fixture, dữ liệu cần có>
- **Thao tác:** <làm gì để kích hoạt>
- **Mong đợi:** <quan sát được từ bên ngoài, không phải 'không lỗi'>
- **Bằng chứng:** <dòng log nào, hàng nào trong DB, event nào>
- **Tên test:** `Test<ID bỏ gạch>_<MôTả>`

## ID đề xuất thêm vào catalog

> Hành vi feature này cần canh mà catalog chưa có ID. Thêm vào
> `05-test-catalog.md` + `CATALOG` của `track.py` CÙNG một commit
> (quy tắc catalog #3) TRƯỚC khi dùng — `./mo trace` sẽ chặn nếu quên.

- <chưa có / hoặc: OTA-13 — [I] — mô tả hành vi>
