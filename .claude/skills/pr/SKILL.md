---
name: pr
description: Dựng PR đã sẵn sàng để founder duyệt trong 5 phút — audit, code-review, digest, rồi mở PR.
argument-hint: "[tiêu đề PR]"
disable-model-invocation: true
allowed-tools: Bash(git status:*) Bash(git diff:*) Bash(git log:*) Bash(git push:*) Bash(gh pr:*) Bash(bash ./mo:*)
---

# PR — chuẩn bị để người khác duyệt được

Mục tiêu không phải "mở PR" mà là **PR không cần hỏi lại câu nào**.

## Thứ tự, không đảo

1. `./mo verify` — phải xanh. Đỏ thì dừng ở đây, chưa có gì để review.
2. `./mo trace` — không được có dòng `LỖI`.
3. `/audit` — cả `spec-guardian` lẫn `test-auditor` phải PASS. Giữ nguyên văn kết luận, sẽ dán vào PR.
4. `/code-review` — đọc theo `REVIEW.md`. Sửa hết 🔴 Important trước khi đi tiếp.
   Nit thì tự quyết: sửa hoặc ghi rõ vì sao không sửa.
5. `./mo digest --base origin/main --head HEAD` — lấy phần thân máy sinh.
6. `git push -u origin <nhánh>` rồi `gh pr create`.

## Thân PR

Theo `.github/pull_request_template.md`. Điền **đúng phần của người**:

- Mục "Làm gì": 1–3 câu, test ID nào và vì sao bây giờ.
- Dòng `Implements:` khớp với ID thật sự chạm.
- Dán kết luận hai kiểm toán viên ở bước 3 vào đúng hai ô của nó.
- Mục "Ngoài phạm vi": nói rõ thứ cố tình không làm, để người review khỏi đi tìm.

Không chép lại nội dung digest — bot đã đăng nó thành comment riêng.

## Không làm

- Không merge. Merge vào `main` luôn là việc của người (constitution #9).
- Không mở PR khi có test [H] chưa ai chạy mà PR lại tự nhận là xong.
- Không "tạm bỏ qua" một 🔴 Important với lý do sẽ sửa ở PR sau.
