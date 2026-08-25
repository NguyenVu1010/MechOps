---
id: S0011
date: 2026-08-25T19:34:04Z
kind: risky
outcome: open
title: "cd /c/Users/AnhND0904/workspace/MechOps ; bash ./mo steer close S0010"
decision: ""
reversible: yes
deciders: hook
revisit: 
area: infra
plan: m1-contract-v01
milestone: M1
test_ids: []
supersedes: []
branch: "feat/ai-flow"
commit: ce0a263
evidence: "docs/evidence/ci/2026-07-14T193011Z-544e2a4"
promoted_to: ""
source: hook
---

# S0011 · cd /c/Users/AnhND0904/workspace/MechOps ; bash ./mo steer close S0010 

## Vì sao đụng tới
Hook PreToolUse ghi tự động khi thấy lệnh có sức phá hoại.

## Lệnh
```
cd /c/Users/AnhND0904/workspace/MechOps\nbash ./mo steer close S0010 --outcome reverted \\\n  --why "Bao oan: hook khop chu 'rm -rf' trong noi dung heredoc cua commit message, khong phai lenh that. Da cat heredoc truoc khi khop, va sua tiep lo json_str cat chuoi o dau ngoac kep dau tien." \\\n  --promoted "record-risky.sh: scan=\\${cmd%%<<*} + _lib.sh json_str xu ly dau escape; ma tran 20 ca trong scratchpad"\nbash ./mo steer index >/dev/null\ngit add -A\ngit commit -F - <<'MSG'\nHook risky: cắt heredoc, và vá lỗ json_str bỏ sót cờ sau dấu ngoặc kép\n\nHai lỗi cùng lộ ra khi commit lần trước.\n\n1. Báo oan: hook khớp cụm "rm -rf" nằm trong nội dung heredoc của chính commit\n   message (S0010), không phải lệnh thật. Giờ chỉ soi phần trước `<<`.\n   Cảnh báo oan là cảnh báo người ta học cách bỏ qua.\n\n2. Bỏ sót thật, nặng hơn: `json_str` dùng mẫu `"[^"]*"` nên dừng ở dấu `"` đầu\n   tiên, kể cả dấu đã escape. Nghĩa là `git commit -m "fix" --amend` bị cắt thành\n   `git commit -m ` và cờ `--amend` phía sau không bao giờ được thấy — hook im\n   lặng đúng lúc cần ghi nhất. Cùng họ với lỗi "cờ chèn vào giữa" đã sửa trước\n   đó: mẫu khớp bằng chuỗi thì luôn có một cách viết lách được.\n   Với `file_path` thì vô hại (đường dẫn không có ngoặc kép) nên guard-tracker\n   không bị ảnh hưởng.\n\nKiểm: ma trận 20 ca — 9 phải ghi, 4 phải bỏ qua, 2 ca heredoc, 4 ca cờ nằm sau\ntham số có ngoặc kép, 1 ca commit -m thường. Tất cả PASS.\n\nImplements: none\nMSG
```

## Kết luận
<điền khi đóng>

## Đã nâng thành
<điền khi đóng: test ID / ADR-00NN / dòng trong skill nào / none>
