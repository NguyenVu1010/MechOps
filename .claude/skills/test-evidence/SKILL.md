---
name: test-evidence
description: BẮT BUỘC đọc khi viết test, chạy test, hoặc làm việc với test-status/tracker/evidence. Trigger với từ khóa: test, tick, xanh, evidence, catalog, coverage, TestXXX.
---

# Test & Evidence

## Naming — đây là hợp đồng với tracker
- Test Go: `Test<ID bỏ dấu gạch><số>_<MôTảNgắn>` — ví dụ `TestOTA07_DigestMismatch`, `TestPRB03_ProbeDeath`.
- Một test cover nhiều ID → dùng subtest: `t.Run("OTA02_HealthFailRollback", ...)`.
- ID không có trong catalog → tracker bỏ qua. Muốn thêm ID mới: sửa CATALOG trong track.py + docs/05-test-catalog.md CÙNG một commit (quy tắc "bug mới → test ID mới trước khi sửa").

## Tier
- [U]: file `*_test.go` thường, chạy mọi PR.
- [I]: build tag `//go:build integration`, cần compose up. Chạy `make test-integration`.
- [H]: KHÔNG viết test Go cho tier này. Người chạy `make hw-test`. Claude không bao giờ tick [H].

## Cấm
- `t.Skip` để né test đỏ. Test đỏ = việc chưa xong.
- Sửa test cho khớp bug của code. Spec thắng code.
- Ghi vào docs/test-status.* — hook chặn, và đó là chủ đích.

## Lệnh duy nhất để tick
`make verify` → chạy test với `-json`, pipe vào track.py, evidence tự lưu vào docs/evidence/ci/.
