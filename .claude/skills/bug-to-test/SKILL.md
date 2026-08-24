---
name: bug-to-test
description: BẮT BUỘC đọc khi phát hiện bug, regression, hành vi sai, hoặc user báo "chỗ này chạy sai". Trigger, bug, lỗi, regression, hỏng, sai, không đúng, fix, sửa lỗi, hotfix.
---

# Bug → test ID mới → rồi mới sửa

Quy tắc catalog #3: **bug mới phát hiện thì thêm test ID mới TRƯỚC khi sửa.**
Catalog chỉ phình ra, không teo lại.

Cám dỗ khi thấy bug là sửa ngay — thường chỉ mất hai phút. Cái mất là: bug đó
không có gì canh, nên nó quay lại. Bug quay lại lần thứ hai đắt gấp nhiều lần
mười phút thêm một test ID.

## Thứ tự

1. **Tái hiện trước.** Chưa tái hiện được thì chưa hiểu bug — đừng sửa theo phỏng đoán.

2. **Cấp ID mới.** Chọn prefix theo nhóm (`OTA`, `TEL`, `PRV`...), lấy số tiếp theo còn trống.
   Sửa **cùng một commit** ở cả hai chỗ, nếu không tracker sẽ bỏ qua ID:
   - `docs/product/05-test-catalog.md` — thêm dòng vào bảng đúng nhóm
   - `tools/testtrack/track.py` — thêm vào `CATALOG` với `(tầng, mô tả ngắn)`

   Đặt mô tả theo **hành vi đúng**, không theo triệu chứng.
   Viết "Digest sai → không start", không viết "sửa lỗi container chạy nhầm image".

3. **Viết test, thấy nó ĐỎ.** Tên theo skill `test-evidence`. Test phải đỏ *vì đúng bug đó*,
   không phải đỏ vì compile lỗi. Test đỏ sai lý do là test vô dụng.

4. **Sửa code.** Tối thiểu để test xanh. Không nhân tiện refactor — PR sửa bug mà lẫn
   refactor thì không ai biết cái nào làm nó xanh trở lại.

5. `./mo verify` → `/audit` → commit với `Implements: <ID mới>`.

## Bug đã lặp lần thứ hai

Ngoài test, thêm **một dòng** vào skill liên quan (`go-conventions`, `contract-guard`...)
ngay lúc còn nhớ. Bug lặp hai lần nghĩa là thiếu một dòng ở đâu đó — skill tốt được
nuôi bằng sự cố, không bằng dự đoán.

## Không được

- Sửa code trước rồi mới thêm test (test viết sau luôn viết vừa khít cái sửa vừa làm).
- Sửa test cho khớp hành vi sai của code. Spec thắng code (constitution #4).
- Gộp nhiều bug vào một ID.
