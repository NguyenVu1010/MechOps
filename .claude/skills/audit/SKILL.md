---
name: audit
description: Chạy hai kiểm toán viên độc lập trước khi commit — spec-guardian rồi test-auditor.
disable-model-invocation: true
allowed-tools: Bash(git diff:*) Bash(git status:*) Bash(git log:*) Bash(bash ./mo:*)
---

# Audit — hai kiểm toán viên

Chạy **tuần tự**, không gộp, không tự làm thay:

1. Subagent `spec-guardian` — review toàn bộ diff hiện tại về mặt contract.
2. Subagent `test-auditor` — soi các test ID vừa tick trong phiên.

Báo cáo PASS/FAIL của **cả hai**, nguyên văn, kèm `file:dòng` nếu có vi phạm.

## Vì sao tách khỏi phiên chính

Người vừa viết code là người dở nhất để kiểm code đó — đã quen tay với chính giả
định của mình. Hai subagent có context riêng, không thấy hội thoại vừa rồi, nên
đọc diff bằng mắt lạnh. Đó là toàn bộ giá trị; gộp lại là mất.

## Sau khi có kết quả

- **Cả hai PASS** → commit, message chứa dòng `Implements: <các ID>`.
- **Có FAIL** → liệt kê vi phạm và **DỪNG**. Không tự sửa rồi tự tuyên bố đã xong;
  sửa xong phải chạy lại `/audit` từ đầu.

Không bao giờ commit khi một trong hai FAIL, kể cả khi vi phạm "trông có vẻ nhỏ".
