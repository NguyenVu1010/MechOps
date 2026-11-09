---
id: S0018
date: 2026-11-08T05:21:32Z
kind: risky
outcome: kept
title: "S=C:/Users/NguyenVD/AppData/Local/Temp/claude/bb657f28194a187e/651f69"
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
promoted_to: "dòng CLAUDE.md cấm ghi công AI + tools/checks/commit_msg.py"
source: hook
---

# S0018 · S=C:/Users/NguyenVD/AppData/Local/Temp/claude/bb657f28194a187e/651f69

## Vì sao đụng tới
Hook PreToolUse ghi tự động khi thấy lệnh có sức phá hoại.

## Lệnh
```
S="/c/Users/NguyenVD/AppData/Local/Temp/claude/bb657f28194a187e/651f6916-13db-489e-84a2-5e5a974fce72/scratchpad/rewrite"; R=repos/NguyenVu1010/MechOps\ncd "/clean.git" && git config --unset remote.origin.mirror && git remote set-url origin git@github.com:NguyenVu1010/MechOps.git && git remote -v | head -1\nrestore() { gh api -X PUT /branches/main/protection --input "/main-restore.json" --jq '"main: force=\(.allow_force_pushes.enabled) admins=\(.enforce_admins.enabled)"'; gh api -X PUT /rulesets/22067311 -f enforcement=active --jq '"develop ruleset: \(.enforcement)"'; }\ntrap restore EXIT\ngh api -X PUT /rulesets/22067311 -f enforcement=disabled --jq '"develop ruleset: \(.enforcement)"'\ngh api -X PUT /branches/main/protection --input "/main-open.json" --jq '"main: force=\(.allow_force_pushes.enabled)"'\ngit push --force origin refs/heads/develop:refs/heads/develop refs/heads/main:refs/heads/main refs/heads/feat/ai-flow:refs/heads/feat/ai-flow 2>&1 | tail -4\ngit push origin --delete docs/adr-0012-0018-master-plan 2>&1 | tail -2
```

## Kết luận
**kept** — Force-push develop và feat/ai-flow đã gỡ dòng Co-Authored-By/Claude-Session (cây file trùng bản cũ, tác giả và ngày giữ nguyên); xoá nhánh đã merge docs/adr-0012-0018-master-plan; main bị từ chối vì enforce_admins; bảo vệ khôi phục bằng trap.

_Đóng 2026-11-08T05:22:55Z · commit `84ca357`_

## Đã nâng thành
dòng CLAUDE.md cấm ghi công AI + tools/checks/commit_msg.py
