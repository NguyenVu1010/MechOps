---
id: S0002
date: 2026-08-23T06:37:17Z
kind: discovery
outcome: kept
title: "4 skill co frontmatter YAML khong hop le ma van chay"
area: flow
milestone: M1
test_ids: []
supersedes: []
branch: "main"
commit: 9f5be49
evidence: "docs/evidence/ci/2026-08-22T192826Z-9f5be49"
promoted_to: "trace.py check_frontmatter() — CI bat thay vi dua vao may man"
source: agent
---

# S0002 · 4 skill co frontmatter YAML khong hop le ma van chay

## Vì sao đụng tới
Viet script kiem frontmatter cua 16 skill bang PyYAML truoc khi bao la xong.

## Tin rằng
Tuong frontmatter cac skill co san deu hop le, vi Claude Code van nap va trigger chung binh thuong.

## Đã làm
- Chay yaml.safe_load tren tung SKILL.md
- Doi 'Trigger:' thanh 'Trigger —' o adr, contract-guard, go-conventions, test-evidence

## Bằng chứng
yaml.scanner.ScannerError: mapping values are not allowed here — .claude/skills/adr/SKILL.md dong 3, tai 'Trigger: ADR, decision'

## Kết luận
**kept** — Claude Code doc frontmatter long nen skill van nap duoc: hong im lang. Se vo o phien ban sau hoac khi dong goi skill, va khong ai biet vi sao skill ngung trigger.

_Đóng 2026-08-23T06:37:18Z · commit `9f5be49`_

## Đã nâng thành
trace.py check_frontmatter() — CI bat thay vi dua vao may man
