---
id: S0021
date: 2026-11-08T15:52:04Z
kind: risky
outcome: kept
title: "./mo check-commit --range origin/develop..HEAD 2>&1 | tail -2; git wor"
decision: ""
reversible: yes
deciders: hook
revisit: 
area: infra
plan: 
milestone: M1
test_ids: []
supersedes: []
branch: "docs/adr-0019-repo-split"
commit: 05b6231
evidence: "docs/evidence/ci/2026-07-14T193011Z-544e2a4"
promoted_to: "none"
source: hook
---

# S0021 · ./mo check-commit --range origin/develop..HEAD 2>&1 | tail -2; git wor

## Vì sao đụng tới
Hook PreToolUse ghi tự động khi thấy lệnh có sức phá hoại.

## Lệnh
```
./mo check-commit --range origin/develop..HEAD 2>&1 | tail -2; git worktree remove "/c/Users/NguyenVD/AppData/Local/Temp/claude/bb657f28194a187e/651f6916-13db-489e-84a2-5e5a974fce72/scratchpad/verify" --force && git worktree list
```

## Kết luận
**kept** — Gỡ worktree kiểm tra thứ hai trong scratchpad sau khi xác nhận .steering chỉ lệch CRLF và commit-msg OK trong container.

_Đóng 2026-11-08T15:52:18Z · commit `05b6231`_

## Đã nâng thành
none
