<!--
Bot sẽ tự đăng "PR digest" (tick mới + evidence + specs đã đổi) ở comment đầu tiên.
Phần dưới đây là thứ CHỈ người viết được — đừng chép lại những gì bot đã in.
-->

## Làm gì

<!-- 1-3 câu. Test ID nào, vì sao bây giờ. -->

Implements: <!-- OTA-07, OTA-08 — hoặc `none` nếu PR không gắn test ID -->

## Ba gate của founder

> Chi tiết: `docs/DEVELOPMENT.md`. Ba ô này là hợp đồng review, không phải nghi thức.

- [ ] **Clarify đã xong** — không còn câu hỏi mở nào trong `clarify.md` của feature này
- [ ] **Đã chạy `/audit`** — dán kết luận vào đây:
  - `spec-guardian`:
  - `test-auditor`:
- [ ] **Test [H]** (nếu có): người đã chạy `./mo hw-test`, biên bản ở `docs/evidence/hw/`

## Tự kiểm trước khi xin review

- [ ] `./mo verify` xanh trên máy tôi
- [ ] `./mo trace` không có LỖI
- [ ] Không sửa tay `docs/test-status.*`
- [ ] Đổi `specs/` → đã thêm/cập nhật test vector và `covers:`
- [ ] Dependency mới → đã có ADR (constitution #5, #6)
- [ ] Không có `t.Skip` mới

## Ngoài phạm vi

<!-- Thứ cố tình KHÔNG làm trong PR này, để người review không đi tìm. -->
