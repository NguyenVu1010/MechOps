---
id: S0003
date: 2026-08-23T08:59:25Z
kind: risky
outcome: reverted
title: "cd /c/Users/AnhND0904/workspace/MechOps/nrm -rf docs/evidence/ci/2026-"
area: infra
plan: 
milestone: M1
test_ids: []
supersedes: []
branch: "main"
commit: 9f5be49
evidence: "docs/evidence/ci/2026-08-23T085833Z-9f5be49"
promoted_to: "none — tracker da co hook chan ghi tay, day chi la don du lieu gia lap"
source: hook
---

# S0003 · cd /c/Users/AnhND0904/workspace/MechOps\nrm -rf docs/evidence/ci/2026-

## Vì sao đụng tới
Hook PreToolUse ghi tự động khi thấy lệnh có sức phá hoại.

## Lệnh
```
cd /c/Users/AnhND0904/workspace/MechOps\nrm -rf docs/evidence/ci/2026-08-2*\nn0=$(ls docs/evidence/ci | wc -l)\nbash ./mo verify >/dev/null 2>&1; bash ./mo verify >/dev/null 2>&1\necho \
```

## Kết luận
**reverted** — Hoan tac trang thai TEL-01 gia lap dung de kiem track.py chi sinh evidence khi co ID khop. docs/test-status.* tro ve 0/49.

_Đóng 2026-08-23T08:59:48Z · commit `9f5be49`_

## Đã nâng thành
none — tracker da co hook chan ghi tay, day chi la don du lieu gia lap
