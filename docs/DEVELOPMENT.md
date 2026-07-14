# Hướng dẫn phát triển (cho người)

> Agent đọc CLAUDE.md — file này dành cho dev. Nội dung trùng nhau chỉ có MỘT nhà:
> vòng lặp & luật ở CLAUDE.md · nguyên tắc bất biến ở constitution.md · "vì sao" ở docs/adr/.

## Cài đặt
1. Go 1.22+, Python 3.11+ (`pip install jsonschema`), Docker, Claude Code
2. `make status` — sinh tracker, xác nhận 49 test ⬜

## Quy trình 1 feature — vai trò của bạn ở 3 gate
| Gate | Việc của bạn | Thời gian |
|---|---|---|
| 1. Clarify | Agent chạy `/feature <tên>` xong sẽ dừng ở clarify.md — trả lời từng câu hỏi thẳng vào file. Giả định sai bị giết ở đây rẻ hơn trong code. | ~15 phút/feature |
| 2. Review PR | Nhìn 3 thứ: tick mới trên docs/test-status.md · click 1 link evidence xem raw log · kết luận spec-guardian + test-auditor. Không cần đọc từng dòng code — evidence tồn tại để bạn không phải làm vậy. | ~5 phút/PR |
| 3. Hardware | Test [H] chỉ người tick: `make hw-test ID=OTA-04 TESTER=<tên> HW="Jetson Orin"` — trả lời checklist, biên bản tự sinh vào docs/evidence/hw/. | theo catalog |

Giữa các gate, agent tự chạy: `/task <ID>` → plan → contract → test đỏ → code → `make verify` → `/audit` → commit.

## Lệnh hằng ngày
- `/feature <tên + milestone + IDs>` · `/task <ID>` · `/audit` — trong Claude Code
- `make verify` · `make status` · `make hw-test` — trong terminal
- 1 phiên = 1 task = 1 nhánh `feat/<ID>-mô-tả`. Task song song → `git worktree`.

## Đọc evidence khi nghi ngờ một tick ✅
1. Mở docs/test-status.md → click link evidence của ID
2. Raw log là output `go test -json` nguyên bản, kèm commit hash trong tên thư mục
3. Tự chạy lại: `go test -run Test<ID bỏ gạch> ./...`
4. Muốn xem agent đã đi đường nào đến tick đó: transcript JSONL của phiên (hooks)

## Khi nào viết ADR / sửa skill
- Chọn giữa ≥2 phương án có hệ quả dài hạn → ADR mới (template: docs/adr/TEMPLATE.md)
- Bug lặp ≥2 lần → thêm 1 dòng vào skill liên quan TRƯỚC khi quên
- Cuối mỗi milestone: 30 phút đọc lại 5 skill, xóa dòng lỗi thời
