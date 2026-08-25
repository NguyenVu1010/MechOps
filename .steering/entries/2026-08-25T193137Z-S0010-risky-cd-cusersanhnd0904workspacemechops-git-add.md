---
id: S0010
date: 2026-08-25T19:31:37Z
kind: risky
outcome: open
title: "cd /c/Users/AnhND0904/workspace/MechOps ; git add -A ; git commit -F -"
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
commit: 2e7338f
evidence: "docs/evidence/ci/2026-07-14T193011Z-544e2a4"
promoted_to: ""
source: hook
---

# S0010 · cd /c/Users/AnhND0904/workspace/MechOps ; git add -A ; git commit -F -

## Vì sao đụng tới
Hook PreToolUse ghi tự động khi thấy lệnh có sức phá hoại.

## Lệnh
```
cd /c/Users/AnhND0904/workspace/MechOps\ngit add -A\ngit commit -F - <<'MSG'\n.steering v2: mốc thời gian, vòng đời plan, và chốt chặn hợp đồng\n\nBốn thay đổi, mỗi cái thêm một chốt chặn MÁY kiểm chứ không thêm một dòng văn bản\n(ADR-0011).\n\n1. Tên mục nhật ký mở đầu bằng mốc UTC, dạng y hệt docs/evidence/ci/ — một quy\n   ước cho mọi dấu thời gian trong repo, không phải hai. `ls entries/` đọc ra\n   được dòng thời gian mà không mở file nào. trace kiểm mốc khớp `date:`: lệch\n   nghĩa là có người đổi tên tay, và tên đang nói dối về lúc sự việc xảy ra.\n\n2. Plan bị bỏ có cửa ra hợp lệ: `plan abandon` giữ nguyên thư mục, bắt buộc\n   `--why`, tự sinh mục nhật ký. Trước đó vòng đời chỉ draft->locked->frozen và\n   freeze đòi cả bốn cổng, nên cửa duy nhất là `rm -rf` — đã mất một plan đúng\n   như thế (S0007), không để lại gì kể cả trong git.\n   Thêm HISTORY.md: dòng thời gian gộp plan, cổng chốt, đáp án clarify của\n   founder, mục nhật ký, ADR. INDEX trả lời \
```

## Kết luận
<điền khi đóng>

## Đã nâng thành
<điền khi đóng: test ID / ADR-00NN / dòng trong skill nào / none>
