---
id: S0013
date: 2026-09-01T03:55:45Z
kind: risky
outcome: reverted
title: "git checkout -- docs/test-status.json docs/test-status.md && rm -rf d"
decision: ""
reversible: yes
deciders: hook
revisit: 
area: infra
plan: 
milestone: M1
test_ids: []
supersedes: []
branch: "develop"
commit: 36f2c06
evidence: "docs/evidence/ci/2026-09-01T035534Z-36f2c06"
promoted_to: "none — hook bao dung, day la rm -rf that"
source: hook
---

# S0013 · git checkout -- docs/test-status.json docs/test-status.md && rm -rf d

## Vì sao đụng tới
Hook PreToolUse ghi tự động khi thấy lệnh có sức phá hoại.

## Lệnh
```
git checkout -- docs/test-status.json docs/test-status.md && rm -rf "docs/evidence/ci/2026-09-01T035534Z-36f2c06" && echo "đã dọn test dương" && echo "=== PROGRESS.md còn bẩn vì gì ===" && git diff -- docs/PROGRESS.md | grep -E '^[-+]' | grep -v '^[-+][-+]' && echo "=== chỗ progress.py đặt timestamp ===" && grep -n "Cập nhật\\|now()\\|updated\\|strftime" tools/report/progress.py
```

## Kết luận
**reverted** — Chay test duong cho ban va track.py: nap mot dong go-json gia de TEL-01 tick, xac nhan tracker VAN duoc ghi khi co ID doi trang thai. Sau do hoan tracker va xoa thu muc evidence vua sinh — day la du lieu test, khong phai ket qua do that.

_Đóng 2026-09-01T03:56:53Z · commit `36f2c06`_

## Đã nâng thành
none — hook bao dung, day la rm -rf that
