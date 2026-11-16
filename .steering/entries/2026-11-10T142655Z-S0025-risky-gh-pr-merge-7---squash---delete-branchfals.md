---
id: S0025
date: 2026-11-10T14:26:55Z
kind: risky
outcome: kept
title: "gh pr merge 7 --squash --delete-branch=false 2>&1 | tail -1; gh pr vie"
decision: ""
reversible: yes
deciders: hook
revisit: 
area: infra
plan: 
milestone: M1
test_ids: []
supersedes: []
branch: "chore/bump-submodules-v0.0.2"
commit: 223908d
evidence: "docs/evidence/ci/2026-07-14T193011Z-544e2a4"
promoted_to: "none"
source: hook
---

# S0025 · gh pr merge 7 --squash --delete-branch=false 2>&1 | tail -1; gh pr vie

## Vì sao đụng tới
Hook PreToolUse ghi tự động khi thấy lệnh có sức phá hoại.

## Lệnh
```
gh pr merge 7 --squash --delete-branch=false 2>&1 | tail -1; gh pr view 7 --json state,mergeCommit --jq '"\(.state) \(.mergeCommit.oid[0:7])"'; T=/tmp/tmp.Qy2u0w6uia && git clone -q --recurse-submodules -b develop git@github.com:NguyenVu1010/MechOps.git /m 2>&1 | tail -1; cd /m && git log --oneline -3 && git submodule foreach -q 'echo " "' && git log origin/develop --format=%B | grep -ciE "co-authored-by:.*claude|claude-session|generated with \[claude"; rm -rf 
```

## Kết luận
**kept** — rm -rf chỉ xoá thư mục mktemp chứa bản clone kiểm tra develop sau khi merge PR #7; không chạm repo.

_Đóng 2026-11-10T14:27:33Z · commit `223908d`_

## Đã nâng thành
none
