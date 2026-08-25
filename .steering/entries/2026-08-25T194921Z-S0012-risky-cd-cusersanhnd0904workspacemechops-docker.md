---
id: S0012
date: 2026-08-25T19:49:21Z
kind: risky
outcome: kept
title: "cd /c/Users/AnhND0904/workspace/MechOps ; docker compose -f docker-com"
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
commit: 5d7cd9e
evidence: "docs/evidence/ci/2026-07-14T193011Z-544e2a4"
promoted_to: "trace.py check_exec_bits() — MUST_EXEC phai la 100755"
source: hook
---

# S0012 · cd /c/Users/AnhND0904/workspace/MechOps ; docker compose -f docker-com

## Vì sao đụng tới
Hook PreToolUse ghi tự động khi thấy lệnh có sức phá hoại.

## Lệnh
```
cd /c/Users/AnhND0904/workspace/MechOps\ndocker compose -f docker-compose.dev.yml exec -T dev bash -c '\nset -e\nrm -rf /tmp/ci; git clone -q /w /tmp/ci 2>/dev/null; cd /tmp/ci\ngit checkout -q feat/ai-flow 2>/dev/null || true\necho "### YAML workflow có parse được không ###"\npython3 -c "import yaml,sys; [yaml.safe_load(open(f)) for f in (\\".github/workflows/pr.yml\\",\\".github/workflows/nightly.yml\\")]; print(\\"YAML OK\\")"\necho\necho "### quyền thực thi sau khi clone (giống runner) ###"\nls -l mo .githooks/commit-msg | awk "{print \\$1, \\$NF}"\necho\necho "### chạy ./mo --native gen như CI ###"\n./mo --native gen; echo "exit=$?"' 2>&1 | tail -20
```

## Kết luận
**kept** — Dung lai moi truong CI trong container tu ban clone sach; lo ra mo khong co bit thuc thi trong git.

_Đóng 2026-08-25T19:51:53Z · commit `5d7cd9e`_

## Đã nâng thành
trace.py check_exec_bits() — MUST_EXEC phai la 100755
