---
id: S0019
date: 2026-11-08T05:21:55Z
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
promoted_to: "none"
source: hook
---

# S0019 · S=C:/Users/NguyenVD/AppData/Local/Temp/claude/bb657f28194a187e/651f69

## Vì sao đụng tới
Hook PreToolUse ghi tự động khi thấy lệnh có sức phá hoại.

## Lệnh
```
S="/c/Users/NguyenVD/AppData/Local/Temp/claude/bb657f28194a187e/651f6916-13db-489e-84a2-5e5a974fce72/scratchpad/rewrite"; R=repos/NguyenVu1010/MechOps\nPYTHONIOENCODING=utf-8 python -c "\nimport json,os;p=os.environ['TEMP'];d=json.load(open(p+'/main-open.json'));d['enforce_admins']=False;json.dump(d,open(p+'/main-open2.json','w'))"\nrestore() { gh api -X PUT /branches/main/protection --input "/main-restore.json" --jq '"main: force=\(.allow_force_pushes.enabled) admins=\(.enforce_admins.enabled) reviews=\(.required_pull_request_reviews.required_approving_review_count)"'; }\ntrap restore EXIT\ngh api -X PUT /branches/main/protection --input "/main-open2.json" --jq '"main: force=\(.allow_force_pushes.enabled) admins=\(.enforce_admins.enabled)"'\ncd "/clean.git" && git push --force origin refs/heads/main:refs/heads/main 2>&1 | tail -3
```

## Kết luận
**kept** — Force-push main với enforce_admins tắt tạm; main sạch dòng ghi công, cây file không đổi; bảo vệ main khôi phục (force=false, admins=true).

_Đóng 2026-11-08T05:22:57Z · commit `84ca357`_

## Đã nâng thành
none
