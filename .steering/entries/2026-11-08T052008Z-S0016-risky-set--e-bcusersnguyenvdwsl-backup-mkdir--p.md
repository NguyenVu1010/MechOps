---
id: S0016
date: 2026-11-08T05:20:08Z
kind: risky
outcome: kept
title: "set -e; B=/c/Users/NguyenVD/wsl-backup; mkdir -p  && cd  && rm -rf"
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
commit: 5a9f8b6
evidence: "docs/evidence/ci/2026-07-14T193011Z-544e2a4"
promoted_to: "none"
source: hook
---

# S0016 · set -e; B=/c/Users/NguyenVD/wsl-backup; mkdir -p  && cd  && rm -rf

## Vì sao đụng tới
Hook PreToolUse ghi tự động khi thấy lệnh có sức phá hoại.

## Lệnh
```
set -e; B=/c/Users/NguyenVD/wsl-backup; mkdir -p  && cd  && rm -rf mechops-before-rewrite.git && git clone -q --mirror git@github.com:NguyenVu1010/MechOps.git mechops-before-rewrite.git && cd mechops-before-rewrite.git && git bundle create ../mechops-before-rewrite-20261108.bundle --all 2>&1 | tail -1 && git for-each-ref --format='%(refname) %(objectname:short)' | grep -v refs/pull && ls -la ../mechops-before-rewrite-20261108.bundle
```

## Kết luận
**kept** — Sao lưu mirror + bundle toàn bộ repo GitHub trước khi gỡ dòng ghi công AI khỏi lịch sử; bản lưu ở C:/Users/NguyenVD/wsl-backup/mechops-before-rewrite*.

_Đóng 2026-11-08T05:22:51Z · commit `84ca357`_

## Đã nâng thành
none
