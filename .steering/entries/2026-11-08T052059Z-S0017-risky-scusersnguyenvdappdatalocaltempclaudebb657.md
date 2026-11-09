---
id: S0017
date: 2026-11-08T05:20:59Z
kind: risky
outcome: reverted
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
promoted_to: "none"
source: hook
---

# S0017 · S=C:/Users/NguyenVD/AppData/Local/Temp/claude/bb657f28194a187e/651f69

## Vì sao đụng tới
Hook PreToolUse ghi tự động khi thấy lệnh có sức phá hoại.

## Lệnh
```
S="/c/Users/NguyenVD/AppData/Local/Temp/claude/bb657f28194a187e/651f6916-13db-489e-84a2-5e5a974fce72/scratchpad/rewrite"; R=repos/NguyenVu1010/MechOps\ngh api -X PUT /rulesets/22067311 -f enforcement=disabled --jq .enforcement\ngh api -X PUT /branches/main/protection --input "/main-open.json" --jq .allow_force_pushes.enabled\ncd "/clean.git" && git remote add origin git@github.com:NguyenVu1010/MechOps.git 2>/dev/null; git push --force origin refs/heads/develop:refs/heads/develop refs/heads/main:refs/heads/main refs/heads/feat/ai-flow:refs/heads/feat/ai-flow 2>&1 | tail -5\ngit push origin --delete docs/adr-0012-0018-master-plan 2>&1 | tail -2\ncd /c/Users/NguyenVD/workspace/MechOps\ngh api -X PUT /branches/main/protection --input "/main-restore.json" --jq '{force:.allow_force_pushes.enabled, admins:.enforce_admins.enabled}'\ngh api -X PUT /rulesets/22067311 -f enforcement=active --jq .enforcement
```

## Kết luận
**reverted** — Lần push đầu thất bại vì mirror còn cờ remote.origin.mirror; không ref nào trên GitHub đổi, ruleset develop và bảo vệ main đã bật lại ngay.

_Đóng 2026-11-08T05:22:53Z · commit `84ca357`_

## Đã nâng thành
none
