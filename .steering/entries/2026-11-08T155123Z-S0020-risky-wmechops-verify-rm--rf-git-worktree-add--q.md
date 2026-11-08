---
id: S0020
date: 2026-11-08T15:51:23Z
kind: risky
outcome: kept
title: "W=../mechops-verify && rm -rf  && git worktree add -q  HEAD && cd"
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

# S0020 · W=../mechops-verify && rm -rf  && git worktree add -q  HEAD && cd 

## Vì sao đụng tới
Hook PreToolUse ghi tự động khi thấy lệnh có sức phá hoại.

## Lệnh
```
W=../mechops-verify && rm -rf  && git worktree add -q  HEAD && cd  && PYTHONIOENCODING=utf-8 python tools/trace/trace.py 2>&1 | tail -1 && PYTHONIOENCODING=utf-8 python tools/steering/steer.py index >/dev/null 2>&1; git status --short | head; echo "(rỗng = .steering khớp)"; PYTHONIOENCODING=utf-8 python tools/checks/commit_msg.py --range origin/develop..HEAD 2>&1 | tail -1; cd .. && git -C MechOps worktree remove --force mechops-verify
```

## Kết luận
**kept** — Xoá worktree tạm dùng để chạy trace/steer index trên đúng nội dung commit 05b6231; không chạm repo chính.

_Đóng 2026-11-08T15:52:16Z · commit `05b6231`_

## Đã nâng thành
none
